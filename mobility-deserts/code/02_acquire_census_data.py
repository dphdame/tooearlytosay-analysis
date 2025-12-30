"""
02_acquire_census_data.py

Downloads California census tract boundaries and ACS demographic data.

Data sources:
- TIGER/Line Shapefiles (tract boundaries)
- American Community Survey 2019-2023 5-year estimates (demographics)

Outputs:
- data/processed/ca_tracts.gpkg (tract boundaries)
- data/processed/acs_demographics.csv (demographic variables)
"""

import os
import pandas as pd
import geopandas as gpd
from pathlib import Path
from census import Census
from dotenv import load_dotenv
import requests
import zipfile
import io

# Load environment variables
load_dotenv()

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"

# California FIPS code
CA_FIPS = "06"


def download_tiger_tracts(year: int = 2023) -> gpd.GeoDataFrame:
    """
    Download California census tract boundaries from TIGER/Line.

    If already downloaded to raw folder, load from there.
    """
    shapefile_dir = RAW_DIR / f"tl_{year}_{CA_FIPS}_tract"
    shapefile_path = shapefile_dir / f"tl_{year}_{CA_FIPS}_tract.shp"

    if shapefile_path.exists():
        print(f"Loading existing shapefile: {shapefile_path}")
        return gpd.read_file(shapefile_path)

    print(f"Downloading TIGER/Line tracts for California ({year})...")

    # TIGER/Line URL pattern
    url = f"https://www2.census.gov/geo/tiger/TIGER{year}/TRACT/tl_{year}_{CA_FIPS}_tract.zip"

    response = requests.get(url)
    response.raise_for_status()

    # Extract ZIP file
    shapefile_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(io.BytesIO(response.content)) as z:
        z.extractall(shapefile_dir)

    print(f"  Downloaded and extracted to: {shapefile_dir}")

    return gpd.read_file(shapefile_path)


def filter_residential_tracts(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """
    Filter to residential census tracts.

    Excludes:
    - Water-only tracts (ALAND = 0)
    - Tracts with no population (will be filtered after joining demographics)
    """
    print("Filtering to residential tracts...")

    original_count = len(gdf)

    # Filter out water-only tracts
    gdf_land = gdf[gdf['ALAND'] > 0].copy()

    final_count = len(gdf_land)
    print(f"  Land-based tracts: {final_count:,} of {original_count:,}")

    return gdf_land


def get_acs_demographics() -> pd.DataFrame:
    """
    Download ACS 5-year demographic data for California tracts.

    Variables:
    - B01003_001E: Total population
    - B17001_001E: Population for poverty status
    - B17001_002E: Population below poverty level
    - B25044_001E: Total occupied housing units
    - B25044_003E: Owner-occupied, no vehicle
    - B25044_010E: Renter-occupied, no vehicle
    - B25003_001E: Total occupied units (tenure)
    - B25003_003E: Renter-occupied units
    """
    print("Downloading ACS demographic data...")

    api_key = os.getenv("CENSUS_API_KEY")
    if not api_key:
        raise ValueError(
            "CENSUS_API_KEY not found in environment.\n"
            "Get a free key at: https://api.census.gov/data/key_signup.html\n"
            "Add to .env file: CENSUS_API_KEY=your_key_here"
        )

    c = Census(api_key)

    # ACS 5-year estimates (2019-2023)
    variables = [
        'NAME',
        'B01003_001E',  # Total population
        'B17001_001E',  # Pop for poverty determination
        'B17001_002E',  # Pop below poverty
        'B25044_001E',  # Total occupied housing units
        'B25044_003E',  # Owner-occupied, no vehicle
        'B25044_010E',  # Renter-occupied, no vehicle
        'B25003_001E',  # Total occupied units
        'B25003_003E',  # Renter-occupied
    ]

    # Query all California tracts
    data = c.acs5.state_county_tract(
        fields=variables,
        state_fips=CA_FIPS,
        county_fips='*',
        tract='*',
        year=2023
    )

    df = pd.DataFrame(data)
    print(f"  Downloaded data for {len(df):,} tracts")

    # Create GEOID to match with shapefile
    df['GEOID'] = df['state'] + df['county'] + df['tract']

    # Rename columns
    df = df.rename(columns={
        'B01003_001E': 'total_pop',
        'B17001_001E': 'pop_poverty_universe',
        'B17001_002E': 'pop_below_poverty',
        'B25044_001E': 'total_housing_units',
        'B25044_003E': 'owner_no_vehicle',
        'B25044_010E': 'renter_no_vehicle',
        'B25003_001E': 'tenure_total',
        'B25003_003E': 'renter_occupied',
    })

    # Calculate derived variables
    # Poverty rate
    df['poverty_rate'] = (
        df['pop_below_poverty'].astype(float) /
        df['pop_poverty_universe'].astype(float).replace(0, pd.NA)
    ) * 100

    # Households with no vehicle
    df['hh_no_vehicle'] = (
        df['owner_no_vehicle'].astype(float) +
        df['renter_no_vehicle'].astype(float)
    )
    df['pct_no_vehicle'] = (
        df['hh_no_vehicle'] /
        df['total_housing_units'].astype(float).replace(0, pd.NA)
    ) * 100

    # Renter rate
    df['renter_rate'] = (
        df['renter_occupied'].astype(float) /
        df['tenure_total'].astype(float).replace(0, pd.NA)
    ) * 100

    # Select output columns
    output_cols = [
        'GEOID', 'NAME', 'total_pop', 'poverty_rate',
        'pct_no_vehicle', 'renter_rate'
    ]

    return df[output_cols]


def main():
    """Main processing pipeline."""

    print("=" * 60)
    print("Census Data Acquisition")
    print("=" * 60)

    # Download tract boundaries
    print("\n--- Census Tract Boundaries ---")
    tracts = download_tiger_tracts()
    tracts = filter_residential_tracts(tracts)

    # Download ACS demographics
    print("\n--- ACS Demographics ---")
    demographics = get_acs_demographics()

    # Merge demographics with tract boundaries
    print("\n--- Merging Data ---")
    tracts_with_demo = tracts.merge(demographics, on='GEOID', how='left')

    # Filter to residential tracts (population > 0)
    tracts_residential = tracts_with_demo[
        tracts_with_demo['total_pop'].fillna(0) > 0
    ].copy()

    print(f"  Residential tracts with population: {len(tracts_residential):,}")

    # Save outputs
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    # Save GeoPackage with tract boundaries + demographics
    output_gpkg = PROCESSED_DIR / "ca_tracts.gpkg"
    tracts_residential.to_file(output_gpkg, driver="GPKG")
    print(f"\nSaved: {output_gpkg}")

    # Save demographics CSV
    output_csv = PROCESSED_DIR / "acs_demographics.csv"
    demographics.to_csv(output_csv, index=False)
    print(f"Saved: {output_csv}")

    print("\n" + "=" * 60)
    print("Census data processing complete!")
    print(f"Total residential tracts: {len(tracts_residential):,}")
    print("=" * 60)


if __name__ == "__main__":
    main()
