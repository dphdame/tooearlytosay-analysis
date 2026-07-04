"""
verify_estimator: a drop-in planted-truth check for a reimplemented estimator.

Plant a KNOWN effect in simulated data, run the estimator many times, and check
whether it recovers the planted truth ON AVERAGE (bias), not on a single draw.
A single draw from a high-variance estimator cannot separate a bug from an
unlucky sample; the many-rep mean can, for the class of bugs that BIAS the
estimate.

Copy this function into your own work. It is a lightweight template, not a
package. Honest scope:
  - It checks that the estimator RECOVERS a planted truth in expectation.
  - It does NOT validate identification (parallel trends, exogeneity, ...).
  - It is BLIND to "measure-preserving" bugs that reshuffle which draw you get
    without biasing the estimator (e.g. shared-RNG-state / execution-order
    bugs). Those are caught by source review + a code invariant, not by this
    test. See the Limits section of the article.
  - It catches a biasing bug ONLY if your `simulate_dgp` exercises the feature
    that triggers it. The check is only as strong as the DGP you plant: it
    verifies recovery under the process you simulate, not correctness in general.

Deps: numpy.
"""
import numpy as np


def verify_estimator(estimator, simulate_dgp, true_effect, tol,
                     reps=1000, base_seed=0):
    """Run `estimator` on `reps` simulated datasets with a planted `true_effect`;
    report whether the mean estimate recovers it within `tol`.

    Parameters
    ----------
    estimator     : callable(data) -> float          the reimplementation under test
    simulate_dgp  : callable(true_effect, rng) -> data   plants the known effect
    true_effect   : float                             the planted ground truth
    tol           : float                             allowed |mean - true_effect|
    reps          : int                               Monte Carlo replications
    base_seed     : int                               reproducibility

    Returns
    -------
    dict with mean, mc_se (Monte Carlo SE of the mean), bias, passed, estimates.
    """
    est = np.empty(reps)
    for i in range(reps):
        rng = np.random.default_rng(base_seed + i)      # independent stream per rep
        est[i] = estimator(simulate_dgp(true_effect, rng))
    mean = float(est.mean())
    mc_se = float(est.std(ddof=1) / np.sqrt(reps))
    bias = mean - true_effect
    passed = abs(bias) <= tol
    return dict(mean=mean, mc_se=mc_se, bias=bias, sd=float(est.std(ddof=1)),
                passed=passed, estimates=est)


def report(name, result, true_effect):
    """One-line PASS/FAIL against the planted truth."""
    flag = "PASS" if result["passed"] else "FAIL"
    print(f"{name:<28} planted {true_effect:.2f} | recovered "
          f"{result['mean']:.3f} +/- {result['mc_se']:.3f} (MC SE) | "
          f"bias {result['bias']:+.3f} | {flag}")
    return result["passed"]
