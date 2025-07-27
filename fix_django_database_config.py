#!/usr/bin/env python3
"""
Fix Django Database Configuration for XAMPP
Ensures Django uses correct XAMPP MySQL credentials
"""

import os
import sys
import subprocess

def clear_environment_variables():
    """Clear any existing database environment variables that might conflict"""
    print("🔧 Clearing conflicting environment variables...")
    
    # List of database environment variables that might conflict
    db_env_vars = [
        'DB_ENGINE', 'DB_NAME', 'DB_USER', 'DB_PASSWORD', 
        'DB_HOST', 'DB_PORT', 'DATABASE_URL'
    ]
    
    cleared = []
    for var in db_env_vars:
        if var in os.environ:
            old_value = os.environ[var]
            del os.environ[var]
            cleared.append(f"{var}={old_value}")
    
    if cleared:
        print(f"✅ Cleared: {', '.join(cleared)}")
    else:
        print("✅ No conflicting environment variables found")
    
    return len(cleared) > 0

def set_xampp_environment():
    """Set environment variables for XAMPP MySQL"""
    print("🔧 Setting XAMPP MySQL environment variables...")
    
    xampp_config = {
        'DB_ENGINE': 'django.db.backends.mysql',
        'DB_NAME': 'stockscanner',
        'DB_USER': 'root',
        'DB_PASSWORD': '',  # Empty password for XAMPP
        'DB_HOST': 'localhost',
        'DB_PORT': '3306'
    }
    
    for key, value in xampp_config.items():
        os.environ[key] = value
        print(f"✅ Set {key}={value}")

def test_mysql_connection():
    """Test MySQL connection using command line"""
    print("🔧 Testing MySQL connection...")
    
    try:
        # Test with XAMPP's MySQL client
        xampp_mysql = r"C:\xampp\mysql\bin\mysql.exe"
        if os.path.exists(xampp_mysql):
            result = subprocess.run([
                xampp_mysql, '-h', 'localhost', '-u', 'root', 
                '-e', 'SELECT "Connection successful" AS status;'
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                print("✅ MySQL connection successful")
                return True
            else:
                print(f"❌ MySQL connection failed: {result.stderr}")
                return False
        else:
            print("⚠️  XAMPP MySQL client not found")
            return False
            
    except Exception as e:
        print(f"❌ Connection test error: {e}")
        return False

def verify_database_exists():
    """Verify stockscanner database exists"""
    print("🔧 Verifying stockscanner database...")
    
    try:
        xampp_mysql = r"C:\xampp\mysql\bin\mysql.exe"
        if os.path.exists(xampp_mysql):
            result = subprocess.run([
                xampp_mysql, '-h', 'localhost', '-u', 'root', 
                '-e', 'SHOW DATABASES LIKE "stockscanner";'
            ], capture_output=True, text=True, timeout=10)
            
            if 'stockscanner' in result.stdout:
                print("✅ stockscanner database exists")
                return True
            else:
                print("❌ stockscanner database not found, creating...")
                # Create database
                create_result = subprocess.run([
                    xampp_mysql, '-h', 'localhost', '-u', 'root', 
                    '-e', 'CREATE DATABASE IF NOT EXISTS stockscanner;'
                ], capture_output=True, text=True, timeout=10)
                
                if create_result.returncode == 0:
                    print("✅ stockscanner database created")
                    return True
                else:
                    print(f"❌ Failed to create database: {create_result.stderr}")
                    return False
        else:
            print("⚠️  XAMPP MySQL client not found")
            return False
            
    except Exception as e:
        print(f"❌ Database verification error: {e}")
        return False

def test_django_connection():
    """Test Django database connection"""
    print("🔧 Testing Django database connection...")
    
    try:
        # Add current directory to Python path
        current_dir = os.getcwd()
        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)
        
        # Test Django database connection
        result = subprocess.run([
            sys.executable, 'manage.py', 'check', '--database', 'default'
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ Django database connection successful")
            return True
        else:
            print(f"❌ Django database connection failed")
            print(f"Error: {result.stderr}")
            print(f"Output: {result.stdout}")
            return False
            
    except Exception as e:
        print(f"❌ Django connection test error: {e}")
        return False

def run_migrations():
    """Run Django migrations"""
    print("🔧 Running Django migrations...")
    
    try:
        # Run makemigrations
        print("Running makemigrations...")
        result1 = subprocess.run([
            sys.executable, 'manage.py', 'makemigrations'
        ], capture_output=True, text=True, timeout=60)
        
        if result1.returncode == 0:
            print("✅ makemigrations completed")
        else:
            print(f"⚠️  makemigrations warnings: {result1.stdout}")
        
        # Run migrate
        print("Running migrate...")
        result2 = subprocess.run([
            sys.executable, 'manage.py', 'migrate'
        ], capture_output=True, text=True, timeout=120)
        
        if result2.returncode == 0:
            print("✅ Django migrations completed successfully")
            return True
        else:
            print(f"❌ Django migrations failed")
            print(f"Error: {result2.stderr}")
            print(f"Output: {result2.stdout}")
            return False
            
    except Exception as e:
        print(f"❌ Migration error: {e}")
        return False

def main():
    print("========================================")
    print("DJANGO DATABASE CONFIGURATION FIXER")
    print("========================================")
    print()
    
    print("This script will fix Django database configuration for XAMPP MySQL")
    print()
    
    # Step 1: Clear conflicting environment variables
    env_cleared = clear_environment_variables()
    print()
    
    # Step 2: Set XAMPP environment variables
    set_xampp_environment()
    print()
    
    # Step 3: Test MySQL connection
    if not test_mysql_connection():
        print("❌ MySQL connection failed. Please ensure:")
        print("1. XAMPP MySQL is running")
        print("2. MySQL service is started in XAMPP Control Panel")
        return False
    print()
    
    # Step 4: Verify database exists
    if not verify_database_exists():
        print("❌ Database verification failed")
        return False
    print()
    
    # Step 5: Test Django connection
    if not test_django_connection():
        print("❌ Django connection test failed")
        print("Trying alternative configuration...")
        
        # Try with alternative settings
        os.environ['DB_PASSWORD'] = ''  # Ensure empty password
        os.environ['DB_HOST'] = '127.0.0.1'  # Try IP instead of localhost
        
        if not test_django_connection():
            print("❌ Django connection still failing")
            return False
    print()
    
    # Step 6: Run migrations
    if not run_migrations():
        print("❌ Migrations failed")
        return False
    print()
    
    print("========================================")
    print("🎉 CONFIGURATION FIXED SUCCESSFULLY!")
    print("========================================")
    print()
    print("✅ Database: stockscanner")
    print("✅ User: root")
    print("✅ Password: (empty)")
    print("✅ Host: localhost:3306")
    print("✅ Django migrations: completed")
    print()
    print("Next steps:")
    print("1. Start Django server: python manage.py runserver")
    print("2. Start stock scheduler: python start_stock_scheduler.py --background")
    print("3. Create admin user: python manage.py createsuperuser")
    print()
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if not success:
            print("\n❌ Configuration fix failed")
            print("Please check the errors above and try again")
            sys.exit(1)
        else:
            print("✅ All done! Django is ready to use with XAMPP MySQL")
    except KeyboardInterrupt:
        print("\n⚠️  Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)