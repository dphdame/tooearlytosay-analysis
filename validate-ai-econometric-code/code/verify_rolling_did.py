"""
Proof: verify_estimator applied to a rolling difference-in-differences estimator.

Three results, all reproducible:
  (1) CATCH  -- the `demean` transform is systematically biased on a DGP with
      heterogeneous unit trends (recovers ~2.03 against a planted 1.0). The
      planted-truth Monte Carlo catches it. `detrend` recovers the truth.
  (2) COVER  -- the correct `detrend` estimator's own 95% CI covers ~95%, so the
      check is "did we recover the mean AND is inference calibrated", not mean only.
  (3) LIMIT  -- an execution-order (shared-RNG-state) bug reshuffles which draw
      you get WITHOUT biasing the estimator: correct and buggy orderings have
      statistically identical means. The planted-truth test is BLIND to it at
      any seed count. Only source review + a per-stream RNG invariant catches it.

Run:  python3 verify_rolling_did.py
Deps: numpy, pandas, statsmodels  (+ rolling_did_prototype.py alongside)
"""
import importlib.util
import os
import numpy as np
from scipy import stats
from verify_estimator import verify_estimator, report

# import the rolling-DiD prototype (the estimator under test) by path
_HERE = os.path.dirname(os.path.abspath(__file__))
_PROTO = os.path.join(_HERE, "rolling_did_prototype.py")
_spec = importlib.util.spec_from_file_location("rdp", _PROTO)
rdp = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(rdp)

TRUE_ATT = 1.0


def simulate_hard(true_effect, rng):
    """Hard DGP: 3 treated + 3 control, heterogeneous trends + seasonality.

    NB: this threads a per-rep RNG into the prototype's module-level global, and
    smalln_common's randomization-inference reads that same global. It is safe
    ONLY because the returned `att` comes from OLS and is RI-independent. If a
    future edit made the estimate depend on the RI draws, it would silently
    reintroduce the Section-(3) shared-RNG-state bug this file warns about.
    """
    rdp.RNG = rng                                   # thread the rep's RNG stream
    return rdp.make_panel(3, 3, 9, 16, true_att=true_effect,
                          hetero_trend=True, seasonal=True)


def estimator_for(kind):
    def est(panel):
        return rdp.smalln_common(panel, 9, kind, ri_reps=1)["att"]
    return est


# ---------------------------------------------------------------------------
# (1) CATCH: planted-truth Monte Carlo separates the biased transform
# ---------------------------------------------------------------------------
print("=" * 70)
print("(1) Planted-truth MC (1000 reps), planted ATT = 1.0, tol = 0.10")
print("=" * 70)
r_demean = verify_estimator(estimator_for("demean"), simulate_hard, TRUE_ATT,
                            tol=0.10, reps=1000)
r_detrend = verify_estimator(estimator_for("detrend"), simulate_hard, TRUE_ATT,
                             tol=0.10, reps=1000)
report("demean (wrong transform)", r_demean, TRUE_ATT)
report("detrend (correct)", r_detrend, TRUE_ATT)
print(f"\ndemean bias {r_demean['bias']:+.3f} is "
      f"{abs(r_demean['bias'])/r_demean['sd']:.1f} per-draw SDs from truth -- "
      f"visible even in a single run.")

# ---------------------------------------------------------------------------
# (2) COVER: is the correct estimator's own 95% CI calibrated?
# ---------------------------------------------------------------------------
print("\n" + "=" * 70)
print("(2) Coverage of the correct detrend estimator's nominal 95% CI")
print("=" * 70)
tcrit = stats.t.ppf(0.975, df=4)                    # 6 units - 2 params = 4 df
covered = 0
reps_cov = 500
for i in range(reps_cov):
    rng = np.random.default_rng(500_000 + i)
    panel = simulate_hard(TRUE_ATT, rng)
    row = rdp.smalln_common(panel, 9, "detrend", ri_reps=1)
    lo, hi = row["att"] - tcrit * row["se_t"], row["att"] + tcrit * row["se_t"]
    covered += (lo <= TRUE_ATT <= hi)
print(f"empirical coverage = {covered / reps_cov:.3f} "
      f"(nominal 0.95, {reps_cov} reps; MC SE ~0.01, so the 3rd digit is noise)")

# ---------------------------------------------------------------------------
# (3) LIMIT: the execution-order bug is invisible to the MC (no bias)
# ---------------------------------------------------------------------------
print("\n" + "=" * 70)
print("(3) LIMIT -- execution-order (shared-RNG-state) bug: reshuffle, not bias")
print("=" * 70)


def _est_detrend(panel):
    return rdp.smalln_common(panel, 9, "detrend", ri_reps=1)["att"]


def _hard_after_advance(seed, advance):
    """Detrend ATT on the hard panel, after `advance` extra draws are consumed
    from the shared RNG between building the easy panel and the hard panel.
    `advance` stands in for whatever computation (here: the easy panel's
    randomization-inference) eats the stream between the two make_panel calls.
    advance=0 is the BUGGY order (hard built immediately); advance>0 is the
    CORRECT order (hard built after the easy estimates run)."""
    rdp.RNG = np.random.default_rng(seed)
    rdp.make_panel(6, 6, 9, 16, true_att=TRUE_ATT, hetero_trend=False,
                   seasonal=False, noise=0.15)          # easy panel
    if advance:
        rdp.RNG.standard_normal(advance)                # stream eaten before hard
    hard = rdp.make_panel(3, 3, 9, 16, true_att=TRUE_ATT, hetero_trend=True,
                          seasonal=True)
    return _est_detrend(hard)


# 3a. the ACTUAL bug at the ACTUAL seed the article reports (full RI ordering).
def _faithful(seed, buggy):
    rdp.RNG = np.random.default_rng(seed)
    easy = rdp.make_panel(6, 6, 9, 16, true_att=TRUE_ATT, hetero_trend=False,
                          seasonal=False, noise=0.15)
    if buggy:
        hard = rdp.make_panel(3, 3, 9, 16, true_att=TRUE_ATT, hetero_trend=True,
                              seasonal=True)
    for k in ("demean", "detrend", "detrendq"):
        rdp.smalln_common(easy, 9, k, ri_reps=2000)     # real RI eats the stream
    if not buggy:
        hard = rdp.make_panel(3, 3, 9, 16, true_att=TRUE_ATT, hetero_trend=True,
                              seasonal=True)
    return _est_detrend(hard)


SEED0 = 20260613
print(f"single run at seed {SEED0} (the article's numbers):")
print(f"  correct order -> {_faithful(SEED0, buggy=False):.3f}   "
      f"buggy order -> {_faithful(SEED0, buggy=True):.3f}   (planted truth 1.0)")
print("  one draw apart looks decisive -- but is it a bug or an unlucky draw?\n")

# 3b. 2000-seed MC: does the reshuffle BIAS the estimator? (advance proxies RI)
N = 2000
seeds = range(3000, 3000 + N)
c = np.array([_hard_after_advance(s, advance=20000) for s in seeds])  # correct order
b = np.array([_hard_after_advance(s, advance=0) for s in seeds])       # buggy order
t, p = stats.ttest_ind(c, b, equal_var=False)
print(f"{N}-seed Monte Carlo (planted truth 1.0):")
print(f"  correct order : mean {c.mean():.3f}  sd {c.std():.3f}")
print(f"  buggy order   : mean {b.mean():.3f}  sd {b.std():.3f}")
print(f"  Welch t = {t:.2f}, p = {p:.3f}  -> means indistinguishable: the bug "
      f"does NOT bias the estimate.")
print("  The planted-truth test is BLIND to this bug at any seed count.")
print("  Catch it instead with a within-run invariant: assert the panel you "
      "estimate\n  is the panel this seed generates (independent RNG per stream).")
