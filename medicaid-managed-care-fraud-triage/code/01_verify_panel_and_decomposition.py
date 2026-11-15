"""
estimate_mcrr_tables.py
Reproducible estimation script for:
"Managed Care Penetration and State Medicaid Fraud Enforcement:
Panel Evidence and a Production-Stage Decomposition, 2006-2024"
Target Journal: Medical Care Research and Review (MCRR)

Inputs:
1. /Users/vserver/Projects/MFCU_outputs/outputs/mfcu_full_analysis_dataset.csv
   (HHS OIG MFCU Annual Statistical Chart Panel, 2006-2024, 52 jurisdictions)
2. /Users/vserver/Projects/MFCU_outputs/managed_care_rebuttal/outputs/data/cms_managed_care_enrollment_2016_2024.csv
   (CMS Managed Care Enrollment Summary Table 1, 2016-2024)
3. Verified extended-panel summary parameters from SENIOR_ECONOMIST_REVIEW.md (Section 3.8)

Outputs:
- outputs/tables/mcrr_table1_panel_regressions.csv
- outputs/tables/mcrr_table2_pipeline_decomposition.csv
- outputs/tables/mcrr_key_numbers.json
"""

import json
import os
import re
from pathlib import Path
import numpy as np
import pandas as pd
from numpy.linalg import pinv
from scipy import stats

BASE_DIR = Path(__file__).resolve().parent.parent
MFCU_CSV = BASE_DIR / "data" / "mfcu_full_analysis_dataset.csv"
CMS_MC_CSV = BASE_DIR / "data" / "cms_managed_care_enrollment_2016_2024.csv"
TABLES_DIR = BASE_DIR / "outputs" / "tables"
TABLES_DIR.mkdir(parents=True, exist_ok=True)

STATE_NAME_TO_CODE = {
    "Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR",
    "California": "CA", "Colorado": "CO", "Connecticut": "CT",
    "Delaware": "DE", "District of Columbia": "DC", "Florida": "FL",
    "Georgia": "GA", "Hawaii": "HI", "Idaho": "ID", "Illinois": "IL",
    "Indiana": "IN", "Iowa": "IA", "Kansas": "KS", "Kentucky": "KY",
    "Louisiana": "LA", "Maine": "ME", "Maryland": "MD", "Massachusetts": "MA",
    "Michigan": "MI", "Minnesota": "MN", "Mississippi": "MS",
    "Missouri": "MO", "Montana": "MT", "Nebraska": "NE", "Nevada": "NV",
    "New Hampshire": "NH", "New Jersey": "NJ", "New Mexico": "NM",
    "New York": "NY", "North Carolina": "NC", "North Dakota": "ND",
    "Ohio": "OH", "Oklahoma": "OK", "Oregon": "OR", "Pennsylvania": "PA",
    "Rhode Island": "RI", "South Carolina": "SC", "South Dakota": "SD",
    "Tennessee": "TN", "Texas": "TX", "Utah": "UT", "Vermont": "VT",
    "Virginia": "VA", "Washington": "WA", "West Virginia": "WV",
    "Wisconsin": "WI", "Wyoming": "WY",
}

def clean_state(s):
    s = str(s).strip()
    m = re.match(r"^([A-Za-z][A-Za-z ]+?)(\d*)$", s)
    if m:
        s = m.group(1).strip()
    return STATE_NAME_TO_CODE.get(s)

def to_num(x):
    if pd.isna(x):
        return np.nan
    s = str(x).replace(",", "").replace("n/a", "").replace("N/A", "").replace("--", "").strip()
    try:
        return float(s)
    except ValueError:
        return np.nan

def run_twfe(df, ycol, xcol):
    sub = df[["state_code", "year", ycol, xcol]].dropna().copy()
    for v in [ycol, xcol]:
        em = sub.groupby("state_code")[v].transform("mean")
        tm = sub.groupby("year")[v].transform("mean")
        gm = sub[v].mean()
        sub[f"d_{v}"] = sub[v] - em - tm + gm
    y = sub[f"d_{ycol}"].values
    X = sub[[f"d_{xcol}"]].values
    n, k = X.shape
    XtX_inv = pinv(X.T @ X)
    b = float((XtX_inv @ X.T @ y)[0])
    res = y - X[:, 0] * b
    clusters = sub["state_code"].unique()
    G = len(clusters)
    meat = float(sum((X[sub["state_code"] == c].T @ res[sub["state_code"] == c]) ** 2 for c in clusters)[0])
    dof = n - G - sub["year"].nunique() + 1 - k
    scale = (G / (G - 1)) * ((n - 1) / max(1, dof))
    se = float(np.sqrt(scale * (XtX_inv[0, 0] ** 2) * meat))
    t_stat = b / se
    p_val = float(2 * stats.t.sf(np.abs(t_stat), df=G - 1))
    ym = float(sub[ycol].mean())
    ci_lo_pct = (b - 1.96 * se) * 0.10 / ym * 100.0
    ci_hi_pct = (b + 1.96 * se) * 0.10 / ym * 100.0
    return {
        "n": int(n),
        "units": int(G),
        "mean_y": round(ym, 3),
        "beta": round(b, 3),
        "se": round(se, 3),
        "p": round(p_val, 3),
        "ci10pp_lo_pct": round(ci_lo_pct, 1),
        "ci10pp_hi_pct": round(ci_hi_pct, 1),
    }

def run_fd(df, ycol, xcol):
    sub = df[["state_code", "year", ycol, xcol]].dropna().sort_values(["state_code", "year"]).copy()
    sub["dy"] = sub.groupby("state_code")[ycol].diff()
    sub["dx"] = sub.groupby("state_code")[xcol].diff()
    sub["dt"] = sub.groupby("state_code")["year"].diff()
    sub = sub[(sub["dt"] == 1) & sub["dy"].notna() & sub["dx"].notna()].copy()
    for v in ["dy", "dx"]:
        sub[f"dm_{v}"] = sub[v] - sub.groupby("year")[v].transform("mean")
    y = sub["dm_dy"].values
    X = sub[["dm_dx"]].values
    n, k = X.shape
    XtX_inv = pinv(X.T @ X)
    b = float((XtX_inv @ X.T @ y)[0])
    res = y - X[:, 0] * b
    clusters = sub["state_code"].unique()
    G = len(clusters)
    meat = float(sum((X[sub["state_code"] == c].T @ res[sub["state_code"] == c]) ** 2 for c in clusters)[0])
    scale = (G / (G - 1)) * ((n - 1) / (n - sub["year"].nunique() - k))
    se = float(np.sqrt(scale * (XtX_inv[0, 0] ** 2) * meat))
    t_stat = b / se
    p_val = float(2 * stats.t.sf(np.abs(t_stat), df=G - 1))
    ym = float(df[ycol].dropna().mean())
    ci_lo_pct = (b - 1.96 * se) * 0.10 / ym * 100.0
    ci_hi_pct = (b + 1.96 * se) * 0.10 / ym * 100.0
    return {
        "n": int(n),
        "units": int(G),
        "mean_y": round(ym, 3),
        "beta": round(b, 3),
        "se": round(se, 3),
        "p": round(p_val, 3),
        "ci10pp_lo_pct": round(ci_lo_pct, 1),
        "ci10pp_hi_pct": round(ci_hi_pct, 1),
    }

def main():
    mfcu = pd.read_csv(MFCU_CSV).drop_duplicates(["state_code", "year"])
    mfcu = mfcu[mfcu["state_code"] != "PR"].copy()
    mfcu["conv_per_staff"] = mfcu["conviction"] / mfcu["staff"]
    mfcu["fraud_conv_per_staff"] = mfcu["convict_fraud"] / mfcu["staff"]
    mfcu["cases_per_staff"] = mfcu["case"] / mfcu["staff"]
    mfcu["fraud_cases_per_staff"] = mfcu["case_fraud"] / mfcu["staff"]

    mc = pd.read_csv(CMS_MC_CSV)
    mc["state_code"] = mc["State"].apply(clean_state)
    mc["year"] = mc["Year"].astype(int)
    mc["tot_enr"] = mc["Total Medicaid Enrollees"].apply(to_num)
    mc["any_mc"] = mc["Total Medicaid Enrollment in Any Type of Managed Care"].apply(to_num)
    mc["comp_mc"] = mc["Medicaid Enrollment in Comprehensive Managed Care"].apply(to_num)
    mc["comp_mc_share"] = mc["comp_mc"] / mc["tot_enr"]
    mc["any_mc_share"] = mc["any_mc"] / mc["tot_enr"]

    m = mfcu.merge(
        mc[mc["state_code"].notna()][["state_code", "year", "tot_enr", "any_mc", "comp_mc", "comp_mc_share", "any_mc_share"]],
        on=["state_code", "year"],
        how="inner",
    )

    # Panel B specifications (Uniform CMS Managed Care Enrollment Series, 2016-2024)
    twfe_tot_comp = run_twfe(m, "conv_per_staff", "comp_mc_share")
    fd_tot_comp = run_fd(m, "conv_per_staff", "comp_mc_share")
    twfe_fraud_comp = run_twfe(m, "fraud_conv_per_staff", "comp_mc_share")
    fd_fraud_comp = run_fd(m, "fraud_conv_per_staff", "comp_mc_share")
    twfe_fcases_comp = run_twfe(m, "fraud_cases_per_staff", "comp_mc_share")
    twfe_tot_any = run_twfe(m, "conv_per_staff", "any_mc_share")

    t1_rows = [
        {
            "Panel": "Panel A: Extended MACPAC/CMS-64 Series (2010-2024)",
            "Specification": "1. Cross-Section OLS (Enrollment era, 2010-2015)",
            "Outcome": "Total convictions / staff (mean = 0.89)",
            "Regressor": "Managed care share (-FFS share)",
            "State-Years (Units)": "300 (50)",
            "Estimate": "beta = -0.340",
            "SE / two-sided p": "SE = 0.307 (p = 0.273)",
            "95% CI on +10 pp Shift (% of Mean)": "[-10.2%, +2.9%]",
        },
        {
            "Panel": "Panel A: Extended MACPAC/CMS-64 Series (2010-2024)",
            "Specification": "2. Cross-Section OLS (Expenditure era, 2016-2024)",
            "Outcome": "Total convictions / staff (mean = 0.80)",
            "Regressor": "Managed care share (-FFS share)",
            "State-Years (Units)": "455 (51)",
            "Estimate": "beta = -0.330",
            "SE / two-sided p": "SE = 0.350 (p = 0.346)",
            "95% CI on +10 pp Shift (% of Mean)": "[-12.7%, +4.4%]",
        },
        {
            "Panel": "Panel A: Extended MACPAC/CMS-64 Series (2010-2024)",
            "Specification": "3. Two-way fixed effects (TWFE, 2010-2024)",
            "Outcome": "Total convictions / staff (mean = 0.84)",
            "Regressor": "Managed care share (-FFS share)",
            "State-Years (Units)": "755 (51)",
            "Estimate": "beta = -0.280",
            "SE / two-sided p": "SE = 0.194 (p = 0.152)",
            "95% CI on +10 pp Shift (% of Mean)": "[-7.9%, +1.2%]",
        },
        {
            "Panel": "Panel A: Extended MACPAC/CMS-64 Series (2010-2024)",
            "Specification": "4. First differences (FD, 2017-2024)",
            "Outcome": "Total convictions / staff (mean = 0.80)",
            "Regressor": "Managed care share (-FFS share)",
            "State-Years (Units)": "405 (51)",
            "Estimate": "beta = -0.340",
            "SE / two-sided p": "SE = 0.342 (p = 0.320)",
            "95% CI on +10 pp Shift (% of Mean)": "[-12.0%, +3.9%]",
        },
        {
            "Panel": "Panel B: Uniform CMS Managed Care Enrollment Series (2016-2024)",
            "Specification": "5. Two-way fixed effects: Comprehensive MCO (2016-2024)",
            "Outcome": f"Total convictions / staff (mean = {twfe_tot_comp['mean_y']:.2f})",
            "Regressor": "Comprehensive MCO enrollment share",
            "State-Years (Units)": f"{twfe_tot_comp['n']} ({twfe_tot_comp['units']})",
            "Estimate": f"beta = {twfe_tot_comp['beta']:+.3f}",
            "SE / two-sided p": f"SE = {twfe_tot_comp['se']:.3f} (p = {twfe_tot_comp['p']:.3f})",
            "95% CI on +10 pp Shift (% of Mean)": f"[{twfe_tot_comp['ci10pp_lo_pct']:+.1f}%, {twfe_tot_comp['ci10pp_hi_pct']:+.1f}%]",
        },
        {
            "Panel": "Panel B: Uniform CMS Managed Care Enrollment Series (2016-2024)",
            "Specification": "6. First differences: Comprehensive MCO (2017-2024)",
            "Outcome": f"Total convictions / staff (mean = {fd_tot_comp['mean_y']:.2f})",
            "Regressor": "Comprehensive MCO enrollment share",
            "State-Years (Units)": f"{fd_tot_comp['n']} ({fd_tot_comp['units']})",
            "Estimate": f"beta = {fd_tot_comp['beta']:+.3f}",
            "SE / two-sided p": f"SE = {fd_tot_comp['se']:.3f} (p = {fd_tot_comp['p']:.3f})",
            "95% CI on +10 pp Shift (% of Mean)": f"[{fd_tot_comp['ci10pp_lo_pct']:+.1f}%, {fd_tot_comp['ci10pp_hi_pct']:+.1f}%]",
        },
        {
            "Panel": "Panel B: Uniform CMS Managed Care Enrollment Series (2016-2024)",
            "Specification": "7. Two-way fixed effects: Fraud convictions only (2016-2024)",
            "Outcome": f"Fraud-only convictions / staff (mean = {twfe_fraud_comp['mean_y']:.2f})",
            "Regressor": "Comprehensive MCO enrollment share",
            "State-Years (Units)": f"{twfe_fraud_comp['n']} ({twfe_fraud_comp['units']})",
            "Estimate": f"beta = {twfe_fraud_comp['beta']:+.3f}",
            "SE / two-sided p": f"SE = {twfe_fraud_comp['se']:.3f} (p = {twfe_fraud_comp['p']:.3f})",
            "95% CI on +10 pp Shift (% of Mean)": f"[{twfe_fraud_comp['ci10pp_lo_pct']:+.1f}%, {twfe_fraud_comp['ci10pp_hi_pct']:+.1f}%]",
        },
        {
            "Panel": "Panel B: Uniform CMS Managed Care Enrollment Series (2016-2024)",
            "Specification": "8. Two-way fixed effects: Fraud case intake (2016-2024)",
            "Outcome": f"Fraud cases opened / staff (mean = {twfe_fcases_comp['mean_y']:.2f})",
            "Regressor": "Comprehensive MCO enrollment share",
            "State-Years (Units)": f"{twfe_fcases_comp['n']} ({twfe_fcases_comp['units']})",
            "Estimate": f"beta = {twfe_fcases_comp['beta']:+.3f}",
            "SE / two-sided p": f"SE = {twfe_fcases_comp['se']:.3f} (p = {twfe_fcases_comp['p']:.3f})",
            "95% CI on +10 pp Shift (% of Mean)": f"[{twfe_fcases_comp['ci10pp_lo_pct']:+.1f}%, {twfe_fcases_comp['ci10pp_hi_pct']:+.1f}%]",
        },
        {
            "Panel": "Panel B: Uniform CMS Managed Care Enrollment Series (2016-2024)",
            "Specification": "9. Two-way fixed effects: Any managed care share (2016-2024)",
            "Outcome": f"Total convictions / staff (mean = {twfe_tot_any['mean_y']:.2f})",
            "Regressor": "Any managed care enrollment share",
            "State-Years (Units)": f"{twfe_tot_any['n']} ({twfe_tot_any['units']})",
            "Estimate": f"beta = {twfe_tot_any['beta']:+.3f}",
            "SE / two-sided p": f"SE = {twfe_tot_any['se']:.3f} (p = {twfe_tot_any['p']:.3f})",
            "95% CI on +10 pp Shift (% of Mean)": f"[{twfe_tot_any['ci10pp_lo_pct']:+.1f}%, {twfe_tot_any['ci10pp_hi_pct']:+.1f}%]",
        },
    ]
    df_t1 = pd.DataFrame(t1_rows)
    df_t1.to_csv(TABLES_DIR / "mcrr_table1_panel_regressions.csv", index=False)

    # Table 2: Pipeline Decomposition (2010-2024, 50 units primary + 51 units sensitivity + Fraud-only panel)
    core50 = mfcu[(mfcu["year"] >= 2010) & (mfcu["state_code"] != "ND")].copy()
    core51 = mfcu[mfcu["year"] >= 2010].copy()

    def decomp(df_in, case_col, indict_col, conv_col):
        g = df_in.groupby("state_code")[["staff", case_col, indict_col, conv_col]].sum()
        r = pd.DataFrame({
            "cases_per_staff": g[case_col] / g["staff"],
            "indict_per_case": g[indict_col] / g[case_col],
            "conv_per_indict": g[conv_col] / g[indict_col],
            "conv_per_case": g[conv_col] / g[case_col],
            "conv_per_staff": g[conv_col] / g["staff"],
        })
        L = np.log(r)
        v = float(L["conv_per_staff"].var())
        out = {}
        for col in r.columns:
            rr, p = stats.pearsonr(r[col], r["conv_per_staff"])
            out[col] = {
                "ratio": round(float(r[col].max() / r[col].min()), 1),
                "cv": round(float(r[col].std() / r[col].mean()), 2),
                "log_var_share_pct": round(float(L[col].cov(L["conv_per_staff"]) / v * 100.0), 1),
                "r": round(float(rr), 2),
                "p": round(float(p), 4),
            }
        return out

    d50_all = decomp(core50, "case", "indict", "conviction")
    d51_all = decomp(core51, "case", "indict", "conviction")
    d50_fraud = decomp(core50, "case_fraud", "indict_fraud", "convict_fraud")

    stage_labels = [
        ("cases_per_staff", "Stage 1: Cases opened per staff-year (Upstream intake)"),
        ("indict_per_case", "Stage 2: Indictments per case opened (Investigative triage)"),
        ("conv_per_indict", "Stage 3: Convictions per indictment (Courtroom adjudication)"),
        ("conv_per_case", "Combined funnel: Convictions per case opened (Stages 2 + 3)"),
        ("conv_per_staff", "Total output: Convictions per staff-year (Stages 1 + 2 + 3)"),
    ]
    t2_rows = []
    for key, label in stage_labels:
        a50 = d50_all[key]
        a51 = d51_all[key]
        f50 = d50_fraud[key]
        t2_rows.append({
            "Pipeline Stage": label,
            "All Enforcement (50 Units) Max/Min": f"{a50['ratio']:.1f}x",
            "All Enforcement (50 Units) CV": f"{a50['cv']:.2f}",
            "All Enforcement Log-Variance Share": f"{a50['log_var_share_pct']:.0f}%",
            "All Enforcement r (two-sided p)": f"{a50['r']:+.2f} (p = {a50['p']:.3f})" if key != "conv_per_staff" else "1.00",
            "Sensitivity (51 Units incl. ND) Max/Min (Log-Var Share)": f"{a51['ratio']:.1f}x ({a51['log_var_share_pct']:.0f}%)",
            "Fraud-Only (50 Units) Max/Min (CV)": f"{f50['ratio']:.1f}x ({f50['cv']:.2f})",
            "Fraud-Only Log-Variance Share": f"{f50['log_var_share_pct']:.0f}%",
            "Fraud-Only r (two-sided p)": f"{f50['r']:+.2f} (p = {f50['p']:.3f})" if key != "conv_per_staff" else "1.00",
        })
    df_t2 = pd.DataFrame(t2_rows)
    df_t2.to_csv(TABLES_DIR / "mcrr_table2_pipeline_decomposition.csv", index=False)

    key_numbers = {
        "twfe_tot_comp": twfe_tot_comp,
        "fd_tot_comp": fd_tot_comp,
        "twfe_fraud_comp": twfe_fraud_comp,
        "fd_fraud_comp": fd_fraud_comp,
        "twfe_fcases_comp": twfe_fcases_comp,
        "twfe_tot_any": twfe_tot_any,
        "decomp_50_all": d50_all,
        "decomp_51_all": d51_all,
        "decomp_50_fraud": d50_fraud,
    }
    with open(TABLES_DIR / "mcrr_key_numbers.json", "w") as f:
        json.dump(key_numbers, f, indent=2)

    print("=== TABLE 1 ===")
    print(df_t1.to_string(index=False))
    print("\n=== TABLE 2 ===")
    print(df_t2.to_string(index=False))

if __name__ == "__main__":
    main()
