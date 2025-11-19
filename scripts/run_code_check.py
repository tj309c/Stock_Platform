"""
Run a full critical error and static analysis check across the codebase.
Creates a JSON and human-readable summary of problems detected.

Checks performed:
- Syntax check (compile all .py files)
- AST-based import discovery and dependency verification (no module imports executed)
- 3rd-party dependency import verification (subprocess import)
- Run pytest (tests/unit by default)
- Run flake8 or pyflakes if available

Usage:
    python scripts/run_code_check.py [options]

Options:
    --tests PATH    Path to tests to run (default: tests/unit)
    --report FILE   Write JSON report file (default: data/logs/codecheck_report.json)
    --skip-pytest   Don't run pytest
    --skip-lint     Don't run flake8/pyflakes lint
    --fail-fast     Stop on first critical error

Notes:
- The check avoids importing repository modules to prevent side-effects; instead checks imports via static analysis and subprocess import attempts for 3rd-party packages.
- The script is safe to run in a dev environment and produces a summary for triage.
"""

import argparse
import ast
import json
import os
import re
import subprocess
import sys
import traceback
from collections import defaultdict
from typing import Dict, List, Set, Tuple

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

EXCLUDE_DIRS = {'.venv', 'venv', '__pycache__', '.git', 'data/logs'}


def find_py_files(root: str) -> List[str]:
    matches = []
    for dirpath, dirnames, filenames in os.walk(root):
        # Skip excluded directories
        parts = dirpath.replace(root, '').split(os.sep)
        if any(p in EXCLUDE_DIRS for p in parts if p):
            continue
        for fn in filenames:
            if fn.endswith('.py'):
                matches.append(os.path.join(dirpath, fn))
    return matches


def compile_check(files: List[str]) -> Dict[str, List[Dict]]:
    results = {'syntax_errors': []}
    for path in files:
        try:
            with open(path, 'r', encoding='utf-8') as f:
                src = f.read()
            compile(src, path, 'exec')
        except SyntaxError as e:
            results['syntax_errors'].append({
                'file': path,
                'lineno': getattr(e, 'lineno', None),
                'msg': str(e)
            })
        except Exception as e:
            # Unexpected read/IO error
            results['syntax_errors'].append({'file': path, 'lineno': None, 'msg': f'Error reading/compiling: {e}'})
    return results


def parse_imports_from_ast(files: List[str]) -> Tuple[Dict[str, Set[str]], Dict[str, Set[str]]]:
    """
    Returns (module_to_imports, module_to_from_imports)
    module_to_imports: mapping file -> set of 'import module' roots (first part)
    module_to_from_imports: mapping file -> set of 'from module import X' roots
    """
    module_to_imports: Dict[str, Set[str]] = defaultdict(set)
    module_to_from_imports: Dict[str, Set[str]] = defaultdict(set)
    for path in files:
        try:
            with open(path, 'r', encoding='utf-8') as fh:
                src = fh.read()
            tree = ast.parse(src, filename=path)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for n in node.names:
                        name = n.name.split('.')[0]
                        module_to_imports[path].add(name)
                elif isinstance(node, ast.ImportFrom):
                    # node.module can be None (e.g., relative imports: from . import something)
                    if node.module:
                        name = node.module.split('.')[0]
                        module_to_from_imports[path].add(name)
                    else:
                        # relative import; treat as local
                        module_to_from_imports[path].add('.')
        except Exception as e:
            # If parsing fails for some reason, record
            module_to_imports[path].add(f'__AST_ERROR__:{e}')
    return module_to_imports, module_to_from_imports


def is_local_module(name: str, root: str) -> bool:
    """Check if import name is a local (repo) module by searching for a matching file or package under root."""
    # If the name is '.' (relative import), mark as local
    if name == '.':
        return True
    # Search recursively for a module file or package with this name under root or root/src
    search_paths = [root, os.path.join(root, 'src')]
    for base in search_paths:
        if not os.path.exists(base):
            continue
        for dirpath, dirnames, filenames in os.walk(base):
            if f'{name}.py' in filenames:
                return True
            if name in dirnames and os.path.exists(os.path.join(dirpath, name, '__init__.py')):
                return True
    return False


def check_third_party_imports(import_names: Set[str]) -> Dict[str, bool]:
    """Attempt to import each module name in a subprocess python -c 'import name' to catch ImportError.
    Returns mapping name -> True if importable, False otherwise
    """
    results = {}
    python_exe = sys.executable
    for name in sorted(import_names):
        if not name:
            continue
        # Built-in and local packages may succeed; we only care about import errors
        # Skip obvious stdlib names that are always present
        cmd = [python_exe, '-c', f"import {name}; print({name}.__name__) if hasattr({name}, '__name__') else print('OK')"]
        try:
            out = subprocess.run(cmd, capture_output=True, text=True, check=False)
            if out.returncode == 0:
                results[name] = True
            else:
                results[name] = False
        except Exception as e:
            results[name] = False
    return results


def installed_package_check(requirements_path: str) -> Dict[str, bool]:
    """Parse requirements.txt and attempt to import core package names to confirm installation.
    This is heuristic: for a requirement 'pandas>=2' we try 'import pandas'.
    """
    results = {}
    if not os.path.exists(requirements_path):
        return results
    with open(requirements_path, 'r', encoding='utf-8') as fh:
        for ln in fh:
            ln = ln.strip()
            if not ln or ln.startswith('#'):
                continue
            pkg = re.split('[<>=]', ln)[0].strip()
            # map common package names to import names if they differ
            mapping = {
                'yfinance': 'yfinance',
                'pandas': 'pandas',
                'numpy': 'numpy',
                'flask-cors': 'flask_cors',
            }
            import_name = mapping.get(pkg, pkg.replace('-', '_'))
            try:
                subprocess.run([sys.executable, '-c', f'import {import_name}'], check=True, capture_output=True)
                results[pkg] = True
            except subprocess.CalledProcessError:
                results[pkg] = False
            except Exception:
                results[pkg] = False
    return results


def run_pytest(tests_path: str) -> Dict[str, object]:
    cmd = [sys.executable, '-m', 'pytest', '-q', tests_path]
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, check=False)
        return {'returncode': out.returncode, 'stdout': out.stdout, 'stderr': out.stderr}
    except Exception as e:
        return {'returncode': 2, 'stdout': '', 'stderr': str(e)}


def run_flake_or_pyflakes(root: str) -> Dict[str, object]:
    # Try flake8 first, then pyflakes, otherwise skip
    try:
        out = subprocess.run([sys.executable, '-m', 'flake8', '--version'], capture_output=True, text=True, check=True)
        cmd = [sys.executable, '-m', 'flake8', root]
        r = subprocess.run(cmd, capture_output=True, text=True, check=False)
        return {'tool': 'flake8', 'returncode': r.returncode, 'stdout': r.stdout, 'stderr': r.stderr}
    except Exception:
        try:
            out = subprocess.run([sys.executable, '-m', 'pyflakes', '--version'], capture_output=True, text=True, check=True)
            cmd = [sys.executable, '-m', 'pyflakes', root]
            r = subprocess.run(cmd, capture_output=True, text=True, check=False)
            return {'tool': 'pyflakes', 'returncode': r.returncode, 'stdout': r.stdout, 'stderr': r.stderr}
        except Exception:
            return {'tool': None, 'returncode': None, 'stdout': '', 'stderr': 'flake8/pyflakes not installed'}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--report', default=os.path.join(ROOT, 'data', 'logs', 'codecheck_report.json'))
    parser.add_argument('--tests', default=os.path.join(ROOT, 'tests', 'unit'))
    parser.add_argument('--skip-pytest', action='store_true')
    parser.add_argument('--skip-lint', action='store_true')
    parser.add_argument('--fail-fast', action='store_true')
    args = parser.parse_args()

    print(f'Running full code check in {ROOT}')
    all_files = find_py_files(ROOT)
    print(f'Python files found: {len(all_files)}')

    report = {
        'root': ROOT,
        'python_files': len(all_files),
        'syntax_errors': [],
        'import_tree': {},
        'missing_imports': {},
        'requirements_checks': {},
        'pytest': None,
        'linter': None,
    }

    syntax = compile_check(all_files)
    report['syntax_errors'] = syntax['syntax_errors']
    if report['syntax_errors']:
        print(f"Syntax errors: {len(report['syntax_errors'])}")
        for e in report['syntax_errors'][:10]:
            print(f" - {e['file']}:{e['lineno']} {e['msg']}")
        if args.fail_fast:
            print('Fail-fast: exiting due to syntax error')
            with open(args.report, 'w', encoding='utf-8') as fh:
                json.dump(report, fh, indent=2)
            sys.exit(1)

    ast_imports, ast_froms = parse_imports_from_ast(all_files)
    report['import_tree']['imports'] = {k: sorted(list(v)) for k, v in ast_imports.items()}
    report['import_tree']['from_imports'] = {k: sorted(list(v)) for k, v in ast_froms.items()}

    # Build set of unique module names (non-local) for 3rd party import checking
    all_import_names = set()
    local_imports = set()
    for fn, names in ast_imports.items():
        for n in names:
            if is_local_module(n, ROOT):
                local_imports.add(n)
            else:
                all_import_names.add(n)
    for fn, names in ast_froms.items():
        for n in names:
            if is_local_module(n, ROOT):
                local_imports.add(n)
            else:
                all_import_names.add(n)

    report['import_tree']['local_imports'] = sorted(list(local_imports))
    report['import_tree']['third_party_candidates'] = sorted(list(all_import_names))

    print(f'Checking third-party imports: {len(all_import_names)} candidates')
    import_results = check_third_party_imports(all_import_names)
    report['missing_imports'] = {k: v for k, v in import_results.items() if not v}
    if report['missing_imports']:
        print(f"Missing third-party imports: {len(report['missing_imports'])}")
        for k, v in list(report['missing_imports'].items())[:20]:
            print(f" - {k}")
        if args.fail_fast:
            print('Fail-fast: exiting due to missing imports')
            with open(args.report, 'w', encoding='utf-8') as fh:
                json.dump(report, fh, indent=2)
            sys.exit(2)

    # Check requirements file
    reqs = os.path.join(ROOT, 'requirements.txt')
    if os.path.exists(reqs):
        reqs_res = installed_package_check(reqs)
        report['requirements_checks'] = reqs_res
        missing_pkgs = {k: v for k, v in reqs_res.items() if not v}
        if missing_pkgs:
            print(f"Missing packages from requirements: {len(missing_pkgs)}")
            for k in list(missing_pkgs)[:20]:
                print(f" - {k}")
        else:
            print('All requirements appear importable')

    if not args.skip_pytest:
        print(f'Running pytest on: {args.tests}')
        pytest_res = run_pytest(args.tests)
        report['pytest'] = pytest_res
        print(f"pytest finished with returncode {pytest_res['returncode']}")

    if not args.skip_lint:
        print('Running flake8/pyflakes lint')
        lint_res = run_flake_or_pyflakes(ROOT)
        report['linter'] = lint_res
        if lint_res['tool']:
            print(f"{lint_res['tool']} returned {lint_res['returncode']}")
        else:
            print('No linter detected (flake8/pyflakes not installed)')

    os.makedirs(os.path.dirname(args.report), exist_ok=True)
    with open(args.report, 'w', encoding='utf-8') as fh:
        json.dump(report, fh, indent=2)

    print('\nSummary:')
    print(f" - Python files scanned: {report['python_files']}")
    print(f" - Syntax errors: {len(report['syntax_errors'])}")
    print(f" - Third-party import failures: {len(report['missing_imports'])}")
    if report['pytest']:
        print(f" - pytest return: {report['pytest']['returncode']}")
    if report['linter'] and report['linter']['tool']:
        print(f" - linter: {report['linter']['tool']} return code: {report['linter']['returncode']}")

    rc = 0
    if report['syntax_errors']:
        rc = 1
    elif report['missing_imports']:
        rc = 2
    elif report['pytest'] and report['pytest']['returncode'] != 0:
        rc = 3
    elif report['linter'] and report['linter']['tool'] and report['linter']['returncode'] != 0:
        rc = 4

    sys.exit(rc)


if __name__ == '__main__':
    main()
