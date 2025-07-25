#!/usr/bin/env python3
"""
Common Utilities Module
Consolidates frequently used functions across the Stock Scanner project.

This module provides:
- Django setup utilities
- Database connection helpers
- Common testing functions
- Error handling utilities

Author: Stock Scanner Project
Version: 1.0.0
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import Dict, Optional, Union, Any


class DjangoSetup:
"""Django setup utilities"""

@staticmethod
def setup_django_environment() -> bool:
"""
Setup Django environment with proper settings module.

Returns:
bool: True if setup successful, False otherwise
"""
try:
# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stockscanner_django.settings')

# Import and setup Django
import django
django.setup()

return True
except ImportError as e:
print(f" Django import failed: {e}")
return False
except Exception as e:
print(f" Django setup failed: {e}")
return False

@staticmethod
def test_django_imports() -> Dict[str, bool]:
"""
Test essential Django imports.

Returns:
Dict[str, bool]: Test results for each import
"""
tests = {}

# Core Django imports
import_tests = [
('django', 'Django core'),
('django.conf', 'Django configuration'),
('django.db', 'Django database'),
('django.core.management', 'Django management'),
('rest_framework', 'Django REST Framework'),
]

for module, description in import_tests:
try:
__import__(module)
tests[description] = True
except ImportError:
tests[description] = False

return tests


class DatabaseUtils:
"""Database utilities"""

@staticmethod
def test_database_connection() -> bool:
"""
Test database connection.

Returns:
bool: True if connection successful
"""
try:
from django.db import connection
cursor = connection.cursor()
cursor.execute("SELECT 1")
cursor.fetchone()
return True
except Exception as e:
print(f" Database connection failed: {e}")
return False

@staticmethod
def get_database_info() -> Dict[str, Any]:
"""
Get database configuration information.

Returns:
Dict: Database configuration details
"""
try:
from django.conf import settings
db_config = settings.DATABASES.get('default', {})

return {
'engine': db_config.get('ENGINE', 'Unknown'),
'name': db_config.get('NAME', 'Unknown'),
'host': db_config.get('HOST', 'localhost'),
'port': db_config.get('PORT', 'default'),
'user': db_config.get('USER', 'Unknown'),
}
except Exception as e:
print(f" Could not get database info: {e}")
return {}


class SystemUtils:
"""System utilities"""

@staticmethod
def run_command(command: str, check: bool = True, capture_output: bool = False) -> Union[bool, str]:
"""
Run a system command with consistent error handling.

Args:
command (str): Command to execute
check (bool): Whether to check return code
capture_output (bool): Whether to capture and return output

Returns:
Union[bool, str]: Success status or command output
"""
try:
if capture_output:
result = subprocess.run(
command, shell=True, capture_output=True, 
text=True, check=check
)
return result.stdout.strip()
else:
result = subprocess.run(command, shell=True, check=check)
return result.returncode == 0
except subprocess.CalledProcessError as e:
if check:
print(f" Command failed: {command}")
print(f"Error: {e}")
return False if not capture_output else ""
except Exception as e:
print(f" Error running command: {command}")
print(f"Error: {e}")
return False if not capture_output else ""

@staticmethod
def check_python_version() -> Dict[str, Any]:
"""
Check Python version and environment info.

Returns:
Dict: Python environment information
"""
return {
'version': sys.version,
'executable': sys.executable,
'platform': sys.platform,
'virtual_env': os.environ.get('VIRTUAL_ENV'),
'python_path': sys.path[0] if sys.path else None,
}

@staticmethod
def ensure_directory(path: Union[str, Path]) -> bool:
"""
Ensure directory exists, create if necessary.

Args:
path: Directory path to ensure

Returns:
bool: True if directory exists or was created
"""
try:
Path(path).mkdir(parents=True, exist_ok=True)
return True
except Exception as e:
print(f" Could not create directory {path}: {e}")
return False


class TestingUtils:
"""Testing utilities"""

@staticmethod
def test_package_import(package_name: str) -> bool:
"""
Test if a package can be imported.

Args:
package_name (str): Name of package to test

Returns:
bool: True if import successful
"""
try:
__import__(package_name)
return True
except ImportError:
return False

@staticmethod
def run_django_check() -> bool:
"""
Run Django system check.

Returns:
bool: True if check passes
"""
try:
from django.core.management import call_command
from io import StringIO

out = StringIO()
call_command('check', stdout=out)
output = out.getvalue()

if 'System check identified no issues' in output:
return True
else:
print(f" Django check output: {output}")
return False
except Exception as e:
print(f" Django check failed: {e}")
return False

@staticmethod
def test_yfinance_connection() -> bool:
"""
Test yfinance package and basic functionality.

Returns:
bool: True if yfinance is working
"""
try:
import yfinance as yf

# Test basic functionality
ticker = yf.Ticker("AAPL")
info = ticker.info

if info and 'symbol' in info:
return True
else:
print(" yfinance imported but no data returned")
return False
except ImportError:
print(" yfinance not installed")
return False
except Exception as e:
print(f" yfinance test failed: {e}")
return False


class ProjectUtils:
"""Project-specific utilities"""

@staticmethod
def get_project_root() -> Path:
"""
Get the project root directory.

Returns:
Path: Project root path
"""
# Look for manage.py to identify project root
current = Path.cwd()
while current != current.parent:
if (current / 'manage.py').exists():
return current
current = current.parent

# Fallback to current working directory
return Path.cwd()

@staticmethod
def check_required_files() -> Dict[str, bool]:
"""
Check if required project files exist.

Returns:
Dict[str, bool]: File existence status
"""
project_root = ProjectUtils.get_project_root()

required_files = [
'manage.py',
'requirements.txt',
'stockscanner_django/settings.py',
'stocks/models.py',
'core/models.py',
]

return {
file_path: (project_root / file_path).exists()
for file_path in required_files
}

@staticmethod
def get_installed_packages() -> Dict[str, bool]:
"""
Check if required packages are installed.

Returns:
Dict[str, bool]: Package installation status
"""
required_packages = [
'django',
'djangorestframework',
'yfinance',
'requests',
'celery',
'redis',
]

return {
package: TestingUtils.test_package_import(package)
for package in required_packages
}


# Convenience functions for backward compatibility
def setup_django():
"""Backward compatible Django setup function"""
return DjangoSetup.setup_django_environment()

def test_database_connection():
"""Backward compatible database test function"""
return DatabaseUtils.test_database_connection()

def run_command(command, check=True, capture_output=False):
"""Backward compatible command runner"""
return SystemUtils.run_command(command, check, capture_output)

# Export main classes and functions
__all__ = [
'DjangoSetup',
'DatabaseUtils', 
'SystemUtils',
'TestingUtils',
'ProjectUtils',
'setup_django',
'test_database_connection',
'run_command',
]