# 🔥 Analysis Master: System Architecture

This document outlines the current and future architecture of the Analysis Master platform. It is intended to be a living document, updated as the platform evolves.

## 1. High-Level Overview

The platform is designed as a modular Streamlit application with optional, decoupled backend services for advanced features.

-   **Frontend (UI Layer):** A pure Streamlit application that serves as the user interface. It's composed of multiple, independent dashboards that are selected via the `DashboardSelector`.
-   **Application Core (`src/core`):** A set of shared, foundational modules for configuration (`AppConfig`), styling (`DesignSystem`), caching (`CacheManager`), and other core utilities like the `WSBQuotes` generator.
-   **Data Layer (`src/pipelines`):** A collection of data pipelines responsible for fetching information from various external sources (APIs, web scraping). All pipelines are designed to be cached to minimize latency and API usage.
-   **Analysis Layer (`src/analysis`):** The core "brains" of the platform. These are pure Python modules that perform quantitative analysis, valuation, and prediction. They are decoupled from the UI and can be used independently.
-   **Backend Services (`src/server` - Optional):** For scalability and advanced features, the platform includes optional backend services that can be run separately:
    -   **Settings Server:** A Flask-based API to manage and persist user settings in a multi-user environment. The app can be configured to use this instead of local file storage.
    -   **LLM Worker:** A background worker that processes computationally expensive LLM scoring jobs from a queue, preventing the UI from blocking.

---

## 2. Component Breakdown

This section details the key modules within the `src` directory.

### `src/dashboards`
-   **Purpose:** Contains all the UI-facing components. Each file generally corresponds to one of the main dashboards.
-   **Key Files:**
    -   `dashboard_selector.py`: The main navigation component in the sidebar.
    -   `dashboard_equity.py`: Equity analysis UI.
    -   `dashboard_options.py`: Options analysis UI.
    -   `dashboard_crypto.py`: Crypto analysis UI.
    -   `dashboard_predictive.py`: Predictive modeling UI.
    -   `dashboard_portfolio.py`: Portfolio management UI.
    -   `dashboard_settings.py`: Centralized settings management UI.
    -   `dashboard_debug.py`: Developer-facing diagnostics panel.

### `src/pipelines`
-   **Purpose:** All data ingestion logic lives here. These modules are responsible for connecting to external sources.
-   **Key Files:**
    -   `get_market_data.py`: Fetches stock and options data (default: `yfinance`).
    -   `get_crypto_data.py`: Fetches cryptocurrency data (default: `ccxt`).
    -   `get_sentiment_scraper.py`: API-free scraper for news headlines (Finviz, Yahoo).
    -   `get_sec_rss_feeds.py`: Scraper for SEC EDGAR RSS feeds (Form 4, 8-K).
    -   `get_fmp_data.py`: Client for Financial Modeling Prep API.
    -   `get_economic_data.py`: Client for FRED and EIA APIs.
    -   `get_political_data.py`: Scraper for congressional trading data.
    -   `llm_scoring.py`: Handles interaction with LLM APIs for sentiment scoring.

### `src/analysis`
-   **Purpose:** Contains the core analytical models and engines. These are pure Python modules that take data and produce insights.
-   **Key Files:**
    -   `valuation_models.py`: Core calculation logic for DCF.
    -   `interactive_dcf.py`: The UI component that uses `valuation_models.py`.
    -   **(Future)** `zero_fcf_valuation.py`: Alternative valuation models.
    -   **(Future)** `ape_intelligence.py`: "Good Buy" scoring engine.
    -   **(Future)** `pro_indicator_engine.py`: 7-tier technical indicator engine.

### `src/core`
-   **Purpose:** Shared, cross-cutting concerns for the entire application.
-   **Key Files:**
    -   `config.py`: Central `AppConfig` class for loading secrets and settings.
    -   `cache_manager.py`: Provides caching decorators (`@CacheManager.cache_market_data`, etc.).
    -   `design_system.py`: `ThemeManager` and `MetricCardRenderer` for consistent UI.
    -   `settings_store.py`: Abstraction for loading/saving settings (local file or server).
    -   `queue_manager.py`: Simple disk-backed or Redis-backed job queue for the LLM worker.

### `src/server`
-   **Purpose:** Optional, standalone backend services.
-   **Key Files:**
    -   `settings_server.py`: A Flask API for managing settings.
    -   `llm_worker.py`: The background worker that processes jobs from the `QueueManager`.

---

## 3. Data & Control Flow

### Standard UI Flow
1.  **User** selects a dashboard (e.g., Equity) and enters a ticker.
2.  The **Dashboard** (`dashboard_equity.py`) calls a **Pipeline** (`get_market_data.py`).
3.  The **Pipeline** function checks the **Cache** (`CacheManager`).
4.  If data is not cached or is stale, the **Pipeline** fetches it from the **External Source** (e.g., `yfinance` API).
5.  The **Pipeline** returns the data to the **Dashboard**.
6.  The **Dashboard** may pass this data to an **Analysis Engine** (`valuation_models.py`) for computation.
7.  The **Dashboard** renders the results using the **Design System** (`MetricCardRenderer`).

### Asynchronous LLM Scoring Flow
1.  A **Dashboard** or **Pipeline** needs to score a batch of headlines.
2.  It calls `llm_scoring.score_texts_with_llm()`.
3.  If configured for `server-queue` mode, this function makes a POST request to `/score/submit` on the **Settings Server**.
4.  The **Settings Server** creates a new job in the **Queue Manager** (`QueueManager`) and returns a `job_id`.
5.  The **LLM Worker** (`llm_worker.py`), running in a separate process, polls the queue, finds the job, and processes it by calling the LLM API.
6.  The **Worker** writes the results back to the job file via the **Queue Manager**.
7.  The original caller polls the `/score/poll/<job_id>` endpoint until the job status is `complete` and then retrieves the results.

---

## 4. Architectural Evolution ("To-Be" State)

The architecture is designed to evolve from a simple, all-in-one Streamlit app to a more robust, multi-service system.

-   **From Local to Server Settings:** By changing `SETTINGS_STORE_TYPE` from `local` to `server` in `secrets.toml`, the app will use the Flask API for all settings, enabling multi-user configurations without file-based conflicts.
-   **From Free to Professional Data:** The pipelines will be refactore-d to prioritize professional data sources (e.g., Polygon.io) if an API key is present, while retaining the free sources (`yfinance`) as a reliable fallback. This unlocks high-performance features like the Market Screener and Backtester.
-   **Decoupling Heavy Computation:** More computationally intensive tasks, like backtesting or Monte Carlo simulations, can be offloaded to background workers using the existing `QueueManager` pattern established for LLM scoring.