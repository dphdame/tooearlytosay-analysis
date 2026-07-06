#!/usr/bin/env python3
"""
iv_planted_truth.py — planted-truth harness for the Too Early To Say article
"Instrumental variables in Python".

We plant a KNOWN causal effect of an endogenous regressor and test which estimator recovers it.
The point (priority-centered): 2SLS recovers the effect only if the instrument affects the outcome
ONLY through the regressor (the exclusion restriction). That assumption is not testable from the
data in the just-identified case; a strong first stage does not vouch for it. The catchable failure
(a weak instrument) is the one to NOT lead with, because it has a diagnostic (the first-stage F);
the uncatchable failure (a small direct effect of the instrument on the outcome) is the real limit.

DGP (one unobserved confounder U, one instrument Z):
  U ~ N(0,1)                          unobserved, confounds D and Y
  Z ~ N(0,1)                          instrument (valid: Z independent of U and of the outcome error)
  D = pi*Z + U + noise                endogenous regressor (Z relevant, U makes D endogenous)
  Y = TAU*D + 1.5*U + noise           planted effect TAU of D on Y, plus confounding through U

Estimators:
  - NAIVE (wrong): OLS of Y on D. Biased because D and Y share the unobserved U; controlling for
    observed covariates cannot fix it (U is unobserved).
  - CORRECT: 2SLS, beta = cov(Z, Y) / cov(Z, D). Uses only the part of D moved by Z, which is clean
    of U, so it recovers TAU -- IF the exclusion restriction holds.

Blind spots of THIS harness (quote in the article's Limits):
  - HARD limit (structurally uncatchable): if the instrument has ANY direct effect on the outcome
    (Z -> Y, not only through D), 2SLS is biased and, with a single instrument, NO in-sample test
    detects it -- the first-stage F is still large. A planted-truth check built on a VALID instrument
    recovers TAU and passes; it cannot see the exclusion violation.
  - Weak instruments are the EASY limit: a small pi gives a small first-stage F and unstable 2SLS,
    but that IS diagnosable from the data, so it is not the limit to dwell on.
"""
import json
import numpy as np

SEED = 20260705
N = 4000
TAU = 2.0          # planted causal effect of D on Y
PI = 0.8           # instrument strength (Z -> D)
DRAWS = 200


def simulate(rng, pi=PI, exclusion_violation=0.0):
    U = rng.normal(0, 1, N)                       # unobserved confounder
    Z = rng.normal(0, 1, N)                       # instrument
    D = pi * Z + U + rng.normal(0, 0.5, N)        # endogenous regressor
    Y = TAU * D + 1.5 * U + exclusion_violation * Z + rng.normal(0, 0.5, N)
    return Z, D, Y


def ols(D, Y):
    """Naive OLS slope of Y on D (with intercept)."""
    X = np.column_stack([np.ones(len(D)), D])
    beta = np.linalg.lstsq(X, Y, rcond=None)[0]
    return float(beta[1])


def tsls(Z, D, Y):
    """Just-identified 2SLS: beta = cov(Z, Y) / cov(Z, D)."""
    zc = Z - Z.mean()
    return float((zc @ (Y - Y.mean())) / (zc @ (D - D.mean())))


def first_stage_F(Z, D):
    """First-stage F for D ~ Z (single instrument): F = t^2."""
    zc = Z - Z.mean(); dc = D - D.mean()
    b = (zc @ dc) / (zc @ zc)
    resid = dc - b * zc
    se = np.sqrt((resid @ resid) / (len(Z) - 2) / (zc @ zc))
    return float((b / se) ** 2)


def main():
    rng = np.random.default_rng(SEED)
    Z, D, Y = simulate(rng)
    ols_single = ols(D, Y)
    tsls_single = tsls(Z, D, Y)
    F_single = first_stage_F(Z, D)

    # many-draw means (systematic)
    rng2 = np.random.default_rng(SEED + 1)
    ols_l, tsls_l, F_l = [], [], []
    for _ in range(DRAWS):
        z, d, y = simulate(rng2)
        ols_l.append(ols(d, y)); tsls_l.append(tsls(z, d, y)); F_l.append(first_stage_F(z, d))

    # NO-STRAWMAN SWEEP: the naive bias is not fixed by "adding controls" -- U is unobserved, so any
    # OLS that omits it stays biased. We show OLS bias is stable across sample sizes (not noise).
    ols_by_n = {}
    for n in (1000, 4000, 16000):
        rng3 = np.random.default_rng(SEED + 9)
        vals = []
        for _ in range(40):
            u = rng3.normal(0, 1, n); z = rng3.normal(0, 1, n)
            d = PI * z + u + rng3.normal(0, 0.5, n); yy = TAU * d + 1.5 * u + rng3.normal(0, 0.5, n)
            vals.append(ols(d, yy))
        ols_by_n[str(n)] = round(float(np.mean(vals)), 3)

    # WEAK-INSTRUMENT (easy, DIAGNOSABLE limit): small pi -> small first-stage F, unstable 2SLS.
    rng4 = np.random.default_rng(SEED + 3)
    weak_tsls, weak_F = [], []
    for _ in range(DRAWS):
        z, d, y = simulate(rng4, pi=0.05)
        weak_tsls.append(tsls(z, d, y)); weak_F.append(first_stage_F(z, d))

    # HARD limit (exclusion VIOLATION, uncatchable): Z has a small direct effect on Y. 2SLS biased,
    # first-stage F still large.
    rng5 = np.random.default_rng(SEED + 7)
    bad_tsls, bad_F = [], []
    for _ in range(DRAWS):
        z, d, y = simulate(rng5, exclusion_violation=0.5)
        bad_tsls.append(tsls(z, d, y)); bad_F.append(first_stage_F(z, d))

    results = {
        "source": "iv_planted_truth.py — planted IV, seed 20260705, N=4000, one confounder + one instrument",
        "true_effect": TAU,
        "ols_naive_single": round(ols_single, 3),
        "ols_naive_mean": round(float(np.mean(ols_l)), 3),
        "tsls_single": round(tsls_single, 3),
        "tsls_mean": round(float(np.mean(tsls_l)), 3),
        "first_stage_F_mean": round(float(np.mean(F_l)), 1),
        "ols_bias_mean": round(float(np.mean(ols_l)) - TAU, 3),
        "ols_by_sample_size": ols_by_n,
        "weak_tsls_mean": round(float(np.mean(weak_tsls)), 3),
        "weak_tsls_sd": round(float(np.std(weak_tsls)), 3),
        "weak_first_stage_F_mean": round(float(np.mean(weak_F)), 1),
        "exclusion_violation_tsls_mean": round(float(np.mean(bad_tsls)), 3),
        "exclusion_violation_first_stage_F_mean": round(float(np.mean(bad_F)), 1),
        "draws": DRAWS,
    }
    print(json.dumps(results, indent=2))
    with open("../data/results.json", "w") as fh:
        json.dump(results, fh, indent=2)
    print("\nwrote ../data/results.json")


if __name__ == "__main__":
    main()
