# WordPress Integration & Production Setup Guide

## Overview
This guide covers the complete setup process for integrating the Stock Scanner Django backend with WordPress and deploying to production.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [WordPress Setup](#wordpress-setup)
3. [Django Production Configuration](#django-production-configuration)
4. [Database Setup](#database-setup)
5. [WordPress Theme Installation](#wordpress-theme-installation)
6. [WordPress Plugin Installation](#wordpress-plugin-installation)
7. [API Integration Configuration](#api-integration-configuration)
8. [Production Deployment](#production-deployment)
9. [SSL & Security](#ssl--security)
10. [Monitoring & Maintenance](#monitoring--maintenance)
11. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Server Requirements
- **VPS/Server**: Ubuntu 20.04+ or CentOS 8+
- **RAM**: Minimum 2GB (4GB+ recommended)
- **Storage**: 20GB+ SSD
- **PHP**: 8.0+
- **Python**: 3.9+
- **MySQL**: 8.0+
- **Web Server**: Nginx + Apache (or just Nginx)

### Domain & DNS
- Domain name pointing to your server
- SSL certificate (Let's Encrypt recommended)

---

## WordPress Setup

### 1. Install WordPress
```bash
# Download WordPress
cd /var/www/html
sudo wget https://wordpress.org/latest.tar.gz
sudo tar xzf latest.tar.gz
sudo mv wordpress/* .
sudo rm -rf wordpress latest.tar.gz

# Set permissions
sudo chown -R www-data:www-data /var/www/html
sudo chmod -R 755 /var/www/html
```

### 2. WordPress Database Setup
```sql
-- Create WordPress database
CREATE DATABASE wordpress_stockscanner CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'wp_user'@'localhost' IDENTIFIED BY 'your_secure_password';
GRANT ALL PRIVILEGES ON wordpress_stockscanner.* TO 'wp_user'@'localhost';
FLUSH PRIVILEGES;
```

### 3. WordPress Configuration
Create `wp-config.php`:
```php
<?php
// Database settings
define('DB_NAME', 'wordpress_stockscanner');
define('DB_USER', 'wp_user');
define('DB_PASSWORD', 'your_secure_password');
define('DB_HOST', 'localhost');
define('DB_CHARSET', 'utf8mb4');
define('DB_COLLATE', '');

// Security keys (generate at https://api.wordpress.org/secret-key/1.1/salt/)
define('AUTH_KEY',         'your-unique-key');
define('SECURE_AUTH_KEY',  'your-unique-key');
define('LOGGED_IN_KEY',    'your-unique-key');
define('NONCE_KEY',        'your-unique-key');
define('AUTH_SALT',        'your-unique-key');
define('SECURE_AUTH_SALT', 'your-unique-key');
define('LOGGED_IN_SALT',   'your-unique-key');
define('NONCE_SALT',       'your-unique-key');

// WordPress URLs
define('WP_HOME', 'https://yourdomain.com');
define('WP_SITEURL', 'https://yourdomain.com');

// Django API Integration
define('DJANGO_API_URL', 'https://api.yourdomain.com');
define('DJANGO_API_KEY', 'your-django-api-key');

$table_prefix = 'wp_';
define('WP_DEBUG', false);

if (!defined('ABSPATH')) {
    define('ABSPATH', __DIR__ . '/');
}

require_once ABSPATH . 'wp-settings.php';
?>
```

---

## Django Production Configuration

### 1. Production Settings
Create `stockscanner_django/settings_production.py`:
```python
from .settings import *
import os

# Production settings
DEBUG = False
ALLOWED_HOSTS = ['yourdomain.com', 'api.yourdomain.com', 'www.yourdomain.com']

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'stockscanner_production',
        'USER': 'django_user',
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}

# Security
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = '/var/www/stockscanner/static/'
MEDIA_URL = '/media/'
MEDIA_ROOT = '/var/www/stockscanner/media/'

# CORS for WordPress integration
CORS_ALLOWED_ORIGINS = [
    "https://yourdomain.com",
    "https://www.yourdomain.com",
]

# API Rate limiting
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/day',
        'user': '1000/day'
    }
}

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '/var/log/stockscanner/django.log',
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

### 2. Environment Variables
Create `/etc/environment` or use systemd environment file:
```bash
DJANGO_SECRET_KEY=your-super-secret-key
DB_PASSWORD=your-database-password
DJANGO_SETTINGS_MODULE=stockscanner_django.settings_production
```

---

## Database Setup

### 1. Production Database
```sql
-- Create production database
CREATE DATABASE stockscanner_production CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'django_user'@'localhost' IDENTIFIED BY 'your_secure_password';
GRANT ALL PRIVILEGES ON stockscanner_production.* TO 'django_user'@'localhost';
FLUSH PRIVILEGES;
```

### 2. Run Migrations
```bash
cd /var/www/stockscanner
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

### 3. Load Initial Data
```bash
# Load NASDAQ data
python manage.py load_nasdaq_only

# Start background scheduler
python manage.py runserver 0.0.0.0:8000
```

---

## WordPress Theme Installation

### 1. Upload Theme
```bash
# Copy theme to WordPress
sudo cp -r wordpress_theme/stock-scanner-theme /var/www/html/wp-content/themes/
sudo chown -R www-data:www-data /var/www/html/wp-content/themes/stock-scanner-theme
```

### 2. Activate Theme
1. Login to WordPress admin (`https://yourdomain.com/wp-admin`)
2. Go to **Appearance > Themes**
3. Activate "Stock Scanner Pro Theme"

### 3. Configure Theme Settings
Add to your theme's `functions.php`:
```php
// Django API Integration
function get_django_api_data($endpoint) {
    $api_url = DJANGO_API_URL . '/api/' . $endpoint;
    $response = wp_remote_get($api_url, array(
        'headers' => array(
            'Authorization' => 'Bearer ' . DJANGO_API_KEY
        ),
        'timeout' => 30
    ));
    
    if (is_wp_error($response)) {
        return false;
    }
    
    return json_decode(wp_remote_retrieve_body($response), true);
}
```

---

## WordPress Plugin Installation

### 1. Required Plugins
Install these essential plugins:
- **Paid Memberships Pro** (for user subscriptions)
- **WP Crontrol** (for scheduled tasks)
- **WP Security Audit Log** (for security monitoring)
- **UpdraftPlus** (for backups)

### 2. Custom Stock Scanner Plugin
```bash
# Copy plugin to WordPress
sudo cp -r wordpress_plugin/stock-scanner-integration /var/www/html/wp-content/plugins/
sudo chown -R www-data:www-data /var/www/html/wp-content/plugins/stock-scanner-integration
```

Activate the plugin in WordPress admin.

---

## API Integration Configuration

### 1. Django API Endpoints
Ensure these endpoints are accessible:
- `/api/wordpress/stocks/` - Stock data for WordPress
- `/api/wordpress/news/` - News data for WordPress
- `/api/stocks/search/` - Stock search functionality
- `/api/admin/status/` - System status

### 2. WordPress API Calls
Create WordPress shortcodes for displaying data:
```php
// Stock data shortcode
function stock_scanner_stocks_shortcode($atts) {
    $stocks = get_django_api_data('wordpress/stocks');
    if (!$stocks) return 'Unable to load stock data.';
    
    ob_start();
    include get_template_directory() . '/templates/stocks-display.php';
    return ob_get_clean();
}
add_shortcode('stock_scanner_stocks', 'stock_scanner_stocks_shortcode');
```

---

## Production Deployment

### 1. Nginx Configuration
Create `/etc/nginx/sites-available/stockscanner`:
```nginx
# WordPress site
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;
    
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    
    root /var/www/html;
    index index.php index.html;
    
    location / {
        try_files $uri $uri/ /index.php?$args;
    }
    
    location ~ \.php$ {
        fastcgi_pass unix:/var/run/php/php8.0-fpm.sock;
        fastcgi_index index.php;
        fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
        include fastcgi_params;
    }
}

# Django API
server {
    listen 443 ssl http2;
    server_name api.yourdomain.com;
    
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /static/ {
        alias /var/www/stockscanner/static/;
        expires 30d;
    }
}
```

### 2. Systemd Service for Django
Create `/etc/systemd/system/stockscanner.service`:
```ini
[Unit]
Description=Stock Scanner Django App
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/stockscanner
Environment=DJANGO_SETTINGS_MODULE=stockscanner_django.settings_production
ExecStart=/var/www/stockscanner/venv/bin/python manage.py runserver 127.0.0.1:8000
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable stockscanner
sudo systemctl start stockscanner
sudo systemctl enable nginx
sudo systemctl restart nginx
```

### 3. SSL Certificate
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com -d api.yourdomain.com
```

---

## SSL & Security

### 1. WordPress Security
Add to `wp-config.php`:
```php
// Security headers
define('DISALLOW_FILE_EDIT', true);
define('FORCE_SSL_ADMIN', true);
define('WP_AUTO_UPDATE_CORE', true);
```

### 2. Django Security
Ensure these settings in production:
```python
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
```

### 3. Firewall Setup
```bash
# UFW firewall
sudo ufw enable
sudo ufw allow 22
sudo ufw allow 80
sudo ufw allow 443
```

---

## Monitoring & Maintenance

### 1. Log Monitoring
```bash
# Create log directories
sudo mkdir -p /var/log/stockscanner
sudo chown www-data:www-data /var/log/stockscanner

# Monitor logs
tail -f /var/log/stockscanner/django.log
tail -f /var/log/nginx/access.log
```

### 2. Backup Strategy
```bash
#!/bin/bash
# Daily backup script
DATE=$(date +%Y%m%d_%H%M%S)

# Database backups
mysqldump -u root -p stockscanner_production > /backups/django_$DATE.sql
mysqldump -u root -p wordpress_stockscanner > /backups/wordpress_$DATE.sql

# File backups
tar -czf /backups/files_$DATE.tar.gz /var/www/stockscanner /var/www/html

# Keep only last 7 days
find /backups -name "*.sql" -mtime +7 -delete
find /backups -name "*.tar.gz" -mtime +7 -delete
```

### 3. Health Checks
Create monitoring script:
```bash
#!/bin/bash
# Check if services are running
systemctl is-active --quiet stockscanner || systemctl restart stockscanner
systemctl is-active --quiet nginx || systemctl restart nginx
systemctl is-active --quiet mysql || systemctl restart mysql

# Check API endpoint
curl -f https://api.yourdomain.com/api/admin/status/ || echo "API DOWN" | mail admin@yourdomain.com
```

---

## Troubleshooting

### Common Issues

1. **Django not starting**
   ```bash
   sudo journalctl -u stockscanner -f
   ```

2. **WordPress can't connect to API**
   - Check CORS settings in Django
   - Verify API endpoints are accessible
   - Check SSL certificates

3. **Database connection issues**
   ```bash
   sudo mysql -u root -p
   SHOW PROCESSLIST;
   ```

4. **Permission issues**
   ```bash
   sudo chown -R www-data:www-data /var/www/
   sudo chmod -R 755 /var/www/
   ```

### Performance Optimization

1. **Enable caching**
   - Install Redis for Django caching
   - Use WordPress caching plugins

2. **Database optimization**
   ```sql
   OPTIMIZE TABLE stocks_stock;
   OPTIMIZE TABLE stocks_stockprice;
   ```

3. **Static file optimization**
   - Enable Nginx gzip compression
   - Use CDN for static assets

---

## Quick Start Checklist

- [ ] Server setup with required software
- [ ] Domain and DNS configuration
- [ ] SSL certificate installation
- [ ] WordPress installation and configuration
- [ ] Django production setup
- [ ] Database creation and migration
- [ ] Theme and plugin installation
- [ ] API integration testing
- [ ] Security configuration
- [ ] Backup system setup
- [ ] Monitoring implementation

---

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review Django and WordPress logs
3. Test API endpoints individually
4. Verify database connections

**Production URLs:**
- WordPress: `https://yourdomain.com`
- Django Admin: `https://api.yourdomain.com/admin-dashboard/`
- API Status: `https://api.yourdomain.com/api/admin/status/`