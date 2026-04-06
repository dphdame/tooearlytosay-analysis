"""
Step 2: Acquire HHS Medicaid Provider Spending data.

The spending file is ~3 GB and must be downloaded from CMS.
This script documents the source and verifies the download.

Source: https://data.cms.gov/summary-statistics-on-use-and-payments/medicaid-provider-spending
Dataset: Medicaid Provider Spending by Healthcare Common Procedure Coding System

Output:
    data/raw/medicaid_provider_spending.csv
"""
import os
from pathlib import Path

RAW = Path(__file__).parent.parent / "data" / "raw"

def check_spending_file():
    """Verify the spending file exists and has expected structure."""
    f = RAW / "medicaid_provider_spending.csv"
    if not f.exists():
        print("Medicaid Provider Spending file not found.")
        print("")
        print("Download instructions:")
        print("  1. Visit https://data.cms.gov/summary-statistics-on-use-and-payments/medicaid-provider-spending")
        print("  2. Download the full CSV (~3 GB)")
        print(f"  3. Save as: {f}")
        print("")
        print("Expected columns: NPI, HCPCS_CD, YEAR, QTR, TOTAL_CLAIMS,")
        print("                  TOTAL_BENEFICIARIES, TOTAL_PAID")
        print("Expected rows: ~227 million")
        return False

    size_gb = os.path.getsize(f) / (1024**3)
    print(f"Found: {f}")
    print(f"  Size: {size_gb:.1f} GB")

    # Quick header check
    with open(f) as fh:
        header = fh.readline().strip()
    print(f"  Header: {header}")
    return True

if __name__ == "__main__":
    check_spending_file()
