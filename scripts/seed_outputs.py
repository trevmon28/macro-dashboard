"""
seed_outputs.py — Pull live FRED data and create data/outputs/ stubs
so the newsletter script can run without the full notebook pipeline.

Run once before monthly_newsletter.py:
    python scripts/seed_outputs.py
"""

import json
import os
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
from fredapi import Fred
from scipy.stats import norm

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parent.parent / ".env")
except ImportError:
    pass

FRED_KEY = os.environ.get("FRED_API_KEY", "")
OUTPUTS = Path(__file__).resolve().parent.parent / "data" / "outputs"
OUTPUTS.mkdir(parents=True, exist_ok=True)

fred = Fred(api_key=FRED_KEY) if FRED_KEY else Fred()

print("Fetching FRED series...")

def fetch(series_id, start="2010-01-01"):
    try:
        s = fred.get_series(series_id, observation_start=start)
        s.index = pd.to_datetime(s.index)
        return s.resample("ME").last()
    except Exception as e:
        print(f"  WARNING: {series_id} failed: {e}")
        return pd.Series(dtype=float)

t10y = fetch("DGS10")
t2y  = fetch("DGS2")
t3m  = fetch("DTB3")
cpi  = fetch("CPIAUCSL")
hy   = fetch("BAMLH0A0HYM2")
tips = fetch("DFII10")

print("Building indicators...")
ind = pd.DataFrame(index=t10y.index)
ind["t10y"] = t10y
ind["t2y"]  = t2y
ind["t3m"]  = t3m
ind["yield_spread_10y2y"] = t10y - t2y
ind["yield_spread_10y3m"] = t10y - t3m
ind["cpi_yoy_pct"] = cpi.pct_change(12) * 100
ind["real_rate_10y"] = t10y - ind["cpi_yoy_pct"]

# Recession probability (Estrella-Mishkin 1996)
spread = ind["yield_spread_10y3m"].dropna()
ind["recession_prob"] = norm.cdf(-0.6521 - 0.2375 * spread)

# Inversion signal
ind["inverted"] = (ind["yield_spread_10y2y"] < 0).astype(int)
consec = 0
months_inv = []
for v in ind["inverted"]:
    if v:
        consec += 1
    else:
        consec = 0
    months_inv.append(consec)
ind["months_inverted"]  = months_inv
ind["inversion_signal"] = (ind["inverted"] == 1).astype(int)

# Inflation z-score & regime
cpi_yoy = ind["cpi_yoy_pct"].dropna()
roll_mean = cpi_yoy.rolling(240, min_periods=60).mean()
roll_std  = cpi_yoy.rolling(240, min_periods=60).std()
ind["inflation_zscore"] = (cpi_yoy - roll_mean) / roll_std

def regime(z):
    if pd.isna(z): return 0
    if z < -0.5: return -1
    if z < 0.5:  return 0
    if z < 1.5:  return 1
    return 2

ind["inflation_regime"] = ind["inflation_zscore"].map(regime)

# Risk score (simplified: credit spread z-score + real rate z-score + curve z-score)
if not hy.empty:
    ind["hy_spread"] = hy
    hy_z   = (hy - hy.rolling(60, min_periods=24).mean()) / hy.rolling(60, min_periods=24).std()
    rr_z   = (ind["real_rate_10y"] - ind["real_rate_10y"].rolling(60, min_periods=24).mean()) / ind["real_rate_10y"].rolling(60, min_periods=24).std()
    cur_z  = ind["inflation_zscore"]
    risk   = (-hy_z * 0.4 + -rr_z * 0.3 + -cur_z * 0.3).clip(-1, 1)
    ind["risk_score"] = risk

# Global growth pulse stub (US GDP proxy)
ind["global_growth_pulse"] = np.nan

ind = ind.ffill(limit=3).dropna(how="all")
ind.to_parquet(OUTPUTS / "indicators.parquet")
print(f"  indicators.parquet saved: {ind.shape}")

# Latest snapshot
latest = ind.dropna(how="all").iloc[-1]

def sf(v, d=2):
    try:
        f = float(v)
        return round(f, d) if not np.isnan(f) else None
    except Exception:
        return None

snapshot = {
    "as_of":               str(latest.name.date()),
    "yield_spread_10y2y":  sf(latest.get("yield_spread_10y2y")),
    "yield_spread_10y3m":  sf(latest.get("yield_spread_10y3m")),
    "inversion_signal":    int(latest.get("inversion_signal", 0)),
    "months_inverted":     int(latest.get("months_inverted", 0)),
    "recession_prob":      sf(latest.get("recession_prob"), 4),
    "inflation_zscore":    sf(latest.get("inflation_zscore")),
    "inflation_regime":    regime(latest.get("inflation_zscore")),
    "global_growth_pulse": sf(latest.get("global_growth_pulse")),
    "risk_score":          sf(latest.get("risk_score")),
}

(OUTPUTS / "latest_snapshot.json").write_text(json.dumps(snapshot, indent=2))
print(f"  latest_snapshot.json saved")
print(json.dumps(snapshot, indent=2))

# Country scoreboard — US populated from FRED; others stub until full pipeline runs
COUNTRIES = [
    "United States", "China", "Germany", "Japan", "United Kingdom",
    "France", "India", "Brazil", "Canada", "Australia", "South Korea", "Italy",
]
sb = pd.DataFrame({
    "gdp_forecast":    [None] * 12,
    "gdp_actual":      [None] * 12,
    "inflation":       [None] * 12,
    "unemployment":    [None] * 12,
    "current_account": [None] * 12,
    "govt_debt":       [None] * 12,
    "policy_rate":     [None] * 12,
    "stock_ytd":       [None] * 12,
    "data_source":     ["—"] * 12,
}, index=pd.Index(COUNTRIES, name="country"))

# Populate US row from FRED data already fetched
us_ff   = fred.get_series("FEDFUNDS").dropna()
us_unemp = fred.get_series("UNRATE").dropna()
us_gdp  = fred.get_series("A191RL1Q225SBEA").dropna()

sb.loc["United States", "policy_rate"]  = round(float(us_ff.iloc[-1]), 2)
sb.loc["United States", "unemployment"] = round(float(us_unemp.iloc[-1]), 1)
sb.loc["United States", "inflation"]    = round(float(ind["cpi_yoy_pct"].dropna().iloc[-1]), 1)
sb.loc["United States", "gdp_actual"]   = round(float(us_gdp.iloc[-1]), 1)
sb.loc["United States", "data_source"]  = "FRED"
print(f"  US row populated from FRED")

sb.to_parquet(OUTPUTS / "country_scoreboard.parquet")
print(f"  country_scoreboard.parquet saved (stub — run full pipeline for real data)")

print("\nDone. You can now run: python scripts/monthly_newsletter.py --issue 1")
