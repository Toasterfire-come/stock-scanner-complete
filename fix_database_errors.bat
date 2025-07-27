@echo off
echo ========================================
echo Complete Database Error Fix Tool
echo ========================================
echo.
echo This tool will:
echo - Test MySQL connection
echo - Fix MySQL errors if possible
echo - Switch to SQLite if MySQL fails
echo - No MySQL server required with SQLite
echo.

REM Set UTF-8 encoding for Windows
chcp 65001 > nul

REM Check if Python is available
python --version > nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.8+ and add it to your PATH
    pause
    exit /b 1
)

echo [INFO] Starting database diagnosis and fix...
echo.

REM Run the database fix tool
python fix_database_completely.py

echo.
echo [INFO] Database fix completed
echo.

REM Test if scheduler can start now
echo [TEST] Testing if scheduler can start...
python -c "import django; import os; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stockscanner_django.settings'); django.setup(); print('[SUCCESS] Django can start properly')" 2>nul

if errorlevel 1 (
    echo [WARNING] Django may still have issues
    echo Try running: python manage.py check
) else (
    echo [SUCCESS] Database is ready for scheduler
    echo.
    echo You can now run:
    echo   start_scheduler_background.bat
    echo   python start_stock_scheduler.py --background
)

echo.
echo Press any key to close...
pause > nul