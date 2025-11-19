@echo off
REM scripts/run_app_with_venv.bat - Ensure a virtual environment is used, activate it, and run the Streamlit app
REM Usage: scripts\run_app_with_venv.bat [--skip-install] [dev] [migrate]

cd /d "%~dp0"

call "scripts\venv_helpers.bat"

set SKIP_INSTALL=0
set DEV_MODE=0
set MIGRATE=0
set ARGS=%*
for %%A in (%ARGS%) do (
    if /I "%%A"=="--skip-install" set SKIP_INSTALL=1
    if /I "%%A"=="dev" set DEV_MODE=1
    if /I "%%A"=="migrate" set MIGRATE=1
)

IF DEFINED VENV_ACTIVATION (
    rem Activate venv
    call "%VENV_ACTIVATION%"
)

IF "%SKIP_INSTALL%"=="0" (
    rem Install base requirements in venv
    if DEFINED VENV_PY (
        "%VENV_PY%" -m pip install -r requirements.txt || (
            echo [WARNING] Failed to install runtime requirements into the venv.
        )
    ) else (
        pip install -r requirements.txt
    )
)

IF "%DEV_MODE%"=="1" (
    echo [INFO] Dev mode: installing dev dependencies...
    if DEFINED VENV_PY (
        "%VENV_PY%" -m pip install -r requirements-dev.txt || (
            echo [WARNING] Failed to install dev requirements into the venv.
        )
    ) else (
        pip install -r requirements-dev.txt
    )
)

IF "%MIGRATE%"=="1" (
    REM Choose invocation method from venv if available
    set "_PY_CMD=python"
    if defined VENV_PY set "_PY_CMD=%VENV_PY%"
    "%_PY_CMD%" scripts\migrate_repo_secrets_to_dotstreamlit.py --force || (
        echo [WARNING] Migration script failed or not available; check scripts/migrate_repo_secrets_to_dotstreamlit.py
    )
    set "_PY_CMD="
)

rem Start Streamlit
if DEFINED VENV_PY (
    "%VENV_PY%" -m streamlit run main.py
) else (
    streamlit run main.py
)

exit /B %ERRORLEVEL%
