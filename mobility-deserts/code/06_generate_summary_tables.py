"""
06_generate_summary_tables.py

Generates summary tables for mobility desert analysis:
1. Statewide summary - counts and percentages by classification
2. Regional breakdown - summary by California region

Input: data/processed/tract_classifications.csv
Outputs:
- data/processed/summary_statewide.csv
- data/processed/summary_by_region.csv
"""

import pandas as pd
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
PROCESSED_DIR = DATA_DIR / "processed"

# California regions by county FIPS
# County FIPS is characters 2-4 of GEOID (state is chars 0-1)
REGIONS = {
    "Los Angeles": ["037"],
    "San Diego": ["073"],
    "Bay Area": ["001", "013", "041", "055", "075", "081", "085", "095", "097"],
    "Central Valley": ["019", "029", "031", "039", "047", "077", "099", "107"],
    "Inland Empire": ["065", "071"],
    "Orange County": ["059"],
    "Central Coast": ["053", "079", "083", "087", "111"],
    "Sacramento Area": ["017", "061", "067", "101", "113", "115"],
    "Other": []  # Catch-all for remaining counties
}


def load_classifications() -> pd.DataFrame:
    """Load tract classification data."""
    input_path = PROCESSED_DIR / "tract_classifications.csv"

    if not input_path.exists():
        raise FileNotFoundError(
            f"Classification data not found: {input_path}\n"
            "Run 05_classify_tracts.py first."
        )

    df = pd.read_csv(input_path)
    print(f"Loaded {len(df):,} classified tracts")

    return df


def extract_county_fips(geoid: str) -> str:
    """Extract county FIPS code from tract GEOID."""
    # GEOID format: SSCCCTTTTTT (state, county, tract)
    return geoid[2:5]


def assign_region(county_fips: str) -> str:
    """Assign region based on county FIPS code."""
    for region, counties in REGIONS.items():
        if county_fips in counties:
            return region
    return "Other"


def generate_statewide_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Generate statewide summary table."""
    print("\nGenerating statewide summary...")

    # Count by classification
    counts = df['classification'].value_counts()

    # Calculate percentages
    total = len(df)
    summary = pd.DataFrame({
        'classification': counts.index,
        'tract_count': counts.values,
        'percent': (counts.values / total * 100).round(1)
    })

    # Add population if available
    if 'total_pop' in df.columns:
        pop_by_class = df.groupby('classification')['total_pop'].sum()
        summary = summary.merge(
            pop_by_class.reset_index().rename(columns={'total_pop': 'population'}),
            on='classification'
        )
        total_pop = df['total_pop'].sum()
        summary['pop_percent'] = (summary['population'] / total_pop * 100).round(1)

    # Order by classification
    order = ["Traditional Food Desert", "Mobility Desert", "Full Access"]
    summary['sort_order'] = summary['classification'].map(
        {c: i for i, c in enumerate(order)}
    )
    summary = summary.sort_values('sort_order').drop(columns=['sort_order'])

    # Add totals row
    totals = pd.DataFrame([{
        'classification': 'TOTAL',
        'tract_count': total,
        'percent': 100.0
    }])
    if 'population' in summary.columns:
        totals['population'] = df['total_pop'].sum()
        totals['pop_percent'] = 100.0

    summary = pd.concat([summary, totals], ignore_index=True)

    print(summary.to_string(index=False))

    return summary


def generate_regional_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Generate summary by California region."""
    print("\nGenerating regional summary...")

    # Add region column
    df = df.copy()
    df['county_fips'] = df['GEOID'].astype(str).str.zfill(11).apply(extract_county_fips)
    df['region'] = df['county_fips'].apply(assign_region)

    # Create pivot table
    pivot = pd.crosstab(
        df['region'],
        df['classification'],
        margins=True,
        margins_name='Total'
    )

    # Calculate percentages
    pct_pivot = pivot.div(pivot['Total'], axis=0) * 100

    # Combine counts and percentages
    result_rows = []
    for region in pivot.index:
        row = {'region': region}
        for classification in pivot.columns:
            if classification != 'Total':
                count = pivot.loc[region, classification]
                pct = pct_pivot.loc[region, classification]
                row[f'{classification}_count'] = count
                row[f'{classification}_pct'] = round(pct, 1)
        row['total_tracts'] = pivot.loc[region, 'Total']
        result_rows.append(row)

    summary = pd.DataFrame(result_rows)

    # Reorder columns
    col_order = ['region', 'total_tracts']
    for classification in ["Traditional Food Desert", "Mobility Desert", "Full Access"]:
        col_order.extend([f'{classification}_count', f'{classification}_pct'])

    summary = summary[[c for c in col_order if c in summary.columns]]

    print(f"\n{summary.to_string(index=False)}")

    return summary


def main():
    """Main summary generation pipeline."""

    print("=" * 60)
    print("Summary Table Generation")
    print("=" * 60)

    # Load data
    df = load_classifications()

    # Generate statewide summary
    statewide = generate_statewide_summary(df)

    output_statewide = PROCESSED_DIR / "summary_statewide.csv"
    statewide.to_csv(output_statewide, index=False)
    print(f"\nSaved: {output_statewide}")

    # Generate regional summary
    regional = generate_regional_summary(df)

    output_regional = PROCESSED_DIR / "summary_by_region.csv"
    regional.to_csv(output_regional, index=False)
    print(f"Saved: {output_regional}")

    print("\n" + "=" * 60)
    print("Summary tables complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
