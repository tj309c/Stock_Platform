🔥 Analysis Master: Quantitative Trading Platform 🔥

"One Dashboard to Rule Them All, One Framework to Find Them, One Platform to Bring Them All, and in the Alpha Bind Them."

A comprehensive, Python-based quantitative analysis framework that democratizes institutional-grade market intelligence. This is a full-spectrum Digital Landscape Quantitative Modeler designed to identify market inefficiencies, scan for arbitrage opportunities, generate forward-looking predictions, and identify optimal entry points with a quantitative confidence score.

Philosophy: Blend the sophisticated quantitative tools of professional hedge funds with the irreverent, humorous, and context-aware insights of a wsb_quotes.py engine. All models are built on 100% free, public data. No Bloomberg terminals required. 💎🙌

🎯 Project Goal & Philosophy

This project is a comprehensive framework for:

Quantitative Analysis: Deep fundamental, technical, and risk analysis.

Optimal Entry Detection: A core engine to identify when stocks, options, or crypto are "good buys" with a data-driven confidence score.

Proactive Discovery: A market-wide screener and alerter to find new opportunities.

Signal Backtesting: A historical "efficacy engine" to determine which signals have worked for which stocks.

Predictive Modeling: LLM-powered forecasting using "digital landscape" variables (news, sentiment, economic data, congressional trades).

Portfolio Optimization: Modern Portfolio Theory with efficient frontier analysis.

🚀 Core Architecture: 7 Dashboards, 1 Co-pilot, 1 Final Report

The platform is built around 7 specialized dashboards, a consistent design_system (ThemeManager, MetricCardRenderer), an ambient "AI Co-pilot," and a final, exportable report.

---
## Recent Additions (Nov 18, 2025)

- Historical P/E fallback: The platform now computes an approximate historical P/E time series using yfinance if third-party fundamental APIs (like FMP) are unavailable. It attempts to compute a TTM EPS series from quarterly financials (Net Income / Shares Outstanding) and falls back to a trailing EPS constant when needed. The function is available at `src/pipelines/get_market_data.py::get_historical_pe_ratio`.
- Chart & UX: Overlay and subplot control labels are now color-synced to their Plotly traces. Overlay and subplot color maps were centralized as class-level constants so the UI and the chart trace colors remain consistent across the app.
- Dashboard Improvements: The `EquityDashboard` now merges the computed historical P/E into the chart if FMP data is unavailable and emits a small user-facing warning when P/E is missing.
- Utilities & Tests: A script `scripts/compute_historical_pe.py` allows export of computed historical P/E series for a ticker (CSV). Deterministic unit tests were added for the new fallback and chart color mapping under `tests/unit`.

---
## Developer Quick Start (Testing & Dev)

Run unit tests locally:
```bash
python -m pytest -q tests/unit -q -vv
```

Run the Streamlit app for local manual testing (Dev mode):
```bash
streamlit run main.py
```

Compute and export historical P/E locally (example for AAPL):
```bash
python scripts/compute_historical_pe.py AAPL --period 2y --interval 1d --out aapl_pe.csv
```

Notes:
- The `get_historical_pe_ratio` function uses `MarketDataPipeline.get_stock_price` so network and caching behavior is consistent across pipelines.
- Unit tests that interact with network data are deterministic using monkeypatch (no network call should be required for `tests/unit`). Integration tests can be added separately for CI.

1. The AI Co-pilot

An ambient, multi-model AI (using Claude, GPT-4, Gemini, and Grok) provides contextual insights.

Example (DCF): As you type "25%" growth, an AI note appears: Warning: This growth rate is 3x higher than the BLS-adjusted employment growth for this sector.

Example (Chart): The AI auto-annotates the chart: AI Note: Insider buying reported here.

Example (Global Consensus): A "Global AI Consensus" button queries all four models to analyze all data points for a ticker and provide a single, weighted BUY/HOLD/SELL recommendation.

2. The AI-Generated PDF Report

The platform's "killer feature" is a one-click "Final Consensus Stock Report" (Export to PDF). The AI Co-pilot consolidates all data from all 7 dashboards—Valuation, Pro Indicators, Options Flow, Sentiment, BLS data, etc.—into a single, professional, multi-page PDF "tear sheet" with a final, data-driven recommendation.

3. Unified Dashboard Structure

Each of the 7 dashboards follows a clean, three-tab UI structure:

Summary: A high-level overview with the most critical metrics and charts.

Deep Dive: All the granular data, advanced charts, and interactive tools for that module.

AI Opinion: The AI Co-pilot's specific analysis and insights for that section (e.g., AI opinion on valuation, AI opinion on technicals).

The 7 Dashboards

📈 1. Equity Analysis Dashboard

Deep-dive tool for comprehensive stock valuation and "good buy" detection.

Ape Intelligence Engine (Good Buy Detection):

Merged Engine: Consolidates multiple factors into a single confidence score.

Multi-Factor Scoring (0-100 "Ape Score"):

Valuation Score: DCF vs. current price.

Technical Score: RSI, MACD, Support/Resistance levels.

Sentiment Score: Social media and news momentum.

Momentum Score: Price trends and pullbacks.

Fundamentals Score: P/E, margins, growth.

Outputs:

GOOD BUY RANGE: $XXX - $YYY

CONFIDENCE SCORE: ##/100

Risk/Reward Ratio

Price & Technical Analysis (7-Tier Pro Engine):

A professional-grade technical analysis engine with 60+ indicators. It produces a visual summary bar (Trend, Momentum, Volatility, etc.) and multi-tab interactive charts.

Tier 1 (Core): SMA, EMA, RSI, MACD, Bollinger Bands, ADX.

Tier 2 (Pro): Ichimoku Cloud, Fibonacci Retracement, Stochastic, Pivot Points.

Tier 3 (Volume): Volume Profile (VPFR), On-Balance Volume (OBV), Accumulation/Distribution (A/D).

Tier 4 (Momentum): Rate of Change (ROC), TRIX, Connors RSI.

Tier 5 (Market Breadth): VIX, Put/Call Ratio, TRIN, Dark Pool Estimates.

Tier 6 (Quant): Beta, Alpha, Sharpe Ratio, Sortino Ratio.

Tier 7 (AI/ML): ML-based Trend Prediction, Market Regime Detection.

Algorithmic Pattern Recognition:

Implements statistical analysis to identify patterns on charts using price and volume data.

Visually highlights detected patterns on the interactive chart.

Patterns Include: Head and Shoulders, Double/Triple Tops/Bottoms, Support/Resistance, Trendlines, Triangles, Wedges, and Flags.

Includes a UI slider (10-200 periods) for lookback windows.

Fundamental & Financial Analysis:

Deep dive into financial statements (Income Statement, Balance Sheet, Cash Flow).

Ratio Analysis: P/E, P/B, P/S, PEG, ROE, ROA, Profit Margins, Debt-to-Equity, Current Ratio.

Enterprise Value (EV) metrics and EV/EBITDA multiples.

Quantitative Valuation Models:

Interactive DCF Calculator: A multi-faceted tool for granular valuation:

GAAP vs. Non-GAAP Toggle: Allows the user to toggle between standard GAAP FCF and "Adjusted" FCF. The AI Co-pilot assists by automatically scanning 10-K/10-Q filings to find non-cash adjustments (like Stock-Based Compensation), revealing the impact of accounting practices on valuation.

Parameter Preset Engine: One-click presets (Conservative, Base Case, Aggressive) that automatically adjust all valuation sliders (Growth, WACC, FCF assumptions, etc.).

Interactive Sliders: Adjust 7+ key assumptions (Growth Rate, WACC, Terminal Growth) in real-time.

Monte Carlo Simulation: Runs 1,000-10,000 simulations with randomized variables to generate a probability distribution of the stock's fair value.

Sensitivity Analysis: Creates one-way and two-way heatmaps to show which assumptions matter most.

Bear/Base/Bull Scenario Comparison: Provides a side-by-side comparison of fair value.

Detailed Breakdown: Includes a "Value Bridge" (EV to Equity Value) and year-by-year cash flow projections.

User Guide: Provides "Best Practices & Common Mistakes" for performing a DCF.

Zero-FCF Valuation Engine: An alternative 5-method engine for high-growth, SaaS, or unprofitable companies where a traditional DCF fails.

Auto-Selection Logic: Automatically detects company type (e.g., SaaS, E-commerce) to apply the most relevant models.

Methods: 1. Revenue Multiple, 2. EBITDA Multiple, 3. Rule of 40 (for SaaS), 4. Unit Economics (LTV:CAC), 5. Revenue Terminal Value.

Confidence Score: Generates a "High," "Medium," or "Low" confidence rating for its final valuation.

Sum-of-the-Parts (SOTP) Analysis: Values complex companies by breaking them into distinct business segments.

BLS Employment Regime Analysis: Integrates Bureau of Labor Statistics (BLS) data. Use Case: Applies regime-based valuation multipliers and makes automatic adjustments to Monte Carlo simulations based on macro employment trends.

Other Intrinsic Models: Dividend Discount Model (DDM) and Net Asset Value (NAV).

Risk & Return Analysis:

Metrics: Beta (Market Correlation), Rolling Volatility, Sharpe Ratio, Sortino Ratio (Downside Risk), and Maximum Drawdown.

Value at Risk (VaR) and Conditional VVaR (CVaR).

Sentiment & News:

Real-time sentiment from Reddit, Twitter/X, and StockTwits.

Latest news feed from financial news APIs.

API-Free Scraper: Fallback scraper for Finviz, and Yahoo Finance RSS.

Institutional & Insider Tracking:

Tracks institutional holdings (e.g., BlackRock, Vanguard).

Insider Transactions:

Primary Free Source: Monitors SEC EDGAR Form 4 RSS Feeds for real-time, primary source data on insider trades.

API Fallback: Uses Finnhub for additional formatted data.

Congressional Trades Monitoring: Tracks and displays recent trades by members of Congress. Use Case: Serves as a powerful leading indicator for sector-specific policy. (Free Data Source: Scrapes public disclosures from sites like housestockwatcher.com or senatestockwatcher.com).

⚡ 2. Derivatives & Options Dashboard

Identify opportunity and risk like an institutional flow desk.

Options Flow Analysis:

Unusual Volume & Open Interest (OI) Scanner: Flags abnormal activity.

High Volume/OI Ratio Screening: Detects new large positions.

Advanced Options Chain Analysis:

Greeks Tracking: Delta, Gamma, Theta, Vega, Rho.

Implied Volatility (IV) Percentile & Skew Analysis.

Gamma Exposure (GEX) Profile: Visualizes dealer hedging impact, identifying strike prices that may act as price 'magnets' (positive gamma) or 'repellers' (negative gamma).

Open Interest (OI) Profile: Charts OI concentrations ('OI Walls') at different strikes, highlighting potential support and resistance levels.

Historical Put/Call Ratio (PCR) Chart: Tracks market sentiment over time to identify 'Fear' (high PCR) vs. 'Greed' (low PCR).

Delta Divergence Chart: A volume-weighted analysis of call vs. put delta.

Features: Includes an interactive expiration slider, Moneyness Zone analysis (ITM/OTM), and a summary chart showing net delta across all expirations.

Output: Generates an automatic "Market Expectation" (Bullish/Bearish) label.

Strategy Builder & Visualization:

Payoff-diagram modeler for pre-built strategies (Spreads, Iron Condors, Straddles, etc.).

Risk/Reward, Break-Even, and Probability of Profit (PoP) calculator.

₿ 3. Crypto & Digital Assets Dashboard

Analysis tools tailored for 24/7, high-volatility crypto markets.

Market & Technical Analysis:

Real-time price tracking for a curated basket (BTC, ETH, SOL, XRP, DOGE, etc.).

Technical indicators adapted for 24/7 markets.

Volume profile and order book depth analysis.

On-Chain & Sentiment Metrics:

Fear & Greed Index integration.

HODL Wave & Strength Analysis: Age distribution of UTXO set.

Transaction Volume and Active Address monitoring.

Whale wallet tracking (large holder movements).

Performance & Target Modeling:

Price Target Projection Models: Fibonacci extensions, etc.

"When Lambo" HODL & DCA Calculator:

HODL Mode: Calculates the future price needed to reach a target profit (e..g., a "Lambo" via a price slider) based on an initial investment.

DCA Mode: Simulates a Dollar Cost Average (DCA) strategy, allowing the user to input a monthly investment amount over a set period to project total coins and average cost basis.

🔬 4. Predictive Modeling & Arbitrage Dashboard

The core alpha-generation engine. Scans for inefficiencies and predicts future moves.

Earnings Play Predictor:

A dedicated tool for analyzing earnings announcements.

1. Surprise Likelihood Score: Predicts if a company will beat or miss estimates by synthesizing:

Sentiment Velocity: Social sentiment trends (Reddit, Twitter) leading into the call.

Peer Analysis: Earnings results from similar companies that have already reported.

Macro Context: The current BLS Employment Regime for the stock's sector.

Options Sentiment: Unusual call/put activity and Delta Divergence.

2. Historical Reaction Backtest: An event study showing how the stock historically reacted to past beats, meets, and misses (e.g., Avg. 1-Day Gain on BEAT: +4.8%).

3. Implied vs. Historical Move: Compares the options market's implied move (from the straddle price) against the stock's average historical move to identify if options are "cheap" or "expensive."

LLM-Based Predictive Modeler (User-Selectable):

Multi-Model Support: Allows user to select their preferred model via API key (Claude, Gemini, GPT-4, Grok).

Ingests ALL "Digital Landscape" Variables: News, economic data (FRED), political signals (congressional trades), etc.

Correlation Discovery: Models relationships between disparate data.

Price Direction Forecasts: Generates bullish/bearish/neutral outlook.

Arbitrage Scanning Engine:

Statistical Arbitrage (Pairs Trading): Identifies highly correlated/cointegrated asset pairs (e.g., KO vs. PEP).

Crypto Triangular Arbitrage: Scans for price discrepancies across exchanges.

Future Forecasting & Backtesting:

Statistical Forecasting: Prophet-based trend analysis.

Sector Comparison Analysis: Benchmarks the stock's key metrics (P/E, Profit Margin, ROE, Debt/Equity) against its sector and industry averages to provide a relative valuation.

Model Backtesting Engine: Tests historical accuracy of valuation models.

💼 5. Portfolio & Risk Management Dashboard

Top-down portfolio construction and monitoring.

Portfolio Optimization:

Modern Portfolio Theory (MPT): Efficient Frontier analysis.

Optimization Models: Maximum Sharpe Ratio, Minimum Volatility, and Risk Parity.

Asset Allocation & Risk:

Multi-Asset Portfolio Builder: Stocks, crypto, commodities, bonds.

Correlation Matrix Heatmap: Visualizes diversification.

Risk Management Tools: Beta-Neutral strategies and Tail Risk Hedging.

Rebalancing & Monitoring:

Automatic Rebalancing Suggestions: Threshold-based alerts.

Tax-Loss Harvesting Alerts: Identifies losing positions.

Performance Attribution: Shows which holdings contributed to gains/losses.

📊 6. Market Screener & Alerter

A proactive discovery engine to find opportunities across the entire market.
Requires a Polygon.io API key for market-wide scanning.

Earnings Calendar: A filterable list of companies reporting "Today," "This Week," and "Next Week." Clicking a ticker loads the Earnings Play Predictor.

Custom Screener: A UI to build screens using the platform's unique data.

Example: (Tier-3: Volume Profile = Bullish) AND (Zero-FCF: Rule of 40 > 50) AND (Options: Delta Divergence = Bullish)

Pre-built Screens: "Top Squeeze Candidates," "Ape Engine Strong Buys," "Bullish BLS Sector Growth."

Real-Time Alert System: Allows users to create "push" notifications (Email/SMS).

Event Alerts: Monitor SEC 8-K (Material Event) RSS Feeds for instant alerts on major corporate news.

Screen Alerts: Get an alert when a new stock matches one of your saved screens.

⚙️ 7. Signal & Strategy Backtester

Answers the question: "Which signals actually work for this stock?"
Requires a Polygon.io API key for historical data processing.

This dashboard unifies all backtesting logic into one powerful engine.

Automated Signal Efficacy Engine:

Auto-backtests all signals from the platform against a stock's history.

Signal Sets:

Technicals (60+): RSI < 30, MACD Bullish Cross, Ichimoku Cloud Breakout, etc.

Sentiment: Reddit Score > 70, News Sentiment turns Positive.

"Smart Money": Congressional Buy Detected, Insider Buy Detected.

Options Flow: Unusual Call Volume > 10x OI, Bullish Delta Divergence.

Output: A "Signal Leaderboard" showing the historical Win Rate, Avg. Gain/Loss, and Trade Count for every signal, specific to that stock.

Event-Study Backtesting:

Measures average price movement after a specific event occurs.

Events: Sentiment Spike > 90, Negative News Spike, Insider Buy, and SPY vs. BLS-signal backtest (to see historical win-rates and drawdowns for macro trading).

Multi-Signal Strategy Builder:

A simple UI (no code) to combine signals into a custom strategy.

Example: ENTRY = (RSI < 30) AND (Reddit Sentiment = Bullish) | EXIT = (RSI > 70) OR (Stop Loss = -8%)

The engine runs this custom strategy and provides a full performance report (Sharpe Ratio, Max Drawdown, Equity Curve).

Methodology: Employs robust methods like Walk-Forward Optimization to prevent overfitting and produce more reliable, realistic results.

📊 Data Sources & Predictive Strategy

This platform uses a hybrid data model: yfinance provides a free-access baseline, while a Polygon.io API key unlocks the platform's most powerful, high-speed features.

Data Category

Specific Sources (Free APIs/Libraries)

Predictive Value & Use Case

Market Data (Standard)

yfinance, CoinGecko (Free Tier)

Core OHLCV, volume, options chain. Good for general use and as a fallback.

Market Data (Professional)

Polygon.io (API Key)

High-speed, real-time, and reliable historical market data. Required for the Screener and Backtester.

Fundamental Data

yfinance, Alpha Vantage (Free), Financial Modeling Prep (Free)

Financial statements, earnings, ratios. Inputs for DCF, DDM, relative valuation models.

Economic Data (Macro)

fredapi (Federal Reserve), bls (Bureau of Labor), eia (Energy Info Admin)

Macro trend analysis. Model correlations between CPI, interest rates, unemployment, etc., vs. asset performance.

Political & Insider

housestockwatcher.com / senatestockwatcher.com (Scraping), Finnhub (Free Tier)

Event-driven signals. Track congressional trades as a leading indicator. Monitor corporate insider buy/sell ratios.

Gov. Filings (Free)

SEC EDGAR RSS Feeds (Form 4, 8-K)

Primary source, real-time data. Used for insider trade tracking and material event alerts.

Alternative & Sentiment (API-Based)

praw (Reddit API), snscrape (Twitter/X), StockTwits API, NewsAPI.org (Dev Plan)

High-quality, real-time psychology. Feed sentiment velocity/scores into LLM to detect market shifts.

Alternative & Sentiment (API-Free)

BeautifulSoup + requests scraping of old.reddit.com, Finviz, and Yahoo Finance RSS.

100% free data source. No API keys required. Excellent for core sentiment analysis as a fallback or primary data feed.

Note: Per-source sentiment weights can be customized from the centralized Settings page (⚙️ -> Application Settings) and are persisted to disk at `data/config/settings.json` under the `scopes` key (scopes include `global`, `equity`, and `predictive`).
Adjust weights to emphasize or de-emphasize individual news sources; the UI normalizes and saves them automatically. Use the scope selection to control where weights apply.
- By default the settings are stored locally; to change to a server-backed store set `SETTINGS_STORE_TYPE` to 'server' in your Streamlit secrets and implement a server store in `src/core/settings_store.py`.
Note: For multi-user environments, you can run the optional Flask settings server and migrate current local settings.

Crypto On-Chain

CoinGecko, Blockchain.com API, Glassnode (limited free), ccxt

On-chain metrics, exchange data, and arbitrage scanning.

Local AI Models

transformers, torch

Advanced, high-speed local sentiment analysis (e.g., FinBERT) and NLP.

🛠️ Technology Stack & Requirements

See requirements.txt for full dependencies. The core stack includes streamlit, pandas, yfinance, polygon-python-client, plotly, statsmodels, anthropic, google-generativeai, openai, beautifulsoup4, lxml, ccxt, transformers, torch, and fpdf2.

🚀 Quick Start

1. Prerequisites

Python 3.10 or 3.11

2. Install Dependencies

Install all required packages:
pip install -r requirements.txt

3. Download NLTK Data

(Required for sentiment analysis)
python -c "import nltk; nltk.download('all')"

4. Set Up Environment Variables

Create a .streamlit/secrets.toml file (or a .env file) in your project directory:

# === LLM Selection (Add keys for ALL models you want to use) ===
ANTHROPIC_API_KEY = "your_claude_api_key_here"
GEMINI_API_KEY = "your_gemini_api_key_here"
OPENAI_API_KEY = "your_gpt4_api_key_here"
XAI_API_KEY = "your_grok_api_key_here"

# === RECOMMENDED: Professional Data (OPTIONAL) ===
# Unlocks high-speed data + Dashboards #6 (Screener) & #7 (Backtester)
POLYGON_API_KEY = "your_polygon_api_key_here"

# === RECOMMENDED: Sentiment Analysis (OPTIONAL) ===
# NOTE: The platform can run WITHOUT these keys by using the built-in API-Free Scraper.
REDDIT_CLIENT_ID = "your_reddit_client_id"
REDDIT_CLIENT_SECRET = "your_reddit_client_secret"
REDDIT_USER_AGENT = "AnalysisMaster/1.0"
NEWS_API_KEY = "your_newsapi_key"

# === OPTIONAL: Enhanced Features ===
FINNHUB_API_KEY = "your_finnhub_key"
FMP_API_KEY = "your_fmp_api_key_here"
ALPHA_VANTAGE_KEY = "your_av_key"
FRED_API_KEY = "your_fred_key"
EIA_API_KEY = "your_eia_key"


5. Run the Dashboard

streamlit run main.py

6. Open in Browser

Open http://localhost:8501

Settings Server (optional):
1. Start the Flask settings server (dev):
```powershell
python -m src.server.settings_server
```
2. Set `SETTINGS_STORE_TYPE = 'server'` and `SETTINGS_SERVER_URL = 'http://localhost:5001'` in your Streamlit `secrets.toml`.
3. Optional: Use migration script to post local `data/config/settings.json` to server:
```powershell
python scripts/migrate_settings_to_server.py --server-url http://localhost:5001
```

Additional server endpoints:
- `GET /status/sources?ticker={TICKER}` - Returns per-source status for the provided ticker including `state` (ok/no_data/error), `last_success`, and `last_error`. The endpoint requires `X-API-KEY` header if `SETTINGS_SERVER_API_KEY` is set.

Full Dev Environment (Streamlit, Settings Server, Worker):
-----------------------------------------------
For an easy, single-step way to launch the UI, the settings server, and the LLM worker together on Windows, use the following helper batch file:

```
scripts\start_dev_env.bat
```
This will open three command windows and start each service individually.

For macOS / Linux users, an equivalent cross-platform script is provided:

```bash
scripts/start_dev_env.sh --with-redis --clean-cache
```
This script starts the Streamlit app, Settings API server, and LLM worker in the background and writes logs to `data/logs`.
 
Optional: Redis Queue (Production)
---------------------------------
The queue manager supports an optional Redis-backed backend using `REDIS_URL` in your secrets.
If `REDIS_URL` is set and an accessible Redis server is available, the system uses Redis for the job queue; otherwise it falls back to a disk-backed queue located at `data/queue/`.

To install Redis on Windows for local testing, see: https://redis.io/docs/getting-started/installation/install-redis-on-windows/

If you plan to enable the Redis-backed queue, you'll also need the Python `redis` client installed in your environment:
```
venv\Scripts\pip install redis
```
Note: If you do not install this package or the `REDIS_URL` is not set, the app will fall back to the disk-backed queue automatically.

If you've accidentally committed your `.streamlit/secrets.toml` file to source control, run the included helper script to untrack it from git (it leaves the file on disk):
```
scripts\untrack_secrets.bat
```
```

E2E Tests (Playwright):
1. Install Playwright and dependencies:
```powershell
pip install playwright pytest-playwright
playwright install
```
2. Start the Streamlit app and optionally the settings server.
3. Run Playwright tests:
```powershell
pytest -q tests/e2e -k settings_flow
```
If you only need to run Playwright tests that require browsers, ensure you have installed Playwright and its browsers; use the following to optionally run Playwright tests in CI manually:

```powershell
python -m pip install playwright pytest-playwright
python -m playwright install --with-deps
```

Integration testing (local):

If you want to reproduce integration tests locally, here's a quick checklist and commands.

1. Ensure your Streamlit app is running (e.g., run `streamlit run main.py`).
2. Ensure your optional settings server is running if you depend on server-backed settings.
3. Install test dependencies in the venv and Playwright browsers:

```powershell
%CD%\.venv\Scripts\python.exe -m pip install pytest pytest-playwright
%CD%\.venv\Scripts\python.exe -m playwright install
```

4. Run the E2E tests (Playwright):

```powershell
%CD%\.venv\Scripts\python.exe -m pytest tests/e2e -q
```

Note: Tests may be skipped if the app is not running or the UI doesn't match the selectors expected in the tests.
If you encounter `greenlet`/Playwright-related plugin import errors while running `pytest`, you can either install Playwright & dependencies or disable pytest's plugin auto-load when running unit tests:

Windows (cmd):
```
set PYTEST_DISABLE_PLUGIN_AUTOLOAD=1
.
venv\Scripts\python.exe -m pytest -q
```

macOS / Linux (bash):
```
export PYTEST_DISABLE_PLUGIN_AUTOLOAD=1
.
venv/bin/python -m pytest -q
```

Alternatively, use the helper script `scripts/run_selected_tests_no_playwright.py` (no Playwright plugin auto-load) for targeted test runs.


⚙️ Settings Page: To configure per-source sentiment weights, open the Settings page from the sidebar (⚙️ -> Application Settings). From there you can set weights scoped to `global`, `equity`, or `predictive`. Use 'Session-only override' to apply temporary weights that won't persist to disk.

🎉 You're ready to find alpha!

🔧 Debugging Tools
------------------
- Use the Debug dashboard (⚙️ -> Debug) to `Force Clear All Cache`, inspect `st.session_state`, and see all cache TTLs. This is useful when experimenting with sentiment scoring and caching behavior.
 - Use the Debug dashboard (⚙️ -> Debug) to `Force Clear All Cache`, inspect `st.session_state`, and see all cache TTLs. Also check the new "Source Health" panel to view per-source (`Finviz`, `Yahoo`, `SEC`) `state`, last_success & last_error for a given ticker.
 - Per-source rate limits: You can now set a per-source minimum delay (in seconds) between scrapes for Finviz, Yahoo, and SEC. Configure them in the Settings dashboard under Application Settings per scope.
- Inline help and short tutorials are available throughout the UI via a small ℹ️ icon or expandable sections; click or hover to learn what each analysis uses and how to interpret it.

New Pipelines
-------------
- `src/pipelines/get_sec_rss_feeds.py`: Centralized EDGAR Atom/Feed parsing used by the SEC Form 4 and 8-K scrapers.
- `src/pipelines/get_fmp_data.py`: Financial Modeling Prep (FMP) client helpers for company profiles and analyst consensus (requires `FMP_API_KEY` configured).


📁 Project Structure

AnalysisMaster/
├── main.py                          # Main Streamlit app entry point
├── requirements.txt                 # Python dependencies
├── .streamlit/
│   └── secrets.toml                 # Environment variables (API keys)
│
├── src/
│   ├── dashboards/                  # UI modules for each dashboard
│   │   ├── dashboard_equity.py          # Dashboard 1
│   │   ├── dashboard_options.py         # Dashboard 2
│   │   ├── dashboard_crypto.py          # Dashboard 3
│   │   ├── dashboard_predictive.py      # Dashboard 4 (Inc. Earnings Predictor)
│   │   ├── dashboard_portfolio.py       # Dashboard 5
│   │   ├── dashboard_screener.py        # Dashboard 6 (Inc. Earnings Calendar)
│   │   ├── dashboard_backtester.py      # Dashboard 7
│   │   ├── dashboard_debug.py           # Debug Panel
│   │   └── dashboard_selector.py        # Navigation
│   │
│   ├── pipelines/                   # Data ingestion modules
│   │   ├── get_market_data.py           # yfinance, CoinGecko
│   │   ├── get_polygon_data.py          # Polygon.io professional data feed
│   │   ├── get_economic_data.py         # FRED, BLS, EIA
│   │   ├── get_sentiment_api.py         # Reddit (PRAW), NewsAPI
│   │   ├── get_sentiment_scraper.py     # API-Free Scraper (Finviz, MW, etc.)
│   │   ├── get_political_data.py        # Congressional trades
│   │   └── get_sec_rss_feeds.py         # SEC EDGAR 8-K / Form 4
│   │
│   ├── analysis/                    # Core quantitative engines
│   │   ├── ape_intelligence.py          # "Good Buy" Engine
│   │   ├── valuation_models.py          # Standard DCF
│   │   ├── interactive_dcf.py           # Monte Carlo, Sensitivity, Presets, GAAP
│   │   ├── zero_fcf_valuation.py        # Rule of 40, Unit Economics, Auto-Select
│   │   ├── bls_analysis.py              # BLS employment regime logic
│   │   ├── earnings_predictor.py        # Logic for earnings analysis
│   │   ├── pro_indicator_engine.py      # 7-Tier, 60+ indicator engine
│   │   ├── technical_analysis.py        # Algorithmic pattern detection
│   │   ├── options_analysis.py          # GEX, OI Profile, PCR, Delta Divergence
│   │   ├── risk_management.py           # Sharpe, Sortino, VaR
│   │   ├── predictive_models.py         # LLM (Claude/Gemini/GPT/Grok)
│   │   ├── arbitrage_engine.py          # Pairs trading, triangular
│   │   ├── screener_engine.py           # Logic for market screener
│   V   ├── signal_backtester.py         # Logic for Signal Efficacy Engine
│   │
│   ├── core/                        # App configuration & utilities
│   │   ├── config.py                    # Settings, constants
│   │   ├── design_system.py             # ThemeManager, MetricCardRenderer
│   │   ├── wsb_quotes.py                # Humorous quote generator
│   │   └── cache_manager.py             # Cache control
│   │
│   └── utils/                       # Helper functions
│       ├── helpers.py                   # Formatters, validators
│       ├── global_ai_panel.py           # Floating AI button UI/logic
│       ├── congressional_display.py     # UI for political trades
│       ├── alert_manager.py             # Handles email/SMS alerts
│       ├── report_generator.py          # AI-powered PDF report engine
│       └── bls_display.py               # UI for BLS regime panel
│
├── tests/                           # Unit tests
│   ├── test_valuation.py
│   ├── test_zero_fcf.py             # Test file for Zero FCF engine
│   ├── test_indicators.py           # Test file for Pro Indicators
│   ├── test_earnings_predictor.py   # Test file for Earnings
│   ├── test_backtester.py           # Test file for Signal Efficacy Engine
│   └── test_screener.py             # Test file for Screener
│
└── data/                            # Cached data, logs
    ├── cache/                       # SQLite cache files
    └── logs/                        # Application logs



🧪 Debugging & Diagnostics Panel

- A robust Debug Dashboard is essential for managing multiple live data feeds.

API Status Monitor: Real-time health checks (✅ 200 OK or ❌ 404 ERROR) and quota tracking.

Data Validation Viewer: View raw DataFrames/JSON from any pipeline to spot NaN or None values.

Model Inspector: See intermediate calculations for any model (e.g., FCF, WACC, and Terminal Value for a DCF).

Cache Management Console: "Force Clear All Cache" button.

Live Log Stream: Scrolling text box for real-time INFO, WARNING, ERROR logs in the UI.

Session State Viewer: Displays the entire st.session_state as JSON.

🎯 Consolidated Roadmap

Phase 1: Build Core Dashboards & Pipelines: Implement the 5 core dashboards (Equity, Options, Crypto, Predictive, Portfolio) and all data pipelines (yfinance, FRED, API-Free Scraper, SEC RSS Feeds).

Phase 2: Develop Core Engines: Build the "Ape Intelligence" (Good Buy) engine, Interactive DCF (with Parameter Presets & GAAP/Non-GAAP Toggle), Zero-FCF Engine (with Auto-Select), and algorithmic pattern recognition.

Phase 3: Integrate Advanced Analytics: Roll out the 7-Tier "Pro Indicators" engine (with ML Classifiers, Dark Pool, etc.) and the advanced options charts (GEX, OI Profile, PCR, Moneyness Zone Delta).

Phase 4: Implement Macro & Quant Overlays: Integrate BLS Employment Regime Analysis (with valuation multipliers), Sector Comparison, and Congressional Trades tracking.

Phase 5: Launch Predictive AI Layer: Implement the Earnings Play Predictor, the user-selectable LLM Predictive Modeler, and the "Global AI Consensus" button.

Phase 6: Build Market Screener & Alerter: Implement Dashboard #6 (with Earnings Calendar and 8-K Alerts) to find new opportunities.

Phase 7: Build Signal & Strategy Backtester: Implement Dashboard #7 to auto-backtest all signals (Technicals, Sentiment, BLS, Earnings, etc.) and create the "Signal Leaderboard."

Phase 8: Evolve to AI Co-pilot & Reporting: Refactor the "Global AI" from a "button" into an ambient, context-aware co-pilot. Build the AI-Generated PDF Consensus Report feature using the new Summary/Deep Dive/AI Opinion tab structure.

Phase 9: Professional Data Integration: Refactor data pipelines to use Polygon.io as the primary, high-speed data source (unlocking Screener/Backtester) and keep yfinance as the free fallback.

Phase 10: UX & Finalization: Build the Portfolio Optimization tools and the Debug & Diagnostics Panel. Implement full Mobile Optimization and Keyboard Shortcuts.

⚠️ Disclaimer

For Educational & Research Purposes Only. Not Financial Advice.

All data is obtained from free, public sources and may contain inaccuracies.

All calculations, models, and signals are algorithmic suggestions, not investment recommendations.

Trading and investing carry significant financial risk. Always Do Your Own Research (DYOR).

Past performance is not indicative of future results.

This app is built by apes, for apes. We eat crayons for breakfast. This is a tool to inform your decisions, not replace them. Always do your own research and never invest more than you can afford to lose. 🖍️🦍

📜 License

MIT License - Feel free to use, modify, and distribute. Just don't blame us when you YOLO into 0DTE options. 😅

🚀 TO THE MOON! 🌙