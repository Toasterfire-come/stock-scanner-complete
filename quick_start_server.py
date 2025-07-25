#!/usr/bin/env python3
"""
Quick Django Server Startup
Uses existing .env configuration to start the server immediately
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    print("DJANGO SERVER - QUICK START")
    print("=" * 50)
    
    # Check if .env exists
    if not Path(".env").exists():
        print("ERROR: No .env file found!")
        print("Run 'python start_server_with_password.py' first to configure database")
        return
    
    print("SUCCESS: Found existing .env configuration")
    
    # Set Django settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stockscanner_django.settings')
    
    print("\nStarting Django development server...")
    print("Server will be available at: http://127.0.0.1:8000")
    print("Admin panel: http://127.0.0.1:8000/admin/")
    print("API status: http://127.0.0.1:8000/api/simple/status/")
    print("\nPress Ctrl+C to stop the server")
    print("-" * 50)
    
    try:
        # Start server directly
        subprocess.run(["python", "manage.py", "runserver", "0.0.0.0:8000"])
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"ERROR: Server failed to start: {e}")
        print("\nTroubleshooting:")
        print("- Check if database is running")
        print("- Verify .env configuration")
        print("- Run migrations: python manage.py migrate")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nServer startup cancelled by user")
    except Exception as e:
        print(f"ERROR: {e}")