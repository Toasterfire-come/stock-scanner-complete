#!/usr/bin/env python3
"""
Django Server Diagnostic and Fix Script
Identifies and fixes common Django server startup issues
"""

import os
import sys
import subprocess
import time
import signal
from pathlib import Path

def print_header(title):
    print(f"\n{'='*60}")
    print(f"🔧 {title}")
    print(f"{'='*60}")

def print_step(step, description):
    print(f"\n📋 Step {step}: {description}")
    print("-" * 50)

def run_command(cmd, description="", check_exit=True):
    """Run a command and return output"""
    print(f"🚀 Running: {cmd}")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        if result.stdout:
            print(f"✅ Output: {result.stdout.strip()}")
        if result.stderr and result.returncode != 0:
            print(f"❌ Error: {result.stderr.strip()}")
        
        if check_exit and result.returncode != 0:
            print(f"❌ Command failed with exit code: {result.returncode}")
            return False, result.stderr
        return True, result.stdout
    except subprocess.TimeoutExpired:
        print(f"⏰ Command timed out after 30 seconds")
        return False, "Timeout"
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False, str(e)

def kill_existing_servers():
    """Kill any existing Django servers"""
    print_step(1, "Killing existing Django servers")
    
    # Find Django processes
    success, output = run_command("ps aux | grep 'manage.py runserver' | grep -v grep", check_exit=False)
    if success and output.strip():
        print("🔍 Found existing Django processes:")
        print(output)
        
        # Extract PIDs and kill them
        lines = output.strip().split('\n')
        for line in lines:
            parts = line.split()
            if len(parts) > 1:
                pid = parts[1]
                print(f"🔪 Killing process {pid}")
                run_command(f"kill -9 {pid}", check_exit=False)
    else:
        print("✅ No existing Django processes found")

def check_environment():
    """Check Python environment and dependencies"""
    print_step(2, "Checking Python environment")
    
    # Check Python version
    print(f"🐍 Python version: {sys.version}")
    
    # Check if in virtual environment
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✅ Running in virtual environment")
        print(f"📁 Virtual env path: {sys.prefix}")
    else:
        print("⚠️  Not in virtual environment")
    
    # Check required packages
    required_packages = [
        'django', 'djangorestframework', 'psycopg2', 'yfinance', 
        'beautifulsoup4', 'requests', 'nltk', 'python-dotenv'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package} - installed")
        except ImportError:
            print(f"❌ {package} - missing")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n📦 Installing missing packages: {', '.join(missing_packages)}")
        cmd = f"pip install {' '.join(missing_packages)}"
        run_command(cmd)
    
    return len(missing_packages) == 0

def check_database():
    """Check database configuration and connectivity"""
    print_step(3, "Checking database configuration")
    
    # Check .env file
    env_path = Path(".env")
    if not env_path.exists():
        print("❌ .env file not found!")
        return False
    
    print("✅ .env file exists")
    
    # Load environment variables
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        db_engine = os.getenv('DB_ENGINE')
        db_name = os.getenv('DB_NAME')
        db_user = os.getenv('DB_USER')
        db_password = os.getenv('DB_PASSWORD')
        db_host = os.getenv('DB_HOST')
        db_port = os.getenv('DB_PORT')
        
        print(f"🗄️  Database Engine: {db_engine}")
        print(f"🗄️  Database Name: {db_name}")
        print(f"🗄️  Database User: {db_user}")
        print(f"🗄️  Database Host: {db_host}:{db_port}")
        print(f"🗄️  Password: {'*' * len(db_password) if db_password else 'NOT SET'}")
        
        if not db_password:
            print("❌ Database password not set!")
            return False
            
    except Exception as e:
        print(f"❌ Error loading .env: {e}")
        return False
    
    # Test database connection
    print("\n🔍 Testing database connection...")
    try:
        import psycopg2
        conn = psycopg2.connect(
            host=db_host,
            port=db_port,
            database=db_name,
            user=db_user,
            password=db_password,
            connect_timeout=10
        )
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"✅ PostgreSQL connection successful!")
        print(f"📋 Version: {version[0][:50]}...")
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("\n💡 Troubleshooting:")
        print("- Make sure PostgreSQL is running")
        print("- Check if database exists")
        print("- Verify credentials in .env file")
        return False

def run_migrations():
    """Run Django migrations"""
    print_step(4, "Running Django migrations")
    
    # Set Django settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stockscanner_django.settings')
    
    # Make migrations
    print("🔄 Making migrations...")
    success, output = run_command("python manage.py makemigrations")
    if not success:
        print("❌ Failed to make migrations")
        return False
    
    # Run migrations
    print("🔄 Applying migrations...")
    success, output = run_command("python manage.py migrate")
    if not success:
        print("❌ Failed to apply migrations")
        return False
    
    print("✅ Migrations completed successfully")
    return True

def collect_static():
    """Collect static files"""
    print_step(5, "Collecting static files")
    
    success, output = run_command("python manage.py collectstatic --noinput")
    if success:
        print("✅ Static files collected")
        return True
    else:
        print("⚠️  Static files collection failed (not critical)")
        return True  # Not critical for development

def test_django_setup():
    """Test Django configuration"""
    print_step(6, "Testing Django configuration")
    
    try:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stockscanner_django.settings')
        import django
        django.setup()
        
        from django.db import connection
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        
        if result[0] == 1:
            print("✅ Django database connection test passed")
            return True
        else:
            print("❌ Django database connection test failed")
            return False
            
    except Exception as e:
        print(f"❌ Django setup failed: {e}")
        return False

def start_server():
    """Start Django development server"""
    print_step(7, "Starting Django development server")
    
    print("🚀 Starting server on 0.0.0.0:8000...")
    print("📝 Server will run in background. Check server.log for output.")
    print("🌐 Access at: http://127.0.0.1:8000")
    print("🛑 To stop: pkill -f 'manage.py runserver'")
    
    # Start server in background
    cmd = "python manage.py runserver 0.0.0.0:8000 > server.log 2>&1 &"
    os.system(cmd)
    
    # Wait a moment for server to start
    time.sleep(3)
    
    # Test if server is responding
    print("\n🔍 Testing server response...")
    try:
        import requests
        response = requests.get("http://127.0.0.1:8000/api/simple/status/", timeout=5)
        if response.status_code == 200:
            print("✅ Server is responding!")
            print(f"📊 Status: {response.status_code}")
            return True
        else:
            print(f"⚠️  Server responded with status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Server test failed: {e}")
        print("📋 Check server.log for details")
        return False

def show_server_log():
    """Show recent server log entries"""
    print_step(8, "Server log (last 20 lines)")
    
    if Path("server.log").exists():
        success, output = run_command("tail -20 server.log", check_exit=False)
        if success and output:
            print(output)
        else:
            print("📝 Server log is empty or not accessible")
    else:
        print("📝 No server.log file found")

def main():
    """Main diagnostic and fix routine"""
    print_header("Django Server Diagnostic & Fix Tool")
    print("🎯 This script will diagnose and fix common Django server issues")
    
    # Step-by-step fixes
    steps = [
        ("Kill existing servers", kill_existing_servers),
        ("Check environment", check_environment),
        ("Check database", check_database),
        ("Run migrations", run_migrations),
        ("Collect static files", collect_static),
        ("Test Django setup", test_django_setup),
        ("Start server", start_server),
        ("Show server log", show_server_log)
    ]
    
    failed_steps = []
    
    for step_name, step_func in steps:
        try:
            if not step_func():
                failed_steps.append(step_name)
        except Exception as e:
            print(f"❌ Step '{step_name}' failed with exception: {e}")
            failed_steps.append(step_name)
    
    # Summary
    print_header("DIAGNOSTIC SUMMARY")
    
    if not failed_steps:
        print("🎉 ALL CHECKS PASSED!")
        print("✅ Django server should be running at http://127.0.0.1:8000")
        print("\n🔗 Test these endpoints:")
        print("   • http://127.0.0.1:8000/api/simple/status/")
        print("   • http://127.0.0.1:8000/api/simple/stocks/")
        print("   • http://127.0.0.1:8000/admin/")
    else:
        print("⚠️  SOME ISSUES FOUND:")
        for step in failed_steps:
            print(f"   ❌ {step}")
        print("\n💡 Manual fixes may be needed for failed steps")
    
    print(f"\n📋 Log files:")
    print(f"   • Server output: server.log")
    print(f"   • Run this script again: python fix_server.py")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Script interrupted by user")
    except Exception as e:
        print(f"\n❌ Script failed: {e}")
        import traceback
        traceback.print_exc()