# Medicaid Managed Care and Fraud Enforcement: Investigative Triage Drives State Output

Replication package for the Too Early To Say article (**[Medicaid Managed Care and Fraud Enforcement: Investigative Triage Drives State Output](https://tooearlytosay.com/research/health-policy/medicaid-managed-care-fraud-triage/)**) and companion working paper (**[SSRN Working Paper No. 7710301](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=7710301)**).

## Overview

We assemble a 15-year state-year panel of 51 U.S. Medicaid Fraud Control Units (MFCUs; 50 states and the District of Columbia, FY 2010–2024, `N = 755` state-years) paired with CMS Medicaid managed care penetration series (`N = 443` state-years in the uniform FY 2016–2024 CMS Managed Care Enrollment Summary).

1. **Within-State Managed Care Expansions (`Table 1`, `Figure 1`):** Across nine cross-sectional, two-way fixed effects (TWFE), and first-difference specifications, within-state increases in comprehensive managed care enrollment show near-zero association with total convictions per staff-year (`slope = -0.007`, `SE = 0.311`, `p = 0.981`) or fraud-only convictions per staff-year (`slope = -0.031`, `SE = 0.189`, `p = 0.870`).
2. **Three-Stage Multiplicative Log-Variance Decomposition (`Table 2`, `Figure 2`):** Decomposing convictions per staff-year (`Y/S = C/S * I/C * Y/I`) across the 50 continuously operating jurisdictions reveals that Stage 2 investigative triage (`I/C`, indictments per opened case) accounts for **75.4%** of cross-state log variance in total convictions per staff-year (`r = +0.58`, `p < 0.001`) and **84.2%** for fraud-only convictions (`r = +0.73`, `p < 0.001`), compared with **24.6%** (**19.0%** fraud-only) for Stage 1 case intake (`C/S`) and **0.0%** (**-3.2%** fraud-only) for Stage 3 courtroom adjudication (`Y/I`).

## Repository Structure

- `code/01_verify_panel_and_decomposition.py`: Reproduces Table 1 (all 9 regression specifications) and Table 2 (three-stage multiplicative log-variance decomposition across 50 continuously operating units and 51-unit sensitivity).
- `code/generate_figures.py`: Generates `figure0_pipeline_conceptual_map`, `figure1_twfe_managed_care_null_forest`, and `figure2_three_stage_variance_decomposition` in `.png`, `.svg`, and `.webp` formats.
- `data/`: Public state-year OIG MFCU and CMS managed care panel (`mfcu_managed_care_panel_2010_2024.csv`) and exported regression/decomposition outputs (`table1_managed_care_regressions.csv`, `table2_pipeline_decomposition.csv`).
- `figures/`: Rendered figures (`figure0`–`figure2`).
- `article-draft.md`: Markdown source for the published Too Early To Say article.
