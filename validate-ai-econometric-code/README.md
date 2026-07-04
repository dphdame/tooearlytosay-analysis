# Validate AI-Written Econometric Code

Replication materials for ["How do we know an AI's estimator does what we meant?"](https://tooearlytosay.com/research/methodology/validate-ai-econometric-code/)

## Overview

When an estimator is reimplemented in Python (by us, a colleague, or an AI assistant), the code can run
cleanly, return a plausible coefficient, and still be wrong. This project ships the check that catches
the errors a clean run hides: plant a **known** treatment effect in simulated data and test whether the
implementation recovers it. `verify_estimator` is a small, drop-in helper you can lift into your own work.

## What it demonstrates

Against a planted true effect of **1.0** on a small-N rolling difference-in-differences design:

1. **The catch (systematic bias).** A `demean` transform recovers **~2.03** — about 4 sampling SDs from
   the truth — because demeaning removes a unit's level but not its diverging trend. The planted-truth
   Monte Carlo flags it; the correct `detrend` transform recovers ~1.00.
2. **Calibration.** The correct estimator's nominal 95% CI covers ~95.6% (±~0.01 at 500 reps).
3. **The limit (what simulation cannot catch).** An input-ordering / shared-RNG-state bug returns 0.18 on
   one seed — but a 2,000-seed Monte Carlo shows it does **not** bias the estimator (buggy and correct
   pipelines have identical means). This class of bug is measure-preserving and is caught only by reading
   the source, not by any planted-truth check. *For speed, the 2,000-seed run uses a raw-draw proxy for
   the RNG stream that randomization inference consumes; the faithful, RI-consuming bug is reproduced
   once at the reported seed (0.18 vs 1.13). Both share the same mechanism — the hard panel is drawn from
   a shifted RNG position — so the proxy is unbiased for any nonzero shift.*

**One caveat that travels with the tool.** The planted-truth check catches a biasing bug only when your
`simulate_dgp` contains the feature that triggers it — here, **heterogeneous unit trends**. On a DGP
without them, `demean` recovers ~1.0 and *passes*. The test is only as strong as the DGP you plant: it
verifies recovery under the process you simulate, not correctness in general.

## How to Run

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cd code
python verify_rolling_did.py
```

The run prints, for each result, the planted truth, the recovered value, and PASS/FAIL. All numbers are
reproducible from a fixed seed; no data download is required.

## Files

| File | What it is |
|------|------------|
| `code/verify_estimator.py` | The generic drop-in `verify_estimator(estimator, simulate_dgp, true_effect, tol)` helper. |
| `code/verify_rolling_did.py` | The proof: applies the helper to the rolling-DiD case (the catch, calibration, and the limit). |
| `code/rolling_did_prototype.py` | The rolling-DiD estimator under test. |
