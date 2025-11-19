PROJECT PLAN: ANALYSIS MASTER - CONSOLIDATED TASK TRACKER

Last Updated: 2025-11-17

STATUS LEGEND:

[COMPLETE] - Task successfully finished.
[IN PROGRESS] - Task is partially complete.
[PENDING] - Task not yet started.

CURRENT STATUS: Phase 0 COMPLETE | Phase 1 IN PROGRESS (80%)

CURRENT PRIORITY: Finish remaining Phase 1 Pipelines and begin Phase 2 Engine Development.

**GUIDING PRINCIPLE: PERFORMANCE-FIRST DESIGN**
All development should prioritize speed and responsiveness. Computationally intensive features (e.g., Monte Carlo simulations, deep backtests) should be designed as optional deep-dives to maintain a fluid user experience, in line with the project's core philosophy.

################################################################################

PHASE 1: CORE DASHBOARDS & PIPELINES (80% Complete)

################################################################################

--- Data Pipelines ---

[COMPLETE] get_sentiment_scraper.py: Implement core sentiment data sources (Finviz, Yahoo, SEC EDGAR).
[COMPLETE] get_sentiment_scraper.py: Implement social media sentiment sources (Reddit, StockTwits, X/Twitter).
[COMPLETE] get_sentiment_scraper.py: Implement mainstream & official news sentiment sources (Google News, Nasdaq).
[PENDING] get_economic_data.py: Implement data fetching from fredapi (for macro) and eia-python (for energy inventories, STEO).
[PENDING] get_fmp_data.py: Implement core FMP pipeline functions: get_company_profile, get_earnings_surprises, get_analyst_consensus, and get_key_metrics.

--- Configuration & Settings ---

[PENDING] Settings UI: Implement server-backed settings storage and Role/ACL logic for multi-user configuration.
[PENDING] Settings UI: Add audit trail/undo history for settings changes.
[PENDING] Debugging: Add automated issue reporting or log collection for maintainers.

NOTE: `AppConfig` (`cfg`) now exposes `cfg.secrets` for compatibility. Additionally, `pro_indicator_engine.py` supports a fallback path for `pandas_ta` versions missing `Strategy`.

################################################################################

PHASE 2: DEVELOP CORE ENGINES (0% Complete)

################################################################################

--- Valuation Models ---

[PENDING] interactive_dcf.py: Implement the GAAP vs. Non-GAAP toggle logic.
[PENDING] interactive_dcf.py: Implement the Parameter Preset Engine (Conservative, Base, Aggressive).
[PENDING] zero_fcf_valuation.py: Implement the Auto-Selection Logic to detect company type for valuation (e.g., Growth, Mature, Financial).

--- Core Analysis ---

[PENDING] ape_intelligence.py: Implement the multi-factor scoring logic (0-100 "Ape Score").
[PENDING] technical_analysis.py: Implement algorithmic pattern recognition for at least 2-3 patterns (e.g., Support/Resistance, Trendlines).

################################################################################

PHASE 3: INTEGRATE ADVANCED ANALYTICS (0% Complete)

################################################################################

--- Pro Indicator Engine ---

[PENDING] pro_indicator_engine.py: Implement the 7-Tier indicator engine with the following statistical layers:

- Tier 1 (Trend): SMA/EMA, VWAP, Parabolic SAR (PSAR), ADX/DMI.

- Tier 2 (Momentum/Oscillators): RSI, MACD, Stochastic Oscillator, CCI (Commodity Channel Index), RVI (Relative Volatility Index).

- Tier 3 (Volatility): Bollinger Bands, Average True Range (ATR), Keltner Channels, Donchian Channels.

- Tier 4 (Volume): OBV (On-Balance Volume), Accumulation/Distribution (A/D) Line, Volume Profile.

[PENDING] dashboard_equity.py: Integrate the Pro Indicator Engine with its visual summary bar and interactive charts.

--- Options Analysis ---

[PENDING] options_analysis.py: Implement the calculation logic for: Gamma Exposure (GEX) Profile, Open Interest (OI) Profile, Historical Put/Call Ratio (PCR), and Delta Divergence.
[PENDING] dashboard_options.py: Integrate the GEX, OI Profile, and PCR charts into the options dashboard.

--- Momentum Analysis ---

[PENDING] driver_analysis.py: Implement "Retail Momentum Score" and "Institutional Momentum Score" time-series scores.
[PENDING] driver_analysis.py: Implement rolling correlation logic between price and each momentum score.
[PENDING] dashboard_equity.py: Add the "Driver Momentum Analysis" chart in the Deep Dive tab.

################################################################################

PHASE 4: IMPLEMENT MACRO & QUANT OVERLAYS (0% Complete)

################################################################################

--- Data Pipelines ---

[PENDING] get_political_data.py: Implement the scraper for congressional stock watchers.

--- Macro Analysis ---

[PENDING] bls_analysis.py: Implement logic to process BLS data and determine the current "employment regime."
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

--- Alerting System ---

[PENDING] alert_manager.py: Implement the logic for sending email/SMS notifications.
[PENDING] dashboard_screener.py: Integrate alert creation (Event Alerts, Screen Alerts) into the UI.

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

[PENDING] test_indicators.py: Write unit tests for the Pro Indicator engine.
[PENDING] test_earnings_predictor.py: Write unit tests for the Earnings Predictor.
[PENDING] test_backtester.py: Write unit tests for the Signal Efficacy Engine.
[PENDING] test_screener.py: Write unit tests for the Screener engine.
[PENDING] test_sentiment_scraper.py: Expand test coverage for network failures and timeouts in sentiment scraper.

--- Final Polish ---

[PENDING] UX: Review and optimize for mobile responsiveness.
[PENDING] UX: Implement keyboard shortcuts for power users.
[PENDING] Code Quality: Final code cleanup and documentation review.
[PENDING] Performance: Profile the entire application to identify and optimize bottlenecks in data pipelines, rendering, and calculations.
[PENDING] CI: Add acceptance tests for Settings UI in CI and snapshot tests covering the preview chart logic.