#!/usr/bin/env python3
"""
Switch to SQLite Database Script
Alternative solution for PostgreSQL permission issues.

This script:
1. Updates Django settings to use SQLite
2. Creates a local SQLite database
3. Runs migrations on SQLite
4. Perfect for development and testing

Usage:
    python switch_to_sqlite.py

Author: Stock Scanner Project
Version: 1.0.0
"""

import os
import sys
import shutil
from pathlib import Path

def backup_settings():
    """Backup current settings file"""
    settings_file = Path("stockscanner_django/settings.py")
    backup_file = Path("stockscanner_django/settings_backup.py")
    
    if settings_file.exists():
        shutil.copy2(settings_file, backup_file)
        print(f"✅ Backed up settings to {backup_file}")
        return True
    else:
        print("❌ Settings file not found")
        return False

def update_settings_for_sqlite():
    """Update Django settings to use SQLite"""
    settings_file = Path("stockscanner_django/settings.py")
    
    if not settings_file.exists():
        print("❌ Settings file not found")
        return False
    
    # Read current settings
    with open(settings_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Create SQLite database configuration
    sqlite_config = '''
# SQLite Database Configuration (Development/Testing)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Commented out PostgreSQL configuration
# Uncomment and update when PostgreSQL permissions are fixed
"""
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'stockscanner_prod'),
        'USER': os.environ.get('DB_USER', 'stockscanner'),
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}
"""'''
    
    # Replace database configuration
    import re
    
    # Find the DATABASES configuration block
    pattern = r'DATABASES\s*=\s*\{[^}]*\{[^}]*\}[^}]*\}'
    
    if re.search(pattern, content, re.DOTALL):
        # Replace existing DATABASES block
        new_content = re.sub(pattern, sqlite_config.strip(), content, flags=re.DOTALL)
    else:
        # Add SQLite configuration if no DATABASES found
        new_content = content + "\n" + sqlite_config
    
    # Write updated settings
    with open(settings_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("✅ Updated settings.py to use SQLite")
    return True

def run_migrations():
    """Run Django migrations with SQLite"""
    print("\n🗄️ Running Django migrations with SQLite...")
    
    commands = [
        "python manage.py makemigrations",
        "python manage.py migrate",
    ]
    
    for cmd in commands:
        print(f"🔧 Running: {cmd}")
        result = os.system(cmd)
        if result != 0:
            print(f"❌ Command failed: {cmd}")
            return False
        else:
            print(f"✅ Command succeeded: {cmd}")
    
    return True

def create_superuser_prompt():
    """Prompt to create superuser"""
    print("\n👤 Create Django superuser...")
    response = input("Do you want to create a superuser now? (y/N): ").strip().lower()
    
    if response in ['y', 'yes']:
        print("🔧 Running: python manage.py createsuperuser")
        os.system("python manage.py createsuperuser")
    else:
        print("⏭️ Skipped superuser creation")
        print("💡 You can create one later with: python manage.py createsuperuser")

def test_server():
    """Test Django server startup"""
    print("\n🌐 Testing Django server...")
    response = input("Do you want to test the server now? (y/N): ").strip().lower()
    
    if response in ['y', 'yes']:
        print("🚀 Starting Django development server...")
        print("📱 Server will start at: http://127.0.0.1:8000")
        print("🛑 Press Ctrl+C to stop the server")
        print()
        os.system("python manage.py runserver")
    else:
        print("⏭️ Skipped server test")
        print("💡 You can start the server later with: python manage.py runserver")

def main():
    """Main function"""
    print("🔄 Switch to SQLite Database")
    print("=" * 40)
    print()
    print("This script will:")
    print("• Backup your current settings")
    print("• Switch Django to use SQLite database")
    print("• Run migrations on SQLite")
    print("• Help you create a superuser")
    print()
    print("💡 SQLite is perfect for:")
    print("• Development and testing")
    print("• Quick setup without database server")
    print("• Learning and experimentation")
    print()
    
    response = input("Continue with SQLite setup? (y/N): ").strip().lower()
    if response not in ['y', 'yes']:
        print("❌ Operation cancelled")
        return False
    
    print("\n🚀 Starting SQLite setup...")
    
    # Step 1: Backup settings
    if not backup_settings():
        return False
    
    # Step 2: Update settings
    if not update_settings_for_sqlite():
        return False
    
    # Step 3: Run migrations
    if not run_migrations():
        print("❌ Migration failed")
        return False
    
    # Step 4: Create superuser
    create_superuser_prompt()
    
    # Step 5: Test server
    test_server()
    
    # Show success message
    print("\n" + "=" * 50)
    print("✅ SQLITE SETUP COMPLETE!")
    print("=" * 50)
    print()
    print("📊 Your Django application is now using SQLite!")
    print()
    print("📋 Quick commands:")
    print("• Start server: python manage.py runserver")
    print("• Admin panel: http://127.0.0.1:8000/admin")
    print("• Create superuser: python manage.py createsuperuser")
    print()
    print("📁 Database file: db.sqlite3")
    print("📄 Settings backup: stockscanner_django/settings_backup.py")
    print()
    print("🔄 To switch back to PostgreSQL later:")
    print("1. Fix PostgreSQL permissions")
    print("2. Restore settings from backup")
    print("3. Update database credentials")
    print("4. Run migrations again")
    print()
    print("🎉 Happy coding!")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if not success:
            print("\n❌ FAILED: Could not switch to SQLite")
        input("\nPress Enter to continue...")
    except KeyboardInterrupt:
        print("\n❌ Operation cancelled by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        input("\nPress Enter to continue...")