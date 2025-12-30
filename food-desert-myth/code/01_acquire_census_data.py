#!/usr/bin/env python3
"""
Census Tract-Level Demographic Data Acquisition for Santa Clara County, CA

Author: V Cholette
Purpose: Acquire ACS 5-year estimates for Santa Clara County census tracts
         from the U.S. Census Bureau API.

Data Sources:
- American Community Survey (ACS) 5-year estimates
- Tables: B01003 (Total Population), B17001 (Poverty Status), B22003 (SNAP Receipt)

Usage:
    python 01_acquire_census_data.py

    Optional: Set CENSUS_API_KEY environment variable for higher rate limits
"""

import os
import requests
import pandas as pd
import json
import hashlib
from datetime import datetime
from pathlib import Path
import sys

# ============================================================================
# Configuration
# ============================================================================

# Use relative paths from project root
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
METADATA_DIR = DATA_DIR / "metadata"

# Ensure directories exist
RAW_DIR.mkdir(parents=True, exist_ok=True)
METADATA_DIR.mkdir(parents=True, exist_ok=True)

# Census API configuration
CENSUS_BASE_URL = "https://api.census.gov/data"
ACS_YEAR = 2022  # Latest available ACS 5-year
ACS_DATASET = "acs/acs5"

# Geographic filters
STATE_FIPS = "06"       # California
COUNTY_FIPS = "085"     # Santa Clara County


# ============================================================================
# Census API Client
# ============================================================================

class CensusDataAcquisition:
    """Handles acquisition and validation of Census data."""

    def __init__(self, api_key=None):
        """
        Initialize Census data acquisition client.

        Args:
            api_key: Census API key (optional, can work without for limited requests)
        """
        self.api_key = api_key or os.environ.get('CENSUS_API_KEY')
        self.base_url = CENSUS_BASE_URL
        self.year = ACS_YEAR
        self.dataset = ACS_DATASET
        self.acquisition_log = []

    def log_acquisition(self, endpoint, status, message, record_count=None):
        """Log acquisition attempt."""
        timestamp = datetime.utcnow().isoformat()
        log_entry = {
            "timestamp": timestamp,
            "endpoint": endpoint,
            "status": status,
            "message": message,
            "record_count": record_count
        }
        self.acquisition_log.append(log_entry)
        print(f"[{timestamp}] {status} | {message}")

    def calculate_checksum(self, data):
        """Calculate SHA-256 checksum for data authenticity."""
        return hashlib.sha256(data.encode('utf-8')).hexdigest()

    def acquire_acs_data(self):
        """
        Acquire ACS data for Santa Clara County tracts.

        Returns:
            pd.DataFrame or None if acquisition fails
        """
        endpoint = f"{self.base_url}/{self.year}/{self.dataset}"

        # Variables to retrieve
        variables = [
            "B01003_001E",  # Total population
            "B17001_001E",  # Total for poverty determination
            "B17001_002E",  # Below poverty level
            "B22003_001E",  # Total households
            "B22003_002E"   # Households receiving SNAP
        ]

        params = {
            "get": ",".join(variables + ["NAME"]),
            "for": "tract:*",
            "in": f"state:{STATE_FIPS} county:{COUNTY_FIPS}"
        }

        if self.api_key:
            params["key"] = self.api_key

        try:
            print(f"\nAcquiring ACS data from Census Bureau...")
            print(f"Endpoint: {endpoint}")
            print(f"Variables: {', '.join(variables)}")

            response = requests.get(endpoint, params=params, timeout=60)

            if response.status_code == 200:
                data = response.json()
                df = pd.DataFrame(data[1:], columns=data[0])

                self.log_acquisition(
                    endpoint, "SUCCESS",
                    f"Retrieved {len(df)} census tracts",
                    len(df)
                )

                # Store raw response for provenance
                self.raw_response = response.text
                self.raw_checksum = self.calculate_checksum(response.text)

                return df
            else:
                self.log_acquisition(
                    endpoint, "FAILURE",
                    f"HTTP {response.status_code}: {response.text}"
                )
                return None

        except requests.exceptions.RequestException as e:
            self.log_acquisition(endpoint, "FAILURE", f"Request failed: {e}")
            return None

    def validate_data(self, df):
        """Perform validation on acquired data."""
        print("\n" + "=" * 60)
        print("DATA VALIDATION")
        print("=" * 60)

        issues = []

        # Check row count (Santa Clara has ~400 tracts)
        print(f"\nRows: {len(df)}")
        if len(df) < 350 or len(df) > 450:
            issues.append(f"Unexpected tract count: {len(df)}")

        # Check for missing values
        numeric_cols = ['B01003_001E', 'B17001_001E', 'B17001_002E',
                        'B22003_001E', 'B22003_002E']
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            missing = df[col].isna().sum()
            if missing > 0:
                print(f"  {col}: {missing} missing values")
                issues.append(f"{col} has {missing} missing values")

        # Check geographic identifiers
        if df['state'].unique().tolist() != [STATE_FIPS]:
            issues.append("Unexpected state FIPS codes")
        if df['county'].unique().tolist() != [COUNTY_FIPS]:
            issues.append("Unexpected county FIPS codes")

        # Summary statistics
        print("\nSummary Statistics:")
        for col in numeric_cols:
            print(f"  {col}: min={df[col].min()}, max={df[col].max()}, "
                  f"mean={df[col].mean():.1f}")

        if issues:
            print(f"\nIssues found: {len(issues)}")
            for issue in issues:
                print(f"  - {issue}")
        else:
            print("\nNo issues found")

        return issues


# ============================================================================
# Main Execution
# ============================================================================

def main():
    """Main execution function."""
    print("=" * 60)
    print("CENSUS DATA ACQUISITION")
    print("Santa Clara County, California")
    print("=" * 60)

    # Initialize client
    client = CensusDataAcquisition()

    if client.api_key:
        print(f"\nUsing Census API key: {client.api_key[:8]}...")
    else:
        print("\nNo API key found. Using unauthenticated requests (rate limited).")
        print("Set CENSUS_API_KEY environment variable for higher limits.")

    # Acquire data
    df = client.acquire_acs_data()

    if df is None:
        print("\nERROR: Failed to acquire Census data")
        print("Check internet connection and try again.")
        sys.exit(1)

    # Validate
    issues = client.validate_data(df)

    # Create GEOID (11-digit tract identifier)
    df['GEOID'] = (df['state'].str.zfill(2) +
                   df['county'].str.zfill(3) +
                   df['tract'].str.zfill(6))

    # Save outputs
    print("\n" + "=" * 60)
    print("SAVING OUTPUTS")
    print("=" * 60)

    # 1. Save cleaned data
    output_file = RAW_DIR / "acs_tracts_scc.csv"
    df.to_csv(output_file, index=False)
    print(f"\n✓ Data saved: {output_file}")

    # 2. Save provenance record
    provenance = {
        "acquired_by": "V Cholette",
        "acquisition_timestamp": datetime.utcnow().isoformat(),
        "source": "U.S. Census Bureau API",
        "dataset": f"ACS 5-Year Estimates ({client.year})",
        "geographic_scope": {
            "state": "California (06)",
            "county": "Santa Clara (085)",
            "level": "Census Tract",
            "tract_count": len(df)
        },
        "data_checksum": client.raw_checksum,
        "validation_issues": issues,
        "acquisition_log": client.acquisition_log
    }

    provenance_file = METADATA_DIR / "acs_provenance.json"
    with open(provenance_file, 'w') as f:
        json.dump(provenance, f, indent=2)
    print(f"✓ Provenance: {provenance_file}")

    # Summary
    print("\n" + "=" * 60)
    print("ACQUISITION COMPLETE")
    print("=" * 60)
    print(f"\nTracts retrieved: {len(df)}")
    print(f"Data checksum: {client.raw_checksum[:16]}...")
    print(f"\nNext step: python 02_calculate_vulnerability_index.py")


if __name__ == "__main__":
    main()
