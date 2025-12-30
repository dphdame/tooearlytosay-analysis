# Data Download Instructions

This analysis requires four datasets. Follow these instructions to obtain each.

## 1. Cal-ITP Transit Stops (GTFS Data)

**Source:** California Integrated Travel Project (Cal-ITP)
**URL:** https://data.ca.gov
**Search for:** "Cal-ITP GTFS Ingest Pipeline" or "California Transit Stops"

### Download Steps

1. Go to https://data.ca.gov
2. Search for "GTFS" or "Cal-ITP transit"
3. Download the consolidated stops file (CSV or GeoJSON)
4. Save to `data/raw/calitp_stops.csv`

**Expected columns:** stop_id, stop_name, stop_lat, stop_lon, agency_name

**Note:** The raw dataset contains ~64,000 stops. After deduplication (removing stops at identical coordinates from different feeds), expect ~24,000 unique locations.

## 2. California Census Tract Boundaries

**Source:** U.S. Census Bureau TIGER/Line Shapefiles
**URL:** https://www.census.gov/geographies/mapping-files/time-series/geo/tiger-line-file.html

### Download Steps

1. Go to the TIGER/Line Shapefiles page
2. Select year: 2023 (or most recent)
3. Select layer type: "Census Tracts"
4. Select state: California
5. Download the shapefile (ZIP)
6. Extract to `data/raw/tl_2023_06_tract/`

**Files included:** .shp, .shx, .dbf, .prj

## 3. American Community Survey Demographics

**Source:** Census Bureau API
**Variables needed:**
- Total population
- Poverty rate
- Vehicle access (households with 0 vehicles)
- Renter-occupied housing
- Age distribution

### Option A: Census API (Recommended)

The script `02_acquire_census_data.py` will download this automatically.

1. Get a free API key: https://api.census.gov/data/key_signup.html
2. Add to `.env` file: `CENSUS_API_KEY=your_key_here`
3. Run the script

### Option B: Manual Download

1. Go to https://data.census.gov
2. Search for "ACS 5-Year Estimates" → "Detailed Tables"
3. Geography: California → Census Tracts → All Census Tracts
4. Tables needed:
   - B01003 (Total Population)
   - B17001 (Poverty Status)
   - B25044 (Tenure by Vehicles Available)
   - B25003 (Tenure - Owner/Renter)
5. Download CSV, save to `data/raw/acs_demographics.csv`

## 4. Grocery Store Locations

**Source:** Validated store data from grocery-store-classifier-validation project

### Option A: Use Existing Data

If you've run the `grocery-store-classifier-validation` analysis:

```bash
cp ../grocery-store-classifier-validation/data/processed/validated_stores.csv data/raw/grocery_stores.csv
```

### Option B: USDA SNAP Retailer Data

1. Go to https://www.fns.usda.gov/snap/retailer-locator
2. Download retailer data for California
3. Filter to grocery stores (Store_Type includes "Supermarket", "Grocery")
4. Save to `data/raw/grocery_stores.csv`

**Required columns:** store_id, store_name, latitude, longitude, store_type

## Directory Structure After Download

```
data/
├── raw/
│   ├── calitp_stops.csv           # Transit stop locations
│   ├── tl_2023_06_tract/          # Census tract shapefiles
│   │   ├── tl_2023_06_tract.shp
│   │   ├── tl_2023_06_tract.shx
│   │   ├── tl_2023_06_tract.dbf
│   │   └── tl_2023_06_tract.prj
│   ├── acs_demographics.csv       # ACS data (if manual download)
│   └── grocery_stores.csv         # Grocery store locations
└── processed/
    └── (outputs created by scripts)
```

## Verification

After downloading, verify file sizes:

| File | Expected Size |
|------|---------------|
| calitp_stops.csv | 5-15 MB |
| Census tract shapefile | 10-30 MB |
| grocery_stores.csv | 1-5 MB |
