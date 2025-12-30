# Mobility Deserts: Transit Barriers to Food Access

Replication materials for ["Mobility Deserts: When Grocery Stores Are Close on Paper But Unreachable Without a Car"](https://tooearlytosay.com/hidden-mobility-deserts/)

## Overview

Federal food access policy assumes proximity equals access. This analysis identifies California census tracts where grocery stores exist within 1 mile, but limited transit infrastructure creates a "mobility desert"—areas where stores are technically close but practically unreachable without a car.

### Key Findings

- **1,086 mobility desert tracts** (12% of California's 9,039 residential tracts)
- **150,000-250,000 transit-dependent Californians** affected
- These tracts are invisible to federal food desert metrics, which only measure distance

## Methodology

### Classification Logic

Each census tract is classified into one of three categories:

```
If grocery distance > 1 mile:
    → Traditional Food Desert
Else if nearest transit stop > 0.5 miles OR stops within 0.5 miles < 2:
    → Mobility Desert
Else:
    → Full Access
```

### Data Sources

| Dataset | Source | Access |
|---------|--------|--------|
| Transit stops | Cal-ITP GTFS Ingest Pipeline | [data.ca.gov](https://data.ca.gov) |
| Census tract boundaries | TIGER/Line Shapefiles | [Census Bureau](https://www.census.gov/geographies/mapping-files/time-series/geo/tiger-line-file.html) |
| Demographics (ACS 2019-2023) | American Community Survey | [Census API](https://www.census.gov/data/developers/data-sets/acs-5year.html) |
| Grocery store locations | Validated store data | See `data/README.md` |

## Repository Structure

```
mobility-deserts/
├── README.md
├── requirements.txt
├── code/
│   ├── 01_acquire_transit_data.py      # Download Cal-ITP GTFS data
│   ├── 02_acquire_census_data.py       # Download tract boundaries + ACS
│   ├── 03_acquire_grocery_data.py      # Load grocery store locations
│   ├── 04_calculate_distances.py       # Compute distances to stores/transit
│   ├── 05_classify_tracts.py           # Apply classification logic
│   ├── 06_generate_summary_tables.py   # Create output tables
│   ├── 07_analyze_demographics.py      # Compare demographics by category
│   └── 08_create_validation_report.py  # Document data quality issues
└── data/
    ├── README.md                       # Download instructions
    ├── raw/                            # Place downloaded data here
    └── processed/                      # Analysis outputs
```

## Setup

### Requirements

```bash
pip install -r requirements.txt
```

### Environment Variables

Create a `.env` file with:

```
CENSUS_API_KEY=your_census_api_key_here
```

Get a free Census API key at: https://api.census.gov/data/key_signup.html

### Running the Analysis

Run scripts in order:

```bash
python code/01_acquire_transit_data.py
python code/02_acquire_census_data.py
python code/03_acquire_grocery_data.py
python code/04_calculate_distances.py
python code/05_classify_tracts.py
python code/06_generate_summary_tables.py
python code/07_analyze_demographics.py
python code/08_create_validation_report.py
```

## Key Outputs

- `data/processed/tract_classifications.csv` - All tracts with classification
- `data/processed/summary_statewide.csv` - Statewide counts and percentages
- `data/processed/summary_by_region.csv` - Regional breakdown
- `data/processed/demographics_comparison.csv` - Demographics by tract type
- `data/processed/validation_report.md` - Data quality documentation

## Notes

### Transit Stop Count Discrepancy

The Cal-ITP dataset reports 64,060 transit stops, but after deduplication and validation, we use approximately 24,000 unique stop locations. This is documented in the validation report.

## Citation

If you use this analysis, please cite:

> Too Early to Say. (2025). Mobility Deserts: When Grocery Stores Are Close on Paper But Unreachable Without a Car. https://tooearlytosay.com/hidden-mobility-deserts/

## License

Code: MIT License
Created data: CC-BY 4.0
