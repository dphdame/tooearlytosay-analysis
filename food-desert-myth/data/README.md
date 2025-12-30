# Data Download Instructions

This folder should contain the raw data files needed to run the analysis. Data files are not included in the repository because they are:
1. Large (shapefiles can be 100MB+)
2. Publicly available
3. Subject to updates

## Required Files

After downloading, your `data/` folder should look like:

```
data/
├── README.md (this file)
├── raw/
│   └── acs_tracts_scc.csv (created by script 01)
├── external/
│   └── shapefiles/
│       ├── tl_2023_06_tract.shp
│       ├── tl_2023_06_tract.shx
│       ├── tl_2023_06_tract.dbf
│       └── tl_2023_06_tract.prj
└── processed/
    └── (created by analysis scripts)
```

---

## 1. Census API Data (Automated)

**What:** ACS 5-Year Estimates for Santa Clara County census tracts

**How:** Script `01_acquire_census_data.py` downloads this automatically via the Census API.

**Optional:** Get a free API key for higher rate limits:
1. Go to https://api.census.gov/data/key_signup.html
2. Enter your email and organization
3. Set environment variable: `export CENSUS_API_KEY="your_key_here"`

---

## 2. Census TIGER/Line Shapefiles (Manual Download)

**What:** Census tract boundary polygons for California

**Download Steps:**

1. Go to: https://www.census.gov/cgi-bin/geo/shapefiles/index.php

2. Select:
   - Year: **2023**
   - Layer Type: **Census Tracts**
   - State: **California**

3. Click "Download" to get `tl_2023_06_tract.zip`

4. Extract and place files in `data/external/shapefiles/`:
   ```bash
   mkdir -p data/external/shapefiles
   unzip tl_2023_06_tract.zip -d data/external/shapefiles/
   ```

**Alternative Direct Link:**
```
https://www2.census.gov/geo/tiger/TIGER2023/TRACT/tl_2023_06_tract.zip
```

**File Size:** ~50MB (zipped), ~150MB (unzipped)

---

## Verification

After downloading, verify files exist:

```bash
# Check shapefile
ls -la data/external/shapefiles/tl_2023_06_tract.*

# Should see:
# tl_2023_06_tract.shp (main geometry file)
# tl_2023_06_tract.shx (index)
# tl_2023_06_tract.dbf (attributes)
# tl_2023_06_tract.prj (projection)
```

---

## Data Dictionary

### ACS Variables Used

| Variable | Table | Description |
|----------|-------|-------------|
| B01003_001E | B01003 | Total population |
| B17001_001E | B17001 | Population for whom poverty status determined |
| B17001_002E | B17001 | Population below poverty level |
| B22003_001E | B22003 | Total households |
| B22003_002E | B22003 | Households receiving SNAP |

### Geographic Identifiers

| Field | Description | Example |
|-------|-------------|---------|
| GEOID | 11-digit tract identifier | 06085500100 |
| state | 2-digit state FIPS | 06 (California) |
| county | 3-digit county FIPS | 085 (Santa Clara) |
| tract | 6-digit tract code | 500100 |

---

## Terms of Use

- **Census Bureau Data**: Public domain, no restrictions
- **TIGER/Line Shapefiles**: Public domain, no restrictions

Attribution appreciated but not required.
