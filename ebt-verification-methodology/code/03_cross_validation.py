#!/usr/bin/env python3
"""
Cross-Validation: Census vs FNS Administrative Data

Author: V Cholette
Purpose: Compare tract-aggregated Census estimates to FNS administrative totals

Approach:
- Sum tract-level Census SNAP households to county total
- Compare to FNS administrative county/state data
- Quantify discrepancy and potential undercount

Usage:
    python 03_cross_validation.py
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
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
OUTPUT_DIR = PROJECT_ROOT / "outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

CENSUS_FILE = PROCESSED_DIR / "snap_validated_substantive.csv"
FNS_FILE = RAW_DIR / "fns_snap_state.csv"

# Known FNS administrative data for California (2022)
# Source: USDA FNS SNAP Data Tables
FNS_CA_2022 = {
    'participants': 4_234_000,  # Average monthly participants
    'households': 1_834_000,   # Average monthly households
    'benefits': 628_000_000    # Average monthly benefits ($)
}

# Santa Clara County share (approximate, based on population)
SCC_POPULATION_SHARE = 0.05  # ~5% of CA population


# ============================================================================
# Cross-Validation
# ============================================================================

def aggregate_census_data(df):
    """Aggregate tract-level data to county totals."""

    total_hh = df['B22003_001E'].sum()
    snap_hh = df['B22003_002E'].sum()

    # Propagate MOE (root sum of squares)
    total_hh_moe = np.sqrt((df['B22003_001M'] ** 2).sum())
    snap_hh_moe = np.sqrt((df['B22003_002M'] ** 2).sum())

    return {
        'total_households': int(total_hh),
        'snap_households': int(snap_hh),
        'snap_rate': snap_hh / total_hh,
        'total_hh_moe': int(total_hh_moe),
        'snap_hh_moe': int(snap_hh_moe)
    }


def compare_to_fns(census_agg, fns_data, pop_share=SCC_POPULATION_SHARE):
    """Compare Census aggregates to FNS administrative data."""

    # Estimate Santa Clara County FNS counts
    fns_estimate = {
        'households': int(fns_data['households'] * pop_share),
        'participants': int(fns_data['participants'] * pop_share)
    }

    # Calculate discrepancy
    discrepancy = census_agg['snap_households'] - fns_estimate['households']
    discrepancy_pct = discrepancy / fns_estimate['households'] * 100

    return {
        'census_snap_hh': census_agg['snap_households'],
        'fns_estimate_hh': fns_estimate['households'],
        'discrepancy': discrepancy,
        'discrepancy_pct': discrepancy_pct,
        'interpretation': (
            'Census likely undercounts' if discrepancy < 0
            else 'Census higher than FNS estimate'
        )
    }


# ============================================================================
# Main
# ============================================================================

def main():
    print("=" * 60)
    print("CROSS-VALIDATION: CENSUS VS FNS")
    print("=" * 60)

    # Load Census data
    if not CENSUS_FILE.exists():
        print(f"\nERROR: Input file not found: {CENSUS_FILE}")
        print("Run script 02_substantive_validation.py first.")
        return

    print(f"\nLoading: {CENSUS_FILE}")
    df = pd.read_csv(CENSUS_FILE)
    print(f"Loaded {len(df)} tracts")

    # Aggregate to county level
    print("\n1. AGGREGATING CENSUS DATA")
    census_agg = aggregate_census_data(df)
    print(f"   Total households: {census_agg['total_households']:,}")
    print(f"   SNAP households: {census_agg['snap_households']:,}")
    print(f"   SNAP rate: {census_agg['snap_rate']:.1%}")

    # Load FNS data (or use default)
    print("\n2. FNS ADMINISTRATIVE DATA")
    if FNS_FILE.exists():
        fns_df = pd.read_csv(FNS_FILE)
        fns_ca = fns_df[fns_df['state'] == 'California'].iloc[0].to_dict()
        print(f"   Loaded from: {FNS_FILE}")
    else:
        fns_ca = FNS_CA_2022
        print(f"   Using default values (FY2022)")

    print(f"   CA SNAP households: {fns_ca['households']:,}")
    print(f"   Estimated SCC share ({SCC_POPULATION_SHARE:.0%}): "
          f"{int(fns_ca['households'] * SCC_POPULATION_SHARE):,}")

    # Compare
    print("\n3. CROSS-VALIDATION COMPARISON")
    comparison = compare_to_fns(census_agg, fns_ca)
    print(f"   Census SNAP HH: {comparison['census_snap_hh']:,}")
    print(f"   FNS estimate HH: {comparison['fns_estimate_hh']:,}")
    print(f"   Discrepancy: {comparison['discrepancy']:+,} ({comparison['discrepancy_pct']:+.1f}%)")
    print(f"   Interpretation: {comparison['interpretation']}")

    # Save results
    print("\n4. SAVING RESULTS")

    results = {
        'census_aggregates': census_agg,
        'fns_comparison': comparison,
        'methodology_notes': {
            'census_source': 'ACS 5-Year (2018-2022) Table B22003',
            'fns_source': 'USDA FNS SNAP Data Tables FY2022',
            'scc_pop_share': SCC_POPULATION_SHARE,
            'limitations': [
                'FNS is administrative count; Census is survey estimate',
                'ACS is 5-year average; FNS is monthly average',
                'County allocation based on population share, not actual counts'
            ]
        }
    }

    results_file = OUTPUT_DIR / "cross_validation_results.json"
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"   Saved: {results_file}")

    # Final summary
    print("\n" + "=" * 60)
    print("CROSS-VALIDATION SUMMARY")
    print("=" * 60)
    print(f"""
Census SNAP households:    {comparison['census_snap_hh']:>10,}
FNS estimated households:  {comparison['fns_estimate_hh']:>10,}
                          {'─' * 12}
Discrepancy:              {comparison['discrepancy']:>+10,} ({comparison['discrepancy_pct']:+.1f}%)

Conclusion: {comparison['interpretation']}

Note: Discrepancy may reflect:
- Survey vs administrative counting differences
- Timing differences (ACS 5-year vs FNS monthly)
- Geographic allocation methodology
""")


if __name__ == "__main__":
    main()
