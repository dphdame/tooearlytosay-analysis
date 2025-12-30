# The Food Security Gap: How COVID Widened Inequality

Replication materials for ["The Food Security Gap: How COVID Widened Inequality"](https://tooearlytosay.com/covid-differential-impact/)

## Overview

This difference-in-differences analysis examines how COVID-19 differentially affected SNAP participation across neighborhood vulnerability levels in Santa Clara County.

## Data Sources

| Dataset | Source | Access |
|---------|--------|--------|
| SNAP rates 2017-2023 | ACS 5-Year | Census API |
| Vulnerability index | 2019 baseline | Computed |
| Tract boundaries | TIGER/Line 2020 | Census Bureau |

## Methodology

### Study Design

- **Unit of analysis**: 408 census tracts
- **Observations**: 2,040 tract-years
- **Treatment**: Quintile 5 (highest vulnerability, 82 tracts)
- **Control**: Quintiles 1-4 (326 tracts)
- **Pre-period**: 2019
- **Post-period**: 2020+

### Difference-in-Differences

```
SNAP_rate = β₀ + β₁(High_Vulnerability) + β₂(Post_COVID)
            + β₃(High_Vulnerability × Post_COVID) + ε
```

### Key Finding

DiD coefficient: +2.35 percentage points (p=0.012)
High-vulnerability tracts saw greater SNAP increases during COVID.

## Repository Structure

```
covid-differential-impact/
├── code/
│   ├── 01_prepare_panel_data.py
│   ├── 02_classify_vulnerability.py
│   ├── 03_run_did_analysis.py
│   └── 04_event_study.py
└── data/README.md
```

## License

Code: MIT License
