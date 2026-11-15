#!/usr/bin/env python3
"""Generate the 3 single-panel TETS figures for medicaid-managed-care-fraud-triage.

Run: python3 -B code/generate_figures.py
Verifies zero overlaps via ~/.claude/scripts/figure_overlap_check.py and < 200 KB WebP budget.
"""
from pathlib import Path
import importlib.util
import os
import shutil
import tempfile

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "figures"
OUT.mkdir(parents=True, exist_ok=True)
MPL_CACHE = tempfile.TemporaryDirectory(prefix="mfcu-triage-mpl-")
os.environ["MPLCONFIGDIR"] = MPL_CACHE.name

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from PIL import Image

SITE = Path("/Users/vserver/code/tooearlytosay-work")
SLUG = "medicaid-managed-care-fraud-triage"
DESTS = [
    SITE / "public/images/health-policy" / SLUG,
    SITE / "drafts" / f"img_{SLUG}",
]

spec = importlib.util.spec_from_file_location(
    "figure_overlap_check", Path.home() / ".claude/scripts/figure_overlap_check.py"
)
overlap_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(overlap_module)
check_overlaps = overlap_module.check_overlaps

BLUE = "#0072B2"
TEAL = "#00796B"
ORANGE = "#B84C00"
SLATE = "#1F3A4D"
GREY = "#626970"
INK = "#26343D"

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 12.0,
    "axes.titlesize": 14.0,
    "axes.titleweight": "bold",
    "axes.labelsize": 12.0,
    "xtick.labelsize": 11.0,
    "ytick.labelsize": 11.0,
    "legend.fontsize": 11.0,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.edgecolor": "#8B9399",
    "text.color": INK,
    "axes.labelcolor": INK,
    "xtick.color": INK,
    "ytick.color": INK,
    "savefig.facecolor": "white",
    "figure.facecolor": "white",
    "lines.linewidth": 2.0,
})


def save(fig: plt.Figure, name: str) -> None:
    problems = check_overlaps(fig, name)
    if problems:
        raise RuntimeError("\n".join(problems))
    png_path = OUT / f"{name}.png"
    svg_path = OUT / f"{name}.svg"
    webp_path = OUT / f"{name}.webp"
    fig.savefig(png_path, dpi=150)
    fig.savefig(svg_path, bbox_inches="tight")
    with Image.open(png_path) as im:
        w, h = im.size
        im.convert("RGB").save(webp_path, quality=82, method=6)
    size = webp_path.stat().st_size
    assert size < 200 * 1024, f"{name}: {size} bytes exceeds 200 KB cap"
    aspect = w / h
    assert aspect <= 1.80, f"{name}: aspect {aspect:.3f} exceeds 1.80 cap"
    for dest in DESTS:
        dest.mkdir(parents=True, exist_ok=True)
        for ext in (".webp", ".svg"):
            shutil.copyfile(OUT / f"{name}{ext}", dest / f"{name}{ext}")
    print(f"[PASS] {name}: {w}x{h} (aspect {aspect:.2f}), overlap=0, WebP={size / 1024:.1f} KB")
    plt.close(fig)


def make_figure0_conceptual_map() -> None:
    name = "figure0_pipeline_conceptual_map"
    fig, ax = plt.subplots(figsize=(8.4, 4.9))
    fig.subplots_adjust(left=0.02, right=0.98, top=0.96, bottom=0.04)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 58)
    ax.axis("off")

    ax.text(
        2, 54.5,
        "Three-Stage Medicaid Fraud Enforcement Pipeline",
        fontsize=14.0, weight="bold", color=INK, ha="left", va="center",
    )
    ax.text(
        2, 50.6,
        "Comparing cooperative plan screening against administrative recoupment and investigative triage",
        fontsize=10.8, color=GREY, ha="left", va="center",
    )

    rows = [
        (
            35.5, BLUE, "#F0F7FB",
            "1. Multiplicative Production Identity (Y/S = C/S × I/C × Y/I)",
            "Stage 1: Case Intake\nCases opened per staff (C/S)",
            "Stage 2: Investigative Triage\nIndictments per case (I/C)",
            "Stage 3: Adjudication\nConvictions per indictment (Y/I)",
        ),
        (
            19.0, TEAL, "#EFF8F6",
            "2. Cooperative Delegation Hypothesis (Front-End Plan Screening)",
            "Prepayment Edits\nPlans block routine billing errors",
            "Targeted SIU Referrals\nHigh-grade fraud leads sent",
            "Higher Conviction Output\nWithin-state slope β > 0",
        ),
        (
            2.5, ORANGE, "#FDF4EE",
            "3. Administrative Recoupment & Triage Bottleneck (Observed in Panel)",
            "Upstream Filtering\n10% of plans send 0 referrals",
            "Stage 2 Triage Bottleneck\n75.4%–84.2% of log variance",
            "Flat Conviction Slope\nWithin-state β ≈ 0 (p = 0.98)",
        ),
    ]

    for y0, border_col, fill_col, lane_title, b1, b2, b3 in rows:
        ax.text(2, y0 + 10.6, lane_title, fontsize=10.8, weight="bold", color=border_col, ha="left", va="center")
        boxes = [(1.5, b1), (35.5, b2), (69.5, b3)]
        for bx, btext in boxes:
            patch = FancyBboxPatch(
                (bx, y0), 29.0, 8.6,
                boxstyle="round,pad=0.35,rounding_size=1.0",
                facecolor=fill_col, edgecolor=border_col, linewidth=1.4,
            )
            ax.add_patch(patch)
            ax.text(
                bx + 14.5, y0 + 4.3, btext,
                fontsize=9.5, color=INK, ha="center", va="center", linespacing=1.25,
            )
        for ax_x in (31.2, 65.2):
            ax.annotate(
                "", xy=(ax_x + 3.6, y0 + 4.3), xytext=(ax_x, y0 + 4.3),
                arrowprops=dict(arrowstyle="->", color=border_col, lw=1.8),
            )

    save(fig, name)


def make_figure1_twfe_forest() -> None:
    name = "figure1_twfe_managed_care_null_forest"
    # Verified specifications from Table 1 (estimate_mcrr_tables.py)
    # Reported as % of sample mean per +10 pp increase in managed care share
    specs = [
        ("1. Cross-section OLS (2010–2015, N=300)", -3.82, -10.2, 2.9, SLATE, "o", "Panel A: 2010–2024 Harmonized"),
        ("2. Cross-section OLS (2016–2024, N=455)", -4.13, -12.7, 4.4, SLATE, "o", "Panel A: 2010–2024 Harmonized"),
        ("3. Two-way FE (2010–2024, N=755)", -3.33, -7.9, 1.2, SLATE, "o", "Panel A: 2010–2024 Harmonized"),
        ("4. First differences (2017–2024, N=405)", -4.25, -12.0, 3.9, SLATE, "o", "Panel A: 2010–2024 Harmonized"),
        ("5. Two-way FE: Total conv./staff (N=443)", -0.09, -7.7, 7.5, BLUE, "s", "Panel B: 2016–2024 Uniform CMS"),
        ("6. First diff.: Total conv./staff (N=392)", 3.63, -4.8, 12.0, BLUE, "s", "Panel B: 2016–2024 Uniform CMS"),
        ("7. Two-way FE: Fraud conv./staff (N=443)", -0.56, -7.3, 6.1, TEAL, "^", "Panel B: 2016–2024 Uniform CMS"),
        ("8. Two-way FE: Fraud cases/staff (N=443)", 1.31, -3.2, 5.8, TEAL, "^", "Panel B: 2016–2024 Uniform CMS"),
        ("9. Two-way FE: Any MC share (N=451)", -7.11, -20.0, 5.7, ORANGE, "D", "Panel B: 2016–2024 Uniform CMS"),
    ]

    fig, ax = plt.subplots(figsize=(8.4, 5.1))
    fig.subplots_adjust(left=0.39, right=0.96, top=0.84, bottom=0.15)
    fig.suptitle(
        "Within-State Managed Care Shifts Show Near-Zero Enforcement Effects",
        x=0.03, ha="left", y=0.95, va="top", fontsize=13.2, weight="bold", color=INK,
    )

    y_positions = np.arange(len(specs))[::-1]
    ax.axvline(0.0, color="#64748B", linestyle="--", linewidth=1.2, zorder=1)
    ax.axhline(4.5, color="#CBD5E1", linestyle=":", linewidth=1.0, zorder=1)

    for idx, (label_txt, pt, ci_lo, ci_hi, col, marker, _grp) in enumerate(specs):
        y = y_positions[idx]
        ax.plot([ci_lo, ci_hi], [y, y], color=col, linewidth=2.0, zorder=2)
        ax.plot(pt, y, marker=marker, color=col, markersize=7.0, zorder=3)

    ax.set_yticks(y_positions)
    ax.set_yticklabels([s[0] for s in specs], fontsize=10.2)
    ax.set_xlim(-22.5, 15.0)
    ax.set_ylim(-0.6, len(specs) - 0.3)
    ax.set_xlabel("Implied % change in mean outcome per +10 pp managed care share (95% CI)", fontsize=11.0)
    ax.grid(axis="x", color="#E4E7EA", linewidth=0.7)
    ax.set_axisbelow(True)

    save(fig, name)


def make_figure2_variance_decomposition() -> None:
    name = "figure2_three_stage_variance_decomposition"
    stages = [
        "Stage 2: Investigative Triage\n(Indictments per opened case, I/C)",
        "Stage 1: Case Intake\n(Cases opened per staff-year, C/S)",
        "Stage 3: Courtroom Adjudication\n(Convictions per indictment, Y/I)",
    ]
    all_actions = [75.4, 24.6, 0.0]
    fraud_only = [84.2, 19.0, -3.2]

    fig, ax = plt.subplots(figsize=(8.4, 4.8))
    fig.subplots_adjust(left=0.36, right=0.95, top=0.76, bottom=0.16)
    fig.suptitle(
        "Stage 2 Investigative Triage Governs Cross-State Conviction Variance",
        x=0.03, ha="left", y=0.95, va="top", fontsize=13.2, weight="bold", color=INK,
    )

    y = np.arange(len(stages))[::-1]
    bar_h = 0.32

    ax.axvline(0.0, color="#64748B", linewidth=1.0, zorder=1)
    bars1 = ax.barh(y + bar_h / 2, all_actions, height=bar_h, color=BLUE, label="All enforcement actions (50 states)")
    bars2 = ax.barh(y - bar_h / 2, fraud_only, height=bar_h, color=ORANGE, label="Fraud-only actions (50 states)")

    for bar, val in zip(bars1, all_actions):
        x_pos = max(val, 0.0) + 1.5
        ax.text(x_pos, bar.get_y() + bar.get_height() / 2, f"{val:.1f}%", va="center", ha="left", fontsize=10.5, color=BLUE, weight="bold")

    for bar, val in zip(bars2, fraud_only):
        x_pos = max(val, 0.0) + 1.5
        ax.text(x_pos, bar.get_y() + bar.get_height() / 2, f"{val:.1f}%", va="center", ha="left", fontsize=10.5, color=ORANGE, weight="bold")

    ax.set_yticks(y)
    ax.set_yticklabels(stages, fontsize=10.5)
    ax.set_xlim(-10.0, 98.0)
    ax.set_xlabel("Share of cross-state log variance in convictions per staff-year (%)", fontsize=11.0)
    ax.legend(loc="lower left", bbox_to_anchor=(-0.38, 1.02), frameon=False, ncol=2, fontsize=10.2)
    ax.grid(axis="x", color="#E4E7EA", linewidth=0.7)
    ax.set_axisbelow(True)

    save(fig, name)


if __name__ == "__main__":
    make_figure0_conceptual_map()
    make_figure1_twfe_forest()
    make_figure2_variance_decomposition()
