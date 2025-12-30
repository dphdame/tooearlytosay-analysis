#!/usr/bin/env python3
"""
Vulnerability Index Sensitivity Analysis

Author: V Cholette
Purpose: Test how index rankings change under different weight assumptions

Inputs:
- Vulnerability index data (from script 02)

Outputs:
- Sensitivity analysis results
- Weight comparison visualizations

Usage:
    python 04_sensitivity_analysis.py
"""

import pandas as pd
import numpy as np
from pathlib import Path
import json
from itertools import product

# ============================================================================
# Configuration
# ============================================================================

PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_DIR = PROJECT_ROOT / "outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

INPUT_FILE = DATA_DIR / "processed" / "vulnerability_index.csv"

# Weight scenarios to test
WEIGHT_SCENARIOS = {
    'baseline': {'poverty': 0.40, 'snap': 0.35, 'isolation': 0.25},
    'poverty_heavy': {'poverty': 0.60, 'snap': 0.25, 'isolation': 0.15},
    'snap_heavy': {'poverty': 0.25, 'snap': 0.60, 'isolation': 0.15},
    'isolation_heavy': {'poverty': 0.30, 'snap': 0.25, 'isolation': 0.45},
    'equal': {'poverty': 0.333, 'snap': 0.333, 'isolation': 0.334},
}


# ============================================================================
# Analysis Functions
# ============================================================================

def normalize(series):
    """Min-max normalize a series to [0, 1]."""
    min_val = series.min()
    max_val = series.max()
    if max_val == min_val:
        return pd.Series(0, index=series.index)
    return (series - min_val) / (max_val - min_val)


def calculate_index_with_weights(df, poverty_w, snap_w, isolation_w):
    """Calculate vulnerability index with specified weights."""

    poverty_norm = normalize(df['poverty_rate'])
    snap_norm = normalize(df['snap_rate'])
    density_norm = normalize(df['pop_density'])
    isolation_norm = 1 - density_norm  # Invert: lower density = higher isolation

    index = (poverty_w * poverty_norm +
             snap_w * snap_norm +
             isolation_w * isolation_norm)

    return index


def compare_rankings(df, scenarios):
    """Compare tract rankings across weight scenarios."""

    results = {}

    for name, weights in scenarios.items():
        index = calculate_index_with_weights(
            df,
            weights['poverty'],
            weights['snap'],
            weights['isolation']
        )
        df[f'index_{name}'] = index
        df[f'rank_{name}'] = index.rank(ascending=False)

        results[name] = {
            'weights': weights,
            'index_mean': float(index.mean()),
            'index_std': float(index.std())
        }

    # Calculate rank correlations
    rank_cols = [f'rank_{name}' for name in scenarios.keys()]
    correlations = df[rank_cols].corr()

    return results, correlations


def identify_sensitive_tracts(df, scenarios, threshold=20):
    """
    Identify tracts whose rankings change significantly across scenarios.

    Args:
        threshold: Maximum rank change to flag a tract as sensitive
    """

    rank_cols = [f'rank_{name}' for name in scenarios.keys()]

    df['rank_range'] = df[rank_cols].max(axis=1) - df[rank_cols].min(axis=1)
    df['rank_std'] = df[rank_cols].std(axis=1)

    sensitive = df[df['rank_range'] > threshold].copy()

    return sensitive


# ============================================================================
# Main
# ============================================================================

def main():
    print("=" * 60)
    print("SENSITIVITY ANALYSIS")
    print("=" * 60)

    # Load data
    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Input file not found: {INPUT_FILE}\n"
            "Run script 02_calculate_vulnerability_index.py first."
        )

    print(f"\nLoading: {INPUT_FILE}")
    df = pd.read_csv(INPUT_FILE)
    print(f"Loaded {len(df)} tracts")

    # Run sensitivity analysis
    print("\nTesting weight scenarios:")
    for name, weights in WEIGHT_SCENARIOS.items():
        print(f"  {name}: poverty={weights['poverty']}, "
              f"snap={weights['snap']}, isolation={weights['isolation']}")

    results, correlations = compare_rankings(df, WEIGHT_SCENARIOS)

    # Identify sensitive tracts
    sensitive = identify_sensitive_tracts(df, WEIGHT_SCENARIOS, threshold=50)
    print(f"\nTracts with rank change > 50: {len(sensitive)}")

    # Save results
    print("\n" + "=" * 60)
    print("SAVING RESULTS")
    print("=" * 60)

    # 1. Rank correlations
    corr_file = OUTPUT_DIR / "sensitivity_correlations.csv"
    correlations.to_csv(corr_file)
    print(f"\n✓ Correlations: {corr_file}")

    # 2. Sensitive tracts
    sensitive_file = OUTPUT_DIR / "sensitive_tracts.csv"
    if len(sensitive) > 0:
        sensitive[['GEOID', 'NAMELSAD', 'rank_range', 'rank_std']].to_csv(
            sensitive_file, index=False
        )
        print(f"✓ Sensitive tracts: {sensitive_file}")

    # 3. Summary
    summary = {
        'scenarios_tested': len(WEIGHT_SCENARIOS),
        'tract_count': len(df),
        'sensitive_tracts': len(sensitive),
        'scenario_results': results,
        'rank_correlations': correlations.to_dict()
    }

    summary_file = OUTPUT_DIR / "sensitivity_summary.json"
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)
    print(f"✓ Summary: {summary_file}")

    # Print key findings
    print("\n" + "=" * 60)
    print("KEY FINDINGS")
    print("=" * 60)

    print("\nRank Correlations (baseline vs others):")
    for name in WEIGHT_SCENARIOS.keys():
        if name != 'baseline':
            corr = correlations.loc['rank_baseline', f'rank_{name}']
            print(f"  Baseline vs {name}: {corr:.3f}")

    print(f"\nConclusion:")
    min_corr = min(
        correlations.loc['rank_baseline', f'rank_{name}']
        for name in WEIGHT_SCENARIOS.keys() if name != 'baseline'
    )
    if min_corr > 0.9:
        print("  Rankings are ROBUST to weight changes (all correlations > 0.9)")
    elif min_corr > 0.7:
        print("  Rankings are MODERATELY ROBUST (correlations 0.7-0.9)")
    else:
        print("  Rankings are SENSITIVE to weight assumptions (some correlations < 0.7)")


if __name__ == "__main__":
    main()
