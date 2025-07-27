#!/usr/bin/env python3
"""
Fix Django Database Configuration for Linux Environment
Forces Django to use correct MySQL credentials when XAMPP detection fails
"""

import os
import sys
import subprocess

def main():
    print("========================================")
    print("DJANGO DATABASE CONFIGURATION FIXER")
    print("(Linux Environment)")
    print("========================================")
    print()
    
    print("Setting environment variables to override Django settings...")
    
    # Force correct database settings via environment variables
    # These will override the Django settings.py configuration
    correct_settings = {
        'DB_ENGINE': 'django.db.backends.mysql',
        'DB_NAME': 'stockscanner',
        'DB_USER': 'root',
        'DB_PASSWORD': '',  # Empty password
        'DB_HOST': 'localhost',
        'DB_PORT': '3306'
    }
    
    for key, value in correct_settings.items():
        os.environ[key] = value
        print(f"SUCCESS: Set {key}={value}")
    
    print()
    print("Testing Django database connection with new settings...")
    
    try:
        # Test Django database connection
        result = subprocess.run([
            sys.executable, 'manage.py', 'check', '--database', 'default'
        ], capture_output=True, text=True, timeout=30, env=os.environ)
        
        if result.returncode == 0:
            print("SUCCESS: Django database connection working!")
            print()
            
            print("Running Django migrations...")
            # Run migrations
            migration_result = subprocess.run([
                sys.executable, 'manage.py', 'migrate'
            ], capture_output=True, text=True, timeout=120, env=os.environ)
            
            if migration_result.returncode == 0:
                print("SUCCESS: Django migrations completed!")
                print()
                print("========================================")
                print("CONFIGURATION FIXED!")
                print("========================================")
                print()
                print("Database: stockscanner")
                print("User: root")
                print("Password: (empty)")
                print("Host: localhost:3306")
                print()
                print("Next steps:")
                print("1. Export these environment variables in your shell:")
                print()
                for key, value in correct_settings.items():
                    print(f"export {key}='{value}'")
                print()
                print("2. Then run Django:")
                print("python3 manage.py runserver")
                print()
                return True
            else:
                print("ERROR: Django migrations failed")
                print(f"Migration error: {migration_result.stderr}")
                print(f"Migration output: {migration_result.stdout}")
                return False
        else:
            print("ERROR: Django database connection failed")
            print(f"Connection error: {result.stderr}")
            print(f"Connection output: {result.stdout}")
            print()
            print("Possible solutions:")
            print("1. Ensure MySQL is running: sudo systemctl start mysql")
            print("2. Create database: mysql -u root -e 'CREATE DATABASE stockscanner;'")
            print("3. Check MySQL user permissions")
            return False
            
    except Exception as e:
        print(f"ERROR: Database test failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        print()
        print("Configuration fix failed. Please check MySQL is running and accessible.")
        sys.exit(1)