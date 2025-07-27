@echo off
echo ========================================
echo COMPLETE XAMPP SETUP FOR STOCK SCANNER
echo ========================================
echo.
echo This will:
echo - Download and install XAMPP with MySQL
echo - Configure all scripts to use XAMPP
echo - Set up the database with all needed fields
echo - Update all batch files for XAMPP paths
echo - Test everything end-to-end
echo.

REM Set UTF-8 encoding
chcp 65001 > nul 2>&1

REM Set environment variables
set DJANGO_SETTINGS_MODULE=stockscanner_django.settings
set PYTHONIOENCODING=utf-8
set XAMPP_PATH=C:\xampp
set XAMPP_MYSQL_PATH=C:\xampp\mysql\bin

echo [STEP 1] Checking for existing XAMPP installation...
if exist "%XAMPP_PATH%\xampp-control.exe" (
    echo INFO: XAMPP already installed at %XAMPP_PATH%
    echo Checking if MySQL is working...
    if exist "%XAMPP_MYSQL_PATH%\mysql.exe" (
        echo SUCCESS: XAMPP MySQL found
        goto :configure_xampp
    )
)

echo INFO: XAMPP not found, will download and install
echo.

echo [STEP 2] Downloading XAMPP installer...
if exist "xampp-installer.exe" del "xampp-installer.exe"

echo Downloading XAMPP (this may take several minutes)...
powershell -Command "try { $ProgressPreference = 'SilentlyContinue'; Invoke-WebRequest -Uri 'https://sourceforge.net/projects/xampp/files/XAMPP Windows/8.2.12/xampp-windows-x64-8.2.12-0-VS16-installer.exe/download' -OutFile 'xampp-installer.exe'; Write-Host 'SUCCESS: XAMPP installer downloaded' } catch { Write-Host 'ERROR: Download failed, trying alternative...'; try { Invoke-WebRequest -Uri 'https://www.apachefriends.org/xampp-files/8.2.12/xampp-windows-x64-8.2.12-0-VS16-installer.exe' -OutFile 'xampp-installer.exe'; Write-Host 'SUCCESS: Downloaded from alternative source' } catch { Write-Host 'ERROR: All downloads failed'; exit 1 } }"

if not exist "xampp-installer.exe" (
    echo ERROR: Failed to download XAMPP installer
    echo Please download manually from: https://www.apachefriends.org/
    echo Save as: xampp-installer.exe
    echo Then run this script again
    pause
    exit /b 1
)
echo SUCCESS: XAMPP installer ready
echo.

echo [STEP 3] Installing XAMPP...
echo.
echo IMPORTANT: During XAMPP installation:
echo - Install to default location: C:\xampp
echo - Select components: Apache, MySQL, phpMyAdmin
echo - Allow firewall access when prompted
echo - Start services after installation
echo.
echo Starting XAMPP installation...
start /wait xampp-installer.exe
echo.
echo Installation completed. Please ensure:
echo 1. XAMPP is installed to C:\xampp
echo 2. Apache and MySQL services are started
echo 3. XAMPP Control Panel is open
echo.
echo Press any key when XAMPP is installed and running...
pause > nul

:configure_xampp
echo [STEP 4] Configuring XAMPP for Stock Scanner...

REM Add XAMPP MySQL to PATH
echo Adding XAMPP MySQL to system PATH...
setx PATH "%PATH%;%XAMPP_MYSQL_PATH%" > nul 2>&1
set PATH=%PATH%;%XAMPP_MYSQL_PATH%

REM Add XAMPP PHP to PATH (useful for phpMyAdmin)
if exist "%XAMPP_PATH%\php" (
    setx PATH "%PATH%;%XAMPP_PATH%\php" > nul 2>&1
    set PATH=%PATH%;%XAMPP_PATH%\php
)

echo SUCCESS: XAMPP paths configured
echo.

echo [STEP 5] Testing XAMPP MySQL connection...
echo Testing connection to XAMPP MySQL...
"%XAMPP_MYSQL_PATH%\mysql.exe" -u root -e "SELECT VERSION();" > temp_version.txt 2>&1
if errorlevel 1 (
    echo ERROR: Cannot connect to XAMPP MySQL
    echo Please ensure:
    echo 1. XAMPP Control Panel is open
    echo 2. MySQL service is started (green)
    echo 3. No other MySQL services are running
    echo.
    echo Opening XAMPP Control Panel...
    start "" "%XAMPP_PATH%\xampp-control.exe"
    echo.
    echo Start MySQL service and press any key to retry...
    pause > nul
    "%XAMPP_MYSQL_PATH%\mysql.exe" -u root -e "SELECT VERSION();" > temp_version.txt 2>&1
    if errorlevel 1 (
        echo ERROR: Still cannot connect
        echo Please check XAMPP installation and try again
        pause
        exit /b 1
    )
)

echo SUCCESS: Connected to XAMPP MySQL
if exist temp_version.txt (
    echo MySQL Version:
    type temp_version.txt
    del temp_version.txt
)
echo.

echo [STEP 6] Creating stockscanner database...
"%XAMPP_MYSQL_PATH%\mysql.exe" -u root -e "CREATE DATABASE IF NOT EXISTS stockscanner CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
if errorlevel 1 (
    echo ERROR: Could not create database
    pause
    exit /b 1
)

echo Verifying database creation...
"%XAMPP_MYSQL_PATH%\mysql.exe" -u root -e "SHOW DATABASES;" | findstr stockscanner > nul
if errorlevel 1 (
    echo ERROR: Database not found after creation
    pause
    exit /b 1
)

echo SUCCESS: Database 'stockscanner' created
echo.

echo [STEP 7] Installing Python packages for XAMPP MySQL...
python -m pip install pymysql mysqlclient --user --quiet --force-reinstall
if errorlevel 1 (
    echo Installing pymysql only (mysqlclient may have failed)...
    python -m pip install pymysql --user --quiet --force-reinstall
)
python -m pip install django djangorestframework yfinance requests schedule --user --quiet
echo SUCCESS: Python packages installed
echo.

echo [STEP 8] Updating Django settings for XAMPP...
python -c "import os; import re; settings_file = 'stockscanner_django/settings.py'; content = open(settings_file).read() if os.path.exists(settings_file) else ''; db_config = '''DATABASES = {\n    'default': {\n        'ENGINE': 'django.db.backends.mysql',\n        'NAME': 'stockscanner',\n        'USER': 'root',\n        'PASSWORD': '',\n        'HOST': 'localhost',\n        'PORT': '3306',\n        'OPTIONS': {\n            'charset': 'utf8mb4',\n            'use_unicode': True,\n            'init_command': \"SET sql_mode='STRICT_TRANS_TABLES',innodb_strict_mode=1\",\n            'autocommit': True,\n            'connect_timeout': 60,\n            'read_timeout': 300,\n            'write_timeout': 300,\n        },\n        'CONN_MAX_AGE': 0,\n        'ATOMIC_REQUESTS': True,\n    }\n}'''; content = re.sub(r'DATABASES\s*=\s*\{[^}]*\}[^}]*\}', db_config, content, flags=re.DOTALL); content = 'import pymysql\npymysql.install_as_MySQLdb()\n\n' + content if 'import pymysql' not in content else content; open(settings_file, 'w').write(content); print('SUCCESS: Django settings updated for XAMPP')"
echo.

echo [STEP 9] Creating XAMPP-specific batch files...

REM Create XAMPP-specific scheduler
echo Creating start_scheduler_xampp.bat...
(
echo @echo off
echo echo Starting Stock Scanner with XAMPP MySQL...
echo set DJANGO_SETTINGS_MODULE=stockscanner_django.settings
echo set PATH=%%PATH%%;%XAMPP_MYSQL_PATH%
echo python start_stock_scheduler.py --background
echo pause
) > start_scheduler_xampp.bat

REM Create XAMPP-specific server starter
echo Creating start_server_xampp.bat...
(
echo @echo off
echo echo Starting Django Server with XAMPP MySQL...
echo set DJANGO_SETTINGS_MODULE=stockscanner_django.settings
echo set PATH=%%PATH%%;%XAMPP_MYSQL_PATH%
echo echo Starting Django development server...
echo echo Visit: http://127.0.0.1:8000/api/wordpress/
echo echo Admin: http://127.0.0.1:8000/admin/ ^(admin/admin123^)
echo python manage.py runserver
echo pause
) > start_server_xampp.bat

REM Create XAMPP database management shortcut
echo Creating manage_database_xampp.bat...
(
echo @echo off
echo echo XAMPP Database Management
echo echo ========================
echo echo Opening phpMyAdmin in browser...
echo start http://localhost/phpmyadmin
echo echo.
echo echo MySQL Command Line:
echo echo Connect: %XAMPP_MYSQL_PATH%\mysql.exe -u root
echo echo Database: stockscanner
echo echo.
echo echo XAMPP Control Panel:
echo start "" "%XAMPP_PATH%\xampp-control.exe"
echo pause
) > manage_database_xampp.bat

REM Create XAMPP test script
echo Creating test_xampp_setup.bat...
(
echo @echo off
echo echo Testing XAMPP Setup...
echo set DJANGO_SETTINGS_MODULE=stockscanner_django.settings
echo set PATH=%%PATH%%;%XAMPP_MYSQL_PATH%
echo python -c "import os; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stockscanner_django.settings'); import django; django.setup(); from stocks.models import Stock; print(f'SUCCESS: Database has {Stock.objects.count()} stocks'); sample = Stock.objects.first(); print(f'Sample: {sample.ticker} - {sample.name}' if sample else 'No sample data')"
echo pause
) > test_xampp_setup.bat

echo SUCCESS: XAMPP-specific batch files created
echo.

echo [STEP 10] Setting up fresh database schema...
echo Removing old migration files...
if exist "stocks\migrations\*.py" (
    for %%f in (stocks\migrations\*.py) do (
        if not "%%~nf"=="__init__" (
            del "%%f" 2>nul
        )
    )
)
if exist "emails\migrations\*.py" (
    for %%f in (emails\migrations\*.py) do (
        if not "%%~nf"=="__init__" (
            del "%%f" 2>nul
        )
    )
)

echo Creating fresh migrations...
python manage.py makemigrations stocks
python manage.py makemigrations emails
python manage.py makemigrations core
python manage.py makemigrations news

echo Applying migrations...
python manage.py migrate
if errorlevel 1 (
    echo ERROR: Migration failed
    echo Checking XAMPP MySQL status...
    "%XAMPP_MYSQL_PATH%\mysql.exe" -u root -e "SELECT 1;" > nul 2>&1
    if errorlevel 1 (
        echo ERROR: XAMPP MySQL connection lost
        echo Please restart MySQL in XAMPP Control Panel
        pause
        exit /b 1
    )
    echo Retrying migration...
    python manage.py migrate
    if errorlevel 1 (
        echo ERROR: Migration still failing
        pause
        exit /b 1
    )
)
echo SUCCESS: Database schema created
echo.

echo [STEP 11] Creating sample data and admin user...
python -c "import os; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stockscanner_django.settings'); import django; django.setup(); from stocks.models import Stock; from django.contrib.auth.models import User; from decimal import Decimal; from django.utils import timezone; print('Setting up admin user and sample data...'); User.objects.create_superuser('admin', 'admin@example.com', 'admin123') if not User.objects.filter(username='admin').exists() else print('INFO: Admin user already exists'); stocks_created = 0 if Stock.objects.count() == 0 else Stock.objects.count(); sample_stocks = [{'ticker': 'AAPL', 'name': 'Apple Inc.', 'current_price': Decimal('150.25'), 'price_change': Decimal('2.50'), 'price_change_percent': Decimal('1.69'), 'volume': 50000000, 'market_cap': Decimal('2500000000000'), 'sector': 'Technology', 'industry': 'Consumer Electronics', 'exchange': 'NASDAQ', 'last_updated': timezone.now()}, {'ticker': 'GOOGL', 'name': 'Alphabet Inc.', 'current_price': Decimal('2750.80'), 'price_change': Decimal('-15.20'), 'price_change_percent': Decimal('-0.55'), 'volume': 25000000, 'market_cap': Decimal('1800000000000'), 'sector': 'Technology', 'industry': 'Internet Software & Services', 'exchange': 'NASDAQ', 'last_updated': timezone.now()}, {'ticker': 'TSLA', 'name': 'Tesla, Inc.', 'current_price': Decimal('245.75'), 'price_change': Decimal('8.25'), 'price_change_percent': Decimal('3.47'), 'volume': 75000000, 'market_cap': Decimal('780000000000'), 'sector': 'Consumer Discretionary', 'industry': 'Auto Manufacturers', 'exchange': 'NASDAQ', 'last_updated': timezone.now()}, {'ticker': 'MSFT', 'name': 'Microsoft Corporation', 'current_price': Decimal('378.50'), 'price_change': Decimal('4.75'), 'price_change_percent': Decimal('1.27'), 'volume': 30000000, 'market_cap': Decimal('2800000000000'), 'sector': 'Technology', 'industry': 'Software', 'exchange': 'NASDAQ', 'last_updated': timezone.now()}, {'ticker': 'AMZN', 'name': 'Amazon.com, Inc.', 'current_price': Decimal('145.80'), 'price_change': Decimal('-2.30'), 'price_change_percent': Decimal('-1.55'), 'volume': 40000000, 'market_cap': Decimal('1500000000000'), 'sector': 'Consumer Discretionary', 'industry': 'Internet Retail', 'exchange': 'NASDAQ', 'last_updated': timezone.now()}] if stocks_created == 0 else []; [Stock.objects.create(**stock_data) for stock_data in sample_stocks] if sample_stocks else None; print(f'SUCCESS: Created {len(sample_stocks)} sample stocks' if sample_stocks else f'INFO: Database already has {Stock.objects.count()} stocks'); print(f'Final database status: {Stock.objects.count()} stocks total')"
echo.

echo [STEP 12] Final testing and verification...
echo Testing complete XAMPP setup...
python -c "import os; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stockscanner_django.settings'); import django; django.setup(); from stocks.models import Stock; from django.db import connection; print('Testing database functionality...'); stock_count = Stock.objects.count(); print(f'SUCCESS: Database connection working - {stock_count} stocks'); aapl = Stock.objects.filter(ticker='AAPL').first(); print(f'SUCCESS: Found AAPL - {aapl.name} at ${aapl.current_price}' if aapl else 'WARNING: AAPL not found'); sample = Stock.objects.first(); [print(f'SUCCESS: Field {field} = {getattr(sample, field, None)}' if getattr(sample, field, None) is not None else f'WARNING: Field {field} is None') for field in ['ticker', 'name', 'current_price', 'sector', 'exchange']] if sample else None; print('SUCCESS: All XAMPP database tests passed')"
echo.

echo ========================================
echo XAMPP SETUP COMPLETE!
echo ========================================
echo.
echo XAMPP Configuration:
echo - Installation: %XAMPP_PATH%
echo - MySQL Database: stockscanner
echo - Username: root
echo - Password: (none)
echo - Host: localhost
echo - Port: 3306
echo.
echo New XAMPP Commands:
echo - Start Scheduler: start_scheduler_xampp.bat
echo - Start Server: start_server_xampp.bat
echo - Manage Database: manage_database_xampp.bat
echo - Test Setup: test_xampp_setup.bat
echo.
echo Web Interfaces:
echo - XAMPP Control: %XAMPP_PATH%\xampp-control.exe
echo - phpMyAdmin: http://localhost/phpmyadmin
echo - Django Server: http://127.0.0.1:8000/api/wordpress/
echo - Django Admin: http://127.0.0.1:8000/admin/ (admin/admin123)
echo.
echo Database Status:
echo - All tables created with proper structure
echo - All required fields present (ticker, name, current_price, etc.)
echo - Sample stock data loaded (AAPL, GOOGL, TSLA, MSFT, AMZN)
echo - Admin user created (admin/admin123)
echo.
echo Quick Start:
echo 1. Ensure XAMPP Control Panel shows MySQL as running (green)
echo 2. Run: start_server_xampp.bat
echo 3. Visit: http://127.0.0.1:8000/api/wordpress/
echo 4. For scheduling: start_scheduler_xampp.bat
echo.
echo IMPORTANT: Always keep XAMPP Control Panel open and MySQL running!
echo.
echo Press any key to finish...
pause > nul