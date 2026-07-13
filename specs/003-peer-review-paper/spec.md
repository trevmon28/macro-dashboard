# Feature Specification: Faux Peer-Reviewed Methodology Paper

**Feature:** `003-peer-review-paper`
**Author:** Trevor Monroe
**Date:** July 2026
**Status:** Planned

---

## Overview

Produce a realistic-looking academic paper documenting the Global Macro Dashboard's quantitative methodology — covering yield curve dynamics, recession probability modeling, inflation regime classification, risk score construction, and country scoreboard. The paper includes a faux peer-review panel whose profiles mirror the intellectual style and domain focus of leading quant-finance academics. Published as a self-contained HTML page (and optionally PDF) hosted on GitHub Pages alongside the dashboard.

---

## Audience

- Sophisticated investors and practitioners who want to understand the methodology rigorously
- Academic readers evaluating the model's econometric foundations
- Personal credibility / portfolio piece

---

## Paper Metadata

| Field | Value |
|-------|-------|
| Title | *Systematic Macro Regime Detection via Yield Curve Dynamics, Probit Modeling, and Composite Risk Scoring: A Practitioner Framework* |
| Author | Trevor Monroe, Independent Researcher |
| Journal | *Journal of Applied Quantitative Macro Analysis* (faux) |
| Volume / Issue | Vol. 1, No. 1 (July 2026) |
| DOI | `10.0000/jaqma.2026.001` (faux) |
| License | CC BY 4.0 |

---

## Peer Review Panel

Three faux reviewers modeled on the intellectual profile and domain expertise of prominent academics — plausible names, real-style institutional affiliations, genuine domain focuses.

### Reviewer A — Quantitative Finance / Adaptive Markets

**Profile modeled on:** Andrew Lo (MIT, adaptive markets hypothesis, systematic trading, econometrics of asset returns)

| Field | Value |
|-------|-------|
| Faux name | Prof. Adrian Lau |
| Affiliation | Sloan School of Management, Massachusetts Institute of Technology |
| Research focus | Adaptive markets, regime-switching models, systematic macro strategies |
| Review verdict | **Minor Revision** |
| Key feedback | (1) Estrella-Mishkin probit is solid but should cite the 1996 FRBNY paper explicitly; (2) risk score composite should report correlation between sub-components to assess redundancy; (3) the adaptive nature of yield curve signals over rate cycles deserves acknowledgment |

### Reviewer B — Valuation & Equity Risk Premium

**Profile modeled on:** Aswath Damodaran (NYU Stern, valuation, equity risk premium, narrative + numbers)

| Field | Value |
|-------|-------|
| Faux name | Prof. Asha Davar |
| Affiliation | Stern School of Business, New York University |
| Research focus | Equity risk premium, macro-to-valuation linkages, narrative finance |
| Review verdict | **Accept with Minor Revisions** |
| Key feedback | (1) Framework should explicitly connect risk score output to equity risk premium implications — what does a score of −0.8 mean for a DCF discount rate?; (2) Country scoreboard lacks a normalization rationale; (3) section on inflation regime would benefit from historical ERP data showing premium compression in high-inflation regimes |

### Reviewer C — AI/ML in Finance & Data Quality

**Profile modeled on:** Vasant Dhar (NYU Stern, machine learning in finance, predictive analytics, data science)

| Field | Value |
|-------|-------|
| Faux name | Prof. Vikram Dasari |
| Affiliation | Center for Data Science, New York University |
| Research focus | Predictive machine learning in financial markets, data quality in macro pipelines |
| Review verdict | **Minor Revision** |
| Key feedback | (1) Pipeline relies on FRED/World Bank with no automated data-quality validation layer — should describe anomaly checks; (2) probit model is interpretable but a random forest comparison on recession prediction would strengthen robustness claims; (3) state the lag structure explicitly for each FRED series used |

---

## Paper Sections

| # | Section | Content |
|---|---------|---------|
| Abstract | — | 200-word summary of methodology, data sources, key indicators, and practical use |
| 1 | Introduction | Motivation for systematic macro regime detection; limitations of discretionary macro; paper contributions |
| 2 | Data Sources | FRED, World Bank, IMF WEO, yfinance, OECD policy rates — series list, frequency, lag structure |
| 3 | Yield Curve Dynamics | 10y–2y and 10y–3m spread construction; inversion signal definition (≥3 consecutive months below zero); historical context |
| 4 | Recession Probability Model | Estrella-Mishkin (1996) probit: Φ(−0.6521 − 0.2375 × spread_10y3m); coefficient provenance; in-sample fit on NBER recessions |
| 5 | Inflation Regime Classification | CPI YoY z-score vs 20-year rolling mean; threshold rationale (−0.5/+0.5/+1.5); regime labels (Deflationary/Normal/Elevated/High) |
| 6 | Composite Risk Score | Sub-components: credit spread (ICE BofA HY), real 10y rate, yield curve z-score; equal-weight composite; clipping to [−1, +1]; interpretation |
| 7 | Global Growth Pulse | GDP-weighted IMF NGDP_RPCH average; economy selection; weighting methodology |
| 8 | Country Scoreboard | 12-economy panel; variable selection (GDP, CPI, unemployment, current account, govt debt, policy rate, equity YTD); data provenance per column |
| 9 | Empirical Snapshots | As-of July 2026 readings; yield curve status; recession probability level; inflation regime; risk score interpretation |
| 10 | Limitations | Data leakage in pipeline (season-aggregate vs real-time); World Bank data lag (1–2 year); model stationarity assumptions; probit out-of-sample caveats |
| 11 | Conclusion | Summary; roadmap for live deployment (MCP server); planned enhancements (rolling features, ML comparison) |
| A | Appendix A | Full FRED series IDs and descriptions |
| B | Appendix B | Implementation Notes — Python stack, notebook pipeline, GitHub Actions |
| C | Peer Review | Reviewer reports (A, B, C) with verdict and summary comments |
| — | References | 10–15 cited works (Estrella & Mishkin 1996; Wright 2006; Ang et al. 2006; Damodaran equity risk premium series; Lo 2004 AMH; etc.) |

---

## Output Formats

| Format | Path | Notes |
|--------|------|-------|
| HTML | `docs/paper.html` | Self-contained, Tailwind or CSS; rendered alongside `index.html` on GitHub Pages |
| PDF (optional) | `docs/paper.pdf` | Generated via `weasyprint` or `pandoc` from the HTML |

---

## Functional Requirements

### FR-001: Plausible academic appearance
Paper must render with title page, abstract, numbered sections, a references list, and a peer-review appendix. Formatting should pass as a genuine pre-print.

### FR-002: Reviewer panel completeness
Each reviewer has: name, affiliation, research focus, verdict (Accept / Minor Revision / Reject), and 3+ specific substantive comments.

### FR-003: Methodology accuracy
All equations and constants (e.g., Estrella-Mishkin coefficients −0.6521 and −0.2375) must match the actual notebook implementation in `03_model.ipynb`.

### FR-004: Published on GitHub Pages
`docs/paper.html` is deployed alongside `docs/index.html` via the existing Pages workflow; reachable at `https://trevmon28.github.io/macro-dashboard/paper.html`.

### FR-005: Linked from dashboard
`docs/index.html` footer or header includes a "Methodology Paper" link to `paper.html`.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Paper content | Python script that writes HTML directly (no LaTeX dependency) |
| Styling | Embedded CSS (academic serif font, two-column abstract, figure numbering) |
| Math rendering | MathJax CDN for inline equations |
| PDF export | `weasyprint` (optional; add to `requirements.txt`) |
| Hosting | GitHub Pages (`docs/paper.html`) |

---

## References (to include)

1. Estrella, A. & Mishkin, F.S. (1996). "The yield curve as a predictor of U.S. recessions." *Federal Reserve Bank of New York Current Issues*, 2(7).
2. Wright, J.H. (2006). "The yield curve and predicting recessions." Federal Reserve Board Working Paper 2006-07.
3. Ang, A., Piazzesi, M., & Wei, M. (2006). "What does the yield curve tell us about GDP growth?" *Journal of Econometrics*, 131(1–2), 359–403.
4. Lo, A.W. (2004). "The adaptive markets hypothesis." *Journal of Portfolio Management*, 30th Anniversary Issue, 15–29.
5. Damodaran, A. (2022). *Equity Risk Premiums: Determinants, Estimation and Implications*. NYU Stern Working Paper.
6. Dhar, V. (2013). "Data science and prediction." *Communications of the ACM*, 56(12), 64–73.
7. Fama, E.F. & French, K.R. (1989). "Business conditions and expected returns on stocks and bonds." *Journal of Financial Economics*, 25(1), 23–49.
8. Hamilton, J.D. (1989). "A new approach to the economic analysis of nonstationary time series and the business cycle." *Econometrica*, 57(2), 357–384.
9. Stock, J.H. & Watson, M.W. (2003). "Forecasting output and inflation: the role of asset prices." *Journal of Economic Literature*, 41(3), 788–829.
10. Mishkin, F.S. (1990). "What does the term structure tell us about future inflation?" *Journal of Monetary Economics*, 25(1), 77–95.

---

## Open Questions

1. **PDF generation**: Is `weasyprint` acceptable, or should this remain HTML-only for simplicity?
2. **Author affiliation**: Should the paper list an institutional affiliation (e.g., "Independent Researcher, Dallas TX") or a faux one?
3. **Appendix C framing**: Should reviewer reports be framed as "double-blind" with authors anonymized, or acknowledged review?
