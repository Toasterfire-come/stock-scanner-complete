#!/usr/bin/env python3
"""
Simple Requirements Checker
Basic validation without pkg_resources dependency
"""

import subprocess
import sys
import importlib
from pathlib import Path

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
        'beautifulsoup4': 'bs4',
        'requests-cache': 'requests_cache',
        'asyncio-throttle': 'asyncio_throttle',
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

def install_package(package_name):
    """Install a single package"""
    try:
        subprocess.run([
            sys.executable, '-m', 'pip', 'install', package_name
        ], check=True, capture_output=True, text=True)
        return True
    except subprocess.CalledProcessError:
        return False

def main():
    """Main validation process"""
    print("🔍 Simple Requirements Check")
    print("=" * 40)
    
    # Parse requirements
    req_file = Path('requirements.txt')
    if not req_file.exists():
        print("❌ requirements.txt not found!")
        return False
    
    packages = parse_requirements(req_file)
    print(f"📦 Found {len(packages)} packages to check")
    print()
    
    results = {
        'import_success': [],
        'import_failed': [],
        'fixed': []
    }
    
    for package in packages:
        print(f"🔍 Testing: {package}")
        
        # Test import
        can_import, error = test_package_import(package)
        if can_import:
            print(f"   ✅ Import: Success")
            results['import_success'].append(package)
        else:
            print(f"   ❌ Import: Failed - {error}")
            results['import_failed'].append((package, error))
            
            # Try to install the package
            print(f"   🔧 Attempting to install {package}...")
            if install_package(package):
                # Test import again
                can_import_retry, _ = test_package_import(package)
                if can_import_retry:
                    print(f"   ✅ Fixed: {package} installed and working")
                    results['fixed'].append(package)
                    results['import_success'].append(package)
                else:
                    print(f"   ⚠️ Installed but still can't import")
            else:
                print(f"   ❌ Failed to install {package}")
        
        print()
    
    # Summary
    print("=" * 40)
    print("📊 CHECK SUMMARY")
    print("=" * 40)
    
    total_working = len(results['import_success'])
    total_failed = len(results['import_failed']) - len(results['fixed'])
    
    print(f"✅ Working: {total_working}/{len(packages)}")
    print(f"🔧 Fixed: {len(results['fixed'])}")
    print(f"❌ Still Failed: {total_failed}")
    
    if results['fixed']:
        print(f"\n🔧 PACKAGES FIXED:")
        for package in results['fixed']:
            print(f"   • {package}")
    
    remaining_failed = [pkg for pkg, _ in results['import_failed'] if pkg not in results['fixed']]
    if remaining_failed:
        print(f"\n❌ STILL FAILING:")
        for package in remaining_failed:
            print(f"   • {package}")
    
    success_rate = (total_working / len(packages)) * 100
    print(f"\n📈 Success Rate: {success_rate:.1f}%")
    
    if success_rate >= 95:
        print("\n🎉 REQUIREMENTS CHECK PASSED!")
        return True
    elif success_rate >= 85:
        print("\n✅ Most requirements working. System should function.")
        return True
    else:
        print("\n⚠️ Multiple package issues detected.")
        return False

if __name__ == "__main__":
    try:
        success = main()
        
        if success:
            print("\n💡 Next steps:")
            print("   1. Run: python setup_environment.py")
            print("   2. Run: python manage.py migrate")
            print("   3. Run: python test_yfinance_system.py")
        
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n⚠️ Check interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Check failed: {e}")
        sys.exit(1)