"""
07_analyze_demographics.py

Compares demographic characteristics across tract classifications:
- Poverty rates
- Vehicle access (% households without vehicles)
- Renter rates
- Population density

Input: data/processed/tract_classifications.csv
Output: data/processed/demographics_comparison.csv
"""

import pandas as pd
import numpy as np
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
PROCESSED_DIR = DATA_DIR / "processed"


def load_classifications() -> pd.DataFrame:
    """Load tract classification data with demographics."""
    input_path = PROCESSED_DIR / "tract_classifications.csv"

    if not input_path.exists():
        raise FileNotFoundError(
            f"Classification data not found: {input_path}\n"
            "Run 05_classify_tracts.py first."
        )

    df = pd.read_csv(input_path)
    print(f"Loaded {len(df):,} tracts")

    return df


def calculate_summary_stats(
    df: pd.DataFrame,
    variable: str,
    group_col: str = 'classification'
) -> pd.DataFrame:
    """
    Calculate summary statistics for a variable by group.

    Returns mean, median, std, and count for each group.
    """
    stats = df.groupby(group_col)[variable].agg([
        ('mean', 'mean'),
        ('median', 'median'),
        ('std', 'std'),
        ('count', 'count')
    ]).round(2)

    return stats


def compare_demographics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compare demographic variables across classifications.

    Variables:
    - poverty_rate: % population below poverty line
    - pct_no_vehicle: % households without vehicle access
    - renter_rate: % renter-occupied housing units
    """
    print("\nComparing demographics by classification...")

    demographic_vars = ['poverty_rate', 'pct_no_vehicle', 'renter_rate']

    # Filter to available variables
    available_vars = [v for v in demographic_vars if v in df.columns]

    if not available_vars:
        print("WARNING: No demographic variables found in data")
        return pd.DataFrame()

    results = []

    for var in available_vars:
        print(f"\n  {var}:")
        stats = calculate_summary_stats(df, var)

        for classification in stats.index:
            row = {
                'variable': var,
                'classification': classification,
                'mean': stats.loc[classification, 'mean'],
                'median': stats.loc[classification, 'median'],
                'std': stats.loc[classification, 'std'],
                'n_tracts': stats.loc[classification, 'count']
            }
            results.append(row)
            print(f"    {classification}: mean={row['mean']:.1f}%, median={row['median']:.1f}%")

    return pd.DataFrame(results)


def calculate_transit_dependency_risk(df: pd.DataFrame) -> pd.DataFrame:
    """
    Estimate transit-dependent population at risk in mobility deserts.

    Transit-dependent residents = population × (% without vehicle / 100)
    """
    print("\nEstimating transit-dependent population at risk...")

    if 'total_pop' not in df.columns or 'pct_no_vehicle' not in df.columns:
        print("WARNING: Missing population or vehicle data")
        return pd.DataFrame()

    df = df.copy()

    # Estimate transit-dependent population per tract
    df['transit_dependent_pop'] = (
        df['total_pop'] * df['pct_no_vehicle'].fillna(0) / 100
    )

    # Summarize by classification
    summary = df.groupby('classification').agg({
        'total_pop': 'sum',
        'transit_dependent_pop': 'sum',
        'GEOID': 'count'
    }).rename(columns={'GEOID': 'n_tracts'})

    summary['pct_transit_dependent'] = (
        summary['transit_dependent_pop'] / summary['total_pop'] * 100
    ).round(1)

    print("\nTransit-dependent population by classification:")
    for classification in summary.index:
        pop = summary.loc[classification, 'transit_dependent_pop']
        pct = summary.loc[classification, 'pct_transit_dependent']
        print(f"  {classification}: {pop:,.0f} ({pct}%)")

    # Focus on mobility deserts
    if "Mobility Desert" in summary.index:
        md_pop = summary.loc["Mobility Desert", "transit_dependent_pop"]
        print(f"\n  ** Transit-dependent residents in mobility deserts: {md_pop:,.0f} **")

    return summary.reset_index()


def statistical_comparison(df: pd.DataFrame) -> pd.DataFrame:
    """
    Perform statistical tests comparing mobility deserts to other tracts.

    Uses t-test to compare means.
    """
    from scipy import stats

    print("\nStatistical comparison (Mobility Desert vs. Full Access)...")

    mobility_desert = df[df['classification'] == 'Mobility Desert']
    full_access = df[df['classification'] == 'Full Access']

    demographic_vars = ['poverty_rate', 'pct_no_vehicle', 'renter_rate']
    available_vars = [v for v in demographic_vars if v in df.columns]

    results = []

    for var in available_vars:
        md_values = mobility_desert[var].dropna()
        fa_values = full_access[var].dropna()

        if len(md_values) > 0 and len(fa_values) > 0:
            t_stat, p_value = stats.ttest_ind(md_values, fa_values)

            result = {
                'variable': var,
                'mobility_desert_mean': md_values.mean(),
                'full_access_mean': fa_values.mean(),
                'difference': md_values.mean() - fa_values.mean(),
                't_statistic': t_stat,
                'p_value': p_value,
                'significant': p_value < 0.05
            }
            results.append(result)

            sig_marker = "***" if p_value < 0.001 else "**" if p_value < 0.01 else "*" if p_value < 0.05 else ""
            print(f"  {var}: diff={result['difference']:.1f} (p={p_value:.4f}) {sig_marker}")

    return pd.DataFrame(results)


def main():
    """Main demographic analysis pipeline."""

    print("=" * 60)
    print("Demographic Analysis")
    print("=" * 60)

    # Load data
    df = load_classifications()

    # Compare demographics
    comparison = compare_demographics(df)

    if not comparison.empty:
        output_comparison = PROCESSED_DIR / "demographics_comparison.csv"
        comparison.to_csv(output_comparison, index=False)
        print(f"\nSaved: {output_comparison}")

    # Estimate transit-dependent population
    transit_risk = calculate_transit_dependency_risk(df)

    if not transit_risk.empty:
        output_risk = PROCESSED_DIR / "transit_dependency_risk.csv"
        transit_risk.to_csv(output_risk, index=False)
        print(f"Saved: {output_risk}")

    # Statistical comparison
    try:
        stats_results = statistical_comparison(df)
        if not stats_results.empty:
            output_stats = PROCESSED_DIR / "statistical_tests.csv"
            stats_results.to_csv(output_stats, index=False)
            print(f"Saved: {output_stats}")
    except ImportError:
        print("\nNote: scipy not installed, skipping statistical tests")

    print("\n" + "=" * 60)
    print("Demographic analysis complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
