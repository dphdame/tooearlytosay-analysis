"""
Rolling difference-in-differences: a transparent Python prototype.

Reimplements the LOGIC of the Lee-Wooldridge rolling DiD estimator (the
`lwdid` Stata command, Hur, Lee & Wooldridge 2026) outside Stata, so the
method can be interrogated rather than trusted.

The rolling idea, in one line: use ONLY a unit's pre-treatment periods to
strip out its level, trend, or seasonal pattern, then estimate the treatment
effect by a cross-sectional regression on the transformed outcomes.

This prototype implements:
  (1) three unit-level transformations -- demean, detrend, detrend+seasonal
  (2) the small-N common-timing estimator: collapse transformed post-period
      outcomes to one number per unit, regress on a treated dummy
  (3) three inference modes -- exact t (normal), HC3-robust, randomization
  (4) the staggered ATT(g,t) -> event-time aggregation, including the
      pre-treatment placebo cells the method gives you for free
  (5) an EASY case (all transforms agree) and a HARD case (heterogeneous
      trends + seasonality + few units), to show where the method is stable
      and where it is fragile.

Not a package. A prototype whose every step is visible. Reproducible: seed set.
"""

import numpy as np
import pandas as pd
import statsmodels.api as sm

RNG = np.random.default_rng(20260613)
Q = 4  # quarterly data


# ---------------------------------------------------------------------------
# Data generating process
# ---------------------------------------------------------------------------
def make_panel(n_treated, n_control, treat_period, n_periods,
               true_att, hetero_trend, seasonal, common_timing=True,
               cohorts=None, noise=0.4):
    """Build a balanced panel. y = unit FE + unit trend + season + common
    shock + ATT*post-treat + noise. Returns long-format DataFrame."""
    rows = []
    n_units = n_treated + n_control
    # common (aggregate) time shocks: a real time effect the controls absorb
    common_shock = np.cumsum(RNG.normal(0, 0.15, n_periods))
    season_pattern = np.array([0.0, 0.9, -0.3, -0.6])  # quarter-of-year effect

    if common_timing:
        gvar = [treat_period] * n_treated + [0] * n_control
    else:
        gvar = list(cohorts) + [0] * n_control

    for i in range(n_units):
        alpha = RNG.normal(5, 1.0)                       # unit level
        # treated units trend a bit differently from controls when hetero_trend
        if hetero_trend:
            slope = RNG.normal(0.18 if i < n_treated else 0.05, 0.03)
        else:
            slope = RNG.normal(0.05, 0.01)
        g = gvar[i]
        for t in range(1, n_periods + 1):
            season = season_pattern[(t - 1) % Q] if seasonal else 0.0
            treated_now = (g != 0) and (t >= g)
            y = (alpha + slope * t + season + common_shock[t - 1]
                 + (true_att if treated_now else 0.0)
                 + RNG.normal(0, noise))
            rows.append(dict(unit=i, t=t, q=((t - 1) % Q) + 1,
                             g=g, treated_unit=int(g != 0), y=y))
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# The rolling transformation: fit on pre-window ONLY, residualize all periods
# ---------------------------------------------------------------------------
def transform_unit(df_u, pre_mask, kind):
    """Return transformed outcome for one unit. The regression that defines
    the counterfactual is fit using only pre-treatment rows (pre_mask)."""
    y = df_u["y"].to_numpy()
    t = df_u["t"].to_numpy()
    q = df_u["q"].to_numpy()
    pre = pre_mask.to_numpy()
    if pre.sum() < 2 and kind != "demean":
        return np.full_like(y, np.nan, dtype=float)

    if kind == "demean":
        fit = y[pre].mean()
        return y - fit
    # design matrix: const + time (+ quarter dummies)
    cols = [np.ones_like(t, dtype=float), t.astype(float)]
    if kind == "detrendq":
        for qq in (2, 3, 4):
            cols.append((q == qq).astype(float))
    X = np.column_stack(cols)
    beta, *_ = np.linalg.lstsq(X[pre], y[pre], rcond=None)
    yhat = X @ beta
    return y - yhat


def rolling_transform(df, kind, ref_period):
    """Transform every unit using pre-`ref_period` rows as the pre-window."""
    out = []
    for _, du in df.groupby("unit"):
        du = du.sort_values("t")
        pre_mask = du["t"] < ref_period
        du = du.assign(yt=transform_unit(du, pre_mask, kind))
        out.append(du)
    return pd.concat(out)


# ---------------------------------------------------------------------------
# Small-N common-timing estimator + three inference modes
# ---------------------------------------------------------------------------
def smalln_common(df, treat_period, kind, ri_reps=2000):
    """Collapse transformed post-treatment outcomes within unit, regress on
    treated dummy. Return ATT plus exact-t, HC3, and randomization p-values."""
    dft = rolling_transform(df, kind, ref_period=treat_period)
    post = dft[dft["t"] >= treat_period]
    coll = (post.groupby(["unit", "treated_unit"])["yt"]
            .mean().reset_index().dropna())
    y = coll["yt"].to_numpy()
    d = coll["treated_unit"].to_numpy().astype(float)
    X = sm.add_constant(d)

    ols = sm.OLS(y, X).fit()                 # classical -> exact t under normality
    hc3 = sm.OLS(y, X).fit(cov_type="HC3")
    att = ols.params[1]

    # randomization inference: permute treatment labels, recompute slope
    n1 = int(d.sum())
    n = len(d)
    perm = np.empty(ri_reps)
    base_idx = np.arange(n)
    for b in range(ri_reps):
        lab = np.zeros(n)
        lab[RNG.choice(base_idx, n1, replace=False)] = 1.0
        Xb = sm.add_constant(lab)
        perm[b] = sm.OLS(y, Xb).fit().params[1]
    p_ri = (1 + np.sum(np.abs(perm) >= np.abs(att))) / (ri_reps + 1)

    return dict(kind=kind, n_treated=n1, n_control=n - n1, att=att,
                p_exact_t=ols.pvalues[1], p_hc3=hc3.pvalues[1], p_ri=p_ri,
                se_t=ols.bse[1])


# ---------------------------------------------------------------------------
# Staggered ATT(g,t) -> event-time WATT(r), incl. pre-period placebo cells
# ---------------------------------------------------------------------------
def staggered_event_study(df, kind, n_periods):
    cohorts = sorted(c for c in df["g"].unique() if c != 0)
    recs = []
    for g in cohorts:
        dft = rolling_transform(df, kind, ref_period=g)
        for t in range(2, n_periods + 1):
            # comparison sample A_{g,t}: cohort-g units + not-yet/never treated
            elig = df.groupby("unit")["g"].first()
            keep = elig[(elig == g) | (elig == 0) | (elig > max(g, t))].index
            cell = dft[(dft["t"] == t) & (dft["unit"].isin(keep))].dropna(subset=["yt"])
            treat = (cell["g"] == g).astype(float)
            if treat.sum() == 0 or (1 - treat).sum() == 0:
                continue
            X = sm.add_constant(treat.to_numpy())
            att = sm.OLS(cell["yt"].to_numpy(), X).fit().params[1]
            recs.append(dict(g=g, t=t, r=t - g, att=att))
    cell_df = pd.DataFrame(recs)
    # WATT(r): cohort-size-weighted mean of ATT(g,t) across cohorts at event
    # time r (paper Table 1 Step 4). Weights are N_g, the number of treated
    # units in cohort g. (All cohorts are size 2 here, so this equals the
    # simple mean; weighting is kept so the code is correct on unbalanced panels.)
    n_g = df[df["g"] != 0].groupby("g")["unit"].nunique()
    cell_df["w"] = cell_df["g"].map(n_g)
    cell_df["wa"] = cell_df["att"] * cell_df["w"]
    g = cell_df.groupby("r")
    watt = (g["wa"].sum() / g["w"].sum()).reset_index(name="att")
    return watt


# ---------------------------------------------------------------------------
# Run it
# ---------------------------------------------------------------------------
def banner(s):
    print("\n" + "=" * 70 + "\n" + s + "\n" + "=" * 70)


if __name__ == "__main__":
    TRUE_ATT = 1.0

    banner("EASY CASE: 6 treated + 6 control, homogeneous trends, no season")
    easy = make_panel(n_treated=6, n_control=6, treat_period=9, n_periods=16,
                      true_att=TRUE_ATT, hetero_trend=False, seasonal=False,
                      noise=0.15)
    rows = [smalln_common(easy, 9, k) for k in ("demean", "detrend", "detrendq")]
    easy_tab = pd.DataFrame(rows)
    print(easy_tab.to_string(index=False,
          float_format=lambda x: f"{x:8.3f}"))

    banner("HARD CASE: 3 treated + 3 control, heterogeneous trends + seasonality")
    hard = make_panel(n_treated=3, n_control=3, treat_period=9, n_periods=16,
                      true_att=TRUE_ATT, hetero_trend=True, seasonal=True)
    rows = [smalln_common(hard, 9, k) for k in ("demean", "detrend", "detrendq")]
    hard_tab = pd.DataFrame(rows)
    print(hard_tab.to_string(index=False,
          float_format=lambda x: f"{x:8.3f}"))

    banner("STAGGERED EVENT STUDY: 3 cohorts (g=6,9,12), hetero trends")
    cohorts = [6, 6, 9, 9, 12, 12]   # 6 treated units in 3 cohorts
    stag = make_panel(n_treated=6, n_control=6, treat_period=None, n_periods=16,
                      true_att=TRUE_ATT, hetero_trend=True, seasonal=False,
                      common_timing=False, cohorts=cohorts)
    for k in ("demean", "detrend"):
        watt = staggered_event_study(stag, k, 16)
        print(f"\n-- transform = {k} -- (pre-period r<0 cells are placebos)")
        print(watt.to_string(index=False,
              float_format=lambda x: f"{x:8.3f}"))

    # save backing data
    easy_tab.to_csv("results_easy.csv", index=False)
    hard_tab.to_csv("results_hard.csv", index=False)
    print("\nTRUE ATT = ", TRUE_ATT, " (target for every estimate above)")
    print("Saved results_easy.csv, results_hard.csv")
