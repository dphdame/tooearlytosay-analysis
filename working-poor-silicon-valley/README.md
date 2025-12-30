# Working Poor in Silicon Valley

Replication materials for ["When Work Isn't Enough: What Census Data Reveals About Silicon Valley's Working Poor"](https://tooearlytosay.com/working-poor-silicon-valley/)

## Overview

In the heart of the nation's wealthiest tech hub, some neighborhoods tell a different story: residents who work full-time, year-round, yet still fall below the poverty line. This analysis identifies census tracts in the Bay Area where **60% or more of residents are employed full-time** but **poverty rates exceed 10%**.

### Key Findings

- Identifies "working poor" neighborhoods in Silicon Valley and the broader Bay Area
- Reveals where full-time employment doesn't guarantee economic security
- Shows the extreme local cost of living's impact on working families

## Methodology

### Working Poor Definition

A census tract is classified as "working poor" if it meets BOTH criteria:

```
Employment rate ≥ 60% (full-time, year-round workers)
AND
Poverty rate > 10%
```

This captures neighborhoods where most residents are working, yet a significant portion remain in poverty—suggesting wage-cost mismatches rather than unemployment.

### Data Sources

| Dataset | Source | Access |
|---------|--------|--------|
| Employment status | ACS 5-Year (2019-2023), Table B23025 | [Census API](https://www.census.gov/data/developers/data-sets/acs-5year.html) |
| Poverty status | ACS 5-Year (2019-2023), Table B17001 | [Census API](https://www.census.gov/data/developers/data-sets/acs-5year.html) |
| Income distribution | ACS 5-Year (2019-2023), Table B19001 | [Census API](https://www.census.gov/data/developers/data-sets/acs-5year.html) |
| Tract boundaries | TIGER/Line Shapefiles | [Census Bureau](https://www.census.gov/geographies/mapping-files/time-series/geo/tiger-line-file.html) |

### Geographic Focus

**Bay Area Counties (9-county definition):**
- Alameda, Contra Costa, Marin, Napa, San Francisco
- San Mateo, Santa Clara, Solano, Sonoma

## Repository Structure

```
working-poor-silicon-valley/
├── README.md
├── requirements.txt
├── code/
│   ├── 01_acquire_census_data.py      # Download ACS data for Bay Area
│   ├── 02_calculate_employment_poverty.py  # Identify working poor tracts
│   ├── 03_geographic_analysis.py      # Map clusters and patterns
│   ├── 04_demographic_profile.py      # Compare tract characteristics
│   └── 05_generate_summary_tables.py  # Create output tables
└── data/
    ├── README.md                      # Download instructions
    ├── raw/                           # Place downloaded data here
    └── processed/                     # Analysis outputs
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
python code/01_acquire_census_data.py
python code/02_calculate_employment_poverty.py
python code/03_geographic_analysis.py
python code/04_demographic_profile.py
python code/05_generate_summary_tables.py
```

## Key Outputs

- `data/processed/bay_area_tracts.csv` - All tracts with employment/poverty data
- `data/processed/working_poor_tracts.csv` - Tracts meeting working poor criteria
- `data/processed/demographic_comparison.csv` - Working poor vs. other tracts
- `data/processed/summary_by_county.csv` - County-level breakdown

## Key Variables

| Variable | ACS Table | Description |
|----------|-----------|-------------|
| Employment rate | B23025 | % population 16+ employed (civilian labor force) |
| Full-time rate | B23027 | % workers employed 35+ hours/week, 50+ weeks/year |
| Poverty rate | B17001 | % population below federal poverty level |
| Median income | B19013 | Median household income |
| Cost burden | B25070 | % renters paying 30%+ of income on housing |

## Citation

If you use this analysis, please cite:

> Too Early to Say. (2025). When Work Isn't Enough: What Census Data Reveals About Silicon Valley's Working Poor. https://tooearlytosay.com/working-poor-silicon-valley/

## License

Code: MIT License
Created data: CC-BY 4.0
