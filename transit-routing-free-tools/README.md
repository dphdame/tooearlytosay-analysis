# How to Calculate 2.7 Million Transit Routes for Free

Replication materials for ["How to Calculate 2.7 Million Transit Routes for Free"](https://tooearlytosay.com/transit-routing-free-tools/)

## Overview

This project demonstrates calculating multimodal travel times at scale using open-source tools (r5py) instead of commercial APIs, reducing costs from ~$13,500 to $0.

## Data Sources

| Dataset | Source | Access |
|---------|--------|--------|
| Transit schedules | Cal-ITP GTFS | data.ca.gov |
| Street networks | OpenStreetMap | osm.org |
| Origins | Census tract centroids | Census TIGER |
| Destinations | Grocery stores (6,613) | Google Places |

## Methodology

### Routing Engine

r5py (Python wrapper for Conveyal R5):
- Builds transport network from GTFS + OSM
- Calculates walking + transit travel times
- Handles transfers and waiting time

### Parameters

- Departure window: 9:00-11:00 AM (median time used)
- Maximum travel time: 60 minutes
- Modes: Walking + transit only

### Batch Processing

- 50-tract batches to manage memory
- 2,697,704 total origin-destination pairs
- ~6 hours processing time

## Repository Structure

```
transit-routing-free-tools/
├── code/
│   ├── 01_prepare_network.py
│   ├── 02_prepare_origins_destinations.py
│   ├── 03_calculate_travel_times.py
│   └── 04_analyze_accessibility.py
└── data/README.md
```

## Requirements

```bash
pip install r5py geopandas pandas
```

Note: r5py requires Java 11+

## License

Code: MIT License
