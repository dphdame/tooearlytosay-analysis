"""
02_calculate_employment_poverty.py

Identifies "working poor" census tracts in the Bay Area.

Definition:
- Employment rate >= 60% (majority of residents work full-time)
- Poverty rate > 10% (significant portion below poverty line)

This captures neighborhoods where most people work but wages don't
cover basic living costs - a hallmark of the Bay Area's cost-of-living crisis.

Input: data/processed/bay_area_acs_data.csv
Output: data/processed/working_poor_tracts.csv
"""

import pandas as pd
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
PROCESSED_DIR = DATA_DIR / "processed"

# Classification thresholds
EMPLOYMENT_THRESHOLD = 60.0  # % of population employed (or full-time working)
POVERTY_THRESHOLD = 10.0     # % below poverty line


def load_acs_data() -> pd.DataFrame:
    """Load Bay Area ACS data."""
    input_path = PROCESSED_DIR / "bay_area_acs_data.csv"

    if not input_path.exists():
        raise FileNotFoundError(
            f"ACS data not found: {input_path}\n"
            "Run 01_acquire_census_data.py first."
        )

    df = pd.read_csv(input_path)
    print(f"Loaded {len(df):,} Bay Area tracts")

    return df


def classify_working_poor(df: pd.DataFrame) -> pd.DataFrame:
    """
    Classify tracts as working poor or not.

    Criteria:
    1. High employment: fulltime_rate >= 60%
    2. Elevated poverty: poverty_rate > 10%
    """
    print(f"\nClassification thresholds:")
    print(f"  Full-time rate >= {EMPLOYMENT_THRESHOLD}%")
    print(f"  Poverty rate > {POVERTY_THRESHOLD}%")

    df = df.copy()

    # Create flags
    df['high_employment'] = df['fulltime_rate'] >= EMPLOYMENT_THRESHOLD
    df['elevated_poverty'] = df['poverty_rate'] > POVERTY_THRESHOLD

    # Working poor = both criteria met
    df['is_working_poor'] = df['high_employment'] & df['elevated_poverty']

    # Summary
    n_high_emp = df['high_employment'].sum()
    n_high_pov = df['elevated_poverty'].sum()
    n_working_poor = df['is_working_poor'].sum()
    total = len(df)

    print(f"\nTract counts:")
    print(f"  High employment (>={EMPLOYMENT_THRESHOLD}%): {n_high_emp:,} ({n_high_emp/total*100:.1f}%)")
    print(f"  Elevated poverty (>{POVERTY_THRESHOLD}%): {n_high_pov:,} ({n_high_pov/total*100:.1f}%)")
    print(f"  Working poor (both): {n_working_poor:,} ({n_working_poor/total*100:.1f}%)")

    return df


def analyze_working_poor_characteristics(df: pd.DataFrame) -> None:
    """Print summary statistics for working poor tracts."""
    working_poor = df[df['is_working_poor']]
    other = df[~df['is_working_poor']]

    print("\n" + "=" * 60)
    print("Working Poor Tract Characteristics")
    print("=" * 60)

    print(f"\nNumber of working poor tracts: {len(working_poor):,}")

    # County distribution
    print("\nBy county:")
    county_counts = working_poor['county_name'].value_counts()
    for county, count in county_counts.items():
        county_total = (df['county_name'] == county).sum()
        pct = count / county_total * 100
        print(f"  {county}: {count} tracts ({pct:.1f}% of county)")

    # Compare key metrics
    print("\nMetric comparison (Working Poor vs. Other Tracts):")
    print("-" * 50)

    metrics = {
        'poverty_rate': 'Poverty Rate',
        'fulltime_rate': 'Full-Time Rate',
        'median_hh_income': 'Median HH Income',
        'rent_burden_rate': 'Rent Burden Rate'
    }

    for var, label in metrics.items():
        if var in df.columns:
            wp_mean = working_poor[var].mean()
            other_mean = other[var].mean()

            if var == 'median_hh_income':
                print(f"  {label}:")
                print(f"    Working poor: ${wp_mean:,.0f}")
                print(f"    Other tracts: ${other_mean:,.0f}")
            else:
                print(f"  {label}:")
                print(f"    Working poor: {wp_mean:.1f}%")
                print(f"    Other tracts: {other_mean:.1f}%")


def main():
    """Main classification pipeline."""

    print("=" * 60)
    print("Working Poor Classification")
    print("=" * 60)

    # Load data
    df = load_acs_data()

    # Filter to valid tracts (with population)
    df = df[df['poverty_universe'].fillna(0) > 0].copy()
    print(f"Tracts with valid data: {len(df):,}")

    # Classify
    df = classify_working_poor(df)

    # Analyze characteristics
    analyze_working_poor_characteristics(df)

    # Save full dataset with classification
    output_all = PROCESSED_DIR / "bay_area_tracts_classified.csv"
    df.to_csv(output_all, index=False)
    print(f"\nSaved: {output_all}")

    # Save working poor tracts only
    working_poor = df[df['is_working_poor']].copy()
    output_wp = PROCESSED_DIR / "working_poor_tracts.csv"
    working_poor.to_csv(output_wp, index=False)
    print(f"Saved: {output_wp}")

    print("\n" + "=" * 60)
    print("Classification complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
