#!/usr/bin/env python3
"""
Calculate Validation Metrics

Author: V Cholette
Purpose: Compute precision, recall, F1-score for store type classifications

Usage:
    python 03_calculate_validation_metrics.py
"""

import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.metrics import classification_report, confusion_matrix
import json

# ============================================================================
# Configuration
# ============================================================================

PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
VALIDATION_DIR = DATA_DIR / "validation"
OUTPUT_DIR = PROJECT_ROOT / "outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

INPUT_FILE = VALIDATION_DIR / "google_maps_results.csv"

# Mapping Google types to USDA categories
GOOGLE_TO_USDA = {
    'supermarket': 'Supermarket',
    'grocery_or_supermarket': 'Supermarket',
    'convenience_store': 'Convenience Store',
    'gas_station': 'Convenience Store',
    'store': 'Small Grocery Store',
    'food': 'Small Grocery Store',
}


# ============================================================================
# Analysis Functions
# ============================================================================

def map_google_types(google_types_str):
    """Map Google types to USDA category."""
    if pd.isna(google_types_str):
        return 'Unknown'

    types = google_types_str.lower().split(',')

    for gtype in types:
        gtype = gtype.strip()
        if gtype in GOOGLE_TO_USDA:
            return GOOGLE_TO_USDA[gtype]

    return 'Other'


def calculate_metrics(df):
    """Calculate classification metrics."""

    # Filter to matched stores
    matched = df[df['match_status'] == 'found'].copy()

    if len(matched) == 0:
        print("No matched stores to analyze")
        return None

    # Map Google types to categories
    matched['predicted_type'] = matched['google_types'].apply(map_google_types)

    # Simplify USDA types for comparison
    type_mapping = {
        'Supermarket': 'Supermarket',
        'Super Store': 'Supermarket',
        'Medium Grocery Store': 'Supermarket',
        'Convenience Store': 'Convenience',
        'Small Grocery Store': 'Other'
    }
    matched['actual_type'] = matched['Store_Type'].map(type_mapping).fillna('Other')
    matched['predicted_type_simplified'] = matched['predicted_type'].map({
        'Supermarket': 'Supermarket',
        'Convenience Store': 'Convenience',
        'Small Grocery Store': 'Other'
    }).fillna('Other')

    # Classification report
    labels = ['Supermarket', 'Convenience', 'Other']
    report = classification_report(
        matched['actual_type'],
        matched['predicted_type_simplified'],
        labels=labels,
        output_dict=True,
        zero_division=0
    )

    # Confusion matrix
    cm = confusion_matrix(
        matched['actual_type'],
        matched['predicted_type_simplified'],
        labels=labels
    )

    return {
        'matched_count': len(matched),
        'report': report,
        'confusion_matrix': cm.tolist(),
        'labels': labels
    }


# ============================================================================
# Main
# ============================================================================

def main():
    print("=" * 60)
    print("VALIDATION METRICS")
    print("=" * 60)

    # Load data
    if not INPUT_FILE.exists():
        print(f"\nERROR: Input file not found: {INPUT_FILE}")
        print("Run script 02_fetch_google_maps_data.py first.")
        return

    print(f"\nLoading: {INPUT_FILE}")
    df = pd.read_csv(INPUT_FILE)
    print(f"Total records: {len(df)}")

    # Match statistics
    found = (df['match_status'] == 'found').sum()
    print(f"Matched stores: {found}")

    # Calculate metrics
    results = calculate_metrics(df)

    if results is None:
        return

    # Print results
    print("\n" + "=" * 60)
    print("CLASSIFICATION REPORT")
    print("=" * 60)

    report = results['report']
    print(f"\n{'Category':<15} {'Precision':>10} {'Recall':>10} {'F1-Score':>10} {'Support':>10}")
    print("-" * 55)

    for label in results['labels']:
        if label in report:
            metrics = report[label]
            print(f"{label:<15} {metrics['precision']:>10.2f} {metrics['recall']:>10.2f} "
                  f"{metrics['f1-score']:>10.2f} {int(metrics['support']):>10}")

    print("-" * 55)
    print(f"{'Accuracy':<15} {'':<10} {'':<10} {report['accuracy']:>10.2f}")
    print(f"{'Weighted Avg':<15} {report['weighted avg']['precision']:>10.2f} "
          f"{report['weighted avg']['recall']:>10.2f} {report['weighted avg']['f1-score']:>10.2f}")

    # Confusion matrix
    print("\n" + "=" * 60)
    print("CONFUSION MATRIX")
    print("=" * 60)
    print("\nPredicted →")
    print(f"Actual ↓    {'Supermarket':>12} {'Convenience':>12} {'Other':>12}")
    print("-" * 50)

    cm = results['confusion_matrix']
    for i, label in enumerate(results['labels']):
        row = "  ".join(f"{cm[i][j]:>12}" for j in range(len(results['labels'])))
        print(f"{label:<12} {row}")

    # Save results
    print("\n" + "=" * 60)
    print("SAVING RESULTS")
    print("=" * 60)

    # Save metrics
    metrics_file = OUTPUT_DIR / "validation_metrics.json"
    with open(metrics_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\n✓ Metrics saved: {metrics_file}")

    # Save detailed results
    detailed_file = DATA_DIR / "processed" / "validation_results.csv"
    detailed_file.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(detailed_file, index=False)
    print(f"✓ Detailed results: {detailed_file}")

    print("\n" + "=" * 60)
    print("COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()
