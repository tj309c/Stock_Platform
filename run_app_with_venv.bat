REM Load venv helper to detect existing venv paths
call "scripts\venv_helpers.bat"

REM If helper didn't find a venv, create one in .venv using the system python
IF NOT DEFINED VENV_PY (
    echo [INFO] No venv python detected by helper; attempting to create .venv using system python
    python -m venv .venv
    if %ERRORLEVEL% NEQ 0 (
        echo [ERROR] Failed to create .venv virtual environment. Check that Python is installed and in PATH.
        exit /B 1
    )
    REM Reload helpers to get paths for the new venv
    call "scripts\venv_helpers.bat" reload
)

REM Now try to activate venv if available
IF DEFINED VENV_ACTIVATION (
    echo [INFO] Activating detected virtual environment when available...
    call "%VENV_ACTIVATION%"
) ELSE (
    echo [WARNING] Could not find a virtual environment activation script; running with system Python.
)

REM Parse arguments: --skip-install (skip installing dependencies), dev (install dev deps), migrate (migrate secrets)
set SKIP_INSTALL=0
set DEV_MODE=0
set MIGRATE=0
set ARGS=%*
for %%A in (%ARGS%) do (
    if /I "%%A"=="--skip-install" set SKIP_INSTALL=1
    if /I "%%A"=="dev" set DEV_MODE=1
    if /I "%%A"=="migrate" set MIGRATE=1
)

IF "%SKIP_INSTALL%"=="0" (
    echo [INFO] Installing base requirements (requirements.txt) into venv...
    if DEFINED VENV_PY (
        "%VENV_PY%" -m pip install -r requirements.txt || (
            echo [WARNING] Failed to install requirements. Continuing, but the app may be missing dependencies.
        )
    ) else (
        pip install -r requirements.txt || (
            echo [WARNING] Failed to install requirements with system python.
        )
    )
    echo.
) ELSE (
    echo [INFO] --skip-install specified; not installing requirements.
)

IF "%DEV_MODE%"=="1" (
    echo [INFO] Installing dev requirements (requirements-dev.txt)...
    if DEFINED VENV_PY (
        "%VENV_PY%" -m pip install -r requirements-dev.txt || (
            echo [WARNING] Failed to install dev requirements.
        )
    ) else (
        pip install -r requirements-dev.txt || (
            echo [WARNING] Failed to install dev requirements with system python.
        )
    )
)

IF "%MIGRATE%"=="1" (
    echo [INFO] Running migration of repo-root secrets to .streamlit/secrets.toml (dry-run suppressed)
    python scripts\migrate_repo_secrets_to_dotstreamlit.py --force || (
        echo [WARNING] Migration script failed or not available; check scripts/migrate_repo_secrets_to_dotstreamlit.py
    )
    echo.
)

echo [INFO] Starting Streamlit (using %VENV_PY% if available)...
echo [INFO] App will open at: http://localhost:8501
echo.
echo =========================================  REM App header
echo Press Ctrl+C to stop the server
echo =========================================  REM End header
echo.

REM If venv python is present use it to run streamlit to ensure the venv is used; otherwise fallback to system
IF DEFINED VENV_PY (
    "%VENV_PY%" -m streamlit run main.py
) ELSE (
    streamlit run main.py
)

echo.
echo [INFO] Server stopped.
pause

