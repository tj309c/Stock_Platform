"""
settings_store.py
Centralized storage helper for persisted settings (weights, user config, etc.).
Stores JSON under `data/config/settings.json` with a `scopes` mapping.

File format:
{
  "version": 1,
  "scopes": {
     "global": { ... },
     "equity": { ... },
     "predictive": { ... }
  }
}

This module provides a consistent interface to load/save settings with scope fallback.
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Dict, Any

from src.core.config import AppConfig
import os
import tempfile

logger = logging.getLogger(__name__)

SETTINGS_FILENAME = "settings.json"
DEFAULT_CONTENT = {"version": 1, "scopes": {}}


def _settings_file_path() -> Path:
    cfg = AppConfig()
    conf_dir = cfg.DATA_DIR / "config"
    conf_dir.mkdir(parents=True, exist_ok=True)
    # During pytest runs, avoid writing to repo-local config; use temp dir
    if 'PYTEST_CURRENT_TEST' in os.environ:
        # Use a per-test file when running under pytest to avoid cross-test pollution
        test_id = os.environ.get('PYTEST_CURRENT_TEST') or ''
        if test_id:
            # sanitize the id to be filename safe
            import re
            safe = re.sub(r'[^a-zA-Z0-9_-]', '_', test_id)
            return Path(tempfile.gettempdir()) / f"settings_{safe}.json"
        return Path(tempfile.gettempdir()) / SETTINGS_FILENAME
    # If not running under pytest, return a unique file path per process/worker to avoid
    # accidental reuse or leftover files across runs. This keeps environment state isolated.
    import uuid
    unique_name = f"settings_{os.getpid()}_{uuid.uuid4().hex}.json"
    return Path(tempfile.gettempdir()) / unique_name


def load_settings() -> Dict[str, Any]:
    cfg = AppConfig()
    store_type = getattr(cfg, 'SETTINGS_STORE_TYPE', 'local')
    if store_type == 'server':
        try:
            import requests
            url = cfg.secrets.get('SETTINGS_SERVER_URL') or 'http://localhost:5001/settings'
            r = requests.get(url, timeout=3)
            r.raise_for_status()
            return r.json()
        except Exception:
            logger.debug("Failed to get settings from server, falling back to local")
            # continue to local
    p = _settings_file_path()
    if not p.exists():
        return DEFAULT_CONTENT.copy()
    try:
        with open(p, 'r', encoding='utf-8') as fh:
            return json.load(fh)
    except Exception as ex:
        logger.debug("Failed to read settings file: %s", ex)
        return DEFAULT_CONTENT.copy()


def save_settings(content: Dict[str, Any]) -> bool:
    cfg = AppConfig()
    store_type = getattr(cfg, 'SETTINGS_STORE_TYPE', 'local')
    if store_type == 'server':
        try:
            import requests
            base = cfg.secrets.get('SETTINGS_SERVER_URL') or 'http://localhost:5001'
            url = f"{base}/settings"
            # The server expects a full settings object
            r = requests.post(url, json=content, timeout=3)
            r.raise_for_status()
            return True
        except Exception:
            logger.debug("Failed to save settings to server, falling back to local")
            # fallback to local file
    p = _settings_file_path()
    try:
        with open(p, 'w', encoding='utf-8') as fh:
            json.dump(content, fh, indent=2)
        return True
    except Exception as ex:
        logger.debug("Failed to save settings: %s", ex)
        return False


def get_scope_weights(scope: str, default_weights: Dict[str, float]) -> Dict[str, float]:
    content = load_settings()
    scopes = content.get("scopes", {})
    # The scopes mapping can contain either a plain weights mapping or a more
    # complex dict with 'weights' and 'scoring_mode'. If we find a dict, return its 'weights'.
    val = scopes.get(scope)
    if isinstance(val, dict) and 'weights' in val:
        return val['weights']
    if isinstance(val, dict):
        # If plain mapping, return it
        return val
    # fallback to global
    g = scopes.get("global")
    if isinstance(g, dict) and 'weights' in g:
        return g['weights']
    if isinstance(g, dict):
        return g
    return default_weights.copy()


def get_scope_config(scope: str) -> Dict[str, Any]:
    cfg = AppConfig()
    store_type = getattr(cfg, 'SETTINGS_STORE_TYPE', 'local')
    if store_type == 'server':
        try:
            import requests
            base = cfg.secrets.get('SETTINGS_SERVER_URL') or 'http://localhost:5001'
            url = f"{base}/settings/{scope}"
            r = requests.get(url, timeout=3)
            r.raise_for_status()
            return r.json()
        except Exception:
            # fallback to local
            pass
    content = load_settings()
    scopes = content.get('scopes', {})
    return scopes.get(scope, {})


def set_scope_config(scope: str, config: Dict[str, Any]) -> bool:
    cfg = AppConfig()
    store_type = getattr(cfg, 'SETTINGS_STORE_TYPE', 'local')
    if store_type == 'server':
        try:
            import requests
            base = cfg.secrets.get('SETTINGS_SERVER_URL') or 'http://localhost:5001'
            url = f"{base}/settings/{scope}"
            r = requests.post(url, json=config, timeout=3)
            r.raise_for_status()
            return True
        except Exception:
            # fallback to local
            pass
    content = load_settings()
    if 'scopes' not in content:
        content['scopes'] = {}
    content['scopes'][scope] = config.copy()
    return save_settings(content)


def set_scope_weights(scope: str, weights: Dict[str, float]) -> bool:
    content = load_settings()
    if "scopes" not in content:
        content["scopes"] = {}
    content["scopes"][scope] = weights.copy()
    return save_settings(content)


def reset_scope_weights(scope: str) -> bool:
    content = load_settings()
    if "scopes" not in content or scope not in content.get("scopes", {}):
        # Nothing to do; success
        return True
    content["scopes"].pop(scope, None)
    return save_settings(content)
