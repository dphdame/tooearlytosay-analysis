"""
The estimator under test: double/debiased machine learning (DML) for the
partially linear model, and the naive plug-in it is meant to replace.

Partially linear model:  Y = theta * D + g(X) + e,   D = m(X) + v
theta is the causal parameter we want. g(X) and m(X) are high-dimensional
nuisance functions we do NOT care about but must control for. We let a
machine-learning model (gradient boosting) estimate those nuisances.

- naive_plugin: regress Y on an in-sample ML prediction of g(X), then OLS of
  the residual on D. No cross-fitting, no orthogonalization of D. Biased by
  regularization and overfitting: the ML fit of g(X) absorbs treatment-linked
  variation in X, so subtracting it also subtracts part of the treatment
  signal and attenuates theta toward zero.

- dml_plm: residualize BOTH Y and D on X with out-of-fold ML predictions
  (cross-fitting), then regress the Y residual on the D residual. This is the
  Neyman-orthogonal, cross-fitted moment of Chernozhukov et al. (2018); the
  orthogonalization of D is what the naive plug-in omits.

Both take an explicit rng so the same DGP can be replayed across many draws by
verify_estimator.

Deps: numpy, scikit-learn.
"""
import numpy as np
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import KFold


def simulate(true_effect, rng, n=2000, p=20):
    """Confounded treatment: X drives both D and Y through nonlinear g, m.
    X contains every confounder by construction, so a correct estimator can
    recover the planted true_effect."""
    X = rng.normal(size=(n, p))
    g = np.sin(X[:, 0]) + 0.5 * X[:, 1] ** 2 + X[:, 2] * X[:, 3]   # nuisance in outcome
    m = 0.8 * np.cos(X[:, 0]) + 0.4 * X[:, 1]                       # propensity/treatment
    D = m + rng.normal(scale=1.0, size=n)
    Y = true_effect * D + g + rng.normal(scale=1.0, size=n)
    return dict(Y=Y, D=D, X=X)


def simulate_omitted_confounder(true_effect, rng, n=2000, p=20):
    """Same model, plus a hidden confounder U that moves BOTH D and Y and is
    NOT included in the controls X the estimator sees. Identification fails:
    even the correct DML estimator is biased for true_effect here."""
    X = rng.normal(size=(n, p))
    U = rng.normal(size=n)                                          # unobserved confounder
    g = np.sin(X[:, 0]) + 0.5 * X[:, 1] ** 2 + X[:, 2] * X[:, 3]
    m = 0.8 * np.cos(X[:, 0]) + 0.4 * X[:, 1]
    D = m + 1.0 * U + rng.normal(scale=1.0, size=n)                 # U raises D
    Y = true_effect * D + g + 1.0 * U + rng.normal(scale=1.0, size=n)  # U raises Y
    return dict(Y=Y, D=D, X=X)                                      # U is never returned


def naive_plugin(data):
    """Regress Y on ML-predicted g(X), then OLS of residualized Y on D.
    No cross-fitting, no orthogonalization of D: biased by construction."""
    Y, D, X = data["Y"], data["D"], data["X"]
    ghat = GradientBoostingRegressor(random_state=0).fit(X, Y).predict(X)
    Yres = Y - ghat
    return float(np.dot(D, Yres) / np.dot(D, D))


def dml_plm(data, n_folds=5):
    """Double ML for the partially linear model with 5-fold cross-fitting.
    Orthogonal moment: residualize BOTH Y and D on X with out-of-fold ML
    predictions, then regress Y-resid on D-resid. Returns theta only."""
    Y, D, X = data["Y"], data["D"], data["X"]
    n = len(Y)
    Yres = np.zeros(n)
    Dres = np.zeros(n)
    for tr, te in KFold(n_folds, shuffle=True, random_state=1).split(X):
        ell = GradientBoostingRegressor(random_state=0).fit(X[tr], Y[tr])   # E[Y|X]
        mhat = GradientBoostingRegressor(random_state=0).fit(X[tr], D[tr])  # E[D|X]
        Yres[te] = Y[te] - ell.predict(X[te])
        Dres[te] = D[te] - mhat.predict(X[te])
    return float(np.dot(Dres, Yres) / np.dot(Dres, Dres))


def dml_plm_se(data, n_folds=5):
    """dml_plm plus the Neyman-orthogonal standard error, for a single draw."""
    Y, D, X = data["Y"], data["D"], data["X"]
    n = len(Y)
    Yres = np.zeros(n)
    Dres = np.zeros(n)
    for tr, te in KFold(n_folds, shuffle=True, random_state=1).split(X):
        ell = GradientBoostingRegressor(random_state=0).fit(X[tr], Y[tr])
        mhat = GradientBoostingRegressor(random_state=0).fit(X[tr], D[tr])
        Yres[te] = Y[te] - ell.predict(X[te])
        Dres[te] = D[te] - mhat.predict(X[te])
    theta = float(np.dot(Dres, Yres) / np.dot(Dres, Dres))
    psi = (Yres - theta * Dres) * Dres
    J = np.mean(Dres ** 2)
    se = float(np.sqrt(np.mean(psi ** 2) / J ** 2 / n))
    return theta, se
