#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Django Migration Fix Script - Windows Compatible
Resolves complex migration state issues and database inconsistencies

This script will:
1. Analyze the current migration state
2. Fix database schema inconsistencies
3. Reset migrations if necessary
4. Apply clean migrations

Usage: python fix_migration_issue_windows.py
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
    print(f"ERROR: Django setup failed: {e}")
    sys.exit(1)

from django.core.management import call_command, execute_from_command_line
from django.db import connection, transaction
from django.conf import settings
from django.utils import timezone
from io import StringIO
import subprocess

def print_header(title):
    """Print a formatted header"""
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")

def print_step(message):
    """Print a step message"""
    print(f"\n[STEP] {message}")

def print_success(message):
    """Print a success message"""
    print(f"[SUCCESS] {message}")

def print_warning(message):
    """Print a warning message"""
    print(f"[WARNING] {message}")

def print_error(message):
    """Print an error message"""
    print(f"[ERROR] {message}")

def run_management_command(command, *args, **kwargs):
    """Run a Django management command and capture output"""
    old_stdout = sys.stdout
    old_stderr = sys.stderr
    
    stdout_capture = StringIO()
    stderr_capture = StringIO()
    
    try:
        sys.stdout = stdout_capture
        sys.stderr = stderr_capture
        
        call_command(command, *args, **kwargs)
        
        success = True
        output = stdout_capture.getvalue()
        error = stderr_capture.getvalue()
        
    except Exception as e:
        success = False
        output = stdout_capture.getvalue()
        error = str(e)
    finally:
        sys.stdout = old_stdout
        sys.stderr = old_stderr
    
    return success, output, error

def check_database_connection():
    """Check if database connection is working"""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            return True
    except Exception as e:
        print_error(f"Database connection failed: {e}")
        return False

def get_migration_status():
    """Get current migration status"""
    try:
        success, output, error = run_management_command('showmigrations', '--plan')
        if success:
            return output
        else:
            print_error(f"Failed to get migration status: {error}")
            return None
    except Exception as e:
        print_error(f"Error getting migration status: {e}")
        return None

def backup_database():
    """Create a database backup"""
    try:
        db_config = settings.DATABASES['default']
        
        if db_config['ENGINE'] == 'django.db.backends.mysql':
            backup_file = f"migration_backup_{timezone.now().strftime('%Y%m%d_%H%M%S')}.sql"
            
            cmd = [
                'mysqldump',
                f"--host={db_config.get('HOST', 'localhost')}",
                f"--port={db_config.get('PORT', '3306')}",
                f"--user={db_config.get('USER', 'root')}",
                f"--password={db_config.get('PASSWORD', '')}",
                db_config['NAME']
            ]
            
            with open(backup_file, 'w') as f:
                result = subprocess.run(cmd, stdout=f, stderr=subprocess.PIPE, text=True)
            
            if result.returncode == 0:
                print_success(f"Database backup created: {backup_file}")
                return backup_file
            else:
                print_error(f"Backup failed: {result.stderr}")
                return None
                
        elif db_config['ENGINE'] == 'django.db.backends.sqlite3':
            import shutil
            backup_file = f"db_backup_{timezone.now().strftime('%Y%m%d_%H%M%S')}.sqlite3"
            shutil.copy2(db_config['NAME'], backup_file)
            print_success(f"SQLite backup created: {backup_file}")
            return backup_file
            
    except Exception as e:
        print_error(f"Backup failed: {e}")
        return None

def reset_migrations():
    """Reset all migrations"""
    print_step("Resetting migrations...")
    
    try:
        # Get all apps with migrations
        apps_with_migrations = []
        
        for app_config in django.apps.apps.get_app_configs():
            app_name = app_config.name
            if app_name not in ['django.contrib.admin', 'django.contrib.auth', 
                               'django.contrib.contenttypes', 'django.contrib.sessions']:
                migrations_dir = Path(app_config.path) / 'migrations'
                if migrations_dir.exists():
                    apps_with_migrations.append(app_name)
        
        # Fake unapply all migrations
        for app_name in apps_with_migrations:
            success, output, error = run_management_command('migrate', app_name, 'zero', '--fake')
            if success:
                print_success(f"Reset migrations for {app_name}")
            else:
                print_error(f"Failed to reset {app_name}: {error}")
        
        # Reset built-in Django apps
        django_apps = ['contenttypes', 'auth', 'admin', 'sessions']
        for app_name in django_apps:
            success, output, error = run_management_command('migrate', app_name, 'zero', '--fake')
            if success:
                print_success(f"Reset Django app {app_name}")
        
        return True
        
    except Exception as e:
        print_error(f"Migration reset failed: {e}")
        return False

def recreate_database_schema():
    """Recreate database schema from scratch"""
    print_step("Recreating database schema...")
    
    try:
        with connection.cursor() as cursor:
            # Get all table names
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = DATABASE()
            """)
            
            tables = [row[0] for row in cursor.fetchall()]
            
            # Drop all tables
            cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
            for table in tables:
                cursor.execute(f"DROP TABLE IF EXISTS `{table}`")
            cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
            
            print_success(f"Dropped {len(tables)} tables")
        
        # Run migrate to create fresh schema
        success, output, error = run_management_command('migrate')
        
        if success:
            print_success("Database schema recreated successfully")
            return True
        else:
            print_error(f"Schema recreation failed: {error}")
            return False
            
    except Exception as e:
        print_error(f"Schema recreation failed: {e}")
        return False

def apply_migrations():
    """Apply all migrations"""
    print_step("Applying migrations...")
    
    try:
        success, output, error = run_management_command('migrate')
        
        if success:
            print_success("All migrations applied successfully")
            print("Migration output:")
            print(output)
            return True
        else:
            print_error(f"Migration failed: {error}")
            return False
            
    except Exception as e:
        print_error(f"Migration application failed: {e}")
        return False

def verify_migration_state():
    """Verify that migrations are in a good state"""
    print_step("Verifying migration state...")
    
    try:
        status = get_migration_status()
        if status:
            print("Current migration status:")
            print(status)
            
            # Check for any unapplied migrations
            if "[X]" in status or "[ ]" in status:
                unapplied = status.count("[ ]")
                applied = status.count("[X]")
                print_success(f"Applied: {applied}, Unapplied: {unapplied}")
                
                if unapplied == 0:
                    print_success("All migrations are applied")
                    return True
                else:
                    print_warning(f"{unapplied} migrations still need to be applied")
                    return False
            else:
                print_success("Migration state verified")
                return True
        else:
            print_error("Could not verify migration state")
            return False
            
    except Exception as e:
        print_error(f"Migration verification failed: {e}")
        return False

def main():
    """Main migration fix process"""
    print_header("Django Migration Fix - Windows Compatible")
    
    # Check database connection
    if not check_database_connection():
        print_error("Cannot proceed without database connection")
        return False
    
    print_success("Database connection verified")
    
    # Create backup
    backup_file = backup_database()
    if backup_file:
        print_success(f"Backup created: {backup_file}")
    else:
        print_warning("Could not create backup - proceeding anyway")
    
    # Try standard migration first
    print_step("Attempting standard migration...")
    if apply_migrations():
        if verify_migration_state():
            print_header("MIGRATION FIX COMPLETED SUCCESSFULLY")
            return True
    
    # If standard migration fails, try reset approach
    print_step("Standard migration failed, trying reset approach...")
    
    if not reset_migrations():
        print_error("Could not reset migrations")
        return False
    
    if not recreate_database_schema():
        print_error("Could not recreate database schema")
        return False
    
    if verify_migration_state():
        print_header("MIGRATION FIX COMPLETED SUCCESSFULLY")
        return True
    else:
        print_header("MIGRATION FIX FAILED")
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print_error("Migration fix interrupted by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        sys.exit(1)