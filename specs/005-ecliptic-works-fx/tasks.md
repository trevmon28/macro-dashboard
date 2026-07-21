# Tasks: Ecliptic Works — Phase 1 FX Strategy

**Feature:** `005-ecliptic-works-fx`
**Input**: Design documents from `specs/005-ecliptic-works-fx/` (plan.md, spec.md, research.md, data-model.md, contracts/signal-schema.md, quickstart.md)
**Tests**: Included — plan.md's Technical Context explicitly calls for pytest unit tests (DSR formula, carry/momentum construction) and integration tests (data pipeline against fixture data).
**Organization**: Tasks are grouped by user story (P1–P5 from spec.md) to enable independent implementation and testing of each.
**Code root**: `C:\Users\trevm\Projects\macro-dashboard\Ecliptic-works\` (existing `macro_env` conda environment — see quickstart.md)

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1–US5)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project scaffolding per plan.md's Project Structure section

- [ ] T001 Create directory structure under `Ecliptic-works/`: `ecliptic/{data,harness,factors,conditioning,execution,backtest,research}/`, `tests/{unit,integration}/`, `configs/`, `data/{raw/fx,raw/macro,processed,signals,trials,execution}/` (data/ gitignored)
- [ ] T002 [P] Create `Ecliptic-works/requirements_ecliptic.txt` with `duka`, `ib_insync`, `pyarrow`, `scipy`, `scikit-learn` and install into `macro_env` (research.md §8)
- [ ] T003 [P] Create `Ecliptic-works/configs/baseline.yml` — default research config (carry bins, momentum window, DSR threshold, embargo days, per research.md decisions table)
- [ ] T004 [P] Add `Ecliptic-works/.gitignore` entry for `data/` (all artifacts, per plan.md Structure Decision)
- [ ] T005 [P] Add `__init__.py` to every `ecliptic/` subpackage and `tests/{unit,integration}/`

**Checkpoint**: Directory scaffold and dependencies ready.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared infrastructure every user story imports — nothing story-specific yet

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T006 Create `Ecliptic-works/ecliptic/paths.py` — central path constants for every `data/` subdirectory listed in data-model.md's Storage Layout
- [ ] T007 [P] Create `Ecliptic-works/ecliptic/io_utils.py` — shared Parquet read/append-write helpers (used by data, harness, and execution layers; enforces plan.md invariant 5 — execution logs are append-only, never mutated)
- [ ] T008 [P] Create `Ecliptic-works/ecliptic/config.py` — loads `configs/baseline.yml` and exposes `FRED_API_KEY`, `ECLIPTIC_PORTFOLIO_SIZE`, `ECLIPTIC_DSR_THRESHOLD`, `ECLIPTIC_IBKR_PORT`, `ECLIPTIC_RISK_STALENESS_DAYS` env vars (quickstart.md's Key Environment Variables table)

**Checkpoint**: Foundation ready — User Story 1 can now begin.

---

## Phase 3: User Story 1 — Assemble a Trustworthy Point-in-Time Dataset (Priority: P1) 🎯 MVP

**Goal**: Produce a daily G10 FX + macro feature matrix where every row reflects only what was knowable on that date.

**Independent Test**: Ingest two years of G10 FX and macro data, then verify macro values on a given backtest date match what ALFRED reported as of that date, before any model or signal is built (spec.md Independent Test, SC-001).

### Tests for User Story 1

- [ ] T009 [P] [US1] Integration test `tests/integration/test_feature_pipeline.py` — spot-check 50 random date/series combinations confirming vintage value matches ALFRED as-of that date, zero violations (SC-001)

### Implementation for User Story 1

- [ ] T010 [P] [US1] Implement `ecliptic/data/ingest_fx.py` — Dukascopy tick pull via `duka`, resample to daily OHLCV at 17:00 NY close, write `data/raw/fx/{pair}/{year}.parquet` (research.md §1; data-model.md FXPriceBar)
- [ ] T011 [US1] Implement gap-handling fill rule for FX holidays/missing feeds in `ingest_fx.py` — documented rule, not silent forward-fill or drop (FR-004; Edge Case)
- [ ] T012 [P] [US1] Implement `ecliptic/data/ingest_macro.py` — ALFRED `realtime_start`/`realtime_end` vintage pull for the series table in research.md §2 (FEDFUNDS, ECBMLFR, BOERUKM, IRSTJPN, CURRENTACCOUNT, B9B1Q027S1, CPIAUCSL, VIXCLS), fixed 30-day lag fallback via World Bank/IMF IFS for AUD/NZD/NOK/SEK policy rates; write `data/raw/macro/{series_id}.parquet` (FR-002; data-model.md MacroVintage)
- [ ] T013 [US1] Implement `ecliptic/data/build_features.py` — join FXPriceBar + MacroVintage + macro-dashboard risk score into `data/processed/feature_matrix.parquet` (data-model.md FeatureRow), depends on T010, T012
- [ ] T014 [US1] Implement look-ahead assertion in `build_features.py`: every macro value on date `t` has `vintage_date ≤ t`; print audit summary on completion (FR-003; plan.md invariant 1)
- [ ] T015 [US1] Wire `risk_score_date ≤ feature date` check and `data_complete` flag into `FeatureRow` construction (data-model.md)
- [ ] T016 [US1] CLI entrypoints: `python -m ecliptic.data.ingest_fx --pairs ... --start ...`, `python -m ecliptic.data.ingest_macro --start ...`, `python -m ecliptic.data.build_features --start ... --end ...` per quickstart.md

**Checkpoint**: User Story 1 fully functional and testable independently — clean point-in-time feature matrix exists.

---

## Phase 4: User Story 2 — Run a Signal Search with Honest Overfitting Controls (Priority: P2)

**Goal**: Track every backtest trial, compute the Deflated Sharpe Ratio, and refuse to certify results that don't clear the credibility bar.

**Independent Test**: Run a known number of parameter combinations against historical data; verify the harness counts every trial, computes DSR correctly, and flags results below threshold — before any signal is deployed (spec.md Independent Test, SC-004).

### Tests for User Story 2

- [ ] T017 [P] [US2] Unit test `tests/unit/test_dsr.py` — DSR against a known synthetic example (fixed trial count + return moments) matches the analytical formula within numerical precision (SC-004)

### Implementation for User Story 2

- [ ] T018 [P] [US2] Implement `ecliptic/harness/trial_registry.py` — append-only `data/trials/trial_registry.parquet` writer, auto-incrementing `trial_id`, `session_id` UUID per research session (data-model.md TrialRecord)
- [ ] T019 [P] [US2] Implement `ecliptic/harness/dsr.py` — Bailey & López de Prado (2014) DSR formula (research.md §5), min 60 monthly observations before a report is meaningful
- [ ] T020 [P] [US2] Implement `ecliptic/harness/cv.py` — purged + embargoed walk-forward (expanding window) CV; embargo = `max(1 trading day, ceil(2 × signal autocorrelation halflife))`, default 10 trading days (research.md §6; FR-007)
- [ ] T021 [US2] Wire DSR credibility gate (FR-008): refuse to certify a result as validated if DSR falls below the documented threshold (`ECLIPTIC_DSR_THRESHOLD`, default 0.5)
- [ ] T022 [US2] Guard `run_research.py`/harness entrypoint: refuse to run without an initialized `trial_registry.parquet` (Edge Case; plan.md invariant 2)
- [ ] T023 [US2] CLI: `python -m ecliptic.harness.dsr --report` — prints current DSR, trial count, pass/fail (quickstart.md)

**Checkpoint**: User Stories 1 and 2 both work independently — harness can gate any trial series, including synthetic fixtures.

---

## Phase 5: User Story 3 — Replicate the Carry and Momentum Factors (Priority: P3)

**Goal**: Reproduce the Lustig-Roussanov-Verdelhan carry factor and Menkhoff et al. momentum factor on the clean dataset from US1, and compare to published benchmarks.

**Independent Test**: Run replication and compare summary statistics (annualized return, Sharpe, max drawdown) to published figures, independently of conditioning/execution (spec.md Independent Test, SC-002, SC-003).

### Tests for User Story 3

- [ ] T024 [P] [US3] Unit test `tests/unit/test_carry.py` — HML_FX construction, minimum 6 valid currencies per period, degenerate-portfolio skip behavior
- [ ] T025 [P] [US3] Unit test `tests/unit/test_momentum.py` — top-3/bottom-3 ranking, dollar-neutral construction, no skip-month

### Implementation for User Story 3

- [ ] T026 [P] [US3] Implement `ecliptic/factors/carry.py` — LRV carry: monthly sort by forward discount (rate differential proxy for CIP), 3–5 bins, HML_FX long-short, `rx_{t+1} = Δs_{t+1} + (i*-i)_t`; skip rebalance period if fewer than 6 valid currencies (research.md §3; FR-009; data-model.md CarryPortfolio)
- [ ] T027 [P] [US3] Implement `ecliptic/factors/momentum.py` — Menkhoff spec: rank by prior 1-month excess return, long top-3/short bottom-3, 1-month hold, no skip-month (research.md §4; FR-010; data-model.md MomentumPortfolio)
- [ ] T028 [US3] Implement `ecliptic/research/replicate.py` — replication CLI comparing factor summary stats (annualized return, Sharpe, max drawdown) to published Lustig et al. / Menkhoff et al. figures; depends on T026, T027 and US1's feature matrix (FR-011)
- [ ] T029 [US3] Surface a diagnostic divergence report identifying the likely source data/construction step when replication deviates materially (Acceptance Scenario 3)
- [ ] T030 [US3] Add out-of-sample (post-publication) factor check with no significance claim unless the DSR gate (US2) has passed (Acceptance Scenario 4)
- [ ] T031 [US3] CLI: `python -m ecliptic.research.replicate --factor carry|momentum --start ... --end ...` per quickstart.md

**Checkpoint**: All three of US1–US3 independently functional — carry/momentum replication validated against SC-002/SC-003 within ±30% tolerance.

---

## Phase 6: User Story 4 — Apply the Conditioning Overlay and Measure Its Effect (Priority: P4)

**Goal**: Scale carry exposure by the macro-dashboard risk score and measure the effect on risk-adjusted return and drawdown.

**Independent Test**: Run conditioned vs. unconditioned backtest variants and produce a side-by-side Sharpe/max-drawdown/Calmar comparison, before any execution layer is connected (spec.md Independent Test).

### Tests for User Story 4

- [ ] T032 [P] [US4] Unit test `tests/unit/test_overlay.py` — exposure scalar mapping is continuous 0–1, staleness default is conservative (≤0.5), `conditioned_weight = combined_weight × risk_scalar` invariant holds

### Implementation for User Story 4

- [ ] T033 [US4] Implement `ecliptic/conditioning/overlay.py` risk score loader — read macro-dashboard `data/outputs/risk_score.parquet` (read-only), cache aligned series to `data/processed/risk_score_aligned.parquet` (data-model.md RiskScore)
- [ ] T034 [US4] Implement continuous exposure scalar mapping (0% at full risk-off, 100% at full risk-on), documented and reproducible (FR-012)
- [ ] T035 [US4] Implement staleness handling: when risk score is unavailable or >`ECLIPTIC_RISK_STALENESS_DAYS` (default 7) stale, default to conservative reduced exposure rather than risk-on (FR-014)
- [ ] T036 [US4] Implement `ecliptic/backtest/engine.py` — vectorized backtest producing both conditioned and unconditioned carry return series over the same period (FR-013), depends on US3's carry portfolio
- [ ] T037 [US4] Implement `ecliptic/backtest/report.py` — side-by-side annualized return, volatility, Sharpe, max drawdown, Calmar ratio, plus DSR for the conditioned result (SC-003 acceptance scenario 3)
- [ ] T038 [US4] Validate SC-005: conditioned strategy shows materially lower max drawdown than unconditioned in at least 2 of the 3 most severe historical risk-off episodes (e.g. 2008–09, 2020) in the backtest sample
- [ ] T039 [US4] Validate SC-006: conditioned carry Sharpe passes the DSR gate (US2) at 95% confidence with Phase 1's accumulated trial count

**Checkpoint**: US1–US4 independently functional — conditioning overlay's effect is quantified and DSR-gated.

---

## Phase 7: User Story 5 — Paper Trade the Strategy via IBKR (Priority: P5)

**Goal**: Wire the daily conditioned signal to IBKR paper trading — submit orders, log fills, reconcile positions.

**Independent Test**: Submit a known set of synthetic FX orders to the IBKR paper account, verify fills are received/logged, and run reconciliation — independently of any backtest/research layer (spec.md Independent Test, SC-007).

### Tests for User Story 5

- [ ] T040 [P] [US5] Contract test `tests/integration/test_signal_schema.py` — validates every invariant in `contracts/signal-schema.md` (conditioned_weight/target_notional formulas, stale→risk_scalar≤0.5, n_currencies_active≥4 else empty positions, Σ|conditioned_weight|≤1.5 leverage cap)

### Implementation for User Story 5

- [ ] T041 [US5] Extend `ecliptic/conditioning/overlay.py` to write the daily signal JSON to `data/signals/signal_{YYYY-MM-DD}.json` conforming exactly to `contracts/signal-schema.md` (data-model.md ConditionedSignal), depends on US4
- [ ] T042 [US5] Implement `ecliptic/execution/ibkr.py` — `ib_insync` connection on port 7497 (paper), submit `MarketOrder`/`LimitOrder` for FX pairs from the signal, record IBKR order IDs (FR-015; data-model.md Order); reads **only** from `data/signals/` — no imports from `factors/`/`conditioning/` (plan.md invariant 4)
- [ ] T043 [US5] Implement fill logging in `ibkr.py` — timestamp, instrument, quantity, fill price, order ID, estimated commission per fill (FR-016; data-model.md Fill)
- [ ] T044 [US5] Handle TWS/IB Gateway connection failure: log failure, retain unfilled target positions, single retry, no silent skip or duplicate on reconnect (Edge Case; research.md §7)
- [ ] T045 [US5] Implement `ecliptic/execution/reconcile.py` — daily reconciliation comparing actual vs. target paper positions, $100 default tolerance, flag discrepancies for review (FR-017; data-model.md ReconciliationRecord)
- [ ] T046 [US5] Implement `run_daily.py` entrypoint — refresh FX for yesterday's close → reload risk score → compute conditioned signal → submit IBKR orders → run end-of-day reconciliation (quickstart.md daily sequence)
- [ ] T047 [US5] Validate SC-007: submit, fill, and reconcile 10 synthetic IBKR paper orders with zero unlogged fills and zero position discrepancies at EOD reconciliation

**Checkpoint**: All five user stories independently functional — full research-to-paper-trading loop operational.

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Ties the independently-built stories into the full daily/research pipelines described in plan.md's Data Flow diagram

- [ ] T048 Implement `run_research.py` — full research loop entrypoint (data → harness → carry+momentum → conditioning), writes trial records, prints DSR report (quickstart.md)
- [ ] T049 Validate SC-008: full daily pipeline (data refresh → signal → conditioning → order generation → IBKR submission) completes end-to-end in under 10 minutes on the primary workstation
- [ ] T050 [P] Pin dependency versions in `requirements_ecliptic.txt` once the above is working end-to-end
- [ ] T051 Run `quickstart.md` top-to-bottom on a clean checkout as a final validation pass

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **Foundational (Phase 2)**: Depends on Setup — BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational only — this is the real MVP; nothing else can produce honest results without it
- **User Story 2 (Phase 4)**: Depends on Foundational only — independently testable via synthetic/fixture return series, does not require US1's real data to build and unit-test
- **User Story 3 (Phase 5)**: Depends on US1 (needs the real feature matrix to replicate published factors on) — not independently runnable against real data without it, though its unit tests (T024/T025) can run against fixtures in parallel
- **User Story 4 (Phase 6)**: Depends on US3 (carry portfolio) and US2 (DSR gate for SC-006)
- **User Story 5 (Phase 7)**: Depends on US4 (conditioned signal is the hand-off contract)
- **Polish (Phase 8)**: Depends on all five user stories being complete

### Within Each User Story

- Tests before implementation where both exist for the same task group
- Data/model-layer tasks before the CLI entrypoint that wires them together
- Story complete (checkpoint) before moving to the next priority

### Parallel Opportunities

- T002–T005 (Setup) in parallel
- T007–T008 (Foundational) in parallel once T006 exists
- T010 and T012 (FX vs. macro ingestion, US1) in parallel — different data sources, no shared state
- T018–T020 (trial registry, DSR, CV — US2) in parallel — separate modules
- T026 and T027 (carry vs. momentum — US3) in parallel — separate modules
- Once Foundational is done, US1 and US2 can be built in parallel by different sessions; US3 must wait on US1

---

## Parallel Example: User Story 1

```bash
# Launch FX and macro ingestion together — independent data sources:
Task: "Implement ecliptic/data/ingest_fx.py — Dukascopy daily OHLCV"
Task: "Implement ecliptic/data/ingest_macro.py — ALFRED vintage pull"

# Then, once both land, build_features.py joins them (not parallel — depends on both)
```

## Parallel Example: User Story 2

```bash
# All three harness modules are independent of each other:
Task: "Implement ecliptic/harness/trial_registry.py"
Task: "Implement ecliptic/harness/dsr.py"
Task: "Implement ecliptic/harness/cv.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1 — point-in-time feature matrix
4. **STOP and VALIDATE**: run T009's integration test, confirm SC-001 (zero look-ahead violations across 50 spot-checks)
5. This is the foundation the literature review calls "if you can't reproduce known results, you can't trust novel ones" — do not proceed to US3 until this is solid

### Incremental Delivery

1. Setup + Foundational → foundation ready
2. US1 → validate independently (MVP — a trustworthy dataset, no signal yet)
3. US2 → validate independently (harness works on any return series, including synthetic ones — can happen in parallel with US1)
4. US3 → validate against SC-002/SC-003 (needs US1's real data)
5. US4 → validate against SC-005/SC-006 (needs US3 + US2)
6. US5 → validate against SC-007 (needs US4; requires TWS/IB Gateway running locally)

### Notes

- [P] tasks touch different files with no dependency on incomplete work
- Every `data/` write path traces back to data-model.md's Storage Layout — if a task needs a path not listed there, data-model.md is out of date and should be revisited, not the task
- Live trading (real capital) is explicitly out of scope for Phase 1 (spec.md Assumptions) — Phase 7 targets the IBKR **paper** account only
