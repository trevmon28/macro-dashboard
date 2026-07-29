# Implementation Plan: Emerging Markets & Developing Economies Baskets

**Feature:** `006-em-developing-baskets` | **Date**: 2026-07-29 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/006-em-developing-baskets/spec.md`

---

## Summary

Extend the existing country scoreboard (built in `notebooks/03_model.ipynb`, rendered in `docs/index.html` and `scripts/monthly_newsletter.py`) with two new baskets — Emerging Markets and Developing/Frontier Economies — reusing the existing World Bank / IMF WEO / FRED sources and the existing OECD-vs-IMF-fallback (`_coalesce`) pattern. The scoreboard row shape gains a `basket` label, an `as_of` date per metric, and a `stale` flag per metric, computed against a per-basket staleness threshold. All three baskets (including the existing major-economy one) get the same as-of/staleness display.

---

## Technical Context

**Language/Version**: Python 3.11+ (existing `macro_env`), same notebook pipeline (`01_ingest.ipynb` → `02_transform.ipynb` → `03_model.ipynb` → `04_render.ipynb`)

**Primary Dependencies**: `wbdata`, `imf-reader`, `fredapi` (all already in use) — no new dependencies

**Storage**: Extends existing `data/outputs/country_scoreboard.parquet`; no new storage layer

**Testing**: Spot-check pattern consistent with existing pipeline (no formal pytest suite exists for the notebooks today) — a smoke check that every rendered cell has either a value+as-of or an explicit "not available" state (SC-002)

**Target Platform**: Same as existing pipeline — runs via GitHub Actions `weekly_pipeline.yml`, output published to GitHub Pages

**Project Type**: Data pipeline + static HTML/newsletter rendering (extension of existing feature, not a new system)

**Performance Goals**: No material change to existing pipeline runtime (~2-7 min observed); two more World Bank/IMF WEO country batches is not expected to be a bottleneck

**Constraints**: Must not alter existing major-economy basket's data values (SC-004) — only additive as-of/staleness display on top of it

**Scale/Scope**: +8 EM countries, +6 Developing countries (see data-model.md), same 7 metrics per country as today

---

## Constitution Check

*macro-dashboard has no formal constitution. Adopting the same working guardrails used for Ecliptic Works ([specs/005](../005-ecliptic-works-fx/plan.md)):*

| Principle | This Feature's Application | Status |
|-----------|----------------------------|--------|
| Freshness transparency | Every metric carries `as_of` + `stale`; no value presented without it | Adopted |
| Graceful degradation | Missing data renders "not available", never blank/zero/forward-filled (FR-006, FR-007) | Adopted |
| Schema-first contracts | Scoreboard row schema extension defined below before notebook/render changes | Adopted |
| Read-only separation | New baskets reuse existing ingest data; no changes to `01_ingest.ipynb` sources | Adopted |

No constitution violations.

---

## Project Structure

### Documentation (this feature)

```text
specs/006-em-developing-baskets/
├── plan.md              # This file
├── data-model.md         # Basket country lists, schema extension, staleness thresholds
└── tasks.md              # /speckit-tasks output
```

### Code changes (repository root)

```text
notebooks/03_model.ipynb          # Extend Country Scoreboard cell: add EM_COUNTRIES,
                                   # DEVELOPING_COUNTRIES lists, basket label, as_of + stale
                                   # columns per metric, applied to ALL three baskets
notebooks/04_render.ipynb         # Render three basket tables into docs/index.html instead
                                   # of one; add as_of/staleness display (badge or footnote)
scripts/monthly_newsletter.py     # Same three-basket rendering + staleness display in the
                                   # newsletter HTML template
```

**Structure Decision**: No new top-level modules or packages — this is an in-place extension of the existing `03_model.ipynb` → `04_render.ipynb` → `monthly_newsletter.py` chain, consistent with how the original 12-country scoreboard was built. A `data-model.md` is included (unlike a typical small change) because the row-schema extension (as_of/stale columns) is shared across three render call sites and needs to be pinned down once.

---

## Phase 0: Research — Complete

**Key decisions**:

| Decision | Choice |
|----------|--------|
| EM country list | Mexico, Indonesia, Turkey, South Africa, Poland, Thailand, Saudi Arabia, Taiwan (8) — disjoint from existing 12; existing scoreboard's China/India/Brazil/South Korea stay in the major-economy basket, not duplicated into EM |
| Developing country list | Nigeria, Vietnam, Bangladesh, Kenya, Egypt, Pakistan (6) |
| As-of date source | IMF WEO reference year (annual) / World Bank indicator date; FRED policy-rate observation date; stock data's own last-trade date |
| Staleness thresholds | Major: >6 months stale; EM: >9 months stale; Developing: >12 months stale (see data-model.md rationale) |
| Missing-data display | Literal "N/A" cell text + no as-of badge, distinct from a stale-but-present value |
| Basket overlap rule | A country belongs to exactly one basket; classification is a fixed list in code, not derived from a live IMF/World Bank classification API (Edge Case in spec.md) |

Rationale for thresholds: the existing major-economy basket already runs on a mix of monthly (OECD members) and quarterly/annual (China/India/Brazil via IMF WEO fallback) cadence, so 6 months covers one missed OECD monthly release without false-flagging. EM economies typically report GDP/current-account quarterly with a 1–2 quarter lag even in IMF WEO's own vintage; 9 months gives headroom for a missed quarter without constant stale-flagging noise. Developing/frontier economies frequently only get annual IMF WEO estimates with 12+ month lag; 12 months is the threshold below which a reader should not yet be alarmed, but any older figure clearly needs a flag.

---

## Phase 1: Design — Complete

### Data Flow

```
World Bank (wbdata) ──────────────┐
IMF WEO (imf-reader) ─────────────┼── country_scoreboard.parquet (+ basket, as_of, stale cols)
FRED policy rates ─────────────────┤              │
stock_indices.parquet ────────────┘              │
                                                    ├── docs/index.html (3 basket tables)
                                                    └── newsletter HTML (3 basket tables)
```

### Key Invariants

1. **Every value has provenance**: no metric renders without either (`value`, `as_of`, `stale`) or an explicit "not available" marker — no third state.
2. **Basket membership is static**: country→basket mapping lives in code as a fixed list (`EM_COUNTRIES`, `DEVELOPING_COUNTRIES`), not computed from a live classification source, so a country never silently moves baskets week to week.
3. **Existing basket values are untouched**: the major-economy basket's `gdp_actual`/`inflation`/etc. columns keep identical values pre- and post-feature; only `as_of`/`stale` columns are additive (SC-004).
4. **No forward-fill**: a missing metric for a given week stays missing (renders "N/A") rather than carrying forward a prior week's value under a new as-of date.

### Artifacts generated (Phase 1)

- [data-model.md](data-model.md) — basket country lists, scoreboard row schema extension, staleness threshold table

---

## Complexity Tracking

> No constitution violations requiring justification.
