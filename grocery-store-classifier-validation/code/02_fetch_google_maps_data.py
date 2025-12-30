#!/usr/bin/env python3
"""
Fetch Google Maps Data for Validation

Author: V Cholette
Purpose: Query Google Maps Places API to get business categories for validation

Requires: GOOGLE_MAPS_API_KEY environment variable

Usage:
    export GOOGLE_MAPS_API_KEY="your_key_here"
    python 02_fetch_google_maps_data.py
"""

import os
import pandas as pd
import requests
import time
from pathlib import Path
import json

# ============================================================================
# Configuration
# ============================================================================

PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
VALIDATION_DIR = DATA_DIR / "validation"

INPUT_FILE = VALIDATION_DIR / "validation_sample.csv"
OUTPUT_FILE = VALIDATION_DIR / "google_maps_results.csv"

# API configuration
PLACES_API_URL = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
RATE_LIMIT_DELAY = 0.1  # seconds between requests


# ============================================================================
# Google Maps API
# ============================================================================

def get_api_key():
    """Get API key from environment."""
    key = os.environ.get('GOOGLE_MAPS_API_KEY')
    if not key:
        raise ValueError(
            "GOOGLE_MAPS_API_KEY environment variable not set.\n"
            "Get a key from https://console.cloud.google.com/\n"
            "Then run: export GOOGLE_MAPS_API_KEY='your_key'"
        )
    return key


def search_place(name, lat, lng, api_key):
    """
    Search for a place near coordinates.

    Returns:
        dict with place details or None if not found
    """
    params = {
        'location': f'{lat},{lng}',
        'radius': 100,  # meters
        'keyword': name,
        'key': api_key
    }

    try:
        response = requests.get(PLACES_API_URL, params=params, timeout=10)
        data = response.json()

        if data['status'] == 'OK' and data['results']:
            place = data['results'][0]
            return {
                'google_name': place.get('name'),
                'google_types': ','.join(place.get('types', [])),
                'google_place_id': place.get('place_id'),
                'google_rating': place.get('rating'),
                'google_user_ratings': place.get('user_ratings_total'),
                'match_status': 'found'
            }
        else:
            return {'match_status': 'not_found'}

    except Exception as e:
        return {'match_status': 'error', 'error': str(e)}


# ============================================================================
# Main
# ============================================================================

def main():
    print("=" * 60)
    print("GOOGLE MAPS DATA COLLECTION")
    print("=" * 60)

    # Check API key
    try:
        api_key = get_api_key()
        print(f"\nAPI key found: {api_key[:8]}...")
    except ValueError as e:
        print(f"\nERROR: {e}")
        return

    # Load sample
    if not INPUT_FILE.exists():
        print(f"\nERROR: Input file not found: {INPUT_FILE}")
        print("Run script 01_sample_snap_retailers.py first.")
        return

    print(f"\nLoading: {INPUT_FILE}")
    df = pd.read_csv(INPUT_FILE)
    print(f"Stores to validate: {len(df)}")

    # Estimate cost
    cost_estimate = len(df) * 0.017
    print(f"\nEstimated API cost: ${cost_estimate:.2f}")
    print("Continue? (Ctrl+C to cancel)")
    time.sleep(3)

    # Query each store
    print("\nQuerying Google Maps...")
    results = []

    for idx, row in df.iterrows():
        if idx % 50 == 0:
            print(f"  Progress: {idx}/{len(df)}")

        result = search_place(
            name=row['Store_Name'],
            lat=row['Latitude'],
            lng=row['Longitude'],
            api_key=api_key
        )

        # Combine with original data
        combined = row.to_dict()
        combined.update(result)
        results.append(combined)

        time.sleep(RATE_LIMIT_DELAY)

    # Create output dataframe
    results_df = pd.DataFrame(results)

    # Summary
    found = (results_df['match_status'] == 'found').sum()
    not_found = (results_df['match_status'] == 'not_found').sum()
    errors = (results_df['match_status'] == 'error').sum()

    print(f"\nResults:")
    print(f"  Found: {found}")
    print(f"  Not found: {not_found}")
    print(f"  Errors: {errors}")

    # Save
    results_df.to_csv(OUTPUT_FILE, index=False)
    print(f"\n✓ Results saved: {OUTPUT_FILE}")

    print(f"\nNext step: python 03_calculate_validation_metrics.py")


if __name__ == "__main__":
    main()
