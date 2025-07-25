#!/usr/bin/env python3
"""
Complete Database Reset Script
WARNING: This will completely wipe your database and start fresh!

Use this only if the migration fix script doesn't work and you're okay 
with losing all existing data.

Usage: python reset_database_completely.py
"""

import os
import sys
import django
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stockscanner_django.settings')

try:
    django.setup()
except Exception as e:
    print(f"❌ Django setup failed: {e}")
    sys.exit(1)

from django.core.management import call_command
from django.db import connection
from django.conf import settings
import subprocess

def print_header(message):
    print(f"\n{'='*70}")
    print(f"💥 {message}")
    print('='*70)

def print_step(message):
    print(f"\n📋 {message}")
    
def print_success(message):
    print(f"✅ {message}")
    
def print_warning(message):
    print(f"⚠️  {message}")
    
def print_error(message):
    print(f"❌ {message}")

def get_user_confirmation():
    """Get user confirmation before proceeding"""
    print_header("⚠️  DANGER ZONE ⚠️")
    print("This script will:")
    print("1. 💥 DROP ALL TABLES in your database")
    print("2. 🗑️  DELETE ALL DATA permanently")
    print("3. 🔄 Recreate everything from scratch")
    print("4. 📊 You'll need to reload all your stock data")
    
    print("\n" + "="*70)
    response = input("Are you ABSOLUTELY SURE you want to continue? (type 'YES' to confirm): ")
    
    if response != 'YES':
        print("❌ Operation cancelled. Database unchanged.")
        return False
    
    print_warning("Last chance to back out...")
    response2 = input("Type 'DELETE EVERYTHING' to proceed: ")
    
    if response2 != 'DELETE EVERYTHING':
        print("❌ Operation cancelled. Database unchanged.")
        return False
    
    return True

def backup_database():
    """Create database backup before destruction"""
    print_step("Creating final backup before reset...")
    try:
        db_settings = settings.DATABASES['default']
        backup_file = f"final_backup_before_reset.sql"
        
        cmd = [
            'mysqldump',
            f"--host={db_settings.get('HOST', 'localhost')}",
            f"--port={db_settings.get('PORT', '3306')}",
            f"--user={db_settings['USER']}",
            f"--password={db_settings['PASSWORD']}",
            '--single-transaction',
            '--routines',
            '--triggers',
            db_settings['NAME']
        ]
        
        with open(backup_file, 'w') as f:
            result = subprocess.run(cmd, stdout=f, stderr=subprocess.PIPE, text=True)
        
        if result.returncode == 0:
            print_success(f"Final backup created: {backup_file}")
            return backup_file
        else:
            print_error(f"Backup failed: {result.stderr}")
            return None
    except Exception as e:
        print_error(f"Backup failed: {e}")
        return None

def drop_all_tables():
    """Drop all tables in the database"""
    print_step("Dropping all tables...")
    try:
        with connection.cursor() as cursor:
            # Disable foreign key checks
            cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
            
            # Get all table names
            cursor.execute("SHOW TABLES")
            tables = [row[0] for row in cursor.fetchall()]
            
            print(f"Found {len(tables)} tables to drop: {', '.join(tables)}")
            
            # Drop all tables
            for table in tables:
                cursor.execute(f"DROP TABLE IF EXISTS `{table}`")
                print(f"Dropped table: {table}")
            
            # Re-enable foreign key checks
            cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
            
            print_success(f"Successfully dropped {len(tables)} tables")
            return True
            
    except Exception as e:
        print_error(f"Failed to drop tables: {e}")
        return False

def recreate_fresh_database():
    """Create fresh database schema"""
    print_step("Creating fresh database schema...")
    try:
        # Run migrations to create fresh schema
        call_command('migrate', verbosity=2)
        print_success("Fresh database schema created")
        return True
    except Exception as e:
        print_error(f"Failed to create fresh schema: {e}")
        return False

def verify_fresh_database():
    """Verify the database is working"""
    print_step("Verifying fresh database...")
    try:
        with connection.cursor() as cursor:
            cursor.execute("SHOW TABLES")
            tables = [row[0] for row in cursor.fetchall()]
            
            print(f"Database now has {len(tables)} tables:")
            for table in sorted(tables):
                print(f"  - {table}")
            
            # Test basic functionality
            cursor.execute("SELECT COUNT(*) FROM django_migrations")
            migration_count = cursor.fetchone()[0]
            print_success(f"Database has {migration_count} migrations applied")
            
            return True
    except Exception as e:
        print_error(f"Database verification failed: {e}")
        return False

def main():
    """Main execution function"""
    print_header("COMPLETE DATABASE RESET TOOL")
    
    # Get user confirmation
    if not get_user_confirmation():
        return False
    
    print_header("STARTING DATABASE RESET")
    
    # Step 1: Create backup
    backup_file = backup_database()
    if not backup_file:
        print_warning("Proceeding without backup")
    
    # Step 2: Drop all tables
    if not drop_all_tables():
        print_error("Failed to drop tables. Aborting.")
        return False
    
    # Step 3: Recreate fresh database
    if not recreate_fresh_database():
        print_error("Failed to recreate database. Aborting.")
        return False
    
    # Step 4: Verify everything works
    if not verify_fresh_database():
        print_error("Database verification failed.")
        return False
    
    print_header("DATABASE RESET COMPLETED SUCCESSFULLY!")
    print_success("Your database has been completely reset")
    
    if backup_file:
        print_success(f"Your old data is backed up in: {backup_file}")
    
    print("\n🎉 Next steps:")
    print("1. Create a superuser: python manage.py createsuperuser")
    print("2. Load NASDAQ tickers: python manage.py load_nasdaq_only")
    print("3. Test your application: python manage.py runserver")
    
    return True

if __name__ == "__main__":
    success = main()
    
    if not success:
        print("\n💥 Database reset failed!")
        print("Please check the errors above.")
        sys.exit(1)