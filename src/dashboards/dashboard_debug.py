"""
Debug Dashboard
Provides utilities for developers to inspect and control caches and settings.
"""
import streamlit as st
from src.core.cache_manager import CacheManager, CacheConfig
from src.core.design_system import HelpWidget
from src.pipelines.get_sentiment_scraper import SentimentScraper
from src.pipelines.get_sec_rss_feeds import get_cik_for_ticker
import pandas as pd
from src.pipelines.get_market_data import MarketDataPipeline
from src.pipelines.get_fmp_data import FMPDataPipeline
from src.pipelines.get_crypto_data import CryptoDataPipeline
from src.core.config import AppConfig


class DebugDashboard:
    def display(self):
        st.title("🛠️ Debug & Diagnostics")
        st.markdown("Use these tools carefully; they affect cached data and app state.")
        st.header("Cache Controls")
        HelpWidget.render_help_tooltip("Tools here clear or inspect caches which affects what data is displayed and app performance. Use for debugging.")
        with st.expander("What does clearing the cache do?"):
            st.markdown(
                """
                Clearing caches will remove stored API results and LLM scores, forcing a re-fetch from remote sources on next access. This is useful when testing or debugging but may increase API request usage and latency.
                The 'Force Clear All Cache' button targets all registered cache stores; 'Clear Sentiment Cache Only' targets the sentiment/news cache specifically.
                """
            )
        st.write("TTL configuration for caches:")
        st.table({
            'cache': ['market', 'news', 'sentiment', 'analysis'],
            'ttl_seconds': [CacheConfig.MARKET_DATA_TTL, CacheConfig.NEWS_TTL, CacheConfig.SENTIMENT_TTL, CacheConfig.ANALYSIS_TTL]
        })
        if st.button("Force Clear All Cache"):
            CacheManager.clear_all_cache()
            st.success("Cleared all Streamlit caches via CacheManager.clear_all_cache().")
        if st.button("Clear Sentiment Cache Only"):
            cm = CacheManager()
            cm.clear_all_cache()
            st.success("Cleared sentiment/news cache using CacheManager.clear_all_cache().")

        st.header("Session State")
        if st.button("Show Session State"):
            st.json(st.session_state)

        st.markdown('---')
        st.header('System-Wide Data Source Health')
        st.write('Perform a live check on all major data sources to verify connectivity and configuration.')

        if st.button('Run All Health Checks'):
            with st.spinner('Running health checks...'):
                results = []

                # 1. yfinance (MarketDataPipeline)
                try:
                    if MarketDataPipeline.validate_ticker('AAPL'):
                        results.append({'Source': 'yfinance', 'Status': '✅ OK', 'Details': 'Successfully validated AAPL.'})
                    else:
                        results.append({'Source': 'yfinance', 'Status': '❌ Error', 'Details': 'Failed to validate AAPL.'})
                except Exception as e:
                    results.append({'Source': 'yfinance', 'Status': '❌ Error', 'Details': str(e)})

                # 2. FMP (FMPDataPipeline)
                try:
                    fmp_pipeline = FMPDataPipeline()
                    if not fmp_pipeline.api_key:
                        results.append({'Source': 'FMP', 'Status': '⚠️ Not Configured', 'Details': 'FMP_API_KEY not found.'})
                    else:
                        profile = fmp_pipeline.get_company_profile('AAPL')
                        if profile and profile.get('symbol') == 'AAPL':
                            results.append({'Source': 'FMP', 'Status': '✅ OK', 'Details': 'Successfully fetched AAPL profile.'})
                        else:
                            results.append({'Source': 'FMP', 'Status': '❌ Error', 'Details': 'Failed to fetch valid profile for AAPL.'})
                except Exception as e:
                    results.append({'Source': 'FMP', 'Status': '❌ Error', 'Details': str(e)})

                # 3. Crypto (CryptoDataPipeline)
                try:
                    crypto_pipeline = CryptoDataPipeline()
                    ticker_info = crypto_pipeline.get_ticker_info('BTC/USD')
                    if ticker_info and 'last' in ticker_info:
                        results.append({'Source': 'Crypto (ccxt)', 'Status': '✅ OK', 'Details': 'Successfully fetched BTC/USD ticker.'})
                    else:
                        results.append({'Source': 'Crypto (ccxt)', 'Status': '❌ Error', 'Details': 'Failed to fetch valid ticker for BTC/USD.'})
                except Exception as e:
                    results.append({'Source': 'Crypto (ccxt)', 'Status': '❌ Error', 'Details': str(e)})

                # 4. Sentiment Scraper (Finviz, Yahoo, SEC)
                try:
                    sentiment_scraper = SentimentScraper()
                    _, status = sentiment_scraper.get_headlines_with_status('AAPL')
                    for source, stt in status.items():
                        if stt.get('state') == 'ok':
                            results.append({'Source': f'Sentiment ({source})', 'Status': '✅ OK', 'Details': 'Successfully fetched headlines.'})
                        else:
                            results.append({'Source': f'Sentiment ({source})', 'Status': '❌ Error', 'Details': stt.get('last_error', 'No headlines returned.')})
                except Exception as e:
                    results.append({'Source': 'Sentiment Scraper', 'Status': '❌ Error', 'Details': str(e)})

                # 5. LLM APIs
                config = AppConfig()
                llm_apis = {'OpenAI': config.openai_api_key, 'Anthropic': config.anthropic_api_key, 'Gemini': config.gemini_api_key, 'Groq (XAI)': config.xai_api_key}
                for name, key in llm_apis.items():
                    if key:
                        results.append({'Source': f'LLM ({name})', 'Status': '✅ Configured', 'Details': 'API key is present.'})
                    else:
                        results.append({'Source': f'LLM ({name})', 'Status': '⚠️ Not Configured', 'Details': 'API key not found.'})

                st.table(pd.DataFrame(results))

        st.markdown('---')
        st.header('Source Health')
        st.write('Check the per-source status for a ticker and quick actions to refresh or clear caches if needed.')
        ticker = st.text_input('Ticker (for source status)', value='AAPL')
        source_choice = st.selectbox('Source to inspect', options=['Finviz', 'Yahoo', 'SEC'])
        if st.button('Check Source Health'):
            if not ticker:
                st.error('Please provide a ticker')
            else:
                s = SentimentScraper()
                headlines, status = s.get_headlines_with_status(ticker.upper())
                rows = []
                for src, stt in status.items():
                    row = {'source': src, 'state': stt.get('state'), 'last_success': stt.get('last_success'), 'last_error': stt.get('last_error')}
                    if src == 'SEC':
                        # Resolve CIK if possible for easier triage
                        row['cik'] = get_cik_for_ticker(ticker.upper())
                    rows.append(row)
                if rows:
                    df = pd.DataFrame(rows)
                    st.table(df)
                else:
                    st.write('No source statuses available')
                st.write(f'Headlines fetched: {len(headlines)}')
                if st.button('Clear Sentiment Cache (debug)'):
                    cm = CacheManager()
                    cm.clear_all_cache()
                    st.success('Cleared sentiment/news cache')
                if st.button('Clear Sentiment Cache for ticker (debug)'):
                    cm = CacheManager()
                    cm.clear_all_cache()
                    st.success('Cleared sentiment/news cache for ticker')
                if st.button('Refresh source status'):
                    # Re-run status for this ticker and display the single source
                    s = SentimentScraper()
                    hh, stt = s.get_headlines_with_status(ticker.upper())
                    src_status = stt.get(source_choice, {})
                    if source_choice == 'SEC':
                        src_status['cik'] = get_cik_for_ticker(ticker.upper())
                    st.json({ 'source': source_choice, 'status': src_status })
