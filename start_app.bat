@echo off
title Stock Scanner - Start Application
echo 🚀 Starting Stock Scanner Application
echo ===================================

REM Check if virtual environment exists
if exist "venv\Scripts\activate.bat" (
    echo 🔧 Activating virtual environment...
    call venv\Scripts\activate.bat
    echo ✅ Virtual environment activated
) else (
    echo ❌ Virtual environment not found!
    echo 💡 Please run setup.bat first to create virtual environment
    pause
    exit /b 1
)

echo.
echo 🔧 Installing/updating requirements...
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Failed to install requirements
    pause
    exit /b 1
)

echo.
echo 🔧 Running database migrations...
python manage.py migrate
if errorlevel 1 (
    echo ❌ Migration failed - checking database setup...
    echo 💡 Try running setup_database.bat first
    pause
    exit /b 1
)

echo.
echo 🔧 Collecting static files...
python manage.py collectstatic --noinput

echo.
echo 🚀 Starting Django development server...
echo 🌐 Open your browser to: http://127.0.0.1:8000
echo 📋 Press Ctrl+C to stop the server
echo.
python manage.py runserver

pause
