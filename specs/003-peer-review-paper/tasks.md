# Tasks: Faux Peer-Reviewed Methodology Paper

**Feature:** `003-peer-review-paper`
**Spec:** [spec.md](spec.md)
**Status:** Pending

---

## Phase 1 — Content Drafting

- [ ] **T-001** Extract exact Estrella-Mishkin coefficients and all threshold values from `notebooks/03_model.ipynb` — verify against spec before writing equations
- [ ] **T-002** Draft Sections 1–3 (Introduction, Data Sources, Yield Curve) as structured text; include FRED series IDs in data table
- [ ] **T-003** Draft Section 4 (Recession Probability): write Estrella-Mishkin probit equation in LaTeX/MathJax; describe NBER recession alignment
- [ ] **T-004** Draft Sections 5–7 (Inflation Regime, Risk Score, Global Growth Pulse): document z-score formula, sub-component weights, composite clipping
- [ ] **T-005** Draft Sections 8–9 (Country Scoreboard, Empirical Snapshots): pull current July 2026 indicator values from `data/outputs/latest_snapshot.json` for the snapshot section
- [ ] **T-006** Draft Sections 10–11 (Limitations, Conclusion): acknowledge data leakage, World Bank lag, probit stationarity assumptions
- [ ] **T-007** Draft Appendix A (FRED series IDs) and Appendix B (Implementation Notes — notebooks, GitHub Actions, conda env)
- [ ] **T-008** Write reviewer panel (Appendix C): three reviewer reports (Prof. Adrian Lau / Asha Davar / Vikram Dasari) with verdict + 3 substantive comments each per spec
- [ ] **T-009** Compile references list (10 entries minimum per spec)

## Phase 2 — HTML Rendering

- [ ] **T-010** Create `scripts/build_paper.py` — Python script that writes a self-contained `docs/paper.html` from the drafted sections
- [ ] **T-011** Style: embedded CSS with academic serif font (Georgia/Palatino), title page block, abstract box, numbered sections, figure/table captions
- [ ] **T-012** Add MathJax CDN script tag so Estrella-Mishkin probit equation renders as proper math
- [ ] **T-013** Render peer-review appendix with visually distinct reviewer cards (name, affiliation chip, verdict badge, bulleted comments)
- [ ] **T-014** Add references section with numbered citations linked from in-text `[N]` markers
- [ ] **T-015** Validate HTML renders correctly in browser: check MathJax, section numbering, reviewer cards, references

## Phase 3 — Integration

- [ ] **T-016** Add "Methodology Paper" link in `docs/index.html` footer (or header nav) pointing to `paper.html`
- [ ] **T-017** Add `scripts/build_paper.py` to GitHub Actions workflow so `paper.html` is rebuilt on each weekly pipeline run
- [ ] **T-018** Verify GitHub Pages serves `paper.html` at `https://trevmon28.github.io/macro-dashboard/paper.html`
- [ ] **T-019** (Optional) Install `weasyprint`, run `weasyprint docs/paper.html docs/paper.pdf`, commit PDF
