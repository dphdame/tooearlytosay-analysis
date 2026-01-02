# tooearlytosay-analysis - Project Instructions

## Overview

Public GitHub repository containing replication materials for research published on [Too Early to Say](https://tooearlytosay.com).

**Repository:** https://github.com/dphdame/tooearlytosay-analysis
**Author:** V. Cholette (vcholette)

## Git Configuration

```bash
git config user.name "vcholette"
git config user.email "vcholette@users.noreply.github.com"
```

**IMPORTANT:** Use the GitHub noreply email to protect privacy. Never use personal email in commits.

## Repository Structure

```
tooearlytosay-analysis/
├── README.md                    # Main repo documentation
├── DATA_SOURCES.md              # Comprehensive data source guide
├── CONTRIBUTING.md              # How to add new projects
├── CLAUDE.md                    # This file
├── LICENSE                      # MIT License
└── [project-name]/              # One folder per blog post
    ├── README.md                # Research question, methodology
    ├── requirements.txt         # Python dependencies
    ├── code/                    # Analysis scripts (numbered)
    │   ├── 01_acquire_*.py
    │   ├── 02_process_*.py
    │   └── 03_analyze_*.py
    └── data/
        ├── README.md            # Data download instructions
        ├── raw/.gitkeep         # Raw data (not committed)
        └── processed/.gitkeep   # Processed data (not committed)
```

## Current Projects (18 total)

| Project | Blog Post | Status |
|---------|-----------|--------|
| food-desert-myth | The Food Desert Myth | Published |
| grocery-store-classifier-validation | 400 Labels to 94% Accuracy | Published |
| ebt-verification-methodology | The Retail Density Paradox | Published |
| mobility-deserts | Mobility Deserts | Published |
| working-poor-silicon-valley | When Work Isn't Enough | Published |
| housing-tenure | Renters vs. Owners | Draft |
| transit-equity-race | Transit Equity and Race | Draft |
| crime-geography-precision | Crime Geography Precision | Published |
| food-access-vulnerability-paradox | The Vulnerability Paradox | Published |
| scaling-statewide | Scaling Statewide | Published |
| residualized-accessibility-index | Beyond Distance | Published |
| county-comparison-methods | Apples to Apples | Published |
| data-quality-improvement | From 49% to 12% | Published |
| transit-routing-free-tools | Free Transit Routing | Published |
| diverging-trajectories | Diverging Trajectories | Published |
| covid-differential-impact | COVID's Unequal Impact | Published |
| extended-vulnerability-index | Extended Vulnerability Index | Published |
| robust-api-collection | 6,613 Stores, Zero Lost Data | Published |

## Blog Posts WITHOUT Repo Projects

These posts don't have replication code (by design):

**Education Policy (different domain):**
- protecting-special-ed-shifted-cuts
- stimulus-saved-schools-then-worse

**Meta/AI Coding Posts (methodology, not data analysis):**
- ai-research-graphics-antigravity
- cleaning-research-codebase
- copy-paste-ai-coding-limits
- methodology-to-code-ai
- claude-md-research-context

## Adding a New Project

### 1. Create Directory Structure

```bash
mkdir -p project-name/{code,data/{raw,processed}}
touch project-name/data/raw/.gitkeep
touch project-name/data/processed/.gitkeep
```

### 2. Required Files

**README.md** - Include:
- Link to blog post
- Research question
- Methodology overview
- Data sources table
- How to run

**requirements.txt** - Python dependencies

**data/README.md** - Download instructions for each dataset

### 3. Code Organization

Number scripts in execution order:
```
01_acquire_census_data.py
02_acquire_gtfs_data.py
03_merge_datasets.py
04_calculate_metrics.py
05_generate_figures.py
```

### 4. Update Main README

Add row to projects table in `/README.md`

### 5. Commit and Push

```bash
git add .
git commit -m "Add [project-name] replication materials"
git push origin main
```

## Common Data Sources

| Source | Access | API Key Required |
|--------|--------|------------------|
| Census ACS | api.census.gov | Yes (free) |
| USDA SNAP Retailers | usda-fns.hub.arcgis.com | No |
| Cal-ITP GTFS | data.ca.gov | No |
| Google Places API | console.cloud.google.com | Yes (paid) |
| BLS Wages | api.bls.gov | Yes (free) |
| SafeGraph | safegraph.com | Commercial license |

## Ghost Blog Integration

When adding repo projects, update the corresponding blog posts to link to the repo:

```javascript
// Use mobiledoc format for Ghost edits
const GhostAdminAPI = require('@tryghost/admin-api');
const api = new GhostAdminAPI({
    url: 'https://tooearlytosay.com',
    key: '68f7d73612f7490002ca976b:01c2973db84b5e2b668a328960a9fd09a323e1826f2db78045b19e47fb81eecb',
    version: 'v5.0'
});
```

**Important:** Ghost stores content in mobiledoc format, not HTML. Edits using `html` parameter won't persist. Parse and modify `mobiledoc` directly.

## Checking Blog-Repo Alignment

To list all blog posts and check for repo coverage:

```bash
cd /Users/victoriaperez/Projects/TooEarly
node -e "
const GhostAdminAPI = require('@tryghost/admin-api');
const api = new GhostAdminAPI({
    url: 'https://tooearlytosay.com',
    key: '68f7d73612f7490002ca976b:01c2973db84b5e2b668a328960a9fd09a323e1826f2db78045b19e47fb81eecb',
    version: 'v5.0'
});
api.posts.browse({ limit: 'all' }).then(posts => {
    posts.forEach(p => console.log(p.slug + ' | ' + p.status + ' | ' + p.title));
});
"
```

## Last Updated

2025-01-01: Added 13 research projects (housing-tenure through robust-api-collection)
