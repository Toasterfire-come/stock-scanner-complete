@echo off
echo ========================================
echo Stock Scanner Scheduler Startup
echo ========================================
echo.

REM Set UTF-8 encoding for Windows
chcp 65001 > nul

REM Check if Python is available
python --version > nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ and add it to your PATH
    pause
    exit /b 1
)

REM Check if the script exists
if not exist "start_stock_scheduler_windows.py" (
    if exist "start_stock_scheduler.py" (
        echo Using start_stock_scheduler.py...
        python start_stock_scheduler.py
    ) else (
        echo ERROR: Scheduler script not found
        echo Please ensure you are in the correct directory
        pause
        exit /b 1
    )
) else (
    echo Using Windows-optimized scheduler...
    python start_stock_scheduler_windows.py
)

echo.
echo Scheduler has stopped.
pause