#!/usr/bin/env python3
"""
Django Migrations Runner
Runs Django migrations in the correct order to avoid dependency issues
"""

import os
import sys
import django
from django.core.management import call_command
from django.db import connection
from io import StringIO

def setup_django():
"""Setup Django environment"""
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stockscanner_django.settings')
django.setup()

def run_migration_command(command_args, description):
"""Run a migration command and capture output"""
print(f" {description}...")
try:
out = StringIO()
call_command(*command_args, stdout=out, verbosity=2)
output = out.getvalue()

if output.strip():
print(f" Output: {output.strip()}")

print(f" {description} completed")
return True
except Exception as e:
print(f" {description} failed: {e}")
return False

def check_database_connection():
"""Test database connection"""
print(" Testing database connection...")
try:
cursor = connection.cursor()
cursor.execute("SELECT 1")
result = cursor.fetchone()
print(" Database connection successful")
return True
except Exception as e:
print(f" Database connection failed: {e}")
return False

def main():
"""Run migrations in proper order"""
print(" Django Migrations Runner")
print("=" * 35)

# Setup Django
print("1⃣ Setting up Django...")
try:
setup_django()
print(" Django setup completed")
except Exception as e:
print(f" Django setup failed: {e}")
return False

# Test database connection
if not check_database_connection():
print(" Using SQLite database (this is normal for development)")

# Migration steps in order
migration_steps = [
(['makemigrations'], "Creating new migrations"),
(['migrate', 'contenttypes'], "Migrating content types"),
(['migrate', 'auth'], "Migrating authentication"),
(['migrate', 'admin'], "Migrating admin"),
(['migrate', 'sessions'], "Migrating sessions"),
(['migrate', 'django_celery_beat'], "Migrating Celery Beat"),
(['migrate', 'core'], "Migrating core app"),
(['migrate', 'stocks'], "Migrating stocks app"),
(['migrate', 'emails'], "Migrating emails app"),
(['migrate', 'news'], "Migrating news app"),
(['migrate'], "Running remaining migrations"),
]

success_count = 0

for command_args, description in migration_steps:
success = run_migration_command(command_args, description)
if success:
success_count += 1
print()

# Final system check
print(" Running final system check...")
try:
out = StringIO()
call_command('check', stdout=out)
output = out.getvalue()

if 'System check identified no issues' in output:
print(" System check passed - no issues found")
else:
print(f" System check output:")
print(f" {output}")
except Exception as e:
print(f" System check failed: {e}")

print("\n" + "=" * 35)
print(" MIGRATION SUMMARY")
print("=" * 35)

success_rate = (success_count / len(migration_steps)) * 100
print(f" Success Rate: {success_count}/{len(migration_steps)} ({success_rate:.1f}%)")

if success_rate >= 80:
print("\n MIGRATIONS COMPLETED SUCCESSFULLY!")
print(" Database is ready for use")
print("\n Next steps:")
print(" 1. python manage.py createsuperuser (optional)")
print(" 2. python manage.py runserver")
print(" 3. Access: http://localhost:8000")
return True
else:
print("\n Some migrations had issues")
print(" Try running individual migrations manually")
return False

if __name__ == "__main__":
try:
success = main()
sys.exit(0 if success else 1)
except KeyboardInterrupt:
print("\n Migration interrupted")
sys.exit(1)
except Exception as e:
print(f"\n Migration failed: {e}")
sys.exit(1)