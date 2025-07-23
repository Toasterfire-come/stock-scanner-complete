#!/usr/bin/env python3
"""
Import Tester
Tests specific imports to isolate syntax errors
"""

import sys
import os

def test_import(module_name, description):
    """Test importing a specific module"""
    print(f"🔍 Testing {description}...")
    try:
        if '.' in module_name:
            # Import submodule
            parts = module_name.split('.')
            module = __import__(module_name, fromlist=[parts[-1]])
        else:
            module = __import__(module_name)
        print(f"   ✅ {description} imported successfully")
        return True
    except SyntaxError as e:
        print(f"   ❌ Syntax Error in {description}: {e}")
        print(f"      File: {e.filename}, Line: {e.lineno}")
        return False
    except ImportError as e:
        print(f"   ⚠️ Import Error in {description}: {e}")
        return True  # Import errors are OK, syntax errors are not
    except Exception as e:
        print(f"   ❌ Error in {description}: {e}")
        return False

def main():
    """Test imports step by step"""
    print("🧪 Import Syntax Tester")
    print("=" * 30)
    
    # Set up Django environment
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stockscanner_django.settings')
    
    # First test basic imports (before Django setup)
    basic_tests = [
        ('core', 'Core app'),
        ('emails', 'Emails app'),
        ('stocks', 'Stocks app'),
        ('news', 'News app'),
        ('stockscanner_django.settings', 'Django settings'),
    ]
    
    print("📋 Testing basic imports...")
    basic_passed = True
    
    for module_name, description in basic_tests:
        success = test_import(module_name, description)
        if not success:
            basic_passed = False
        print()
    
    # Try Django setup
    print("🔧 Setting up Django...")
    django_setup_success = False
    try:
        import django
        django.setup()
        print("✅ Django setup successful!")
        django_setup_success = True
    except Exception as e:
        print(f"❌ Django setup failed: {e}")
        basic_passed = False
    
    # Test Django-dependent imports (after Django setup)
    if django_setup_success:
        print("\n📋 Testing Django-dependent imports...")
        django_tests = [
            ('core.models', 'Core models'),
            ('core.admin', 'Core admin'),
        ]
        
        for module_name, description in django_tests:
            success = test_import(module_name, description)
            if not success:
                basic_passed = False
            print()
    
    print("=" * 30)
    if basic_passed and django_setup_success:
        print("✅ All imports passed!")
        print("✅ Django setup successful!")
        print("🎉 Ready to run Django server!")
    elif basic_passed:
        print("✅ Basic imports OK, Django setup has issues")
    else:
        print("❌ Import/syntax errors found!")
    
    return basic_passed and django_setup_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)