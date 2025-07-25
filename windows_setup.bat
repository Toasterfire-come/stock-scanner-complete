@echo off
REM Windows Setup Script for Stock Scanner
REM This script will automatically set up the Stock Scanner application on Windows

echo ============================================================
echo  Stock Scanner - Windows Setup
echo ============================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python from https://python.org
    pause
    exit /b 1
)

echo [SUCCESS] Python is installed
echo.

REM Check if pip is available
pip --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] pip is not available
    echo Please ensure pip is installed with Python
    pause
    exit /b 1
)

echo [SUCCESS] pip is available
echo.

REM Install basic requirements
echo [STEP] Installing basic Python packages...
pip install PyMySQL python-dotenv dj-database-url Django==4.2.11

REM Run the main setup script
echo [STEP] Running main setup script...
python windows_mysql_setup.py

if errorlevel 1 (
    echo [ERROR] Setup script failed
    pause
    exit /b 1
)

echo.
echo ============================================================
echo  Setup completed successfully!
echo ============================================================
echo.
echo To start the application:
echo   python manage.py runserver
echo.
echo Then open your browser to: http://localhost:8000
echo.
pause