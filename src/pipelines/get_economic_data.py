"""
get_economic_data.py
Client for fetching economic data from FRED (Federal Reserve) and EIA (Energy Info Admin).
Requires FRED_API_KEY and EIA_API_KEY in the secrets.toml file.
"""
import requests
import streamlit as st
from typing import Optional, Dict, Any

from src.core.config import AppConfig
from src.core.cache_manager import CacheManager

class EconomicDataPipeline:
    """
    Provides methods to fetch data from various economic data APIs.
    """
    def __init__(self):
        self.fred_api_key = AppConfig().fred_api_key
        self.eia_api_key = AppConfig().eia_api_key
        self.fred_base_url = "https://api.stlouisfed.org/fred"
        self.eia_base_url = "https://api.eia.gov/v2" # Using v2 for EIA

    @CacheManager.cache_economic_data
    def get_fred_series(_self, series_id: str) -> Optional[Dict[str, Any]]:
        """
        Fetch a FRED series by ID.
        Returns a dict with 'series' and optionally 'observations'.
        """
        if not _self.fred_api_key:
            st.warning("FRED API key not found. FRED data will be unavailable.", icon="⚠️")
            return None

        params = {
            "series_id": series_id,
            "api_key": _self.fred_api_key,
            "file_type": "json"
        }
        try:
            response = requests.get(f"{_self.fred_base_url}/series/observations", params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            st.error(f"Failed to fetch FRED series '{series_id}': {e}")
            return None

    @CacheManager.cache_economic_data
    def get_eia_series(_self, series_id: str) -> Optional[Dict[str, Any]]:
        """
        Fetch EIA data for a series ID using the v2 API.
        Returns JSON dict or None.
        """
        if not _self.eia_api_key:
            st.warning("EIA API key not found. EIA data will be unavailable.", icon="⚠️")
            return None

        # EIA API v2 has a different structure
        url = f"{_self.eia_base_url}/{series_id}/data/"
        params = {"api_key": _self.eia_api_key}
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            st.error(f"Failed to fetch EIA series '{series_id}': {e}")
            return None
