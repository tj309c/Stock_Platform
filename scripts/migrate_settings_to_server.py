"""
Migrate local `data/config/settings.json` to server-backed store.

Usage:
  python scripts/migrate_settings_to_server.py --server-url http://localhost:5001

This posts the entire settings file to the server endpoint.
"""
import argparse
import json
from pathlib import Path
import requests


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--server-url', default='http://localhost:5001')
    args = parser.parse_args()
    p = Path(__file__).parent.parent / 'data' / 'config' / 'settings.json'
    if not p.exists():
        print('No local settings found at', p)
        return
    with open(p, 'r', encoding='utf-8') as fh:
        data = json.load(fh)
    url = f"{args.server_url}/settings"
    r = requests.post(url, json=data)
    r.raise_for_status()
    print('Migration completed')


if __name__ == '__main__':
    main()
