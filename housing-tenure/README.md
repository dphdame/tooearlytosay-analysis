# Housing Tenure and Grocery Access

Replication materials for ["Renters vs. Owners: Housing Tenure and Grocery Access"](https://tooearlytosay.com/housing-tenure/)

## Overview

This analysis examines the relationship between housing tenure (renter vs. owner) and grocery store accessibility across California census tracts. Contrary to expectations, renter-dominated neighborhoods show better locational access to grocery stores, while owner-dominated tracts face greater transit barriers.

## Data Sources

| Dataset | Source | Access |
|---------|--------|--------|
| Housing tenure | ACS 2018-2022, Table B25003 | Census API |
| Store locations | SafeGraph (2023) | Commercial license |
| Transit stops | Cal-ITP GTFS (2024) | data.ca.gov |
| Tract boundaries | TIGER/Line Shapefiles | Census Bureau |

## Methodology

### Key Variables

- **Renter-dominated tracts**: >50% renter-occupied housing units
- **Owner-dominated tracts**: >50% owner-occupied housing units
- **Grocery distance**: Distance from tract centroid to nearest grocery store
- **Mobility desert status**: Grocery within 1 mile but poor transit access

### Analysis

1. Classify tracts by tenure dominance (renter vs. owner majority)
2. Calculate average grocery distance by tenure type
3. Compare mobility desert rates between groups
4. Test statistical significance of differences

## Repository Structure

```
housing-tenure/
├── README.md
├── requirements.txt
├── code/
│   ├── 01_acquire_census_data.py
│   ├── 02_classify_tenure.py
│   ├── 03_calculate_access_metrics.py
│   └── 04_compare_tenure_groups.py
└── data/
    └── README.md
```

## Key Findings

- Renter-dominated tracts average closer grocery access
- Owner-dominated tracts have higher mobility desert rates
- The pattern holds after controlling for income and density

## License

Code: MIT License | Data: See original source terms
