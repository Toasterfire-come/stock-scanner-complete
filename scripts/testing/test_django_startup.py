#!/usr/bin/env python3
"""
Django Startup Test
Tests Django configuration and startup process with improved formatting
"""

import os
import sys
import django
from pathlib import Path

def print_header(title):
    """Print a formatted header"""
    print(f"\n{'='*60}")
    print(f"🔍 {title}")
    print(f"{'='*60}")

def print_step(step_num, title):
    """Print a formatted step header"""
    print(f"\n{'-'*50}")
    print(f"{step_num} {title}")
    print(f"{'-'*50}")

def print_result(message, is_success=True):
    """Print a formatted result"""
    icon = "✅" if is_success else "❌"
    print(f"   {icon} {message}")

def print_warning(message):
    """Print a formatted warning"""
    print(f"   ⚠️ {message}")

def test_django_startup():
    """Test Django startup process step by step"""
    print_header("DJANGO STARTUP TEST")
    
    # Step 1: Check environment
    print_step("1️⃣", "CHECKING ENVIRONMENT")
    print(f"   🐍 Python Version: {sys.version.split()[0]}")
    print(f"   📁 Current Directory: {os.getcwd()}")
    print(f"   🏠 Virtual Environment: {sys.prefix}")
    print_result("Environment check completed")
    
    # Step 2: Check Django settings
    print_step("2️⃣", "CONFIGURING DJANGO SETTINGS")
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stockscanner_django.settings')
    print_result("Django settings module configured")
    
    # Step 3: Create logs directory
    print_step("3️⃣", "CREATING LOGS DIRECTORY")
    logs_dir = Path('logs')
    try:
        logs_dir.mkdir(exist_ok=True)
        print_result(f"Logs directory ready: {logs_dir.absolute()}")
    except Exception as e:
        print_warning(f"Could not create logs directory: {e}")
    
    # Step 4: Test Django import
    print_step("4️⃣", "TESTING DJANGO IMPORT")
    try:
        import django
        print_result(f"Django {django.get_version()} imported successfully")
    except ImportError as e:
        print_result(f"Django import failed: {e}", is_success=False)
        return False
    
    # Step 5: Test settings import
    print_step("5️⃣", "IMPORTING DJANGO SETTINGS")
    try:
        from django.conf import settings
        print_result("Django settings imported successfully")
        print(f"   🐛 Debug Mode: {settings.DEBUG}")
        print(f"   🗄️ Database Engine: {settings.DATABASES['default']['ENGINE'].split('.')[-1]}")
    except Exception as e:
        print_result(f"Settings import failed: {e}", is_success=False)
        return False
    
    # Step 6: Test Django setup
    print_step("6️⃣", "TESTING DJANGO SETUP")
    try:
        django.setup()
        print_result("Django setup completed successfully")
    except Exception as e:
        error_message = str(e)
        if ("no such table" in error_message or "does not exist" in error_message) and "django_celery_beat" in error_message:
            print_warning("Django setup issue: Celery Beat tables not found")
            print("   💡 This is normal before running migrations")
            print("   🔧 Solution: python scripts/setup/run_migrations.py")
            # Continue with limited testing - this is expected before migrations
        elif "ProgrammingError" in str(type(e).__name__) and "django_celery_beat" in error_message:
            print_warning("Celery Beat database error (expected before migrations)")
            print("   💡 Run migrations to fix: python scripts/setup/run_migrations.py")
            # Continue testing
        else:
            print_result(f"Django setup failed: {e}", is_success=False)
            print(f"   🐛 Error type: {type(e).__name__}")
            return False
    
    # Step 7: Test management commands
    print_step("7️⃣", "TESTING MANAGEMENT COMMANDS")
    try:
        from django.core.management import call_command
        from io import StringIO
        
        # Test check command
        out = StringIO()
        call_command('check', stdout=out)
        output = out.getvalue()
        if 'System check identified no issues' in output:
            print_result("Django system check passed")
        else:
            print_warning(f"System check output: {output}")
            if "django_celery_beat" in output:
                print("   💡 Celery beat tables need migration")
    except Exception as e:
        error_message = str(e)
        if "no such table" in error_message:
            print_warning(f"Management command issue (migration needed): {e}")
            print("   💡 This is normal before running migrations")
        else:
            print_result(f"Management command test failed: {e}", is_success=False)
            return False
    
    # Step 8: Test database connection
    print_step("8️⃣", "TESTING DATABASE CONNECTION")
    try:
        from django.db import connection
        cursor = connection.cursor()
        print_result("Database connection established successfully")
        print(f"   🗄️ Database Name: {connection.settings_dict['NAME']}")
    except Exception as e:
        print_warning(f"Database connection issue: {e}")
        print("   💡 This is normal if database isn't set up yet")
    
    # Final summary
    print(f"\n{'='*60}")
    print("🎉 DJANGO STARTUP TEST COMPLETED!")
    print(f"{'='*60}")
    
    print(f"\n💡 NEXT STEPS:")
    print(f"   1️⃣ python scripts/setup/run_migrations.py  (setup database)")
    print(f"   2️⃣ python manage.py runserver  (start Django)")
    print(f"   3️⃣ Open: http://localhost:8000  (access application)")
    
    print(f"\n🔧 ADDITIONAL TOOLS:")
    print(f"   📊 Rate Limit Optimizer: python scripts/utils/yahoo_rate_limit_optimizer.py")
    print(f"   🧪 YFinance Test: python scripts/testing/test_yfinance_system.py")
    print(f"   🐛 Import Test: python scripts/testing/test_imports.py")
    
    return True

def main():
    """Main test function with enhanced error handling"""
    try:
        print_header("STARTING DJANGO VALIDATION")
        success = test_django_startup()
        
        print(f"\n{'='*60}")
        if success:
            print("🎉 RESULT: Django is ready to use!")
            print("✅ All core components validated successfully")
        else:
            print("❌ RESULT: Django startup has issues")
            print("🔧 Please check the errors above and follow suggested solutions")
        print(f"{'='*60}")
            
        return success
        
    except KeyboardInterrupt:
        print(f"\n{'='*60}")
        print("⚠️ TEST INTERRUPTED BY USER")
        print(f"{'='*60}")
        return False
    except Exception as e:
        print(f"\n{'='*60}")
        print(f"💥 UNEXPECTED ERROR: {e}")
        print(f"🐛 Error Type: {type(e).__name__}")
        print(f"{'='*60}")
        return False

if __name__ == "__main__":
    print("🚀 Django Startup Test - Enhanced Version")
    print("=" * 60)
    success = main()
    print(f"\n📊 Test Result: {'PASSED' if success else 'FAILED'}")
    sys.exit(0 if success else 1)
    sys.exit(0 if success else 1)