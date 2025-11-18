"""
export_project_state.py

Creates a zip backup of the current project workspace, excluding large and environment-only folders
like `.venv`, `.git`, and `data/backups` itself. The generated file is placed in `data/backups/` with
the timestamp embedded in the filename for easy retrieval.

Usage: Run from project root using the project's venv: `python scripts/export_project_state.py`
"""
from __future__ import annotations

import zipfile
import os
from pathlib import Path
from datetime import datetime


EXCLUDE_DIRS = {'.venv', '.git', 'data/backups', 'node_modules', '__pycache__'}


def should_exclude(path: Path) -> bool:
    parts = {p for p in path.parts}
    for exclude in EXCLUDE_DIRS:
        if exclude in parts:
            return True
    return False


def make_backup(dest_dir: Path, base_dir: Path) -> Path:
    dest_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
    zip_name = f"analysis_master_backup_{timestamp}.zip"
    zip_path = dest_dir / zip_name

    print(f"Creating backup: {zip_path}")
    with zipfile.ZipFile(zip_path, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(base_dir):
            root_p = Path(root)
            # Skip excluded directories entirely
            if should_exclude(root_p):
                # Prevent walking into them
                dirs[:] = []
                continue
            for f in files:
                fp = root_p / f
                # Skip hidden files and exclude files in backup directory
                if should_exclude(fp):
                    continue
                # Store files relative to base_dir
                arcname = fp.relative_to(base_dir)
                try:
                    zf.write(fp, arcname)
                except ValueError:
                    # Some files may have timestamps before 1980 which Zip does not support.
                    # In that case, explicitly write the bytes and set a sane timestamp to avoid errors.
                    try:
                        data = fp.read_bytes()
                        zi = zipfile.ZipInfo(str(arcname))
                        zi.date_time = datetime.utcnow().timetuple()[:6]
                        zi.compress_type = zipfile.ZIP_DEFLATED
                        zf.writestr(zi, data)
                    except Exception:
                        print(f"Skipped file due to write error: {fp}")
    return zip_path


def main():
    base = Path(__file__).parent.parent
    dest = base / 'data' / 'backups'
    z = make_backup(dest, base)
    print('Done. Backup saved at:', z)


if __name__ == '__main__':
    main()
