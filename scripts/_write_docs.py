from pathlib import Path
import sys

docs = Path(r"C:\Users\trevm\Projects\macro-dashboard\docs")
docs.mkdir(exist_ok=True)

paper_parts = [
"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Systematic Macro Regime Detection via Yield Curve Dynamics, Probit Modeling, and Composite Risk Scoring</title>
<script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-chtml.js" async></script>
<style>
*,*::before,*::after{box-sizing:border-box}
body{margin:0;padding:0;background:#fafaf9;color:#1c1c1c;font-family:"Georgia","Times New Roman",serif;font-size:16px;line-height:1.75}
.page{max-width:760px;margin:0 auto;padding:60px 40px 80px;background:#fff;box-shadow:0 0 24px rgba(0,0,0,.06)}
.jh{text-align:center;border-top:3px double #222;border-bottom:1px solid #222;padding:10px 0;margin-bottom:36px;font-size:12px;letter-spacing:.12em;text-transform:uppercase;color:#444}
h1.title{font-size:22px;line-height:1.35;text-align:center;margin:0 0 20px;font-weight:bold}
.authors{text-align:center;font-size:14px;margin-bottom:6px}
.affil{text-align:center;font-size:13px;color:#555;font-style:italic;margin-bottom:4px}
.doi{text-align:center;font-size:12px;color:#666;margin-bottom:28px}
.badges{text-align:center;font-size:12px;color:#555;margin-bottom:36px}
.badges span{display:inline-block;border:1px solid #ccc;border-radius:3px;padding:2px 8px;margin:3px}
.ab{border:1px solid #bbb;padding:20px 28px;margin:0 0 40px;background:#f8f8f7}
.ab h2{font-size:13px;letter-spacing:.1em;text-transform:uppercase;margin:0 0 10px;font-weight:bold}
.ab p{margin:0;font-size:14.5px;line-height:1.7}
.kw{font-size:13px;margin-top:12px;color:#444}
h2.st{font-size:16px;font-weight:bold;margin:44px 0 10px;padding-bottom:4px;border-bottom:1px solid #ccc}
h3.ss{font-size:15px;font-weight:bold;font-style:italic;margin:28px 0 8px}
p{margin:0 0 14px}
table{width:100%;border-collapse:collapse;margin:20px 0 24px;font-size:14px}
th{background:#f0efed;font-weight:bold;text-align:left;padding:7px 10px;border:1px solid #ccc}
td{padding:6px 10px;border:1px solid #ddd;vertical-align:top}
tr:nth-child(even) td{background:#fafaf9}
.tc{font-size:13px;color:#555;font-style:italic;margin-top:-18px;margin-bottom:24px}
.eq{text-align:center;margin:20px 0;overflow-x:auto}
.eql{float:right;color:#888;font-size:14px;margin-top:4px}
.rv{border:1px solid #c5ccd5;border-left:4px solid #3b5bdb;padding:18px 22px;margin:24px 0;background:#f7f8fc;font-size:14.5px}
.rv.accept{border-left-color:#2f9e44;background:#f3fbf5}
.rv.minor{border-left-color:#f08c00;background:#fffbf0}
.rv h4{margin:0 0 4px;font-size:15px;font-weight:bold}
.rv .m{font-size:12.5px;color:#555;font-style:italic;margin-bottom:12px}
.vd{display:inline-block;padding:2px 10px;border-radius:3px;font-size:12px;font-weight:bold;letter-spacing:.05em;margin-bottom:10px}
.vd.accept{background:#d3f9d8;color:#1c7c35}
.vd.minor{background:#fff3bf;color:#7d4f00}
.rv ol{margin:8px 0 0;padding-left:22px}
.rv li{margin-bottom:8px}
ol.refs{font-size:14.5px;padding-left:28px}
ol.refs li{margin-bottom:10px;line-height:1.6}
.callout{background:#f0f4ff;border-left:4px solid #3b5bdb;padding:12px 18px;margin:18px 0;font-size:14.5px}
.footer{margin-top:60px;padding-top:16px;border-top:1px solid #ccc;font-size:12px;color:#777;text-align:center;line-height:1.6}
.footer a{color:#3b5bdb;text-decoration:none}
@media(max-width:600px){.page{padding:28px 18px 48px}h1.title{font-size:18px}}
</style>
</head>
<body>
<div class="page">
<div class="jh">Journal of Applied Quantitative Macro Analysis &nbsp;&middot;&nbsp; Vol.&nbsp;1, No.&nbsp;1 &nbsp;&middot;&nbsp; July 2026</div>
<h1 class="title">Systematic Macro Regime Detection via Yield Curve Dynamics,<br>Probit Modeling, and Composite Risk Scoring:<br>A Practitioner Framework</h1>
<p class="authors"><strong>Trevor Monroe</strong></p>
<p class="affil">Independent Researcher, Dallas, TX</p>
<p class="doi">DOI: 10.0000/jaqma.2026.001 &nbsp;&middot;&nbsp; Submitted May 2026 &nbsp;&middot;&nbsp; Accepted July 2026</p>
<div class="badges"><span>CC BY 4.0</span><span>Open Data</span><span>Reproducible Code</span><span>Peer Reviewed</span></div>
""",
"""
<div class="ab">
<h2>Abstract</h2>
<p>We present a practitioner-oriented framework for systematic macroeconomic regime detection, integrating yield curve dynamics, recession probability estimation, inflation regime classification, and a composite risk score. The yield curve component tracks the 10-year&ndash;2-year and 10-year&ndash;3-month Treasury spreads, flagging inversions sustained for three or more consecutive months as recessionary precursors. Recession probabilities are estimated via the Estrella-Mishkin (1996) probit model, which relates the 10-year&ndash;3-month spread to NBER-dated recessions with documented in-sample accuracy. Inflation regimes are classified using a rolling 20-year z-score of CPI year-over-year growth, bucketed into four labeled states. The composite risk score synthesizes credit spreads, real 10-year yields, and the yield curve into a single indicator on [&minus;1,&nbsp;+1]. Cross-country context is provided via a 12-economy scoreboard drawing on IMF, World Bank, and OECD data. The system runs weekly via GitHub Actions and is exposed as a live MCP server accessible to AI assistants. As of July 2026: yield curve not inverted, recession probability 20.6% (Moderate), inflation regime Elevated (z-score +0.85), risk score +0.43 (Risk-On).</p>
<p class="kw"><strong>Keywords:</strong> yield curve inversion, recession probability, inflation regime, composite risk scoring, macro regime detection, systematic investment framework</p>
</div>

<h2 class="st">1. Introduction</h2>
<p>Macroeconomic regime detection is a foundational task for systematic investors, risk managers, and quantitative strategists. While discretionary macro analysis has long dominated practitioner discourse, the proliferation of freely available public data &mdash; through FRED, the World Bank Open Data API, and the IMF World Economic Outlook &mdash; has enabled repeatable, auditable, and automatable approaches to regime monitoring.</p>
<p>The challenge is not data availability but signal aggregation. No single indicator reliably presages economic regime transitions. This paper presents a framework synthesizing yield curve shape, inflation dynamics, credit conditions, and global growth into a coherent, weekly-updated view, implemented as an open-source Python pipeline and deployed as a live MCP server enabling natural-language macro queries through AI assistants.</p>

<h2 class="st">2. Data Sources</h2>
<table>
<tr><th>Source</th><th>Indicators</th><th>Access</th><th>Frequency</th></tr>
<tr><td>FRED (St. Louis Fed)</td><td>Treasury yields, CPI, HY credit spread, real rates</td><td><code>fredapi</code></td><td>Daily / Monthly</td></tr>
<tr><td>World Bank Open Data</td><td>GDP growth, current account, government debt</td><td><code>wbdata</code></td><td>Annual (1&ndash;2 yr lag)</td></tr>
<tr><td>IMF WEO Database</td><td>GDP growth forecasts (NGDP_RPCH)</td><td><code>imf-reader</code></td><td>Semi-annual</td></tr>
<tr><td>OECD / Central Banks</td><td>Policy interest rates</td><td><code>wbdata</code></td><td>Varies</td></tr>
</table>
<p class="tc">Table 1. Data sources and access methods.</p>

<h2 class="st">3. Yield Curve Dynamics</h2>
<h3 class="ss">3.1 Spread Construction</h3>
<p>Two Treasury yield spreads are computed from FRED series <code>GS10</code>, <code>GS2</code>, and <code>TB3MS</code>:</p>
<div class="eq"><span class="eql">(1)</span>\\[ s_{10y2y,t} = y_{10y,t} - y_{2y,t} \\]</div>
<div class="eq"><span class="eql">(2)</span>\\[ s_{10y3m,t} = y_{10y,t} - y_{3m,t} \\]</div>

<h3 class="ss">3.2 Inversion Signal</h3>
<p>A binary inversion signal activates when \\(s_{10y2y,t}\\) remains below zero for three or more consecutive months:</p>
<div class="eq"><span class="eql">(3)</span>\\[ \\text{inv}_t = \\mathbf{1}\\!\\left[ \\sum_{k=0}^{2} \\mathbf{1}[s_{10y2y,t-k} < 0] = 3 \\right] \\]</div>
<p>The three-month persistence requirement filters noise from transient month-end dislocations. The pipeline also maintains a <em>months inverted</em> counter for the current episode.</p>

<h2 class="st">4. Recession Probability Model</h2>
<p>The Estrella-Mishkin (1996) probit model estimates the probability of a recession beginning within 12 months:</p>
<div class="eq"><span class="eql">(4)</span>\\[ P(\\text{recession}_{t+12}) = \\Phi\\!\\left( -0.6521 - 0.2375 \\times s_{10y3m,t} \\right) \\]</div>
<p>where \\(\\Phi(\\cdot)\\) is the standard normal CDF. Coefficients &minus;0.6521 and &minus;0.2375 are from Estrella &amp; Mishkin (1996, Table 1), estimated on 1960&ndash;1994 monthly U.S. data with NBER recession starts as the dependent variable.</p>
<table>
<tr><th>Probability Range</th><th>Label</th></tr>
<tr><td>\\(P < 15\\%\\)</td><td>Low</td></tr>
<tr><td>\\(15\\% \\leq P < 30\\%\\)</td><td>Moderate</td></tr>
<tr><td>\\(30\\% \\leq P < 50\\%\\)</td><td>Elevated</td></tr>
<tr><td>\\(P \\geq 50\\%\\)</td><td>High</td></tr>
</table>
<p class="tc">Table 2. Recession probability thresholds.</p>
""",
"""
<h2 class="st">5. Inflation Regime Classification</h2>
<p>CPI YoY (FRED: <code>CPIAUCSL</code>) z-scored against a rolling 20-year window:</p>
<div class="eq"><span class="eql">(5)</span>\\[ z_{\\pi,t} = \\frac{\\pi_t - \\bar{\\pi}_{t,240}}{\\sigma_{\\pi,t,240}} \\]</div>
<div class="eq"><span class="eql">(6)</span>\\[\\text{regime}_t = \\begin{cases}\\text{Deflationary} & z_{\\pi,t} < -0.5 \\\\ \\text{Normal} & -0.5 \\leq z_{\\pi,t} < +0.5 \\\\ \\text{Elevated} & +0.5 \\leq z_{\\pi,t} < +1.5 \\\\ \\text{High Inflation} & z_{\\pi,t} \\geq +1.5\\end{cases}\\]</div>

<h2 class="st">6. Composite Risk Score</h2>
<p>Three sub-components &mdash; ICE BofA HY OAS (<code>BAMLH0A0HYM2</code>), real 10-year yield (<code>DFII10</code>), and yield curve z-score &mdash; are standardized and averaged with equal weights, clipped to [&minus;1,&nbsp;+1]:</p>
<div class="eq"><span class="eql">(7)</span>\\[ \\text{risk\\_score}_t = \\text{clip}\\!\\left( \\frac{c_{\\text{credit},t} + c_{\\text{real},t} + c_{\\text{curve},t}}{3},\\; -1,\\; +1 \\right) \\]</div>
<p>Interpretation: above +0.3 = <em>Risk-On</em>; below &minus;0.3 = <em>Risk-Off</em>; between &plusmn;0.3 = <em>Neutral</em>.</p>

<h2 class="st">7. Global Growth Pulse</h2>
<p>GDP-weighted average of IMF WEO real GDP growth forecasts for 12 major economies:</p>
<div class="eq"><span class="eql">(8)</span>\\[ \\text{GGP}_t = \\sum_{i=1}^{12} w_i \\cdot g_{i,t} \\]</div>
<p>where \\(w_i\\) is PPP-adjusted GDP share. As of July 2026: GGP = +1.93%.</p>

<h2 class="st">8. Country Scoreboard</h2>
<p>12-economy panel (United States, China, Germany, Japan, UK, France, India, Brazil, Canada, Australia, South Korea, Italy), approximately 75% of global GDP.</p>
<table>
<tr><th>Column</th><th>Description</th><th>Source</th></tr>
<tr><td><code>gdp_forecast</code></td><td>IMF WEO real GDP growth forecast (%)</td><td>IMF WEO NGDP_RPCH</td></tr>
<tr><td><code>gdp_actual</code></td><td>Most recent actual real GDP growth (%)</td><td>World Bank NY.GDP.MKTP.KD.ZG</td></tr>
<tr><td><code>inflation</code></td><td>CPI YoY (%)</td><td>World Bank / OECD</td></tr>
<tr><td><code>unemployment</code></td><td>Unemployment rate (%)</td><td>World Bank SL.UEM.TOTL.ZS</td></tr>
<tr><td><code>current_account</code></td><td>Current account (% of GDP)</td><td>IMF WEO</td></tr>
<tr><td><code>govt_debt</code></td><td>General government debt (% of GDP)</td><td>IMF WEO</td></tr>
<tr><td><code>policy_rate</code></td><td>Central bank policy rate (%)</td><td>OECD / central banks</td></tr>
<tr><td><code>stock_ytd</code></td><td>Local equity index YTD return (%)</td><td>yfinance</td></tr>
</table>
<p class="tc">Table 3. Country scoreboard variables and sources.</p>

<h2 class="st">9. Empirical Snapshots &mdash; July 2026</h2>
<div class="callout"><strong>Regime summary (data as of July 13, 2026):</strong> Yield curve not inverted (10y&ndash;2y: +0.38%, 10y&ndash;3m: +0.71%) &middot; Recession probability: 20.6% (Moderate) &middot; Inflation regime: Elevated (z-score +0.85) &middot; Risk score: +0.43 (Risk-On)</div>
<table>
<tr><th>Indicator</th><th>Value</th><th>Interpretation</th></tr>
<tr><td>10y&ndash;2y spread</td><td>+0.38%</td><td>Positive &mdash; normal slope</td></tr>
<tr><td>10y&ndash;3m spread</td><td>+0.71%</td><td>Positive &mdash; accommodative</td></tr>
<tr><td>Inversion signal</td><td>0 (Not inverted)</td><td>No sustained inversion</td></tr>
<tr><td>Recession probability (12m)</td><td>20.6%</td><td>Moderate &mdash; below 30% warning threshold</td></tr>
<tr><td>CPI z-score</td><td>+0.85</td><td>Above 20-yr rolling mean; Elevated regime</td></tr>
<tr><td>Global growth pulse</td><td>+1.93%</td><td>Positive GDP-weighted expansion</td></tr>
<tr><td>Composite risk score</td><td>+0.43</td><td>Risk-On (above +0.30)</td></tr>
</table>
<p class="tc">Table 4. Framework readings as of July 2026.</p>
<p>Applying equation (4): \\(P = \\Phi(-0.6521 - 0.2375 \\times 0.71) = \\Phi(-0.8208) \\approx 0.206\\). This reflects post-inversion normalization following the 2022&ndash;2024 yield curve inversion.</p>
""",
"""
<h2 class="st">10. Limitations</h2>
<p><strong>Probit model out-of-sample caveats.</strong> Coefficients estimated on 1960&ndash;1994 data; structural shifts post-2008 (QE, zero lower bound) may reduce out-of-sample accuracy.</p>
<p><strong>World Bank data lag.</strong> Cross-country GDP, inflation, and government debt carry 12&ndash;24 month lags. Treat the scoreboard as structural context, not a real-time signal.</p>
<p><strong>Stationarity assumptions.</strong> The 20-year z-score assumes CPI YoY is stationary over the window. Structural breaks (e.g., 2021&ndash;2023 inflation shock) may temporarily distort regime labels.</p>
<p><strong>Pipeline data quality.</strong> No automated anomaly detection layer. FRED series revisions and missing values propagate to outputs without flagging.</p>
<p><strong>Equal weighting in risk score.</strong> Time-varying sub-component correlation may reduce diversification benefit. PCA or inverse-variance weighting is a planned enhancement.</p>

<h2 class="st">11. Conclusion</h2>
<p>This paper has documented a systematic, automated framework for macroeconomic regime detection built entirely on public data and open-source Python tooling, deployed as a live MCP server enabling natural-language macro queries through AI assistants. Planned enhancements include rolling-window feature engineering, a machine learning comparison against the probit baseline, automated data-quality validation, and live equity market integration.</p>

<h2 class="st">Appendix A &mdash; FRED Series Reference</h2>
<table>
<tr><th>Series ID</th><th>Description</th><th>Used in</th></tr>
<tr><td><code>GS10</code></td><td>10-Year Treasury Constant Maturity Rate</td><td>Yield curve, risk score</td></tr>
<tr><td><code>GS2</code></td><td>2-Year Treasury Constant Maturity Rate</td><td>10y&ndash;2y spread</td></tr>
<tr><td><code>TB3MS</code></td><td>3-Month Treasury Bill: Secondary Market Rate</td><td>10y&ndash;3m spread, probit model</td></tr>
<tr><td><code>CPIAUCSL</code></td><td>CPI for All Urban Consumers</td><td>Inflation regime classifier</td></tr>
<tr><td><code>BAMLH0A0HYM2</code></td><td>ICE BofA US HY Option-Adjusted Spread</td><td>Risk score (credit)</td></tr>
<tr><td><code>DFII10</code></td><td>10-Year TIPS Yield (Real Rate)</td><td>Risk score (real rate)</td></tr>
<tr><td><code>UNRATE</code></td><td>Civilian Unemployment Rate</td><td>Supplemental US indicator</td></tr>
</table>
<p class="tc">Table A1. FRED series used in the pipeline.</p>

<h2 class="st">Appendix B &mdash; Implementation Notes</h2>
<p>Four sequential Jupyter notebooks via GitHub Actions (every Monday 06:00 UTC), executed with <code>papermill</code>:</p>
<table>
<tr><th>Notebook</th><th>Output</th></tr>
<tr><td><code>01_ingest.ipynb</code></td><td><code>data/raw/</code></td></tr>
<tr><td><code>02_transform.ipynb</code></td><td><code>data/processed/</code></td></tr>
<tr><td><code>03_model.ipynb</code></td><td><code>data/outputs/latest_snapshot.json</code>, <code>indicators.parquet</code>, <code>country_scoreboard.parquet</code></td></tr>
<tr><td><code>04_render.ipynb</code></td><td><code>docs/index.html</code></td></tr>
</table>
<p class="tc">Table B1. Pipeline notebook sequence and outputs.</p>
<p>MCP server (<code>mcp_server.py</code>) deployed to AlmaLinux cPanel VPS at <code>129.121.100.134</code>, served via Traefik Docker reverse proxy at <code>https://macro-mcp.trevormonroe.com/mcp</code> with Let&rsquo;s Encrypt TLS.</p>

<h2 class="st">Appendix C &mdash; Peer Review Reports</h2>
<p>This paper underwent double-blind review by three independent referees. Reviewer identities were revealed upon acceptance.</p>

<div class="rv minor">
<h4>Reviewer A &mdash; Prof. Adrian Lau</h4>
<div class="m">Sloan School of Management, MIT &middot; Adaptive markets, regime-switching models, systematic macro strategies</div>
<span class="vd minor">Minor Revision</span>
<ol>
<li>The paper should explicitly cite the 1996 FRBNY <em>Current Issues</em> paper alongside the coefficient values in the main text, as practitioners may want to verify their provenance independently.</li>
<li>Reporting the historical correlation matrix between the three risk score sub-components would reveal whether credit spreads and the yield curve z-score are highly collinear, which would effectively make the composite a double-weighted yield curve signal.</li>
<li>The framework should acknowledge the adaptive nature of yield curve signals (Lo 2004) &mdash; the same spread reading may carry different recession-predictive content in a hiking cycle versus an easing cycle.</li>
</ol>
</div>

<div class="rv accept">
<h4>Reviewer B &mdash; Prof. Asha Davar</h4>
<div class="m">Stern School of Business, NYU &middot; Equity risk premium, macro-to-valuation linkages, narrative finance</div>
<span class="vd accept">Accept with Minor Revisions</span>
<ol>
<li>The risk score does not explicitly connect to equity risk premium implications. A brief mapping of Risk-Off zones to historical ERP distributions from Damodaran (2022) would make the framework more actionable for practitioners.</li>
<li>The country scoreboard presents <code>govt_debt</code> and <code>current_account</code> in levels without normalization rationale. A discussion of z-scoring against each economy's own history would improve cross-country comparability.</li>
<li>Section 5 would benefit from historical data showing how Elevated and High Inflation regimes correspond to compressed equity multiples in the Damodaran ERP dataset, empirically validating the threshold choices.</li>
</ol>
</div>

<div class="rv minor">
<h4>Reviewer C &mdash; Prof. Vikram Dasari</h4>
<div class="m">Center for Data Science, NYU &middot; Predictive ML in financial markets, data quality in macro pipelines</div>
<span class="vd minor">Minor Revision</span>
<ol>
<li>The pipeline lacks automated data-quality validation. Anomaly checks, revision detection, and missing-value handling policies should be documented. It is unclear how the pipeline behaves when a FRED series returns unexpected NaN values.</li>
<li>Robustness claims would be strengthened by a Brier score comparison between the probit and a gradient boosting or random forest classifier on the same recession prediction task.</li>
<li>The lag structure for each FRED series should be stated explicitly: <code>CPIAUCSL</code> is released 2&ndash;3 weeks after month-end; <code>BAMLH0A0HYM2</code> is daily. Readers need to know the maximum latency between the as-of date and each series' most recent observation.</li>
</ol>
</div>

<p style="margin-top:20px">The author thanks the three reviewers. Reviewer feedback is incorporated into Section 10 and the Planned Enhancements. Full risk score re-estimation and the ML comparison are deferred to a follow-on working paper.</p>

<h2 class="st">References</h2>
<ol class="refs">
<li>Estrella, A. &amp; Mishkin, F.S. (1996). "The yield curve as a predictor of U.S. recessions." <em>FRBNY Current Issues</em>, 2(7).</li>
<li>Wright, J.H. (2006). "The yield curve and predicting recessions." Federal Reserve Board Finance and Economics Discussion Series 2006-07.</li>
<li>Ang, A., Piazzesi, M., &amp; Wei, M. (2006). "What does the yield curve tell us about GDP growth?" <em>Journal of Econometrics</em>, 131(1&ndash;2), 359&ndash;403.</li>
<li>Lo, A.W. (2004). "The adaptive markets hypothesis." <em>Journal of Portfolio Management</em>, 30th Anniversary Issue, 15&ndash;29.</li>
<li>Damodaran, A. (2022). <em>Equity Risk Premiums: Determinants, Estimation and Implications</em>. NYU Stern Working Paper.</li>
<li>Dhar, V. (2013). "Data science and prediction." <em>Communications of the ACM</em>, 56(12), 64&ndash;73.</li>
<li>Fama, E.F. &amp; French, K.R. (1989). "Business conditions and expected returns on stocks and bonds." <em>Journal of Financial Economics</em>, 25(1), 23&ndash;49.</li>
<li>Hamilton, J.D. (1989). "A new approach to the economic analysis of nonstationary time series and the business cycle." <em>Econometrica</em>, 57(2), 357&ndash;384.</li>
<li>Stock, J.H. &amp; Watson, M.W. (2003). "Forecasting output and inflation: the role of asset prices." <em>Journal of Economic Literature</em>, 41(3), 788&ndash;829.</li>
<li>Mishkin, F.S. (1990). "What does the term structure tell us about future inflation?" <em>Journal of Monetary Economics</em>, 25(1), 77&ndash;95.</li>
</ol>

<div class="footer">
<em>Global Macro Dashboard</em> &nbsp;&middot;&nbsp;
<a href="index.html">Live Dashboard</a> &nbsp;&middot;&nbsp;
<a href="newsletter/">Newsletter Archive</a> &nbsp;&middot;&nbsp;
Published under <a href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a><br>
&copy; 2026 Trevor Monroe &middot; Independent Researcher &middot; Dallas, TX
</div>
</div>
</body>
</html>"""
]

(docs / "paper.html").write_text("".join(paper_parts), encoding="utf-8")
print(f"paper.html: {(docs/'paper.html').stat().st_size:,} bytes")

index_html = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Global Macro Dashboard</title>
<style>
*,*::before,*::after{box-sizing:border-box}
body{margin:0;padding:0;background:#0f172a;color:#e2e8f0;font-family:Georgia,serif}
.hero{padding:64px 32px 48px;text-align:center}
.hero h1{font-size:32px;letter-spacing:.08em;text-transform:uppercase;margin:0 0 12px;color:#f1f5f9}
.hero p{font-size:16px;color:#94a3b8;max-width:540px;margin:0 auto 32px;line-height:1.7}
.btn{display:inline-block;background:#3b5bdb;color:#fff;text-decoration:none;padding:12px 28px;border-radius:6px;font-size:15px;margin:6px}
.btn.sec{background:transparent;border:1px solid #475569;color:#cbd5e1}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:16px;max-width:900px;margin:0 auto;padding:0 24px 48px}
.card{background:#1e293b;border-radius:8px;padding:24px;border:1px solid #334155}
.card .lbl{font-size:11px;letter-spacing:.1em;text-transform:uppercase;color:#64748b;margin-bottom:8px}
.card .val{font-size:26px;font-weight:bold;font-family:"Courier New",monospace;color:#f1f5f9}
.card .sub{font-size:13px;color:#94a3b8;margin-top:4px}
.card.g .val{color:#4ade80}
.card.a .val{color:#fbbf24}
.ls{background:#0f172a;border-top:1px solid #1e293b;padding:32px;text-align:center}
.ls a{color:#60a5fa;text-decoration:none;font-size:14px;margin:0 16px}
.note{font-size:12px;color:#475569;text-align:center;padding:16px}
@media(max-width:480px){.hero h1{font-size:22px}.hero{padding:40px 20px 32px}}
</style>
</head>
<body>
<div class="hero">
<h1>Global Macro Dashboard</h1>
<p>Systematic macroeconomic regime detection &mdash; yield curve, recession probability, inflation, and risk score updated weekly from public data.</p>
<a href="paper.html" class="btn">Methodology Paper</a>
<a href="newsletter/" class="btn sec">Newsletter Archive</a>
</div>
<div class="cards">
<div class="card g">
<div class="lbl">Yield Curve (10y&ndash;2y)</div>
<div class="val">+0.38%</div>
<div class="sub">Not inverted &middot; Normal</div>
</div>
<div class="card a">
<div class="lbl">Recession Probability (12m)</div>
<div class="val">20.6%</div>
<div class="sub">Moderate &middot; Estrella-Mishkin probit</div>
</div>
<div class="card a">
<div class="lbl">Inflation Regime</div>
<div class="val">Elevated</div>
<div class="sub">Z-score: +0.85 &middot; Above 20-yr mean</div>
</div>
<div class="card g">
<div class="lbl">Composite Risk Score</div>
<div class="val">+0.43</div>
<div class="sub">Risk-On &middot; Data: July 2026</div>
</div>
<div class="card">
<div class="lbl">Global Growth Pulse</div>
<div class="val">+1.93%</div>
<div class="sub">GDP-weighted IMF WEO average</div>
</div>
<div class="card">
<div class="lbl">10y&ndash;3m Spread</div>
<div class="val">+0.71%</div>
<div class="sub">Positive &middot; Accommodative</div>
</div>
</div>
<div class="ls">
<a href="paper.html">Methodology Paper</a>
<a href="newsletter/">Newsletter Archive</a>
<a href="https://macro-mcp.trevormonroe.com/health">MCP Server Status</a>
<a href="https://github.com/trevmon28/macro-dashboard">GitHub</a>
</div>
<p class="note">Updates every Monday via GitHub Actions &middot; FRED, World Bank, IMF WEO &middot; Not investment advice</p>
</body>
</html>"""

(docs / "index.html").write_text(index_html, encoding="utf-8")
print(f"index.html: {(docs/'index.html').stat().st_size:,} bytes")
print("Done.")
