import streamlit as st
import os
import logging
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
    # Optional exchange keys
    coinbase_api_name = None
    coinbase_private_key = None
    coinbase_api_password = None
    SETTINGS_STORE_TYPE = 'local'
    LLM_SCORING_MODE = 'local'
    REDIS_URL = None

    def __init__(self):
        # ensure cache directory exists
        self.CACHE_DIR.mkdir(parents=True, exist_ok=True)
        # expose secrets for convenience (st.secrets may be a dict-like object)
        # Expose the Streamlit secrets object for compatibility with code expecting cfg.secrets
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
        # Optional exchange credentials for ccxt (e.g., Coinbase)
        # Support both COINBASE_API_NAME and legacy COINBASE_API_KEY naming for backwards compatibility
        # Only override class defaults if streamlit secrets define them (support both historic and new names)
        _cname = st.secrets.get("COINBASE_API_NAME") or st.secrets.get("COINBASE_API_KEY")
        if _cname is not None:
            self.coinbase_api_name = _cname
        _private = st.secrets.get("COINBASE_PRIVATE_KEY") or st.secrets.get("COINBASE_API_SECRET")
        if _private is not None:
            self.coinbase_private_key = _private
        _pass = st.secrets.get("COINBASE_API_PASSWORD") or st.secrets.get("COINBASE_PASSWORD") or st.secrets.get("COINBASE_PASSPHRASE")
        if _pass is not None:
            self.coinbase_api_password = _pass
        # Settings storage type: 'local' (file) or 'server' (future)
        self.SETTINGS_STORE_TYPE = st.secrets.get("SETTINGS_STORE_TYPE", "local")
        # LLM scoring mode: 'local', 'server', 'server-queue'
        self.LLM_SCORING_MODE = st.secrets.get("LLM_SCORING_MODE", "local")
        # Optional Redis url for queue manager: 'redis://...' or empty
        self.REDIS_URL = st.secrets.get("REDIS_URL")
        # Debug logging control: set via environment var ANALYSIS_DEBUG (1/true to enable)
        self.DEBUG_LOGGING = os.getenv('ANALYSIS_DEBUG', '0').lower() in ('1', 'true', 'yes')
        # Optionally read log level for finer control
        self.LOG_LEVEL = os.getenv('APP_LOG_LEVEL', 'INFO').upper()
        if self.DEBUG_LOGGING:
            try:
                logging.getLogger().setLevel(logging.DEBUG)
            except Exception:
                pass
        # Module-level debug control: comma separated names (e.g., 'src.pipelines,get_fmp_data')
        self.DEBUG_MODULES = [m.strip() for m in os.getenv('ANALYSIS_DEBUG_MODULES', '').split(',') if m.strip()]
        if self.DEBUG_MODULES:
            for m in self.DEBUG_MODULES:
                try:
                    logging.getLogger(m).setLevel(logging.DEBUG)
                except Exception:
                    logging.getLogger(__name__).debug("Failed to set debug for module %s", m)
        # Also apply persisted settings if available (read local settings file directly to avoid importing settings_store and circular imports)
        try:
            cfg_file = self.DATA_DIR / 'config' / 'settings.json'
            if cfg_file.exists():
                import json
                pref = json.loads(cfg_file.read_text(encoding='utf-8'))
                scopes = pref.get('scopes', {})
                global_scope = scopes.get('global', {})
                saved_modules = global_scope.get('debug_modules')
                if saved_modules and isinstance(saved_modules, (list, tuple)):
                    for m in saved_modules:
                        if m and m not in self.DEBUG_MODULES:
                            self.DEBUG_MODULES.append(m)
                            try:
                                logging.getLogger(m).setLevel(logging.DEBUG)
                            except Exception:
                                logging.getLogger(__name__).debug("Failed to set debug for persisted module %s", m)
        except Exception:
            pass

        # If important keys are missing in st.secrets, support a developer fallback that reads 'secrets.toml' from the repository root (local dev only)
        try:
            if (not self.fmp_api_key or not self.coinbase_api_name):
                repo_secrets = self.BASE_DIR.parent / 'secrets.toml'
                if repo_secrets.exists():
                    try:
                        # Read via built-in tomllib for 3.11+, fall back to pypi 'toml' if available
                        try:
                            import tomllib as _toml
                            parsed = _toml.loads(repo_secrets.read_text(encoding='utf-8'))
                        except Exception:
                            try:
                                import toml as _toml
                                parsed = _toml.loads(repo_secrets.read_text(encoding='utf-8'))
                            except Exception:
                                parsed = {}
                        # Only override missing secrets; prefer st.secrets
                        if not self.fmp_api_key and 'FMP_API_KEY' in parsed:
                            self.fmp_api_key = parsed['FMP_API_KEY']
                        if not self.coinbase_api_name and 'COINBASE_API_NAME' in parsed:
                            self.coinbase_api_name = parsed['COINBASE_API_NAME']
                        if not self.coinbase_api_name and 'COINBASE_API_KEY' in parsed:
                            self.coinbase_api_name = parsed['COINBASE_API_KEY']
                        if not self.coinbase_private_key and 'COINBASE_PRIVATE_KEY' in parsed:
                            self.coinbase_private_key = parsed['COINBASE_PRIVATE_KEY']
                        if not self.coinbase_private_key and 'COINBASE_API_SECRET' in parsed:
                            self.coinbase_private_key = parsed['COINBASE_API_SECRET']
                        if not self.coinbase_api_password and 'COINBASE_API_PASSWORD' in parsed:
                            self.coinbase_api_password = parsed['COINBASE_API_PASSWORD']
                        if not self.coinbase_api_password and 'COINBASE_PASSWORD' in parsed:
                            self.coinbase_api_password = parsed['COINBASE_PASSWORD']
                        if not self.coinbase_api_password and 'COINBASE_PASSPHRASE' in parsed:
                            self.coinbase_api_password = parsed['COINBASE_PASSPHRASE']
                    except Exception:
                        # Best-effort parsing only
                        pass
        except Exception:
            pass