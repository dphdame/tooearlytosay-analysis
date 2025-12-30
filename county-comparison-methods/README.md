# Why County Rankings Confound Policy with Context

Replication materials for ["Why County Rankings Confound Policy with Context"](https://tooearlytosay.com/county-comparison-methods/)

## Overview

This analysis demonstrates how raw county rankings in food security vulnerability confound structural factors with policy-responsive variation. It applies cost-of-living adjustments and residualization to improve comparability.

## Data Sources

| Dataset | Source | Access |
|---------|--------|--------|
| Demographics | ACS 2019-2023 | Census API |
| Cost of living | BEA Regional Price Parities (2023) | bea.gov |
| Vulnerability index | Computed | Derived |

## Methodology

### Vulnerability Index Components

| Component | Weight |
|-----------|--------|
| Food access | 25% |
| Poverty rate | 25% |
| Renter percentage | 20% |
| Minority percentage | 15% |
| Sprawl index | 15% |

### Adjustments

1. **Cost-of-living adjustment**: Scale poverty thresholds by regional price parities
2. **Structural controls**: Income, density, car ownership
3. **Within-county inequality**: Gini coefficients

### Sample

9,039 California census tracts across 58 counties

## Repository Structure

```
county-comparison-methods/
├── code/
│   ├── 01_calculate_vulnerability.py
│   ├── 02_apply_col_adjustment.py
│   ├── 03_rank_counties.py
│   └── 04_analyze_inequality.py
└── data/README.md
```

## License

Code: MIT License
