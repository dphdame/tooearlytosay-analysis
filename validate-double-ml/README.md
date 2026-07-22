# Validate Double Machine Learning

Replication materials for ["Validating a Double Machine Learning Estimate"](https://tooearlytosay.com/research/methodology/validate-double-ml/)

## Overview

Double machine learning (DML) folds a flexible machine-learning model into a causal estimator: it lets
the model estimate high-dimensional nuisance functions while still recovering the treatment effect at
the usual parametric rate. A **naive** way to do this — regress the outcome on an in-sample ML prediction
of the controls, then OLS on the treatment — runs cleanly and returns an **attenuated** effect. This
project ships the check that catches it: plant a **known** treatment effect in simulated data and test
whether each implementation recovers it. The `verify_estimator` helper is the same drop-in tool from the
companion project ([validate-ai-econometric-code](../validate-ai-econometric-code/)); here it is pointed
at DML.

## What it demonstrates

Against a planted true effect of **1.0** in a partially linear model whose treatment is confounded
through a 20-dimensional set of controls:

1. **The catch (regularization/overfitting bias).** On the reference seed, the naive ML plug-in recovers
   **0.554** (bias -0.446) while cross-fitted DML recovers **0.968**, 95% CI [0.904, 1.032]. The naive
   attenuation is systematic across many draws, not a single-draw fluke. It comes from fitting `g(X)`
   in-sample and never orthogonalizing `D`, so the regularized fit absorbs treatment-linked variation in
   `X`.
2. **The limit — close, not exact.** Across 50 draws, DML recovers about 0.97 rather than 1.0. This
   package establishes that the mean is within the pre-specified 0.10 tolerance. It does not identify
   the remaining difference as finite-sample noise or demonstrate that the difference shrinks with
   sample size; those claims would require a sample-size and coverage study.
3. **The limit that matters — only a planted omission can be caught.** On the included negative-control
   DGP, a hidden confounder `U` moves both `D` and `Y` but is left out of the controls, so DML is biased
   and the runner requires this case to **FAIL**. The check catches the omission only because the DGP
   explicitly generates it. A validation DGP that never generates the missing `U` cannot establish that
   a real control set is complete. DML removes regularization bias from the nuisances; it does not
   manufacture the identifying assumption that `X` is complete.

## How to Run

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cd code
python verify_double_ml.py
```

The run prints the single reference draw, the many-draw planted-truth check (with PASS/FAIL against the
planted effect), and the omitted-confounder limit. The expected release-gate pattern is naive **FAIL**,
cross-fitted DML **PASS**, and omitted-confounder **FAIL**; the runner exits nonzero if any status flips.
All numbers are reproducible from fixed seeds; no data download is required.

## Files

| File | What it is |
|------|------------|
| `code/verify_estimator.py` | The generic drop-in `verify_estimator(estimator, simulate_dgp, true_effect, tol)` helper (shared with the companion project). |
| `code/dml_plm.py` | The estimators under test: the naive ML plug-in and cross-fitted DML for the partially linear model, plus the two data-generating processes. |
| `code/verify_double_ml.py` | The proof: applies the helper to the naive-vs-DML case (the catch), and to the omitted-confounder case (the limit). |

## References

- Chernozhukov, V., Chetverikov, D., Demirer, M., Duflo, E., Hansen, C., Newey, W., & Robins, J. (2018).
  Double/debiased machine learning for treatment and structural parameters. *The Econometrics Journal*,
  21(1), C1–C68. https://doi.org/10.1111/ectj.12097
- Robinson, P. M. (1988). Root-N-consistent semiparametric regression. *Econometrica*, 56(4), 931–954.
  https://doi.org/10.2307/1912705
