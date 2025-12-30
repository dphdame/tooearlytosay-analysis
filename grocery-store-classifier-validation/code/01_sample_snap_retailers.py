#!/usr/bin/env python3
"""
Sample SNAP Retailers for Validation

Author: V Cholette
Purpose: Select random sample of SNAP retailers for Google Maps validation

Usage:
    python 01_sample_snap_retailers.py
"""

import pandas as pd
import numpy as np
from pathlib import Path

# ============================================================================
# Configuration
# ============================================================================

PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
OUTPUT_DIR = DATA_DIR / "validation"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

INPUT_FILE = RAW_DIR / "snap_retailers_scc.csv"
OUTPUT_FILE = OUTPUT_DIR / "validation_sample.csv"

# Sampling parameters
SAMPLE_SIZE = 400
RANDOM_SEED = 42

# Store types to include
STORE_TYPES = ['Supermarket', 'Super Store', 'Convenience Store',
               'Small Grocery Store', 'Medium Grocery Store']


# ============================================================================
# Main
# ============================================================================

def main():
    print("=" * 60)
    print("SNAP RETAILER SAMPLING")
    print("=" * 60)

    # Load data
    if not INPUT_FILE.exists():
        print(f"\nERROR: Input file not found: {INPUT_FILE}")
        print("\nDownload SNAP retailer data from:")
        print("  https://snap-retailers-usda-fns.hub.arcgis.com/")
        print("\nSee data/README.md for detailed instructions.")
        return

    print(f"\nLoading: {INPUT_FILE}")
    df = pd.read_csv(INPUT_FILE)
    print(f"Total retailers: {len(df)}")

    # Filter to relevant store types
    df_filtered = df[df['Store_Type'].isin(STORE_TYPES)].copy()
    print(f"After filtering to target store types: {len(df_filtered)}")

    # Show distribution
    print("\nStore type distribution:")
    for store_type, count in df_filtered['Store_Type'].value_counts().items():
        print(f"  {store_type}: {count}")

    # Stratified sample to maintain proportions
    np.random.seed(RANDOM_SEED)

    # Calculate sample size per stratum
    type_counts = df_filtered['Store_Type'].value_counts()
    type_proportions = type_counts / len(df_filtered)
    sample_per_type = (type_proportions * SAMPLE_SIZE).round().astype(int)

    # Adjust to hit exact sample size
    diff = SAMPLE_SIZE - sample_per_type.sum()
    if diff != 0:
        sample_per_type.iloc[0] += diff

    # Sample from each stratum
    samples = []
    for store_type, n in sample_per_type.items():
        stratum = df_filtered[df_filtered['Store_Type'] == store_type]
        sample = stratum.sample(n=min(n, len(stratum)), random_state=RANDOM_SEED)
        samples.append(sample)

    sample_df = pd.concat(samples, ignore_index=True)

    # Select columns for validation
    columns = ['Store_Name', 'Address', 'City', 'State', 'Zip5',
               'Store_Type', 'Longitude', 'Latitude']
    columns = [c for c in columns if c in sample_df.columns]
    sample_df = sample_df[columns]

    # Save
    sample_df.to_csv(OUTPUT_FILE, index=False)
    print(f"\n✓ Sample saved: {OUTPUT_FILE}")
    print(f"  Sample size: {len(sample_df)}")

    print("\nSample distribution:")
    for store_type, count in sample_df['Store_Type'].value_counts().items():
        print(f"  {store_type}: {count}")

    print(f"\nNext step: python 02_fetch_google_maps_data.py")


if __name__ == "__main__":
    main()
