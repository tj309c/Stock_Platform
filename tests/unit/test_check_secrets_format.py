import os
import sys
import subprocess
import tempfile
from pathlib import Path


def run_check_with_file(secrets_file: Path) -> tuple[int, str]:
    cmd = [sys.executable, os.path.join(os.path.dirname(__file__), '..', '..', 'scripts', 'check_secrets_format.py'), '--secrets-file', str(secrets_file)]
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, cwd=str(secrets_file.parent))
    return p.returncode, p.stdout


def test_check_secrets_format_detects_paste_error(tmp_path):
    secrets_file = tmp_path / "secrets.toml"
    content = 'KRAKEN_API_KEY = "TESTKEY"\nKRAKEN_API_SECRET = "TESTKEY"\n'
    secrets_file.write_text(content, encoding='utf-8')
    rc, out = run_check_with_file(secrets_file)
    assert rc != 0
    assert 'appears to equal the API key' in out


def test_check_secrets_format_detects_pem(tmp_path):
    secrets_file = tmp_path / "secrets.toml"
    pem = '-----BEGIN EC PRIVATE KEY-----\\nMIITEST\\n-----END EC PRIVATE KEY-----'
    content = f'KRAKEN_API_KEY = "TESTKEY"\nKRAKEN_API_SECRET = "{pem}"\n'
    secrets_file.write_text(content, encoding='utf-8')
    rc, out = run_check_with_file(secrets_file)
    assert rc != 0
    assert 'looks like a PEM private key' in out
