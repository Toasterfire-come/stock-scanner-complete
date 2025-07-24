# 🚀 Stock Scanner - Linux Production Setup

**Single Command Setup: `./setup_linux_complete.sh`**

## 🎯 Quick Start

```bash
# Clone the repository
git clone https://github.com/Toasterfire-come/stock-scanner-complete.git
cd stock-scanner-complete

# Run the complete setup (single command)
chmod +x setup_linux_complete.sh
./setup_linux_complete.sh

# Start the application
./start_stock_scanner.sh
```

## 📁 Project Structure

```
stock-scanner/
├── 🚀 setup_linux_complete.sh   # Single setup script (START HERE!)
├── 🌐 start_stock_scanner.sh    # Application launcher
├── 📊 manage.py                 # Django management
├── 📋 requirements.txt          # Linux dependencies
│
├── 📂 stocks/                   # Main application
├── 📂 data/nasdaq_only/         # NASDAQ ticker data
├── 📂 tools/                    # Utility scripts
├── 📂 setup/                    # Setup configurations
└── 📂 docs/                     # Documentation
```

## 🎯 What This Setup Includes

✅ **MySQL Database** - Production-ready configuration  
✅ **Django Framework** - Web application backend  
✅ **yfinance Integration** - Real-time stock data  
✅ **NASDAQ-Only Tickers** - Focus on NASDAQ securities  
✅ **Automated Testing** - Complete system verification  
✅ **Linux Compatibility** - Ubuntu/Debian/CentOS/RHEL/Fedora  

## 🛠️ System Requirements

- **Linux OS**: Ubuntu 18.04+, Debian 10+, CentOS 7+, RHEL 7+, or Fedora 30+
- **Python**: 3.8+ (automatically installed)
- **MySQL**: 5.7+ or 8.0+ (automatically installed)
- **Memory**: 2GB+ RAM recommended
- **Storage**: 1GB+ free space

## 🚀 Quick Commands

After setup completion:

```bash
# Start the stock scanner
./start_stock_scanner.sh

# Load/update NASDAQ tickers
source venv/bin/activate
python manage.py load_nasdaq_only --update-existing

# Backup database
./setup/scripts/backup_database.sh

# Create admin user
source venv/bin/activate
python manage.py createsuperuser
```

## 🌐 Access Points

- **Main Application**: http://localhost:8000
- **Django Admin**: http://localhost:8000/admin
- **API Endpoint**: http://localhost:8000/api/stocks

## 📚 Documentation

- **Setup Info**: `setup/configs/installation_info.txt`
- **NASDAQ Guide**: `docs/NASDAQ_ONLY_GUIDE.md`
- **MySQL Production**: `docs/production/MYSQL_PRODUCTION_GUIDE.md`
- **Setup Logs**: `setup.log`

## 🔧 Management Commands

```bash
# Activate virtual environment first
source venv/bin/activate

# Django management
python manage.py load_nasdaq_only              # Load NASDAQ tickers
python manage.py makemigrations                # Create migrations  
python manage.py migrate                       # Apply migrations
python manage.py collectstatic                 # Collect static files
python manage.py createsuperuser               # Create admin user

# Database management
./setup/scripts/backup_database.sh             # Backup database
mysql -u stock_scanner -p stock_scanner_nasdaq # Connect to database
```

## ⚠️ Troubleshooting

### Setup Issues
- **Permission denied**: Run with `sudo ./setup_linux_complete.sh`
- **MySQL fails**: Check if port 3306 is available
- **Python errors**: Ensure Python 3.8+ is installed

### Runtime Issues  
- **Can't connect to database**: Check MySQL service status
- **yfinance errors**: Check internet connection
- **Import errors**: Reactivate virtual environment

### Getting Help
- Check setup logs: `cat setup.log`
- View installation info: `cat setup/configs/installation_info.txt`
- Test installation: Run the built-in tests during setup

## 🎯 Features

- **NASDAQ-Only Focus**: Streamlined for NASDAQ securities
- **Real-time Data**: yfinance integration for live market data
- **Production Ready**: MySQL database with optimized settings
- **Automated Setup**: Single script handles everything
- **Linux Native**: Optimized for Linux server environments
- **Backup System**: Automated database backup scripts
- **Health Monitoring**: Built-in system health checks

## 🚀 Production Deployment

The setup script configures everything for production use:

- **Security**: DEBUG=False, secure SECRET_KEY, proper ALLOWED_HOSTS
- **Database**: MySQL with optimized connection pooling
- **Performance**: Static file optimization, database indexing
- **Monitoring**: Health checks and backup systems
- **Logging**: Comprehensive logging configuration

## 📊 NASDAQ Ticker System

The application focuses exclusively on NASDAQ-listed securities:

- **Automatic Download**: Fetches latest NASDAQ ticker list
- **Fallback System**: Core tickers available if download fails  
- **Database Integration**: Seamless loading into Django models
- **Update Mechanism**: Easy ticker list updates

## 🎉 Ready to Start?

**Run the setup script and you'll be scanning NASDAQ stocks in minutes!**

```bash
./setup_linux_complete.sh
```
