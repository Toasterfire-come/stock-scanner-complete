#!/usr/bin/env python3
"""
Quick Environment Variable Checker
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
        print(f"  ✅ XAMPP directory found: {xampp_path}")
        if os.path.exists(xampp_mysql_path):
            print(f"  ✅ XAMPP MySQL found: {xampp_mysql_path}")
        else:
            print(f"  ❌ XAMPP MySQL not found: {xampp_mysql_path}")
    else:
        print(f"  ❌ XAMPP directory not found: {xampp_path}")
    
    print()

if __name__ == "__main__":
    main()