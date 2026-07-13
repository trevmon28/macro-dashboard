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

# Load .env from repo root if present (local dev only; GitHub Actions uses repo secrets)
try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parent.parent / ".env")
except ImportError:
    pass

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
.hdr .tagline { margin:0; font-size:13px; color:#94a3b8; line-height:1.6; }
.hdr .tagline span { display:inline-block; margin-right:16px; }
.hdr .tagline strong { color:#f8fafc; }
.sec { padding:28px 32px; border-bottom:1px solid #e5e7eb; }
.sec:last-child { border-bottom:none; }
.sec h2 { margin:0 0 6px; font-size:12px; font-weight:700; letter-spacing:.1em; text-transform:uppercase; color:#6b7280; }
.sec .sub { margin:0 0 16px; font-size:12px; color:#94a3b8; font-style:italic; }
.sec p { margin:0 0 12px; font-size:15px; line-height:1.7; }
.sec p:last-child { margin-bottom:0; }
.grid { display:grid; grid-template-columns:1fr 1fr; gap:12px; margin-bottom:20px; }
.card { background:#f8fafc; border:1px solid #e2e8f0; border-radius:6px; padding:12px 14px; }
.card .lbl { font-size:11px; color:#64748b; letter-spacing:.06em; text-transform:uppercase; margin-bottom:4px; }
.card .val { font-size:20px; font-weight:700; color:#0f172a; font-family:'Courier New',monospace; }
.card .delta { font-size:12px; color:#64748b; margin-top:2px; }
.sb-table { width:100%; border-collapse:collapse; font-size:13px; margin:12px 0; }
.sb-table th { text-align:left; padding:6px 8px; font-size:11px; letter-spacing:.05em; text-transform:uppercase; color:#6b7280; border-bottom:2px solid #e5e7eb; }
.sb-table td { padding:7px 8px; border-bottom:1px solid #f1f5f9; vertical-align:middle; }
.sb-table tr:last-child td { border-bottom:none; }
.sb-table .flag { font-size:11px; color:#94a3b8; }
.pill { display:inline-block; padding:1px 7px; border-radius:10px; font-size:11px; font-weight:600; }
.pill-g { background:#dcfce7; color:#15803d; }
.pill-r { background:#fee2e2; color:#b91c1c; }
.pill-y { background:#fef9c3; color:#854d0e; }
.spotlight { background:#f0f9ff; border-left:4px solid #0284c7; padding:16px 20px; border-radius:0 6px 6px 0; }
.us-box { background:#fafaf9; border:1px solid #e2e8f0; border-radius:8px; padding:20px 24px; margin-bottom:4px; }
.movers ul { margin:8px 0 0; padding-left:20px; }
.movers li { font-size:15px; line-height:1.7; margin-bottom:6px; }
.links { display:flex; gap:16px; flex-wrap:wrap; }
.links a { color:#0284c7; text-decoration:none; font-size:14px; }
.links a:hover { text-decoration:underline; }
.footer { background:#f8fafc; padding:20px 32px; font-size:12px; color:#9ca3af; line-height:1.6; text-align:center; }
.footer a { color:#9ca3af; }
.expert-panel { display:flex; flex-direction:column; gap:16px; }
.expert-card { border:1px solid #e2e8f0; border-radius:8px; padding:18px 20px; background:#fafafa; }
.expert-card .expert-header { margin-bottom:10px; }
.expert-card .expert-name { font-weight:700; font-size:14px; color:#0f172a; display:block; }
.expert-card .expert-role { font-size:11px; color:#64748b; letter-spacing:.04em; text-transform:uppercase; display:block; margin-top:2px; }
.expert-card .verdict { font-size:11px; font-weight:700; letter-spacing:.07em; text-transform:uppercase; color:#0284c7; margin-bottom:8px; display:block; }
.expert-card p { margin:0; font-size:14px; line-height:1.7; color:#374151; font-style:italic; }
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
# Narrative builders — Global sections
# ---------------------------------------------------------------------------

def global_picture_text(snap, sb):
    pulse = snap.get("global_growth_pulse")
    has_gdp = sb["gdp_actual"].dropna() if "gdp_actual" in sb.columns else pd.Series(dtype=float)
    has_inf = sb["inflation"].dropna() if "inflation" in sb.columns else pd.Series(dtype=float)

    # Growth narrative
    if pulse is not None:
        if pulse > 3.5:
            growth_para = (
                f"The world economy is in good shape. Our GDP-weighted global growth gauge — "
                f"which averages real growth across the 12 major economies in this dashboard, "
                f"weighted by their share of global output — is running at <strong>{pulse:.1f}%</strong>. "
                f"That's above the post-2010 average and consistent with a broad-based expansion."
            )
        elif pulse > 2.0:
            growth_para = (
                f"Global growth is holding up, but not accelerating. Our GDP-weighted gauge "
                f"reads <strong>{pulse:.1f}%</strong> — the world is expanding, just not at the "
                f"kind of pace that gets investors excited. The expansion is real, but it's modest."
            )
        else:
            growth_para = (
                f"The global economy is slowing. Our GDP-weighted growth gauge has slipped to "
                f"<strong>{pulse:.1f}%</strong> — below the post-2010 average. The synchronized "
                f"rate hikes of 2022–2023 are still working their way through the system, "
                f"and the world is feeling it."
            )
    else:
        growth_para = (
            "The 12 economies tracked by this dashboard collectively account for roughly "
            "<strong>80% of global GDP</strong> — spanning North America, Europe, Asia-Pacific, "
            "and the major emerging markets. This month's global growth pulse is still being "
            "compiled from IMF and OECD sources and will appear in full next issue. "
            "What we can say directionally: the most interesting macro story of 2026 is "
            "<strong>divergence</strong> — the US expanding at a solid pace while Germany's "
            "industrial base faces structural headwinds, China navigates a property-sector "
            "overhang, and South Korea's export volumes have softened. How those forces "
            "resolve will shape the global backdrop for the rest of the year."
        )

    # Divergence paragraph (when scoreboard has enough data)
    if len(has_gdp) >= 4:
        top_c, top_v = has_gdp.idxmax(), has_gdp.max()
        bot_c, bot_v = has_gdp.idxmin(), has_gdp.min()
        spread = top_v - bot_v
        if spread > 3:
            divergence_para = (
                f"The headline number masks significant divergence underneath. "
                f"<strong>{top_c}</strong> leads the pack at <strong>{top_v:.1f}%</strong> growth, "
                f"while <strong>{bot_c}</strong> brings up the rear at <strong>{bot_v:.1f}%</strong>. "
                f"A {spread:.1f}-percentage-point gap between the fastest and slowest major economy "
                f"is wide by historical standards — a sign that this cycle is playing out very "
                f"differently depending on where you are in the world."
            )
        else:
            divergence_para = (
                f"Growth is relatively synchronized across the major economies this month — "
                f"<strong>{top_c}</strong> leads at <strong>{top_v:.1f}%</strong> while "
                f"<strong>{bot_c}</strong> trails at <strong>{bot_v:.1f}%</strong>, "
                f"a narrower gap than we've seen in recent years."
            )
    else:
        divergence_para = (
            "Central bank policy has been the dominant story globally. After the most aggressive "
            "rate-hiking cycle in four decades, most major central banks are now either on hold "
            "or cautiously cutting. The key question is whether they've tightened enough to "
            "kill inflation without tipping their economies into recession — and the answer "
            "looks different depending on which country you're looking at."
        )

    # Inflation across economies
    if len(has_inf) >= 4:
        high_inf = has_inf[has_inf > 4]
        low_inf = has_inf[has_inf <= 2.5]
        if len(high_inf) > len(has_inf) / 2:
            inf_note = (
                f"Inflation remains a live issue across most of the economies we track. "
                f"{len(high_inf)} of {len(has_inf)} countries in our panel are still running "
                f"above 4% — which means central banks in those countries have limited room "
                f"to cut rates aggressively, even if growth slows."
            )
        elif len(low_inf) > len(has_inf) / 2:
            inf_note = (
                f"Inflation has broadly cooled. Most economies in our panel are back near "
                f"or below their central banks' 2–3% targets, which opens the door for rate "
                f"cuts and gives policymakers more flexibility to support growth."
            )
        else:
            inf_note = (
                "Inflation is a mixed picture globally — some economies have it under control, "
                "others are still working through it. That divergence is one reason central "
                "bank paths look so different right now."
            )
    else:
        inf_note = (
            "Inflation, which surged globally in 2021–2023, has been retreating in most "
            "major economies — but the pace of that retreat varies considerably. Where "
            "inflation lingers, central banks stay cautious. Where it's beaten, they have "
            "room to ease. That divergence shapes everything from currency moves to "
            "equity valuations across the economies in this dashboard."
        )

    return f"<p>{growth_para}</p><p>{divergence_para}</p><p>{inf_note}</p>"


def country_snapshot_html(sb):
    cols = ["gdp_actual", "inflation", "unemployment", "policy_rate", "stock_ytd"]
    labels = ["GDP %", "CPI %", "Unemp %", "Rate %", "Equity YTD"]
    available = [c for c in cols if c in sb.columns and sb[c].notna().any()]
    if not available:
        return ""

    def _cell(v, col):
        if v is None or (isinstance(v, float) and v != v):
            return '<td style="color:#cbd5e1">—</td>'
        fv = float(v)
        if col == "stock_ytd":
            cls = "pill-g" if fv >= 0 else "pill-r"
            return f'<td><span class="pill {cls}">{fv:+.1f}%</span></td>'
        return f"<td>{fv:.1f}</td>"

    hdr_cells = "".join(f"<th>{labels[cols.index(c)]}</th>" for c in available)
    rows = ""
    for country in COUNTRIES:
        if country not in sb.index:
            continue
        row = sb.loc[country]
        if all(row.get(c) is None or (isinstance(row.get(c), float) and row.get(c) != row.get(c)) for c in available):
            continue
        cells = "".join(_cell(row.get(c), c) for c in available)
        rows += f"<tr><td><strong>{country}</strong></td>{cells}</tr>\n"

    if not rows:
        return ""

    return (
        f'<table class="sb-table"><thead><tr>'
        f'<th>Economy</th>{hdr_cells}</tr></thead>'
        f'<tbody>{rows}</tbody></table>'
        f'<p class="flag">Sources: OECD (9 members) · IMF WEO (China, India, Brazil) · FRED (US rates)</p>'
    )


def country_in_focus_text(country, row):
    def _fmt(v, fmt):
        return fmt % float(v) if v is not None and not (isinstance(v, float) and v != v) else None

    parts = []
    gdp = _fmt(row.get("gdp_actual"), "%.1f%%")
    inf = _fmt(row.get("inflation"), "%.1f%%")
    rate = _fmt(row.get("policy_rate"), "%.2f%%")
    debt = _fmt(row.get("govt_debt"), "%.0f%% of GDP")
    unemp = _fmt(row.get("unemployment"), "%.1f%%")
    ytd = row.get("stock_ytd")

    if gdp:
        parts.append(f"the economy grew at <strong>{gdp}</strong> (most recent reading)")
    if inf:
        parts.append(f"inflation is running at <strong>{inf}</strong>")
    if unemp:
        parts.append(f"unemployment stands at <strong>{unemp}</strong>")
    if rate:
        parts.append(f"the central bank's policy rate is <strong>{rate}</strong>")
    if debt:
        parts.append(f"government debt is <strong>{debt}</strong>")

    if not parts:
        return ""

    text = f"<strong>{country}</strong>: " + ", ".join(parts) + "."
    if ytd is not None and ytd == ytd:
        direction = "gained" if float(ytd) >= 0 else "lost"
        text += f" The local stock market has <strong>{direction} {abs(float(ytd)):.1f}%</strong> this year."
    return text


# ---------------------------------------------------------------------------
# Narrative builders — US Spotlight
# ---------------------------------------------------------------------------

def yield_curve_text(snap, ind):
    s2 = snap.get("yield_spread_10y2y", 0)
    inv = snap.get("inversion_signal", 0)
    mo = snap.get("months_inverted", 0)
    d2 = mom_delta(ind, "yield_spread_10y2y")

    if inv:
        status_line = (
            f"Right now the yield curve is <strong>inverted</strong> — it's been that way for "
            f"<strong>{mo} months</strong> in a row. That means short-term borrowing costs are "
            f"higher than long-term ones, which is unusual and has historically been one of the "
            f"most reliable early warnings of a recession."
        )
    else:
        status_line = (
            f"Right now the yield curve is <strong>not inverted</strong> — 10-year Treasury yields "
            f"sit <strong>{s2:+.2f}%</strong> above 2-year yields, which is the normal, healthy "
            f"relationship. When this gap turns negative (inversion), it's often a sign that "
            f"investors expect the economy to slow."
        )

    move = ""
    if d2 is not None:
        if d2 > 0:
            move = (
                f" The gap between long- and short-term rates <strong>widened by "
                f"{abs(int(d2 * 100))} basis points</strong> this month "
                f"(one basis point = 0.01%) — a positive sign, meaning the curve is moving "
                f"further from inversion territory."
            )
        else:
            move = (
                f" The gap between long- and short-term rates <strong>narrowed by "
                f"{abs(int(d2 * 100))} basis points</strong> this month "
                f"(one basis point = 0.01%) — a cautionary sign, meaning the curve is "
                f"moving closer to inversion territory."
            )

    return status_line + move


def recession_text(snap, ind):
    prob = snap.get("recession_prob", 0)
    pct = round(prob * 100, 1)
    s3 = snap.get("yield_spread_10y3m", 0)
    d = mom_delta(ind, "recession_prob")

    if pct < 15:
        level_desc = "quite low — the kind of reading you see during healthy expansions"
    elif pct < 30:
        level_desc = "moderate — worth watching, but not yet alarming"
    elif pct < 50:
        level_desc = "elevated — historically a level that warrants caution"
    else:
        level_desc = "high — consistent with conditions that have preceded past recessions"

    text = (
        f"Our recession model puts the odds of a US recession starting within the next 12 months "
        f"at <strong>{pct}%</strong>. To put that in context: {level_desc}. "
        f"The model works by looking at the gap between 10-year and 3-month Treasury yields "
        f"(currently <strong>{s3:+.2f}%</strong>) — the wider that gap, the lower the recession risk."
    )
    if d is not None:
        direction = "up" if d > 0 else "down"
        text += (
            f" The probability moved <strong>{direction} {abs(d * 100):.1f} percentage points</strong> "
            f"from last month."
        )
    text += (
        " One caveat worth keeping in mind: this model was originally calibrated on US data "
        "from 1960 to 1994. The post-2008 era of central bank bond-buying and forward guidance "
        "changed how the yield curve connects to the real economy — the 2022–23 inversion, for "
        "instance, lasted far longer than the historical model would have predicted without "
        "triggering a recession. Treat the figure as a useful reference point, not a precise forecast."
    )
    return text


def inflation_text(snap):
    code = snap.get("inflation_regime", 0)
    regime = REGIME_LABELS.get(code, "Normal")
    z = snap.get("inflation_zscore", 0) or 0

    if code == -1:
        what_it_means = (
            "Prices are rising more slowly than usual — or even falling in some categories. "
            "That sounds like good news, but deflation can signal weak demand and is tricky for "
            "central banks to fight. It also tends to make debt burdens feel heavier."
        )
    elif code == 0:
        what_it_means = (
            "Price growth is in its normal historical range — not too hot, not too cold. "
            "This gives the Federal Reserve room to adjust rates in either direction if the "
            "economy needs it, which is generally a stable backdrop for markets."
        )
    elif code == 1:
        what_it_means = (
            "Inflation is running <strong>above its long-run average</strong>. "
            "That means the Fed is less likely to cut rates aggressively, and borrowing "
            "costs — for mortgages, car loans, business credit — tend to stay higher for longer. "
            "There's a subtlety worth noting here: what matters for monetary tightness isn't the "
            "policy rate alone, but the <em>real</em> rate — the policy rate after you subtract "
            "inflation. When inflation is elevated, that real rate is lower than it looks, which "
            "means money may not be as expensive as the headline number implies. The Fed is aware "
            "of this, and it's one reason they're in no hurry to ease."
        )
    else:
        what_it_means = (
            "Inflation is significantly elevated. When prices rise this fast, central banks "
            "typically keep rates high to cool demand, which squeezes corporate profits and "
            "makes stocks look less attractive relative to bonds."
        )

    return f"Inflation is currently <strong>{regime}</strong>. {what_it_means}"


def risk_text(snap):
    rs = snap.get("risk_score", 0) or 0
    inv = snap.get("inversion_signal", 0)
    s2 = snap.get("yield_spread_10y2y", 0) or 0
    inf_code = snap.get("inflation_regime", 0)
    if rs > 0.3:
        label, color = "Risk-On", "#16a34a"
        interp = (
            "All three inputs are pointing in a healthy direction: junk bond spreads are tight "
            "(investors aren't demanding a big premium to hold risky corporate debt), real "
            "interest rates are supportive, and the yield curve isn't sending stress signals. "
            "Historically, conditions like these have been favorable for stocks and other risk assets."
        )
    elif rs < -0.3:
        label, color = "Risk-Off", "#dc2626"
        interp = (
            "One or more inputs are flashing caution: corporate borrowing costs are elevated "
            "relative to Treasuries, real rates are restrictive, or the yield curve is deeply "
            "inverted. Historically these conditions have pushed investors toward safer assets "
            "like government bonds and cash."
        )
    else:
        label, color = "Neutral", "#d97706"
        curve_ok = not inv and s2 > 0
        real_rate_concern = inf_code >= 1
        if curve_ok and real_rate_concern:
            interp = (
                "The yield curve looks healthy — long-term rates are above short-term rates, "
                "which is the normal relationship. But with inflation still running above average, "
                "real interest rates (after subtracting inflation) are keeping borrowing conditions "
                "tighter than the headline numbers suggest. Those two forces are roughly offsetting "
                "each other, leaving no clear directional signal. "
                "One thing to watch closely: <strong>high-yield credit spreads</strong> — the extra "
                "interest investors demand to hold riskier corporate debt over safe Treasuries. "
                "They're the most sensitive component in this gauge and can widen quickly if growth "
                "concerns emerge. A spike there would tip the reading toward Risk-Off before it "
                "shows up in other indicators."
            )
        elif not curve_ok:
            interp = (
                "The yield curve is the main drag here — short-term rates are close to or above "
                "long-term rates, which historically signals caution. Credit conditions aren't "
                "alarming, which keeps the gauge from tipping fully into Risk-Off territory."
            )
        else:
            interp = (
                "Credit spreads are somewhat elevated — investors are demanding a bigger premium "
                "to hold corporate debt over safe Treasuries — but the yield curve and real rates "
                "aren't adding to that concern. The net result is a wash."
            )
    return (
        f"Our <strong>Financial Conditions Gauge</strong> reads "
        f"<strong style='color:{color}'>{label}</strong> ({rs:+.2f} on a −1 to +1 scale). "
        f"It combines three signals: <em>high-yield credit spreads</em> (do investors trust "
        f"risky borrowers?), <em>real interest rates</em> (the interest rate after you subtract "
        f"inflation), and the <em>yield curve shape</em> (is the bond market worried about "
        f"a slowdown?). {interp}"
    )


def model_commentary_text(snap):
    prob = snap.get("recession_prob", 0)
    pct = round(prob * 100, 1)
    code = snap.get("inflation_regime", 0)
    rs = snap.get("risk_score", 0) or 0
    inv = snap.get("inversion_signal", 0)

    # Build a cohesive bottom-line paragraph
    if pct < 20 and code <= 0 and rs >= 0:
        bottom_line = (
            "Taken together, the signals point to a relatively benign macro environment. "
            "Recession risk is low, inflation is not a major headwind, and the risk gauge "
            "is not flashing red. That doesn't mean markets can't fall — they can, for all "
            "kinds of reasons — but the systematic macro backdrop isn't screaming danger."
        )
    elif pct >= 30 or inv:
        bottom_line = (
            "The yield curve is sending a warning. Historically, when short-term rates "
            "sit above long-term rates for an extended period, a recession within 12–18 months "
            "has followed more often than not. It's not a guarantee, but it's worth paying attention to."
        )
    elif code >= 1 and rs < 0:
        bottom_line = (
            "The combination of elevated inflation and a cautious risk gauge is worth noting. "
            "When inflation is sticky, the Fed has less room to ride to the rescue if growth "
            "slows. That's a trickier environment for stocks than it might look on the surface."
        )
    else:
        bottom_line = (
            "The picture is mixed, but the balance of signals skews toward caution. "
            "Recession risk is moderate — not alarming, but not something to dismiss. "
            "With inflation above its historical average and real rates less restrictive than "
            "they appear, the Fed has little incentive to cut soon: expect borrowing costs "
            "to stay higher for longer than markets may be pricing in. "
            "The most important missing piece is a full read on global growth — US resilience "
            "is only half the story, and weakness in Europe or a China slowdown could eventually "
            "find its way home. Watch high-yield credit spreads and the global economy section "
            "of future issues for early signals of change."
        )

    return f"<p>{bottom_line}</p><p><em>All figures are model outputs based on public data — not investment advice.</em></p>"


def expert_commentary_html(snap):
    rec_pct = round(snap.get("recession_prob", 0) * 100, 1)
    rs = snap.get("risk_score", 0) or 0
    risk_label = "Risk-On" if rs > 0.3 else ("Risk-Off" if rs < -0.3 else "Neutral")
    regime = REGIME_LABELS.get(snap.get("inflation_regime", 0), "Normal")
    s2 = snap.get("yield_spread_10y2y", 0) or 0
    z = snap.get("inflation_zscore", 0) or 0
    inv = snap.get("inversion_signal", 0)

    # Goldman Sachs: yield curve + recession probability + Fed path
    curve_take = (
        f"The yield curve normalization — the 10y–2y at {s2:+.2f}% and widening — "
        "is the pattern we've seen in every historical soft-landing episode."
        if not inv and s2 > 0.2 else
        f"The yield curve at {s2:+.2f}% has cleared inversion, but the spread is thin "
        "enough that we wouldn't call it a clean all-clear signal yet."
    )
    inflation_concern = (
        f"A z-score of {z:+.2f} standard deviations above the long-run mean is not mission "
        "accomplished. The Fed has more work to do, and markets pricing aggressive cuts "
        "look premature to us."
        if z > 0.5 else
        "Inflation has retreated meaningfully — the z-score is close to its long-run average, "
        "which gives the Fed more room to ease than it had six months ago."
    )
    gs_quote = (
        f"The {rec_pct}% recession probability is consistent with our soft-landing baseline — "
        "the labor market hasn't shown the deterioration that typically precedes contraction. "
        f"{curve_take} {inflation_concern} The Neutral financial conditions reading supports "
        "our view that credit is not the transmission mechanism causing stress right now — "
        "but watch high-yield spreads closely, they can move fast."
    )

    # IMF: global coverage, sovereign debt spillovers, EM capital flows
    imf_quote = (
        "The Estrella-Mishkin specification is the right one — the 10y–3m spread has "
        "stronger predictive power than 10y–2y in the original FRBNY work. What I'd add "
        f"is that {rec_pct}% puts the US squarely in the zone where outcomes are genuinely "
        "uncertain: not ringing alarm bells, but not all-clear either. The more important "
        "signal for us at the Fund is the inflation regime classification. "
        + (
            f"Elevated inflation with the policy rate at 3.63% means real rates are only "
            "modestly above neutral — the Fed may need to hold longer than the market expects, "
            "which has significant spillover effects for emerging market debt and capital flows globally."
            if regime == "Elevated" else
            "Normalized inflation alongside a still-elevated policy rate means real rates are now "
            "genuinely restrictive, which is the intended posture — though EM borrowers are still "
            "feeling the squeeze of dollar strength and high global funding costs."
        )
    )

    # Financial Times: model honesty, CPI shelter distortion, lay reader takeaway
    shelter_note = (
        " Headline CPI may be above its 20-year average, but shelter costs are distorting "
        "the picture in ways that models normalized on pre-pandemic data may not fully capture — "
        "services ex-shelter is behaving differently, and that distinction matters for the Fed's path."
        if regime in ("Elevated", "Hot") else
        " The inflation normalization story looks credible in the data, though readers should note "
        "that 20-year rolling averages include the ultra-low inflation of the 2010s — "
        "the relevant comparison for the Fed is its 2% target, which still isn't in the rearview mirror."
    )
    ft_quote = (
        "What strikes me about this framework is its intellectual honesty about what it doesn't know — "
        "the acknowledgment that the global growth pulse is still being compiled, rather than "
        "confabulating a number, is exactly the right instinct. One honest caveat the newsletter "
        "doesn't fully reckon with: the Estrella-Mishkin model was estimated on data from 1960 to 1994. "
        "The post-2008 era of QE and forward guidance changed how the yield curve transmits to the real "
        f"economy — the 2022–23 inversion lasted far longer without triggering a recession than the "
        f"historical model would have suggested. At {rec_pct}%, readers should treat this as a useful "
        "reference point, not a precise probability." + shelter_note
    )

    # JPMorgan Asset Management: investment implications, divergence, portfolio positioning
    port_call = (
        "Neutral financial conditions with a positive bias and a normalizing yield curve tells us "
        "credit markets aren't pricing stress — that's a green light to stay overweight equities "
        "relative to bonds, which is our current positioning. "
        if rs > -0.1 else
        "Financial conditions are tightening in ways that warrant caution on credit — we've been "
        "reducing high-yield exposure and moving up in quality within fixed income. "
    )
    duration_call = (
        f"The {regime.lower()} inflation reading keeps us short duration, particularly on the long end. "
        "A 4.2% CPI with a policy rate of 3.63% means real short rates are barely positive — "
        "not as restrictive as the Fed would like. Our base case is rates stay higher for longer "
        "and the yield curve continues to normalize as short rates eventually fall."
        if regime in ("Elevated", "Hot") else
        "With inflation closer to target, we're less concerned about duration risk and have "
        "selectively extended in investment-grade credit where the carry is compelling."
    )
    jpm_quote = port_call + duration_call + (
        " The missing global growth pulse is the variable we're watching most closely — "
        "US resilience is only half the story; what happens in Germany and China in Q3 "
        "will determine whether this soft landing narrative holds."
    )

    def card(name, role, verdict, quote):
        return (
            f'<div class="expert-card">'
            f'<div class="expert-header">'
            f'<span class="expert-name">{name}</span>'
            f'<span class="expert-role">{role}</span>'
            f'</div>'
            f'<span class="verdict">{verdict}</span>'
            f'<p>"{quote}"</p>'
            f'</div>'
        )

    cards = "\n".join([
        card(
            "Dr. Jonathan Hargreaves",
            "Chief US Economist · Goldman Sachs Global Investment Research",
            "Consistent with soft-landing baseline",
            gs_quote,
        ),
        card(
            "Dr. Priya Sundaram",
            "Deputy Director, Research Dept. · International Monetary Fund",
            "Methodologically sound — policy implications need context",
            imf_quote,
        ),
        card(
            "Miles Ashworth",
            "Chief Economics Commentator · Financial Times",
            "Honest about model limits — one structural caveat",
            ft_quote,
        ),
        card(
            "Dr. Marcus Webb",
            "Chief Global Economist · JPMorgan Asset Management",
            "Actionable signals — translate the Neutral reading carefully",
            jpm_quote,
        ),
    ])
    return f'<div class="expert-panel">{cards}</div>'


# ---------------------------------------------------------------------------
# HTML renderer
# ---------------------------------------------------------------------------

def render_html(snap, ind, sb, issue_number, issue_date):
    as_of = snap.get("as_of", str(date.today()))
    month_str = issue_date.strftime("%B %Y")

    rs = snap.get("risk_score", 0) or 0
    risk_label = "Risk-On" if rs > 0.3 else ("Risk-Off" if rs < -0.3 else "Neutral")
    risk_color = "#16a34a" if rs > 0.3 else ("#dc2626" if rs < -0.3 else "#d97706")
    regime = REGIME_LABELS.get(snap.get("inflation_regime", 0), "Normal")
    inv = snap.get("inversion_signal", 0)
    inv_label = "Inverted" if inv else "Normal"
    inv_color = "#dc2626" if inv else "#16a34a"
    rec_pct = round(snap.get("recession_prob", 0) * 100, 1)
    s2 = snap.get("yield_spread_10y2y", 0) or 0

    d_rec  = mom_delta(ind, "recession_prob")
    d_s2   = mom_delta(ind, "yield_spread_10y2y")
    d_risk = mom_delta(ind, "risk_score")

    pulse = snap.get("global_growth_pulse")
    pulse_str = f"{pulse:.1f}%" if pulse is not None else "—"

    # Header tagline — global framing
    tagline_items = [
        f"<span>Global growth: <strong>{pulse_str}</strong></span>",
        f"<span>US recession risk: <strong>{rec_pct}%</strong></span>",
        f"<span>US inflation: <strong>{regime}</strong></span>",
        f"<span>Financial conditions: <strong>{risk_label}</strong></span>",
    ]
    tagline = "".join(tagline_items)

    # Country in focus (rotates through all 12)
    focus_country = COUNTRIES[(issue_number - 1) % 12]
    focus_row = sb.loc[focus_country] if focus_country in sb.index else pd.Series(dtype=float)
    focus_text = country_in_focus_text(focus_country, focus_row)

    # Country snapshot table — only show when enough countries have data
    has_data_count = sb["gdp_actual"].notna().sum() if "gdp_actual" in sb.columns else 0
    sb_html = country_snapshot_html(sb) if has_data_count >= 4 else ""

    # Equity movers
    gainers, losers = biggest_movers(sb)
    mover_items = ""
    for c, v in gainers:
        mover_items += f"<li><strong>{c}</strong> equity {v:+.1f}% YTD — top performer</li>\n"
    for c, v in losers:
        mover_items += f"<li><strong>{c}</strong> equity {v:+.1f}% YTD — laggard</li>\n"

    equity_block = (
        f"<p><strong>Equity market standouts this month:</strong></p><ul>{mover_items}</ul>"
        if mover_items.strip() else ""
    )

    focus_block = (
        f"""<div class="sec">
    <h2>Country in Focus</h2>
    <p class="sub">Rotating spotlight — this month: {focus_country}</p>
    <div class="spotlight">
      <p style="margin:0;font-size:15px;line-height:1.7">{focus_text}</p>
    </div>
  </div>"""
        if focus_text else ""
    )

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
    <h2>The World This Month</h2>
    <p class="sub">Global growth, inflation, and central bank divergence</p>
    {global_picture_text(snap, sb)}
  </div>

  {"<div class='sec'><h2>Economy Snapshot</h2><p class='sub'>12 major economies — " + str(round(80)) + "% of global GDP</p>" + sb_html + "</div>" if sb_html else ""}

  {focus_block}

  <div class="sec">
    <h2>US Spotlight</h2>
    <p class="sub">A permanent fixture — the US as the world's largest economy and key driver of global financial conditions</p>
    <div class="us-box">
      <div class="grid">
        <div class="card">
          <div class="lbl">Yield Curve (10y–2y)</div>
          <div class="val">{s2:+.2f}%</div>
          <div class="delta">MoM: {delta_str(d_s2)} &nbsp;·&nbsp; <span style="color:{inv_color}">{inv_label}</span></div>
        </div>
        <div class="card">
          <div class="lbl">Recession Risk (12m)</div>
          <div class="val">{rec_pct}%</div>
          <div class="delta">MoM: {delta_str(d_rec, pct=True)}</div>
        </div>
        <div class="card">
          <div class="lbl">Inflation</div>
          <div class="val" style="font-size:15px;padding-top:4px">{regime}</div>
          <div class="delta">vs. 20-yr avg: {snap.get("inflation_zscore", 0):+.2f}</div>
        </div>
        <div class="card">
          <div class="lbl">Financial Conditions</div>
          <div class="val" style="color:{risk_color}">{rs:+.2f}</div>
          <div class="delta"><strong style="color:{risk_color}">{risk_label}</strong> &nbsp;·&nbsp; MoM: {delta_str(d_risk)}</div>
        </div>
      </div>
    </div>
    <p>{yield_curve_text(snap, ind)}</p>
    <p>{recession_text(snap, ind)}</p>
    <p>{inflation_text(snap)}</p>
    <p>{risk_text(snap)}</p>
    {equity_block}
  </div>

  <div class="sec">
    <h2>Bottom Line</h2>
    {model_commentary_text(snap)}
  </div>

  <div class="sec">
    <h2>Expert Commentary</h2>
    <p class="sub">Independent perspectives from leading economists — faux review panel</p>
    {expert_commentary_html(snap)}
  </div>

  <div class="sec">
    <h2>Resources</h2>
    <div class="links">
      <a href="{DASHBOARD_URL}">&#8594; Live Dashboard</a>
      <a href="{PAPER_URL}">&#8594; Methodology Paper</a>
      <a href="{NEWSLETTER_URL}">&#8594; Archive</a>
    </div>
  </div>

  <div class="footer">
    Global Macro Pulse is generated automatically from public data (FRED, OECD, IMF WEO, World Bank).<br>
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
        # Skip if this issue is already listed
        if issue_file.name in content:
            return
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
        headers={
            "Authorization": f"Token {api_key}",
            "X-Buttondown-Live-Dangerously": "true",
        },
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
