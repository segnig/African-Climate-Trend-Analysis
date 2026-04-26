# African Climate Trend Analysis (Week 0)

This repository is a starter implementation for the **10 Academy Week 0 challenge**:
- Task 1: Git + Environment + CI
- Task 2: Country-level profiling, cleaning, and EDA
- Task 3: Cross-country comparison and vulnerability framing
- Bonus: Streamlit dashboard starter

## Project Structure

```text
.
├── .vscode/
│   └── settings.json
├── .github/
│   └── workflows/
│       └── ci.yml
├── app/
│   ├── __init__.py
│   ├── main.py
│   └── utils.py
├── notebooks/
│   ├── __init__.py
│   ├── README.md
│   ├── ethiopia_eda.ipynb
│   └── compare_countries.ipynb
├── scripts/
│   ├── __init__.py
│   ├── README.md
│   ├── run_country_eda.py
│   └── run_compare.py
├── src/
│   ├── __init__.py
│   ├── compare.py
│   ├── data_utils.py
│   └── eda.py
├── tests/
│   └── __init__.py
├── dashboard_screenshots/
│   └── .gitkeep
├── .gitignore
├── requirements.txt
└── README.md
```

## Environment Setup

### 1) Create and activate virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

### 2) Install dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## Branching and Conventional Commits

Recommended branch flow:

- `setup-task` for Task 1
- `eda-ethiopia`, `eda-kenya`, `eda-sudan`, `eda-tanzania`, `eda-nigeria` for Task 2
- `compare-countries` for Task 3
- `dashboard-dev` for Streamlit bonus

Conventional commit examples:

- `init: add project scaffold`
- `chore: configure python environment and dependencies`
- `ci: add github actions workflow`
- `feat: add country-level eda pipeline`
- `feat: add cross-country comparison analysis`
- `feat: basic streamlit ui`

## Data Policy

- Place raw files under `data/` locally.
- `data/` and `*.csv` are ignored by Git.
- **Do not commit climate CSV files to GitHub**.

## Data Legend Alignment

Implementation is aligned to `data/Data Legend.txt`:

- Expected schema: `YEAR`, `DOY`, `T2M`, `T2M_MAX`, `T2M_MIN`, `T2M_RANGE`, `PRECTOTCORR`, `RH2M`, `WS2M`, `WS2M_MAX`, `PS`, `QV2M`.
- Loader supports NASA-style files with metadata lines by auto-detecting the header row containing `YEAR` and `DOY`.
- Sentinel handling: all `-999` values are replaced with `NaN` before profiling/statistics.
- Date reconstruction: `DATE = to_datetime(YEAR*1000 + DOY, format="%Y%j")`; invalid DOY values are coerced to missing.
- Country context uses representative capital coordinates from the legend (Addis Ababa, Nairobi, Khartoum, Dar es Salaam, Lagos).

Note: dataset reflects **representative point locations**, not whole-country spatial averages.

## Task 2 Quick Start (Country EDA)

For one country (example: Ethiopia):

```bash
python scripts/run_country_eda.py --country ethiopia --input data/ethiopia.csv
```

Outputs:
- `data/ethiopia_clean.csv`
- charts in `reports/figures/`
- cleaning metrics in terminal output

Use `notebooks/ethiopia_eda.ipynb` for narrative interpretation and required markdown commentary.

## Task 3 Quick Start (Comparison)

After generating all five cleaned files:

```bash
python scripts/run_compare.py
```

Outputs in `reports/`:
- figures: multi-country temperature comparison
- tables: summary statistics, extreme heat, dry spells
- significance tests JSON (ANOVA + Kruskal-Wallis)

Use `notebooks/compare_countries.ipynb` for final vulnerability ranking and COP32-framed bullet insights.

## Streamlit Dashboard (Bonus)

Run:

```bash
streamlit run app/main.py
```

Included minimum features:
- country multi-select
- year range slider
- temperature trend line chart
- precipitation distribution boxplot

## CI

GitHub Actions workflow in `.github/workflows/ci.yml` runs on push/PR to `main`:
- installs dependencies from `requirements.txt`
- checks `python --version`

## Submission Checklist

### Interim (Sun, 26 Apr 2026)
- GitHub main branch link
- Task 1 summary
- Task 2 profiling/cleaning approach

### Final (Tue, 28 Apr 2026)
- GitHub main branch link
- Final Medium-style report in PDF
- Optional dashboard screenshot under `dashboard_screenshots/`

## Notes on Negotiation-Grade Insights

Aim for each key figure to answer:
1. What is changing? (trend/anomaly)
2. What did it cause? (impact stat from secondary source)
3. What does it demand? (policy/finance ask)

That framing is what elevates EDA outputs into COP-relevant evidence.
# African-Climate-Trend-Analysis
