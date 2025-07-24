@echo off
setlocal enabledelayedexpansion

REM =========================================================================
REM Load NASDAQ-Only Tickers - Stock Scanner
REM Loads ONLY NASDAQ-listed securities (excludes NYSE, ARCA, BATS, etc.)
REM =========================================================================

echo.
echo ================================================================================
echo ^|                        LOAD NASDAQ-ONLY TICKERS                           ^|
echo ^|                         Stock Scanner v4.0                                ^|
echo ================================================================================
echo.
echo 🏛️  This script will load ONLY NASDAQ-listed securities into your database
echo 📊 NASDAQ Exchange ONLY (excludes NYSE, ARCA, BATS, OTC, etc.)
echo 📈 Pure NASDAQ ticker list for focused trading
echo.
echo ✅ INCLUDES:  NASDAQ-listed securities ONLY
echo ❌ EXCLUDES:  NYSE, ARCA, BATS, OTC, Pink Sheets, etc.
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
    echo ❌ Django not found. Please run WINDOWS_SETUP_FIX.bat first.
    pause
    exit /b 1
)

REM Check if NASDAQ-only ticker file exists
echo 🔧 Checking for NASDAQ-only ticker file...
if not exist "data\nasdaq_only\nasdaq_only_tickers_*.py" (
    echo ❌ NASDAQ-only ticker file not found!
    echo 💡 Please run the downloader first:
    echo    python tools/nasdaq_only_downloader.py
    echo.
    set /p download_now="Would you like to download the NASDAQ-only ticker list now? (y/n): "
    if /i "!download_now!"=="y" (
        echo 🔧 Downloading NASDAQ-only ticker list...
        python tools/nasdaq_only_downloader.py
        if errorlevel 1 (
            echo ❌ Download failed. Please check your internet connection.
            pause
            exit /b 1
        )
    ) else (
        echo ❌ Cannot proceed without NASDAQ-only ticker file.
        pause
        exit /b 1
    )
)

echo.
echo 📋 Choose NASDAQ loading option:
echo    1. Load ALL NASDAQ tickers (RECOMMENDED)
echo    2. Dry run - See what would be loaded without changes
echo    3. Update existing NASDAQ tickers only
echo    4. Show current database statistics
echo.

set /p choice="Enter your choice (1-4): "

REM Set command based on choice
set django_cmd=python manage.py load_nasdaq_only

if "%choice%"=="1" (
    echo 🏛️  Loading ALL NASDAQ tickers...
    echo 📊 This will add ONLY NASDAQ-listed securities
    set django_cmd=!django_cmd! --update-existing --batch-size 100
) else if "%choice%"=="2" (
    echo 🔍 Dry run mode...
    set django_cmd=!django_cmd! --dry-run
) else if "%choice%"=="3" (
    echo 🔄 Updating existing NASDAQ tickers only...
    set django_cmd=!django_cmd! --update-existing
) else if "%choice%"=="4" (
    echo 📊 Showing current database statistics...
    echo.
    python manage.py shell -c "
from stocks.models import Stock
from django.db.models import Count

total = Stock.objects.count()
nasdaq = Stock.objects.filter(exchange='NASDAQ').count()
active_nasdaq = Stock.objects.filter(exchange='NASDAQ', is_active=True).count()

print(f'📈 Total stocks in database: {total:,}')
print(f'🏛️  NASDAQ stocks: {nasdaq:,}')
print(f'✅ Active NASDAQ stocks: {active_nasdaq:,}')
print()

exchanges = Stock.objects.values('exchange').annotate(count=Count('exchange')).order_by('-count')
print('📊 Exchange Breakdown:')
for ex in exchanges:
    exchange_name = ex['exchange'] or 'Unknown'
    is_nasdaq = '🏛️' if exchange_name == 'NASDAQ' else '  '
    print(f'   {is_nasdaq} {exchange_name}: {ex[\"count\"]:,} stocks')
"
    echo.
    echo Press any key to continue...
    pause >nul
    exit /b 0
) else (
    echo ❌ Invalid choice. Using default (load all NASDAQ).
    set django_cmd=!django_cmd! --update-existing --batch-size 100
)

echo.
echo 🚀 Executing: !django_cmd!
echo.
echo ⏱️  Loading started at: %time%
echo 📊 Progress will be shown during loading...
echo.

REM Record start time
set start_time=%time%

REM Run the Django command
!django_cmd!

if errorlevel 1 (
    echo.
    echo ❌ Error occurred during NASDAQ ticker loading.
    echo 💡 Check the error message above and try again.
    echo 🔧 Common solutions:
    echo    - Run: python manage.py migrate
    echo    - Check database connection
    echo    - Ensure NASDAQ ticker file exists
    echo    - Try: python tools/nasdaq_only_downloader.py
) else (
    echo.
    echo ⏱️  Loading completed at: %time%
    echo ✅ NASDAQ-only ticker loading finished successfully!
    echo.
    echo 🏛️  Database now contains NASDAQ securities ONLY
    echo 📈 Ready for NASDAQ-focused stock scanning!
    echo.
    echo 🚀 Next steps:
    echo    1. Verify: python manage.py shell -c "from stocks.models import Stock; print(f'NASDAQ stocks: {Stock.objects.filter(exchange=\"NASDAQ\").count():,}')"
    echo    2. Fetch NASDAQ price data: python manage.py update_stocks_yfinance --exchange NASDAQ
    echo    3. Start NASDAQ scanner: START_HERE.bat
    echo    4. Test web interface: python manage.py runserver
    echo.
    echo 💡 NASDAQ-only advantages:
    echo    - Faster data processing
    echo    - Focus on growth stocks
    echo    - Technology sector emphasis
    echo    - Clean, focused ticker list
    echo    - No penny stocks or OTC issues
)

echo.
echo 🏛️  NASDAQ-ONLY INTEGRATION SUMMARY:
echo    📊 Exchange: NASDAQ ONLY
echo    ❌ Excluded: NYSE, ARCA, BATS, OTC, Pink Sheets
echo    🎯 Focus: Technology, Growth, and Innovation stocks
echo    ⚡ Performance: Optimized for NASDAQ securities
echo    🛡️  Quality: Clean, validated ticker list
echo.

echo Press any key to continue...
pause >nul