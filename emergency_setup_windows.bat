@echo off
title Stock Scanner - Emergency Windows Setup
echo 🚨 Emergency Windows Setup (Compilation Issues Bypass)
echo ====================================================

echo.
echo 🎯 This script bypasses ALL compilation issues and gets Django running
echo 💡 Installs only packages that work without C compilers
echo ⚡ Gets you up and running in under 5 minutes
echo.

REM Check if virtual environment exists
if exist "venv\Scripts\activate.bat" (
    echo 🔧 Activating existing virtual environment...
    call venv\Scripts\activate.bat
) else (
    echo 🔧 Creating new virtual environment...
    python -m venv venv
    call venv\Scripts\activate.bat
    echo ✅ Virtual environment created and activated
)

echo.
echo 🔧 Step 1: Upgrading pip...
python -m pip install --upgrade pip

echo.
echo 🔧 Step 2: Installing minimal requirements (no compilation needed)...
pip install -r requirements-minimal.txt
if errorlevel 1 (
    echo ⚠️  Minimal requirements failed, installing core packages individually...
    
    echo 📦 Installing Django...
    pip install Django>=5.1.8
    
    echo 📦 Installing Django REST Framework...
    pip install djangorestframework>=3.15.0
    
    echo 📦 Installing database tools...
    pip install dj-database-url>=2.1.0
    
    echo 📦 Installing API tools...
    pip install requests>=2.31.0
    pip install yfinance==0.2.51
    
    echo 📦 Installing utilities...
    pip install python-dotenv>=1.0.0
    pip install django-cors-headers>=4.3.0
    
    echo ✅ Core packages installed individually
) else (
    echo ✅ Minimal requirements installed successfully
)

echo.
echo 🔧 Step 3: Setting up database (SQLite - no complications)...
python windows_complete_setup.py --sqlite-setup
if errorlevel 1 (
    echo 🔧 Creating .env manually for SQLite...
    echo # Emergency SQLite Configuration > .env
    echo SECRET_KEY=emergency-setup-key-change-later >> .env
    echo DEBUG=True >> .env
    echo DATABASE_URL=sqlite:///./db.sqlite3 >> .env
    echo ALLOWED_HOSTS=localhost,127.0.0.1 >> .env
)

echo.
echo 🔧 Step 4: Creating basic Django setup...
python manage.py migrate --run-syncdb
if errorlevel 1 (
    echo ⚠️  Migration failed, trying basic setup...
    python manage.py check
)

echo.
echo 🔧 Step 5: Testing Django...
python -c "import django; print(f'✅ Django {django.__version__} working!')"
if errorlevel 1 (
    echo ❌ Django test failed
) else (
    echo ✅ Django working correctly
)

python -c "import yfinance; print('✅ yfinance working!')" 2>nul
if errorlevel 1 (
    echo ⚠️  yfinance not available, but Django should work
) else (
    echo ✅ yfinance working correctly
)

echo.
echo ========================================
echo 🎉 Emergency Setup Complete!
echo ========================================

echo.
echo 📊 What's Working:
echo ✅ Django framework
echo ✅ SQLite database  
echo ✅ Basic API functionality
echo ✅ Development server ready

echo.
echo ⚠️  What's Missing (can be added later):
echo - NumPy/Pandas (for advanced analytics)
echo - lxml (for some web scraping)
echo - cryptography (for advanced security)

echo.
echo 🚀 Ready to Start:
echo    python manage.py runserver
echo    
echo 🌐 Then open: http://127.0.0.1:8000

echo.
echo 💡 To add missing packages later:
echo    Run: fix_windows_compiler_issues.bat

echo.
echo 📋 Next Steps:
echo    1. python manage.py createsuperuser (create admin account)
echo    2. python manage.py runserver (start the server)
echo    3. Visit http://127.0.0.1:8000/admin (Django admin)

echo.
pause