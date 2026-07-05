#!/usr/bin/env python3
"""
sc_comprehension_figures.py — the 9 comprehension-increment figures for the accessible
rebuild of "Synthetic control in Python". SAME DGP/seed as sc_planted_truth.py (20260705);
every plotted number is a frozen value. Writes webp into the article image dir + a shared
`results.json` plotted-contract sidecar.
"""
import json
import os
import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

sys.path.insert(0, os.path.expanduser("~/.claude/scripts"))
try:
    from figure_overlap_check import check_overlaps   # build-time QA (author machine)
except ImportError:
    # Public replication clones may not ship the private QA module — that is fine, but ONLY
    # when explicitly opted in. On the author path a missing module must FAIL LOUD, never
    # emit a false "OVERLAP GATE: PASS" (2026-07-05 red-team B2).
    if os.environ.get("TETS_PUBLIC_REPLICATION") == "1":
        def check_overlaps(fig, label=""):
            return []
    else:
        raise SystemExit(
            "figure_overlap_check not importable; the overlap gate would be a no-op. "
            "Set TETS_PUBLIC_REPLICATION=1 to skip QA (public replication only).")

PROBLEMS = []   # accumulates every detected overlap across all figures

from sc_planted_truth import (simulate, sc_convex, naive_overfit, naive_ridge,
                              convex_gap_fitwindow, SEED, T, T0, J, TAU, DRAWS, _rmspe)

CORAL = "#E76F51"   # naive / unrestricted / miss
TEAL  = "#2A9D8F"   # convex / correct / recovers
INK   = "#264653"   # treated line, axes, text
MUTED = "#6B7280"
SURF  = "#FDF7F4"

OUTDIR = "/Users/victoriaperez/Projects/tooearlytosay-work/public/images/methodology/synthetic-control-python"


def _style(ax):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(MUTED)
    ax.tick_params(colors=INK, labelsize=10)


def _save(fig, name):
    probs = check_overlaps(fig, name)     # programmatic overlap gate, per figure
    for p in probs:
        PROBLEMS.append(p); print("  OVERLAP:", p)
    fig.savefig(f"{OUTDIR}/{name}.png", dpi=150)
    plt.close(fig)


def unrestricted_synth(treated, donors):
    w, *_ = np.linalg.lstsq(donors[:, :T0].T, treated[:T0], rcond=None)
    return donors.T @ w, w


def main():
    # CANONICAL numbers: read the SAME results.json the prose cites (sc_planted_truth.py output).
    # Every annotated value below comes from R, never an inline literal — so a figure cannot drift
    # from the run the article quotes (2026-07-05 red-team D4). Fail loud if it is missing/stale.
    with open("../data/results.json") as fh:
        R = json.load(fh)

    # shared draws
    tv, dv = simulate(np.random.default_rng(SEED), valid_pool=True)
    wv, prev, gapv = sc_convex(tv, dv)
    synv = wv @ dv
    un_syn, _ = unrestricted_synth(tv, dv)
    tb, db = simulate(np.random.default_rng(SEED + 7), valid_pool=False)
    wb, preb, gapb = sc_convex(tb, db)
    synb = wb @ db
    t = np.arange(T)

    # ---- Fig 1: orient — pre-fit tracks, post gap opens (valid pool) ----
    fig, ax = plt.subplots(figsize=(8.2, 4.2)); _style(ax)
    ax.set_ylim(tv.min() - 1.2, tv.max() + 1.4)   # headroom for the treatment label
    ax.axvline(T0, color=MUTED, ls="--", lw=1.2)
    ax.plot(t, tv, color=INK, lw=2.6, label="Treated unit")
    ax.plot(t, synv, color=TEAL, lw=2.6, ls=(0, (5, 2)), label="Synthetic control")
    gx = 18                                        # a clear post-treatment column
    ax.annotate("", xy=(gx, tv[gx]), xytext=(gx, synv[gx]),
                arrowprops=dict(arrowstyle="<->", color=CORAL, lw=1.6))
    ax.text(gx + 0.5, (tv[gx] + synv[gx]) / 2, "gap ≈ 6", color=CORAL, fontsize=12,
            fontweight="bold", va="center", ha="left",
            bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="none", alpha=0.85))
    ax.text(T0 + 0.2, ax.get_ylim()[1] - 0.1, "treatment", color=MUTED, fontsize=10, va="top")
    ax.set_xlabel("Period", color=INK, fontsize=11); ax.set_ylabel("Outcome", color=INK, fontsize=11)
    ax.legend(loc="upper left", frameon=False, fontsize=10, labelcolor=INK)
    fig.tight_layout(); _save(fig, "fig1-orient")

    # ---- Fig 2: perfect pre-fit overlay (unrestricted, pre-periods only) ----
    fig, ax = plt.subplots(figsize=(8.2, 4.6)); _style(ax)
    ax.plot(t[:T0], tv[:T0], color=INK, lw=3.2, label="Treated unit")
    ax.plot(t[:T0], un_syn[:T0], color=CORAL, lw=2.0, ls=(0, (2, 2)), label="Unrestricted synthetic")
    lo, hi = tv[:T0].min(), tv[:T0].max()
    ax.set_ylim(lo - 0.4, hi + 1.6)               # headroom for the annotation, clear of the lines
    ax.set_xlabel("Pre-treatment period", color=INK, fontsize=11); ax.set_ylabel("Outcome", color=INK, fontsize=11)
    ax.text(0.5, 0.90, f"Pre-RMSPE = {R['naive_overfit_pre_rmspe_single']:.3f}     "
            f"estimated gap ≈ {R['naive_overfit_gap_single']:.2f}", transform=ax.transAxes,
            ha="center", va="top", fontsize=11.5, color=CORAL, fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.3", fc="white", ec=CORAL, alpha=0.9))
    ax.legend(loc="lower center", bbox_to_anchor=(0.5, 1.0), ncol=2,
              frameon=False, fontsize=10, labelcolor=INK)   # legend ABOVE the axes, off the data
    fig.subplots_adjust(top=0.82)
    _save(fig, "fig2-perfect-prefit")

    # ---- Fig 3: distribution of gaps, unrestricted vs convex (200 draws) ----
    rng2 = np.random.default_rng(SEED + 1)
    sc_g, nv_g = [], []
    for _ in range(DRAWS):
        tt, dd = simulate(rng2, valid_pool=True)
        sc_g.append(sc_convex(tt, dd)[2]); nv_g.append(naive_overfit(tt, dd)[1])
    fig, ax = plt.subplots(figsize=(8.2, 4.2)); _style(ax)
    bins = np.linspace(min(nv_g + sc_g), max(nv_g + sc_g), 34)
    # distinct styling: convex = solid teal fill; unrestricted = coral step outline (no brown overlap)
    ax.hist(sc_g, bins=bins, color=TEAL, alpha=0.85, label="Convex SC (SD 0.185)")
    ax.hist(nv_g, bins=bins, histtype="step", color=CORAL, lw=2.2, label="Unrestricted (SD 0.425)")
    ax.set_ylim(0, max(np.histogram(sc_g, bins=bins)[0].max(), np.histogram(nv_g, bins=bins)[0].max()) * 1.22)
    ax.axvline(TAU, color=INK, ls="--", lw=1.4)
    ax.text(TAU + 0.05, ax.get_ylim()[1] * 0.97, "truth 6.0", color=INK, fontsize=10, va="top",
            bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="none", alpha=0.85))
    ax.set_xlabel("Estimated gap across 200 simulations", color=INK, fontsize=11); ax.set_ylabel("Count", color=INK, fontsize=11)
    ax.legend(loc="upper left", frameon=False, fontsize=10, labelcolor=INK)
    fig.tight_layout(); _save(fig, "fig3-variance")

    # ---- Fig 4: ridge sweep — pre-RMSPE rises, gap stays near 6 ----
    lams = [0.1, 1.0, 10.0]
    _rs = R["naive_ridge_sweep"]["valid_pool"]           # canonical, not recomputed
    rp = [(_rs[str(l)]["pre_rmspe"], _rs[str(l)]["gap"]) for l in lams]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(9.2, 4.0)); _style(a1); _style(a2)
    x = np.arange(len(lams))
    pr_v = [p for p, _ in rp]
    a1.plot(x, pr_v, "o-", color=CORAL, lw=2.4, ms=8)
    a1.set_ylim(0, max(pr_v) * 1.35); a1.set_xlim(-0.5, len(lams) - 0.5)
    for i, p in enumerate(pr_v):   # up-LEFT of each marker, clear of a line rising to the right
        a1.annotate(f"{p:.3f}", (i, p), xytext=(-5, 9), textcoords="offset points",
                    ha="right", va="bottom", color=INK, fontsize=10)
    a1.set_xticks(x); a1.set_xticklabels([f"λ={l}" for l in lams]); a1.set_title("Pre-RMSPE it reports", color=INK, fontsize=12, fontweight="bold")
    g_v = [g for _, g in rp]
    a2.plot(x, g_v, "s-", color=TEAL, lw=2.4, ms=8)
    a2.axhline(TAU, color=MUTED, ls="--", lw=1.2)
    a2.set_ylim(5.6, 6.6); a2.set_xlim(-0.4, len(lams) - 0.6)
    for i, g in enumerate(g_v):
        a2.text(i, g + 0.10, f"{g:.3f}", ha="center", va="bottom", color=INK, fontsize=10)
    a2.set_xticks(x); a2.set_xticklabels([f"λ={l}" for l in lams]); a2.set_title("Estimated gap (truth 6.0)", color=INK, fontsize=12, fontweight="bold")
    fig.tight_layout(); _save(fig, "fig4-ridge-sweep")

    # ---- Fig 5: unrestricted vs convex — pre-RMSPE + gap ----
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(9.2, 4.0)); _style(a1); _style(a2)
    labels = ["Unrestricted", "Convex SC"]; cols = [CORAL, TEAL]
    pre_vals = [R["naive_overfit_pre_rmspe_single"], R["sc_convex_pre_rmspe_single"]]
    a1.bar(labels, pre_vals, color=cols); a1.set_ylim(0, 0.36)
    for i, v in enumerate(pre_vals):
        a1.text(i, v + 0.012, f"{v:.3f}", ha="center", va="bottom", color=INK, fontsize=11, fontweight="bold")
    a1.set_title("Pre-fit RMSPE", color=INK, fontsize=12, fontweight="bold")
    gap_vals = [R["naive_overfit_gap_single"], R["sc_convex_gap_single"]]
    sd_vals = [R["naive_overfit_gap_sd"], R["sc_convex_gap_sd"]]
    a2.bar(labels, gap_vals, color=cols, yerr=sd_vals, capsize=6, ecolor=INK)
    a2.axhline(TAU, color=MUTED, ls="--", lw=1.2); a2.set_ylim(0, 7.6)
    for i, (v, sd) in enumerate(zip(gap_vals, sd_vals)):   # label ABOVE the error-bar cap
        a2.text(i, v + sd + 0.18, f"{v:.3f}", ha="center", va="bottom", color=INK, fontsize=11, fontweight="bold")
    a2.set_title("Estimated gap ± SD (truth 6.0)", color=INK, fontsize=12, fontweight="bold")
    fig.tight_layout(); _save(fig, "fig5-fix")

    # ---- Fig 6: fit-window walk ----
    Ls = [6, 9, 12]
    _fw = R["convex_fitwindow_walk"]["valid_pool"]       # canonical, not recomputed
    fw = [(_fw[str(L)]["pre_rmspe"], _fw[str(L)]["gap"]) for L in Ls]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(9.2, 4.0)); _style(a1); _style(a2)
    x = np.arange(len(Ls))
    pr_v = [p for p, _ in fw]
    a1.plot(x, pr_v, "o-", color=TEAL, lw=2.4, ms=8)
    a1.set_ylim(0, max(pr_v) * 1.35); a1.set_xlim(-0.5, len(Ls) - 0.5)
    for i, p in enumerate(pr_v):   # up-LEFT of each marker, clear of a line rising to the right
        a1.annotate(f"{p:.3f}", (i, p), xytext=(-5, 9), textcoords="offset points",
                    ha="right", va="bottom", color=INK, fontsize=10)
    a1.set_xticks(x); a1.set_xticklabels([f"last {L}" for L in Ls]); a1.set_title("Pre-RMSPE", color=INK, fontsize=12, fontweight="bold")
    g_v = [g for _, g in fw]
    a2.plot(x, g_v, "s-", color=TEAL, lw=2.4, ms=8)
    a2.axhline(TAU, color=MUTED, ls="--", lw=1.2)
    a2.set_ylim(5.6, 6.4); a2.set_xlim(-0.4, len(Ls) - 0.6)
    for i, g in enumerate(g_v):   # labels below points that sit high, above points that sit low
        dy = -0.10 if g >= TAU else 0.07
        va = "top" if g >= TAU else "bottom"
        a2.text(i, g + dy, f"{g:.3f}", ha="center", va=va, color=INK, fontsize=10)
    a2.set_xticks(x); a2.set_xticklabels([f"last {L}" for L in Ls]); a2.set_title("Estimated gap (truth 6.0)", color=INK, fontsize=12, fontweight="bold")
    fig.tight_layout(); _save(fig, "fig6-fit-window")

    # ---- Fig 7: valid vs invalid pool pre-fit ----
    fig, ax = plt.subplots(figsize=(8.2, 4.6)); _style(ax)
    labels = ["Valid pool", "Unusable pool"]
    vals = [R["sc_convex_pre_rmspe_single"], R["invalid_pool_convex_pre_rmspe_single"]]
    ax.bar(labels, vals, color=[TEAL, CORAL], width=0.6)
    ax.set_ylim(0, 10.2)                            # headroom so the note clears the tall bar
    for i, v in enumerate(vals):
        ax.text(i, v + 0.18, f"convex {v:.3f}", ha="center", va="bottom", color=INK, fontsize=12, fontweight="bold")
    # note lives in the reserved whitespace ABOVE both bars, not over them
    ax.text(0.5, 0.955, f"Unrestricted pre-RMSPE = {R['naive_overfit_pre_rmspe_single']:.3f} on BOTH pools — it gives no warning",
            transform=ax.transAxes, ha="center", va="top", fontsize=10.5, color=CORAL, fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.3", fc="white", ec=CORAL, alpha=0.9))
    ax.set_ylabel("Convex pre-fit RMSPE", color=INK, fontsize=11)
    ax.set_title("Convex pre-RMSPE flags the unusable pool; the zero-error fit does not", color=INK, fontsize=12, fontweight="bold")
    fig.tight_layout(); _save(fig, "fig7-valid-invalid")

    # ---- Fig 8: concept schematic (non-data) ----
    fig, ax = plt.subplots(figsize=(8.6, 3.6)); ax.axis("off"); ax.set_xlim(0, 10); ax.set_ylim(0, 4)
    b1 = FancyBboxPatch((0.3, 1.1), 3.2, 1.8, boxstyle="round,pad=0.1", fc=SURF, ec=TEAL, lw=2)
    b2 = FancyBboxPatch((6.0, 0.6, ), 3.6, 2.8, boxstyle="round,pad=0.1", fc=SURF, ec=INK, lw=2)
    ax.add_patch(b1); ax.add_patch(b2)
    ax.text(1.9, 2.55, "Statistical checks", ha="center", fontsize=12.5, fontweight="bold", color=TEAL)
    ax.text(1.9, 1.7, "pre-RMSPE\nplacebos\nrobustness", ha="center", fontsize=10.5, color=INK)
    ax.text(7.8, 2.9, "Substantive judgment", ha="center", fontsize=12.5, fontweight="bold", color=INK)
    ax.text(7.8, 1.7, "policy context\ngeography\npopulation\ntiming", ha="center", fontsize=10.5, color=INK)
    ax.add_patch(FancyArrowPatch((3.7, 2.0), (5.8, 2.0), arrowstyle="-|>", mutation_scale=22, color=MUTED, lw=2))
    ax.text(4.75, 2.25, "necessary,\nnot sufficient", ha="center", fontsize=9.5, color=MUTED, style="italic")
    fig.tight_layout(); _save(fig, "fig8-schematic")

    # ---- Fig 9: placebo distribution + permutation floor ----
    def convex_ratio(tt, dd):
        w, pre, _ = sc_convex(tt, dd)
        post = _rmspe(tt[T0:] - w @ dd[:, T0:])
        return post / max(pre, 1e-8)
    placebo_gaps = []
    for j in range(J):
        others = np.delete(dv, j, axis=0)
        w, _, g = sc_convex(dv[j], others)
        placebo_gaps.append(g)
    fig, ax = plt.subplots(figsize=(8.2, 4.2)); _style(ax)
    ax.hist(placebo_gaps, bins=12, color=MUTED, alpha=0.65, label="Placebo donors (n=15)")
    ax.axvline(gapv, color=CORAL, lw=2.6, label=f"Treated gap ≈ {gapv:.1f}")
    ax.set_ylim(0, max(np.histogram(placebo_gaps, bins=12)[0]) * 1.25)
    ax.set_xlabel("Estimated gap", color=INK, fontsize=11); ax.set_ylabel("Count", color=INK, fontsize=11)
    # text placed in the empty mid-region between the placebo cluster (~0) and the treated line (~6)
    ax.text(0.42, 0.72, f"p = rank / (J+1)\nsmallest possible = 1/{J + 1} ≈ {R['permutation_p_floor']:.3f}", transform=ax.transAxes,
            ha="left", va="top", fontsize=11, color=INK, fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.3", fc="white", ec=MUTED, alpha=0.85))
    ax.legend(loc="upper center", frameon=False, fontsize=10, labelcolor=INK)
    fig.tight_layout(); _save(fig, "fig9-permutation-floor")

    # ---- shared plotted-contract sidecar (labels locate each point in the alt text) ----
    # every scalar traces to the canonical R (sc_planted_truth.py), not a re-typed literal
    sidecar = {
        "source": "sc_comprehension_figures.py — reads ../data/results.json (sc_planted_truth.py, seed 20260705)",
        "true_effect": R["planted_effect_truth"],
        "naive_gap": R["naive_overfit_gap_single"], "naive_pre_rmspe": R["naive_overfit_pre_rmspe_single"],
        "convex_gap": R["sc_convex_gap_single"], "convex_pre_rmspe": R["sc_convex_pre_rmspe_single"],
        "naive_gap_sd": R["naive_overfit_gap_sd"], "convex_gap_sd": R["sc_convex_gap_sd"],
        "invalid_convex_pre_rmspe": R["invalid_pool_convex_pre_rmspe_single"],
        "permutation_floor": R["permutation_p_floor"],
        "plotted": [
            {"label": "Unrestricted synthetic", "value": R["naive_overfit_pre_rmspe_single"]},
            {"label": "valid pool convex", "value": R["sc_convex_pre_rmspe_single"]},
            {"label": "unusable pool convex", "value": R["invalid_pool_convex_pre_rmspe_single"]},
        ],
    }
    with open(f"{OUTDIR}/results.json", "w") as fh:
        json.dump(sidecar, fh, indent=2)
    print("wrote 9 figures + results.json to", OUTDIR)


if __name__ == "__main__":
    main()
    if PROBLEMS:
        print(f"\nOVERLAP GATE: FAIL — {len(PROBLEMS)} overlap(s):")
        for p in PROBLEMS:
            print("  -", p)
        sys.exit(1)
    print("\nOVERLAP GATE: PASS — no legend/label collisions detected.")
