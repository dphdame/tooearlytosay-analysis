"""
The proof: apply the generic planted-truth check to double machine learning.

We plant a known treatment effect (theta = 1.0) in a partially linear model
whose treatment is confounded by high-dimensional X, then ask which estimator
recovers it:

  1. naive ML plug-in   -> attenuated (regularization/overfitting bias)
  2. cross-fitted DML    -> recovers close to 1.0

Then a limit: an explicit negative-control DGP adds a HIDDEN confounder omitted
from the controls, and DML must fail the planted-truth check. That failure is
visible only because the simulator plants the omission; a DGP that never
generates it cannot establish that the real controls are complete.

Run:  python verify_double_ml.py
Deps: numpy, scikit-learn.
"""
import os

import numpy as np

from verify_estimator import verify_estimator, report
from dml_plm import (simulate, simulate_omitted_confounder,
                     naive_plugin, dml_plm, dml_plm_se)

THETA_TRUE = 1.0
MC_WORKERS = min(4, os.cpu_count() or 1)


def assert_expected_status(name, result, expected):
    """Fail the runner when a control does not produce its expected status."""
    for field in ("mean", "mc_se", "bias", "sd"):
        if not np.isfinite(result[field]):
            raise AssertionError(f"{name}: non-finite {field} ({result[field]})")
    passed = result["passed"]
    if passed != expected:
        actual_status = "PASS" if passed else "FAIL"
        expected_status = "PASS" if expected else "FAIL"
        raise AssertionError(
            f"{name}: expected {expected_status}, got {actual_status}"
        )


def single_draw():
    """One draw, matching the article's headline numbers."""
    rng = np.random.default_rng(20260701)
    data = simulate(THETA_TRUE, rng)
    naive = naive_plugin(data)
    theta, se = dml_plm_se(data)
    print("Single planted-truth draw (seed 20260701):")
    print(f"  planted true effect      : {THETA_TRUE:.3f}")
    print(f"  naive ML plug-in         : {naive:.3f}   (bias {naive - THETA_TRUE:+.3f})")
    print(f"  double ML (cross-fitted) : {theta:.3f}   95% CI "
          f"[{theta - 1.96 * se:.3f}, {theta + 1.96 * se:.3f}]")
    print()


def many_draws(reps=50):
    """The bias is systematic, not a single-draw fluke: the mean over many
    independent draws still attenuates for the naive plug-in and recovers for
    DML."""
    print(f"Planted-truth check over {reps} draws (mean recovery):")
    print(f"  running independent draws with {MC_WORKERS} workers")
    naive_res = verify_estimator(naive_plugin, simulate, THETA_TRUE,
                                 tol=0.10, reps=reps, base_seed=0,
                                 workers=MC_WORKERS)
    dml_res = verify_estimator(dml_plm, simulate, THETA_TRUE,
                               tol=0.10, reps=reps, base_seed=0,
                               workers=MC_WORKERS)
    report("naive ML plug-in", naive_res, THETA_TRUE)
    report("double ML (cross-fit)", dml_res, THETA_TRUE)
    assert_expected_status("naive ML negative control", naive_res, expected=False)
    assert_expected_status("double ML estimator", dml_res, expected=True)
    print()
    return naive_res, dml_res


def omitted_confounder_limit(reps=50):
    """Negative control for the limit: explicitly plant an omitted confounder.

    This DGP should fail. The broader limit remains that a validation DGP that
    does not plant the omission cannot establish that real controls are complete.
    """
    print(f"Limit: omitted confounder ({reps} draws):")
    print(f"  running independent draws with {MC_WORKERS} workers")
    dml_res = verify_estimator(dml_plm, simulate_omitted_confounder, THETA_TRUE,
                               tol=0.10, reps=reps, base_seed=0,
                               workers=MC_WORKERS)
    report("double ML, U omitted", dml_res, THETA_TRUE)
    assert_expected_status(
        "omitted-confounder negative control", dml_res, expected=False
    )
    print("  This negative-control DGP explicitly plants hidden confounding,")
    print("  so FAIL is expected. A DGP that never generates the omitted U")
    print("  cannot establish that the real control set is complete.")
    print()
    return dml_res


if __name__ == "__main__":
    single_draw()
    many_draws()
    omitted_confounder_limit()
    print("Release gate: PASS (naive FAIL; double ML PASS; omitted confounder FAIL)")
