#!/usr/bin/env python3
"""
Simple MySQL Setup Script
Prompts for password and updates .env file
"""

import os
import getpass
from pathlib import Path

def main():
    print("MySQL Setup for Stock Scanner")
    print("=" * 40)
    
    # Get MySQL password
    password = getpass.getpass("Enter your MySQL password: ")
    
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
        if line.strip().startswith('# DB_ENGINE=django.db.backends.mysql') or line.strip().startswith('DB_ENGINE=django.db.backends.mysql'):
            updated_lines.append('DB_ENGINE=django.db.backends.mysql\n')
        elif line.strip().startswith('# DB_NAME=stockscanner_db'):
            updated_lines.append('DB_NAME=stockscanner_db\n')
        elif line.strip().startswith('# DB_USER=root') or line.strip().startswith('DB_USER=root'):
            updated_lines.append('DB_USER=root\n')
        elif line.strip().startswith('# DB_PASSWORD=StockScaner2010') or line.strip().startswith('DB_PASSWORD='):
            updated_lines.append(f'DB_PASSWORD={password}\n')
        elif line.strip().startswith('# DB_HOST=127.0.0.1') or line.strip().startswith('DB_HOST=127.0.0.1'):
            updated_lines.append('DB_HOST=127.0.0.1\n')
        elif line.strip().startswith('# DB_PORT=3306') or line.strip().startswith('DB_PORT=3306'):
            updated_lines.append('DB_PORT=3306\n')
        else:
            updated_lines.append(line)
    
    # Write updated .env file
    with open(env_file, 'w') as f:
        f.writelines(updated_lines)
    
    print("[SUCCESS] MySQL configuration updated in .env file")
    print("[RUN] You can now run: python manage.py runserver")
    print("\n[TIP] To switch back to SQLite, comment out the DB_* lines in .env")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[ERROR] Setup cancelled by user")
    except Exception as e:
        print(f"[ERROR] Error: {e}")