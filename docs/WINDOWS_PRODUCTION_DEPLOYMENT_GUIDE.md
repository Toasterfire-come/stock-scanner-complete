# 🚀 Complete Windows Production Deployment Guide

## 📋 Table of Contents
1. [System Requirements & Prerequisites](#system-requirements--prerequisites)
2. [Step 1: Windows Environment Setup](#step-1-windows-environment-setup)
3. [Step 2: Repository Setup & Dependencies](#step-2-repository-setup--dependencies)
4. [Step 3: Database Configuration](#step-3-database-configuration)
5. [Step 4: Django Production Setup](#step-4-django-production-setup)
6. [Step 5: WordPress Integration](#step-5-wordpress-integration)
7. [Step 6: SSL & Domain Configuration](#step-6-ssl--domain-configuration)
8. [Step 7: Payment System Setup](#step-7-payment-system-setup)
9. [Step 8: Production Server Deployment](#step-8-production-server-deployment)
10. [Step 9: Monitoring & Maintenance](#step-9-monitoring--maintenance)
11. [Troubleshooting](#troubleshooting)

---

## System Requirements & Prerequisites

### 🖥️ **Windows System Requirements**
- **OS**: Windows 10/11 Pro or Windows Server 2019/2022
- **RAM**: Minimum 8GB (16GB recommended for production)
- **Storage**: 50GB free space minimum
- **CPU**: 4 cores minimum (8 cores recommended)
- **Network**: Static IP address for production server

### 🔧 **Required Software Checklist**
- [ ] Python 3.9+ (3.11 recommended)
- [ ] Git for Windows
- [ ] Visual Studio Code or PyCharm
- [ ] PostgreSQL 14+
- [ ] Redis Server
- [ ] Node.js 18+ (for build tools)
- [ ] IIS or Apache/Nginx for Windows
- [ ] SSL Certificate (Let's Encrypt or commercial)

---

## Step 1: Windows Environment Setup

### 1.1 Install Python 3.11

1. **Download Python**: Go to https://www.python.org/downloads/windows/
2. **Download Python 3.11.x** (latest stable version)
3. **Run installer as Administrator**
4. **CRITICAL**: Check "Add Python to PATH" ✅
5. **CRITICAL**: Check "Install for all users" ✅
6. **Click "Customize installation"**
7. **Optional Features**: Check all boxes ✅
8. **Advanced Options**: 
   - ✅ Install for all users
   - ✅ Add Python to environment variables
   - ✅ Precompile standard library
   - ✅ Download debugging symbols

```cmd
# Verify installation
python --version
pip --version
```

### 1.2 Install Git for Windows

1. **Download**: https://git-scm.com/download/win
2. **Run installer as Administrator**
3. **Important Settings**:
   - Editor: Use Visual Studio Code (recommended)
   - PATH environment: Git from command line and 3rd-party software
   - HTTPS transport backend: Use the OpenSSL library
   - Line ending conversions: Checkout Windows-style, commit Unix-style
   - Terminal emulator: Use MinTTY
   - Git Credential Manager: Enable

```cmd
# Verify installation
git --version
```

### 1.3 Install PostgreSQL

1. **Download**: https://www.postgresql.org/download/windows/
2. **Run installer as Administrator**
3. **Installation Settings**:
   - Components: PostgreSQL Server, pgAdmin 4, Stack Builder
   - Data Directory: `C:\Program Files\PostgreSQL\14\data`
   - **Password**: Set a strong password (remember this!)
   - Port: 5432 (default)
   - Locale: Default locale

```cmd
# Verify installation (add to PATH if needed)
psql --version
```

### 1.4 Install Redis for Windows

1. **Download**: https://github.com/microsoftarchive/redis/releases
2. **Download MSI installer** (Redis-x64-x.x.xxx.msi)
3. **Run as Administrator**
4. **Installation**:
   - Install location: `C:\Program Files\Redis`
   - Port: 6379 (default)
   - Max memory: 100MB (adjust based on your system)
   - ✅ Add Redis to PATH

```cmd
# Verify installation
redis-cli ping
# Should return: PONG
```

### 1.5 Install Node.js

1. **Download**: https://nodejs.org/en/download/
2. **Download LTS version** (18.x.x)
3. **Run installer as Administrator**
4. **Installation Settings**:
   - ✅ Add to PATH
   - ✅ Install npm package manager
   - ✅ Install tools for native modules

```cmd
# Verify installation
node --version
npm --version
```

---

## Step 2: Repository Setup & Dependencies

### 2.1 Clone Repository

```cmd
# Open Command Prompt as Administrator
cd C:\
mkdir WebApps
cd WebApps

# Clone the repository
git clone https://github.com/Toasterfire-come/stock-scanner-complete.git
cd stock-scanner-complete

# Verify structure
dir
```

### 2.2 Create Python Virtual Environment

```cmd
# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate

# Verify activation (should show (venv) in prompt)
where python
# Should show: C:\WebApps\stock-scanner-complete\venv\Scripts\python.exe
```

### 2.3 Install Python Dependencies

```cmd
# Ensure you're in virtual environment
venv\Scripts\activate

# Upgrade pip first
python -m pip install --upgrade pip

# Install main requirements
pip install -r requirements.txt

# Install additional production packages
pip install gunicorn whitenoise psycopg2-binary redis celery

# Verify critical packages
python -c "import django; print(f'Django: {django.VERSION}')"
python -c "import yfinance; print('yfinance: OK')"
python -c "import psycopg2; print('PostgreSQL: OK')"
python -c "import redis; print('Redis: OK')"
```

### 2.4 Run Windows Compatibility Fix

```cmd
# Run the Windows compatibility script
python scripts/setup/windows_fix_install.py

# This fixes:
# - Unicode encoding issues
# - Path separators
# - Windows service compatibility
# - Registry settings
```

---

## Step 3: Database Configuration

### 3.1 Create Production Database

```cmd
# Open PostgreSQL command line (run as Administrator)
# Password is what you set during PostgreSQL installation
psql -U postgres

# Create database and user
CREATE DATABASE stockscanner_prod;
CREATE USER stockscanner WITH PASSWORD 'your_secure_password_here';
GRANT ALL PRIVILEGES ON DATABASE stockscanner_prod TO stockscanner;
ALTER USER stockscanner CREATEDB;
\q
```

### 3.2 Configure Database Settings

Create `.env` file in project root:

```cmd
# Create environment file
notepad .env
```

Add this content to `.env`:

```env
# Production Environment Variables
DEBUG=False
SECRET_KEY=your-super-secret-key-here-make-it-long-and-random
ALLOWED_HOSTS=localhost,127.0.0.1,your-domain.com,www.your-domain.com

# Database Configuration
DATABASE_URL=postgresql://stockscanner:your_secure_password_here@localhost:5432/stockscanner_prod
DB_NAME=stockscanner_prod
DB_USER=stockscanner
DB_PASSWORD=your_secure_password_here
DB_HOST=localhost
DB_PORT=5432

# Redis Configuration
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Email Configuration (Production)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.your-email-provider.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@domain.com
EMAIL_HOST_PASSWORD=your-email-password

# Payment Configuration
STRIPE_PUBLIC_KEY=pk_live_your_stripe_public_key
STRIPE_SECRET_KEY=sk_live_your_stripe_secret_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret

# Yahoo Finance API Configuration
STOCK_API_RATE_LIMIT=1.0
YFINANCE_THREADS=5

# Security Settings
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True
SECURE_CONTENT_TYPE_NOSNIFF=True
SECURE_BROWSER_XSS_FILTER=True
X_FRAME_OPTIONS=DENY

# Static Files (Production)
STATIC_URL=/static/
STATIC_ROOT=C:/WebApps/stock-scanner-complete/staticfiles/
MEDIA_URL=/media/
MEDIA_ROOT=C:/WebApps/stock-scanner-complete/media/
```

### 3.3 Run Database Migrations

```cmd
# Ensure virtual environment is active
venv\Scripts\activate

# Set environment variables temporarily
set DJANGO_SETTINGS_MODULE=stockscanner_django.settings

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser account
python manage.py createsuperuser
# Enter your admin username, email, and password

# Collect static files
python manage.py collectstatic --noinput
```

---

## Step 4: Django Production Setup

### 4.1 Test Django Application

```cmd
# Test the application
python scripts/testing/test_django_startup.py

# Run development server for testing
python manage.py runserver 127.0.0.1:8000

# Open browser and test:
# http://127.0.0.1:8000 - Main site
# http://127.0.0.1:8000/admin - Admin panel
# http://127.0.0.1:8000/api/stocks/ - API endpoint
```

### 4.2 Configure Production Settings

Edit `stockscanner_django/settings.py` for production:

```python
# Add to settings.py
import os
from decouple import config

# Production security settings
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost').split(',')

# Database configuration
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
    }
}

# Static files configuration
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files configuration
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Add WhiteNoise middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Add this line
    # ... other middleware
]
```

### 4.3 Setup Celery for Background Tasks

Create `celery_worker.bat`:

```cmd
notepad celery_worker.bat
```

Add this content:

```batch
@echo off
cd /d C:\WebApps\stock-scanner-complete
call venv\Scripts\activate
set DJANGO_SETTINGS_MODULE=stockscanner_django.settings
celery -A stockscanner_django worker --loglevel=info --pool=solo
```

Create `celery_beat.bat`:

```cmd
notepad celery_beat.bat
```

Add this content:

```batch
@echo off
cd /d C:\WebApps\stock-scanner-complete
call venv\Scripts\activate
set DJANGO_SETTINGS_MODULE=stockscanner_django.settings
celery -A stockscanner_django beat --loglevel=info
```

---

## Step 5: WordPress Integration

### 5.1 Install XAMPP for WordPress

1. **Download XAMPP**: https://www.apachefriends.org/download.html
2. **Install XAMPP** to `C:\xampp`
3. **Start Services**:
   - ✅ Apache
   - ✅ MySQL
   - ✅ FileZilla (optional)

### 5.2 Install WordPress

1. **Download WordPress**: https://wordpress.org/download/
2. **Extract to**: `C:\xampp\htdocs\wordpress`
3. **Create MySQL Database**:
   - Open http://localhost/phpmyadmin
   - Create database: `wordpress_stockscanner`
   - User: `wp_user`
   - Password: `secure_wp_password`

### 5.3 Configure WordPress

1. **Copy** `wp-config-sample.php` to `wp-config.php`
2. **Edit** `wp-config.php`:

```php
// Database settings
define('DB_NAME', 'wordpress_stockscanner');
define('DB_USER', 'wp_user');
define('DB_PASSWORD', 'secure_wp_password');
define('DB_HOST', 'localhost');

// Django integration settings
define('DJANGO_API_URL', 'http://localhost:8000/api/');
define('DJANGO_API_KEY', 'your-api-key-here');

// Security keys (generate at https://api.wordpress.org/secret-key/1.1/salt/)
// Add the generated keys here
```

### 5.4 Install Stock Scanner WordPress Plugin

```cmd
# Copy plugin files
xcopy /E /I wordpress_plugin C:\xampp\htdocs\wordpress\wp-content\plugins\stock-scanner

# Copy theme files
xcopy /E /I wordpress_theme C:\xampp\htdocs\wordpress\wp-content\themes\stockscanner-theme
```

---

## Step 6: SSL & Domain Configuration

### 6.1 Install IIS (Internet Information Services)

1. **Open**: Control Panel → Programs → Turn Windows features on or off
2. **Enable**: Internet Information Services
3. **Enable sub-features**:
   - ✅ Web Management Tools
   - ✅ World Wide Web Services
   - ✅ Application Development Features
   - ✅ CGI
   - ✅ ISAPI Extensions
   - ✅ ISAPI Filters

### 6.2 Configure IIS for Django

1. **Open IIS Manager** (Run as Administrator)
2. **Add Website**:
   - Site name: `StockScannerDjango`
   - Physical path: `C:\WebApps\stock-scanner-complete`
   - Port: 8000
   - Host name: `api.retailtradescanner.com`

3. **Install Python CGI**:
   - Download: https://www.iis.net/downloads/microsoft/wfastcgi
   - Install WFastCGI
   - Run: `wfastcgi-enable`

### 6.3 SSL Certificate Setup

#### Option A: Let's Encrypt (Free)

1. **Install Certbot for Windows**:
   - Download: https://certbot.eff.org/instructions?ws=iis&os=windows
   - Install and run as Administrator

```cmd
# Generate SSL certificate
certbot --iis -d retailtradescanner.com -d www.retailtradescanner.com
```

#### Option B: Commercial SSL Certificate

1. **Purchase SSL certificate** from provider (GoDaddy, Namecheap, etc.)
2. **Generate CSR** in IIS Manager
3. **Install certificate** in IIS Manager
4. **Bind certificate** to your website

---

## Step 7: Payment System Setup

### 7.1 Stripe Configuration

1. **Create Stripe Account**: https://stripe.com
2. **Get API Keys**:
   - Dashboard → Developers → API keys
   - Copy Publishable key and Secret key
   - Add to `.env` file

3. **Configure Webhooks**:
   - Dashboard → Developers → Webhooks
   - Add endpoint: `https://retailtradescanner.com/stripe/webhook/`
   - Select events: `payment_intent.succeeded`, `customer.subscription.created`

### 7.2 Tax Configuration

```python
# Add to Django settings
STRIPE_TAX_RATE_ID = 'txr_your_tax_rate_id'  # Create in Stripe Dashboard
AUTOMATIC_TAX = True
TAX_CALCULATION_SERVICE = 'stripe'
```

---

## Step 8: Production Server Deployment

### 8.1 Windows Service Setup

Create `django_service.py`:

```python
import sys
import os
import servicemanager
import socket
import win32serviceutil
import win32service
import win32event

class DjangoService(win32serviceutil.ServiceFramework):
    _svc_name_ = "StockScannerDjango"
    _svc_display_name_ = "Stock Scanner Django Service"
    _svc_description_ = "Django application for Stock Scanner platform"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        socket.setdefaulttimeout(60)

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                              servicemanager.PYS_SERVICE_STARTED,
                              (self._svc_name_, ''))
        self.main()

    def main(self):
        os.chdir('C:\\WebApps\\stock-scanner-complete')
        os.system('venv\\Scripts\\activate && python manage.py runserver 0.0.0.0:8000')

if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(DjangoService)
```

Install and start service:

```cmd
# Install service
python django_service.py install

# Start service
python django_service.py start

# Check service status
python django_service.py status
```

### 8.2 Configure Firewall

```cmd
# Open Windows Firewall
# Add inbound rules for:
# - Port 80 (HTTP)
# - Port 443 (HTTPS)
# - Port 8000 (Django API)
# - Port 5432 (PostgreSQL) - if external access needed

# PowerShell commands:
New-NetFirewallRule -DisplayName "Django API" -Direction Inbound -Protocol TCP -LocalPort 8000 -Action Allow
New-NetFirewallRule -DisplayName "HTTP" -Direction Inbound -Protocol TCP -LocalPort 80 -Action Allow
New-NetFirewallRule -DisplayName "HTTPS" -Direction Inbound -Protocol TCP -LocalPort 443 -Action Allow
```

### 8.3 Domain Configuration

1. **Update DNS Records**:
   - A Record: `retailtradescanner.com` → Your Server IP
   - A Record: `www.retailtradescanner.com` → Your Server IP
   - A Record: `api.retailtradescanner.com` → Your Server IP

2. **Update hosts file** for testing:
```cmd
# Edit C:\Windows\System32\drivers\etc\hosts
127.0.0.1 retailtradescanner.com
127.0.0.1 www.retailtradescanner.com
127.0.0.1 api.retailtradescanner.com
```

---

## Step 9: Monitoring & Maintenance

### 9.1 Setup Logging

Create `logs` directory and configure logging:

```cmd
mkdir logs
mkdir logs\django
mkdir logs\celery
mkdir logs\nginx
```

Add to Django settings:

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'logs/django/django.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

### 9.2 Backup Scripts

Create `backup.bat`:

```batch
@echo off
set BACKUP_DIR=C:\Backups\StockScanner\%date:~-4,4%-%date:~-10,2%-%date:~-7,2%
mkdir "%BACKUP_DIR%"

REM Backup database
pg_dump -U stockscanner stockscanner_prod > "%BACKUP_DIR%\database.sql"

REM Backup media files
xcopy /E /I C:\WebApps\stock-scanner-complete\media "%BACKUP_DIR%\media"

REM Backup configuration
copy C:\WebApps\stock-scanner-complete\.env "%BACKUP_DIR%\.env"

echo Backup completed: %BACKUP_DIR%
```

### 9.3 Performance Monitoring

Install performance monitoring:

```cmd
pip install django-debug-toolbar psutil
```

Add monitoring endpoints in Django:

```python
# Add to urls.py
from django.urls import path, include
from . import monitoring_views

urlpatterns = [
    # ... existing urls
    path('monitor/', monitoring_views.system_status, name='system_status'),
    path('monitor/health/', monitoring_views.health_check, name='health_check'),
]
```

---

## Step 10: Final Production Checklist

### ✅ **Pre-Launch Checklist**

- [ ] Python 3.11+ installed and configured
- [ ] PostgreSQL database created and migrated
- [ ] Redis server running and accessible
- [ ] Django application starts without errors
- [ ] Celery workers and beat scheduler running
- [ ] WordPress installed and plugin activated
- [ ] SSL certificate installed and configured
- [ ] Stripe payment system configured
- [ ] Domain DNS records pointing to server
- [ ] Firewall rules configured
- [ ] Backup system configured
- [ ] Monitoring and logging active
- [ ] All tests passing

### 🚀 **Launch Commands**

```cmd
# Start all services
net start Redis
net start postgresql-x64-14
python django_service.py start

# Start Celery workers
start celery_worker.bat
start celery_beat.bat

# Verify everything is running
python scripts/testing/test_production_system.py
```

### 🔍 **Post-Launch Verification**

1. **Test Main Website**: https://retailtradescanner.com
2. **Test API Endpoints**: https://api.retailtradescanner.com/api/stocks/
3. **Test Admin Panel**: https://api.retailtradescanner.com/admin/
4. **Test Payment Flow**: Complete a test subscription
5. **Test Stock Data**: Verify real-time stock prices
6. **Test WordPress Integration**: Check all 24 pages

---

## Troubleshooting

### 🔧 **Common Windows Issues**

#### Python Path Issues
```cmd
# Fix Python PATH
setx PATH "%PATH%;C:\Python311;C:\Python311\Scripts"
```

#### PostgreSQL Connection Issues
```cmd
# Check PostgreSQL service
net start postgresql-x64-14

# Test connection
psql -U postgres -h localhost -p 5432
```

#### Redis Connection Issues
```cmd
# Check Redis service
net start Redis

# Test connection
redis-cli ping
```

#### Permission Issues
```cmd
# Run Command Prompt as Administrator
# Grant permissions to application folder
icacls "C:\WebApps\stock-scanner-complete" /grant Everyone:F /T
```

#### IIS Configuration Issues
```cmd
# Reset IIS
iisreset

# Check application pool
# IIS Manager → Application Pools → DefaultAppPool → Advanced Settings
# Process Model → Identity: ApplicationPoolIdentity
```

### 📞 **Support & Resources**

- **Django Documentation**: https://docs.djangoproject.com/
- **PostgreSQL Windows Guide**: https://www.postgresql.org/docs/current/tutorial-install.html
- **Redis Windows Installation**: https://redis.io/docs/getting-started/installation/install-redis-on-windows/
- **IIS Django Deployment**: https://docs.microsoft.com/en-us/iis/
- **Stripe Documentation**: https://stripe.com/docs

### 🔄 **Maintenance Schedule**

- **Daily**: Check application logs and system status
- **Weekly**: Run database backups and system updates
- **Monthly**: Review performance metrics and optimize
- **Quarterly**: Update dependencies and security patches

---

## 🎉 Success!

Your **Complete Stock Scanner Production Platform** is now live on Windows! 

- **Main Website**: https://retailtradescanner.com
- **API**: https://api.retailtradescanner.com
- **Admin**: https://api.retailtradescanner.com/admin

The platform includes:
- ✅ Real-time stock data with optimized rate limiting
- ✅ 4-tier membership system with Stripe payments
- ✅ Complete WordPress integration with 24 pages
- ✅ Professional admin dashboard
- ✅ Automated email notifications
- ✅ SSL security and production optimization
- ✅ Full Windows service integration

**Ready for business at retailtradescanner.com!** 🚀