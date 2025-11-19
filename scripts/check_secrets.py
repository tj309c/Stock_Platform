#!/usr/bin/env python
"""Check .streamlit/secrets.toml for required keys.
Usage: python scripts/check_secrets.py --keys FMP_API_KEY,POLYGON_API_KEY --file .streamlit/secrets.toml
"""
import argparse
from pathlib import Path
import sys

def load_toml(path: Path):
    if not path.exists():
        print(f"[ERROR] {path} not found")
        return None
    txt = path.read_text(encoding='utf-8')
    try:
        import tomllib as toml
    except Exception:
        try:
            import toml
        except Exception:
            toml = None
    if toml:
        try:
            return toml.loads(txt)
        except Exception:
            pass
    # fallback regex scan for simple keys
    data = {}
    import re
    for m in re.finditer(r"^([A-Z0-9_]+)\s*=\s*\"([\s\S]*?)\"$", txt, re.M):
        k = m.group(1)
        v = m.group(2)
        data[k] = v
    return data

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--keys", default="FMP_API_KEY,POLYGON_API_KEY,KRAKEN_API_KEY,KRAKEN_API_SECRET,OPENAI_API_KEY")
    parser.add_argument("--file", default=".streamlit/secrets.toml")
    args = parser.parse_args()
    keys = [k.strip() for k in args.keys.split(',') if k.strip()]
    p = Path(args.file)
    parsed = load_toml(p)
    if parsed is None:
        sys.exit(2)
    missing = []
    for k in keys:
        if k not in parsed or parsed.get(k) in (None, ''):
            # alias handling for the default exchange (KRAKEN) and fallback to legacy exchange key names
            if k == 'KRAKEN_API_KEY' and (parsed.get('KRAKEN_API_KEY') or parsed.get('KRAKEN_API_NAME') or parsed.get('BINANCE_API_KEY') or parsed.get('BINANCE_API_NAME') or parsed.get('COINBASE_API_NAME') or parsed.get('COINBASE_API_KEY')):
                continue
            if k == 'KRAKEN_API_SECRET' and (parsed.get('KRAKEN_API_SECRET') or parsed.get('KRAKEN_PRIVATE_KEY') or parsed.get('BINANCE_PRIVATE_KEY') or parsed.get('BINANCE_API_SECRET') or parsed.get('COINBASE_PRIVATE_KEY') or parsed.get('COINBASE_API_SECRET')):
                continue
            missing.append(k)
    if missing:
        print('[MISSING] The following keys are missing from {0}: {1}'.format(p, ','.join(missing)))
        sys.exit(3)
    print('[OK] All required keys found (or reasonable aliases present).')
    sys.exit(0)

if __name__ == '__main__':
    main()
