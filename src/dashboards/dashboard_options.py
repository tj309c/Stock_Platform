"""
Options Dashboard - Derivatives & Options Analysis
Provides comprehensive options chain analysis with real-time data, Greeks, and volatility metrics.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta

from src.pipelines.get_market_data import MarketDataPipeline
from src.core.design_system import MetricCardRenderer, ThemeManager, HelpWidget
from src.core.wsb_quotes import WSBQuotes, QuoteCategory
from src.utils.helpers import format_large_number


class OptionsDashboard:
    """
    Options & Derivatives Analysis Dashboard.
    Displays options chains, Greeks, volatility analysis, and options flow.
    """

    def __init__(self):
        self.pipeline = MarketDataPipeline()
        self.quote_generator = WSBQuotes()

    def display(self):
        """Main entry point for the Options Dashboard."""
        st.title("⚡ Derivatives & Options Analysis")

        # Display a motivational WSB quote
        quote = self.quote_generator.get_random_quote(QuoteCategory.OPTIONS)
        st.markdown(f"> *{quote}*")
        st.markdown("---")

        ticker = st.text_input(
            "Enter Stock Ticker",
            value="AAPL",
            help="Enter a stock ticker symbol (e.g., AAPL, TSLA, SPY)"
        ).upper()

        if not ticker:
            st.info("👆 Enter a ticker symbol to start analyzing options data.")
            return

        # Create tabs for different views
        tab1, tab2, tab3 = st.tabs(["📊 Summary", "🔬 Deep Dive", "🤖 AI Opinion"])

        with tab1:
            self._render_summary_tab(ticker)

        with tab2:
            self._render_deep_dive_tab(ticker)

        with tab3:
            self._render_ai_opinion_tab(ticker)

    def _render_summary_tab(self, ticker: str):
        """Render the Summary tab with options chain and key metrics."""
        st.header(f"{ticker} - Options Summary")
        HelpWidget.render_help_tooltip("Options Dashboard shows chains, Greeks, and implied vol analysis. Expand for more explanation of the derived metrics.")
        with st.expander("About this options analysis"):
            st.markdown(
                """
                The Options Dashboard offers:
                - Options chain visualization with strike filters
                - Greeks (Delta, Gamma, Theta, Vega) and implied volatility smile
                - Volume, open interest, and put/call ratio insights
                
                What it uses:
                - Calls to MarketDataPipeline to fetch chain and market data
                - Derived calculations for Greeks and IV where available
                """
            )

        # Fetch options data
        with st.spinner("Fetching options data..."):
            options_data = self.pipeline.get_options_chain(ticker)
            current_price = self.pipeline.get_current_price(ticker)
            company_info = self.pipeline.get_company_info(ticker)

        if not options_data:
            st.error(f"Unable to fetch options data for {ticker}. This ticker may not have options available.")
            return

        # Display current stock price
        st.subheader("Underlying Stock")
        col1, col2, col3 = st.columns(3)

        with col1:
            MetricCardRenderer.render_metric(
                label="Current Price",
                value=f"${current_price:.2f}" if current_price else "N/A"
            )

        with col2:
            if company_info:
                volume = company_info.get('volume', 0)
                MetricCardRenderer.render_metric(
                    label="Volume",
                    value=format_large_number(volume)
                )

        with col3:
            if company_info:
                market_cap = company_info.get('marketCap', 0)
                MetricCardRenderer.render_metric(
                    label="Market Cap",
                    value=format_large_number(market_cap)
                )

        st.markdown("---")

        # Expiration selector
        available_expirations = options_data.get('available_expirations', [])
        if not available_expirations:
            st.warning("No options expirations available for this ticker.")
            return

        selected_expiration = st.selectbox(
            "Select Expiration Date",
            options=available_expirations,
            help="Choose an options expiration date to view the chain"
        )

        # Fetch options for selected expiration
        with st.spinner(f"Loading options chain for {selected_expiration}..."):
            options_data = self.pipeline.get_options_chain(ticker, selected_expiration)

        if not options_data:
            st.error(f"Unable to fetch options chain for expiration {selected_expiration}")
            return

        calls = options_data.get('calls')
        puts = options_data.get('puts')

        if calls is None or puts is None or calls.empty or puts.empty:
            st.warning("No options data available for this expiration.")
            return

        # Calculate days to expiration
        try:
            exp_date = pd.to_datetime(selected_expiration)
            days_to_exp = (exp_date - pd.Timestamp.now()).days
        except:
            days_to_exp = 0

        # Display key options metrics
        st.subheader("Options Chain Overview")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            total_call_volume = calls['volume'].sum() if 'volume' in calls.columns else 0
            MetricCardRenderer.render_metric(
                label="Total Call Volume",
                value=format_large_number(total_call_volume)
            )

        with col2:
            total_put_volume = puts['volume'].sum() if 'volume' in puts.columns else 0
            MetricCardRenderer.render_metric(
                label="Total Put Volume",
                value=format_large_number(total_put_volume)
            )

        with col3:
            pcr = total_put_volume / total_call_volume if total_call_volume > 0 else 0
            MetricCardRenderer.render_metric(
                label="Put/Call Ratio",
                value=f"{pcr:.2f}",
                help_text="Higher ratio indicates more bearish sentiment"
            )

        with col4:
            MetricCardRenderer.render_metric(
                label="Days to Expiration",
                value=str(days_to_exp)
            )

        # Options chain display
        st.markdown("---")
        st.subheader("Options Chain")

        # Add strike range filter
        col1, col2 = st.columns(2)
        with col1:
            show_all = st.checkbox("Show all strikes", value=False)

        if not show_all and current_price:
            # Filter to strikes within 20% of current price
            strike_min = current_price * 0.8
            strike_max = current_price * 1.2
            calls_filtered = calls[(calls['strike'] >= strike_min) & (calls['strike'] <= strike_max)]
            puts_filtered = puts[(puts['strike'] >= strike_min) & (puts['strike'] <= strike_max)]
        else:
            calls_filtered = calls
            puts_filtered = puts

        # Display calls and puts side by side
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**📈 Calls**")
            if not calls_filtered.empty:
                calls_display = self._format_options_table_html(calls_filtered.head(20), current_price)
                st.markdown(calls_display, unsafe_allow_html=True)
            else:
                st.info("No call options in selected range")

        with col2:
            st.markdown("**📉 Puts**")
            if not puts_filtered.empty:
                puts_display = self._format_options_table_html(puts_filtered.head(20), current_price)
                st.markdown(puts_display, unsafe_allow_html=True)
            else:
                st.info("No put options in selected range")

        # Visualization: Open Interest
        st.markdown("---")
        st.subheader("Open Interest Analysis")
        fig = self._create_open_interest_chart(calls_filtered, puts_filtered, current_price)
        st.plotly_chart(fig, width='stretch')

    def _render_deep_dive_tab(self, ticker: str):
        """Render the Deep Dive tab with Greeks and volatility analysis."""
        st.header(f"{ticker} - Options Deep Dive")

        # Fetch options data
        with st.spinner("Fetching options data..."):
            options_data = self.pipeline.get_options_chain(ticker)
            current_price = self.pipeline.get_current_price(ticker)

        if not options_data:
            st.error(f"Unable to fetch options data for {ticker}")
            return

        available_expirations = options_data.get('available_expirations', [])
        if not available_expirations:
            st.warning("No options expirations available.")
            return

        selected_expiration = st.selectbox(
            "Select Expiration Date",
            options=available_expirations,
            key="deep_dive_expiration"
        )

        # Fetch options for selected expiration
        options_data = self.pipeline.get_options_chain(ticker, selected_expiration)
        if not options_data:
            st.error("Unable to fetch options chain")
            return

        calls = options_data.get('calls')
        puts = options_data.get('puts')

        if calls is None or puts is None or calls.empty or puts.empty:
            st.warning("No options data available.")
            return

        # Greeks Analysis
        st.subheader("Greeks Analysis")

        # Check if Greeks are available
        has_greeks = all(col in calls.columns for col in ['delta', 'gamma', 'theta', 'vega'])

        if has_greeks:
            # Display average Greeks for ATM options
            atm_calls = calls[calls['inTheMoney'] == False].head(5) if 'inTheMoney' in calls.columns else calls.head(5)
            atm_puts = puts[puts['inTheMoney'] == False].head(5) if 'inTheMoney' in puts.columns else puts.head(5)

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                avg_delta = atm_calls['delta'].mean() if 'delta' in atm_calls.columns else 0
                MetricCardRenderer.render_metric(
                    label="Avg Call Delta",
                    value=f"{avg_delta:.3f}",
                    help_text="Rate of change of option price with respect to underlying"
                )

            with col2:
                avg_gamma = atm_calls['gamma'].mean() if 'gamma' in atm_calls.columns else 0
                MetricCardRenderer.render_metric(
                    label="Avg Call Gamma",
                    value=f"{avg_gamma:.3f}",
                    help_text="Rate of change of delta"
                )

            with col3:
                avg_theta = atm_calls['theta'].mean() if 'theta' in atm_calls.columns else 0
                MetricCardRenderer.render_metric(
                    label="Avg Call Theta",
                    value=f"{avg_theta:.3f}",
                    help_text="Time decay per day"
                )

            with col4:
                avg_vega = atm_calls['vega'].mean() if 'vega' in atm_calls.columns else 0
                MetricCardRenderer.render_metric(
                    label="Avg Call Vega",
                    value=f"{avg_vega:.3f}",
                    help_text="Sensitivity to volatility changes"
                )

            # Greeks visualization
            st.markdown("---")
            st.subheader("Greeks by Strike")
            fig = self._create_greeks_chart(calls, puts, current_price)
            st.plotly_chart(fig, width='stretch')

        else:
            st.info("Greeks data not available for this ticker. This is common for less liquid options.")

        # Implied Volatility Analysis
        st.markdown("---")
        st.subheader("Implied Volatility Analysis")

        if 'impliedVolatility' in calls.columns and 'impliedVolatility' in puts.columns:
            fig = self._create_iv_chart(calls, puts, current_price)
            st.plotly_chart(fig, width='stretch')

            # IV statistics
            col1, col2 = st.columns(2)
            with col1:
                avg_call_iv = calls['impliedVolatility'].mean() * 100
                MetricCardRenderer.render_metric(
                    label="Avg Call IV",
                    value=f"{avg_call_iv:.2f}%"
                )

            with col2:
                avg_put_iv = puts['impliedVolatility'].mean() * 100
                MetricCardRenderer.render_metric(
                    label="Avg Put IV",
                    value=f"{avg_put_iv:.2f}%"
                )
        else:
            st.info("Implied Volatility data not available.")

        # Volume Analysis
        st.markdown("---")
        st.subheader("Volume & Open Interest")

        if 'volume' in calls.columns and 'openInterest' in calls.columns:
            fig = self._create_volume_chart(calls, puts, current_price)
            st.plotly_chart(fig, width='stretch')
        else:
            st.info("Volume data not available.")

    def _render_ai_opinion_tab(self, ticker: str):
        """Render the AI Opinion tab (placeholder for Phase 5)."""
        st.header(f"{ticker} - AI Options Analysis")

        MetricCardRenderer.render_alert_box(
            message="AI-powered options analysis will be available in Phase 5. This will include earnings play predictions, volatility forecasting, and multi-model consensus.",
            alert_type="info",
            title="🤖 Coming Soon",
            icon="🚀"
        )

        st.markdown("### Planned Features:")
        st.markdown("- **Earnings Play Predictor**: Analyze historical reactions and implied moves")
        st.markdown("- **Volatility Forecast**: Predict IV changes using machine learning")
        st.markdown("- **Options Strategy Recommender**: AI-suggested strategies based on market conditions")
        st.markdown("- **Greeks Sensitivity Analysis**: Dynamic scenario modeling")
        st.markdown("- **Global AI Consensus**: Multi-model opinions from Claude, GPT-4, Gemini, and Grok")

    def _format_options_table(self, df: pd.DataFrame, current_price: float = None) -> pd.DataFrame:
        """Format options DataFrame for display."""
        display_df = df.copy()

        # Select and rename columns for display
        columns_to_show = {
            'strike': 'Strike',
            'lastPrice': 'Last',
            'bid': 'Bid',
            'ask': 'Ask',
            'volume': 'Volume',
            'openInterest': 'Open Int',
            'impliedVolatility': 'IV'
        }

        # Only include columns that exist
        display_cols = {}
        for col, name in columns_to_show.items():
            if col in display_df.columns:
                display_cols[col] = name

        display_df = display_df[list(display_cols.keys())].rename(columns=display_cols)

        # Format numeric columns
        if 'Strike' in display_df.columns:
            display_df['Strike'] = display_df['Strike'].apply(lambda x: f"${x:.2f}")

        for col in ['Last', 'Bid', 'Ask']:
            if col in display_df.columns:
                display_df[col] = display_df[col].apply(lambda x: f"${x:.2f}" if pd.notna(x) else "-")

        for col in ['Volume', 'Open Int']:
            if col in display_df.columns:
                display_df[col] = display_df[col].apply(lambda x: f"{int(x):,}" if pd.notna(x) else "-")

        if 'IV' in display_df.columns:
            display_df['IV'] = display_df['IV'].apply(lambda x: f"{x*100:.1f}%" if pd.notna(x) else "-")

        return display_df

    def _format_options_table_html(self, df: pd.DataFrame, current_price: float = None) -> str:
        """Format options DataFrame as HTML table to avoid pyarrow dependency."""
        # Use the existing formatting method
        display_df = self._format_options_table(df, current_price)

        # Convert to HTML
        html = display_df.to_html(index=False, escape=False, classes='options-table')

        # Build HTML without leading whitespace to avoid Streamlit code block formatting
        styled_html = (
            "<style>"
            ".options-table { width: 100%; border-collapse: collapse; font-family: Arial, Helvetica, sans-serif; font-size: 0.85rem; margin: 0.5rem 0; }"
            ".options-table th, .options-table td { border: 1px solid #ddd; padding: 6px 8px; }"
            ".options-table th { background-color: #f5f5f5; text-align: right; font-weight: 700; font-size: 0.8rem; }"
            ".options-table th:first-child { text-align: left; }"
            ".options-table td { text-align: right; font-size: 0.8rem; }"
            ".options-table tr:nth-child(even) { background-color: #fafafa; }"
            ".options-table tr:hover { background-color: #e8f4f8; }"
            "</style>"
            f'<div class="table-container scrollable-y">{html}</div>'
        )

        return styled_html

    def _create_open_interest_chart(self, calls: pd.DataFrame, puts: pd.DataFrame, current_price: float = None) -> go.Figure:
        """Create a chart showing open interest for calls and puts."""
        fig = go.Figure()

        # Add calls
        if not calls.empty and 'openInterest' in calls.columns:
            fig.add_trace(go.Bar(
                x=calls['strike'],
                y=calls['openInterest'],
                name='Calls',
                marker_color='green',
                hovertemplate='Strike: $%{x:.2f}<br>OI: %{y:,}<extra></extra>'
            ))

        # Add puts
        if not puts.empty and 'openInterest' in puts.columns:
            fig.add_trace(go.Bar(
                x=puts['strike'],
                y=-puts['openInterest'],  # Negative for visual separation
                name='Puts',
                marker_color='red',
                hovertemplate='Strike: $%{x:.2f}<br>OI: %{y:,}<extra></extra>'
            ))

        # Add current price line
        if current_price:
            fig.add_vline(
                x=current_price,
                line_dash="dash",
                line_color="yellow",
                annotation_text="Current Price",
                annotation_position="top"
            )

        fig.update_layout(
            title='Open Interest by Strike',
            xaxis_title='Strike Price',
            yaxis_title='Open Interest',
            barmode='relative',
            hovermode='x unified',
            template='plotly_dark',
            height=400
        )

        return fig

    def _create_greeks_chart(self, calls: pd.DataFrame, puts: pd.DataFrame, current_price: float = None) -> go.Figure:
        """Create a chart showing Greeks across strikes."""
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Delta', 'Gamma', 'Theta', 'Vega'),
            vertical_spacing=0.15,
            horizontal_spacing=0.1
        )

        greeks = ['delta', 'gamma', 'theta', 'vega']
        positions = [(1, 1), (1, 2), (2, 1), (2, 2)]

        for greek, (row, col) in zip(greeks, positions):
            if greek in calls.columns:
                # Calls
                fig.add_trace(
                    go.Scatter(
                        x=calls['strike'],
                        y=calls[greek],
                        name=f'Call {greek.title()}',
                        line=dict(color='green'),
                        showlegend=(row == 1 and col == 1)
                    ),
                    row=row, col=col
                )

            if greek in puts.columns:
                # Puts
                fig.add_trace(
                    go.Scatter(
                        x=puts['strike'],
                        y=puts[greek],
                        name=f'Put {greek.title()}',
                        line=dict(color='red'),
                        showlegend=(row == 1 and col == 1)
                    ),
                    row=row, col=col
                )

            # Add current price line
            if current_price:
                fig.add_vline(
                    x=current_price,
                    line_dash="dash",
                    line_color="yellow",
                    row=row, col=col
                )

        fig.update_xaxes(title_text="Strike Price")
        fig.update_layout(
            template='plotly_dark',
            height=600,
            showlegend=True
        )

        return fig

    def _create_iv_chart(self, calls: pd.DataFrame, puts: pd.DataFrame, current_price: float = None) -> go.Figure:
        """Create a chart showing implied volatility smile."""
        fig = go.Figure()

        # Calls IV
        if 'impliedVolatility' in calls.columns:
            fig.add_trace(go.Scatter(
                x=calls['strike'],
                y=calls['impliedVolatility'] * 100,
                name='Call IV',
                mode='lines+markers',
                line=dict(color='green', width=2),
                hovertemplate='Strike: $%{x:.2f}<br>IV: %{y:.2f}%<extra></extra>'
            ))

        # Puts IV
        if 'impliedVolatility' in puts.columns:
            fig.add_trace(go.Scatter(
                x=puts['strike'],
                y=puts['impliedVolatility'] * 100,
                name='Put IV',
                mode='lines+markers',
                line=dict(color='red', width=2),
                hovertemplate='Strike: $%{x:.2f}<br>IV: %{y:.2f}%<extra></extra>'
            ))

        # Add current price line
        if current_price:
            fig.add_vline(
                x=current_price,
                line_dash="dash",
                line_color="yellow",
                annotation_text="Current Price",
                annotation_position="top"
            )

        fig.update_layout(
            title='Implied Volatility Smile',
            xaxis_title='Strike Price',
            yaxis_title='Implied Volatility (%)',
            hovermode='x unified',
            template='plotly_dark',
            height=400
        )

        return fig

    def _create_volume_chart(self, calls: pd.DataFrame, puts: pd.DataFrame, current_price: float = None) -> go.Figure:
        """Create a chart comparing volume and open interest."""
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=('Volume', 'Open Interest'),
            horizontal_spacing=0.1
        )

        # Volume chart
        if 'volume' in calls.columns:
            fig.add_trace(
                go.Bar(x=calls['strike'], y=calls['volume'], name='Call Volume', marker_color='green'),
                row=1, col=1
            )
        if 'volume' in puts.columns:
            fig.add_trace(
                go.Bar(x=puts['strike'], y=-puts['volume'], name='Put Volume', marker_color='red'),
                row=1, col=1
            )

        # Open Interest chart
        if 'openInterest' in calls.columns:
            fig.add_trace(
                go.Bar(x=calls['strike'], y=calls['openInterest'], name='Call OI', marker_color='lightgreen', showlegend=False),
                row=1, col=2
            )
        if 'openInterest' in puts.columns:
            fig.add_trace(
                go.Bar(x=puts['strike'], y=-puts['openInterest'], name='Put OI', marker_color='lightcoral', showlegend=False),
                row=1, col=2
            )

        # Add current price lines
        if current_price:
            for col in [1, 2]:
                fig.add_vline(x=current_price, line_dash="dash", line_color="yellow", row=1, col=col)

        fig.update_xaxes(title_text="Strike Price")
        fig.update_yaxes(title_text="Volume", row=1, col=1)
        fig.update_yaxes(title_text="Open Interest", row=1, col=2)
        fig.update_layout(
            template='plotly_dark',
            height=400,
            barmode='relative'
        )

        return fig
