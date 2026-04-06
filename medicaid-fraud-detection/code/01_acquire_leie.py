"""
Step 1: Acquire LEIE exclusion data from OIG.

Downloads the current LEIE CSV from the HHS Office of Inspector General.
Also acquires the California DHCS Suspended & Ineligible list.

Output:
    data/raw/UPDATED.csv          - Current LEIE
    data/raw/ca_si_list.csv       - CA S&I list
"""
import requests
from pathlib import Path

RAW = Path(__file__).parent.parent / "data" / "raw"
RAW.mkdir(parents=True, exist_ok=True)

LEIE_URL = "https://oig.hhs.gov/exclusions/downloadables/UPDATED.csv"

def download_leie():
    """Download current LEIE exclusion list."""
    print("Downloading LEIE from OIG...")
    resp = requests.get(LEIE_URL, timeout=60)
    resp.raise_for_status()
    out = RAW / "UPDATED.csv"
    out.write_bytes(resp.content)
    print(f"  Saved {len(resp.content):,} bytes to {out}")

def download_ca_si():
    """
    CA DHCS S&I list requires manual download.
    Visit: https://www.dhcs.ca.gov/provgovpart/Pages/SandIList.aspx
    Save the CSV/Excel file as data/raw/ca_si_list.csv
    """
    out = RAW / "ca_si_list.csv"
    if not out.exists():
        print("WARNING: CA S&I list not found.")
        print("  Download manually from:")
        print("  https://www.dhcs.ca.gov/provgovpart/Pages/SandIList.aspx")
        print(f"  Save as: {out}")
    else:
        print(f"  CA S&I list found: {out}")

if __name__ == "__main__":
    download_leie()
    download_ca_si()
    print("Done.")
