import streamlit as st
import os
import logging
from pathlib import Path

def get_secret(secret_name: str, default=None):
    """
    Retrieves a secret from Streamlit's secrets.
    This provides a consistent way to access secrets throughout the application.
    Args:
        secret_name (str): The name of the secret to retrieve.
        default: The default value to return if the secret is not found.
    Returns:
        The secret value or the default.
    """
    return st.secrets.get(secret_name, default)

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
    # Prefer Kraken as the default exchange key names, but keep coinbase/binance names for legacy compatibility
    kraken_api_key = None
    kraken_api_secret = None
    kraken_api_password = None
    binance_api_name = None
    binance_private_key = None
    binance_api_password = None
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
        self.anthropic_api_key = get_secret("ANTHROPIC_API_KEY")
        self.gemini_api_key = get_secret("GEMINI_API_KEY")
        self.openai_api_key = get_secret("OPENAI_API_KEY")
        self.xai_api_key = get_secret("XAI_API_KEY")

        # --- Professional Data API Key (Unlocks Screener & Backtester) ---
        self.polygon_api_key = get_secret("POLYGON_API_KEY")

        # --- Other Optional API Keys ---
        self.fred_api_key = get_secret("FRED_API_KEY")
        self.finnhub_api_key = get_secret("FINNHUB_API_KEY")
        self.news_api_key = get_secret("NEWS_API_KEY")
        self.alpha_vantage_api_key = get_secret("ALPHA_VANTAGE_API_KEY")
        self.fmp_api_key = get_secret("FMP_API_KEY")
        self.eia_api_key = get_secret("EIA_API_KEY")

        # --- Social Media API Keys ---
        self.reddit_client_id = get_secret("REDDIT_CLIENT_ID")
        self.reddit_client_secret = get_secret("REDDIT_CLIENT_SECRET")
        self.reddit_user_agent = get_secret("REDDIT_USER_AGENT")
        # Optional exchange credentials for ccxt (prefer KRAKEN; maintain BINANCE/COINBASE for legacy compatibility)
        _kname = get_secret("KRAKEN_API_KEY") or get_secret("KRAKEN_API_NAME") or get_secret("KRAKEN_KEY")
        if _kname is not None:
            self.kraken_api_key = _kname
        _kprivate = get_secret("KRAKEN_API_SECRET") or get_secret("KRAKEN_PRIVATE_KEY") or get_secret("KRAKEN_SECRET")
        if _kprivate is not None:
            self.kraken_api_secret = _kprivate
        _kpass = get_secret("KRAKEN_API_PASSWORD") or get_secret("KRAKEN_PASSWORD") or get_secret("KRAKEN_PASSPHRASE")
        if _kpass is not None:
            self.kraken_api_password = _kpass
        # Backwards compatibility: if no kraken secrets were provided, allow binance/coinbase-style names to be used
        _preferred = None
        _preferred = get_secret("KRAKEN_API_KEY") or get_secret("KRAKEN_API_NAME") or get_secret("KRAKEN_KEY")
        if not _preferred:
            _preferred = get_secret("BINANCE_API_NAME") or get_secret("BINANCE_API_KEY") or get_secret("BINANCE_KEY")
        if not _preferred:
            _preferred = get_secret("COINBASE_API_NAME") or get_secret("COINBASE_API_KEY")
        if _preferred is not None and not self.kraken_api_key:
            self.kraken_api_key = _preferred
        # Secrets fallback to legacy shapes
        _private = get_secret("KRAKEN_API_SECRET") or get_secret("KRAKEN_PRIVATE_KEY") or get_secret("KRAKEN_SECRET") or get_secret("BINANCE_PRIVATE_KEY") or get_secret("BINANCE_API_SECRET") or get_secret("COINBASE_PRIVATE_KEY") or get_secret("COINBASE_API_SECRET")
        if _private is not None and not self.kraken_api_secret:
            self.kraken_api_secret = _private
        _pass = get_secret("KRAKEN_API_PASSWORD") or get_secret("KRAKEN_PASSWORD") or get_secret("KRAKEN_PASSPHRASE") or get_secret("BINANCE_API_PASSWORD") or get_secret("BINANCE_PASSWORD") or get_secret("BINANCE_PASSPHRASE") or get_secret("COINBASE_API_PASSWORD") or get_secret("COINBASE_PASSWORD") or get_secret("COINBASE_PASSPHRASE")
        if _pass is not None and not self.kraken_api_password:
            self.kraken_api_password = _pass
        # Settings storage type: 'local' (file) or 'server' (future)
        self.SETTINGS_STORE_TYPE = get_secret("SETTINGS_STORE_TYPE", "local")
        # LLM scoring mode: 'local', 'server', 'server-queue'
        self.LLM_SCORING_MODE = get_secret("LLM_SCORING_MODE", "local")
        # Optional Redis url for queue manager: 'redis://...' or empty
        self.REDIS_URL = get_secret("REDIS_URL")
        # Debug logging control: set via environment var ANALYSIS_DEBUG (1/true to enable)
        self.DEBUG_LOGGING = True # os.getenv('ANALYSIS_DEBUG', '0').lower() in ('1', 'true', 'yes')
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
            # Check for FMP or configured exchange keys (prefer Binance for exchange access)
            if (not self.fmp_api_key or not self.binance_api_name):
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
                        # BINANCE preferred in repo-root secrets, but accept COINBASE legacy names
                        if not self.binance_api_name and 'BINANCE_API_NAME' in parsed:
                            self.binance_api_name = parsed['BINANCE_API_NAME']
                        if not self.binance_api_name and 'BINANCE_API_KEY' in parsed:
                            self.binance_api_name = parsed['BINANCE_API_KEY']
                        if not self.binance_private_key and 'BINANCE_PRIVATE_KEY' in parsed:
                            self.binance_private_key = parsed['BINANCE_PRIVATE_KEY']
                        if not self.binance_private_key and 'BINANCE_API_SECRET' in parsed:
                            self.binance_private_key = parsed['BINANCE_API_SECRET']
                        if not self.binance_api_password and 'BINANCE_API_PASSWORD' in parsed:
                            self.binance_api_password = parsed['BINANCE_API_PASSWORD']
                        if not self.binance_api_password and 'BINANCE_PASSWORD' in parsed:
                            self.binance_api_password = parsed['BINANCE_PASSWORD']
                        if not self.binance_api_password and 'BINANCE_PASSPHRASE' in parsed:
                            self.binance_api_password = parsed['BINANCE_PASSPHRASE']
                        # Backwards compatibility: populate from COINBASE keys if present and BINANCE not set
                        if not self.binance_api_name and 'COINBASE_API_NAME' in parsed:
                            self.binance_api_name = parsed['COINBASE_API_NAME']
                        if not self.binance_api_name and 'COINBASE_API_KEY' in parsed:
                            self.binance_api_name = parsed['COINBASE_API_KEY']
                        if not self.binance_private_key and 'COINBASE_PRIVATE_KEY' in parsed:
                            self.binance_private_key = parsed['COINBASE_PRIVATE_KEY']
                        if not self.binance_private_key and 'COINBASE_API_SECRET' in parsed:
                            self.binance_private_key = parsed['COINBASE_API_SECRET']
                        if not self.binance_api_password and 'COINBASE_API_PASSWORD' in parsed:
                            self.binance_api_password = parsed['COINBASE_API_PASSWORD']
                        if not self.binance_api_password and 'COINBASE_PASSWORD' in parsed:
                            self.binance_api_password = parsed['COINBASE_PASSWORD']
                        if not self.binance_api_password and 'COINBASE_PASSPHRASE' in parsed:
                            self.binance_api_password = parsed['COINBASE_PASSPHRASE']
                    except Exception:
                        # Best-effort parsing only
                        pass
        except Exception:
            pass