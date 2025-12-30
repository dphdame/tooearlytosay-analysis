# Data Sources

This document describes all data sources used across projects in this repository.

## U.S. Census Bureau

### American Community Survey (ACS) 5-Year Estimates

**What:** Demographic, economic, and housing data at census tract level

**Access:**
- API: https://api.census.gov/data.html
- Data Explorer: https://data.census.gov/
- API Key (free): https://api.census.gov/data/key_signup.html

**Tables Used:**
| Table | Description | Projects |
|-------|-------------|----------|
| B01003 | Total Population | food-desert-myth, mobility-deserts |
| B17001 | Poverty Status | food-desert-myth, mobility-deserts, working-poor |
| B22003 | SNAP/Food Stamps Receipt | food-desert-myth, ebt-verification |
| B19013 | Median Household Income | food-desert-myth, working-poor |
| B23025 | Employment Status | working-poor |
| B23027 | Weeks Worked (Full-time) | working-poor |
| B25003 | Housing Tenure (Owner/Renter) | food-desert-myth, mobility-deserts |
| B25044 | Vehicles Available | mobility-deserts |
| B25070 | Rent as % of Income | working-poor |

**Geography:** Census tracts in California (FIPS: 06), Santa Clara County (085), Bay Area (001, 013, 041, 055, 075, 081, 085, 095, 097)

**Years:** 2019-2023 ACS 5-year estimates (released 2024)

**Terms of Use:** Public domain. No restrictions on use.

---

## Cal-ITP Transit Data (GTFS)

**What:** Transit stop locations from California's integrated GTFS data pipeline

**Access:**
- Portal: https://data.ca.gov
- Search for "Cal-ITP GTFS" or "California Transit Stops"

**Fields Used:**
- Stop ID, name, coordinates
- Agency information
- Stop type

**Coverage:** 200+ California transit agencies, ~64,000 stops (raw), ~24,000 unique locations (deduplicated)

**Projects:** mobility-deserts

**Terms of Use:** Public data. California Open Data license.

---

## USDA SNAP Retailer Locator

**What:** List of authorized SNAP/EBT retailers with store type classifications

**Access:**
- Web: https://www.fns.usda.gov/snap/retailer-locator
- Data Download: https://snap-retailers-usda-fns.hub.arcgis.com/

**Fields Used:**
- Store name, address, coordinates
- Store type (Supermarket, Convenience Store, etc.)
- Authorization status

**Terms of Use:** Public data. Redistribution allowed with attribution.

---

## Google Maps Places API

**What:** Business listings with category tags, used to validate store classifications

**Access:**
- API Console: https://console.cloud.google.com/
- Places API Documentation: https://developers.google.com/maps/documentation/places/web-service

**Requires:** Google Cloud account and API key (paid, ~$0.017 per request)

**Terms of Use:** Subject to Google Maps Platform Terms of Service. Data cannot be cached long-term or redistributed.

**Note:** Due to API terms, we provide the validation methodology but not the raw Google data. Users must collect their own sample for validation.

---

## Census TIGER/Line Shapefiles

**What:** Geographic boundaries for census tracts

**Access:**
- FTP: https://www.census.gov/geographies/mapping-files/time-series/geo/tiger-line-file.html
- Direct Download: https://www2.census.gov/geo/tiger/

**Files Used:**
- `tl_2023_06_tract.shp` - California census tract boundaries (2023)

**Terms of Use:** Public domain. No restrictions on use.

---

## Data Not Included

This repository does not include:

1. **Raw data files** - Too large, change over time, publicly available
2. **Google Maps API responses** - Terms prohibit redistribution
3. **Processed intermediate files** - Can be regenerated from scripts

Each project's `data/README.md` provides step-by-step instructions to obtain the required datasets.
