"""
Crypto Dashboard - Cryptocurrency Analysis & Trading
Provides comprehensive crypto analysis with real-time data, charts, and market metrics.
"""

import streamlit as st
import textwrap
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
from typing import Dict

from src.pipelines.get_crypto_data import CryptoDataPipeline
from src.core.design_system import MetricCardRenderer, ThemeManager, HelpWidget
from src.utils.helpers import format_large_number
from src.core.wsb_quotes import WSBQuotes, QuoteCategory
from src.analysis.pro_indicator_engine import ProIndicatorEngine


class CryptoDashboard:
    """
    Main cryptocurrency analysis dashboard.
    Displays crypto price data, market metrics, and trading information.
    """

    def __init__(self):
        self.name = "Crypto & Digital Assets"
        self.pipeline = CryptoDataPipeline()
        self.indicator_engine = ProIndicatorEngine()

    def display(self):
        """Main display method for the crypto dashboard."""
        st.title("₿ Crypto & Digital Assets Dashboard")

        # Symbol input in sidebar
        with st.sidebar:
            st.markdown("---")
            st.subheader("Crypto Selection")

            # Popular crypto pairs (Coinbase uses USD pairs)
            popular_pairs = [
                "BTC/USD", "ETH/USD", "SOL/USD", "DOGE/USD",
                "AVAX/USD", "MATIC/USD", "LINK/USD", "UNI/USD"
            ]

            symbol_input = st.selectbox(
                "Select or enter a trading pair",
                options=popular_pairs,
                help="Select a popular pair or enter your own (e.g., BTC/USD)"
            )
            symbol = symbol_input.strip().upper()

        # --- Timeframe Selection ---
        c1, c2 = st.columns(2)
        with c1:
            periods = {"90d": "3 Months", "180d": "6 Months", "1y": "1 Year", "max": "Max"}
            selected_period = st.selectbox("Period", options=list(periods.keys()), format_func=lambda x: periods[x], index=1)
        with c2:
            intervals = {"1h": "Hourly", "4h": "4 Hours", "1d": "Daily", "1w": "Weekly"}
            selected_interval = st.selectbox("Interval", options=list(intervals.keys()), index=2)

        # Map UI selection to pipeline parameters
        limit_map = {"90d": 90, "180d": 180, "1y": 365, "max": 1000}
        limit = limit_map.get(selected_period, 365)
        timeframe = selected_interval

        # --- Data Fetching (once for all tabs) ---
        with st.spinner(f"Fetching data for {symbol}..."):
            ticker_info = self.pipeline.get_ticker_info(symbol)
            price_data = self.pipeline.get_crypto_price(symbol, timeframe=timeframe, limit=limit)
            market_info = self.pipeline.get_market_info(symbol)
            orderbook = self.pipeline.get_orderbook(symbol, limit=20)

            # Standardize column names to lowercase for consistency
            if price_data is not None:
                price_data.columns = [col.lower() for col in price_data.columns]

            if price_data is not None and not price_data.empty:
                indicators_df = self.indicator_engine.calculate_indicators(price_data)
            else:
                indicators_df = None

        # Create tabs
        tab1, tab2, tab3 = st.tabs(["📊 Summary", "🔬 Deep Dive", "🤖 AI Opinion"])

        with tab1:
            self._render_summary_tab(symbol, ticker_info, indicators_df, market_info)

        with tab2:
            # Pass the already fetched data to the deep dive tab
            self._render_deep_dive_tab(symbol, indicators_df, orderbook, market_info)

        with tab3:
            self._render_ai_opinion_tab(symbol)

    def _render_summary_tab(self, symbol: str, ticker_info: Dict, indicators_df: pd.DataFrame, market_info: Dict):
        """Render the Summary tab with key metrics and price chart."""
        st.header(f"{symbol} - Summary")
        HelpWidget.render_help_tooltip("Crypto Dashboard shows on-chain & market metrics and price charts. Expand for more details about the data used here.")
        with st.expander("About this crypto analysis"):
            st.markdown(
                """
                The Crypto Dashboard provides:
                - Price charts with volume and volatility
                - Orderbook and market depth analysis
                - On-chain and market-level metrics where available
                
                Data sources used include public exchange APIs and on-chain explorers, varying by coin and provider.
                """
            )

        # Display a WSB quote
        quote = WSBQuotes.get_random_quote(QuoteCategory.CRYPTO)
        MetricCardRenderer.render_alert_box(
            message=quote,
            alert_type="info",
            title="Crypto Wisdom",
            icon="💭"
        )

        if ticker_info is None or indicators_df is None:
            st.error(f"Unable to fetch data for {symbol}. Please try another symbol.")
            return

        # Display basic info
        base_currency = symbol.split('/')[0] if '/' in symbol else symbol
        quote_currency = symbol.split('/')[1] if '/' in symbol else 'USDT'

        # Calculate price change
        current_price = ticker_info.get('last', 0)
        if indicators_df is not None and not indicators_df.empty:
            start_price = indicators_df['close'].iloc[0]
            price_change = ((current_price - start_price) / start_price) * 100
        else:
            price_change = 0

        # Key metrics row
        st.markdown("---")
        st.subheader("Key Metrics")

        # Always use ticker_info for true 24h metrics to ensure accuracy regardless of selected chart interval.
        high_24h = ticker_info.get('high') or 0
        low_24h = ticker_info.get('low') or 0
        volume_24h = ticker_info.get('volume') or 0
        pct_change = ticker_info.get('percentage') or 0

        metrics = [
            {
                "label": "Current Price",
                "value": f"${current_price:,.2f}" if isinstance(current_price, (int, float)) else "N/A",
                "delta": f"{price_change:+.2f}%" if price_change != 0 else None
            },
            {
                "label": "24h High",
                "value": f"${high_24h:,.2f}" if isinstance(high_24h, (int, float)) else "N/A",
            },
            {
                "label": "24h Low",
                "value": f"${low_24h:,.2f}" if isinstance(low_24h, (int, float)) else "N/A",
            },
            {
                "label": "24h Volume",
                "value": format_large_number(volume_24h),
            },
            {
                "label": "24h Change",
                "value": f"{pct_change:+.2f}%" if pct_change else "N/A",
            }
        ]

        MetricCardRenderer.render_metric_row(metrics)

        # Price chart
        st.markdown("---")
        st.subheader(f"{symbol} Price Chart")

        if indicators_df is not None and not indicators_df.empty:
            fig = self._create_price_chart(symbol, indicators_df)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No price data available for the selected period.")

        # Additional metrics
        st.markdown("---")
        st.subheader("Market Metrics")

        col1, col2, col3, col4 = st.columns(4)

        # Safe extraction with None handling
        bid_price = ticker_info.get('bid') or 0
        ask_price = ticker_info.get('ask') or 0
        spread = ask_price - bid_price if (ask_price and bid_price) else 0

        with col1:
            MetricCardRenderer.render_metric(
                label="Bid Price",
                value=f"${bid_price:,.2f}" if bid_price else "N/A",
            )

        with col2:
            MetricCardRenderer.render_metric(
                label="Ask Price",
                value=f"${ask_price:,.2f}" if ask_price else "N/A",
            )

        with col3:
            MetricCardRenderer.render_metric(
                label="Spread",
                value=f"${spread:,.2f}" if spread else "N/A",
            )

        with col4:
            if market_info:
                taker_fee = (market_info.get('taker_fee') or 0) * 100
                MetricCardRenderer.render_metric(
                    label="Taker Fee",
                    value=f"{taker_fee:.3f}%" if taker_fee else "N/A",
                )

    def _render_deep_dive_tab(self, symbol: str, indicators_df: pd.DataFrame, orderbook: Dict, market_info: Dict):
        """Render the Deep Dive tab with detailed analysis."""
        st.header(f"{symbol} - Deep Dive Analysis")

        # Orderbook Analysis
        st.subheader("Order Book")

        if orderbook:
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("**Bids (Buy Orders)**")
                bids_df = pd.DataFrame(orderbook['bids'], columns=['Price', 'Size'])
                bids_df['Total Value'] = bids_df['Price'] * bids_df['Size']
                # Format with professional styling
                formatted_bids = self._format_orderbook_table(bids_df.head(10))
                st.markdown(formatted_bids, unsafe_allow_html=True)

            with col2:
                st.markdown("**Asks (Sell Orders)**")
                asks_df = pd.DataFrame(orderbook['asks'], columns=['Price', 'Size'])
                asks_df['Total Value'] = asks_df['Price'] * asks_df['Size']
                # Format with professional styling
                formatted_asks = self._format_orderbook_table(asks_df.head(10))
                st.markdown(formatted_asks, unsafe_allow_html=True)

            # Orderbook depth
            st.markdown("**Order Book Depth**")
            fig = self._create_orderbook_chart(orderbook)
            st.plotly_chart(fig, width='stretch')
        else:
            st.warning("Order book data not available.")

        # Technical Analysis
        st.markdown("---")
        st.subheader("Technical Analysis")

        if indicators_df is not None and not indicators_df.empty:
            # Calculate returns and volatility
            returns_df = self.pipeline.calculate_returns(indicators_df)
            volatility_df = self.pipeline.calculate_volatility(indicators_df)

            # Extract summary statistics
            total_return = returns_df['Cumulative_Return'].iloc[-1] * 100 if not returns_df.empty and 'Cumulative_Return' in returns_df.columns else 0

            # Calculate annualized return (365 days for crypto)
            days = len(returns_df)
            years = days / 365  # 365 days for 24/7 crypto markets
            annualized_return = ((1 + returns_df['Cumulative_Return'].iloc[-1]) ** (1 / years) - 1) * 100 if not returns_df.empty and years > 0 else 0

            # Get annualized volatility
            annualized_volatility = volatility_df['Volatility'].iloc[-1] * 100 if not volatility_df.empty and 'Volatility' in volatility_df.columns and not volatility_df['Volatility'].isna().all() else 0

            col1, col2, col3 = st.columns(3)

            with col1:
                MetricCardRenderer.render_metric(
                    label="Total Return",
                    value=f"{total_return:.2f}%",
                    delta=None
                )

            with col2:
                MetricCardRenderer.render_metric(
                    label="Annualized Return",
                    value=f"{annualized_return:.2f}%",
                    delta=None
                )

            with col3:
                MetricCardRenderer.render_metric(
                    label="Annualized Volatility",
                    value=f"{annualized_volatility:.2f}%",
                    delta=None
                )

            # Volume analysis
            st.markdown("---")
            st.subheader("Volume Analysis")

            avg_volume = indicators_df['volume'].mean()
            recent_volume = indicators_df['volume'].iloc[-1]
            volume_change = ((recent_volume - avg_volume) / avg_volume) * 100

            col1, col2 = st.columns(2)

            with col1:
                MetricCardRenderer.render_metric(
                    label="Average Volume",
                    value=format_large_number(avg_volume),
                )

            with col2:
                MetricCardRenderer.render_metric(
                    label="Recent Volume",
                    value=format_large_number(recent_volume),
                    delta=f"{volume_change:+.2f}%"
                )
        else:
            st.warning("No price data available for technical analysis.")

        # Market Info - simplified to show only useful information
        if market_info and market_info.get('active'):
            st.markdown("---")
            st.subheader("Market Information")

            col1, col2, col3 = st.columns(3)

            with col1:
                st.markdown("**Exchange**")
                st.markdown(f"{self.pipeline.exchange_id.title()}")

            with col2:
                st.markdown("**Base / Quote**")
                base = market_info.get('base', 'N/A')
                quote = market_info.get('quote', 'N/A')
                st.markdown(f"{base} / {quote}")

            with col3:
                st.markdown("**Status**")
                status = "Active ✓" if market_info.get('active') else "Inactive"
                st.markdown(f"{status}")

    def _render_ai_opinion_tab(self, symbol: str):
        """Render the AI Opinion tab (placeholder for Phase 5)."""
        st.header(f"{symbol} - AI Analysis")

        # WSB-style placeholder
        quote = WSBQuotes.get_random_quote(QuoteCategory.YOLO)
        MetricCardRenderer.render_alert_box(
            message=quote,
            alert_type="info",
            title="AI's Take (Coming Soon)",
            icon="🤖"
        )

        st.info("""
        **AI Opinion Coming in Phase 5!**

        This tab will feature:
        - Multi-model AI consensus (Claude, GPT-4, Gemini, Grok)
        - Contextual analysis of on-chain metrics, sentiment, and technicals
        - Real-time crypto market insights and warnings
        - BUY/HOLD/SELL recommendations based on market data

        Stay tuned for moon missions! 🚀
        """)

        # Placeholder for future AI analysis
        st.markdown("---")
        st.subheader("Preview: What's Coming")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**On-Chain Analysis**")
            st.markdown("- Network activity and hash rate")
            st.markdown("- Wallet distribution analysis")
            st.markdown("- Exchange inflow/outflow tracking")

        with col2:
            st.markdown("**Sentiment & Momentum**")
            st.markdown("- Social media sentiment trends")
            st.markdown("- Fear & Greed Index")
            st.markdown("- Whale wallet activity")

    def _create_price_chart(self, symbol: str, indicators_df: pd.DataFrame) -> go.Figure:
        """Create an interactive price chart with volume."""
        # Create figure with secondary y-axis
        # We'll add subplots for RSI and Stochastic Oscillator
        fig = make_subplots(
            rows=5, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.03,
            subplot_titles=(f'{symbol} Price', 'Volume', 'RSI', 'Stochastic Oscillator', 'MACD'),
            row_heights=[0.55, 0.1, 0.1, 0.1, 0.15]
        )

        # Add candlestick chart
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

        # Add volume bars
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

        # --- Add RSI Indicator ---
        # Column names from pandas-ta are like 'RSI_14'
        rsi_col = next((col for col in indicators_df.columns if 'RSI' in col), None)
        if rsi_col:
            fig.add_trace(
                go.Scatter(x=indicators_df.index, y=indicators_df[rsi_col], name='RSI', line=dict(color='cyan', width=1)),
                row=3, col=1
            )
            # Add overbought/oversold lines for RSI
            fig.add_hline(y=70, line_dash="dash", line_color="red", line_width=1, row=3, col=1)
            fig.add_hline(y=30, line_dash="dash", line_color="green", line_width=1, row=3, col=1)

        # --- Add Stochastic Oscillator ---
        # Column names are like 'STOCHk_14_3_3' and 'STOCHd_14_3_3'
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
            # Add overbought/oversold lines for Stochastic
            fig.add_hline(y=80, line_dash="dash", line_color="red", line_width=1, row=4, col=1)
            fig.add_hline(y=20, line_dash="dash", line_color="green", line_width=1, row=4, col=1)

        # --- Add MACD Indicator ---
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
            yaxis_title='Price (USDT)',
            yaxis2_title='Volume',
            yaxis3_title='RSI',
            yaxis4_title='Stochastic',
            yaxis5_title='MACD',
            xaxis_rangeslider_visible=False,
            height=900,  # Increase height to accommodate new charts
            hovermode='x unified',
            template='plotly_dark'
        )

        # Update axes
        fig.update_xaxes(title_text="Date", row=5, col=1)

        # Set ranges for indicator y-axes
        if rsi_col:
            fig.update_yaxes(range=[0, 100], row=3, col=1)
        if stoch_k_col:
            fig.update_yaxes(range=[0, 100], row=4, col=1)

        # Improve legend
        fig.update_layout(legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ))

        return fig

    def _create_orderbook_chart(self, orderbook: Dict) -> go.Figure:
        """Create an orderbook depth chart."""
        bids = orderbook.get('bids', [])
        asks = orderbook.get('asks', [])

        if not bids or not asks:
            return go.Figure()

        # Convert to DataFrames
        bids_df = pd.DataFrame(bids[:20], columns=['Price', 'Amount'])
        asks_df = pd.DataFrame(asks[:20], columns=['Price', 'Amount'])

        # Calculate cumulative amounts
        bids_df['Cumulative'] = bids_df['Amount'].cumsum()
        asks_df['Cumulative'] = asks_df['Amount'].cumsum()

        # Create figure
        fig = go.Figure()

        # Add bids (buy orders)
        fig.add_trace(go.Scatter(
            x=bids_df['Price'],
            y=bids_df['Cumulative'],
            mode='lines',
            name='Bids',
            fill='tozeroy',
            line=dict(color='green', width=2),
            hovertemplate='Price: $%{x:,.2f}<br>Cumulative: %{y:.4f}<extra></extra>'
        ))

        # Add asks (sell orders)
        fig.add_trace(go.Scatter(
            x=asks_df['Price'],
            y=asks_df['Cumulative'],
            mode='lines',
            name='Asks',
            fill='tozeroy',
            line=dict(color='red', width=2),
            hovertemplate='Price: $%{x:,.2f}<br>Cumulative: %{y:.4f}<extra></extra>'
        ))

        fig.update_layout(
            title='Order Book Depth',
            xaxis_title='Price',
            yaxis_title='Cumulative Amount',
            hovermode='x unified',
            template='plotly_dark',
            height=400
        )

        return fig

    def _format_orderbook_table(self, df: pd.DataFrame) -> str:
        """
        Format an orderbook DataFrame with professional styling matching equity dashboard.

        Args:
            df: DataFrame containing orderbook data (Price, Size, Total Value)

        Returns:
            str: Formatted HTML string
        """
        import textwrap

        # Format numbers in the dataframe
        df_display = df.copy()

        # Format each column with appropriate precision
        df_display['Price'] = df_display['Price'].apply(lambda x: f"${x:,.2f}")
        df_display['Size'] = df_display['Size'].apply(lambda x: f"{x:,.8f}")
        df_display['Total Value'] = df_display['Total Value'].apply(lambda x: f"${x:,.2f}")

        # Convert to HTML - use escape=False to render formatted values properly
        html = df_display.to_html(index=False, escape=False, classes='financial-table')

        # Apply the same professional styling as financial statements
        # Use centralized styles from the design system
        styled_html = MetricCardRenderer.get_table_styles() + f'<div class="table-container">{html}</div>'

        return styled_html
