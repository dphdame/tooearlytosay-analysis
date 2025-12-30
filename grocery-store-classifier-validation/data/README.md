# Data Download Instructions

## Required Files

```
data/
├── README.md (this file)
├── raw/
│   └── snap_retailers_scc.csv (download instructions below)
├── validation/
│   └── google_maps_results.csv (created by script 02)
└── processed/
    └── validation_results.csv (created by script 03)
```

---

## 1. USDA SNAP Retailer Data

**What:** List of authorized SNAP/EBT retailers with store classifications

**Download Steps:**

1. Go to: https://snap-retailers-usda-fns.hub.arcgis.com/

2. Click "Download" and select CSV format

3. Filter to California (or download all and filter locally)

4. Save as `data/raw/snap_retailers_scc.csv`

**Alternative: Direct API Query**

```python
import requests

# USDA SNAP Retailer API
url = "https://services1.arcgis.com/RLQu0rK7h4kbsBq5/arcgis/rest/services/SNAP_Store_Locations/FeatureServer/0/query"

params = {
    "where": "State='CA' AND County='SANTA CLARA'",
    "outFields": "*",
    "f": "json"
}

response = requests.get(url, params=params)
data = response.json()
```

**Key Fields:**

| Field | Description |
|-------|-------------|
| Store_Name | Business name |
| Address | Street address |
| City | City name |
| State | State code (CA) |
| Zip5 | 5-digit ZIP |
| Store_Type | USDA classification (Supermarket, Convenience, etc.) |
| Longitude | Store longitude |
| Latitude | Store latitude |

---

## 2. Google Maps Validation Data

**What:** Business categories from Google Maps Places API

**How to Collect:**

Script `02_fetch_google_maps_data.py` handles this, but requires:

1. Google Cloud account: https://console.cloud.google.com/
2. Enable Places API
3. Create API key
4. Set environment variable: `export GOOGLE_MAPS_API_KEY="your_key"`

**Cost:** ~$0.017 per request. 400 stores ≈ $7

**API Terms:** Data cannot be cached long-term or redistributed. Each user must query their own sample.

---

## Data Not Included

- **Raw SNAP data**: Public, but subject to frequent updates
- **Google Maps results**: API terms prohibit redistribution
- **Validation labels**: Regenerate by running scripts

---

## Terms of Use

- **USDA SNAP Data**: Public domain
- **Google Maps Data**: Subject to Google Maps Platform Terms of Service
