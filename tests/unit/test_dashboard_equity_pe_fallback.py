import pandas as pd
import streamlit as st
from src.dashboards.dashboard_equity import EquityDashboard


def test_render_summary_handles_missing_pe_ratio(monkeypatch):
    """Ensure the summary rendering does not crash when historical P/E is missing and shows a warning."""
    ed = EquityDashboard()

    # Fake company info
    company_info = {
        'longName': 'Test Co',
        'currentPrice': 100.0,
        'previousClose': 95.0,
        'marketCap': 1000000,
        'fiftyTwoWeekHigh': 150,
        'fiftyTwoWeekLow': 75,
    }

    # Minimal key_metrics
    key_metrics = {'pe_ratio': 20.0}

    # Minimal indicators dataframe without peRatio
    df = pd.DataFrame({
        'open': [90.0, 95.0, 100.0],
        'high': [91.0, 96.0, 101.0],
        'low': [89.0, 94.0, 99.0],
        'close': [90.5, 95.5, 100.5],
        'volume': [1000, 1500, 1200]
    }, index=pd.to_datetime(['2024-01-01', '2024-02-01', '2024-03-01']))

    # Monkeypatch Streamlit UI functions and MetricCardRenderer to be safe in headless mode
    from src.core.design_system import MetricCardRenderer

    monkeypatch.setattr(MetricCardRenderer, 'render_metric', lambda *args, **kwargs: None)
    monkeypatch.setattr(MetricCardRenderer, 'render_score_card', lambda *args, **kwargs: None)
    monkeypatch.setattr(MetricCardRenderer, 'render_metric_row', lambda *args, **kwargs: None)
    monkeypatch.setattr(MetricCardRenderer, 'render_kpi_card', lambda *args, **kwargs: None)
    alert_calls = []
    def record_alert_box(message, alert_type='info', title=None, icon=None):
        alert_calls.append({'message': message, 'alert_type': alert_type, 'title': title, 'icon': icon})
    monkeypatch.setattr(MetricCardRenderer, 'render_alert_box', record_alert_box)
    # Create a dummy Streamlit object to patch into the module under test
    from src.dashboards import dashboard_equity as de

    class DummySt:
        def subheader(self, *args, **kwargs):
            return None
        def markdown(self, *args, **kwargs):
            return None
        def json(self, *args, **kwargs):
            return None
        def dataframe(self, *args, **kwargs):
            return None
        def multiselect(self, *args, **kwargs):
            # args[0] is the label; choose a safe default for overlays and subplots
            label = args[0] if args else ''
            if 'Overlay' in label:
                return []
            if 'Subplot' in label:
                return ['Volume']
            return []
        def plotly_chart(self, *args, **kwargs):
            return None
        def checkbox(self, *args, **kwargs):
            return kwargs.get('value', False)
        def selectbox(self, *args, **kwargs):
            options = kwargs.get('options') or (args[1] if len(args) > 1 else [])
            return options[0] if options else None
        def columns(self, *args, **kwargs):
            first = args[0] if args else None
            try:
                # Handle both integer and list inputs for st.columns
                if isinstance(first, list):
                    num = len(first)
                else:
                    num = int(first) if isinstance(first, (int, float)) else 2
            except Exception:
                num = 2
            return [type('C', (), {'__enter__': lambda self: self, '__exit__': lambda self, exc_type, exc_val, exc_tb: None})() for _ in range(num)]

    monkeypatch.setattr(de, 'st', DummySt(), raising=False)
    def fake_columns(*args, **kwargs):
        first = args[0] if args else None
        try:
            # Handle both integer and list inputs for st.columns
            if isinstance(first, list):
                num = len(first)
            else:
                num = int(first) if isinstance(first, (int, float)) else 2
        except Exception:
            num = 2
        return [type('C', (), {'__enter__': lambda self: self, '__exit__': lambda self, exc_type, exc_val, exc_tb: None})() for _ in range(num)]

    monkeypatch.setattr(st, 'columns', fake_columns, raising=False)

    # Call render summary and ensure it doesn't raise; include sentiment_data and detected_patterns
    sentiment_data = {'score': 0.0, 'num_headlines': 0}
    ed._render_summary('TEST', company_info, key_metrics, sentiment_data, df)

    # Validate that a warning was recorded for missing historical P/E
    assert any(call['alert_type'] == 'warning' and 'Historical P/E' in call['title'] for call in alert_calls)
