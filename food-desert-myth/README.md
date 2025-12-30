# Food Desert Myth: Vulnerability Index Methodology

**Blog Post:** [The Food Desert Myth: Zero Geographic Barriers, Clear Economic Disparities](https://tooearlytosay.com/food-desert-myth/)

## Research Question

Do "food deserts" (areas lacking grocery store access) explain food insecurity in Santa Clara County, or are economic factors more predictive?

## Key Finding

Geographic access is not the barrier. 100% of Santa Clara County census tracts have a grocery store within 1 mile. The vulnerability index shows economic factors (poverty, SNAP participation) are the primary drivers of food insecurity.

## Methodology

This analysis constructs a **composite vulnerability index** at the census tract level using three components:

| Component | Weight | Source | Interpretation |
|-----------|--------|--------|----------------|
| Poverty Rate | 40% | ACS B17001 | Higher = more vulnerable |
| SNAP Participation Rate | 35% | ACS B22003 | Higher = more vulnerable |
| Population Density (inverse) | 25% | ACS + TIGER | Lower density = more isolated |

**Formula:**
```
Vulnerability Index = 0.40 × poverty_norm + 0.35 × snap_norm + 0.25 × (1 - density_norm)
```

Where each component is min-max normalized to [0, 1].

## Data Sources

| Data | Source | Table/File | Geography |
|------|--------|------------|-----------|
| Population, Poverty | ACS 5-Year (2019-2023) | B01003, B17001 | Census Tract |
| SNAP Participation | ACS 5-Year (2019-2023) | B22003 | Census Tract |
| Tract Boundaries | Census TIGER/Line | tl_2023_06_tract.shp | Santa Clara County |

See `data/README.md` for download instructions.

## Scripts

Run in order:

| Script | Purpose | Inputs | Outputs |
|--------|---------|--------|---------|
| `01_acquire_census_data.py` | Download ACS data via Census API | Census API | `data/raw/acs_tracts_scc.csv` |
| `02_calculate_vulnerability_index.py` | Calculate composite index | ACS data, shapefiles | `data/processed/vulnerability_index.csv` |
| `03_create_vulnerability_map.py` | Generate choropleth map | Index data, shapefiles | `outputs/vulnerability_map.png` |
| `04_sensitivity_analysis.py` | Test weight assumptions | Index data | `outputs/sensitivity_results.csv` |

## Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set Census API key (optional but recommended)
export CENSUS_API_KEY="your_key_here"

# Download data (see data/README.md)
# Then run scripts in order
python code/01_acquire_census_data.py
python code/02_calculate_vulnerability_index.py
```

## Output

The vulnerability index assigns each of Santa Clara County's ~400 census tracts to a quintile:

- **Q1 (Lowest)**: Least vulnerable neighborhoods
- **Q2-Q4**: Intermediate vulnerability
- **Q5 (Highest)**: Most vulnerable neighborhoods

## Limitations

1. **Temporal mismatch**: ACS 5-year estimates span 2019-2023; conditions may have changed
2. **Weight sensitivity**: Index values depend on chosen weights (see sensitivity analysis)
3. **Aggregation**: Tract-level data may mask within-tract variation
4. **SNAP undercount**: ACS may underestimate SNAP participation

## Citation

> See blog post at https://tooearlytosay.com/food-desert-myth/

## License

Code: MIT License
Data: Subject to Census Bureau terms (public domain)
