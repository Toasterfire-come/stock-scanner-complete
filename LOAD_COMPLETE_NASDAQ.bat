@echo off
setlocal enabledelayedexpansion

REM =========================================================================
REM Load Complete NASDAQ Tickers - Stock Scanner
REM Loads the complete 11,658+ NASDAQ ticker list into the database
REM =========================================================================

echo.
echo ================================================================================
echo ^|                      LOAD COMPLETE NASDAQ TICKERS                         ^|
echo ^|                         Stock Scanner v3.0                                ^|
echo ================================================================================
echo.
echo 🎯 This script will load the COMPLETE NASDAQ ticker list into your database
echo 📊 Total tickers available: 11,658+ (ALL NASDAQ, NYSE, and major exchanges)
echo 📡 Sources: NASDAQ FTP, Alpha Vantage, Finviz
echo.
echo ⚠️  WARNING: This is a LARGE dataset that will take several minutes to load
echo    Make sure you have sufficient database space and time for the operation.
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

REM Check if complete ticker file exists
echo 🔧 Checking for complete ticker file...
if not exist "data\complete_nasdaq\complete_nasdaq_tickers_*.py" (
    echo ❌ Complete NASDAQ ticker file not found!
    echo 💡 Please run the downloader first:
    echo    python tools/complete_nasdaq_downloader.py
    echo.
    set /p download_now="Would you like to download the complete ticker list now? (y/n): "
    if /i "!download_now!"=="y" (
        echo 🔧 Downloading complete NASDAQ ticker list...
        python tools/complete_nasdaq_downloader.py
        if errorlevel 1 (
            echo ❌ Download failed. Please check your internet connection.
            pause
            exit /b 1
        )
    ) else (
        echo ❌ Cannot proceed without ticker file.
        pause
        exit /b 1
    )
)

echo.
echo 📋 Choose loading option:
echo    1. Load ALL 11,658+ tickers (RECOMMENDED for production)
echo    2. Load first 1,000 tickers (testing/development)
echo    3. Load first 5,000 tickers (partial deployment)
echo    4. Dry run - See what would be loaded without changes
echo    5. Update existing tickers only
echo    6. Custom limit
echo.

set /p choice="Enter your choice (1-6): "

REM Set command based on choice
set django_cmd=python manage.py load_complete_nasdaq

if "%choice%"=="1" (
    echo 🎯 Loading ALL 11,658+ tickers...
    echo ⏱️  This will take 10-15 minutes. Please be patient.
    set django_cmd=!django_cmd! --update-existing --batch-size 500
) else if "%choice%"=="2" (
    echo 🎯 Loading first 1,000 tickers for testing...
    set django_cmd=!django_cmd! --limit 1000 --update-existing --batch-size 200
) else if "%choice%"=="3" (
    echo 🎯 Loading first 5,000 tickers...
    set django_cmd=!django_cmd! --limit 5000 --update-existing --batch-size 500
) else if "%choice%"=="4" (
    echo 🔍 Dry run mode...
    set django_cmd=!django_cmd! --dry-run
) else if "%choice%"=="5" (
    echo 🔄 Updating existing tickers only...
    set django_cmd=!django_cmd! --update-existing
) else if "%choice%"=="6" (
    set /p custom_limit="Enter number of tickers to load: "
    echo 🎯 Loading first !custom_limit! tickers...
    set django_cmd=!django_cmd! --limit !custom_limit! --update-existing --batch-size 200
) else (
    echo ❌ Invalid choice. Using default (load all).
    set django_cmd=!django_cmd! --update-existing --batch-size 500
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
    echo ❌ Error occurred during ticker loading.
    echo 💡 Check the error message above and try again.
    echo 🔧 Common solutions:
    echo    - Run: python manage.py migrate
    echo    - Check database connection
    echo    - Ensure sufficient disk space
    echo    - Try with smaller batch size
) else (
    echo.
    echo ⏱️  Loading completed at: %time%
    echo ✅ Complete NASDAQ ticker loading finished successfully!
    echo.
    echo 📊 Database now contains the complete NASDAQ ticker list
    echo 🎯 Ready for comprehensive stock scanning!
    echo.
    echo 🚀 Next steps:
    echo    1. Verify: python manage.py shell -c "from stocks.models import Stock; print(f'Total stocks: {Stock.objects.count():,}')"
    echo    2. Fetch price data: python manage.py update_stocks_yfinance
    echo    3. Start Stock Scanner: START_HERE.bat
    echo    4. Test web interface: python manage.py runserver
    echo.
    echo 💡 Performance tips:
    echo    - Price data fetching will take longer with 11,658+ tickers
    echo    - Consider using filters in your stock scanner
    echo    - Use batch processing for large operations
    echo    - Monitor database performance and add indexes as needed
)

echo.
echo 📈 COMPLETE NASDAQ INTEGRATION STATISTICS:
echo    📊 Target tickers: 11,658+
echo    📡 Data sources: NASDAQ FTP, Alpha Vantage, Finviz
echo    🗄️  Database: MySQL production ready
echo    ⚡ Performance: Batch processing enabled
echo    🛡️  Validation: Duplicate removal and error handling
echo.

echo Press any key to continue...
pause >nul