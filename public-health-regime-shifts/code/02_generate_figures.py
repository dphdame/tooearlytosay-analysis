#!/usr/bin/env python3
"""
02_generate_figures.py
======================
Generates clean, publication-grade figures for TETS Article #1A:
1. figures/fig1_regime_inversion_forest.png (and .svg)
   Horizontal forest plot of TWFE OLS slope estimates (deaths per 100,000 per $1
   per capita, with 95% confidence intervals) across pre-pandemic regimes, SCO
   2017 crosswalk specifications, the 2020-2023 COVID-19 emergency grant era,
   and the unstratified 2003-2023 pooled panel.
2. figures/fig2_long_diff_lag_horizon.png (and .svg)
   Two-panel horizontal/vertical comparison of:
   - Panel A: Contemporaneous within-regime TWFE and aligned long-differences vs.
     temporally separated long-differences and multi-year rolling averages.
   - Panel B: Distributed lag coefficients (0, 1, 2, 3, 5, 8 years) and stacked
     first-difference horizons (k = 1..16 years), illustrating that individual
     lagged and multi-year horizon estimates do not pass BH-FDR / Holm q < 0.05.

Follows /figure-workflow Clean Figures Policy:
- NO embedded figure titles, subtitles, sample sizes, p-values, or source notes
  inside the canvas.
- ONLY axis labels, tick labels, zero reference line, data points/error bars,
  and a clean minimal legend inside the image.
"""

from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from PIL import Image

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
FIG_DIR = BASE_DIR / "figures"

# High-contrast, WCAG-compliant Too Early To Say (TETS) palette
COLOR_PRE_COVID = "#1F3A4D"      # Deep TETS slate: Pre-COVID protective regime
COLOR_CROSSWALK = "#136F63"      # TETS support teal: Pre-COVID 2017 crosswalk checks
COLOR_COVID_ERA = "#B93829"      # TETS action coral/rust: COVID-19 emergency grant era
COLOR_POOLED = "#475569"         # Muted slate: Unstratified pooled / null
COLOR_SEPARATED = "#B45309"      # Warm amber/gold: Temporally separated / cumulative

plt.rcParams.update(
    {
        "font.family": "sans-serif",
        "font.sans-serif": ["DejaVu Sans", "Arial", "Helvetica"],
        "font.size": 11,
        "axes.labelsize": 11.5,
        "axes.titlesize": 11.5,
        "xtick.labelsize": 10.5,
        "ytick.labelsize": 10.5,
        "legend.fontsize": 10,
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "axes.edgecolor": "#333333",
        "axes.linewidth": 0.9,
    }
)


def make_fig1_regime_inversion_forest() -> None:
    """Generate Figure 1: TWFE Regime Inversion & Crosswalk Sensitivity Forest Plot."""
    df = pd.read_csv(DATA_DIR / "panel_regime_and_crosswalk_sensitivity.csv")

    specs = [
        (
            "1. 2003-2016 Single-Regime Consistent (Nominal USD)",
            "2003–2016 Single-Regime\n(Pre-2017 SCO Schema)",
            "Pre-COVID Baseline",
            COLOR_PRE_COVID,
            "o",
        ),
        (
            "3. 2003-2019 Pre-COVID SCO Crosswalk Ex-Debt (Nominal USD)",
            "2003–2019 Pre-COVID Baseline\n(SCO Crosswalk Ex-Debt)",
            "Pre-COVID Baseline",
            COLOR_PRE_COVID,
            "o",
        ),
        (
            "5. 2003-2019 Pre-COVID Crosswalk + 5 Outlier Post-2017 Step-Shift FE",
            "2003–2019 + 5 Outlier\nStep-Shift Indicators",
            "2017 Crosswalk Checks",
            COLOR_CROSSWALK,
            "s",
        ),
        (
            "6. 2003-2019 Pre-COVID Crosswalk Excluding 5 Outliers Post-2016",
            "2003–2019 Excluding 5\nOutliers Post-2016",
            "2017 Crosswalk Checks",
            COLOR_CROSSWALK,
            "s",
        ),
        (
            "7. 2003-2019 Pre-COVID Crosswalk Incl-Debt Service (Nominal USD)",
            "2003–2019 Including\nDebt Service Category",
            "2017 Crosswalk Checks",
            COLOR_CROSSWALK,
            "s",
        ),
        (
            "8. 2003-2019 Pre-COVID Crosswalk + All-County Regime-Interacted FE",
            "2003–2019 + All-County\nRegime-Interacted FEs",
            "2017 Crosswalk Checks",
            COLOR_CROSSWALK,
            "s",
        ),
        (
            "9. 2020-2023 COVID-19 Emergency Grant Era Only (Nominal USD)",
            "2020–2023 COVID-19\nEmergency Grant Era",
            "COVID-19 Era (2020–2023)",
            COLOR_COVID_ERA,
            "D",
        ),
        (
            "10. 2003-2023 Unstratified Pooled Panel (Contaminated by COVID)",
            "2003–2023 Unstratified\nPooled Panel",
            "Unstratified Pooled (2003–2023)",
            COLOR_POOLED,
            "^",
        ),
    ]

    rows = []
    for raw_name, clean_label, group_label, color, marker in specs:
        match = df.loc[df["specification"] == raw_name].iloc[0]
        rows.append(
            {
                "label": clean_label,
                "group": group_label,
                "beta": float(match["ols_coef"]),
                "se": float(match["ols_se"]),
                "ci_low": float(match["ols_coef"] - 1.96 * match["ols_se"]),
                "ci_high": float(match["ols_coef"] + 1.96 * match["ols_se"]),
                "color": color,
                "marker": marker,
            }
        )

    plot_df = pd.DataFrame(rows).iloc[::-1].reset_index(drop=True)

    fig, ax = plt.subplots(figsize=(9.2, 5.8), dpi=300)
    ax.set_axisbelow(True)
    ax.grid(axis="x", color="#EAEAEA", linestyle="-", linewidth=0.8)

    # Zero reference line
    ax.axvline(0.0, color="#222222", linestyle="--", linewidth=1.2, zorder=2)

    # Subtle horizontal separator lines between regime blocks
    ax.axhline(1.5, color="#DCDCDC", linestyle=":", linewidth=0.9, zorder=1)
    ax.axhline(5.5, color="#DCDCDC", linestyle=":", linewidth=0.9, zorder=1)

    seen_groups = set()
    for idx, row in plot_df.iterrows():
        lbl = row["group"] if row["group"] not in seen_groups else None
        if lbl is not None:
            seen_groups.add(row["group"])

        ax.errorbar(
            row["beta"],
            idx,
            xerr=1.96 * row["se"],
            fmt=row["marker"],
            color=row["color"],
            ecolor=row["color"],
            elinewidth=2.2,
            capsize=4.5,
            capthick=1.6,
            markersize=8.0,
            label=lbl,
            zorder=3,
        )

    ax.set_yticks(range(len(plot_df)))
    ax.set_yticklabels(plot_df["label"])
    ax.set_xlim(-0.56, 0.48)
    ax.set_ylim(-0.65, len(plot_df) - 0.35)
    ax.set_xlabel(
        "TWFE Slope Estimate (Resident Deaths per 100,000 per $1 Per Capita Spending, 95% CI)"
    )

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    # Place legend in the completely open upper-right quadrant (rows 2..7 have x < 0)
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(
        handles[::-1],
        labels[::-1],
        loc="upper right",
        frameon=True,
        facecolor="white",
        edgecolor="#CCCCCC",
        framealpha=0.96,
    )

    fig.tight_layout()
    png_path = FIG_DIR / "fig1_regime_inversion_forest.png"
    webp_path = FIG_DIR / "fig1_regime_inversion_forest.webp"
    fig.savefig(png_path, dpi=300, bbox_inches="tight")
    fig.savefig(FIG_DIR / "fig1_regime_inversion_forest.svg", bbox_inches="tight")
    plt.close(fig)
    with Image.open(png_path) as im:
        im.save(webp_path, format="WEBP", quality=92)
    print("[PASS] Saved fig1_regime_inversion_forest.png, .webp, and .svg")


def make_fig2_long_diff_lag_horizon() -> None:
    """Generate Figure 2: Exposure Horizons, Temporally Separated Long-Diffs & Lags."""
    lags_df = pd.read_csv(DATA_DIR / "explicit_lag_and_cumulative_results.csv")
    long_df = pd.read_csv(DATA_DIR / "temporally_separated_long_diff_results.csv")
    horizons_df = pd.read_csv(DATA_DIR / "long_difference_and_lag_results.csv")
    horizons_df = horizons_df.loc[
        horizons_df["sample_type"] == "2003-2019 Pre-COVID Crosswalk (All available years)"
    ].sort_values("k_years")

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.0, 5.8), dpi=300)

    # -------------------------------------------------------------------------
    # Left Panel (ax1): Contemporaneous vs. Temporally Separated & Cumulative
    # -------------------------------------------------------------------------
    panel_a_items = [
        (
            "Contemporaneous TWFE\n(2011–2019 Fixed Window)",
            float(
                lags_df.loc[
                    (lags_df["sample_window"] == "2011-2019 Pre-COVID Crosswalk Fixed Sample")
                    & (lags_df["regressor"] == "Contemporaneous PH_t (lag 0)")
                ]["ols_coef"].iloc[0]
            ),
            float(
                lags_df.loc[
                    (lags_df["sample_window"] == "2011-2019 Pre-COVID Crosswalk Fixed Sample")
                    & (lags_df["regressor"] == "Contemporaneous PH_t (lag 0)")
                ]["ols_se"].iloc[0]
            ),
            "Contemporaneous / Aligned",
            COLOR_PRE_COVID,
            "o",
        ),
        (
            "Aligned Long-Difference\n(2003–2016 Single-Regime)",
            float(
                long_df.loc[
                    long_df["specification"] == "3. Single-Regime ΔPH(2003->2016) -> Aligned ΔMort(2003->2016)"
                ]["ols_coef"].iloc[0]
            ),
            float(
                long_df.loc[
                    long_df["specification"] == "3. Single-Regime ΔPH(2003->2016) -> Aligned ΔMort(2003->2016)"
                ]["ols_se"].iloc[0]
            ),
            "Contemporaneous / Aligned",
            COLOR_PRE_COVID,
            "o",
        ),
        (
            "Early ΔPH (2003–2010) →\nFull ΔMort (2003–2016 Overlap)",
            float(
                long_df.loc[
                    long_df["specification"] == "2. Early-period ΔPH(2003->2010) -> Long ΔMort(2003->2016)"
                ]["ols_coef"].iloc[0]
            ),
            float(
                long_df.loc[
                    long_df["specification"] == "2. Early-period ΔPH(2003->2010) -> Long ΔMort(2003->2016)"
                ]["ols_se"].iloc[0]
            ),
            "Contemporaneous / Aligned",
            COLOR_PRE_COVID,
            "o",
        ),
        (
            "Temporally Separated ΔPH\n(2003–2010) → ΔMort (2010–2016)",
            float(
                long_df.loc[
                    long_df["specification"] == "1. Early-period ΔPH(2003->2010) -> Subsequent ΔMort(2010->2016)"
                ]["ols_coef"].iloc[0]
            ),
            float(
                long_df.loc[
                    long_df["specification"] == "1. Early-period ΔPH(2003->2010) -> Subsequent ΔMort(2010->2016)"
                ]["ols_se"].iloc[0]
            ),
            "Temporally Separated / Cumulative",
            COLOR_SEPARATED,
            "s",
        ),
        (
            "Aligned Long-Difference\n(2003–2019 All Reporting)",
            float(
                long_df.loc[
                    long_df["specification"] == "5. Crosswalk ΔPH(2003->2019) -> Aligned Pre-COVID ΔMort(2003->2019)"
                ]["ols_coef"].iloc[0]
            ),
            float(
                long_df.loc[
                    long_df["specification"] == "5. Crosswalk ΔPH(2003->2019) -> Aligned Pre-COVID ΔMort(2003->2019)"
                ]["ols_se"].iloc[0]
            ),
            "Temporally Separated / Cumulative",
            COLOR_SEPARATED,
            "s",
        ),
        (
            "4-Year Rolling Mean\n(t-3 to t, 2011–2019)",
            float(
                lags_df.loc[
                    (lags_df["sample_window"] == "2011-2019 Pre-COVID Crosswalk Fixed Sample")
                    & (lags_df["regressor"] == "Cumulative mean PH_{t-3..t} (4-yr avg)")
                ]["ols_coef"].iloc[0]
            ),
            float(
                lags_df.loc[
                    (lags_df["sample_window"] == "2011-2019 Pre-COVID Crosswalk Fixed Sample")
                    & (lags_df["regressor"] == "Cumulative mean PH_{t-3..t} (4-yr avg)")
                ]["ols_se"].iloc[0]
            ),
            "Temporally Separated / Cumulative",
            COLOR_SEPARATED,
            "s",
        ),
        (
            "6-Year Rolling Mean\n(t-5 to t, 2011–2019)",
            float(
                lags_df.loc[
                    (lags_df["sample_window"] == "2011-2019 Pre-COVID Crosswalk Fixed Sample")
                    & (lags_df["regressor"] == "Cumulative mean PH_{t-5..t} (6-yr avg)")
                ]["ols_coef"].iloc[0]
            ),
            float(
                lags_df.loc[
                    (lags_df["sample_window"] == "2011-2019 Pre-COVID Crosswalk Fixed Sample")
                    & (lags_df["regressor"] == "Cumulative mean PH_{t-5..t} (6-yr avg)")
                ]["ols_se"].iloc[0]
            ),
            "Temporally Separated / Cumulative",
            COLOR_SEPARATED,
            "s",
        ),
        (
            "9-Year Rolling Mean\n(t-8 to t, 2011–2019)",
            float(
                lags_df.loc[
                    (lags_df["sample_window"] == "2011-2019 Pre-COVID Crosswalk Fixed Sample")
                    & (lags_df["regressor"] == "Cumulative mean PH_{t-8..t} (9-yr avg)")
                ]["ols_coef"].iloc[0]
            ),
            float(
                lags_df.loc[
                    (lags_df["sample_window"] == "2011-2019 Pre-COVID Crosswalk Fixed Sample")
                    & (lags_df["regressor"] == "Cumulative mean PH_{t-8..t} (9-yr avg)")
                ]["ols_se"].iloc[0]
            ),
            "Temporally Separated / Cumulative",
            COLOR_SEPARATED,
            "s",
        ),
    ]

    pa_df = pd.DataFrame(
        panel_a_items,
        columns=["label", "beta", "se", "group", "color", "marker"],
    ).iloc[::-1].reset_index(drop=True)

    ax1.set_axisbelow(True)
    ax1.grid(axis="x", color="#EAEAEA", linestyle="-", linewidth=0.8)
    ax1.axvline(0.0, color="#222222", linestyle="--", linewidth=1.1, zorder=2)
    ax1.axhline(4.5, color="#DCDCDC", linestyle=":", linewidth=0.9, zorder=1)

    seen_a = set()
    for idx, row in pa_df.iterrows():
        lbl = row["group"] if row["group"] not in seen_a else None
        if lbl is not None:
            seen_a.add(row["group"])
        ax1.errorbar(
            row["beta"],
            idx,
            xerr=1.96 * row["se"],
            fmt=row["marker"],
            color=row["color"],
            ecolor=row["color"],
            elinewidth=2.0,
            capsize=4.0,
            capthick=1.5,
            markersize=7.5,
            label=lbl,
            zorder=3,
        )

    ax1.set_yticks(range(len(pa_df)))
    ax1.set_yticklabels(pa_df["label"])
    ax1.set_xlim(-0.92, 0.88)
    ax1.set_ylim(-0.6, len(pa_df) + 0.55)
    ax1.set_xlabel("Slope Estimate (Deaths per 100,000 per $1, 95% CI)")
    ax1.spines["top"].set_visible(False)
    ax1.spines["right"].set_visible(False)
    h1, l1 = ax1.get_legend_handles_labels()
    ax1.legend(
        h1[::-1],
        l1[::-1],
        loc="upper right",
        frameon=True,
        facecolor="white",
        edgecolor="#CCCCCC",
        framealpha=0.96,
    )

    # -------------------------------------------------------------------------
    # Right Panel (ax2): Stacked First-Difference Horizons (k = 1..16) & Lags
    # -------------------------------------------------------------------------
    ax2.set_axisbelow(True)
    ax2.grid(axis="both", color="#EAEAEA", linestyle="-", linewidth=0.8)
    ax2.axhline(0.0, color="#222222", linestyle="--", linewidth=1.1, zorder=2)

    k_vals = horizons_df["k_years"].to_numpy(dtype=float)
    b_vals = horizons_df["ols_coef"].to_numpy(dtype=float)
    se_vals = horizons_df["ols_se"].to_numpy(dtype=float)

    ax2.fill_between(
        k_vals,
        b_vals - 1.96 * se_vals,
        b_vals + 1.96 * se_vals,
        color=COLOR_CROSSWALK,
        alpha=0.22,
        label="k-Year First Difference (95% CI)",
        zorder=2,
    )
    ax2.plot(
        k_vals,
        b_vals,
        color=COLOR_PRE_COVID,
        marker="o",
        linewidth=1.8,
        markersize=5.5,
        label="k-Year First Difference (2003–2019)",
        zorder=3,
    )

    # Overlay discrete distributed lags on 2011-2019 fixed sample (lags 0, 1, 2, 3, 5, 8)
    lag_map = [
        (0, "Contemporaneous PH_t (lag 0)"),
        (1, "1-year lag PH_{t-1}"),
        (2, "2-year lag PH_{t-2}"),
        (3, "3-year lag PH_{t-3}"),
        (5, "5-year lag PH_{t-5}"),
        (8, "8-year lag PH_{t-8}"),
    ]
    lag_x, lag_y, lag_se = [], [], []
    for k_lag, spec_name in lag_map:
        sub = lags_df.loc[
            (lags_df["sample_window"] == "2011-2019 Pre-COVID Crosswalk Fixed Sample")
            & (lags_df["regressor"] == spec_name)
        ].iloc[0]
        lag_x.append(k_lag)
        lag_y.append(float(sub["ols_coef"]))
        lag_se.append(float(sub["ols_se"]))

    ax2.errorbar(
        lag_x,
        lag_y,
        yerr=1.96 * np.array(lag_se),
        fmt="D",
        color=COLOR_COVID_ERA,
        ecolor=COLOR_COVID_ERA,
        elinewidth=1.8,
        capsize=3.8,
        markersize=6.5,
        label="Distributed Lag PH(t-k) (2011–2019)",
        zorder=4,
    )

    ax2.set_xticks([0, 2, 4, 6, 8, 10, 12, 14, 16])
    ax2.set_xlim(-0.6, 16.6)
    ax2.set_ylim(-0.92, 0.92)
    ax2.set_xlabel("Horizon or Lag Length k (Years)")
    ax2.set_ylabel("Slope Estimate (Deaths per 100,000 per $1, 95% CI)")
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)
    ax2.legend(
        loc="upper right",
        frameon=True,
        facecolor="white",
        edgecolor="#CCCCCC",
        framealpha=0.96,
    )

    fig.tight_layout()
    png_path = FIG_DIR / "fig2_long_diff_lag_horizon.png"
    webp_path = FIG_DIR / "fig2_long_diff_lag_horizon.webp"
    fig.savefig(png_path, dpi=300, bbox_inches="tight")
    fig.savefig(FIG_DIR / "fig2_long_diff_lag_horizon.svg", bbox_inches="tight")
    plt.close(fig)
    with Image.open(png_path) as im:
        im.save(webp_path, format="WEBP", quality=92)
    print("[PASS] Saved fig2_long_diff_lag_horizon.png, .webp, and .svg")


if __name__ == "__main__":
    make_fig1_regime_inversion_forest()
    make_fig2_long_diff_lag_horizon()
