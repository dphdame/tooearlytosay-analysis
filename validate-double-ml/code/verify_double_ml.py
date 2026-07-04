"""
The proof: apply the generic planted-truth check to double machine learning.

We plant a known treatment effect (theta = 1.0) in a partially linear model
whose treatment is confounded by high-dimensional X, then ask which estimator
recovers it:

  1. naive ML plug-in   -> attenuated (regularization/overfitting bias)
  2. cross-fitted DML    -> recovers close to 1.0

Then a limit: on a DGP with a HIDDEN confounder omitted from the controls, DML
is biased, yet a planted-truth check built on the SAME (incomplete) control set
still "recovers" the truth and passes. The check cannot see the omission.

Run:  python verify_double_ml.py
Deps: numpy, scikit-learn.
"""
import numpy as np

from verify_estimator import verify_estimator, report
from dml_plm import (simulate, simulate_omitted_confounder,
                     naive_plugin, dml_plm, dml_plm_se)

THETA_TRUE = 1.0


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
    naive_res = verify_estimator(naive_plugin, simulate, THETA_TRUE,
                                 tol=0.10, reps=reps, base_seed=0)
    dml_res = verify_estimator(dml_plm, simulate, THETA_TRUE,
                               tol=0.10, reps=reps, base_seed=0)
    report("naive ML plug-in", naive_res, THETA_TRUE)
    report("double ML (cross-fit)", dml_res, THETA_TRUE)
    print()
    return naive_res, dml_res


def omitted_confounder_limit(reps=50):
    """The limit: with a confounder omitted from the controls, DML is biased,
    but a planted-truth check on the SAME control set still passes. The test is
    blind to whether the controls are complete."""
    print(f"Limit: omitted confounder ({reps} draws):")
    dml_res = verify_estimator(dml_plm, simulate_omitted_confounder, THETA_TRUE,
                               tol=0.10, reps=reps, base_seed=0)
    report("double ML, U omitted", dml_res, THETA_TRUE)
    print("  The estimator is biased for the true effect, yet nothing in a")
    print("  simulation whose X also omits U would ever generate the bias to")
    print("  flag. An omitted confounder passes the planted-truth check unseen.")
    print()
    return dml_res


if __name__ == "__main__":
    single_draw()
    many_draws()
    omitted_confounder_limit()
