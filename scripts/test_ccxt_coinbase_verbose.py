"""
Verbose CCXT Coinbase authenticated test.
Reads Coinbase credentials from `.streamlit/secrets.toml` or environment and
attempts `fetch_balance` with `exchange.verbose = True` so that headers and
signatures are printed. Use for diagnostics only.

Usage:
  python scripts/test_ccxt_coinbase_verbose.py
"""

from __future__ import annotations

import os
import sys
import importlib
import traceback
from pathlib import Path
from pprint import pprint

try:
    import ccxt
except ImportError:
    print("Please install ccxt in the venv: pip install -r requirements.txt")
    sys.exit(2)

ROOT = Path(__file__).resolve().parent.parent
SECRETS = ROOT / ".streamlit" / "secrets.toml"

def load_coinbase_creds() -> dict:
    # Env vars first
    ak = os.getenv('COINBASE_API_KEY')
    sk = os.getenv('COINBASE_API_SECRET')
    pw = os.getenv('COINBASE_API_PASSWORD')
    if ak and sk:
        return {'apiKey': ak, 'secret': sk, 'password': pw}
    # Try reading secrets file
    if SECRETS.exists():
        try:
            try:
                import tomllib as _toml
            except Exception:
                import toml as _toml
            parsed = _toml.loads(SECRETS.read_text(encoding='utf-8'))
        except Exception:
            # fallback raw scan
            text = SECRETS.read_text(encoding='utf-8')
            import re
            m_key = re.search(r'COINBASE_API_KEY\s*=\s*"([^"]+)"', text)
            m_secret = re.search(r'COINBASE_API_SECRET\s*=\s*"([\s\S]*?)"', text)
            if m_key and m_secret:
                return {'apiKey': m_key.group(1), 'secret': m_secret.group(1).strip(), 'password': None}
            return {}
        ak = parsed.get('COINBASE_API_KEY')
        sk = parsed.get('COINBASE_API_SECRET')
        pw = parsed.get('COINBASE_API_PASSWORD')
        return {'apiKey': ak, 'secret': sk, 'password': pw}
    return {}

def main():
    creds = load_coinbase_creds()
    if not creds.get('apiKey') or not creds.get('secret'):
        print('No Coinbase credentials found in environment or .streamlit/secrets.toml')
        return 2

    print('Loaded Coinbase API key:', creds.get('apiKey')[:10] + '...' + creds.get('apiKey')[-6:])
    secret_value = creds.get('secret') or ''
    # Print mask of secret length for diagnostic purposes (no full secret)
    print('Secret length:', len(secret_value), 'chars, newline_count:', secret_value.count('\n'))
    if len(secret_value) < 16:
        print('WARNING: secret looks very short — possibly not the full secret value.')
    # detect common mistakes: PEM, JSON cloud key, or accidentally pasted key=secret
    if 'PRIVATE KEY' in secret_value:
        print('\nDetected a PEM/Cloud-style key in COINBASE_API_SECRET which CCXT will not accept for classic auth.')
        print('If you intend to use CCXT (classic), create a classic API key with a plain secret string and update `.streamlit/secrets.toml` or your environment variables.')
        print('Use `scripts/convert_pem_secret_to_toml.py` to convert multiline PEM values to a TOML-friendly block if needed for Cloud usage.')
        # Quick in-place check for PEM formatting: look for BEGIN/END and newlines
        has_begin = '-----BEGIN' in secret_value
        has_end = '-----END' in secret_value
        newline_count = secret_value.count('\n')
        if not (has_begin and has_end and newline_count > 2):
            print('\nPEM appears incomplete or truncated (missing BEGIN/END or newlines).')
            print('TOML with double-quoted strings may have collapsed newlines; convert to triple-quoted block with `scripts/convert_pem_secret_to_toml.py` or store the full PEM in an environment variable.')
        else:
            print('\nPEM seems correctly formatted with', newline_count, 'newlines.')
    if secret_value.strip().startswith('{') and 'private_key' in secret_value:
        print('\nDetected what looks like a JSON Cloud key in the secret value. Use Coinbase Cloud JWT flow rather than CCXT classic auth.')
    exchange = ccxt.coinbase({'apiKey': creds.get('apiKey'), 'secret': secret_value, 'enableRateLimit': True})
    exchange.verbose = True
    print('Exchange id:', getattr(exchange, 'id', 'n/a'))
    print('Exchange version:', getattr(exchange, 'version', 'n/a'))

    # Some CCXT adapters may not implement fetch_balance for this exchange.
    if not getattr(exchange, 'has', {}).get('fetchBalance', False):
        print('This exchange does not advertise fetchBalance support via CCXT. Will attempt `fetch_accounts()` as an alternative.')
    try:
        print('Attempting fetch_balance() (authenticated)')
        balance = exchange.fetch_balance()
        print('Balance:')
        pprint(balance)
        return 0
    except Exception as e:
        print('Authenticated fetch_balance() failed:', type(e).__name__, e)
        # Print detailed CCXT last-response information for diagnostic purposes
        try:
            print('\n--- CCXT DIAGNOSTICS ---')
            print('last_http_status_code:', getattr(exchange, 'last_http_status_code', None))
            print('last_http_headers:')
            pprint(getattr(exchange, 'last_http_headers', None))
            print('last_http_response (raw):')
            pprint(getattr(exchange, 'last_http_response', None))
            print('last_json_response (parsed):')
            pprint(getattr(exchange, 'last_json_response', None))
        except Exception:
            print('Failed to print CCXT diagnostics:')
            traceback.print_exc()
        # Additional hints
        reason = 'Unknown'
        code = getattr(exchange, 'last_http_status_code', None)
        if code == 401:
            reason = '401 Unauthorized — likely wrong key/secret or using a Cloud PEM key where CCXT expects classic secret.'
        elif code == 403:
            reason = '403 Forbidden — check IP whitelisting or account permissions.'
        elif code == 503:
            reason = '503 Service Unavailable — endpoint deprecated or rate-limited; coinbasepro may be deprecated.'
        print('\nSuggested Remediation:')
        print('- Ensure you are using a "classic" Coinbase API key / secret (plain string) for CCXT. If using a Cloud PEM JSON key, you must use Coinbase Cloud flow instead (JWT).')
        print('- If using a PEM in the secrets file, convert to triple-quoted TOML with `scripts/convert_pem_secret_to_toml.py` or place them in environment variables.')
        print('- Verify the key has the required scopes (read/wallet) and any IP whitelist allows current IP.')
        print('- Try running `scripts/test_ccxt_coinbase.py --verbose` to capture more logs or enable exchange.verbose to see raw signing headers.')
        traceback.print_exc()
        return 2

if __name__ == '__main__':
    sys.exit(main())
