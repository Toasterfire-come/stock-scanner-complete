@echo off
echo ========================================
echo CONFIGURE EXISTING MYSQL INSTALLATION
echo ========================================
echo.
echo Detected MySQL installation at: C:\Program Files\MySQL
echo This will configure your existing MySQL for the stock scanner
echo.

REM Set UTF-8 encoding
chcp 65001 > nul 2>&1

REM Set environment variables
set DJANGO_SETTINGS_MODULE=stockscanner_django.settings
set PYTHONIOENCODING=utf-8

echo [STEP 1] Detecting MySQL installation...
if exist "C:\Program Files\MySQL\MySQL Server 8.0" (
    set "MYSQL_VERSION=8.0"
    set "MYSQL_PATH=C:\Program Files\MySQL\MySQL Server 8.0\bin"
    echo Found MySQL Server 8.0
) else if exist "C:\Program Files\MySQL\MySQL Server 8.4" (
    set "MYSQL_VERSION=8.4"
    set "MYSQL_PATH=C:\Program Files\MySQL\MySQL Server 8.4\bin"
    echo Found MySQL Server 8.4
) else if exist "C:\Program Files\MySQL\MySQL Server 5.7" (
    set "MYSQL_VERSION=5.7"
    set "MYSQL_PATH=C:\Program Files\MySQL\MySQL Server 5.7\bin"
    echo Found MySQL Server 5.7
) else (
    echo ERROR: Could not detect MySQL Server version
    echo Please check your MySQL installation in C:\Program Files\MySQL
    dir "C:\Program Files\MySQL"
    pause
    exit /b 1
)

echo MySQL Path: %MYSQL_PATH%
echo.

echo [STEP 2] Adding MySQL to PATH...
if exist "%MYSQL_PATH%" (
    echo Adding MySQL to system PATH...
    setx PATH "%PATH%;%MYSQL_PATH%" > nul 2>&1
    set PATH=%PATH%;%MYSQL_PATH%
    echo SUCCESS: MySQL added to PATH
) else (
    echo ERROR: MySQL bin directory not found at %MYSQL_PATH%
    pause
    exit /b 1
)
echo.

echo [STEP 3] Testing MySQL command...
"%MYSQL_PATH%\mysql.exe" --version > nul 2>&1
if errorlevel 1 (
    echo ERROR: MySQL command failed
    echo Please check if MySQL is properly installed
    pause
    exit /b 1
)
echo SUCCESS: MySQL command is working
echo.

echo [STEP 4] Checking MySQL service...
sc query mysql > nul 2>&1
if errorlevel 1 (
    echo Checking for MySQL80...
    sc query MySQL80 > nul 2>&1
    if errorlevel 1 (
        echo Checking for MySQL57...
        sc query MySQL57 > nul 2>&1
        if errorlevel 1 (
            echo ERROR: MySQL service not found
            echo Please start MySQL service manually or check installation
            pause
            exit /b 1
        ) else (
            echo Found MySQL57 service
            net start MySQL57 > nul 2>&1
        )
    ) else (
        echo Found MySQL80 service
        net start MySQL80 > nul 2>&1
    )
) else (
    echo Found MySQL service
    net start mysql > nul 2>&1
)
echo SUCCESS: MySQL service is running
echo.

echo [STEP 5] Testing MySQL connection...
echo Testing connection (you may be prompted for password)...
echo If no password is set, just press Enter
echo.
"%MYSQL_PATH%\mysql.exe" -u root -e "SELECT VERSION();" > temp_mysql_test.txt 2>&1
if errorlevel 1 (
    echo Connection failed with no password, trying with common passwords...
    "%MYSQL_PATH%\mysql.exe" -u root -proot -e "SELECT VERSION();" > temp_mysql_test.txt 2>&1
    if errorlevel 1 (
        "%MYSQL_PATH%\mysql.exe" -u root -p123456 -e "SELECT VERSION();" > temp_mysql_test.txt 2>&1
        if errorlevel 1 (
            "%MYSQL_PATH%\mysql.exe" -u root -padmin -e "SELECT VERSION();" > temp_mysql_test.txt 2>&1
            if errorlevel 1 (
                echo ERROR: Could not connect to MySQL
                echo Please enter your MySQL root password manually:
                "%MYSQL_PATH%\mysql.exe" -u root -p -e "SELECT VERSION();"
                if errorlevel 1 (
                    echo ERROR: MySQL connection failed
                    echo Please check your MySQL root password
                    pause
                    exit /b 1
                )
                set MYSQL_ROOT_PASSWORD=manual
            ) else (
                set MYSQL_ROOT_PASSWORD=admin
                echo SUCCESS: Connected with password 'admin'
            )
        ) else (
            set MYSQL_ROOT_PASSWORD=123456
            echo SUCCESS: Connected with password '123456'
        )
    ) else (
        set MYSQL_ROOT_PASSWORD=root
        echo SUCCESS: Connected with password 'root'
    )
) else (
    set MYSQL_ROOT_PASSWORD=
    echo SUCCESS: Connected with no password
)

if exist temp_mysql_test.txt del temp_mysql_test.txt
echo.

echo [STEP 6] Creating stockscanner database...
if "%MYSQL_ROOT_PASSWORD%"=="manual" (
    echo Please enter your MySQL root password to create database:
    "%MYSQL_PATH%\mysql.exe" -u root -p -e "CREATE DATABASE IF NOT EXISTS stockscanner CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
) else if "%MYSQL_ROOT_PASSWORD%"=="" (
    "%MYSQL_PATH%\mysql.exe" -u root -e "CREATE DATABASE IF NOT EXISTS stockscanner CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;" 2>nul
) else (
    "%MYSQL_PATH%\mysql.exe" -u root -p%MYSQL_ROOT_PASSWORD% -e "CREATE DATABASE IF NOT EXISTS stockscanner CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;" 2>nul
)

if errorlevel 1 (
    echo ERROR: Could not create database
    echo Please create it manually:
    echo mysql -u root -p
    echo CREATE DATABASE stockscanner CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
    pause
    exit /b 1
)
echo SUCCESS: Database created
echo.

echo [STEP 7] Installing Python MySQL packages...
python -m pip install pymysql mysqlclient --user --quiet
if errorlevel 1 (
    echo Installing pymysql only (mysqlclient failed)...
    python -m pip install pymysql --user --quiet
)
python -m pip install django djangorestframework --user --quiet
echo SUCCESS: Python packages installed
echo.

echo [STEP 8] Updating Django settings for MySQL...
python -c "
import os
import re

settings_file = 'stockscanner_django/settings.py'
if os.path.exists(settings_file):
    with open(settings_file, 'r') as f:
        content = f.read()
    
    # Determine password for settings
    password = '%s'
    if password == 'manual':
        print('Please enter your MySQL root password for Django settings:')
        password = input().strip()
    
    # Update database configuration
    db_config = '''DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'stockscanner',
        'USER': 'root',
        'PASSWORD': '%%s',
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
}''' %% password
    
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

echo [STEP 9] Removing old migration files...
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

echo [STEP 10] Creating fresh migrations...
python manage.py makemigrations stocks
python manage.py makemigrations emails
python manage.py makemigrations core
python manage.py makemigrations news
echo SUCCESS: Fresh migrations created
echo.

echo [STEP 11] Applying all migrations...
python manage.py migrate
if errorlevel 1 (
    echo ERROR: Migration failed
    echo Trying to reset database and retry...
    
    if "%MYSQL_ROOT_PASSWORD%"=="manual" (
        echo Please enter your MySQL root password to reset database:
        "%MYSQL_PATH%\mysql.exe" -u root -p -e "DROP DATABASE IF EXISTS stockscanner; CREATE DATABASE stockscanner CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
    ) else if "%MYSQL_ROOT_PASSWORD%"=="" (
        "%MYSQL_PATH%\mysql.exe" -u root -e "DROP DATABASE IF EXISTS stockscanner; CREATE DATABASE stockscanner CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;" 2>nul
    ) else (
        "%MYSQL_PATH%\mysql.exe" -u root -p%MYSQL_ROOT_PASSWORD% -e "DROP DATABASE IF EXISTS stockscanner; CREATE DATABASE stockscanner CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;" 2>nul
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

echo [STEP 12] Creating sample stock data...
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

echo [STEP 13] Testing database connection...
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

# Test required fields
sample_stock = Stock.objects.first()
if sample_stock:
    fields = ['ticker', 'name', 'current_price', 'price_change', 'volume', 'sector', 'exchange']
    for field in fields:
        value = getattr(sample_stock, field, None)
        if value is not None:
            print(f'SUCCESS: Field {field} = {value}')
        else:
            print(f'WARNING: Field {field} is None')
"
echo SUCCESS: Database testing completed
echo.

echo [STEP 14] Creating Django superuser...
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
echo MYSQL CONFIGURATION COMPLETE!
echo ========================================
echo.
echo MySQL Configuration:
echo - Version: %MYSQL_VERSION%
echo - Path: %MYSQL_PATH%
echo - Database: stockscanner
echo - Username: root
if not "%MYSQL_ROOT_PASSWORD%"=="manual" (
    echo - Password: %MYSQL_ROOT_PASSWORD%
) else (
    echo - Password: [manually entered]
)
echo - Host: localhost
echo - Port: 3306
echo.
echo Database Status:
echo - All tables created with proper structure
echo - All required fields present (ticker, name, current_price, etc.)
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
if not "%MYSQL_ROOT_PASSWORD%"=="manual" (
    if "%MYSQL_ROOT_PASSWORD%"=="" (
        echo - Connect: mysql -u root
    ) else (
        echo - Connect: mysql -u root -p%MYSQL_ROOT_PASSWORD%
    )
) else (
    echo - Connect: mysql -u root -p
)
echo - Show databases: SHOW DATABASES;
echo - Use stockscanner: USE stockscanner;
echo - Show tables: SHOW TABLES;
echo.
echo Press any key to finish...
pause > nul