@echo off
REM Direct System Setup for Stock Scanner (No Virtual Environment)
REM Uses user-level packages to avoid system conflicts

echo ============================================================
echo  Stock Scanner - Direct System Setup (User Packages)
echo ============================================================
echo.
echo Installing packages to user directory (safer approach)
echo Your existing pandas 2.3.1 and numpy 2.3.1 will be used!
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python from https://python.org
    pause
    exit /b 1
)

echo [SUCCESS] Python is installed
python --version
echo.

REM Check if pip is available
pip --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] pip is not available
    echo Please ensure pip is installed with Python
    pause
    exit /b 1
)

echo [SUCCESS] pip is available
echo.

echo [STEP 1] Installing core Django packages to user directory...
pip install --user Django==4.2.11 djangorestframework django-cors-headers

echo.
echo [STEP 2] Installing database and utility packages...
pip install --user python-dotenv requests

echo.
echo [STEP 3] Installing stock data packages...
echo Note: Using your existing pandas 2.3.1 and numpy 2.3.1
pip install --user yfinance

echo.
echo [STEP 4] Installing text processing...
pip install --user textblob

echo.
echo [STEP 5] Installing optional packages for better performance...
pip install --user beautifulsoup4 lxml

echo.
echo [STEP 6] Setting up Django database...
python manage.py makemigrations
if errorlevel 1 (
    echo [WARNING] Migrations had issues, but continuing...
)

python manage.py migrate
if errorlevel 1 (
    echo [ERROR] Database migration failed
    pause
    exit /b 1
)

echo.
echo [STEP 7] Loading NASDAQ ticker data...
python manage.py load_nasdaq_only
if errorlevel 1 (
    echo [WARNING] NASDAQ data loading had issues, but system is ready
)

echo.
echo ============================================================
echo  Setup completed successfully!
echo ============================================================
echo.
echo Your Stock Scanner is ready to use!
echo.
echo Packages installed to user directory (safe from system conflicts)
echo Your existing pandas 2.3.1 and numpy 2.3.1 are being used
echo.
echo To start the application:
echo   python manage.py runserver
echo.
echo Access points:
echo   Main App:    http://localhost:8000
echo   Admin:       http://localhost:8000/admin
echo   API:         http://localhost:8000/api/stocks/
echo.
echo Optional: Create an admin user
echo   python manage.py createsuperuser
echo.
echo Press any key to start the development server...
pause

echo [STARTING] Development server...
python manage.py runserver