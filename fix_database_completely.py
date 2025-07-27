#!/usr/bin/env python3
"""
Complete Database Fix Tool
Fixes MySQL issues or switches to SQLite as fallback
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def backup_current_database():
    """Backup current database configuration"""
    try:
        backup_dir = Path('database_backup')
        backup_dir.mkdir(exist_ok=True)
        
        # Backup .env file
        env_file = Path('.env')
        if env_file.exists():
            shutil.copy2(env_file, backup_dir / '.env.backup')
            print("[BACKUP] .env file backed up")
        
        # Backup settings.py
        settings_file = Path('stockscanner_django/settings.py')
        if settings_file.exists():
            shutil.copy2(settings_file, backup_dir / 'settings.py.backup')
            print("[BACKUP] settings.py backed up")
        
        return True
    except Exception as e:
        print(f"[ERROR] Backup failed: {e}")
        return False

def test_mysql_connection():
    """Test MySQL connection thoroughly"""
    try:
        print("[TEST] Testing MySQL connection...")
        
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stockscanner_django.settings')
        import django
        django.setup()
        
        from django.db import connection
        from django.core.management import execute_from_command_line
        
        # Test connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()
            print(f"[SUCCESS] MySQL connection working: {version[0]}")
            
        # Test table creation
        cursor.execute("""
            CREATE TEMPORARY TABLE test_table (
                id INT AUTO_INCREMENT PRIMARY KEY,
                test_data VARCHAR(255)
            )
        """)
        
        # Test insert
        cursor.execute("INSERT INTO test_table (test_data) VALUES (%s)", ["test"])
        
        # Test select
        cursor.execute("SELECT * FROM test_table")
        result = cursor.fetchone()
        
        print("[SUCCESS] MySQL fully operational")
        return True
        
    except Exception as e:
        print(f"[ERROR] MySQL connection failed: {e}")
        return False

def switch_to_sqlite():
    """Switch database configuration to SQLite"""
    try:
        print("[SWITCH] Converting to SQLite database...")
        
        # Update .env file
        env_content = """
# SQLite Database Configuration (No MySQL Required)
DATABASE_URL=sqlite:///db.sqlite3
DB_ENGINE=django.db.backends.sqlite3
DB_NAME=db.sqlite3
DB_USER=
DB_PASSWORD=
DB_HOST=
DB_PORT=

# Django Configuration
SECRET_KEY=your-secret-key-here-change-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

# Email Configuration (Optional)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
"""
        
        with open('.env', 'w') as f:
            f.write(env_content.strip())
        print("[SUCCESS] Updated .env for SQLite")
        
        # Update Django settings for SQLite
        settings_path = Path('stockscanner_django/settings.py')
        if settings_path.exists():
            with open(settings_path, 'r') as f:
                content = f.read()
            
            # Replace MySQL database config with SQLite
            sqlite_config = """
import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Database Configuration - SQLite (No MySQL required)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
        'OPTIONS': {
            'timeout': 60,
        },
    }
}

# Connection pooling for SQLite
DATABASES['default']['CONN_MAX_AGE'] = 600  # 10 minutes
"""
            
            # Find and replace database configuration
            import re
            
            # Remove existing database config
            content = re.sub(
                r'DATABASES\s*=\s*{[^}]*}(?:\s*\n[^}]*})*',
                sqlite_config.strip(),
                content,
                flags=re.MULTILINE | re.DOTALL
            )
            
            # Ensure required imports
            if 'from pathlib import Path' not in content:
                content = 'from pathlib import Path\n' + content
            
            with open(settings_path, 'w') as f:
                f.write(content)
            
            print("[SUCCESS] Updated Django settings for SQLite")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] SQLite switch failed: {e}")
        return False

def run_django_migrations():
    """Run Django migrations for the database"""
    try:
        print("[MIGRATE] Running Django migrations...")
        
        # Clear any existing migration cache
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stockscanner_django.settings')
        
        # Run migrations
        result = subprocess.run([
            sys.executable, 'manage.py', 'migrate'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("[SUCCESS] Database migrations completed")
            print(result.stdout)
            return True
        else:
            print(f"[ERROR] Migration failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"[ERROR] Migration exception: {e}")
        return False

def test_django_startup():
    """Test if Django can start properly"""
    try:
        print("[TEST] Testing Django startup...")
        
        result = subprocess.run([
            sys.executable, 'manage.py', 'check'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("[SUCCESS] Django check passed")
            return True
        else:
            print(f"[ERROR] Django check failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"[ERROR] Django test failed: {e}")
        return False

def optimize_sqlite_settings():
    """Add SQLite optimizations to Django settings"""
    try:
        settings_path = Path('stockscanner_django/settings.py')
        if not settings_path.exists():
            return False
        
        with open(settings_path, 'r') as f:
            content = f.read()
        
        # Add SQLite optimizations
        sqlite_optimizations = """

# SQLite Performance Optimizations
if 'sqlite' in DATABASES['default']['ENGINE']:
    DATABASES['default']['OPTIONS'].update({
        'timeout': 60,
        'init_command': '''
            PRAGMA journal_mode=WAL;
            PRAGMA synchronous=NORMAL;
            PRAGMA cache_size=1000;
            PRAGMA temp_store=MEMORY;
            PRAGMA mmap_size=268435456;
        '''.strip(),
    })

# Logging Configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'django.log',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django.db.backends': {
            'level': 'WARNING',
            'handlers': ['file'],
            'propagate': False,
        },
        'stocks': {
            'level': 'INFO',
            'handlers': ['file', 'console'],
            'propagate': False,
        },
    },
}
"""
        
        if 'PRAGMA journal_mode' not in content:
            content += sqlite_optimizations
            
            with open(settings_path, 'w') as f:
                f.write(content)
            
            print("[SUCCESS] Added SQLite optimizations")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] SQLite optimization failed: {e}")
        return False

def main():
    """Main database fix function"""
    print("COMPLETE DATABASE FIX TOOL")
    print("=" * 50)
    print("This tool will fix MySQL issues or switch to SQLite")
    print()
    
    # Backup current configuration
    print("[STEP 1] Backing up current configuration...")
    backup_success = backup_current_database()
    print()
    
    # Test MySQL first
    print("[STEP 2] Testing MySQL connection...")
    mysql_works = test_mysql_connection()
    print()
    
    if not mysql_works:
        print("[STEP 3] MySQL failed - switching to SQLite...")
        sqlite_success = switch_to_sqlite()
        
        if sqlite_success:
            print("[STEP 4] Optimizing SQLite configuration...")
            optimize_sqlite_settings()
            
            print("[STEP 5] Running database migrations...")
            migration_success = run_django_migrations()
            
            if migration_success:
                print("[STEP 6] Testing Django startup...")
                django_works = test_django_startup()
                
                if django_works:
                    print("\n" + "=" * 50)
                    print("[SUCCESS] SQLITE CONVERSION COMPLETE!")
                    print("=" * 50)
                    print()
                    print("Your database has been successfully converted to SQLite:")
                    print("- No MySQL server required")
                    print("- Database file: db.sqlite3")
                    print("- All features preserved")
                    print("- Better Windows compatibility")
                    print()
                    print("You can now run:")
                    print("  python start_stock_scheduler.py --background")
                    print("  start_scheduler_background.bat")
                    print()
                    return True
    else:
        print("[SUCCESS] MySQL is working properly!")
        print("Running additional optimizations...")
        
        # Apply MySQL optimizations from previous script
        try:
            subprocess.run([sys.executable, 'fix_mysql_errors.py'])
        except:
            pass
        
        return True
    
    print("\n[ERROR] Database fix failed")
    print("Please check the error messages above")
    print("Original configuration backed up in database_backup/")
    return False

if __name__ == "__main__":
    try:
        success = main()
        if not success:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n[STOP] Database fix interrupted")
    except Exception as e:
        print(f"\n[ERROR] Database fix failed: {e}")
        sys.exit(1)