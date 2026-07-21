# Tasks: Macro Newsletter

**Feature:** `004-monthly-newsletter`
**Spec:** [spec.md](spec.md)
**Status:** In progress — cadence changed from monthly to **weekly** on 2026-07-20 (see note below); Phases 1–3 substantially done, Phase 4 partial

> **Cadence change (2026-07-20):** Originally spec'd as monthly (first Monday). Now generates **every week** as part of `weekly_pipeline.yml`, publish-only (no auto-send — see T-013/T-014 note). Filenames moved from `docs/newsletter/YYYY-MM.html` to `docs/newsletter/YYYY-MM-DD.html`; issue numbers auto-increment from the count of existing issue files instead of a manually-passed `--issue` arg. `spec.md` still describes the original monthly design and hasn't been rewritten for this change.

---

## Phase 1 — Generation Script

- [x] **T-001** ~~Decide email platform~~ — **Buttondown** selected; API docs at `https://api.buttondown.email/v1/`
- [x] **T-002** Create `scripts/monthly_newsletter.py` skeleton: load `latest_snapshot.json`, `indicators.parquet`, `country_scoreboard.parquet`
- [x] **T-003** Implement MoM delta calculation for recession probability, 10y–2y spread, 10y–3m spread, and risk score using `indicators.parquet` — now week-over-week given weekly cadence
- [x] **T-004** Implement country spotlight rotation: `issue_number % 12` maps to country index in scoreboard — now cycles every ~12 weeks instead of 12 months
- [x] **T-005** Implement "biggest movers" logic for country scoreboard: top 2 equity YTD gainers/losers vs prior month
- [x] **T-006** Write HTML template (inline CSS, email-safe) covering all 5 newsletter sections per spec
- [x] **T-007** Write plain-language narrative renderer: converts indicator values + deltas into paragraph strings (e.g., "Recession probability rose to X%, the highest since…")
- [x] **T-008** Output `docs/newsletter/YYYY-MM-DD.html` and update/create `docs/newsletter/index.html` (prepend new issue link)
- [x] **T-009** Test locally: run script against current `data/outputs/` and verify HTML renders correctly in browser — Issue #1 published 2026-07-13

## Phase 2 — GitHub Actions Integration

- [x] **T-010** ~~Create separate `monthly_newsletter.yml`~~ — instead added as a step inside the existing `weekly_pipeline.yml` job (runs after `build_paper.py`, before the commit step) so it shares the same data checkout, commit, and Pages deploy — no separate workflow/cron needed
- [x] **T-011** Workflow step runs `python scripts/monthly_newsletter.py` (no `--send`); output is committed and pushed by the existing "Commit outputs and docs" step, which already globs `docs/`
- [x] **T-012** Resolved without an `ISSUE_NUMBER` env var — `main()` now auto-increments by counting existing `docs/newsletter/*.html` issue files (excluding `index.html` and today's own target filename, for idempotent re-runs)

## Phase 3 — Email Delivery

- [x] **T-013** Implement Buttondown send in `monthly_newsletter.py`: `POST https://api.buttondown.email/v1/emails`, auth via `Authorization: Token <BUTTONDOWN_API_KEY>` — implemented, gated behind `--send` flag
- [x] **T-014** Store API key as GitHub Actions secret `BUTTONDOWN_API_KEY` — present in repo secrets since 2026-07-13. **Not wired into the weekly workflow** — the automated job never passes `--send`, so no email goes out automatically; sending is a deliberate manual step (`python scripts/monthly_newsletter.py --send`)
- [ ] **T-015** Set up Buttondown account at buttondown.email; configure sender name "Global Macro Pulse", reply-to `trevmon28@gmail.com` — unverified from repo, confirm directly in Buttondown
- [ ] **T-016** Send Issue #1 test to personal email; verify formatting in Gmail, Apple Mail, Outlook — unverified from repo

## Phase 4 — Integration & Polish

- [ ] **T-017** Add "Newsletter" link in `docs/index.html` nav/footer pointing to `newsletter/index.html` — not present yet
- [x] **T-018** Add "Newsletter" link in `docs/paper.html` footer — present
- [ ] **T-019** Verify `docs/newsletter/index.html` archive lists issues in reverse chronological order — logic prepends new issues, but only 1 issue exists so far; re-verify once a few weekly issues have accumulated
- [ ] **T-020** (Optional) Implement Claude API narrative generation: pass indicator values to claude-haiku-4-5, receive 2–3 sentence plain-language summary per section; add `ANTHROPIC_API_KEY` to Actions secrets
