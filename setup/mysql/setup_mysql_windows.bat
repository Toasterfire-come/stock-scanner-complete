@echo off
REM ============================================================================
REM Stock Scanner - Complete MySQL Production Setup for Windows
REM ============================================================================
REM This script sets up MySQL production database for the Stock Scanner app
REM Includes: MySQL installation check, database creation, user setup,
REM          environment configuration, Django integration, and monitoring tools
REM 
REM Usage: setup_mysql_windows.bat
REM 
REM Author: Stock Scanner Project
REM Version: 2.0.0 - Production Ready
REM ============================================================================

title Stock Scanner - MySQL Production Setup

echo.
echo ===================================================================
echo 🚀 STOCK SCANNER - MYSQL PRODUCTION SETUP
echo ===================================================================
echo 🎯 This will configure MySQL for production deployment
echo ⏱️  Estimated time: 15-20 minutes
echo 🔒 Sets up secure production database with optimizations
echo.

echo 📋 This setup will:
echo    1. Check MySQL installation
echo    2. Start MySQL service
echo    3. Create production database and user
echo    4. Generate production .env file
echo    5. Update Django settings for MySQL
echo    6. Run database migrations
echo    7. Create backup and monitoring scripts
echo.

pause
echo.

REM ============================================================================
REM Step 1: Check if Python is available
REM ============================================================================
echo 🔍 Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python not found in PATH
    echo    Please ensure Python is installed and in your PATH
    echo    Download from: https://python.org/downloads/
    pause
    exit /b 1
)

python --version
echo ✅ Python is available

REM ============================================================================
REM Step 2: Activate virtual environment if it exists
REM ============================================================================
echo.
echo 🔍 Checking for virtual environment...
if exist "venv\Scripts\activate.bat" (
    echo ✅ Activating virtual environment...
    call venv\Scripts\activate.bat
) else (
    echo ⚠️  No virtual environment found
    echo    Consider creating one with: python -m venv venv
)

REM ============================================================================
REM Step 3: Install/Update required packages
REM ============================================================================
echo.
echo 📦 Installing required MySQL packages...
python -m pip install --upgrade pip
python -m pip install mysqlclient PyMySQL dj-database-url cryptography

if %errorlevel% neq 0 (
    echo ⚠️  Package installation failed, trying alternative method...
    python install_windows_safe.py
)

REM ============================================================================
REM Step 4: Run the comprehensive MySQL setup script
REM ============================================================================
echo.
echo 🚀 Running comprehensive MySQL production setup...
python setup_mysql_production_complete.py

if %errorlevel% neq 0 (
    echo ❌ MySQL setup failed
    echo.
    echo 💡 Troubleshooting suggestions:
    echo    1. Ensure MySQL is installed from: https://dev.mysql.com/downloads/mysql/
    echo    2. Make sure MySQL service is running
    echo    3. Check Windows Firewall isn't blocking MySQL
    echo    4. Try running as Administrator
    echo.
    pause
    exit /b 1
)

REM ============================================================================
REM Step 5: Create additional Windows-specific scripts
REM ============================================================================
echo.
echo 🔧 Creating Windows management scripts...

REM Create MySQL service management script
echo @echo off > mysql_service_manager.bat
echo REM MySQL Service Management for Stock Scanner >> mysql_service_manager.bat
echo. >> mysql_service_manager.bat
echo echo 🔧 MySQL Service Manager >> mysql_service_manager.bat
echo echo ======================= >> mysql_service_manager.bat
echo echo. >> mysql_service_manager.bat
echo echo 1. Start MySQL Service >> mysql_service_manager.bat
echo echo 2. Stop MySQL Service >> mysql_service_manager.bat
echo echo 3. Restart MySQL Service >> mysql_service_manager.bat
echo echo 4. Check MySQL Status >> mysql_service_manager.bat
echo echo 5. Exit >> mysql_service_manager.bat
echo echo. >> mysql_service_manager.bat
echo set /p choice="Enter your choice (1-5): " >> mysql_service_manager.bat
echo. >> mysql_service_manager.bat
echo if "%%choice%%"=="1" ( >> mysql_service_manager.bat
echo     echo Starting MySQL service... >> mysql_service_manager.bat
echo     net start mysql ^|^| net start mysql80 ^|^| net start mysql84 >> mysql_service_manager.bat
echo ) >> mysql_service_manager.bat
echo if "%%choice%%"=="2" ( >> mysql_service_manager.bat
echo     echo Stopping MySQL service... >> mysql_service_manager.bat
echo     net stop mysql ^|^| net stop mysql80 ^|^| net stop mysql84 >> mysql_service_manager.bat
echo ) >> mysql_service_manager.bat
echo if "%%choice%%"=="3" ( >> mysql_service_manager.bat
echo     echo Restarting MySQL service... >> mysql_service_manager.bat
echo     net stop mysql ^|^| net stop mysql80 ^|^| net stop mysql84 >> mysql_service_manager.bat
echo     timeout /t 3 >> mysql_service_manager.bat
echo     net start mysql ^|^| net start mysql80 ^|^| net start mysql84 >> mysql_service_manager.bat
echo ) >> mysql_service_manager.bat
echo if "%%choice%%"=="4" ( >> mysql_service_manager.bat
echo     echo Checking MySQL status... >> mysql_service_manager.bat
echo     sc query mysql ^|^| sc query mysql80 ^|^| sc query mysql84 >> mysql_service_manager.bat
echo ) >> mysql_service_manager.bat
echo pause >> mysql_service_manager.bat

echo ✅ Created mysql_service_manager.bat

REM Create Django MySQL management script
echo @echo off > django_mysql_manager.bat
echo REM Django MySQL Management for Stock Scanner >> django_mysql_manager.bat
echo. >> django_mysql_manager.bat
echo if exist "venv\Scripts\activate.bat" call venv\Scripts\activate.bat >> django_mysql_manager.bat
echo. >> django_mysql_manager.bat
echo echo 🔧 Django MySQL Manager >> django_mysql_manager.bat
echo echo ====================== >> django_mysql_manager.bat
echo echo. >> django_mysql_manager.bat
echo echo 1. Run Django Migrations >> django_mysql_manager.bat
echo echo 2. Create Superuser >> django_mysql_manager.bat
echo echo 3. Start Django Server >> django_mysql_manager.bat
echo echo 4. Django Shell >> django_mysql_manager.bat
echo echo 5. Database Shell >> django_mysql_manager.bat
echo echo 6. Collect Static Files >> django_mysql_manager.bat
echo echo 7. Test Django Settings >> django_mysql_manager.bat
echo echo 8. Exit >> django_mysql_manager.bat
echo echo. >> django_mysql_manager.bat
echo set /p choice="Enter your choice (1-8): " >> django_mysql_manager.bat
echo. >> django_mysql_manager.bat
echo if "%%choice%%"=="1" ( >> django_mysql_manager.bat
echo     echo Running migrations... >> django_mysql_manager.bat
echo     python manage.py makemigrations >> django_mysql_manager.bat
echo     python manage.py migrate >> django_mysql_manager.bat
echo ) >> django_mysql_manager.bat
echo if "%%choice%%"=="2" ( >> django_mysql_manager.bat
echo     echo Creating superuser... >> django_mysql_manager.bat
echo     python manage.py createsuperuser >> django_mysql_manager.bat
echo ) >> django_mysql_manager.bat
echo if "%%choice%%"=="3" ( >> django_mysql_manager.bat
echo     echo Starting Django development server... >> django_mysql_manager.bat
echo     python manage.py runserver >> django_mysql_manager.bat
echo ) >> django_mysql_manager.bat
echo if "%%choice%%"=="4" ( >> django_mysql_manager.bat
echo     echo Opening Django shell... >> django_mysql_manager.bat
echo     python manage.py shell >> django_mysql_manager.bat
echo ) >> django_mysql_manager.bat
echo if "%%choice%%"=="5" ( >> django_mysql_manager.bat
echo     echo Opening database shell... >> django_mysql_manager.bat
echo     python manage.py dbshell >> django_mysql_manager.bat
echo ) >> django_mysql_manager.bat
echo if "%%choice%%"=="6" ( >> django_mysql_manager.bat
echo     echo Collecting static files... >> django_mysql_manager.bat
echo     python manage.py collectstatic --noinput >> django_mysql_manager.bat
echo ) >> django_mysql_manager.bat
echo if "%%choice%%"=="7" ( >> django_mysql_manager.bat
echo     echo Testing Django settings... >> django_mysql_manager.bat
echo     python fix_django_settings_error.py >> django_mysql_manager.bat
echo ) >> django_mysql_manager.bat
echo pause >> django_mysql_manager.bat

echo ✅ Created django_mysql_manager.bat

REM ============================================================================
REM Step 6: Test the setup
REM ============================================================================
echo.
echo 🧪 Testing MySQL production setup...
python -c "
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stockscanner_django.settings')
import django
django.setup()
from django.db import connection
cursor = connection.cursor()
cursor.execute('SELECT VERSION();')
version = cursor.fetchone()[0]
print(f'✅ MySQL connection test successful - Version: {version}')
"

if %errorlevel% neq 0 (
    echo ⚠️  MySQL connection test failed
    echo    The database may not be fully configured yet
    echo    Try running the setup again or check mysql_health_check.bat
)

REM ============================================================================
REM Setup Complete
REM ============================================================================
echo.
echo ===================================================================
echo 🎉 MYSQL PRODUCTION SETUP COMPLETED!
echo ===================================================================
echo.
echo 📋 What was created:
echo    ✅ Production MySQL database: stock_scanner_production
echo    ✅ Database user: stock_scanner_prod
echo    ✅ Production .env file with MySQL configuration
echo    ✅ Django settings optimized for MySQL
echo    ✅ Database backup script: backup_database.bat
echo    ✅ Health monitoring script: mysql_health_check.bat
echo    ✅ Service manager: mysql_service_manager.bat
echo    ✅ Django manager: django_mysql_manager.bat
echo.
echo 🚀 Next Steps:
echo    1. Review and customize your .env file
echo    2. Run: django_mysql_manager.bat (option 2) - Create superuser
echo    3. Run: django_mysql_manager.bat (option 3) - Start Django server
echo    4. Open browser to: http://127.0.0.1:8000
echo    5. Schedule backup_database.bat to run daily
echo.
echo 🔧 Useful Commands:
echo    mysql_health_check.bat     - Check database health
echo    backup_database.bat        - Manual database backup
echo    mysql_service_manager.bat  - Manage MySQL service
echo    django_mysql_manager.bat   - Django management tasks
echo.
echo 💡 Tips:
echo    - Keep your .env file secure and backed up
echo    - Run mysql_health_check.bat regularly
echo    - Setup automated backups using Task Scheduler
echo    - Monitor disk space for database growth
echo.

pause
echo.
echo 🚀 Starting Django management interface...
call django_mysql_manager.bat