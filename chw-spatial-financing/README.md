# Why Flat Medi-Cal Rates Underfund Community Health Care (`chw-spatial-financing`)

Replication code, processed datasets, and publication figures for the Too Early To Say study:
**[Why Flat Medi-Cal Rates Underfund Community Health Care](https://tooearlytosay.com/research/health-policy/chw-spatial-financing-medi-cal/)**

## Overview
California reimburses Community Health Worker (CHW) preventive services at a flat fee-for-service benchmark of **$31.74 per 30-minute encounter** (`DHCS SPA 22-0001`). This package evaluates how a uniform statewide reimbursement schedule interacts with two spatial cost pressures across all **58 California counties** (`9,039` Census tracts) and within-county **Census tract density quintiles (`Q1`–`Q5`)** in **San Bernardino County** (`466` tracts) and **Santa Barbara County** (`109` tracts):

1. **Regional Labor & Overhead Dispersion:** Fully loaded annual CHW employment costs range from **$92,684** in rural northern counties to **$122,102** in **San Francisco County** (`186.0` cost index; statewide average **$103,719**).
2. **Unreimbursed Windshield Time & Mileage:** Using U.S. Census Bureau TIGER/Line tract land areas (`land_area_sqmi`), Cal-ITP GTFS transit coverage, and AAA/IRS vehicle operating cost schedules, we compute how round-trip field travel reduces billable encounters per day and erodes net cost recovery from **8.3%** in dense urban cores (`Q1`) down to **0.9%–1.3%** in remote rural and desert tracts (`Q5`).

## Directory Structure
```text
chw-spatial-financing/
├── README.md
├── requirements.txt
├── code/
│   ├── 01_build_chw_spatial_panel.py              # Verifies 58-county & within-county tract quintile tables
│   └── 02_generate_figures.py                     # Verifies Figure 1 (58-county) & Figure 2 (SB/SBD tract quintiles)
├── data/
│   ├── raw/
│   │   └── chw_county_benchmarks_2024.json        # 58-county BLS QCEW / MIT Living Wage / PQI 90 input benchmarks
│   └── processed/
│       ├── ca_58_counties_chw_spatial.csv         # 58-county spatial cost & Medi-Cal recovery panel
│       ├── within_county_tract_quintiles_sb_sbd.csv # Q1-Q5 tract density quintiles for San Bernardino & Santa Barbara
│       └── chw_scenario_sensitivity_summary.csv   # Cross-county sensitivity summary across Scenarios 0, A, B1, B2, C, D, 3
└── figures/
    ├── fig1_58_county_wage_distance_squeeze.webp  # Figure 1: 58-county labor squeeze vs. windshield loss
    └── fig2_within_county_tract_dispersion.webp   # Figure 2: Q1-Q5 tract density dispersion in San Bernardino & Santa Barbara
```

## Reproducing the Analysis
```bash
pip install -r requirements.txt
python3 code/01_build_chw_spatial_panel.py
python3 code/02_generate_figures.py
```
