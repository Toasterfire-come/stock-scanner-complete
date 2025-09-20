@echo off
REM Market Hours Manager Startup Script - Windows Version
REM Starts the automated market hours manager for stock scanner components

setlocal enabledelayedexpansion

echo.
echo ============================================================
echo  Stock Scanner - Market Hours Manager
echo ============================================================
echo.

REM Check if Python is available
echo [STEP] Checking Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python and add it to your PATH
    pause
    exit /b 1
)

echo [SUCCESS] Python found

REM Check if market_hours_manager.py exists
if not exist "market_hours_manager.py" (
    echo [ERROR] market_hours_manager.py not found in current directory
    pause
    exit /b 1
)

REM Check if required packages are installed
echo [STEP] Checking required packages
python -c "import pytz, psutil, schedule" 2>nul
if errorlevel 1 (
    echo [WARNING] Some required packages may be missing
    echo [STEP] Installing required packages
    
    pip install pytz psutil schedule
    if errorlevel 1 (
        echo [ERROR] Failed to install required packages
        echo Please install manually: pip install pytz psutil schedule
        pause
        exit /b 1
    )
    
    echo [SUCCESS] Required packages installed
)

REM Check if manage.py exists (Django project)
if not exist "manage.py" (
    echo [ERROR] manage.py not found. Make sure you're in the Django project root directory
    pause
    exit /b 1
)

REM Check if restart-enabled scripts exist
if not exist "enhanced_stock_retrieval_working.py" (
    echo [WARNING] enhanced_stock_retrieval_working.py not found
    echo [WARNING] Stock retrieval component will not work
)

if not exist "news_scraper_with_restart.py" (
    echo [WARNING] news_scraper_with_restart.py not found
    echo [WARNING] News scraper component will not work
)

if not exist "email_sender_with_restart.py" (
    echo [WARNING] email_sender_with_restart.py not found
    echo [WARNING] Email sender component will not work
)

echo [SUCCESS] Environment checks passed
echo.

echo [STEP] Starting Market Hours Manager
echo [WARNING] Press Ctrl+C to stop the manager gracefully
echo [WARNING] Logs will be written to market_hours_manager.log
echo.

echo Market Hours Schedule:
echo   Premarket:    4:00 AM - 9:30 AM ET (retrieval, news, emails)
echo   Market:       9:30 AM - 4:00 PM ET (all components + server)
echo   Postmarket:   4:00 PM - 8:00 PM ET (retrieval, news, emails)
echo   After Hours:  8:00 PM - 4:00 AM ET (all components stopped)
echo.

REM Start the market hours manager
python market_hours_manager.py

pause