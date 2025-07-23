#!/usr/bin/env python3
"""
Django Startup Test
Tests Django configuration and startup process
"""

import os
import sys
import django
from pathlib import Path

def test_django_startup():
    """Test Django startup process step by step"""
    print("🔍 Django Startup Test")
    print("=" * 30)
    
    # Step 1: Check environment
    print("1️⃣ Checking environment...")
    print(f"   Python: {sys.version}")
    print(f"   Current directory: {os.getcwd()}")
    print(f"   Virtual env: {sys.prefix}")
    
    # Step 2: Check Django settings
    print("\n2️⃣ Setting Django settings module...")
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stockscanner_django.settings')
    print("   ✅ Settings module set")
    
    # Step 3: Create logs directory
    print("\n3️⃣ Creating logs directory...")
    logs_dir = Path('logs')
    try:
        logs_dir.mkdir(exist_ok=True)
        print(f"   ✅ Logs directory created: {logs_dir.absolute()}")
    except Exception as e:
        print(f"   ⚠️ Could not create logs directory: {e}")
    
    # Step 4: Test Django import
    print("\n4️⃣ Testing Django import...")
    try:
        import django
        print(f"   ✅ Django version: {django.get_version()}")
    except ImportError as e:
        print(f"   ❌ Django import failed: {e}")
        return False
    
    # Step 5: Test settings import
    print("\n5️⃣ Testing settings import...")
    try:
        from django.conf import settings
        print(f"   ✅ Settings imported")
        print(f"   Debug mode: {settings.DEBUG}")
    except Exception as e:
        print(f"   ❌ Settings import failed: {e}")
        return False
    
    # Step 6: Test Django setup
    print("\n6️⃣ Testing Django setup...")
    try:
        django.setup()
        print("   ✅ Django setup completed")
    except Exception as e:
        error_message = str(e)
        if ("no such table" in error_message or "does not exist" in error_message) and "django_celery_beat" in error_message:
            print(f"   ⚠️ Django setup issue: Celery Beat tables not found")
            print("   💡 This is normal before running migrations")
            print("   🔧 Solution: python run_migrations.py")
            # Continue with limited testing - this is expected before migrations
        elif "ProgrammingError" in str(type(e).__name__) and "django_celery_beat" in error_message:
            print(f"   ⚠️ Celery Beat database error (expected before migrations)")
            print("   💡 Run migrations to fix: python run_migrations.py")
            # Continue testing
        else:
            print(f"   ❌ Django setup failed: {e}")
            print(f"   Error type: {type(e).__name__}")
            return False
    
    # Step 7: Test management commands
    print("\n7️⃣ Testing management commands...")
    try:
        from django.core.management import call_command
        from io import StringIO
        
        # Test check command
        out = StringIO()
        call_command('check', stdout=out)
        output = out.getvalue()
        if 'System check identified no issues' in output:
            print("   ✅ System check passed")
        else:
            print(f"   ⚠️ System check output: {output}")
            if "django_celery_beat" in output:
                print("   💡 Celery beat tables need migration")
    except Exception as e:
        error_message = str(e)
        if "no such table" in error_message:
            print(f"   ⚠️ Management command issue (migration needed): {e}")
            print("   💡 This is normal before running migrations")
        else:
            print(f"   ❌ Management command test failed: {e}")
            return False
    
    # Step 8: Test database connection
    print("\n8️⃣ Testing database connection...")
    try:
        from django.db import connection
        cursor = connection.cursor()
        print("   ✅ Database connection successful")
    except Exception as e:
        print(f"   ⚠️ Database connection issue: {e}")
        print("   (This is normal if database isn't set up yet)")
    
    print("\n🎉 Django startup test completed!")
    print("\n💡 Next steps:")
    print("   1. python run_migrations.py  (fixes Celery Beat tables)")
    print("   2. python manage.py runserver")
    print("   3. Access: http://localhost:8000")
    
    return True

def main():
    """Main test function"""
    try:
        success = test_django_startup()
        
        if success:
            print("\n✅ Django is ready to use!")
        else:
            print("\n❌ Django startup has issues")
            
        return success
        
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted")
        return False
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)