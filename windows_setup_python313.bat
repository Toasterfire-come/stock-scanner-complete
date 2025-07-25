@echo off
REM Windows Setup Script for Stock Scanner - Python 3.13 Compatible
REM This script will automatically set up the Stock Scanner application on Windows with Python 3.13

echo ============================================================
echo  Stock Scanner - Windows Setup (Python 3.13)
echo ============================================================
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

REM Check Python version
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo Python version: %PYTHON_VERSION%
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

REM Create virtual environment
echo [STEP] Creating virtual environment...
python -m venv venv
if errorlevel 1 (
    echo [ERROR] Failed to create virtual environment
    pause
    exit /b 1
)

REM Activate virtual environment
echo [STEP] Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip first
echo [STEP] Upgrading pip...
python -m pip install --upgrade pip

REM Install wheel and setuptools for better package building
echo [STEP] Installing build tools...
pip install wheel setuptools

REM Install Windows-compatible requirements
echo [STEP] Installing Python packages (this may take a few minutes)...
pip install -r requirements_windows.txt

if errorlevel 1 (
    echo [WARNING] Some packages failed to install, trying core packages only...
    echo [STEP] Installing core Django packages...
    pip install Django>=4.2.11 djangorestframework>=3.14.0 django-cors-headers>=4.3.1
    
    echo [STEP] Installing database connector...
    pip install PyMySQL>=1.1.0 dj-database-url>=2.1.0 python-dotenv>=1.0.0
    
    echo [STEP] Installing stock data packages...
    pip install yfinance>=0.2.25 requests>=2.31.0
    
    echo [STEP] Installing optional packages (pandas/numpy already installed)...
    pip install textblob>=0.17.1 cryptography>=41.0.0
)

REM Create database and run migrations
echo [STEP] Setting up database...
python manage.py makemigrations
python manage.py migrate

REM Create superuser (optional)
echo [STEP] Would you like to create an admin user? (y/n)
set /p CREATE_USER="Create admin user (y/n): "
if /i "%CREATE_USER%"=="y" (
    python manage.py createsuperuser
)

REM Load NASDAQ data
echo [STEP] Loading NASDAQ ticker data...
python manage.py load_nasdaq_only

echo.
echo ============================================================
echo  Setup completed successfully!
echo ============================================================
echo.
echo Your virtual environment is now active.
echo.
echo To start the application:
echo   python manage.py runserver
echo.
echo To activate the environment later:
echo   call venv\Scripts\activate.bat
echo.
echo Then open your browser to: http://localhost:8000
echo Admin interface: http://localhost:8000/admin
echo.
echo Press any key to start the development server...
pause

REM Start the development server
python manage.py runserver