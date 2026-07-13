# Tasks: Monthly Macro Newsletter

**Feature:** `004-monthly-newsletter`
**Spec:** [spec.md](spec.md)
**Status:** Pending

---

## Phase 1 — Generation Script

- [x] **T-001** ~~Decide email platform~~ — **Buttondown** selected; API docs at `https://api.buttondown.email/v1/`
- [ ] **T-002** Create `scripts/monthly_newsletter.py` skeleton: load `latest_snapshot.json`, `indicators.parquet`, `country_scoreboard.parquet`
- [ ] **T-003** Implement MoM delta calculation for recession probability, 10y–2y spread, 10y–3m spread, and risk score using `indicators.parquet`
- [ ] **T-004** Implement country spotlight rotation: `issue_number % 12` maps to country index in scoreboard
- [ ] **T-005** Implement "biggest movers" logic for country scoreboard: top 2 equity YTD gainers/losers vs prior month
- [ ] **T-006** Write HTML template (inline CSS, email-safe) covering all 5 newsletter sections per spec
- [ ] **T-007** Write plain-language narrative renderer: converts indicator values + deltas into paragraph strings (e.g., "Recession probability rose to X%, the highest since…")
- [ ] **T-008** Output `docs/newsletter/YYYY-MM.html` and update/create `docs/newsletter/index.html` (prepend new issue link)
- [ ] **T-009** Test locally: run script against current `data/outputs/` and verify HTML renders correctly in browser

## Phase 2 — GitHub Actions Integration

- [ ] **T-010** Create `.github/workflows/monthly_newsletter.yml` with `cron: '0 8 1-7 * 1'` (first Monday of each month, 08:00 UTC — after main pipeline at 06:00)
- [ ] **T-011** Workflow steps: checkout → activate venv → run `python scripts/monthly_newsletter.py` → commit `docs/newsletter/` changes → push (triggers Pages deploy)
- [ ] **T-012** Add `ISSUE_NUMBER` as a workflow environment variable (or derive from git tag / commit count) so rotation logic works correctly

## Phase 3 — Email Delivery

- [ ] **T-013** Implement Buttondown send in `monthly_newsletter.py`: `POST https://api.buttondown.email/v1/emails` with `{"subject": "Global Macro Pulse — Month YYYY", "body": "<html>...", "status": "about_to_send"}`; auth via `Authorization: Token <BUTTONDOWN_API_KEY>`
- [ ] **T-014** Store API key as GitHub Actions secret `BUTTONDOWN_API_KEY`; reference in workflow as `env: BUTTONDOWN_API_KEY: ${{ secrets.BUTTONDOWN_API_KEY }}`
- [ ] **T-015** Set up Buttondown account at buttondown.email; configure sender name "Global Macro Pulse", reply-to `trevmon28@gmail.com`; Buttondown handles unsubscribe and CAN-SPAM footer automatically
- [ ] **T-016** Send Issue #1 test to personal email; verify formatting in Gmail, Apple Mail, Outlook

## Phase 4 — Integration & Polish

- [ ] **T-017** Add "Newsletter" link in `docs/index.html` nav/footer pointing to `newsletter/index.html`
- [ ] **T-018** Add "Newsletter" link in `docs/paper.html` footer
- [ ] **T-019** Verify `docs/newsletter/index.html` archive lists issues in reverse chronological order
- [ ] **T-020** (Optional) Implement Claude API narrative generation: pass indicator values to claude-haiku-4-5, receive 2–3 sentence plain-language summary per section; add `ANTHROPIC_API_KEY` to Actions secrets
