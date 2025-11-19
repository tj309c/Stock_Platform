import os
import json
import logging
from pathlib import Path
from src.core.config import AppConfig
from src.core.settings_store import _settings_file_path
import pytest


def test_appconfig_picks_up_persisted_debug_modules(tmp_path, monkeypatch):
    # Setup config directory so that settings file is created at this location
    monkeypatch.setattr(AppConfig, 'DATA_DIR', tmp_path)
    monkeypatch.setattr(AppConfig, 'CACHE_DIR', tmp_path / 'cache')

    cfg_dir = tmp_path / 'config'
    cfg_dir.mkdir(parents=True, exist_ok=True)
    settings_file = cfg_dir / 'settings.json'
    settings = {
        'version': 1,
        'scopes': {
            'global': {
                'debug_modules': ['tests.unit.test_appconfig_debug_modules']
            }
        }
    }
    settings_file.write_text(json.dumps(settings), encoding='utf-8')

    # Ensure logging starts at INFO
    logging.getLogger('tests.unit.test_appconfig_debug_modules').setLevel(logging.INFO)
    appcfg = AppConfig()

    assert 'tests.unit.test_appconfig_debug_modules' in appcfg.DEBUG_MODULES
    assert logging.getLogger('tests.unit.test_appconfig_debug_modules').getEffectiveLevel() == logging.DEBUG
