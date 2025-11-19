"""
Convert a PEM value in `.streamlit/secrets.toml` that is stored in a double-quoted
string (illegal TOML) into a TOML multiline triple-quoted string. This helps when
users paste private keys with newlines into a TOML file but didn't use triple quotes.

Usage:
  python scripts/convert_pem_secret_to_toml.py --dry-run
  python scripts/convert_pem_secret_to_toml.py --apply

By default, the script prints what it would change. Use `--apply` to write the change
and create a backup file: `.streamlit/secrets.toml.bak`.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import re
import shutil
import html


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SECRETS_PATH = ROOT / ".streamlit" / "secrets.toml"


def find_pem_double_quoted_entries(text: str) -> dict:
    """
    Find potential PEM strings that are double-quoted (invalid TOML multiline) and return mapping of
    a descriptive key -> dict with keys: 'key', 'match_text', 'pem', 'start', 'end'.
    - Detect top-level keys like COINBASE_API_SECRET
    - Detect nested COINBASE table keys: secret, api_secret, api_secret
    - Detect escaped newlines (\n) and replace them when converting.
    """
    results: dict = {}

    # Top-level keys
    toplevel_pattern = re.compile(r'(?P<key>[A-Z0-9_]+)\s*=\s*"(?P<val>-----BEGIN [^-]+ PRIVATE KEY-----.*?-----END [^-]+ PRIVATE KEY-----)"', flags=re.S)
    for m in toplevel_pattern.finditer(text):
        key = m.group('key')
        val = m.group('val')
        results[f'toplevel:{key}'] = {'key': key, 'match_text': m.group(0), 'pem': val, 'start': m.start(), 'end': m.end()}

    # Nested [COINBASE] table keys like `secret = "-----BEGIN..."
    # Capture simple cases inside the [COINBASE] block
    coinbase_block_pattern = re.compile(r'\[COINBASE\](?P<body>.*?)(?=\n\[[A-Z0-9_\]]|\Z)', flags=re.S | re.I)
    secret_entry_pattern = re.compile(r'(?P<key>secret|api_secret|COINBASE_API_SECRET|COINBASE_SECRET)\s*=\s*"(?P<val>-----BEGIN [^-]+ PRIVATE KEY-----.*?-----END [^-]+ PRIVATE KEY-----)"', flags=re.S | re.I)
    for mb in coinbase_block_pattern.finditer(text):
        body = mb.group('body')
        for s in secret_entry_pattern.finditer(body):
            key = s.group('key')
            val = s.group('val')
            full_match_start = mb.start() + s.start()
            full_match_end = mb.start() + s.end()
            results[f'coinbase:{key}:{full_match_start}'] = {'key': key, 'match_text': s.group(0), 'pem': val, 'start': full_match_start, 'end': full_match_end}

    # Also detect JSON-like Cloud keys accidentally pasted into a double-quote
    json_pattern = re.compile(r'(?P<key>[A-Z0-9_]+)\s*=\s*"(?P<val>\{\s*\"name\"\s*:\s*\".*?\".*?\})"', flags=re.S)
    for m in json_pattern.finditer(text):
        key = m.group('key')
        val = m.group('val')
        results[f'json:{key}'] = {'key': key, 'match_text': m.group(0), 'pem': None, 'json': val, 'start': m.start(), 'end': m.end()}

    return results


def convert_to_triple_quote_block(key: str, val: str) -> str:
    # Ensure the PEM has real newlines; if it contains `\n` sequences, unescape them.
    if isinstance(val, str) and '\\n' in val:
        val = val.replace('\\n', '\n')
    # Avoid accidentally creating trailing newlines being inside triple quotes
    return f'{key} = """{val}"""'


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="Apply changes (write file). Without this, a dry-run will be performed.")
    parser.add_argument("--show-keys", action="store_true", help="Show keys that would be converted")
    parser.add_argument("--secrets-file", default=None, help="Path to the secrets.toml to inspect (defaults to repo .streamlit/secrets.toml).")
    args = parser.parse_args()

    secrets_path = Path(args.secrets_file) if args.secrets_file else DEFAULT_SECRETS_PATH
    if not secrets_path.exists():
        print(f"No {secrets_path} found. Nothing to do.")
        return 2

    text = secrets_path.read_text(encoding="utf-8")
    found = find_pem_double_quoted_entries(text)
    if not found:
        print("No double-quoted PEM entries found (nothing to convert).")
        return 0

    print(f"Found PEM-like entries: {', '.join(found.keys())}")
    if args.show_keys:
        for k, v in found.items():
            print(f"--- {k} ---\n{v[:200]}...\n")

    new_text = text
    for fkey, meta in found.items():
        # Only convert entries that are PEM strings; skip JSON detection entries
        if meta.get('pem'):
            key_name = meta['key']
            pem = meta['pem']
            match_text = meta['match_text']
            # If the match contains escaped newlines (\n) in a double-quoted string, unescape them
            if '\\n' in match_text:
                # replace \n escapes in the stored value, not the entire match
                pem_unescaped = pem.replace('\\n', '\n')
            else:
                pem_unescaped = pem
            # Warn if PEM seems truncated (no newlines at all)
            if '\n' not in pem_unescaped and '\\n' not in match_text:
                print(f"WARNING: The PEM string for key {key_name} appears to be a single-line or truncated. Consider verifying the value; conversion may not fix content.")
            new_block = convert_to_triple_quote_block(key_name, pem_unescaped)
            new_text = new_text.replace(match_text, new_block)
        else:
            # JSON-like block placed in a double-quoted string; leave as is but warn
            print(f"Detected a JSON-like value assigned to {meta['key']} — not converting. Please store the JSON key separately (file or env var).")

    if args.apply:
        bak = secrets_path.with_suffix(secrets_path.suffix + ".bak")
        print(f"Backing up original secrets to {bak}")
        shutil.copy(secrets_path, bak)
        secrets_path.write_text(new_text, encoding="utf-8")
        print("Updated secrets.toml. Please review the backup and new file for correctness.")
    else:
        print("Dry-run: the following replacements would be made:")
        for k, v in found.items():
            print(f" - {k}: double-quoted PEM -> triple-quoted block")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

