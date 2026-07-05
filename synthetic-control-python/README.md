# Synthetic control in Python

Replication materials for ["Synthetic control in Python: read the pre-fit before the gap"](https://tooearlytosay.com/research/methodology/synthetic-control-python/).

## What it shows

We can plant a known treatment effect in a simulated panel and test which way of building the
synthetic control recovers it. The point: the post-treatment gap is the least reliable output, and a
*perfect* pre-treatment fit is the weakest evidence for it, not the strongest.

Against a planted effect of **6.0** in a factor-model panel (15 donors, 24 periods, treatment from
period 12), on the reference seed (20260705):

- An **unrestricted (overfitting) fit** matches the pre-period perfectly (pre-RMSPE **0.000**) and
  reads a gap of **6.132**. That number is **not biased** — across 200 draws it centers on **6.002**
  against the truth of 6.0. The failure is not a fabricated number; it is that a perfect pre-fit is
  achievable for any unit, so it certifies nothing. Its cost is variance (gap SD **0.425** vs the
  convex **0.185**) and a discarded diagnostic.
- The **convex** synthetic control (weights ≥ 0, summing to 1, minimizing pre-MSPE) recovers the
  effect too (gap **6.058**, 200-draw mean **5.988**), but with an *honest* pre-RMSPE of **0.303** —
  the diagnostic the perfect fit throws away. It is stable across the pre-period fit window (gap
  6.047 / 5.970 / 6.058 over the last 6 / 9 / 12 periods).
- On an **invalid pool** (treated unit outside the donor hull, no valid counterfactual), the
  unrestricted fit *still* fits perfectly (pre-RMSPE **0.000**) and hides a wrong gap of **4.299**;
  the convex pre-RMSPE blows past it to **7.613** (200-draw mean **8.701**) — the alarm the perfect
  fit never rings. Ridge-shrinking the naive weights does not restore it: the alarm it reports
  (0.529 / 1.148 / 2.494) is a function of the arbitrary penalty, not the data.
- **Permutation inference** is bounded below by 1/(J+1); with 15 donors the smallest attainable
  p-value is **0.062**, and the permutation p sits exactly at that floor even though the effect is 6.0.

The structurally uncatchable limit: a small pre-fit is *necessary* but never *sufficient* to certify
a valid counterfactual. No in-sample number rules out a pool that pre-fits well yet holds no valid
control; that judgment is substantive, not statistical.

## Files

| File | What it is |
|------|------------|
| `code/sc_planted_truth.py` | The harness: factor-model DGP (valid + invalid pool), unrestricted vs convex estimators, ridge no-strawman sweep, convex fit-window stability walk, invalid-pool case, permutation test. Writes `data/results.json`. |
| `code/sc_prefit_panels.py` | Regenerates the article's two-panel figure (valid pool: pre-fit earned; unusable pool: pre-fit fails loudly) from the same seeded DGP. |
| `data/results.json` | Every number cited in the article, frozen from a fixed seed. |

## Run

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python code/sc_planted_truth.py      # prints + writes data/results.json
python code/sc_prefit_panels.py      # writes the two-panel webp
```

Seed is fixed (20260705); no data download. Shifting the treated unit's loadings inside or outside
the donor range is what flips the pre-fit diagnostic from small to large.
