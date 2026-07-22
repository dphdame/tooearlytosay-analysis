#!/usr/bin/env python3
"""
rdd_planted_truth.py — planted-truth harness for the Too Early To Say article
"Regression discontinuity in Python".

We plant a KNOWN treatment effect at a cutoff and test which estimator recovers it.
The point the harness makes:
  1. A naive GLOBAL polynomial returns a clean, plausible, WRONG number, and the
     number it returns swings with an arbitrary, unverifiable choice: the order.
  2. A LOCAL fit at the cutoff avoids committing to a global functional form and
     lands close to the truth, with an honest confidence interval.
  3. The local fit is close, NOT exact, and it depends on the bandwidth (a seam).
  4. A limit the harness CANNOT self-catch: if a second program switches on at the
     SAME cutoff, the estimate is biased and a McCrary density test still passes.

DGP (honest, so the lesson is real not a strawman):
  running var  X ~ Uniform(-1, 1)
  assignment   D = 1[X >= 0]                       (sharp)
  baseline     f(X) = sin(3X) + 0.5*exp(X)         (non-polynomial; no finite global
                                                    polynomial order is exactly correct)
  effect       tau(X) = 0.75 + 1.5*X               (heterogeneous: cutoff LATE 0.75
                                                    != treated-average 1.50, so RDD's
                                                    "identified only at the cutoff" is real)
  outcome      Y = f(X) + tau(X)*D + N(0, 0.7)

All results are reproducible from the fixed seed. No data download.
"""
import json
import sys
import numpy as np
import statsmodels.api as sm

SEED = 20260704
N = 2000
CUTOFF = 0.0
SIGMA = 0.7
CUTOFF_LATE = 0.75          # the planted truth: effect AT the cutoff
DRAWS = 200


def tau(x):
    return 0.75 + 1.5 * x


def f(x):
    return np.sin(3 * x) + 0.5 * np.exp(x)


def simulate(rng):
    x = rng.uniform(-1, 1, N)
    d = (x >= CUTOFF).astype(float)
    y = f(x) + tau(x) * d + rng.normal(0, SIGMA, N)
    return x, d, y


def global_poly(x, d, y, degree):
    cols = [d] + [x ** k for k in range(1, degree + 1)]
    return sm.OLS(y, sm.add_constant(np.column_stack(cols))).fit().params[1]


def local_linear(x, d, y, h):
    m = np.abs(x) <= h
    xw, dw, yw = x[m], d[m], y[m]
    w = 1 - np.abs(xw) / h                       # triangular kernel
    xd = sm.add_constant(np.column_stack([dw, xw, dw * xw]))
    res = sm.WLS(yw, xd, weights=w).fit(cov_type="HC3")
    return res.params[1], res.bse[1], int(m.sum())


def cv_bandwidth(x, d, y, grid):
    best_h, best_mse = None, np.inf
    for h in grid:
        errs = []
        for side in ((x < CUTOFF), (x >= CUTOFF)):
            xs, ys = x[side], y[side]
            m = np.abs(xs) <= h
            if m.sum() < 30:
                continue
            xm, ym = xs[m], ys[m]
            w = 1 - np.abs(xm) / h
            fit = sm.WLS(ym, sm.add_constant(xm), weights=w).fit()
            errs.append(np.mean((ym - fit.predict(sm.add_constant(xm))) ** 2))
        if errs and np.mean(errs) < best_mse:
            best_h, best_mse = h, np.mean(errs)
    return best_h


def simulate_compound(rng, jump):
    """A SECOND program also switches on at the cutoff (+jump to Y), no manipulation."""
    x = rng.uniform(-1, 1, N)
    d = (x >= CUTOFF).astype(float)
    y = f(x) + tau(x) * d + jump * d + rng.normal(0, SIGMA, N)
    return x, d, y


def mccrary_z(x, band=0.1):
    """Simple density-continuity check at the cutoff: counts just left vs right.

    NOTE: this is a two-proportion z-test on counts within `band` of the cutoff.
    It is NOT the McCrary (2008) local-linear density-discontinuity estimator,
    despite the function name. Production work should use rddensity.
    """
    left = np.sum((x >= -band) & (x < 0))
    right = np.sum((x >= 0) & (x < band))
    tot = left + right
    # z for a proportion test against 0.5 (smooth density -> ~equal counts)
    p = right / tot
    return (p - 0.5) / np.sqrt(0.25 / tot), int(left), int(right)



def verify_estimator(ll_est, ll_mean, naive_q, truth=CUTOFF_LATE):
    """Fail loudly if the planted truth is not recovered.

    Without this, the script exits 0 no matter what the estimator returns, so a
    replication package could silently stop demonstrating its own point. Any claim
    that this artifact fails loudly depends on this function existing.
    """
    failures = []
    if abs(ll_mean - truth) > 0.10:
        failures.append(
            f"local-linear 200-draw mean {ll_mean:.3f} is not within 0.10 of the "
            f"planted {truth}")
    if abs(ll_est - truth) > 0.30:
        failures.append(
            f"local-linear single draw {ll_est:.3f} is not within 0.30 of the "
            f"planted {truth}")
    if abs(naive_q - truth) <= abs(ll_mean - truth):
        failures.append(
            f"naive global quadratic {naive_q:.3f} is no worse than local-linear "
            f"{ll_mean:.3f}; the demonstration no longer demonstrates anything")
    if failures:
        for f in failures:
            print(f"VERIFY FAILED: {f}", file=sys.stderr)
        raise SystemExit(1)
    print("verify_estimator: OK — local-linear recovers the planted effect, "
          "naive global does not")


def main():
    rng = np.random.default_rng(SEED)
    x, d, y = simulate(rng)

    treated_avg = float(np.mean(tau(np.random.default_rng(1).uniform(0, 1, 200000))))

    # --- reference single draw ---
    naive_q = float(global_poly(x, d, y, 2))
    order_sweep_single = {str(k): float(global_poly(x, d, y, k)) for k in (2, 3, 5)}
    h = float(cv_bandwidth(x, d, y, np.linspace(0.08, 0.6, 27)))
    ll_est, ll_se, ll_n = local_linear(x, d, y, h)
    ll_ci = [float(ll_est - 1.96 * ll_se), float(ll_est + 1.96 * ll_se)]

    # --- bandwidth walk (single draw) ---
    walk = {f"{hh:.2f}": float(local_linear(x, d, y, hh)[0]) for hh in (0.10, 0.20, 0.30, 0.50, 0.75, 1.00)}

    # --- many-draw means (systematic, not one lucky seed) ---
    rng2 = np.random.default_rng(SEED + 1)
    naive_draws, ll_draws = [], []
    sweep_draws = {2: [], 3: [], 5: []}
    for _ in range(DRAWS):
        xx, dd, yy = simulate(rng2)
        naive_draws.append(global_poly(xx, dd, yy, 2))
        ll_draws.append(local_linear(xx, dd, yy, h)[0])
        for k in sweep_draws:
            sweep_draws[k].append(global_poly(xx, dd, yy, k))
    naive_mean = float(np.mean(naive_draws))
    ll_mean = float(np.mean(ll_draws))
    sweep_mean = {str(k): float(np.mean(v)) for k, v in sweep_draws.items()}

    # --- the hard limit: compound treatment at the cutoff ---
    xc, dc, yc = simulate_compound(np.random.default_rng(SEED + 2), jump=0.5)
    compound_est = float(local_linear(xc, dc, yc, h)[0])
    z, cl, cr = mccrary_z(xc)

    results = {
        "source": "rdd_planted_truth.py — planted-truth sharp RDD, seed 20260704, N=2000",
        "cutoff_late_truth": CUTOFF_LATE,
        "treated_average_effect_truth": round(treated_avg, 3),
        "naive_global_quadratic_single": round(naive_q, 3),
        "naive_global_quadratic_mean": round(naive_mean, 3),
        "order_sweep_single": {k: round(v, 3) for k, v in order_sweep_single.items()},
        "order_sweep_mean": {k: round(v, 3) for k, v in sweep_mean.items()},
        "local_linear_cv_bandwidth": round(h, 3),
        "local_linear_single": round(float(ll_est), 3),
        "local_linear_single_ci": [round(ll_ci[0], 3), round(ll_ci[1], 3)],
        "local_linear_mean": round(ll_mean, 3),
        "bandwidth_walk_single": {k: round(v, 3) for k, v in walk.items()},
        "compound_treatment_estimate": round(compound_est, 3),
        "mccrary_z": round(float(z), 3),
        "mccrary_counts": [cl, cr],
        "draws": DRAWS,
    }

    verify_estimator(float(ll_est), ll_mean, naive_q)

    print(json.dumps(results, indent=2))
    with open("../data/results.json", "w") as fh:
        json.dump(results, fh, indent=2)
    print("\nwrote ../data/results.json")


if __name__ == "__main__":
    main()
