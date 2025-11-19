Export Project State (Backups)
--------------------------------

This folder contains a small utility to create a ZIP backup of the project workspace.

Usage (Windows):
1. Activate the project's venv, or rely on system Python if venv isn't present.
2. Run the Python script:

```
%CD%\.venv\Scripts\python.exe scripts\export_project_state.py
```

Alternatively use the included batch wrapper:

```
scripts\export_project_state.bat
```

Output:
- The generated zip is written to `data/backups` with filename `analysis_master_backup_<timestamp>.zip`.
- The script excludes the following directories: `.venv`, `.git`, and `data/backups` itself to avoid recursion.

Notes:
- The script will skip files that cannot be written due to metadata issues and safely continue.
- You can edit the `EXCLUDE_DIRS` constant inside the script to add more folders to ignore.
