#!/usr/bin/env python3
"""
did_planted_truth.py — planted-truth harness for the Too Early To Say article
"Difference-in-differences in Python".

We plant KNOWN cohort-time treatment effects in a staggered-adoption panel and test which
estimator recovers the true average. The point (priority-centered): with staggered timing and
effects that grow with exposure, the two-way fixed-effects (TWFE) coefficient is NOT the average
treatment effect — it is a weighted average that puts NEGATIVE weights on some comparisons
(Goodman-Bacon 2021; de Chaisemartin & D'Haultfoeuille 2020), because already-treated units act as
controls for later-treated ones. A group-time estimator that only ever uses not-yet-treated units as
controls (Callaway & Sant'Anna 2021) recovers the planted average.

DGP (staggered adoption, cohort-heterogeneous DYNAMIC effects):
  - N units in 3 cohorts: treated in period 4, treated in period 7, and never-treated.
  - Unit and period fixed effects + noise.
  - Treatment effect turns on at adoption and GROWS with exposure (dynamic), and DIFFERS by cohort.
    Early adopters get a larger per-period effect than late adopters. The true simple average of the
    post-treatment effects across all treated unit-periods is the target (ATT_true).

Estimators:
  - NAIVE (wrong): static TWFE — regress Y on unit FE, period FE, and a single post-treatment dummy.
    Its coefficient is contaminated by forbidden comparisons (already-treated used as controls).
  - CORRECT: a group-time estimator (CS-style). For each cohort g and period t>=g, estimate the
    ATT(g,t) as the change in Y for cohort g from its last pre-period (g-1) to t, MINUS the same
    change for the not-yet-treated units, then average the ATT(g,t) over treated unit-periods.

Blind spots of THIS harness (quote in the article's Limits):
  - It CANNOT verify "no anticipation": the planted effect is zero before adoption BY CONSTRUCTION, so
    the pre-trend test passes; a real anticipatory response would bias BOTH the pre-test and the
    estimator, and nothing in-sample distinguishes it. The clean-controls fix removes the negative-
    weight contamination, NOT an anticipation or parallel-trends violation.
"""
import json
import numpy as np
import statsmodels.api as sm

SEED = 20260705
T = 10                      # periods 0..9
N_PER = 60                  # units per cohort
COHORTS = {4: 0.6, 7: 0.3}  # adoption period -> per-period-per-exposure effect slope (early > late)
DRAWS = 200


def simulate(rng, cohorts=None, dynamic=True):
    cohorts = COHORTS if cohorts is None else cohorts
    cohort_ids = list(cohorts) + [None]              # None = never-treated
    rows = []
    uid = 0
    unit_fe_scale, period_fe = 1.0, rng.normal(0, 0.5, T)
    truth_num, truth_den = 0.0, 0                    # to accumulate the true ATT (simple average)
    for g in cohort_ids:
        for _ in range(N_PER):
            ufe = rng.normal(0, unit_fe_scale)
            for t in range(T):
                eff = 0.0
                if g is not None and t >= g:
                    exposure = (t - g + 1) if dynamic else 1   # dynamic grows; static is flat
                    eff = cohorts[g] * exposure                 # cohort-heterogeneous
                    truth_num += eff; truth_den += 1
                y = ufe + period_fe[t] + eff + rng.normal(0, 0.5)
                rows.append((uid, t, g if g is not None else -1, y, eff))
            uid += 1
    arr = np.array(rows, dtype=float)                 # cols: uid, t, cohort, y, true_eff
    att_true = truth_num / truth_den
    return arr, att_true


def twfe_static(arr):
    """Naive: Y ~ unit FE + period FE + a single post-treatment dummy (the forbidden-comparison bias)."""
    uid, t, cohort, y = arr[:, 0], arr[:, 1], arr[:, 2], arr[:, 3]
    post = ((cohort >= 0) & (t >= cohort)).astype(float)
    U = sm.categorical_dummies(uid) if hasattr(sm, "categorical_dummies") else _dummies(uid)
    Tt = _dummies(t)
    X = np.column_stack([post, U[:, 1:], Tt[:, 1:], np.ones(len(y))])
    beta = np.linalg.lstsq(X, y, rcond=None)[0]
    return float(beta[0])


def _dummies(col):
    vals = np.unique(col)
    return np.column_stack([(col == v).astype(float) for v in vals])


def cs_group_time(arr):
    """Correct: CS-style. ATT(g,t) = [Y_g(t) - Y_g(g-1)] - [Y_nyt(t) - Y_nyt(g-1)], using only
    NOT-YET-TREATED units as controls; average over treated unit-periods (weight by cell size)."""
    t, cohort, y = arr[:, 1], arr[:, 2], arr[:, 3]
    def cell_mean(mask):
        return y[mask].mean() if mask.any() else np.nan
    num, den = 0.0, 0
    for g in [c for c in np.unique(cohort) if c >= 0]:
        base = int(g) - 1
        for tt in range(int(g), T):
            treated_now = (cohort == g)
            # controls: not-yet-treated at period tt (never-treated, or adopt strictly after tt)
            control = (cohort == -1) | (cohort > tt)
            dg = cell_mean(treated_now & (t == tt)) - cell_mean(treated_now & (t == base))
            dc = cell_mean(control & (t == tt)) - cell_mean(control & (t == base))
            if np.isnan(dg) or np.isnan(dc):
                continue
            n_cell = int((treated_now & (t == tt)).sum())
            num += (dg - dc) * n_cell; den += n_cell
    return num / den


def main():
    rng = np.random.default_rng(SEED)
    arr, att_true = simulate(rng)
    twfe_single = twfe_static(arr)
    cs_single = cs_group_time(arr)

    # ESTIMAND is a CHOICE: the same design supports more than one valid average. The unit-period
    # weighted average (att_true, 1.60) weights cohorts by how many treated periods they contribute;
    # an equally-defensible equal-weight-by-cohort average (1.35) treats each cohort's ATT the same.
    # The 19% gap is not error — it is the estimand the analyst must NAME (econometric-analyst, 2026-07-05).
    t_, cohort_, eff_ = arr[:, 1], arr[:, 2], arr[:, 4]
    cohort_atts = {}
    for g in [c for c in np.unique(cohort_) if c >= 0]:
        m = (cohort_ == g) & (t_ >= g)
        cohort_atts[str(int(g))] = float(eff_[m].mean())
    att_equal_weight_cohorts = float(np.mean(list(cohort_atts.values())))

    # many-draw means (systematic, not one seed)
    rng2 = np.random.default_rng(SEED + 1)
    twfe_list, cs_list, truth_list = [], [], []
    for _ in range(DRAWS):
        a, tr = simulate(rng2)
        twfe_list.append(twfe_static(a)); cs_list.append(cs_group_time(a)); truth_list.append(tr)

    # Goodman-Bacon-style: how far the naive falls below truth (the negative-weight pull)
    twfe_mean = float(np.mean(twfe_list)); cs_mean = float(np.mean(cs_list)); truth_mean = float(np.mean(truth_list))

    # NO-STRAWMAN SWEEP: the bias is not a coding mistake and cannot be read off the TWFE output.
    # It appears once effects are dynamic or heterogeneous, and its MAGNITUDE shifts with the pattern
    # the analyst cannot see (all scenarios shown here bias downward; a sign flip needs stronger late
    # heterogeneity than any shown). Four scenarios, same TWFE regression each time.
    def scen(cohorts, dynamic):
        rng3 = np.random.default_rng(SEED + 5)
        tw, tr = [], []
        for _ in range(80):
            a, t = simulate(rng3, cohorts=cohorts, dynamic=dynamic)
            tw.append(twfe_static(a)); tr.append(t)
        return round(float(np.mean(tw)), 3), round(float(np.mean(tr)), 3)
    homog_tw, homog_tr = scen({4: 0.5, 7: 0.5}, dynamic=False)   # identical STATIC effect -> TWFE ok
    homdyn_tw, homdyn_tr = scen({4: 0.5, 7: 0.5}, dynamic=True)  # identical but DYNAMIC -> still biased
    early_tw, early_tr = scen({4: 0.6, 7: 0.3}, dynamic=True)    # early adopters bigger -> biased down
    late_tw, late_tr = scen({4: 0.3, 7: 0.6}, dynamic=True)     # late adopters bigger -> biased differently
    sweep = {
        "homogeneous_static": {"twfe": homog_tw, "truth": homog_tr},
        "homogeneous_dynamic": {"twfe": homdyn_tw, "truth": homdyn_tr},
        "heterogeneous_early_larger": {"twfe": early_tw, "truth": early_tr},
        "heterogeneous_late_larger": {"twfe": late_tw, "truth": late_tr},
    }

    results = {
        "source": "did_planted_truth.py — staggered adoption, cohort-heterogeneous dynamic effects, seed 20260705",
        "att_true_single": round(att_true, 3),
        "att_true_mean": round(truth_mean, 3),
        "att_equal_weight_cohorts": round(att_equal_weight_cohorts, 3),
        "cohort_atts": {k: round(v, 3) for k, v in cohort_atts.items()},
        "twfe_static_single": round(twfe_single, 3),
        "twfe_static_mean": round(twfe_mean, 3),
        "cs_group_time_single": round(cs_single, 3),
        "cs_group_time_mean": round(cs_mean, 3),
        "twfe_bias_mean": round(twfe_mean - truth_mean, 3),
        "cs_bias_mean": round(cs_mean - truth_mean, 3),
        "no_strawman_sweep": sweep,
        "cohorts": {"early_adopt_period": 4, "late_adopt_period": 7, "never_treated": True},
        "draws": DRAWS,
    }
    print(json.dumps(results, indent=2))
    with open("../data/results.json", "w") as fh:
        json.dump(results, fh, indent=2)
    print("\nwrote ../data/results.json")


if __name__ == "__main__":
    main()
