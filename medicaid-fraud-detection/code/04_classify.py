"""
JPAM Paper — Phase 3 v2: Classification & Evaluation (Revised)
Fixes from validation:
  1. Fixed random seed bug (per-fold seeding, not global reset)
  2. Added specialty-adjusted spending baseline (critical benchmark)
  3. Added label leakage diagnostic test (months_since_exclusion, total_months_active)
  4. Added precision@1%, 5%, 10% thresholds
  5. Added single-feature threshold baseline
  6. Reads phase2_features_v2.parquet (LOO z-scores, Group C features)
  7. XGBoost now installed

Produces Tables 4-7 and Figures 3-4.
"""
import duckdb
import json
import numpy as np
import pandas as pd
import warnings
warnings.filterwarnings('ignore')
from datetime import datetime
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (roc_auc_score, average_precision_score,
                             precision_recall_curve, roc_curve,
                             precision_score, recall_score)
from sklearn.preprocessing import StandardScaler, LabelEncoder
from xgboost import XGBClassifier

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)

FRAUD = Path("/tmp/mcaid/05_fraud_detection")

# ═══════════════════════════════════════════════════════════════════════
# STEP 1: Load features and prepare data
# ═══════════════════════════════════════════════════════════════════════
log("═══ STEP 1: Load and prepare data ═══")

con = duckdb.connect()
df = con.sql(f"""
    SELECT * FROM read_parquet('{FRAUD}/phase2_features_v2.parquet')
""").fetchdf()
con.close()

# Numeric features (25 = 21 raw + 4 z-scores)
numeric_features = [
    'total_paid', 'total_claims', 'total_beneficiaries', 'months_active', 'claims_per_month',
    'avg_paid_per_claim', 'avg_paid_per_beneficiary', 'claims_per_beneficiary', 'max_single_month_paid',
    'monthly_spending_volatility', 'cv_monthly_paid', 'avg_monthly_paid', 'billing_gap_ratio',
    'share_top_code', 'hcpcs_hhi', 'hcpcs_entropy', 'unique_hcpcs',
    'share_em_codes', 'share_high_reimburse', 'telehealth_share', 'rbcs_category_diversity',
    'z_cpm', 'z_ppb', 'z_entropy', 'z_paid',
]

# Encode entity_type
le_entity = LabelEncoder()
df['entity_type_enc'] = le_entity.fit_transform(df['entity_type'].fillna('Unknown').astype(str))

all_features = numeric_features + ['entity_type_enc']
feature_names = all_features

log(f"  Total rows: {len(df):,}")
log(f"  Features: {len(feature_names)}")

# Split by temporal category
fraud_during = df[df['temporal_category'] == 'during_period'].copy()
fraud_post = df[df['temporal_category'] == 'post_period'].copy()
non_excluded = df[df['temporal_category'] == 'non_excluded'].copy()

log(f"  During-period fraud: {len(fraud_during)}")
log(f"  Post-period fraud (holdout): {len(fraud_post)}")
log(f"  Non-excluded: {len(non_excluded):,}")

# Parse exclusion year for during-period
fraud_during['excl_year'] = pd.to_datetime(fraud_during['exclusion_date']).dt.year

# ═══════════════════════════════════════════════════════════════════════
# STEP 2: Forward-chaining temporal CV
# ═══════════════════════════════════════════════════════════════════════
log("═══ STEP 2: Forward-chaining temporal CV ═══")

RATIO = 10

def make_fold_data(train_fraud, val_fraud, non_excl, fold_idx, ratio=RATIO):
    """Create train/val sets with undersampled non-excluded.
    FIX: Use per-fold seed instead of global reset."""
    rng = np.random.RandomState(42 + fold_idx)  # deterministic but unique per fold
    # Train: all fraud + sampled non-excluded
    n_neg_train = min(len(train_fraud) * ratio, len(non_excl))
    train_neg_idx = rng.choice(len(non_excl), size=n_neg_train, replace=False)
    train_df = pd.concat([train_fraud, non_excl.iloc[train_neg_idx]])

    # Val: all fraud + different sampled non-excluded
    remaining = np.setdiff1d(np.arange(len(non_excl)), train_neg_idx)
    n_neg_val = min(len(val_fraud) * ratio, len(remaining))
    val_neg_idx = rng.choice(remaining, size=n_neg_val, replace=False)
    val_df = pd.concat([val_fraud, non_excl.iloc[val_neg_idx]])

    return train_df, val_df

# Forward-chaining folds
folds = [
    ([2018, 2019], 2020),
    ([2018, 2019, 2020], 2021),
    ([2018, 2019, 2020, 2021], 2022),
    ([2018, 2019, 2020, 2021, 2022], 2023),
    ([2018, 2019, 2020, 2021, 2022, 2023], 2024),
]

# Three classifiers
classifiers = {
    'Logistic (L1)': lambda: LogisticRegression(
        penalty='l1', solver='saga', class_weight='balanced',
        max_iter=5000, random_state=42, C=0.1
    ),
    'Random Forest': lambda: RandomForestClassifier(
        n_estimators=200, max_depth=12, min_samples_leaf=5,
        class_weight='balanced', random_state=42, n_jobs=-1
    ),
    'XGBoost': lambda: XGBClassifier(
        n_estimators=200, max_depth=6, learning_rate=0.1,
        scale_pos_weight=RATIO, random_state=42,
        eval_metric='logloss', verbosity=0
    ),
}
log(f"  Classifiers: {list(classifiers.keys())}")

scaler = StandardScaler()

cv_results = {name: {'auc_roc': [], 'pr_auc': [], 'prec_top1': [], 'prec_top5': [],
                      'prec_top10': [], 'rec_top5': []}
              for name in classifiers}

for fold_idx, (train_years, val_year) in enumerate(folds):
    train_fraud = fraud_during[fraud_during['excl_year'].isin(train_years)]
    val_fraud = fraud_during[fraud_during['excl_year'] == val_year]

    if len(train_fraud) < 5 or len(val_fraud) < 3:
        log(f"  Fold {fold_idx+1}: skipping (train={len(train_fraud)}, val={len(val_fraud)})")
        continue

    train_df, val_df = make_fold_data(train_fraud, val_fraud, non_excluded, fold_idx)

    X_train = train_df[feature_names].fillna(0).values
    y_train = train_df['is_fraud_excluded'].astype(int).values
    X_val = val_df[feature_names].fillna(0).values
    y_val = val_df['is_fraud_excluded'].astype(int).values

    X_train_s = scaler.fit_transform(X_train)
    X_val_s = scaler.transform(X_val)

    log(f"  Fold {fold_idx+1}: train {train_years}→val {val_year} "
        f"(train: {y_train.sum()} fraud/{len(y_train)}, val: {y_val.sum()} fraud/{len(y_val)})")

    for name, clf_fn in classifiers.items():
        clf = clf_fn()
        if 'Logistic' in name:
            clf.fit(X_train_s, y_train)
            y_score = clf.predict_proba(X_val_s)[:, 1]
        else:
            clf.fit(X_train, y_train)
            y_score = clf.predict_proba(X_val)[:, 1]

        if y_val.sum() > 0 and y_val.sum() < len(y_val):
            auc = roc_auc_score(y_val, y_score)
            pr_auc = average_precision_score(y_val, y_score)

            # Precision at top 1%, 5%, 10%
            for pct, key in [(1, 'prec_top1'), (5, 'prec_top5'), (10, 'prec_top10')]:
                threshold = np.percentile(y_score, 100 - pct)
                y_pred = (y_score >= threshold).astype(int)
                prec = precision_score(y_val, y_pred, zero_division=0)
                rec = recall_score(y_val, y_pred, zero_division=0)
                cv_results[name][key].append(prec)
                if pct == 5:
                    cv_results[name]['rec_top5'].append(rec)

            cv_results[name]['auc_roc'].append(auc)
            cv_results[name]['pr_auc'].append(pr_auc)

# ═══════════════════════════════════════════════════════════════════════
# TABLE 4: CV Performance Summary
# ═══════════════════════════════════════════════════════════════════════
log("═══ TABLE 4: Cross-Validation Performance ═══")

print("\n┌────────────────────────────────────────────────────────────────────────────────────┐")
print("│           TABLE 4: Forward-Chaining CV Performance (Fraud-Only Labels)             │")
print("├─────────────────┬───────────────┬───────────────┬─────────┬─────────┬─────────┬────┤")
print("│ Model           │ AUC-ROC       │ PR-AUC        │ P@Top1% │ P@Top5% │ P@Top10%│  N │")
print("├─────────────────┼───────────────┼───────────────┼─────────┼─────────┼─────────┼────┤")

table4 = {}
for name in classifiers:
    r = cv_results[name]
    if r['auc_roc']:
        mean_auc = np.mean(r['auc_roc'])
        sd_auc = np.std(r['auc_roc'])
        mean_pr = np.mean(r['pr_auc'])
        sd_pr = np.std(r['pr_auc'])
        mean_p1 = np.mean(r['prec_top1'])
        mean_p5 = np.mean(r['prec_top5'])
        mean_p10 = np.mean(r['prec_top10'])
        n_folds = len(r['auc_roc'])
        print(f"│ {name:<15} │ {mean_auc:.3f} ± {sd_auc:.3f} │ {mean_pr:.3f} ± {sd_pr:.3f} │   {mean_p1:.3f} │   {mean_p5:.3f} │   {mean_p10:.3f} │ {n_folds:>2} │")
        table4[name] = {
            'auc_roc_mean': mean_auc, 'auc_roc_sd': sd_auc,
            'pr_auc_mean': mean_pr, 'pr_auc_sd': sd_pr,
            'prec_top1_mean': mean_p1, 'prec_top5_mean': mean_p5, 'prec_top10_mean': mean_p10,
            'n_folds': n_folds, 'fold_aucs': r['auc_roc'],
        }

print("└─────────────────┴───────────────┴───────────────┴─────────┴─────────┴─────────┴────┘")

# ═══════════════════════════════════════════════════════════════════════
# STEP 3: Holdout test (2025+ exclusions)
# ═══════════════════════════════════════════════════════════════════════
log("═══ STEP 3: Holdout test (2025+ exclusions) ═══")

rng_holdout = np.random.RandomState(42)
train_all = pd.concat([fraud_during, non_excluded.sample(
    n=min(len(fraud_during)*RATIO, len(non_excluded)), random_state=42)])

remaining_ne = non_excluded.drop(train_all[~train_all['is_fraud_excluded']].index, errors='ignore')
holdout = pd.concat([fraud_post, remaining_ne.sample(
    n=min(len(fraud_post)*RATIO, len(remaining_ne)), random_state=99)])

X_train_all = train_all[feature_names].fillna(0).values
y_train_all = train_all['is_fraud_excluded'].astype(int).values
X_holdout = holdout[feature_names].fillna(0).values
y_holdout = holdout['is_fraud_excluded'].astype(int).values
X_train_all_s = scaler.fit_transform(X_train_all)
X_holdout_s = scaler.transform(X_holdout)

log(f"  Train: {y_train_all.sum()} fraud / {len(y_train_all)} total")
log(f"  Holdout: {y_holdout.sum()} fraud / {len(y_holdout)} total")

print("\n┌────────────────────────────────────────────────────────────────────────────────────┐")
print("│           TABLE 5: Holdout Test (2025+ Exclusions)                                 │")
print("├─────────────────┬───────────────┬───────────────┬─────────┬─────────┬──────────────┤")
print("│ Model           │ AUC-ROC       │ PR-AUC        │ P@Top1% │ P@Top5% │ Recall@Top5% │")
print("├─────────────────┼───────────────┼───────────────┼─────────┼─────────┼──────────────┤")

holdout_results = {}
holdout_scores = {}
for name, clf_fn in classifiers.items():
    clf = clf_fn()
    if 'Logistic' in name:
        clf.fit(X_train_all_s, y_train_all)
        y_score = clf.predict_proba(X_holdout_s)[:, 1]
    else:
        clf.fit(X_train_all, y_train_all)
        y_score = clf.predict_proba(X_holdout)[:, 1]

    holdout_scores[name] = y_score

    if y_holdout.sum() > 0:
        auc = roc_auc_score(y_holdout, y_score)
        pr_auc = average_precision_score(y_holdout, y_score)
        results_row = {'auc_roc': auc, 'pr_auc': pr_auc}

        for pct, key in [(1, 'prec_top1'), (5, 'prec_top5'), (10, 'prec_top10')]:
            threshold = np.percentile(y_score, 100 - pct)
            y_pred = (y_score >= threshold).astype(int)
            results_row[key] = precision_score(y_holdout, y_pred, zero_division=0)
            if pct == 5:
                results_row['rec_top5'] = recall_score(y_holdout, y_pred, zero_division=0)

        print(f"│ {name:<15} │         {auc:.3f} │         {pr_auc:.3f} │   {results_row['prec_top1']:.3f} │   {results_row['prec_top5']:.3f} │        {results_row['rec_top5']:.3f} │")
        holdout_results[name] = results_row

print("└─────────────────┴───────────────┴───────────────┴─────────┴─────────┴──────────────┘")

# ═══════════════════════════════════════════════════════════════════════
# STEP 4: Baseline comparisons (Table 6) — WITH specialty-adjusted
# ═══════════════════════════════════════════════════════════════════════
log("═══ TABLE 6: Baseline Comparisons ═══")

baseline_rate = y_holdout.mean()

print("\n┌────────────────────────────────────────────────────────────────────┐")
print("│      TABLE 6: Lift Over Baselines (Holdout, Prec@Top5%)          │")
print("├──────────────────────────────────────┬─────────────┬──────────────┤")
print("│ Method                               │ Prec@Top5%  │ Lift vs Rand │")
print("├──────────────────────────────────────┼─────────────┼──────────────┤")

def baseline_prec(scores, y_true, pct=5):
    """Precision when flagging top pct% by score."""
    n_flag = max(1, int(pct/100 * len(scores)))
    top_idx = np.argsort(-scores)[:n_flag]
    pred = np.zeros(len(scores))
    pred[top_idx] = 1
    return precision_score(y_true, pred, zero_division=0)

baselines = {}

# 1. Random
baselines['Random'] = baseline_rate
print(f"│ Random baseline                      │       {baseline_rate:.4f} │         1.0x │")

# 2. Top spenders (raw total_paid)
tp_scores = holdout['total_paid'].fillna(0).values
tp_prec = baseline_prec(tp_scores, y_holdout)
baselines['Top spenders (raw)'] = tp_prec
print(f"│ Top 5% by total paid                 │       {tp_prec:.4f} │       {tp_prec/max(baseline_rate,1e-8):.1f}x │")

# 3. Top claims/month (raw)
cpm_scores = holdout['claims_per_month'].fillna(0).values
cpm_prec = baseline_prec(cpm_scores, y_holdout)
baselines['Top claims/month'] = cpm_prec
print(f"│ Top 5% by claims/month               │       {cpm_prec:.4f} │       {cpm_prec/max(baseline_rate,1e-8):.1f}x │")

# 4. ★ SPECIALTY-ADJUSTED spending baseline (critical benchmark)
# Flag providers in top 5% of total_paid within their specialty-state peer group
holdout_copy = holdout.copy()
holdout_copy['pctile_in_peer'] = holdout_copy.groupby(['specialty', 'state'])['total_paid'].rank(pct=True)
spec_adj_pred = (holdout_copy['pctile_in_peer'] >= 0.95).astype(int).values
spec_adj_prec = precision_score(y_holdout, spec_adj_pred, zero_division=0)
baselines['Specialty-adjusted spending'] = spec_adj_prec
print(f"│ ★ Top 5% spending (specialty-adj.)   │       {spec_adj_prec:.4f} │       {spec_adj_prec/max(baseline_rate,1e-8):.1f}x │")

# 5. Single-feature threshold (best z-score)
z_feat = 'z_cpm'
if z_feat in holdout.columns:
    z_scores = holdout[z_feat].fillna(0).values
    z_prec = baseline_prec(z_scores, y_holdout)
    baselines[f'Top 5% by {z_feat}'] = z_prec
    print(f"│ Top 5% by z_claims_per_month         │       {z_prec:.4f} │       {z_prec/max(baseline_rate,1e-8):.1f}x │")

print("├──────────────────────────────────────┼─────────────┼──────────────┤")

# ML classifiers
for name in classifiers:
    if name in holdout_results:
        ml_prec = holdout_results[name]['prec_top5']
        baselines[name] = ml_prec
        print(f"│ {name:<36} │       {ml_prec:.4f} │       {ml_prec/max(baseline_rate,1e-8):.1f}x │")

print("└──────────────────────────────────────┴─────────────┴──────────────┘")

# ═══════════════════════════════════════════════════════════════════════
# STEP 5: SHAP on final RF model
# ═══════════════════════════════════════════════════════════════════════
log("═══ STEP 5: SHAP analysis (RF) ═══")

import shap

# Train final RF on all during-period data
rf_final = RandomForestClassifier(
    n_estimators=200, max_depth=12, min_samples_leaf=5,
    class_weight='balanced', random_state=42, n_jobs=-1
)
rf_final.fit(X_train_all, y_train_all)

log("  Computing SHAP values...")
rng_shap = np.random.RandomState(42)
shap_idx = rng_shap.choice(len(X_train_all), size=min(2000, len(X_train_all)), replace=False)
X_shap = X_train_all[shap_idx]

explainer = shap.TreeExplainer(rf_final)
shap_values = explainer.shap_values(X_shap)
if isinstance(shap_values, list):
    shap_vals = shap_values[1]
elif shap_values.ndim == 3:
    shap_vals = shap_values[:, :, 1]
else:
    shap_vals = shap_values

mean_abs_shap = np.abs(shap_vals).mean(axis=0)
feature_importance = sorted(zip(feature_names, mean_abs_shap.tolist()), key=lambda x: -x[1])

mean_shap_signed = shap_vals.mean(axis=0)
directions = {fn: "Higher->Fraud" if ms > 0 else "Lower->Fraud"
              for fn, ms in zip(feature_names, mean_shap_signed)}

log("═══ TABLE 7: SHAP Feature Importance ═══")
print("\n┌──────────────────────────────────────────────────────────────────────┐")
print("│         TABLE 7: Top Features (SHAP, Fraud-Only Labels)             │")
print("├──────┬──────────────────────────────────┬──────────┬─────────────────┤")
print("│ Rank │ Feature                          │ Mean|SHAP│ Direction       │")
print("├──────┼──────────────────────────────────┼──────────┼─────────────────┤")

table7_data = []
for i, (fn, importance) in enumerate(feature_importance[:15]):
    direction = directions[fn]
    print(f"│ {i+1:>4} │ {fn:<32} │ {importance:>8.4f} │ {direction:<15} │")
    table7_data.append({"rank": i+1, "feature": fn,
                        "mean_abs_shap": float(importance), "direction": direction})

print("└──────┴──────────────────────────────────┴──────────┴─────────────────┘")

# Key validation: check direction reversal from all-type to fraud-only
n_higher = sum(1 for t in table7_data if t['direction'] == 'Higher->Fraud')
n_lower = sum(1 for t in table7_data if t['direction'] == 'Lower->Fraud')
log(f"  Direction summary (top 15): {n_higher} Higher->Fraud, {n_lower} Lower->Fraud")
if n_higher > n_lower:
    log("  ✓ Majority Higher->Fraud (label contamination resolved)")
else:
    log("  ⚠ Majority Lower->Fraud (investigate further)")

# ═══════════════════════════════════════════════════════════════════════
# STEP 6: Label leakage diagnostic test
# ═══════════════════════════════════════════════════════════════════════
log("═══ STEP 6: Label leakage diagnostic ═══")

# Add diagnostic features (NEVER for actual prediction)
diag_df = train_all.copy()
# months_active is already a feature, use it as proxy for total_months_active
# For excluded: compute months_since_exclusion relative to a reference date
diag_df['months_since_exclusion'] = 0.0
mask = diag_df['is_fraud_excluded']
if mask.sum() > 0:
    ref_date = pd.Timestamp('2025-01-01')
    diag_df.loc[mask, 'months_since_exclusion'] = (
        (ref_date - pd.to_datetime(diag_df.loc[mask, 'exclusion_date'])).dt.days / 30.44
    )

diag_features = feature_names + ['months_since_exclusion']
X_diag = diag_df[diag_features].fillna(0).values
y_diag = diag_df['is_fraud_excluded'].astype(int).values

rf_diag = RandomForestClassifier(
    n_estimators=200, max_depth=12, min_samples_leaf=5,
    class_weight='balanced', random_state=42, n_jobs=-1
)
rf_diag.fit(X_diag, y_diag)

# Check feature importance of diagnostic feature
diag_importances = rf_diag.feature_importances_
diag_feat_imp = sorted(zip(diag_features, diag_importances.tolist()), key=lambda x: -x[1])

# Find rank of months_since_exclusion
mse_rank = next(i+1 for i, (fn, _) in enumerate(diag_feat_imp) if fn == 'months_since_exclusion')
mse_imp = next(imp for fn, imp in diag_feat_imp if fn == 'months_since_exclusion')
ma_rank = next(i+1 for i, (fn, _) in enumerate(diag_feat_imp) if fn == 'months_active')
ma_imp = next(imp for fn, imp in diag_feat_imp if fn == 'months_active')

print(f"\n  Label Leakage Diagnostic:")
print(f"    months_since_exclusion: rank {mse_rank}/{len(diag_features)}, importance = {mse_imp:.4f}")
print(f"    months_active:          rank {ma_rank}/{len(diag_features)}, importance = {ma_imp:.4f}")

if mse_rank <= 3:
    log("  ⚠ months_since_exclusion in top 3 — temporal leakage concern")
else:
    log("  ✓ months_since_exclusion not dominant — no temporal leakage detected")

if ma_rank <= 3:
    log("  ⚠ months_active in top 3 — possible selection bias (shorter billing → exclusion)")
else:
    log("  ✓ months_active not dominant — no obvious selection bias")

leakage_results = {
    'months_since_exclusion': {'rank': mse_rank, 'importance': mse_imp},
    'months_active': {'rank': ma_rank, 'importance': ma_imp},
    'top_5': [(fn, float(imp)) for fn, imp in diag_feat_imp[:5]],
    'passed': mse_rank > 3 and ma_rank > 3,
}

# ═══════════════════════════════════════════════════════════════════════
# STEP 7: Placebo test (S&I non-fraud labels)
# ═══════════════════════════════════════════════════════════════════════
log("═══ STEP 7: Placebo test ═══")

con2 = duckdb.connect()
si_npis = con2.sql(r"""
    SELECT DISTINCT unnest(regexp_extract_all("Provider Number", '(\d{10})')) as npi
    FROM read_csv('/tmp/mcaid/raw/provider-suspended-and-ineligible-list-s-i-list.csv',
         auto_detect=true, ignore_errors=true, all_varchar=true)
    WHERE "Provider Number" IS NOT NULL
""").fetchdf()['npi'].tolist()
con2.close()

df['is_si_only'] = df['billing_npi'].isin(si_npis) & ~df['is_fraud_excluded']
si_df = df[df['is_si_only'] | df['temporal_category'] == 'non_excluded'].copy()
si_df['placebo_label'] = si_df['is_si_only'].astype(int)

n_si = si_df['placebo_label'].sum()
log(f"  S&I non-fraud providers (placebo positives): {n_si}")

if n_si > 20:
    rng_placebo = np.random.RandomState(42)
    si_pos = si_df[si_df['placebo_label'] == 1]
    si_neg = si_df[si_df['placebo_label'] == 0].sample(
        n=min(n_si*RATIO, len(si_df[si_df['placebo_label']==0])), random_state=42)
    si_test = pd.concat([si_pos, si_neg])

    X_si = si_test[feature_names].fillna(0).values
    y_si = si_test['placebo_label'].values

    rf_placebo = RandomForestClassifier(
        n_estimators=200, max_depth=12, min_samples_leaf=5,
        class_weight='balanced', random_state=42, n_jobs=-1
    )

    from sklearn.model_selection import train_test_split
    X_si_tr, X_si_te, y_si_tr, y_si_te = train_test_split(
        X_si, y_si, test_size=0.2, stratify=y_si, random_state=42)
    rf_placebo.fit(X_si_tr, y_si_tr)
    y_si_score = rf_placebo.predict_proba(X_si_te)[:, 1]
    placebo_auc = roc_auc_score(y_si_te, y_si_score) if y_si_te.sum() > 0 else 0

    print(f"\n  Placebo AUC-ROC (S&I non-fraud labels): {placebo_auc:.3f}")
    print(f"  Interpretation: {'Features are fraud-SPECIFIC ✓' if placebo_auc < 0.60 else 'Features detect general exclusion risk ⚠'}")
else:
    placebo_auc = None
    log("  Not enough S&I providers for placebo test")

# ═══════════════════════════════════════════════════════════════════════
# FIGURES
# ═══════════════════════════════════════════════════════════════════════
log("═══ Generating figures ═══")

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# Figure 3: PR + ROC curves (3 models + baselines)
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

ax1 = axes[0]
for name in classifiers:
    if name in holdout_scores:
        prec_c, rec_c, _ = precision_recall_curve(y_holdout, holdout_scores[name])
        pr_auc = holdout_results[name]['pr_auc']
        ax1.plot(rec_c, prec_c, linewidth=2, label=f'{name} (PR-AUC={pr_auc:.3f})')
ax1.axhline(y=baseline_rate, color='k', linestyle='--', alpha=0.5, label=f'Random ({baseline_rate:.4f})')
ax1.set_xlabel('Recall', fontsize=16)
ax1.set_ylabel('Precision', fontsize=16)
ax1.set_title('Precision-Recall (Holdout 2025+)', fontsize=17)
ax1.legend(fontsize=13)
ax1.grid(True, alpha=0.3)

ax2 = axes[1]
for name in classifiers:
    if name in holdout_scores:
        fpr_c, tpr_c, _ = roc_curve(y_holdout, holdout_scores[name])
        auc = holdout_results[name]['auc_roc']
        ax2.plot(fpr_c, tpr_c, linewidth=2, label=f'{name} (AUC={auc:.3f})')
ax2.plot([0, 1], [0, 1], 'k--', alpha=0.5, label='Random')
ax2.set_xlabel('False Positive Rate', fontsize=16)
ax2.set_ylabel('True Positive Rate', fontsize=16)
ax2.set_title('ROC Curve (Holdout 2025+)', fontsize=17)
ax2.legend(fontsize=13)
ax2.grid(True, alpha=0.3)

plt.tight_layout()
fig.savefig(f'{FRAUD}/figure3_pr_roc.png', dpi=300, bbox_inches='tight')
plt.close()
log(f"  Saved figure3_pr_roc.png")

# Figure 4: SHAP bar plot with directions
fig, ax = plt.subplots(figsize=(10, 8))
top_n = 15
top_feats = feature_importance[:top_n]
names = [f[0] for f in top_feats][::-1]
vals = [f[1] for f in top_feats][::-1]
colors = ['#D4652F' if directions[n] == 'Higher->Fraud' else '#008080' for n in names]
ax.barh(range(len(names)), vals, color=colors)
ax.set_yticks(range(len(names)))
ax.set_yticklabels(names, fontsize=10)
ax.set_xlabel('Mean |SHAP value|', fontsize=12)
ax.set_title('SHAP Feature Importance (Fraud-Only Labels, RF)', fontsize=13)

from matplotlib.patches import Patch
legend_elements = [Patch(facecolor='#D4652F', label='Higher → Predicts Fraud'),
                   Patch(facecolor='#008080', label='Lower → Predicts Fraud')]
ax.legend(handles=legend_elements, fontsize=10)
ax.grid(True, alpha=0.3, axis='x')

plt.tight_layout()
fig.savefig(f'{FRAUD}/figure4_shap_fraud.png', dpi=150, bbox_inches='tight')
plt.close()
log(f"  Saved figure4_shap_fraud.png")

# ═══════════════════════════════════════════════════════════════════════
# Save all results
# ═══════════════════════════════════════════════════════════════════════
results = {
    "table4_cv": table4,
    "table5_holdout": {k: {kk: float(vv) if isinstance(vv, (np.floating, float)) else vv
                           for kk, vv in v.items()} for k, v in holdout_results.items()},
    "table6_baselines": {k: float(v) for k, v in baselines.items()},
    "table7_shap": table7_data,
    "leakage_test": leakage_results,
    "placebo_auc": float(placebo_auc) if placebo_auc is not None else None,
    "n_during_period": len(fraud_during),
    "n_holdout": len(fraud_post),
    "n_features": len(feature_names),
    "feature_names": feature_names,
}
with open(f"{FRAUD}/phase3_results.json", "w") as f:
    json.dump(results, f, indent=2, default=str)
log(f"  Saved phase3_results.json")

np.savez_compressed(f"{FRAUD}/phase3_shap.npz",
                    shap_values=shap_vals,
                    feature_names=np.array(feature_names),
                    X_shap=X_shap)
log(f"  Saved phase3_shap.npz")

log("Phase 3 v2 classification complete.")
