#!/usr/bin/env python3
"""
Quick Fix Installer
Installs essential packages to get Django working
"""

import subprocess
import sys

def run_pip_install(packages, description):
    """Install packages via pip"""
    print(f"🔧 {description}...")
    try:
        cmd = [sys.executable, '-m', 'pip', 'install'] + packages
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"   ✅ {description} completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"   ❌ {description} failed: {e}")
        if e.stderr:
            print(f"   📄 Error: {e.stderr.strip()}")
        return False

def main():
    """Install essential packages in order"""
    print("🚀 Quick Fix Installer")
    print("=" * 30)
    
    # Essential packages in order of dependency
    install_steps = [
        (["setuptools", "wheel"], "Installing setuptools and wheel"),
        (["pip", "--upgrade"], "Upgrading pip"),
        (["dj-database-url", "python-decouple"], "Installing database utilities"),
        (["django>=5.1.8"], "Installing Django"),
        (["djangorestframework", "django-cors-headers"], "Installing Django REST"),
        (["psycopg2-binary"], "Installing PostgreSQL adapter"),
        (["celery", "django-celery-beat", "redis"], "Installing task queue"),
        (["yfinance", "requests", "pandas", "numpy"], "Installing stock APIs"),
        (["beautifulsoup4", "nltk", "lxml"], "Installing web scraping"),
    ]
    
    success_count = 0
    total_steps = len(install_steps)
    
    for packages, description in install_steps:
        success = run_pip_install(packages, description)
        if success:
            success_count += 1
        print()
    
    # Install remaining from requirements.txt
    print("🔧 Installing remaining requirements...")
    try:
        cmd = [sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt']
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("   ✅ Requirements installation completed")
        success_count += 1
        total_steps += 1
    except subprocess.CalledProcessError as e:
        print(f"   ⚠️ Some requirements may have failed: {e}")
    
    print("\n" + "=" * 30)
    print("📊 INSTALLATION SUMMARY")
    print("=" * 30)
    
    success_rate = (success_count / total_steps) * 100
    print(f"📈 Success Rate: {success_count}/{total_steps} ({success_rate:.1f}%)")
    
    if success_rate >= 80:
        print("\n🎉 INSTALLATION SUCCESSFUL!")
        print("✅ Django should now work")
        print("\n💡 Next steps:")
        print("   1. python manage.py migrate")
        print("   2. python test_yfinance_system.py")
        print("   3. python manage.py runserver")
        return True
    else:
        print("\n⚠️ Some installations failed")
        print("🔧 Try running setup_environment.py")
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n💥 Installation failed: {e}")
        sys.exit(1)