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
    
    # Test imports in order
    tests = [
        ('core', 'Core app'),
        ('core.models', 'Core models'),
        ('core.admin', 'Core admin'),
        ('emails', 'Emails app'),
        ('stocks', 'Stocks app'),
        ('news', 'News app'),
        ('stockscanner_django.settings', 'Django settings'),
    ]
    
    all_passed = True
    
    for module_name, description in tests:
        success = test_import(module_name, description)
        if not success:
            all_passed = False
        print()
    
    print("=" * 30)
    if all_passed:
        print("✅ All imports passed syntax check!")
        
        # Try Django setup
        print("\n🔧 Testing Django setup...")
        try:
            import django
            django.setup()
            print("✅ Django setup successful!")
        except Exception as e:
            print(f"❌ Django setup failed: {e}")
            all_passed = False
            
    else:
        print("❌ Syntax errors found in imports!")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)