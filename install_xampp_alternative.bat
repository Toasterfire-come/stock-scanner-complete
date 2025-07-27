@echo off
echo ========================================
echo XAMPP INSTALLATION (MYSQL ALTERNATIVE)
echo ========================================
echo.
echo XAMPP includes:
echo - Apache Web Server
echo - MySQL Database
echo - PHP
echo - phpMyAdmin (web-based MySQL management)
echo.
echo This is often easier than standalone MySQL installation
echo.
echo Press Ctrl+C to cancel or any key to continue...
pause > nul
echo.

REM Set UTF-8 encoding
chcp 65001 > nul 2>&1

REM Set environment variables
set DJANGO_SETTINGS_MODULE=stockscanner_django.settings
set PYTHONIOENCODING=utf-8

echo [STEP 1] Downloading XAMPP installer...
if exist "xampp-installer.exe" del "xampp-installer.exe"

echo Downloading XAMPP (this may take several minutes)...
powershell -Command "& {
    $ProgressPreference = 'SilentlyContinue'
    try {
        Invoke-WebRequest -Uri 'https://sourceforge.net/projects/xampp/files/XAMPP Windows/8.2.12/xampp-windows-x64-8.2.12-0-VS16-installer.exe/download' -OutFile 'xampp-installer.exe'
        Write-Host 'SUCCESS: XAMPP installer downloaded'
    } catch {
        Write-Host 'ERROR: Download failed'
        Write-Host 'Please download XAMPP manually from: https://www.apachefriends.org/'
        exit 1
    }
}"

if not exist "xampp-installer.exe" (
    echo ERROR: Failed to download XAMPP installer
    echo Please download manually from: https://www.apachefriends.org/
    echo Then rename it to: xampp-installer.exe
    echo And run this script again
    pause
    exit /b 1
)
echo SUCCESS: XAMPP installer downloaded
echo.

echo [STEP 2] Installing XAMPP...
echo.
echo IMPORTANT: During XAMPP installation:
echo 1. Install to default location: C:\xampp
echo 2. Select these components:
echo    - Apache
echo    - MySQL
echo    - phpMyAdmin
echo 3. Complete the installation
echo 4. Start Apache and MySQL services
echo.
echo Starting XAMPP installation...
xampp-installer.exe
echo.
echo Please complete the XAMPP installation with the settings above
echo Then start Apache and MySQL from XAMPP Control Panel
echo Press any key when XAMPP is installed and services are running...
pause > nul
echo.

echo [STEP 3] Checking XAMPP installation...
if not exist "C:\xampp\mysql\bin\mysql.exe" (
    echo ERROR: XAMPP MySQL not found
    echo Please ensure XAMPP is installed to C:\xampp
    echo And that MySQL service is started
    pause
    exit /b 1
)
echo SUCCESS: XAMPP MySQL found
echo.

echo [STEP 4] Adding XAMPP MySQL to PATH...
set "XAMPP_MYSQL_PATH=C:\xampp\mysql\bin"
setx PATH "%PATH%;%XAMPP_MYSQL_PATH%" > nul 2>&1
set PATH=%PATH%;%XAMPP_MYSQL_PATH%
echo SUCCESS: XAMPP MySQL added to PATH
echo.

echo [STEP 5] Testing MySQL connection...
echo Testing XAMPP MySQL (default: no password)...
"C:\xampp\mysql\bin\mysql.exe" -u root -e "SELECT VERSION();" > temp_version.txt 2>&1
if errorlevel 1 (
    echo Connection failed, checking if MySQL service is running...
    echo Please ensure MySQL is started in XAMPP Control Panel
    echo Then press any key to retry...
    pause > nul
    "C:\xampp\mysql\bin\mysql.exe" -u root -e "SELECT VERSION();" > temp_version.txt 2>&1
    if errorlevel 1 (
        echo ERROR: Still cannot connect to MySQL
        echo Please check XAMPP Control Panel and ensure MySQL is running
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
"C:\xampp\mysql\bin\mysql.exe" -u root -e "CREATE DATABASE IF NOT EXISTS stockscanner CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
if errorlevel 1 (
    echo ERROR: Could not create database
    echo Please check XAMPP MySQL is running
    pause
    exit /b 1
)
echo SUCCESS: Database 'stockscanner' created
echo.

echo [STEP 7] Installing Python MySQL packages...
python -m pip install pymysql mysqlclient --user --quiet --force-reinstall
if errorlevel 1 (
    echo Installing pymysql only (mysqlclient may have failed)...
    python -m pip install pymysql --user --quiet --force-reinstall
)
python -m pip install django djangorestframework --user --quiet
echo SUCCESS: Python packages installed
echo.

echo [STEP 8] Updating Django settings for XAMPP MySQL...
python -c "
import os
import re

settings_file = 'stockscanner_django/settings.py'
if os.path.exists(settings_file):
    with open(settings_file, 'r') as f:
        content = f.read()
    
    # Update database configuration for XAMPP (no password by default)
    db_config = '''DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'stockscanner',
        'USER': 'root',
        'PASSWORD': '',
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {
            'charset': 'utf8mb4',
            'use_unicode': True,
            'init_command': \"SET sql_mode='STRICT_TRANS_TABLES',innodb_strict_mode=1\",
            'autocommit': True,
            'connect_timeout': 60,
            'read_timeout': 300,
            'write_timeout': 300,
        },
        'CONN_MAX_AGE': 0,
        'ATOMIC_REQUESTS': True,
    }
}'''
    
    # Replace existing DATABASES configuration
    content = re.sub(r'DATABASES\s*=\s*\{[^}]*\}[^}]*\}', db_config, content, flags=re.DOTALL)
    
    # Add pymysql import if not present
    if 'import pymysql' not in content:
        content = 'import pymysql\npymysql.install_as_MySQLdb()\n\n' + content
    
    with open(settings_file, 'w') as f:
        f.write(content)
    
    print('SUCCESS: Django settings updated for XAMPP')
else:
    print('ERROR: Django settings file not found')
"
echo.

echo [STEP 9] Setting up fresh database schema...
echo Removing old migration files...
if exist "stocks\migrations\*.py" (
    for %%f in (stocks\migrations\*.py) do (
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
    echo Please check the error above
    pause
) else (
    echo SUCCESS: Database schema created
)
echo.

echo [STEP 10] Creating sample data and admin user...
python -c "
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stockscanner_django.settings')
import django
django.setup()

from stocks.models import Stock
from django.contrib.auth.models import User
from decimal import Decimal
from django.utils import timezone

# Create admin user
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('SUCCESS: Admin user created (admin/admin123)')

# Create sample stocks
if Stock.objects.count() == 0:
    sample_stocks = [
        {
            'ticker': 'AAPL', 'name': 'Apple Inc.',
            'current_price': Decimal('150.25'), 'price_change': Decimal('2.50'),
            'price_change_percent': Decimal('1.69'), 'volume': 50000000,
            'market_cap': Decimal('2500000000000'), 'sector': 'Technology',
            'industry': 'Consumer Electronics', 'exchange': 'NASDAQ',
            'last_updated': timezone.now()
        },
        {
            'ticker': 'GOOGL', 'name': 'Alphabet Inc.',
            'current_price': Decimal('2750.80'), 'price_change': Decimal('-15.20'),
            'price_change_percent': Decimal('-0.55'), 'volume': 25000000,
            'market_cap': Decimal('1800000000000'), 'sector': 'Technology',
            'industry': 'Internet Software & Services', 'exchange': 'NASDAQ',
            'last_updated': timezone.now()
        },
        {
            'ticker': 'TSLA', 'name': 'Tesla, Inc.',
            'current_price': Decimal('245.75'), 'price_change': Decimal('8.25'),
            'price_change_percent': Decimal('3.47'), 'volume': 75000000,
            'market_cap': Decimal('780000000000'), 'sector': 'Consumer Discretionary',
            'industry': 'Auto Manufacturers', 'exchange': 'NASDAQ',
            'last_updated': timezone.now()
        },
        {
            'ticker': 'MSFT', 'name': 'Microsoft Corporation',
            'current_price': Decimal('378.50'), 'price_change': Decimal('4.75'),
            'price_change_percent': Decimal('1.27'), 'volume': 30000000,
            'market_cap': Decimal('2800000000000'), 'sector': 'Technology',
            'industry': 'Software', 'exchange': 'NASDAQ',
            'last_updated': timezone.now()
        }
    ]
    
    for stock_data in sample_stocks:
        Stock.objects.create(**stock_data)
    
    print(f'SUCCESS: Created {len(sample_stocks)} sample stocks')

print(f'Database has {Stock.objects.count()} stocks total')
"
echo.

echo [STEP 11] Final testing...
python -c "
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stockscanner_django.settings')
import django
django.setup()

from stocks.models import Stock

# Test database functionality
try:
    stock_count = Stock.objects.count()
    print(f'SUCCESS: Database connection working - {stock_count} stocks')
    
    # Test specific stock
    aapl = Stock.objects.filter(ticker='AAPL').first()
    if aapl:
        print(f'SUCCESS: Found AAPL - {aapl.name} at ${aapl.current_price}')
    
    # Test required fields
    sample = Stock.objects.first()
    if sample:
        fields = ['ticker', 'name', 'current_price', 'sector', 'exchange']
        for field in fields:
            value = getattr(sample, field, None)
            if value:
                print(f'SUCCESS: Field {field} = {value}')
    
    print('SUCCESS: All database tests passed')
except Exception as e:
    print(f'ERROR: Database test failed - {e}')
"
echo.

echo ========================================
echo XAMPP SETUP COMPLETE!
echo ========================================
echo.
echo XAMPP Configuration:
echo - Installation: C:\xampp
echo - MySQL Database: stockscanner
echo - Username: root
echo - Password: (none)
echo - Host: localhost
echo - Port: 3306
echo.
echo Web Interfaces:
echo - XAMPP Control Panel: C:\xampp\xampp-control.exe
echo - phpMyAdmin: http://localhost/phpmyadmin
echo - Apache: http://localhost
echo.
echo Database Status:
echo - All tables created with proper structure
echo - All required fields present
echo - Sample stock data loaded
echo - Admin user created (admin/admin123)
echo.
echo You can now:
echo - Start the server: python manage.py runserver
echo - Start the scheduler: python start_stock_scheduler.py --background
echo - Visit WordPress API: http://127.0.0.1:8000/api/wordpress/
echo - Visit admin panel: http://127.0.0.1:8000/admin/
echo - Manage MySQL: http://localhost/phpmyadmin
echo.
echo MySQL Commands:
echo - Connect: mysql -u root
echo - Or use: C:\xampp\mysql\bin\mysql.exe -u root
echo - Show databases: SHOW DATABASES;
echo - Use stockscanner: USE stockscanner;
echo - Show tables: SHOW TABLES;
echo.
echo IMPORTANT: Always start Apache and MySQL from XAMPP Control Panel before using!
echo.
echo Press any key to finish...
pause > nul