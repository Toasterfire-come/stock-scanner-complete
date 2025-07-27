@echo off
echo ========================================
echo Stock Scanner Background Scheduler
echo ========================================
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

REM Set environment variables for background operation
set DJANGO_SETTINGS_MODULE=stockscanner_django.settings
set PYTHONIOENCODING=utf-8

echo [INFO] Starting Stock Scanner in background mode...
echo [INFO] The scheduler will run silently in the background
echo [INFO] Check stock_scheduler.log for status updates
echo.

REM Check if the script exists and run in background
if not exist "start_stock_scheduler_windows.py" (
    if exist "start_stock_scheduler.py" (
        echo [RUN] Using start_stock_scheduler.py (background mode)...
        start /B python start_stock_scheduler.py --background
    ) else (
        echo [ERROR] Scheduler script not found
        echo Please ensure you are in the correct directory
        pause
        exit /b 1
    )
) else (
    echo [RUN] Using Windows-optimized scheduler (background mode)...
    start /B python start_stock_scheduler_windows.py --background
)

echo.
echo [SUCCESS] Stock Scanner started in background
echo [INFO] Process is running silently - check logs for status
echo [INFO] Log file: stock_scheduler.log
echo [INFO] To stop: Use Task Manager to end Python processes
echo.
echo Press any key to close this window...
pause > nul