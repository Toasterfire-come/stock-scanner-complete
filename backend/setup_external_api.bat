@echo off
echo Django API External Access Setup
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python and try again
    pause
    exit /b 1
)

REM Check if Django project exists
if not exist "manage.py" (
    echo ERROR: manage.py not found. Please run this script from the Django project root.
    pause
    exit /b 1
)

REM Run the setup script
echo Running setup script...
python setup_external_api.py

echo.
echo Setup complete! Check the output above for next steps.
pause