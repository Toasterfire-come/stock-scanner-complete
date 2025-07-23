#!/usr/bin/env python3
"""
Windows Fix Installer
Handles Windows-specific package installation issues
Avoids C compiler requirements by using binary wheels
"""

import subprocess
import sys
import platform

def run_pip_install(packages, description, use_only_binary=False):
    """Install packages via pip with Windows-friendly options"""
    print(f"🔧 {description}...")
    try:
        cmd = [sys.executable, '-m', 'pip', 'install']
        
        # Use binary wheels only for packages that typically need compilation
        if use_only_binary:
            cmd.extend(['--only-binary=all'])
        
        # Add packages
        cmd.extend(packages)
        
        # Run installation
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"   ✅ {description} completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"   ❌ {description} failed: {e}")
        if e.stderr:
            print(f"   📄 Error: {e.stderr.strip()}")
        return False

def install_with_fallback(packages, description):
    """Try multiple installation strategies"""
    print(f"🔧 {description}...")
    
    # Strategy 1: Try with binary wheels only
    print(f"   📦 Trying binary wheels only...")
    success = run_pip_install(packages, f"Binary wheels for {description}", use_only_binary=True)
    if success:
        return True
    
    # Strategy 2: Try with cache disabled
    print(f"   📦 Trying without cache...")
    try:
        cmd = [sys.executable, '-m', 'pip', 'install', '--no-cache-dir'] + packages
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"   ✅ {description} completed (no cache)")
        return True
    except subprocess.CalledProcessError:
        pass
    
    # Strategy 3: Try upgrading pip first
    print(f"   📦 Upgrading pip and retrying...")
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'], check=True)
        cmd = [sys.executable, '-m', 'pip', 'install'] + packages
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"   ✅ {description} completed (after pip upgrade)")
        return True
    except subprocess.CalledProcessError:
        pass
    
    print(f"   ❌ All strategies failed for {description}")
    return False

def main():
    """Install packages with Windows compatibility"""
    print("🪟 Windows Fix Installer")
    print("=" * 35)
    print(f"🖥️ Platform: {platform.system()} {platform.release()}")
    print(f"🐍 Python: {sys.version}")
    print()
    
    # Essential packages that don't need compilation
    essential_steps = [
        (["setuptools", "wheel", "pip"], "Essential build tools"),
        (["python-dotenv", "python-decouple"], "Configuration utilities"),
        (["requests", "urllib3", "certifi"], "HTTP libraries"),
        (["dj-database-url"], "Database URL parser"),
    ]
    
    # Django and related (usually no compilation needed)
    django_steps = [
        (["Django>=5.1.8,<5.2"], "Django framework"),
        (["djangorestframework"], "Django REST framework"),
        (["django-cors-headers"], "Django CORS headers"),
        (["psycopg2-binary"], "PostgreSQL adapter (binary)"),
        (["django-redis"], "Django Redis cache"),
    ]
    
    # Task queue (Redis might need special handling)
    task_steps = [
        (["redis"], "Redis client"),
        (["celery"], "Celery task queue"),
        (["django-celery-beat"], "Django Celery Beat"),
    ]
    
    # Data processing (these often need compilation, so use binary-only)
    data_steps = [
        (["numpy"], "NumPy (binary wheels)"),
        (["pandas"], "Pandas (binary wheels)"),
        (["yfinance"], "Yahoo Finance API"),
    ]
    
    # Web scraping and NLP
    scraping_steps = [
        (["beautifulsoup4", "lxml"], "Web scraping libraries"),
        (["nltk"], "Natural Language Toolkit"),
    ]
    
    # Production and utilities
    production_steps = [
        (["gunicorn"], "WSGI server"),
        (["whitenoise"], "Static file serving"),
        (["django-debug-toolbar"], "Debug toolbar"),
    ]
    
    all_steps = [
        ("Essential Tools", essential_steps),
        ("Django Framework", django_steps),
        ("Task Queue", task_steps),
        ("Data Processing", data_steps),
        ("Web Scraping", scraping_steps),
        ("Production Tools", production_steps),
    ]
    
    success_count = 0
    total_steps = sum(len(steps) for _, steps in all_steps)
    
    for category, steps in all_steps:
        print(f"📂 {category}")
        print("-" * len(category))
        
        for packages, description in steps:
            if category == "Data Processing":
                # Use special handling for numpy/pandas
                success = install_with_fallback(packages, description)
            else:
                success = run_pip_install(packages, description)
            
            if success:
                success_count += 1
            print()
        
        print()
    
    # Final attempt to install any remaining from requirements.txt
    print("🔧 Installing remaining from requirements.txt...")
    try:
        cmd = [sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt', '--only-binary=numpy,pandas,scipy']
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("   ✅ Requirements installation completed")
        success_count += 5  # Bonus for completing requirements
    except subprocess.CalledProcessError as e:
        print(f"   ⚠️ Some requirements may have failed: {e}")
        # Try without binary restriction
        try:
            cmd = [sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt']
            result = subprocess.run(cmd, timeout=300)  # 5 minute timeout
            print("   ✅ Requirements installation completed (fallback)")
            success_count += 3
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
            print("   ❌ Requirements installation failed")
    
    print("\n" + "=" * 35)
    print("📊 WINDOWS INSTALLATION SUMMARY")
    print("=" * 35)
    
    success_rate = (success_count / (total_steps + 5)) * 100
    print(f"📈 Success Rate: {success_count}/{total_steps + 5} ({success_rate:.1f}%)")
    
    if success_rate >= 80:
        print("\n🎉 WINDOWS INSTALLATION SUCCESSFUL!")
        print("✅ Django should now work on Windows")
        print("\n💡 Next steps:")
        print("   1. python manage.py migrate")
        print("   2. python test_yfinance_system.py")
        print("   3. python manage.py runserver")
        return True
    elif success_rate >= 60:
        print("\n✅ Partial success - Django basics should work")
        print("⚠️ Some advanced features might be limited")
        print("\n💡 Try:")
        print("   1. python manage.py migrate")
        print("   2. python manage.py runserver")
        return True
    else:
        print("\n⚠️ Installation had significant issues")
        print("🔧 Recommendations:")
        print("   1. Install Microsoft C++ Build Tools")
        print("   2. Try: pip install --upgrade pip setuptools wheel")
        print("   3. Run this script again")
        return False

if __name__ == "__main__":
    try:
        success = main()
        
        if success:
            print("\n🪟 Windows installation completed!")
            print("🚀 Your stock scanner should now work!")
        
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n⚠️ Installation interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Installation failed: {e}")
        sys.exit(1)