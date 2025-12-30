# Data Download Instructions

## Statewide Census Data

Use Census API to download all California tracts:

```python
from census import Census
c = Census(api_key)
data = c.acs5.state_county_tract(
    fields=['B01003_001E', ...],
    state_fips='06',
    county_fips='*',
    tract='*',
    year=2022
)
```

## Cal-ITP Transit Data

Consolidated GTFS from 200+ agencies:
https://data.ca.gov - search "Cal-ITP"

## Store Locations

SafeGraph Core Places (2023) or alternatives listed in main README.
