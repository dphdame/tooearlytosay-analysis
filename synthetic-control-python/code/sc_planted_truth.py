#!/usr/bin/env python3
"""
sc_planted_truth.py — planted-truth harness for the Too Early To Say article
"Synthetic control in Python".

We can plant a KNOWN treatment effect in a simulated panel and test which way of building the
synthetic control recovers it. The point (priority-centered): the post-treatment gap is the least
trustworthy output. What matters is whether the PRE-treatment fit is honest (not overfit) and whether
the donor pool actually contains a valid counterfactual.

DGP (factor model, so a convex combination of donors CAN reproduce the treated unit's path):
  Y_it = lambda_i . F_t + noise,  t = 0..T-1;  treatment on unit 0 for t >= T0 adds a known effect.
  Donor loadings are drawn so the treated unit's loadings sit INSIDE their convex hull (a valid pool).

Estimators:
  - CORRECT: convex synthetic control (w >= 0, sum w = 1) minimizing pre-period MSPE (scipy SLSQP),
    then read the post gap, CHECK the pre-treatment RMSPE, and do placebo/permutation inference. Its
    pre-RMSPE is an HONEST diagnostic: small on a valid pool, LARGE when no counterfactual exists.
  - NAIVE (overfit): unrestricted least-squares weights on the pre-period. With more donors than
    pre-periods it fits the pre-period PERFECTLY (RMSPE = 0) -- on a VALID pool AND on an INVALID one.
    The perfect fit is false confidence: it is achievable for ANY treated unit, so it tells you
    nothing about whether the pool contains a real counterfactual, and it is higher-variance
    out-of-sample. The lesson is NOT "the naive number is biased" (it is not); it is that a perfect
    pre-fit is uninformative about validity, so the gap must be judged by the honest pre-RMSPE + the
    pool + permutation inference, never by the in-sample fit.

  DGP-SPECIFIC HEDGE (quote it; do not over-generalize): the naive overfit is unbiased HERE because
  the DGP is exactly linear everywhere, which is precisely the setting where Abadie's classic
  extrapolation-bias argument for convex weights cannot bite. On a valid pool the unrestricted fit is
  merely noisier; on an INVALID pool it is actively wrong (gap 4.299 vs truth 6.0) behind the same
  0.000 pre-fit. The takeaway is "unconstrained SC discards the diagnostic," NOT "unconstrained SC is
  fine, just noisier."

Blind spots of THIS harness (quote in the article's Limits):
  - The genuinely uncatchable part is narrow and exact: a good (small) pre-fit is NECESSARY but never
    SUFFICIENT to certify a valid counterfactual. On the invalid pool here the convex diagnostic DID
    fire loudly (pre-RMSPE 7.613), so "structurally uncatchable" overstates it -- what no in-sample
    number can rule out is a pool that pre-fits well yet has no valid counterfactual. That judgment is
    substantive (is this donor a plausible control?), not statistical.
  - Permutation inference is bounded below by 1/(J+1): with a small pool, conventional significance
    is unreachable regardless of the true effect size.
"""
import json
import numpy as np
from scipy.optimize import minimize

SEED = 20260705
T, T0, K = 24, 12, 3           # periods, pre-treatment periods, latent factors
J = 15                          # donors (J > T0 so the naive fit can overfit)
TAU = 6.0                       # planted treatment effect (post-treatment, on unit 0)
DRAWS = 200


def simulate(rng, valid_pool=True):
    F = rng.normal(0, 1, (T, K))                     # common factors over time
    donor_load = rng.normal(0, 1, (J, K))            # donor loadings
    if valid_pool:
        # treated loadings = a convex mix of donors (inside the hull -> a valid counterfactual exists)
        a = rng.dirichlet(np.ones(J))
        treat_load = a @ donor_load
    else:
        # IRRELEVANT pool: treated loadings shifted far outside the donor hull
        treat_load = rng.normal(0, 1, K) + 6.0
    donors = donor_load @ F.T + rng.normal(0, 0.5, (J, T))     # J x T
    treated = treat_load @ F.T + rng.normal(0, 0.5, T)         # T
    treated = treated.copy()
    treated[T0:] += TAU                                        # plant the effect post-T0
    return treated, donors


def _rmspe(resid):
    return float(np.sqrt(np.mean(resid ** 2)))


def sc_convex(treated, donors):
    """Convex synthetic control: w>=0, sum w=1, min pre-period MSPE."""
    n = donors.shape[0]                               # infer donor count (placebos drop one)
    Ypre_t, Ypre_d = treated[:T0], donors[:, :T0]     # T0 , n x T0
    def obj(w):
        return np.sum((Ypre_t - w @ Ypre_d) ** 2)
    w0 = np.ones(n) / n
    cons = ({"type": "eq", "fun": lambda w: np.sum(w) - 1},)
    bnds = [(0, 1)] * n
    res = minimize(obj, w0, method="SLSQP", bounds=bnds, constraints=cons,
                   options={"maxiter": 500, "ftol": 1e-10})
    w = res.x
    pre_rmspe = _rmspe(Ypre_t - w @ Ypre_d)
    synth_post = w @ donors[:, T0:]
    post_gap = float(np.mean(treated[T0:] - synth_post))
    return w, pre_rmspe, post_gap


def naive_overfit(treated, donors):
    """Unrestricted least-squares weights on the pre-period -> overfits, extrapolates."""
    Ypre_t, Ypre_d = treated[:T0], donors[:, :T0].T   # T0 , T0 x J
    w, *_ = np.linalg.lstsq(Ypre_d, Ypre_t, rcond=None)
    pre_rmspe = _rmspe(Ypre_t - Ypre_d @ w)
    synth_post = donors[:, T0:].T @ w
    post_gap = float(np.mean(treated[T0:] - synth_post))
    return pre_rmspe, post_gap


def naive_ridge(treated, donors, lam):
    """The naive family's MOST-OBVIOUS FIX for overfitting: ridge-shrink the unrestricted weights.
    lam is a FREE knob with no principled selector -- the no-strawman point. w = (X'X + lam I)^-1 X'y."""
    Ypre_t, Ypre_d = treated[:T0], donors[:, :T0].T        # T0 , T0 x J
    XtX = Ypre_d.T @ Ypre_d
    w = np.linalg.solve(XtX + lam * np.eye(XtX.shape[0]), Ypre_d.T @ Ypre_t)
    pre_rmspe = _rmspe(Ypre_t - Ypre_d @ w)
    post_gap = float(np.mean(treated[T0:] - donors[:, T0:].T @ w))
    return pre_rmspe, post_gap


def convex_gap_fitwindow(treated, donors, L):
    """Correct-method STABILITY WALK: convex SC fit on the LAST L pre-periods only (treatment date
    fixed at T0). The bandwidth analogue -- how much pre-history to fit on. Post window always T0..end."""
    n = donors.shape[0]
    lo = T0 - L
    Ypre_t, Ypre_d = treated[lo:T0], donors[:, lo:T0]
    def obj(w):
        return np.sum((Ypre_t - w @ Ypre_d) ** 2)
    cons = ({"type": "eq", "fun": lambda w: np.sum(w) - 1},)
    res = minimize(obj, np.ones(n) / n, method="SLSQP", bounds=[(0, 1)] * n,
                   constraints=cons, options={"maxiter": 500, "ftol": 1e-10})
    w = res.x
    pre_rmspe = _rmspe(Ypre_t - w @ Ypre_d)
    post_gap = float(np.mean(treated[T0:] - w @ donors[:, T0:]))
    return pre_rmspe, post_gap


def permutation_p(treated, donors):
    """Placebo: apply convex SC to each donor as-if-treated; rank treated post/pre RMSPE ratio."""
    def ratio(t, d):
        _, pre, _ = sc_convex(t, d)
        w, _, _ = sc_convex(t, d)
        post = _rmspe(t[T0:] - w @ d[:, T0:])
        return post / max(pre, 1e-8)
    treated_ratio = ratio(treated, donors)
    placebo = []
    for j in range(J):
        others = np.delete(donors, j, axis=0)
        placebo.append(ratio(donors[j], others))
    rank = 1 + sum(r >= treated_ratio for r in placebo)   # 1 = most extreme
    return rank / (J + 1), 1.0 / (J + 1)                  # p, and the floor


def main():
    rng = np.random.default_rng(SEED)
    treated, donors = simulate(rng, valid_pool=True)

    _, sc_pre, sc_gap = sc_convex(treated, donors)
    nv_pre, nv_gap = naive_overfit(treated, donors)
    perm_p, perm_floor = permutation_p(treated, donors)

    # NO-STRAWMAN SWEEP: the naive family's obvious fix for overfitting is to ridge-shrink the weights.
    # It does NOT cleanly rescue the real failure (invalid-pool blindness): it only trades the blind
    # perfect fit for an ARBITRARY knob. On the invalid pool the pre-RMSPE it reports is a direct
    # function of the unpickable lam (0.529 -> 5.469), whereas the convex constraint delivers the honest
    # 7.613 alarm with NO knob. (lam=0 is the singular unregularized case = naive_overfit, reported above.)
    rng_bad0 = np.random.default_rng(SEED + 7)
    tb0, db0 = simulate(rng_bad0, valid_pool=False)
    ridge_sweep = {"valid_pool": {}, "invalid_pool": {}}
    for lam in (0.1, 1.0, 10.0):
        pr, g = naive_ridge(treated, donors, lam)
        ridge_sweep["valid_pool"][str(lam)] = {"pre_rmspe": round(pr, 3), "gap": round(g, 3)}
        prb, gb = naive_ridge(tb0, db0, lam)
        ridge_sweep["invalid_pool"][str(lam)] = {"pre_rmspe": round(prb, 3), "gap": round(gb, 3)}

    # CORRECT-METHOD STABILITY WALK: convex SC over the pre-period fit window (treatment date fixed).
    # A referee-defensible estimator should not swing with this choice; report if it does. Also walk the
    # INVALID pool to confirm the choice cannot collapse the valid/invalid pre-RMSPE separation the whole
    # diagnostic argument rests on (it does not -- the alarm stays large at every window).
    fitwindow_walk = {"valid_pool": {}, "invalid_pool": {}}
    for L in (6, 9, 12):
        pr, g = convex_gap_fitwindow(treated, donors, L)
        fitwindow_walk["valid_pool"][str(L)] = {"pre_rmspe": round(pr, 3), "gap": round(g, 3)}
        prb, gb = convex_gap_fitwindow(tb0, db0, L)
        fitwindow_walk["invalid_pool"][str(L)] = {"pre_rmspe": round(prb, 3), "gap": round(gb, 3)}

    # HARD limit / the key contrast: an IRRELEVANT donor pool (no valid counterfactual).
    # Convex SC's pre-RMSPE blows up (the loud warning); the naive overfit STILL fits perfectly,
    # hiding the invalidity behind a perfect in-sample fit.
    rng_bad = np.random.default_rng(SEED + 7)
    t_bad, d_bad = simulate(rng_bad, valid_pool=False)
    _, bad_pre, bad_gap = sc_convex(t_bad, d_bad)
    nv_bad_pre, nv_bad_gap = naive_overfit(t_bad, d_bad)

    # many-draw means AND spread (overfitting inflates variance, not mean bias — the honest cost)
    rng2 = np.random.default_rng(SEED + 1)
    sc_gaps, nv_gaps, sc_bad_pre, nv_bad_pre_d = [], [], [], []
    for _ in range(DRAWS):
        t, d = simulate(rng2, valid_pool=True)
        sc_gaps.append(sc_convex(t, d)[2]); nv_gaps.append(naive_overfit(t, d)[1])
        tb, db = simulate(rng2, valid_pool=False)
        sc_bad_pre.append(sc_convex(tb, db)[1]); nv_bad_pre_d.append(naive_overfit(tb, db)[0])

    results = {
        "source": "sc_planted_truth.py — planted-truth synthetic control, seed 20260705, T=24 T0=12 J=15",
        "planted_effect_truth": TAU,
        "sc_convex_gap_single": round(sc_gap, 3),
        "sc_convex_gap_mean": round(float(np.mean(sc_gaps)), 3),
        "sc_convex_gap_sd": round(float(np.std(sc_gaps)), 3),
        "sc_convex_pre_rmspe_single": round(sc_pre, 3),
        "naive_overfit_gap_single": round(nv_gap, 3),
        "naive_overfit_gap_mean": round(float(np.mean(nv_gaps)), 3),
        "naive_overfit_gap_sd": round(float(np.std(nv_gaps)), 3),
        "naive_overfit_pre_rmspe_single": round(nv_pre, 3),
        "permutation_p_single": round(perm_p, 3),
        "permutation_p_floor": round(perm_floor, 3),
        "invalid_pool_convex_gap_single": round(bad_gap, 3),
        "invalid_pool_convex_pre_rmspe_single": round(bad_pre, 3),
        "invalid_pool_convex_pre_rmspe_mean": round(float(np.mean(sc_bad_pre)), 3),
        "invalid_pool_naive_gap_single": round(nv_bad_gap, 3),
        "invalid_pool_naive_pre_rmspe_single": round(nv_bad_pre, 3),
        "invalid_pool_naive_pre_rmspe_mean": round(float(np.mean(nv_bad_pre_d)), 3),
        "naive_ridge_sweep": ridge_sweep,
        "convex_fitwindow_walk": fitwindow_walk,
        "draws": DRAWS,
    }
    print(json.dumps(results, indent=2))
    with open("../data/results.json", "w") as fh:
        json.dump(results, fh, indent=2)
    print("\nwrote ../data/results.json")


if __name__ == "__main__":
    main()
