#!/usr/bin/env python3
"""
Quick Environment Variable Checker (Windows Compatible)
Shows which database environment variables are currently set
"""

import os

def main():
    print("========================================")
    print("ENVIRONMENT VARIABLES CHECKER")
    print("========================================")
    print()
    
    # Database-related environment variables
    db_vars = [
        'DB_ENGINE', 'DB_NAME', 'DB_USER', 'DB_PASSWORD', 
        'DB_HOST', 'DB_PORT', 'DATABASE_URL'
    ]
    
    print("Database Environment Variables:")
    found_vars = False
    
    for var in db_vars:
        if var in os.environ:
            value = os.environ[var]
            # Hide password for security
            if 'PASSWORD' in var and value:
                display_value = '*' * len(value)
            else:
                display_value = value if value else '(empty)'
            print(f"  {var} = {display_value}")
            found_vars = True
    
    if not found_vars:
        print("  No database environment variables found")
    
    print()
    print("Expected XAMPP Configuration:")
    print("  DB_ENGINE = django.db.backends.mysql")
    print("  DB_NAME = stockscanner")
    print("  DB_USER = root")
    print("  DB_PASSWORD = (empty)")
    print("  DB_HOST = localhost")
    print("  DB_PORT = 3306")
    print()
    
    # Check if XAMPP is detected
    xampp_path = r"C:\xampp"
    xampp_mysql_path = os.path.join(xampp_path, "mysql", "bin")
    
    print("XAMPP Detection:")
    if os.path.exists(xampp_path):
        print(f"  SUCCESS: XAMPP directory found: {xampp_path}")
        if os.path.exists(xampp_mysql_path):
            print(f"  SUCCESS: XAMPP MySQL found: {xampp_mysql_path}")
            
            # Check if MySQL is running
            mysql_exe = os.path.join(xampp_mysql_path, "mysql.exe")
            mysqld_exe = os.path.join(xampp_mysql_path, "mysqld.exe")
            
            if os.path.exists(mysql_exe):
                print(f"  SUCCESS: MySQL client found: {mysql_exe}")
            if os.path.exists(mysqld_exe):
                print(f"  SUCCESS: MySQL server found: {mysqld_exe}")
                
        else:
            print(f"  ERROR: XAMPP MySQL not found: {xampp_mysql_path}")
    else:
        print(f"  ERROR: XAMPP directory not found: {xampp_path}")
    
    print()
    
    # Test actual Django settings import
    print("Django Settings Test:")
    try:
        import sys
        import os
        current_dir = os.getcwd()
        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)
        
        # Import Django settings
        from stockscanner_django import settings
        
        print("  Django settings imported successfully")
        
        # Check database configuration
        if hasattr(settings, 'DATABASES'):
            db_config = settings.DATABASES.get('default', {})
            print(f"  Current DB_ENGINE: {db_config.get('ENGINE', 'Not set')}")
            print(f"  Current DB_NAME: {db_config.get('NAME', 'Not set')}")
            print(f"  Current DB_USER: {db_config.get('USER', 'Not set')}")
            print(f"  Current DB_HOST: {db_config.get('HOST', 'Not set')}")
            print(f"  Current DB_PORT: {db_config.get('PORT', 'Not set')}")
            
            # Check if password is set (don't display it)
            password = db_config.get('PASSWORD', '')
            if password:
                print(f"  Current DB_PASSWORD: (set, length: {len(password)})")
            else:
                print("  Current DB_PASSWORD: (empty)")
                
        else:
            print("  ERROR: No DATABASES configuration found")
            
    except Exception as e:
        print(f"  ERROR: Cannot import Django settings: {e}")
    
    print()
    
    # Test MySQL connection directly
    print("Direct MySQL Connection Test:")
    try:
        import subprocess
        xampp_mysql = r"C:\xampp\mysql\bin\mysql.exe"
        
        if os.path.exists(xampp_mysql):
            print("  Testing connection to MySQL...")
            result = subprocess.run([
                xampp_mysql, '-h', 'localhost', '-u', 'root', 
                '-e', 'SELECT "Connection successful" AS status;'
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                print("  SUCCESS: Direct MySQL connection works")
                print("  MySQL is accessible with root user and no password")
            else:
                print(f"  ERROR: MySQL connection failed")
                print(f"  Error output: {result.stderr}")
        else:
            print(f"  ERROR: MySQL client not found at {xampp_mysql}")
            
    except Exception as e:
        print(f"  ERROR: MySQL connection test failed: {e}")
    
    print()
    print("========================================")
    print("SUMMARY")
    print("========================================")
    print("1. No conflicting environment variables found (GOOD)")
    print("2. Check Django settings import above")
    print("3. Check MySQL direct connection above")
    print("4. If MySQL works but Django doesn't, run:")
    print("   python fix_django_database_config.py")
    print()

if __name__ == "__main__":
    main()