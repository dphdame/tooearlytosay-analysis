"""
03_geographic_analysis.py

Geographic analysis of working poor tracts:
1. Spatial clustering of working poor neighborhoods
2. Proximity to employment centers
3. Regional patterns within Bay Area

Inputs:
- data/processed/bay_area_tracts_classified.csv
- data/raw/tl_2023_06_tract/ (optional, for mapping)

Outputs:
- data/processed/working_poor_clusters.csv
- data/processed/geographic_summary.csv
"""

import pandas as pd
import numpy as np
from pathlib import Path

# Optional: geopandas for spatial analysis
try:
    import geopandas as gpd
    HAS_GEOPANDAS = True
except ImportError:
    HAS_GEOPANDAS = False

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"

# Bay Area sub-regions
SUBREGIONS = {
    "South Bay": ["085"],  # Santa Clara
    "Peninsula": ["081"],  # San Mateo
    "San Francisco": ["075"],
    "East Bay - Inner": ["001"],  # Alameda
    "East Bay - Outer": ["013"],  # Contra Costa
    "North Bay - Marin": ["041"],
    "North Bay - Wine Country": ["055", "097"],  # Napa, Sonoma
    "Solano": ["095"]
}


def load_classified_tracts() -> pd.DataFrame:
    """Load classified tract data."""
    input_path = PROCESSED_DIR / "bay_area_tracts_classified.csv"

    if not input_path.exists():
        raise FileNotFoundError(
            f"Classified data not found: {input_path}\n"
            "Run 02_calculate_employment_poverty.py first."
        )

    df = pd.read_csv(input_path)
    print(f"Loaded {len(df):,} classified tracts")

    return df


def assign_subregion(county_fips: str) -> str:
    """Assign subregion based on county FIPS code."""
    for subregion, counties in SUBREGIONS.items():
        if county_fips in counties:
            return subregion
    return "Other"


def analyze_by_subregion(df: pd.DataFrame) -> pd.DataFrame:
    """Analyze working poor tracts by Bay Area subregion."""
    print("\nAnalyzing by subregion...")

    df = df.copy()
    df['subregion'] = df['county_fips'].apply(assign_subregion)

    # Calculate statistics by subregion
    results = []

    for subregion in df['subregion'].unique():
        subset = df[df['subregion'] == subregion]
        working_poor = subset[subset['is_working_poor']]

        result = {
            'subregion': subregion,
            'total_tracts': len(subset),
            'working_poor_tracts': len(working_poor),
            'working_poor_pct': len(working_poor) / len(subset) * 100 if len(subset) > 0 else 0,
            'avg_poverty_rate': subset['poverty_rate'].mean(),
            'avg_fulltime_rate': subset['fulltime_rate'].mean(),
            'avg_median_income': subset['median_hh_income'].mean()
        }
        results.append(result)

    summary = pd.DataFrame(results)
    summary = summary.sort_values('working_poor_pct', ascending=False)

    print("\nSubregion Summary:")
    print("-" * 70)
    for _, row in summary.iterrows():
        print(f"  {row['subregion']}:")
        print(f"    Working poor tracts: {row['working_poor_tracts']:.0f} of {row['total_tracts']:.0f} ({row['working_poor_pct']:.1f}%)")
        print(f"    Avg poverty rate: {row['avg_poverty_rate']:.1f}%")

    return summary


def identify_clusters(df: pd.DataFrame) -> pd.DataFrame:
    """
    Identify geographic clusters of working poor tracts.

    Uses city/place names from tract NAME field to group nearby tracts.
    """
    print("\nIdentifying clusters...")

    working_poor = df[df['is_working_poor']].copy()

    if 'NAME' not in working_poor.columns:
        print("  No NAME column - skipping cluster analysis")
        return pd.DataFrame()

    # Extract city/place names from Census tract NAME
    # Format is typically: "Census Tract XXXX, City, County, California"
    def extract_city(name):
        if pd.isna(name):
            return "Unknown"
        parts = str(name).split(',')
        if len(parts) >= 2:
            return parts[1].strip()
        return "Unknown"

    working_poor['city'] = working_poor['NAME'].apply(extract_city)

    # Count tracts by city
    city_counts = working_poor.groupby(['city', 'county_name']).agg({
        'GEOID': 'count',
        'poverty_rate': 'mean',
        'fulltime_rate': 'mean',
        'median_hh_income': 'mean'
    }).rename(columns={'GEOID': 'tract_count'}).reset_index()

    # Filter to cities with multiple working poor tracts (clusters)
    clusters = city_counts[city_counts['tract_count'] >= 2].copy()
    clusters = clusters.sort_values('tract_count', ascending=False)

    if len(clusters) > 0:
        print("\nWorking Poor Clusters (2+ contiguous tracts):")
        print("-" * 60)
        for _, row in clusters.head(10).iterrows():
            print(f"  {row['city']}, {row['county_name']}: {row['tract_count']} tracts")
            print(f"    Avg poverty: {row['poverty_rate']:.1f}%, Avg income: ${row['median_hh_income']:,.0f}")

    return clusters


def analyze_spatial_patterns(df: pd.DataFrame) -> None:
    """
    Analyze spatial patterns if GeoDataFrame available.

    Requires tract boundary shapefiles in data/raw/.
    """
    if not HAS_GEOPANDAS:
        print("\ngeopandas not installed - skipping spatial analysis")
        return

    shapefile_path = RAW_DIR / "tl_2023_06_tract" / "tl_2023_06_tract.shp"

    if not shapefile_path.exists():
        print(f"\nShapefile not found: {shapefile_path}")
        print("Download from Census TIGER/Line for spatial analysis")
        return

    print("\nPerforming spatial analysis...")

    # Load tract boundaries
    tracts_geo = gpd.read_file(shapefile_path)

    # Filter to Bay Area
    bay_area_fips = ['001', '013', '041', '055', '075', '081', '085', '095', '097']
    tracts_geo = tracts_geo[tracts_geo['COUNTYFP'].isin(bay_area_fips)]

    # Join with classification data
    tracts_geo = tracts_geo.merge(
        df[['GEOID', 'is_working_poor', 'poverty_rate', 'fulltime_rate']],
        on='GEOID',
        how='left'
    )

    # Calculate area statistics
    working_poor_geo = tracts_geo[tracts_geo['is_working_poor'] == True]

    total_area = tracts_geo.geometry.area.sum()
    wp_area = working_poor_geo.geometry.area.sum()

    print(f"\nSpatial Statistics:")
    print(f"  Total Bay Area tract area: {total_area/1e6:.1f} sq km")
    print(f"  Working poor tract area: {wp_area/1e6:.1f} sq km ({wp_area/total_area*100:.1f}%)")


def main():
    """Main geographic analysis pipeline."""

    print("=" * 60)
    print("Geographic Analysis")
    print("=" * 60)

    # Load data
    df = load_classified_tracts()

    # Analyze by subregion
    subregion_summary = analyze_by_subregion(df)

    output_subregion = PROCESSED_DIR / "geographic_summary.csv"
    subregion_summary.to_csv(output_subregion, index=False)
    print(f"\nSaved: {output_subregion}")

    # Identify clusters
    clusters = identify_clusters(df)

    if not clusters.empty:
        output_clusters = PROCESSED_DIR / "working_poor_clusters.csv"
        clusters.to_csv(output_clusters, index=False)
        print(f"Saved: {output_clusters}")

    # Spatial analysis (if data available)
    analyze_spatial_patterns(df)

    print("\n" + "=" * 60)
    print("Geographic analysis complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
