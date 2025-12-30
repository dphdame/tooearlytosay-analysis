"""
03_acquire_grocery_data.py

Loads and processes grocery store location data.

Data sources (choose one):
1. Validated store data from grocery-store-classifier-validation project
2. USDA SNAP retailer data

Output: data/processed/grocery_stores_clean.csv
"""

import pandas as pd
import geopandas as gpd
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"

# California bounding box
CA_BOUNDS = {
    'lat_min': 32.5,
    'lat_max': 42.0,
    'lon_min': -124.5,
    'lon_max': -114.0
}


def load_grocery_stores() -> pd.DataFrame:
    """
    Load grocery store data from available sources.

    Tries multiple file locations in order of preference.
    """
    print("Loading grocery store data...")

    # Try validated data from sister project
    validated_path = (
        PROJECT_ROOT.parent /
        "grocery-store-classifier-validation" /
        "data" / "processed" / "validated_stores.csv"
    )

    # Try raw grocery data
    raw_path = RAW_DIR / "grocery_stores.csv"

    # Try USDA SNAP data
    snap_path = RAW_DIR / "snap_retailers.csv"

    for filepath in [validated_path, raw_path, snap_path]:
        if filepath.exists():
            print(f"  Loading from: {filepath}")
            df = pd.read_csv(filepath)
            return df

    raise FileNotFoundError(
        "No grocery store data found. Please download data:\n"
        "  Option 1: Copy from grocery-store-classifier-validation project\n"
        "  Option 2: Download USDA SNAP retailer data\n"
        f"  Save to: {raw_path}"
    )


def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Standardize column names for grocery store data.

    Maps various column naming conventions to standard names.
    """
    print("Standardizing column names...")

    # Common column name variations
    lat_columns = ['latitude', 'lat', 'Latitude', 'LAT', 'y', 'Y']
    lon_columns = ['longitude', 'lon', 'lng', 'Longitude', 'LON', 'LNG', 'x', 'X']
    name_columns = ['store_name', 'name', 'Store_Name', 'NAME', 'business_name']
    type_columns = ['store_type', 'type', 'Store_Type', 'TYPE', 'category']

    column_mapping = {}

    for col in df.columns:
        if col in lat_columns:
            column_mapping[col] = 'latitude'
        elif col in lon_columns:
            column_mapping[col] = 'longitude'
        elif col in name_columns:
            column_mapping[col] = 'store_name'
        elif col in type_columns:
            column_mapping[col] = 'store_type'

    df = df.rename(columns=column_mapping)

    # Validate required columns
    required = ['latitude', 'longitude']
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    return df


def filter_california(df: pd.DataFrame) -> pd.DataFrame:
    """Filter stores to California bounding box."""
    print("Filtering to California...")

    original_count = len(df)

    df_ca = df[
        (df['latitude'] >= CA_BOUNDS['lat_min']) &
        (df['latitude'] <= CA_BOUNDS['lat_max']) &
        (df['longitude'] >= CA_BOUNDS['lon_min']) &
        (df['longitude'] <= CA_BOUNDS['lon_max'])
    ].copy()

    final_count = len(df_ca)
    print(f"  California stores: {final_count:,} of {original_count:,}")

    return df_ca


def filter_grocery_types(df: pd.DataFrame) -> pd.DataFrame:
    """
    Filter to grocery store types only.

    Includes: supermarkets, grocery stores, food stores
    Excludes: convenience stores, gas stations, dollar stores
    """
    print("Filtering to grocery store types...")

    if 'store_type' not in df.columns:
        print("  No store_type column - keeping all stores")
        return df

    original_count = len(df)

    # Store types to include (case-insensitive)
    include_types = [
        'supermarket', 'grocery', 'super market', 'food store',
        'grocer', 'market', 'food mart'
    ]

    # Store types to exclude
    exclude_types = [
        'convenience', 'gas', 'dollar', 'liquor', 'pharmacy',
        'drugstore', 'c-store'
    ]

    # Convert to lowercase for matching
    df['type_lower'] = df['store_type'].str.lower().fillna('')

    # Apply filters
    include_mask = df['type_lower'].str.contains('|'.join(include_types), na=False)
    exclude_mask = df['type_lower'].str.contains('|'.join(exclude_types), na=False)

    # If include patterns found, use them; otherwise keep all non-excluded
    if include_mask.any():
        df_filtered = df[include_mask & ~exclude_mask].copy()
    else:
        df_filtered = df[~exclude_mask].copy()

    df_filtered = df_filtered.drop(columns=['type_lower'])

    final_count = len(df_filtered)
    print(f"  Grocery stores: {final_count:,} of {original_count:,}")

    return df_filtered


def remove_duplicates(df: pd.DataFrame, precision: int = 5) -> pd.DataFrame:
    """Remove duplicate stores at the same location."""
    print("Removing duplicate locations...")

    original_count = len(df)

    # Round coordinates for deduplication
    df['lat_rounded'] = df['latitude'].round(precision)
    df['lon_rounded'] = df['longitude'].round(precision)

    df_unique = df.drop_duplicates(
        subset=['lat_rounded', 'lon_rounded'],
        keep='first'
    )
    df_unique = df_unique.drop(columns=['lat_rounded', 'lon_rounded'])

    final_count = len(df_unique)
    print(f"  Unique locations: {final_count:,} of {original_count:,}")

    return df_unique


def create_geodataframe(df: pd.DataFrame) -> gpd.GeoDataFrame:
    """Convert to GeoDataFrame with point geometry."""
    print("Creating GeoDataFrame...")

    gdf = gpd.GeoDataFrame(
        df,
        geometry=gpd.points_from_xy(df['longitude'], df['latitude']),
        crs="EPSG:4326"
    )

    return gdf


def main():
    """Main processing pipeline."""

    print("=" * 60)
    print("Grocery Store Data Acquisition")
    print("=" * 60)

    # Load data
    df = load_grocery_stores()

    # Process
    df = standardize_columns(df)
    df = filter_california(df)
    df = filter_grocery_types(df)
    df = remove_duplicates(df)

    # Convert to GeoDataFrame
    gdf = create_geodataframe(df)

    # Save outputs
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    # CSV (without geometry)
    output_csv = PROCESSED_DIR / "grocery_stores_clean.csv"
    df_out = df[['latitude', 'longitude'] +
                [c for c in df.columns if c not in ['latitude', 'longitude', 'geometry']]]
    df_out.to_csv(output_csv, index=False)
    print(f"\nSaved: {output_csv}")

    # GeoPackage (with geometry)
    output_gpkg = PROCESSED_DIR / "grocery_stores_clean.gpkg"
    gdf.to_file(output_gpkg, driver="GPKG")
    print(f"Saved: {output_gpkg}")

    print("\n" + "=" * 60)
    print("Grocery store data processing complete!")
    print(f"Total grocery stores: {len(gdf):,}")
    print("=" * 60)


if __name__ == "__main__":
    main()
