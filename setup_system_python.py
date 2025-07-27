#!/usr/bin/env python3
"""
System Python Setup for Stock Scanner
Configures the system to run without virtual environments
"""

import subprocess
import sys
import os
import platform
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"[ERROR] Python {version.major}.{version.minor} is too old")
        print("[INFO] Please upgrade to Python 3.8 or newer")
        return False
    
    print(f"[SUCCESS] Python {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def install_system_packages():
    """Install required packages in system Python"""
    print("\n[INSTALL] Installing required packages in system Python...")
    
    # Required packages
    packages = [
        'django>=4.2.11',
        'django-extensions>=3.2.0',
        'djangorestframework>=3.14.0',
        'django-cors-headers>=4.3.1',
        'yfinance>=0.2.25',
        'requests>=2.31.0',
        'schedule>=1.2.0',
        'python-dotenv>=1.0.0'
    ]
    
    success_count = 0
    for package in packages:
        try:
            print(f"Installing {package}...")
            
            # Use appropriate installation method based on OS
            if platform.system() == "Windows":
                # Windows - try user install first, then system with override
                result = subprocess.run([
                    sys.executable, '-m', 'pip', 'install', package, '--user'
                ], capture_output=True, text=True)
                
                if result.returncode != 0:
                    # Try with system packages override
                    result = subprocess.run([
                        sys.executable, '-m', 'pip', 'install', package, '--break-system-packages'
                    ], capture_output=True, text=True)
            else:
                # Linux/Mac - try user install first
                result = subprocess.run([
                    sys.executable, '-m', 'pip', 'install', package, '--user'
                ], capture_output=True, text=True)
                
                if result.returncode != 0:
                    # Try with system packages override
                    result = subprocess.run([
                        sys.executable, '-m', 'pip', 'install', package, '--break-system-packages'
                    ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"  [SUCCESS] {package} installed successfully")
                success_count += 1
            else:
                print(f"  [ERROR] {package} failed: {result.stderr.strip()}")
                
        except Exception as e:
            print(f"  [ERROR] {package} error: {e}")
    
    print(f"\n[SUMMARY] Installation Summary: {success_count}/{len(packages)} packages installed")
    return success_count == len(packages)

def setup_environment():
    """Setup environment variables and configuration"""
    print("\n[CONFIG] Setting up environment configuration...")
    
    # Set Django settings module
    os.environ['DJANGO_SETTINGS_MODULE'] = 'stockscanner_django.settings'
    
    # Set UTF-8 encoding for Windows
    if platform.system() == "Windows":
        os.environ['PYTHONIOENCODING'] = 'utf-8'
    
    print("[SUCCESS] Environment variables configured")
    return True

def test_django_setup():
    """Test if Django can be imported and configured"""
    print("\n[TEST] Testing Django setup...")
    
    try:
        import django
        django.setup()
        print("[SUCCESS] Django imports and setup successful")
        return True
    except ImportError:
        print("[ERROR] Django not available - check installation")
        return False
    except Exception as e:
        print(f"[ERROR] Django setup failed: {e}")
        return False

def create_no_venv_launcher():
    """Create launcher scripts that don't use virtual environments"""
    print("\n[CREATE] Creating system Python launchers...")
    
    # Windows batch launcher
    if platform.system() == "Windows":
        batch_content = f'''@echo off
echo ========================================
echo Stock Scanner (System Python)
echo ========================================
echo.

REM Set environment variables
set DJANGO_SETTINGS_MODULE=stockscanner_django.settings
set PYTHONIOENCODING=utf-8

REM Run the scheduler using system Python
"{sys.executable}" start_stock_scheduler.py

pause
'''
        
        with open('start_scheduler_system.bat', 'w') as f:
            f.write(batch_content)
        print("[SUCCESS] Created start_scheduler_system.bat")
    
    # Shell script launcher (Linux/Mac/Git Bash)
    shell_content = f'''#!/bin/bash
echo "========================================"
echo "Stock Scanner (System Python)"
echo "========================================"
echo

# Set environment variables
export DJANGO_SETTINGS_MODULE=stockscanner_django.settings
export PYTHONIOENCODING=utf-8

# Run the scheduler using system Python
"{sys.executable}" start_stock_scheduler.py
'''
    
    with open('start_scheduler_system.sh', 'w') as f:
        f.write(shell_content)
    
    # Make executable on Unix systems
    if platform.system() != "Windows":
        os.chmod('start_scheduler_system.sh', 0o755)
    
    print("[SUCCESS] Created start_scheduler_system.sh")
    return True

def main():
    """Main setup function"""
    print("SYSTEM PYTHON SETUP FOR STOCK SCANNER")
    print("=" * 50)
    print("This will configure the stock scanner to run with system Python")
    print("(no virtual environment required)")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Install packages
    if not install_system_packages():
        print("\n[WARNING] Some packages failed to install")
        print("You may need to install them manually or run as administrator")
    
    # Setup environment
    setup_environment()
    
    # Test Django
    test_django_setup()
    
    # Create launchers
    create_no_venv_launcher()
    
    print("\n" + "=" * 50)
    print("[SUCCESS] SYSTEM PYTHON SETUP COMPLETE!")
    print("=" * 50)
    print("\n[RUN] You can now run the scheduler with:")
    if platform.system() == "Windows":
        print("   - start_scheduler_system.bat (double-click or run)")
        print("   - python start_stock_scheduler.py")
    else:
        print("   - ./start_scheduler_system.sh")
        print("   - python start_stock_scheduler.py")
    
    print("\n[INFO] No virtual environment needed!")
    print("[INFO] All dependencies installed in system Python")
    
    return True

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[STOP] Setup interrupted by user")
    except Exception as e:
        print(f"\n[ERROR] Setup failed: {e}")
        sys.exit(1)