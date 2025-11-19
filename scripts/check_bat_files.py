#!/usr/bin/env python3
"""Simple check for obvious issues in .bat scripts.

This script is intentionally lightweight and used in CI or manual audits to
warn about broken or duplicated scripts.
"""
import sys
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parents[1]

BAD_TOKENS = ["pauseecho", "echo.REM", "echo.REM", "echo.REM"]

def inspect_file(p: Path):
    issues = []
    try:
        text = p.read_text(encoding='utf-8', errors='ignore')
    except Exception as e:
        issues.append(f"Could not read: {e}")
        return issues

    lines = [l.rstrip('\n') for l in text.splitlines()]
    # Detect suspicious token usage
    for i, l in enumerate(lines, start=1):
        for token in BAD_TOKENS:
            if token in l:
                issues.append(f"Line {i}: contains bad token '{token}': {l.strip()}")

    # Detect repeated lines (exact duplicates) - flag if a line appears multiple times and is fairly long
    counter = Counter([l.strip() for l in lines if len(l.strip()) > 20])
    for ln, ct in counter.items():
        if ct > 1:
            issues.append(f"Repeated line ({ct} times): {ln[:80]}{('...' if len(ln) > 80 else '')}")

    # Detect extremely long single-line commands which may indicate corruption
    for i, l in enumerate(lines, start=1):
        if len(l) > 400:
            issues.append(f"Line {i}: very long line ({len(l)} characters) - may be corruption")

    return issues

def main():
    bat_files = list(ROOT.glob('**/*.bat'))
    overall_issues = {}
    for p in bat_files:
        # Skip node_modules or virtual envs (if present)
        if any(part in ("venv", ".venv", "node_modules") for part in p.parts):
            continue
        issues = inspect_file(p)
        if issues:
            overall_issues[str(p.relative_to(ROOT))] = issues

    if overall_issues:
        print('Found issues in .bat files:')
        for file, issues in overall_issues.items():
            print(f"\n-- {file} --")
            for i in issues:
                print(f"  - {i}")
        return 1
    print('No major issues detected in .bat files.')
    return 0

if __name__ == '__main__':
    sys.exit(main())
