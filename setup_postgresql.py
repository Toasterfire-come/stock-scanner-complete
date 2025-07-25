#!/usr/bin/env python3
"""
Simple PostgreSQL Setup Script
Prompts for password and updates .env file
"""

import os
import getpass
from pathlib import Path

def main():
    print("PostgreSQL Setup for Stock Scanner")
    print("=" * 40)
    
    # Get PostgreSQL password
    password = getpass.getpass("Enter your PostgreSQL password: ")
    
    if not password:
        print("No password entered. Using SQLite instead.")
        return
    
    # Read current .env file
    env_file = Path('.env')
    if not env_file.exists():
        print("Error: .env file not found!")
        return
    
    with open(env_file, 'r') as f:
        lines = f.readlines()
    
    # Update the .env file
    updated_lines = []
    for line in lines:
        if line.strip().startswith('# DB_ENGINE=django.db.backends.postgresql'):
            updated_lines.append('DB_ENGINE=django.db.backends.postgresql\n')
        elif line.strip().startswith('# DB_NAME=stockscanner_db'):
            updated_lines.append('DB_NAME=stockscanner_db\n')
        elif line.strip().startswith('# DB_USER=postgres'):
            updated_lines.append('DB_USER=postgres\n')
        elif line.strip().startswith('# DB_PASSWORD=your_postgresql_password_here'):
            updated_lines.append(f'DB_PASSWORD={password}\n')
        elif line.strip().startswith('# DB_HOST=127.0.0.1'):
            updated_lines.append('DB_HOST=127.0.0.1\n')
        elif line.strip().startswith('# DB_PORT=5432'):
            updated_lines.append('DB_PORT=5432\n')
        else:
            updated_lines.append(line)
    
    # Write updated .env file
    with open(env_file, 'w') as f:
        f.writelines(updated_lines)
    
    print("✅ PostgreSQL configuration updated in .env file")
    print("🚀 You can now run: python manage.py runserver")
    print("\n💡 To switch back to SQLite, comment out the DB_* lines in .env")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n❌ Setup cancelled by user")
    except Exception as e:
        print(f"❌ Error: {e}")