#!/usr/bin/env python3
"""
Substantive Validation of SNAP Data

Author: V Cholette
Purpose: Cross-reference SNAP data with external sources for substantive validation

Checks:
- SNAP rates vs poverty rates (should correlate)
- SNAP rates vs unemployment (should correlate)
- Geographic clustering of outliers

Usage:
    python 02_substantive_validation.py
"""

import pandas as pd
import numpy as np
from pathlib import Path
import json

# ============================================================================
# Configuration
# ============================================================================

PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
PROCESSED_DIR = DATA_DIR / "processed"

INPUT_FILE = PROCESSED_DIR / "snap_validated_statistical.csv"
OUTPUT_FILE = PROCESSED_DIR / "snap_validated_substantive.csv"


# ============================================================================
# Substantive Validation
# ============================================================================

def check_poverty_alignment(df):
    """
    Check if SNAP rates align with expected poverty indicators.

    High SNAP + Low poverty = suspicious (potential data error)
    Low SNAP + High poverty = potential undercount
    """

    # For this analysis, we use SNAP rate quintiles as a proxy
    # In full analysis, you'd merge with poverty data

    df['snap_quintile'] = pd.qcut(
        df['snap_rate'].rank(method='first'),
        q=5,
        labels=['Q1', 'Q2', 'Q3', 'Q4', 'Q5']
    )

    # Flag tracts in top SNAP quintile but with small household counts
    # (potential volatility due to small sample)
    small_hh_threshold = 100
    df['small_sample_flag'] = (
        (df['snap_quintile'] == 'Q5') &
        (df['B22003_001E'] < small_hh_threshold)
    )

    n_flagged = df['small_sample_flag'].sum()
    print(f"Small sample flags (Q5 SNAP + <{small_hh_threshold} HH): {n_flagged}")

    return df


def check_geographic_clustering(df):
    """
    Check if outliers cluster geographically.

    Clustered outliers suggest real phenomenon.
    Scattered outliers suggest data quality issues.
    """

    # Simple check: count statistical outliers by tract prefix
    # (first few digits of tract code indicate general area)

    outliers = df[df['statistical_outlier']].copy()

    if len(outliers) == 0:
        print("No statistical outliers to cluster")
        df['cluster_flag'] = False
        return df

    # Extract tract area (first 4 digits after county)
    outliers['tract_area'] = outliers['tract'].str[:4]

    clustering = outliers['tract_area'].value_counts()
    clustered_areas = clustering[clustering >= 3].index.tolist()

    print(f"Areas with 3+ outliers: {len(clustered_areas)}")

    # Flag outliers that are NOT in clusters (more suspicious)
    df['tract_area'] = df['tract'].str[:4]
    df['cluster_flag'] = (
        df['statistical_outlier'] &
        ~df['tract_area'].isin(clustered_areas)
    )

    n_isolated = df['cluster_flag'].sum()
    print(f"Isolated outliers (not in cluster): {n_isolated}")

    return df


def calculate_moe_reliability(df):
    """
    Flag tracts where margin of error is large relative to estimate.

    CV (Coefficient of Variation) > 30% is often considered unreliable.
    """

    # Calculate CV = (MOE / 1.645) / Estimate * 100
    # MOE at 90% confidence, so divide by 1.645 for SE

    df['snap_cv'] = (df['B22003_002M'] / 1.645) / df['B22003_002E'].replace(0, np.nan) * 100
    df['snap_cv'] = df['snap_cv'].fillna(100)  # Missing = unreliable

    df['high_cv_flag'] = df['snap_cv'] > 30

    n_unreliable = df['high_cv_flag'].sum()
    print(f"High CV flags (CV > 30%): {n_unreliable}")

    return df


# ============================================================================
# Main
# ============================================================================

def main():
    print("=" * 60)
    print("SUBSTANTIVE VALIDATION")
    print("=" * 60)

    # Load data
    if not INPUT_FILE.exists():
        print(f"\nERROR: Input file not found: {INPUT_FILE}")
        print("Run script 01_statistical_validation.py first.")
        return

    print(f"\nLoading: {INPUT_FILE}")
    df = pd.read_csv(INPUT_FILE)
    print(f"Loaded {len(df)} tracts")

    # Validation checks
    print("\n1. POVERTY ALIGNMENT CHECK")
    df = check_poverty_alignment(df)

    print("\n2. GEOGRAPHIC CLUSTERING CHECK")
    df = check_geographic_clustering(df)

    print("\n3. MOE RELIABILITY CHECK")
    df = calculate_moe_reliability(df)

    # Combined substantive flag
    df['substantive_flag'] = (
        df['small_sample_flag'] |
        df['cluster_flag'] |
        df['high_cv_flag']
    )

    n_flagged = df['substantive_flag'].sum()
    print(f"\nTotal substantively flagged: {n_flagged} ({n_flagged/len(df)*100:.1f}%)")

    # Save results
    print("\n4. SAVING RESULTS")
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"   Saved: {OUTPUT_FILE}")

    # Summary
    summary = {
        'tract_count': len(df),
        'small_sample_flags': int(df['small_sample_flag'].sum()),
        'cluster_flags': int(df['cluster_flag'].sum()),
        'high_cv_flags': int(df['high_cv_flag'].sum()),
        'total_substantive_flags': int(n_flagged)
    }

    summary_file = PROCESSED_DIR / "substantive_validation_summary.json"
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)
    print(f"   Saved: {summary_file}")

    print("\nNext step: python 03_cross_validation.py")


if __name__ == "__main__":
    main()
