"""
monthly_newsletter.py — Global Macro Pulse newsletter generator.

Reads data/outputs/ and produces:
  docs/newsletter/YYYY-MM.html  — this month's issue
  docs/newsletter/index.html    — updated archive index

Optionally sends via Buttondown if BUTTONDOWN_API_KEY is set.

Usage:
    python scripts/monthly_newsletter.py --issue 1 [--send]
"""

import argparse
import json
import os
from datetime import datetime, date
from pathlib import Path

import pandas as pd
import requests

# ---------------------------------------------------------------------------
# Paths / constants
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data" / "outputs"
NL_DIR = ROOT / "docs" / "newsletter"

DASHBOARD_URL = "https://trevmon28.github.io/macro-dashboard/"
PAPER_URL = "https://trevmon28.github.io/macro-dashboard/paper.html"
NEWSLETTER_URL = "https://trevmon28.github.io/macro-dashboard/newsletter/"
BUTTONDOWN_API = "https://api.buttondown.email/v1/emails"

COUNTRIES = [
    "United States", "China", "Germany", "Japan", "United Kingdom",
    "France", "India", "Brazil", "Canada", "Australia", "South Korea", "Italy",
]
REGIME_LABELS = {-1: "Deflationary", 0: "Normal", 1: "Elevated", 2: "High Inflation"}

CSS = """
body { margin:0; padding:0; background:#f3f4f6; font-family:Georgia,serif; color:#1f2937; }
.wrapper { max-width:620px; margin:32px auto; background:#fff; border-radius:8px; overflow:hidden; box-shadow:0 2px 8px rgba(0,0,0,.08); }
.hdr { background:#0f172a; color:#f8fafc; padding:36px 32px 24px; }
.hdr h1 { margin:0 0 4px; font-size:22px; letter-spacing:.12em; text-transform:uppercase; font-weight:700; }
.hdr .issue { margin:0 0 12px; font-size:13px; color:#94a3b8; letter-spacing:.05em; }
.hdr .tagline { margin:0; font-size:14px; color:#cbd5e1; font-style:italic; line-height:1.5; }
.sec { padding:28px 32px; border-bottom:1px solid #e5e7eb; }
.sec:last-child { border-bottom:none; }
.sec h2 { margin:0 0 16px; font-size:12px; font-weight:700; letter-spacing:.1em; text-transform:uppercase; color:#6b7280; }
.sec p { margin:0 0 12px; font-size:15px; line-height:1.7; }
.sec p:last-child { margin-bottom:0; }
.grid { display:grid; grid-template-columns:1fr 1fr; gap:12px; margin-bottom:20px; }
.card { background:#f8fafc; border:1px solid #e2e8f0; border-radius:6px; padding:12px 14px; }
.card .lbl { font-size:11px; color:#64748b; letter-spacing:.06em; text-transform:uppercase; margin-bottom:4px; }
.card .val { font-size:20px; font-weight:700; color:#0f172a; font-family:'Courier New',monospace; }
.card .delta { font-size:12px; color:#64748b; margin-top:2px; }
.movers ul { margin:8px 0 0; padding-left:20px; }
.movers li { font-size:15px; line-height:1.7; margin-bottom:6px; }
.spotlight { background:#f0f9ff; border-left:4px solid #0284c7; padding:16px 20px; border-radius:0 6px 6px 0; }
.links { display:flex; gap:16px; flex-wrap:wrap; }
.links a { color:#0284c7; text-decoration:none; font-size:14px; }
.links a:hover { text-decoration:underline; }
.footer { background:#f8fafc; padding:20px 32px; font-size:12px; color:#9ca3af; line-height:1.6; text-align:center; }
.footer a { color:#9ca3af; }
"""


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_data():
    snap = json.loads((DATA_DIR / "latest_snapshot.json").read_text(encoding="utf-8"))
    ind = pd.read_parquet(DATA_DIR / "indicators.parquet")
    ind.index = pd.to_datetime(ind.index)
    sb = pd.read_parquet(DATA_DIR / "country_scoreboard.parquet")
    return snap, ind, sb


# ---------------------------------------------------------------------------
# Calculations
# ---------------------------------------------------------------------------

def mom_delta(ind: pd.DataFrame, col: str):
    if col not in ind.columns:
        return None
    s = ind[col].dropna()
    return round(float(s.iloc[-1] - s.iloc[-2]), 4) if len(s) >= 2 else None


def biggest_movers(sb: pd.DataFrame, col: str = "stock_ytd", n: int = 2):
    valid = sb[col].dropna()
    if valid.empty:
        return [], []
    return list(valid.nlargest(n).items()), list(valid.nsmallest(n).items())


def _sign(v):
    return "+" if v >= 0 else ""


def delta_str(v, pct=False):
    if v is None:
        return "—"
    if pct:
        return f"{_sign(v)}{v * 100:.1f}pp"
    return f"{_sign(v)}{v:.3f}"


# ---------------------------------------------------------------------------
# Narrative builders
# ---------------------------------------------------------------------------

def yield_curve_text(snap, ind):
    s2 = snap.get("yield_spread_10y2y", 0)
    s3 = snap.get("yield_spread_10y3m", 0)
    inv = snap.get("inversion_signal", 0)
    mo = snap.get("months_inverted", 0)
    d2 = mom_delta(ind, "yield_spread_10y2y")
    d3 = mom_delta(ind, "yield_spread_10y3m")
    status = f"inverted for {mo} consecutive months" if inv else "not inverted"
    text = (
        f"The 10y–2y Treasury spread stands at <strong>{s2:+.2f}%</strong> "
        f"and the 10y–3m spread at <strong>{s3:+.2f}%</strong> — "
        f"the yield curve is currently <strong>{status}</strong>."
    )
    if d2 is not None:
        text += f" The 10y–2y spread moved <strong>{int(d2 * 100):+d} bps</strong> month-over-month"
    if d3 is not None:
        text += f", while the 10y–3m spread shifted <strong>{int(d3 * 100):+d} bps</strong>."
    else:
        text += "."
    return text


def recession_text(snap, ind):
    prob = snap.get("recession_prob", 0)
    pct = round(prob * 100, 1)
    d = mom_delta(ind, "recession_prob")
    level = "low" if pct < 15 else ("moderate" if pct < 30 else ("elevated" if pct < 50 else "high"))
    text = (
        f"The Estrella-Mishkin 12-month recession probability stands at "
        f"<strong>{pct}%</strong> — a <strong>{level}</strong> reading."
    )
    if d is not None:
        direction = "rose" if d > 0 else "fell"
        text += f" This {direction} <strong>{abs(d * 100):.1f} percentage points</strong> from the prior month."
    text += " Readings above 30% are historically associated with elevated recession risk over the following year."
    return text


def inflation_text(snap):
    code = snap.get("inflation_regime", 0)
    regime = REGIME_LABELS.get(code, "Normal")
    z = snap.get("inflation_zscore", 0)
    if z > 1.5:
        ctx = "significantly above its 20-year historical average"
    elif z > 0.5:
        ctx = "above its 20-year historical average"
    elif z < -0.5:
        ctx = "below its 20-year historical average"
    else:
        ctx = "near its 20-year historical average"
    tail = (
        "Elevated inflation has historically compressed equity multiples and extended central bank tightening cycles."
        if code >= 1
        else "Normal inflation conditions support stable monetary policy and risk appetite."
    )
    return (
        f"The inflation regime is classified as <strong>{regime}</strong>, "
        f"with a 20-year rolling z-score of <strong>{z:+.2f}</strong> — {ctx}. {tail}"
    )


def risk_text(snap):
    rs = snap.get("risk_score", 0)
    if rs > 0.3:
        label, color = "Risk-On", "#16a34a"
        interp = "Credit spreads are contained, real rates are supportive, and the yield curve is not deeply inverted — conditions that historically favor equity and risk assets."
    elif rs < -0.3:
        label, color = "Risk-Off", "#dc2626"
        interp = "Elevated credit spreads, negative real rates, or deep inversion signal financial stress — conditions that historically favor safe havens."
    else:
        label, color = "Neutral", "#d97706"
        interp = "Mixed signals across credit spreads, real rates, and the yield curve leave overall risk posture in a neutral zone."
    return (
        f"The composite risk score is <strong style='color:{color}'>{rs:+.2f} ({label})</strong> "
        f"on a scale of −1 to +1. {interp}"
    )


def model_commentary_text(snap):
    prob = snap.get("recession_prob", 0)
    pct = round(prob * 100, 1)
    s3 = snap.get("yield_spread_10y3m", 0)
    code = snap.get("inflation_regime", 0)
    regime = REGIME_LABELS.get(code, "Normal")
    rec_comment = (
        f"Historically, readings above 30% have preceded recessions with meaningful frequency, "
        f"though false positives occur — particularly when the inversion is brief."
        if pct > 20
        else "Readings below 20% have historically been associated with expansion phases, "
        "though the model has a 12-month lag and should be read alongside other signals."
    )
    inf_comment = (
        f"The current inflation regime ({regime}) is above the historical baseline. "
        "Elevated inflation has historically been associated with tighter monetary conditions "
        "and compressed equity multiples, though the path depends heavily on central bank credibility."
        if code >= 1
        else "Inflation remains near normal levels. This is consistent with an environment where "
        "central banks retain flexibility to ease if growth disappoints, providing a potential backstop for risk assets."
    )
    return (
        f"<p>The Estrella-Mishkin probit model estimates a <strong>{pct}%</strong> probability of recession "
        f"beginning within 12 months, derived from the 10y–3m spread of <strong>{s3:+.2f}%</strong>. {rec_comment}</p>"
        f"<p>{inf_comment}</p>"
    )


def spotlight_text(country, row):
    def _fmt(v, fmt):
        return fmt % v if v is not None and not (isinstance(v, float) and v != v) else None

    parts = []
    gdp = _fmt(row.get("gdp_forecast"), "%.1f%%")
    inf = _fmt(row.get("inflation"), "%.1f%%")
    rate = _fmt(row.get("policy_rate"), "%.2f%%")
    debt = _fmt(row.get("govt_debt"), "%.0f%% of GDP")

    if gdp:
        parts.append(f"GDP growth is forecast at <strong>{gdp}</strong>")
    if inf:
        parts.append(f"CPI inflation runs at <strong>{inf}</strong>")
    if rate:
        parts.append(f"the policy rate is <strong>{rate}</strong>")
    if debt:
        parts.append(f"government debt stands at <strong>{debt}</strong>")

    text = f"{country}: " + ", ".join(parts) + "." if parts else f"Data for {country} is limited this month."
    ytd = row.get("stock_ytd")
    if ytd is not None and ytd == ytd:
        direction = "gained" if ytd >= 0 else "lost"
        text += f" The local equity index has <strong>{direction} {abs(ytd):.1f}%</strong> YTD."
    return text


# ---------------------------------------------------------------------------
# HTML renderer
# ---------------------------------------------------------------------------

def render_html(snap, ind, sb, issue_number, issue_date):
    as_of = snap.get("as_of", str(date.today()))
    month_str = issue_date.strftime("%B %Y")

    rs = snap.get("risk_score", 0)
    risk_label = "Risk-On" if rs > 0.3 else ("Risk-Off" if rs < -0.3 else "Neutral")
    risk_color = "#16a34a" if rs > 0.3 else ("#dc2626" if rs < -0.3 else "#d97706")
    regime = REGIME_LABELS.get(snap.get("inflation_regime", 0), "Normal")
    inv = snap.get("inversion_signal", 0)
    inv_label = "Inverted" if inv else "Normal"
    inv_color = "#dc2626" if inv else "#16a34a"
    rec_pct = round(snap.get("recession_prob", 0) * 100, 1)
    s2 = snap.get("yield_spread_10y2y", 0)

    d_rec = mom_delta(ind, "recession_prob")
    d_s2 = mom_delta(ind, "yield_spread_10y2y")
    d_risk = mom_delta(ind, "risk_score")

    tagline = f"Yield curve {inv_label.lower()} · Recession risk {rec_pct}% · Inflation {regime} · {risk_label}"

    # Country spotlight
    country = COUNTRIES[(issue_number - 1) % 12]
    s_row = sb.loc[country] if country in sb.index else pd.Series(dtype=float)
    s_text = spotlight_text(country, s_row)

    # Biggest movers
    gainers, losers = biggest_movers(sb)
    mover_items = ""
    for c, v in gainers:
        mover_items += f"      <li><strong>{c}</strong> equity {v:+.1f}% YTD — top performer</li>\n"
    for c, v in losers:
        mover_items += f"      <li><strong>{c}</strong> equity {v:+.1f}% YTD — laggard</li>\n"

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Global Macro Pulse — Issue #{issue_number} · {month_str}</title>
<style>{CSS}</style>
</head>
<body>
<div class="wrapper">

  <div class="hdr">
    <h1>Global Macro Pulse</h1>
    <p class="issue">Issue #{issue_number} &nbsp;·&nbsp; {month_str} &nbsp;·&nbsp; Data as of {as_of}</p>
    <p class="tagline">{tagline}</p>
  </div>

  <div class="sec">
    <h2>Regime Snapshot</h2>
    <div class="grid">
      <div class="card">
        <div class="lbl">Yield Curve (10y–2y)</div>
        <div class="val">{s2:+.2f}%</div>
        <div class="delta">MoM: {delta_str(d_s2)} &nbsp;·&nbsp; <span style="color:{inv_color}">{inv_label}</span></div>
      </div>
      <div class="card">
        <div class="lbl">Recession Prob (12m)</div>
        <div class="val">{rec_pct}%</div>
        <div class="delta">MoM: {delta_str(d_rec, pct=True)}</div>
      </div>
      <div class="card">
        <div class="lbl">Inflation Regime</div>
        <div class="val" style="font-size:15px;padding-top:4px">{regime}</div>
        <div class="delta">Z-score: {snap.get("inflation_zscore", 0):+.2f}</div>
      </div>
      <div class="card">
        <div class="lbl">Risk Score</div>
        <div class="val" style="color:{risk_color}">{rs:+.2f}</div>
        <div class="delta"><strong style="color:{risk_color}">{risk_label}</strong> &nbsp;·&nbsp; MoM: {delta_str(d_risk)}</div>
      </div>
    </div>
    <p>{yield_curve_text(snap, ind)}</p>
    <p>{recession_text(snap, ind)}</p>
  </div>

  <div class="sec movers">
    <h2>What Moved This Month</h2>
    <p>{inflation_text(snap)}</p>
    <p>{risk_text(snap)}</p>
    <p>Equity market standouts:</p>
    <ul>
{mover_items}    </ul>
  </div>

  <div class="sec">
    <h2>Model Commentary</h2>
    {model_commentary_text(snap)}
  </div>

  <div class="sec">
    <h2>Country Spotlight — {country}</h2>
    <div class="spotlight">
      <p style="margin:0;font-size:15px;line-height:1.7">{s_text}</p>
    </div>
  </div>

  <div class="sec">
    <h2>Resources</h2>
    <div class="links">
      <a href="{DASHBOARD_URL}">&#8594; Live Dashboard</a>
      <a href="{PAPER_URL}">&#8594; Methodology Paper</a>
      <a href="{NEWSLETTER_URL}">&#8594; Newsletter Archive</a>
    </div>
  </div>

  <div class="footer">
    Global Macro Pulse is generated automatically from public data sources (FRED, World Bank, IMF WEO).<br>
    Not investment advice. &nbsp;·&nbsp; <a href="{NEWSLETTER_URL}">View archive</a>
  </div>

</div>
</body>
</html>"""


# ---------------------------------------------------------------------------
# Archive index
# ---------------------------------------------------------------------------

def update_index(issue_file: Path, issue_number: int, month_str: str, tagline: str):
    index_path = NL_DIR / "index.html"
    new_li = (
        f'      <li><a href="{issue_file.name}">Issue #{issue_number} — {month_str}</a>'
        f' &nbsp;<span style="color:#6b7280;font-size:13px">{tagline}</span></li>'
    )
    if index_path.exists():
        content = index_path.read_text(encoding="utf-8")
        content = content.replace("<!-- ISSUES -->", f"<!-- ISSUES -->\n{new_li}")
        index_path.write_text(content, encoding="utf-8")
    else:
        index_path.write_text(
            f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Global Macro Pulse — Archive</title>
<style>
  body {{ font-family:Georgia,serif; max-width:640px; margin:48px auto; color:#1f2937; padding:0 16px; }}
  h1 {{ font-size:24px; letter-spacing:.08em; text-transform:uppercase; border-bottom:2px solid #0f172a; padding-bottom:12px; }}
  ul {{ list-style:none; padding:0; }}
  li {{ padding:12px 0; border-bottom:1px solid #e5e7eb; font-size:16px; }}
  a {{ color:#0284c7; text-decoration:none; }}
  a:hover {{ text-decoration:underline; }}
  .back {{ font-size:13px; color:#6b7280; margin-top:32px; }}
</style>
</head>
<body>
<h1>Global Macro Pulse</h1>
<p style="color:#6b7280;font-size:14px">Monthly macro newsletter — auto-generated from public data (FRED, World Bank, IMF WEO).</p>
<ul>
<!-- ISSUES -->
{new_li}
</ul>
<p class="back"><a href="../index.html">&larr; Dashboard</a> &nbsp;&middot;&nbsp; <a href="../paper.html">Methodology Paper</a></p>
</body>
</html>""",
            encoding="utf-8",
        )


# ---------------------------------------------------------------------------
# Buttondown send
# ---------------------------------------------------------------------------

def send_email(subject: str, html: str):
    api_key = os.environ.get("BUTTONDOWN_API_KEY", "")
    if not api_key:
        print("BUTTONDOWN_API_KEY not set — skipping email send.")
        return
    resp = requests.post(
        BUTTONDOWN_API,
        headers={"Authorization": f"Token {api_key}"},
        json={"subject": subject, "body": html, "status": "about_to_send"},
        timeout=30,
    )
    if resp.status_code in (200, 201):
        print(f"Email queued via Buttondown: {resp.json().get('id')}")
    else:
        print(f"Buttondown error {resp.status_code}: {resp.text}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Generate Global Macro Pulse newsletter")
    parser.add_argument("--issue", type=int, default=1, help="Issue number (default: 1)")
    parser.add_argument("--send", action="store_true", help="Send via Buttondown API")
    args = parser.parse_args()

    snap, ind, sb = load_data()

    as_of = snap.get("as_of", str(date.today()))
    issue_date = datetime.strptime(as_of, "%Y-%m-%d")
    month_str = issue_date.strftime("%B %Y")
    ym = issue_date.strftime("%Y-%m")

    NL_DIR.mkdir(parents=True, exist_ok=True)

    html = render_html(snap, ind, sb, args.issue, issue_date)

    out_path = NL_DIR / f"{ym}.html"
    out_path.write_text(html, encoding="utf-8")
    print(f"Written: {out_path}")

    rs = snap.get("risk_score", 0)
    risk_label = "Risk-On" if rs > 0.3 else ("Risk-Off" if rs < -0.3 else "Neutral")
    rec_pct = round(snap.get("recession_prob", 0) * 100, 1)
    tagline = f"Recession {rec_pct}% · {risk_label}"
    update_index(out_path, args.issue, month_str, tagline)
    print(f"Index updated: {NL_DIR / 'index.html'}")

    if args.send:
        subject = f"Global Macro Pulse — {month_str}"
        send_email(subject, html)


if __name__ == "__main__":
    main()
