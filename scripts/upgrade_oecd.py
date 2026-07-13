"""
upgrade_oecd.py — Add OECD data ingest (quarterly GDP, monthly CPI, unemployment)
for 9 OECD member countries, replacing World Bank annual data where available.

Modifies:
  notebooks/01_ingest.ipynb    — new OECD fetch cell
  notebooks/02_transform.ipynb — load + merge oecd_country.parquet
  notebooks/03_model.ipynb     — country scoreboard prefers OECD over IMF
"""

import json
from pathlib import Path

NB_DIR = Path("notebooks")


def code_cell(lines, cell_id="oecd-0000-0000"):
    return {
        "cell_type": "code",
        "execution_count": None,
        "id": cell_id,
        "metadata": {},
        "outputs": [],
        "source": lines,
    }


# ──────────────────────────────────────────────────────────────────────────────
# 01_ingest.ipynb — new OECD cell inserted after IMF cell (index 7)
# ──────────────────────────────────────────────────────────────────────────────

OECD_CELL_LINES = [
    "# --- OECD quarterly/monthly data (primary for 9 OECD member countries) ---\n",
    "# GDP quarterly YoY%, CPI monthly YoY%, unemployment monthly %\n",
    "# ~1 quarter lag vs World Bank 12-24 month lag\n",
    "# Countries: USA, DEU, JPN, GBR, FRA, ITA, CAN, AUS, KOR\n",
    "# China, India, Brazil: not full OECD members; keep World Bank / IMF for those.\n",
    "\n",
    "import requests, io\n",
    "\n",
    "OECD_MEMBERS = {\n",
    '    "USA": "United States",\n',
    '    "DEU": "Germany",\n',
    '    "JPN": "Japan",\n',
    '    "GBR": "United Kingdom",\n',
    '    "FRA": "France",\n',
    '    "ITA": "Italy",\n',
    '    "CAN": "Canada",\n',
    '    "AUS": "Australia",\n',
    '    "KOR": "South Korea",\n',
    "}\n",
    '_CODES = "+".join(OECD_MEMBERS.keys())\n',
    '_BASE  = "https://sdmx.oecd.org/public/rest/data"\n',
    "\n",
    "def _oecd_csv(url):\n",
    "    # Fetch OECD SDMX CSV; return tidy DataFrame with cols: code, period, value\n",
    "    r = requests.get(url, timeout=45, headers={'Accept': 'text/csv'})\n",
    "    r.raise_for_status()\n",
    "    df = pd.read_csv(io.StringIO(r.text))\n",
    "    df.columns = [c.strip().lower().replace(' ', '_') for c in df.columns]\n",
    "    area_col = next((c for c in df.columns if 'ref_area' in c or 'reference_area' in c), None)\n",
    "    time_col = next((c for c in df.columns if 'time_period' in c), None)\n",
    "    val_col  = next((c for c in df.columns if 'obs_value' in c or 'observation_value' in c), None)\n",
    "    if not all([area_col, time_col, val_col]):\n",
    "        raise ValueError(f'Unexpected CSV columns: {df.columns.tolist()}')\n",
    "    return df[[area_col, time_col, val_col]].rename(\n",
    "        columns={area_col: 'code', time_col: 'period', val_col: 'value'}\n",
    "    ).dropna(subset=['value'])\n",
    "\n",
    "print('Fetching OECD data for 9 member countries...')\n",
    "oecd_frames = []\n",
    "\n",
    "# 1. GDP growth — quarterly YoY %\n",
    "try:\n",
    "    gdp_url = (\n",
    "        f'{_BASE}/OECD.SDD.NAD,DSD_NAMAIN1@DF_QNA_EXPENDITURE_NATIONAL,1.0/'\n",
    "        f'Q.{_CODES}.B1GQ..YA_GY'\n",
    "        f'?startPeriod=2020-Q1&format=csv'\n",
    "    )\n",
    "    gdp = _oecd_csv(gdp_url)\n",
    "    gdp['indicator'] = 'oecd_gdp_yoy'\n",
    "    def _q_to_date(p):\n",
    "        yr, q = p.split('-Q')\n",
    "        month = int(q) * 3\n",
    "        return pd.Timestamp(year=int(yr), month=month, day=1) + pd.offsets.MonthEnd(0)\n",
    "    gdp['date'] = gdp['period'].apply(_q_to_date)\n",
    "    oecd_frames.append(gdp[['code', 'date', 'indicator', 'value']])\n",
    "    print(f'  GDP:          {len(gdp)} rows, latest {gdp[\"period\"].max()}')\n",
    "except Exception as e:\n",
    "    print(f'  GDP fetch failed: {e}')\n",
    "\n",
    "# 2. CPI inflation — monthly YoY %\n",
    "try:\n",
    "    cpi_url = (\n",
    "        f'{_BASE}/OECD.SDD.TPS,DSD_PRICES@DF_PRICES_T,1.0/'\n",
    "        f'M.{_CODES}.CPI.PA.._T.N.GY'\n",
    "        f'?startPeriod=2020-01&format=csv'\n",
    "    )\n",
    "    cpi = _oecd_csv(cpi_url)\n",
    "    cpi['indicator'] = 'oecd_cpi_yoy'\n",
    "    cpi['date'] = pd.to_datetime(cpi['period']) + pd.offsets.MonthEnd(0)\n",
    "    oecd_frames.append(cpi[['code', 'date', 'indicator', 'value']])\n",
    "    print(f'  CPI:          {len(cpi)} rows, latest {cpi[\"period\"].max()}')\n",
    "except Exception as e:\n",
    "    print(f'  CPI fetch failed: {e}')\n",
    "\n",
    "# 3. Unemployment — monthly % of labour force\n",
    "try:\n",
    "    unemp_url = (\n",
    "        f'{_BASE}/OECD.SDD.TPS,DSD_LFS@DF_IALFS_INDIC,1.0/'\n",
    "        f'M.{_CODES}..._T..UNE_LF.PT_LF_TOTEM'\n",
    "        f'?startPeriod=2020-01&format=csv'\n",
    "    )\n",
    "    unemp = _oecd_csv(unemp_url)\n",
    "    unemp['indicator'] = 'oecd_unemployment'\n",
    "    unemp['date'] = pd.to_datetime(unemp['period']) + pd.offsets.MonthEnd(0)\n",
    "    oecd_frames.append(unemp[['code', 'date', 'indicator', 'value']])\n",
    "    print(f'  Unemployment: {len(unemp)} rows, latest {unemp[\"period\"].max()}')\n",
    "except Exception as e:\n",
    "    print(f'  Unemployment fetch failed: {e}')\n",
    "\n",
    "if oecd_frames:\n",
    "    oecd_long = pd.concat(oecd_frames, ignore_index=True)\n",
    "    oecd_long['country'] = oecd_long['code'].map(OECD_MEMBERS)\n",
    "    oecd_wide = oecd_long.pivot_table(\n",
    "        index=['country', 'date'], columns='indicator', values='value', aggfunc='last'\n",
    "    ).rename_axis(columns=None).sort_index()\n",
    "    out = RAW_DIR / 'oecd_country.parquet'\n",
    "    oecd_wide.to_parquet(out)\n",
    "    print(f'OECD saved: {oecd_wide.shape} -> {out}')\n",
    "    us = oecd_wide.xs('United States', level='country') if 'United States' in oecd_wide.index.get_level_values('country') else oecd_wide\n",
    "    print(us.tail(4))\n",
    "else:\n",
    "    print('WARNING: No OECD data fetched — oecd_country.parquet not created')\n",
]

# ──────────────────────────────────────────────────────────────────────────────
# 02_transform.ipynb patched cell sources
# ──────────────────────────────────────────────────────────────────────────────

TRANSFORM_LOAD = """\
# --- Load raw parquets ---
fred_raw = pd.read_parquet(RAW_DIR / "fred_series.parquet")

try:
    wb_raw = pd.read_parquet(RAW_DIR / "worldbank.parquet")
    print("WB:    ", wb_raw.shape, "| index:", wb_raw.index.names)
except FileNotFoundError:
    print("WARNING: worldbank.parquet not found — World Bank data will be skipped")
    wb_raw = pd.DataFrame()

try:
    imf_raw = pd.read_parquet(RAW_DIR / "imf_weo.parquet")
    print("IMF:   ", imf_raw.shape, "| columns:", imf_raw.columns.tolist())
except FileNotFoundError:
    print("WARNING: imf_weo.parquet not found — IMF data will be skipped")
    imf_raw = pd.DataFrame()

try:
    oecd_raw = pd.read_parquet(RAW_DIR / "oecd_country.parquet")
    print("OECD:  ", oecd_raw.shape, "| latest:", oecd_raw.index.get_level_values("date").max().date())
except FileNotFoundError:
    print("NOTE: oecd_country.parquet not found — run 01_ingest first; OECD data skipped")
    oecd_raw = pd.DataFrame()

print("FRED:  ", fred_raw.shape, "| index:", fred_raw.index.dtype)
"""

TRANSFORM_MERGE = """\
# --- World Bank: normalize to annual datetime index ---
if not wb_raw.empty:
    wb = wb_raw.reset_index()
    wb["date"] = pd.to_datetime(wb["date"].astype(str).str[:4], format="%Y")
    wb = wb.set_index(["country", "date"]).sort_index()
    wb.columns = ["wb_" + c for c in wb.columns]
    print("WB shape:", wb.shape)
else:
    wb = pd.DataFrame()
    print("World Bank data unavailable — skipping")

# --- IMF WEO: pivot to wide format ---
if not imf_raw.empty:
    imf = imf_raw.copy()
    imf["date"] = pd.to_datetime(imf["TIME_PERIOD"].astype(str), format="%Y")
    imf_wide = imf.pivot_table(
        index=["REF_AREA_LABEL", "date"],
        columns="CONCEPT_CODE",
        values="OBS_VALUE",
        aggfunc="first"
    ).rename_axis(index={"REF_AREA_LABEL": "country"})
    imf_wide.columns = ["imf_" + c for c in imf_wide.columns]
    print("IMF wide shape:", imf_wide.shape)
else:
    imf_wide = pd.DataFrame()
    print("IMF data unavailable — skipping")

# --- OECD: already wide (country, date) with oecd_* columns ---
oecd = oecd_raw.copy() if not oecd_raw.empty else pd.DataFrame()
if not oecd.empty:
    print("OECD wide shape:", oecd.shape)

# --- Merge WB + IMF + OECD into global panel ---
frames = [f for f in [wb, imf_wide, oecd] if not f.empty]
if not frames:
    global_panel = pd.DataFrame()
    print("WARNING: No global panel data — country scoreboard will be empty")
else:
    global_panel = frames[0]
    for other in frames[1:]:
        global_panel = global_panel.join(other, how="outer")
    global_panel = global_panel.sort_index().ffill(limit=2)
    print("Global panel shape:", global_panel.shape)
    if "United States" in global_panel.index.get_level_values("country"):
        us_rows = global_panel.xs("United States", level="country")
        show_cols = [c for c in global_panel.columns if c.startswith("oecd_") or c in ("imf_NGDP_RPCH", "imf_PCPIPCH", "imf_LUR")]
        print(us_rows[show_cols].dropna(how="all").tail(5))
"""

# ──────────────────────────────────────────────────────────────────────────────
# 03_model.ipynb — updated country scoreboard cell
# ──────────────────────────────────────────────────────────────────────────────

SCOREBOARD = """\
# --- Country Scoreboard ---
try:
    stocks = pd.read_parquet(RAW_DIR / "stock_indices.parquet")
    print(f"Stock indices loaded: {stocks.shape}")
except FileNotFoundError:
    stocks = pd.DataFrame(columns=["stock_ytd_pct"])
    print("Warning: stock_indices.parquet not found — re-run 01_ingest to populate stock data")

try:
    policy = pd.read_parquet(RAW_DIR / "policy_rates.parquet")
    print(f"Policy rates loaded: {policy.shape}")
except FileNotFoundError:
    policy = pd.DataFrame(columns=["policy_rate"])
    print("Warning: policy_rates.parquet not found — re-run 01_ingest to populate policy rates")

SCOREBOARD_COUNTRIES = [
    "United States", "China", "Germany", "Japan", "United Kingdom",
    "France", "India", "Brazil", "Canada", "Australia", "South Korea", "Italy",
]

# OECD members get quarterly GDP and monthly CPI/unemployment from oecd_* columns
OECD_MEMBERS = {
    "United States", "Germany", "Japan", "United Kingdom",
    "France", "Italy", "Canada", "Australia", "South Korea",
}

def _latest(col, country):
    try:
        vals = panel[col].xs(country, level="country").dropna().sort_index()
        return round(float(vals.iloc[-1]), 1) if len(vals) else None
    except KeyError:
        return None

def _prev(col, country):
    try:
        vals = panel[col].xs(country, level="country").dropna().sort_index()
        return round(float(vals.iloc[-2]), 1) if len(vals) >= 2 else None
    except KeyError:
        return None

def _coalesce(country, *cols):
    # Return first non-None value from the ordered list of panel columns
    for col in cols:
        v = _latest(col, country)
        if v is not None:
            return v
    return None

rows = []
for country in SCOREBOARD_COUNTRIES:
    row = {"country": country}
    is_oecd = country in OECD_MEMBERS

    if is_oecd:
        # GDP: OECD quarterly actuals (most recent); fall back to IMF annual forecast
        row["gdp_actual"]   = _coalesce(country, "oecd_gdp_yoy", "imf_NGDP_RPCH")
        row["gdp_forecast"] = row["gdp_actual"]   # OECD provides actuals only
        row["inflation"]    = _coalesce(country, "oecd_cpi_yoy", "imf_PCPIPCH")
        row["unemployment"] = _coalesce(country, "oecd_unemployment", "imf_LUR")
        row["data_source"]  = "OECD"
    else:
        row["gdp_forecast"] = _latest("imf_NGDP_RPCH", country)
        row["gdp_actual"]   = _prev(  "imf_NGDP_RPCH", country)
        row["inflation"]    = _latest("imf_PCPIPCH",    country)
        row["unemployment"] = _latest("imf_LUR",        country)
        row["data_source"]  = "IMF WEO"

    row["current_account"] = _latest("imf_BCA_NGDPD",   country)
    row["govt_debt"]       = _latest("imf_GGXWDG_NGDP", country)
    row["policy_rate"]     = float(policy.loc[country, "policy_rate"]) if country in policy.index else None
    row["stock_ytd"]       = float(stocks.loc[country, "stock_ytd_pct"]) if country in stocks.index else None
    rows.append(row)

scoreboard = pd.DataFrame(rows).set_index("country")
scoreboard.to_parquet(OUTPUTS_DIR / "country_scoreboard.parquet")
print("Country scoreboard saved:")
print(scoreboard.to_string())
"""


# ──────────────────────────────────────────────────────────────────────────────
# Apply patches
# ──────────────────────────────────────────────────────────────────────────────

def replace_cell_by_id(cells, cell_id, new_source):
    for cell in cells:
        if cell.get("id") == cell_id:
            cell["source"] = [new_source]
            cell["outputs"] = []
            return True
    return False


def insert_after_index(cells, idx, new_cell):
    cells.insert(idx + 1, new_cell)


def patch(path, ops):
    with open(path, encoding="utf-8") as f:
        nb = json.load(f)
    for op in ops:
        if op["action"] == "replace_by_id":
            ok = replace_cell_by_id(nb["cells"], op["id"], op["source"])
            print(f"  {'OK' if ok else 'NOT FOUND'} — replaced cell id={op['id']}")
        elif op["action"] == "insert_after":
            insert_after_index(nb["cells"], op["index"], op["cell"])
            print(f"  OK — inserted cell after index {op['index']}")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(nb, f, indent=1, ensure_ascii=False)
    print(f"  Saved {path}")


print("=== Patching 01_ingest.ipynb ===")
patch(NB_DIR / "01_ingest.ipynb", [
    {
        "action": "insert_after",
        "index": 7,
        "cell": code_cell(OECD_CELL_LINES, "oecd-ingest-cell-0001"),
    }
])

print("\n=== Patching 02_transform.ipynb ===")
patch(NB_DIR / "02_transform.ipynb", [
    {"action": "replace_by_id", "id": "b2c3d4e5-0002-0002-0002-000000000004", "source": TRANSFORM_LOAD},
    {"action": "replace_by_id", "id": "b2c3d4e5-0002-0002-0002-000000000006", "source": TRANSFORM_MERGE},
])

print("\n=== Patching 03_model.ipynb ===")
patch(NB_DIR / "03_model.ipynb", [
    {"action": "replace_by_id", "id": "92a4db01", "source": SCOREBOARD},
])

print("\nDone. Run notebooks in order: 01_ingest -> 02_transform -> 03_model")
