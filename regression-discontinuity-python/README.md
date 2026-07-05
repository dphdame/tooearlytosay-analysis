# Regression discontinuity in Python

Replication materials for ["Regression discontinuity in Python: getting the effect at the cutoff right"](https://tooearlytosay.com/research/methodology/regression-discontinuity-python/).

## What it shows

We can plant a known treatment effect at a cutoff and test which estimator recovers it. The point:
the number the code returns is the least reliable part of an RDD, and two things matter more than it
— whether the estimate is stable across defensible modeling choices, and whether the cutoff isolates
the treatment at all.

Against a planted cutoff effect of **0.75** (treated-average effect 1.5, so the design is genuinely
local), on the reference seed:

- A naive **global quadratic** returns **1.82**; the answer swings with the polynomial order
  (cubic 0.81, fifth-order 0.74) with nothing in the output saying which is right.
- A **local-linear** fit at a data-driven bandwidth returns **0.87** (95% CI covers 0.75; 200-draw
  mean 0.75) — close, not exact, and it moves with the bandwidth (the seam).
- A **compound treatment** at the same cutoff biases the local fit to **1.18** while a density test
  passes cleanly — the identification limit a smooth planted-truth harness cannot self-catch.

## Files

| File | What it is |
|------|------------|
| `code/rdd_planted_truth.py` | The harness: DGP, naive global vs local-linear, order sweep, bandwidth walk, compound-treatment case. Writes `data/results.json`. |
| `code/rdd_scatter.py` | Regenerates the article's scatter figure (global fit overshoot vs local fit) from the same seeded DGP. |
| `data/results.json` | Every number cited in the article, frozen from a fixed seed. |

## Run

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python code/rdd_planted_truth.py     # prints + writes data/results.json
python code/rdd_scatter.py           # writes the scatter webp
```

Seed is fixed (20260704); no data download. Change the outcome shape or the effect and the harness
reports how each estimator behaves.
