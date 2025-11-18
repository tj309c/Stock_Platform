"""
Portfolio Dashboard - Placeholder
This file contains a basic placeholder implementation for portfolio tools, risk analysis, and optimization UI.
"""
import streamlit as st
from src.core.wsb_quotes import WSBQuotes, QuoteCategory
from src.core.design_system import MetricCardRenderer
from src.pipelines.get_market_data import MarketDataPipeline
import pandas as pd
import plotly.graph_objects as go
import numpy as np

# Optional dependency: PyPortfolioOpt (pypfopt). If it's not installed, we still
# want the app to start; optimization features will be disabled with a clear
# message in the UI.
try:
    from pypfopt import EfficientFrontier, risk_models, expected_returns
    from pypfopt.exceptions import OptimizationError
    HAS_PYPFOPT = True
except Exception:
    EfficientFrontier = None
    risk_models = None
    expected_returns = None
    OptimizationError = Exception
    HAS_PYPFOPT = False


class PortfolioDashboard:
    """Placeholder for portfolio & risk dashboard."""

    def __init__(self):
        self.name = "💼 Portfolio & Risk Management"
        self.quoter = WSBQuotes()
        self.market_pipeline = MarketDataPipeline()
        self._initialize_session_state()

    def display(self):
        st.title("💼 Portfolio & Risk")

        quote = self.quoter.get_random_quote(QuoteCategory.RISK)
        MetricCardRenderer.render_alert_box(
            message=quote,
            alert_type='info',
            title='Portfolio (placeholder)',
            icon='💼'
        )

        st.markdown("---")
        st.header("Summary")
        st.info("This dashboard will include portfolio allocation, efficient frontier, and correlation heatmaps.")

        tab1, tab2, tab3 = st.tabs(["📊 Allocation", "🔍 Correlations", "📈 Optimization"])

        with tab1:
            self._render_allocation_tab()

        with tab2:
            self._render_correlations_tab()
        with tab3:
            self._render_optimization_tab()

    def _initialize_session_state(self):
        """Initialize session state for portfolio holdings."""
        if 'portfolio_holdings' not in st.session_state:
            st.session_state.portfolio_holdings = [
                {'ticker': 'AAPL', 'shares': 10},
                {'ticker': 'MSFT', 'shares': 15},
                {'ticker': 'GOOGL', 'shares': 5},
            ]

    def _render_allocation_tab(self):
        """Renders the UI for portfolio allocation and summary."""
        st.subheader("Your Holdings")

        # --- Holdings Editor ---
        for i, holding in enumerate(st.session_state.portfolio_holdings):
            cols = st.columns([2, 2, 1])
            st.session_state.portfolio_holdings[i]['ticker'] = cols[0].text_input(f"Ticker {i+1}", value=holding['ticker'], key=f"ticker_{i}").upper()
            st.session_state.portfolio_holdings[i]['shares'] = cols[1].number_input(f"Shares {i+1}", value=holding['shares'], min_value=0, key=f"shares_{i}")
            if cols[2].button("❌", key=f"del_{i}", help="Remove this holding"):
                st.session_state.portfolio_holdings.pop(i)
                st.rerun()

        if st.button("➕ Add Holding"):
            st.session_state.portfolio_holdings.append({'ticker': '', 'shares': 0})
            st.rerun()

        st.markdown("---")

        # --- Portfolio Calculation ---
        holdings = [h for h in st.session_state.portfolio_holdings if h['ticker'] and h['shares'] > 0]
        if not holdings:
            st.warning("Please add at least one holding to see the analysis.")
            return

        tickers = [h['ticker'] for h in holdings]
        shares = {h['ticker']: h['shares'] for h in holdings}

        with st.spinner("Fetching current prices and calculating portfolio value..."):
            try:
                # Fetch current prices in a batch
                current_prices = self.market_pipeline.get_multiple_tickers_current_price(tickers)

                portfolio_data = []
                total_portfolio_value = 0

                for ticker in tickers:
                    price = current_prices.get(ticker)
                    if price is not None:
                        num_shares = shares[ticker]
                        market_value = price * num_shares
                        total_portfolio_value += market_value
                        portfolio_data.append({
                            "Ticker": ticker,
                            "Shares": num_shares,
                            "Current Price": price,
                            "Market Value": market_value
                        })
                    else:
                        portfolio_data.append({
                            "Ticker": ticker,
                            "Shares": shares[ticker],
                            "Current Price": "N/A",
                            "Market Value": "N/A"
                        })

                if not portfolio_data:
                    st.error("Could not fetch data for any of the tickers.")
                    return

                df = pd.DataFrame(portfolio_data)
                df['Weight'] = (df['Market Value'] / total_portfolio_value) if total_portfolio_value > 0 else 0

                # --- Display Metrics and Table ---
                st.subheader("Portfolio Summary")
                MetricCardRenderer.render_metric(
                    label="Total Portfolio Value",
                    value=f"${total_portfolio_value:,.2f}",
                    help_text="The total current market value of all your holdings."
                )

                st.dataframe(df.style.format({
                    "Current Price": "${:,.2f}",
                    "Market Value": "${:,.2f}",
                    "Weight": "{:.2%}"
                }), use_container_width=True)

            except Exception as e:
                st.error(f"An error occurred while calculating the portfolio: {e}")

    def _render_correlations_tab(self):
        """Renders the correlation matrix for the portfolio holdings."""
        st.subheader("Asset Correlation Matrix")
        st.info("This heatmap shows how closely the daily returns of your assets move together. A value of 1 means they move in perfect sync; -1 means they move in opposite directions; 0 means there is no correlation.")

        holdings = [h for h in st.session_state.portfolio_holdings if h['ticker'] and h['shares'] > 0]
        tickers = [h['ticker'] for h in holdings]

        if len(tickers) < 2:
            st.warning("You need at least two assets in your portfolio to calculate correlations.")
            return

        period = st.selectbox(
            "Select time period for correlation analysis:",
            ("1y", "6mo", "3mo", "ytd"),
            index=0,
            key="corr_period"
        )

        with st.spinner(f"Fetching historical data for {len(tickers)} tickers..."):
            try:
                # Fetch historical data for all tickers
                hist_data = self.market_pipeline.get_multiple_tickers_historical_data(tickers, period=period)

                # Combine 'Adj Close' from each ticker into a single DataFrame
                adj_close_df = pd.DataFrame({ticker: data['Adj Close'] for ticker, data in hist_data.items() if not data.empty})

                if adj_close_df.empty or len(adj_close_df.columns) < 2:
                    st.error("Could not fetch sufficient historical data to calculate correlations.")
                    return

                # Calculate daily returns
                returns_df = adj_close_df.pct_change().dropna()

                # Calculate correlation matrix
                corr_matrix = returns_df.corr()

                # Create heatmap
                fig = go.Figure(data=go.Heatmap(
                    z=corr_matrix.values,
                    x=corr_matrix.columns,
                    y=corr_matrix.columns,
                    colorscale='RdBu', zmin=-1, zmax=1,
                    text=corr_matrix.values,
                    texttemplate="%{text:.2f}"
                ))
                fig.update_layout(title='Portfolio Asset Correlation Heatmap', yaxis_autorange='reversed')
                st.plotly_chart(fig, use_container_width=True)

            except Exception as e:
                st.error(f"An error occurred during correlation analysis: {e}")

    def _render_optimization_tab(self):
        """Renders the Efficient Frontier optimization for the portfolio."""
        st.subheader("Portfolio Optimization (Efficient Frontier)")
        st.info("This tool calculates the optimal asset allocation to maximize the Sharpe Ratio (risk-adjusted return) based on historical performance.")

        holdings = [h for h in st.session_state.portfolio_holdings if h['ticker'] and h['shares'] > 0]
        tickers = [h['ticker'] for h in holdings]

        if len(tickers) < 2:
            st.warning("You need at least two assets in your portfolio to perform optimization.")
            return

        if not HAS_PYPFOPT:
            st.warning(
                "Portfolio optimization requires the optional package 'PyPortfolioOpt' (import name: pypfopt)."
            )
            st.info("Install it with `pip install pyportfolioopt` to enable this feature.")
            return

        with st.spinner("Calculating Efficient Frontier..."):
            try:
                # Fetch historical data (1 year is standard for this)
                hist_data = self.market_pipeline.get_multiple_tickers_historical_data(tickers, period="1y")
                adj_close_df = pd.DataFrame({ticker: data['Adj Close'] for ticker, data in hist_data.items() if not data.empty})

                if adj_close_df.empty or len(adj_close_df.columns) < 2:
                    st.error("Could not fetch sufficient historical data for optimization.")
                    return

                # Calculate expected returns and sample covariance
                mu = expected_returns.mean_historical_return(adj_close_df)
                S = risk_models.sample_cov(adj_close_df)

                # Optimize for maximal Sharpe ratio
                ef = EfficientFrontier(mu, S)
                weights = ef.max_sharpe()
                cleaned_weights = ef.clean_weights()

                st.subheader("Optimal Asset Allocation (Max Sharpe Ratio)")
                weights_df = pd.DataFrame.from_dict(cleaned_weights, orient='index', columns=['Weight'])
                weights_df.index.name = 'Ticker'
                st.dataframe(weights_df.style.format({"Weight": "{:.2%}"}), use_container_width=True)

                st.subheader("Expected Portfolio Performance")
                expected_return, annual_vol, sharpe_ratio = ef.portfolio_performance(verbose=False)
                perf_cols = st.columns(3)
                perf_cols[0].metric("Expected Annual Return", f"{expected_return:.2%}")
                perf_cols[1].metric("Annual Volatility", f"{annual_vol:.2%}")
                perf_cols[2].metric("Sharpe Ratio", f"{sharpe_ratio:.2f}")

                # --- Plotting the Efficient Frontier ---
                st.subheader("Efficient Frontier Visualization")
                ef_plot = EfficientFrontier(mu, S)
                fig = go.Figure()

                # Plot random portfolios
                n_samples = 10000
                w = np.random.dirichlet(np.ones(len(mu)), n_samples)
                rets = w.dot(mu)
                stds = np.sqrt(np.diag(w @ S @ w.T))
                sharpes = rets / stds
                fig.add_trace(go.Scatter(
                    x=stds, y=rets, mode='markers',
                    marker=dict(size=5, color=sharpes, colorscale='Viridis', showscale=True, colorbar=dict(title="Sharpe Ratio")),
                    name='Random Portfolios'
                ))

                # Plot the frontier
                frontier_returns = np.linspace(mu.min(), mu.max(), 100)
                frontier_vols = []
                for r in frontier_returns:
                    try:
                        ef_plot.efficient_return(r)
                        frontier_vols.append(ef_plot.portfolio_performance()[1])
                    except OptimizationError:
                        continue # Skip if no portfolio can be found for this return

                fig.add_trace(go.Scatter(x=frontier_vols, y=frontier_returns, mode='lines', line=dict(color='red', width=2), name='Efficient Frontier'))

                # Plot Max Sharpe portfolio
                fig.add_trace(go.Scatter(x=[annual_vol], y=[expected_return], mode='markers',
                                         marker=dict(color='gold', size=15, symbol='star'), name='Max Sharpe Ratio'))

                fig.update_layout(title='Efficient Frontier',
                                  xaxis_title='Annual Volatility (Risk)',
                                  yaxis_title='Expected Annual Return',
                                  yaxis_tickformat=".2%", xaxis_tickformat=".2%")
                st.plotly_chart(fig, use_container_width=True)

            except Exception as e:
                st.error(f"An error occurred during portfolio optimization: {e}")
