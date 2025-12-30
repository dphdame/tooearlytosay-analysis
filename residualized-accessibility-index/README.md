# Residualized Accessibility Index

Replication materials for ["Building a Better Metric: The Residualized Accessibility Index"](https://tooearlytosay.com/residualized-accessibility-index/)

## Overview

This analysis constructs a residualized accessibility index that separates structural factors (income, density, car ownership) from policy-responsive variation in food access vulnerability.

## Data Sources

| Dataset | Source | Access |
|---------|--------|--------|
| Demographics | ACS 2019-2023 | Census API |
| Vulnerability index | Computed from components | Derived |

## Methodology

### OLS Regression Specification

```
Vulnerability = β₀ + β₁(Income) + β₂(Density) + β₃(Car_Ownership) + ε
```

The residuals (ε) represent unexplained variation after controlling for structural factors.

### Key Statistics

- R² = 0.81 (81% of between-county variance explained)
- Robust HC1 standard errors for heteroskedasticity
- 58 county observations

### Sensitivity Testing

- Poverty rate substitution for income
- Land area inclusion
- Alternative functional forms

## Repository Structure

```
residualized-accessibility-index/
├── code/
│   ├── 01_prepare_county_data.py
│   ├── 02_run_ols_regression.py
│   ├── 03_extract_residuals.py
│   └── 04_sensitivity_analysis.py
└── data/README.md
```

## License

Code: MIT License
