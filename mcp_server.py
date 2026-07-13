"""
mcp_server.py — Global Macro Dashboard MCP Server

Exposes live macro indicators over MCP streamable-HTTP transport.
Run:  MCP_TRANSPORT=http MCP_PORT=9002 python mcp_server.py

Endpoint: https://macro-mcp.trevormonroe.com/mcp
Health:   https://macro-mcp.trevormonroe.com/health
"""

import json
import os
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import uvicorn
from mcp.server.fastmcp import FastMCP

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
PORT      = int(os.environ.get("MCP_PORT", 9002))
TRANSPORT = os.environ.get("MCP_TRANSPORT", "http")
DATA_DIR  = Path(__file__).resolve().parent / "data" / "outputs"
STALE_DAYS = 7

mcp = FastMCP(
    name="macro-dashboard",
    instructions=(
        "Query live global macroeconomic indicators from the Global Macro Dashboard. "
        "Data is refreshed weekly via GitHub Actions. "
        "Use check_pipeline_health first to confirm data freshness."
    ),
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_snapshot() -> dict:
    path = DATA_DIR / "latest_snapshot.json"
    if not path.exists():
        raise FileNotFoundError(
            "latest_snapshot.json not found. Run the pipeline (01_ingest → 03_model)."
        )
    return json.loads(path.read_text(encoding="utf-8"))


def _load_indicators() -> pd.DataFrame:
    path = DATA_DIR / "indicators.parquet"
    if not path.exists():
        raise FileNotFoundError(
            "indicators.parquet not found. Run the pipeline (01_ingest → 03_model)."
        )
    df = pd.read_parquet(path)
    df.index = pd.to_datetime(df.index)
    return df


def _load_scoreboard() -> pd.DataFrame:
    path = DATA_DIR / "country_scoreboard.parquet"
    if not path.exists():
        raise FileNotFoundError(
            "country_scoreboard.parquet not found. Run the pipeline."
        )
    return pd.read_parquet(path)


def _is_stale(snapshot: dict) -> tuple[bool, str]:
    as_of = snapshot.get("as_of", "")
    try:
        snap_date = datetime.fromisoformat(as_of)
        delta = (datetime.now(timezone.utc) - snap_date.replace(tzinfo=timezone.utc)).days
        return delta > STALE_DAYS, f"{delta} days old (as_of {as_of})"
    except Exception:
        return True, f"cannot parse as_of date: {as_of!r}"


def _safe(v, decimals=2):
    if v is None:
        return None
    try:
        f = float(v)
        return None if f != f else round(f, decimals)  # NaN check
    except (TypeError, ValueError):
        return None

# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------

@mcp.tool()
def get_macro_snapshot() -> dict:
    """
    Return the latest snapshot of all US macro indicators:
    yield curve spreads, inversion signal, recession probability (12m ahead),
    inflation regime and z-score, global growth pulse, and risk-on/risk-off score.
    Data is from the most recent weekly pipeline run.
    """
    snap = _load_snapshot()
    stale, age_str = _is_stale(snap)
    regime_map = {-1: "Deflationary", 0: "Normal", 1: "Elevated", 2: "High"}
    risk_val = _safe(snap.get("risk_score"))
    return {
        "as_of": snap.get("as_of"),
        "data_age": age_str,
        "stale": stale,
        "yield_curve": {
            "spread_10y2y_pct": _safe(snap.get("yield_spread_10y2y")),
            "spread_10y3m_pct": _safe(snap.get("yield_spread_10y3m")),
            "inverted": bool(snap.get("inversion_signal")),
            "months_inverted": int(snap.get("months_inverted") or 0),
        },
        "recession_probability_12m": _safe(snap.get("recession_prob"), 3),
        "inflation": {
            "regime": regime_map.get(snap.get("inflation_regime"), "Unknown"),
            "regime_code": snap.get("inflation_regime"),
            "zscore": _safe(snap.get("inflation_zscore")),
        },
        "global_growth_pulse_pct": _safe(snap.get("global_growth_pulse")),
        "risk_score": {
            "value": risk_val,
            "label": (
                "Risk-On" if (risk_val or 0) > 0.3
                else "Risk-Off" if (risk_val or 0) < -0.3
                else "Neutral"
            ),
            "range": "[-1, +1] where +1 = strongest risk-on",
        },
    }


@mcp.tool()
def get_yield_curve(months: int = 120) -> dict:
    """
    Return yield curve spread time series (10y–2y and 10y–3m).
    Includes inversion signal history and current reading.

    Args:
        months: Number of months of history to return (default 120 = 10 years).
    """
    df = _load_indicators()
    months = max(1, min(months, len(df)))
    df = df.tail(months)

    def _series(col):
        if col not in df.columns:
            return []
        s = df[col].dropna()
        return [{"date": str(d.date()), "value": round(float(v), 3)}
                for d, v in zip(s.index, s.values)]

    snap = _load_snapshot()
    return {
        "as_of": snap.get("as_of"),
        "months_returned": months,
        "spread_10y2y": _series("yield_spread_10y2y"),
        "spread_10y3m": _series("yield_spread_10y3m"),
        "inversion_signal": _series("inversion_signal"),
        "current": {
            "spread_10y2y_pct": _safe(snap.get("yield_spread_10y2y")),
            "spread_10y3m_pct": _safe(snap.get("yield_spread_10y3m")),
            "inverted": bool(snap.get("inversion_signal")),
            "months_inverted": int(snap.get("months_inverted") or 0),
        },
    }


@mcp.tool()
def get_recession_probability(months: int = 60) -> dict:
    """
    Return the Estrella-Mishkin recession probability time series (12-month ahead).
    Model: P = Φ(−0.6521 − 0.2375 × spread_10y3m). Based on the 10y–3m Treasury spread.

    Args:
        months: Number of months of history (default 60 = 5 years).
    """
    df = _load_indicators()
    months = max(1, min(months, len(df)))
    df = df.tail(months)

    snap = _load_snapshot()
    current_prob = _safe(snap.get("recession_prob"), 3)

    series = []
    if "recession_prob" in df.columns:
        s = df["recession_prob"].dropna()
        series = [{"date": str(d.date()), "probability": round(float(v), 3)}
                  for d, v in zip(s.index, s.values)]

    return {
        "as_of": snap.get("as_of"),
        "model": "Estrella-Mishkin (1996) probit, 12-month horizon",
        "coefficients": {"alpha": -0.6521, "beta": -0.2375},
        "input": "10-year minus 3-month Treasury spread",
        "months_returned": months,
        "current_probability": current_prob,
        "current_pct": round(current_prob * 100, 1) if current_prob is not None else None,
        "threshold_note": "Readings above 30% are historically elevated",
        "series": series,
    }


@mcp.tool()
def get_country_scoreboard() -> dict:
    """
    Return the 12-economy country scoreboard with GDP growth forecasts, CPI inflation,
    unemployment, current account balance, government debt, central bank policy rates,
    and year-to-date equity index performance.
    """
    sb = _load_scoreboard()
    snap = _load_snapshot()
    countries = []
    for country, row in sb.iterrows():
        entry = {"country": str(country)}
        for col in ["gdp_forecast", "gdp_actual", "inflation", "unemployment",
                    "current_account", "govt_debt", "policy_rate", "stock_ytd"]:
            entry[col] = _safe(row.get(col))
        countries.append(entry)

    return {
        "as_of": snap.get("as_of"),
        "economies": countries,
        "columns": {
            "gdp_forecast": "IMF WEO real GDP growth forecast, %",
            "gdp_actual":   "IMF WEO real GDP growth (prior year), %",
            "inflation":    "IMF WEO CPI inflation, %",
            "unemployment": "IMF WEO unemployment rate, %",
            "current_account": "Current account balance, % GDP",
            "govt_debt":    "Gross government debt, % GDP",
            "policy_rate":  "Central bank policy rate, %",
            "stock_ytd":    "Local equity index YTD return, %",
        },
    }


@mcp.tool()
def check_pipeline_health() -> dict:
    """
    Check whether the macro pipeline data is fresh.
    Reports the as_of date, file modification time, and whether data is stale
    (older than 7 days — the expected weekly pipeline cadence).
    """
    snap_path = DATA_DIR / "latest_snapshot.json"
    if not snap_path.exists():
        return {
            "status": "error",
            "message": "latest_snapshot.json does not exist. Pipeline has not been run.",
            "data_dir": str(DATA_DIR),
        }

    snap = json.loads(snap_path.read_text(encoding="utf-8"))
    mtime = datetime.fromtimestamp(snap_path.stat().st_mtime, tz=timezone.utc)
    stale, age_str = _is_stale(snap)

    output_files = {}
    for fname in ["indicators.parquet", "country_scoreboard.parquet", "latest_snapshot.json"]:
        p = DATA_DIR / fname
        output_files[fname] = {
            "exists": p.exists(),
            "size_kb": round(p.stat().st_size / 1024, 1) if p.exists() else None,
        }

    return {
        "status": "stale" if stale else "ok",
        "as_of": snap.get("as_of"),
        "file_mtime_utc": mtime.isoformat(),
        "age": age_str,
        "stale_threshold_days": STALE_DAYS,
        "output_files": output_files,
        "message": (
            f"Data is stale ({age_str}). Re-run the pipeline."
            if stale
            else f"Data is current ({age_str})."
        ),
    }

# ---------------------------------------------------------------------------
# Health middleware (intercepts GET /health before MCP app)
# ---------------------------------------------------------------------------

class _HealthMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http" and scope.get("path") in ("/", "/health"):
            from starlette.responses import JSONResponse
            response = JSONResponse({"status": "ok", "service": "macro-dashboard"})
            await response(scope, receive, send)
        else:
            await self.app(scope, receive, send)

# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print(f"Starting Macro Dashboard MCP server on port {PORT} (transport={TRANSPORT})")
    if TRANSPORT == "http":
        mcp.settings.host = "0.0.0.0"
        mcp.settings.port = PORT
        mcp.settings.transport_security.enable_dns_rebinding_protection = False
        mcp_app = mcp.streamable_http_app()
        app = _HealthMiddleware(mcp_app)
        uvicorn.run(app, host="0.0.0.0", port=PORT)
    else:
        mcp.run()
