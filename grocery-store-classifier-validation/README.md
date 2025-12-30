# Grocery Store Classifier Validation

**Blog Post:** [400 Labels to 94% Accuracy: Validating Grocery Store Data](https://tooearlytosay.com/grocery-store-classifier-validation/)

## Research Question

How accurate are USDA SNAP retailer store type classifications? Can we validate them using Google Maps business data?

## Key Finding

Manual validation of 400 store labels against Google Maps data revealed:
- **94% accuracy** for "Supermarket" classification
- **78% accuracy** for "Convenience Store" classification
- Misclassifications tend to be small grocery stores labeled as convenience stores

## Methodology

1. **Sample Selection**: Random sample of 400 SNAP retailers in Santa Clara County
2. **Ground Truth**: Google Maps Places API to retrieve business categories
3. **Validation**: Compare USDA store type vs Google Maps categories
4. **Metrics**: Precision, recall, F1-score for each store type

## Data Sources

| Data | Source | Access |
|------|--------|--------|
| SNAP Retailers | USDA FNS | https://snap-retailers-usda-fns.hub.arcgis.com/ |
| Store Validation | Google Maps Places API | Requires API key |

**Note:** Due to Google Maps API terms, we cannot redistribute the validation data. Users must collect their own sample.

## Scripts

| Script | Purpose |
|--------|---------|
| `01_sample_snap_retailers.py` | Select random sample from SNAP retailer list |
| `02_fetch_google_maps_data.py` | Query Google Maps for each sampled store |
| `03_calculate_validation_metrics.py` | Compute precision/recall/F1 |

## Setup

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Required: Google Maps API key
export GOOGLE_MAPS_API_KEY="your_key_here"

# Download SNAP retailer data (see data/README.md)
python code/01_sample_snap_retailers.py
python code/02_fetch_google_maps_data.py
python code/03_calculate_validation_metrics.py
```

## Validation Results

| Store Type | Precision | Recall | F1-Score | n |
|------------|-----------|--------|----------|---|
| Supermarket | 0.94 | 0.91 | 0.92 | 156 |
| Convenience | 0.78 | 0.82 | 0.80 | 189 |
| Other | 0.71 | 0.68 | 0.69 | 55 |

## Limitations

1. **API Costs**: Google Maps charges ~$0.017/request
2. **Temporal lag**: USDA data may not reflect recent store changes
3. **Category mapping**: Google categories don't map 1:1 to USDA types
4. **Sample size**: 400 stores from one county may not generalize

## Citation

> See blog post at https://tooearlytosay.com/grocery-store-classifier-validation/

## License

Code: MIT License
