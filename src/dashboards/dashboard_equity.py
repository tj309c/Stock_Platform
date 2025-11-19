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
from src.core.design_system import MetricCardRenderer
from src.core.wsb_quotes import WSBQuotes, QuoteCategory
from src.pipelines.get_sentiment_scraper import SentimentScraper
from src.analysis.interactive_dcf import InteractiveDCF
from src.utils.helpers import format_large_number
from src.analysis.pro_indicator_engine import ProIndicatorEngine


class EquityDashboard:
    """
    Dashboard for deep-dive analysis of a single equity.
    """

    def __init__(self):
        self.name = "Equity Analysis"
        self.interactive_dcf = InteractiveDCF()
        self.market_pipeline = MarketDataPipeline()
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
        with st.spinner(f"Fetching data for {ticker}... {WSBQuotes.get_random_quote(QuoteCategory.GENERAL)}"):
            company_info = self.market_pipeline.get_company_info(ticker)
            key_metrics = self.market_pipeline.get_key_metrics(ticker)
            price_data = self.market_pipeline.get_stock_price(ticker, period="1y")
            sentiment_data = self.sentiment_scraper.get_sentiment_for_ticker(ticker)

        if company_info is None:
            st.error(f"Could not retrieve data for ticker '{ticker}'. Please check the ticker and try again.")
            return

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
        """Create an interactive price chart with volume and indicators."""
        fig = make_subplots(
            rows=5, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.03,
            subplot_titles=(f'{symbol} Price', 'Volume', 'RSI', 'Stochastic Oscillator', 'MACD'),
            row_heights=[0.55, 0.1, 0.1, 0.1, 0.15]
        )

        # Candlestick chart
        fig.add_trace(
            go.Candlestick(
                x=indicators_df.index,
                open=indicators_df['open'],
                high=indicators_df['high'],
                low=indicators_df['low'],
                close=indicators_df['close'],
                name='Price'
            ),
            row=1, col=1
        )

        # Volume bars
        colors = np.where(indicators_df['close'] >= indicators_df['open'], 'green', 'red')
        fig.add_trace(
            go.Bar(
                x=indicators_df.index,
                y=indicators_df['volume'],
                name='Volume',
                marker_color=colors,
                showlegend=False
            ),
            row=2, col=1
        )

        # RSI Indicator
        rsi_col = next((col for col in indicators_df.columns if 'RSI' in col), None)
        if rsi_col:
            fig.add_trace(
                go.Scatter(x=indicators_df.index, y=indicators_df[rsi_col], name='RSI', line=dict(color='cyan', width=1)),
                row=3, col=1
            )
            fig.add_hline(y=70, line_dash="dash", line_color="red", line_width=1, row=3, col=1)
            fig.add_hline(y=30, line_dash="dash", line_color="green", line_width=1, row=3, col=1)

        # Stochastic Oscillator
        stoch_k_col = next((col for col in indicators_df.columns if 'STOCHk' in col), None)
        stoch_d_col = next((col for col in indicators_df.columns if 'STOCHd' in col), None)
        if stoch_k_col and stoch_d_col:
            fig.add_trace(
                go.Scatter(x=indicators_df.index, y=indicators_df[stoch_k_col], name='%K', line=dict(color='orange', width=1)),
                row=4, col=1
            )
            fig.add_trace(
                go.Scatter(x=indicators_df.index, y=indicators_df[stoch_d_col], name='%D', line=dict(color='blue', width=1)),
                row=4, col=1
            )
            fig.add_hline(y=80, line_dash="dash", line_color="red", line_width=1, row=4, col=1)
            fig.add_hline(y=20, line_dash="dash", line_color="green", line_width=1, row=4, col=1)

        # MACD Indicator
        macd_col = next((col for col in indicators_df.columns if col.startswith('MACD_')), None)
        macdh_col = next((col for col in indicators_df.columns if col.startswith('MACDh_')), None) # Histogram
        macds_col = next((col for col in indicators_df.columns if col.startswith('MACDs_')), None) # Signal

        if macd_col and macdh_col and macds_col:
            # Histogram bars
            macd_colors = np.where(indicators_df[macdh_col] < 0, 'red', 'green')
            fig.add_trace(
                go.Bar(x=indicators_df.index, y=indicators_df[macdh_col], name='MACD Hist', marker_color=macd_colors),
                row=5, col=1
            )
            # MACD Line
            fig.add_trace(
                go.Scatter(x=indicators_df.index, y=indicators_df[macd_col], name='MACD', line=dict(color='blue', width=1)),
                row=5, col=1
            )
            # Signal Line
            fig.add_trace(
                go.Scatter(x=indicators_df.index, y=indicators_df[macds_col], name='Signal', line=dict(color='orange', width=1)),
                row=5, col=1
            )

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
            template='plotly_dark'
        )

        # Update axes
        fig.update_xaxes(title_text="Date", row=5, col=1)
        if rsi_col:
            fig.update_yaxes(range=[0, 100], row=3, col=1)
        if stoch_k_col:
            fig.update_yaxes(range=[0, 100], row=4, col=1)

        fig.update_layout(legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ))
        return fig

    def _render_ai_opinion(self, ticker):
        """Renders the AI opinion tab."""
        st.subheader("Co-pilot's Take")
        st.info("🤖 AI Opinion and analysis for this section are coming in Phase 5!")
        # Placeholder for future content
