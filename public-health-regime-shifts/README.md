# Public Health Spending & Mortality Across Fiscal and Pandemic Regimes (2003–2023)

Companion analysis repository for the *Too Early to Say* methods and empirical article:
**"Why Pooled 20-Year Panel Regressions Miss Pandemic Regime Shifts: Public Health Spending and Mortality Before and During COVID-19"**

## Overview

This repository provides the verified empirical tables, regime-sensitivity checks, exposure-horizon diagnostics, and figure-generation scripts accompanying our analysis of `1,163` county-year observations across `57` California counties from fiscal year `2002–2003` through `2022–2023` (`2003–2023`).

### Key Empirical Findings

1. **Pandemic Regime Inversion Masks Pre-Pandemic Associations in Unstratified Panels:**
   - **2003–2016 Single-Regime Consistent Panel (`N = 779`, 57 counties):** Two-way fixed effects (`TWFE`) ordinary least squares (`OLS`) slope of `-0.264` resident deaths per 100,000 per `$1` per capita public health spending (`SE = 0.116`, `p = 0.0227`; wild cluster bootstrap `p = 0.0831`).
   - **2003–2019 Pre-COVID State Controller's Office (SCO) Crosswalk Panel (`N = 943`, 57 counties):** `-0.238` deaths per 100,000 per `$1` per capita (`2.38` fewer deaths per 100,000 per `$10` per capita; `SE = 0.078`, `p = 0.0022`; wild cluster bootstrap `p = 0.0070`, 95% CI `[-0.419, -0.083]`).
   - **2020–2023 COVID-19 Emergency Grant Era (`N = 220`, 57 counties):** Slope inverts to `+0.247` (`SE = 0.076`, `p = 0.0011`) as federal emergency grants (`CARES Act`, `ELC`, `ARPA`) surged into counties experiencing severe pandemic mortality waves.
   - **2003–2023 Unstratified Pooled Panel (`N = 1,163`, 57 counties):** Pooling across the 2020 structural break produces an attenuated, statistically null slope of `-0.024` (`SE = 0.030`, `p = 0.4132`).

2. **2017 SCO Chart-of-Accounts Crosswalk Diagnostics:**
   - Across the 2017 SCO reporting transition from two expenditure categories (`Operating Expenditures` + `Capital Outlay`) to four governmental fund categories (`General`, `Special Revenue`, `Capital Projects`, `Debt Service`), `51` of `56` reporting counties transitioned smoothly (`2016–2017` cross-sectional correlation `r = 0.996` in total dollars, `r = 0.916` per capita).
   - Controlling for `5` transition-outlier counties (`>50%` one-year jump in 2017: Glenn, Madera, San Luis Obispo, Sutter, Trinity) via post-2017 step-shift indicators (`-0.254`, `p = 0.0062`), excluding them post-2016 (`-0.229`, `p = 0.0274`), including debt service (`-0.238`, `p = 0.0022`), or saturating all 57 counties with regime-interacted fixed effects (`-0.267`, `p = 0.0044`) preserves the pre-pandemic negative slope.

3. **Exposure Horizons, Distributed Lags, and Temporally Separated Long-Differences:**
   - While aligned `2003–2016` cross-sectional long-differences (`-0.432`, `SE = 0.154`, `p = 0.0052`) and overlapping early-spending specifications (`ΔPH 2003–2010` predicting `ΔMort 2003–2016`: `-0.451`, `SE = 0.176`, `p = 0.0105`) are negative, **temporally separated** long-differences (`ΔPH 2003–2010` predicting subsequent `ΔMort 2010–2016`: `-0.295`, `SE = 0.251`, `p = 0.2402`) and multi-year rolling averages (`4-year` `-0.189`, `6-year` `+0.123`, `9-year` `-0.024` in `2011–2019`) are statistically indistinguishable from zero.
   - Across `16` stacked first-difference horizons (`k = 1..16` years in `2003–2019`) and discrete distributed lags (`1, 2, 3, 5, 8` years), **zero** individual horizons or lags pass Benjamini-Hochberg false discovery rate (`FDR q < 0.05`) or Holm-Bonferroni family-wise error control (`minimum q = 0.0788` at `k = 4`).

## Repository Structure

```text
public-health-regime-shifts/
├── README.md
├── requirements.txt
├── README.md
├── https://tooearlytosay.com/research/health-policy/public-health-spending-regime-shifts/
├── code/
│   ├── 01_verify_regime_and_horizon_estimates.py
│   └── 02_generate_figures.py
├── data/
│   ├── panel_regime_and_crosswalk_sensitivity.csv
│   ├── temporally_separated_long_diff_results.csv
│   ├── explicit_lag_and_cumulative_results.csv
│   ├── long_difference_and_lag_results.csv
│   ├── additional_diagnostics_summary.csv
│   ├── sco_2017_crosswalk_validation.csv
│   ├── regime_comparison_summary.csv
│   ├── verified_distributed_lags_summary.csv
│   ├── verified_16horizons_summary.csv
│   ├── verified_long_diff_summary.csv
│   └── verified_regime_summary_stats.csv
└── figures/
    ├── fig1_regime_inversion_forest.png
    ├── fig1_regime_inversion_forest.svg
    ├── fig2_long_diff_lag_horizon.png
    ├── fig2_long_diff_lag_horizon.svg
    └── QI_REPORT.json
```

## Reproduction

```bash
python3 code/01_verify_regime_and_horizon_estimates.py
python3 code/02_generate_figures.py
```
