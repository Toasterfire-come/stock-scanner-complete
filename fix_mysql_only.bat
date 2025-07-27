@echo off
echo ========================================
echo MySQL Specific Fix Tool
echo ========================================
echo.
echo This tool will:
echo - Check and start MySQL service
echo - Optimize Django MySQL settings
echo - Add comprehensive error handling
echo - Test MySQL connection thoroughly
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

echo [INFO] Starting MySQL-specific fixes...
echo.

REM Run the MySQL fix tool
python fix_mysql_specifically.py

echo.
echo [INFO] MySQL fix completed
echo.

REM Test if Django can connect to MySQL now
echo [TEST] Testing Django MySQL connection...
python -c "import os; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stockscanner_django.settings'); import django; django.setup(); from django.db import connection; cursor = connection.cursor(); cursor.execute('SELECT 1'); print('[SUCCESS] MySQL connection working!')" 2>nul

if errorlevel 1 (
    echo [WARNING] MySQL connection may still have issues
    echo Check MySQL service status and credentials
    echo.
    echo Try these commands:
    echo   net start mysql
    echo   python manage.py check
) else (
    echo [SUCCESS] MySQL is ready for stock scanner
    echo.
    echo You can now run:
    echo   start_scheduler_background.bat
    echo   python start_stock_scheduler.py --background
)

echo.
echo Press any key to close...
pause > nul