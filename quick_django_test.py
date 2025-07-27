#!/usr/bin/env python3
"""
Quick Django Configuration Test
Simple diagnostic script to identify Django database configuration issues
"""

import os
import sys

def main():
    print("========================================")
    print("QUICK DJANGO CONFIGURATION TEST")
    print("========================================")
    print()
    
    # Check environment variables
    print("1. Environment Variables:")
    db_vars = ['DB_ENGINE', 'DB_NAME', 'DB_USER', 'DB_PASSWORD', 'DB_HOST', 'DB_PORT']
    found_any = False
    
    for var in db_vars:
        if var in os.environ:
            value = os.environ[var]
            if 'PASSWORD' in var and value:
                print(f"   {var} = {'*' * len(value)}")
            else:
                print(f"   {var} = {value}")
            found_any = True
    
    if not found_any:
        print("   No database environment variables found")
    print()
    
    # Check XAMPP
    print("2. XAMPP Check:")
    xampp_path = r"C:\xampp"
    if os.path.exists(xampp_path):
        print(f"   SUCCESS: XAMPP found at {xampp_path}")
        mysql_path = os.path.join(xampp_path, "mysql", "bin", "mysql.exe")
        if os.path.exists(mysql_path):
            print(f"   SUCCESS: MySQL client found")
        else:
            print(f"   ERROR: MySQL client not found")
    else:
        print(f"   ERROR: XAMPP not found at {xampp_path}")
    print()
    
    # Test Django settings import
    print("3. Django Settings Import:")
    try:
        # Add current directory to path
        current_dir = os.getcwd()
        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)
            
        # Import Django settings
        from stockscanner_django import settings
        print("   SUCCESS: Django settings imported")
        
        # Check database configuration
        if hasattr(settings, 'DATABASES'):
            db_config = settings.DATABASES.get('default', {})
            print("   Current Django database configuration:")
            print(f"     ENGINE: {db_config.get('ENGINE', 'Not set')}")
            print(f"     NAME: {db_config.get('NAME', 'Not set')}")
            print(f"     USER: {db_config.get('USER', 'Not set')}")
            print(f"     HOST: {db_config.get('HOST', 'Not set')}")
            print(f"     PORT: {db_config.get('PORT', 'Not set')}")
            
            password = db_config.get('PASSWORD', '')
            if password:
                print(f"     PASSWORD: (set, length: {len(password)})")
            else:
                print("     PASSWORD: (empty)")
        else:
            print("   ERROR: No DATABASES configuration found")
            
    except Exception as e:
        print(f"   ERROR: Cannot import Django settings: {e}")
    print()
    
    # Test direct MySQL connection
    print("4. Direct MySQL Test:")
    try:
        import subprocess
        mysql_exe = r"C:\xampp\mysql\bin\mysql.exe"
        
        if os.path.exists(mysql_exe):
            result = subprocess.run([
                mysql_exe, '-h', 'localhost', '-u', 'root', 
                '-e', 'SELECT "MySQL OK" AS status;'
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                print("   SUCCESS: MySQL connection works with root/no password")
            else:
                print(f"   ERROR: MySQL connection failed: {result.stderr}")
        else:
            print("   ERROR: MySQL executable not found")
            
    except Exception as e:
        print(f"   ERROR: MySQL test failed: {e}")
    print()
    
    print("========================================")
    print("DIAGNOSIS COMPLETE")
    print("========================================")
    print()
    print("If Django shows 'USER: django_user' but MySQL works with root:")
    print("Run: python fix_django_database_config_safe.py")
    print()

if __name__ == "__main__":
    main()