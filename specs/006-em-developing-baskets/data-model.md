# Data Model: Emerging Markets & Developing Economies Baskets

**Feature:** `006-em-developing-baskets` | **Spec**: [spec.md](spec.md) | **Plan**: [plan.md](plan.md)

---

## Basket Country Lists

### Major Economies (existing, unchanged)

`United States, China, Germany, Japan, United Kingdom, France, India, Brazil, Canada, Australia, South Korea, Italy` (12 — from `SCOREBOARD_COUNTRIES` in `notebooks/03_model.ipynb`)

### Emerging Markets (new — `EM_COUNTRIES`)

`Mexico, Indonesia, Turkey, South Africa, Poland, Thailand, Saudi Arabia, Taiwan` (8)

### Developing / Frontier Economies (new — `DEVELOPING_COUNTRIES`)

`Nigeria, Vietnam, Bangladesh, Kenya, Egypt, Pakistan` (6)

**Disjointness rule**: no country appears in more than one list. China, India, Brazil, and South Korea are commonly classified as "emerging markets" by index providers (e.g. MSCI) but stay in the Major basket here because they're already covered by the existing scoreboard (spec.md FR-001, Edge Cases).

---

## Scoreboard Row Schema Extension

Current `country_scoreboard.parquet` row (per country): `gdp_actual, gdp_forecast, inflation, unemployment, data_source, current_account, govt_debt, policy_rate, stock_ytd`.

**New columns**:

| Column | Type | Description |
|--------|------|--------------|
| `basket` | str | One of `"Major"`, `"Emerging Markets"`, `"Developing"` |
| `{metric}_as_of` | date or null | Vintage/reference date of the underlying data point, one per existing metric column (`gdp_actual_as_of`, `inflation_as_of`, `current_account_as_of`, `govt_debt_as_of`, `policy_rate_as_of`, `stock_ytd_as_of`) |
| `{metric}_stale` | bool or null | `true` if `{metric}_as_of` is older than that basket's threshold for that metric type; `null` if the metric itself is null (no double-signal — "not available" is its own state, not "stale") |

The metrics carrying an as_of/stale pair are: `gdp_actual`, `gdp_forecast`, `inflation`, `unemployment`, `current_account`, `govt_debt`, `policy_rate`, `stock_ytd`.

**Implementation note (2026-07-29):** `gdp_forecast` gets its *own* `as_of`/`stale` pair rather than inheriting `gdp_actual`'s. On the OECD path forecast and actual are the same value/date so it's moot, but on the IMF path `gdp_forecast` is the latest annual estimate and `gdp_actual` is the prior year — genuinely different reference dates — so giving each its own vintage is more honest than sharing one. (This supersedes the original "inherits" note here.)

**Source of `as_of` for `policy_rate` / `stock_ytd`:** these two come from country-indexed frames (`policy_rates.parquet`, `stock_indices.parquet`) that historically stored only the value. `01_ingest.ipynb` cells 9–10 were extended to also capture the observation date (`stock_ytd_as_of` = last close date; `policy_rate_as_of` = last FRED observation date). The model layer degrades gracefully if it reads a pre-change parquet lacking those columns: the value still renders, with as_of/stale left `None` (shown as "as-of date unavailable", never falsely flagged stale).

---

## Staleness Thresholds

| Basket | GDP / Current Account / Govt Debt (quarterly-or-slower) | Inflation / Unemployment / Policy Rate (monthly-or-faster) |
|--------|-----------------------------------------------------------|---------------------------------------------------------------|
| Major | > 6 months | > 2 months |
| Emerging Markets | > 9 months | > 4 months |
| Developing | > 12 months | > 6 months |

`stock_ytd_as_of` uses a fixed 5-trading-day threshold across all baskets (it's a daily series wherever it exists at all).

---

## "Not Available" vs. "Stale"

- **Not available**: the metric is `null` for that country in the source data. Renders as literal `N/A` text, no as-of badge. (FR-006)
- **Stale**: the metric has a real value and a real `as_of` date, but that date is older than the threshold above. Renders the value with a visible staleness badge/footnote. (FR-005)
- A metric is never both — `{metric}_stale` is `null` whenever the metric itself is `null`, so downstream rendering code checks `value is None` before checking `stale`.
