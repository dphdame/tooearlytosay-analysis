# Contributing to tooearlytosay-analysis

This document describes how to add new replication projects to the repository.

## When to Add a Project

Add a project when:
- Publishing a new research blog post with data analysis
- The analysis uses reproducible methods (code, not manual work)
- Data sources are publicly accessible (or have clear acquisition paths)

Do NOT add a project for:
- Meta posts about methodology/AI coding workflow
- Education policy posts (different research domain)
- Posts without quantitative analysis

## Project Template

### Directory Structure

```
project-name/
├── README.md
├── requirements.txt
├── code/
│   ├── 01_acquire_data.py
│   ├── 02_process_data.py
│   └── 03_analyze.py
└── data/
    ├── README.md
    ├── raw/.gitkeep
    └── processed/.gitkeep
```

### README.md Template

```markdown
# [Project Title]

Replication materials for ["Blog Post Title"](https://tooearlytosay.com/slug/)

## Overview

[2-3 sentences describing the research question and approach]

## Data Sources

| Dataset | Source | Access |
|---------|--------|--------|
| [Name] | [Provider] | [How to get it] |

## Methodology

[Brief methodology description - reference blog post for details]

## How to Run

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Download data per data/README.md instructions
# Then run scripts in order
python code/01_acquire_data.py
python code/02_process_data.py
python code/03_analyze.py
```

## License

Code: MIT License
```

### requirements.txt Template

```
# Core dependencies
pandas>=2.0.0
numpy>=1.24.0

# Add project-specific packages below
```

### data/README.md Template

```markdown
# Data Download Instructions

## [Dataset Name]

**Source:** [URL]
**Access:** [Free/API key/Commercial]

### Download Steps

1. [Step 1]
2. [Step 2]
3. Save to `raw/[filename]`
```

## Naming Conventions

- **Project folders:** Use blog post slug (e.g., `food-desert-myth`)
- **Code files:** Number prefix + descriptive name (e.g., `01_acquire_census_data.py`)
- **Data files:** Descriptive, lowercase, underscores (e.g., `acs_poverty_2022.csv`)

## Code Standards

### Script Header

```python
"""
01_acquire_census_data.py

Downloads ACS data for [purpose].

Input: None (downloads from API)
Output: data/raw/acs_data.csv
"""
```

### Environment Variables

Use `.env` files for API keys:

```python
from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv("CENSUS_API_KEY")
```

### Path Handling

Use relative paths from project root:

```python
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
```

## Updating Main README

After adding a project, update the main `README.md` projects table:

```markdown
| [project-name](./project-name/) | [Post Title](https://tooearlytosay.com/slug/) | Brief description |
```

## Commit Message Format

```
Add [project-name] replication materials

- [Key methodology point]
- [Data sources used]
- [Notable analysis approach]

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
```

## Checklist Before Committing

- [ ] README.md with methodology and data sources
- [ ] requirements.txt with all dependencies
- [ ] data/README.md with download instructions
- [ ] .gitkeep files in data/raw/ and data/processed/
- [ ] Code files numbered in execution order
- [ ] Main README.md updated with new project
- [ ] No raw data files committed (only instructions)
- [ ] No API keys or credentials in code
