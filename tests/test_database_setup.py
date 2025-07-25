#!/usr/bin/env python3
"""
Database Setup Test Script
Tests SQLite database functionality without requiring Django
"""

import sqlite3
import os
import sys
from pathlib import Path
from datetime import datetime

def print_step(message):
"""Print setup step"""
print(f"\n {message}")

def print_success(message):
"""Print success message"""
print(f" {message}")

def print_error(message):
"""Print error message"""
print(f" {message}")

def print_warning(message):
"""Print warning message"""
print(f" {message}")

def test_sqlite_installation():
"""Test if SQLite is available"""
print_step("Testing SQLite installation...")

try:
import sqlite3
version = sqlite3.sqlite_version
print_success(f"SQLite {version} is available")
return True
except ImportError:
print_error("SQLite is not available")
return False

def create_test_database():
"""Create and test SQLite database"""
print_step("Creating test database...")

db_path = "test_stock_scanner.db"

try:
# Remove existing test database
if os.path.exists(db_path):
os.remove(db_path)

# Create connection
connection = sqlite3.connect(db_path)
cursor = connection.cursor()

# Create test tables (similar to Django models)
cursor.execute('''
CREATE TABLE IF NOT EXISTS test_stocks (
id INTEGER PRIMARY KEY AUTOINCREMENT,
ticker TEXT NOT NULL UNIQUE,
company_name TEXT NOT NULL,
current_price REAL,
price_change_today REAL,
volume_today INTEGER,
dvav REAL,
dvsa REAL,
pe_ratio REAL,
market_cap INTEGER,
note TEXT,
last_update TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS test_email_subscriptions (
id INTEGER PRIMARY KEY AUTOINCREMENT,
email TEXT NOT NULL UNIQUE,
category TEXT NOT NULL,
is_active BOOLEAN DEFAULT 1,
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')

# Create indexes
cursor.execute('CREATE INDEX IF NOT EXISTS idx_test_stock_ticker ON test_stocks(ticker)')
cursor.execute('CREATE INDEX IF NOT EXISTS idx_test_email_category ON test_email_subscriptions(category)')

connection.commit()
print_success(f"Test database created: {db_path}")

# Test insert
cursor.execute('''
INSERT INTO test_stocks (ticker, company_name, current_price, volume_today, note)
VALUES (?, ?, ?, ?, ?)
''', ('AAPL', 'Apple Inc.', 150.25, 45000000, 'Test stock data'))

cursor.execute('''
INSERT INTO test_email_subscriptions (email, category)
VALUES (?, ?)
''', ('test@example.com', 'technology'))

connection.commit()
print_success("Test data inserted successfully")

# Test query
cursor.execute('SELECT * FROM test_stocks WHERE ticker = ?', ('AAPL',))
stock_data = cursor.fetchone()

cursor.execute('SELECT * FROM test_email_subscriptions WHERE category = ?', ('technology',))
email_data = cursor.fetchone()

if stock_data and email_data:
print_success("Test data retrieved successfully")
print(f" Stock: {stock_data[1]} - ${stock_data[3]}")
print(f" Email: {email_data[1]} - {email_data[2]}")
else:
print_error("Failed to retrieve test data")
return False

connection.close()

# Clean up test database
os.remove(db_path)
print_success("Test database cleaned up")

return True

except Exception as e:
print_error(f"Database test failed: {e}")
return False

def test_yfinance_import():
"""Test yfinance import without making requests"""
print_step("Testing yfinance import...")

try:
import yfinance
print_success(f"yfinance is available (version check skipped)")
return True
except ImportError:
print_warning("yfinance not installed - will be installed during setup")
return False

def test_email_configuration():
"""Test email configuration structure"""
print_step("Testing email configuration...")

# Test Gmail SMTP settings
gmail_settings = {
'smtp_host': 'smtp.gmail.com',
'smtp_port': 587,
'email_user': 'noreply.retailtradescanner@gmail.com',
'email_password': 'mzqmvhsjqeqrjmjv',
'use_tls': True
}

# Validate settings
if all(gmail_settings.values()):
print_success("Gmail SMTP settings configured")
print(f" Host: {gmail_settings['smtp_host']}:{gmail_settings['smtp_port']}")
print(f" User: {gmail_settings['email_user']}")
print(f" TLS: {gmail_settings['use_tls']}")
return True
else:
print_error("Gmail SMTP settings incomplete")
return False

def test_file_structure():
"""Test if all required files exist"""
print_step("Testing file structure...")

required_files = [
'manage.py',
'setup_local.py',
'database_settings_local.py',
'emails/email_config.py',
'stocks/yfinance_config.py',
'security_hardening.py'
]

missing_files = []
for file_path in required_files:
if not os.path.exists(file_path):
missing_files.append(file_path)

if missing_files:
print_error(f"Missing files: {', '.join(missing_files)}")
return False
else:
print_success("All required files present")
return True

def create_sample_env_file():
"""Create a sample .env file for testing"""
print_step("Creating sample .env file...")

env_content = """# Sample Environment File for Stock Scanner

# Django Configuration
SECRET_KEY=test-secret-key-change-in-production
DEBUG=True
ADMIN_URL=admin

# Database Configuration (Local SQLite)
DB_TYPE=sqlite3
DB_NAME=stock_scanner.db
DB_PATH=./stock_scanner.db

# Email Configuration (Gmail)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=noreply.retailtradescanner@gmail.com
EMAIL_HOST_PASSWORD=mzqmvhsjqeqrjmjv
ADMIN_EMAIL=noreply.retailtradescanner@gmail.com

# Site Configuration
SITE_URL=http://localhost:8000
ALLOWED_HOSTS=localhost,127.0.0.1

# Stock API Configuration
USE_YFINANCE_ONLY=True
STOCK_API_RATE_LIMIT=1.0
YFINANCE_CACHE_DURATION=300

# Security Settings (Development)
SECURE_SSL_REDIRECT=False
SESSION_COOKIE_SECURE=False
CSRF_COOKIE_SECURE=False
"""

env_file = ".env.sample"
with open(env_file, 'w') as f:
f.write(env_content)

print_success(f"Sample .env file created: {env_file}")
return True

def run_comprehensive_test():
"""Run all tests"""
print("🧪 Stock Scanner Database & Configuration Test")
print("=" * 50)

tests = [
("SQLite Installation", test_sqlite_installation),
("Database Operations", create_test_database),
("yfinance Import", test_yfinance_import),
("Email Configuration", test_email_configuration),
("File Structure", test_file_structure),
("Environment File", create_sample_env_file)
]

results = {}

for test_name, test_function in tests:
try:
results[test_name] = test_function()
except Exception as e:
print_error(f"{test_name} failed with exception: {e}")
results[test_name] = False

# Summary
print("\n" + "=" * 50)
print(" Test Results Summary")
print("=" * 50)

passed = 0
total = len(tests)

for test_name, passed_test in results.items():
status = " PASS" if passed_test else " FAIL"
print(f"{status} {test_name}")
if passed_test:
passed += 1

print(f"\n Overall: {passed}/{total} tests passed")

if passed == total:
print_success("All tests passed! System is ready for setup.")
return True
else:
print_warning(f"{total - passed} tests failed. Some features may not work correctly.")
return False

if __name__ == "__main__":
success = run_comprehensive_test()
sys.exit(0 if success else 1)