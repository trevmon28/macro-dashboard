# Literature Review: Building a Systematic, Market-Neutral Strategy with Agentic AI

**Prepared for:** Trevor Monroe
**Context:** Personal capital, capable infrastructure (colo/data feeds), horizon open to whatever the edge supports, priority on what is actually tradable with theory in a supporting role.
**Date:** May 2026

---

## 0. How to read this document, and one honest reframe up front

You named three lodestars — Simons, Thorp, and Dhar — and an ambition to let a general-equilibrium (GE) / quantitative-spatial model *inform* a market-neutral trading strategy. Before the literature, here is the single most important thing to internalize, because it will save you months:

**The people you admire did not get their edge from macroeconomic theory.** Renaissance's Medallion extracts statistical structure from short-horizon price and microstructure data; Simons was explicit that fundamental/narrative models underperformed signal-driven ones. Thorp's edge came from *provable* relative-value mispricings (convertible/warrant arbitrage) and, earlier, card counting — bounded bets with a quantifiable advantage. Dhar, the closest to your instinct, has run ML-based systematic programs for two decades and is refreshingly blunt about it: he does not believe there is "a code to crack," only a constant search for a *sustainable* edge, and he stresses an inverse relationship between a program's performance and its capacity.

So the role of your spatial-econ and global-imbalances reading is **prior formation and risk awareness, not signal generation.** A GE model tells you *where structural vulnerability lives* (which currencies are fragile, which external positions are unsustainable). It does not tell you *when* to put on a trade, and its predictions are slow-moving, badly identified at the parameter level, and largely already in prices. Treat theory as the thing that keeps you out of stupid trades and shapes your universe — not the thing that fires the signal.

The document is organized in four parts, deliberately front-loading the tradable material:

1. **Tradable strategy archetypes** — what is genuinely market-neutral and has survived scrutiny.
2. **Macro-as-signal** — currency carry/value/momentum and rates, honestly appraised.
3. **Methods & epistemics** — how not to fool yourself; this is where most solo quant projects die.
4. **Theory-as-prior** — where your GE/spatial reading actually belongs.

A recommendation on instruments closes the document.

---

## Part 1 — Tradable Strategy Archetypes (lead with this)

### 1.1 Relative-value / statistical arbitrage (the Thorp lineage, generalized)

The cleanest market-neutral idea is relative value: hold a long and a short whose difference (the "spread") is mean-reverting, so you are exposed to the *convergence* and hedged against the *common factor*. The canonical academic anchor is **Gatev, Goetzmann & Rouwenhorst (2006), "Pairs Trading: Performance of a Relative-Value Arbitrage Rule"** (Review of Financial Studies), which formalized the distance-based pairs approach and documented meaningful excess returns in early samples.

The essential survey is **Krauss (2017), "Statistical Arbitrage Pairs Trading Strategies: Review and Outlook"** (Journal of Economic Surveys). It categorizes the field into five families — distance, cointegration, time-series (mean-reversion modeling), stochastic-control, and "other" — and is the single best map of the terrain. Read it first.

**The sobering empirical fact you must absorb:** these strategies have decayed substantially. Reviews of the literature document average pairs-trading performance falling from the mid-teens annualized in pre-2000 samples to mid-single-digits post-2010 as markets grew more efficient and the trade became crowded. Some studies find naïve pairs trading unprofitable after the early 2000s once realistic costs are applied. The implication is not "abandon the idea" but "the vanilla version is arbitraged away — your edge must be in a *non-obvious* construction (better pair selection, regime conditioning, faster execution, or a less-crowded universe)."

Two modeling touchstones worth your time:
- **Avellaneda & Lee (2010), "Statistical Arbitrage in the US Equities Market"** (Quantitative Finance) — the standard reference for the factor-residual approach: strip out systematic factors, trade the mean-reverting idiosyncratic residual. This decomposition (systematic vs. idiosyncratic) is the conceptual backbone of modern equity stat-arb.
- **Engelberg, Gao & Jagannathan, "An Anatomy of Pairs Trading"** — important because it identifies *why* pairs converge (idiosyncratic news, common information, liquidity) and finds return potential decays sharply with time-since-divergence, motivating the practitioner rule of cutting trades that haven't converged within a window.

Modeling the spread itself: the **Ornstein–Uhlenbeck mean-reverting process** is the workhorse; much of the time-series and stochastic-control literature builds optimal entry/exit and sizing rules on top of an OU spread, and explicitly studies how parameter uncertainty (in the long-run mean and volatility) degrades the guarantee of profit.

### 1.2 Cross-sectional factor / characteristic strategies

The other large market-neutral family sorts a universe on a characteristic and goes long-short (top minus bottom), so the dollar-neutral long-short cancels the common factor. Value, momentum, profitability, low-volatility, carry all live here. This is the most *studied* corner of finance — and, as Part 3 explains, the most contaminated by data-mining. The key cross-asset reference is **Asness, Moskowitz & Pedersen (2013), "Value and Momentum Everywhere"** (Journal of Finance), which shows value and momentum premia appear consistently across equities, currencies, bonds, and commodities and are linked by common (notably funding-liquidity) risk. The cross-asset consistency is what makes these effects more believable than any single-market anomaly.

### 1.3 Time-series momentum (trend) and carry as portfolio-level engines

- **Moskowitz, Ooi & Pedersen (2012), "Time Series Momentum"** (Journal of Financial Economics) — distinct from cross-sectional momentum: an asset's *own* past return predicts its future return, robust across dozens of futures markets. This is the academic spine of the managed-futures/CTA industry and is naturally implementable in liquid futures.
- **Koijen, Moskowitz, Pedersen & Vrugt (2018), "Carry"** (JFE) — generalizes "carry" beyond currencies to a unifying predictor across asset classes. Useful as a portfolio-construction lens, not just an FX trade.

These are not strictly "market neutral" in the dollar-neutral sense, but they are *uncorrelated-to-equity-beta* engines that combine well with relative-value sleeves.

---

## Part 2 — Macro-as-Signal: Currencies and Rates (honestly appraised)

This is where your macro dashboard connects to an actual trade, and where I think your best risk-adjusted opportunity lies (see the instrument recommendation). The FX cross-section is attractive precisely because the long-short construction is *naturally* dollar-neutral — the dollar leg cancels in a high-minus-low portfolio.

**The carry foundation.** **Lustig & Verdelhan (2007)** and **Lustig, Roussanov & Verdelhan (2011), "Common Risk Factors in Currency Markets"** built the portfolio approach: sort currencies by forward discount (interest differential), and a "carry" factor (high-minus-low, often labeled HMLFX) plus a "dollar" factor explain most of the cross-section of currency excess returns. The high-minus-low carry return historically ran on the order of ~6% annualized before costs in their samples. The economic interpretation matters: carry is widely read as compensation for crash/global-risk exposure (it pays steadily, then loses sharply in risk-off episodes — the "picking up nickels in front of a steamroller" property documented by Brunnermeier, Nagel & Pedersen, 2009).

**Currency momentum and value.** **Menkhoff, Sarno, Schmeling & Schrimpf (2012), "Currency Momentum Strategies"** documents profitable cross-sectional FX momentum that is notably *not* explained by standard risk factors (carry, volatility, business-cycle, or equity factors) — an unresolved puzzle that cuts both ways: it may be a real anomaly, or a sign the risk model is wrong. The long-short momentum portfolios are dollar-neutral by construction. Asness et al.'s value-and-momentum work extends value to FX as well.

**Important honesty flags from the recent literature:**
- A 200+-year FX study (QuantPedia summary of recent academic work) finds the currency *momentum* effect has only limited long-run support, and the currency *reversal* effect essentially does not exist — while cross-currency yield-curve (flattening) trades and long-bond carry have been surprisingly robust. Treat the most "obvious" FX anomalies as the most likely to be regime-dependent or decayed.
- Macro fundamentals *do* have some predictive content for currencies (Dahlquist & Hasseltoft, 2020), partially rescuing the idea that your dashboard's variables — current-account balances, policy-rate paths, inflation regimes — carry information. But the effect is modest and slow.

**Where your dashboard plugs in.** Your scoreboard already tracks policy rates (the carry signal), current-account balances and government debt (structural vulnerability / value), inflation regimes, and a risk-on/off score (the conditioning variable that governs *when* carry is dangerous). That is a coherent feature set for a conditional cross-sectional FX strategy: carry as the base return engine, momentum as a complementary sleeve, and your risk score as a *de-risking overlay* that cuts carry exposure when the global risk regime turns — addressing carry's central weakness directly.

---

## Part 3 — Methods & Epistemics (the part that decides whether any of this works)

If you read only one part carefully, make it this one. With capable infrastructure you can backtest millions of configurations, and that capability is exactly what will destroy you if uncontrolled.

### 3.1 The multiple-testing / backtest-overfitting problem

- **Harvey, Liu & Zhu (2016), "...and the Cross-Section of Expected Returns"** (Review of Financial Studies) — the field's wake-up call. Given hundreds of factors mined over decades, a t-statistic of 2.0 is *meaningless*; they argue a newly discovered factor needs a t-stat closer to **3.0** to be credible, and that "most claimed research findings in financial economics are likely false."
- **Bailey & López de Prado (2014), "The Deflated Sharpe Ratio"** (Journal of Portfolio Management) — the practical tool. The **DSR** corrects an observed Sharpe ratio for (a) the number of trials you ran, (b) non-normal (skewed, fat-tailed) returns, and (c) sample length. Their companion concept, **Minimum Backtest Length**, tells you how much history you need before a given Sharpe is even potentially meaningful. *Implement this in your pipeline as a gate, not an afterthought.* If your research loop tries 500 parameter combinations, the DSR knows, even if your conscience doesn't.
- **Bailey, Borwein, López de Prado & Zhu (2014), "Pseudo-Mathematics and Financial Charlatanism"** (Notices of the AMS) — shows formally how easy it is to manufacture a beautiful overfit backtest, and why out-of-sample claims from a searched-over backtest are nearly worthless without trial-count adjustment.

### 3.2 The replication crisis — and the counterpoint

- **Hou, Xue & Zhang (2020), "Replicating Anomalies"** (RFS) — replicated ~450 anomalies and found the majority fail to survive once microcaps are down-weighted and consistent methodology is applied; well over half lose significance.
- **The counterpoint, which intellectual honesty requires:** **Jensen, Kelly & Pedersen (2023), "Is There a Replication Crisis in Finance?"** (Journal of Finance) argues that when factors are tested with consistent methodology and a Bayesian multiple-testing lens, replication rates are actually *high* (e.g., CAPM-alpha replication rises above 80%), and some "failures to replicate" actually *confirm* theory (the betting-against-beta case). The lesson is not nihilism — it is that **methodology discipline determines whether an effect is real.** The same data yields "crisis" or "no crisis" depending on rigor.

### 3.3 Position sizing — the Thorp contribution you *should* borrow

Where Thorp's influence belongs in your system is not the trades but the **sizing**: the **Kelly criterion** and, in practice, **fractional Kelly**. Kelly maximizes long-run log-growth but is brutally sensitive to estimation error in your edge; serious practitioners run half-Kelly or less to trade a little growth for a large reduction in drawdown risk. This is the rigorous version of "bet more when the edge is bigger," and it pairs naturally with a model that outputs a *probability* and a *confidence*, which is exactly what an ML/ensemble stack gives you.

### 3.4 Where ML actually helps vs. overfits (the Dhar lens)

Dhar's framing is the right one for an agentic-AI build. His view: ML is a credible "generate-and-test" engine for hypotheses — it automates Popper's predictive-accuracy criterion at scale — but in markets there is **no code to crack**, only the search for a *sustainable* edge, and **capacity is the enemy of performance.** Concretely for you:
- ML earns its keep in **conditioning and combination** (regime detection, sizing, combining weak signals, modeling non-linear interactions among your macro features) far more than in *discovering* a raw signal from price alone.
- The **"out-of-sample and out-of-time"** discipline Dhar stresses is non-negotiable: validate across time periods the model never saw, not just held-out random samples (markets have regimes; random splits leak).
- For the methods stack itself, **López de Prado, *Advances in Financial Machine Learning* (2018)** is the standard practitioner text — purged/embargoed cross-validation, meta-labeling, sample uniqueness, feature importance done correctly. It directly addresses why naïve ML cross-validation lies in finance.

---

## Part 4 — Theory-as-Prior: Where Your GE / Spatial Reading Belongs

Now your three sources find their proper home — informing *priors and risk*, not firing signals.

- **Itskhoki & Mukhin, "Global Imbalances: A Progress Report"** (your Source 1) is the most directly *usable* of your three. It builds on the savings-glut (Caballero–Farhi–Gourinchas), the intertemporal current-account approach (Obstfeld–Rogoff), and exorbitant privilege (Gourinchas–Rey). For a currency strategy, this literature is your **structural-vulnerability map**: persistent external imbalances, the special role of the dollar as the global safe asset, and the conditions under which a currency is fragile. Use it to (a) define which currencies belong in your "structurally weak / value-short" bucket, and (b) understand *why* carry crashes are correlated globally (the safe-asset/risk-off mechanism). It rationalizes the de-risking overlay in Part 2.
- **Redding & Rossi-Hansberg, "Quantitative Spatial Economics"** (your Source 3), with Eaton–Kortum, Allen–Arkolakis (uniqueness of spatial equilibrium), and Caliendo et al. (sectoral I-O linkages), is genuinely beautiful — and the **least tradable** of the three. Its outputs are multi-year reallocation comparative statics with badly identified parameters. Its honest use to you: *very* long-horizon priors on which economies/sectors face structural headwinds or tailwinds (a slow tilt, not a signal), and a framework for thinking about commodity/trade-linked currencies. Do not try to extract a dated trade from it.
- **McCord & Sachs, "Development, Structure, and Transformation"** (your Source 5), as a geography-vs-institutions counterweight to Acemoglu–Johnson–Robinson, belongs at the *slowest* layer: a multi-year prior on growth trajectories (the kind of thing that, at most, tilts a strategic allocation, never a tactical trade).

**The general-equilibrium ambition, stated plainly:** building a GE model that *informs* the strategy is reasonable and intellectually satisfying *if* "informs" means "sets the universe, the structural priors, and the risk overlay." Building a GE model that *generates* the tradable signal is, on the current evidence, a project that will consume enormous effort and produce a slow, badly identified, already-priced output. I'd steer you to the former.

---

## Recommendation: Instruments and a Concrete Path

**Recommended primary instrument: G10 + select EM currencies (via forwards/futures), with government-bond futures as the second sleeve.** Reasoning:

1. **The macro-to-trade link is real here and nowhere else.** Your dashboard's variables (policy rates, current accounts, debt, inflation regime, risk score) map directly onto established FX return predictors (carry, value, momentum) and onto a *conditioning* overlay. For single-name equities, your macro features are far more diffuse.
2. **Market-neutral by construction.** High-minus-low FX portfolios are dollar-neutral automatically; the dollar factor cancels. You get neutrality without fighting for it.
3. **Deep, cheap, ~24-hour, futures-friendly.** Ideal for capable-but-personal infrastructure. FX and rates futures have low transaction costs and high capacity — and capacity, per Dhar, is what preserves the edge.
4. **Equity stat-arb is the most crowded, infrastructure-hungry, decay-prone corner.** It is viable, but it is where you compete most directly with the best-resourced players and where the literature documents the steepest decay. Keep it as a later, optional sleeve — ideally factor-residual (Avellaneda–Lee) rather than naïve pairs.

**A staged build I'd suggest:**

1. **Replicate before you innovate.** Reproduce the Lustig–Verdelhan carry factor and Menkhoff et al. momentum factor on clean data. If you can't reproduce known results, you can't trust novel ones.
2. **Build the methods harness first.** DSR gate, purged/embargoed out-of-time CV (López de Prado), and a trial counter — *before* you search for signals. The harness is your edge against yourself.
3. **Add the conditioning layer.** Use your risk score to modulate carry exposure (de-risk in risk-off regimes). This is the most defensible place for ML/ensemble methods.
4. **Size with fractional Kelly** off model-implied probabilities, capped conservatively.
5. **Use the GE/imbalances theory as the universe filter and risk map**, per Part 4.
6. **Only then**, if warranted, add an equity factor-residual stat-arb sleeve for diversification.

---

## Core Reading List (priority order)

**Tier 1 — read first (tradable + methods):**
1. Krauss (2017), *Statistical Arbitrage Pairs Trading Strategies: Review and Outlook*, J. Economic Surveys.
2. Harvey, Liu & Zhu (2016), *...and the Cross-Section of Expected Returns*, RFS.
3. Bailey & López de Prado (2014), *The Deflated Sharpe Ratio*, J. Portfolio Management.
4. Lustig, Roussanov & Verdelhan (2011), *Common Risk Factors in Currency Markets*, RFS.
5. López de Prado (2018), *Advances in Financial Machine Learning* (book).

**Tier 2 — strategy depth:**
6. Asness, Moskowitz & Pedersen (2013), *Value and Momentum Everywhere*, J. Finance.
7. Moskowitz, Ooi & Pedersen (2012), *Time Series Momentum*, JFE.
8. Menkhoff, Sarno, Schmeling & Schrimpf (2012), *Currency Momentum Strategies*, JFE.
9. Avellaneda & Lee (2010), *Statistical Arbitrage in the US Equities Market*, Quantitative Finance.
10. Koijen, Moskowitz, Pedersen & Vrugt (2018), *Carry*, JFE.
11. Gatev, Goetzmann & Rouwenhorst (2006), *Pairs Trading*, RFS.

**Tier 3 — epistemics & the replication debate:**
12. Hou, Xue & Zhang (2020), *Replicating Anomalies*, RFS.
13. Jensen, Kelly & Pedersen (2023), *Is There a Replication Crisis in Finance?*, J. Finance.
14. Bailey, Borwein, López de Prado & Zhu (2014), *Pseudo-Mathematics and Financial Charlatanism*, Notices of the AMS.
15. Dhar (2013), *Data Science and Prediction*, Communications of the ACM; and Dhar's writing on the sustainability of ML-based trading edges.

**Tier 4 — theory-as-prior (your sources + foundations):**
16. Itskhoki & Mukhin, *Global Imbalances: A Progress Report* (your Source 1).
17. Brunnermeier, Nagel & Pedersen (2009), *Carry Trades and Currency Crashes*, NBER Macro Annual — the bridge between your macro theory and carry's crash risk.
18. Redding & Rossi-Hansberg, *Quantitative Spatial Economics* (your Source 3).
19. McCord & Sachs, *Development, Structure, and Transformation* (your Source 5).

---

*A closing note in the spirit of being a good collaborator rather than a cheerleader: the hardest and most valuable discipline in this whole enterprise is resisting the beauty of your own models. The GE framework is elegant; the ML stack is powerful; the macro dashboard is genuinely good work. None of that is the same as a Sharpe-positive, capacity-aware, out-of-time-validated edge that survives costs. Build the harness that tells you the truth, replicate what's known, and let the theory shape your priors — not your P&L expectations. That is, in the end, exactly what Dhar, Thorp, and even Simons actually did.*
