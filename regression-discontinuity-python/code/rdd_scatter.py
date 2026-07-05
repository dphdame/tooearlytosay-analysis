#!/usr/bin/env python3
"""
rdd_scatter.py — the article's scatter figure, regenerated from the SAME seeded DGP as
rdd_planted_truth.py. Shows the global quadratic fit overshooting the jump at the cutoff
(reads 1.82) against the local-linear fit (reads 0.87, near the planted 0.75).
Writes figures/rdd-scatter.png. (The site build converts it to webp.)
"""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import statsmodels.api as sm

SEED = 20260704
rng = np.random.default_rng(SEED)
N = 2000
X = rng.uniform(-1, 1, N)
D = (X >= 0).astype(float)
Y = np.sin(3 * X) + 0.5 * np.exp(X) + (0.75 + 1.5 * X) * D + rng.normal(0, 0.7, N)

SLATE, CORAL, TEAL, INK = "#264653", "#E76F51", "#2A9D8F", "#0F172A"
fig, ax = plt.subplots(figsize=(8.4, 4.9), dpi=130)
idx = rng.choice(N, 600, replace=False)
ax.scatter(X[idx], Y[idx], s=8, c="#c7ccd1", alpha=0.6, linewidths=0, zorder=1)
ax.axvline(0, ls="--", c=INK, lw=1.2, zorder=2)

xs = np.linspace(-1, 1, 400)
gq = sm.OLS(Y, sm.add_constant(np.column_stack([D, X, X ** 2]))).fit().params
ax.plot(xs[xs < 0], gq[0] + gq[2] * xs[xs < 0] + gq[3] * xs[xs < 0] ** 2, c=CORAL, lw=2.4, zorder=3)
ax.plot(xs[xs >= 0], gq[0] + gq[1] + gq[2] * xs[xs >= 0] + gq[3] * xs[xs >= 0] ** 2, c=CORAL, lw=2.4,
        zorder=3, label="global quadratic (jump 1.82)")

h = 0.20
def ll(side):
    m = (np.abs(X) <= h) & side
    w = 1 - np.abs(X[m]) / h
    return sm.WLS(Y[m], sm.add_constant(X[m]), weights=w).fit().params
lL, lR = ll(X < 0), ll(X >= 0)
xl, xr = np.linspace(-h, 0, 50), np.linspace(0, h, 50)
ax.plot(xl, lL[0] + lL[1] * xl, c=TEAL, lw=3, zorder=4)
ax.plot(xr, lR[0] + lR[1] * xr, c=TEAL, lw=3, zorder=4, label="local linear (jump 0.87)")

ax.set_xlabel("running variable", color=INK, fontsize=12)
ax.set_ylabel("outcome", color=INK, fontsize=12)
ax.set_title("The jump at the cutoff: the global fit reads 1.82, the local fit 0.87",
             color=SLATE, fontsize=12.5, fontweight="bold", pad=10)
ax.legend(loc="upper left", fontsize=10, frameon=False)
ax.tick_params(colors=INK, labelsize=10)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
for s in ("left", "bottom"):
    ax.spines[s].set_color("#c7ccd1")
plt.tight_layout()
os.makedirs("figures", exist_ok=True)
plt.savefig("figures/rdd-scatter.png", dpi=130, bbox_inches="tight")
print("wrote figures/rdd-scatter.png")
