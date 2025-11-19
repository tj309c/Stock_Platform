"""
Crypto Dashboard - Cryptocurrency Analysis & Trading
Provides comprehensive crypto analysis with real-time data, charts, and market metrics.
"""

import streamlit as st
import textwrap
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
from typing import Dict

from src.pipelines.get_crypto_data import CryptoDataPipeline
from src.core.design_system import MetricCardRenderer, ThemeManager, HelpWidget
from src.core.wsb_quotes import WSBQuotes, QuoteCategory


class CryptoDashboard:
    """
    Main cryptocurrency analysis dashboard.
    Displays crypto price data, market metrics, and trading information.
    """

    def __init__(self):
        self.name = "Crypto & Digital Assets"
        self.pipeline = CryptoDataPipeline()

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

            # Timeframe selector
            timeframe_options = {
                "1 Hour": "1h",
                "4 Hours": "4h",
                "1 Day": "1d",
                "1 Week": "1w"
            }
            selected_timeframe = st.selectbox(
                "Timeframe",
                options=list(timeframe_options.keys()),
                index=2  # Default to 1 Day
            )
            timeframe = timeframe_options[selected_timeframe]

            # Number of candles
            limit_options = {
                "1 Week": 7,
                "1 Month": 30,
                "3 Months": 90,
                "6 Months": 180,
                "1 Year": 365
            }
            selected_limit = st.selectbox(
                "Period",
                options=list(limit_options.keys()),
                index=2  # Default to 3 Months
            )
            limit = limit_options[selected_limit]

        # Create tabs
        tab1, tab2, tab3 = st.tabs(["📊 Summary", "🔬 Deep Dive", "🤖 AI Opinion"])

        with tab1:
            self._render_summary_tab(symbol, timeframe, limit)

        with tab2:
            self._render_deep_dive_tab(symbol, timeframe, limit)

        with tab3:
            self._render_ai_opinion_tab(symbol)

    def _render_summary_tab(self, symbol: str, timeframe: str, limit: int):
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

        # Fetch current ticker and price data
        with st.spinner(f"Fetching data for {symbol}..."):
            ticker_info = self.pipeline.get_ticker_info(symbol)
            price_data = self.pipeline.get_crypto_price(symbol, timeframe=timeframe, limit=limit)
            market_info = self.pipeline.get_market_info(symbol)

        if ticker_info is None or price_data is None:
            st.error(f"Unable to fetch data for {symbol}. Please try another symbol.")
            return

        # Display basic info
        base_currency = symbol.split('/')[0] if '/' in symbol else symbol
        quote_currency = symbol.split('/')[1] if '/' in symbol else 'USDT'

        # Calculate price change
        current_price = ticker_info.get('last', 0)
        if price_data is not None and not price_data.empty:
            start_price = price_data['Close'].iloc[0]
            price_change = ((current_price - start_price) / start_price) * 100
        else:
            price_change = 0

        # Key metrics row
        st.markdown("---")
        st.subheader("Key Metrics")

        # Calculate 24h metrics from price data (last candle)
        if price_data is not None and not price_data.empty:
            latest_candle = price_data.iloc[-1]
            high_24h = latest_candle['High']
            low_24h = latest_candle['Low']
            volume_24h = latest_candle['Volume']

            # Calculate 24h change
            if len(price_data) >= 2:
                prev_close = price_data['Close'].iloc[-2]
                pct_change = ((current_price - prev_close) / prev_close) * 100
            else:
                pct_change = price_change
        else:
            # Fallback to ticker_info if price_data unavailable
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
                "value": self._format_large_number(volume_24h),
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

        if price_data is not None and not price_data.empty:
            fig = self._create_price_chart(symbol, price_data)
            st.plotly_chart(fig, width='stretch')
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

    def _render_deep_dive_tab(self, symbol: str, timeframe: str, limit: int):
        """Render the Deep Dive tab with detailed analysis."""
        st.header(f"{symbol} - Deep Dive Analysis")

        # Fetch detailed data
        with st.spinner("Fetching detailed data..."):
            price_data = self.pipeline.get_crypto_price(symbol, timeframe=timeframe, limit=limit)
            orderbook = self.pipeline.get_orderbook(symbol, limit=20)
            market_info = self.pipeline.get_market_info(symbol)

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

        if price_data is not None and not price_data.empty:
            # Calculate returns and volatility
            returns_df = self.pipeline.calculate_returns(price_data)
            volatility_df = self.pipeline.calculate_volatility(price_data)

            # Extract summary statistics
            total_return = returns_df['Cumulative_Return'].iloc[-1] * 100 if 'Cumulative_Return' in returns_df.columns else 0

            # Calculate annualized return (365 days for crypto)
            days = len(returns_df)
            years = days / 365  # 365 days for 24/7 crypto markets
            annualized_return = ((1 + returns_df['Cumulative_Return'].iloc[-1]) ** (1 / years) - 1) * 100 if years > 0 else 0

            # Get annualized volatility
            annualized_volatility = volatility_df['Volatility'].iloc[-1] * 100 if 'Volatility' in volatility_df.columns and not volatility_df['Volatility'].isna().all() else 0

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

            avg_volume = price_data['Volume'].mean()
            recent_volume = price_data['Volume'].iloc[-1]
            volume_change = ((recent_volume - avg_volume) / avg_volume) * 100

            col1, col2 = st.columns(2)

            with col1:
                MetricCardRenderer.render_metric(
                    label="Average Volume",
                    value=self._format_large_number(avg_volume),
                )

            with col2:
                MetricCardRenderer.render_metric(
                    label="Recent Volume",
                    value=self._format_large_number(recent_volume),
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

    def _create_price_chart(self, symbol: str, price_data: pd.DataFrame) -> go.Figure:
        """Create an interactive price chart with volume."""
        # Create figure with secondary y-axis
        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.03,
            subplot_titles=(f'{symbol} Price', 'Volume'),
            row_heights=[0.7, 0.3]
        )

        # Add candlestick chart
        fig.add_trace(
            go.Candlestick(
                x=price_data.index,
                open=price_data['Open'],
                high=price_data['High'],
                low=price_data['Low'],
                close=price_data['Close'],
                name='Price'
            ),
            row=1, col=1
        )

        # Add volume bars
        colors = ['red' if price_data['Close'].iloc[i] < price_data['Open'].iloc[i]
                  else 'green' for i in range(len(price_data))]

        fig.add_trace(
            go.Bar(
                x=price_data.index,
                y=price_data['Volume'],
                name='Volume',
                marker_color=colors,
                showlegend=False
            ),
            row=2, col=1
        )

        # Update layout
        fig.update_layout(
            title=f'{symbol} Price & Volume',
            yaxis_title='Price (USDT)',
            yaxis2_title='Volume',
            xaxis_rangeslider_visible=False,
            height=600,
            hovermode='x unified',
            template='plotly_dark'
        )

        # Update axes
        fig.update_xaxes(title_text="Date", row=2, col=1)

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
        # Build HTML without leading whitespace to avoid Streamlit code block formatting
        styled_html = (
            "<style>"
            ".financial-table { width: 100%; border-collapse: collapse; font-family: Arial, Helvetica, sans-serif; font-size: 0.9rem; margin: 0.5rem 0; }"
            ".financial-table th, .financial-table td { border: 1px solid #ddd; padding: 8px 10px; }"
            ".financial-table th { background-color: #f5f5f5; text-align: right; font-weight: 700; }"
            ".financial-table th:first-child { text-align: left; }"
            ".financial-table td { text-align: right; }"
            ".financial-table tr:nth-child(even) { background-color: #fafafa; }"
            "</style>"
            f'<div class="table-container">{html}</div>'
        )

        return styled_html

    @staticmethod
    def _format_large_number(num) -> str:
        """Format large numbers with appropriate suffixes (K, M, B, T)."""
        if num is None:
            return "N/A"

        if num == 0:
            return "$0.00"

        try:
            num = float(num)
            is_negative = num < 0
            abs_num = abs(num)
            sign = "-" if is_negative else ""

            if abs_num >= 1e12:
                return f"{sign}${abs_num/1e12:.2f}T"
            elif abs_num >= 1e9:
                return f"{sign}${abs_num/1e9:.2f}B"
            elif abs_num >= 1e6:
                return f"{sign}${abs_num/1e6:.2f}M"
            elif abs_num >= 1e3:
                return f"{sign}${abs_num/1e3:.2f}K"
            else:
                return f"{sign}${abs_num:.2f}"
        except (ValueError, TypeError):
            return "N/A"
