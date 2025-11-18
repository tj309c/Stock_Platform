"""
Predictive Dashboard - Placeholder
Provides the UI for future predictive analytics features (Earnings Play Predictor, LLM model wrapppers, etc.).
"""
import streamlit as st
from src.core.wsb_quotes import WSBQuotes, QuoteCategory
from src.core.design_system import MetricCardRenderer, HelpWidget
from src.pipelines.get_sentiment_scraper import SentimentScraper, DEFAULT_SOURCE_WEIGHTS
import plotly.graph_objects as go


class PredictiveDashboard:
    """Placeholder for Predictive (Phase 5) dashboard."""

    def __init__(self):
        self.quoter = WSBQuotes()
        self.sentiment = SentimentScraper()

    def display(self):
        st.title("🔮 Predictive Modeling & Earnings Plays")

        quote = self.quoter.get_random_quote(QuoteCategory.YOLO)
        MetricCardRenderer.render_alert_box(
            message=quote,
            alert_type='info',
            title='Predictive (placeholder)',
            icon='🤖'
        )

        st.markdown("---")
        st.header("Summary")
        # Small help widget describing the predictive dashboard
        HelpWidget.render_help_tooltip("Predictive dashboard shows per-ticker sentiment and preview forecasts. Uses VADER/TextBlob locally and an optional LLM scoring path. Expand for more details.")
        st.info("This dashboard will host the Earnings Play Predictor, Volatility Forecasting, and LLM-based scenario analysis (Phase 5).")
        with st.expander("About this dashboard"):
            st.markdown(
                """
                This dashboard provides:
                - A preview of per-ticker sentiment using the configured scoring method (VADER/TextBlob by default, optional LLM batch scoring available via server).
                - Per-source weighting and contribution visualizations
                - Forecasting and backtesting stubs for future expansions
                
                What it uses:
                - Headline scrapers across multiple sources (Finviz, Yahoo, SEC). 
                - Local scorers (VADER/TextBlob) for low-latency scoring; optional LLM mode for more nuanced scoring (replaceable per scope).
                - Per-scope weights stored in local or server-backed settings (accessible via Settings). 
                """
            )

        tab1, tab2, tab3 = st.tabs(["📈 Forecasts", "🔬 Backtests", "🤖 AI Opinion"])
        with tab1:
            ticker = st.text_input("Ticker for sentiment preview", "AAPL")
            if ticker:
                import pandas as pd
                with st.spinner("Fetching headline sentiment..."):
                    res = self.sentiment.get_sentiment_for_ticker(ticker.upper())
                
                score = res.get('score', 0.0)

                def get_sentiment_label(s):
                    if s > 0.2: return "Positive"
                    if s > 0.05: return "Slightly Positive"
                    if s < -0.2: return "Negative"
                    if s < -0.05: return "Slightly Negative"
                    return "Neutral"

                label = get_sentiment_label(score)
                
                col1, col2 = st.columns([1, 2])
                with col1:
                    st.metric(label=f"{ticker.upper()} - Sentiment Score", value=f"{score:.2f}", help="A score from -1 (very negative) to +1 (very positive).")
                    st.caption(f"**Interpretation:** {label}")
                    st.caption(f"Based on {res.get('num_headlines', 0)} headlines.")

                with col2:
                    headlines = res.get('headlines', [])
                    if headlines:
                        HelpWidget.render_help_expander(
                            title="How to Read the Sentiment Distribution Chart",
                            content="""
                            This **violin plot** visualizes the distribution of sentiment scores from individual news headlines.
                            *   **Shape**: The width of the violin shows the density of scores. Wider parts mean more headlines have scores in that range.
                            *   **Box Plot (inside)**: The inner box shows the median (middle line) and the interquartile range (the box itself), representing the middle 50% of scores.
                            *   **Mean Line**: The solid line across the violin is the average (mean) score.
                            *   **Points**: The individual dots represent the score of each single headline.
                            """
                        )

                        scores = [h.get('score', 0.0) for h in headlines]
                        
                        fig = go.Figure()
                        fig.add_trace(go.Violin(
                            x=['All Headlines'] * len(scores), # Add a category for the x-axis
                            y=scores,
                            name='Scores',
                            box_visible=True,
                            meanline_visible=True,
                            points='all',
                            jitter=0.1,
                            marker_color='#1E88E5',
                            hoveron='points+kde'
                        ))
                        
                        fig.update_layout(
                            title_text="Distribution of Headline Sentiment Scores",
                            yaxis_title="Sentiment Score (-1.0 to +1.0)",
                            xaxis_title="Source Category",
                            showlegend=False)
                        fig.update_yaxes(range=[-1.1, 1.1])
                        st.plotly_chart(fig, use_container_width=True)

                if st.button("🔄 Refresh Sentiment"):
                    # Clear cache and re-fetch
                    self.sentiment.clear_cache()
                    with st.spinner("Refreshing sentiment..."):
                        res = self.sentiment.get_sentiment_for_ticker(ticker.upper())
                    st.success("Sentiment refreshed")
                st.markdown("---")
                st.subheader("Source Status")
                # Display per-source status
                status_cols = st.columns(len(res['source_status']))
                for i, (src, status) in enumerate(res['source_status'].items()):
                    with status_cols[i]:
                        if isinstance(status, dict) and status.get('state') == 'ok':
                            MetricCardRenderer.render_metric(label=src, value="OK", help_text=f"Source healthy (last: {status.get('last_success')})")
                        else:
                            # show last_error or 'No recent data'
                            err = status.get('last_error') if isinstance(status, dict) else None
                            MetricCardRenderer.render_metric(label=src, value="⚠️ Needs attention", help_text=err or "No recent data or fetch failed")
                # Report button shows extended error details
                if any(status.get('state') == 'error' for status in res['source_status'].values()):
                    if st.button("🚨 Report Issue"):
                        detail_lines = []
                        for src, info in res['source_status'].items():
                            detail_lines.append(f"{src}: {info.get('state')} (last_success={info.get('last_success')}, last_error={info.get('last_error')})")
                        report_text = "\n".join(detail_lines)
                        with st.expander("Issue details"):
                            st.text_area("Copy the report below and paste into GitHub issue or support chat:", value=report_text, height=160)
                st.markdown("---")
                st.subheader("Sentiment Weights")
                st.write("You can also configure weights in Settings: ⚙️ > Application Settings")
                with st.expander("Configure per-source weights (saved to local data/config)"):
                    # Load current weights and render sliders for each known source
                    # Show stacked bar of contributions per source for the current weights
                    try:
                        cur_w = self.sentiment.get_weights(scope='predictive')
                        per_source = res.get('per_source', {})
                        # Compute contributions
                        contributions = {s: (per_source.get(s, {}).get('score', 0.0) * cur_w.get(s, 0.0)) for s in cur_w}
                        # Build stacked bar chart with a single category 'Overall'
                        fig = go.Figure()
                        for src, val in contributions.items():
                            fig.add_trace(go.Bar(name=src, x=['Overall'], y=[val]))
                        fig.update_layout(barmode='relative', title='Per-source contribution to overall sentiment', yaxis_title='Contribution')
                        st.plotly_chart(fig, width='stretch')
                    except Exception:
                        st.write('Unable to show contributions chart')

                    # Scoring mode toggle (predictive scope)
                    try:
                        scoring_mode = self.sentiment.get_scoring_mode(scope='predictive')
                    except Exception:
                        scoring_mode = 'auto'
                    mode = st.selectbox('Scoring Mode (predictive scope)', options=['auto', 'vader', 'textblob', 'llm', 'keyword'], index=['auto','vader','textblob','llm','keyword'].index(scoring_mode))
                    if st.button('Save Scoring Mode (predictive)'):
                        if self.sentiment.set_scoring_mode(mode, scope='predictive'):
                            self.sentiment.clear_cache()
                            st.success('Scoring mode saved and cache cleared')
                        else:
                            st.error('Failed to save scoring mode')

                    current_weights = self.sentiment.get_weights()
                    cols = st.columns(len(DEFAULT_SOURCE_WEIGHTS))
                    new_weights = {}
                    for i, src in enumerate(DEFAULT_SOURCE_WEIGHTS.keys()):
                        with cols[i]:
                            val = st.slider(label=f"{src}", min_value=0.0, max_value=1.0, value=current_weights.get(src, DEFAULT_SOURCE_WEIGHTS[src]), step=0.05)
                            new_weights[src] = float(val)
                    if st.button("Save Weights"):
                        # Normalize to sum to 1.0
                        total = sum(new_weights.values())
                        if total <= 0:
                            st.error("Weights must sum to a value greater than 0. Please adjust sliders.")
                        else:
                            normalized = {k: v / total for k, v in new_weights.items()}
                            if self.sentiment.set_weights(normalized):
                                # Clear sentiment cache to ensure new weights take effect immediately
                                self.sentiment.clear_cache()
                                st.success("Saved weights (normalized). Cache cleared.")
                            else:
                                st.error("Failed to save weights. Check file permissions and retry.")
                    if st.button("Reset to Defaults"):
                        if self.sentiment.reset_weights_to_default():
                            self.sentiment.clear_cache()
                            st.success("Weights reset to defaults. Cache cleared.")
                        else:
                            st.error("Failed to reset weights.")
        with tab2:
            st.warning("Backtests and predictive performance will be shown here.")
        with tab3:
            st.warning("AI Opinion engine (multi-model consensus) placeholder.")
