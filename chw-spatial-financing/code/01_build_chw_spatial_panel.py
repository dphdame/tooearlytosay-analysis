#!/usr/bin/env python3
"""
01_build_chw_spatial_panel.py
Verifies and summarizes the 58-county California CHW spatial financing panel
and the within-county Census tract density quintiles (Q1-Q5) for San Bernardino
and Santa Barbara counties.
"""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
PROC = ROOT / "data" / "processed"

def main() -> None:
    df_58 = pd.read_csv(PROC / "ca_58_counties_chw_spatial.csv")
    df_q = pd.read_csv(PROC / "within_county_tract_quintiles_sb_sbd.csv")
    assert len(df_58) in (58, 59), f"Expected 58-59 rows, got {len(df_58)}"
    assert len(df_q) == 10, f"Expected 10 tract quintile rows (Q1-Q5 x 2 counties), got {len(df_q)}"
    print(f"[PASS] 58-County Panel verified ({len(df_58)} rows, {len(df_58.columns)} columns).")
    print(f"[PASS] Tract Quintiles verified ({len(df_q)} rows, {len(df_q.columns)} columns).")

if __name__ == "__main__":
    main()
