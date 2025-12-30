# Data Download Instructions

This analysis uses American Community Survey data from the U.S. Census Bureau.

## Census API Setup

### Step 1: Get an API Key

1. Go to: https://api.census.gov/data/key_signup.html
2. Fill out the form with your email
3. Check your email for the API key
4. Create a `.env` file in the project root:

```
CENSUS_API_KEY=your_api_key_here
```

### Step 2: Run the Acquisition Script

The script `01_acquire_census_data.py` will automatically download:
- Employment status data (Table B23025)
- Work schedule data (Table B23027)
- Poverty status data (Table B17001)
- Income data (Tables B19001, B19013)
- Housing cost burden data (Table B25070)

```bash
python code/01_acquire_census_data.py
```

## Manual Download (Alternative)

If you prefer to download data manually:

### Option 1: data.census.gov

1. Go to https://data.census.gov
2. Search → Advanced Search
3. Select:
   - Survey: American Community Survey
   - Year: 2023
   - Product: ACS 5-Year Estimates Detailed Tables
4. Geography:
   - Census Tract
   - State: California
   - Counties: Alameda, Contra Costa, Marin, Napa, San Francisco, San Mateo, Santa Clara, Solano, Sonoma
5. Tables needed:
   - B17001 (Poverty Status)
   - B23025 (Employment Status)
   - B23027 (Weeks Worked)
   - B19013 (Median Household Income)
   - B25070 (Gross Rent as Percentage of Income)
6. Download as CSV

### Option 2: Census FTP

Direct download from Census FTP:
https://www2.census.gov/programs-surveys/acs/data/

## Bay Area County FIPS Codes

| County | FIPS Code |
|--------|-----------|
| Alameda | 001 |
| Contra Costa | 013 |
| Marin | 041 |
| Napa | 055 |
| San Francisco | 075 |
| San Mateo | 081 |
| Santa Clara | 085 |
| Solano | 095 |
| Sonoma | 097 |

## Census Tract Boundaries (Optional)

For mapping, download TIGER/Line shapefiles:

1. Go to: https://www.census.gov/geographies/mapping-files/time-series/geo/tiger-line-file.html
2. Download → Year: 2023 → Layer: Census Tracts → State: California
3. Extract the ZIP file to `data/raw/tl_2023_06_tract/`

## Directory Structure After Download

```
data/
├── raw/
│   ├── acs_employment.csv     # Employment status data
│   ├── acs_poverty.csv        # Poverty status data
│   ├── acs_income.csv         # Income data
│   └── tl_2023_06_tract/      # Census tract shapefiles (optional)
└── processed/
    └── (outputs from analysis scripts)
```

## Data Notes

### ACS 5-Year Estimates

- Uses 2019-2023 pooled data for reliable tract-level estimates
- Margins of error are larger for small tracts
- Estimates represent average over the 5-year period

### Poverty Threshold

The federal poverty level varies by household size. For reference:
- 1 person: ~$14,580/year (2023)
- 4 person family: ~$30,000/year (2023)

In the Bay Area, where median home prices exceed $1 million, these thresholds represent severe economic hardship.
