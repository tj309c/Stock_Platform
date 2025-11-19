import json
from pathlib import Path
from src.core.settings_store import load_settings, save_settings, get_scope_weights, set_scope_weights, reset_scope_weights
from src.core.config import AppConfig


def test_set_get_reset_scope_weights(tmp_path, monkeypatch):
    # Redirect AppConfig.DATA_DIR to temp path
    monkeypatch.setattr(AppConfig, 'DATA_DIR', tmp_path)
    # Clean default settings
    settings = load_settings()
    assert isinstance(settings, dict)

    weights_global = {'Finviz': 0.4, 'Yahoo': 0.4, 'MarketWatch': 0.1, 'SEC': 0.1}
    assert set_scope_weights('global', weights_global)
    got = get_scope_weights('global', {'Finviz': 0.25, 'Yahoo': 0.25, 'MarketWatch': 0.25, 'SEC': 0.25})
    assert got['Finviz'] == weights_global['Finviz']

    # Set a specific scope (equity)
    weights_eq = {'Finviz': 0.6, 'Yahoo': 0.2, 'MarketWatch': 0.1, 'SEC': 0.1}
    assert set_scope_weights('equity', weights_eq)
    got_eq = get_scope_weights('equity', weights_global)
    assert got_eq['Finviz'] == weights_eq['Finviz']

    # reset equity; should now fallback to global
    assert reset_scope_weights('equity')
    got_eq2 = get_scope_weights('equity', weights_global)
    assert got_eq2 == weights_global
