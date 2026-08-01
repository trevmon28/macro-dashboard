# Feature Specification: Emerging Markets & Developing Economies Baskets

**Feature Branch**: `006-em-developing-baskets`

**Created**: 2026-07-29

**Status**: Draft

**Input**: User description: "Add a basket of emerging market economies, and developing economies [to the country scoreboard]. Realizing the data on these economies might be lagging, note that."

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Compare Emerging Market Economies at a Glance (Priority: P1)

A newsletter reader wants to see how major emerging markets (e.g. India, Brazil, Mexico, Indonesia, South Africa, Turkey) are doing on the same footing as the existing major-economy scoreboard — growth, inflation, unemployment, current account, government debt, policy rate, and stock performance — without having to cross-reference a separate source.

**Why this priority**: This is the core ask — an EM basket is the primary new content, and it delivers value the moment it renders anywhere in the dashboard or newsletter, even before the developing-economies basket exists.

**Independent Test**: Can be fully tested by running the pipeline and confirming a new "Emerging Markets" table appears with the same metric columns as the existing scoreboard, populated for a defined EM country list, independent of whether the developing-economies basket is built yet.

**Acceptance Scenarios**:

1. **Given** the pipeline has run for the current week, **When** the dashboard or newsletter renders, **Then** an "Emerging Markets" basket table appears showing GDP growth, inflation, unemployment, current account % GDP, govt debt % GDP, policy rate, and stock YTD (where available) for each EM country in the defined list.
2. **Given** an EM country has no policy-rate coverage in the existing data sources, **When** the basket renders, **Then** that cell shows an explicit "not available" state rather than a blank cell or a stale/incorrect value.
3. **Given** the existing 12-economy scoreboard already includes some countries commonly classified as emerging markets (e.g. China, India, Brazil), **When** the EM basket is defined, **Then** the spec's country list and any overlap with the existing scoreboard is explicit and documented, not left ambiguous.

---

### User Story 2 - Compare Developing/Frontier Economies at a Glance (Priority: P2)

A reader wants visibility into smaller developing/frontier economies (e.g. Nigeria, Vietnam, Bangladesh, Kenya, Egypt) that aren't covered by either the major-economy scoreboard or the EM basket, understanding upfront that this tier's data will be sparser and older than the other two baskets.

**Why this priority**: This is explicitly the second, lower-priority basket in the request — it depends on the same rendering and staleness mechanism built for User Story 1, and delivers standalone value once that mechanism exists.

**Independent Test**: Can be fully tested by running the pipeline and confirming a "Developing Economies" table appears with the same metric columns and staleness treatment as the EM basket, for a defined developing-economy country list.

**Acceptance Scenarios**:

1. **Given** the pipeline has run for the current week, **When** the dashboard or newsletter renders, **Then** a "Developing Economies" basket table appears with the same metric columns as the other two baskets.
2. **Given** a developing economy's most recent GDP figure is more than one full reporting period older than the major-economy basket's typical freshness, **When** that row renders, **Then** the staleness indicator (User Story 3) is visibly present on that cell.

---

### User Story 3 - Know Which Numbers Are Current vs. Lagging (Priority: P1)

A reader looking at any basket (existing major-economy, new EM, or new developing) wants to know, for each figure, roughly how current it is — so a six-month-old current-account number for a frontier economy is never mistaken for as fresh as this week's US inflation print.

**Why this priority**: This is the explicit constraint driving the whole feature request. Without it, adding lower-coverage baskets would silently degrade the dashboard's trustworthiness — a stale EM figure sitting next to a fresh G7 figure with no visual distinction is worse than not showing the EM figure at all. This must ship alongside User Story 1, not as a later polish pass.

**Independent Test**: Can be fully tested by feeding the render step a scoreboard row with a known-old `as_of` date for one metric and a known-fresh date for another, and confirming the stale metric is visually flagged and the fresh one is not — independent of which basket the row belongs to.

**Acceptance Scenarios**:

1. **Given** any scoreboard metric (existing major-economy basket included), **When** the value is rendered, **Then** the reader can see the as-of date or a staleness badge for that value, either inline or on hover/tap.
2. **Given** a metric's as-of date is older than a documented staleness threshold for its basket tier, **When** the value renders, **Then** it is visually distinguished (e.g. muted color, badge, or footnote marker) from metrics within the threshold.
3. **Given** a metric has no data available at all for a given country, **When** the basket renders, **Then** the cell explicitly says so rather than being left blank or showing a zero.
4. **Given** the existing major-economy scoreboard, **When** this feature ships, **Then** its own metrics also carry as-of/staleness display — the standard is applied consistently across all baskets, not just the two new ones.

---

### Edge Cases

- What happens when a country appears in more than one basket definition (e.g. a country reclassified from "developing" to "emerging" between IMF vintages)? The country list per basket must be a fixed, documented set rather than derived dynamically from a classification API, to avoid a country silently jumping baskets week to week.
- How does the dashboard behave when an entire basket (e.g. Developing Economies) has zero countries with fresh-enough data in a given week — does the basket still render (all rows flagged stale) or is it hidden with a note?
- What happens when a country in the EM or developing basket has a currency/stock index that isn't tracked by the existing stock-index data source — does `stock_ytd` simply show "not available," consistent with any other missing metric?
- How is "staleness threshold" defined per basket tier, given that even the existing major-economy basket already has looser (quarterly/annual) cadence for some non-OECD members (China, India, Brazil) via the existing IMF-fallback path?

---

## Requirements *(mandatory)*

### Functional Requirements

**Basket Definition**

- **FR-001**: The system MUST define a fixed, documented Emerging Markets country list and a fixed, documented Developing/Frontier Economies country list, each disjoint from the existing 12-country major-economy scoreboard list and from each other.
- **FR-002**: The system MUST document, in the basket definitions, any country that could reasonably be classified into more than one tier, and record the deliberate choice of which single basket it belongs to.

**Data & Staleness**

- **FR-003**: The system MUST compute the same metric set for EM and Developing baskets as the existing scoreboard: GDP growth, CPI inflation, unemployment, current account % GDP, government debt % GDP, policy rate, and stock YTD, using the existing World Bank / IMF WEO / FRED sources and existing fallback (coalesce) pattern used for non-OECD members today.
- **FR-004**: The system MUST record an as-of date (the vintage/reference date of the underlying data point, not the pipeline run date) for every metric value in every basket, including the existing major-economy basket.
- **FR-005**: The system MUST classify each metric value's freshness against a documented per-tier staleness threshold and expose that classification (fresh vs. stale) alongside the value.
- **FR-006**: The system MUST render an explicit "not available" state for any metric with no data for a given country, distinct from the stale-but-present state.
- **FR-007**: The system MUST NOT silently forward-fill or estimate a missing metric value to avoid a gap in the table.

**Presentation**

- **FR-008**: The dashboard (`docs/index.html`) MUST render the EM and Developing baskets as their own labeled tables/sections, alongside the existing major-economy scoreboard.
- **FR-009**: The weekly newsletter (`scripts/monthly_newsletter.py` output) MUST include the EM and Developing baskets using the same staleness treatment as the dashboard.
- **FR-010**: Every rendered metric value across all three baskets MUST carry a visible or discoverable (e.g. hover/tap) as-of date or staleness badge, per User Story 3.

### Key Entities

- **Basket**: A named, fixed list of countries (Major, Emerging Markets, Developing/Frontier) with an associated staleness threshold policy.
- **Scoreboard Row**: One country's set of metric values for a given pipeline run — extends the existing `country_scoreboard.parquet` row shape with an as-of date and staleness flag per metric, plus a basket label.
- **Staleness Threshold**: A per-basket, per-metric-type policy (e.g. "quarterly GDP is stale beyond 6 months old for Major, beyond 9 months for EM, beyond 12 months for Developing") used to classify a value as fresh or stale.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A reader can identify, for any metric in any basket, whether the figure is current or lagging without leaving the dashboard or newsletter page (no external lookup needed).
- **SC-002**: 100% of rendered metric cells across all three baskets carry either a value with a visible as-of/staleness indicator, or an explicit "not available" state — zero blank cells.
- **SC-003**: The Emerging Markets basket covers at least 8 countries and the Developing Economies basket covers at least 6 countries in the first release.
- **SC-004**: Adding the two new baskets does not *accidentally* change the existing major-economy basket's data values — only adds the as-of/staleness display and the `basket` label to it. **Amended (2026-07-31):** the one intended exception is the T026 vintage-cap fix (see `tasks.md` T026), which deliberately corrects Major values that previously showed a future IMF forecast (e.g. a 2031 projection) as the "actual". Verified by rebuilding the Major basket old-code vs. new-code on the same panel: all 50 value diffs were T026 corrections (every changed cell's pre-fix vintage was future-dated, 2030/2031); zero unexplained changes; the original value columns are all still present (purely additive schema otherwise).

---

## Assumptions

- The existing World Bank / IMF WEO / FRED data sources have adequate (if lower-frequency) coverage for the chosen EM and Developing country lists; no new data source is being added in this feature.
- "As-of date" can be derived from the vintage/reference-period metadata already available from IMF WEO and World Bank API responses (e.g. IMF WEO's reference year/quarter, World Bank's indicator date) — this is a data-availability assumption, not a new external dependency.
- Stock index (`stock_ytd`) coverage will be incomplete for many EM/Developing countries; this is expected and handled via the "not available" state (FR-006), not treated as a blocking gap.
- This feature is presentation- and data-pipeline-only. It has no relationship to, and does not block or depend on, the Ecliptic Works FX strategy project (`specs/005-ecliptic-works-fx`), which explicitly defers any EM-FX work to its own later phase.
- Exact EM and Developing country lists (FR-001) will be finalized during planning (`/speckit-plan`) based on IMF WEO's own EM/Developing classification as a starting reference, adjusted for data availability.
- Staleness thresholds (Key Entities) will be finalized during planning; the reasonable default is materially looser than the major-economy basket's cadence, reflecting these tiers' inherently lower-frequency official statistics.
