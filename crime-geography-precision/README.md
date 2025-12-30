# Crime Measurement and Geographic Precision

Replication materials for ["What Happens When You Measure Crime Where People Actually Live"](https://tooearlytosay.com/crime-geography-precision/)

## Overview

This analysis demonstrates how geographic aggregation level affects conclusions about crime and labor outcomes. County-level analysis shows null effects, while PUMA-level analysis reveals significant relationships—illustrating how geographic precision matters for policy-relevant research.

## Data Sources

| Dataset | Source | Access |
|---------|--------|--------|
| Crime data | CA DOJ Criminal Justice Statistics (2018-2022) | openjustice.doj.ca.gov |
| Labor outcomes | ACS PUMS 5-year (2018-2022) | Census Bureau |
| Geographic boundaries | TIGER/Line (cities, PUMAs) | Census Bureau |

## Methodology

### Geographic Crosswalk

Crime data from 462 police agencies is proportionally allocated to 275 PUMAs based on spatial intersection. For example, Berkeley's crime splits 72%/28% across two PUMAs based on jurisdictional boundaries.

### Analysis

- Weighted least squares regression with clustered standard errors
- County and year fixed effects
- Compare county-level vs. PUMA-level coefficient estimates

### Sample

817,000 working-age California adults (ages 25-64)

## Repository Structure

```
crime-geography-precision/
├── code/
│   ├── 01_acquire_crime_data.py
│   ├── 02_build_geographic_crosswalk.py
│   ├── 03_allocate_crime_to_puma.py
│   ├── 04_merge_labor_outcomes.py
│   └── 05_regression_analysis.py
└── data/README.md
```

## Key Finding

Geographic aggregation masks real relationships between crime exposure and employment.

## License

Code: MIT License | Data: See original source terms
