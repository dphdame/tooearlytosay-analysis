"""
04_demographic_profile.py

Creates demographic profile comparing working poor tracts to other tracts.

Comparisons:
- Income levels
- Housing cost burden
- Employment characteristics
- Statistical significance tests

Input: data/processed/bay_area_tracts_classified.csv
Output: data/processed/demographic_comparison.csv
"""

import pandas as pd
import numpy as np
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
PROCESSED_DIR = DATA_DIR / "processed"


def load_classified_tracts() -> pd.DataFrame:
    """Load classified tract data."""
    input_path = PROCESSED_DIR / "bay_area_tracts_classified.csv"

    if not input_path.exists():
        raise FileNotFoundError(
            f"Classified data not found: {input_path}\n"
            "Run 02_calculate_employment_poverty.py first."
        )

    df = pd.read_csv(input_path)
    print(f"Loaded {len(df):,} tracts")

    return df


def compare_groups(
    df: pd.DataFrame,
    variable: str,
    group_col: str = 'is_working_poor'
) -> dict:
    """
    Compare a variable between working poor and other tracts.

    Returns statistics for both groups.
    """
    working_poor = df[df[group_col] == True][variable].dropna()
    other = df[df[group_col] == False][variable].dropna()

    result = {
        'variable': variable,
        'working_poor_mean': working_poor.mean(),
        'working_poor_median': working_poor.median(),
        'working_poor_std': working_poor.std(),
        'working_poor_n': len(working_poor),
        'other_mean': other.mean(),
        'other_median': other.median(),
        'other_std': other.std(),
        'other_n': len(other),
        'difference': working_poor.mean() - other.mean(),
        'pct_difference': (working_poor.mean() - other.mean()) / other.mean() * 100 if other.mean() != 0 else None
    }

    # Statistical test
    try:
        from scipy import stats
        t_stat, p_value = stats.ttest_ind(working_poor, other)
        result['t_statistic'] = t_stat
        result['p_value'] = p_value
        result['significant'] = p_value < 0.05
    except ImportError:
        result['t_statistic'] = None
        result['p_value'] = None
        result['significant'] = None

    return result


def create_demographic_profile(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create comprehensive demographic comparison.

    Compares all available metrics between working poor and other tracts.
    """
    print("\nCreating demographic profile...")

    # Variables to compare
    variables = [
        'poverty_rate',
        'fulltime_rate',
        'employment_rate',
        'median_hh_income',
        'rent_burden_rate',
    ]

    # Filter to available variables
    available_vars = [v for v in variables if v in df.columns]

    results = []
    for var in available_vars:
        result = compare_groups(df, var)
        results.append(result)

    comparison = pd.DataFrame(results)

    return comparison


def print_profile_summary(comparison: pd.DataFrame) -> None:
    """Print formatted summary of demographic comparison."""
    print("\n" + "=" * 70)
    print("Demographic Profile: Working Poor vs. Other Tracts")
    print("=" * 70)

    for _, row in comparison.iterrows():
        var = row['variable']
        wp_mean = row['working_poor_mean']
        other_mean = row['other_mean']
        diff = row['difference']
        p_val = row.get('p_value')

        # Format based on variable type
        if 'income' in var.lower():
            wp_str = f"${wp_mean:,.0f}"
            other_str = f"${other_mean:,.0f}"
            diff_str = f"${diff:+,.0f}"
        else:
            wp_str = f"{wp_mean:.1f}%"
            other_str = f"{other_mean:.1f}%"
            diff_str = f"{diff:+.1f}pp"

        # Significance marker
        if p_val is not None and p_val < 0.001:
            sig = "***"
        elif p_val is not None and p_val < 0.01:
            sig = "**"
        elif p_val is not None and p_val < 0.05:
            sig = "*"
        else:
            sig = ""

        print(f"\n{var}:")
        print(f"  Working poor tracts: {wp_str}")
        print(f"  Other tracts:        {other_str}")
        print(f"  Difference:          {diff_str} {sig}")


def analyze_income_distribution(df: pd.DataFrame) -> pd.DataFrame:
    """
    Analyze income distribution in working poor vs. other tracts.

    Shows what median income looks like in working poor neighborhoods.
    """
    print("\nIncome Distribution Analysis:")

    working_poor = df[df['is_working_poor'] == True]['median_hh_income'].dropna()
    other = df[df['is_working_poor'] == False]['median_hh_income'].dropna()

    # Income quartiles
    print("\nMedian Household Income Quartiles:")
    print("-" * 50)

    percentiles = [25, 50, 75, 90]
    results = []

    for p in percentiles:
        wp_val = np.percentile(working_poor, p)
        other_val = np.percentile(other, p)
        results.append({
            'percentile': f'P{p}',
            'working_poor': wp_val,
            'other': other_val,
            'difference': wp_val - other_val
        })
        print(f"  {p}th percentile:")
        print(f"    Working poor: ${wp_val:,.0f}")
        print(f"    Other:        ${other_val:,.0f}")

    return pd.DataFrame(results)


def calculate_cost_burden_severity(df: pd.DataFrame) -> None:
    """
    Analyze severity of housing cost burden in working poor tracts.
    """
    if 'rent_burden_rate' not in df.columns:
        return

    print("\nHousing Cost Burden Severity:")
    print("-" * 50)

    working_poor = df[df['is_working_poor'] == True]
    other = df[df['is_working_poor'] == False]

    # What percent have severe burden (>50% of income to rent)?
    # This would require additional variables from B25070

    # For now, compare rent burden rates
    wp_burden = working_poor['rent_burden_rate'].mean()
    other_burden = other['rent_burden_rate'].mean()

    print(f"  Average rent-burdened rate (30%+ income to rent):")
    print(f"    Working poor tracts: {wp_burden:.1f}%")
    print(f"    Other tracts:        {other_burden:.1f}%")


def main():
    """Main demographic profiling pipeline."""

    print("=" * 60)
    print("Demographic Profile Analysis")
    print("=" * 60)

    # Load data
    df = load_classified_tracts()

    # Create comparison
    comparison = create_demographic_profile(df)

    # Print summary
    print_profile_summary(comparison)

    # Income distribution
    income_dist = analyze_income_distribution(df)

    # Cost burden
    calculate_cost_burden_severity(df)

    # Save outputs
    output_comparison = PROCESSED_DIR / "demographic_comparison.csv"
    comparison.to_csv(output_comparison, index=False)
    print(f"\n\nSaved: {output_comparison}")

    output_income = PROCESSED_DIR / "income_distribution.csv"
    income_dist.to_csv(output_income, index=False)
    print(f"Saved: {output_income}")

    print("\n" + "=" * 60)
    print("Demographic profile complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
