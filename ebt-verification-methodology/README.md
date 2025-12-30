# EBT Verification Methodology

**Blog Post:** [The Retail Density Paradox: Why More Stores Mean Worse Data](https://tooearlytosay.com/ebt-verification-methodology/)

## Research Question

How reliable is USDA SNAP retailer data? What data quality issues emerge in high-density retail areas?

## Key Finding

The "Retail Density Paradox": Areas with more SNAP retailers have **worse** data quality:
- **49%** of stores in high-density areas had classification errors
- After verification, only **12%** of flagged stores were true "mobility deserts"
- Store churn (openings/closings) creates persistent data lag

## Methodology

Three-stage validation pipeline:

1. **Statistical Validation**: Flag outliers using z-scores and IQR methods
2. **Substantive Validation**: Cross-reference with external data sources
3. **Cross-Validation**: Compare Census SNAP estimates to FNS administrative data

## Data Sources

| Data | Source | Purpose |
|------|--------|---------|
| SNAP Retailers | USDA FNS | Store locations and types |
| ACS B22003 | Census Bureau | Household SNAP participation |
| FNS Administrative | USDA | State-level SNAP participation counts |

## Scripts

| Script | Purpose |
|--------|---------|
| `01_statistical_validation.py` | Flag statistical outliers in SNAP data |
| `02_substantive_validation.py` | Cross-reference with external sources |
| `03_cross_validation.py` | Compare Census vs FNS estimates |
| `04_create_validation_summary.py` | Generate summary report |

## Setup

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Download data (see data/README.md)
python code/01_statistical_validation.py
python code/02_substantive_validation.py
python code/03_cross_validation.py
```

## Key Metrics

| Metric | Value | Interpretation |
|--------|-------|----------------|
| Initial "mobility deserts" | 49% | Tracts flagged as lacking access |
| After verification | 12% | True mobility deserts |
| False positive rate | 76% | Flagged tracts that were actually OK |
| Data lag | 6-18 months | Time for USDA to reflect store changes |

## Validation Framework

```
                    ┌─────────────────┐
                    │   Raw SNAP      │
                    │   Data (FNS)    │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
     ┌────────────┐  ┌────────────┐  ┌────────────┐
     │ Statistical│  │Substantive │  │   Cross    │
     │ Validation │  │ Validation │  │ Validation │
     └──────┬─────┘  └──────┬─────┘  └──────┬─────┘
            │               │               │
            └───────────────┼───────────────┘
                            ▼
                    ┌─────────────────┐
                    │   Validated     │
                    │   Dataset       │
                    └─────────────────┘
```

## Limitations

1. **Temporal mismatch**: USDA data updated monthly; Census is 5-year estimate
2. **Geographic aggregation**: Census at tract level; USDA at point level
3. **Definition differences**: "SNAP participant" defined differently across sources

## Citation

> See blog post at https://tooearlytosay.com/ebt-verification-methodology/

## License

Code: MIT License
