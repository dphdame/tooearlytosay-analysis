"""
JPAM Paper — Phase 2 v2: Feature Engineering (Revised)
Fixes from validation:
  1. Leave-one-out z-scores (prevents circularity)
  2. Group C features: share_em_codes, share_high_reimburse, telehealth_share, rbcs_category_diversity
  3. z_total_paid bug fix (was computed but never output)
  4. QI checks: correlation matrix, VIF, winsorization at 1st/99th

Fraud-only labels (LEIE 1128a1, a3, b7, b8, b1).
Pre-exclusion temporal windowing for excluded providers.
"""
import duckdb
import json
import numpy as np
import pandas as pd
from datetime import datetime
from pathlib import Path

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)

OUT = Path("/tmp/mcaid/processed")
FRAUD = Path("/tmp/mcaid/05_fraud_detection")
RAW = Path("/tmp/mcaid/raw")
FRAUD.mkdir(parents=True, exist_ok=True)

con = duckdb.connect()
con.sql("SET memory_limit='8GB'")
con.sql("SET threads=4")

# ═══════════════════════════════════════════════════════════════════════
# STEP 1: Build fraud-only label table
# ═══════════════════════════════════════════════════════════════════════
log("═══ STEP 1: Fraud-only labels ═══")

con.sql("""
    CREATE TEMP TABLE fraud_labels AS
    SELECT npi, min(exclusion_date) as exclusion_date,
        first(excl_type) as excl_type
    FROM (
        SELECT DISTINCT NPI as npi,
            EXCLTYPE as excl_type,
            TRY_CAST(LEFT(EXCLDATE,4)||'-'||SUBSTR(EXCLDATE,5,2)||'-'||SUBSTR(EXCLDATE,7,2) AS DATE) as exclusion_date
        FROM read_csv('/tmp/mcaid/raw/oig_leie.csv', auto_detect=true, all_varchar=true)
        WHERE NPI IS NOT NULL AND length(NPI) = 10 AND NPI != '0000000000'
          AND EXCLTYPE IN ('1128a1','1128a3','1128b7','1128b8','1128b1')
    )
    GROUP BY npi
""")

n_labels = con.sql("SELECT count(*) FROM fraud_labels").fetchone()[0]
log(f"  Fraud label NPIs: {n_labels:,}")

con.sql("""
    SELECT
        CASE
            WHEN exclusion_date < '2018-01-01' THEN 'pre_period'
            WHEN exclusion_date BETWEEN '2018-01-01' AND '2024-12-31' THEN 'during_period'
            WHEN exclusion_date > '2024-12-31' THEN 'post_period'
            ELSE 'no_date'
        END as period,
        count(*) as n
    FROM fraud_labels
    GROUP BY 1 ORDER BY 1
""").show()

# ═══════════════════════════════════════════════════════════════════════
# STEP 2: Load reference tables for Group C features
# ═══════════════════════════════════════════════════════════════════════
log("═══ STEP 2: Load reference tables ═══")

# Telehealth-eligible HCPCS codes (CMS 2026 list)
con.sql(f"""
    CREATE TEMP TABLE telehealth_codes AS
    SELECT DISTINCT TRIM(hcpcs) as hcpcs_code
    FROM (
        SELECT TRIM("CY 2026 Final List of Medicare Telehealth Services") as hcpcs
        FROM read_csv('{RAW}/telehealth_codes.txt', auto_detect=true, all_varchar=true,
                      header=true)
        WHERE "CY 2026 Final List of Medicare Telehealth Services" IS NOT NULL
    )
    WHERE hcpcs ~ '^[A-Z0-9]{{4,5}}$' AND hcpcs != 'HCPCS'
""")
n_tele = con.sql("SELECT count(*) FROM telehealth_codes").fetchone()[0]
log(f"  Telehealth-eligible HCPCS codes: {n_tele}")

# RBCS taxonomy (HCPCS → category)
con.sql(f"""
    CREATE TEMP TABLE rbcs AS
    SELECT DISTINCT HCPCS_Cd as hcpcs_code, RBCS_Cat_Subcat as rbcs_subcat
    FROM read_csv('{RAW}/RBCS_Taxonomy_RY2025.csv', auto_detect=true)
    WHERE RBCS_Latest_Assignment = 1
      OR RBCS_Analysis_End_Dt >= '2024-01-01'
""")
n_rbcs = con.sql("SELECT count(*) FROM rbcs").fetchone()[0]
log(f"  RBCS mappings: {n_rbcs}")

# ═══════════════════════════════════════════════════════════════════════
# STEP 3: Compute national high-reimbursement threshold
# ═══════════════════════════════════════════════════════════════════════
log("═══ STEP 3: National high-reimburse threshold ═══")

con.sql(f"""
    CREATE TEMP TABLE national_code_rates AS
    SELECT hcpcs_code,
        SUM(paid) / NULLIF(SUM(claims), 0) as avg_paid_per_claim,
        SUM(claims) as total_claims
    FROM read_parquet('{OUT}/spending.parquet')
    GROUP BY hcpcs_code
    HAVING SUM(claims) >= 100
""")

high_reimb_threshold = con.sql("""
    SELECT PERCENTILE_CONT(0.90) WITHIN GROUP (ORDER BY avg_paid_per_claim) as p90
    FROM national_code_rates
""").fetchone()[0]
log(f"  High-reimburse threshold (90th pctile avg paid/claim): ${high_reimb_threshold:,.2f}")

con.sql(f"""
    CREATE TEMP TABLE high_reimburse_codes AS
    SELECT hcpcs_code FROM national_code_rates
    WHERE avg_paid_per_claim >= {high_reimb_threshold}
""")
n_hr = con.sql("SELECT count(*) FROM high_reimburse_codes").fetchone()[0]
log(f"  High-reimburse HCPCS codes: {n_hr}")

# ═══════════════════════════════════════════════════════════════════════
# STEP 4: Provider features from spending (2 passes)
# ═══════════════════════════════════════════════════════════════════════
log("═══ STEP 4: Provider features (pre-exclusion windowed) ═══")

# --- Pass 1: Monthly aggregates ---
log("  Pass 1: Monthly aggregates with temporal filter...")
con.sql(f"""
    CREATE TEMP TABLE provider_months AS
    SELECT
        s.billing_npi,
        s.claim_month,
        SUM(s.paid) as month_paid,
        SUM(s.claims) as month_claims,
        SUM(s.beneficiaries) as month_beneficiaries,
        COUNT(DISTINCT s.hcpcs_code) as month_hcpcs
    FROM read_parquet('{OUT}/spending.parquet') s
    LEFT JOIN fraud_labels fl ON s.billing_npi = fl.npi
    WHERE fl.npi IS NULL
       OR s.claim_month < fl.exclusion_date
    GROUP BY s.billing_npi, s.claim_month
""")

pm_count = con.sql("SELECT count(*) FROM provider_months").fetchone()[0]
log(f"  Provider-month rows (filtered): {pm_count:,}")

# Volume & intensity features
log("  Computing volume & intensity features...")
con.sql("""
    CREATE TEMP TABLE vol_features AS
    SELECT
        billing_npi,
        -- Volume (5)
        SUM(month_paid) as total_paid,
        SUM(month_claims) as total_claims,
        SUM(month_beneficiaries) as total_beneficiaries,
        COUNT(DISTINCT claim_month) as months_active,
        SUM(month_claims) * 1.0 / COUNT(DISTINCT claim_month) as claims_per_month,
        -- Intensity (4)
        SUM(month_paid) / NULLIF(SUM(month_claims), 0) as avg_paid_per_claim,
        SUM(month_paid) / NULLIF(SUM(month_beneficiaries), 0) as avg_paid_per_beneficiary,
        SUM(month_claims) * 1.0 / NULLIF(SUM(month_beneficiaries), 0) as claims_per_beneficiary,
        MAX(month_paid) as max_single_month_paid,
        -- Temporal (3)
        STDDEV(month_paid) as monthly_spending_volatility,
        STDDEV(month_paid) / NULLIF(AVG(month_paid), 0) as cv_monthly_paid,
        SUM(month_paid) / NULLIF(COUNT(DISTINCT claim_month), 0) as avg_monthly_paid
    FROM provider_months
    GROUP BY billing_npi
""")

# Temporal: billing gaps
log("  Computing temporal pattern features...")
con.sql("""
    CREATE TEMP TABLE temporal_features AS
    SELECT
        billing_npi,
        datediff('month', min(claim_month), max(claim_month)) + 1 as billing_window_months,
        CASE WHEN datediff('month', min(claim_month), max(claim_month)) > 0
            THEN 1.0 - (COUNT(DISTINCT claim_month) * 1.0 /
                        (datediff('month', min(claim_month), max(claim_month)) + 1))
            ELSE 0
        END as billing_gap_ratio
    FROM provider_months
    GROUP BY billing_npi
""")

# --- Pass 2: HCPCS-level features (all Group C) ---
log("  Pass 2: HCPCS-level features (Group C)...")
con.sql(f"""
    CREATE TEMP TABLE hcpcs_features AS
    SELECT
        billing_npi,
        -- Original HCPCS features (4)
        MAX(code_share) as share_top_code,
        SUM(code_share * code_share) as hcpcs_hhi,
        -SUM(CASE WHEN code_share > 0 THEN code_share * LN(code_share) ELSE 0 END) as hcpcs_entropy,
        COUNT(DISTINCT hcpcs_code) as unique_hcpcs,
        -- NEW Group C features (4)
        SUM(CASE WHEN hcpcs_code BETWEEN '99201' AND '99499' THEN claim_share ELSE 0 END) as share_em_codes,
        SUM(CASE WHEN is_high_reimb THEN claim_share ELSE 0 END) as share_high_reimburse,
        SUM(CASE WHEN is_telehealth THEN claim_share ELSE 0 END) as telehealth_share,
        COUNT(DISTINCT rbcs_subcat) as rbcs_category_diversity
    FROM (
        SELECT
            s.billing_npi,
            s.hcpcs_code,
            SUM(s.paid) / NULLIF(SUM(SUM(s.paid)) OVER (PARTITION BY s.billing_npi), 0) as code_share,
            SUM(s.claims) * 1.0 / NULLIF(SUM(SUM(s.claims)) OVER (PARTITION BY s.billing_npi), 0) as claim_share,
            MAX(CASE WHEN hr.hcpcs_code IS NOT NULL THEN true ELSE false END) as is_high_reimb,
            MAX(CASE WHEN tc.hcpcs_code IS NOT NULL THEN true ELSE false END) as is_telehealth,
            MAX(rb.rbcs_subcat) as rbcs_subcat
        FROM read_parquet('{OUT}/spending.parquet') s
        LEFT JOIN fraud_labels fl ON s.billing_npi = fl.npi
        LEFT JOIN high_reimburse_codes hr ON s.hcpcs_code = hr.hcpcs_code
        LEFT JOIN telehealth_codes tc ON s.hcpcs_code = tc.hcpcs_code
        LEFT JOIN rbcs rb ON s.hcpcs_code = rb.hcpcs_code
        WHERE fl.npi IS NULL OR s.claim_month < fl.exclusion_date
        GROUP BY s.billing_npi, s.hcpcs_code
    )
    GROUP BY billing_npi
""")

hcpcs_n = con.sql("SELECT count(*) FROM hcpcs_features").fetchone()[0]
log(f"  Providers with HCPCS features: {hcpcs_n:,}")

# ═══════════════════════════════════════════════════════════════════════
# STEP 5: Join all features + crosswalk + labels
# ═══════════════════════════════════════════════════════════════════════
log("═══ STEP 5: Join features + crosswalk ═══")

con.sql(f"""
    CREATE TEMP TABLE all_features AS
    SELECT
        v.billing_npi,
        -- Labels
        CASE WHEN fl.npi IS NOT NULL THEN true ELSE false END as is_fraud_excluded,
        fl.exclusion_date,
        fl.excl_type,
        CASE
            WHEN fl.exclusion_date < '2018-01-01' THEN 'pre_period'
            WHEN fl.exclusion_date BETWEEN '2018-01-01' AND '2024-12-31' THEN 'during_period'
            WHEN fl.exclusion_date > '2024-12-31' THEN 'post_period'
            WHEN fl.npi IS NULL THEN 'non_excluded'
            ELSE 'no_date'
        END as temporal_category,
        -- Crosswalk
        cx.nucc_grouping as specialty,
        cx.provider_state as state,
        cx.entity_type,
        -- Volume features (5)
        v.total_paid,
        v.total_claims,
        v.total_beneficiaries,
        v.months_active,
        v.claims_per_month,
        -- Intensity features (4)
        v.avg_paid_per_claim,
        v.avg_paid_per_beneficiary,
        v.claims_per_beneficiary,
        v.max_single_month_paid,
        -- Temporal features (4)
        v.monthly_spending_volatility,
        v.cv_monthly_paid,
        v.avg_monthly_paid,
        t.billing_gap_ratio,
        -- HCPCS features (8 — original 4 + new 4)
        h.share_top_code,
        h.hcpcs_hhi,
        h.hcpcs_entropy,
        h.unique_hcpcs,
        h.share_em_codes,
        h.share_high_reimburse,
        h.telehealth_share,
        h.rbcs_category_diversity
    FROM vol_features v
    LEFT JOIN temporal_features t ON v.billing_npi = t.billing_npi
    LEFT JOIN hcpcs_features h ON v.billing_npi = h.billing_npi
    LEFT JOIN fraud_labels fl ON v.billing_npi = fl.npi
    LEFT JOIN (
        SELECT DISTINCT ON (npi) npi, nucc_grouping, provider_state, entity_type
        FROM read_parquet('{OUT}/provider_crosswalk.parquet')
    ) cx ON v.billing_npi = cx.npi
""")

total = con.sql("SELECT count(*) FROM all_features").fetchone()[0]
fraud = con.sql("SELECT count(*) FROM all_features WHERE is_fraud_excluded").fetchone()[0]
log(f"  Total providers: {total:,}, Fraud-excluded: {fraud:,}")

# ═══════════════════════════════════════════════════════════════════════
# STEP 6: Leave-one-out peer z-scores (specialty × state)
# ═══════════════════════════════════════════════════════════════════════
log("═══ STEP 6: Leave-one-out peer z-scores ═══")

# Compute group sums and sum-of-squares for LOO adjustment
z_features = ['claims_per_month', 'avg_paid_per_beneficiary', 'hcpcs_entropy', 'total_paid']
z_aliases = ['cpm', 'ppb', 'entropy', 'paid']

# Build group stats with sum and sum_sq for each z-feature
agg_cols = ["COUNT(*) as peer_n"]
for feat, alias in zip(z_features, z_aliases):
    agg_cols.append(f"SUM({feat}) as peer_sum_{alias}")
    agg_cols.append(f"SUM({feat} * {feat}) as peer_sum_sq_{alias}")

agg_sql = ",\n        ".join(agg_cols)

con.sql(f"""
    CREATE TEMP TABLE peer_stats AS
    SELECT specialty, state,
        {agg_sql}
    FROM all_features
    WHERE specialty IS NOT NULL AND state IS NOT NULL
    GROUP BY specialty, state
""")

# Build LOO z-score expressions
# LOO mean: (group_sum - x_i) / (n - 1)
# LOO var: ((group_sum_sq - x_i^2) / (n - 2)) - ((group_sum - x_i) / (n - 1))^2
# LOO SD: sqrt(LOO_var)  [require n >= 3]
# z = (x_i - LOO_mean) / LOO_SD
z_score_cols = []
for feat, alias in zip(z_features, z_aliases):
    z_score_cols.append(f"""
            CASE WHEN ps.peer_n >= 20 AND ps.peer_n >= 3
                AND ((ps.peer_sum_sq_{alias} - af.{feat} * af.{feat}) / NULLIF(ps.peer_n - 2, 0)
                     - POWER((ps.peer_sum_{alias} - af.{feat}) / NULLIF(ps.peer_n - 1, 0), 2)) > 0
                THEN (af.{feat} - (ps.peer_sum_{alias} - af.{feat}) / NULLIF(ps.peer_n - 1, 0))
                     / SQRT((ps.peer_sum_sq_{alias} - af.{feat} * af.{feat}) / NULLIF(ps.peer_n - 2, 0)
                            - POWER((ps.peer_sum_{alias} - af.{feat}) / NULLIF(ps.peer_n - 1, 0), 2))
                ELSE NULL
            END as z_{alias}""")

z_sql = ",".join(z_score_cols)

# Final output with LOO z-scores and percentile ranks
log("  Computing LOO z-scores and percentile ranks...")
con.sql(f"""
    COPY (
        SELECT
            af.*,
            ps.peer_n as peer_group_size,
            -- LOO Z-scores (4)
            {z_sql},
            -- Percentile ranks within peer group
            PERCENT_RANK() OVER (PARTITION BY af.specialty, af.state ORDER BY af.total_paid) as pctile_total_paid,
            PERCENT_RANK() OVER (PARTITION BY af.specialty, af.state ORDER BY af.claims_per_month) as pctile_claims_per_month,
            PERCENT_RANK() OVER (PARTITION BY af.specialty, af.state ORDER BY af.avg_paid_per_beneficiary) as pctile_paid_per_bene
        FROM all_features af
        LEFT JOIN peer_stats ps ON af.specialty = ps.specialty AND af.state = ps.state
    ) TO '{FRAUD}/phase2_features_v2.parquet' (FORMAT 'parquet', COMPRESSION 'zstd')
""")

# ═══════════════════════════════════════════════════════════════════════
# STEP 7: QI Checks
# ═══════════════════════════════════════════════════════════════════════
log("═══ STEP 7: QI Checks ═══")

df = con.sql(f"SELECT * FROM read_parquet('{FRAUD}/phase2_features_v2.parquet')").fetchdf()

feature_cols = [
    'total_paid', 'total_claims', 'total_beneficiaries', 'months_active', 'claims_per_month',
    'avg_paid_per_claim', 'avg_paid_per_beneficiary', 'claims_per_beneficiary', 'max_single_month_paid',
    'monthly_spending_volatility', 'cv_monthly_paid', 'avg_monthly_paid', 'billing_gap_ratio',
    'share_top_code', 'hcpcs_hhi', 'hcpcs_entropy', 'unique_hcpcs',
    'share_em_codes', 'share_high_reimburse', 'telehealth_share', 'rbcs_category_diversity',
    'z_cpm', 'z_ppb', 'z_entropy', 'z_paid',
]

log(f"  Total features: {len(feature_cols)}")

# --- QI 1: Correlation matrix (flag |r| > 0.90) ---
log("  QI 1: Correlation matrix...")
numeric_df = df[feature_cols].fillna(0)
corr = numeric_df.corr()
high_corr = []
for i in range(len(feature_cols)):
    for j in range(i+1, len(feature_cols)):
        r = corr.iloc[i, j]
        if abs(r) > 0.90:
            high_corr.append((feature_cols[i], feature_cols[j], r))

if high_corr:
    log(f"  ⚠ High correlations (|r| > 0.90): {len(high_corr)}")
    for f1, f2, r in sorted(high_corr, key=lambda x: -abs(x[2])):
        log(f"    {f1} × {f2}: r = {r:.3f}")
else:
    log("  ✓ No feature pairs with |r| > 0.90")

# --- QI 2: VIF ---
log("  QI 2: VIF (Variance Inflation Factor)...")
from numpy.linalg import LinAlgError
try:
    X = numeric_df[feature_cols[:21]].values  # raw features only (not z-scores)
    X = np.nan_to_num(X, nan=0.0, posinf=1e10, neginf=-1e10)
    from sklearn.preprocessing import StandardScaler as SS
    X_s = SS().fit_transform(X)
    # VIF = 1/(1-R²) for each feature regressed on all others
    # Use correlation matrix inverse diagonal for speed
    corr_raw = np.corrcoef(X_s, rowvar=False)
    # Add small ridge to prevent singularity
    corr_reg = corr_raw + np.eye(corr_raw.shape[0]) * 1e-6
    try:
        inv = np.linalg.inv(corr_reg)
        vifs = np.diag(inv)
        high_vif = [(feature_cols[i], vifs[i]) for i in range(len(vifs)) if vifs[i] > 10]
        if high_vif:
            log(f"  ⚠ High VIF (>10): {len(high_vif)}")
            for fn, v in sorted(high_vif, key=lambda x: -x[1]):
                log(f"    {fn}: VIF = {v:.1f}")
        else:
            log("  ✓ All VIFs < 10")
    except LinAlgError:
        log("  ⚠ Correlation matrix singular — cannot compute VIF")
except Exception as e:
    log(f"  ⚠ VIF computation error: {e}")

# --- QI 3: Missing data report ---
log("  QI 3: Missing data report (fraud-excluded)...")
fraud_df = df[df['is_fraud_excluded']]
for col in feature_cols:
    n_null = fraud_df[col].isna().sum()
    if n_null > 0:
        log(f"    {col}: {n_null}/{len(fraud_df)} missing ({100*n_null/len(fraud_df):.1f}%)")

# --- QI 4: Winsorization check ---
log("  QI 4: Winsorization check (1st/99th percentiles)...")
raw_features = [f for f in feature_cols if not f.startswith('z_')]
needs_winsorize = []
for col in raw_features:
    vals = df[col].dropna()
    if len(vals) > 100:
        p1, p99 = vals.quantile([0.01, 0.99])
        below = (vals < p1).sum()
        above = (vals > p99).sum()
        skew = vals.skew()
        if abs(skew) > 5:
            needs_winsorize.append((col, skew, p1, p99))

if needs_winsorize:
    log(f"  Features with |skew| > 5 (candidates for winsorization):")
    for col, skew, p1, p99 in needs_winsorize:
        log(f"    {col}: skew={skew:.1f}, 1st%={p1:.2f}, 99th%={p99:.2f}")
else:
    log("  ✓ No features with extreme skew (|skew| > 5)")

# --- QI 5: Z-score direction check ---
log("  QI 5: Z-score direction check (LOO)...")
z_cols = ['z_cpm', 'z_ppb', 'z_entropy', 'z_paid']
for zc in z_cols:
    fraud_med = fraud_df[zc].median()
    non_med = df[~df['is_fraud_excluded']][zc].median()
    direction = "Higher (✓)" if fraud_med > non_med else "Lower (⚠)"
    log(f"    {zc}: fraud median={fraud_med:.3f}, non-excl median={non_med:.3f} → {direction}")

# --- QI 6: Peer group coverage ---
log("  QI 6: Peer group coverage...")
pg_fraud = fraud_df['peer_group_size'].fillna(0)
log(f"    Fraud in peer groups >= 20: {(pg_fraud >= 20).sum()}/{len(fraud_df)}")
log(f"    Fraud with z-scores: {fraud_df['z_cpm'].notna().sum()}/{len(fraud_df)}")

# --- QI 7: New Group C feature distributions ---
log("  QI 7: Group C feature sanity check (fraud-excluded medians)...")
group_c = ['share_em_codes', 'share_high_reimburse', 'telehealth_share', 'rbcs_category_diversity']
for col in group_c:
    fraud_med = fraud_df[col].median()
    non_med = df[~df['is_fraud_excluded']][col].median()
    log(f"    {col}: fraud={fraud_med:.3f}, non-excl={non_med:.3f}")

# ═══════════════════════════════════════════════════════════════════════
# Summary
# ═══════════════════════════════════════════════════════════════════════
log("═══ SUMMARY ═══")
n = len(df)
log(f"  Saved: {FRAUD}/phase2_features_v2.parquet ({n:,} rows)")
log(f"  Features: {len(feature_cols)}")
for f in feature_cols:
    log(f"    - {f}")

# Temporal category breakdown
log("\n  Temporal categories (fraud-excluded):")
con.sql(f"""
    SELECT temporal_category, count(*) as n,
        median(months_active) as med_months,
        median(total_paid) as med_paid
    FROM read_parquet('{FRAUD}/phase2_features_v2.parquet')
    WHERE is_fraud_excluded
    GROUP BY 1 ORDER BY 1
""").show()

# Save QI report
qi_report = {
    "high_correlations": [(f1, f2, float(r)) for f1, f2, r in high_corr] if high_corr else [],
    "features_needing_winsorization": [(col, float(s)) for col, s, _, _ in needs_winsorize] if needs_winsorize else [],
    "n_features": len(feature_cols),
    "n_providers": n,
    "n_fraud_excluded": int(fraud),
}
with open(f"{FRAUD}/phase2_qi_report.json", "w") as f:
    json.dump(qi_report, f, indent=2)
log(f"  Saved: phase2_qi_report.json")

con.close()
log("Phase 2 v2 feature engineering complete.")
