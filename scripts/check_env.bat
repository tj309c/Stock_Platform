@echo off
REM Run a set of environment checks (Python packages and connectivity)
SETLOCAL
REM Try to use project venv if it exists
SET "VENV_PY=%~dp0..\.venv\Scripts\python.exe"
IF NOT EXIST "%VENV_PY%" (
    SET "VENV_PY=%~dp0..\venv\Scripts\python.exe"
)
IF NOT EXIST "%VENV_PY%" (
    SET "VENV_PY=python"
)

echo Using Python: %VENV_PY%
%VENV_PY% -c "import sys, os; print('Python:', sys.version); import numpy, pandas; print('numpy', numpy.__version__); print('pandas', pandas.__version__)"
IF %ERRORLEVEL% NEQ 0 (
    echo One or more package imports failed. Try reinstalling numpy/pandas:
    echo %VENV_PY% -m pip install --upgrade --force-reinstall --no-cache-dir numpy pandas
    exit /B 1
)
echo All basic checks passed.
IF EXIST "%~dp0..\venv\Scripts\activate.bat" (
    echo venv detected under 'venv'
) ELSE IF EXIST "%~dp0..\.venv\Scripts\activate.bat" (
    echo venv detected under '.venv'
) ELSE (
    echo No local venv detected; ensure you run from a Python venv for best results
)
ENDLOCAL
exit /B 0
