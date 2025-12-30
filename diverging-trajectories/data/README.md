# Data Download Instructions

## Multi-Year SNAP Data

Download ACS Table B22003 for multiple years:
- 2019 (ACS 2015-2019)
- 2020 (ACS 2016-2020)
- 2021 (ACS 2017-2021)
- 2022 (ACS 2018-2022)
- 2023 (ACS 2019-2023)

```python
from census import Census
c = Census(api_key)
for year in [2019, 2020, 2021, 2022, 2023]:
    data = c.acs5.state_county_tract(
        fields=['B22003_001E', 'B22003_002E'],
        state_fips='06',
        county_fips='085',  # Santa Clara
        tract='*',
        year=year
    )
```
