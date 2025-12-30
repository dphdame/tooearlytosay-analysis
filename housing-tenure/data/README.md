# Data Download Instructions

## Census ACS Data

Download housing tenure data (Table B25003) via Census API.

```bash
# Set your Census API key
export CENSUS_API_KEY=your_key_here

# Run acquisition script
python code/01_acquire_census_data.py
```

Get a free API key: https://api.census.gov/data/key_signup.html

## SafeGraph Store Locations

SafeGraph data requires a commercial license. Alternatives:
- USDA SNAP Retailer Data: https://www.fns.usda.gov/snap/retailer-locator
- Google Places API (paid)

## Cal-ITP Transit Data

Download from https://data.ca.gov - search for "Cal-ITP GTFS"
