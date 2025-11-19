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


ROOT = Path(__file__).resolve().parent.parent
SECRETS_PATH = ROOT / ".streamlit" / "secrets.toml"


def find_pem_double_quoted_entries(text: str) -> dict:
    # Find keys that appear to be double-quoted strings with PEM headers inside (invalid TOML if contains newlines)
    # Pattern: KEY = "...BEGIN ... PRIVATE KEY-----\n...\n-----END ... PRIVATE KEY-----"
    pattern = re.compile(r"(?P<key>\w+)\s*=\s*\"(?P<val>-----BEGIN [^-]+ PRIVATE KEY-----.*?-----END [^-]+ PRIVATE KEY-----)\"", flags=re.S)
    matches = {m.group('key'): m.group('val') for m in pattern.finditer(text)}
    return matches


def convert_to_triple_quote_block(key: str, val: str) -> str:
    return f'{key} = """{val}"""'


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="Apply changes (write file). Without this, a dry-run will be performed.")
    parser.add_argument("--show-keys", action="store_true", help="Show keys that would be converted")
    args = parser.parse_args()

    if not SECRETS_PATH.exists():
        print(f"No {SECRETS_PATH} found. Nothing to do.")
        return 2

    text = SECRETS_PATH.read_text(encoding="utf-8")
    found = find_pem_double_quoted_entries(text)
    if not found:
        print("No double-quoted PEM entries found (nothing to convert).")
        return 0

    print(f"Found PEM-like entries: {', '.join(found.keys())}")
    if args.show_keys:
        for k, v in found.items():
            print(f"--- {k} ---\n{v[:200]}...\n")

    new_text = text
    for k, v in found.items():
        old = f'{k} = "{v}"'
        new = convert_to_triple_quote_block(k, v)
        new_text = new_text.replace(old, new)

    if args.apply:
        bak = SECRETS_PATH.with_suffix(SECRETS_PATH.suffix + ".bak")
        print(f"Backing up original secrets to {bak}")
        shutil.copy(SECRETS_PATH, bak)
        SECRETS_PATH.write_text(new_text, encoding="utf-8")
        print("Updated secrets.toml. Please review the backup and new file for correctness.")
    else:
        print("Dry-run: the following replacements would be made:")
        for k, v in found.items():
            print(f" - {k}: double-quoted PEM -> triple-quoted block")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

