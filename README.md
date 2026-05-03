# Global Macro Dashboard

An automated investment decision-support dashboard tracking global macroeconomic
conditions across growth, inflation, monetary policy, credit, and risk sentiment.
Runs weekly via GitHub Actions and publishes to GitHub Pages.

---

## Data Sources

| Source | Coverage | Access |
|--------|----------|--------|
| FRED (St. Louis Fed) | US macro series (GDP, CPI, yield curve, unemployment) | Free API key — set `FRED_API_KEY` secret |
| World Bank | Cross-country GDP, inflation, current account | Public via `wbdata` |
| IMF | WEO forecasts, financial soundness indicators | Public via `imf-reader` |

---

## Notebooks

| Notebook | Purpose |
|----------|---------|
| `01_ingest.ipynb` | Fetch raw data from all sources, save to `data/raw/` |
| `02_transform.ipynb` | Clean, align, and merge datasets, save to `data/processed/` |
| `03_model.ipynb` | Compute indicators (yield curve, recession probability, z-scores), save to `data/outputs/` |
| `04_render.ipynb` | Build Plotly charts and export HTML dashboard to `docs/` |

---

## Deployment

The pipeline runs every Monday at 06:00 UTC via `.github/workflows/weekly_pipeline.yml`.

1. Papermill executes each notebook in sequence
2. Outputs are committed back to the repo
3. The `docs/` folder is deployed to GitHub Pages

To enable GitHub Pages: **Settings → Pages → Source → Deploy from branch → `gh-pages`**

To run manually: **Actions → Weekly Macro Dashboard Pipeline → Run workflow**

---

## Local Setup

```bash
# Activate environment
macro_env\Scripts\Activate.ps1   # Windows
source macro_env/bin/activate    # Mac/Linux

# Run a single notebook
papermill notebooks/01_ingest.ipynb notebooks/01_ingest_out.ipynb
```

---

## Secrets Required

| Secret | Description |
|--------|-------------|
| `FRED_API_KEY` | FRED API key from fred.stlouisfed.org |
