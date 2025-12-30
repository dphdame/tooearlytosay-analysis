"""
01_acquire_census_data.py

Downloads ACS housing tenure data (Table B25003) for California tracts.
"""

import os
import pandas as pd
from pathlib import Path
from census import Census
from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).parent.parent
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

CA_FIPS = "06"


def main():
    api_key = os.getenv("CENSUS_API_KEY")
    if not api_key:
        raise ValueError("CENSUS_API_KEY not found. Get one at: https://api.census.gov/data/key_signup.html")

    c = Census(api_key)

    print("Downloading housing tenure data (B25003)...")

    variables = [
        'NAME',
        'B25003_001E',  # Total occupied units
        'B25003_002E',  # Owner-occupied
        'B25003_003E',  # Renter-occupied
    ]

    data = c.acs5.state_county_tract(
        fields=variables,
        state_fips=CA_FIPS,
        county_fips='*',
        tract='*',
        year=2022
    )

    df = pd.DataFrame(data)
    df['GEOID'] = df['state'] + df['county'] + df['tract']

    df = df.rename(columns={
        'B25003_001E': 'total_occupied',
        'B25003_002E': 'owner_occupied',
        'B25003_003E': 'renter_occupied',
    })

    # Calculate percentages
    df['pct_renter'] = df['renter_occupied'].astype(float) / df['total_occupied'].astype(float).replace(0, pd.NA) * 100
    df['pct_owner'] = df['owner_occupied'].astype(float) / df['total_occupied'].astype(float).replace(0, pd.NA) * 100

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    output_path = PROCESSED_DIR / "housing_tenure.csv"
    df.to_csv(output_path, index=False)

    print(f"Saved {len(df)} tracts to {output_path}")


if __name__ == "__main__":
    main()
