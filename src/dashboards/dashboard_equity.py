"""
Equity Dashboard - Stock Analysis & Valuation
Provides comprehensive equity analysis with real-time data, charts, and metrics.
"""

import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from src.pipelines.get_market_data import MarketDataPipeline
from src.core.design_system import MetricCardRenderer
from src.core.wsb_quotes import WSBQuotes, QuoteCategory
from src.pipelines.get_sentiment_scraper import SentimentScraper
from src.analysis.pro_indicator_engine import ProIndicatorEngine # Direct import
from src.pipelines.get_fmp_data import FMPDataPipeline
from src.pipelines.get_economic_data import EconomicDataPipeline
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
        self.indicator_engine = ProIndicatorEngine()
        self.fmp_pipeline = FMPDataPipeline()
        self.economic_pipeline = EconomicDataPipeline()

    def display(self):
        """Main display method for the equity dashboard."""
        st.title("📈 Equity Analysis Dashboard")
        st.markdown(WSBQuotes.get_random_quote(QuoteCategory.GENERAL))

        # Ticker input in sidebar
        ticker = st.text_input("Enter a stock ticker:", "AAPL", key="equity_ticker_input").upper().strip()

        if not ticker:
            st.warning("Please enter a stock ticker to begin analysis.")
            return

        # --- Timeframe Selection (now at the top level) ---
        periods = {"3mo": "3 Months", "6mo": "6 Months", "1y": "1 Year", "2y": "2 Years", "5y": "5 Years", "ytd": "YTD", "max": "Max"}
        c_controls_1, c_controls_2 = st.columns([1, 1])
        with c_controls_1:
            period_key = f"equity_period_{ticker}"
            selected_period_key = st.selectbox("Period", options=list(periods.keys()), format_func=lambda x: periods[x], index=2, key=period_key)
        with c_controls_2:
            intervals = {"1d": "Daily", "1wk": "Weekly", "1mo": "Monthly"}
            if selected_period_key in ["3mo", "6mo"]:
                intervals = {"1h": "Hourly", "1d": "Daily", "1wk": "Weekly"}
            interval_key = f"equity_interval_{ticker}"
            selected_interval_key = st.selectbox("Interval", options=list(intervals.keys()), format_func=lambda x: intervals[x], index=0, key=interval_key)

        # --- Data Fetching ---
        with st.spinner(f"Fetching data for {ticker}... {WSBQuotes.get_random_quote(QuoteCategory.GENERAL)}"):
            company_info = self.market_pipeline.get_company_info(ticker)
            key_metrics = self.market_pipeline.get_key_metrics(ticker)
            # Fetch price data based on user selection
            price_data = self.market_pipeline.get_stock_price(ticker, period=selected_period_key, interval=selected_interval_key)
            sentiment_data = self.sentiment_scraper.get_sentiment_for_ticker(ticker)
            historical_metrics = self.fmp_pipeline.get_key_metrics(ticker, period="quarterly", limit=40) # Last 10 years
            financials = self.market_pipeline.get_financials(ticker)

            # Calculate indicators if price data is available
            if price_data is not None and not price_data.empty:
                indicators_df = self.indicator_engine.calculate_indicators(price_data)
                indicators_df = self.indicator_engine.add_market_breadth_indicators(indicators_df, ticker, self.market_pipeline)

                # Merge historical P/E ratio
                if historical_metrics:
                    pe_df = pd.DataFrame(historical_metrics)
                    pe_df['date'] = pd.to_datetime(pe_df['date'])
                    pe_df = pe_df.set_index('date')[['peRatio']]
                    indicators_df = indicators_df.join(pe_df, how='left')
                    indicators_df['peRatio'] = indicators_df['peRatio'].ffill() # Forward fill to have a continuous line

                # Add sentiment score to the dataframe for conviction score calculation
                if sentiment_data:
                    indicators_df['sentiment_score'] = sentiment_data.get('score', 0.0)

                # Calculate the conviction score
                indicators_df = self.indicator_engine.calculate_conviction_score(indicators_df)
                indicators_df = self.indicator_engine.calculate_narrative_divergence(indicators_df)

                # Add macro indicators
                indicators_df = self.indicator_engine.add_macro_indicators(indicators_df, self.economic_pipeline)

                # Add quant indicators
                indicators_df = self.indicator_engine.add_quant_indicators(indicators_df, self.market_pipeline)
            else:
                indicators_df = None

        if company_info is None:
            st.error(f"Could not retrieve data for ticker '{ticker}'. Please check the ticker and try again.")
            return

        # --- Three-tab structure ---
        tab1, tab2, tab3 = st.tabs(["**Summary**", "**Deep Dive**", "**AI Opinion**"])

        with tab1:
            self._render_summary(ticker, company_info, key_metrics, sentiment_data, indicators_df)

        with tab2:
            self._render_deep_dive(ticker, indicators_df, company_info, financials)

        with tab3:
            self._render_ai_opinion(ticker)

        # --- Debug Section ---
        with st.expander("🐞 Debug Output (Developer View)"):
            st.subheader("Raw Data from Pipelines")

            st.markdown("#### Company Info (`yfinance`)")
            st.json(company_info)

            st.markdown("#### Key Metrics (`yfinance`)")
            st.json(key_metrics)

            st.markdown("#### Sentiment Data")
            st.json(sentiment_data)

            st.markdown("#### Historical Metrics (FMP)")
            if historical_metrics:
                st.dataframe(pd.DataFrame(historical_metrics).head())
            else:
                st.write("No historical metrics data from FMP.")

            st.markdown("#### Price Data with Indicators (Chart Input)")
            st.dataframe(indicators_df.head() if indicators_df is not None else "No indicator data frame available.")

    def _render_summary(self, ticker, company_info, key_metrics, sentiment_data, indicators_df):
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

        # --- Key Metrics Row ---
        st.subheader("Key Metrics")
        metrics = [
            {"label": "52-Wk High", "value": f"${company_info.get('fiftyTwoWeekHigh'):.2f}" if isinstance(company_info.get('fiftyTwoWeekHigh'), (int, float)) else "N/A", "help_text": "Highest price in the last 52 weeks."},
            {"label": "52-Wk Low", "value": f"${company_info.get('fiftyTwoWeekLow'):.2f}" if isinstance(company_info.get('fiftyTwoWeekLow'), (int, float)) else "N/A", "help_text": "Lowest price in the last 52 weeks."},
            {"label": "Volume", "value": format_large_number(company_info.get('volume', 'N/A')), "help_text": "Number of shares traded today."},
            {
                "label": "Dividend Yield",
                "value": f"{company_info.get('dividendYield', 0) * 100:.2f}%" if isinstance(company_info.get('dividendYield'), (int, float)) else "N/A",
                "help_text": "Annual dividend per share as a percentage of the stock's price."
            }
        ]
        quant_metrics = []
        if indicators_df is not None and 'BETA_1_5' in indicators_df.columns:
            latest_beta = indicators_df['BETA_1_5'].iloc[-1]
            quant_metrics.append({"label": "Beta", "value": f"{latest_beta:.2f}", "help_text": "Volatility relative to the S&P 500."})

        # Combine and render all metrics
        MetricCardRenderer.render_metric_row(metrics + quant_metrics, columns=len(metrics + quant_metrics))

        st.markdown("---")

        # --- Advanced Chart ---
        st.subheader("Price Chart & Indicators")
        # Friendly UI warning if historical P/E is unavailable in indicators_df
        if indicators_df is None or 'peRatio' not in indicators_df.columns or indicators_df['peRatio'].isna().all():
            MetricCardRenderer.render_alert_box(
                message="Historical P/E data is unavailable (FMP key metrics restricted or API access denied).",
                alert_type="warning",
                title="Historical P/E Unavailable",
                icon="⚠️",
            )

        # --- Indicator Summary Bar ---
        if indicators_df is not None and not indicators_df.empty:
            summary = self.indicator_engine.get_indicator_summary(indicators_df)
            summary_metrics = [
                {"label": "Trend", "value": summary.get('Trend', 'N/A')},
                {"label": "Momentum", "value": summary.get('Momentum', 'N/A')},
                {"label": "Volatility", "value": summary.get('Volatility', 'N/A')},
                {"label": "Volume", "value": summary.get('Volume', 'N/A')},
            ]
            MetricCardRenderer.render_metric_row(summary_metrics)
            st.markdown("---")

        # --- Indicator Selection ---
        overlay_options = ['SMA 20', 'SMA 50', 'EMA 20', 'EMA 50', 'Bollinger Bands', 'Ichimoku Cloud']
        subplot_options = ['Volume', 'RSI', 'MACD', 'Stochastic', 'MFI', 'Historical P/E Ratio', 'Inflation-Adjusted P/E', 'Conviction Score', 'Narrative Divergence']

        c1, c2 = st.columns(2)
        with c1:
            selected_overlays = st.multiselect("Select Overlays", overlay_options, default=['SMA 20', 'EMA 50', 'Ichimoku Cloud'])
        with c2:
            selected_subplots = st.multiselect("Select Subplots", subplot_options, default=['Volume', 'RSI', 'Conviction Score'])

        if indicators_df is not None:
            fig = self._create_advanced_chart(indicators_df, overlays=selected_overlays, subplots=selected_subplots)
            st.plotly_chart(fig, use_container_width=True)
    
    def _calculate_dcf_defaults(self, company_info, financials) -> dict:
        """Derives sensible defaults for the DCF model from fetched data."""
        defaults = {}
        
        # Shares Outstanding
        defaults['shares_outstanding'] = company_info.get('sharesOutstanding', 1_000_000_000)
        
        # Free Cash Flow
        if financials and financials.get('cash_flow') is not None and not financials['cash_flow'].empty:
            cash_flow_df = financials['cash_flow']
            if 'Free Cash Flow' in cash_flow_df.index:
                defaults['fcf'] = cash_flow_df.loc['Free Cash Flow'].iloc[0]

        # Growth Rate (from revenue growth)
        if company_info.get('revenueGrowth') is not None:
            defaults['growth_rate'] = round(company_info['revenueGrowth'] * 100, 2)

        # WACC (simplified CAPM)
        beta = company_info.get('beta', 1.0)
        if beta is not None:
            risk_free_rate = 4.5  # Assumption for 10-year treasury
            market_risk_premium = 5.0  # Standard assumption
            cost_of_equity = risk_free_rate + beta * market_risk_premium
            defaults['wacc'] = round(cost_of_equity, 2)

        return defaults

    def _render_deep_dive(self, ticker, indicators_df, company_info, financials):
        """Renders the deep dive tab with more detailed analysis."""
        st.subheader("Valuation Analysis")

        dcf_defaults = self._calculate_dcf_defaults(company_info, financials)
        self.interactive_dcf.display(defaults=dcf_defaults)

    def _create_advanced_chart(self, df: pd.DataFrame, overlays: list, subplots: list) -> go.Figure:
        """Creates an advanced chart with price, MAs, RSI, and MACD."""
        num_subplots = 1 + len(subplots)
        row_heights = [0.6] + [0.2] * len(subplots)

        fig = make_subplots(
            rows=num_subplots, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.05,
            row_heights=row_heights
        )

        # --- Subplot 1: Price and Moving Averages ---
        fig.add_trace(go.Candlestick(x=df.index, open=df['open'], high=df['high'], low=df['low'], close=df['close'], name='Price'), row=1, col=1)

        if 'SMA 20' in overlays and 'sma_20' in df.columns:
            fig.add_trace(go.Scatter(x=df.index, y=df['sma_20'], name='SMA 20', line=dict(color='orange', width=1)), row=1, col=1)
        if 'SMA 50' in overlays and 'sma_50' in df.columns:
            fig.add_trace(go.Scatter(x=df.index, y=df['sma_50'], name='SMA 50', line=dict(color='yellow', width=1)), row=1, col=1)
        if 'EMA 20' in overlays and 'ema_20' in df.columns:
            fig.add_trace(go.Scatter(x=df.index, y=df['ema_20'], name='EMA 20', line=dict(color='lightblue', width=1)), row=1, col=1)
        if 'EMA 50' in overlays and 'ema_50' in df.columns:
            fig.add_trace(go.Scatter(x=df.index, y=df['ema_50'], name='EMA 50', line=dict(color='cyan', width=1)), row=1, col=1)
        if 'Bollinger Bands' in overlays and 'bbu_20_2.0' in df.columns and 'bbl_20_2.0' in df.columns:
            fig.add_trace(go.Scatter(x=df.index, y=df['bbu_20_2.0'], name='Upper Band', line=dict(color='gray', width=1, dash='dash')), row=1, col=1)
            fig.add_trace(go.Scatter(x=df.index, y=df['bbl_20_2.0'], name='Lower Band', line=dict(color='gray', width=1, dash='dash'), fill='tonexty', fillcolor='rgba(128,128,128,0.1)'), row=1, col=1)
        if 'Ichimoku Cloud' in overlays and 'isa_9' in df.columns:
            fig.add_trace(go.Scatter(x=df.index, y=df['isa_9'], name='Tenkan-sen', line=dict(color='aqua', width=1, dash='dot')), row=1, col=1)
            if 'isb_26' in df.columns:
                fig.add_trace(go.Scatter(x=df.index, y=df['isb_26'], name='Kijun-sen', line=dict(color='pink', width=1, dash='dot')), row=1, col=1)
            if 'ics_26' in df.columns:
                fig.add_trace(go.Scatter(x=df.index, y=df['ics_26'], name='Chikou Span', line=dict(color='lightgreen', width=1, dash='dash')), row=1, col=1)
            if 'iks_26' in df.columns:
                fig.add_trace(go.Scatter(x=df.index, y=df['iks_26'], name='Senkou Span A', line=dict(color='rgba(0,255,0,0)', width=0)), row=1, col=1)
            if 'iss_52' in df.columns:
                fig.add_trace(go.Scatter(x=df.index, y=df['iss_52'], name='Senkou Span B', line=dict(color='rgba(255,0,0,0)', width=0), fill='tonexty', fillcolor='rgba(0, 255, 127, 0.1)'), row=1, col=1)

        # --- Dynamic Subplots ---
        current_row = 2
        for subplot_name in subplots:
            if subplot_name == 'Volume':
                # Use a vectorized numpy operation for performance instead of iterrows()
                colors = np.where(df['close'] >= df['open'], 'green', 'red')
                fig.add_trace(go.Bar(x=df.index, y=df['volume'], name='Volume', marker_color=colors), row=current_row, col=1)
                fig.update_yaxes(title_text="Volume", row=current_row, col=1)
            elif subplot_name == 'RSI':
                fig.add_trace(go.Scatter(x=df.index, y=df['rsi_14'], name='RSI', line=dict(color='purple', width=1.5)), row=current_row, col=1)
                fig.add_hline(y=70, line_dash="dash", line_color="red", row=current_row, col=1)
                fig.add_hline(y=30, line_dash="dash", line_color="green", row=current_row, col=1)
                fig.update_yaxes(title_text="RSI", row=current_row, col=1)
            elif subplot_name == 'MACD':
                macd_signal_col = 'macds_12_26_9' if 'macds_12_26_9' in df.columns else 'macd_signal_12_26_9'
                macd_hist_col = 'macdh_12_26_9' if 'macdh_12_26_9' in df.columns else 'macd_hist_12_26_9'
                fig.add_trace(go.Scatter(x=df.index, y=df['macd_12_26_9'], name='MACD', line=dict(color='blue', width=1.5)), row=current_row, col=1)
                if macd_signal_col in df.columns:
                    fig.add_trace(go.Scatter(x=df.index, y=df[macd_signal_col], name='Signal', line=dict(color='orange', width=1)), row=current_row, col=1)
                if macd_hist_col in df.columns:
                    fig.add_trace(go.Bar(x=df.index, y=df[macd_hist_col], name='Histogram', marker_color=df[macd_hist_col].apply(lambda x: 'green' if x > 0 else 'red')), row=current_row, col=1)
                fig.update_yaxes(title_text="MACD", row=current_row, col=1)
            elif subplot_name == 'Stochastic':
                fig.add_trace(go.Scatter(x=df.index, y=df['stochk_14_3_3'], name='Stoch %K', line=dict(color='lightblue')), row=current_row, col=1)
                fig.add_trace(go.Scatter(x=df.index, y=df['stochd_14_3_3'], name='Stoch %D', line=dict(color='orange')), row=current_row, col=1)
                fig.add_hline(y=80, line_dash="dash", line_color="red", row=current_row, col=1)
                fig.add_hline(y=20, line_dash="dash", line_color="green", row=current_row, col=1)
                fig.update_yaxes(title_text="Stochastic", row=current_row, col=1)
            elif subplot_name == 'Historical P/E Ratio' and 'peRatio' in df.columns:
                fig.add_trace(go.Scatter(x=df.index, y=df['peRatio'], name='P/E Ratio', line=dict(color='teal')), row=current_row, col=1)
                fig.update_yaxes(title_text="P/E Ratio", row=current_row, col=1)
            elif subplot_name == 'Conviction Score' and 'conviction_score' in df.columns:
                fig.add_trace(go.Scatter(x=df.index, y=df['conviction_score'], name='Conviction Score', line=dict(color='gold')), row=current_row, col=1)
                fig.update_yaxes(title_text="Conviction Score", range=[0, 100], row=current_row, col=1)
            elif subplot_name == 'MFI' and 'mfi_14' in df.columns:
                fig.add_trace(go.Scatter(x=df.index, y=df['mfi_14'], name='MFI', line=dict(color='turquoise')), row=current_row, col=1)
                fig.update_yaxes(title_text="Money Flow Index", row=current_row, col=1)
            elif subplot_name == 'Narrative Divergence' and 'narrative_divergence_index' in df.columns:
                fig.add_trace(go.Scatter(x=df.index, y=df['narrative_divergence_index'], name='Divergence Index', line=dict(color='magenta')), row=current_row, col=1)
                fig.update_yaxes(title_text="Divergence Index", range=[0, 100], row=current_row, col=1)
            elif subplot_name == 'Inflation-Adjusted P/E' and 'real_pe_ratio' in df.columns:
                fig.add_trace(go.Scatter(x=df.index, y=df['real_pe_ratio'], name='Real P/E Ratio', line=dict(color='silver')), row=current_row, col=1)
                fig.update_yaxes(title_text="Real P/E Ratio", row=current_row, col=1)
            current_row += 1

        # --- Layout ---
        fig.update_layout(height=400 + (200 * len(subplots)), showlegend=False, template='plotly_dark', xaxis_rangeslider_visible=False)
        fig.update_yaxes(title_text="Price", row=1, col=1)

        return fig

    def _render_ai_opinion(self, ticker):
        """Renders the AI opinion tab."""
        st.subheader("Co-pilot's Take")
        st.info("🤖 AI Opinion and analysis for this section are coming in Phase 5!")
        # Placeholder for future content
