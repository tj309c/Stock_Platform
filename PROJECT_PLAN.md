PROJECT PLAN: ANALYSIS MASTER - CONSOLIDATED TASK TRACKER

Last Updated: 2025-11-17

STATUS LEGEND:

[PENDING] - Task not yet started.

[COMPLETE] - Task successfully finished.

CURRENT STATUS: Phase 1 COMPLETE | Phase 2 & 3 IN PROGRESS

CURRENT PRIORITY: Finalize core analysis engines and build out remaining dashboards.

################################################################################

PHASE 1: CORE DASHBOARDS & PIPELINES (100% Complete)

################################################################################

--- Data Pipelines ---

[COMPLETE] get_sentiment_scraper.py: Implement SEC EDGAR Form 4 (insider trades) and 8-K (material events) RSS feeds scraper.
[COMPLETE] get_economic_data.py: Implement data fetching from fredapi (for macro) and eia-python (for energy inventories, STEO).
[COMPLETE] get_fmp_data.py: Implement core FMP pipeline functions: get_company_profile, get_earnings_surprises, get_analyst_consensus, and get_key_metrics.
[COMPLETE] get_market_data.py: Implemented `get_historical_pe_ratio` using yfinance TTM EPS (quarterly financials), added `start`/`end` support to `get_stock_price` for date-range requests.

--- Configuration & Settings ---

[PENDING] Settings UI: Implement server-backed settings storage and Role/ACL logic for multi-user configuration.
[PENDING] Settings UI: Add audit trail/undo history for settings changes.
[PENDING] Debugging: Add automated issue reporting or log collection for maintainers.

################################################################################

PHASE 2: DEVELOP CORE ENGINES (50% Complete)

################################################################################

--- Valuation Models ---

[PENDING] interactive_dcf.py: Implement the GAAP vs. Non-GAAP toggle logic.
[COMPLETE] interactive_dcf.py: Implement the Parameter Preset Engine (data-driven defaults for FCF, Growth, WACC).
[PENDING] zero_fcf_valuation.py: Implement the Auto-Selection Logic to detect company type for valuation (e.g., Growth, Mature, Financial).

--- Core Analysis ---

[PENDING] ape_intelligence.py: Implement the multi-factor scoring logic (0-100 "Ape Score").
[PENDING] technical_analysis.py: Implement algorithmic pattern recognition (Support/Resistance engine exists but was reverted from UI).

################################################################################

PHASE 3: INTEGRATE ADVANCED ANALYTICS (75% Complete)

################################################################################

--- Pro Indicator Engine ---

[PENDING] pro_indicator_engine.py: Implement the 7-Tier indicator engine with the following statistical layers:

- [COMPLETE] Tier 1 (Trend): SMA/EMA, VWAP, Parabolic SAR (PSAR), ADX/DMI.

- [COMPLETE] Tier 2 (Momentum/Oscillators): RSI, MACD, Stochastic Oscillator, CCI, RVI, MFI.

- [COMPLETE] Tier 3 (Volatility): Bollinger Bands, Average True Range (ATR), Keltner Channels, Donchian Channels.

- [COMPLETE] Tier 4 (Volume): OBV (On-Balance Volume), Accumulation/Distribution (A/D) Line.

[COMPLETE] dashboard_equity.py: Integrate the Pro Indicator Engine with its visual summary bar and interactive charts.

--- Options Analysis ---

[PENDING] options_analysis.py: Implement the calculation logic for: Gamma Exposure (GEX) Profile, Open Interest (OI) Profile, Historical Put/Call Ratio (PCR), and Delta Divergence.
[PENDING] dashboard_options.py: Integrate the GEX, OI Profile, and PCR charts into the options dashboard.

--- Momentum Analysis ---

[COMPLETE] driver_analysis.py: Implemented as "Digital Landscape Conviction Score" and "Narrative Divergence Index" in pro_indicator_engine.py.
[COMPLETE] dashboard_equity.py: Integrated Conviction Score and Narrative Divergence into the main chart as selectable subplots.
[COMPLETE] dashboard_equity.py: Added the historical P/E fallback (yfinance TTM/trailing EPS) and consolidated overlay/subplot color maps with consistent chart trace colors; added user-facing warning for missing historical P/E.

################################################################################

PHASE 4: IMPLEMENT MACRO & QUANT OVERLAYS (0% Complete)

################################################################################

--- Data Pipelines ---

[PENDING] get_political_data.py: Implement the scraper for congressional stock watchers.

--- Macro Analysis ---

[COMPLETE] bls_analysis.py: Implemented as "Inflation-Adjusted P/E" using FRED CPI data in pro_indicator_engine.py.
[PENDING] eia_analysis.py: Implement logic to process EIA data and determine the current "energy regime."

--- Dashboard Integration ---

[PENDING] interactive_dcf.py: Integrate BLS/EIA regime analysis to adjust valuation multipliers and create "Commodity-Adjusted" presets.
[PENDING] dashboard_equity.py: Add the Sector Comparison Analysis component.
[PENDING] congressional_display.py: Create UI component to display congressional trades and integrate it into dashboard_equity.py.

################################################################################

PHASE 5: LAUNCH PREDICTIVE AI LAYER (0% Complete)

################################################################################

--- Predictive Engine ---

[PENDING] earnings_predictor.py: Implement the Earnings Play Predictor (Surprise Likelihood Score, Historical Reaction Backtest, and Implied vs. Historical Move analysis).
[PENDING] predictive_models.py: Implement the wrapper to call external LLM APIs (Claude, Gemini, GPT-4, Grok) with user-selectable keys.

--- Dashboard & UI ---

[PENDING] dashboard_predictive.py: Build the UI for the Earnings Play Predictor.
[PENDING] dashboard_predictive.py: Build the UI for the LLM-Based Predictive Modeler.
[PENDING] global_ai_panel.py: Implement the "Global AI Consensus" button and its associated logic to query the LLMs.

################################################################################

PHASE 6: BUILD MARKET SCREENER & ALERTER (0% Complete)

################################################################################

--- Data Pipelines ---

[PENDING] get_polygon_data.py: Implement functions for market-wide data fetching from Polygon.io.

--- Screener Engine ---

[PENDING] screener_engine.py: Implement the logic to filter and screen stocks based on custom criteria.

--- Dashboard & UI ---

[PENDING] dashboard_screener.py: Build the Screener UI, including the Earnings Calendar, Custom Screener Builder, pre-built screens, and integration of FMP fundamental data.

################################################################################

PHASE 7: BUILD SIGNAL & STRATEGY BACKTESTER (0% Complete)

################################################################################

--- Backtesting Engine ---

[PENDING] signal_backtester.py: Implement the core backtesting engine with Signal Efficacy, Event-Study, Custom Strategy Builder, Walk-Forward Optimization, and EIA Signals.

--- Dashboard & UI ---

[PENDING] dashboard_backtester.py: Build the UI to display the backtesting results, including the Signal Leaderboard and custom strategy performance reports.

################################################################################

PHASE 8: EVOLVE TO AI CO-PILOT & REPORTING (0% Complete)

################################################################################

--- AI Co-pilot ---

[PENDING] global_ai_panel.py: Refactor AI components to be context-aware (e.g., auto-annotating charts, providing warnings on input).

--- Report Generation ---

[PENDING] report_generator.py: Implement the engine to consolidate all data points for a ticker, use AI Co-pilot to generate analysis, and implement PDF generation/export.

################################################################################

PHASE 9: PROFESSIONAL DATA INTEGRATION (0% Complete)

################################################################################

--- Refactoring ---

[PENDING] Data Pipelines: Modify all modules that fetch market data to prioritize get_polygon_data.py (if key is present) while retaining yfinance as a fallback.
[PENDING] API Handling: Add standardized API key handling for all optional services (Finnhub, FMP, NewsAPI, etc.).

################################################################################

PHASE 10: UX, FINALIZATION, & TESTING (10% Complete)

################################################################################

--- Portfolio Dashboard ---

[PENDING] dashboard_portfolio.py: Implement Rebalancing and Tax-Loss Harvesting alerts.

--- Debugging Panel ---

[PENDING] dashboard_debug.py: Build the Debug Panel UI (API Status, Data Validation, Model Inspector, Cache Management, Live Log Stream, Session State Viewer).

--- Unit & Integration Testing ---

[COMPLETE] test_indicators.py: Write unit tests for the Pro Indicator engine, Conviction Score, and Narrative Divergence.
[COMPLETE] tests: Added deterministic unit tests for yfinance historical P/E fallback and chart color mapping; dashboard PE fallback UI test (headless, monkeypatched Streamlit UI).
[PENDING] test_earnings_predictor.py: Write unit tests for the Earnings Predictor.
[PENDING] test_backtester.py: Write unit tests for the Signal Efficacy Engine.
[PENDING] test_screener.py: Write unit tests for the Screener engine.
[PENDING] test_sentiment_scraper.py: Expand test coverage for network failures and timeouts in sentiment scraper.

--- Final Polish ---

[PENDING] UX: Review and optimize for mobile responsiveness.
[PENDING] UX: Implement keyboard shortcuts for power users.
[PENDING] Code Quality: Final code cleanup and documentation review.
[PENDING] CI: Add acceptance tests for Settings UI in CI and snapshot tests covering the preview chart logic.
[PENDING] CI: Add GitHub Actions workflow for running `pytest` in `tests/unit` and `tests/integration`; include linting and basic coverage reporting.