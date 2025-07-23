@echo off
echo 🔧 Django Migration Conflict Fixer for Windows
echo =============================================
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
echo 🚀 Running migration conflict fix...
python fix_migrations_windows.py

echo.
echo 📋 Next: Run these commands to complete the setup:
echo    python manage.py migrate
echo    python manage.py createsuperuser
echo    python manage.py runserver
echo.
pause