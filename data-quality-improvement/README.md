# The Data Quality Problem: 49% to 12%

Replication materials for ["The Data Quality Problem: How We Went From 49% to 12% Mobility Deserts"](https://tooearlytosay.com/data-quality-49-to-12/)

## Overview

This analysis documents how transit data completeness dramatically affects research conclusions. Using incomplete data from 8 agencies suggested 49% of tracts were mobility deserts; using complete Cal-ITP data reduced this to 12%.

## Data Sources

### Original (Incomplete)
- 8 individual agency GTFS feeds
- 24,421 transit stops

### Corrected (Complete)
- Cal-ITP statewide aggregation
- 143,203 raw stops → 64,060 unique after deduplication
- 200+ agencies

## Methodology

### Mobility Desert Classification

```
If grocery distance > 1 mile:
    → Traditional Food Desert
Else if transit stop > 0.5 miles OR stops within 0.5 miles < 2:
    → Mobility Desert
Else:
    → Full Access
```

### Comparison

Apply identical classification logic to both datasets:
1. Calculate distances using same spatial methods
2. Apply same thresholds
3. Compare resulting classifications

## Key Finding

The 4-fold difference (49% → 12%) stems entirely from transit data completeness, not methodological changes.

## Repository Structure

```
data-quality-improvement/
├── code/
│   ├── 01_load_original_transit.py
│   ├── 02_load_calitp_transit.py
│   ├── 03_classify_with_each.py
│   └── 04_compare_results.py
└── data/README.md
```

## License

Code: MIT License
