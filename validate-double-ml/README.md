# Validate Double Machine Learning

Replication materials for ["Plant a known effect before trusting a double machine learning estimate"](https://tooearlytosay.com/research/methodology/validate-double-ml/)

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
2. **The limit — close, not exact.** DML recovers ~0.97, not 1.0. The residual is finite-sample noise
   that shrinks with sample size; the confidence interval covers the truth. Passing means close and
   consistent on this process, not exact on one draw.
3. **The limit that matters — an omitted confounder passes unseen.** On a DGP with a hidden confounder
   `U` that moves both `D` and `Y` and is left out of the controls, DML is biased for the true effect.
   Yet a planted-truth check built on the **same** (incomplete) control set never generates the
   confounding, so it reports clean recovery and the omission passes unseen. DML removes regularization
   bias from the nuisances; it does not manufacture the identifying assumption that `X` is complete.

## How to Run

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cd code
python verify_double_ml.py
```

The run prints the single reference draw, the many-draw planted-truth check (with PASS/FAIL against the
planted effect), and the omitted-confounder limit. All numbers are reproducible from fixed seeds; no data
download is required.

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
