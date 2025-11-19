#!/usr/bin/env python3
"""
Migrate secrets from repo root `secrets.toml` to `.streamlit/secrets.toml`.
This script is interactive by default and will not overwrite an existing `.streamlit/secrets.toml` unless `--force` is passed.

Usage:
    python scripts/migrate_repo_secrets_to_dotstreamlit.py
    python scripts/migrate_repo_secrets_to_dotstreamlit.py --force
"""
from __future__ import annotations
import argparse
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parent.parent
REPO_SECRETS = ROOT / 'secrets.toml'
DST_DIR = ROOT / '.streamlit'
DST_SECRETS = DST_DIR / 'secrets.toml'


def main():
    parser = argparse.ArgumentParser(description='Migrate secrets.toml to .streamlit/secrets.toml')
    parser.add_argument('--force', action='store_true', help='Overwrite .streamlit/secrets.toml if exists')
    parser.add_argument('--dry-run', action='store_true', help='Only report keys that would migrate (no copy)')
    parser.add_argument('--show-keys', action='store_true', help='Show list of keys found in the repo-root secrets file (no values)')
    args = parser.parse_args()

    if not REPO_SECRETS.exists():
        print('No secrets.toml found at repository root. Nothing to do.')
        return 0

    # parse the repo-secret file and show recommendations
    found_recommended = {}
    RECOMMENDED_KEYS = [
        'FMP_API_KEY', 'POLYGON_API_KEY', 'COINBASE_API_KEY', 'COINBASE_API_SECRET', 'COINBASE_API_PASSWORD',
        'OPENAI_API_KEY', 'ANTHROPIC_API_KEY', 'GEMINI_API_KEY', 'XAI_API_KEY',
        'FINNHUB_API_KEY', 'NEWS_API_KEY', 'REDDIT_CLIENT_ID', 'REDDIT_CLIENT_SECRET', 'REDDIT_USER_AGENT'
    ]
    # Provide user-facing descriptions for important keys
    RECOMMENDED_KEY_DESC = {
        'FMP_API_KEY': 'Fallback fundamental data (Financial Modeling Prep) when YahooFinance fails',
        'POLYGON_API_KEY': 'Professional market data (Polygon.io) for screeners & backtesting (optional but recommended)',
        'COINBASE_API_KEY': 'Coinbase API Key (legacy: for CCXT authenticated endpoints)',
        'COINBASE_API_NAME': 'Coinbase API Key (preferred name for CCXT authenticated endpoints)',
        'COINBASE_API_SECRET': 'Coinbase API Secret (legacy: paired with COINBASE_API_KEY)',
        'COINBASE_PRIVATE_KEY': 'Coinbase private key (preferred: COINBASE_PRIVATE_KEY for private keys)',
        'COINBASE_API_PASSWORD': 'Coinbase API Password (if required by your Coinbase product or passphrase)',
        'OPENAI_API_KEY': 'OpenAI GPT-4+ key for LLM features',
        'ANTHROPIC_API_KEY': 'Anthropic Claude key for LLM features',
        'GEMINI_API_KEY': 'Google Gemini key if using Gemini',
        'XAI_API_KEY': 'Grok / XAI key if using that provider',
        'FINNHUB_API_KEY': 'Finnhub key (news, fundamentals opt-in)',
        'NEWS_API_KEY': 'NewsAPI.org key (optional, used for news sentiment)',
        'REDDIT_CLIENT_ID': 'Reddit API client id (for Reddit scraping)',
        'REDDIT_CLIENT_SECRET': 'Reddit API client secret',
        'REDDIT_USER_AGENT': 'Reddit user agent string required by some reddit scrapers'
    }
    try:
        text = REPO_SECRETS.read_text(encoding='utf-8')
        try:
            import tomllib as toml
        except Exception:
            try:
                import toml as toml
            except Exception:
                toml = None
        parsed = toml.loads(text) if toml else {}
        for k in RECOMMENDED_KEYS:
            found_recommended[k] = k in parsed
    except Exception:
        # If we cannot parse keys, leave mapping blank but continue
        parsed = {}
        for k in RECOMMENDED_KEYS:
            found_recommended[k] = False

    if args.show_keys or args.dry_run:
        print('\nKeys presence summary (repo-root secrets.toml):')
        for k in RECOMMENDED_KEYS:
            print(f"  - {k}: {'FOUND' if found_recommended.get(k) else 'MISSING'} — {RECOMMENDED_KEY_DESC.get(k, '')}")
        # show any keys (no values) found in the secrets file if user requested
        if args.show_keys:
            print('\nAll keys present in secrets.toml (names only):')
            for k in parsed.keys():
                print('  -', k)
        if args.dry_run:
            print('\nDry-run mode: no files will be copied. Use --force to perform copy.')
            return 0

    if DST_SECRETS.exists() and not args.force:
        print('Destination .streamlit/secrets.toml already exists. Use --force to overwrite.')
        print('Aborting.')
        return 2

    if not DST_DIR.exists():
        DST_DIR.mkdir(parents=True)

    # We don't modify the repo root secret file; we copy it
    try:
        shutil.copy2(REPO_SECRETS, DST_SECRETS)
        print(f'Copied {REPO_SECRETS} to {DST_SECRETS}')
        print('Reminder: Do not commit secrets to source control. Use `git rm --cached .streamlit/secrets.toml` if necessary.')
        return 0
    except Exception as e:
        print('Failed to copy secrets:', e)
        return 1


if __name__ == '__main__':
    sys.exit(main())
