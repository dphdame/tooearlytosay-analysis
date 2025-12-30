"""
01_acquire_census_data.py

Downloads ACS 5-year estimates for Bay Area census tracts.

Variables downloaded:
- Employment status (B23025)
- Work schedule (B23027)
- Poverty status (B17001)
- Household income (B19013)
- Rent burden (B25070)

Output: data/processed/bay_area_acs_data.csv
"""

import os
import pandas as pd
from pathlib import Path
from census import Census
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"

# California FIPS
CA_FIPS = "06"

# Bay Area county FIPS codes
BAY_AREA_COUNTIES = {
    "001": "Alameda",
    "013": "Contra Costa",
    "041": "Marin",
    "055": "Napa",
    "075": "San Francisco",
    "081": "San Mateo",
    "085": "Santa Clara",
    "095": "Solano",
    "097": "Sonoma"
}


def get_census_client() -> Census:
    """Initialize Census API client."""
    api_key = os.getenv("CENSUS_API_KEY")

    if not api_key:
        raise ValueError(
            "CENSUS_API_KEY not found in environment.\n"
            "Get a free key at: https://api.census.gov/data/key_signup.html\n"
            "Add to .env file: CENSUS_API_KEY=your_key_here"
        )

    return Census(api_key)


def download_employment_data(c: Census) -> pd.DataFrame:
    """
    Download employment status data.

    Table B23025: Employment Status for the Population 16 Years and Over
    """
    print("Downloading employment data (B23025)...")

    variables = [
        'NAME',
        'B23025_001E',  # Total population 16+
        'B23025_002E',  # In labor force
        'B23025_003E',  # Civilian labor force
        'B23025_004E',  # Employed (civilian)
        'B23025_005E',  # Unemployed
        'B23025_007E',  # Not in labor force
    ]

    all_data = []
    for county_fips, county_name in BAY_AREA_COUNTIES.items():
        print(f"  {county_name}...")
        data = c.acs5.state_county_tract(
            fields=variables,
            state_fips=CA_FIPS,
            county_fips=county_fips,
            tract='*',
            year=2023
        )
        all_data.extend(data)

    df = pd.DataFrame(all_data)

    # Create GEOID
    df['GEOID'] = df['state'] + df['county'] + df['tract']

    # Rename columns
    df = df.rename(columns={
        'B23025_001E': 'pop_16_plus',
        'B23025_002E': 'in_labor_force',
        'B23025_003E': 'civilian_labor_force',
        'B23025_004E': 'employed_civilian',
        'B23025_005E': 'unemployed',
        'B23025_007E': 'not_in_labor_force',
    })

    print(f"  Downloaded {len(df):,} tracts")
    return df


def download_fulltime_data(c: Census) -> pd.DataFrame:
    """
    Download full-time work schedule data.

    Table B23027: Work Status in the Past 12 Months
    Looking for workers who worked 50-52 weeks and usually worked 35+ hours
    """
    print("Downloading full-time work data (B23027)...")

    variables = [
        'B23027_001E',  # Total population 16-64
        'B23027_007E',  # Worked 50-52 weeks, usually 35+ hours (male)
        'B23027_012E',  # Worked 50-52 weeks, usually 35+ hours (female)
    ]

    all_data = []
    for county_fips, county_name in BAY_AREA_COUNTIES.items():
        print(f"  {county_name}...")
        data = c.acs5.state_county_tract(
            fields=variables,
            state_fips=CA_FIPS,
            county_fips=county_fips,
            tract='*',
            year=2023
        )
        all_data.extend(data)

    df = pd.DataFrame(all_data)
    df['GEOID'] = df['state'] + df['county'] + df['tract']

    # Calculate full-time workers
    df['fulltime_workers'] = (
        df['B23027_007E'].astype(float) +
        df['B23027_012E'].astype(float)
    )
    df['pop_16_64'] = df['B23027_001E'].astype(float)

    print(f"  Downloaded {len(df):,} tracts")
    return df[['GEOID', 'pop_16_64', 'fulltime_workers']]


def download_poverty_data(c: Census) -> pd.DataFrame:
    """
    Download poverty status data.

    Table B17001: Poverty Status in the Past 12 Months
    """
    print("Downloading poverty data (B17001)...")

    variables = [
        'B17001_001E',  # Total for poverty determination
        'B17001_002E',  # Income below poverty level
    ]

    all_data = []
    for county_fips, county_name in BAY_AREA_COUNTIES.items():
        print(f"  {county_name}...")
        data = c.acs5.state_county_tract(
            fields=variables,
            state_fips=CA_FIPS,
            county_fips=county_fips,
            tract='*',
            year=2023
        )
        all_data.extend(data)

    df = pd.DataFrame(all_data)
    df['GEOID'] = df['state'] + df['county'] + df['tract']

    df = df.rename(columns={
        'B17001_001E': 'poverty_universe',
        'B17001_002E': 'below_poverty',
    })

    print(f"  Downloaded {len(df):,} tracts")
    return df[['GEOID', 'poverty_universe', 'below_poverty']]


def download_income_data(c: Census) -> pd.DataFrame:
    """
    Download median household income data.

    Table B19013: Median Household Income
    """
    print("Downloading income data (B19013)...")

    variables = [
        'B19013_001E',  # Median household income
    ]

    all_data = []
    for county_fips, county_name in BAY_AREA_COUNTIES.items():
        print(f"  {county_name}...")
        data = c.acs5.state_county_tract(
            fields=variables,
            state_fips=CA_FIPS,
            county_fips=county_fips,
            tract='*',
            year=2023
        )
        all_data.extend(data)

    df = pd.DataFrame(all_data)
    df['GEOID'] = df['state'] + df['county'] + df['tract']

    df = df.rename(columns={
        'B19013_001E': 'median_hh_income',
    })

    print(f"  Downloaded {len(df):,} tracts")
    return df[['GEOID', 'median_hh_income']]


def download_rent_burden_data(c: Census) -> pd.DataFrame:
    """
    Download rent burden data.

    Table B25070: Gross Rent as a Percentage of Household Income
    """
    print("Downloading rent burden data (B25070)...")

    variables = [
        'B25070_001E',  # Total renter-occupied units
        'B25070_007E',  # 30-34.9%
        'B25070_008E',  # 35-39.9%
        'B25070_009E',  # 40-49.9%
        'B25070_010E',  # 50% or more
    ]

    all_data = []
    for county_fips, county_name in BAY_AREA_COUNTIES.items():
        print(f"  {county_name}...")
        data = c.acs5.state_county_tract(
            fields=variables,
            state_fips=CA_FIPS,
            county_fips=county_fips,
            tract='*',
            year=2023
        )
        all_data.extend(data)

    df = pd.DataFrame(all_data)
    df['GEOID'] = df['state'] + df['county'] + df['tract']

    # Calculate rent-burdened households (30%+ of income)
    df['total_renters'] = df['B25070_001E'].astype(float)
    df['rent_burdened'] = (
        df['B25070_007E'].astype(float) +
        df['B25070_008E'].astype(float) +
        df['B25070_009E'].astype(float) +
        df['B25070_010E'].astype(float)
    )

    print(f"  Downloaded {len(df):,} tracts")
    return df[['GEOID', 'total_renters', 'rent_burdened']]


def merge_all_data(dfs: list) -> pd.DataFrame:
    """Merge all downloaded datasets on GEOID."""
    print("\nMerging datasets...")

    result = dfs[0]
    for df in dfs[1:]:
        result = result.merge(df, on='GEOID', how='outer')

    print(f"  Merged dataset: {len(result):,} tracts")
    return result


def calculate_derived_variables(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate derived percentage variables."""
    print("Calculating derived variables...")

    df = df.copy()

    # Employment rate (% of 16+ population employed)
    df['employment_rate'] = (
        df['employed_civilian'].astype(float) /
        df['pop_16_plus'].astype(float).replace(0, pd.NA)
    ) * 100

    # Full-time rate (% of 16-64 working full-time year-round)
    df['fulltime_rate'] = (
        df['fulltime_workers'].astype(float) /
        df['pop_16_64'].astype(float).replace(0, pd.NA)
    ) * 100

    # Poverty rate
    df['poverty_rate'] = (
        df['below_poverty'].astype(float) /
        df['poverty_universe'].astype(float).replace(0, pd.NA)
    ) * 100

    # Rent burden rate
    df['rent_burden_rate'] = (
        df['rent_burdened'].astype(float) /
        df['total_renters'].astype(float).replace(0, pd.NA)
    ) * 100

    # Add county name
    df['county_fips'] = df['GEOID'].str[2:5]
    df['county_name'] = df['county_fips'].map(BAY_AREA_COUNTIES)

    return df


def main():
    """Main data acquisition pipeline."""

    print("=" * 60)
    print("Census Data Acquisition - Bay Area")
    print("=" * 60)

    # Initialize Census client
    c = get_census_client()

    # Download all datasets
    print("\n--- Downloading ACS Data ---")
    employment = download_employment_data(c)
    fulltime = download_fulltime_data(c)
    poverty = download_poverty_data(c)
    income = download_income_data(c)
    rent = download_rent_burden_data(c)

    # Merge datasets
    df = merge_all_data([employment, fulltime, poverty, income, rent])

    # Calculate derived variables
    df = calculate_derived_variables(df)

    # Save output
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    output_path = PROCESSED_DIR / "bay_area_acs_data.csv"
    df.to_csv(output_path, index=False)

    print(f"\nSaved: {output_path}")

    # Summary
    print("\n" + "=" * 60)
    print("Download Summary")
    print("=" * 60)
    print(f"Total tracts: {len(df):,}")
    print(f"Counties: {df['county_name'].nunique()}")
    for county in sorted(df['county_name'].unique()):
        n = (df['county_name'] == county).sum()
        print(f"  {county}: {n:,} tracts")


if __name__ == "__main__":
    main()
