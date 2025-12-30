"""
05_classify_tracts.py

Classifies census tracts into food access categories:
1. Traditional Food Desert - grocery store > 1 mile away
2. Mobility Desert - grocery within 1 mile, but poor transit access
3. Full Access - grocery within 1 mile AND adequate transit

Classification logic:
    If grocery distance > 1 mile:
        → Traditional Food Desert
    Else if transit stop > 0.5 miles OR stops within 0.5 miles < 2:
        → Mobility Desert
    Else:
        → Full Access

Input: data/processed/tract_distances.csv
Output: data/processed/tract_classifications.csv
"""

import pandas as pd
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
PROCESSED_DIR = DATA_DIR / "processed"

# Classification thresholds
GROCERY_THRESHOLD_MILES = 1.0  # Federal food desert definition
TRANSIT_DISTANCE_THRESHOLD = 0.5  # Miles to nearest transit stop
TRANSIT_COUNT_THRESHOLD = 2  # Minimum stops within 0.5 miles

# Classification labels
FOOD_DESERT = "Traditional Food Desert"
MOBILITY_DESERT = "Mobility Desert"
FULL_ACCESS = "Full Access"


def load_distance_data() -> pd.DataFrame:
    """Load tract distance calculations."""
    input_path = PROCESSED_DIR / "tract_distances.csv"

    if not input_path.exists():
        raise FileNotFoundError(
            f"Distance data not found: {input_path}\n"
            "Run 04_calculate_distances.py first."
        )

    df = pd.read_csv(input_path)
    print(f"Loaded {len(df):,} tracts with distance data")

    return df


def classify_tract(row: pd.Series) -> str:
    """
    Classify a single tract based on grocery and transit access.

    Args:
        row: DataFrame row with distance metrics

    Returns:
        Classification label
    """
    grocery_dist = row['dist_to_grocery_miles']
    transit_dist = row['dist_to_transit_miles']
    transit_count = row['transit_stops_nearby']

    # Step 1: Check for traditional food desert
    if grocery_dist > GROCERY_THRESHOLD_MILES:
        return FOOD_DESERT

    # Step 2: Check for mobility desert
    # Poor transit = far from any stop OR too few stops nearby
    poor_transit = (
        transit_dist > TRANSIT_DISTANCE_THRESHOLD or
        transit_count < TRANSIT_COUNT_THRESHOLD
    )

    if poor_transit:
        return MOBILITY_DESERT

    # Step 3: Full access
    return FULL_ACCESS


def apply_classification(df: pd.DataFrame) -> pd.DataFrame:
    """Apply classification logic to all tracts."""
    print("\nClassifying tracts...")

    df = df.copy()
    df['classification'] = df.apply(classify_tract, axis=1)

    # Print summary
    counts = df['classification'].value_counts()
    total = len(df)

    print("\nClassification Results:")
    print("-" * 50)
    for category in [FOOD_DESERT, MOBILITY_DESERT, FULL_ACCESS]:
        count = counts.get(category, 0)
        pct = count / total * 100
        print(f"  {category}: {count:,} ({pct:.1f}%)")
    print("-" * 50)
    print(f"  Total: {total:,}")

    return df


def add_transit_status_flags(df: pd.DataFrame) -> pd.DataFrame:
    """Add binary flags for transit access components."""
    df = df.copy()

    # Flag: is tract far from any transit stop?
    df['far_from_transit'] = df['dist_to_transit_miles'] > TRANSIT_DISTANCE_THRESHOLD

    # Flag: does tract have insufficient transit frequency?
    df['insufficient_transit'] = df['transit_stops_nearby'] < TRANSIT_COUNT_THRESHOLD

    # Combined transit access flag
    df['poor_transit_access'] = df['far_from_transit'] | df['insufficient_transit']

    # Grocery access flag
    df['has_grocery_access'] = df['dist_to_grocery_miles'] <= GROCERY_THRESHOLD_MILES

    return df


def main():
    """Main classification pipeline."""

    print("=" * 60)
    print("Tract Classification")
    print("=" * 60)
    print(f"\nClassification thresholds:")
    print(f"  Grocery threshold: {GROCERY_THRESHOLD_MILES} mile")
    print(f"  Transit distance threshold: {TRANSIT_DISTANCE_THRESHOLD} miles")
    print(f"  Minimum transit stops: {TRANSIT_COUNT_THRESHOLD}")

    # Load data
    df = load_distance_data()

    # Classify
    df = apply_classification(df)
    df = add_transit_status_flags(df)

    # Save output
    output_path = PROCESSED_DIR / "tract_classifications.csv"
    df.to_csv(output_path, index=False)
    print(f"\nSaved: {output_path}")

    # Additional insights
    print("\n" + "=" * 60)
    print("Mobility Desert Analysis")
    print("=" * 60)

    mobility_deserts = df[df['classification'] == MOBILITY_DESERT]

    # Why are they mobility deserts?
    far_only = mobility_deserts['far_from_transit'] & ~mobility_deserts['insufficient_transit']
    few_only = ~mobility_deserts['far_from_transit'] & mobility_deserts['insufficient_transit']
    both = mobility_deserts['far_from_transit'] & mobility_deserts['insufficient_transit']

    print(f"\nMobility desert breakdown ({len(mobility_deserts):,} tracts):")
    print(f"  Far from transit only: {far_only.sum():,}")
    print(f"  Too few stops only: {few_only.sum():,}")
    print(f"  Both factors: {both.sum():,}")

    # Affected population estimate
    if 'total_pop' in df.columns:
        affected_pop = mobility_deserts['total_pop'].sum()
        print(f"\nEstimated affected population: {affected_pop:,.0f}")

        # Transit-dependent estimate (no vehicle households)
        if 'pct_no_vehicle' in df.columns:
            transit_dep = (
                mobility_deserts['total_pop'] *
                mobility_deserts['pct_no_vehicle'] / 100
            ).sum()
            print(f"Transit-dependent residents: {transit_dep:,.0f}")


if __name__ == "__main__":
    main()
