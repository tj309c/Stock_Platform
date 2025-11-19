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
                # For historic MarketWatch config the prior default rate limit was 0.2, now defaults to 0.05
                rl = st.number_input(f"{src} rate limit (s)", min_value=0.0, max_value=60.0, value=float(scope_conf.get('rate_limits', {}).get(src, 0.05)), step=0.01)
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

        # Add a debug logging toggle for the session (useful for developers)
        debug_toggle = st.checkbox("Enable detailed debug logs (session only)")
        if debug_toggle:
            import logging
            logging.getLogger().setLevel(logging.DEBUG)
            st.success("Debug logging enabled (session only). Check logs for detail.")
        else:
            # If not toggled and AppConfig says debug is enabled, keep it; otherwise, set to INFO
            from src.core.config import AppConfig
            try:
                if not AppConfig().DEBUG_LOGGING:
                    import logging
                    logging.getLogger().setLevel(logging.INFO)
            except Exception:
                pass

        st.markdown("---")
        # Module-level debug control: allow developers to specify module loggers
        # Default comes from saved config (scope_conf) or env var ANALYSIS_DEBUG_MODULES
        module_debug_default = ''
        if isinstance(scope_conf.get('debug_modules', None), (list, tuple)):
            module_debug_default = ','.join(scope_conf.get('debug_modules', []))
        elif scope_conf.get('debug_modules'):
            module_debug_default = str(scope_conf.get('debug_modules'))
        if not module_debug_default:
            module_debug_default = ','.join([m for m in __import__('os').getenv('ANALYSIS_DEBUG_MODULES', '').split(',') if m.strip()])
        st.text('Module-level debug loggers: toggle specific modules to DEBUG for the session or persist them in settings')
        module_debug_input = st.text_input("Module-level debug loggers (comma-separated)", value=module_debug_default, help="Enter module names (e.g., 'src.pipelines.get_fmp_data,src.pipelines.get_market_data') to set those loggers to DEBUG level for this session.")
        st.caption("Tip: set ANALYSIS_DEBUG_MODULES env var for a system-wide default, or persist below for the selected scope.")
        col_apply, col_save, col_clear = st.columns(3)
        with col_apply:
            if st.button('Apply module debuggers'):
                modules = [m.strip() for m in module_debug_input.split(',') if m.strip()]
                import logging
                for m in modules:
                    logging.getLogger(m).setLevel(logging.DEBUG)
                st.success('Applied module debug settings for this session')
        with col_save:
            if st.button('Save module debuggers (persist)'):
                try:
                    mods = [m.strip() for m in module_debug_input.split(',') if m.strip()]
                    conf = get_scope_config(scope) or {}
                    conf['debug_modules'] = mods
                    if set_scope_config(scope, conf):
                        st.success('Saved module debuggers to settings')
                    else:
                        st.error('Failed to save module debuggers to settings')
                except Exception as e:
                    st.error(f'Failed to save module debuggers: {e}')
        with col_clear:
            if st.button('Clear persisted module debuggers'):
                try:
                    conf = get_scope_config(scope) or {}
                    if 'debug_modules' in conf:
                        conf.pop('debug_modules', None)
                        if set_scope_config(scope, conf):
                            st.success('Cleared persisted module debuggers')
                        else:
                            st.error('Failed to clear persisted module debuggers')
                    else:
                        st.info('No persisted module debuggers found')
                except Exception as e:
                    st.error(f'Failed to clear persisted module debuggers: {e}')
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
                if not headlines:
                    st.info('No headlines available to compute contributions. Use a ticker with recent news or check your network.')
                    st.markdown('**Current per-source weights**')
                    st.table(cur_weights)
                    st.markdown('**Preview weights (unsaved)**')
                    st.table(new_weights)
                # Add a button for exploring the settings file used by the app
                if st.button("Show settings file path"):
                    try:
                        from src.core.settings_store import _settings_file_path
                        p = _settings_file_path()
                        st.write(f"Settings file: {p}")
                        import json
                        if p.exists():
                            st.json(json.loads(p.read_text(encoding='utf-8')))
                        else:
                            st.write("Settings file not found (using defaults)")
                    except Exception as e:
                        st.write("Error showing settings file:", e)
                if st.button('Download settings file'):
                    try:
                        from src.core.settings_store import _settings_file_path
                        p = _settings_file_path()
                        import json
                        if p.exists():
                            content = p.read_text(encoding='utf-8')
                        else:
                            content = json.dumps(load_settings(), indent=2)
                        st.download_button("Download settings JSON", data=content, file_name="settings.json", mime="application/json")
                    except Exception as e:
                        st.write('Error preparing download:', e)
                else:
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
        # Create heatmap by sweeping two source weights and distributing remainder among the rest
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
                        # distribute remainder equally across other sources
                        other = [s for s in DEFAULT_SOURCE_WEIGHTS.keys() if s != 'Finviz']
                        if other:
                            distribute = rem / len(other)
                        else:
                            distribute = 0.0
                        weights = { 'Finviz': wf }
                        for s in other:
                            weights[s] = distribute
                        agg = self.sentiment._aggregate_scores(headlines, source_weights=weights)
                        row.append(agg['overall'])
                    z.append(row)
                fig = px.imshow(z, x=[f'{v:.2f}' for v in values], y=[f'{v:.2f}' for v in values], labels={'x': 'Other sources weight', 'y': 'Finviz weight'}, origin='lower', aspect='auto', color_continuous_scale='RdYlGn')
                st.plotly_chart(fig, width='stretch')
        except Exception as e:
            st.write('Unable to render heatmap', e)

        st.markdown("---")
        st.write("For advanced usage or multi-user / server-side storage, implement a 'server' storage option and switch the `SETTINGS_STORE` in `AppConfig`.")
