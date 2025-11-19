"""
Equity Dashboard - Stock Analysis & Valuation
Provides comprehensive equity analysis with real-time data, charts, and metrics.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from src.pipelines.get_market_data import MarketDataPipeline
from src.pipelines.get_fmp_data import FMPDataPipeline
from src.core.design_system import MetricCardRenderer
from src.core.wsb_quotes import WSBQuotes, QuoteCategory
from src.pipelines.get_sentiment_scraper import SentimentScraper
from src.analysis.interactive_dcf import InteractiveDCF
from src.utils.helpers import format_large_number
from src.analysis.pro_indicator_engine import ProIndicatorEngine
from src.core.cache_manager import CacheManager


@CacheManager.cache_analysis
def _build_price_chart_figure(symbol: str, indicators_df: pd.DataFrame) -> go.Figure:
    """Helper that actually builds a Plotly figure for the given symbol and indicators.

    This function is cached to avoid expensive re-computation when Streamlit re-renders the
    dashboard with the same input data repeatedly.
    """
    fig = make_subplots(
        rows=5, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        subplot_titles=(f'{symbol} Price', 'Volume', 'RSI', 'Stochastic Oscillator', 'MACD'),
        row_heights=[0.55, 0.1, 0.1, 0.1, 0.15]
    )

    x_vals = indicators_df.index
    open_vals = indicators_df['open'].tolist()
    high_vals = indicators_df['high'].tolist()
    low_vals = indicators_df['low'].tolist()
    close_vals = indicators_df['close'].tolist()
    volume_vals = indicators_df['volume'].tolist()

    # Build traces list and rows/cols for faster add_traces
    traces = []
    rows = []
    cols = []

    # Candlestick chart (Price)
    traces.append(go.Candlestick(x=x_vals, open=open_vals, high=high_vals, low=low_vals, close=close_vals, name='Price'))
    rows.append(1)
    cols.append(1)

    # Volume bars
    colors = ['green' if c >= o else 'red' for o, c in zip(open_vals, close_vals)]
    traces.append(go.Bar(x=x_vals, y=volume_vals, name='Volume', marker_color=colors, showlegend=False))
    rows.append(2)
    cols.append(1)

    # RSI Indicator
    rsi_col = next((col for col in indicators_df.columns if 'RSI' in col), None)
    if rsi_col:
        traces.append(go.Scatter(x=x_vals, y=indicators_df[rsi_col].tolist(), name='RSI', line=dict(color='cyan', width=1)))
        rows.append(3)
        cols.append(1)

    # Stochastic Oscillator
    stoch_k_col = next((col for col in indicators_df.columns if 'STOCHk' in col), None)
    stoch_d_col = next((col for col in indicators_df.columns if 'STOCHd' in col), None)
    if stoch_k_col and stoch_d_col:
        traces.append(go.Scatter(x=x_vals, y=indicators_df[stoch_k_col].tolist(), name='%K', line=dict(color='orange', width=1)))
        rows.append(4)
        cols.append(1)
        traces.append(go.Scatter(x=x_vals, y=indicators_df[stoch_d_col].tolist(), name='%D', line=dict(color='blue', width=1)))
        rows.append(4)
        cols.append(1)

    # MACD Indicator
    macd_col = next((col for col in indicators_df.columns if col.startswith('MACD_')), None)
    macdh_col = next((col for col in indicators_df.columns if col.startswith('MACDh_')), None) # Histogram
    macds_col = next((col for col in indicators_df.columns if col.startswith('MACDs_')), None) # Signal

    if macd_col and macdh_col and macds_col:
        # Histogram bars
        macd_colors = ['red' if v < 0 else 'green' for v in indicators_df[macdh_col].tolist()]
        traces.append(go.Bar(x=x_vals, y=indicators_df[macdh_col].tolist(), name='MACD Hist', marker_color=macd_colors))
        rows.append(5)
        cols.append(1)
        # MACD Line
        traces.append(go.Scatter(x=x_vals, y=indicators_df[macd_col].tolist(), name='MACD', line=dict(color='blue', width=1)))
        rows.append(5)
        cols.append(1)
        # Signal Line
        traces.append(go.Scatter(x=x_vals, y=indicators_df[macds_col].tolist(), name='Signal', line=dict(color='orange', width=1)))
        rows.append(5)
        cols.append(1)

    # Add traces in bulk
    fig.add_traces(traces, rows=rows, cols=cols)

    # Build shapes list for horizontal lines (RSI, Stochastic) to avoid multiple add_hline calls
    shapes = []
    if rsi_col:
        shapes.extend([
            dict(type='line', xref='x', yref='y3', x0=x_vals[0], x1=x_vals[-1], y0=70, y1=70, line=dict(dash='dash', color='red', width=1)),
            dict(type='line', xref='x', yref='y3', x0=x_vals[0], x1=x_vals[-1], y0=30, y1=30, line=dict(dash='dash', color='green', width=1)),
        ])
    if stoch_k_col and stoch_d_col:
        shapes.extend([
            dict(type='line', xref='x', yref='y4', x0=x_vals[0], x1=x_vals[-1], y0=80, y1=80, line=dict(dash='dash', color='red', width=1)),
            dict(type='line', xref='x', yref='y4', x0=x_vals[0], x1=x_vals[-1], y0=20, y1=20, line=dict(dash='dash', color='green', width=1)),
        ])

    # Update layout
    fig.update_layout(
        title=f'{symbol} Price & Indicators',
        yaxis_title='Price (USD)',
        yaxis2_title='Volume',
        yaxis3_title='RSI',
        yaxis4_title='Stochastic',
        yaxis5_title='MACD',
        xaxis_rangeslider_visible=False,
        height=900,
        hovermode='x unified',
        template='plotly_dark',
        shapes=shapes
    )

    # Update axes
    fig.update_xaxes(title_text='Date', row=5, col=1)
    if rsi_col:
        fig.update_yaxes(range=[0, 100], row=3, col=1)
    if stoch_k_col:
        fig.update_yaxes(range=[0, 100], row=4, col=1)

    fig.update_layout(legend=dict(
        orientation='h',
        yanchor='bottom',
        y=1.02,
        xanchor='right',
        x=1
    ))
    return fig
from src.core.cache_manager import CacheManager


class EquityDashboard:
    """
    Dashboard for deep-dive analysis of a single equity.
    """

    def __init__(self):
        self.name = "Equity Analysis"
        self.interactive_dcf = InteractiveDCF()
        self.market_pipeline = MarketDataPipeline()
        self.fmp_pipeline = FMPDataPipeline()
        self.sentiment_scraper = SentimentScraper()
        self.indicator_engine = ProIndicatorEngine()

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
        # Fetch data using helper that prefers FMP for core fundamentals and Polygon (if available) for prices
        with st.spinner(f"Fetching data for {ticker}... {WSBQuotes.get_random_quote(QuoteCategory.GENERAL)}"):
            company_info, company_info_error, key_metrics, key_metrics_error, price_data, price_data_error, sentiment_data, sentiment_error = self._fetch_data(ticker)

        # If we can't get basic company info, we can't proceed.
        if company_info is None:
            st.error(f"Error fetching company info for {ticker}: {company_info_error}")
            return

        # Use empty dicts as fallback if parts of the data are missing
        key_metrics = key_metrics or {}
        sentiment_data = sentiment_data or {}

        # Display warnings for non-critical data failures
        if key_metrics_error:
            st.warning(f"Could not fetch key metrics: {key_metrics_error}")
        if price_data_error:
            st.warning(f"Could not fetch price data: {price_data_error}")
        if sentiment_error:
            st.warning(f"Could not fetch sentiment data: {sentiment_error}")

        # Calculate indicators
        if price_data is not None and not price_data.empty:
            # The engine expects lowercase columns
            price_data.columns = [col.lower() for col in price_data.columns]
            indicators_df = self.indicator_engine.calculate_indicators(price_data)
        else:
            indicators_df = None

        # --- Three-tab structure ---
        tab1, tab2, tab3 = st.tabs(["**Summary**", "**Deep Dive**", "**AI Opinion**"])

        with tab1:
            self._render_summary(ticker, company_info, key_metrics, indicators_df, sentiment_data)

        with tab2:
            self._render_deep_dive(ticker, indicators_df)

        with tab3:
            self._render_ai_opinion(ticker)

    def _render_summary(self, ticker, company_info, key_metrics, indicators_df, sentiment_data):
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
        st.subheader("Price & Indicator Chart (1 Year)")
        if indicators_df is not None and not indicators_df.empty:
            fig = self._create_price_chart(ticker, indicators_df)
            st.plotly_chart(fig, use_container_width=True)
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

    def _render_deep_dive(self, ticker, indicators_df):
        """Renders the deep dive tab with more detailed analysis."""
        st.subheader("Deep Dive Analysis")
        st.info("More detailed charts, financial statements, and volume analysis will be available here in a future phase.")
        # Placeholder for future content
        self.interactive_dcf.display()

    def _create_price_chart(self, symbol: str, indicators_df: pd.DataFrame) -> go.Figure:
        """Create an interactive price chart with volume and indicators.

        This method delegates to a cached builder to avoid re-computation during
        repetitive Streamlit re-renders.
        """
        return _build_price_chart_figure(symbol, indicators_df)

    def _render_ai_opinion(self, ticker):
        """Renders the AI opinion tab."""
        st.subheader("Co-pilot's Take")
        st.info("🤖 AI Opinion and analysis for this section are coming in Phase 5!")
        # Placeholder for future content

    def _fetch_data(self, ticker: str):
        """Fetch data for a ticker and return standardized tuples for the UI.

        Returns: (company_info, company_info_error, key_metrics, key_metrics_error,
                  price_data, price_data_error, sentiment_data, sentiment_error)
        """
        company_info = None
        company_info_error = None
        key_metrics = None
        key_metrics_error = None
        price_data = None
        price_data_error = None
        sentiment_data = None
        sentiment_error = None

        # Prefer FMP for company profile
        try:
            company_info = self.fmp_pipeline.get_company_profile(ticker)
        except Exception as e:
            company_info_error = str(e)

        if not company_info:
            try:
                r = self.market_pipeline.get_company_info(ticker)
                if isinstance(r, tuple):
                    company_info, company_info_error = r
                else:
                    company_info = r
                    company_info_error = None
            except Exception as e:
                company_info_error = company_info_error or str(e)

        # Attempt FMP key metrics then fallback to yfinance-based extraction
        try:
            fmp_key_metrics = self.fmp_pipeline.get_key_metrics(ticker)
            if fmp_key_metrics:
                if isinstance(fmp_key_metrics, list):
                    fmp_first = fmp_key_metrics[0] if len(fmp_key_metrics) > 0 else None
                else:
                    fmp_first = fmp_key_metrics
                if fmp_first:
                    key_metrics = {
                        'pe_ratio': fmp_first.get('peRatioTTM') or fmp_first.get('peRatio') or None,
                        'dividend_yield': fmp_first.get('dividendYield') or fmp_first.get('dividend_yield') or None,
                        'market_cap': fmp_first.get('marketCap') or fmp_first.get('market_cap') or None,
                    }
        except Exception as e:
            key_metrics_error = str(e)

        if not key_metrics:
            try:
                r = self.market_pipeline.get_key_metrics(ticker)
                if isinstance(r, tuple):
                    key_metrics, key_metrics_error = r
                else:
                    key_metrics = r
                    key_metrics_error = None
            except Exception as e:
                key_metrics_error = key_metrics_error or str(e)

        # Price data: prefer Polygon (if enabled by MarketDataPipeline) then yfinance
        try:
            r = self.market_pipeline.get_stock_price(ticker, period="1y")
            if isinstance(r, tuple):
                price_data, price_data_error = r
            else:
                price_data = r
                price_data_error = None
        except Exception as e:
            price_data_error = str(e)

        # Sentiment
        try:
            sentiment_data, sentiment_error = self.sentiment_scraper.get_sentiment_for_ticker(ticker)
        except Exception as e:
            sentiment_error = str(e)

        return (
            company_info,
            company_info_error,
            key_metrics,
            key_metrics_error,
            price_data,
            price_data_error,
            sentiment_data,
            sentiment_error,
        )
