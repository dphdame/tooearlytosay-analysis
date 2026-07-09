#!/usr/bin/env python3
"""
matching_comprehension_figures.py — the 4 comprehension-increment figures for the matching article.
Imports the DGP straight from matching_planted_truth.py (so figures cannot drift from the frozen
numbers) and reads the SAME data/results.json the prose cites. Overlap-gated.
  fig-overlap          the two propensity distributions; the high-PS tail where treated have no control
  fig-balance-vs-bias  SMD before/after (balanced) set against the biased estimate
  fig-fix              naive match vs the two overlap-restoring fixes (trim, logit-caliper) vs planted
  fig-hard-limit       schematic: observed balanced + overlap fixed, estimate still wrong via unobserved U
"""
import os
import sys
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

sys.path.insert(0, os.path.dirname(__file__))
from matching_planted_truth import simulate, est_propensity, crump_mask, SEED  # noqa: E402

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
OUT = "/Users/victoriaperez/Projects/tooearlytosay-work/public/images/methodology/matching-python"
PROBLEMS = []
with open(os.path.join(os.path.dirname(__file__), "..", "data", "results.json")) as fh:
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
    os.makedirs(OUT, exist_ok=True)
    # reference draw (same seed the harness freezes), observed-confounding world
    rng = np.random.default_rng(SEED)
    X, d, y = simulate(rng, unobserved=False)
    ps = est_propensity(X, d)
    db = d.astype(bool)
    max_c = R["overlap_single"]["max_control_ps"]

    # ---- Fig overlap: the two propensity distributions; the tail with no controls ----
    fig, ax = plt.subplots(figsize=(8.2, 4.4)); _style(ax)
    bins = np.linspace(0, 1, 31)
    ax.hist(ps[~db], bins=bins, density=True, color=SLATE, alpha=0.55, label="controls")
    ax.hist(ps[db], bins=bins, density=True, color=CORAL, alpha=0.55, label="treated")
    ax.axvspan(max_c, 1.0, color=CORAL, alpha=0.12)
    ax.axvline(max_c, color=INK, ls="--", lw=1.3)
    ymax = ax.get_ylim()[1]
    ax.text(max_c - 0.03, ymax * 0.92, "no controls beyond here:\n6% of treated off support",
            ha="right", va="top", fontsize=10.5, color=INK, fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.3", fc="white", ec=INK, alpha=0.95))
    ax.set_xlabel("Estimated propensity score", color=INK, fontsize=11)
    ax.set_ylabel("Density", color=INK, fontsize=11)
    ax.legend(loc="upper center", frameon=False, fontsize=10.5, labelcolor=INK)
    ax.set_title("Balanced on average, yet the treated tail has no comparison", color=SLATE,
                 fontsize=12.5, fontweight="bold", pad=10)
    fig.tight_layout(); _save(fig, "fig-overlap")

    # ---- Fig balance-vs-bias: SMD before/after (balanced) beside the biased estimate ----
    before = R["smd_before_single"]; after = R["smd_after_single"]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(9.8, 4.4), gridspec_kw={"width_ratios": [1.25, 1]})
    _style(a1); _style(a2)
    ylab = ["X1", "X2"]; ypos = [1, 0]
    a1.axvline(0.10, color=MUTED, ls=":", lw=1.3)
    a1.text(0.32, 1.68, "dotted = 0.10 rule", ha="left", va="center", fontsize=9.5, color=MUTED)
    a1.scatter(before, ypos, s=90, color=CORAL, zorder=3, label="before matching")
    a1.scatter(after, ypos, s=90, color=TEAL, zorder=3, label="after matching")
    for b, a_, yp in zip(before, after, ypos):
        a1.annotate("", xy=(a_, yp), xytext=(b, yp),
                    arrowprops=dict(arrowstyle="->", color=MUTED, lw=1.4))
    a1.set_yticks(ypos); a1.set_yticklabels(ylab, color=INK, fontsize=11)
    a1.set_ylim(-0.6, 1.9); a1.set_xlim(-0.1, 1.9)
    a1.set_xlabel("Standardized mean difference", color=INK, fontsize=11)
    a1.legend(loc="upper right", frameon=False, fontsize=9.5, labelcolor=INK)
    a1.set_title("The balance table: clean after matching", color=SLATE, fontsize=11.5, fontweight="bold")
    # right: the estimate against the truth
    naive = R["att_full_match_single"]
    a2.bar(["matched\nestimate"], [naive], color=CORAL, width=0.5)
    a2.axhline(TRUE, color=INK, ls="--", lw=1.4, label=f"planted effect {TRUE:.1f}")
    a2.set_ylim(0, naive * 1.35)
    a2.text(0, naive + naive * 0.02, f"{naive:.2f}", ha="center", va="bottom", color=INK,
            fontsize=13, fontweight="bold")
    a2.legend(loc="upper right", frameon=False, fontsize=9.5, labelcolor=INK)
    a2.set_ylabel("Estimated ATT", color=INK, fontsize=11)
    a2.set_title("...but the estimate is 10% high", color=SLATE, fontsize=11.5, fontweight="bold")
    fig.tight_layout(); _save(fig, "fig-balance-vs-bias")

    # ---- Fig fix: naive vs two overlap-restoring fixes vs planted ----
    trim = R["att_crump_single"]
    logit_cal = R["logit_caliper_walk"]["0.20"]["att"]
    fig, ax = plt.subplots(figsize=(8.4, 4.6)); _style(ax)
    labels = ["naive match", "trimming\n[0.1, 0.9]", "logit caliper\n(Austin)"]
    vals = [naive, trim, logit_cal]
    cols = [CORAL, TEAL, TEAL]
    ax.bar(labels, vals, color=cols, width=0.6)
    ax.axhline(TRUE, color=INK, ls="--", lw=1.4, label=f"planted effect {TRUE:.1f}")
    ax.set_ylim(0, max(vals) * 1.25)
    for i, v in enumerate(vals):
        ax.text(i, v + max(vals) * 0.02, f"{v:.2f}", ha="center", va="bottom", color=INK,
                fontsize=12, fontweight="bold")
    ax.legend(loc="upper right", frameon=False, fontsize=10.5, labelcolor=INK)
    ax.set_ylabel("Estimated ATT", color=INK, fontsize=11)
    ax.set_title("Restoring common support recovers the planted effect, two ways", color=SLATE,
                 fontsize=12.5, fontweight="bold", pad=10)
    fig.tight_layout(); _save(fig, "fig-fix")

    # ---- Fig hard-limit: schematic (non-data) ----
    hard = R["hard_att_crump_single"]
    fig, ax = plt.subplots(figsize=(8.6, 3.8)); ax.axis("off"); ax.set_xlim(0, 10); ax.set_ylim(0, 4)

    def box(x, y, w, h, label, ec, fc=SURF, fs=11):
        ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h, boxstyle="round,pad=0.08",
                                     fc=fc, ec=ec, lw=2))
        ax.text(x, y, label, ha="center", va="center", fontsize=fs, fontweight="bold", color=ec)

    box(2.0, 3.1, 3.2, 0.8, "observed X balanced", TEAL)
    box(2.0, 1.9, 3.2, 0.8, "overlap restored", TEAL)
    box(7.2, 2.5, 3.0, 1.0, f"estimate {hard:.2f}\n(truth {TRUE:.1f})", CORAL, fs=12)
    ax.add_patch(FancyArrowPatch((3.7, 3.1), (5.7, 2.7), arrowstyle="-|>", mutation_scale=18,
                                 color=TEAL, lw=2))
    ax.add_patch(FancyArrowPatch((3.7, 1.9), (5.7, 2.3), arrowstyle="-|>", mutation_scale=18,
                                 color=TEAL, lw=2))
    # the uncheckable path: unobserved U feeds the bias
    box(5.0, 0.5, 2.6, 0.7, "unobserved U", MUTED, fc="white", fs=10.5)
    ax.add_patch(FancyArrowPatch((5.0, 0.9), (6.7, 2.0), connectionstyle="arc3,rad=-0.25",
                                 arrowstyle="-|>", mutation_scale=18, color=CORAL, lw=2, ls=(0, (4, 2))))
    fig.tight_layout(); _save(fig, "fig-hard-limit")

    # ---- sidecar (plotted contract binds fig-fix bars) ----
    sidecar = {
        "source": "matching_comprehension_figures.py — imports DGP from matching_planted_truth.py; "
                  "reads ../data/results.json (seed 20260705).",
        "true_effect": TRUE,
        "naive_match": naive,
        "trimming": trim,
        "logit_caliper": logit_cal,
        "hard_att": hard,
        "plotted": [
            {"label": "naive match", "value": naive},
            {"label": "trimming", "value": trim},
            {"label": "logit caliper", "value": logit_cal},
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
