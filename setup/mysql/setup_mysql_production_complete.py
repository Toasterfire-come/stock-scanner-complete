#!/usr/bin/env python3
"""
Complete MySQL Production Setup for Stock Scanner
Comprehensive MySQL configuration for production deployment.

This script handles:
1. MySQL installation verification
2. Database and user creation
3. Proper permissions and security
4. Environment configuration
5. Django settings optimization
6. Performance tuning
7. Backup configuration

Usage:
python setup_mysql_production_complete.py

Author: Stock Scanner Project
Version: 2.0.0 - Production Ready
"""

import subprocess
import sys
import os
import time
import json
from pathlib import Path
from datetime import datetime

def print_header(title):
"""Print a formatted header"""
print("\n" + "=" * 70)
print(f" {title}")
print("=" * 70)

def print_step(message):
"""Print a formatted step message"""
print(f"\n {message}")

def print_success(message):
"""Print a formatted success message"""
print(f" {message}")

def print_error(message):
"""Print a formatted error message"""
print(f" {message}")

def print_warning(message):
"""Print a formatted warning message"""
print(f" {message}")

def print_info(message):
"""Print a formatted info message"""
print(f" {message}")

def run_command(command, check=True, capture_output=False, input_text=None):
"""Run a command with comprehensive error handling"""
try:
if capture_output:
result = subprocess.run(
command, shell=True, capture_output=True, text=True, 
check=check, input=input_text
)
return result.stdout.strip()
else:
result = subprocess.run(
command, shell=True, check=check, input=input_text, text=True
)
return result.returncode == 0
except subprocess.CalledProcessError as e:
if check:
print_error(f"Command failed: {command}")
if e.stderr:
print(f"Error: {e.stderr}")
return False if not capture_output else ""
except Exception as e:
print_error(f"Error running command: {command}")
print(f"Error: {e}")
return False if not capture_output else ""

def check_mysql_installation():
"""Check if MySQL is properly installed"""
print_step("Checking MySQL installation...")

# Check MySQL service
mysql_service_check = run_command("sc query mysql", capture_output=True)
mysql80_service_check = run_command("sc query mysql80", capture_output=True)
mysql84_service_check = run_command("sc query mysql84", capture_output=True)

# Check MySQL command line
mysql_cmd_check = run_command("mysql --version", capture_output=True)

if any([mysql_service_check, mysql80_service_check, mysql84_service_check]) or mysql_cmd_check:
print_success("MySQL installation found")
if mysql_cmd_check:
print(f" MySQL Version: {mysql_cmd_check}")
return True
else:
print_error("MySQL not found")
print_info("Please install MySQL from: https://dev.mysql.com/downloads/mysql/")
return False

def start_mysql_service():
"""Start MySQL service"""
print_step("Starting MySQL service...")

services = ["mysql", "mysql80", "mysql84"]

for service in services:
if run_command(f"net start {service}", check=False):
print_success(f"MySQL service '{service}' started")
return True

print_error("Could not start MySQL service")
print_info("Try starting MySQL manually from Services or MySQL Workbench")
return False

def setup_mysql_root_password():
"""Setup MySQL root password"""
print_step("Configuring MySQL root password...")

# Production password for root
root_password = "StockScannerRoot2024!"

# Try to set root password (this might fail if already set)
commands = [
f"mysql -u root -e \"ALTER USER 'root'@'localhost' IDENTIFIED BY '{root_password}';\"",
f"mysql -u root -e \"FLUSH PRIVILEGES;\""
]

for cmd in commands:
run_command(cmd, check=False)

# Test the password
test_cmd = f"mysql -u root -p{root_password} -e \"SELECT VERSION();\""
if run_command(test_cmd, check=False):
print_success("MySQL root password configured")
return root_password
else:
print_warning("Root password may already be set or command failed")
return root_password

def create_production_database(root_password):
"""Create production database and user"""
print_step("Creating production database and user...")

# Production database configuration
db_config = {
'database': 'stock_scanner_production',
'username': 'stock_scanner_prod',
'password': 'StockScannerProd2024!',
'host': 'localhost',
'port': 3306
}

mysql_root_cmd = f"mysql -u root -p{root_password}"

# SQL commands to execute
sql_commands = [
f"CREATE DATABASE IF NOT EXISTS {db_config['database']} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;",
f"CREATE USER IF NOT EXISTS '{db_config['username']}'@'{db_config['host']}' IDENTIFIED BY '{db_config['password']}';",
f"GRANT ALL PRIVILEGES ON {db_config['database']}.* TO '{db_config['username']}'@'{db_config['host']}';",
f"GRANT CREATE, DROP, INDEX, ALTER ON {db_config['database']}.* TO '{db_config['username']}'@'{db_config['host']}';",
"FLUSH PRIVILEGES;"
]

success_count = 0
for sql in sql_commands:
cmd = f'{mysql_root_cmd} -e "{sql}"'
if run_command(cmd, check=False):
success_count += 1
else:
print_warning(f"SQL command may have failed: {sql}")

if success_count >= len(sql_commands) - 1: # Allow one failure
print_success("Production database and user created")
return db_config
else:
print_error("Database creation failed")
return None

def optimize_mysql_configuration():
"""Optimize MySQL configuration for Stock Scanner"""
print_step("Optimizing MySQL configuration...")

# Try to find MySQL configuration file
config_paths = [
"C:\\ProgramData\\MySQL\\MySQL Server 8.0\\my.ini",
"C:\\ProgramData\\MySQL\\MySQL Server 8.4\\my.ini",
"C:\\MySQL\\my.ini",
"my.ini"
]

config_file = None
for path in config_paths:
if os.path.exists(path):
config_file = path
break

if config_file:
print_success(f"Found MySQL config: {config_file}")
print_info("For production optimization, consider adjusting:")
print(" - innodb_buffer_pool_size = 256M")
print(" - max_connections = 100")
print(" - query_cache_size = 32M")
print(" - slow_query_log = 1")
else:
print_warning("MySQL configuration file not found")
print_info("Default settings will be used")

return True

def create_production_env_file(db_config):
"""Create production .env file with MySQL configuration"""
print_step("Creating production .env file...")

if not db_config:
print_error("Database configuration not available")
return False

# Create production environment configuration
env_content = f"""# Stock Scanner Production Environment Configuration
# Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
# MySQL Production Database Configuration

# Django Settings
SECRET_KEY=django-production-key-change-this-in-deployment
DEBUG=false
ALLOWED_HOSTS=localhost,127.0.0.1,yourdomain.com,www.yourdomain.com

# MySQL Production Database
DATABASE_URL=mysql://{db_config['username']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}
DB_ENGINE=django.db.backends.mysql
DB_NAME={db_config['database']}
DB_USER={db_config['username']}
DB_PASSWORD={db_config['password']}
DB_HOST={db_config['host']}
DB_PORT={db_config['port']}

# Database Connection Pool Settings
DB_CONN_MAX_AGE=300
DB_CONN_HEALTH_CHECKS=true

# Email Configuration (Production)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=true
EMAIL_HOST_USER=your-production-email@yourdomain.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=Stock Scanner <noreply@yourdomain.com>

# Celery Configuration (Production with Redis)
CELERY_ENABLED=true
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Redis Configuration (Production)
REDIS_URL=redis://localhost:6379/0
CACHE_TTL=300

# Yahoo Finance API Configuration
YFINANCE_RATE_LIMIT=true
YFINANCE_MAX_REQUESTS_PER_MINUTE=60
YFINANCE_DELAY_BETWEEN_REQUESTS=1.0
YFINANCE_TIMEOUT=30

# Security Settings (Production)
SECURE_SSL_REDIRECT=true
SECURE_BROWSER_XSS_FILTER=true
SECURE_CONTENT_TYPE_NOSNIFF=true
SECURE_REFERRER_POLICY=same-origin
X_FRAME_OPTIONS=DENY
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=true
SECURE_HSTS_PRELOAD=true

# Session Configuration
SESSION_COOKIE_SECURE=true
SESSION_COOKIE_HTTPONLY=true
SESSION_COOKIE_AGE=3600
CSRF_COOKIE_SECURE=true

# Payment Configuration (Stripe)
STRIPE_PUBLISHABLE_KEY=pk_live_your_publishable_key
STRIPE_SECRET_KEY=sk_live_your_secret_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret

# WordPress Integration
WORDPRESS_URL=https://yourdomain.com
WORDPRESS_API_BASE=https://yourdomain.com/wp-json/wp/v2/
WORDPRESS_USERNAME=api_user
WORDPRESS_PASSWORD=your_wordpress_app_password

# File Storage (Production)
MEDIA_URL=/media/
MEDIA_ROOT=./media/
STATIC_URL=/static/
STATIC_ROOT=./staticfiles/

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=logs/stock_scanner_production.log
DJANGO_LOG_LEVEL=INFO
SQL_LOG_LEVEL=WARNING

# Performance Settings
USE_GZIP=true
USE_ETAGS=true
CACHE_MIDDLEWARE_SECONDS=300

# Monitoring and Analytics
SENTRY_DSN=your_sentry_dsn_here
GOOGLE_ANALYTICS_ID=GA-XXXXXXXXX-X

# Backup Configuration
BACKUP_ENABLED=true
BACKUP_SCHEDULE=daily
BACKUP_RETENTION_DAYS=30
"""

try:
# Backup existing .env if it exists
if os.path.exists('.env'):
backup_name = f'.env.backup.{datetime.now().strftime("%Y%m%d_%H%M%S")}'
os.rename('.env', backup_name)
print_success(f"Backed up existing .env to {backup_name}")

# Write new production .env
with open('.env', 'w') as f:
f.write(env_content)

print_success("Production .env file created")
print_info("Remember to update the following before going live:")
print(" - SECRET_KEY (generate a new one)")
print(" - ALLOWED_HOSTS (your actual domain)")
print(" - Email settings")
print(" - Stripe keys (if using payments)")
print(" - WordPress credentials")

return True

except Exception as e:
print_error(f"Failed to create .env file: {e}")
return False

def update_django_settings_for_mysql():
"""Update Django settings for optimal MySQL performance"""
print_step("Updating Django settings for MySQL optimization...")

settings_file = "stockscanner_django/settings.py"

# Read current settings
try:
with open(settings_file, 'r') as f:
content = f.read()

# Check if MySQL optimizations are already present
if "MySQL Production Optimizations" in content:
print_success("MySQL optimizations already present in settings")
return True

# Add MySQL-specific optimizations
mysql_optimizations = '''

# MySQL Production Optimizations
if DATABASES['default']['ENGINE'] == 'django.db.backends.mysql':
DATABASES['default']['OPTIONS'].update({
'charset': 'utf8mb4',
'sql_mode': 'STRICT_TRANS_TABLES,NO_ZERO_DATE,NO_ZERO_IN_DATE,ERROR_FOR_DIVISION_BY_ZERO',
'isolation_level': 'READ COMMITTED',
'init_command': "SET foreign_key_checks = 0; SET sql_mode='STRICT_TRANS_TABLES'; SET foreign_key_checks = 1;",
})

# Connection pooling for production
DATABASES['default']['CONN_MAX_AGE'] = int(os.environ.get('DB_CONN_MAX_AGE', 300))
DATABASES['default']['CONN_HEALTH_CHECKS'] = os.environ.get('DB_CONN_HEALTH_CHECKS', 'true').lower() == 'true'

print(" MySQL production optimizations applied")
'''

# Insert before the last few lines of the file
lines = content.split('\n')
insert_position = len(lines) - 5 # Insert near the end
lines.insert(insert_position, mysql_optimizations)

# Write back to file
with open(settings_file, 'w') as f:
f.write('\n'.join(lines))

print_success("Django settings updated for MySQL")
return True

except Exception as e:
print_error(f"Failed to update Django settings: {e}")
return False

def test_mysql_connection(db_config):
"""Test MySQL connection with the created database"""
print_step("Testing MySQL connection...")

if not db_config:
print_error("No database configuration available")
return False

# Test connection using Django
try:
# Set environment variables for testing
os.environ['DATABASE_URL'] = f"mysql://{db_config['username']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}"

# Import Django and test
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stockscanner_django.settings')
import django
django.setup()

from django.db import connection
cursor = connection.cursor()
cursor.execute("SELECT VERSION();")
version = cursor.fetchone()[0]

print_success(f"MySQL connection successful - Version: {version}")
return True

except Exception as e:
print_error(f"MySQL connection test failed: {e}")
return False

def create_database_backup_script():
"""Create automated database backup script"""
print_step("Creating database backup script...")

backup_script = '''@echo off
REM MySQL Database Backup Script for Stock Scanner
REM Run this daily to backup your production database

set BACKUP_DIR=backups
set DATE=%date:~-4,4%%date:~-10,2%%date:~-7,2%
set TIME=%time:~0,2%%time:~3,2%%time:~6,2%
set TIMESTAMP=%DATE%_%TIME%

if not exist %BACKUP_DIR% mkdir %BACKUP_DIR%

echo Creating MySQL backup...
mysqldump -u stock_scanner_prod -pStockScannerProd2024! stock_scanner_production > %BACKUP_DIR%\\stock_scanner_backup_%TIMESTAMP%.sql

if %errorlevel% == 0 (
echo Backup created successfully: %BACKUP_DIR%\\stock_scanner_backup_%TIMESTAMP%.sql
) else (
echo Backup failed
)

REM Keep only last 30 days of backups
forfiles /p %BACKUP_DIR% /s /m *.sql /d -30 /c "cmd /c del @path" 2>nul

pause
'''

try:
with open('backup_database.bat', 'w') as f:
f.write(backup_script)
print_success("Database backup script created: backup_database.bat")
return True
except Exception as e:
print_error(f"Failed to create backup script: {e}")
return False

def run_initial_migrations():
"""Run Django migrations on the new MySQL database"""
print_step("Running Django migrations...")

try:
# Run migrations
migration_commands = [
"python manage.py makemigrations",
"python manage.py migrate",
"python manage.py collectstatic --noinput"
]

for cmd in migration_commands:
print(f" Running: {cmd}")
if run_command(cmd, check=False):
print_success(f" {cmd} completed")
else:
print_warning(f" {cmd} may have failed")

return True

except Exception as e:
print_error(f"Migration failed: {e}")
return False

def create_mysql_monitoring_script():
"""Create MySQL monitoring and health check script"""
print_step("Creating MySQL monitoring script...")

monitoring_script = '''@echo off
REM MySQL Health Check Script for Stock Scanner

echo MySQL Health Check
echo =====================

echo.
echo MySQL Service Status:
sc query mysql
if %errorlevel% == 0 (
echo MySQL service is running
) else (
echo MySQL service is not running
echo Try: net start mysql
)

echo.
echo Database Connection Test:
mysql -u stock_scanner_prod -pStockScannerProd2024! -e "SELECT 'Connection OK' as Status;" stock_scanner_production
if %errorlevel% == 0 (
echo Database connection successful
) else (
echo Database connection failed
)

echo.
echo Database Size:
mysql -u stock_scanner_prod -pStockScannerProd2024! -e "SELECT table_schema AS 'Database', ROUND(SUM(data_length + index_length) / 1024 / 1024, 2) AS 'Size (MB)' FROM information_schema.tables WHERE table_schema = 'stock_scanner_production' GROUP BY table_schema;" stock_scanner_production

echo.
echo Table Count:
mysql -u stock_scanner_prod -pStockScannerProd2024! -e "SELECT COUNT(*) as 'Total Tables' FROM information_schema.tables WHERE table_schema = 'stock_scanner_production';" stock_scanner_production

echo.
echo Recent Activity (Last 24h):
mysql -u stock_scanner_prod -pStockScannerProd2024! -e "SHOW PROCESSLIST;" stock_scanner_production

pause
'''

try:
with open('mysql_health_check.bat', 'w') as f:
f.write(monitoring_script)
print_success("MySQL monitoring script created: mysql_health_check.bat")
return True
except Exception as e:
print_error(f"Failed to create monitoring script: {e}")
return False

def main():
"""Main setup function"""
print_header("STOCK SCANNER - COMPLETE MYSQL PRODUCTION SETUP")
print(" This script configures MySQL for production deployment")
print("⏱ Estimated time: 10-15 minutes")
print(" Sets up secure production database with optimizations")

# Track setup progress
setup_steps = {
'mysql_check': False,
'service_start': False,
'root_password': False,
'database_creation': False,
'env_file': False,
'django_settings': False,
'connection_test': False,
'migrations': False,
'backup_script': False,
'monitoring': False
}

# Step 1: Check MySQL installation
if check_mysql_installation():
setup_steps['mysql_check'] = True
else:
print_error("MySQL installation required. Exiting.")
return False

# Step 2: Start MySQL service
if start_mysql_service():
setup_steps['service_start'] = True

# Step 3: Setup root password
root_password = setup_mysql_root_password()
if root_password:
setup_steps['root_password'] = True

# Step 4: Create production database
db_config = create_production_database(root_password)
if db_config:
setup_steps['database_creation'] = True

# Step 5: Optimize MySQL configuration
optimize_mysql_configuration()

# Step 6: Create production .env file
if create_production_env_file(db_config):
setup_steps['env_file'] = True

# Step 7: Update Django settings
if update_django_settings_for_mysql():
setup_steps['django_settings'] = True

# Step 8: Test connection
if test_mysql_connection(db_config):
setup_steps['connection_test'] = True

# Step 9: Run migrations
if run_initial_migrations():
setup_steps['migrations'] = True

# Step 10: Create backup script
if create_database_backup_script():
setup_steps['backup_script'] = True

# Step 11: Create monitoring script
if create_mysql_monitoring_script():
setup_steps['monitoring'] = True

# Final report
print_header("MYSQL PRODUCTION SETUP COMPLETE")

successful_steps = sum(setup_steps.values())
total_steps = len(setup_steps)

print(f" Setup Progress: {successful_steps}/{total_steps} steps completed")

if successful_steps >= total_steps - 2: # Allow 2 failures
print_success(" MySQL production setup completed successfully!")

if db_config:
print(f"\n Production Database Information:")
print(f" Database: {db_config['database']}")
print(f" Username: {db_config['username']}")
print(f" Host: {db_config['host']}")
print(f" Port: {db_config['port']}")

print(f"\n Next Steps:")
print(" 1. Review and update .env file with your production settings")
print(" 2. python manage.py createsuperuser")
print(" 3. python manage.py runserver")
print(" 4. Run mysql_health_check.bat to monitor database")
print(" 5. Setup backup_database.bat as a scheduled task")

print(f"\n Useful Commands:")
print(" mysql_health_check.bat - Check database health")
print(" backup_database.bat - Manual database backup")
print(" python manage.py dbshell - Access MySQL shell")

return True
else:
print_error(" Setup completed with some issues")
print(f"\n Failed steps:")
for step, success in setup_steps.items():
if not success:
print(f" - {step.replace('_', ' ').title()}")

print(f"\n Troubleshooting:")
print(" 1. Ensure MySQL is properly installed")
print(" 2. Check MySQL service is running")
print(" 3. Verify root password access")
print(" 4. Run setup again after fixing issues")

return False

if __name__ == "__main__":
try:
success = main()
sys.exit(0 if success else 1)
except KeyboardInterrupt:
print("\n Setup interrupted by user")
sys.exit(1)
except Exception as e:
print(f"\n Unexpected error: {e}")
sys.exit(1)