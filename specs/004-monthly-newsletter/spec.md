# Feature Specification: Monthly Macro Newsletter

**Feature:** `004-monthly-newsletter`
**Author:** Trevor Monroe
**Date:** July 2026
**Status:** Planned

---

## Overview

A monthly auto-generated newsletter that narrates the current macro regime — summarizing yield curve status, recession probability movement, inflation regime, risk score, and country scoreboard highlights. The newsletter is produced by a Python script reading `data/outputs/` after the weekly pipeline run, then published as:
1. A web version hosted at `https://trevmon28.github.io/macro-dashboard/newsletter/YYYY-MM.html`
2. An email distribution (platform TBD — Substack, Buttondown, or SendGrid)

The newsletter is generated once per month (first Monday), while the dashboard pipeline runs weekly. The monthly generation is a separate GitHub Actions job gated on the month-start condition.

---

## Distribution Channels

| Channel | Platform | Notes |
|---------|----------|-------|
| Web | GitHub Pages | `docs/newsletter/YYYY-MM.html` + index at `docs/newsletter/index.html` |
| Email | Buttondown (`api.buttondown.email/v1/emails`) | API key stored as `BUTTONDOWN_API_KEY` GitHub Actions secret |
| Archive | GitHub Pages | `docs/newsletter/index.html` lists all past issues |

**Platform: Buttondown.** API-first, no subscriber lock-in, free tier covers up to 100 subscribers. POST rendered HTML to `https://api.buttondown.email/v1/emails` with `Authorization: Token <BUTTONDOWN_API_KEY>`.

---

## Newsletter Structure

### Header
```
GLOBAL MACRO PULSE
Issue #N · Month YYYY
"[One-sentence macro regime summary]"
```

### Section 1 — Regime Snapshot (lead)
- Current yield curve status: spread values, inversion flag, months inverted
- Recession probability: current % + change from prior month + historical context
- Inflation regime label + current CPI YoY
- Risk score: current value + interpretation (Risk-On / Neutral / Risk-Off)

### Section 2 — What Moved This Month
- Biggest movers in the country scoreboard (equity YTD, policy rate changes)
- Notable FRED series moves (e.g., spread narrowed X bps, HY credit spread widened)
- Written in short narrative paragraphs (~3–4 sentences per bullet)

### Section 3 — Model Commentary
- One paragraph: what the recession probability signal implies for the next 12 months given current spread levels
- One paragraph: inflation regime context — is this consistent with historical turning points?

### Section 4 — Country Spotlight (rotating)
- Each month highlights one of the 12 scoreboard economies
- 3–4 sentences: GDP trajectory, inflation, policy rate, equity performance YTD

### Section 5 — Dashboard Link + Archive
- Link to `https://trevmon28.github.io/macro-dashboard/`
- Link to methodology paper: `../paper.html`
- Link to newsletter archive: `index.html`

### Footer
```
Global Macro Pulse is generated automatically from public data sources (FRED, World Bank, IMF WEO).
Not investment advice. | Unsubscribe | View in browser
```

---

## Data Sources (pipeline outputs consumed)

| File | Used for |
|------|---------|
| `data/outputs/latest_snapshot.json` | Current indicator values, as_of date, regime labels |
| `data/outputs/indicators.parquet` | Month-over-month change calculation for recession prob, spreads |
| `data/outputs/country_scoreboard.parquet` | Country section, biggest movers |

---

## Generation Logic

```
monthly_newsletter.py
  ├── load latest_snapshot.json
  ├── load indicators.parquet → compute MoM delta for key series
  ├── load country_scoreboard.parquet → identify top/bottom equity YTD movers
  ├── select rotating country spotlight (issue_number % 12 → country index)
  ├── render HTML template → docs/newsletter/YYYY-MM.html
  ├── update docs/newsletter/index.html (prepend new issue)
  └── (Phase 3) POST to email platform API
```

---

## GitHub Actions Integration

Add a job `monthly-newsletter` to `.github/workflows/weekly_pipeline.yml`:

```yaml
monthly-newsletter:
  needs: deploy          # runs after main pipeline completes
  if: github.event_name == 'schedule' && startsWith(github.event.schedule, '0 6 * * 1') && ...
  # Gate condition: only run on the first Monday of the month
  # (check: day-of-month <= 7)
```

Alternatively, add a separate `monthly_newsletter.yml` workflow with `cron: '0 8 1-7 * 1'` (first Monday of each month at 08:00 UTC, after the main pipeline at 06:00 UTC).

---

## Functional Requirements

### FR-001: Auto-generated from pipeline outputs
Newsletter content is derived entirely from `data/outputs/` — no manual editing required to publish each month.

### FR-002: Rotating country spotlight
Country spotlight cycles through all 12 scoreboard economies over 12 months, driven by `issue_number % 12`.

### FR-003: Month-over-month delta for key indicators
Recession probability, 10y–2y spread, and risk score must show current value + MoM change (pulled from `indicators.parquet`).

### FR-004: Web archive
`docs/newsletter/index.html` lists all past issues in reverse chronological order with issue date and one-line regime summary.

### FR-005: Email delivery (Phase 3)
On first publish, email is delivered to subscriber list via chosen platform API. Requires API key stored as GitHub Actions secret.

### FR-006: Plain-language narrative
Numeric values are translated into plain-language sentences (e.g., "Recession probability rose to 42%, the highest reading since March 2023, as the 10y–3m spread deepened its inversion to −87 bps.").

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Generation script | `scripts/monthly_newsletter.py` (Python) |
| HTML templating | Python f-strings or Jinja2 |
| Styling | Embedded CSS (email-safe: inline styles for email version, stylesheet for web version) |
| Data reading | `pandas`, `json` |
| Email delivery | Buttondown API (`POST /v1/emails`, `Authorization: Token`) |
| Hosting | GitHub Pages (`docs/newsletter/`) |
| Scheduling | GitHub Actions `cron: '0 8 1-7 * 1'` (first Monday ≤ day 7) |

---

## Open Questions

1. **Email platform:** ~~Decided — Buttondown.~~ API key goes in `BUTTONDOWN_API_KEY` GitHub Actions secret.
2. **Narrative generation:** Pure template logic (deterministic) or use Claude API to write the narrative paragraphs from the data? A Claude-generated draft would be more readable; a template is more predictable.
3. **Issue numbering:** Start at Issue #1 (July 2026)? Or backfill with historical snapshots?
4. **Unsubscribe compliance:** If email goes to more than a test list, CAN-SPAM / GDPR unsubscribe link required — email platform handles this automatically.
