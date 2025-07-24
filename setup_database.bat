@echo off
title Stock Scanner - Database Setup
echo 🔧 Stock Scanner Database Setup for Windows
echo ===========================================

echo.
echo 📋 Choose your database option:
echo.
echo 1. MySQL (Production ready, requires MySQL installed)
echo 2. SQLite (Development/testing, no additional software needed)
echo 3. Auto-detect and configure
echo.

:choice
set /p choice="Enter your choice (1, 2, or 3): "

if "%choice%"=="1" goto mysql
if "%choice%"=="2" goto sqlite
if "%choice%"=="3" goto autodetect
echo ❌ Invalid choice. Please enter 1, 2, or 3.
goto choice

:autodetect
echo.
echo 🔍 Auto-detecting database options...
python windows_complete_setup.py --database-only
goto migrations

:mysql
echo.
echo 🔧 Setting up MySQL database...
echo 🔧 Starting MySQL service...
net start mysql
if errorlevel 1 (
    echo ⚠️  Trying alternative service names...
    net start mysql80
    if errorlevel 1 (
        net start mysql84
        if errorlevel 1 (
            echo ❌ Could not start MySQL service
            echo 💡 Please install MySQL or choose SQLite option
            pause
            goto choice
        )
    )
)

echo.
echo 🔧 Configuring MySQL database...
mysql -u root -e "ALTER USER 'root'@'localhost' IDENTIFIED BY 'StockScannerPass2024';" 2>nul
mysql -u root -e "FLUSH PRIVILEGES;" 2>nul
mysql -u root -pStockScannerPass2024 -e "CREATE DATABASE IF NOT EXISTS stock_scanner_db;" 2>nul
mysql -u root -pStockScannerPass2024 -e "CREATE USER IF NOT EXISTS 'stock_scanner_user'@'localhost' IDENTIFIED BY 'StockScannerPass2024';" 2>nul
mysql -u root -pStockScannerPass2024 -e "GRANT ALL PRIVILEGES ON stock_scanner_db.* TO 'stock_scanner_user'@'localhost';" 2>nul
mysql -u root -pStockScannerPass2024 -e "FLUSH PRIVILEGES;" 2>nul

echo.
echo 🔧 Updating .env file for MySQL...
python windows_complete_setup.py --mysql-setup

echo ✅ MySQL setup complete!
echo.
echo 📋 Database Information:
echo   Database: stock_scanner_db
echo   User: stock_scanner_user
echo   Password: StockScannerPass2024
echo   Host: localhost
echo   Port: 3306
goto migrations

:sqlite
echo.
echo 🔧 Setting up SQLite database...
echo 🔧 Updating .env file for SQLite...
python windows_complete_setup.py --sqlite-setup
echo ✅ SQLite setup complete!
echo.
echo 📋 Database Information:
echo   Database: db.sqlite3 (file-based)
echo   No additional configuration needed
goto migrations

:migrations
echo.
echo 🔧 Fixing migration conflicts...
python fix_migrations_windows.py
if errorlevel 1 (
    echo ⚠️  Migration fix may have issues, continuing...
)

echo.
echo 🔧 Running database migrations...
python manage.py migrate
if errorlevel 1 (
    echo ❌ Migration failed
    echo 💡 Check database configuration and try again
    pause
    exit /b 1
)

echo.
echo 🔧 Testing Django configuration...
python test_django_startup.py

echo.
echo ✅ Database setup complete!
echo.
echo 🚀 Next steps:
echo   1. Run: start_app.bat (to start the application)
echo   2. Or manually:
echo      - venv\Scripts\activate
echo      - python manage.py createsuperuser
echo      - python manage.py runserver
echo.
pause
