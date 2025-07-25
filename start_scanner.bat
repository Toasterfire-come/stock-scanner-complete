@echo off
echo ============================================================
echo  🚀 Starting Stock Scanner 
echo ============================================================
echo.

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo [ERROR] Virtual environment not found!
    echo Please run setup first or create venv manually.
    pause
    exit /b 1
)

echo [INFO] Activating virtual environment...
call venv\Scripts\activate.bat

echo [INFO] Starting Django development server...
echo.
echo Access points:
echo  - Main App: http://localhost:8000
echo  - Admin:    http://localhost:8000/admin
echo  - API:      http://localhost:8000/api/stocks/
echo.
echo Press Ctrl+C to stop the server
echo.

python manage.py runserver

echo.
echo Server stopped. Press any key to exit...
pause