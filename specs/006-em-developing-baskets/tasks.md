# Tasks: Emerging Markets & Developing Economies Baskets

**Feature:** `006-em-developing-baskets`
**Input**: Design documents from `specs/006-em-developing-baskets/` (plan.md, spec.md, data-model.md)
**Organization**: Tasks are grouped by user story (P1–P3 from spec.md) to enable independent implementation and testing of each.
**Code root**: `notebooks/03_model.ipynb` (data), `notebooks/04_render.ipynb` + `scripts/monthly_newsletter.py` (presentation)

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files/cells, no dependencies)
- **[Story]**: Which user story this task belongs to (US1–US3)

---

## Phase 1: Setup (Shared Infrastructure)

- [x] T001 Add `EM_COUNTRIES` and `DEVELOPING_COUNTRIES` country lists to `notebooks/03_model.ipynb`'s Country Scoreboard cell, per data-model.md
- [x] T002 [P] Document the basket disjointness rule (China/India/Brazil/South Korea stay in Major, not duplicated into EM) as a code comment next to the new lists, per spec.md Edge Cases
- [x] T003 [P] Add the staleness threshold table (data-model.md) as a `STALENESS_THRESHOLDS` dict keyed by `(basket, metric_type)` in `notebooks/03_model.ipynb`

**Checkpoint**: Country lists and threshold config exist; nothing consumes them yet.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared as-of/staleness computation every user story needs

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T004 Extend `_latest()`/`_coalesce()`/`_prev()` helpers in `notebooks/03_model.ipynb` to also return the source vintage/reference date (`as_of`) alongside the value (FR-004). Also added a `_lookup()` helper for the country-indexed `policy`/`stock` frames, and extended `01_ingest.ipynb` cells 9–10 to capture `policy_rate_as_of` / `stock_ytd_as_of` at ingest (the frames previously discarded the observation date). Reads of a pre-change parquet degrade gracefully (value shown, as_of `None`).
- [x] T005 Implement `_is_stale(as_of, basket, metric_type) -> bool | None` — returns `None` when the value/as_of is null, else compares `as_of` against `STALENESS_THRESHOLDS` (data-model.md "Not Available vs Stale" rule). `NOW` reference is the workflow-injected `run_date`, else current UTC.
- [x] T006 Wire `{metric}_as_of` and `{metric}_stale` columns into the scoreboard row-building loop for every metric (incl. `gdp_forecast` — see data-model.md impl note), applied uniformly to all rows regardless of basket
- [x] T007 Add a `basket` column to every row (`"Major"` for existing `SCOREBOARD_COUNTRIES`, set explicitly rather than inferred)

**Checkpoint**: `country_scoreboard.parquet` now carries basket + as_of + stale for the existing 12 countries; no new countries yet, no render changes yet.

---

## Phase 3: User Story 3 — Know Which Numbers Are Current vs. Lagging (Priority: P1) 🎯 MVP mechanism

**Goal**: Prove the as-of/staleness display end-to-end on the existing Major basket before extending to new baskets — lowest-risk place to validate the rendering mechanism.

**Independent Test**: Feed the render step a row with a known-old `as_of` for one metric and a known-fresh one for another; confirm the stale metric is visually flagged and the fresh one isn't (spec.md Independent Test, US3).

### Implementation for User Story 3

- [x] T008 [US3] In `notebooks/04_render.ipynb`, add an as-of/staleness badge (muted `sb-stale` cell + `†` marker + `title` tooltip with the as-of date) to each scoreboard cell, reading the new `{metric}_as_of`/`{metric}_stale` columns; added a legend line under the table
- [x] T009 [US3] Render explicit `N/A` text (not a blank cell) when a metric value is null, distinct visually from the stale badge (FR-006) — `sb-na` cell with "not reported" tooltip
- [x] T010 [US3] Apply the same badge/N/A treatment in `scripts/monthly_newsletter.py`'s scoreboard section; also hardened the dashboard-scrape fallback (`_parse_scoreboard_from_dashboard`) to strip the `†` marker so values still parse
- [x] T011 [US3] Validated via a fixture harness that execs the REAL `03_model` cell 8 + `04_render` cell 9 source against a panel/policy/stock fixture with known fresh/stale/missing values: **108 dashboard cells rendered, 0 blank** across all 12 Major countries; stale/fresh/N-A classifications all correct; newsletter section likewise 0 blank. NOTE: a full *live* pipeline run (01_ingest → 04_render) needs FRED/IMF/OECD API keys + network and happens on the GitHub Actions weekly run — the fixture harness exercises the exact production cell source, which is the strongest check available locally. The spec's US3 Independent Test (fixture-driven) is fully satisfied; the live GH Actions run is the final confirmation.

**Checkpoint**: US3 fully functional and testable on the existing basket. New baskets (US1, US2) can now reuse this mechanism directly.

---

## Phase 4: User Story 1 — Compare Emerging Market Economies at a Glance (Priority: P1)

**Goal**: A new "Emerging Markets" table with the same metrics and staleness treatment as Major.

**Independent Test**: Run the pipeline and confirm an "Emerging Markets" table appears with the same metric columns, populated for `EM_COUNTRIES`, independent of whether Developing exists yet (spec.md Independent Test, US1).

### Implementation for User Story 1

- [x] T012 [US1] Extend the scoreboard-building loop in `notebooks/03_model.ipynb` to also iterate `EM_COUNTRIES`, tagging each row `basket="Emerging Markets"`, via the IMF WEO path. **Required upstream plumbing:** the scoreboard consumes only `imf_*`/`oecd_*` columns, and IMF ingest (`01_ingest.ipynb` cell 7) was filtered to 10 majors — so EM (and Developing) IMF areas were added to the fetch (`WEO_AREAS`), and `02_transform.ipynb` cell 7 now renames IMF's area labels to the scoreboard's display names (Türkiye→Turkey, Poland/Taiwan/Egypt, +Korea). Developing IMF data is plumbed too (Phase 5 is now render-only).
- [x] T013 [US1] Confirmed `policy_rate` has no EM coverage (`policy_rates.parquet` holds only the 12 majors) → resolves to `None`/`N/A` via `_lookup`, no error. Verified in end-to-end run.
- [x] T014 [US1] Confirmed `stock_ytd` has no EM coverage (`stock_indices.parquet` holds only the 12 majors) → `N/A`, no error.
- [x] T015 [US1] `notebooks/04_render.ipynb` cell 9 refactored to render one titled `<table>` per basket present (Major, Emerging Markets, [Developing]) with a per-basket heading, reusing the T008/T009 badge/N-A cell rendering.
- [x] T016 [US1] `scripts/monthly_newsletter.py` `country_snapshot_html` refactored to the same per-basket tables; narrative sections (`global_picture_text`, `scoreboard_summary_text`, country-in-focus) scoped to the Major basket so EM rows don't reshape existing prose.
- [x] T017 [US1] Validated end-to-end against **live IMF WEO data** (local harness exec-ing the real ingest→transform→model→render cell source): 8 EM countries all populated (SC-003), dashboard + newsletter each render 2 basket tables / 180 cells / **0 blank** (SC-002), zero future-dated vintages (T026).

**Checkpoint**: US1 + US3 both independently functional — Emerging Markets basket renders with full staleness treatment.

---

## Phase 5: User Story 2 — Compare Developing/Frontier Economies at a Glance (Priority: P2)

**Goal**: A "Developing Economies" table, same pattern as US1, expected to show more stale/N-A cells given sparser source coverage.

**Independent Test**: Run the pipeline and confirm a "Developing Economies" table appears with the same columns and staleness treatment as EM (spec.md Independent Test, US2).

### Implementation for User Story 2

- [ ] T018 [US2] [P] Extend the scoreboard-building loop to also iterate `DEVELOPING_COUNTRIES`, tagging `basket="Developing"` — same code path as T012, different list
- [ ] T019 [US2] [P] Add the "Developing Economies" table section to `docs/index.html` (same mechanism as T015)
- [ ] T020 [US2] [P] Add the "Developing Economies" section to the newsletter template (same mechanism as T016)
- [ ] T021 [US2] Validate SC-003 (≥6 Developing countries) — expect a higher proportion of `stale`/`N/A` cells than EM or Major; confirm this renders correctly rather than looking broken (spec.md US2 Acceptance Scenario 2)

**Checkpoint**: All three user stories independently functional — three-basket scoreboard with consistent staleness treatment.

---

## Phase 6: Polish & Validation

- [ ] T022 Validate SC-004: diff `country_scoreboard.parquet`'s original 9 value columns for the 12 existing Major countries, pre- vs. post-feature — confirm zero value changes (only new `as_of`/`stale`/`basket` columns added)
- [ ] T023 Handle the Edge Case where an entire basket has zero fresh rows in a given week — confirm the basket still renders (all flagged stale) rather than being silently hidden, per spec.md Edge Cases
- [ ] T024 [P] Update `specs/001-macro-pipeline/spec.md`'s Country Scoreboard description (currently says "12 major economies") to reflect the three-basket structure
- [ ] T025 Run the full weekly pipeline locally end-to-end (`01_ingest` → `04_render` → newsletter) as a final validation pass before the next scheduled GitHub Actions run
- [x] T026 **(done in the Phase 4 pass)** Fixed the vintage-selection issue the staleness feature exposed in the US3 live run (PR #5, run 30500668322). `_latest`/`_prev` in `notebooks/03_model.ipynb` now cap the candidate vintages at `NOW` (`vals = vals[vals.index <= NOW]`) before selecting, so a future IMF forecast year (e.g. 2031) can never be chosen as an "actual". Verified end-to-end: US GDP now resolves to the 2026 estimate (as-of 2026-01-01), zero future-dated as_of values across the whole scoreboard. The ancient-vintage case (e.g. only-1961-data-available) still selects the most-recent past value and is correctly flagged stale. Original note follows for context: `_latest`/`_prev` on the IMF/WB panel currently pick whatever non-null value exists, which surfaces two problems now that as-of dates are visible: (a) **future forecast years** — IMF WEO includes projections out to ~2031, and a 2031 "GDP Actual" renders as *fresh* because its as-of is in the future (`_is_stale` only tests too-OLD, not implausibly-future); (b) **ancient vintages** — when recent years are NaN, `_latest` falls back to decades-old rows (observed: China GDP as-of 1961). Fix in `notebooks/03_model.ipynb`: cap the selected vintage at `NOW` (never pick a future-dated observation as an "actual") and prefer the most-recent *past* vintage; optionally have `_is_stale` treat a future as-of as a data error rather than fresh. Especially important before Phase 4/5 land, since EM/Developing sources are sparser and lag more. This is a pre-existing pipeline behavior the transparency feature made visible — not a regression from US3.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **Foundational (Phase 2)**: Depends on Setup — BLOCKS all user stories
- **User Story 3 (Phase 3)**: Depends on Foundational only — validates the staleness mechanism on data that already exists, no new country data needed
- **User Story 1 (Phase 4)**: Depends on Foundational + US3 (reuses the badge/N-A rendering built there)
- **User Story 2 (Phase 5)**: Depends on Foundational + US3; independent of US1 (different country list, same mechanism) — could run in parallel with Phase 4 by a different session
- **Polish (Phase 6)**: Depends on US1 + US2 + US3 all complete

### Parallel Opportunities

- T002–T003 (Setup) in parallel
- Phase 4 (US1) and Phase 5 (US2) can be built in parallel once Phase 3 (US3) is done — different country lists, same shared mechanism, no file conflicts if done as separate notebook-cell edits
- T018–T020 (US2) in parallel with each other

---

## Implementation Strategy

### MVP First (User Story 3 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 3 — staleness mechanism proven on existing Major basket
4. **STOP and VALIDATE**: T011 — zero blank cells across the existing 12 countries
5. This de-risks the two new baskets: if the staleness display doesn't work cleanly on data we already trust, it's not ready to layer sparser EM/Developing data on top of

### Incremental Delivery

1. Setup + Foundational → schema ready
2. US3 → validate independently on existing data (mechanism proof)
3. US1 → validate against SC-003 (needs US3's rendering mechanism)
4. US2 → validate against SC-003 (needs US3; can run parallel to US1)
5. Polish → SC-004 regression check + docs update
