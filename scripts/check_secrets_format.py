"""
Simple secrets format checker for .streamlit/secrets.toml to be used as a diagnostic
or pre-commit hook. Flags common misconfiguration problems:
 - Coinbase API key starting with organizations/ (Cloud-style)
 - Coinbase secret containing PEM (BEGIN ... PRIVATE KEY)
 - Coinbase secret equal to API key (likely a paste error)

Usage:
  python scripts/check_secrets_format.py
  # For CI, ensure it exits with non-zero if misconfigured
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SECRETS_FILE = ROOT / ".streamlit" / "secrets.toml"


def raw_scan_text(text: str) -> dict:
    # find likely keys via regex
    data = {}
    m_key = re.search(r'COINBASE_API_KEY\s*=\s*"([^"]+)"', text)
    m_secret = re.search(r'COINBASE_API_SECRET\s*=\s*"([\s\S]*?)"', text)
    if m_key:
        data['COINBASE_API_KEY'] = m_key.group(1)
    if m_secret:
        data['COINBASE_API_SECRET'] = m_secret.group(1).strip()
    return data


def load_secrets(secrets_file: Path | None = None) -> dict:
    secrets_file = secrets_file or DEFAULT_SECRETS_FILE
    
    if not secrets_file.exists():
        return {}
    text = secrets_file.read_text(encoding='utf-8')
    try:
        try:
            import tomllib as toml
        except Exception:
            import toml
        parsed = toml.loads(text)
    except Exception:
        parsed = raw_scan_text(text)
    return parsed


def run_check(secrets_file: Path | None = None) -> int:
    parsed = load_secrets(secrets_file)
    errs = 0
    if not parsed:
        print("No .streamlit/secrets.toml found or file could not be parsed; skipping checks.")
        return 0

    ckey = parsed.get('COINBASE_API_KEY')
    csec = parsed.get('COINBASE_API_SECRET')

    # Check for org key
    if ckey and isinstance(ckey, str) and ckey.startswith('organizations/'):
        print('WARNING: COINBASE_API_KEY looks like a Coinbase Cloud organization key (starts with organizations/).')
        print('  > CCXT may not support org-style keys for authenticated requests; consider creating a classic API key for CCXT or use Coinbase Cloud SDK.')
        errs += 1

    # Check for PEM secret
    if csec and isinstance(csec, str) and ('BEGIN' in csec and 'PRIVATE KEY' in csec):
        print('WARNING: COINBASE_API_SECRET looks like a PEM private key (BEGIN ... PRIVATE KEY)')
        print('  > CCXT expects a plain API secret for classic keys; use triple-quoted TOML strings or consider classic keys for CCXT.')
        errs += 1

    # Check for paste error (secret equals key)
    if ckey and csec and ckey == csec:
        print('ERROR: COINBASE_API_SECRET appears to equal the API key (paste error). Please fix.')
        errs += 1

    if errs == 0:
        print('Secrets format looks OK for the checks run (no common issues detected).')
        return 0
    else:
        print(f'{errs} issue(s) found. Fix or confirm and re-run.')
        return 2


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--secrets-file", default=None, help="Path to secrets.toml (defaults to .streamlit/secrets.toml)")
    args = parser.parse_args()
    secrets_file = Path(args.secrets_file) if args.secrets_file else None
    sys.exit(run_check(secrets_file))
