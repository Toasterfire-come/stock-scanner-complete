#!/usr/bin/env python3
"""
Requirements Validation Script
Tests all packages in requirements.txt to ensure they can be installed and imported
"""

import subprocess
import sys
import importlib
from pathlib import Path

# Try to import pkg_resources, fallback to importlib.metadata for Python 3.8+
try:
    import pkg_resources
    USE_PKG_RESOURCES = True
except ImportError:
    try:
        import importlib.metadata as importlib_metadata
        USE_PKG_RESOURCES = False
    except ImportError:
        # Fallback for older Python versions
        import importlib_metadata
        USE_PKG_RESOURCES = False

def parse_requirements(file_path):
    """Parse requirements.txt and extract package names"""
    packages = []
    
    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            
            # Skip comments and empty lines
            if not line or line.startswith('#'):
                continue
                
            # Skip -r includes
            if line.startswith('-r'):
                continue
                
            # Extract package name (before version specifier)
            if '>=' in line:
                package_name = line.split('>=')[0]
            elif '==' in line:
                package_name = line.split('==')[0]
            elif '<' in line:
                package_name = line.split('<')[0]
            else:
                package_name = line
                
            packages.append(package_name.strip())
    
    return packages

def test_package_import(package_name):
    """Test if a package can be imported"""
    # Package name to import name mapping
    import_mapping = {
        'django-cors-headers': 'corsheaders',
        'django-redis': 'django_redis',
        'django-celery-beat': 'django_celery_beat',
        'django-debug-toolbar': 'debug_toolbar',
        'django-extensions': 'django_extensions',
        'django-ratelimit': 'django_ratelimit',
        'django-silk': 'silk',
        'django-migration-testcase': 'django_migration_testcase',
        'beautifulsoup4': 'bs4',
        'requests-cache': 'requests_cache',
        'requests-mock': 'requests_mock',
        'asyncio-throttle': 'asyncio_throttle',
        'factory-boy': 'factory',
        'sphinx-rtd-theme': 'sphinx_rtd_theme',
        'memory-profiler': 'memory_profiler',
        'dj-database-url': 'dj_database_url',
        'python-dateutil': 'dateutil',
        'python-dotenv': 'dotenv',
        'python-decouple': 'decouple',
        'psycopg2-binary': 'psycopg2',
    }
    
    import_name = import_mapping.get(package_name, package_name)
    
    try:
        importlib.import_module(import_name)
        return True, None
    except ImportError as e:
        return False, str(e)

def check_installed_version(package_name):
    """Check if package is installed and get version"""
    if USE_PKG_RESOURCES:
        try:
            distribution = pkg_resources.get_distribution(package_name)
            return True, distribution.version
        except pkg_resources.DistributionNotFound:
            return False, None
    else:
        try:
            distribution = importlib_metadata.distribution(package_name)
            return True, distribution.version
        except importlib_metadata.PackageNotFoundError:
            return False, None

def main():
    """Main validation process"""
    print("🔍 Requirements Validation")
    print("=" * 50)
    
    # Parse requirements
    req_file = Path('requirements.txt')
    if not req_file.exists():
        print("❌ requirements.txt not found!")
        return False
    
    packages = parse_requirements(req_file)
    print(f"📦 Found {len(packages)} packages to validate")
    print()
    
    results = {
        'installed': [],
        'not_installed': [],
        'import_failed': [],
        'import_success': []
    }
    
    for package in packages:
        print(f"🔍 Testing: {package}")
        
        # Check if installed
        is_installed, version = check_installed_version(package)
        
        if is_installed:
            print(f"   ✅ Installed: {version}")
            results['installed'].append((package, version))
            
            # Test import
            can_import, error = test_package_import(package)
            if can_import:
                print(f"   ✅ Import: Success")
                results['import_success'].append(package)
            else:
                print(f"   ⚠️ Import: Failed - {error}")
                results['import_failed'].append((package, error))
        else:
            print(f"   ❌ Not installed")
            results['not_installed'].append(package)
        
        print()
    
    # Summary
    print("=" * 50)
    print("📊 VALIDATION SUMMARY")
    print("=" * 50)
    
    print(f"✅ Installed: {len(results['installed'])}/{len(packages)}")
    print(f"✅ Import Success: {len(results['import_success'])}/{len(packages)}")
    print(f"⚠️ Import Failed: {len(results['import_failed'])}")
    print(f"❌ Not Installed: {len(results['not_installed'])}")
    
    if results['not_installed']:
        print("\n❌ MISSING PACKAGES:")
        for package in results['not_installed']:
            print(f"   • {package}")
    
    if results['import_failed']:
        print("\n⚠️ IMPORT FAILURES:")
        for package, error in results['import_failed']:
            print(f"   • {package}: {error}")
    
    success_rate = (len(results['installed']) / len(packages)) * 100
    import_rate = (len(results['import_success']) / len(packages)) * 100
    
    print(f"\n📈 Installation Rate: {success_rate:.1f}%")
    print(f"📈 Import Rate: {import_rate:.1f}%")
    
    if success_rate >= 95 and import_rate >= 90:
        print("\n🎉 REQUIREMENTS VALIDATION PASSED!")
        return True
    elif success_rate >= 90:
        print("\n✅ Most requirements validated. System should work.")
        return True
    else:
        print("\n⚠️ Requirements validation has issues.")
        return False

def install_missing():
    """Install missing packages"""
    print("🔧 Installing missing packages...")
    try:
        subprocess.run([
            sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'
        ], check=True)
        print("✅ Installation completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Installation failed: {e}")
        return False

if __name__ == "__main__":
    try:
        # First try to validate current state
        success = main()
        
        if not success:
            print("\n🔧 Attempting to install missing packages...")
            if install_missing():
                print("\n🔍 Re-running validation...")
                success = main()
        
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n⚠️ Validation interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Validation failed: {e}")
        sys.exit(1)