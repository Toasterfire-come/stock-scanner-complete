#!/usr/bin/env python
"""
Windows-Safe Package Installer
Installs packages using binary wheels to avoid C compiler issues on Windows.

This script specifically handles packages that commonly fail on Windows:
- numpy (requires MSVC compiler)
- pandas (depends on numpy)
- lxml (requires libxml2/libxslt)
- cryptography (requires Rust compiler)

Usage:
    python install_windows_safe.py

Author: Stock Scanner Project
Version: 1.0.0 - Windows Optimized
"""

import subprocess
import sys
import os
from pathlib import Path

def print_header(title):
    """Print a formatted header"""
    print("\n" + "=" * 60)
    print(f"🪟 {title}")
    print("=" * 60)

def print_step(message):
    """Print a formatted step message"""
    print(f"\n🔧 {message}")

def print_success(message):
    """Print a formatted success message"""
    print(f"✅ {message}")

def print_error(message):
    """Print a formatted error message"""
    print(f"❌ {message}")

def print_warning(message):
    """Print a formatted warning message"""
    print(f"⚠️  {message}")

def run_pip_command(command, description):
    """Run a pip command with error handling"""
    print_step(f"{description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print_success(f"{description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"{description} failed")
        print(f"Command: {command}")
        print(f"Error: {e.stderr}")
        return False

def install_problematic_packages():
    """Install packages that commonly fail on Windows using binary wheels"""
    print_header("INSTALLING PROBLEMATIC PACKAGES WITH BINARY WHEELS")
    
    # Define problematic packages with specific installation methods
    problematic_packages = [
        {
            'name': 'numpy',
            'command': 'pip install --only-binary=numpy "numpy>=1.24.0,<1.27.0"',
            'description': 'Installing NumPy (binary wheel only)',
            'fallback': 'pip install numpy==1.24.4'
        },
        {
            'name': 'pandas', 
            'command': 'pip install --only-binary=pandas "pandas>=2.0.0,<2.3.0"',
            'description': 'Installing Pandas (binary wheel only)',
            'fallback': 'pip install pandas==2.0.3'
        },
        {
            'name': 'lxml',
            'command': 'pip install --only-binary=lxml "lxml>=4.9.0"',
            'description': 'Installing lxml (binary wheel only)',
            'fallback': 'pip install lxml==4.9.3'
        },
        {
            'name': 'cryptography',
            'command': 'pip install --only-binary=cryptography "cryptography>=41.0.0"',
            'description': 'Installing cryptography (binary wheel only)',
            'fallback': 'pip install cryptography==41.0.7'
        }
    ]
    
    installed_packages = []
    failed_packages = []
    
    for package in problematic_packages:
        print(f"\n📦 Processing {package['name']}...")
        
        # Try main installation command
        if run_pip_command(package['command'], package['description']):
            installed_packages.append(package['name'])
        else:
            print_warning(f"Main installation failed, trying fallback...")
            # Try fallback command
            if run_pip_command(package['fallback'], f"Installing {package['name']} (fallback version)"):
                installed_packages.append(package['name'])
            else:
                failed_packages.append(package['name'])
                print_error(f"Both main and fallback installation failed for {package['name']}")
    
    return installed_packages, failed_packages

def install_remaining_requirements():
    """Install remaining packages from requirements.txt, excluding problematic ones"""
    print_header("INSTALLING REMAINING REQUIREMENTS")
    
    # Read requirements.txt and filter out problematic packages
    try:
        with open('requirements.txt', 'r') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print_error("requirements.txt not found")
        return False
    
    # Filter out problematic packages
    problematic_keywords = ['numpy', 'pandas', 'lxml', 'cryptography']
    safe_requirements = []
    
    for line in lines:
        line = line.strip()
        if line and not line.startswith('#') and not line.startswith('--'):
            # Check if line contains problematic packages
            is_problematic = any(keyword in line.lower() for keyword in problematic_keywords)
            if not is_problematic:
                safe_requirements.append(line)
    
    if not safe_requirements:
        print_warning("No safe requirements to install")
        return True
    
    # Create temporary requirements file
    temp_req_file = 'requirements_safe.txt'
    try:
        with open(temp_req_file, 'w') as f:
            f.write('\n'.join(safe_requirements))
        
        # Install safe requirements
        command = f'pip install -r {temp_req_file}'
        success = run_pip_command(command, "Installing safe requirements")
        
        # Clean up temporary file
        os.remove(temp_req_file)
        
        return success
    except Exception as e:
        print_error(f"Failed to create temporary requirements file: {e}")
        return False

def verify_installations():
    """Verify that critical packages are installed and working"""
    print_header("VERIFYING INSTALLATIONS")
    
    test_packages = [
        ('django', 'Django framework'),
        ('numpy', 'NumPy for numerical computing'),
        ('pandas', 'Pandas for data manipulation'),
        ('requests', 'HTTP requests library'),
        ('yfinance', 'Yahoo Finance API'),
        ('rest_framework', 'Django REST Framework'),
    ]
    
    successful_imports = []
    failed_imports = []
    
    for package, description in test_packages:
        print_step(f"Testing {description}...")
        try:
            __import__(package)
            print_success(f"{description} import successful")
            successful_imports.append(package)
        except ImportError as e:
            print_error(f"{description} import failed: {e}")
            failed_imports.append(package)
    
    return successful_imports, failed_imports

def main():
    """Main installation function"""
    print_header("WINDOWS-SAFE PACKAGE INSTALLER")
    print("🎯 This script installs packages safely on Windows without C compiler issues")
    print("⏱️  Estimated time: 5-10 minutes depending on internet speed")
    
    # Step 1: Upgrade pip
    print_step("Upgrading pip...")
    upgrade_success = run_pip_command(
        "python -m pip install --upgrade pip", 
        "Upgrading pip to latest version"
    )
    
    if not upgrade_success:
        print_warning("Pip upgrade failed, continuing with existing version...")
    
    # Step 2: Install problematic packages with binary wheels
    installed_problematic, failed_problematic = install_problematic_packages()
    
    # Step 3: Install remaining requirements
    remaining_success = install_remaining_requirements()
    
    # Step 4: Verify installations
    successful_imports, failed_imports = verify_installations()
    
    # Step 5: Final report
    print_header("INSTALLATION REPORT")
    
    print(f"\n📊 Summary:")
    print(f"   Problematic packages installed: {len(installed_problematic)}")
    print(f"   Problematic packages failed: {len(failed_problematic)}")
    print(f"   Remaining requirements: {'✅ Success' if remaining_success else '❌ Failed'}")
    print(f"   Successful imports: {len(successful_imports)}")
    print(f"   Failed imports: {len(failed_imports)}")
    
    if installed_problematic:
        print(f"\n✅ Successfully installed problematic packages:")
        for package in installed_problematic:
            print(f"   - {package}")
    
    if failed_problematic:
        print(f"\n❌ Failed to install:")
        for package in failed_problematic:
            print(f"   - {package}")
        print("\n💡 Solutions for failed packages:")
        print("   1. Install Microsoft Visual Studio Build Tools")
        print("   2. Use conda instead of pip: conda install <package>")
        print("   3. Download pre-compiled wheels from https://www.lfd.uci.edu/~gohlke/pythonlibs/")
    
    if failed_imports:
        print(f"\n⚠️  Import failures:")
        for package in failed_imports:
            print(f"   - {package}")
        print("\n🔧 Next steps:")
        print("   1. Run: pip install <failed_package>")
        print("   2. Check for typos in package names")
        print("   3. Verify virtual environment is activated")
    
    # Determine overall success
    critical_packages = ['django', 'numpy', 'pandas', 'requests', 'yfinance']
    critical_success = all(pkg in successful_imports for pkg in critical_packages)
    
    if critical_success:
        print_success("\n🎉 All critical packages installed successfully!")
        print("🚀 You can now run: python manage.py runserver")
        return True
    else:
        print_error("\n💥 Some critical packages failed to install")
        print("🔧 Please address the issues above before running the application")
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️ Installation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)