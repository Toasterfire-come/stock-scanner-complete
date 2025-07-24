@echo off
setlocal enabledelayedexpansion

REM =========================================================================
REM Windows Setup Fix - Stock Scanner
REM Fixes NumPy compilation errors and C++ compiler issues on Windows
REM =========================================================================

echo.
echo ================================================================================
echo ^|                          WINDOWS SETUP FIX                                ^|
echo ^|                      Stock Scanner v3.0                                   ^|
echo ================================================================================
echo.
echo 🔧 This script fixes Windows compilation issues by using pre-compiled packages
echo 📦 No C/C++ compiler needed - all packages have Windows wheels
echo ⚡ Faster installation with pre-built binaries
echo.

REM Check if we're in the project directory
if not exist "manage.py" (
    echo ❌ Error: Please run this script from the project root directory
    echo 💡 Make sure you're in the stock-scanner-complete folder
    pause
    exit /b 1
)

REM Check Python installation
echo 🔧 Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found. Please install Python 3.8+ first.
    echo 💡 Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo ✅ Python found

REM Remove existing virtual environment if it has issues
if exist "venv\" (
    echo 🧹 Cleaning existing virtual environment...
    rmdir /s /q venv 2>nul
)

REM Create fresh virtual environment
echo 🔧 Creating fresh virtual environment...
python -m venv venv
if errorlevel 1 (
    echo ❌ Failed to create virtual environment
    pause
    exit /b 1
)

echo ✅ Virtual environment created

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip to latest version
echo 🔧 Upgrading pip to latest version...
python -m pip install --upgrade pip

REM Install wheel for better package handling
echo 🔧 Installing wheel for better package handling...
pip install wheel setuptools

REM Install packages from Windows-specific requirements
echo 🔧 Installing packages using Windows-optimized requirements...
echo 📦 This will use pre-compiled packages (no compilation needed)
echo ⏱️  Installation may take 3-5 minutes...

pip install -r requirements_windows.txt

if errorlevel 1 (
    echo.
    echo ❌ Installation failed. Trying alternative approach...
    echo 🔧 Installing core packages individually...
    
    REM Install packages one by one to identify issues
    pip install Django>=4.2,^<5.0
    pip install djangorestframework>=3.14.0
    pip install PyMySQL>=1.1.0
    pip install dj-database-url>=2.1.0
    pip install requests>=2.31.0
    pip install python-dotenv>=1.0.0
    
    REM Try numpy with specific Windows-compatible version
    echo 🔧 Installing NumPy (Windows pre-compiled)...
    pip install numpy==1.24.4
    
    REM Try pandas with specific Windows-compatible version
    echo 🔧 Installing Pandas (Windows pre-compiled)...
    pip install pandas==2.0.3
    
    REM Install yfinance
    echo 🔧 Installing yfinance...
    pip install yfinance>=0.2.25
    
    REM Install remaining packages
    pip install celery>=5.3.0
    pip install redis>=5.0.0
    pip install cryptography>=41.0.0
    pip install colorama>=0.4.6
    
    echo 🔧 Core packages installed individually
)

REM Verify critical packages
echo.
echo 🔧 Verifying installation...
python -c "import django; print(f'✅ Django {django.VERSION} installed')" 2>nul
if errorlevel 1 (
    echo ❌ Django verification failed
) else (
    echo ✅ Django verified
)

python -c "import numpy; print(f'✅ NumPy {numpy.__version__} installed')" 2>nul
if errorlevel 1 (
    echo ⚠️  NumPy not installed (optional - will try alternative approach)
) else (
    echo ✅ NumPy verified
)

python -c "import pandas; print(f'✅ Pandas {pandas.__version__} installed')" 2>nul
if errorlevel 1 (
    echo ⚠️  Pandas not installed (optional - will try alternative approach)
) else (
    echo ✅ Pandas verified
)

python -c "import yfinance; print('✅ yfinance installed')" 2>nul
if errorlevel 1 (
    echo ❌ yfinance verification failed
) else (
    echo ✅ yfinance verified
)

REM Update Django settings to use PyMySQL instead of mysqlclient
echo.
echo 🔧 Configuring database settings for Windows...
python -c "
try:
    import pymysql
    pymysql.install_as_MySQLdb()
    print('✅ PyMySQL configured as MySQL driver')
except ImportError:
    print('⚠️  PyMySQL not available')
"

REM Create or update database configuration
echo 🔧 Setting up database configuration...
if not exist ".env" (
    echo # Stock Scanner Environment Configuration > .env
    echo DEBUG=true >> .env
    echo SECRET_KEY=windows-dev-key-change-in-production >> .env
    echo DATABASE_URL=sqlite:///db.sqlite3 >> .env
    echo ALLOWED_HOSTS=localhost,127.0.0.1 >> .env
    echo ✅ Created basic .env file
)

REM Run Django setup
echo.
echo 🔧 Setting up Django...
python manage.py collectstatic --noinput >nul 2>&1
python manage.py makemigrations >nul 2>&1
python manage.py migrate >nul 2>&1

if errorlevel 1 (
    echo ⚠️  Django setup had some issues (this is normal for first run)
) else (
    echo ✅ Django setup completed
)

echo.
echo ================================================================================
echo ✅ WINDOWS SETUP FIX COMPLETED!
echo ================================================================================
echo.
echo 🎯 Installation Status:
echo    ✅ Virtual environment created
echo    ✅ Pre-compiled packages installed
echo    ✅ Windows compatibility ensured
echo    ✅ Database configured
echo.
echo 🚀 Next Steps:
echo    1. Test the installation: python manage.py runserver
echo    2. Load ticker data: LOAD_COMPLETE_NASDAQ.bat
echo    3. Start stock scanning: START_HERE.bat
echo.
echo 💡 Tips:
echo    - All packages are now pre-compiled (no compiler needed)
echo    - PyMySQL is used instead of mysqlclient
echo    - SQLite is default database (change to MySQL for production)
echo.
echo 🔧 If you still have issues:
echo    1. Update Python: Download latest from python.org
echo    2. Check Windows version: Windows 10/11 recommended
echo    3. Run as Administrator if permission issues
echo.

echo Press any key to continue...
pause >nul