# Transit Access and Race in California

Replication materials for ["Who Gets Left Behind: Transit Access and Race in California"](https://tooearlytosay.com/transit-equity-race/)

## Overview

This analysis examines disparities in transit access across racial demographics in California census tracts. It combines racial composition data with transit infrastructure to identify systematic patterns in mobility desert distribution.

## Data Sources

| Dataset | Source | Access |
|---------|--------|--------|
| Racial composition | ACS 2018-2022, Table B03002 | Census API |
| Housing tenure | ACS 2018-2022, Table B25003 | Census API |
| Transit stops | Cal-ITP GTFS (2024) | data.ca.gov |
| Grocery locations | SafeGraph (2023) | Commercial |

## Methodology

### Key Variables

- **Majority-minority tracts**: Non-Hispanic non-white residents exceed 50%
- **Renter-dominated tracts**: Renters occupy more than half of housing units
- **Mobility desert**: Grocery within 1 mile, but transit >0.5 miles or <2 stops nearby

### Analysis

1. Classify tracts by racial composition
2. Calculate mobility desert rates by demographic group
3. Linear probability model controlling for income and density
4. Regional stratification across 9 California regions

## Repository Structure

```
transit-equity-race/
├── code/
│   ├── 01_acquire_demographic_data.py
│   ├── 02_classify_tracts.py
│   ├── 03_calculate_mobility_metrics.py
│   └── 04_regression_analysis.py
└── data/README.md
```

## License

Code: MIT License | Data: See original source terms
