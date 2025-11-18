"""
Delete files with reserved Windows device names that cause Git to fail in staging.
This script attempts to delete such files from the repository root and subdirectories.
It uses the '\\?\' prefix to bypass path handling and force removal.
"""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
reserved_names = {'nul', 'con', 'prn', 'aux', 'com1', 'com2', 'lpt1', 'lpt2'}

def try_remove(p: Path):
    p_abs = str(p.resolve())
    try:
        # try normal remove first
        if p.exists():
            p.unlink()
            print('Deleted (normal):', p)
            return True
    except Exception as e:
        print('Normal unlink failed for', p, '->', e)
    # Try extended path (Windows)
    try:
        extended = r"\\?\\" + p_abs
        os.remove(extended)
        print('Deleted via extended path:', p)
        return True
    except Exception as e:
        print('Extended path remove failed for', p, '->', e)
        return False

if __name__ == '__main__':
    print('Checking for reserved device file names to remove')
    for p in ROOT.rglob('*'):
        if not p.is_file():
            continue
        if p.name.lower() in reserved_names:
            print('Found reserved file name:', p)
            try_remove(p)
    print('Done')
