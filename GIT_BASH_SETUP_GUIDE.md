# 🪟 Stock Scanner - Git Bash Setup for Windows

## 🚀 Quick Start (Single Command)

```bash
# In Git Bash, navigate to your project and run:
cd /c/Stock-scanner-project/stock-scanner-complete
chmod +x setup_gitbash_complete.sh
./setup_gitbash_complete.sh
```

## 📋 Prerequisites

Before running the setup, ensure you have:

1. **Python 3.8+** installed
   - Download from: https://python.org/downloads/
   - ⚠️ **IMPORTANT**: Check "Add Python to PATH" during installation

2. **MySQL Server 8.0+** installed
   - Download from: https://dev.mysql.com/downloads/mysql/
   - Remember your root password

3. **Git Bash** installed
   - Comes with Git for Windows: https://git-scm.com/download/win

## 🗂️ Path Navigation in Git Bash

Your Windows path: `C:\Stock-scanner-project\stock-scanner-complete`
Git Bash path: `/c/Stock-scanner-project/stock-scanner-complete`

### Navigation Commands:
```bash
# Navigate to your project
cd /c/Stock-scanner-project/stock-scanner-complete

# Verify you're in the right place
pwd
ls -la

# You should see setup_gitbash_complete.sh
```

## 🎯 What the Script Does

The Git Bash setup script automatically:

✅ **Environment Detection** - Detects Windows/Git Bash environment  
✅ **Prerequisites Check** - Verifies Python, pip, and MySQL  
✅ **Virtual Environment** - Creates and activates Python venv  
✅ **Package Installation** - Installs all required packages (with Windows compatibility)  
✅ **MySQL Configuration** - Sets up database and user  
✅ **Django Setup** - Configures Django with migrations  
✅ **NASDAQ Tickers** - Downloads and loads NASDAQ-only tickers  
✅ **Testing** - Comprehensive system testing  
✅ **Startup Scripts** - Creates both .bat and .sh startup files  

## 🔧 Key Differences from Linux Version

### Windows Compatibility Features:
- **PyMySQL Fallback**: Uses PyMySQL if mysqlclient compilation fails
- **Path Handling**: Converts Windows paths to Unix-style for Git Bash
- **Multiple Python Detection**: Checks for `python`, `python3`, and `py` commands
- **MySQL Path Detection**: Searches common Windows MySQL installation paths
- **Dual Startup Scripts**: Creates both `.bat` and `.sh` startup files

### Virtual Environment:
- **Linux**: `venv/bin/activate`
- **Windows Git Bash**: `venv/Scripts/activate`

## 🚀 Complete Setup Process

```bash
# 1. Open Git Bash and navigate to your project
cd /c/Stock-scanner-project/stock-scanner-complete

# 2. Make the script executable
chmod +x setup_gitbash_complete.sh

# 3. Run the setup (will take 5-10 minutes)
./setup_gitbash_complete.sh

# 4. Script will automatically use your MySQL root password: stockscanner2010

# 5. After completion, start the application
./start_gitbash.sh
# OR double-click start_windows.bat
```

## 🌐 Startup Options

After setup completion, you have multiple ways to start:

### Option 1: Windows Batch File (Easiest)
```cmd
# Double-click this file in Windows Explorer
start_windows.bat
```

### Option 2: Git Bash Script
```bash
./start_gitbash.sh
```

### Option 3: Manual
```bash
# Activate virtual environment
source venv/Scripts/activate

# Start Django server
python manage.py runserver
```

## 📊 Access Points

- **Main Application**: http://localhost:8000
- **Django Admin**: http://localhost:8000/admin
- **API Endpoint**: http://localhost:8000/api/stocks

## 🔧 Management Commands

```bash
# Always activate virtual environment first
source venv/Scripts/activate

# Load/update NASDAQ tickers
python manage.py load_nasdaq_only --update-existing

# Create admin user
python manage.py createsuperuser

# Django management
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic
```

## 🗄️ Database Configuration

The script automatically creates:
- **Database**: `stock_scanner_nasdaq`
- **User**: `stock_scanner`
- **Password**: `StockScanner2024!`
- **MySQL Root**: Uses your password `stockscanner2010`

### Manual MySQL Setup (if needed):
```sql
-- Using your MySQL root password: stockscanner2010
CREATE DATABASE stock_scanner_nasdaq CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'stock_scanner'@'localhost' IDENTIFIED BY 'StockScanner2024!';
GRANT ALL PRIVILEGES ON stock_scanner_nasdaq.* TO 'stock_scanner'@'localhost';
FLUSH PRIVILEGES;
```

### Quick MySQL Test:
```bash
# Test your root connection
mysql -u root -pstockscanner2010

# Test application connection
mysql -u stock_scanner -pStockScanner2024! stock_scanner_nasdaq
```

## 📁 Project Structure After Setup

```
stock-scanner-complete/
├── 🚀 setup_gitbash_complete.sh    # Main setup script
├── 🌐 start_windows.bat           # Windows startup
├── 🌐 start_gitbash.sh            # Git Bash startup
├── 📊 manage.py                   # Django management
├── 📋 requirements.txt            # Dependencies
│
├── 📂 venv/                       # Virtual environment
│   └── Scripts/activate           # Windows activation script
│
├── 📂 data/nasdaq_only/           # NASDAQ ticker data
├── 📂 setup/                      # Setup configurations
│   ├── configs/                   # Installation info
│   └── scripts/                   # Management scripts
│
├── 📂 stocks/                     # Main Django app
└── 📂 stockscanner_django/        # Django settings
```

## ⚠️ Troubleshooting

### Common Issues:

#### 1. "Python not found"
```bash
# Check if Python is in PATH
python --version
python3 --version
py --version

# If none work, reinstall Python with "Add to PATH" checked
```

#### 2. "MySQL not found"
```bash
# Add MySQL to PATH or install from:
# https://dev.mysql.com/downloads/mysql/

# Or use full path
"/c/Program Files/MySQL/MySQL Server 8.0/bin/mysql.exe" --version
```

#### 3. "Permission denied"
```bash
# Make script executable
chmod +x setup_gitbash_complete.sh

# Check current permissions
ls -la setup_gitbash_complete.sh
```

#### 4. "mysqlclient installation failed"
This is normal on Windows. The script automatically falls back to PyMySQL.

#### 5. Virtual environment issues
```bash
# Remove and recreate
rm -rf venv
python -m venv venv
source venv/Scripts/activate
```

### Getting Help:
- **Setup logs**: `cat setup.log`
- **Installation info**: `cat setup/configs/installation_info.txt`
- **Django logs**: Check `logs/` directory

## 🎯 Features Included

### Core Functionality:
- **NASDAQ-Only Focus**: Streamlined for NASDAQ securities
- **Real-time Data**: yfinance integration for live market data
- **MySQL Database**: Production-ready database setup
- **Django Admin**: Web-based administration interface

### Windows Optimizations:
- **No Compilation Required**: Uses pre-compiled packages when possible
- **PyMySQL Fallback**: Avoids compilation issues with mysqlclient
- **Path Compatibility**: Handles Windows paths in Git Bash
- **Dual Startup**: Both .bat and .sh startup scripts

### NASDAQ Ticker System:
- **Automatic Download**: Fetches latest NASDAQ ticker list from FTP
- **Fallback System**: 40+ core tickers if download fails
- **Database Integration**: Seamless loading into Django models
- **Update Mechanism**: Easy ticker list updates

## 🚀 Production Features

- **Security**: DEBUG=False, secure SECRET_KEY, proper ALLOWED_HOSTS
- **Performance**: Connection pooling, database optimization
- **Logging**: Comprehensive logging system
- **Error Handling**: Graceful fallbacks for network/compilation issues

## 🎉 Success Indicators

After successful setup, you should see:

```
🎉 STOCK SCANNER SETUP COMPLETED SUCCESSFULLY! (Windows Git Bash)
===============================================================================

📊 Setup Summary:
  ✅ Python virtual environment configured
  ✅ Django application setup
  ✅ NASDAQ-only tickers loaded
  ✅ yfinance integration ready
  ✅ Windows startup scripts created

🚀 Quick Start Options:
  Option 1 (Windows): Double-click start_windows.bat
  Option 2 (Git Bash): ./start_gitbash.sh
  Option 3 (Manual): source venv/Scripts/activate && python manage.py runserver

🌐 Access: http://localhost:8000
```

## 📞 Support

### Self-Help Resources:
1. Check logs: `setup.log`
2. Review setup info: `setup/configs/installation_info.txt`
3. Test components individually
4. Verify prerequisites are installed

### Common Commands:
```bash
# Activate environment
source venv/Scripts/activate

# Check Django
python manage.py check

# Test database
python manage.py dbshell

# View NASDAQ count
python manage.py shell -c "from stocks.models import Stock; print(f'NASDAQ: {Stock.objects.filter(exchange=\"NASDAQ\").count()}')"
```

---

**Your Stock Scanner is now ready for Windows development with Git Bash!** 🚀