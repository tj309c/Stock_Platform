@echo off
REM Wrapper to call the Python export script using the venv Python if present
set ROOT=%~dp0..
set PYTHON=%ROOT%\.venv\Scripts\python.exe
if exist "%PYTHON%" (
    "%PYTHON%" "%ROOT%\scripts\export_project_state.py"
) else (
    python "%ROOT%\scripts\export_project_state.py"
)

pause
