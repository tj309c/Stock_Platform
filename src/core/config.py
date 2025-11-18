import streamlit as st
from pathlib import Path

class AppConfig:
    """
    A centralized configuration class for the Analysis Master application.
    It loads API keys and settings from Streamlit's secrets management.
    """
    # --- Project Directories ---
    BASE_DIR = Path(__file__).parent.parent.parent
    DATA_DIR = BASE_DIR / "data"
    CACHE_DIR = DATA_DIR / "cache"

    # class level defaults (allow tests to patch attributes on the class without requiring instance)
    anthropic_api_key = None
    gemini_api_key = None
    openai_api_key = None
    xai_api_key = None
    polygon_api_key = None
    fred_api_key = None
    finnhub_api_key = None
    news_api_key = None
    alpha_vantage_api_key = None
    fmp_api_key = None
    eia_api_key = None
    reddit_client_id = None
    reddit_client_secret = None
    reddit_user_agent = None
    SETTINGS_STORE_TYPE = 'local'
    LLM_SCORING_MODE = 'local'
    REDIS_URL = None

    def __init__(self):
        # Ensure cache directory exists
        self.CACHE_DIR.mkdir(parents=True, exist_ok=True)
        # expose secrets for convenience (st.secrets may be a dict-like object)
        self.secrets = st.secrets

        # --- LLM API Keys ---
        self.anthropic_api_key = st.secrets.get("ANTHROPIC_API_KEY")
        self.gemini_api_key = st.secrets.get("GEMINI_API_KEY")
        self.openai_api_key = st.secrets.get("OPENAI_API_KEY")
        self.xai_api_key = st.secrets.get("XAI_API_KEY")

        # --- Professional Data API Key (Unlocks Screener & Backtester) ---
        self.polygon_api_key = st.secrets.get("POLYGON_API_KEY")

        # --- Other Optional API Keys ---
        self.fred_api_key = st.secrets.get("FRED_API_KEY")
        self.finnhub_api_key = st.secrets.get("FINNHUB_API_KEY")
        self.news_api_key = st.secrets.get("NEWS_API_KEY")
        self.alpha_vantage_api_key = st.secrets.get("ALPHA_VANTAGE_API_KEY")
        self.fmp_api_key = st.secrets.get("FMP_API_KEY")
        self.eia_api_key = st.secrets.get("EIA_API_KEY")

        # --- Social Media API Keys ---
        self.reddit_client_id = st.secrets.get("REDDIT_CLIENT_ID")
        self.reddit_client_secret = st.secrets.get("REDDIT_CLIENT_SECRET")
        self.reddit_user_agent = st.secrets.get("REDDIT_USER_AGENT")
        # Settings storage type: 'local' (file) or 'server' (future)
        self.SETTINGS_STORE_TYPE = st.secrets.get("SETTINGS_STORE_TYPE", "local")
        # LLM scoring mode: 'local', 'server', 'server-queue'
        self.LLM_SCORING_MODE = st.secrets.get("LLM_SCORING_MODE", "local")
        # Optional Redis url for queue manager: 'redis://...' or empty
        self.REDIS_URL = st.secrets.get("REDIS_URL")