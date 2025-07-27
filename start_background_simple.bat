@echo off
echo ========================================
echo Stock Scanner Background Mode
echo ========================================
echo.

REM Set UTF-8 encoding
chcp 65001 > nul 2>&1

REM Set environment variables
set DJANGO_SETTINGS_MODULE=stockscanner_django.settings
set PYTHONIOENCODING=utf-8

echo Starting Stock Scanner in background mode...
echo The process will run silently in the background.
echo Check stock_scheduler.log for status updates.
echo.

REM Check for Python
python --version > nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found in PATH
    pause
    exit /b 1
)

REM Start the background scheduler
if exist "start_stock_scheduler_windows.py" (
    echo Using Windows-optimized scheduler...
    start /B python start_stock_scheduler_windows.py --background
) else (
    if exist "start_stock_scheduler.py" (
        echo Using standard scheduler...
        start /B python start_stock_scheduler.py --background
    ) else (
        echo ERROR: No scheduler script found
        pause
        exit /b 1
    )
)

echo.
echo SUCCESS: Stock Scanner started in background
echo Process is running silently - check logs for status
echo To stop: Use Task Manager to end Python processes
echo.
pause