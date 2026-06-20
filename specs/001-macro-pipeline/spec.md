# Feature Specification: Global Macro Dashboard Pipeline

**Feature:** `001-macro-pipeline`
**Author:** Trevor Monroe
**Date:** June 2026
**Status:** Operational

---

## Overview

A four-notebook pipeline that fetches, transforms, models, and renders a weekly Global Macro Dashboard published to GitHub Pages. The pipeline runs automatically every Monday via GitHub Actions and produces a self-contained `docs/index.html` with Plotly charts and a country scoreboard.

---

## Architecture

```
01_ingest → 02_transform → 03_model → 04_render → docs/index.html
```

Each notebook is executed by `papermill`, which injects `run_date` (the UTC date of the workflow run) as a parameter. Outputs are committed back to the repo and deployed to GitHub Pages.

---

## Notebooks

| Notebook | Purpose | Key Outputs |
|----------|---------|-------------|
| `01_ingest.ipynb` | Fetch raw data from FRED, World Bank, IMF WEO, yfinance, FRED policy rates | `data/raw/*.parquet` |
| `02_transform.ipynb` | Resample to monthly, compute derived series, merge into unified panel | `data/processed/us_series.parquet`, `data/processed/macro_panel.parquet` |
| `03_model.ipynb` | Compute indicators (yield curve, recession prob, inflation regime, risk score, country scoreboard) | `data/outputs/indicators.parquet`, `data/outputs/latest_snapshot.json`, `data/outputs/country_scoreboard.parquet` |
| `04_render.ipynb` | Build Plotly charts, assemble self-contained HTML dashboard | `docs/index.html` |

---

## Data Sources

| Source | Library | Series / Indicators |
|--------|---------|-------------------|
| FRED (St. Louis Fed) | `fredapi` | GDP growth, CPI, PCE, Fed funds rate, 2y/10y/3m Treasury yields, unemployment, M2, HY credit spread (ICE BofA) |
| World Bank | `wbdata` | GDP growth, CPI inflation, current account % GDP, govt debt % GDP, unemployment — G20 economies |
| IMF World Economic Outlook | `imf-reader` | Real GDP growth, CPI, unemployment, current account, govt debt — major economies + forecasts |
| yfinance | `yfinance` | YTD equity index performance — 12 major indices (S&P 500, DAX, Nikkei, FTSE, etc.) |
| FRED (policy rates) | `fredapi` | Central bank policy rates — 12 economies via OECD/ECB/Fed series |

**FRED API Key:** Required. Set via:
- GitHub Actions: `secrets.FRED_API_KEY`
- Colab: Colab Secrets (`FRED_API_KEY`)
- Local: `.env` file (`FRED_API_KEY=...`)

---

## Indicators Produced

| Indicator | Method |
|-----------|--------|
| Yield curve spread (10y–2y, 10y–3m) | FRED daily yields resampled to month-end |
| Inversion signal | Spread < 0 for ≥ 3 consecutive months |
| Recession probability (12m ahead) | Estrella-Mishkin probit: Φ(−0.6521 − 0.2375 × spread_10y3m) |
| Inflation regime | CPI YoY z-score vs 20-year rolling mean; thresholds at −0.5 / +0.5 / +1.5 |
| Global growth pulse | GDP-weighted IMF NGDP_RPCH average across major economies |
| Risk-on/risk-off score | Composite z-score of credit spread, real 10y rate, yield curve; clipped to [−1, +1] |

---

## Dashboard Output

`docs/index.html` — self-contained HTML (Plotly CDN, no backend required). Deployed to GitHub Pages.

**Tabs:**
1. **Macro Signals** — yield curve time series, recession probability history, inflation regime bar chart, risk gauge, key metrics card
2. **Country Scoreboard** — 12 major economies with GDP, inflation, unemployment, current account, govt debt, policy rate, stock YTD

**Header:** `"As of YYYY-MM-DD · Powered by FRED · World Bank · IMF WEO"` — date is the `run_date` injected by papermill (the actual pipeline run date, not a data timestamp).

---

## GitHub Actions Workflow

**File:** `.github/workflows/weekly_pipeline.yml`

- **Schedule:** Every Monday at 06:00 UTC (`cron: '0 6 * * 1'`)
- **Trigger:** Also supports manual dispatch from the Actions tab
- **Runner:** `ubuntu-latest`, Python 3.14
- **Steps:** install deps → run 4 notebooks via papermill → commit `docs/` + `data/outputs/` → deploy to GitHub Pages via `peaceiris/actions-gh-pages@v4`
- **GitHub Pages branch:** `gh-pages`

**Required secrets:**
| Secret | Purpose |
|--------|---------|
| `FRED_API_KEY` | FRED data pull in 01_ingest |
| `GITHUB_TOKEN` | Auto-provided; used for Pages deploy |

---

## Known Issues

### Date label shows future month-end (resample artifact)
`02_transform.ipynb` uses `fred.resample("ME").last()`. Pandas `"ME"` labels buckets with the last day of the month, so mid-month data for June gets indexed as `2026-06-30`. The `as_of` field in `latest_snapshot.json` previously took this index date directly, resulting in a dashboard date 10 days in the future.

**Fix (applied):** `03_model.ipynb` now uses `run_date or str(latest.name.date())` — papermill injects the real run date, so the header reflects the actual pipeline execution date.

### Colab vs Actions data paths
The notebooks support two environments: Google Colab (data in Google Drive at `/content/drive/MyDrive/macro-dashboard/`) and GitHub Actions (data in local `data/` directory). The `_IN_COLAB` flag controls which path is used. Running locally outside of either environment requires the `data/raw/`, `data/processed/`, and `data/outputs/` directories to exist.

### Local data directories are gitignored
`data/raw/`, `data/processed/`, and `data/outputs/` contain only `.gitkeep` files in the repo. Running the pipeline locally requires executing all four notebooks in order to populate them.

---

## Running Locally

```bash
# Activate environment
source macro_env/Scripts/activate   # Windows: macro_env\Scripts\activate

# Run each notebook in order (inject today's date)
TODAY=$(date -u +%Y-%m-%d)
papermill notebooks/01_ingest.ipynb /dev/null -p run_date "$TODAY"
papermill notebooks/02_transform.ipynb /dev/null -p run_date "$TODAY"
papermill notebooks/03_model.ipynb /dev/null -p run_date "$TODAY"
papermill notebooks/04_render.ipynb /dev/null -p run_date "$TODAY"

# Output: docs/index.html
```

---

## File Reference

| Path | Purpose |
|------|---------|
| `notebooks/01_ingest.ipynb` | Data ingestion |
| `notebooks/02_transform.ipynb` | Data transformation and feature engineering |
| `notebooks/03_model.ipynb` | Indicator computation and snapshot JSON |
| `notebooks/04_render.ipynb` | HTML dashboard render |
| `docs/index.html` | Published dashboard (GitHub Pages) |
| `data/raw/` | Raw parquet files (gitignored, populated by 01_ingest) |
| `data/processed/` | Processed parquet files (gitignored, populated by 02_transform) |
| `data/outputs/` | Model outputs and snapshot (gitignored, populated by 03_model) |
| `.github/workflows/weekly_pipeline.yml` | GitHub Actions workflow |
| `requirements.txt` | Python dependencies |
| `macro_env/` | Local virtualenv (not committed to git) |
