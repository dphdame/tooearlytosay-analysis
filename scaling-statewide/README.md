# Scaling Up: From 7 Counties to Statewide

Replication materials for ["Scaling Up: From 7 Counties to Statewide"](https://tooearlytosay.com/scaling-statewide/)

## Overview

This project documents the technical approach to scaling food security analysis from a pilot of 7 counties to all 58 California counties (9,039 census tracts). It covers data acquisition, spatial indexing, and computational efficiency strategies.

## Data Sources

| Dataset | Source | Scale |
|---------|--------|-------|
| Census ACS | Census API | 58 counties |
| Grocery stores | SafeGraph (2023) | 24,850+ stores |
| Transit stops | Cal-ITP GTFS | 200+ agencies |
| Tract boundaries | TIGER/Line | 9,039 tracts |

## Methodology

### Efficient Spatial Indexing

KD-tree structures enable finding nearest stores among 24,850 options in <30 seconds.

### Vulnerability Index

Composite measure with five normalized components:
- Food access (25%)
- Poverty (25%)
- Renter status (20%)
- Minority share (15%)
- Sprawl (15%)

### Mobility Desert Classification

Tracts with grocery <1 mile but transit >0.5 miles or <2 stops nearby.

## Repository Structure

```
scaling-statewide/
├── code/
│   ├── 01_download_statewide_data.py
│   ├── 02_build_spatial_index.py
│   ├── 03_calculate_distances.py
│   └── 04_classify_all_tracts.py
└── data/README.md
```

## License

Code: MIT License
