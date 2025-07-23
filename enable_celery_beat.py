#!/usr/bin/env python3
"""
Enable Celery Beat
Safely enables Celery Beat after database migrations are complete
"""

import os
import sys
import re
from pathlib import Path

def enable_celery_beat_in_settings():
    """Enable Celery Beat in Django settings"""
    settings_file = Path('stockscanner_django/settings.py')
    
    if not settings_file.exists():
        print("❌ Django settings file not found!")
        return False
    
    print("🔧 Enabling Celery Beat in Django settings...")
    
    # Read the settings file
    with open(settings_file, 'r') as f:
        content = f.read()
    
    # Check current state
    if 'include_celery_beat = True' in content:
        print("✅ Celery Beat is already enabled")
        return True
    
    # Find and update the include_celery_beat setting
    pattern = r'include_celery_beat = False'
    if re.search(pattern, content):
        # Replace False with True
        updated_content = re.sub(pattern, 'include_celery_beat = True', content)
        
        # Backup original
        backup_file = settings_file.with_suffix('.py.backup')
        with open(backup_file, 'w') as f:
            f.write(content)
        
        # Write updated content
        with open(settings_file, 'w') as f:
            f.write(updated_content)
        
        print("✅ Celery Beat enabled in settings")
        print(f"💾 Backup saved to {backup_file}")
        return True
    else:
        print("⚠️ Could not find Celery Beat configuration in settings")
        return False

def test_celery_beat():
    """Test if Celery Beat is working"""
    print("\n🧪 Testing Celery Beat configuration...")
    
    try:
        # Set up Django
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stockscanner_django.settings')
        import django
        django.setup()
        
        # Test if django_celery_beat is in installed apps
        from django.conf import settings
        if 'django_celery_beat' in settings.INSTALLED_APPS:
            print("   ✅ django_celery_beat is in INSTALLED_APPS")
        else:
            print("   ❌ django_celery_beat is not in INSTALLED_APPS")
            return False
        
        # Test if we can import Celery Beat models
        from django_celery_beat.models import PeriodicTask
        print("   ✅ Celery Beat models can be imported")
        
        # Test database connection to Celery Beat tables
        count = PeriodicTask.objects.count()
        print(f"   ✅ Celery Beat database connection working ({count} tasks)")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Celery Beat test failed: {e}")
        return False

def check_database_tables():
    """Check if Celery Beat database tables exist"""
    print("🗄️ Checking Celery Beat database tables...")
    
    try:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stockscanner_django.settings')
        import django
        django.setup()
        
        from django.db import connection
        
        # Check for Celery Beat tables
        with connection.cursor() as cursor:
            # For PostgreSQL
            if 'postgresql' in connection.settings_dict['ENGINE']:
                cursor.execute("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_name LIKE 'django_celery_beat_%'
                """)
                tables = [row[0] for row in cursor.fetchall()]
            else:
                # For SQLite
                cursor.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name LIKE 'django_celery_beat_%'
                """)
                tables = [row[0] for row in cursor.fetchall()]
        
        if tables:
            print(f"   ✅ Found {len(tables)} Celery Beat tables:")
            for table in tables:
                print(f"      • {table}")
            return True
        else:
            print("   ❌ No Celery Beat tables found")
            print("   💡 Run migrations first: python run_migrations.py")
            return False
            
    except Exception as e:
        print(f"   ❌ Database check failed: {e}")
        return False

def main():
    """Main function"""
    print("🔧 Celery Beat Enabler")
    print("=" * 25)
    
    # Step 1: Check if database tables exist
    if not check_database_tables():
        print("\n❌ Celery Beat tables not found!")
        print("🔧 Please run migrations first:")
        print("   python run_migrations.py")
        return False
    
    # Step 2: Enable in settings
    if not enable_celery_beat_in_settings():
        print("\n❌ Failed to enable Celery Beat in settings")
        return False
    
    # Step 3: Test the configuration
    if not test_celery_beat():
        print("\n❌ Celery Beat test failed")
        return False
    
    print("\n🎉 CELERY BEAT ENABLED SUCCESSFULLY!")
    print("✅ Task scheduling is now available")
    print("\n💡 Next steps:")
    print("   1. python manage.py runserver")
    print("   2. Access: http://localhost:8000/admin")
    print("   3. Navigate to Periodic Tasks to schedule tasks")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️ Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Error: {e}")
        sys.exit(1)