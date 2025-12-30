# The Widening Gap: Diverging Neighborhood Trajectories

Replication materials for ["The Widening Gap: Why Some Neighborhoods Are Falling Behind"](https://tooearlytosay.com/diverging-trajectories/)

## Overview

This analysis tracks SNAP participation trajectories across Santa Clara County census tracts over 4 years, revealing divergent patterns between stable and deteriorating neighborhoods.

## Data Sources

| Dataset | Source | Access |
|---------|--------|--------|
| SNAP rates | ACS 2019-2023 | Census API |
| Demographics | ACS 2019-2023 | Census API |
| Tract boundaries | TIGER/Line 2020 | Census Bureau |

## Methodology

### Trajectory Classification

Each tract classified by 4-year SNAP participation change:

| Category | Criteria |
|----------|----------|
| Deteriorating | SNAP increased >1 percentage point |
| Stable | Change within ±1 percentage point |
| Improving | SNAP decreased >1 percentage point |

### Sample

- 408 census tracts in Santa Clara County
- 334 tracts (82%) with complete 4-year data
- 112 tracts excluded for boundary changes or missing years

### Analysis

1. Calculate year-over-year SNAP rate changes
2. Classify trajectories
3. Correlate with baseline vulnerability quintiles
4. Map geographic clustering

## Repository Structure

```
diverging-trajectories/
├── code/
│   ├── 01_download_multiyear_snap.py
│   ├── 02_calculate_trajectories.py
│   ├── 03_classify_tracts.py
│   └── 04_analyze_patterns.py
└── data/README.md
```

## License

Code: MIT License
