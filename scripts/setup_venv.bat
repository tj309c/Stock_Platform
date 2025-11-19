@echo off
REM scripts/setup_venv.bat - Create .venv and install runtime and dev requirements

cd %~dp0\..
if not exist .venv (
    python -m venv .venv
)
call .venv\Scripts\activate
python -m pip install --upgrade pip wheel

if exist requirements.txt (
    pip install -r requirements.txt
)
if exist requirements-dev.txt (
    pip install -r requirements-dev.txt
)

REM Install Playwright browsers if Playwright is installed
python -m playwright install