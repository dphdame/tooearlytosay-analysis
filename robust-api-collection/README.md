# Robust API Data Collection

Replication materials for ["6,613 Stores, $147, Zero Lost Data"](https://tooearlytosay.com/robust-api-data-collection/)

## Overview

This project documents patterns for reliable large-scale API data collection, demonstrated through Google Places API collection of grocery store locations across 7 California counties.

## Data Collection Statistics

| Metric | Value |
|--------|-------|
| Total stores collected | 6,613 |
| API cost | $147.23 |
| Errors recovered | 23 |
| Collection duration | ~6 hours |
| Data loss | Zero |

## Methodology

### Robustness Patterns

1. **Rate limiting**: 5 calls/second enforcement
2. **Checkpointing**: Resume from last successful batch
3. **Incremental saves**: 20 records per batch file
4. **Retry logic**: Exponential backoff for transient errors

### Counties Covered

Santa Clara, Alameda, San Mateo, Contra Costa, San Francisco, Fresno, Kern

## Repository Structure

```
robust-api-collection/
├── code/
│   ├── 01_setup_collection.py
│   ├── 02_collect_with_checkpoints.py
│   ├── 03_merge_batches.py
│   └── 04_validate_results.py
└── data/README.md
```

## Key Code Pattern

```python
def collect_with_retry(query, max_retries=3):
    for attempt in range(max_retries):
        try:
            result = api.search(query)
            save_checkpoint(result)
            return result
        except TransientError:
            time.sleep(2 ** attempt)
    raise MaxRetriesExceeded
```

## License

Code: MIT License

Note: Google Places API data cannot be redistributed per ToS.
