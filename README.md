# Too Early To Say - Analysis Repository

Replication materials for research published on [Too Early to Say](https://tooearlytosay.com), a personal research blog exploring applied economics in the age of AI.

## Projects

| Project | Blog Post | Description |
|---------|-----------|-------------|
| [food-desert-myth](./food-desert-myth/) | [The Food Desert Myth](https://tooearlytosay.com/food-desert-myth/) | Vulnerability index methodology for Santa Clara County census tracts |
| [grocery-store-classifier-validation](./grocery-store-classifier-validation/) | [400 Labels to 94% Accuracy](https://tooearlytosay.com/grocery-store-classifier-validation/) | Validating grocery store classification using Google Maps data |
| [ebt-verification-methodology](./ebt-verification-methodology/) | [The Retail Density Paradox](https://tooearlytosay.com/ebt-verification-methodology/) | SNAP retailer data validation methodology |
| [mobility-deserts](./mobility-deserts/) | [Mobility Deserts](https://tooearlytosay.com/hidden-mobility-deserts/) | Identifying CA census tracts with grocery access but poor transit |
| [working-poor-silicon-valley](./working-poor-silicon-valley/) | [When Work Isn't Enough](https://tooearlytosay.com/working-poor-silicon-valley/) | Bay Area tracts with high employment but elevated poverty |
| [housing-tenure](./housing-tenure/) | [Renters vs. Owners](https://tooearlytosay.com/housing-tenure/) | Housing tenure and grocery accessibility analysis |
| [transit-equity-race](./transit-equity-race/) | [Transit Equity and Race](https://tooearlytosay.com/transit-equity-race/) | Racial disparities in transit-based food access |
| [crime-geography-precision](./crime-geography-precision/) | [Crime Geography Precision](https://tooearlytosay.com/crime-geography-precision/) | Block-level vs tract-level crime analysis precision |
| [food-access-vulnerability-paradox](./food-access-vulnerability-paradox/) | [The Vulnerability Paradox](https://tooearlytosay.com/food-access-vulnerability-paradox/) | High grocery access coexisting with high vulnerability |
| [scaling-statewide](./scaling-statewide/) | [Scaling Statewide](https://tooearlytosay.com/scaling-statewide/) | County-to-state scaling methodology |
| [residualized-accessibility-index](./residualized-accessibility-index/) | [Beyond Distance](https://tooearlytosay.com/residualized-accessibility-index/) | Accessibility index controlling for confounders |
| [county-comparison-methods](./county-comparison-methods/) | [Apples to Apples](https://tooearlytosay.com/county-comparison-methods/) | Standardized cross-county comparison methods |
| [data-quality-improvement](./data-quality-improvement/) | [From 49% to 12%](https://tooearlytosay.com/data-quality-49-to-12/) | Data quality improvement workflow |
| [transit-routing-free-tools](./transit-routing-free-tools/) | [Free Transit Routing](https://tooearlytosay.com/transit-routing-free-tools/) | Open-source transit accessibility analysis |
| [diverging-trajectories](./diverging-trajectories/) | [Diverging Trajectories](https://tooearlytosay.com/diverging-trajectories/) | Long-term food access trend analysis |
| [covid-differential-impact](./covid-differential-impact/) | [COVID's Unequal Impact](https://tooearlytosay.com/covid-differential-impact/) | Pandemic impact on food access by vulnerability |
| [extended-vulnerability-index](./extended-vulnerability-index/) | [Extended Vulnerability Index](https://tooearlytosay.com/extended-vulnerability-index/) | Multi-domain vulnerability measure construction |
| [robust-api-collection](./robust-api-collection/) | [6,613 Stores, Zero Lost Data](https://tooearlytosay.com/robust-api-data-collection/) | Robust API data collection patterns |

## Getting Started

Each project folder contains:

```
project-name/
├── README.md           # Research question, methodology, how to run
├── requirements.txt    # Python dependencies
├── code/               # Analysis scripts (numbered for order)
└── data/
    └── README.md       # Instructions to download public data
```

### Prerequisites

- Python 3.9+
- Census API key (free): https://api.census.gov/data/key_signup.html

### General Setup

```bash
# Clone the repo
git clone https://github.com/dphdame/tooearlytosay-analysis.git
cd tooearlytosay-analysis

# Navigate to a project
cd food-desert-myth

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Follow data/README.md to download required datasets
# Then run scripts in numbered order
python code/01_acquire_census_data.py
python code/02_calculate_vulnerability_index.py
# etc.
```

## Data

All projects use publicly available data from:

- U.S. Census Bureau American Community Survey (ACS)
- USDA SNAP Retailer Locator
- Google Maps Places API (requires API key)

See [DATA_SOURCES.md](./DATA_SOURCES.md) for detailed information about each data source.

**Note:** Raw data files are not included in this repository. Each project's `data/README.md` contains instructions to download the required datasets.

## Citation

If you use this code or methodology in your work:

> See blog post at https://tooearlytosay.com/[article-name]

## License

Code: [MIT License](./LICENSE)

Data: Subject to original source terms (Census Bureau, USDA, Google)

## Author

V. Cholette
[Too Early to Say](https://tooearlytosay.com)
