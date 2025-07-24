# 🪟 Windows Setup Guide - Stock Scanner
**Complete solution for Windows compilation issues and setup problems**

![Windows](https://img.shields.io/badge/Windows-Compatible-blue)
![Python](https://img.shields.io/badge/Python-3.8+-green)
![No_Compiler](https://img.shields.io/badge/No_Compiler_Needed-red)

## 🎯 Overview

This guide solves common Windows setup issues including:
- ❌ **NumPy compilation errors** 
- ❌ **"Unknown compiler" errors**
- ❌ **C/C++ compiler not found**
- ❌ **Visual Studio dependency issues**
- ❌ **Package installation failures**

## 🚨 Common Windows Errors

### **NumPy Compilation Error**
```
ERROR: Unknown compiler(s): [['icl'], ['cl'], ['cc'], ['gcc'], ['clang']]
The following exception(s) were encountered:
Running `cl /?` gave "[WinError 2] The system cannot find the file specified"
```

### **Visual Studio Error**
```
WARNING: Failed to activate VS environment: Could not find C:\Program Files (x86)\Microsoft Visual Studio\Installer\vswhere.exe
```

### **Package Installation Failures**
```
error: subprocess-exited-with-error
× Preparing metadata (pyproject.toml) did not run successfully.
```

## ✅ SOLUTION: Windows Setup Fix

### **🎯 Quick Fix (Recommended)**

Run the automated Windows setup script:

```cmd
# Run from project root directory
WINDOWS_SETUP_FIX.bat
```

This script will:
- ✅ Create fresh virtual environment
- ✅ Install pre-compiled packages (no compilation needed)
- ✅ Configure PyMySQL instead of mysqlclient
- ✅ Set up Windows-compatible database settings
- ✅ Verify installation and fix common issues

### **🛠️ Manual Setup Steps**

If you prefer manual setup or the script fails:

#### **1. Clean Environment**
```cmd
# Remove problematic virtual environment
rmdir /s /q venv

# Create fresh environment
python -m venv venv
venv\Scripts\activate.bat
```

#### **2. Upgrade pip and tools**
```cmd
python -m pip install --upgrade pip
pip install wheel setuptools
```

#### **3. Install Windows-specific requirements**
```cmd
# Use Windows-optimized requirements
pip install -r requirements_windows.txt
```

#### **4. Install packages individually (if batch fails)**
```cmd
# Core packages
pip install Django>=4.2,<5.0
pip install djangorestframework>=3.14.0
pip install PyMySQL>=1.1.0
pip install dj-database-url>=2.1.0
pip install requests>=2.31.0
pip install python-dotenv>=1.0.0

# Data packages (Windows pre-compiled)
pip install numpy==1.24.4
pip install pandas==2.0.3
pip install yfinance>=0.2.25

# Additional packages
pip install celery>=5.3.0
pip install redis>=5.0.0
pip install colorama>=0.4.6
```

## 📦 Windows-Specific Package Solutions

### **NumPy & Pandas Issues**

**Problem**: Compilation from source fails on Windows
**Solution**: Use specific pre-compiled versions

```cmd
# Install specific Windows-compatible versions
pip install numpy==1.24.4
pip install pandas==2.0.3
```

### **MySQL Driver Issues**

**Problem**: `mysqlclient` requires C++ compiler
**Solution**: Use `PyMySQL` as drop-in replacement

```cmd
# Install PyMySQL instead of mysqlclient
pip install PyMySQL>=1.1.0
```

**Automatic Configuration**: The Stock Scanner automatically detects and configures PyMySQL:

```python
# Automatic in settings.py
try:
    import pymysql
    pymysql.install_as_MySQLdb()
    print("✅ PyMySQL configured as MySQL driver")
except ImportError:
    pass  # mysqlclient will be used if available
```

### **PostgreSQL Driver Issues**

**Problem**: `psycopg2` compilation issues
**Solution**: Use binary version

```cmd
# Use pre-compiled binary
pip install psycopg2-binary>=2.9.9
```

## 🎛️ Windows-Specific Configuration

### **Database Settings**

The system automatically configures Windows-compatible database drivers:

```python
# In .env file (Windows development)
DATABASE_URL=sqlite:///db.sqlite3          # Default for development
DATABASE_URL=mysql://user:pass@host/db     # MySQL with PyMySQL
DATABASE_URL=postgresql://user:pass@host/db # PostgreSQL with psycopg2-binary
```

### **Environment Variables**

Create `.env` file for Windows development:

```env
# Stock Scanner Windows Configuration
DEBUG=true
SECRET_KEY=windows-dev-key-change-in-production
DATABASE_URL=sqlite:///db.sqlite3
ALLOWED_HOSTS=localhost,127.0.0.1

# Optional: MySQL configuration
# DATABASE_URL=mysql://stock_scanner_user:password@localhost/stock_scanner_db

# Optional: Redis configuration
# REDIS_URL=redis://localhost:6379/0
```

## 🔧 Troubleshooting Common Issues

### **Issue 1: Virtual Environment Creation Fails**
```cmd
# Solution: Use full Python path
C:\Python\python.exe -m venv venv

# Or update Python
# Download latest from python.org
```

### **Issue 2: pip is not recognized**
```cmd
# Solution: Add Python to PATH or use full path
C:\Python\Scripts\pip.exe install package_name

# Or reinstall Python with "Add to PATH" option
```

### **Issue 3: Permission Denied Errors**
```cmd
# Solution: Run Command Prompt as Administrator
# Right-click → "Run as administrator"
```

### **Issue 4: Package still fails to install**
```cmd
# Solution: Try with --only-binary flag
pip install --only-binary=all package_name

# Or use conda
conda install package_name
```

### **Issue 5: Django import errors**
```cmd
# Solution: Verify virtual environment activation
venv\Scripts\activate.bat
python -c "import django; print(django.VERSION)"
```

## 🚀 Windows Production Setup

### **For Production on Windows Server**

```cmd
# 1. Install Python 3.8+ from python.org
# 2. Install Git for Windows
# 3. Clone repository
git clone https://github.com/your-username/stock-scanner-complete
cd stock-scanner-complete

# 4. Run Windows setup
WINDOWS_SETUP_FIX.bat

# 5. Configure production database
# Edit .env file with production settings

# 6. Setup MySQL (if using)
# Download MySQL Community Server
# Configure database and user

# 7. Load ticker data
LOAD_COMPLETE_NASDAQ.bat

# 8. Start production server
START_HERE.bat
```

### **Windows Service Setup (Optional)**

For running as Windows service:

```cmd
# Install Windows service wrapper
pip install pywin32

# Create service script (advanced)
python manage.py runserver 0.0.0.0:8000 --settings=stockscanner_django.production_settings
```

## 📊 Windows Performance Tips

### **1. Use SSD Storage**
- Install Python and project on SSD
- Use SSD for database files
- Faster package installation and Django operations

### **2. Increase Virtual Memory**
- Windows Settings → System → Advanced → Performance → Settings
- Increase virtual memory for large dataset processing

### **3. Disable Windows Defender Real-time Scanning**
- Add project folder to exclusions
- Speeds up package installation and Django operations

### **4. Use Windows Terminal**
- Better than Command Prompt
- Download from Microsoft Store
- Supports multiple tabs and better formatting

## 🛡️ Windows Security Considerations

### **Firewall Configuration**
```cmd
# Allow Django development server
netsh advfirewall firewall add rule name="Django Dev Server" dir=in action=allow protocol=TCP localport=8000

# Allow MySQL (if using)
netsh advfirewall firewall add rule name="MySQL" dir=in action=allow protocol=TCP localport=3306
```

### **User Account Control (UAC)**
- Run setup scripts as Administrator when needed
- Some package installations require elevated privileges

## 🎯 Verification Steps

After setup, verify everything works:

### **1. Test Python Environment**
```cmd
venv\Scripts\activate.bat
python --version
pip list
```

### **2. Test Django**
```cmd
python manage.py check
python manage.py migrate
python manage.py runserver
```

### **3. Test Database Connection**
```cmd
python manage.py shell
>>> from django.db import connection
>>> cursor = connection.cursor()
>>> cursor.execute("SELECT 1")
>>> print("✅ Database connection working")
```

### **4. Test Stock Scanner Components**
```cmd
python -c "import yfinance; print('✅ yfinance working')"
python -c "import pandas; print('✅ pandas working')"
python -c "import numpy; print('✅ numpy working')"
```

## 📞 Getting Help

### **If Issues Persist:**

1. **Update Python**: Download latest from [python.org](https://www.python.org/downloads/)
2. **Check Windows Version**: Windows 10/11 recommended
3. **Install Visual Studio Build Tools** (only if absolutely necessary):
   - Download: Visual Studio Build Tools
   - Install: C++ build tools
   - ⚠️ **Warning**: 3GB+ download, try other solutions first

4. **Use Alternative Installation Methods**:
   ```cmd
   # Try conda instead of pip
   conda install package_name
   
   # Try wheels from unofficial binaries
   # Download .whl files from: https://www.lfd.uci.edu/~gohlke/pythonlibs/
   pip install package_name.whl
   ```

5. **Contact Support**:
   - Create GitHub issue with error details
   - Include Windows version, Python version, and full error message

## ✅ Success Checklist

After successful setup, you should have:

- ✅ Python virtual environment activated
- ✅ Django running without errors
- ✅ Database connection working
- ✅ All packages installed (numpy, pandas, yfinance)
- ✅ Stock Scanner components functional
- ✅ Ready to load ticker data and start scanning

## 🎉 Conclusion

The Windows Setup Fix provides a comprehensive solution for Windows-specific issues in the Stock Scanner project. By using pre-compiled packages and Windows-compatible alternatives, you can avoid compilation errors and get up and running quickly.

**Ready to scan stocks on Windows!** 🚀📈

---

### **Quick Commands Summary**

```cmd
# Complete Windows setup
WINDOWS_SETUP_FIX.bat

# Test installation
python manage.py runserver

# Load ticker data
LOAD_COMPLETE_NASDAQ.bat

# Start stock scanning
START_HERE.bat
```