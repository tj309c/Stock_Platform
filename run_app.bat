@echo off
REM Analysis Master - Startup Script
REM This script ensures the app runs from the virtual environment

cd /d "%~dp0"

echo.
echo =========================================
echo    🔥 Analysis Master - Starting App 🔥
echo =========================================
echo.

REM Check if venv exists
SET "VENV_ACTIVATION_SCRIPT=venv\Scripts\activate.bat"
IF NOT EXIST "%VENV_ACTIVATION_SCRIPT%" (
    SET "VENV_ACTIVATION_SCRIPT=.venv\Scripts\activate.bat"
)

if not exist "%VENV_ACTIVATION_SCRIPT%" (
    echo [ERROR] Virtual environment activation script not found!
    echo.
    echo Please ensure Python 3.12 or newer is installed, then run these commands:
    echo   1. py -3.12 -m venv venv
    echo   2. venv\Scripts\pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)

REM Activate the virtual environment and run Streamlit
echo [INFO] Activating virtual environment...
call "%VENV_ACTIVATION_SCRIPT%"

echo [INFO] Installing/updating requirements...
pip install -r requirements.txt
echo.

echo [INFO] Starting Streamlit from virtual environment...
echo [INFO] App will open at: http://localhost:8501
echo [INFO] Network URL will be displayed below
echo.
echo =========================================
echo Press Ctrl+C to stop the server
echo =========================================
echo.

streamlit run main.py

echo.
echo [INFO] Server stopped.
pause
