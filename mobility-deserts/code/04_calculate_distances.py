"""
04_calculate_distances.py

Calculates distances from each census tract centroid to:
1. Nearest grocery store
2. Nearest transit stop
3. Number of transit stops within 0.5 miles

Uses projected coordinates (California Albers) for accurate distance calculations.

Inputs:
- data/processed/ca_tracts.gpkg
- data/processed/grocery_stores_clean.gpkg
- data/processed/transit_stops_clean.gpkg

Output: data/processed/tract_distances.csv
"""

import pandas as pd
import geopandas as gpd
import numpy as np
from pathlib import Path
from shapely.ops import nearest_points
from scipy.spatial import cKDTree
from tqdm import tqdm

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
PROCESSED_DIR = DATA_DIR / "processed"

# California Albers Equal Area projection (meters)
CA_ALBERS = "EPSG:3310"

# Distance thresholds (in miles, converted to meters)
MILES_TO_METERS = 1609.34
GROCERY_THRESHOLD_MILES = 1.0
TRANSIT_THRESHOLD_MILES = 0.5


def load_data():
    """Load all required datasets."""
    print("Loading data...")

    # Census tracts
    tracts_path = PROCESSED_DIR / "ca_tracts.gpkg"
    if not tracts_path.exists():
        raise FileNotFoundError(
            f"Census tracts not found: {tracts_path}\n"
            "Run 02_acquire_census_data.py first."
        )
    tracts = gpd.read_file(tracts_path)
    print(f"  Loaded {len(tracts):,} census tracts")

    # Grocery stores
    grocery_path = PROCESSED_DIR / "grocery_stores_clean.gpkg"
    if not grocery_path.exists():
        raise FileNotFoundError(
            f"Grocery stores not found: {grocery_path}\n"
            "Run 03_acquire_grocery_data.py first."
        )
    stores = gpd.read_file(grocery_path)
    print(f"  Loaded {len(stores):,} grocery stores")

    # Transit stops
    transit_path = PROCESSED_DIR / "transit_stops_clean.gpkg"
    if not transit_path.exists():
        raise FileNotFoundError(
            f"Transit stops not found: {transit_path}\n"
            "Run 01_acquire_transit_data.py first."
        )
    transit = gpd.read_file(transit_path)
    print(f"  Loaded {len(transit):,} transit stops")

    return tracts, stores, transit


def project_to_meters(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Project GeoDataFrame to California Albers (meters)."""
    return gdf.to_crs(CA_ALBERS)


def calculate_centroids(tracts: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Calculate tract centroids."""
    print("Calculating tract centroids...")
    tracts = tracts.copy()
    tracts['centroid'] = tracts.geometry.centroid
    return tracts


def build_spatial_index(gdf: gpd.GeoDataFrame) -> cKDTree:
    """Build KD-tree spatial index for fast nearest neighbor queries."""
    coords = np.array([[geom.x, geom.y] for geom in gdf.geometry])
    return cKDTree(coords)


def calculate_nearest_distance(
    tracts: gpd.GeoDataFrame,
    points: gpd.GeoDataFrame,
    point_type: str
) -> pd.Series:
    """
    Calculate distance from each tract centroid to nearest point.

    Uses KD-tree for efficient nearest neighbor search.
    Returns distances in miles.
    """
    print(f"Calculating distance to nearest {point_type}...")

    # Build spatial index
    tree = build_spatial_index(points)

    # Get centroid coordinates
    centroid_coords = np.array([
        [geom.x, geom.y] for geom in tracts['centroid']
    ])

    # Query nearest neighbor
    distances_meters, _ = tree.query(centroid_coords, k=1)

    # Convert to miles
    distances_miles = distances_meters / MILES_TO_METERS

    print(f"  Min: {distances_miles.min():.2f} miles")
    print(f"  Max: {distances_miles.max():.2f} miles")
    print(f"  Mean: {distances_miles.mean():.2f} miles")

    return pd.Series(distances_miles, index=tracts.index)


def count_nearby_stops(
    tracts: gpd.GeoDataFrame,
    transit: gpd.GeoDataFrame,
    radius_miles: float = 0.5
) -> pd.Series:
    """
    Count transit stops within radius of each tract centroid.

    Returns count of stops within specified radius.
    """
    print(f"Counting transit stops within {radius_miles} miles...")

    radius_meters = radius_miles * MILES_TO_METERS

    # Build spatial index
    tree = build_spatial_index(transit)

    # Get centroid coordinates
    centroid_coords = np.array([
        [geom.x, geom.y] for geom in tracts['centroid']
    ])

    # Query all points within radius
    counts = []
    for coord in tqdm(centroid_coords, desc="  Querying"):
        indices = tree.query_ball_point(coord, r=radius_meters)
        counts.append(len(indices))

    counts = pd.Series(counts, index=tracts.index)

    print(f"  Min stops: {counts.min()}")
    print(f"  Max stops: {counts.max()}")
    print(f"  Mean stops: {counts.mean():.1f}")
    print(f"  Tracts with 0 stops: {(counts == 0).sum():,}")
    print(f"  Tracts with <2 stops: {(counts < 2).sum():,}")

    return counts


def main():
    """Main processing pipeline."""

    print("=" * 60)
    print("Distance Calculations")
    print("=" * 60)

    # Load data
    tracts, stores, transit = load_data()

    # Project to meters
    print("\nProjecting to California Albers...")
    tracts = project_to_meters(tracts)
    stores = project_to_meters(stores)
    transit = project_to_meters(transit)

    # Calculate centroids
    tracts = calculate_centroids(tracts)

    # Calculate distances
    print("\n--- Distance Calculations ---")

    tracts['dist_to_grocery_miles'] = calculate_nearest_distance(
        tracts, stores, "grocery store"
    )

    tracts['dist_to_transit_miles'] = calculate_nearest_distance(
        tracts, transit, "transit stop"
    )

    tracts['transit_stops_nearby'] = count_nearby_stops(
        tracts, transit, radius_miles=TRANSIT_THRESHOLD_MILES
    )

    # Create output DataFrame
    output_cols = [
        'GEOID', 'NAME', 'total_pop', 'poverty_rate',
        'pct_no_vehicle', 'renter_rate',
        'dist_to_grocery_miles', 'dist_to_transit_miles', 'transit_stops_nearby'
    ]

    # Select columns that exist
    output_cols = [c for c in output_cols if c in tracts.columns]
    df_out = tracts[output_cols].copy()

    # Save output
    output_path = PROCESSED_DIR / "tract_distances.csv"
    df_out.to_csv(output_path, index=False)
    print(f"\nSaved: {output_path}")

    # Summary statistics
    print("\n" + "=" * 60)
    print("Distance Calculation Summary")
    print("=" * 60)
    print(f"Total tracts: {len(df_out):,}")
    print(f"\nGrocery store access:")
    print(f"  Within 1 mile: {(df_out['dist_to_grocery_miles'] <= 1).sum():,}")
    print(f"  Beyond 1 mile: {(df_out['dist_to_grocery_miles'] > 1).sum():,}")
    print(f"\nTransit access:")
    print(f"  Stop within 0.5 miles: {(df_out['dist_to_transit_miles'] <= 0.5).sum():,}")
    print(f"  No stop within 0.5 miles: {(df_out['dist_to_transit_miles'] > 0.5).sum():,}")
    print(f"  <2 stops within 0.5 miles: {(df_out['transit_stops_nearby'] < 2).sum():,}")


if __name__ == "__main__":
    main()
