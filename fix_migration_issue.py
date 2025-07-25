#!/usr/bin/env python3
"""
Django Migration Fix Script
Resolves complex migration state issues and database inconsistencies

This script will:
1. Analyze the current migration state
2. Fix database schema inconsistencies
3. Reset migrations if necessary
4. Apply clean migrations

Usage: python fix_migration_issue.py
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

from django.core.management import call_command, execute_from_command_line
from django.db import connection, transaction
from django.conf import settings
from django.utils import timezone
from io import StringIO
import subprocess

class MigrationFixer:
    def __init__(self):
        self.apps_to_fix = ['admin', 'auth', 'contenttypes', 'core', 'emails', 'sessions', 'stocks']
        
    def print_header(self, message):
        print(f"\n{'='*70}")
        print(f"🔧 {message}")
        print('='*70)
    
    def print_step(self, message):
        print(f"\n📋 {message}")
        
    def print_success(self, message):
        print(f"✅ {message}")
        
    def print_warning(self, message):
        print(f"⚠️  {message}")
        
    def print_error(self, message):
        print(f"❌ {message}")
    
    def check_database_connection(self):
        """Test database connectivity"""
        self.print_step("Testing database connection...")
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                if result and result[0] == 1:
                    self.print_success("Database connection successful")
                    return True
        except Exception as e:
            self.print_error(f"Database connection failed: {e}")
            return False
    
    def get_migration_status(self):
        """Get current migration status"""
        self.print_step("Checking migration status...")
        try:
            output = StringIO()
            call_command('showmigrations', stdout=output)
            migration_status = output.getvalue()
            print(migration_status)
            return migration_status
        except Exception as e:
            self.print_error(f"Failed to get migration status: {e}")
            return None
    
    def check_django_tables(self):
        """Check if Django core tables exist"""
        self.print_step("Checking Django core tables...")
        try:
            with connection.cursor() as cursor:
                # Check for django_migrations table
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM information_schema.tables 
                    WHERE table_schema = DATABASE() 
                    AND table_name = 'django_migrations'
                """)
                migrations_exists = cursor.fetchone()[0] > 0
                
                # Check for django_content_type table
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM information_schema.tables 
                    WHERE table_schema = DATABASE() 
                    AND table_name = 'django_content_type'
                """)
                content_type_exists = cursor.fetchone()[0] > 0
                
                self.print_success(f"django_migrations table: {'EXISTS' if migrations_exists else 'MISSING'}")
                self.print_success(f"django_content_type table: {'EXISTS' if content_type_exists else 'MISSING'}")
                
                return migrations_exists, content_type_exists
        except Exception as e:
            self.print_error(f"Failed to check Django tables: {e}")
            return False, False
    
    def check_content_type_schema(self):
        """Check django_content_type table schema"""
        self.print_step("Checking django_content_type table schema...")
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT COLUMN_NAME 
                    FROM information_schema.COLUMNS 
                    WHERE table_schema = DATABASE() 
                    AND table_name = 'django_content_type'
                    ORDER BY ORDINAL_POSITION
                """)
                columns = [row[0] for row in cursor.fetchall()]
                
                print(f"Current columns: {columns}")
                
                # Check if 'name' column exists (it shouldn't in newer Django versions)
                has_name_column = 'name' in columns
                has_required_columns = all(col in columns for col in ['id', 'app_label', 'model'])
                
                self.print_success(f"Has 'name' column (deprecated): {has_name_column}")
                self.print_success(f"Has required columns: {has_required_columns}")
                
                return has_name_column, has_required_columns
        except Exception as e:
            self.print_error(f"Failed to check content type schema: {e}")
            return None, None
    
    def backup_database(self):
        """Create database backup"""
        self.print_step("Creating database backup...")
        try:
            db_settings = settings.DATABASES['default']
            backup_file = f"migration_backup_{timezone.now().strftime('%Y%m%d_%H%M%S')}.sql"
            
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
                self.print_success(f"Database backup created: {backup_file}")
                return backup_file
            else:
                self.print_error(f"Backup failed: {result.stderr}")
                return None
        except Exception as e:
            self.print_error(f"Backup failed: {e}")
            return None
    
    def clear_migration_history(self):
        """Clear migration history from django_migrations table"""
        self.print_step("Clearing migration history...")
        try:
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM django_migrations")
                self.print_success("Migration history cleared")
                return True
        except Exception as e:
            self.print_error(f"Failed to clear migration history: {e}")
            return False
    
    def fix_content_type_table(self):
        """Fix django_content_type table if it has the deprecated 'name' column"""
        self.print_step("Fixing django_content_type table...")
        try:
            has_name_column, has_required_columns = self.check_content_type_schema()
            
            if has_name_column:
                self.print_warning("Removing deprecated 'name' column from django_content_type")
                with connection.cursor() as cursor:
                    cursor.execute("ALTER TABLE django_content_type DROP COLUMN name")
                    self.print_success("Deprecated 'name' column removed")
            
            return True
        except Exception as e:
            self.print_error(f"Failed to fix content type table: {e}")
            return False
    
    def recreate_django_tables(self):
        """Recreate Django core tables"""
        self.print_step("Recreating Django core tables...")
        try:
            with connection.cursor() as cursor:
                # Drop existing tables if they exist
                cursor.execute("DROP TABLE IF EXISTS django_migrations")
                cursor.execute("DROP TABLE IF EXISTS django_content_type")
                cursor.execute("DROP TABLE IF EXISTS django_admin_log")
                cursor.execute("DROP TABLE IF EXISTS auth_permission")
                cursor.execute("DROP TABLE IF EXISTS auth_group_permissions")
                cursor.execute("DROP TABLE IF EXISTS auth_user_groups")
                cursor.execute("DROP TABLE IF EXISTS auth_user_user_permissions")
                cursor.execute("DROP TABLE IF EXISTS auth_group")
                cursor.execute("DROP TABLE IF EXISTS auth_user")
                cursor.execute("DROP TABLE IF EXISTS django_session")
                
                self.print_success("Existing Django tables dropped")
            
            # Run initial migrations
            self.print_step("Creating fresh Django tables...")
            call_command('migrate', verbosity=2)
            self.print_success("Fresh Django tables created")
            return True
            
        except Exception as e:
            self.print_error(f"Failed to recreate Django tables: {e}")
            return False
    
    def fake_initial_migrations(self):
        """Fake the initial migrations for apps that already have tables"""
        self.print_step("Faking initial migrations...")
        try:
            # First, apply core Django migrations
            for app in ['contenttypes', 'auth', 'admin', 'sessions']:
                try:
                    call_command('migrate', app, '--fake-initial', verbosity=1)
                    self.print_success(f"Faked initial migrations for {app}")
                except Exception as e:
                    self.print_warning(f"Could not fake {app} migrations: {e}")
            
            # Then handle custom apps
            for app in ['core', 'emails', 'stocks']:
                try:
                    call_command('migrate', app, '--fake-initial', verbosity=1)
                    self.print_success(f"Faked initial migrations for {app}")
                except Exception as e:
                    self.print_warning(f"Could not fake {app} migrations: {e}")
            
            return True
        except Exception as e:
            self.print_error(f"Failed to fake initial migrations: {e}")
            return False
    
    def apply_remaining_migrations(self):
        """Apply any remaining migrations"""
        self.print_step("Applying remaining migrations...")
        try:
            call_command('migrate', verbosity=2)
            self.print_success("All migrations applied successfully")
            return True
        except Exception as e:
            self.print_error(f"Failed to apply remaining migrations: {e}")
            return False
    
    def verify_migration_state(self):
        """Verify the final migration state"""
        self.print_step("Verifying migration state...")
        try:
            output = StringIO()
            call_command('showmigrations', stdout=output)
            migration_status = output.getvalue()
            
            # Check if all migrations are applied
            unapplied_found = False
            for line in migration_status.split('\n'):
                if '[ ]' in line:  # Unapplied migration
                    unapplied_found = True
                    self.print_warning(f"Unapplied migration: {line.strip()}")
            
            if not unapplied_found:
                self.print_success("All migrations are applied!")
                return True
            else:
                self.print_warning("Some migrations are still unapplied")
                return False
                
        except Exception as e:
            self.print_error(f"Failed to verify migration state: {e}")
            return False
    
    def run_fix(self):
        """Run the complete migration fix process"""
        self.print_header("DJANGO MIGRATION FIX TOOL")
        
        # Step 1: Check database connection
        if not self.check_database_connection():
            return False
        
        # Step 2: Get current migration status
        self.get_migration_status()
        
        # Step 3: Check Django tables
        migrations_exists, content_type_exists = self.check_django_tables()
        
        # Step 4: Create backup
        backup_file = self.backup_database()
        if not backup_file:
            self.print_warning("Proceeding without backup (not recommended)")
        
        # Step 5: Determine fix strategy
        if not migrations_exists or not content_type_exists:
            self.print_step("Missing core Django tables - recreating from scratch")
            if not self.recreate_django_tables():
                return False
        else:
            # Step 6: Fix content type table if needed
            if not self.fix_content_type_table():
                return False
            
            # Step 7: Clear migration history and fake initial
            if not self.clear_migration_history():
                return False
            
            if not self.fake_initial_migrations():
                return False
        
        # Step 8: Apply remaining migrations
        if not self.apply_remaining_migrations():
            return False
        
        # Step 9: Verify final state
        if not self.verify_migration_state():
            return False
        
        self.print_header("MIGRATION FIX COMPLETED SUCCESSFULLY!")
        self.print_success("Your Django project should now be ready to use")
        
        if backup_file:
            self.print_success(f"Database backup saved as: {backup_file}")
        
        return True

if __name__ == "__main__":
    fixer = MigrationFixer()
    success = fixer.run_fix()
    
    if success:
        print("\n🎉 Migration fix completed successfully!")
        print("\nNext steps:")
        print("1. Test your Django application: python manage.py runserver")
        print("2. Create a superuser: python manage.py createsuperuser")
        print("3. Load your stock data: python manage.py load_nasdaq_only")
    else:
        print("\n💥 Migration fix failed!")
        print("Please check the errors above and try manual fixes if needed.")
        sys.exit(1)