# Instrumental variables in Python

Replication materials for ["Instrumental Variables in Python: Strength Is Not Validity"](https://tooearlytosay.com/research/methodology/instrumental-variables-python/).

## What it shows

We plant a known treatment effect in confounded data with one instrument and test which estimator
recovers it. The point: a large first-stage F statistic certifies that the instrument is *relevant*,
and says nothing about whether it is *valid*. The relevance failure (a weak instrument) is diagnosable
from the data; the validity failure (an exclusion violation) is not.

On the reference seed (20260705; N=4,000, one unobserved confounder, one instrument; the planted
effect of the regressor on the outcome is **2.0**):

- **OLS is biased by the confounder.** Regressing the outcome on the regressor directly gives **2.79**
  (200-draw mean; 2.81 on the single reference draw) — about **40% too high**, because the regressor
  and the outcome share the unobserved confounder.
- **The OLS bias does not shrink with more data.** At sample sizes of 1,000 / 4,000 / 16,000 the OLS
  estimate holds at **2.80 / 2.79 / 2.79**. The bias is structural, not sampling noise.
- **2SLS recovers the planted effect.** Using only the variation the instrument supplies gives **2.00**
  (200-draw mean; 2.02 on the single draw), with a first-stage F of about **2,062** — a very strong
  instrument.
- **The weak-instrument limit is diagnosable.** Make the instrument barely move the regressor and 2SLS
  becomes unreliable: the estimate averages **0.99** with a standard deviation of **9.2**, and the
  first-stage F drops to about **9**. The low F is the visible warning.
- **The exclusion limit is not diagnosable.** Give the instrument a small direct effect on the outcome
  (a path that does not run through the regressor) and 2SLS is biased to **2.62** against the true 2.0,
  about **31% too high** — while the first-stage F stays about **2,051**. The instrument still looks
  strong; nothing in the data flags the violation.

The structurally-uncatchable limit: with a single, just-identified instrument there is no overidentifying
restriction to test, so the exclusion restriction rests on an argument about the instrument, not on a
statistic. A large first-stage F confirms relevance and is silent on validity.

## Files

| File | What it is |
|------|------------|
| `code/iv_planted_truth.py` | The harness: confounded DGP with one instrument, naive OLS, 2SLS (`cov(Z,Y)/cov(Z,D)`), first-stage F, the sample-size sweep, and the weak-instrument and exclusion-violation cases. Writes `data/results.json`. |
| `code/iv_comprehension_figures.py` | Regenerates the article's four figures (OLS-vs-2SLS-vs-truth, OLS bias across sample size, the two limits, and the exclusion-path schematic) from the same seeded DGP. |
| `data/results.json` | Every number cited in the article, frozen from a fixed seed. |

## Run

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python code/iv_planted_truth.py          # prints + writes data/results.json
```

Seed is fixed (20260705); no data download. The two-stage estimate corrects the OLS confounding bias,
but only under the exclusion restriction — which no first-stage statistic can certify.

## Optional site-maintainer figure workflow

The figure script targets the Too Early To Say site asset workflow. It is not portable replication
output and is not part of the clean-clone evidence gate.

```bash
python code/iv_comprehension_figures.py  # writes the figure png set
```
