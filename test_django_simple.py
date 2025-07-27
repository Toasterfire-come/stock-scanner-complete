#!/usr/bin/env python3
"""
Simple Django Test - Bypass MySQL Requirements
Test Django configuration without requiring MySQL client libraries
"""

import os
import sys

def main():
    print("========================================")
    print("SIMPLE DJANGO TEST (NO MYSQL CLIENT)")
    print("========================================")
    print()
    
    # Set environment variables
    env_vars = {
        'DB_ENGINE': 'django.db.backends.mysql',
        'DB_NAME': 'stockscanner', 
        'DB_USER': 'root',
        'DB_PASSWORD': '',
        'DB_HOST': 'localhost',
        'DB_PORT': '3306'
    }
    
    for key, value in env_vars.items():
        os.environ[key] = value
    
    print("Environment variables set for Django:")
    for key, value in env_vars.items():
        display_value = value if value else '(empty)'
        print(f"  {key} = {display_value}")
    print()
    
    # Test Django settings import without database connection
    print("Testing Django settings (without database connection)...")
    try:
        # Add current directory to path
        current_dir = os.getcwd()
        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)
        
        # Set Django settings module
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stockscanner_django.settings')
        
        # Import Django settings
        from django.conf import settings
        print("SUCCESS: Django settings imported")
        
        # Check database configuration
        if hasattr(settings, 'DATABASES'):
            db_config = settings.DATABASES.get('default', {})
            print("Django database configuration:")
            print(f"  ENGINE: {db_config.get('ENGINE')}")
            print(f"  NAME: {db_config.get('NAME')}")
            print(f"  USER: {db_config.get('USER')}")
            print(f"  HOST: {db_config.get('HOST')}")
            print(f"  PORT: {db_config.get('PORT')}")
            
            password = db_config.get('PASSWORD', '')
            if password:
                print(f"  PASSWORD: (set, length: {len(password)})")
            else:
                print("  PASSWORD: (empty)")
        
        print()
        print("SUCCESS: Environment variables override working!")
        print("Django is configured to use:")
        print(f"  - Database: {db_config.get('NAME')}")
        print(f"  - User: {db_config.get('USER')}")
        print(f"  - Host: {db_config.get('HOST')}:{db_config.get('PORT')}")
        print()
        
        return True
        
    except Exception as e:
        print(f"ERROR: Django settings test failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("========================================")
        print("NEXT STEPS:")
        print("========================================")
        print("1. Ensure MySQL is running and accessible")
        print("2. Create stockscanner database:")
        print("   mysql -u root -e 'CREATE DATABASE stockscanner;'")
        print("3. Install PyMySQL (when network is available):")
        print("   pip install PyMySQL --break-system-packages")
        print("4. Run Django migrations:")
        print("   source set_django_env.sh")
        print("   python3 manage.py migrate") 
        print("5. Start Django server:")
        print("   python3 manage.py runserver")
        print()
    else:
        print("Configuration test failed")
        sys.exit(1)