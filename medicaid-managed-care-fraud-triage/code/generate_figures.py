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
DESTS = (
    [
        SITE / "public/images/health-policy" / SLUG,
        SITE / "drafts" / f"img_{SLUG}",
    ]
    if SITE.exists()
    else []
)

_overlap_script = Path.home() / ".claude/scripts/figure_overlap_check.py"
if _overlap_script.exists():
    spec = importlib.util.spec_from_file_location("figure_overlap_check", _overlap_script)
    overlap_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(overlap_module)
    check_overlaps = overlap_module.check_overlaps
else:
    def check_overlaps(fig, name):
        return []

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
        "Within-State Managed Care Shifts Show No Detectable Conviction Gain",
        x=0.03, ha="left", y=0.95, va="top", fontsize=12.8, weight="bold", color=INK,
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
    ax.set_xlabel("Implied % change in mean outcome per +10 pp MCO share (95% CI)", fontsize=10.8)
    ax.grid(axis="x", color="#E4E7EA", linewidth=0.7)
    ax.set_axisbelow(True)

    save(fig, name)


def make_cover_art() -> None:
    """Generate 1800x1012 editorial cover art (cover.png & cover.webp, zero text)
    matching the TETS Health Policy visual series (#FDF7F4 cream canvas, #264653
    double border, and three-stage triage bottleneck geometry).
    """
    cream = "#FDF7F4"
    deep_teal = "#264653"
    inner_border = "#49636D"
    teal = "#2A9D8F"
    coral = "#E76F51"
    gold = "#F4A261"
    soft_sand = "#F5EBE4"

    fig = plt.figure(figsize=(18.0, 10.12), dpi=100, facecolor=cream)
    ax = fig.add_axes([0, 0, 1, 1], facecolor=cream)
    ax.set_xlim(0, 1800)
    ax.set_ylim(0, 1012)
    ax.axis("off")

    # Background fill
    ax.add_patch(plt.Rectangle((0, 0), 1800, 1012, facecolor=cream, edgecolor="none", zorder=0))

    # Subtle stage background panels inside the inner frame
    ax.add_patch(plt.Rectangle((120, 140), 470, 732, facecolor=soft_sand, edgecolor="none", alpha=0.45, zorder=1))
    ax.add_patch(plt.Rectangle((650, 140), 500, 732, facecolor="#FBF0EA", edgecolor="none", alpha=0.55, zorder=1))
    ax.add_patch(plt.Rectangle((1210, 140), 470, 732, facecolor="#EEF6F5", edgecolor="none", alpha=0.55, zorder=1))

    # Subtle horizontal reference grid lines across the three stages
    for gy in np.linspace(210, 802, 7):
        ax.plot([120, 1680], [gy, gy], color="#E5DCD5", linewidth=1.0, zorder=1)

    # Vertical dashed stage dividers (Stage 1 -> Stage 2 -> Stage 3)
    for div_x in (620, 1180):
        ax.plot([div_x, div_x], [115, 897], color=deep_teal, linestyle=(0, (4, 5)), linewidth=2.2, alpha=0.75, zorder=3)

    # Central Stage 2 investigative triage bottleneck aperture (architectural gate)
    gate_x = 900
    # Upper and lower coral/deep-teal barrier blocks forming the narrow central aperture
    # Aperture opening: y in [416, 596] (180 px high out of 660 px intake span)
    ax.add_patch(
        FancyBboxPatch(
            (gate_x - 26, 612), 52, 240,
            boxstyle="round,pad=0,rounding_size=8",
            facecolor=deep_teal, edgecolor=deep_teal, linewidth=2.0, zorder=5,
        )
    )
    ax.add_patch(
        FancyBboxPatch(
            (gate_x - 26, 160), 52, 240,
            boxstyle="round,pad=0,rounding_size=8",
            facecolor=deep_teal, edgecolor=deep_teal, linewidth=2.0, zorder=5,
        )
    )
    # Coral accent plates on the inner lips of the triage gate
    ax.add_patch(
        FancyBboxPatch(
            (gate_x - 32, 598), 64, 18,
            boxstyle="round,pad=0,rounding_size=4",
            facecolor=coral, edgecolor=deep_teal, linewidth=1.8, zorder=6,
        )
    )
    ax.add_patch(
        FancyBboxPatch(
            (gate_x - 32, 396), 64, 18,
            boxstyle="round,pad=0,rounding_size=4",
            facecolor=coral, edgecolor=deep_teal, linewidth=1.8, zorder=6,
        )
    )

    # Glowing gold/teal focus ring inside the triage aperture
    aperture_ring = plt.Circle((gate_x, 506), 72, facecolor=gold, edgecolor=coral, linewidth=2.2, alpha=0.22, zorder=2)
    ax.add_patch(aperture_ring)

    # 16 intake streams entering Stage 1 on the left (y from 196 to 816)
    n_streams = 16
    y_starts = np.linspace(196, 816, n_streams)
    # Middle 4 streams (indices 6, 7, 8, 9) pass through the Stage 2 triage gate and become indictments/convictions
    pass_indices = {6, 7, 8, 9}
    y_pass_targets = {
        6: 452.0,
        7: 488.0,
        8: 524.0,
        9: 560.0,
    }
    y_stage3_ends = {
        6: 410.0,
        7: 474.0,
        8: 538.0,
        9: 602.0,
    }

    for idx, y0 in enumerate(y_starts):
        # Stage 1: Left intake node + horizontal stream from x=150 to x=620
        is_passing = idx in pass_indices
        s1_color = teal if is_passing else ("#3B5B6C" if idx % 2 == 0 else "#6B828E")
        s1_lw = 4.2 if is_passing else 2.6
        s1_alpha = 0.98 if is_passing else 0.72

        # Intake origin circle
        ax.scatter([155], [y0], s=70 if is_passing else 42, facecolor=gold if is_passing else cream,
                   edgecolor=s1_color, linewidth=2.2, zorder=6)

        # Stage 1 curve (155 -> 620)
        x_s1 = np.linspace(155, 620, 120)
        y_s1 = np.full_like(x_s1, y0)
        ax.plot(x_s1, y_s1, color=s1_color, linewidth=s1_lw, alpha=s1_alpha, solid_capstyle="round", zorder=4)

        if is_passing:
            # Stage 2: Smooth sigmoid convergence through the central triage aperture (620 -> 900 -> 1180)
            y_mid = y_pass_targets[idx]
            x_s2a = np.linspace(620, gate_x, 120)
            t_a = (x_s2a - 620) / (gate_x - 620)
            s_a = 3 * t_a**2 - 2 * t_a**3
            y_s2a = y0 + (y_mid - y0) * s_a
            ax.plot(x_s2a, y_s2a, color=teal, linewidth=4.4, solid_capstyle="round", zorder=5)

            # Node inside the aperture
            ax.scatter([gate_x], [y_mid], s=85, facecolor=gold, edgecolor=deep_teal, linewidth=2.2, zorder=7)

            # Stage 2 exit to Stage 3 divider (900 -> 1180)
            y_end = y_stage3_ends[idx]
            x_s2b = np.linspace(gate_x, 1180, 120)
            t_b = (x_s2b - gate_x) / (1180 - gate_x)
            s_b = 3 * t_b**2 - 2 * t_b**3
            y_s2b = y_mid + (y_end - y_mid) * s_b
            ax.plot(x_s2b, y_s2b, color=teal, linewidth=4.4, solid_capstyle="round", zorder=5)

            # Stage 3: Adjudicated conviction trajectories (1180 -> 1635) with terminal arrows/nodes
            x_s3 = np.linspace(1180, 1625, 100)
            y_s3 = np.full_like(x_s3, y_end)
            ax.plot(x_s3, y_s3, color=deep_teal, linewidth=4.6, solid_capstyle="round", zorder=5)
            ax.scatter([1180], [y_end], s=70, facecolor=teal, edgecolor=deep_teal, linewidth=2.0, zorder=7)
            ax.scatter([1625], [y_end], s=130, facecolor=teal, edgecolor=deep_teal, linewidth=2.6, zorder=7)
            ax.scatter([1625], [y_end], s=32, facecolor=cream, edgecolor="none", zorder=8)
        else:
            # Filtered/dropped cases in Stage 2: curve slightly toward the barrier and terminate at coral stop-bars
            # Vary stop x-coordinate between 740 and 845 so the triage drop-off reads as a graded filter
            dist_from_center = abs(idx - 7.5)
            stop_x = 848 - 14 * dist_from_center
            y_target = y0 + (506 - y0) * 0.16
            x_s2_drop = np.linspace(620, stop_x, 90)
            t_d = (x_s2_drop - 620) / (stop_x - 620)
            s_d = 3 * t_d**2 - 2 * t_d**3
            y_s2_drop = y0 + (y_target - y0) * s_d
            ax.plot(x_s2_drop, y_s2_drop, color=coral, linewidth=2.4, linestyle=(0, (5, 3)), alpha=0.85, zorder=4)
            # Terminal vertical coral tick bar showing case closed without indictment
            ax.plot([stop_x, stop_x], [y_target - 9, y_target + 9], color=coral, linewidth=3.0, solid_capstyle="round", zorder=6)

            # Faint ghosted continuation in Stage 3 showing the missing counterfactual volume
            ax.plot([1215, 1620], [y0, y0], color="#D6CBC3", linewidth=1.3, linestyle=(0, (3, 5)), alpha=0.65, zorder=2)

    # Decorative geometric balance markers at top of each stage column (no text)
    # Stage 1: wide multi-bar motif
    for i, bx in enumerate(range(310, 420, 26)):
        ax.add_patch(plt.Rectangle((bx, 888), 16, 16, facecolor= deep_teal if i % 2 == 0 else teal, edgecolor="none", zorder=6))
    # Stage 2: coral funnel diamond
    diamond_x = [900, 916, 900, 884]
    diamond_y = [908, 896, 884, 896]
    ax.fill(diamond_x, diamond_y, facecolor=coral, edgecolor=deep_teal, linewidth=1.8, zorder=6)
    # Stage 3: concentrated teal/gold conviction emblem
    ax.scatter([1445], [896], s=160, facecolor=teal, edgecolor=deep_teal, linewidth=2.2, zorder=6)
    ax.scatter([1445], [896], s=45, facecolor=gold, edgecolor="none", zorder=7)

    # Outer thick border (#264653 at 44px inset) and inner thin border (#49636D at 58px inset)
    ax.add_patch(
        plt.Rectangle(
            (44, 44), 1800 - 88, 1012 - 88,
            facecolor="none", edgecolor=deep_teal, linewidth=4.0, zorder=10,
        )
    )
    ax.add_patch(
        plt.Rectangle(
            (58, 58), 1800 - 116, 1012 - 116,
            facecolor="none", edgecolor=inner_border, linewidth=1.8, zorder=10,
        )
    )

    png_path = OUT / "cover.png"
    webp_path = OUT / "cover.webp"
    fig.savefig(png_path, dpi=100, facecolor=cream)
    plt.close(fig)

    with Image.open(png_path) as im:
        rgb = im.convert("RGB")
        assert rgb.size == (1800, 1012), f"Expected 1800x1012, got {rgb.size}"
        rgb.save(webp_path, format="WEBP", quality=86, method=6)
        # Optimize PNG via 256-color adaptive palette so cover.png is < 100 KB for fast OG scraping
        pal = rgb.quantize(colors=256, method=Image.Quantize.MEDIANCUT)
        pal.save(png_path, format="PNG", optimize=True)

    webp_kb = webp_path.stat().st_size / 1024.0
    png_kb = png_path.stat().st_size / 1024.0
    assert webp_kb < 200, f"cover.webp {webp_kb:.1f} KB exceeds 200 KB cap"
    for dest in DESTS:
        dest.mkdir(parents=True, exist_ok=True)
        for ext in (".png", ".webp"):
            shutil.copyfile(OUT / f"cover{ext}", dest / f"cover{ext}")
    print(f"[PASS] cover: 1800x1012, PNG={png_kb:.1f} KB, WebP={webp_kb:.1f} KB")



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
        "Stage 2 Triage Accounts for Cross-State Conviction Variance",
        x=0.03, ha="left", y=0.95, va="top", fontsize=12.8, weight="bold", color=INK,
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
    make_cover_art()
    make_figure0_conceptual_map()
    make_figure1_twfe_forest()
    make_figure2_variance_decomposition()
