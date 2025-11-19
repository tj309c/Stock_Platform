"""
Simple secrets format checker for .streamlit/secrets.toml to be used as a diagnostic
or pre-commit hook. Flags common misconfiguration problems:
 - Binance API key starting with organizations/ (Cloud-style) or Coinbase org-style keys (legacy)
 - Exchange secret containing PEM (BEGIN ... PRIVATE KEY)
 - Exchange secret equal to API key (likely a paste error)

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
    # Prefer KRAKEN keys for detection; fall back to BINANCE/COINBASE legacy names
    m_key = (
        re.search(r'KRAKEN_API_NAME\s*=\s*"([^"]+)"', text)
        or re.search(r'KRAKEN_API_KEY\s*=\s*"([^"]+)"', text)
        or re.search(r'BINANCE_API_NAME\s*=\s*"([^"]+)"', text)
        or re.search(r'BINANCE_API_KEY\s*=\s*"([^"]+)"', text)
        or re.search(r'COINBASE_API_NAME\s*=\s*"([^"]+)"', text)
        or re.search(r'COINBASE_API_KEY\s*=\s*"([^"]+)"', text)
    )
    m_secret = (
        re.search(r'KRAKEN_PRIVATE_KEY\s*=\s*"([^"]+)"', text)
        or re.search(r'KRAKEN_API_SECRET\s*=\s*"([\s\S]*?)"', text)
        or re.search(r'BINANCE_PRIVATE_KEY\s*=\s*"([^"]+)"', text)
        or re.search(r'BINANCE_API_SECRET\s*=\s*"([\s\S]*?)"', text)
        or re.search(r'COINBASE_PRIVATE_KEY\s*=\s*"([^"]+)"', text)
        or re.search(r'COINBASE_API_SECRET\s*=\s*"([\s\S]*?)"', text)
    )
    if m_key:
        # Normalize to KRAKEN_* names so subsequent checks prefer Kraken keys
        data['KRAKEN_API_KEY'] = m_key.group(1)
    if m_secret:
        data['KRAKEN_API_SECRET'] = m_secret.group(1).strip()
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

    # Prefer KRAKEN keys for checks, but also accept BINANCE/COINBASE legacy names
    ckey = (
        parsed.get('KRAKEN_API_NAME')
        or parsed.get('KRAKEN_API_KEY')
        or parsed.get('BINANCE_API_NAME')
        or parsed.get('BINANCE_API_KEY')
        or parsed.get('COINBASE_API_NAME')
        or parsed.get('COINBASE_API_KEY')
    )
    csec = (
        parsed.get('KRAKEN_PRIVATE_KEY')
        or parsed.get('KRAKEN_API_SECRET')
        or parsed.get('BINANCE_PRIVATE_KEY')
        or parsed.get('BINANCE_API_SECRET')
        or parsed.get('COINBASE_PRIVATE_KEY')
        or parsed.get('COINBASE_API_SECRET')
    )

    # Check for org key
    if ckey and isinstance(ckey, str) and ckey.startswith('organizations/'):
        print('WARNING: Exchange API key looks like an organization-style key (starts with organizations/).')
        print('  > CCXT may not support org-style keys for authenticated requests; consider creating a classic API key for CCXT or using the vendor SDK for org-style keys.')
        errs += 1

    # Check for PEM secret
    if csec and isinstance(csec, str) and ('BEGIN' in csec and 'PRIVATE KEY' in csec):
        print('WARNING: Exchange private key looks like a PEM private key (BEGIN ... PRIVATE KEY)')
        print('  > CCXT expects a plain API secret for classic keys; triple-quoted TOML strings are a valid way to store PEM in TOML for migration. For CCXT classic keys, prefer a plaintext secret.')
        errs += 1

    # Check for paste error (secret equals key)
    if ckey and csec and ckey == csec:
        print('ERROR: Exchange secret appears to equal the API key (paste error). Please fix.')
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
