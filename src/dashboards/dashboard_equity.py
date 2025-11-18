"""
Equity Dashboard - Stock Analysis & Valuation
Provides comprehensive equity analysis with real-time data, charts, and metrics.
"""

import streamlit as st
import pandas as pd

from src.pipelines.get_market_data import MarketDataPipeline
from src.core.design_system import MetricCardRenderer
from src.core.wsb_quotes import WSBQuotes, QuoteCategory
from src.pipelines.get_sentiment_scraper import SentimentScraper
from src.analysis.interactive_dcf import InteractiveDCF
from src.utils.helpers import format_large_number


class EquityDashboard:
    """
    Dashboard for deep-dive analysis of a single equity.
    """

    def __init__(self):
        self.name = "Equity Analysis"
        self.interactive_dcf = InteractiveDCF()
        self.market_pipeline = MarketDataPipeline()
        self.sentiment_scraper = SentimentScraper()

    def display(self):
        """Main display method for the equity dashboard."""
        st.title("📈 Equity Analysis Dashboard")
        st.markdown(WSBQuotes.get_random_quote(QuoteCategory.GENERAL))

        # Ticker input in sidebar
        ticker = st.text_input("Enter a stock ticker:", "AAPL", key="equity_ticker_input").upper().strip()

        if not ticker:
            st.warning("Please enter a stock ticker to begin analysis.")
            return

        # --- Data Fetching ---
        with st.spinner(f"Fetching data for {ticker}... {WSBQuotes.get_random_quote(QuoteCategory.GENERAL)}"):
            company_info = self.market_pipeline.get_company_info(ticker)
            key_metrics = self.market_pipeline.get_key_metrics(ticker)
            price_data = self.market_pipeline.get_stock_price(ticker, period="1y")
            sentiment_data = self.sentiment_scraper.get_sentiment_for_ticker(ticker)

        if company_info is None:
            st.error(f"Could not retrieve data for ticker '{ticker}'. Please check the ticker and try again.")
            return

        # --- Three-tab structure ---
        tab1, tab2, tab3 = st.tabs(["**Summary**", "**Deep Dive**", "**AI Opinion**"])

        with tab1:
            self._render_summary(ticker, company_info, key_metrics, price_data, sentiment_data)

        with tab2:
            self._render_deep_dive(ticker, price_data)

        with tab3:
            self._render_ai_opinion(ticker)

    def _render_summary(self, ticker, company_info, key_metrics, price_data, sentiment_data):
        """Renders the summary tab with KPIs and a price chart."""
        st.subheader(f"Summary for {company_info.get('longName', ticker)}")

        # --- KPI Cards ---
        col1, col2 = st.columns([1.5, 1])  # Give more space to the main KPI card
        with col1:
            current_price = company_info.get('currentPrice', 'N/A')
            previous_close = company_info.get('previousClose', 0)
            price_change_val = current_price - previous_close if isinstance(current_price, (int, float)) and isinstance(previous_close, (int, float)) else 0
            price_change_pct = (price_change_val / previous_close * 100) if previous_close else 0

            st.subheader(f"{company_info.get('longName', ticker)} ({ticker.upper()})")
            MetricCardRenderer.render_metric(
                label="Current Price",
                value=f"${current_price:,.2f}" if isinstance(current_price, (int, float)) else "N/A"
            )
            MetricCardRenderer.render_metric(
                label="Change",
                value=f"${price_change_val:+.2f} ({price_change_pct:+.2f}%)",
                help_text="Change since previous close."
            )

        with col2:
            sentiment_score = sentiment_data.get('score', 0.0)
            # Normalize score from [-1, 1] to [0, 100]
            normalized_score = (sentiment_score + 1) * 50
            MetricCardRenderer.render_score_card(
                score=normalized_score,
                max_score=100,
                title="Market Sentiment",
                description=f"Based on {sentiment_data.get('num_headlines', 0)} headlines",
                thresholds={"low": 40, "medium": 60, "high": 100}
            )
            market_cap = company_info.get('marketCap', 'N/A')
            MetricCardRenderer.render_metric(
                label="Market Cap",
                value=format_large_number(market_cap),
                help_text="Total market value of a company's outstanding shares."
            )
            pe_ratio = key_metrics.get('pe_ratio', 'N/A')
            MetricCardRenderer.render_metric(
                label="P/E Ratio (TTM)",
                value=f"{pe_ratio:.2f}" if isinstance(pe_ratio, (int, float)) else "N/A",
                help_text="Price-to-Earnings ratio (Trailing Twelve Months). 'N/A' typically means the company has negative earnings."
            )

        st.markdown("---")

        # --- Price Chart ---
        st.subheader("Price Chart (1 Year)")
        if price_data is not None and not price_data.empty:
            st.line_chart(price_data['Close'], use_container_width=True)
        else:
            st.warning("Could not load price chart.")

        # --- Key Metrics Row ---
        st.subheader("Key Metrics")
        metrics = [
            {"label": "52 Week High", "value": f"${company_info.get('fiftyTwoWeekHigh'):.2f}" if isinstance(company_info.get('fiftyTwoWeekHigh'), (int, float)) else "N/A", "help_text": "Highest price in the last 52 weeks."},
            {"label": "52 Week Low", "value": f"${company_info.get('fiftyTwoWeekLow'):.2f}" if isinstance(company_info.get('fiftyTwoWeekLow'), (int, float)) else "N/A", "help_text": "Lowest price in the last 52 weeks."},
            {"label": "Volume", "value": format_large_number(company_info.get('volume', 'N/A')), "help_text": "Number of shares traded today."},
            {
                "label": "Dividend Yield",
                "value": f"{company_info.get('dividendYield', 0) * 100:.2f}%" if isinstance(company_info.get('dividendYield'), (int, float)) else "N/A",
                "help_text": "Annual dividend per share as a percentage of the stock's price."
            }
        ]
        MetricCardRenderer.render_metric_row(metrics, columns=4)

    def _render_deep_dive(self, ticker, price_data):
        """Renders the deep dive tab with more detailed analysis."""
        st.subheader("Deep Dive Analysis")
        st.info("More detailed charts, financial statements, and volume analysis will be available here in a future phase.")
        # Placeholder for future content
        self.interactive_dcf.display()

    def _render_ai_opinion(self, ticker):
        """Renders the AI opinion tab."""
        st.subheader("Co-pilot's Take")
        st.info("🤖 AI Opinion and analysis for this section are coming in Phase 5!")
        # Placeholder for future content
