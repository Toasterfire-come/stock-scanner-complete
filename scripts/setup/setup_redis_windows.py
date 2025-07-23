#!/usr/bin/env python3
"""
📦 REDIS SETUP FOR WINDOWS
===========================
Helps Windows users install and configure Redis for the stock scanner.
"""

import os
import sys
import subprocess
import requests
import zipfile
import shutil
from pathlib import Path

def check_redis_running():
    """Check if Redis is already running"""
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, db=0)
        r.ping()
        print("✅ Redis is already running!")
        return True
    except Exception:
        print("❌ Redis is not running")
        return False

def download_redis_windows():
    """Download Redis for Windows"""
    print("📦 Downloading Redis for Windows...")
    
    # Redis download URL (using memurai as it's Redis-compatible for Windows)
    redis_url = "https://github.com/microsoftarchive/redis/releases/download/win-3.0.504/Redis-x64-3.0.504.zip"
    redis_zip = "redis-windows.zip"
    
    try:
        response = requests.get(redis_url)
        with open(redis_zip, 'wb') as f:
            f.write(response.content)
        print("✅ Redis downloaded successfully!")
        return redis_zip
    except Exception as e:
        print(f"❌ Failed to download Redis: {e}")
        return None

def extract_and_setup_redis(zip_path):
    """Extract and setup Redis"""
    print("📂 Extracting Redis...")
    
    redis_dir = Path("redis-server")
    if redis_dir.exists():
        shutil.rmtree(redis_dir)
    
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(redis_dir)
        
        print("✅ Redis extracted successfully!")
        
        # Find redis-server.exe
        redis_exe = None
        for root, dirs, files in os.walk(redis_dir):
            if "redis-server.exe" in files:
                redis_exe = os.path.join(root, "redis-server.exe")
                break
        
        if redis_exe:
            print(f"📍 Redis server found at: {redis_exe}")
            return redis_exe
        else:
            print("❌ redis-server.exe not found in extracted files")
            return None
            
    except Exception as e:
        print(f"❌ Failed to extract Redis: {e}")
        return None

def start_redis_server(redis_exe):
    """Start Redis server"""
    print("🚀 Starting Redis server...")
    
    try:
        # Start Redis in the background
        process = subprocess.Popen([redis_exe], 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE,
                                 creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0)
        
        # Wait a moment for Redis to start
        import time
        time.sleep(3)
        
        # Check if it's running
        if check_redis_running():
            print("✅ Redis server started successfully!")
            print(f"🔗 Redis PID: {process.pid}")
            return True
        else:
            print("❌ Redis failed to start properly")
            return False
            
    except Exception as e:
        print(f"❌ Failed to start Redis: {e}")
        return False

def create_redis_startup_script(redis_exe):
    """Create a batch script to start Redis easily"""
    script_content = f"""@echo off
echo 🚀 Starting Redis server for Stock Scanner...
"{redis_exe}"
pause
"""
    
    with open("start_redis.bat", "w") as f:
        f.write(script_content)
    
    print("✅ Created start_redis.bat - double-click this to start Redis anytime!")

def update_env_for_redis():
    """Update .env file to enable Redis/Celery"""
    env_path = ".env"
    env_updates = [
        "CELERY_ENABLED=true",
        "CELERY_BROKER_URL=redis://localhost:6379/0",
        "REDIS_URL=redis://localhost:6379/1"
    ]
    
    try:
        # Read existing .env
        existing_lines = []
        if os.path.exists(env_path):
            with open(env_path, 'r') as f:
                existing_lines = f.readlines()
        
        # Remove existing Redis/Celery settings
        filtered_lines = [line for line in existing_lines 
                         if not any(key in line for key in ['CELERY_', 'REDIS_'])]
        
        # Add new settings
        with open(env_path, 'w') as f:
            f.writelines(filtered_lines)
            f.write("\n# Redis/Celery Configuration\n")
            for setting in env_updates:
                f.write(f"{setting}\n")
        
        print("✅ Updated .env file with Redis configuration!")
        
    except Exception as e:
        print(f"❌ Failed to update .env: {e}")

def main():
    print("🔧 Redis Setup for Windows Stock Scanner")
    print("=" * 50)
    
    # Check if Redis is already running
    if check_redis_running():
        update_env_for_redis()
        print("\n🎉 Redis is ready! You can now use Celery tasks.")
        return
    
    print("\n📋 Redis Setup Options:")
    print("1. 🚀 Auto-install Redis (Recommended)")
    print("2. ℹ️  Manual installation instructions")
    print("3. 🏃 Skip Redis (Django will work without it)")
    
    choice = input("\nChoose option (1-3): ").strip()
    
    if choice == "1":
        # Auto-install
        print("\n🤖 Starting automatic Redis installation...")
        
        # Install redis package
        print("📦 Installing Python redis package...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'redis'])
        
        # Download and setup Redis
        zip_path = download_redis_windows()
        if not zip_path:
            return
        
        redis_exe = extract_and_setup_redis(zip_path)
        if not redis_exe:
            return
        
        # Start Redis
        if start_redis_server(redis_exe):
            create_redis_startup_script(redis_exe)
            update_env_for_redis()
            
            print("\n🎉 Redis setup completed successfully!")
            print("\n📋 Next steps:")
            print("1. Redis is now running")
            print("2. Your .env file has been updated")
            print("3. Use start_redis.bat to restart Redis anytime")
            print("4. Run: python manage.py runserver")
        
        # Cleanup
        if os.path.exists(zip_path):
            os.remove(zip_path)
    
    elif choice == "2":
        print("\n📖 Manual Redis Installation:")
        print("1. Download Redis from: https://github.com/microsoftarchive/redis/releases")
        print("2. Extract to a folder")
        print("3. Run redis-server.exe")
        print("4. Add to .env:")
        print("   CELERY_ENABLED=true")
        print("   CELERY_BROKER_URL=redis://localhost:6379/0")
        print("   REDIS_URL=redis://localhost:6379/1")
    
    elif choice == "3":
        print("\n✅ Skipping Redis setup")
        print("Django will work without Redis (using local memory cache)")
        print("Celery tasks will run immediately instead of in background")
    
    else:
        print("❌ Invalid choice")

if __name__ == "__main__":
    main()