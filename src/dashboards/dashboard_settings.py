"""
Settings Dashboard
Centralized configuration management UI for the Analysis Master app.

Currently supports:
- Per-source sentiment weights (scoped: global / equity / predictive)
- Preview panel showing a pie chart of weights and how the per-source contributions affect the overall sentiment

"""
from __future__ import annotations

import streamlit as st
import plotly.express as px
from typing import Dict

from src.pipelines.get_sentiment_scraper import SentimentScraper, DEFAULT_SOURCE_WEIGHTS
from src.core.design_system import HelpWidget
from src.core.settings_store import load_settings, set_scope_weights, get_scope_weights, set_scope_config, get_scope_config

DEFAULT_SCOPE = 'global'
SCOPES = ['global', 'equity', 'predictive']


class SettingsDashboard:
    def __init__(self):
        self.sentiment = SentimentScraper()

    def display(self):
        st.title("⚙️ Application Settings (Central)")
        st.markdown("Configure global app settings such as the Sentiment per-source weights")
        scope = st.selectbox("Scope to edit", options=SCOPES, index=SCOPES.index(DEFAULT_SCOPE))
        st.markdown("---")
        st.subheader("Per-Source Sentiment Weights")
        # Small help tooltip and expander to explain weights
        HelpWidget.render_help_tooltip("Per-source weights determine each news source's influence on the overall sentiment score. Use the expander for more details.")
        with st.expander("What are per-source weights and how to use them"):
            st.markdown(
                """
                Per-source weights allow you to tune how much influence each news source (e.g., Finviz, Yahoo, SEC) has on the aggregated sentiment score.
                Higher weights give more influence to a source. The weights are normalized to sum to 1.0. 
                Session-only override lets you preview settings without persisting them.
                For production, consider using server-side settings storage and centralized management.
                """
            )
        cur_weights = self.sentiment.get_weights(scope)
        # Scoring mode control
        scoring_opts = ['auto', 'vader', 'textblob', 'llm', 'keyword']
        current_mode = self.sentiment.get_scoring_mode(scope)
        mode_sel = st.selectbox("Scoring Mode", options=scoring_opts, index=scoring_opts.index(current_mode), help="auto: VADER/TextBlob if available, LLM fallback; keyword: naive heuristics")
        HelpWidget.render_help_tooltip("Scoring mode determines which model is used to score headlines. 'auto' uses the best configured option; 'llm' uses server/local LLM scoring.")
        cols = st.columns(len(DEFAULT_SOURCE_WEIGHTS))
        new_weights = {}
        # Load existing enabled_sources from scope config if present
        scope_conf = get_scope_config(scope) or {}
        enabled_sources = scope_conf.get('enabled_sources', {s: True for s in DEFAULT_SOURCE_WEIGHTS.keys()})
        new_enabled = {}
        new_rate_limits = {}
        for i, src in enumerate(DEFAULT_SOURCE_WEIGHTS.keys()):
            with cols[i]:
                w = st.slider(f"{src}", 0.0, 1.0, float(cur_weights.get(src, DEFAULT_SOURCE_WEIGHTS[src])), 0.05)
                new_weights[src] = float(w)
                rl = st.number_input(f"{src} rate limit (s)", min_value=0.0, max_value=60.0, value=float(scope_conf.get('rate_limits', {}).get(src, 0.2 if src=='MarketWatch' else 0.05)), step=0.01)
                new_rate_limits[src] = float(rl)
            # enable toggle for this source
            new_enabled[src] = st.checkbox(f"Enable {src}", value=bool(enabled_sources.get(src, True)))

        st.markdown("---")
        with st.columns(3)[0]:
            session_only = st.checkbox("Session-only override (don't persist)")
        if st.button("Save Weights"):
            total = sum(new_weights.values())
            if total <= 0.0:
                st.error("Total weights must be > 0. Adjust sliders.")
            else:
                normalized = {k: v / total for k, v in new_weights.items()}
                if session_only:
                    # session-only override (do not persist)
                    st.session_state['sentiment_weights_override'] = normalized
                    st.session_state['sentiment_weights_override_scope'] = scope
                    # Update instance weights for immediate use
                    self.sentiment.source_weights = normalized.copy()
                    self.sentiment.rate_limits = new_rate_limits.copy()
                    self.sentiment.clear_cache()
                    st.success("Applied session-only override and cleared cache.")
                else:
                    # Save both normalized weights, scoring mode, and enabled_sources into scope config
                    conf = {'weights': normalized, 'scoring_mode': mode_sel, 'enabled_sources': new_enabled, 'rate_limits': new_rate_limits}
                    if set_scope_config(scope, conf):
                        self.sentiment.source_weights = normalized.copy()
                        self.sentiment.enabled_sources = new_enabled.copy()
                        self.sentiment.rate_limits = new_rate_limits.copy()
                        self.sentiment.scoring_mode = mode_sel
                        self.sentiment.clear_cache()
                        st.success("Saved and cleared cache.")
                    else:
                        st.error("Failed to persist weights.")

        cols = st.columns(3)
        with cols[0]:
            if st.button("Reset to defaults"):
                if self.sentiment.reset_weights_to_default(scope=scope):
                    self.sentiment.clear_cache()
                    st.success("Reset to defaults and cleared cache.")
                else:
                    st.error("Failed to reset weights")
        with cols[1]:
            if st.button("Reload saved weights"):
                # Simply rerun to reload values from disk
                st.experimental_rerun()
        

        if st.button("Revert session override"):
            if 'sentiment_weights_override' in st.session_state:
                st.session_state.pop('sentiment_weights_override')
                st.session_state.pop('sentiment_weights_override_scope', None)
                # reload weights from storage
                self.sentiment.source_weights = get_scope_weights(scope, DEFAULT_SOURCE_WEIGHTS)
                self.sentiment.clear_cache()
                st.experimental_rerun()

        st.markdown("---")
        st.subheader("Preview")
        preview_col1, preview_col2 = st.columns([2, 3])
        with preview_col1:
            st.markdown("**Weight distribution**")
            fig = px.pie(names=list(new_weights.keys()), values=list(new_weights.values()), hole=0.3)
            st.plotly_chart(fig, width='stretch')

        with preview_col2:
            st.markdown("**Live contribution preview**")
            # Use current weights to compute the live contributions given the last headlines
            try:
                headlines = self.sentiment.get_headlines('AAPL')
                # compute per-source scores
                agg = self.sentiment._aggregate_scores(headlines, source_weights=new_weights)
                per_source = agg['per_source']
                # compute contributions as weight * score
                contributions = {src: (per_source.get(src, {}).get('score', 0.0) * new_weights.get(src, 0.0)) for src in new_weights}
                # Show table
                st.table({ 'weight': new_weights, 'per_source_score': {k: (per_source.get(k, {}).get('score', 0.0)) for k in new_weights}, 'contribution': contributions })
            except Exception:
                st.write('No headlines available to compute contributions. Use a ticker with recent news or check your network.')

        st.markdown("---")
        st.subheader("Interactive Weight Heatmap Preview")
        # Allow user to pick a ticker for the preview and a resolution
        preview_ticker = st.text_input('Ticker for heatmap preview', 'AAPL')
        steps = st.slider('Resolution (larger = slower)', min_value=3, max_value=11, value=5)
        # Create heatmap by sweeping two source weights (Finviz vs MarketWatch) and distributing remainder
        try:
            headlines = self.sentiment.get_headlines(preview_ticker)
            if not headlines:
                st.write('No headlines available for preview.')
            else:
                import numpy as np
                import plotly.express as px
                values = np.linspace(0.0, 1.0, steps)
                z = []
                x = []
                y = []
                for wf in values:
                    row = []
                    for wm in values:
                        # remaining weight is split across other sources
                        rem = max(0.0, 1.0 - wf)
                        wy = rem
                        weights = {
                            'Finviz': wf,
                            'Yahoo': wy,
                            'SEC': wsec
                        }
                        agg = self.sentiment._aggregate_scores(headlines, source_weights=weights)
                        row.append(agg['overall'])
                    z.append(row)
                fig = px.imshow(z, x=[f'{v:.2f}' for v in values], y=[f'{v:.2f}' for v in values], labels={'x': 'MarketWatch weight', 'y': 'Finviz weight'}, origin='lower', aspect='auto', color_continuous_scale='RdYlGn')
                st.plotly_chart(fig, width='stretch')
        except Exception as e:
            st.write('Unable to render heatmap', e)

        st.markdown("---")
        st.write("For advanced usage or multi-user / server-side storage, implement a 'server' storage option and switch the `SETTINGS_STORE` in `AppConfig`.")
