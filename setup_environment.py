#!/usr/bin/env python3
"""
Environment Setup Script
Installs missing packages and configures the stock scanner environment
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    """Run a command and return success status"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"   ✅ {description} completed")
        if result.stdout.strip():
            print(f"   📄 Output: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"   ❌ {description} failed: {e}")
        if e.stderr:
            print(f"   📄 Error: {e.stderr.strip()}")
        return False

def check_python_version():
    """Check if Python version is supported"""
    print("🐍 Checking Python version...")
    if sys.version_info < (3, 8):
        print(f"   ❌ Python {sys.version_info.major}.{sys.version_info.minor} is too old. Need Python 3.8+")
        return False
    else:
        print(f"   ✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro} is supported")
        return True

def check_virtual_environment():
    """Check if we're in a virtual environment"""
    print("📦 Checking virtual environment...")
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("   ✅ Virtual environment is active")
        return True
    else:
        print("   ⚠️ Not in a virtual environment")
        print("   💡 Recommendation: Create and activate a virtual environment first")
        return False

def install_requirements():
    """Install packages from requirements.txt"""
    print("📦 Installing Python packages...")
    
    # First upgrade pip
    if not run_command(f"{sys.executable} -m pip install --upgrade pip", "Upgrading pip"):
        return False
    
    # Install requirements
    if not run_command(f"{sys.executable} -m pip install -r requirements.txt", "Installing requirements"):
        return False
    
    return True

def create_env_file():
    """Create .env file from .env.example if it doesn't exist"""
    print("⚙️ Setting up environment configuration...")
    
    env_file = Path('.env')
    env_example = Path('.env.example')
    
    if env_file.exists():
        print("   ✅ .env file already exists")
        return True
    
    if not env_example.exists():
        print("   ❌ .env.example file not found")
        return False
    
    try:
        # Copy .env.example to .env
        with open(env_example, 'r') as source:
            content = source.read()
        
        with open(env_file, 'w') as target:
            target.write(content)
        
        print("   ✅ Created .env file from .env.example")
        print("   💡 Edit .env file to add your API keys")
        return True
        
    except Exception as e:
        print(f"   ❌ Failed to create .env file: {e}")
        return False

def test_django_setup():
    """Test if Django can start"""
    print("🔧 Testing Django setup...")
    
    try:
        # Set environment variable
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stockscanner_django.settings')
        
        # Try to import Django and configure
        import django
        django.setup()
        
        print("   ✅ Django configuration loaded successfully")
        return True
        
    except Exception as e:
        print(f"   ❌ Django setup failed: {e}")
        return False

def run_migrations():
    """Run Django migrations"""
    print("🗄️ Setting up database...")
    
    # Create migrations
    if not run_command(f"{sys.executable} manage.py makemigrations", "Creating migrations"):
        print("   ⚠️ Migration creation failed - this might be normal if no changes detected")
    
    # Apply migrations
    if not run_command(f"{sys.executable} manage.py migrate", "Applying migrations"):
        return False
    
    return True

def test_api_manager():
    """Test the API manager"""
    print("🧪 Testing API manager...")
    
    try:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stockscanner_django.settings')
        import django
        django.setup()
        
        from stocks.api_manager import stock_manager
        
        # Test initialization
        print("   ✅ API manager imported successfully")
        
        # Test basic functionality
        usage_stats = stock_manager.get_usage_stats()
        print(f"   📊 Configured APIs: {len(usage_stats)}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ API manager test failed: {e}")
        return False

def main():
    """Main setup process"""
    print("🚀 Stock Scanner Environment Setup")
    print("=" * 40)
    
    # Check prerequisites
    if not check_python_version():
        return False
    
    # Check virtual environment (warning only)
    check_virtual_environment()
    
    # Setup steps
    steps = [
        ("Install Python packages", install_requirements),
        ("Create environment file", create_env_file),
        ("Test Django configuration", test_django_setup),
        ("Setup database", run_migrations),
        ("Test API manager", test_api_manager),
    ]
    
    results = []
    
    for step_name, step_func in steps:
        print(f"\n📋 {step_name}")
        print("-" * 30)
        
        try:
            result = step_func()
            results.append((step_name, result))
            
            if result:
                print(f"✅ {step_name}: SUCCESS")
            else:
                print(f"❌ {step_name}: FAILED")
                
        except Exception as e:
            print(f"💥 {step_name}: ERROR - {e}")
            results.append((step_name, False))
    
    # Summary
    print("\n" + "=" * 40)
    print("📊 SETUP SUMMARY")
    print("=" * 40)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for step_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status} - {step_name}")
    
    print(f"\n📈 Results: {passed}/{total} steps completed ({(passed/total*100):.1f}%)")
    
    if passed == total:
        print("🎉 SETUP COMPLETE!")
        print("✅ Your stock scanner environment is ready!")
        print("\n💡 Next steps:")
        print("   1. Edit .env file to add your API keys")
        print("   2. Run: python test_yfinance_system.py")
        print("   3. Run: python manage.py update_stocks_yfinance --test-mode")
        print("   4. Start the server: python manage.py runserver")
    elif passed >= total * 0.8:
        print("✅ Most setup steps completed. System should be functional.")
        print("⚠️ Review any failed steps above.")
    else:
        print("⚠️ Several setup steps failed.")
        print("🔧 Please review errors and try again.")
    
    return passed >= total * 0.8

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️ Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Setup failed: {e}")
        sys.exit(1)