# Data Download Instructions

## Required Files

```
data/
├── README.md (this file)
├── raw/
│   ├── acs_snap_tracts.csv (Census API - script 01)
│   └── fns_snap_state.csv (download below)
└── processed/
    └── validation_results.csv (created by scripts)
```

---

## 1. Census ACS SNAP Data (Automated)

**What:** Household SNAP participation by census tract

**Table:** B22003 - Receipt of Food Stamps/SNAP

**How:** Script `01_statistical_validation.py` downloads via Census API.

**Optional:** Get API key from https://api.census.gov/data/key_signup.html

---

## 2. FNS Administrative Data (Manual Download)

**What:** State-level SNAP participation from USDA administrative records

**Download Steps:**

1. Go to: https://www.fns.usda.gov/pd/supplemental-nutrition-assistance-program-snap

2. Download "SNAP State Activity Report" (most recent fiscal year)

3. Extract California data

4. Save as `data/raw/fns_snap_state.csv` with columns:
   - `state`: State name
   - `year`: Fiscal year
   - `month`: Month
   - `participants`: Total SNAP participants
   - `households`: Total SNAP households
   - `benefits`: Total benefits distributed ($)

**Alternative:** Use SNAP Data Tables at:
https://www.fns.usda.gov/pd/supplemental-nutrition-assistance-program-snap

---

## Data Dictionary

### Census ACS B22003

| Variable | Description |
|----------|-------------|
| B22003_001E | Total households |
| B22003_002E | Households receiving SNAP |
| B22003_003E | Households receiving SNAP, income below poverty |
| B22003_004E | Households receiving SNAP, income at/above poverty |

### Derived Variables

| Variable | Formula | Description |
|----------|---------|-------------|
| snap_rate | B22003_002E / B22003_001E | SNAP participation rate |
| snap_poverty_rate | B22003_003E / B22003_002E | % of SNAP households below poverty |

---

## Validation Approach

The scripts implement three validation stages:

1. **Statistical**: Flag tracts with SNAP rates > 2 SD from mean
2. **Substantive**: Check if high SNAP rates align with poverty indicators
3. **Cross-validation**: Compare tract totals to state administrative data

---

## Terms of Use

- **Census Bureau**: Public domain
- **USDA FNS**: Public domain

Both datasets may be freely used and redistributed.
