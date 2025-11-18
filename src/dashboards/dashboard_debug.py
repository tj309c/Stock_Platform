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
