@echo off
echo 🔧 Database Issues Fix for Windows
echo ==================================
echo.

REM Check if virtual environment is activated
if not defined VIRTUAL_ENV (
    echo ⚠️  Virtual environment not detected
    echo 🔧 Attempting to activate virtual environment...
    if exist "venv\Scripts\activate.bat" (
        call venv\Scripts\activate.bat
        echo ✅ Virtual environment activated
    ) else (
        echo ❌ Virtual environment not found
        echo 💡 Please run this from your project directory with venv/ folder
        pause
        exit /b 1
    )
) else (
    echo ✅ Virtual environment is active
)

echo.
echo 📋 You have two options to fix the database permission issue:
echo.
echo 1. Fix PostgreSQL permissions (Production ready)
echo 2. Switch to SQLite (Quick development setup)
echo.
echo 💡 For production deployment, choose option 1
echo 💡 For quick development/testing, choose option 2
echo.

:choice
set /p choice="Enter your choice (1 or 2): "

if "%choice%"=="1" goto postgresql
if "%choice%"=="2" goto sqlite
echo ❌ Invalid choice. Please enter 1 or 2.
goto choice

:postgresql
echo.
echo 🔧 Fixing PostgreSQL permissions...
echo 📋 You will need:
echo    • PostgreSQL superuser password (usually 'postgres' user)
echo    • Database name and user credentials
echo.
python fix_postgresql_permissions.py
goto end

:sqlite
echo.
echo 🔄 Switching to SQLite database...
echo 💡 This is perfect for development and testing
echo.
python switch_to_sqlite.py
goto end

:end
echo.
echo 📋 Next steps after fixing database:
echo    python manage.py migrate
echo    python manage.py createsuperuser  
echo    python manage.py runserver
echo.
pause