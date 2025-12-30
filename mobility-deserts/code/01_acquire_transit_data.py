"""
01_acquire_transit_data.py

Downloads and processes Cal-ITP GTFS transit stop data for California.

Data source: California Integrated Travel Project (Cal-ITP)
URL: https://data.ca.gov

Output: data/processed/transit_stops_clean.csv
"""

import pandas as pd
import geopandas as gpd
from pathlib import Path
import requests
from tqdm import tqdm

# Project paths (relative to script location)
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"


def load_transit_stops(filepath: Path) -> pd.DataFrame:
    """
    Load transit stops from Cal-ITP GTFS data.

    Expected columns: stop_id, stop_name, stop_lat, stop_lon, agency_name
    """
    print(f"Loading transit stops from {filepath}")

    df = pd.read_csv(filepath)

    # Standardize column names (Cal-ITP may use different conventions)
    column_mapping = {
        'stop_latitude': 'stop_lat',
        'stop_longitude': 'stop_lon',
        'latitude': 'stop_lat',
        'longitude': 'stop_lon',
        'lat': 'stop_lat',
        'lon': 'stop_lon',
        'lng': 'stop_lon'
    }
    df = df.rename(columns={k: v for k, v in column_mapping.items() if k in df.columns})

    # Validate required columns
    required = ['stop_lat', 'stop_lon']
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    print(f"  Loaded {len(df):,} transit stops")
    return df


def deduplicate_stops(df: pd.DataFrame, precision: int = 5) -> pd.DataFrame:
    """
    Remove duplicate stops at the same location.

    The raw Cal-ITP data contains ~64,000 stops, but many are duplicates
    from overlapping GTFS feeds. This reduces to ~24,000 unique locations.

    Args:
        df: DataFrame with stop_lat, stop_lon columns
        precision: Decimal places for coordinate rounding (5 = ~1 meter accuracy)

    Returns:
        DataFrame with unique stop locations
    """
    print("Deduplicating stops by location...")

    original_count = len(df)

    # Round coordinates for deduplication
    df['lat_rounded'] = df['stop_lat'].round(precision)
    df['lon_rounded'] = df['stop_lon'].round(precision)

    # Keep first occurrence at each unique location
    df_unique = df.drop_duplicates(subset=['lat_rounded', 'lon_rounded'], keep='first')

    # Clean up temporary columns
    df_unique = df_unique.drop(columns=['lat_rounded', 'lon_rounded'])

    final_count = len(df_unique)
    removed = original_count - final_count

    print(f"  Original stops: {original_count:,}")
    print(f"  Unique locations: {final_count:,}")
    print(f"  Duplicates removed: {removed:,} ({removed/original_count*100:.1f}%)")

    return df_unique


def filter_california_bounds(df: pd.DataFrame) -> pd.DataFrame:
    """
    Filter stops to California bounding box.

    California approximate bounds:
    - Latitude: 32.5° to 42.0°
    - Longitude: -124.5° to -114.0°
    """
    print("Filtering to California bounds...")

    original_count = len(df)

    ca_bounds = {
        'lat_min': 32.5,
        'lat_max': 42.0,
        'lon_min': -124.5,
        'lon_max': -114.0
    }

    df_ca = df[
        (df['stop_lat'] >= ca_bounds['lat_min']) &
        (df['stop_lat'] <= ca_bounds['lat_max']) &
        (df['stop_lon'] >= ca_bounds['lon_min']) &
        (df['stop_lon'] <= ca_bounds['lon_max'])
    ].copy()

    final_count = len(df_ca)
    print(f"  Stops within CA bounds: {final_count:,} of {original_count:,}")

    return df_ca


def create_geodataframe(df: pd.DataFrame) -> gpd.GeoDataFrame:
    """
    Convert DataFrame to GeoDataFrame with point geometry.

    Uses EPSG:4326 (WGS84) as the coordinate reference system.
    """
    print("Creating GeoDataFrame...")

    gdf = gpd.GeoDataFrame(
        df,
        geometry=gpd.points_from_xy(df['stop_lon'], df['stop_lat']),
        crs="EPSG:4326"
    )

    print(f"  Created GeoDataFrame with {len(gdf):,} points")
    return gdf


def main():
    """Main processing pipeline."""

    print("=" * 60)
    print("Transit Stop Data Acquisition")
    print("=" * 60)

    # Check for raw data file
    raw_file = RAW_DIR / "calitp_stops.csv"

    if not raw_file.exists():
        print(f"\nERROR: Raw data file not found: {raw_file}")
        print("\nPlease download Cal-ITP GTFS data:")
        print("  1. Go to https://data.ca.gov")
        print("  2. Search for 'Cal-ITP GTFS' or 'California Transit Stops'")
        print("  3. Download the stops file")
        print(f"  4. Save to: {raw_file}")
        return

    # Load and process
    df = load_transit_stops(raw_file)
    df = filter_california_bounds(df)
    df = deduplicate_stops(df)

    # Convert to GeoDataFrame
    gdf = create_geodataframe(df)

    # Save processed data
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    output_csv = PROCESSED_DIR / "transit_stops_clean.csv"
    output_gpkg = PROCESSED_DIR / "transit_stops_clean.gpkg"

    # Save as CSV (without geometry for smaller file)
    df_out = gdf.drop(columns=['geometry'])
    df_out.to_csv(output_csv, index=False)
    print(f"\nSaved CSV: {output_csv}")

    # Save as GeoPackage (with geometry for spatial operations)
    gdf.to_file(output_gpkg, driver="GPKG")
    print(f"Saved GeoPackage: {output_gpkg}")

    print("\n" + "=" * 60)
    print("Transit data processing complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
