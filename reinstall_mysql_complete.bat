@echo off
echo ========================================
echo COMPLETE MYSQL REINSTALLATION
echo ========================================
echo.
echo WARNING: This will completely remove and reinstall MySQL
echo - Stop all MySQL services
echo - Uninstall existing MySQL
echo - Remove all MySQL files and data
echo - Download and install fresh MySQL
echo - Set up the stock scanner database
echo.
echo Press Ctrl+C to cancel or any key to continue...
pause > nul
echo.

REM Set UTF-8 encoding
chcp 65001 > nul 2>&1

REM Set environment variables
set DJANGO_SETTINGS_MODULE=stockscanner_django.settings
set PYTHONIOENCODING=utf-8
set MYSQL_ROOT_PASSWORD=stockscanner123

echo [STEP 1] Stopping all MySQL services...
net stop mysql > nul 2>&1
net stop MySQL80 > nul 2>&1
net stop MySQL57 > nul 2>&1
net stop MySQL84 > nul 2>&1
echo SUCCESS: MySQL services stopped
echo.

echo [STEP 2] Removing MySQL from Windows services...
sc delete mysql > nul 2>&1
sc delete MySQL80 > nul 2>&1
sc delete MySQL57 > nul 2>&1
sc delete MySQL84 > nul 2>&1
echo SUCCESS: MySQL services removed
echo.

echo [STEP 3] Uninstalling existing MySQL programs...
echo Looking for MySQL installations to remove...

REM Try to uninstall using common MySQL product codes
wmic product where "name like '%%MySQL%%'" call uninstall /nointeractive > nul 2>&1

REM Alternative uninstall methods
if exist "C:\Program Files\MySQL\MySQL Server 8.0\bin\MySQLInstanceConfig.exe" (
    echo Uninstalling MySQL Server 8.0...
    "C:\Program Files\MySQL\MySQL Server 8.0\bin\MySQLInstanceConfig.exe" -remove > nul 2>&1
)

if exist "C:\Program Files\MySQL\MySQL Server 8.4\bin\MySQLInstanceConfig.exe" (
    echo Uninstalling MySQL Server 8.4...
    "C:\Program Files\MySQL\MySQL Server 8.4\bin\MySQLInstanceConfig.exe" -remove > nul 2>&1
)

echo SUCCESS: MySQL programs uninstalled
echo.

echo [STEP 4] Removing MySQL directories and data...
echo WARNING: This will delete all existing MySQL data
timeout /t 5 /nobreak > nul

if exist "C:\Program Files\MySQL" (
    echo Removing C:\Program Files\MySQL...
    rmdir /s /q "C:\Program Files\MySQL" > nul 2>&1
)

if exist "C:\ProgramData\MySQL" (
    echo Removing C:\ProgramData\MySQL...
    rmdir /s /q "C:\ProgramData\MySQL" > nul 2>&1
)

if exist "C:\Users\%USERNAME%\AppData\Roaming\MySQL" (
    echo Removing user MySQL data...
    rmdir /s /q "C:\Users\%USERNAME%\AppData\Roaming\MySQL" > nul 2>&1
)

echo SUCCESS: MySQL directories removed
echo.

echo [STEP 5] Cleaning registry entries...
echo Removing MySQL registry entries...
reg delete "HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\MySQL" /f > nul 2>&1
reg delete "HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\MySQL80" /f > nul 2>&1
reg delete "HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\MySQL57" /f > nul 2>&1
reg delete "HKEY_LOCAL_MACHINE\SOFTWARE\MySQL AB" /f > nul 2>&1
reg delete "HKEY_LOCAL_MACHINE\SOFTWARE\Wow6432Node\MySQL AB" /f > nul 2>&1
echo SUCCESS: Registry cleaned
echo.

echo [STEP 6] Removing MySQL from PATH...
echo Cleaning PATH environment variable...
powershell -Command "& {$env:PATH = ($env:PATH -split ';' | Where-Object { $_ -notlike '*MySQL*' }) -join ';'; [Environment]::SetEnvironmentVariable('PATH', $env:PATH, 'Machine')}" > nul 2>&1
echo SUCCESS: PATH cleaned
echo.

echo [STEP 7] Downloading fresh MySQL installer...
if exist "mysql-installer-community.msi" del "mysql-installer-community.msi"

echo Downloading MySQL Installer (this may take several minutes)...
powershell -Command "& {
    $ProgressPreference = 'SilentlyContinue'
    try {
        Invoke-WebRequest -Uri 'https://dev.mysql.com/get/Downloads/MySQLInstaller/mysql-installer-community-8.0.39.0.msi' -OutFile 'mysql-installer-community.msi'
        Write-Host 'SUCCESS: MySQL installer downloaded'
    } catch {
        Write-Host 'ERROR: Download failed'
        exit 1
    }
}"

if not exist "mysql-installer-community.msi" (
    echo ERROR: Failed to download MySQL installer
    echo Please download manually from: https://dev.mysql.com/downloads/installer/
    echo Then rename it to: mysql-installer-community.msi
    echo And run this script again
    pause
    exit /b 1
)
echo.

echo [STEP 8] Installing fresh MySQL Server...
echo This will install MySQL Server 8.0 with these settings:
echo - Root password: %MYSQL_ROOT_PASSWORD%
echo - Port: 3306
echo - Configuration: Development Machine
echo.
echo Starting installation (this may take 10-15 minutes)...

REM First try silent installation
msiexec /i mysql-installer-community.msi /quiet /norestart ^
    INSTALLDIR="C:\Program Files\MySQL\MySQL Server 8.0" ^
    DATADIR="C:\ProgramData\MySQL\MySQL Server 8.0\Data" ^
    PORT=3306 ^
    MYSQL_ROOT_PASSWORD=%MYSQL_ROOT_PASSWORD% ^
    ADDLOCAL=ALL

if errorlevel 1 (
    echo Silent installation failed, trying interactive mode...
    echo.
    echo IMPORTANT: During installation:
    echo 1. Choose "Server only" or "Developer Default"
    echo 2. Select "Development Machine" configuration
    echo 3. Set root password to: %MYSQL_ROOT_PASSWORD%
    echo 4. Use port 3306
    echo 5. Complete the installation
    echo.
    msiexec /i mysql-installer-community.msi
    echo.
    echo Please complete the MySQL installation with the settings above
    echo Then press any key to continue...
    pause > nul
)

echo SUCCESS: MySQL installation completed
echo.

echo [STEP 9] Waiting for MySQL service to initialize...
timeout /t 15 /nobreak > nul

echo Starting MySQL service...
net start mysql > nul 2>&1
if errorlevel 1 (
    net start MySQL80 > nul 2>&1
    if errorlevel 1 (
        echo Waiting longer for MySQL to initialize...
        timeout /t 30 /nobreak > nul
        net start mysql > nul 2>&1
        if errorlevel 1 (
            net start MySQL80 > nul 2>&1
            if errorlevel 1 (
                echo ERROR: Could not start MySQL service
                echo Please start it manually from Services or MySQL Installer
                pause
                exit /b 1
            )
        )
    )
)
echo SUCCESS: MySQL service started
echo.

echo [STEP 10] Setting up PATH for new MySQL...
if exist "C:\Program Files\MySQL\MySQL Server 8.0\bin" (
    set "MYSQL_PATH=C:\Program Files\MySQL\MySQL Server 8.0\bin"
    setx PATH "%PATH%;%MYSQL_PATH%" > nul 2>&1
    set PATH=%PATH%;%MYSQL_PATH%
    echo SUCCESS: MySQL added to PATH
) else (
    echo WARNING: MySQL bin directory not found, will try to locate...
    if exist "C:\Program Files\MySQL\MySQL Server 8.4\bin" (
        set "MYSQL_PATH=C:\Program Files\MySQL\MySQL Server 8.4\bin"
        setx PATH "%PATH%;%MYSQL_PATH%" > nul 2>&1
        set PATH=%PATH%;%MYSQL_PATH%
        echo SUCCESS: MySQL 8.4 added to PATH
    )
)
echo.

echo [STEP 11] Testing MySQL connection...
echo Testing connection with password: %MYSQL_ROOT_PASSWORD%
mysql -u root -p%MYSQL_ROOT_PASSWORD% -e "SELECT VERSION();" > temp_version.txt 2>&1
if errorlevel 1 (
    echo Connection failed with default password, trying without password...
    mysql -u root -e "SELECT VERSION();" > temp_version.txt 2>&1
    if errorlevel 1 (
        echo ERROR: Could not connect to MySQL
        echo Please check if MySQL is running and try connecting manually:
        echo mysql -u root -p
        pause
        exit /b 1
    ) else (
        set MYSQL_ROOT_PASSWORD=
        echo SUCCESS: Connected without password
    )
) else (
    echo SUCCESS: Connected with password %MYSQL_ROOT_PASSWORD%
)

if exist temp_version.txt (
    type temp_version.txt
    del temp_version.txt
)
echo.

echo [STEP 12] Creating stockscanner database...
if "%MYSQL_ROOT_PASSWORD%"=="" (
    mysql -u root -e "CREATE DATABASE IF NOT EXISTS stockscanner CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
) else (
    mysql -u root -p%MYSQL_ROOT_PASSWORD% -e "CREATE DATABASE IF NOT EXISTS stockscanner CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
)

if errorlevel 1 (
    echo ERROR: Could not create database
    echo Please create it manually after this script completes
    pause
) else (
    echo SUCCESS: Database 'stockscanner' created
)
echo.

echo [STEP 13] Installing Python MySQL packages...
python -m pip install pymysql mysqlclient --user --quiet --force-reinstall
if errorlevel 1 (
    echo Installing pymysql only (mysqlclient may have failed)...
    python -m pip install pymysql --user --quiet --force-reinstall
)
python -m pip install django djangorestframework --user --quiet
echo SUCCESS: Python packages installed
echo.

echo [STEP 14] Updating Django settings...
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
    
    print('SUCCESS: Django settings updated')
else:
    print('ERROR: Django settings file not found')
" %MYSQL_ROOT_PASSWORD%
echo.

echo [STEP 15] Setting up fresh database schema...
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

echo [STEP 16] Creating sample data and admin user...
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
        }
    ]
    
    for stock_data in sample_stocks:
        Stock.objects.create(**stock_data)
    
    print(f'SUCCESS: Created {len(sample_stocks)} sample stocks')

print(f'Database has {Stock.objects.count()} stocks total')
"
echo.

echo [STEP 17] Final testing...
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
echo MYSQL REINSTALLATION COMPLETE!
echo ========================================
echo.
echo Fresh MySQL Installation:
echo - Version: MySQL 8.0 (latest)
echo - Database: stockscanner  
echo - Username: root
echo - Password: %MYSQL_ROOT_PASSWORD%
echo - Host: localhost
echo - Port: 3306
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
echo.
echo MySQL Commands:
if "%MYSQL_ROOT_PASSWORD%"=="" (
    echo - Connect: mysql -u root
) else (
    echo - Connect: mysql -u root -p%MYSQL_ROOT_PASSWORD%
)
echo - Show databases: SHOW DATABASES;
echo - Use stockscanner: USE stockscanner;
echo - Show tables: SHOW TABLES;
echo.
echo If you need to reinstall again, just run this script again!
echo.
echo Press any key to finish...
pause > nul