@echo off
echo ========================================
echo Installing Missing Dependencies
echo ========================================
echo.

REM Check if we're in a virtual environment
if defined VIRTUAL_ENV (
    echo Using virtual environment: %VIRTUAL_ENV%
) else (
    echo Activating virtual environment...
    if exist "venv\Scripts\activate.bat" (
        call venv\Scripts\activate.bat
    ) else (
        echo ERROR: Virtual environment not found
        echo Please create it with: python -m venv venv
        pause
        exit /b 1
    )
)

echo.
echo Installing django_extensions...
pip install django_extensions

echo.
echo Installing other dependencies...
pip install -r requirements.txt

echo.
echo ========================================
echo Dependencies installed successfully!
echo ========================================
pause