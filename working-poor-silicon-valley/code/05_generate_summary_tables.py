"""
05_generate_summary_tables.py

Generates final summary tables for the working poor analysis:
1. County-level summary
2. Overall Bay Area summary
3. Key findings table

Input: data/processed/bay_area_tracts_classified.csv
Outputs:
- data/processed/summary_by_county.csv
- data/processed/summary_overall.csv
- data/processed/key_findings.csv
"""

import pandas as pd
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
    return df


def generate_county_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Generate summary statistics by county."""
    print("\nGenerating county summary...")

    summary = df.groupby('county_name').agg({
        'GEOID': 'count',
        'is_working_poor': 'sum',
        'poverty_rate': 'mean',
        'fulltime_rate': 'mean',
        'median_hh_income': 'mean',
        'rent_burden_rate': 'mean'
    }).rename(columns={
        'GEOID': 'total_tracts',
        'is_working_poor': 'working_poor_tracts'
    })

    summary['working_poor_pct'] = (
        summary['working_poor_tracts'] / summary['total_tracts'] * 100
    ).round(1)

    # Reorder columns
    summary = summary[[
        'total_tracts', 'working_poor_tracts', 'working_poor_pct',
        'poverty_rate', 'fulltime_rate', 'median_hh_income', 'rent_burden_rate'
    ]]

    summary = summary.round(1)
    summary = summary.sort_values('working_poor_pct', ascending=False)

    print("\nCounty Summary:")
    print("-" * 80)
    print(summary.to_string())

    return summary.reset_index()


def generate_overall_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Generate overall Bay Area summary."""
    print("\nGenerating overall summary...")

    total_tracts = len(df)
    working_poor_tracts = df['is_working_poor'].sum()
    working_poor_pct = working_poor_tracts / total_tracts * 100

    # Working poor characteristics
    wp = df[df['is_working_poor'] == True]
    other = df[df['is_working_poor'] == False]

    summary = pd.DataFrame([
        {
            'metric': 'Total Bay Area tracts',
            'value': total_tracts,
            'unit': 'tracts'
        },
        {
            'metric': 'Working poor tracts',
            'value': working_poor_tracts,
            'unit': 'tracts'
        },
        {
            'metric': 'Working poor percentage',
            'value': round(working_poor_pct, 1),
            'unit': '%'
        },
        {
            'metric': 'Avg poverty rate (working poor)',
            'value': round(wp['poverty_rate'].mean(), 1),
            'unit': '%'
        },
        {
            'metric': 'Avg poverty rate (other)',
            'value': round(other['poverty_rate'].mean(), 1),
            'unit': '%'
        },
        {
            'metric': 'Avg median income (working poor)',
            'value': round(wp['median_hh_income'].mean(), 0),
            'unit': '$'
        },
        {
            'metric': 'Avg median income (other)',
            'value': round(other['median_hh_income'].mean(), 0),
            'unit': '$'
        },
        {
            'metric': 'Avg rent burden (working poor)',
            'value': round(wp['rent_burden_rate'].mean(), 1),
            'unit': '%'
        },
        {
            'metric': 'Avg rent burden (other)',
            'value': round(other['rent_burden_rate'].mean(), 1),
            'unit': '%'
        }
    ])

    print("\nOverall Summary:")
    print("-" * 60)
    for _, row in summary.iterrows():
        if row['unit'] == '$':
            print(f"  {row['metric']}: ${row['value']:,.0f}")
        elif row['unit'] == '%':
            print(f"  {row['metric']}: {row['value']}%")
        else:
            print(f"  {row['metric']}: {row['value']:,.0f}")

    return summary


def generate_key_findings(df: pd.DataFrame) -> pd.DataFrame:
    """Generate key findings table for blog post."""
    print("\nGenerating key findings...")

    wp = df[df['is_working_poor'] == True]
    other = df[df['is_working_poor'] == False]

    findings = []

    # Finding 1: Number of working poor tracts
    findings.append({
        'finding': 'Working poor neighborhoods identified',
        'value': f"{len(wp):,} tracts",
        'context': f"out of {len(df):,} Bay Area tracts"
    })

    # Finding 2: County with most working poor
    county_counts = wp['county_name'].value_counts()
    top_county = county_counts.index[0]
    top_count = county_counts.values[0]
    findings.append({
        'finding': 'County with most working poor tracts',
        'value': top_county,
        'context': f"{top_count} tracts"
    })

    # Finding 3: Income gap
    wp_income = wp['median_hh_income'].mean()
    other_income = other['median_hh_income'].mean()
    income_gap = other_income - wp_income
    findings.append({
        'finding': 'Median income gap',
        'value': f"${income_gap:,.0f}",
        'context': f"Working poor (${wp_income:,.0f}) vs. other (${other_income:,.0f})"
    })

    # Finding 4: Rent burden difference
    wp_burden = wp['rent_burden_rate'].mean()
    other_burden = other['rent_burden_rate'].mean()
    burden_diff = wp_burden - other_burden
    findings.append({
        'finding': 'Rent burden difference',
        'value': f"+{burden_diff:.1f} percentage points",
        'context': f"Working poor ({wp_burden:.1f}%) vs. other ({other_burden:.1f}%)"
    })

    # Finding 5: Poverty rate in working poor tracts
    avg_poverty = wp['poverty_rate'].mean()
    findings.append({
        'finding': 'Average poverty rate in working poor tracts',
        'value': f"{avg_poverty:.1f}%",
        'context': f"Despite {wp['fulltime_rate'].mean():.1f}% full-time employment"
    })

    findings_df = pd.DataFrame(findings)

    print("\nKey Findings:")
    print("-" * 70)
    for _, row in findings_df.iterrows():
        print(f"  • {row['finding']}: {row['value']}")
        print(f"    ({row['context']})")

    return findings_df


def main():
    """Main summary generation pipeline."""

    print("=" * 60)
    print("Summary Table Generation")
    print("=" * 60)

    # Load data
    df = load_classified_tracts()
    print(f"Loaded {len(df):,} tracts")

    # Generate summaries
    county_summary = generate_county_summary(df)
    overall_summary = generate_overall_summary(df)
    key_findings = generate_key_findings(df)

    # Save outputs
    output_county = PROCESSED_DIR / "summary_by_county.csv"
    county_summary.to_csv(output_county, index=False)
    print(f"\nSaved: {output_county}")

    output_overall = PROCESSED_DIR / "summary_overall.csv"
    overall_summary.to_csv(output_overall, index=False)
    print(f"Saved: {output_overall}")

    output_findings = PROCESSED_DIR / "key_findings.csv"
    key_findings.to_csv(output_findings, index=False)
    print(f"Saved: {output_findings}")

    print("\n" + "=" * 60)
    print("Summary generation complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
