"""
get_fmp_data.py

Client for fetching data from the Financial Modeling Prep (FMP) API.
Requires an FMP_API_KEY in the secrets.toml file.
"""
import requests
import streamlit as st
from typing import List, Dict, Optional

from src.core.config import AppConfig
from src.core.cache_manager import CacheManager

class FMPDataPipeline:
    """
    Provides methods to fetch data from the Financial Modeling Prep API.
    """
    def __init__(self):
        self.api_key = AppConfig().fmp_api_key
        if not self.api_key:
            st.warning("FMP API key not found. FMP data will be unavailable.", icon="⚠️")
        self.base_url = "https://financialmodelingprep.com/api/v3"

    def _make_request(_self, endpoint: str, params: Optional[Dict] = None) -> Optional[List[Dict]]:
        """Helper function to make requests to the FMP API."""
        if not _self.api_key:
            return None

        if params is None:
            params = {}
        params['apikey'] = _self.api_key

        try:
            response = requests.get(f"{_self.base_url}/{endpoint}", params=params)
            response.raise_for_status()
            data = response.json()
            if isinstance(data, dict) and data.get('Error Message'):
                st.error(f"FMP API Error: {data['Error Message']}")
                return None
            return data
        except requests.exceptions.RequestException as e:
            st.error(f"Failed to fetch data from FMP API endpoint '{endpoint}': {e}")
            return None

    @CacheManager.cache_fundamentals
    def get_company_profile(_self, ticker: str) -> Optional[Dict]:
        """
        Retrieves the company profile for a given ticker.
        """
        endpoint = f"profile/{ticker.upper()}"
        data = _self._make_request(endpoint)
        return data[0] if data else None

    @CacheManager.cache_analysis
    def get_analyst_consensus(_self, ticker: str) -> Optional[Dict]:
        """
        Retrieves analyst ratings and consensus estimates.
        """
        endpoint = f"analyst-estimates/{ticker.upper()}"
        data = _self._make_request(endpoint)
        return data[0] if data else None

    @CacheManager.cache_fundamentals
    def get_earnings_surprises(_self, ticker: str) -> Optional[List[Dict]]:
        """
        Retrieves historical earnings surprises.
        """
        endpoint = f"earnings-surprises/{ticker.upper()}"
        return _self._make_request(endpoint)

    @CacheManager.cache_fundamentals
    def get_key_metrics(_self, ticker: str, period: str = "annual", limit: int = 10) -> Optional[List[Dict]]:
        """
        Retrieves key financial metrics for a company.
        
        Args:
            ticker (str): The stock ticker.
            period (str): 'annual' or 'quarter'.
            limit (int): Number of periods to retrieve.
        """
        endpoint = f"key-metrics/{ticker.upper()}"
        params = {"period": period, "limit": limit}
