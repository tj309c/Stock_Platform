@echo off
REM venv_helpers.bat - Helper for venv detection, activation, and secrets check
REM Usage: call scripts\venv_helpers.bat [activate]

SETLOCAL
SET "SCRIPT_DIR=%~dp0"
REM Discover venv; prefer local `.venv`, then `venv`, otherwise system Python
IF EXIST "%SCRIPT_DIR%..\.venv\Scripts\python.exe" (
  SET "VENV_PY=%SCRIPT_DIR%..\.venv\Scripts\python.exe"
  SET "VENV_ACTIVATION=%SCRIPT_DIR%..\.venv\Scripts\activate.bat"
) ELSE (
  IF EXIST "%SCRIPT_DIR%..\venv\Scripts\python.exe" (
    SET "VENV_PY=%SCRIPT_DIR%..\venv\Scripts\python.exe"
    SET "VENV_ACTIVATION=%SCRIPT_DIR%..\venv\Scripts\activate.bat"
  ) ELSE (
    SET "VENV_PY=python"
    SET "VENV_ACTIVATION="
  )
)

REM Export variables for calling script
SET "VENV_PY=%VENV_PY%"
SET "VENV_ACTIVATION=%VENV_ACTIVATION%"

REM Optionally activate venv
IF /I "%~1"=="activate" (
  IF DEFINED VENV_ACTIVATION ( 
    call "%VENV_ACTIVATION%"
  ) ELSE (
    echo No local venv activation script found; continuing with system Python.
  )
)

REM Check for secrets file and warn if missing (non-destructive)
IF NOT EXIST "%CD%\.streamlit\secrets.toml" (
  echo [WARNING] .streamlit\secrets.toml not found. Authenticated endpoints will be disabled.
)

ENDLOCAL &SET "VENV_PY=%VENV_PY%" & SET "VENV_ACTIVATION=%VENV_ACTIVATION%"
