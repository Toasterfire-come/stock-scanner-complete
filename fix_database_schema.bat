@echo off
echo ========================================
echo Database Schema Fix Tool
echo ========================================
echo.
echo This will fix missing tables and columns:
echo - Reset Django migrations
echo - Create fresh database schema
echo - Add sample data for testing
echo - Verify API endpoints work
echo.

REM Set UTF-8 encoding
chcp 65001 > nul 2>&1

REM Check for Python
python --version > nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found in PATH
    pause
    exit /b 1
)

echo Starting database schema fix...
echo This may take a few minutes...
echo.

REM Set environment variables
set DJANGO_SETTINGS_MODULE=stockscanner_django.settings
set PYTHONIOENCODING=utf-8

REM Run the schema fix tool
python fix_database_schema.py

echo.
echo Schema fix completed!
echo.

REM Test if we can import Django models now
echo Testing Django models...
python -c "import os; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stockscanner_django.settings'); import django; django.setup(); from stocks.models import Stock; print(f'SUCCESS: Found {Stock.objects.count()} stocks in database')" 2>nul

if errorlevel 1 (
    echo WARNING: Django models may still have issues
    echo Try running these commands manually:
    echo   python manage.py makemigrations
    echo   python manage.py migrate
) else (
    echo SUCCESS: Database schema is now working
    echo.
    echo You can now:
    echo   python manage.py runserver
    echo   python start_stock_scheduler.py --background
    echo   Visit: http://127.0.0.1:8000/api/wordpress/
)

echo.
echo Press any key to close...
pause > nul