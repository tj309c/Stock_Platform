"""
A small test script to check CCXT connectivity to Coinbase and fallback public exchanges.

Usage:
  python scripts/test_ccxt_coinbase.py

The script will read COINBASE_API_KEY, COINBASE_API_SECRET, COINBASE_API_PASSWORD from environment variables
or from `.streamlit/secrets.toml` if present. If Coinbase auth is missing or fails, it will try public exchanges
(binance, kraken, coinbasepro) to fetch a ticker for BTC/USDT or BTC/USD.

This script is intentionally lightweight and prints helpful messages for developers to diagnose connectivity
and credential issues.
"""

from __future__ import annotations

import os
import sys
import json
from pathlib import Path

# Prefer the pure stdlib tomllib if available (Python 3.11+), otherwise fallback to toml package
_has_std_tomllib = False
_toml_module = None
_tomllib_std = None
try:
    import tomllib as _tomllib_std
    _has_std_tomllib = True
except Exception:
    try:
        import toml as _toml_thirdparty
        _toml_module = _toml_thirdparty
    except Exception:
        _toml_module = None


try:
    import ccxt
except Exception as e:
    print("ERROR: The 'ccxt' package is not installed in the current Python environment.")
    print("Install requirements: pip install -r requirements.txt")
    print(e)
    sys.exit(1)


def load_dotstreamlit_secrets() -> dict:
    """Try loading `.streamlit/secrets.toml` and return as dict if available.
    Falls back to empty dict when not present or when tomllib/toml is not available.
    """
    repo_root = Path(__file__).resolve().parent.parent
    secrets_path = repo_root / ".streamlit" / "secrets.toml"

    if not secrets_path.exists():
        return {}

    if _has_std_tomllib is False and _toml_module is None:
        print("Warning: No TOML parser available. Can't read `.streamlit/secrets.toml`.")
        return {}

    import re
    try:
        if _has_std_tomllib and _tomllib_std is not None:
            with open(secrets_path, "rb") as f:
                data = _tomllib_std.load(f)
        elif _toml_module is not None:
            # Use the third-party toml.load which expects a text file
            with open(secrets_path, "r", encoding="utf-8") as f:
                data = _toml_module.load(f)
        else:
            data = {}
    except Exception as e:
        # `tomllib` or `toml` may fail to parse if the file contains invalid TOML, e.g.,
        # a double-quoted string spread over multiple lines (which TOML doesn't allow).
        # Attempt a fallback by scanning the raw file for known key patterns.
        print("Failed to read `.streamlit/secrets.toml`:", e)
        print("Attempting a raw-text fallback to extract keys from the file (non-strict parsing)")

        raw = ""
        try:
            with open(secrets_path, "r", encoding="utf-8") as fh:
                raw = fh.read()
        except Exception as e2:
            print("Also failed to read .streamlit/secrets.toml as raw text:", e2)
            return {}

        data = {}

        # Try to extract both triple-quoted and normal double-quoted values, allowing newlines
        def _extract_key(text, key):
            # Triple-quoted (TOML multiline basic string) - non-greedy capture
            m = re.search(rf'{key}\s*=\s*"""(.*?)"""', text, flags=re.S)
            if m:
                return m.group(1)
            # Double-quoted but allow newlines (non-greedy)
            m = re.search(rf'{key}\s*=\s*"(.*?)"', text, flags=re.S)
            if m:
                return m.group(1)
            # Single-quoted or simple token
            m = re.search(rf"{key}\s*=\s*'([^']*)'", text, flags=re.S)
            if m:
                return m.group(1)
            return None

        candidate_keys = ["COINBASE_API_NAME", "COINBASE_API_KEY", "COINBASE_API_SECRET", "COINBASE_PRIVATE_KEY", "COINBASE_API_PASSWORD", "COINBASE_PASSWORD", "COINBASE_PASSPHRASE"]
        for k in candidate_keys:
            v = _extract_key(raw, k)
            if v is not None:
                data[k] = v
    except Exception as e:
        print("Failed to read `.streamlit/secrets.toml`:", e)
        return {}

    return data if isinstance(data, dict) else {}


def get_coinbase_credentials_from_env_or_secrets() -> dict:
    # First try environment variables
    creds: dict[str, str | None] = {
        "apiKey": os.getenv("COINBASE_API_NAME") or os.getenv("COINBASE_API_KEY") or os.getenv("COINBASE_KEY"),
        "secret": os.getenv("COINBASE_PRIVATE_KEY") or os.getenv("COINBASE_API_SECRET") or os.getenv("COINBASE_SECRET"),
        "password": os.getenv("COINBASE_API_PASSWORD") or os.getenv("COINBASE_PASSWORD") or os.getenv("COINBASE_PASSPHRASE")
    }
    creds = {k: v for k, v in creds.items() if v}
    if all(creds.values()):
        return creds

    # Try reading from `.streamlit/secrets.toml`
    secrets = load_dotstreamlit_secrets()
    # the secrets file might contain a nested `COINBASE` table or have top-level keys
    coinbase_section = secrets.get("COINBASE") or secrets.get("coinbase") or {}

    if isinstance(coinbase_section, dict) and coinbase_section:
        creds.update({
            "apiKey": creds.get("apiKey") or coinbase_section.get("apiKey") or coinbase_section.get("api_key"),
            "secret": creds.get("secret") or coinbase_section.get("secret") or coinbase_section.get("api_secret"),
            "password": creds.get("password") or coinbase_section.get("password") or coinbase_section.get("api_password"),
        })
    else:
        # Maybe the file has top-level keys like `COINBASE_API_KEY` and `COINBASE_API_SECRET`.
        # Support both variants so the fallback raw parser can still be used.
        if isinstance(secrets, dict):
            # Look for top-level keys
            top_api_key = secrets.get("COINBASE_API_NAME") or secrets.get("COINBASE_API_KEY") or secrets.get("COINBASE_KEY")
            top_secret = secrets.get("COINBASE_PRIVATE_KEY") or secrets.get("COINBASE_API_SECRET") or secrets.get("COINBASE_SECRET")
            top_pass = secrets.get("COINBASE_API_PASSWORD") or secrets.get("COINBASE_PASSPHRASE")
            if top_api_key or top_secret or top_pass:
                creds.update({
                    "apiKey": creds.get("apiKey") or top_api_key,
                    "secret": creds.get("secret") or top_secret,
                    "password": creds.get("password") or top_pass,
                })

    # Return only non-None values
    return {k: v for k, v in creds.items() if v}


def create_exchange(exchange_id: str, creds: dict | None = None) -> ccxt.Exchange:
    params = {}
    if creds:
        params = {
            "apiKey": creds.get("apiKey"),
            "secret": creds.get("secret"),
            "password": creds.get("password"),
        }

    try:
        ex_cls = getattr(ccxt, exchange_id)
    except AttributeError:
        raise RuntimeError(f"Exchange {exchange_id} is not available in ccxt build.")

    exchange = ex_cls({**params, "enableRateLimit": True})
    return exchange


def try_fetch_ticker_from_exchange(exchange: ccxt.Exchange, symbol: str) -> tuple[bool, dict | None, str | None]:
    try:
        ticker = exchange.fetch_ticker(symbol)
        return True, ticker, None
    except Exception as e:
        return False, None, str(e)


def main() -> int:
    print("Running CCXT Coinbase connectivity test")

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--verbose", action="store_true", help="Enable verbose ccxt logging (shows raw requests)")
    args = parser.parse_args()

    creds = get_coinbase_credentials_from_env_or_secrets()
    have_creds = bool(creds.get("apiKey") and creds.get("secret"))

    if have_creds:
        print("Found Coinbase credentials — trying an authenticated connection.")
        # Print a short summary of credential forms detected (masked) to help diagnose compatibility
        masked_key = (creds.get("apiKey") or "")
        if masked_key:
            mk = masked_key
            mk_masked = mk[:8] + "..." + mk[-6:] if len(mk) > 20 else mk
            print(f"Detected Coinbase API key: {mk_masked}")
            if mk.startswith("organizations/"):
                print("Note: The key looks like a Coinbase Cloud organization key (starts with 'organizations/').")
                print("CCXT may not support Coinbase Cloud keys directly; if you need authenticated CCXT access via Coinbase, use a classic API key/secret/password or the exchange-specific format.")
        secret_preview = creds.get("secret") or ""
        if secret_preview and ("BEGIN" in secret_preview and "PRIVATE KEY" in secret_preview):
            print("Note: The COINBASE_API_SECRET appears to be a PEM private key (BEGIN EC PRIVATE KEY). CCXT typically expects an API secret string, not a PEM file. Verify your secret format.")
    else:
        print("No Coinbase credentials found in env or .streamlit/secrets.toml — trying public fallback exchanges.")

    preferred_symbol_variants = ["BTC/USDT", "BTC/USD", "BTC/USDC", "XBT/USD"]

    # If we have credentials for Coinbase, try to use coinbase and coinbasepro
    tried_results = []

    if have_creds:
        for eid in ["coinbasepro", "coinbase"]:
            try:
                exchange = create_exchange(eid, creds)
                if args.verbose:
                    exchange.verbose = True
            except Exception as e:
                tried_results.append((eid, False, None, f"Init error: {e}"))
                continue

            for symbol in preferred_symbol_variants:
                ok, ticker, err = try_fetch_ticker_from_exchange(exchange, symbol)
                tried_results.append((eid, ok, ticker, err))
                if ok:
                    print(f"Authenticated success on {eid} {symbol}")
                    print(json.dumps(ticker, indent=2))
                    return 0
                else:
                    print(f"Authenticated {eid} {symbol} failed: {err}")

    # If we got here, either no creds or the authenticated exchange failed. Try public exchanges.
    public_exchanges = ["binance", "kraken", "coinbasepro", "coinbase"]
    print("Attempting public exchanges fallback: ", ", ".join(public_exchanges))

    for eid in public_exchanges:
        try:
            exchange = create_exchange(eid, None)
            if args.verbose:
                exchange.verbose = True
        except Exception as e:
            tried_results.append((eid, False, None, f"Init error: {e}"))
            continue

        for symbol in preferred_symbol_variants:
            ok, ticker, err = try_fetch_ticker_from_exchange(exchange, symbol)
            tried_results.append((eid, ok, ticker, err))
            if ok:
                print(f"Success on public {eid} {symbol}")
                print(json.dumps(ticker, indent=2))
                return 0

    # Nothing succeeded — print a helpful diagnostic summary
    print("All attempts to fetch BTC tickers failed.")
    print("Detailed results:")
    for eid, ok, ticker, err in tried_results:
        print(f"{eid:12} | success={ok} | err={err}")

    if not have_creds:
        print("If you need authenticated Coinbase features, add these keys to .streamlit/secrets.toml or environment variables:")
        print("COINBASE_API_KEY, COINBASE_API_SECRET, COINBASE_API_PASSWORD")

    # Final operational note: fallback strategy
    print('\nNOTE: If Coinbase connectivity or auth consistently fails, use supported public crypto data sources (Kraken, Binance, CoinGecko) as the pipeline primary for now and revisit Coinbase integration later. The system already supports CCXT-based fallbacks to public exchanges for continuity.')

    return 2


if __name__ == "__main__":
    sys.exit(main())
