import os
import sys
import tempfile
import subprocess
from pathlib import Path


def test_convert_pem_double_quoted_top_level(tmp_path):
    secrets_file = tmp_path / "secrets.toml"
    pem_content = "-----BEGIN EC PRIVATE KEY-----\\nMII...TEST...\\n-----END EC PRIVATE KEY-----"
    content = f'COINBASE_API_KEY = "abc123"\nCOINBASE_API_SECRET = "{pem_content}"\n'
    secrets_file.write_text(content, encoding='utf-8')

    # Run the conversion script with --apply
    cmd = [sys.executable, os.path.join(os.path.dirname(__file__), '..', '..', 'scripts', 'convert_pem_secret_to_toml.py'), '--apply', '--secrets-file', str(secrets_file)]
    # Ensure we run from project root; sometimes the script uses relative paths
    subprocess.check_call(cmd, cwd=str(tmp_path))

    # Confirm the conversion to triple quotes happened
    new_text = secrets_file.read_text(encoding='utf-8')
    assert 'COINBASE_API_SECRET = """' in new_text
    assert '-----BEGIN EC PRIVATE KEY-----' in new_text


def test_convert_pem_in_coinbase_block(tmp_path):
    secrets_file = tmp_path / "secrets.toml"
    pem = "-----BEGIN EC PRIVATE KEY-----\\nMII...TEST...\\n-----END EC PRIVATE KEY-----"
    content = "[COINBASE]\napiKey = \"abc123\"\nsecret = \"" + pem + "\"\n"
    secrets_file.write_text(content, encoding='utf-8')

    cmd = [sys.executable, os.path.join(os.path.dirname(__file__), '..', '..', 'scripts', 'convert_pem_secret_to_toml.py'), '--apply', '--secrets-file', str(secrets_file)]
    subprocess.check_call(cmd, cwd=str(tmp_path))

    new_text = secrets_file.read_text(encoding='utf-8')
    assert 'secret = """' in new_text or 'api_secret = """' in new_text


def test_convert_truncated_pem_warns(tmp_path):
    secrets_file = tmp_path / "secrets.toml"
    # Single-line PEM (truncated/no newline) – common paste error
    pem = "-----BEGIN EC PRIVATE KEY-----MII...TRUNCATED...-----END EC PRIVATE KEY-----"
    content = f'COINBASE_API_KEY = "abc123"\nCOINBASE_API_SECRET = "{pem}"\n'
    secrets_file.write_text(content, encoding='utf-8')

    cmd = [sys.executable, os.path.join(os.path.dirname(__file__), '..', '..', 'scripts', 'convert_pem_secret_to_toml.py'), '--apply', '--secrets-file', str(secrets_file)]
    import subprocess
    p = subprocess.run(cmd, cwd=str(tmp_path), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    assert p.returncode == 0
    assert 'WARNING: The PEM string for key' in p.stdout
