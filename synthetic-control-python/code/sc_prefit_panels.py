#!/usr/bin/env python3
"""
sc_prefit_panels.py — the article figure for "Synthetic control in Python".
Two panels, SAME DGP/seed as sc_planted_truth.py (20260705): a VALID donor pool
(convex synthetic tracks the treated unit, honest pre-RMSPE 0.303, gap ~6) and an
UNUSABLE pool (convex synthetic cannot track, pre-RMSPE 7.613 -- the warning the
unrestricted perfect fit never gives). Writes a webp + a results.json sidecar with
a `plotted` contract so scripts/check_numeric_provenance.py can bind each annotated
number to the run.
"""
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from sc_planted_truth import simulate, sc_convex, SEED, T, T0

TREATED = "#E76F51"   # Warm Coral
SYNTH   = "#2A9D8F"   # Teal Green
INK     = "#264653"   # Deep Slate
MUTED   = "#6B7280"

OUT_IMG = "/Users/victoriaperez/Projects/tooearlytosay-work/public/images/methodology/synthetic-control-python/sc-prefit-panels.png"
OUT_JSON = "/Users/victoriaperez/Projects/tooearlytosay-work/public/images/methodology/synthetic-control-python/results.json"


def panel(ax, treated, synth, pre_rmspe, title, annotate_gap=None):
    t = np.arange(T)
    ax.axvline(T0, color=MUTED, ls="--", lw=1.2, zorder=1)
    ax.plot(t, treated, color=TREATED, lw=2.4, label="Treated unit", zorder=3)
    ax.plot(t, synth, color=SYNTH, lw=2.4, ls=(0, (5, 2)), label="Synthetic control", zorder=3)
    ax.set_title(title, color=INK, fontsize=13, fontweight="bold", pad=10)
    ax.set_xlabel("Period", color=INK, fontsize=11)
    ax.text(0.03, 0.94, f"pre-fit RMSPE {pre_rmspe:.3f}", transform=ax.transAxes,
            fontsize=11.5, color=INK, fontweight="bold", va="top")
    ax.tick_params(colors=INK, labelsize=10)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(MUTED)
    ax.text(T0 + 0.2, ax.get_ylim()[1], "treatment", color=MUTED, fontsize=9.5, va="top")
    if annotate_gap is not None:
        gx = T0 + (T - T0) / 2
        ax.annotate("", xy=(gx, treated[int(gx)]), xytext=(gx, synth[int(gx)]),
                    arrowprops=dict(arrowstyle="<->", color=INK, lw=1.3))
        ax.text(gx + 0.3, (treated[int(gx)] + synth[int(gx)]) / 2,
                f"gap {annotate_gap:.1f}", color=INK, fontsize=11, fontweight="bold", va="center")


def main():
    # VALID pool
    tv, dv = simulate(np.random.default_rng(SEED), valid_pool=True)
    wv, prev, gapv = sc_convex(tv, dv)
    synv = wv @ dv

    # UNUSABLE pool (treated loadings outside the donor hull)
    tb, db = simulate(np.random.default_rng(SEED + 7), valid_pool=False)
    wb, preb, gapb = sc_convex(tb, db)
    synb = wb @ db

    fig, (a1, a2) = plt.subplots(1, 2, figsize=(10.5, 4.3))
    fig.subplots_adjust(wspace=0.18, left=0.06, right=0.985, top=0.86, bottom=0.16)
    panel(a1, tv, synv, prev, "Valid pool: the pre-fit is earned", annotate_gap=round(gapv))
    panel(a2, tb, synb, preb, "Unusable pool: the pre-fit fails loudly")
    a1.legend(loc="lower left", frameon=False, fontsize=10, labelcolor=INK)

    fig.savefig(OUT_IMG, dpi=150, format="png")
    print(f"wrote {OUT_IMG}")

    sidecar = {
        "source": "sc_prefit_panels.py — same DGP/seed as sc_planted_truth.py (20260705)",
        "true_effect": 6.0,
        "valid_pre_rmspe": round(prev, 3),
        "invalid_pre_rmspe": round(preb, 3),
        "plotted": [
            {"label": "valid pool", "value": round(prev, 3)},
            {"label": "unusable pool", "value": round(preb, 3)},
        ],
    }
    with open(OUT_JSON, "w") as fh:
        json.dump(sidecar, fh, indent=2)
    print(f"wrote {OUT_JSON}")
    print(f"valid pre_rmspe={prev:.3f} gap={gapv:.3f} | invalid pre_rmspe={preb:.3f} gap={gapb:.3f}")


if __name__ == "__main__":
    main()
