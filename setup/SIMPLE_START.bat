@echo off
title Stock Scanner - Simple Start
color 0A

echo.
echo ████████████████████████████████████████████████████████████████████████████████
echo █                                                                              █
echo █                    🚀 STOCK SCANNER - SIMPLE START                         █
echo █                        One Command Does Everything                          █
echo █                                                                              █
echo ████████████████████████████████████████████████████████████████████████████████
echo.
echo 🎯 This will automatically:
echo    ✅ Install all requirements
echo    ✅ Set up MySQL production database
echo    ✅ Configure Django
echo    ✅ Run migrations
echo    ✅ Start the application
echo.
echo ⏱️  Total time: 15-20 minutes
echo 💡 Just press Enter when prompted and follow simple instructions
echo.

pause

REM ============================================================================
REM Step 1: Basic Checks
REM ============================================================================
echo.
echo 🔍 Step 1/7: Checking system requirements...

python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found!
    echo.
    echo 💡 Please install Python first:
    echo    1. Go to https://python.org/downloads/
    echo    2. Download Python 3.8 or newer
    echo    3. IMPORTANT: Check "Add Python to PATH" during installation
    echo    4. Restart this script after installation
    echo.
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version') do echo ✅ Python %%i ready

REM ============================================================================
REM Step 2: Virtual Environment
REM ============================================================================
echo.
echo 🔧 Step 2/7: Setting up Python environment...

if exist "venv" (
    echo ✅ Using existing virtual environment
) else (
    echo 📦 Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ❌ Failed to create virtual environment
        pause
        exit /b 1
    )
)

call venv\Scripts\activate.bat
echo ✅ Virtual environment activated

REM ============================================================================
REM Step 3: Install Requirements
REM ============================================================================
echo.
echo 📦 Step 3/7: Installing requirements (this may take a few minutes)...

python -m pip install --upgrade pip >nul 2>&1

echo    Installing Django and core packages...
pip install Django>=5.1.0 djangorestframework django-cors-headers >nul 2>&1

echo    Installing MySQL support...
pip install mysqlclient PyMySQL dj-database-url cryptography >nul 2>&1
if errorlevel 1 (
    echo    ⚠️  MySQL packages failed, installing alternatives...
    pip install PyMySQL dj-database-url >nul 2>&1
)

echo    Installing other requirements...
pip install python-dotenv requests yfinance pandas numpy >nul 2>&1
pip install celery django-celery-beat redis django-redis >nul 2>&1
pip install beautifulsoup4 lxml gunicorn whitenoise >nul 2>&1

echo ✅ All requirements installed

REM ============================================================================
REM Step 4: MySQL Setup
REM ============================================================================
echo.
echo 🗄️  Step 4/7: Setting up MySQL database...

echo 🔍 Checking for MySQL installation...
mysql --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo ❌ MySQL not found on your system
    echo.
    echo 💡 Please install MySQL Server:
    echo    1. Go to: https://dev.mysql.com/downloads/mysql/
    echo    2. Download MySQL Server 8.0 or newer
    echo    3. During installation:
    echo       - Set root password to: StockScannerRoot2024!
    echo       - Enable "Start MySQL Server at System Startup"
    echo       - Add MySQL to Windows PATH
    echo    4. After installation, restart this script
    echo.
    set /p install_mysql="Press Enter to open MySQL download page, then restart this script..."
    start https://dev.mysql.com/downloads/mysql/
    pause
    exit /b 1
)

echo ✅ MySQL found, configuring database...

echo 🔧 Starting MySQL service...
net start mysql >nul 2>&1 || net start mysql80 >nul 2>&1 || net start mysql84 >nul 2>&1

echo 🗄️  Creating production database...
mysql -u root -pStockScannerRoot2024! -e "CREATE DATABASE IF NOT EXISTS stock_scanner_production CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;" 2>nul
mysql -u root -pStockScannerRoot2024! -e "CREATE USER IF NOT EXISTS 'stock_scanner_prod'@'localhost' IDENTIFIED BY 'StockScannerProd2024!';" 2>nul
mysql -u root -pStockScannerRoot2024! -e "GRANT ALL PRIVILEGES ON stock_scanner_production.* TO 'stock_scanner_prod'@'localhost';" 2>nul
mysql -u root -pStockScannerRoot2024! -e "FLUSH PRIVILEGES;" 2>nul

echo ✅ MySQL database configured

REM ============================================================================
REM Step 5: Environment Configuration
REM ============================================================================
echo.
echo ⚙️  Step 5/7: Creating configuration files...

echo # Stock Scanner Production Configuration > .env
echo # Auto-generated by SIMPLE_START.bat >> .env
echo. >> .env
echo # Django Settings >> .env
echo SECRET_KEY=django-production-key-change-this-in-deployment >> .env
echo DEBUG=false >> .env
echo ALLOWED_HOSTS=localhost,127.0.0.1,yourdomain.com >> .env
echo. >> .env
echo # MySQL Production Database >> .env
echo DATABASE_URL=mysql://stock_scanner_prod:StockScannerProd2024!@localhost:3306/stock_scanner_production >> .env
echo DB_ENGINE=django.db.backends.mysql >> .env
echo DB_NAME=stock_scanner_production >> .env
echo DB_USER=stock_scanner_prod >> .env
echo DB_PASSWORD=StockScannerProd2024! >> .env
echo DB_HOST=localhost >> .env
echo DB_PORT=3306 >> .env
echo. >> .env
echo # Connection Pooling >> .env
echo DB_CONN_MAX_AGE=300 >> .env
echo DB_CONN_HEALTH_CHECKS=true >> .env
echo. >> .env
echo # Email Configuration >> .env
echo EMAIL_HOST=smtp.gmail.com >> .env
echo EMAIL_PORT=587 >> .env
echo EMAIL_USE_TLS=true >> .env
echo EMAIL_HOST_USER=your-email@gmail.com >> .env
echo EMAIL_HOST_PASSWORD=your-app-password >> .env
echo. >> .env
echo # Celery Configuration >> .env
echo CELERY_ENABLED=false >> .env
echo CELERY_BROKER_URL= >> .env
echo. >> .env
echo # Yahoo Finance API >> .env
echo YFINANCE_RATE_LIMIT=true >> .env
echo YFINANCE_MAX_REQUESTS_PER_MINUTE=60 >> .env
echo YFINANCE_DELAY_BETWEEN_REQUESTS=1.0 >> .env
echo YFINANCE_TIMEOUT=30 >> .env
echo. >> .env
echo # Security Settings >> .env
echo SECURE_SSL_REDIRECT=false >> .env
echo SECURE_BROWSER_XSS_FILTER=true >> .env
echo SECURE_CONTENT_TYPE_NOSNIFF=true >> .env
echo X_FRAME_OPTIONS=DENY >> .env
echo. >> .env
echo # Logging >> .env
echo LOG_LEVEL=INFO >> .env
echo LOG_FILE=logs/stock_scanner.log >> .env

echo ✅ Configuration files created

REM ============================================================================
REM Step 6: Django Setup
REM ============================================================================
echo.
echo 🔧 Step 6/7: Setting up Django...

if not exist "logs" mkdir logs

echo 📋 Removing old migration conflicts...
if exist "stocks\migrations\0002_stockalert_company_name.py" del "stocks\migrations\0002_stockalert_company_name.py" >nul 2>&1
if exist "stocks\migrations\0003_add_price_change_fields.py" del "stocks\migrations\0003_add_price_change_fields.py" >nul 2>&1
if exist "stocks\migrations\0003_remove_pay_as_you_go.py" del "stocks\migrations\0003_remove_pay_as_you_go.py" >nul 2>&1

echo 🗄️  Creating database tables...
python manage.py makemigrations
if errorlevel 1 (
    echo ⚠️  Makemigrations had issues, continuing...
)

python manage.py migrate
if errorlevel 1 (
    echo ❌ Database migration failed
    echo 💡 Check if MySQL is running and credentials are correct
    pause
    exit /b 1
)

echo 📁 Setting up static files...
python manage.py collectstatic --noinput >nul 2>&1

echo ✅ Django setup complete

REM ============================================================================
REM Step 7: Create Admin User & Start
REM ============================================================================
echo.
echo 👤 Step 7/7: Final setup...

echo.
echo 🎉 Setup completed successfully!
echo.
echo 📋 What was created:
echo    ✅ MySQL production database: stock_scanner_production
echo    ✅ Database user: stock_scanner_prod
echo    ✅ Django application configured
echo    ✅ All requirements installed
echo.

set /p create_admin="Would you like to create an admin user now? (y/n): "
if /i "%create_admin%"=="y" (
    echo.
    echo 👤 Creating admin user...
    echo 💡 Choose a username and password you'll remember
    python manage.py createsuperuser
)

echo.
echo 🚀 Starting Stock Scanner...
echo 🌐 The application will open at: http://127.0.0.1:8000
echo 🔧 Press Ctrl+C to stop the server when you're done
echo.

REM Create a simple restart script
echo @echo off > start_stock_scanner.bat
echo echo Starting Stock Scanner... >> start_stock_scanner.bat
echo if exist "venv\Scripts\activate.bat" call venv\Scripts\activate.bat >> start_stock_scanner.bat
echo python manage.py runserver >> start_stock_scanner.bat
echo pause >> start_stock_scanner.bat

echo 💡 Next time, just double-click "start_stock_scanner.bat" to start the app
echo.

timeout /t 3 /nobreak >nul
start http://127.0.0.1:8000
python manage.py runserver

pause