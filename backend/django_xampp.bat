@echo off
REM Django XAMPP Wrapper
REM This makes all Django commands work automatically with XAMPP MySQL
REM Usage: django_xampp.bat <django_command>
REM Examples: 
REM   django_xampp.bat runserver
REM   django_xampp.bat migrate
REM   django_xampp.bat makemigrations
REM   django_xampp.bat shell

echo Django XAMPP Command Wrapper
echo ==============================

REM Set environment variables
set DJANGO_SETTINGS_MODULE=stockscanner_django.settings
set PYTHONIOENCODING=utf-8

REM Add XAMPP MySQL to PATH if it exists
set XAMPP_MYSQL_PATH=C:\xampp\mysql\bin
if exist "%XAMPP_MYSQL_PATH%" (
    echo INFO: Adding XAMPP MySQL to PATH...
    set PATH=%PATH%;%XAMPP_MYSQL_PATH%
) else (
    echo WARNING: XAMPP MySQL not found at %XAMPP_MYSQL_PATH%
)

REM Check if XAMPP Control Panel is running
tasklist /fi "imagename eq xampp-control.exe" 2>NUL | find /i /n "xampp-control.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo INFO: XAMPP Control Panel is running
) else (
    echo WARNING: XAMPP Control Panel not detected
    echo Please ensure XAMPP MySQL service is started
)

REM Run the Django command with all arguments
if "%1"=="" (
    echo ERROR: No Django command provided
    echo.
    echo Usage: django_xampp.bat [command] [options]
    echo.
    echo Common commands:
    echo   runserver          - Start the development server
    echo   migrate            - Apply database migrations
    echo   makemigrations     - Create new migrations
    echo   shell              - Open Django shell
    echo   createsuperuser    - Create admin user
    echo   collectstatic      - Collect static files
    echo.
    echo Examples:
    echo   django_xampp.bat runserver
    echo   django_xampp.bat runserver 8080
    echo   django_xampp.bat migrate
    echo   django_xampp.bat makemigrations stocks
    echo   django_xampp.bat shell
    pause
    exit /b 1
)

echo Running: python manage.py %*
echo.
python manage.py %*

REM If runserver, show helpful information
if "%1"=="runserver" (
    echo.
    echo =================================
    echo Django Server with XAMPP MySQL
    echo =================================
    echo.
    echo If the server started successfully, visit:
    echo - WordPress API: http://127.0.0.1:8000/api/wordpress/
    echo - Django Admin: http://127.0.0.1:8000/admin/
    echo - Stock API: http://127.0.0.1:8000/api/stocks/
    echo.
    echo Database Management:
    echo - phpMyAdmin: http://localhost/phpmyadmin
    echo - XAMPP Control: C:\xampp\xampp-control.exe
    echo.
    echo Press Ctrl+C to stop the server
)

echo.
echo Command completed.
if not "%1"=="runserver" pause