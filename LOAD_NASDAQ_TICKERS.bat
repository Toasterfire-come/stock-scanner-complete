@echo off
setlocal enabledelayedexpansion

REM =========================================================================
REM Load NASDAQ Tickers - Stock Scanner
REM Loads the comprehensive NASDAQ ticker list into the database
REM =========================================================================

echo.
echo ================================================================================
echo ^|                         LOAD NASDAQ TICKERS                                ^|
echo ^|                         Stock Scanner v2.0                                 ^|
echo ================================================================================
echo.
echo 🎯 This script will load the comprehensive NASDAQ ticker list into your database
echo 📊 Total tickers available: 457 (NASDAQ, NYSE, ETFs, Crypto, etc.)
echo.

REM Check if virtual environment exists
if exist "venv\Scripts\activate.bat" (
    echo ✅ Virtual environment found
    call venv\Scripts\activate.bat
) else (
    echo ⚠️  Virtual environment not found, using system Python
)

REM Check if Django is available
echo 🔧 Checking Django installation...
python -c "import django; print(f'Django {django.VERSION} detected')" 2>nul
if errorlevel 1 (
    echo ❌ Django not found. Please run SIMPLE_START.bat first.
    pause
    exit /b 1
)

echo.
echo 📋 Choose loading option:
echo    1. Load ALL tickers (457 total) - Recommended
echo    2. Load NASDAQ 100 only (100 most important stocks)
echo    3. Load Technology sector only (50 tech stocks)
echo    4. Load ETFs only (50 popular ETFs)
echo    5. Load Crypto/Fintech only (30 crypto-related stocks)
echo    6. Dry run - See what would be loaded without changes
echo    7. Custom sector
echo.

set /p choice="Enter your choice (1-7): "

REM Set command based on choice
set django_cmd=python manage.py load_nasdaq_tickers

if "%choice%"=="1" (
    echo 🎯 Loading ALL tickers...
    set django_cmd=!django_cmd! --update-existing
) else if "%choice%"=="2" (
    echo 🎯 Loading NASDAQ 100 tickers...
    set django_cmd=!django_cmd! --sector nasdaq100 --update-existing
) else if "%choice%"=="3" (
    echo 🎯 Loading Technology sector...
    set django_cmd=!django_cmd! --sector technology --update-existing
) else if "%choice%"=="4" (
    echo 🎯 Loading ETFs...
    set django_cmd=!django_cmd! --sector etfs --update-existing
) else if "%choice%"=="5" (
    echo 🎯 Loading Crypto/Fintech...
    set django_cmd=!django_cmd! --sector crypto --update-existing
) else if "%choice%"=="6" (
    echo 🔍 Dry run mode...
    set django_cmd=!django_cmd! --dry-run
) else if "%choice%"=="7" (
    echo.
    echo Available sectors:
    echo   nasdaq100, nyse, technology, etfs, crypto, meme, ev, healthcare, finance, energy, reits, consumer
    set /p sector="Enter sector name: "
    set django_cmd=!django_cmd! --sector !sector! --update-existing
) else (
    echo ❌ Invalid choice. Using default (load all).
    set django_cmd=!django_cmd! --update-existing
)

echo.
echo 🚀 Executing: !django_cmd!
echo.

REM Run the Django command
!django_cmd!

if errorlevel 1 (
    echo.
    echo ❌ Error occurred during ticker loading.
    echo 💡 Check the error message above and try again.
) else (
    echo.
    echo ✅ Ticker loading completed successfully!
    echo.
    echo 📊 Database updated with NASDAQ tickers
    echo 🎯 Ready to scan stocks!
    echo.
    echo 🚀 Next steps:
    echo    1. Run START_HERE.bat to start the Stock Scanner
    echo    2. Or run: python manage.py update_stocks_yfinance
    echo    3. Or test: python manage.py shell -c "from stocks.models import Stock; print(f'Total stocks: {Stock.objects.count()}')"
)

echo.
echo Press any key to continue...
pause >nul