# Medicaid Managed Care and Fraud Enforcement: Investigative Triage Accounts for State Output Gaps

Replication package for the *Too Early To Say* article ([https://tooearlytosay.com/research/health-policy/medicaid-managed-care-fraud-triage/](https://tooearlytosay.com/research/health-policy/medicaid-managed-care-fraud-triage/)) and companion working paper (*Privatizing Program Integrity? Managed Care Penetration and Medicaid Fraud Enforcement*, [SSRN 7710301](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=7710301)).

## Summary of Empirical Findings

1. **No Detectable Within-State Managed Care Association at State-Year Precision:**
   - Across 51 U.S. jurisdictions over FY 2010–2024 ($N = 755$ state-years in the harmonized MACPAC/CMS-64 series; $N = 443$ state-years in the uniform 2016–2024 CMS Comprehensive MCO enrollment series), within-state increases in managed care penetration show no detectable association with state Medicaid Fraud Control Unit (MFCU) conviction productivity at state-year precision.
   - In the uniform 2016–2024 two-way fixed effects (TWFE) model, a 10 percentage-point increase in comprehensive MCO enrollment share corresponds to $\hat{\beta} = -0.007$ ($\text{SE} = 0.311, p = 0.981$, 95% CI $[-7.7\%, +7.5\%]$ of the mean) for total convictions per staff-year and $\hat{\beta} = -0.031$ ($\text{SE} = 0.189, p = 0.870$, 95% CI $[-7.3\%, +6.1\%]$) for fraud-only convictions per staff-year.
   - In the 15-year harmonized TWFE panel ($N = 755$), $\hat{\beta} = -0.280$ ($\text{SE} = 0.194, p = 0.152$, 95% CI $[-7.9\%, +1.2\%]$ per +10 pp). These estimates rule out large positive productivity gains while leaving smaller positive or negative shifts inside the confidence bounds.

2. **Descriptive Three-Stage Log-Variance Accounting Identity:**
   - Decomposing state enforcement output per staff-year ($Y_s/S_s = (C_s/S_s) \times (I_s/C_s) \times (Y_s/I_s)$) across the 50 continuously operating jurisdictions (FY 2010–2024) shows that **Stage 2 investigative triage** (indictments per opened case, $I_s/C_s$) accounts for **75.4%** of cross-state log variance in total convictions per staff-year ($r = +0.58, p < 0.001$) and **84.2%** of cross-state log variance in fraud-only convictions per staff-year ($r = +0.73, p < 0.001$).
   - Stage 1 case intake ($C_s/S_s$) accounts for **24.6%** (19.0% for fraud-only), while Stage 3 courtroom adjudication ($Y_s/I_s$) accounts for **0.0%** (-3.2% for fraud-only).
   - Because this covariance split is a descriptive accounting identity rather than a causal experiment, it locates where cross-state dispersion clusters along the enforcement funnel rather than proving what caused it.

## Directory Structure

- `data/`
  - `mfcu_full_analysis_dataset.csv`: HHS OIG MFCU Annual Statistical Report panel dataset (FY 2006–2024; 51 jurisdictions in the FY 2010–2024 analysis window excluding Puerto Rico).
  - `cms_managed_care_enrollment_2016_2024.csv`: CMS Medicaid Managed Care Enrollment and Program Characteristics Summary Table 1 (2016–2024).
  - `INPUT_MANIFEST.json`: SHA-256 hashes, byte counts, and official federal source provenance for all input datasets.
- `code/`
  - `01_verify_panel_and_decomposition.py`: Self-contained estimation script using relative paths (`BASE_DIR = Path(__file__).resolve().parent.parent`) to reproduce Table 1, Table 2, and `outputs/tables/mcrr_key_numbers.json`.
  - `generate_figures.py`: Reproduces the three publication figures (`figure0_pipeline_conceptual_map`, `figure1_twfe_managed_care_null_forest`, `figure2_three_stage_variance_decomposition`).
- `outputs/tables/`
  - `mcrr_table1_panel_regressions.csv`
  - `mcrr_table2_pipeline_decomposition.csv`
  - `mcrr_key_numbers.json`
- `figures/`
  - High-resolution PNG and WebP figures used in the article.
- `article-draft.md`: Full markdown source of the published article.

## Reproduction

```bash
python3 code/01_verify_panel_and_decomposition.py
python3 code/generate_figures.py
```
