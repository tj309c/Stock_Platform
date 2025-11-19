#!/usr/bin/env python3
"""
Environment checklist script for Analysis Master
- Verifies Python version, venv activation, key package versions (yfinance, pandas, numpy, requests, streamlit)
- Checks presence of FMP_API_KEY in environment or .streamlit/secrets.toml
- Prints next steps for a developer if anything is missing

Usage (from repo root):
    python scripts/check_environment.py

"""
from __future__ import annotations

import sys
import os
import platform
import importlib
from pathlib import Path

REQUIRED_PYTHON_MAJOR = 3
REQUIRED_PYTHON_MINOR = 12

CRITICAL_PACKAGES = ["yfinance", "pandas", "numpy", "requests", "streamlit"]

ROOT = Path(__file__).resolve().parent.parent
SECRETS_TOML = ROOT / ".streamlit" / "secrets.toml"


def check_python_version() -> bool:
    ver = sys.version_info
    print(f"Python: {platform.python_implementation()} {ver.major}.{ver.minor}.{ver.micro} ({sys.executable})")
    ok = (ver.major > REQUIRED_PYTHON_MAJOR) or (
        ver.major == REQUIRED_PYTHON_MAJOR and ver.minor >= REQUIRED_PYTHON_MINOR
    )
    if not ok:
        print(f"  -> WARNING: Recommended Python {REQUIRED_PYTHON_MAJOR}.{REQUIRED_PYTHON_MINOR}+. You may encounter compatibility issues.")
    else:
        print("  -> OK: Python version is compatible.")
    return ok


def check_venv_active() -> bool:
    prefix = sys.prefix
    invenv = any(tag in prefix.lower() for tag in (".venv", "\\venv", "/.venv", "/venv"))
    if invenv:
        print(f"Virtual environment active: sys.prefix='{prefix}'")
        return True
    else:
        print("No virtual environment detected in sys.prefix. It's recommended to run inside the project's .venv")
        return False


def check_packages() -> bool:
    all_ok = True
    print("\nChecking critical packages:")
    for pkg in CRITICAL_PACKAGES:
        try:
            m = importlib.import_module(pkg)
            ver = getattr(m, "__version__", None)
            print(f"  - {pkg}: installed (version {ver})")
        except Exception:
            print(f"  - {pkg}: NOT INSTALLED or import failure")
            all_ok = False
    return all_ok


def check_fmp_key() -> bool:
    env_key = os.getenv("FMP_API_KEY")
    if env_key:
        print("FMP_API_KEY found in environment variables.")
        return True
    if SECRETS_TOML.exists():
        # toml is in requirements but may not be installed; support both built-in tomllib (3.11+) or pypi toml
        parsed = {}
        try:
            text = SECRETS_TOML.read_text(encoding='utf-8')
            try:
                import tomllib as toml  # Python 3.11+ builtin
            except Exception:
                try:
                    import toml as toml  # fallback to pypi toml
                except Exception:
                    toml = None
            if toml:
                # Use loads for both tomllib and community toml
                parsed = toml.loads(text)
        except Exception:
            parsed = {}
        if parsed.get("FMP_API_KEY"):
            print("FMP_API_KEY found in .streamlit/secrets.toml")
            return True
        else:
            print("FMP_API_KEY not found in .streamlit/secrets.toml")
    else:
        print("No .streamlit/secrets.toml found; your FMP_API_KEY may not be configured.")
    print("  -> If you need to use FMP fallback, add FMP_API_KEY to your .streamlit/secrets.toml or environment.")
    return False


def check_coinbase_key() -> bool:
    env_key = os.getenv("COINBASE_API_KEY")
    if env_key:
        print("COINBASE_API_KEY found in environment variables.")
        return True
    if SECRETS_TOML.exists():
        try:
            text = SECRETS_TOML.read_text(encoding='utf-8')
            try:
                import tomllib as toml
            except Exception:
                try:
                    import toml as toml
                except Exception:
                    toml = None
            if toml:
                parsed = toml.loads(text)
            else:
                parsed = {}
        except Exception:
            # Fall back to a raw-text scan if TOML parsing failed (e.g., due to a double-quoted PEM with newlines)
            parsed = {}
            # Simple regex scan to find top-level keys like: COINBASE_API_KEY = "..."
            import re
            m_key = re.search(r'COINBASE_API_KEY\s*=\s*"([^\"]+)"', text)
            m_secret = re.search(r'COINBASE_API_SECRET\s*=\s*"([\s\S]*?)"', text)
            if m_key:
                parsed['COINBASE_API_KEY'] = m_key.group(1)
            if m_secret:
                # Remove trailing newlines and spaces
                parsed['COINBASE_API_SECRET'] = m_secret.group(1).strip()

        # Regardless of whether parsing succeeded, check the parsed dict for keys
        if parsed.get("COINBASE_API_KEY"):
            print("COINBASE_API_KEY found in .streamlit/secrets.toml")
            ck = parsed.get("COINBASE_API_KEY")
            if isinstance(ck, str) and ck.startswith("organizations/"):
                print("  -> NOTE: This looks like a Coinbase Cloud organization API key (starts with 'organizations/').")
                print("     CCXT may not support Coinbase Cloud keys. Consider creating a classic API key pair for CCXT or using Coinbase Cloud SDK.")
            cs = parsed.get("COINBASE_API_SECRET")
            if isinstance(cs, str) and "BEGIN" in cs and "PRIVATE KEY" in cs:
                print("  -> NOTE: COINBASE_API_SECRET looks like a PEM private key (BEGIN ... PRIVATE KEY). CCXT typically expects a simple API secret string, not a PEM file.")
            return True
    print("COINBASE_API_KEY not configured. Public data may still work, but authenticated endpoints require a key.")
    return False


def check_repo_root_coinbase() -> bool:
    """Check repo root secrets.toml for COINBASE API key fallback."""
    repo_root = ROOT / 'secrets.toml'
    if not repo_root.exists():
        return False
    try:
        text = repo_root.read_text(encoding='utf-8')
        try:
            import tomllib as toml
        except Exception:
            try:
                import toml as toml
            except Exception:
                toml = None
        parsed = toml.loads(text) if toml else {}
        if parsed.get('COINBASE_API_KEY'):
            print('COINBASE_API_KEY found in repo-root secrets.toml (dev fallback)')
            ck = parsed.get('COINBASE_API_KEY')
            if isinstance(ck, str) and ck.startswith('organizations/'):
                print("  -> NOTE: This looks like a Coinbase Cloud organization API key (starts with 'organizations/').")
                print("     CCXT may not support Coinbase Cloud keys. Consider creating a classic API key pair for CCXT or using Coinbase Cloud SDK.")
            return True
    except Exception:
        return False
    return False


def check_repo_root_secrets() -> bool:
    """Check `secrets.toml` at repository root as a developer convenience fallback."""
    repo_root = ROOT / 'secrets.toml'
    if repo_root.exists():
        print('secrets.toml found in repository root (developer fallback). Consider moving to .streamlit/secrets.toml or environment variables for Streamlit to pick them up.')
        return True
    return False


def show_next_steps(python_ok: bool, venv_ok: bool, pkgs_ok: bool, key_ok: bool, coinbase_ok: bool) -> None:
    print("\nChecklist Results Summary:")
    print(f"  Python OK: {python_ok}")
    print(f"  venv active: {venv_ok}")
    print(f"  packages OK: {pkgs_ok}")
    print(f"  fmp key present: {key_ok}")
    print(f"  coinbase key present: {coinbase_ok}")

    if not python_ok:
        print("\nAction: Install or select Python 3.12+, e.g.:\n  py -3.12 -m venv .venv")

    if not venv_ok:
        print("\nAction: Activate the project's virtual environment before running the app:\n  .venv\\Scripts\\activate  # Windows\n  source .venv/bin/activate  # macOS/Linux")

    if not pkgs_ok:
        print("\nAction: Install required packages from requirements.txt (from project root):\n  .venv\\Scripts\\activate\n  pip install -r requirements.txt")

    if not key_ok:
        print("\nAction: Add FMP_API_KEY into .streamlit/secrets.toml or set the environment variable FMP_API_KEY. Example .streamlit/secrets.toml snippet:\n  FMP_API_KEY = \"YOUR_KEY_HERE\"\n  POLYGON_API_KEY = \"YOUR_POLYGON_KEY_HERE\"")
    # Warn about repo-root secrets
    if not check_repo_root_secrets():
        print('\nIf you have a secrets.toml at the repo root (e.g., for local dev), consider moving the file into `.streamlit/secrets.toml` so Streamlit can load it automatically, or export keys via environment variables.')
    # Coinbase deprecation & key format guidance
    if coinbase_ok:
        print('\nCoinbase note:')
        print('  - Coinbase Pro (API) has been deprecated and may return 503s via ccxt (coinbasepro).')
        print('  - If you rely on authenticated Coinbase CCXT features: create a classic API key (apiKey, secret and passphrase) via the Coinbase settings page, or use Coinbase Cloud SDK for organization keys.')


if __name__ == '__main__':
    print("\nAnalysis Master - Environment Checklist\n")
    python_ok = check_python_version()
    venv_ok = check_venv_active()
    pkgs_ok = check_packages()
    key_ok = check_fmp_key()
    coinbase_ok = check_coinbase_key() or check_repo_root_coinbase()
    show_next_steps(python_ok, venv_ok, pkgs_ok, key_ok, coinbase_ok)
