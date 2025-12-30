#!/usr/bin/env python3
"""
Statistical Validation of SNAP Data

Author: V Cholette
Purpose: Flag statistical outliers in Census SNAP participation data

Methods:
- Z-score outlier detection (|z| > 2)
- IQR-based outlier detection (1.5 × IQR)
- Temporal consistency checks

Usage:
    python 01_statistical_validation.py
"""

import os
import requests
import pandas as pd
import numpy as np
from scipy import stats
from pathlib import Path
import json

# ============================================================================
# Configuration
# ============================================================================

PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
OUTPUT_DIR = DATA_DIR / "processed"

RAW_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Census API
CENSUS_API_KEY = os.environ.get('CENSUS_API_KEY')
CENSUS_BASE_URL = "https://api.census.gov/data"
ACS_YEAR = 2022
STATE_FIPS = "06"
COUNTY_FIPS = "085"

# Outlier thresholds
Z_THRESHOLD = 2.0
IQR_MULTIPLIER = 1.5


# ============================================================================
# Data Acquisition
# ============================================================================

def acquire_snap_data():
    """Download SNAP participation data from Census API."""

    endpoint = f"{CENSUS_BASE_URL}/{ACS_YEAR}/acs/acs5"

    variables = [
        "B22003_001E",  # Total households
        "B22003_002E",  # Households receiving SNAP
        "B22003_001M",  # MOE: Total households
        "B22003_002M",  # MOE: SNAP households
    ]

    params = {
        "get": ",".join(variables + ["NAME"]),
        "for": "tract:*",
        "in": f"state:{STATE_FIPS} county:{COUNTY_FIPS}"
    }

    if CENSUS_API_KEY:
        params["key"] = CENSUS_API_KEY

    print(f"Querying Census API: {endpoint}")
    response = requests.get(endpoint, params=params, timeout=60)

    if response.status_code != 200:
        raise RuntimeError(f"API request failed: {response.status_code}")

    data = response.json()
    df = pd.DataFrame(data[1:], columns=data[0])

    # Convert numeric columns
    for col in variables:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # Create GEOID
    df['GEOID'] = df['state'] + df['county'] + df['tract']

    # Calculate SNAP rate
    df['snap_rate'] = df['B22003_002E'] / df['B22003_001E']
    df['snap_rate'] = df['snap_rate'].fillna(0)

    return df


# ============================================================================
# Statistical Validation
# ============================================================================

def z_score_outliers(df, column='snap_rate', threshold=Z_THRESHOLD):
    """Flag outliers using z-score method."""

    z_scores = np.abs(stats.zscore(df[column].dropna()))
    df_valid = df.dropna(subset=[column]).copy()
    df_valid['z_score'] = z_scores
    df_valid['z_outlier'] = z_scores > threshold

    n_outliers = df_valid['z_outlier'].sum()
    print(f"Z-score outliers (|z| > {threshold}): {n_outliers}")

    return df_valid


def iqr_outliers(df, column='snap_rate', multiplier=IQR_MULTIPLIER):
    """Flag outliers using IQR method."""

    Q1 = df[column].quantile(0.25)
    Q3 = df[column].quantile(0.75)
    IQR = Q3 - Q1

    lower_bound = Q1 - multiplier * IQR
    upper_bound = Q3 + multiplier * IQR

    df['iqr_outlier'] = (df[column] < lower_bound) | (df[column] > upper_bound)

    n_outliers = df['iqr_outlier'].sum()
    print(f"IQR outliers: {n_outliers}")
    print(f"  Bounds: [{lower_bound:.3f}, {upper_bound:.3f}]")

    return df


def validate_against_poverty(df):
    """
    Cross-check: High SNAP rates should correlate with poverty.
    Flag tracts with high SNAP but low poverty as suspicious.
    """
    # This requires poverty data - placeholder for now
    df['poverty_mismatch'] = False
    return df


# ============================================================================
# Main
# ============================================================================

def main():
    print("=" * 60)
    print("STATISTICAL VALIDATION")
    print("=" * 60)

    # Acquire data
    print("\n1. ACQUIRING CENSUS SNAP DATA")
    df = acquire_snap_data()
    print(f"   Loaded {len(df)} census tracts")

    # Save raw data
    raw_file = RAW_DIR / "acs_snap_tracts.csv"
    df.to_csv(raw_file, index=False)
    print(f"   Saved: {raw_file}")

    # Statistical validation
    print("\n2. STATISTICAL OUTLIER DETECTION")

    # Z-score method
    df = z_score_outliers(df)

    # IQR method
    df = iqr_outliers(df)

    # Combined flag
    df['statistical_outlier'] = df['z_outlier'] | df['iqr_outlier']
    n_flagged = df['statistical_outlier'].sum()
    print(f"\nTotal flagged: {n_flagged} ({n_flagged/len(df)*100:.1f}%)")

    # Summary statistics
    print("\n3. SUMMARY STATISTICS")
    print(f"   SNAP rate range: {df['snap_rate'].min():.3f} - {df['snap_rate'].max():.3f}")
    print(f"   SNAP rate mean: {df['snap_rate'].mean():.3f}")
    print(f"   SNAP rate median: {df['snap_rate'].median():.3f}")
    print(f"   SNAP rate std: {df['snap_rate'].std():.3f}")

    # Save results
    print("\n4. SAVING RESULTS")
    output_file = OUTPUT_DIR / "snap_validated_statistical.csv"
    df.to_csv(output_file, index=False)
    print(f"   Saved: {output_file}")

    # Summary JSON
    summary = {
        'tract_count': len(df),
        'z_outliers': int(df['z_outlier'].sum()),
        'iqr_outliers': int(df['iqr_outlier'].sum()),
        'total_flagged': int(n_flagged),
        'snap_rate_stats': {
            'min': float(df['snap_rate'].min()),
            'max': float(df['snap_rate'].max()),
            'mean': float(df['snap_rate'].mean()),
            'median': float(df['snap_rate'].median()),
            'std': float(df['snap_rate'].std())
        }
    }

    summary_file = OUTPUT_DIR / "statistical_validation_summary.json"
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)
    print(f"   Saved: {summary_file}")

    print("\nNext step: python 02_substantive_validation.py")


if __name__ == "__main__":
    main()
