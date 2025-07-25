#!/usr/bin/env python
"""
Django Settings Float Conversion Error Fix
Fixes the "could not convert string to float: 'True'" error in Django settings.

This error typically occurs when:
1. DATABASE_URL has malformed parameters
2. Environment variables have incorrect boolean/numeric formatting
3. dj_database_url receives invalid connection strings

Usage:
python fix_django_settings_error.py

Author: Stock Scanner Project
Version: 1.0.0
"""

import os
import sys
from pathlib import Path

def print_header(title):
"""Print a formatted header"""
print("\n" + "=" * 60)
print(f" {title}")
print("=" * 60)

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

def check_env_file():
"""Check and fix .env file issues"""
print_step("Checking .env file for issues...")

env_file = Path('.env')
if not env_file.exists():
print_warning(".env file not found, creating a clean one...")
create_clean_env_file()
return True

try:
with open('.env', 'r') as f:
content = f.read()

issues_found = []
lines = content.split('\n')
fixed_lines = []

for line_num, line in enumerate(lines, 1):
line = line.strip()
if not line or line.startswith('#'):
fixed_lines.append(line)
continue

if '=' in line:
key, value = line.split('=', 1)
key = key.strip()
value = value.strip()

# Check for common issues
if key == 'DATABASE_URL' and value:
# Check for malformed DATABASE_URL
if not any(value.startswith(prefix) for prefix in ['postgresql://', 'mysql://', 'sqlite://']):
issues_found.append(f"Line {line_num}: Invalid DATABASE_URL format")
# Fix by creating a proper SQLite URL
value = 'sqlite:///./db.sqlite3'
print_warning(f"Fixed malformed DATABASE_URL on line {line_num}")

# Check for boolean values that should be strings
elif key in ['DEBUG', 'CELERY_ENABLED', 'EMAIL_USE_TLS']:
if value.lower() not in ['true', 'false']:
issues_found.append(f"Line {line_num}: {key} should be 'true' or 'false'")
value = 'false' if key == 'CELERY_ENABLED' else 'true'
print_warning(f"Fixed boolean value for {key} on line {line_num}")

# Check for numeric values that might have boolean strings
elif key in ['EMAIL_PORT', 'DB_PORT', 'REDIS_PORT']:
if value.lower() in ['true', 'false'] or not value.isdigit():
issues_found.append(f"Line {line_num}: {key} should be numeric")
default_ports = {'EMAIL_PORT': '587', 'DB_PORT': '5432', 'REDIS_PORT': '6379'}
value = default_ports.get(key, '80')
print_warning(f"Fixed numeric value for {key} on line {line_num}")

fixed_lines.append(f"{key}={value}")
else:
fixed_lines.append(line)

if issues_found:
print_error(f"Found {len(issues_found)} issues in .env file:")
for issue in issues_found:
print(f" - {issue}")

# Backup original file
backup_file = '.env.backup'
with open(backup_file, 'w') as f:
f.write(content)
print_success(f"Created backup: {backup_file}")

# Write fixed content
with open('.env', 'w') as f:
f.write('\n'.join(fixed_lines))
print_success("Fixed .env file issues")

return True
else:
print_success("No issues found in .env file")
return True

except Exception as e:
print_error(f"Error reading .env file: {e}")
print_warning("Creating a new clean .env file...")
create_clean_env_file()
return True

def create_clean_env_file():
"""Create a clean .env file with correct formatting"""
clean_env_content = """# Stock Scanner Environment Configuration
# Fixed format to prevent Django settings errors

# Django Settings
SECRET_KEY=django-insecure-fixed-key-change-in-production
DEBUG=true
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

# Database Configuration (SQLite - no complications)
DATABASE_URL=sqlite:///./db.sqlite3
DB_ENGINE=django.db.backends.sqlite3
DB_NAME=db.sqlite3
DB_USER=
DB_PASSWORD=
DB_HOST=
DB_PORT=

# Email Configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=true
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=your-email@gmail.com

# Celery Configuration (Disabled to prevent Redis issues)
CELERY_ENABLED=false
CELERY_BROKER_URL=

# Redis Configuration (Optional)
REDIS_URL=

# Yahoo Finance API Configuration
YFINANCE_RATE_LIMIT=true
YFINANCE_MAX_REQUESTS_PER_MINUTE=60
YFINANCE_DELAY_BETWEEN_REQUESTS=1.0
YFINANCE_TIMEOUT=15

# Security Settings
SECURE_SSL_REDIRECT=false
SECURE_BROWSER_XSS_FILTER=true
SECURE_CONTENT_TYPE_NOSNIFF=true
X_FRAME_OPTIONS=DENY

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/stock_scanner.log
"""

try:
with open('.env', 'w') as f:
f.write(clean_env_content)
print_success("Created clean .env file with proper formatting")
return True
except Exception as e:
print_error(f"Failed to create .env file: {e}")
return False

def test_django_settings():
"""Test Django settings import"""
print_step("Testing Django settings...")

try:
# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stockscanner_django.settings')

# Test settings import
from django.conf import settings
print_success("Django settings imported successfully")

# Test specific configurations
print(f" DEBUG: {settings.DEBUG}")
print(f" Database Engine: {settings.DATABASES['default']['ENGINE']}")

if hasattr(settings, 'CACHES'):
print(f" Cache Backend: {settings.CACHES['default']['BACKEND']}")

return True

except Exception as e:
print_error(f"Django settings test failed: {e}")
if "could not convert string to float" in str(e):
print_warning("This is the float conversion error we're trying to fix")
return False

def fix_database_url():
"""Fix common DATABASE_URL issues"""
print_step("Checking DATABASE_URL configuration...")

# Read current .env
env_vars = {}
if os.path.exists('.env'):
with open('.env', 'r') as f:
for line in f:
line = line.strip()
if line and '=' in line and not line.startswith('#'):
key, value = line.split('=', 1)
env_vars[key.strip()] = value.strip()

database_url = env_vars.get('DATABASE_URL', '')

if database_url:
print(f" Current DATABASE_URL: {database_url}")

# Check for common issues
if 'True' in database_url or 'False' in database_url:
print_warning("Found boolean values in DATABASE_URL")
# Replace with SQLite
env_vars['DATABASE_URL'] = 'sqlite:///./db.sqlite3'
print_success("Fixed DATABASE_URL to use SQLite")

# Write back to .env
env_lines = []
for key, value in env_vars.items():
env_lines.append(f"{key}={value}")

with open('.env', 'w') as f:
f.write('\n'.join(env_lines))

return True
else:
print_success("No DATABASE_URL found, will use default SQLite")
return True

def main():
"""Main fix function"""
print_header("DJANGO SETTINGS FLOAT CONVERSION ERROR FIX")
print(" Fixing: 'could not convert string to float: True' error")
print(" This typically occurs in database or cache configuration")

success_count = 0
total_checks = 4

# Check 1: Fix .env file
if check_env_file():
success_count += 1

# Check 2: Fix DATABASE_URL specifically
if fix_database_url():
success_count += 1

# Check 3: Test Django settings
if test_django_settings():
success_count += 1
else:
# If Django test fails, try one more fix
print_step("Django test failed, trying alternative fix...")
create_clean_env_file()
if test_django_settings():
success_count += 1

# Check 4: Final verification
try:
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stockscanner_django.settings')
django.setup()
print_success("Django setup completed successfully")
success_count += 1
except Exception as e:
print_error(f"Django setup failed: {e}")

# Final report
print_header("FIX RESULTS")
print(f" Successful checks: {success_count}/{total_checks}")

if success_count == total_checks:
print_success(" All issues fixed! Django should work now.")
print("\n Next steps:")
print(" 1. python manage.py migrate")
print(" 2. python manage.py runserver")
print(" 3. Open browser to: http://127.0.0.1:8000")
return True
else:
print_warning(f" {total_checks - success_count} issues remain")
print("\n Additional troubleshooting:")
print(" 1. Check the original error message for specific line numbers")
print(" 2. Manually review .env file for any remaining 'True'/'False' in numeric fields")
print(" 3. Consider using emergency_setup_windows.bat for a clean start")
return False

if __name__ == "__main__":
try:
success = main()
sys.exit(0 if success else 1)
except KeyboardInterrupt:
print("\n Fix interrupted by user")
sys.exit(1)
except Exception as e:
print(f"\n Unexpected error: {e}")
sys.exit(1)