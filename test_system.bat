@echo off
title Stock Scanner - System Test
echo 🧪 Stock Scanner System Test for Windows
echo =========================================

REM Activate virtual environment
if exist "venv\Scripts\activate.bat" (
    echo 🔧 Activating virtual environment...
    call venv\Scripts\activate.bat
    echo ✅ Virtual environment activated
) else (
    echo ❌ Virtual environment not found!
    echo 💡 Please run setup.bat first
    pause
    exit /b 1
)

echo.
echo 🧪 Running comprehensive system test...
echo.

REM Test 1: Python environment
echo 🔍 Test 1: Python Environment
echo ------------------------------
python --version
if errorlevel 1 (
    echo ❌ Python test failed
    set test_failed=1
) else (
    echo ✅ Python test passed
)

echo.
echo 🔍 Test 2: Virtual Environment
echo ------------------------------
if defined VIRTUAL_ENV (
    echo ✅ Virtual environment active: %VIRTUAL_ENV%
) else (
    echo ❌ Virtual environment not detected
    set test_failed=1
)

echo.
echo 🔍 Test 3: Dependencies Check
echo ------------------------------
pip list | findstr "Django"
if errorlevel 1 (
    echo ❌ Django not installed
    set test_failed=1
) else (
    echo ✅ Django found
)

pip list | findstr "requests"
if errorlevel 1 (
    echo ❌ Requests not installed
    set test_failed=1
) else (
    echo ✅ Requests found
)

pip list | findstr "yfinance"
if errorlevel 1 (
    echo ❌ yfinance not installed
    set test_failed=1
) else (
    echo ✅ yfinance found
)

echo.
echo 🔍 Test 4: Project Structure
echo ----------------------------
if exist "manage.py" (
    echo ✅ manage.py found
) else (
    echo ❌ manage.py missing
    set test_failed=1
)

if exist "stocks" (
    echo ✅ stocks app found
) else (
    echo ❌ stocks app missing
    set test_failed=1
)

if exist "stockscanner_django" (
    echo ✅ Django project found
) else (
    echo ❌ Django project missing
    set test_failed=1
)

if exist ".env" (
    echo ✅ .env file found
) else (
    echo ❌ .env file missing
    set test_failed=1
)

echo.
echo 🔍 Test 5: Django Configuration
echo -------------------------------
python test_django_startup.py
if errorlevel 1 (
    echo ❌ Django test failed
    set test_failed=1
) else (
    echo ✅ Django test passed
)

echo.
echo 🔍 Test 6: Database Connection
echo ------------------------------
python manage.py check --database default
if errorlevel 1 (
    echo ❌ Database connection failed
    set test_failed=1
) else (
    echo ✅ Database connection successful
)

echo.
echo 🔍 Test 7: Migration Status
echo ---------------------------
python manage.py showmigrations
if errorlevel 1 (
    echo ❌ Migration check failed
    set test_failed=1
) else (
    echo ✅ Migration check passed
)

echo.
echo 🔍 Test 8: Static Files
echo -----------------------
python manage.py findstatic admin/css/base.css >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Static files may need collection
    echo 💡 Run: python manage.py collectstatic
) else (
    echo ✅ Static files accessible
)

echo.
echo 🔍 Test 9: Import Tests
echo ----------------------
python -c "import django; print('Django version:', django.get_version())"
if errorlevel 1 (
    echo ❌ Django import failed
    set test_failed=1
) else (
    echo ✅ Django import successful
)

python -c "import yfinance; print('yfinance imported successfully')"
if errorlevel 1 (
    echo ❌ yfinance import failed
    set test_failed=1
) else (
    echo ✅ yfinance import successful
)

echo.
echo 🔍 Test 10: Comprehensive Bug Check
echo ------------------------------------
python windows_complete_setup.py --test-only
if errorlevel 1 (
    echo ❌ Comprehensive bug check found issues
    set test_failed=1
) else (
    echo ✅ Comprehensive bug check passed
)

echo.
echo =========================================
echo 📊 SYSTEM TEST RESULTS
echo =========================================

if defined test_failed (
    echo ❌ SOME TESTS FAILED
    echo.
    echo 🔧 Recommended actions:
    echo    1. Run setup.bat to fix installation issues
    echo    2. Run setup_database.bat to fix database issues
    echo    3. Check the logs/ directory for detailed error information
    echo    4. See WINDOWS_SETUP_GUIDE.md for troubleshooting
    echo.
    echo 💡 Common fixes:
    echo    - Reinstall requirements: pip install -r requirements.txt
    echo    - Reset database: python manage.py migrate --run-syncdb
    echo    - Recreate virtual environment: rmdir /s venv && python -m venv venv
) else (
    echo ✅ ALL TESTS PASSED!
    echo.
    echo 🚀 Your Stock Scanner is fully functional!
    echo 🌐 Ready to start: run start_app.bat
    echo 📖 Check README.md for usage instructions
)

echo.
echo 📋 System Information:
echo ----------------------
echo Date: %date%
echo Time: %time%
echo Computer: %computername%
echo User: %username%
echo Python Path: 
python -c "import sys; print(sys.executable)"

echo.
pause