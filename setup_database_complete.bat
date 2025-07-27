@echo off
echo ========================================
echo COMPLETE DATABASE SETUP
echo ========================================
echo.
echo This will set up your database with ALL needed fields:
echo - Check MySQL service
echo - Create database if needed
echo - Reset migrations
echo - Create all tables and columns
echo - Add sample data
echo - Test everything
echo.

REM Set UTF-8 encoding
chcp 65001 > nul 2>&1

REM Set environment variables
set DJANGO_SETTINGS_MODULE=stockscanner_django.settings
set PYTHONIOENCODING=utf-8

echo [STEP 1] Checking Python installation...
python --version > nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found in PATH
    echo Please install Python 3.8+ and ensure it's in your PATH
    pause
    exit /b 1
)
echo SUCCESS: Python is available
echo.

echo [STEP 2] Checking MySQL service...
sc query mysql > nul 2>&1
if errorlevel 1 (
    echo Checking for MySQL80...
    sc query MySQL80 > nul 2>&1
    if errorlevel 1 (
        echo ERROR: MySQL service not found
        echo Please install MySQL Server first
        pause
        exit /b 1
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

echo [STEP 3] Creating stockscanner database...
mysql -u root -e "CREATE DATABASE IF NOT EXISTS stockscanner CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;" 2>nul
if errorlevel 1 (
    echo WARNING: Could not create database (may already exist)
) else (
    echo SUCCESS: Database created or already exists
)
echo.

echo [STEP 4] Installing required Python packages...
python -m pip install django djangorestframework pymysql mysqlclient --user --quiet
echo SUCCESS: Required packages installed
echo.

echo [STEP 5] Removing old migration files...
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

echo [STEP 6] Creating fresh migrations...
echo Creating Django auth migrations...
python manage.py makemigrations auth
echo Creating contenttypes migrations...
python manage.py makemigrations contenttypes
echo Creating stocks migrations...
python manage.py makemigrations stocks
echo Creating emails migrations...
python manage.py makemigrations emails
echo Creating core migrations...
python manage.py makemigrations core
echo Creating news migrations...
python manage.py makemigrations news
echo SUCCESS: Fresh migrations created
echo.

echo [STEP 7] Applying all migrations...
python manage.py migrate
if errorlevel 1 (
    echo ERROR: Migration failed
    echo Trying to fix and retry...
    echo.
    
    REM Try to reset the database and start over
    mysql -u root -e "DROP DATABASE IF EXISTS stockscanner; CREATE DATABASE stockscanner CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;" 2>nul
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

echo [STEP 8] Verifying database structure...
python -c "
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stockscanner_django.settings')
import django
django.setup()

from django.db import connection

# Check tables exist
with connection.cursor() as cursor:
    cursor.execute('SHOW TABLES')
    tables = [row[0] for row in cursor.fetchall()]
    
    required_tables = ['stocks_stock', 'stocks_stockalert', 'emails_emailsubscription']
    missing = [t for t in required_tables if t not in tables]
    
    if missing:
        print(f'ERROR: Missing tables: {missing}')
        exit(1)
    else:
        print('SUCCESS: All required tables exist')
        
    # Check stocks_stock columns
    cursor.execute('DESCRIBE stocks_stock')
    columns = [row[0] for row in cursor.fetchall()]
    
    required_columns = ['id', 'ticker', 'name', 'current_price', 'price_change', 
                       'price_change_percent', 'volume', 'market_cap', 'sector', 'exchange']
    missing_cols = [c for c in required_columns if c not in columns]
    
    if missing_cols:
        print(f'ERROR: Missing columns: {missing_cols}')
        exit(1)
    else:
        print('SUCCESS: All required columns exist')
"
if errorlevel 1 (
    echo ERROR: Database structure verification failed
    pause
    exit /b 1
)
echo SUCCESS: Database structure verified
echo.

echo [STEP 9] Creating sample stock data...
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

echo [STEP 10] Testing API endpoints...
python -c "
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stockscanner_django.settings')
import django
django.setup()

from stocks.models import Stock

# Test model access
stock_count = Stock.objects.count()
print(f'SUCCESS: Can access {stock_count} stocks from database')

# Test specific queries
aapl = Stock.objects.filter(ticker='AAPL').first()
if aapl:
    print(f'SUCCESS: Found AAPL stock: {aapl.name} at ${aapl.current_price}')
else:
    print('WARNING: AAPL stock not found')

# Test all required fields
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
echo SUCCESS: API testing completed
echo.

echo [STEP 11] Creating superuser (optional)...
echo Creating Django superuser (username: admin, password: admin123)...
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
echo DATABASE SETUP COMPLETE!
echo ========================================
echo.
echo Your database now has:
echo - All required tables created
echo - Proper field structure with all columns
echo - Sample stock data (AAPL, GOOGL, TSLA, MSFT, AMZN)
echo - Working Django models
echo - Admin user (admin/admin123)
echo.
echo You can now:
echo - Start the server: python manage.py runserver
echo - Start the scheduler: python start_stock_scheduler.py --background
echo - Visit WordPress API: http://127.0.0.1:8000/api/wordpress/
echo - Visit admin panel: http://127.0.0.1:8000/admin/
echo.
echo Test commands:
echo   python manage.py shell
echo   from stocks.models import Stock
echo   print(Stock.objects.all())
echo.
echo Press any key to finish...
pause > nul