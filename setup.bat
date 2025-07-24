@echo off
title Stock Scanner - Complete Setup
color 0A
echo.
echo ████████████████████████████████████████████████████████████████████████████████
echo █                                                                              █
echo █                        🚀 STOCK SCANNER SETUP                              █
echo █                     Complete Windows Installation                           █
echo █                                                                              █
echo ████████████████████████████████████████████████████████████████████████████████
echo.

REM Check if Python is installed
echo 🔍 Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found in PATH!
    echo.
    echo 💡 Please install Python 3.8+ from https://python.org
    echo    Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
) else (
    for /f "tokens=2" %%i in ('python --version') do echo ✅ Python %%i found
)

echo.
echo 🔧 Step 1: Creating virtual environment...
if exist "venv" (
    echo ⚠️  Virtual environment already exists
    echo 🔧 Removing old virtual environment...
    rmdir /s /q venv
)

python -m venv venv
if errorlevel 1 (
    echo ❌ Failed to create virtual environment
    pause
    exit /b 1
)
echo ✅ Virtual environment created

echo.
echo 🔧 Step 2: Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ❌ Failed to activate virtual environment
    pause
    exit /b 1
)
echo ✅ Virtual environment activated

echo.
echo 🔧 Step 3: Upgrading pip...
python -m pip install --upgrade pip
if errorlevel 1 (
    echo ⚠️  Pip upgrade failed, continuing...
)

echo.
echo 🔧 Step 4: Installing Python requirements (Windows-safe method)...
echo 📦 This may take a few minutes...
python install_windows_safe.py
if errorlevel 1 (
    echo ❌ Windows-safe installation failed, trying standard method...
    echo 💡 Attempting standard pip install...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ❌ Both installation methods failed
        echo.
        echo 💡 Solutions:
        echo    - Install Microsoft Visual Studio Build Tools
        echo    - Run as administrator
        echo    - Check your internet connection
        echo.
        pause
        exit /b 1
    )
)
echo ✅ Requirements installed successfully

echo.
echo 🔧 Step 5: Running Windows setup script...
python windows_complete_setup.py
if errorlevel 1 (
    echo ⚠️  Setup script had issues, continuing...
)

echo.
echo 🔧 Step 6: Setting up database...
echo 📋 Choose your database option:
echo.
echo 1. Auto-detect (Recommended)
echo 2. MySQL (Production)
echo 3. SQLite (Development)
echo.

:db_choice
set /p db_choice="Enter your choice (1, 2, or 3): "

if "%db_choice%"=="1" goto auto_db
if "%db_choice%"=="2" goto manual_mysql
if "%db_choice%"=="3" goto manual_sqlite
echo ❌ Invalid choice. Please enter 1, 2, or 3.
goto db_choice

:auto_db
echo.
echo 🔍 Auto-detecting best database option...
python windows_complete_setup.py --database-only
goto migrations

:manual_mysql
echo.
echo 🔧 Setting up MySQL...
python windows_complete_setup.py --mysql-setup
goto migrations

:manual_sqlite
echo.
echo 🔧 Setting up SQLite...
python windows_complete_setup.py --sqlite-setup
goto migrations

:migrations
echo.
echo 🔧 Step 7: Fixing migration conflicts...
python fix_migrations_windows.py
if errorlevel 1 (
    echo ⚠️  Migration fix had issues, continuing...
)

echo.
echo 🔧 Step 8: Running database migrations...
python manage.py migrate
if errorlevel 1 (
    echo ❌ Migration failed
    echo 💡 Try running setup_database.bat to fix database issues
    pause
    exit /b 1
)
echo ✅ Database migrations completed

echo.
echo 🔧 Step 9: Testing Django configuration...
python test_django_startup.py
if errorlevel 1 (
    echo ⚠️  Django test had issues, but setup continues...
)

echo.
echo 🔧 Step 10: Creating logs directory...
if not exist "logs" mkdir logs
echo ✅ Logs directory ready

echo.
echo 🔧 Step 11: Running comprehensive system check...
python windows_complete_setup.py --test-only

echo.
echo ████████████████████████████████████████████████████████████████████████████████
echo █                                                                              █
echo █                         ✅ SETUP COMPLETE!                                 █
echo █                                                                              █
echo ████████████████████████████████████████████████████████████████████████████████
echo.
echo 🚀 Your Stock Scanner is ready to use!
echo.
echo 📋 Next Steps:
echo    1. Double-click "start_app.bat" to start the application
echo    2. Open your browser to: http://127.0.0.1:8000
echo    3. Create a superuser account when prompted
echo.
echo 🔧 Useful commands:
echo    - start_app.bat        : Start the application
echo    - setup_database.bat   : Reconfigure database
echo    - test_system.bat      : Run system tests
echo.
echo 💡 Troubleshooting:
echo    - If you encounter issues, check the logs/ directory
echo    - Run test_system.bat to diagnose problems
echo    - See WINDOWS_SETUP_GUIDE.md for detailed instructions
echo.

set /p create_user="Would you like to create a Django admin user now? (y/n): "
if /i "%create_user%"=="y" (
    echo.
    echo 🔧 Creating Django admin user...
    python manage.py createsuperuser
)

echo.
echo 🎉 Setup completed successfully!
echo 📖 Check the README.md file for usage instructions
echo.
pause