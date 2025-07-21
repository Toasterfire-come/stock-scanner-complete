# 🚀 Stock Scanner Complete Setup Guide

## 📋 Overview
This guide will walk you through setting up the Stock Scanner application with:
- **Local SQLite Database** (no passwords required)
- **Gmail SMTP** for email notifications
- **yfinance API** for stock data
- **Django REST API** for WordPress integration
- **Security hardening** for production

## ✅ Prerequisites

### System Requirements
- **Python 3.8+** (Python 3.9+ recommended)
- **Git** (for version control)
- **Internet connection** (for stock data and email)

### Accounts Needed
- **Gmail account** with App Password enabled
- **Domain** (optional, for production deployment)

---

## 🔧 Quick Start (5 Minutes)

### 1. **Clone/Download the Project**
```bash
# If using Git
git clone <repository-url>
cd stock-scanner

# Or extract from zip file
unzip stock-scanner.zip
cd stock-scanner
```

### 2. **Run Automated Setup**
```bash
# This will do everything for you
python3 setup_local.py
```

### 3. **Start the Application**
```bash
# Activate virtual environment (if not already active)
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate     # Windows

# Start Django server
python manage.py runserver
```

### 4. **Access the Application**
- **Main Site**: http://localhost:8000
- **Admin Panel**: http://localhost:8000/admin
- **API Docs**: http://localhost:8000/api/

---

## 📝 Manual Setup (Step by Step)

### Step 1: Environment Setup
```bash
# Check Python version
python3 --version  # Should be 3.8+

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Upgrade pip
pip install --upgrade pip
```

### Step 2: Install Dependencies
```bash
# Install from requirements file
pip install -r requirements_secure.txt

# Or install manually
pip install Django yfinance requests djangorestframework django-cors-headers python-dotenv
```

### Step 3: Configure Environment Variables
```bash
# Copy sample environment file
cp .env.sample .env

# Edit .env file with your settings
nano .env  # or use any text editor
```

**Edit `.env` file:**
```bash
# Django Configuration
SECRET_KEY=your-unique-secret-key-here
DEBUG=True
ADMIN_URL=admin

# Database (SQLite - no password needed)
DB_TYPE=sqlite3
DB_NAME=stock_scanner.db

# Email (Gmail SMTP)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-gmail-app-password

# Site Configuration
SITE_URL=http://localhost:8000
ALLOWED_HOSTS=localhost,127.0.0.1

# Stock API
USE_YFINANCE_ONLY=True
STOCK_API_RATE_LIMIT=1.0
```

### Step 4: Setup Database
```bash
# Test database functionality
python3 test_database_setup.py

# Setup SQLite database
python3 database_settings_local.py

# Run Django migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser (admin account)
python manage.py createsuperuser
```

### Step 5: Collect Static Files
```bash
# Collect static files for production
python manage.py collectstatic --noinput
```

### Step 6: Test the Setup
```bash
# Run development server
python manage.py runserver

# In another terminal, test the API
curl http://localhost:8000/api/stocks/
```

---

## 📧 Gmail Setup (Important!)

### Enable Gmail App Password
1. **Go to Google Account Settings**
   - Visit: https://myaccount.google.com/
   - Click "Security" → "2-Step Verification"

2. **Enable 2-Step Verification** (if not already enabled)
   - Follow the prompts to set up 2FA

3. **Generate App Password**
   - Go to "App passwords" section
   - Select "Mail" and "Other (custom name)"
   - Enter "Stock Scanner" as the name
   - Copy the 16-character password

4. **Update .env File**
   ```bash
   EMAIL_HOST_USER=your-email@gmail.com
   EMAIL_HOST_PASSWORD=abcd-efgh-ijkl-mnop  # 16-character app password
   ```

### Test Email Configuration
```bash
# Run email test
python3 -c "
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'stockscanner_django.settings'
import django
django.setup()
from emails.email_config import test_email_connection
print(test_email_connection())
"
```

---

## 🗄️ Database Information

### SQLite Database Details
- **File**: `stock_scanner.db` (created automatically)
- **Location**: Project root directory
- **Backups**: Automatic backups in `backups/` folder
- **No passwords required**: SQLite is file-based

### Database Management Commands
```bash
# Backup database
python3 -c "from database_settings_local import backup_sqlite_database; backup_sqlite_database()"

# Check database health
python3 -c "from database_settings_local import check_database_health; print(check_database_health())"

# Optimize database
python3 -c "from database_settings_local import optimize_sqlite_database; optimize_sqlite_database()"

# Get database size
python3 -c "from database_settings_local import get_database_size; print(get_database_size())"
```

---

## 📊 Stock Data Configuration

### yfinance Setup
- **No API key required**: yfinance is free
- **Rate limiting**: 1 second between requests (configurable)
- **Caching**: 5-minute cache for better performance
- **Supported markets**: All markets supported by Yahoo Finance

### Test Stock Data
```bash
# Test yfinance connection
python3 -c "
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'stockscanner_django.settings'
import django
django.setup()
from stocks.yfinance_config import test_yfinance_connection
print(test_yfinance_connection())
"

# Get sample stock data
python3 -c "
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'stockscanner_django.settings'
import django
django.setup()
from stocks.yfinance_config import get_stock_data
print(get_stock_data('AAPL'))
"
```

---

## 🌐 API Endpoints

### Stock Data API
- **GET** `/api/stocks/` - List all stocks
- **GET** `/api/stocks/{ticker}/` - Get specific stock
- **GET** `/api/stocks/search/` - Search stocks
- **GET** `/api/market-movers/` - Get market movers
- **GET** `/api/stats/` - Get market statistics

### Email Subscription API
- **POST** `/api/wordpress/subscribe/` - Subscribe to email alerts

### Test API Endpoints
```bash
# Test stock list
curl "http://localhost:8000/api/stocks/"

# Test specific stock
curl "http://localhost:8000/api/stocks/AAPL/"

# Test market movers
curl "http://localhost:8000/api/market-movers/"
```

---

## 🔐 Security Configuration

### Development Security
- **Debug mode**: Enabled for development
- **Secret key**: Generated automatically
- **HTTPS**: Disabled for local development
- **CORS**: Enabled for API access

### Production Security
```bash
# Run security hardening
python3 security_hardening.py

# This creates:
# - Production settings with security headers
# - Custom security middleware
# - Secure environment configuration
# - Deployment scripts
```

---

## 🚀 Deployment Options

### Local Development
```bash
# Start development server
python manage.py runserver 0.0.0.0:8000

# Access from other devices on network
http://YOUR_IP:8000
```

### Production Deployment
```bash
# Run security hardening first
python3 security_hardening.py

# Deploy with the generated script
./deploy_secure.sh
```

### Docker Deployment (Optional)
```dockerfile
# Create Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements_secure.txt .
RUN pip install -r requirements_secure.txt

COPY . .
RUN python manage.py collectstatic --noinput
RUN python manage.py migrate

EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

---

## 🛠️ Maintenance Commands

### Daily Maintenance
```bash
# Update stock data
python manage.py fetch_stock_data

# Send email notifications
python manage.py send_notifications

# Backup database
python3 database_settings_local.py
```

### Weekly Maintenance
```bash
# Vacuum database (optimize)
python3 -c "from database_settings_local import vacuum_database; vacuum_database()"

# Clear old cache
python manage.py clearcache

# Update static files
python manage.py collectstatic --noinput
```

### System Monitoring
```bash
# Check system status
python3 test_database_setup.py

# Check database health
python3 -c "from database_settings_local import check_database_health; print(check_database_health())"

# View logs
tail -f logs/django.log

# Monitor database size
ls -lh stock_scanner.db
```

---

## 🐛 Troubleshooting

### Common Issues

#### 1. **Module Not Found Errors**
```bash
# Solution: Activate virtual environment
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Then install dependencies
pip install -r requirements_secure.txt
```

#### 2. **Database Migration Errors**
```bash
# Solution: Reset migrations
rm -rf */migrations/
python manage.py makemigrations
python manage.py migrate
```

#### 3. **Email Not Sending**
```bash
# Check Gmail app password
# Verify 2FA is enabled
# Test email configuration:
python3 -c "from emails.email_config import test_email_connection; print(test_email_connection())"
```

#### 4. **Stock Data Not Loading**
```bash
# Test yfinance connection
python3 -c "from stocks.yfinance_config import test_yfinance_connection; print(test_yfinance_connection())"

# Check internet connection
# Verify yfinance is installed: pip install yfinance
```

#### 5. **Permission Denied Errors**
```bash
# Make scripts executable
chmod +x setup_local.py
chmod +x database_settings_local.py
chmod +x test_database_setup.py
```

### Getting Help

#### Check Logs
```bash
# Django logs
tail -f logs/django.log

# Python errors
python manage.py check

# Database errors
python3 test_database_setup.py
```

#### Verify Configuration
```bash
# Test all components
python3 test_database_setup.py

# Check Django settings
python manage.py diffsettings

# Validate models
python manage.py validate
```

---

## 📚 Additional Resources

### Documentation
- **Django Documentation**: https://docs.djangoproject.com/
- **yfinance Documentation**: https://pypi.org/project/yfinance/
- **SQLite Documentation**: https://sqlite.org/docs.html

### API Testing Tools
- **Postman**: For testing API endpoints
- **curl**: Command-line API testing
- **Browser**: For web interface testing

### Development Tools
- **VS Code**: Recommended editor with Python extension
- **PyCharm**: Professional Python IDE
- **Git**: Version control system

---

## 🎯 What's Next?

### After Setup
1. **Add Stock Tickers**: Use Django admin to add stocks to monitor
2. **Configure Email Alerts**: Set up email subscriptions for different stock categories
3. **Customize Frontend**: Modify templates in `templates/` directory
4. **Add More Features**: Extend the API or add new stock analysis tools

### WordPress Integration
1. **Install WordPress**: Set up WordPress on your domain
2. **Configure API**: Update WordPress URLs in settings
3. **Deploy Theme**: Use the WordPress theme in `wordpress_deployment_package/`
4. **Test Integration**: Verify data flows from Django to WordPress

### Production Deployment
1. **Get Domain**: Register a domain name
2. **Get Hosting**: Choose a hosting provider (VPS recommended)
3. **Setup SSL**: Install SSL certificate for HTTPS
4. **Deploy**: Use the automated deployment script

---

## 🆘 Support

If you encounter issues:

1. **Check this guide**: Most common issues are covered above
2. **Run diagnostics**: Use `python3 test_database_setup.py`
3. **Check logs**: Look in `logs/` directory for error messages
4. **Verify configuration**: Ensure `.env` file is properly configured
5. **Test components**: Test database, email, and API individually

Remember: This is a local SQLite setup, so no complex database configuration is needed! 🎉