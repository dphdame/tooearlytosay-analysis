# Too Early To Say - Analysis Repository

Replication materials for research published on [Too Early to Say](https://tooearlytosay.com), a personal research blog exploring applied economics in the age of AI.

## Projects

| Project | Blog Post | Description |
|---------|-----------|-------------|
| [food-desert-myth](./food-desert-myth/) | [The Food Desert Myth](https://tooearlytosay.com/food-desert-myth/) | Vulnerability index methodology for Santa Clara County census tracts |
| [grocery-store-classifier-validation](./grocery-store-classifier-validation/) | [400 Labels to 94% Accuracy](https://tooearlytosay.com/grocery-store-classifier-validation/) | Validating grocery store classification using Google Maps data |
| [ebt-verification-methodology](./ebt-verification-methodology/) | [The Retail Density Paradox](https://tooearlytosay.com/ebt-verification-methodology/) | SNAP retailer data validation methodology |

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
