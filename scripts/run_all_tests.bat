@echo off
REM Run all tests (unit + e2e) using the project's venv (Windows CMD)
IF NOT EXIST "%CD%\.venv\Scripts\python.exe" (
  echo Virtual environment not found at %CD%\.venv. Please create or point to your venv.
  exit /b 1
)
REM Run unit tests first
%CD%\.venv\Scripts\python.exe -m pytest tests/unit -q
IF %ERRORLEVEL% NEQ 0 (
  echo Unit tests failed; aborting.
  exit /b %ERRORLEVEL%
)
REM Run e2e tests (if playwright installed) - optionally install playwright browsers first.
%CD%\.venv\Scripts\python.exe -m pip install playwright pytest-playwright
%CD%\.venv\Scripts\python.exe -m playwright install
%CD%\.venv\Scripts\python.exe -m pytest tests/e2e -q
exit /b %ERRORLEVEL%
