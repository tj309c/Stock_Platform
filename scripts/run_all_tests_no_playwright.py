"""
Run the entire pytest suite with Playwright plugin autoload disabled.

This script sets the `PYTEST_DISABLE_PLUGIN_AUTOLOAD` environment variable to
avoid loading Playwright or other optional test plugins that can cause module
import issues (e.g., greenlet dependencies). It runs the full test suite and
exits with pytest's exit code.

Usage:
  python scripts/run_all_tests_no_playwright.py
  DEBUG=1 python scripts/run_all_tests_no_playwright.py  # verbose
"""
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

os.environ['PYTEST_DISABLE_PLUGIN_AUTOLOAD'] = '1'

def main():
    # Run the secrets format checker (optional) and fail early if misconfigured.
    try:
        from subprocess import run, PIPE
        check_cmd = [sys.executable, os.path.join(ROOT, 'scripts', 'check_secrets_format.py')]
        p = run(check_cmd, stdout=PIPE, stderr=PIPE, text=True)
        if p.returncode != 0:
            print('Secrets format checker returned non-zero exit code; failing early.')
            print(p.stdout)
            print(p.stderr)
            return p.returncode
    except Exception:
        # Don't fail tests if the checker itself fails on missing deps—just print warning
        import traceback
        print('Warning: secrets format check failed to run:')
        traceback.print_exc()

    import pytest
    args = ['-q']
    if os.environ.get('DEBUG_TESTS') == '1' or os.environ.get('DEBUG') == '1':
        args = ['-vv', '-s']
    # Allow passing any additional args via environment variable
    extra = os.environ.get('PYTEST_EXTRA_ARGS')
    if extra:
        args.extend(extra.split())
    try:
        return pytest.main(args)
    finally:
        pass

if __name__ == '__main__':
    sys.exit(main())
