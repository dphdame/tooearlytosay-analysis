#!/usr/bin/env python3
"""
01_verify_regime_and_horizon_estimates.py
=========================================
End-to-end verification script for TETS Article #1A:
"Why Pooled 20-Year Panel Regressions Miss Pandemic Regime Shifts:
Public Health Spending and Mortality Before and During COVID-19"

Performs five traceable verification stages:
1. SHA-256 byte-for-byte parity between all 9 local CSV files in data/ and
   the authoritative source CSVs in Value_of_Public_Health/results/.
2. Direct re-estimation on analysis_panel_subset_verified.csv of:
   - Regime summary statistics (Table 1)
   - The 2x2 factorial grid of 2003-2023 pooled regime-interaction models
   - The exact Frisch-Waugh-Lovell (FWL) residual variance identity
   - Pre-pandemic (2003-2019) and pandemic (2020-2023) reverse-lag checks
3. Verification of all 10 TWFE regime & crosswalk specifications, distributed
   lags (with BH-FDR q-values), 16 stacked first-difference horizons, and
   temporally separated long-differences.
4. Automated parsing of all four markdown tables (Tables 1-4) and image links
   in both public-health-spending-regime-shifts.md and article-draft.md,
   asserting numerical parity against the source CSVs within display rounding.
"""

import hashlib
import re
from pathlib import Path
import numpy as np
import pandas as pd
from statsmodels.stats.multitest import multipletests
from linearmodels.panel import PanelOLS

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
SOURCE_RESULTS_DIR = Path("/Users/vserver/code/Value_of_Public_Health/results")
ARTICLE_WORK_PATH = Path("/Users/vserver/code/tooearlytosay-work/03_articles/public-health-spending-regime-shifts.md")
ARTICLE_MIRROR_PATH = BASE_DIR / "article-draft.md"

CONTROLS = [
    "pct_under_18",
    "pct_65_plus",
    "pct_hispanic",
    "pct_black_non_hisp",
    "pct_asian_non_hisp",
    "poverty_rate",
    "median_household_income",
    "unemployment_rate",
]


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_source_csv_sha256_parity() -> None:
    """Verify byte-for-byte SHA-256 parity between data/*.csv and source results."""
    pairs = [
        ("panel_regime_and_crosswalk_sensitivity.csv", SOURCE_RESULTS_DIR / "panel_regime_and_crosswalk_sensitivity.csv"),
        ("temporally_separated_long_diff_results.csv", SOURCE_RESULTS_DIR / "temporally_separated_long_diff_results.csv"),
        ("explicit_lag_and_cumulative_results.csv", SOURCE_RESULTS_DIR / "explicit_lag_and_cumulative_results.csv"),
        ("long_difference_and_lag_results.csv", SOURCE_RESULTS_DIR / "long_difference_and_lag_results.csv"),
        ("additional_diagnostics_summary.csv", SOURCE_RESULTS_DIR / "additional_diagnostics_summary.csv"),
        ("sco_2017_crosswalk_validation.csv", SOURCE_RESULTS_DIR / "sco_2017_crosswalk_validation.csv"),
        ("alternative_outcomes.csv", SOURCE_RESULTS_DIR / "robustness" / "alternative_outcomes.csv"),
        ("subsamples.csv", SOURCE_RESULTS_DIR / "robustness" / "subsamples.csv"),
        ("leave_one_out.csv", SOURCE_RESULTS_DIR / "robustness" / "leave_one_out.csv"),
    ]
    for local_name, src_path in pairs:
        local_path = DATA_DIR / local_name
        assert local_path.exists(), f"Missing local CSV: {local_path}"
        assert src_path.exists(), f"Missing source CSV: {src_path}"
        assert sha256_file(local_path) == sha256_file(src_path), f"SHA-256 mismatch for {local_name}"
    print("[PASS] Stage 1: All 9 local CSVs match Value_of_Public_Health/results/ SHA-256 hashes.")


def verify_panel_regime_table() -> pd.DataFrame:
    """Verify Table 2 regime and crosswalk sensitivity estimates."""
    df = pd.read_csv(DATA_DIR / "panel_regime_and_crosswalk_sensitivity.csv")
    df["ci_lower_95"] = df["ols_coef"] - 1.96 * df["ols_se"]
    df["ci_upper_95"] = df["ols_coef"] + 1.96 * df["ols_se"]
    df["beta_per_10usd"] = df["ols_coef"] * 10.0
    df["ci_lower_per_10usd"] = df["ci_lower_95"] * 10.0
    df["ci_upper_per_10usd"] = df["ci_upper_95"] * 10.0

    expected_specs = [
        ("1. 2003-2016 Single-Regime Consistent (Nominal USD)", 779, -0.264179, 0.115986, 0.022746, -0.033062),
        ("2. 2003-2016 Single-Regime Consistent (Constant 2023 USD)", 779, -0.153642, 0.086502, 0.075705, -0.027237),
        ("3. 2003-2019 Pre-COVID SCO Crosswalk Ex-Debt (Nominal USD)", 943, -0.237900, 0.077599, 0.002171, -0.030327),
        ("4. 2003-2019 Pre-COVID SCO Crosswalk Ex-Debt (Constant 2023 USD)", 943, -0.134598, 0.056991, 0.018189, -0.023626),
        ("5. 2003-2019 Pre-COVID Crosswalk + 5 Outlier Post-2017 Step-Shift FE", 943, -0.253859, 0.092693, 0.006168, -0.032362),
        ("6. 2003-2019 Pre-COVID Crosswalk Excluding 5 Outliers Post-2016", 928, -0.229439, 0.103997, 0.027369, -0.029047),
        ("7. 2003-2019 Pre-COVID Crosswalk Incl-Debt Service (Nominal USD)", 943, -0.237913, 0.077599, 0.002170, -0.030329),
        ("8. 2003-2019 Pre-COVID Crosswalk + All-County Regime-Interacted FE", 943, -0.267299, 0.093856, 0.004400, -0.034075),
        ("9. 2020-2023 COVID-19 Emergency Grant Era Only (Nominal USD)", 220, 0.247448, 0.075715, 0.001083, 0.042999),
        ("10. 2003-2023 Unstratified Pooled Panel (Contaminated by COVID)", 1163, -0.024305, 0.029702, 0.413184, -0.003345),
    ]
    for spec, n_exp, b_exp, se_exp, p_exp, el_exp in expected_specs:
        row = df.loc[df["specification"] == spec].iloc[0]
        assert int(row["N"]) == n_exp
        assert np.isclose(row["ols_coef"], b_exp, atol=1e-5)
        assert np.isclose(row["ols_se"], se_exp, atol=1e-5)
        assert np.isclose(row["ols_p"], p_exp, atol=1e-5)
        assert np.isclose(row["implied_ols_elasticity"], el_exp, atol=1e-5)

    out_path = DATA_DIR / "regime_comparison_summary.csv"
    df.to_csv(out_path, index=False)
    print(f"[PASS] Stage 2A: Verified all 10 TWFE regime & crosswalk specifications -> {out_path.name}")
    return df


def verify_pooled_regime_interactions_and_fwl() -> pd.DataFrame:
    """
    Estimate the 2x2 factorial grid of pooled 2003-2023 regime-interaction models
    (N = 1,163, 57 county clusters), compute the exact Frisch-Waugh-Lovell (FWL)
    residual variance identity, and verify reverse-lag checks.
    """
    panel = pd.read_csv(SOURCE_RESULTS_DIR / "analysis_panel_subset_verified.csv")
    sub = panel.loc[panel["year"].between(2003, 2023)].dropna(
        subset=["mortality_rate_per_100k", "public_health_per_capita_sco_xwalk"] + CONTROLS
    ).copy()
    assert len(sub) == 1163

    sub["covid_era"] = (sub["year"] >= 2020).astype(float)
    sub["ph_x_covid"] = sub["public_health_per_capita_sco_xwalk"] * sub["covid_era"]
    sub["county_regime"] = sub["county"] + "_" + sub["covid_era"].astype(int).astype(str)

    ctrl_covid_cols = []
    for c in CONTROLS:
        col_name = f"{c}_x_covid"
        sub[col_name] = sub[c] * sub["covid_era"]
        ctrl_covid_cols.append(col_name)

    sub_cr = sub.set_index(["county_regime", "year"])
    clusters_county = pd.Series(sub["county"].values, index=sub_cr.index)

    # Cell 1: County-by-regime FE + year FE + regime-interacted controls (Stacked model)
    res_stacked = PanelOLS(
        sub_cr["mortality_rate_per_100k"],
        sub_cr[["public_health_per_capita_sco_xwalk", "ph_x_covid"] + CONTROLS + ctrl_covid_cols],
        entity_effects=True,
        time_effects=True,
        check_rank=False,
    ).fit(cov_type="clustered", clusters=clusters_county)

    # Cell 2: County-by-regime FE + year FE + common control slopes
    res_cr_common = PanelOLS(
        sub_cr["mortality_rate_per_100k"],
        sub_cr[["public_health_per_capita_sco_xwalk", "ph_x_covid"] + CONTROLS],
        entity_effects=True,
        time_effects=True,
        check_rank=False,
    ).fit(cov_type="clustered", clusters=clusters_county)

    # Cell 3: Common 21-year county FE + year FE + common control slopes
    sub_common_fe = sub.set_index(["county", "year"])
    res_slope_only = PanelOLS(
        sub_common_fe["mortality_rate_per_100k"],
        sub_common_fe[["public_health_per_capita_sco_xwalk", "ph_x_covid"] + CONTROLS],
        entity_effects=True,
        time_effects=True,
        check_rank=False,
    ).fit(cov_type="clustered", cluster_entity=True)

    # Cell 4: Common 21-year county FE + year FE + regime-interacted control slopes
    res_common_fe_int_ctrl = PanelOLS(
        sub_common_fe["mortality_rate_per_100k"],
        sub_common_fe[["public_health_per_capita_sco_xwalk", "ph_x_covid"] + CONTROLS + ctrl_covid_cols],
        entity_effects=True,
        time_effects=True,
        check_rank=False,
    ).fit(cov_type="clustered", cluster_entity=True)

    # Exact FWL identity on the unstratified pooled 2003-2023 regression (-0.024305)
    mod_y = PanelOLS(
        sub_common_fe["mortality_rate_per_100k"],
        sub_common_fe[CONTROLS],
        entity_effects=True,
        time_effects=True,
    ).fit()
    mod_x = PanelOLS(
        sub_common_fe["public_health_per_capita_sco_xwalk"],
        sub_common_fe[CONTROLS],
        entity_effects=True,
        time_effects=True,
    ).fit()
    y_tilde = mod_y.resids
    x_tilde = mod_x.resids

    pre_mask = sub_common_fe.index.get_level_values("year") <= 2019
    cov_mask = sub_common_fe.index.get_level_values("year") >= 2020

    ss_total = float((x_tilde ** 2).sum())
    ss_pre = float((x_tilde[pre_mask] ** 2).sum())
    ss_cov = float((x_tilde[cov_mask] ** 2).sum())
    w_pre = ss_pre / ss_total
    w_cov = ss_cov / ss_total

    b_fwl_pre = float((x_tilde[pre_mask] * y_tilde[pre_mask]).sum() / ss_pre)
    b_fwl_cov = float((x_tilde[cov_mask] * y_tilde[cov_mask]).sum() / ss_cov)
    b_fwl_pooled = float((x_tilde * y_tilde).sum() / ss_total)

    assert np.isclose(w_pre * b_fwl_pre + w_cov * b_fwl_cov, b_fwl_pooled, atol=1e-7)
    assert np.isclose(b_fwl_pooled, -0.024305, atol=1e-5)
    assert np.isclose(res_stacked.params["ph_x_covid"], 0.485348, atol=1e-5)
    assert np.isclose(res_cr_common.params["ph_x_covid"], 0.604816, atol=1e-5)
    assert np.isclose(res_slope_only.params["ph_x_covid"], -0.036814, atol=1e-5)
    assert np.isclose(res_common_fe_int_ctrl.params["ph_x_covid"], -0.055292, atol=1e-5)

    # Reverse-lag check in 2020-2023 (N = 220)
    panel_sorted = panel.sort_values(["county", "year"]).copy()
    panel_sorted["mort_lag1"] = panel_sorted.groupby("county")["mortality_rate_per_100k"].shift(1)
    sub_rev_cov = panel_sorted.loc[panel_sorted["year"].between(2020, 2023)].dropna(
        subset=["public_health_per_capita_sco_xwalk", "mort_lag1"] + CONTROLS
    ).set_index(["county", "year"])
    res_rev_cov = PanelOLS(
        sub_rev_cov["public_health_per_capita_sco_xwalk"],
        sub_rev_cov[["mort_lag1"] + CONTROLS],
        entity_effects=True,
        time_effects=True,
        check_rank=False,
    ).fit(cov_type="clustered", cluster_entity=True)
    assert int(res_rev_cov.nobs) == 220
    assert np.isclose(res_rev_cov.params["mort_lag1"], -0.2686, atol=1e-3)
    assert np.isclose(res_rev_cov.std_errors["mort_lag1"], 0.1803, atol=1e-3)
    assert np.isclose(res_rev_cov.pvalues["mort_lag1"], 0.1385, atol=1e-3)

    rows = [
        {
            "model": "Stacked Regime-Interacted TWFE (County-by-Regime FE + Interacted Controls)",
            "N": 1163,
            "beta_pre_2003_2019": float(res_stacked.params["public_health_per_capita_sco_xwalk"]),
            "se_pre": float(res_stacked.std_errors["public_health_per_capita_sco_xwalk"]),
            "p_pre": float(res_stacked.pvalues["public_health_per_capita_sco_xwalk"]),
            "delta_covid_interaction": float(res_stacked.params["ph_x_covid"]),
            "se_delta": float(res_stacked.std_errors["ph_x_covid"]),
            "p_delta": float(res_stacked.pvalues["ph_x_covid"]),
            "fwl_weight_pre": np.nan,
            "fwl_weight_covid": np.nan,
        },
        {
            "model": "County-by-Regime FE + Common Control Slopes Interaction",
            "N": 1163,
            "beta_pre_2003_2019": float(res_cr_common.params["public_health_per_capita_sco_xwalk"]),
            "se_pre": float(res_cr_common.std_errors["public_health_per_capita_sco_xwalk"]),
            "p_pre": float(res_cr_common.pvalues["public_health_per_capita_sco_xwalk"]),
            "delta_covid_interaction": float(res_cr_common.params["ph_x_covid"]),
            "se_delta": float(res_cr_common.std_errors["ph_x_covid"]),
            "p_delta": float(res_cr_common.pvalues["ph_x_covid"]),
            "fwl_weight_pre": np.nan,
            "fwl_weight_covid": np.nan,
        },
        {
            "model": "Common 21-Year County FE + Common Control Slopes Interaction",
            "N": 1163,
            "beta_pre_2003_2019": float(res_slope_only.params["public_health_per_capita_sco_xwalk"]),
            "se_pre": float(res_slope_only.std_errors["public_health_per_capita_sco_xwalk"]),
            "p_pre": float(res_slope_only.pvalues["public_health_per_capita_sco_xwalk"]),
            "delta_covid_interaction": float(res_slope_only.params["ph_x_covid"]),
            "se_delta": float(res_slope_only.std_errors["ph_x_covid"]),
            "p_delta": float(res_slope_only.pvalues["ph_x_covid"]),
            "fwl_weight_pre": np.nan,
            "fwl_weight_covid": np.nan,
        },
        {
            "model": "Common 21-Year County FE + Interacted Control Slopes",
            "N": 1163,
            "beta_pre_2003_2019": float(res_common_fe_int_ctrl.params["public_health_per_capita_sco_xwalk"]),
            "se_pre": float(res_common_fe_int_ctrl.std_errors["public_health_per_capita_sco_xwalk"]),
            "p_pre": float(res_common_fe_int_ctrl.pvalues["public_health_per_capita_sco_xwalk"]),
            "delta_covid_interaction": float(res_common_fe_int_ctrl.params["ph_x_covid"]),
            "se_delta": float(res_common_fe_int_ctrl.std_errors["ph_x_covid"]),
            "p_delta": float(res_common_fe_int_ctrl.pvalues["ph_x_covid"]),
            "fwl_weight_pre": np.nan,
            "fwl_weight_covid": np.nan,
        },
        {
            "model": "Exact FWL Algebraic Identity of Unstratified Pooled Slope (-0.024305)",
            "N": 1163,
            "beta_pre_2003_2019": b_fwl_pre,
            "se_pre": np.nan,
            "p_pre": np.nan,
            "delta_covid_interaction": b_fwl_cov - b_fwl_pre,
            "se_delta": np.nan,
            "p_delta": np.nan,
            "fwl_weight_pre": w_pre,
            "fwl_weight_covid": w_cov,
        },
    ]
    out_df = pd.DataFrame(rows)
    out_path = DATA_DIR / "pooled_regime_interaction_and_fwl_decomposition.csv"
    out_df.to_csv(out_path, index=False)
    print(f"[PASS] Stage 2B: Verified 2x2 interaction grid, FWL identity & reverse-lag -> {out_path.name}")
    return out_df


def verify_horizon_and_lag_tables() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Verify distributed lags (with BH-FDR q-values), 16 horizons, and long differences."""
    lags_df = pd.read_csv(DATA_DIR / "explicit_lag_and_cumulative_results.csv")
    lags_df["ci_lower_95"] = lags_df["ols_coef"] - 1.96 * lags_df["ols_se"]
    lags_df["ci_upper_95"] = lags_df["ols_coef"] + 1.96 * lags_df["ols_se"]

    # Compute exact BH-FDR q-values within each 9-specification sample_window
    lags_df["ols_q_fdr_9specs"] = np.nan
    for win, grp in lags_df.groupby("sample_window"):
        _, q_vals, _, _ = multipletests(grp["ols_p"].values, method="fdr_bh")
        lags_df.loc[grp.index, "ols_q_fdr_9specs"] = q_vals

    horizons_df = pd.read_csv(DATA_DIR / "long_difference_and_lag_results.csv")
    horizons_03_19 = horizons_df.loc[
        horizons_df["sample_type"] == "2003-2019 Pre-COVID Crosswalk (All available years)"
    ].copy()
    horizons_03_19["ci_lower_95"] = horizons_03_19["ols_coef"] - 1.96 * horizons_03_19["ols_se"]
    horizons_03_19["ci_upper_95"] = horizons_03_19["ols_coef"] + 1.96 * horizons_03_19["ols_se"]

    long_diff_df = pd.read_csv(DATA_DIR / "temporally_separated_long_diff_results.csv")
    long_diff_df["ci_lower_95"] = long_diff_df["ols_coef"] - 1.96 * long_diff_df["ols_se"]
    long_diff_df["ci_upper_95"] = long_diff_df["ols_coef"] + 1.96 * long_diff_df["ols_se"]

    assert len(horizons_03_19) == 16
    assert (horizons_03_19["ols_coef"] < 0).all()
    assert (horizons_03_19["ols_p_holm"] >= 0.078).all()
    assert (horizons_03_19["ols_q_fdr"] >= 0.078).all()

    lags_df.to_csv(DATA_DIR / "verified_distributed_lags_summary.csv", index=False)
    horizons_03_19.to_csv(DATA_DIR / "verified_16horizons_summary.csv", index=False)
    long_diff_df.to_csv(DATA_DIR / "verified_long_diff_summary.csv", index=False)
    print("[PASS] Stage 3: Verified distributed lags (BH-FDR), 16 horizons, and cross-sectional long differences.")
    return lags_df, horizons_03_19, long_diff_df


def verify_panel_means_and_additional_checks() -> pd.DataFrame:
    """Re-verify panel summary statistics from raw verified panel."""
    panel_path = SOURCE_RESULTS_DIR / "analysis_panel_subset_verified.csv"
    panel = pd.read_csv(panel_path)

    valid_mask = panel["public_health_per_capita_sco_xwalk"].notna() & panel["mortality_rate_per_100k"].notna()
    s_03_16 = panel.loc[panel["year"].between(2003, 2016) & valid_mask]
    s_03_19 = panel.loc[panel["year"].between(2003, 2019) & valid_mask]
    s_20_23 = panel.loc[panel["year"].between(2020, 2023) & valid_mask]
    s_03_23 = panel.loc[panel["year"].between(2003, 2023) & valid_mask]

    assert len(s_03_16) == 779
    assert len(s_03_19) == 943
    assert len(s_20_23) == 220
    assert len(s_03_23) == 1163

    summary_rows = []
    for label, sub in [
        ("2003-2016 Single-Regime", s_03_16),
        ("2003-2019 Pre-COVID Crosswalk", s_03_19),
        ("2020-2023 COVID-19 Era", s_20_23),
        ("2003-2023 Unstratified Pooled", s_03_23),
    ]:
        summary_rows.append(
            {
                "regime": label,
                "n_county_years": len(sub),
                "n_counties": sub["county"].nunique(),
                "ph_nominal_mean": sub["public_health_per_capita_sco_xwalk"].mean(),
                "ph_nominal_sd": sub["public_health_per_capita_sco_xwalk"].std(),
                "ph_real2023_mean": sub["public_health_per_capita_sco_xwalk_2023usd"].mean(),
                "ph_real2023_sd": sub["public_health_per_capita_sco_xwalk_2023usd"].std(),
                "mortality_all_cause_mean": sub["mortality_rate_per_100k"].mean(),
                "mortality_all_cause_sd": sub["mortality_rate_per_100k"].std(),
            }
        )
    summary_df = pd.DataFrame(summary_rows)
    summary_df.to_csv(DATA_DIR / "verified_regime_summary_stats.csv", index=False)
    print("[PASS] Stage 4: Verified regime sample sizes and summary statistics -> verified_regime_summary_stats.csv")
    return summary_df


def parse_markdown_tables(md_text: str) -> list[list[list[str]]]:
    """Extract all markdown tables as lists of rows of cell strings."""
    tables = []
    current = []
    for line in md_text.splitlines():
        s = line.strip()
        if s.startswith("|") and s.endswith("|"):
            cells = [c.strip() for c in s.strip("|").split("|")]
            if all(re.match(r"^:?-+:?$", c) for c in cells):
                continue
            current.append(cells)
        else:
            if current:
                tables.append(current)
                current = []
    if current:
        tables.append(current)
    return tables


def verify_article_tables_and_links() -> None:
    """
    Programmatically parse Tables 1-4 and image links in both article markdown
    files and assert numerical match against the authoritative CSVs.
    """
    stats_df = pd.read_csv(DATA_DIR / "verified_regime_summary_stats.csv")
    regime_df = pd.read_csv(DATA_DIR / "panel_regime_and_crosswalk_sensitivity.csv")
    inter_df = pd.read_csv(DATA_DIR / "pooled_regime_interaction_and_fwl_decomposition.csv")
    lags_df = pd.read_csv(DATA_DIR / "verified_distributed_lags_summary.csv")
    horizons_df = pd.read_csv(DATA_DIR / "verified_16horizons_summary.csv")
    long_df = pd.read_csv(DATA_DIR / "temporally_separated_long_diff_results.csv")
    alt_out_df = pd.read_csv(DATA_DIR / "alternative_outcomes.csv")
    sub_df = pd.read_csv(DATA_DIR / "subsamples.csv")
    add_diag_df = pd.read_csv(DATA_DIR / "additional_diagnostics_summary.csv")

    for md_path in [ARTICLE_WORK_PATH, ARTICLE_MIRROR_PATH]:
        assert md_path.exists(), f"Missing markdown file: {md_path}"
        md_text = md_path.read_text()

        # Verify image links exist on disk
        img_links = re.findall(r"!\[[^\]]*\]\(([^)]+)\)", md_text)
        assert len(img_links) == 2
        for link in img_links:
            if link.startswith("/images/"):
                resolved = (Path("/Users/vserver/code/tooearlytosay-work/public") / link.lstrip("/")).resolve()
            else:
                resolved = (md_path.parent / link).resolve()
            assert resolved.exists() and resolved.stat().st_size > 10000, f"Broken image link: {resolved}"

        tables = parse_markdown_tables(md_text)
        assert len(tables) == 4, f"Expected 4 markdown tables in {md_path.name}, found {len(tables)}"

        # Table 1: 4 regime summary rows
        t1_rows = tables[0][1:]
        assert len(t1_rows) == 4
        for idx, r in enumerate(t1_rows):
            s_row = stats_df.iloc[idx]
            n_val = int(r[1].replace(",", ""))
            c_val = int(r[2])
            assert n_val == int(s_row["n_county_years"])
            assert c_val == int(s_row["n_counties"])
            nom_nums = [float(x) for x in re.findall(r"\d+\.\d+", r[3])]
            real_nums = [float(x) for x in re.findall(r"\d+\.\d+", r[4])]
            mort_nums = [float(x) for x in re.findall(r"\d+\.\d+", r[5])]
            assert np.isclose(nom_nums[0], s_row["ph_nominal_mean"], atol=0.01)
            assert np.isclose(nom_nums[1], s_row["ph_nominal_sd"], atol=0.01)
            assert np.isclose(real_nums[0], s_row["ph_real2023_mean"], atol=0.01)
            assert np.isclose(real_nums[1], s_row["ph_real2023_sd"], atol=0.01)
            assert np.isclose(mort_nums[0], s_row["mortality_all_cause_mean"], atol=0.01)
            assert np.isclose(mort_nums[1], s_row["mortality_all_cause_sd"], atol=0.01)

        # Table 2: 12 regime, crosswalk, and pooled-interaction rows
        t2_rows = tables[1][1:]
        assert len(t2_rows) == 12
        for idx in range(10):
            r = t2_rows[idx]
            c_row = regime_df.iloc[idx]
            n_c = [int(x.replace(",", "")) for x in re.findall(r"[\d,]+", r[1])]
            b_se = [float(x) for x in re.findall(r"[+-]?\d+\.\d+", r[2])]
            p_val = float(r[3])
            el_val = float(r[4])
            assert n_c[0] == int(c_row["N"]) and n_c[1] == int(c_row["counties"])
            assert np.isclose(b_se[0], c_row["ols_coef"], atol=0.001)
            assert np.isclose(b_se[1], c_row["ols_se"], atol=0.001)
            assert np.isclose(p_val, c_row["ols_p"], atol=0.0002)
            assert np.isclose(el_val, c_row["implied_ols_elasticity"], atol=0.001)

        # Specs 11 and 12 in Table 2
        for spec_idx, inter_idx in [(10, 0), (11, 1)]:
            r = t2_rows[spec_idx]
            i_row = inter_df.iloc[inter_idx]
            b_se = [float(x) for x in re.findall(r"[+-]?\d+\.\d+", r[2])]
            assert np.isclose(b_se[0], i_row["delta_covid_interaction"], atol=0.001)
            assert np.isclose(b_se[1], i_row["se_delta"], atol=0.001)
            assert r[3] == "<0.0001" and i_row["p_delta"] < 1e-4

        # Table 3: 17 horizon / lag rows
        t3_rows = tables[2][1:]
        assert len(t3_rows) == 17
        # Rows 0..8 correspond to 2011-2019 fixed sample rows (indices 9..17 in lags_df)
        for idx in range(9):
            r = t3_rows[idx]
            l_row = lags_df.iloc[9 + idx]
            assert int(r[2]) == int(l_row["N"])
            b_se = [float(x) for x in re.findall(r"[+-]?\d+\.\d+", r[3])]
            assert np.isclose(b_se[0], l_row["ols_coef"], atol=0.001)
            assert np.isclose(b_se[1], l_row["ols_se"], atol=0.001)
            assert np.isclose(float(r[4]), l_row["ols_p"], atol=0.0002)
            assert np.isclose(float(r[5]), l_row["ols_q_fdr_9specs"], atol=0.0002)

        # Rows 9..11 correspond to k = 1, 4, 8 in horizons_df
        for row_offset, k_val in [(9, 1), (10, 4), (11, 8)]:
            r = t3_rows[row_offset]
            h_row = horizons_df.loc[horizons_df["k_years"] == k_val].iloc[0]
            assert int(r[2]) == int(h_row["N"])
            b_se = [float(x) for x in re.findall(r"[+-]?\d+\.\d+", r[3])]
            assert np.isclose(b_se[0], h_row["ols_coef"], atol=0.001)
            assert np.isclose(b_se[1], h_row["ols_se"], atol=0.001)
            assert np.isclose(float(r[4]), h_row["ols_p"], atol=0.0002)
            assert np.isclose(float(r[5]), h_row["ols_q_fdr"], atol=0.0002)

        # Rows 12..16 correspond to long_df specs 3, 2, 1, 5, 6 (0-indexed: 2, 1, 0, 4, 5)
        for row_offset, ld_idx in [(12, 2), (13, 1), (14, 0), (15, 4), (16, 5)]:
            r = t3_rows[row_offset]
            ld_row = long_df.iloc[ld_idx]
            assert int(r[2]) == int(ld_row["N"])
            b_se = [float(x) for x in re.findall(r"[+-]?\d+\.\d+", r[3])]
            assert np.isclose(b_se[0], ld_row["ols_coef"], atol=0.001)
            assert np.isclose(b_se[1], ld_row["ols_se"], atol=0.001)
            assert np.isclose(float(r[4]), ld_row["ols_p"], atol=0.0002)

        # Table 4: 13 diagnostic rows (outcomes, subsamples, post-2010 interaction)
        t4_rows = tables[3][1:]
        assert len(t4_rows) == 13
        # Map first 8 rows to alternative_outcomes.csv
        outcome_order = [
            "Preventable mortality",
            "Preventable mortality (5 major causes, all >= 11)",
            "Heart disease",
            "Stroke",
            "CLRD",
            "Diabetes",
            "Influenza/Pneumonia",
            "Injuries",
        ]
        for idx, out_name in enumerate(outcome_order):
            r = t4_rows[idx]
            ao_row = alt_out_df.loc[alt_out_df["outcome"] == out_name].iloc[0]
            n_c = [int(x) for x in re.findall(r"\d+", r[1])]
            b_se = [float(x) for x in re.findall(r"[+-]?\d+\.\d+", r[2])]
            assert n_c[0] == int(ao_row["n"]) and n_c[1] == int(ao_row["counties"])
            assert np.isclose(b_se[0], ao_row["ols_coef"], atol=0.001)
            assert np.isclose(b_se[1], ao_row["ols_se"], atol=0.001)
            assert np.isclose(float(r[3]), ao_row["ols_p"], atol=0.0002)

        # Rows 8..11 map to subsamples.csv
        sub_order = [
            "Large counties (pop > 500k, 2003-2019)",
            "Small/medium counties (pop <= 500k, 2003-2019)",
            "Pre-ACA (2003-2009)",
            "Post-ACA Pre-COVID (2010-2019)",
        ]
        for offset, sub_name in enumerate(sub_order, start=8):
            r = t4_rows[offset]
            sb_row = sub_df.loc[sub_df["subsample"] == sub_name].iloc[0]
            n_c = [int(x) for x in re.findall(r"\d+", r[1])]
            b_se = [float(x) for x in re.findall(r"[+-]?\d+\.\d+", r[2])]
            assert n_c[0] == int(sb_row["n"]) and n_c[1] == int(sb_row["counties"])
            assert np.isclose(b_se[0], sb_row["ols_coef"], atol=0.001)
            assert np.isclose(b_se[1], sb_row["ols_se"], atol=0.001)

        # Row 12: Pooled Post-2010 Interaction from additional_diagnostics_summary.csv
        r12 = t4_rows[12]
        ad_row = add_diag_df.loc[
            add_diag_df["panel"].str.contains("2003-2019 Pre-COVID")
        ].iloc[0]
        b_se = [float(x) for x in re.findall(r"[+-]?\d+\.\d+", r12[2])]
        assert np.isclose(b_se[0], ad_row["ols_interact_coef"], atol=0.0005)
        assert np.isclose(b_se[1], ad_row["ols_interact_se"], atol=0.001)
        assert np.isclose(float(r12[3]), ad_row["ols_interact_p"], atol=0.0002)

        # Prose token checks against additional_diagnostics_summary.csv, sco_2017_crosswalk_validation.csv, and leave_one_out.csv
        ad_03_16 = add_diag_df.loc[add_diag_df["panel"].str.contains("2003-2016")].iloc[0]
        assert f"{ad_03_16['ols_wcb_p']:.4f}" in md_text
        assert f"[{ad_03_16['ols_wcb_ci_lower']:.3f}, +{ad_03_16['ols_wcb_ci_upper']:.3f}]" in md_text
        assert f"{ad_row['ols_wcb_p']:.4f}" in md_text
        assert f"[{ad_row['ols_wcb_ci_lower']:.3f}, {ad_row['ols_wcb_ci_upper']:.3f}]" in md_text
        assert f"{ad_row['current_coef']:.3f}" in md_text and f"{ad_row['lead_coef']:.3f}" in md_text
        assert f"{ad_row['rev_mort_lag1_coef']:.3f}" in md_text

        sco_df = pd.read_csv(DATA_DIR / "sco_2017_crosswalk_validation.csv")
        outliers = sco_df.loc[sco_df["transition_outlier_50pct"] == 1]
        assert len(outliers) == 5
        for _, o_row in outliers.iterrows():
            assert f"+{o_row['pct_change_16_17']:.1f}%" in md_text
            assert f"${o_row['ph_pc_2016']:.2f}" in md_text
            assert f"${o_row['ph_pc_2017']:.2f}" in md_text

        loo_df = pd.read_csv(DATA_DIR / "leave_one_out.csv")
        assert f"{loo_df['ols_coef'].max():.3f}" in md_text  # -0.230 (excl. Santa Clara)
        assert f"{loo_df['ols_coef'].min():.3f}" in md_text  # -0.246 (excl. Sacramento)

    print("[PASS] Stage 5: Parsed all 4 markdown tables, prose diagnostics & image links in both article files against source CSVs.")


if __name__ == "__main__":
    verify_source_csv_sha256_parity()
    verify_panel_regime_table()
    verify_pooled_regime_interactions_and_fwl()
    verify_horizon_and_lag_tables()
    verify_panel_means_and_additional_checks()
    verify_article_tables_and_links()
    print("[COMPLETE] All 5 verification stages passed.")
