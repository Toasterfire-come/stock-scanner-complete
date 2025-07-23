#!/usr/bin/env python3
"""
🔍 DJANGO MINIMAL DIAGNOSTIC TEST
==================================
Comprehensive step-by-step Django testing to isolate startup issues.
Tests each component individually to find the exact failure point.
"""

import sys
import os
import traceback
import importlib

# 🎯 FIX: Add current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

print("🔍 Django Minimal Diagnostic Test")
print("=" * 50)
print(f"📂 Current directory: {current_dir}")
print(f"🐍 Python path includes current dir: {current_dir in sys.path}")

# 🔍 Check if we're in the right directory
required_files = ['manage.py', 'stockscanner_django', 'core', 'emails']
missing_files = []
for file in required_files:
    if not os.path.exists(os.path.join(current_dir, file)):
        missing_files.append(file)

if missing_files:
    print(f"⚠️  Missing files/dirs: {missing_files}")
    print("❌ You might be in the wrong directory!")
else:
    print("✅ All required files/directories found")

print()

def test_step_by_step():
    """Test Django setup step by step to find exact failure point"""
    print("🔍 Minimal Django Debug Test")
    print("=" * 35)
    
    # Step 1: Test basic Python
    print("1️⃣ Testing Python environment...")
    try:
        print(f"   Python version: {sys.version}")
        print(f"   Current directory: {os.getcwd()}")
        print("   ✅ Python OK")
    except Exception as e:
        print(f"   ❌ Python error: {e}")
        return False
    
    # Step 2: Test environment variable
    print("\n2️⃣ Setting Django settings...")
    try:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stockscanner_django.settings')
        print(f"   Settings module: {os.environ.get('DJANGO_SETTINGS_MODULE')}")
        print("   ✅ Environment OK")
    except Exception as e:
        print(f"   ❌ Environment error: {e}")
        return False
    
    # Step 3: Test Django import
    print("\n3️⃣ Testing Django import...")
    try:
        import django
        print(f"   Django version: {django.get_version()}")
        print("   ✅ Django import OK")
    except Exception as e:
        print(f"   ❌ Django import error: {e}")
        return False
    
    # Step 4: Test settings import (this is where it usually fails)
    print("\n4️⃣ Testing settings import...")
    try:
        from django.conf import settings
        print("   ✅ Settings import OK")
        print(f"   Debug mode: {getattr(settings, 'DEBUG', 'Unknown')}")
    except Exception as e:
        print(f"   ❌ Settings import error: {e}")
        print(f"   Error type: {type(e).__name__}")
        return False
    
    # Step 5: Test django.setup()
    print("\n5️⃣ Testing Django setup...")
    try:
        django.setup()
        print("   ✅ Django setup OK")
    except Exception as e:
        print(f"   ❌ Django setup error: {e}")
        print(f"   Error type: {type(e).__name__}")
        return False
    
    # Step 6: Test basic Django functionality
    print("\n6️⃣ Testing Django functionality...")
    try:
        from django.apps import apps
        installed_apps = [app.label for app in apps.get_app_configs()]
        print(f"   Installed apps: {len(installed_apps)}")
        for app in installed_apps:
            print(f"      • {app}")
        print("   ✅ Django apps OK")
    except Exception as e:
        print(f"   ❌ Django apps error: {e}")
        return False
    
    print("\n🎉 ALL TESTS PASSED!")
    print("✅ Django is working correctly!")
    return True

def test_settings_only():
    """Test just the settings file import"""
    print("\n🔍 Settings-Only Test")
    print("=" * 25)
    
    try:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stockscanner_django.settings')
        
        # Try to import the settings module directly
        import importlib
        settings_module = importlib.import_module('stockscanner_django.settings')
        print("✅ Settings module imported directly")
        
        # Check for basic attributes
        if hasattr(settings_module, 'INSTALLED_APPS'):
            apps = getattr(settings_module, 'INSTALLED_APPS')
            print(f"✅ INSTALLED_APPS found: {len(apps)} apps")
        
        if hasattr(settings_module, 'DATABASES'):
            print("✅ DATABASES configuration found")
        
        return True
        
    except Exception as e:
        print(f"❌ Settings module error: {e}")
        print(f"Error type: {type(e).__name__}")
        
        # Try to get more details
        import traceback
        print("\n📄 Full error traceback:")
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    success1 = test_settings_only()
    
    if success1:
        print("\n" + "=" * 35)
        success2 = test_step_by_step()
        return success2
    else:
        print("\n❌ Settings import failed - Django won't work")
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)