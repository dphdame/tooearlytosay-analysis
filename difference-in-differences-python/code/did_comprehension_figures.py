#!/usr/bin/env python3
"""
did_comprehension_figures.py — the 4 comprehension-increment figures for the DiD article.
Reads the SAME data/results.json the prose cites (did_planted_truth.py output); the orient panel
re-simulates the frozen-seed DGP to draw the cohort paths. Overlap-gated.
  fig-orient        staggered-adoption panel: cohort mean outcomes over time
  fig-fix           TWFE vs CS vs planted truth (naive misses, clean-controls recovers)
  fig-sweep         the 4-scenario sweep: TWFE matches truth only under homogeneous+static
  fig-controls      concept schematic (non-data): clean vs contaminated controls
"""
import os
import sys
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

sys.path.insert(0, os.path.expanduser("~/.claude/scripts"))
try:
    from figure_overlap_check import check_overlaps
except ImportError:
    if os.environ.get("TETS_PUBLIC_REPLICATION") == "1":
        def check_overlaps(fig, label=""):
            return []
    else:
        raise SystemExit("figure_overlap_check not importable; set TETS_PUBLIC_REPLICATION=1 to skip QA.")

from did_planted_truth import simulate, SEED, T

SLATE, CORAL, TEAL, INK, MUTED, SURF = "#264653", "#E76F51", "#2A9D8F", "#0F172A", "#6B7280", "#FDF7F4"
OUT = "/Users/victoriaperez/Projects/tooearlytosay-work/public/images/methodology/difference-in-differences-python"
PROBLEMS = []
with open("../data/results.json") as fh:
    R = json.load(fh)


def _style(ax):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(MUTED)
    ax.tick_params(colors=INK, labelsize=10)


def _save(fig, name):
    for p in check_overlaps(fig, name):
        PROBLEMS.append(p); print("  OVERLAP:", p)
    fig.savefig(f"{OUT}/{name}.png", dpi=150)
    plt.close(fig)


def main():
    # ---- Fig orient: staggered-adoption panel (cohort mean outcomes over time) ----
    arr, _ = simulate(np.random.default_rng(SEED))
    t_, cohort_, y_ = arr[:, 1], arr[:, 2], arr[:, 3]
    fig, ax = plt.subplots(figsize=(8.4, 4.4)); _style(ax)
    series = [(4.0, CORAL, "Early cohort (adopts period 4)"),
              (7.0, TEAL, "Late cohort (adopts period 7)"),
              (-1.0, MUTED, "Never treated")]
    for g, c, lab in series:
        ys = [y_[(cohort_ == g) & (t_ == tt)].mean() for tt in range(T)]
        ax.plot(range(T), ys, "o-", color=c, lw=2.4, ms=5, label=lab)
    for gx, c in [(4, CORAL), (7, TEAL)]:
        ax.axvline(gx, color=c, ls="--", lw=1.1, alpha=0.6)
    ax.set_xlabel("Period", color=INK, fontsize=11); ax.set_ylabel("Mean outcome", color=INK, fontsize=11)
    ax.legend(loc="upper left", frameon=False, fontsize=9.5, labelcolor=INK)
    ax.set_title("Staggered adoption: each cohort turns on at its own time", color=SLATE, fontsize=12.5, fontweight="bold", pad=10)
    fig.tight_layout(); _save(fig, "fig-orient")

    # ---- Fig fix: TWFE vs CS vs planted truth ----
    truth = R["att_true_mean"]; twfe = R["twfe_static_mean"]; cs = R["cs_group_time_mean"]
    fig, ax = plt.subplots(figsize=(8.0, 4.4)); _style(ax)
    ax.bar(["Static TWFE", "Group-time (CS)"], [twfe, cs], color=[CORAL, TEAL], width=0.55)
    ax.set_ylim(0, max(twfe, cs, truth) * 1.28)
    ax.axhline(truth, color=INK, ls="--", lw=1.4, label=f"planted ATT {truth:.2f}")
    ax.legend(loc="upper left", frameon=False, fontsize=10.5, labelcolor=INK)
    for i, v in enumerate([twfe, cs]):
        ax.text(i, v + max(twfe, cs) * 0.02, f"{v:.2f}", ha="center", va="bottom", color=INK, fontsize=12, fontweight="bold")
    ax.set_ylabel("Estimated average effect", color=INK, fontsize=11)
    ax.set_title("Static TWFE misses the planted effect; clean controls recover it", color=SLATE, fontsize=12.5, fontweight="bold", pad=10)
    fig.tight_layout(); _save(fig, "fig-fix")

    # ---- Fig sweep: TWFE vs truth across 4 scenarios ----
    sw = R["no_strawman_sweep"]
    order = [("homogeneous_static", "Homogeneous\n+ static"),
             ("homogeneous_dynamic", "Homogeneous\n+ dynamic"),
             ("heterogeneous_early_larger", "Heterogeneous\nearly larger"),
             ("heterogeneous_late_larger", "Heterogeneous\nlate larger")]
    tw = [sw[k]["twfe"] for k, _ in order]; tr = [sw[k]["truth"] for k, _ in order]
    x = np.arange(len(order)); w = 0.38
    fig, ax = plt.subplots(figsize=(9.4, 4.6)); _style(ax)
    ax.bar(x - w / 2, tr, w, color=INK, label="Truth")
    ax.bar(x + w / 2, tw, w, color=CORAL, label="Static TWFE")
    ax.set_ylim(0, max(tr + tw) * 1.22)
    for xi, v in zip(x - w / 2, tr): ax.text(xi, v + 0.02, f"{v:.2f}", ha="center", va="bottom", color=INK, fontsize=9.5)
    for xi, v in zip(x + w / 2, tw): ax.text(xi, v + 0.02, f"{v:.2f}", ha="center", va="bottom", color=CORAL, fontsize=9.5, fontweight="bold")
    ax.set_xticks(x); ax.set_xticklabels([lab for _, lab in order], fontsize=9.5, color=INK)
    ax.legend(loc="upper left", frameon=False, fontsize=10, labelcolor=INK)
    ax.set_ylabel("Effect", color=INK, fontsize=11)
    ax.set_title("TWFE matches the truth only when effects are homogeneous AND static", color=SLATE, fontsize=12.5, fontweight="bold", pad=10)
    fig.tight_layout(); _save(fig, "fig-sweep")

    # ---- Fig controls: concept schematic (non-data) ----
    fig, ax = plt.subplots(figsize=(9.0, 3.8)); ax.axis("off"); ax.set_xlim(0, 10); ax.set_ylim(0, 4)
    # contaminated (left)
    b1 = FancyBboxPatch((0.3, 0.6), 4.2, 2.8, boxstyle="round,pad=0.1", fc=SURF, ec=CORAL, lw=2)
    ax.add_patch(b1)
    ax.text(2.4, 3.0, "Contaminated comparison", ha="center", fontsize=12, fontweight="bold", color=CORAL)
    ax.text(2.4, 1.9, "late cohort measured against\nthe ALREADY-TREATED early cohort,\nwhose effect is still growing", ha="center", fontsize=10, color=INK)
    # clean (right)
    b2 = FancyBboxPatch((5.5, 0.6), 4.2, 2.8, boxstyle="round,pad=0.1", fc=SURF, ec=TEAL, lw=2)
    ax.add_patch(b2)
    ax.text(7.6, 3.0, "Clean comparison", ha="center", fontsize=12, fontweight="bold", color=TEAL)
    ax.text(7.6, 1.9, "late cohort measured against\nthe NOT-YET-TREATED units only", ha="center", fontsize=10, color=INK)
    fig.tight_layout(); _save(fig, "fig-controls")

    # ---- sidecar ----
    sidecar = {
        "source": "did_comprehension_figures.py — reads ../data/results.json (did_planted_truth.py, 20260705)",
        "att_true": truth, "twfe_static": twfe, "cs_group_time": cs,
        "sweep_homog_static_twfe": sw["homogeneous_static"]["twfe"],
        "sweep_homog_dynamic_twfe": sw["homogeneous_dynamic"]["twfe"],
        "sweep_het_early_twfe": sw["heterogeneous_early_larger"]["twfe"],
        "sweep_het_late_twfe": sw["heterogeneous_late_larger"]["twfe"],
        "plotted": [
            {"label": "Static TWFE", "value": twfe},
            {"label": "Group-time (CS)", "value": cs},
            {"label": "planted ATT", "value": truth},
        ],
    }
    with open(f"{OUT}/results.json", "w") as fh:
        json.dump(sidecar, fh, indent=2)
    print("wrote 4 figures + results.json to", OUT)


if __name__ == "__main__":
    main()
    if PROBLEMS:
        print(f"\nOVERLAP GATE: FAIL — {len(PROBLEMS)}:"); [print("  -", p) for p in PROBLEMS]; sys.exit(1)
    print("\nOVERLAP GATE: PASS")
