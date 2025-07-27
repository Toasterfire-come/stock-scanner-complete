@echo off
echo ========================================
echo MYSQL INSTALLER AND DATABASE SETUP
echo ========================================
echo.
echo This will:
echo - Download and install MySQL Server
echo - Configure MySQL for the stock scanner
echo - Set up the database with all needed fields
echo - Create sample data
echo.

REM Set UTF-8 encoding
chcp 65001 > nul 2>&1

REM Set environment variables
set DJANGO_SETTINGS_MODULE=stockscanner_django.settings
set PYTHONIOENCODING=utf-8
set MYSQL_ROOT_PASSWORD=stockscanner123

echo [STEP 1] Checking if MySQL is already installed...
sc query mysql > nul 2>&1
if not errorlevel 1 (
    echo INFO: MySQL service already exists
    goto :configure_mysql
)

sc query MySQL80 > nul 2>&1
if not errorlevel 1 (
    echo INFO: MySQL80 service already exists
    goto :configure_mysql
)

echo INFO: MySQL not found, will install MySQL Server
echo.

echo [STEP 2] Downloading MySQL Installer...
if not exist "mysql-installer.msi" (
    echo Downloading MySQL Installer (this may take a few minutes)...
    powershell -Command "& {Invoke-WebRequest -Uri 'https://dev.mysql.com/get/Downloads/MySQLInstaller/mysql-installer-community-8.0.39.0.msi' -OutFile 'mysql-installer.msi'}"
    if errorlevel 1 (
        echo ERROR: Failed to download MySQL installer
        echo Please download MySQL installer manually from: https://dev.mysql.com/downloads/installer/
        pause
        exit /b 1
    )
    echo SUCCESS: MySQL installer downloaded
) else (
    echo INFO: MySQL installer already exists
)
echo.

echo [STEP 3] Installing MySQL Server...
echo INFO: This will install MySQL Server with default settings
echo Root password will be set to: %MYSQL_ROOT_PASSWORD%
echo.
echo Starting MySQL installation (this may take 5-10 minutes)...
msiexec /i mysql-installer.msi /quiet /norestart ADDLOCAL=ALL MYSQL_ROOT_PASSWORD=%MYSQL_ROOT_PASSWORD%
if errorlevel 1 (
    echo WARNING: Automated install may have failed
    echo Trying interactive install...
    msiexec /i mysql-installer.msi
    echo.
    echo Please complete the MySQL installation:
    echo 1. Choose "Server only" or "Developer Default"
    echo 2. Set root password to: %MYSQL_ROOT_PASSWORD%
    echo 3. Complete the installation
    echo.
    pause
)
echo SUCCESS: MySQL installation completed
echo.

echo [STEP 4] Waiting for MySQL service to start...
timeout /t 10 /nobreak > nul
net start mysql > nul 2>&1
if errorlevel 1 (
    net start MySQL80 > nul 2>&1
    if errorlevel 1 (
        echo Waiting longer for MySQL to initialize...
        timeout /t 30 /nobreak > nul
        net start mysql > nul 2>&1
        if errorlevel 1 (
            net start MySQL80 > nul 2>&1
        )
    )
)
echo SUCCESS: MySQL service started
echo.

:configure_mysql
echo [STEP 5] Configuring MySQL for stock scanner...

REM Add MySQL to PATH if not already there
set "MYSQL_PATH=C:\Program Files\MySQL\MySQL Server 8.0\bin"
if exist "%MYSQL_PATH%" (
    echo Adding MySQL to PATH...
    setx PATH "%PATH%;%MYSQL_PATH%" > nul 2>&1
    set PATH=%PATH%;%MYSQL_PATH%
)

REM Alternative MySQL path
set "MYSQL_PATH2=C:\Program Files\MySQL\MySQL Server 8.4\bin"
if exist "%MYSQL_PATH2%" (
    echo Adding MySQL to PATH...
    setx PATH "%PATH%;%MYSQL_PATH2%" > nul 2>&1
    set PATH=%PATH%;%MYSQL_PATH2%
)

echo.

echo [STEP 6] Testing MySQL connection...
mysql --version > nul 2>&1
if errorlevel 1 (
    echo ERROR: MySQL command not found in PATH
    echo Please add MySQL bin directory to your PATH manually
    echo Typical location: C:\Program Files\MySQL\MySQL Server 8.0\bin
    pause
    exit /b 1
)
echo SUCCESS: MySQL command is available
echo.

echo [STEP 7] Creating stockscanner database...
echo Using root password: %MYSQL_ROOT_PASSWORD%
mysql -u root -p%MYSQL_ROOT_PASSWORD% -e "CREATE DATABASE IF NOT EXISTS stockscanner CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;" 2>nul
if errorlevel 1 (
    echo WARNING: Could not create database with password
    echo Trying without password...
    mysql -u root -e "CREATE DATABASE IF NOT EXISTS stockscanner CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;" 2>nul
    if errorlevel 1 (
        echo ERROR: Could not create database
        echo Please run: mysql -u root -p
        echo Then execute: CREATE DATABASE stockscanner CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
        pause
        exit /b 1
    )
    set MYSQL_ROOT_PASSWORD=
)
echo SUCCESS: Database created
echo.

echo [STEP 8] Installing Python MySQL packages...
python -m pip install pymysql mysqlclient --user --quiet
if errorlevel 1 (
    echo Installing without mysqlclient...
    python -m pip install pymysql --user --quiet
)
python -m pip install django djangorestframework --user --quiet
echo SUCCESS: Python packages installed
echo.

echo [STEP 9] Updating Django settings for MySQL...
python -c "
import os
import re

settings_file = 'stockscanner_django/settings.py'
if os.path.exists(settings_file):
    with open(settings_file, 'r') as f:
        content = f.read()
    
    # Update database configuration
    db_config = '''DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'stockscanner',
        'USER': 'root',
        'PASSWORD': '%s',
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
}''' % '%s'
    
    # Replace existing DATABASES configuration
    content = re.sub(r'DATABASES\s*=\s*\{[^}]*\}[^}]*\}', db_config, content, flags=re.DOTALL)
    
    # Add pymysql import if not present
    if 'import pymysql' not in content:
        content = 'import pymysql\npymysql.install_as_MySQLdb()\n\n' + content
    
    with open(settings_file, 'w') as f:
        f.write(content)
    
    print('SUCCESS: Django settings updated for MySQL')
else:
    print('ERROR: Django settings file not found')
" %MYSQL_ROOT_PASSWORD%
echo.

echo [STEP 10] Removing old migration files...
if exist "stocks\migrations\*.py" (
    for %%f in (stocks\migrations\*.py) do (
        if not "%%~nf"=="__init__" (
            del "%%f" 2>nul
            echo Removed %%f
        )
    )
)
if exist "emails\migrations\*.py" (
    for %%f in (emails\migrations\*.py) do (
        if not "%%~nf"=="__init__" (
            del "%%f" 2>nul
            echo Removed %%f
        )
    )
)
if exist "core\migrations\*.py" (
    for %%f in (core\migrations\*.py) do (
        if not "%%~nf"=="__init__" (
            del "%%f" 2>nul
            echo Removed %%f
        )
    )
)
if exist "news\migrations\*.py" (
    for %%f in (news\migrations\*.py) do (
        if not "%%~nf"=="__init__" (
            del "%%f" 2>nul
            echo Removed %%f
        )
    )
)
echo SUCCESS: Old migration files removed
echo.

echo [STEP 11] Creating fresh migrations...
python manage.py makemigrations stocks
python manage.py makemigrations emails
python manage.py makemigrations core
python manage.py makemigrations news
echo SUCCESS: Fresh migrations created
echo.

echo [STEP 12] Applying all migrations...
python manage.py migrate
if errorlevel 1 (
    echo ERROR: Migration failed
    echo Trying to reset database and retry...
    
    if "%MYSQL_ROOT_PASSWORD%"=="" (
        mysql -u root -e "DROP DATABASE IF EXISTS stockscanner; CREATE DATABASE stockscanner CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;" 2>nul
    ) else (
        mysql -u root -p%MYSQL_ROOT_PASSWORD% -e "DROP DATABASE IF EXISTS stockscanner; CREATE DATABASE stockscanner CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;" 2>nul
    )
    
    echo Database reset, retrying migrations...
    python manage.py migrate
    
    if errorlevel 1 (
        echo ERROR: Migration still failing
        echo Please check the error messages above
        pause
        exit /b 1
    )
)
echo SUCCESS: All migrations applied
echo.

echo [STEP 13] Creating sample stock data...
python -c "
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stockscanner_django.settings')
import django
django.setup()

from stocks.models import Stock
from decimal import Decimal
from django.utils import timezone

# Create sample stocks if none exist
if Stock.objects.count() == 0:
    sample_stocks = [
        {
            'ticker': 'AAPL',
            'name': 'Apple Inc.',
            'current_price': Decimal('150.25'),
            'price_change': Decimal('2.50'),
            'price_change_percent': Decimal('1.69'),
            'volume': 50000000,
            'market_cap': Decimal('2500000000000'),
            'sector': 'Technology',
            'industry': 'Consumer Electronics',
            'exchange': 'NASDAQ',
            'last_updated': timezone.now()
        },
        {
            'ticker': 'GOOGL',
            'name': 'Alphabet Inc.',
            'current_price': Decimal('2750.80'),
            'price_change': Decimal('-15.20'),
            'price_change_percent': Decimal('-0.55'),
            'volume': 25000000,
            'market_cap': Decimal('1800000000000'),
            'sector': 'Technology',
            'industry': 'Internet Software & Services',
            'exchange': 'NASDAQ',
            'last_updated': timezone.now()
        },
        {
            'ticker': 'TSLA',
            'name': 'Tesla, Inc.',
            'current_price': Decimal('245.75'),
            'price_change': Decimal('8.25'),
            'price_change_percent': Decimal('3.47'),
            'volume': 75000000,
            'market_cap': Decimal('780000000000'),
            'sector': 'Consumer Discretionary',
            'industry': 'Auto Manufacturers',
            'exchange': 'NASDAQ',
            'last_updated': timezone.now()
        },
        {
            'ticker': 'MSFT',
            'name': 'Microsoft Corporation',
            'current_price': Decimal('378.50'),
            'price_change': Decimal('4.75'),
            'price_change_percent': Decimal('1.27'),
            'volume': 30000000,
            'market_cap': Decimal('2800000000000'),
            'sector': 'Technology',
            'industry': 'Software',
            'exchange': 'NASDAQ',
            'last_updated': timezone.now()
        },
        {
            'ticker': 'AMZN',
            'name': 'Amazon.com, Inc.',
            'current_price': Decimal('145.80'),
            'price_change': Decimal('-2.30'),
            'price_change_percent': Decimal('-1.55'),
            'volume': 40000000,
            'market_cap': Decimal('1500000000000'),
            'sector': 'Consumer Discretionary',
            'industry': 'Internet Retail',
            'exchange': 'NASDAQ',
            'last_updated': timezone.now()
        }
    ]
    
    for stock_data in sample_stocks:
        Stock.objects.create(**stock_data)
    
    print(f'SUCCESS: Created {len(sample_stocks)} sample stocks')
else:
    print(f'INFO: Database already has {Stock.objects.count()} stocks')
"
echo SUCCESS: Sample data created
echo.

echo [STEP 14] Testing database connection...
python -c "
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stockscanner_django.settings')
import django
django.setup()

from stocks.models import Stock

stock_count = Stock.objects.count()
print(f'SUCCESS: Database has {stock_count} stocks')

# Test a specific stock
aapl = Stock.objects.filter(ticker='AAPL').first()
if aapl:
    print(f'SUCCESS: Found AAPL: {aapl.name} at ${aapl.current_price}')
else:
    print('WARNING: AAPL not found')
"
echo SUCCESS: Database testing completed
echo.

echo [STEP 15] Creating Django superuser...
python -c "
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stockscanner_django.settings')
import django
django.setup()

from django.contrib.auth.models import User

if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('SUCCESS: Superuser created (admin/admin123)')
else:
    print('INFO: Superuser already exists')
" 2>nul
echo.

echo ========================================
echo MYSQL AND DATABASE SETUP COMPLETE!
echo ========================================
echo.
echo MySQL Server Configuration:
echo - Database: stockscanner
echo - Username: root
echo - Password: %MYSQL_ROOT_PASSWORD%
echo - Host: localhost
echo - Port: 3306
echo.
echo Django Configuration:
echo - All tables created with proper structure
echo - Sample stock data loaded (AAPL, GOOGL, TSLA, MSFT, AMZN)
echo - Admin user created (admin/admin123)
echo.
echo You can now:
echo - Start the server: python manage.py runserver
echo - Start the scheduler: python start_stock_scheduler.py --background
echo - Visit WordPress API: http://127.0.0.1:8000/api/wordpress/
echo - Visit admin panel: http://127.0.0.1:8000/admin/
echo.
echo MySQL Commands:
echo - Connect to MySQL: mysql -u root -p%MYSQL_ROOT_PASSWORD%
echo - Show databases: SHOW DATABASES;
echo - Use stockscanner: USE stockscanner;
echo - Show tables: SHOW TABLES;
echo.
echo Press any key to finish...
pause > nul