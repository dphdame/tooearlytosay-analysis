#!/usr/bin/env python3
"""
matching_planted_truth.py — planted-truth harness for the matching / unconfoundedness article.

The show-don't-tell spine:
  - Plant a KNOWN constant treatment effect (TAU = 2.0) with selection ON OBSERVABLES, and build a
    covariate region (the high-X1 tail) where treated units have almost no comparable controls
    (thin common support).
  - NAIVE-WRONG: nearest-neighbor propensity-score matching, reported with a covariate-balance
    (standardized mean difference) table that looks CLEAN (max |SMD| well under the 0.10 rule after
    matching) — yet the matched ATT is biased about 10% high, because treated units in the thin tail
    are matched to distant controls and the nonlinear outcome surface turns that mismatch into
    outcome bias. Balance is achieved; identification is not.
  - THE CHECK: a common-support / overlap diagnostic (propensity overlap; the count of treated units
    whose propensity exceeds the maximum control propensity). Restricting to the region of common
    support recovers TAU.
  - CORRECT ESTIMATOR: Crump, Hotz, Imbens & Mitnik (2009) trimming — discard units with estimated
    propensity outside [0.1, 0.9], then match on the trimmed sample. A fixed, citable rule, not a
    tuned knob. Recovers ~2.0 and is stable across the trimming band.
  - NO-STRAWMAN: across 200 draws the balance table stays clean (max |SMD| < 0.1) while the matched
    ATT stays biased — a balanced table does not certify the estimate. And the "obvious" fix a reader
    proposes (a propensity CALIPER) does not de-bias: near propensity 1 the off-support treated sit a
    tiny propensity-distance from the densest controls, so a caliper keeps the bad matches.
  - HARD LIMIT (structurally uncatchable): add an UNOBSERVED confounder U that moves both treatment
    and outcome. With overlap restored (Crump) and every OBSERVED SMD balanced, the estimate is still
    badly biased, and nothing computable from the observed data flags it. That is the unconfoundedness
    (conditional-independence) assumption — matching cannot test it.

DGP:
  X1, X2 correlated standard normals (corr ~0.4).
  Propensity (observed-confounding world): logit p = 2.4*X1 + 0.8*X2 - 0.5  (strong X1 dependence
    => the high-X1 tail is almost all treated => thin overlap there).
  D ~ Bernoulli(p).
  Outcome: Y = TAU*D + 1.0*X1 + 0.7*X2 + 1.3*X1^2 + noise   (nonlinear in X1).
  HARD-limit world additionally: logit p += 1.1*U ; Y += 1.3*U  (U unobserved).

Constant effect => ATT = ATE = TAU = 2.0 exactly on any subpopulation, so trimming to common support
does not change the TRUE target; it only removes the bad-match bias. Everything is frozen to
data/results.json with a fixed seed.
"""
import json
from pathlib import Path

import numpy as np
import statsmodels.api as sm

SEED = 20260705
N = 4000
TAU = 2.0
DRAWS = 200
A_SEL = 2.4
B_NL = 1.3
RESULTS_PATH = Path(__file__).resolve().parent.parent / "data" / "results.json"


def simulate(rng, n=N, unobserved=False):
    x1 = rng.normal(0, 1, n)
    x2 = 0.4 * x1 + np.sqrt(1 - 0.16) * rng.normal(0, 1, n)
    u = rng.normal(0, 1, n)
    logit = A_SEL * x1 + 0.8 * x2 - 0.5
    if unobserved:
        logit = logit + 1.1 * u
    p = 1.0 / (1.0 + np.exp(-logit))
    d = (rng.uniform(size=n) < p).astype(float)
    y = TAU * d + 1.0 * x1 + 0.7 * x2 + B_NL * x1 ** 2 + rng.normal(0, 1, n)
    if unobserved:
        y = y + 1.3 * u
    X = np.column_stack([x1, x2])
    return X, d, y


def est_propensity(X, d):
    """Logit propensity on the OBSERVED covariates (the analyst never sees U)."""
    Xc = sm.add_constant(X)
    return sm.Logit(d, Xc).fit(disp=0, maxiter=200).predict(Xc)


def _smd(a, b):
    sd = np.sqrt((a.var(ddof=1) + b.var(ddof=1)) / 2.0)
    return abs((a.mean() - b.mean()) / sd) if sd > 0 else 0.0


def nn_match_att(ps, d, y, mask=None):
    """Nearest-neighbor ATT on the propensity score, with replacement. mask optionally restricts which
    treated units are included (used for common-support trimming). Returns (att, n_treated_used)."""
    d = d.astype(bool)
    t_idx = np.where(d)[0]
    if mask is not None:
        t_idx = t_idx[mask[t_idx]]
    c_idx = np.where(~d)[0]
    ps_c = ps[c_idx]
    matched = [c_idx[np.argmin(np.abs(ps_c - ps[i]))] for i in t_idx]
    return float(np.mean(y[t_idx] - y[matched])), len(t_idx)


def smd_after_match(X, ps, d, mask=None, per_cov=False):
    """|SMD| between treated and their nearest-neighbor matched controls. Returns the max across
    covariates, or the per-covariate list if per_cov=True."""
    d = d.astype(bool)
    t_idx = np.where(d)[0]
    if mask is not None:
        t_idx = t_idx[mask[t_idx]]
    c_idx = np.where(~d)[0]
    ps_c = ps[c_idx]
    matched = [c_idx[np.argmin(np.abs(ps_c - ps[i]))] for i in t_idx]
    per = [_smd(X[t_idx, k], X[matched, k]) for k in range(X.shape[1])]
    return per if per_cov else max(per)


def smd_before(X, d):
    d = d.astype(bool)
    return [_smd(X[d, k], X[~d, k]) for k in range(X.shape[1])]


def caliper_match_att(ps, d, y, caliper):
    """NN matching but DROP any treated unit whose nearest control is farther than `caliper` in
    propensity. The 'obvious fix' that silently drops units without de-biasing."""
    d = d.astype(bool)
    t_idx = np.where(d)[0]
    c_idx = np.where(~d)[0]
    ps_c = ps[c_idx]
    diffs, used = [], 0
    for i in t_idx:
        k = np.argmin(np.abs(ps_c - ps[i]))
        if abs(ps_c[k] - ps[i]) <= caliper:
            diffs.append(y[i] - y[c_idx[k]])
            used += 1
    att = float(np.mean(diffs)) if diffs else float("nan")
    return att, used, len(t_idx)


def logit_caliper_match_att(ps, d, y, width_sd):
    """Austin (2011) caliper: match on the LOGIT of the propensity, dropping a treated unit whose
    nearest control is farther than width_sd * SD(logit(PS)). Unlike a raw-PS caliper, the logit scale
    does NOT compress near PS=1, so this DOES drop the off-support tail and de-bias."""
    d = d.astype(bool)
    L = np.log(ps / (1 - ps))
    cal = width_sd * L.std(ddof=1)
    t_idx = np.where(d)[0]
    c_idx = np.where(~d)[0]
    L_c = L[c_idx]
    diffs, used = [], 0
    for i in t_idx:
        k = np.argmin(np.abs(L_c - L[i]))
        if abs(L_c[k] - L[i]) <= cal:
            diffs.append(y[i] - y[c_idx[k]])
            used += 1
    att = float(np.mean(diffs)) if diffs else float("nan")
    return att, used, len(t_idx)


def overlap_stats(ps, d):
    """How many treated units sit ABOVE the maximum control propensity (no comparable control)?"""
    d = d.astype(bool)
    ps_t, ps_c = ps[d], ps[~d]
    off = int(np.sum(ps_t > ps_c.max()))
    return {
        "max_control_ps": float(ps_c.max()),
        "n_treated": int(d.sum()),
        "treated_off_support": off,
        "pct_treated_off_support": float(100.0 * off / d.sum()),
    }


def crump_mask(ps, lo=0.1):
    """Crump et al. (2009) trimming: keep units with lo <= PS <= 1-lo (both arms)."""
    return (ps >= lo) & (ps <= 1 - lo)


def one_draw(seed, unobserved=False):
    rng = np.random.default_rng(seed)
    X, d, y = simulate(rng, unobserved=unobserved)
    ps = est_propensity(X, d)
    naive = float(y[d == 1].mean() - y[d == 0].mean())
    att_full, _ = nn_match_att(ps, d, y)
    smd_a = smd_after_match(X, ps, d)
    ov = overlap_stats(ps, d)
    cm = crump_mask(ps, 0.1)
    att_cr, n_cr = nn_match_att(ps, d, y, mask=cm)
    smd_cr = smd_after_match(X, ps, d, mask=cm)
    return {"naive": naive, "att_full": att_full, "smd_after": smd_a, "overlap": ov,
            "att_crump": att_cr, "n_crump": n_cr, "smd_crump": smd_cr,
            "pct_treated_kept_crump": 100.0 * int(np.sum(cm[d.astype(bool)])) / int(d.sum())}


def main():
    ref = one_draw(SEED, unobserved=False)

    # many-draw means (no-strawman: the ATT bias is systematic, not sampling noise)
    acc = {k: [] for k in ["naive", "att_full", "smd_after", "att_crump"]}
    off_pct = []
    for s in range(DRAWS):
        r = one_draw(SEED + 1 + s, unobserved=False)
        for k in acc:
            acc[k].append(r[k])
        off_pct.append(r["overlap"]["pct_treated_off_support"])
    means = {k: float(np.mean(v)) for k, v in acc.items()}
    # honesty: how often does the matched balance table actually pass the 0.10 rule?
    smd_arr = np.array(acc["smd_after"])
    smd_median = float(np.median(smd_arr))
    smd_pass_rate = float(100.0 * np.mean(smd_arr <= 0.10))
    # honesty: the matched bias is large in expectation but NOT "every time" — report the spread
    af = np.array(acc["att_full"])
    af_sd = float(af.std(ddof=1))
    af_min = float(af.min())
    af_pct_above_true = float(100.0 * np.mean(af > TAU))

    # correct-estimator stability: Crump trimming band
    rng = np.random.default_rng(SEED)
    X, d, y = simulate(rng, unobserved=False)
    ps = est_propensity(X, d)
    dbool = d.astype(bool)
    crump_walk = {}
    for lo in [0.05, 0.10, 0.15]:
        m = crump_mask(ps, lo)
        att, n = nn_match_att(ps, d, y, mask=m)
        crump_walk[f"{lo:.2f}"] = {"att": round(att, 3), "band": f"[{lo:.2f},{1 - lo:.2f}]",
                                    "treated_kept_pct": round(100.0 * int(np.sum(m[dbool])) / int(dbool.sum()), 1)}

    # scale subtlety: a RAW-propensity caliper keeps the off-support bad matches (PS compresses near 1)
    caliper_walk = {}
    for c in [0.20, 0.10, 0.05, 0.01]:
        att, used, total = caliper_match_att(ps, d, y, caliper=c)
        caliper_walk[f"{c:.2f}"] = {"att": round(att, 3), "pct_dropped": round(100 * (total - used) / total, 1)}
    # ...but the field-standard LOGIT-propensity caliper (Austin 2011) DOES de-bias, like Crump trimming
    logit_caliper_walk = {}
    for w in [0.20, 0.10, 0.05]:
        att, used, total = logit_caliper_match_att(ps, d, y, width_sd=w)
        logit_caliper_walk[f"{w:.2f}"] = {"att": round(att, 3), "pct_dropped": round(100 * (total - used) / total, 1)}

    # HARD limit: unobserved confounder
    hard = one_draw(SEED, unobserved=True)

    results = {
        "source": "matching_planted_truth.py — planted ATT, selection on observables, seed 20260705, "
                   "N=4000; thin common support in the high-X1 tail; nonlinear outcome surface.",
        "true_effect": TAU,
        "draws": DRAWS,
        # observed-confounding world (conditional independence holds on observed X)
        "naive_diff_single": round(ref["naive"], 3),
        "naive_diff_mean": round(means["naive"], 3),
        "att_full_match_single": round(ref["att_full"], 3),
        "att_full_match_mean": round(means["att_full"], 3),
        "att_full_match_sd": round(af_sd, 3),
        "att_full_match_min": round(af_min, 3),
        "att_full_pct_above_true": round(af_pct_above_true, 1),
        "smd_after_max_single": round(ref["smd_after"], 3),
        "smd_after_max_mean": round(means["smd_after"], 3),
        "smd_after_max_median": round(smd_median, 3),
        "smd_after_pass_rate_pct": round(smd_pass_rate, 1),
        "smd_before_single": [round(v, 3) for v in smd_before(X, d)],
        "smd_after_single": [round(v, 3) for v in smd_after_match(X, ps, d, per_cov=True)],
        "overlap_single": {k: (round(v, 3) if isinstance(v, float) else v) for k, v in ref["overlap"].items()},
        "pct_treated_off_support_mean": round(float(np.mean(off_pct)), 2),
        "att_crump_single": round(ref["att_crump"], 3),
        "att_crump_mean": round(means["att_crump"], 3),
        "smd_crump_after_max_single": round(ref["smd_crump"], 3),
        "pct_treated_kept_crump_single": round(ref["pct_treated_kept_crump"], 1),
        "crump_walk": crump_walk,
        "caliper_walk": caliper_walk,
        "logit_caliper_walk": logit_caliper_walk,
        # HARD limit: unobserved confounding
        "hard_att_full_match_single": round(hard["att_full"], 3),
        "hard_att_crump_single": round(hard["att_crump"], 3),
        "hard_smd_crump_after_max_single": round(hard["smd_crump"], 3),
    }

    RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with RESULTS_PATH.open("w", encoding="utf-8") as fh:
        json.dump(results, fh, indent=2)

    print("PLANTED TRUTH (ATT) =", TAU)
    print(f"  naive difference-in-means   : {results['naive_diff_single']}  (mean {results['naive_diff_mean']})")
    print(f"  NN PS-match, full sample    : {results['att_full_match_single']}  (mean {results['att_full_match_mean']})")
    print(f"  max |SMD| after matching    : {results['smd_after_max_single']}  (mean {results['smd_after_max_mean']}, "
          f"median {results['smd_after_max_median']}; passes 0.10 rule in {results['smd_after_pass_rate_pct']}% of draws)  <- reference table BALANCED")
    print(f"  treated off common support  : {results['overlap_single']['treated_off_support']} "
          f"({results['overlap_single']['pct_treated_off_support']}%)  <- the hidden failure")
    print(f"  Crump [0.1,0.9] trim + match : {results['att_crump_single']}  (mean {results['att_crump_mean']})  "
          f"kept {results['pct_treated_kept_crump_single']}% treated  <- recovers {TAU}")
    print("  Crump band stability:")
    for lo, v in crump_walk.items():
        print(f"    {v['band']}: att {v['att']}  (treated kept {v['treated_kept_pct']}%)")
    print("  RAW-PS caliper (keeps off-support bad matches; PS compresses near 1, does not de-bias):")
    for c, v in caliper_walk.items():
        print(f"    caliper {c}: att {v['att']}  dropped {v['pct_dropped']}%")
    print("  LOGIT-PS caliper (Austin 2011; does de-bias, like Crump trimming):")
    for w, v in logit_caliper_walk.items():
        print(f"    {w}*SD(logit): att {v['att']}  dropped {v['pct_dropped']}%")
    print("HARD LIMIT (unobserved confounder U in both D and Y):")
    print(f"  Crump-trimmed match, observed max-SMD {results['hard_smd_crump_after_max_single']}: "
          f"att {results['hard_att_crump_single']}  <- biased, and NO observed diagnostic flags it")
    print("wrote data/results.json")


if __name__ == "__main__":
    main()
