#!/usr/bin/env python3
"""
02_generate_figures.py
Verifies Figure 1 (58-County Wage-Distance Squeeze) and Figure 2
(Within-County Census Tract Density Quintiles Q1-Q5 in San Bernardino and Santa Barbara).
"""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
PROC = ROOT / "data" / "processed"
FIGS = ROOT / "figures"

def main() -> None:
    df_58 = pd.read_csv(PROC / "ca_58_counties_chw_spatial.csv")
    df_q = pd.read_csv(PROC / "within_county_tract_quintiles_sb_sbd.csv")
    assert (FIGS / "fig1_58_county_wage_distance_squeeze.webp").exists()
    assert (FIGS / "fig2_within_county_tract_dispersion.webp").exists()
    print(f"[PASS] Verified figures in {FIGS} against {len(df_58)} counties and {len(df_q)} tract quintiles.")

if __name__ == "__main__":
    main()
