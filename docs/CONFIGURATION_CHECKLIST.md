# 🔧 Complete Configuration Checklist

## 📋 **Required Configuration Items**

### 🔑 **1. API Keys & External Services**

#### **Stripe Payment Processing**
```php
// wp-config.php (WordPress)
define('STRIPE_PUBLISHABLE_KEY', 'pk_live_51xxxxx'); // Get from stripe.com/dashboard
define('STRIPE_SECRET_KEY', 'sk_live_51xxxxx');
define('STRIPE_WEBHOOK_SECRET', 'whsec_xxxxx');

// For testing:
define('STRIPE_PUBLISHABLE_KEY', 'pk_test_51xxxxx');
define('STRIPE_SECRET_KEY', 'sk_test_51xxxxx');
```

#### **Stock Data APIs (Choose Primary + Backup)**
```python
# Django settings.py
STOCK_API_SETTINGS = {
    # Primary: Yahoo Finance (yfinance) - FREE
    'YFINANCE_ENABLED': True,
    
    # Backup APIs (Optional but recommended)
    'ALPHA_VANTAGE_API_KEY': 'YOUR_KEY',  # alphavantage.co - FREE tier available
    'FINNHUB_API_KEY': 'YOUR_KEY',        # finnhub.io - FREE tier available
    'IEX_CLOUD_API_KEY': 'YOUR_KEY',      # iexcloud.io - FREE tier available
    'POLYGON_API_KEY': 'YOUR_KEY',        # polygon.io - PAID
    'TWELVE_DATA_API_KEY': 'YOUR_KEY',    # twelvedata.com - FREE tier available
}
```

#### **Email Services**
```python
# Django settings.py - Choose one:

# Option 1: SMTP (Gmail, Outlook, etc.)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'  # or 'smtp-mail.outlook.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'  # Generate app password
DEFAULT_FROM_EMAIL = 'Stock Scanner <your-email@gmail.com>'

# Option 2: SendGrid
EMAIL_BACKEND = 'sendgrid_backend.SendgridBackend'
SENDGRID_API_KEY = 'SG.xxxxx'  # sendgrid.com

# Option 3: AWS SES
EMAIL_BACKEND = 'django_ses.SESBackend'
AWS_ACCESS_KEY_ID = 'AKIAXXXXX'
AWS_SECRET_ACCESS_KEY = 'xxxxx'
AWS_SES_REGION_NAME = 'us-east-1'
```

#### **News Scraping (Optional)**
```python
# Django settings.py
NEWS_API_SETTINGS = {
    'NEWS_API_KEY': 'YOUR_KEY',           # newsapi.org - FREE tier available
    'ALPHA_VANTAGE_NEWS_KEY': 'YOUR_KEY', # alphavantage.co news
    'POLYGON_NEWS_KEY': 'YOUR_KEY',       # polygon.io news
}
```

### 🌐 **2. Domain & Hosting Configuration**

#### **Domain Settings**
```python
# Django settings.py
ALLOWED_HOSTS = [
    'retailtradescan.net',
    'www.retailtradescan.net',
    'localhost',
    '127.0.0.1',
]

CORS_ALLOWED_ORIGINS = [
    "https://retailtradescan.net",
    "https://www.retailtradescan.net",
    "http://localhost:8000",  # Development
]

# WordPress URL for API integration
WORDPRESS_URL = 'https://retailtradescan.net'
```

#### **SSL Certificate**
- ✅ **Let's Encrypt** (Free) - Recommended
- ✅ **Cloudflare SSL** (Free)
- ✅ **Paid SSL Certificate**

#### **CDN & Performance**
```python
# Django settings.py (Optional but recommended)
CLOUDFLARE_API_TOKEN = 'YOUR_TOKEN'  # For cache purging
AWS_S3_ACCESS_KEY_ID = 'AKIAXXXXX'   # For static file hosting
AWS_S3_SECRET_ACCESS_KEY = 'xxxxx'
AWS_STORAGE_BUCKET_NAME = 'stock-scanner-static'
```

### 🗄️ **3. Database Configuration**

#### **Production Database**
```python
# Django settings.py
DATABASES = {
    'default': {
        # Option 1: PostgreSQL (Recommended)
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'stock_scanner_db',
        'USER': 'stock_scanner_user',
        'PASSWORD': 'SECURE_PASSWORD',
        'HOST': 'localhost',  # or your database server
        'PORT': '5432',
        
        # Option 2: MySQL
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'stock_scanner_db',
        'USER': 'stock_scanner_user',
        'PASSWORD': 'SECURE_PASSWORD',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

#### **Redis Cache (Recommended)**
```python
# Django settings.py
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# Redis connection for Celery (background tasks)
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
```

### 🔐 **4. Security Configuration**

#### **Django Security Settings**
```python
# Django settings.py
SECRET_KEY = 'GENERATE_SECURE_50_CHAR_KEY'  # Use django.core.management.utils.get_random_secret_key()

# Security settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# CORS security
CORS_ALLOW_CREDENTIALS = True
CORS_EXPOSE_HEADERS = ['Content-Range', 'X-Content-Range']
```

#### **WordPress Security**
```php
// wp-config.php
define('AUTH_KEY',         'GENERATE_UNIQUE_KEY');
define('SECURE_AUTH_KEY',  'GENERATE_UNIQUE_KEY');
define('LOGGED_IN_KEY',    'GENERATE_UNIQUE_KEY');
define('NONCE_KEY',        'GENERATE_UNIQUE_KEY');
define('AUTH_SALT',        'GENERATE_UNIQUE_KEY');
define('SECURE_AUTH_SALT', 'GENERATE_UNIQUE_KEY');
define('LOGGED_IN_SALT',   'GENERATE_UNIQUE_KEY');
define('NONCE_SALT',       'GENERATE_UNIQUE_KEY');

// Generate at: https://api.wordpress.org/secret-key/1.1/salt/
```

### 📧 **5. Email Configuration**

#### **SMTP Settings (Gmail Example)**
```python
# Django settings.py
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-business-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-16-digit-app-password'  # Not your regular password!
DEFAULT_FROM_EMAIL = 'Stock Scanner <your-business-email@gmail.com>'

# Email settings
ADMINS = [('Your Name', 'admin@retailtradescan.net')]
SERVER_EMAIL = 'server@retailtradescan.net'
```

#### **Gmail App Password Setup**
1. Enable 2-Factor Authentication
2. Google Account → Security → 2-Step Verification → App Passwords
3. Generate password for "Mail"
4. Use the 16-character password (not your regular password)

### 🏃‍♂️ **6. Background Tasks (Celery)**

#### **Celery Configuration**
```python
# Django settings.py
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'

# Celery Beat Schedule (for periodic tasks)
CELERY_BEAT_SCHEDULE = {
    'fetch-stock-data': {
        'task': 'stocks.tasks.fetch_all_stock_data',
        'schedule': 300.0,  # Every 5 minutes
    },
    'send-email-alerts': {
        'task': 'emails.tasks.send_scheduled_alerts',
        'schedule': 900.0,  # Every 15 minutes
    },
}
```

### 🌍 **7. Environment Variables (.env file)**

```bash
# Create .env file in Django root
DEBUG=False
SECRET_KEY=your-django-secret-key
DATABASE_URL=postgresql://user:pass@localhost/dbname

# Stripe
STRIPE_PUBLISHABLE_KEY=pk_live_xxxxx
STRIPE_SECRET_KEY=sk_live_xxxxx
STRIPE_WEBHOOK_SECRET=whsec_xxxxx

# Email
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Stock APIs
ALPHA_VANTAGE_API_KEY=your-key
FINNHUB_API_KEY=your-key
IEX_CLOUD_API_KEY=your-key

# WordPress
WORDPRESS_URL=https://retailtradescan.net
WORDPRESS_API_KEY=your-wordpress-api-key

# Redis
REDIS_URL=redis://localhost:6379/0

# CDN/Storage (Optional)
AWS_ACCESS_KEY_ID=AKIAXXXXX
AWS_SECRET_ACCESS_KEY=xxxxx
AWS_STORAGE_BUCKET_NAME=stock-scanner-static
```

### 📱 **8. Social Media & Analytics**

#### **Google Analytics**
```html
<!-- Add to WordPress theme header.php -->
<script async src="https://www.googletagmanager.com/gtag/js?id=GA_MEASUREMENT_ID"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'GA_MEASUREMENT_ID');
</script>
```

#### **Social Media Integration**
```python
# Django settings.py (Optional)
SOCIAL_MEDIA_SETTINGS = {
    'TWITTER_API_KEY': 'YOUR_KEY',
    'FACEBOOK_APP_ID': 'YOUR_APP_ID',
    'LINKEDIN_CLIENT_ID': 'YOUR_CLIENT_ID',
}
```

### 🔧 **9. Server Configuration**

#### **Web Server (Nginx Example)**
```nginx
# /etc/nginx/sites-available/stock-scanner
server {
    listen 80;
    server_name retailtradescan.net www.retailtradescan.net;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name retailtradescan.net www.retailtradescan.net;
    
    # SSL configuration
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/private.key;
    
    # Django static files
    location /static/ {
        alias /path/to/stock-scanner/static/;
    }
    
    # Django application
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    # WordPress
    location / {
        try_files $uri $uri/ /index.php?$args;
    }
}
```

### 📊 **10. Monitoring & Logging**

#### **Log Configuration**
```python
# Django settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '/var/log/stock-scanner/django.log',
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
        },
    },
    'root': {
        'handlers': ['file'],
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'mail_admins'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

## ✅ **Quick Setup Commands**

### **Generate Django Secret Key**
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### **Create App Passwords**
- **Gmail**: Google Account → Security → App Passwords
- **Outlook**: Account Settings → Security → Additional Security → App Passwords

### **Test Configuration**
```bash
# Test Django setup
python manage.py check --deploy

# Test email configuration
python manage.py shell -c "from django.core.mail import send_mail; send_mail('Test', 'Testing email', 'from@example.com', ['to@example.com'])"

# Test Stripe connection
wp stock-scanner test-stripe

# Test API endpoints
curl https://retailtradescan.net/api/stocks/
```

## 🎯 **Priority Order for Setup**

1. **🔑 Domain & SSL** - Get your site accessible
2. **🗄️ Database** - Set up production database
3. **💳 Stripe Keys** - Enable payments immediately
4. **📧 Email SMTP** - For user notifications
5. **📊 Stock APIs** - For data fetching
6. **🔒 Security Settings** - Harden the system
7. **📈 Analytics** - Track user behavior
8. **⚡ Performance** - Redis, CDN, optimization

## 🚨 **Security Checklist**

- ✅ Strong passwords for all accounts
- ✅ 2FA enabled on all services
- ✅ Regular security updates
- ✅ SSL certificate installed
- ✅ Database access restricted
- ✅ API keys in environment variables (not code)
- ✅ Regular backups scheduled
- ✅ Error monitoring set up

**Your stock scanner will be production-ready once all these items are configured!** 🚀