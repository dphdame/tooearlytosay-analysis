# Medicaid Fraud Detection: Replication Materials

Replication code for the 4-part blog series [Screening for Medicaid Fraud with Public Data](https://tooearlytosay.com/research/methodology/medicaid-data-landscape/) and the working paper [What Do Medicaid Fraud Classifiers Actually Detect?](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6251138) (Cholette, 2026).

## Research Question

Can supervised classifiers trained on public Medicaid billing data detect fraud-specific signals, or do they primarily learn enforcement artifacts like truncated billing histories and label contamination from non-fraud exclusions?

## Blog Series

| Post | Title | Link |
|------|-------|------|
| 1 | What 227 Million Rows of Medicaid Data Can and Can't Tell Us | [Link](https://tooearlytosay.com/research/methodology/medicaid-data-landscape/) |
| 2 | The Label That Isn't: Why "Excluded" Doesn't Mean "Fraudulent" | [Link](https://tooearlytosay.com/research/methodology/medicaid-fraud-labels/) |
| 3 | What Billing Patterns Actually Look Like | [Link](https://tooearlytosay.com/research/methodology/medicaid-billing-patterns/) |
| 4 | Can a Classifier Find What Investigators Miss? | [Link](https://tooearlytosay.com/research/methodology/medicaid-fraud-classifier/) |

## Methodology

- **Data**: HHS Medicaid Provider Spending File (2018-2024), OIG LEIE, CA DHCS S&I List
- **Label construction**: Fraud-specific LEIE codes (1128(a)(1), (a)(3), (b)(7), (b)(8), (b)(1)); separate during-panel (N=229) vs. post-panel (N=95) cohorts
- **Censoring correction**: Per-month billing rates instead of panel totals to account for enforcement-truncated observation windows
- **Classification**: Random Forest with grouped 5-fold CV, 10:1 undersampling, 1,000-iteration bootstrap CIs
- **Validation**: Prospective temporal split (train on during-panel exclusions, test on post-panel); placebo test using non-fraud exclusions
- **Key finding**: Prospective AUC 0.725 (95% CI: 0.676-0.777); within-panel AUC 0.830 overstates by 0.105 points due to enforcement censoring

## Data Sources

| Source | URL | Format | Notes |
|--------|-----|--------|-------|
| HHS Medicaid Provider Spending | [data.cms.gov](https://data.cms.gov/summary-statistics-on-use-and-payments/medicaid-provider-spending) | CSV | 227M rows, 7 columns. Privacy suppression below 12 claims. |
| OIG LEIE (current) | [oig.hhs.gov/exclusions](https://oig.hhs.gov/exclusions/exclusions_list.asp) | CSV | ~82,700 entries as of Feb 2026 |
| OIG LEIE (historical) | Same source, archived snapshots | CSV | Captures reinstated providers |
| CA DHCS S&I List | [dhcs.ca.gov](https://www.dhcs.ca.gov/provgovpart/Pages/SandIList.aspx) | CSV | ~22,000 entries |

## How to Run

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Download raw data (see data/README.md for instructions)
python code/01_acquire_leie.py
python code/02_acquire_spending.py

# 3. Construct features and labels
python code/03_build_features.py

# 4. Run classifiers
python code/04_classify.py

# 5. Generate figures
python code/05_generate_figures.py
```

## Citation

```bibtex
@article{cholette2026medicaid,
  title={What Do Medicaid Fraud Classifiers Actually Detect?},
  author={Cholette, Victoria},
  year={2026},
  journal={SSRN Working Paper},
  url={https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6251138}
}
```
