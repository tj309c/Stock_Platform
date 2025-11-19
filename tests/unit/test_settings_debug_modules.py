import json
import pytest
from src.core.settings_store import load_settings, set_scope_config, get_scope_config, _settings_file_path
from src.core.config import AppConfig


def test_debug_modules_persist(tmp_path, monkeypatch):
    # Ensure isolated settings path
    monkeypatch.setattr(AppConfig, 'DATA_DIR', tmp_path)
    monkeypatch.setattr(AppConfig, 'CACHE_DIR', tmp_path / 'cache')

    # Start with empty config
    conf = get_scope_config('global') or {}
    conf['debug_modules'] = ['src.pipelines.get_fmp_data']
    assert set_scope_config('global', conf)

    # Ensure we can read it back
    saved = get_scope_config('global')
    assert 'debug_modules' in saved
    assert isinstance(saved['debug_modules'], list)
    assert saved['debug_modules'][0] == 'src.pipelines.get_fmp_data'

    # Ensure settings file exists and contains the data
    p = _settings_file_path()
    content = json.loads(p.read_text())
    assert content['scopes']['global']['debug_modules'] == ['src.pipelines.get_fmp_data']
