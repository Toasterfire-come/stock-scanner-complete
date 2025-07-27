#!/usr/bin/env python3
"""
Django Extensions Dependency Fix
Handles the django_extensions module not found error
"""

import subprocess
import sys
import os
from pathlib import Path

def check_virtual_env():
    """Check if we're in a virtual environment"""
    return hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)

def install_django_extensions():
    """Install django_extensions in the current environment"""
    try:
        print("Installing django_extensions...")
        result = subprocess.run([sys.executable, '-m', 'pip', 'install', 'django_extensions'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ django_extensions installed successfully")
            return True
        else:
            print(f"❌ Installation failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error installing django_extensions: {e}")
        return False

def remove_from_settings():
    """Remove django_extensions from INSTALLED_APPS if installation fails"""
    settings_file = Path('stockscanner_django/settings.py')
    
    if not settings_file.exists():
        print("❌ Settings file not found")
        return False
    
    try:
        with open(settings_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Remove django_extensions line
        lines = content.split('\n')
        new_lines = []
        
        for line in lines:
            if "'django_extensions'," not in line and '"django_extensions",' not in line:
                new_lines.append(line)
            else:
                print(f"Removing line: {line.strip()}")
        
        # Write back
        with open(settings_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(new_lines))
        
        print("✅ Removed django_extensions from INSTALLED_APPS")
        return True
        
    except Exception as e:
        print(f"❌ Error modifying settings: {e}")
        return False

def main():
    """Main fix function"""
    print("🔧 DJANGO EXTENSIONS DEPENDENCY FIX")
    print("=" * 50)
    
    # Check environment
    if check_virtual_env():
        print("📦 Virtual environment detected")
    else:
        print("⚠️  Not in virtual environment")
    
    # Try to install django_extensions
    print("\n1. Attempting to install django_extensions...")
    if install_django_extensions():
        print("✅ Fix complete - django_extensions is now available")
        print("\nYou can now run: python start_stock_scheduler.py")
        return True
    
    # If installation fails, offer to remove it from settings
    print("\n2. Installation failed. Removing from settings...")
    if remove_from_settings():
        print("✅ Fix complete - django_extensions removed from INSTALLED_APPS")
        print("\n⚠️  Note: Some Django admin features may not be available")
        print("You can now run: python start_stock_scheduler.py")
        return True
    
    print("❌ Unable to fix the issue automatically")
    print("\nManual solutions:")
    print("1. Install in virtual environment: pip install django_extensions")
    print("2. Or manually remove 'django_extensions' from INSTALLED_APPS in settings.py")
    
    return False

if __name__ == "__main__":
    main()