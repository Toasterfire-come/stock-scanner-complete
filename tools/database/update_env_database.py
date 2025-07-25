#!/usr/bin/env python3
"""
Update .env Database Configuration Script
Automatically updates .env file with PostgreSQL credentials.

Usage:
python update_env_database.py

Author: Stock Scanner Project
Version: 1.0.0
"""

import os
from pathlib import Path

def update_env_file():
"""Update .env file with PostgreSQL configuration"""
print(" Updating .env file with database configuration...")

env_file = Path(".env")

# Database configuration (only these will be updated)
db_config = {
'DB_HOST': 'localhost',
'DB_PORT': '5432',
'DB_NAME': 'stockscanner_prod',
'DB_USER': 'stockscanner',
'DB_PASSWORD': 'C2rt3rK#2010',
'DATABASE_URL': 'postgresql://stockscanner:C2rt3rK#2010@localhost:5432/stockscanner_prod'
}

# Read existing .env file if it exists
existing_config = {}
if env_file.exists():
print(" Reading existing .env file...")
with open(env_file, 'r', encoding='utf-8') as f:
for line in f:
line = line.strip()
if '=' in line and not line.startswith('#'):
key, value = line.split('=', 1)
existing_config[key] = value
print(f" Found {len(existing_config)} existing settings - preserving them")

# Only update database-specific configuration, preserve everything else
for key, value in db_config.items():
existing_config[key] = value
print(f" Updated: {key}")

# Set default values for missing keys (but don't override existing ones)
default_config = {
'DEBUG': 'False',
'SECRET_KEY': 'your-super-secret-key-here-make-it-long-and-random',
'ALLOWED_HOSTS': 'localhost,127.0.0.1,your-domain.com,www.your-domain.com',
'REDIS_URL': 'redis://localhost:6379/0',
'CELERY_BROKER_URL': 'redis://localhost:6379/0',
'CELERY_RESULT_BACKEND': 'redis://localhost:6379/0',
'EMAIL_BACKEND': 'django.core.mail.backends.smtp.EmailBackend',
'EMAIL_HOST': 'smtp.your-email-provider.com',
'EMAIL_PORT': '587',
'EMAIL_USE_TLS': 'True',
'EMAIL_HOST_USER': 'your-email@domain.com',
'EMAIL_HOST_PASSWORD': 'your-email-password',
'STRIPE_PUBLIC_KEY': 'pk_test_your_stripe_public_key',
'STRIPE_SECRET_KEY': 'sk_test_your_stripe_secret_key',
'STRIPE_WEBHOOK_SECRET': 'whsec_your_webhook_secret',
'STOCK_API_RATE_LIMIT': '1.0',
'YFINANCE_THREADS': '5',
'STATIC_URL': '/static/',
'MEDIA_URL': '/media/'
}

# Only add defaults for missing keys
for key, value in default_config.items():
if key not in existing_config:
existing_config[key] = value
print(f" Added default: {key}")

# Write updated .env file
print(" Writing updated .env file...")
with open(env_file, 'w', encoding='utf-8') as f:
f.write("# Stock Scanner Environment Configuration\n")
f.write("# Database configuration updated automatically\n")
f.write("# Other settings preserved from existing configuration\n\n")

# Group related settings
groups = {
'Production Environment': ['DEBUG', 'SECRET_KEY', 'ALLOWED_HOSTS'],
'Database Configuration': ['DATABASE_URL', 'DB_NAME', 'DB_USER', 'DB_PASSWORD', 'DB_HOST', 'DB_PORT'],
'Redis Configuration': ['REDIS_URL', 'CELERY_BROKER_URL', 'CELERY_RESULT_BACKEND'],
'Email Configuration': ['EMAIL_BACKEND', 'EMAIL_HOST', 'EMAIL_PORT', 'EMAIL_USE_TLS', 'EMAIL_HOST_USER', 'EMAIL_HOST_PASSWORD'],
'Payment Configuration': ['STRIPE_PUBLIC_KEY', 'STRIPE_SECRET_KEY', 'STRIPE_WEBHOOK_SECRET'],
'Yahoo Finance API Configuration': ['STOCK_API_RATE_LIMIT', 'YFINANCE_THREADS'],
'Static Files': ['STATIC_URL', 'MEDIA_URL']
}

# Write grouped settings
written_keys = set()
for group_name, keys in groups.items():
f.write(f"# {group_name}\n")
for key in keys:
if key in existing_config:
f.write(f"{key}={existing_config[key]}\n")
written_keys.add(key)
f.write("\n")

# Write any remaining settings not in groups
remaining_keys = set(existing_config.keys()) - written_keys
if remaining_keys:
f.write("# Additional Configuration\n")
for key in sorted(remaining_keys):
f.write(f"{key}={existing_config[key]}\n")
f.write("\n")

print(" .env file updated successfully!")
print()
print(" Database configuration updated:")
print(" Host: localhost")
print(" Port: 5432")
print(" Database: stockscanner_prod")
print(" Username: stockscanner")
print(" Password: C2rt3rK#2010")
print()
print(" Preserved all existing settings (passwords, API keys, etc.)")
print(" Only database settings were updated")

return True

def main():
"""Main function"""
print(" Database Configuration Updater")
print("=" * 40)
print()
print("This script will update your .env file with the correct")
print("PostgreSQL database configuration.")
print()

try:
if update_env_file():
print("\n SUCCESS: .env file updated!")
print("\n Next steps:")
print(" python manage.py migrate")
print(" python manage.py createsuperuser")
print(" python manage.py runserver")
else:
print("\n FAILED: Could not update .env file")

except Exception as e:
print(f"\n Error: {e}")

input("\nPress Enter to continue...")

if __name__ == "__main__":
main()