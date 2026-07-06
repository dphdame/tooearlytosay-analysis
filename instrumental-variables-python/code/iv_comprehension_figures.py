#!/usr/bin/env python3
"""
iv_comprehension_figures.py — the 4 comprehension-increment figures for the IV article.
Reads the SAME data/results.json the prose cites (iv_planted_truth.py output). Overlap-gated.
  fig-fix         OLS vs 2SLS vs planted truth
  fig-sample      OLS bias is stable across sample size (more data does not fix it)
  fig-two-limits  weak instrument (diagnosable, low F) vs exclusion violation (uncatchable, high F)
  fig-exclusion   concept schematic (non-data): the allowed Z->D->Y path vs the forbidden Z->Y path
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

SLATE, CORAL, TEAL, INK, MUTED, SURF = "#264653", "#E76F51", "#2A9D8F", "#0F172A", "#6B7280", "#FDF7F4"
OUT = "/Users/victoriaperez/Projects/tooearlytosay-work/public/images/methodology/instrumental-variables-python"
PROBLEMS = []
with open("../data/results.json") as fh:
    R = json.load(fh)
TRUE = R["true_effect"]


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
    ols, tsls = R["ols_naive_mean"], R["tsls_mean"]

    # ---- Fig fix: OLS vs 2SLS vs planted truth ----
    fig, ax = plt.subplots(figsize=(8.0, 4.4)); _style(ax)
    ax.bar(["OLS (naive)", "2SLS"], [ols, tsls], color=[CORAL, TEAL], width=0.55)
    ax.set_ylim(0, max(ols, tsls, TRUE) * 1.28)
    ax.axhline(TRUE, color=INK, ls="--", lw=1.4, label=f"planted effect {TRUE:.1f}")
    ax.legend(loc="upper right", frameon=False, fontsize=10.5, labelcolor=INK)
    for i, v in enumerate([ols, tsls]):
        ax.text(i, v + max(ols, tsls) * 0.02, f"{v:.2f}", ha="center", va="bottom", color=INK, fontsize=12, fontweight="bold")
    ax.set_ylabel("Estimated effect of D on Y", color=INK, fontsize=11)
    ax.set_title("OLS is biased by the confounder; 2SLS recovers the planted effect", color=SLATE, fontsize=12.5, fontweight="bold", pad=10)
    fig.tight_layout(); _save(fig, "fig-fix")

    # ---- Fig sample: OLS bias stable across n ----
    bn = R["ols_by_sample_size"]
    ns = sorted(bn, key=int); vals = [bn[n] for n in ns]
    fig, ax = plt.subplots(figsize=(8.0, 4.4)); _style(ax)
    ax.plot(range(len(ns)), vals, "o-", color=CORAL, lw=2.4, ms=9)
    ax.axhline(TRUE, color=INK, ls="--", lw=1.4, label=f"planted effect {TRUE:.1f}")
    ax.set_ylim(TRUE - 0.3, max(vals) + 0.25); ax.set_xlim(-0.4, len(ns) - 0.6)
    for i, v in enumerate(vals):
        ax.text(i, v + 0.03, f"{v:.2f}", ha="center", va="bottom", color=INK, fontsize=11, fontweight="bold")
    ax.set_xticks(range(len(ns))); ax.set_xticklabels([f"n = {int(n):,}" for n in ns], color=INK)
    ax.legend(loc="lower right", frameon=False, fontsize=10.5, labelcolor=INK)
    ax.set_ylabel("OLS estimate", color=INK, fontsize=11)
    ax.set_title("The OLS bias does not shrink with more data", color=SLATE, fontsize=12.5, fontweight="bold", pad=10)
    fig.tight_layout(); _save(fig, "fig-sample")

    # ---- Fig two-limits: weak instrument (diagnosable) vs exclusion violation (uncatchable) ----
    weak_est, weak_sd, weak_F = R["weak_tsls_mean"], R["weak_tsls_sd"], R["weak_first_stage_F_mean"]
    bad_est, bad_F = R["exclusion_violation_tsls_mean"], R["exclusion_violation_first_stage_F_mean"]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(9.6, 4.6)); _style(a1); _style(a2)
    # left: weak instrument — a point with a huge SD; truth via legend; F-note in bottom headroom
    a1.axhline(TRUE, color=INK, ls="--", lw=1.3, label=f"truth {TRUE:.1f}")
    a1.errorbar([0], [weak_est], yerr=[weak_sd], fmt="o", color=CORAL, ms=10, capsize=8, elinewidth=2,
                label=f"2SLS {weak_est:.2f} ± {weak_sd:.1f}")
    a1.set_xlim(-1, 1); a1.set_xticks([])
    a1.set_ylim(weak_est - weak_sd - 6.5, weak_est + weak_sd + 2)   # headroom below for the F-note
    a1.legend(loc="upper left", frameon=False, fontsize=9.5, labelcolor=INK, ncol=1)
    a1.text(0.5, 0.06, f"first-stage F = {weak_F:.0f}: low, so the weak\ninstrument shows itself", transform=a1.transAxes,
            ha="center", va="bottom", fontsize=10, color=TEAL, fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.3", fc="white", ec=TEAL, alpha=0.95))
    a1.set_ylabel("2SLS estimate", color=INK, fontsize=11)
    a1.set_title("Weak instrument: diagnosable", color=SLATE, fontsize=11.5, fontweight="bold")
    # right: exclusion violation — bar vs truth line (labelled via legend); F-note in top headroom
    a2.axhline(TRUE, color=INK, ls="--", lw=1.3, label=f"truth {TRUE:.1f}")
    a2.bar([0], [bad_est], color=CORAL, width=0.45)
    a2.set_xlim(-0.7, 0.7); a2.set_xticks([]); a2.set_ylim(0, bad_est * 1.5)
    a2.text(0, bad_est + bad_est * 0.02, f"2SLS {bad_est:.2f}", ha="center", va="bottom", color=INK, fontsize=12, fontweight="bold")
    a2.legend(loc="lower right", frameon=False, fontsize=9.5, labelcolor=INK)
    a2.text(0.5, 0.96, f"first-stage F = {bad_F:.0f}: large, so the\ninstrument still looks strong", transform=a2.transAxes,
            ha="center", va="top", fontsize=10, color=CORAL, fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.3", fc="white", ec=CORAL, alpha=0.95))
    a2.set_ylabel("2SLS estimate", color=INK, fontsize=11)
    a2.set_title("Exclusion violation: uncatchable", color=SLATE, fontsize=11.5, fontweight="bold")
    fig.tight_layout(); _save(fig, "fig-two-limits")

    # ---- Fig exclusion: concept schematic (non-data) ----
    fig, ax = plt.subplots(figsize=(8.6, 3.6)); ax.axis("off"); ax.set_xlim(0, 10); ax.set_ylim(0, 4)
    def node(x, y, label, ec):
        ax.add_patch(FancyBboxPatch((x - 0.5, y - 0.4), 1.0, 0.8, boxstyle="round,pad=0.08", fc=SURF, ec=ec, lw=2))
        ax.text(x, y, label, ha="center", va="center", fontsize=13, fontweight="bold", color=ec)
    node(1.5, 2.0, "Z", TEAL); node(5.0, 2.0, "D", INK); node(8.5, 2.0, "Y", INK)
    ax.add_patch(FancyArrowPatch((2.1, 2.0), (4.4, 2.0), arrowstyle="-|>", mutation_scale=20, color=TEAL, lw=2.2))
    ax.add_patch(FancyArrowPatch((5.6, 2.0), (7.9, 2.0), arrowstyle="-|>", mutation_scale=20, color=INK, lw=2.2))
    ax.text(3.25, 2.25, "allowed", ha="center", fontsize=10, color=TEAL, style="italic")
    ax.text(6.75, 2.25, "the effect", ha="center", fontsize=10, color=INK, style="italic")
    # forbidden direct path Z -> Y (curved dashed arrow); the full explanation lives in the HTML
    # <figcaption>, not baked into the image (schematic-caption convention, 2026-07-05).
    ax.add_patch(FancyArrowPatch((1.7, 1.55), (8.3, 1.55), connectionstyle="arc3,rad=0.32",
                                 arrowstyle="-|>", mutation_scale=20, color=CORAL, lw=2.2, ls=(0, (4, 2))))
    ax.text(5.0, 1.18, "direct Z → Y: forbidden", ha="center", va="center", fontsize=11,
            color=CORAL, fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.3", fc="white", ec=CORAL, alpha=0.95))
    fig.tight_layout(); _save(fig, "fig-exclusion")

    # ---- sidecar ----
    sidecar = {
        "source": "iv_comprehension_figures.py — reads ../data/results.json (iv_planted_truth.py, 20260705)",
        "true_effect": TRUE, "ols_naive": ols, "tsls": tsls,
        "ols_n1000": bn["1000"], "ols_n4000": bn["4000"], "ols_n16000": bn["16000"],
        "weak_tsls": weak_est, "weak_F": round(weak_F), "exclusion_tsls": bad_est, "exclusion_F": round(bad_F),
        "plotted": [
            {"label": "OLS (naive)", "value": ols},
            {"label": "2SLS", "value": tsls},
            {"label": "planted effect", "value": TRUE},
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
