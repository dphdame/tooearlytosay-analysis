# Data Download Instructions

Raw data files are not included in this repository due to size. Follow these steps to acquire them.

## 1. HHS Medicaid Provider Spending File

**Source**: CMS Data Portal
**URL**: https://data.cms.gov/summary-statistics-on-use-and-payments/medicaid-provider-spending
**Size**: ~3 GB (CSV)
**Records**: 227 million rows, 7 columns

Download the full dataset CSV and place in `raw/`:
```
raw/medicaid_provider_spending.csv
```

## 2. OIG LEIE (List of Excluded Individuals/Entities)

**Source**: HHS Office of Inspector General
**URL**: https://oig.hhs.gov/exclusions/exclusions_list.asp
**Format**: CSV download

Download the current exclusion file:
```
raw/UPDATED.csv
```

## 3. California DHCS Suspended & Ineligible List

**Source**: California Department of Health Care Services
**URL**: https://www.dhcs.ca.gov/provgovpart/Pages/SandIList.aspx
**Format**: CSV/Excel

Download and save as:
```
raw/ca_si_list.csv
```

## 4. Historical LEIE Snapshots (Optional)

For capturing reinstated providers, obtain archived LEIE snapshots from the Wayback Machine or institutional archives. Place in:
```
raw/leie_historical/
```
