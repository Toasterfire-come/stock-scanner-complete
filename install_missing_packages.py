#!/usr/bin/env python3
"""
📦 INSTALL MISSING PACKAGES
============================
Installs missing Django packages and verifies the installation.
"""

import subprocess
import sys
import importlib

def run_pip_install(package):
    """Install a package using pip"""
    try:
        print(f"📦 Installing {package}...")
        result = subprocess.run([sys.executable, '-m', 'pip', 'install', package], 
                              capture_output=True, text=True, check=True)
        print(f"✅ {package} installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install {package}")
        print(f"Error: {e.stderr}")
        return False

def check_package(package_name, import_name=None):
    """Check if a package is installed and importable"""
    if import_name is None:
        import_name = package_name
    
    try:
        importlib.import_module(import_name)
        print(f"✅ {package_name} is installed and importable")
        return True
    except ImportError:
        print(f"❌ {package_name} is NOT installed or importable")
        return False

def main():
    print("🔍 Checking and Installing Missing Django Packages")
    print("=" * 60)
    
    # Critical packages that are commonly missing
    critical_packages = [
        ('djangorestframework', 'rest_framework'),
        ('django-cors-headers', 'corsheaders'),
        ('psycopg2-binary', 'psycopg2'),
        ('django-redis', 'django_redis'),
        ('celery', 'celery'),
        ('django-celery-beat', 'django_celery_beat'),
        ('yfinance', 'yfinance'),
        ('beautifulsoup4', 'bs4'),
        ('python-dotenv', 'dotenv'),
        ('dj-database-url', 'dj_database_url'),
    ]
    
    missing_packages = []
    
    # Check which packages are missing
    print("🔍 Checking installed packages...")
    for package_name, import_name in critical_packages:
        if not check_package(package_name, import_name):
            missing_packages.append(package_name)
    
    if not missing_packages:
        print("\n🎉 All critical packages are installed!")
        return True
    
    print(f"\n📦 Missing packages: {missing_packages}")
    print("\n🔧 Installing missing packages...")
    
    # Install missing packages
    failed_installs = []
    for package in missing_packages:
        if not run_pip_install(package):
            failed_installs.append(package)
    
    if failed_installs:
        print(f"\n❌ Failed to install: {failed_installs}")
        print("\n🔧 Trying full requirements install...")
        if not run_pip_install('-r requirements.txt'):
            print("❌ Requirements install failed")
            return False
    
    print("\n✅ Package installation completed!")
    
    # Verify installation
    print("\n🔍 Verifying installations...")
    all_good = True
    for package_name, import_name in critical_packages:
        if not check_package(package_name, import_name):
            all_good = False
    
    if all_good:
        print("\n🎉 All packages verified successfully!")
        print("\n🚀 You can now run: python django_minimal_test.py")
    else:
        print("\n⚠️  Some packages still missing - check the output above")
    
    return all_good

if __name__ == "__main__":
    main()