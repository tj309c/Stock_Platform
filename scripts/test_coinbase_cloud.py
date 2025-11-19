"""
Test Coinbase Cloud API using a JSON API key (organization key + PEM) by
- loading the JSON key file (fields: name, privateKey),
- using the privateKey (PEM) to sign a short-lived ES256 JWT using PyJWT,
- making a safe read-only request to Coinbase Cloud (e.g., /accounts or /products),
- printing response or helpful diagnostics.

Usage:
  python scripts/test_coinbase_cloud.py --keyfile c:\path\to\cdp_api_key.json

Important: This script uses PyJWT and cryptography to sign JWTs. If those
libraries are not installed, the script will print instructions.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import requests


def check_deps():
    try:
        import jwt as pyjwt  # noqa: F401
    except Exception as e:
        print("Missing dependency: PyJWT (pip install PyJWT[crypto])")
        raise
    try:
        # cryptography is required for using PEM private keys
        import cryptography  # noqa: F401
    except Exception as e:
        print("Missing dependency: cryptography (pip install cryptography)")
        raise


def load_json_key(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(path)
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def build_jwt(name: str, pem_private_key: str, ttl_seconds: int = 30, extra_claims: dict | None = None, headers: dict | None = None) -> str:
    """
    Build an ES256 JWT signed using provided PEM private key.
    We set `iss` to the key name and a short lifetime (ttl_seconds).

    Note: This JWT format is an attempt at Coinbase Cloud-style auth. If the JWT
    format or claims differ for your key, you may need to consult Coinbase Cloud's
    documentation for precise claims.
    """
    import jwt as pyjwt
    now = int(time.time())
    payload = {"iss": name, "iat": now, "exp": now + ttl_seconds}
    if extra_claims:
        payload.update(extra_claims)

    token = pyjwt.encode(payload, pem_private_key, algorithm="ES256", headers=headers or {})
    return token


def call_coinbase_cloud(jwt_token: str, endpoint: str = "/v2/accounts") -> tuple[int, dict | None, str | None]:
    """Make a read-only request to Coinbase Cloud API using Authorization: Bearer JWT"""
    url = f"https://api.coinbase.com{endpoint}"
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Accept": "application/json",
    }
    try:
        r = requests.get(url, headers=headers, timeout=15)
        try:
            body = r.json()
        except Exception:
            body = None
        return r.status_code, body, r.text if body is None else None
    except Exception as e:
        return 0, None, str(e)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--keyfile", required=True, help="Path to JSON API key from Coinbase Cloud")
    parser.add_argument("--endpoint", default="/v2/accounts", help="Coinbase Cloud API endpoint to query; default /v2/accounts")
    args = parser.parse_args()

    keyfile = Path(args.keyfile)
    if not keyfile.exists():
        print(f"Key file not found: {keyfile}")
        return 2

    try:
        check_deps()
    except Exception:
        return 3

    try:
        content = load_json_key(keyfile)
    except Exception as e:
        print(f"Failed to load JSON key: {e}")
        return 2

    # Validate JSON content
    name = content.get("name")
    privateKey = content.get("privateKey")
    if not name or not privateKey:
        print("JSON key missing 'name' or 'privateKey' fields. Inspect the file and confirm structure.")
        return 2

    print("Loaded key name:", name)

    # Build JWT
    try:
        # Try a few common claim/header combos used by JWT-signed APIs
        attempts = []
        # name can be full path: organizations/<org-id>/apiKeys/<key-id>
        parts = name.split("/")
        key_id = parts[-1] if parts else name
        org_id = "/".join(parts[:2]) if len(parts) >= 2 else name
        attempts.append(({"iss": name}, None))
        # iss as organization id and kid header as the key id
        attempts.append(({"iss": org_id}, {"kid": key_id}))
        attempts.append(({"sub": name}, None))
        attempts.append(({"iss": name, "sub": name}, None))
        attempts.append(({"iss": name, "sub": name, "aud": "https://api.coinbase.com"}, None))
        # include 'kid' header (some APIs require a key-id header)
        attempts.append(({"iss": name, "sub": name}, {"kid": name}))
        # try with org-id and kid header
        attempts.append(({"iss": org_id, "sub": org_id}, {"kid": key_id}))

        jwt_token = None
        last_status = None
        last_body = None
        for claims, hdrs in attempts:
            try:
                token = build_jwt(name, privateKey, ttl_seconds=30, extra_claims=claims, headers=hdrs)
            except Exception as e:
                print("Failed to create JWT for claims", claims, "error:", e)
                continue
            status, body, raw = call_coinbase_cloud(token, endpoint=args.endpoint)
            print(f"Tried claims={claims} headers={hdrs} -> HTTP {status}")
            if body is not None:
                print(json.dumps(body, indent=2))
            else:
                print("Raw response or error:", raw)
            last_status, last_body = status, body
            if status == 200:
                jwt_token = token
                break

        if jwt_token is None:
            print("All JWT attempts failed. Last HTTP status:", last_status)
            return 2
    except Exception as e:
        print("Failed to construct JWT:", e)
        return 2

    print("Attempting call to Coinbase Cloud using JWT (read-only)...")
    status, body, raw = call_coinbase_cloud(jwt_token, endpoint=args.endpoint)
    print("HTTP status:", status)
    if body is not None:
        print("Response JSON:")
        print(json.dumps(body, indent=2))
        return 0 if status == 200 else 2
    else:
        print("Raw response or error:", raw)
        return 2


if __name__ == "__main__":
    sys.exit(main())
