# Matching in Python

Replication materials for ["Matching in Python: Balance Does Not Prove Validity"](https://tooearlytosay.com/research/methodology/matching-python/).

## What it shows

We plant a known treatment effect under selection on observables and test which estimator recovers
it. The point: a propensity-score match can pass every covariate-balance check and still return the
wrong number, because a balanced table does not establish that a comparable control existed for every
treated unit. Balance is testable; so is common support; the unconfoundedness assumption beneath both
is not.

On the reference seed (20260705; N = 4,000, two covariates driving both treatment and outcome, a thin
common-support region in the high-X1 tail, nonlinear outcome surface; the planted ATT is **2.0**, the
same for every unit, so ATT = ATE):

- **The naive matched estimate looks clean and is wrong.** Nearest-neighbor propensity-score matching
  returns **2.21** (200-draw mean **2.23**, SD 0.22, above the truth in 84% of draws) — about 10%
  high. The balance table is clean: covariate imbalance falls from an SMD of **1.72 / 0.92** before
  matching to a maximum of **0.08** after, under the 0.10 rule. Across 200 draws the matched balance
  table clears the 0.10 rule only 48.5% of the time (median 0.102), and the estimate runs high even
  when it passes — so the balance check and the bias are close to independent.
- **The check that catches it is common support.** **6.0%** of treated units (200-draw mean 8.9%)
  have a propensity above every control's — no comparable control exists, so nearest-neighbor pairs
  them with distant controls and the nonlinear surface enters as bias.
- **Restoring common support recovers the effect, two ways.** The [0.1, 0.9] propensity-trimming rule
  of thumb (Crump, Hotz, Imbens & Mitnik 2009 — their fixed rule, not their variance-minimizing
  cutoff) gives **2.04**, keeping 62% of treated units (200-draw mean 2.00). The field-standard
  logit-propensity caliper (Austin 2011, width 0.2·SD of the logit) gives **2.05**, dropping the 3.7%
  of pairs with no close comparison. A caliper on the *raw* propensity does not help — it stays at
  2.21 and drops 0% — because the propensity scale compresses near 1; the logit scale keeps the
  non-overlap visible.
- **The structurally uncatchable limit is unconfoundedness.** Add an unobserved confounder that moves
  both treatment and outcome, then run the whole honest workflow — trim to common support, match,
  check balance. Every observed covariate balances (max SMD **0.065**) and overlap is restored, and
  the estimate is **3.23** against the true 2.0, about 60% too high. Nothing computable from the
  observed data flags it. That is the conditional-independence assumption matching rests on: an
  argument about the world, not a quantity in the data.

## Files

| File | What it is |
|------|------------|
| `code/matching_planted_truth.py` | The harness: selection-on-observables DGP with thin common support, nearest-neighbor propensity matching, the balance table, the common-support diagnostic, [0.1, 0.9] trimming, the raw- and logit-propensity caliper walks, the trimming-band stability walk, and the unobserved-confounder case. Writes `data/results.json`. |
| `code/matching_comprehension_figures.py` | Regenerates the article's four figures (propensity overlap, balance-vs-bias, the two overlap-restoring fixes, and the unobserved-confounder schematic) from the same seeded DGP, with a self-asserting layout gate that exits nonzero on a figure collision. |
| `data/results.json` | Every number cited in the article, frozen from a fixed seed. |

## Run

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python code/matching_planted_truth.py          # prints + writes data/results.json
```

Seed is fixed (20260705); no data download. Trimming to common support removes the bad-match bias, but
only the observed-covariate version of it — an unobserved confounder passes every check unmarked.

## Optional site-maintainer figure workflow

The figure script targets the Too Early To Say site asset workflow. It is not portable replication
output and is not part of the clean-clone evidence gate.

```bash
python code/matching_comprehension_figures.py  # writes the figure png set (asserts layout)
```
