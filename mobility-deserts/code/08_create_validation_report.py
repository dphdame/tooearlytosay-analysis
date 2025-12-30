"""
08_create_validation_report.py

Documents data quality issues, limitations, and validation checks.

Key documentation:
1. Transit stop count discrepancy (64K raw vs ~24K deduplicated)
2. Grocery store data source and validation
3. Distance calculation methodology
4. Classification threshold sensitivity

Output: data/processed/validation_report.md
"""

import pandas as pd
from pathlib import Path
from datetime import datetime

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
PROCESSED_DIR = DATA_DIR / "processed"


def load_data_for_validation() -> dict:
    """Load all processed data files for validation checks."""
    data = {}

    files = {
        'transit': PROCESSED_DIR / "transit_stops_clean.csv",
        'tracts': PROCESSED_DIR / "tract_distances.csv",
        'classifications': PROCESSED_DIR / "tract_classifications.csv",
        'grocery': PROCESSED_DIR / "grocery_stores_clean.csv"
    }

    for name, path in files.items():
        if path.exists():
            data[name] = pd.read_csv(path)
            print(f"  Loaded {name}: {len(data[name]):,} rows")
        else:
            print(f"  Missing: {path}")
            data[name] = None

    return data


def generate_validation_report(data: dict) -> str:
    """Generate markdown validation report."""

    report = []
    report.append("# Mobility Deserts Analysis - Validation Report")
    report.append(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

    # Section 1: Transit Stop Data
    report.append("\n## 1. Transit Stop Data Quality")
    report.append("\n### Known Issue: Stop Count Discrepancy")
    report.append("""
The Cal-ITP GTFS dataset reports approximately 64,000 transit stops statewide.
After deduplication (removing stops at identical coordinates from overlapping
GTFS feeds), the count reduces to approximately 24,000 unique locations.

This discrepancy occurs because:
- Multiple transit agencies may report the same physical stop
- The GTFS standard uses internal stop IDs that don't deduplicate across agencies
- Transfer points are often duplicated in each agency's feed

**Approach taken:** We deduplicate by rounding coordinates to 5 decimal places
(~1 meter accuracy) and keeping one stop per unique location.
""")

    if data['transit'] is not None:
        n_stops = len(data['transit'])
        report.append(f"\n**Processed stop count:** {n_stops:,}")

    # Section 2: Distance Calculations
    report.append("\n## 2. Distance Calculation Methodology")
    report.append("""
### Coordinate Reference System
- Input data: WGS84 (EPSG:4326)
- Distance calculations: California Albers Equal Area (EPSG:3310)
- Units: Meters, converted to miles for output

### Centroid Approach
Distances are measured from census tract centroids to nearest facilities.

**Limitations:**
- Large tracts may have significant variation in actual distances
- Rural tracts may have centroids far from population centers
- Tract shape irregularities can affect centroid placement

### Thresholds
- Grocery store threshold: 1.0 mile (federal food desert definition)
- Transit stop threshold: 0.5 miles
- Minimum transit stops: 2 within 0.5 miles
""")

    # Section 3: Classification Validation
    report.append("\n## 3. Classification Validation")

    if data['classifications'] is not None:
        df = data['classifications']
        total = len(df)

        # Classification distribution
        report.append("\n### Classification Distribution")
        report.append("| Classification | Count | Percent |")
        report.append("|----------------|-------|---------|")

        for classification in df['classification'].unique():
            count = (df['classification'] == classification).sum()
            pct = count / total * 100
            report.append(f"| {classification} | {count:,} | {pct:.1f}% |")

        # Edge cases
        report.append("\n### Edge Cases Analyzed")

        # Tracts at threshold boundaries
        if 'dist_to_grocery_miles' in df.columns:
            near_grocery_threshold = (
                (df['dist_to_grocery_miles'] > 0.9) &
                (df['dist_to_grocery_miles'] <= 1.1)
            ).sum()
            report.append(f"- Tracts within 0.1 mile of grocery threshold: {near_grocery_threshold:,}")

        if 'dist_to_transit_miles' in df.columns:
            near_transit_threshold = (
                (df['dist_to_transit_miles'] > 0.4) &
                (df['dist_to_transit_miles'] <= 0.6)
            ).sum()
            report.append(f"- Tracts within 0.1 mile of transit threshold: {near_transit_threshold:,}")

    # Section 4: Data Source Limitations
    report.append("\n## 4. Data Source Limitations")
    report.append("""
### Census Tract Boundaries
- Based on 2020 census geography
- Some tracts may have changed since ACS data collection period

### Transit Data
- Point-in-time snapshot (see data acquisition date)
- Does not capture service frequency or hours of operation
- New transit routes added after snapshot are not included
- Temporary route changes during construction not reflected

### Grocery Store Data
- Classification relies on store type labels
- Small independent grocers may be under-represented
- Store closures after data collection not reflected
- Does not distinguish between full-service and limited-service stores

### Temporal Alignment
- ACS data: 2019-2023 5-year estimates
- Transit data: See acquisition date
- Geographic boundaries: 2020 Census
""")

    # Section 5: Sensitivity Analysis Notes
    report.append("\n## 5. Sensitivity Analysis Considerations")
    report.append("""
### Threshold Sensitivity
The following alternative thresholds could be tested:

| Parameter | Default | Alternatives |
|-----------|---------|--------------|
| Grocery distance | 1.0 mi | 0.5 mi, 1.5 mi |
| Transit distance | 0.5 mi | 0.25 mi, 0.75 mi |
| Min transit stops | 2 | 1, 3, 4 |

### Classification Changes with Different Thresholds
[To be completed with sensitivity analysis results]
""")

    # Section 6: Reproducibility
    report.append("\n## 6. Reproducibility Notes")
    report.append("""
### Software Requirements
- Python 3.9+
- geopandas, shapely, pandas (see requirements.txt)

### Environment Variables
- CENSUS_API_KEY: Required for ACS data download

### Data Acquisition
All source data is publicly available. See data/README.md for download instructions.

### Random Seeds
No random processes are used in this analysis.
""")

    return "\n".join(report)


def main():
    """Generate validation report."""

    print("=" * 60)
    print("Validation Report Generation")
    print("=" * 60)

    # Load data
    print("\nLoading data for validation...")
    data = load_data_for_validation()

    # Generate report
    print("\nGenerating report...")
    report = generate_validation_report(data)

    # Save report
    output_path = PROCESSED_DIR / "validation_report.md"
    with open(output_path, 'w') as f:
        f.write(report)

    print(f"\nSaved: {output_path}")

    print("\n" + "=" * 60)
    print("Validation report complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
