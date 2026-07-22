# Difference-in-differences in Python

Replication materials for ["Difference-in-Differences in Python: When TWFE Misleads"](https://tooearlytosay.com/research/methodology/difference-in-differences-python/).

## What it shows

We plant known cohort-time treatment effects in a staggered-adoption panel and test which estimator
recovers the true average. The point: with staggered timing and effects that differ across cohorts,
the two-way fixed-effects (TWFE) coefficient is a weighted average that can carry negative weights on
some comparisons, so it stops being the average treatment effect.

On the reference seed (20260705; cohorts adopt at periods 4 and 7, plus never-treated; effects grow
with exposure and the early cohort's is larger):

- The **true** average effect across treated unit-periods is **1.60** (exact population arithmetic).
- **Static TWFE** returns **1.01** (200-draw mean; 0.97 on the single reference panel) — about **37%
  too low**, because already-treated units get used as controls (Goodman-Bacon 2021; de Chaisemartin
  & D'Haultfœuille 2020).
- A **group-time** estimator (Callaway & Sant'Anna 2021) that only ever compares against not-yet-
  treated units recovers **1.60**.
- **No-strawman sweep:** TWFE matches the truth only when effects are homogeneous *and* static (0.49
  vs 0.50). Make the identical effect dynamic and it misses (1.06 vs 1.50); add cross-cohort
  heterogeneity and it misses by a size that shifts with the pattern (1.00 vs 1.60 early-larger, 0.91
  vs 1.10 late-larger). All shown scenarios bias downward; a sign flip needs stronger late
  heterogeneity than any shown.
- **The estimand is a choice:** unit-period weighting gives 1.60, equal-weight-by-cohort gives 1.35
  (the two cohort ATTs are 2.1 and 0.6) — a 19% gap the analyst must name.

The structurally-uncatchable limit: the clean-controls fix removes the negative-weight contamination,
not a parallel-trends or anticipation violation. The planted effect is zero pre-adoption by
construction, so a pre-trend test passes; anticipation would bias both the pre-test and the estimate,
and the not-yet-treated controls can themselves anticipate.

## Files

| File | What it is |
|------|------------|
| `code/did_planted_truth.py` | The harness: staggered-adoption DGP, static TWFE, group-time (CS) estimator, the four-scenario sweep, the two estimands. Writes `data/results.json`. |
| `code/did_comprehension_figures.py` | Regenerates the article's figures (staggered panel, TWFE-vs-CS-vs-truth, the sweep, the clean-vs-contaminated-controls schematic) from the same seeded DGP. |
| `data/results.json` | Every number cited in the article, frozen from a fixed seed. |

## Run

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python code/did_planted_truth.py         # prints + writes data/results.json
```

Seed is fixed (20260705); no data download. Changing which cohort has the larger effect changes the
size of the downward TWFE bias while the group-time estimator stays on the truth.

## Optional site-maintainer figure workflow

The figure script targets the Too Early To Say site asset workflow. It is not portable replication
output and is not part of the clean-clone evidence gate.

```bash
python code/did_comprehension_figures.py # writes the figure webp/png set
```
