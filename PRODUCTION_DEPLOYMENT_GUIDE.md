# 🚀 Stock Scanner Production Deployment Guide

This guide will help you deploy the Stock Scanner Django application to production on a Linux server.

## 📋 Prerequisites

- Ubuntu 20.04+ or CentOS 7+ server
- Root or sudo access
- Domain name pointing to your server
- SSL certificate (we'll set up Let's Encrypt)

---

## 🔧 Step 1: Server Setup

### Update System
```bash
sudo apt update && sudo apt upgrade -y
```

### Install Required Packages
```bash
# Install Python, MySQL, Nginx, and other dependencies
sudo apt install -y python3 python3-pip python3-venv python3-dev
sudo apt install -y mysql-server mysql-client libmysqlclient-dev
sudo apt install -y nginx redis-server
sudo apt install -y git curl wget unzip
sudo apt install -y supervisor  # For process management
```

### Install Node.js (for any frontend assets)
```bash
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs
```

---

## 🗄️ Step 2: Database Setup

### Secure MySQL Installation
```bash
sudo mysql_secure_installation
```

### Create Database and User
```bash
sudo mysql -u root -p
```

```sql
-- Create database
CREATE DATABASE stockscanner_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Create user
CREATE USER 'stockscanner_user'@'localhost' IDENTIFIED BY 'your_secure_password_here';

-- Grant privileges
GRANT ALL PRIVILEGES ON stockscanner_db.* TO 'stockscanner_user'@'localhost';
FLUSH PRIVILEGES;

-- Exit MySQL
EXIT;
```

---

## 📁 Step 3: Application Setup

### Create Application Directory
```bash
sudo mkdir -p /var/www/stockscanner
sudo chown $USER:$USER /var/www/stockscanner
cd /var/www/stockscanner
```

### Clone Repository
```bash
git clone https://github.com/Toasterfire-come/stock-scanner-complete.git .
```

### Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Install Additional Production Dependencies
```bash
pip install gunicorn psycopg2-binary
```

---

## ⚙️ Step 4: Environment Configuration

### Create Production Environment File
```bash
cp .env.production .env
```

### Edit Environment Variables
```bash
nano .env
```

**Update these critical values:**
```bash
# Generate a new secret key
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Update .env with your values:
DEBUG=False
SECRET_KEY=your-generated-secret-key
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DATABASE_URL=mysql://stockscanner_user:your_secure_password_here@localhost:3306/stockscanner_db
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

---

## 🔄 Step 5: Django Setup

### Run Database Migrations
```bash
source venv/bin/activate
python manage.py makemigrations
python manage.py migrate
```

### Create Superuser
```bash
python manage.py createsuperuser
```

### Collect Static Files
```bash
sudo mkdir -p /var/www/stockscanner/static
sudo chown $USER:$USER /var/www/stockscanner/static
python manage.py collectstatic --noinput
```

### Load Initial Data
```bash
# Load NASDAQ data
python manage.py load_nasdaq_only

# Update stock prices (optional - will happen automatically)
python manage.py update_stocks_yfinance --limit 100
```

---

## 🌐 Step 6: Gunicorn Setup

### Create Gunicorn Configuration
```bash
sudo nano /etc/systemd/system/stockscanner.service
```

```ini
[Unit]
Description=Stock Scanner Django Application
After=network.target mysql.service

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/var/www/stockscanner
Environment="PATH=/var/www/stockscanner/venv/bin"
ExecStart=/var/www/stockscanner/venv/bin/gunicorn --workers 3 --bind unix:/var/www/stockscanner/stockscanner.sock stockscanner_django.wsgi:application
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true

[Install]
WantedBy=multi-user.target
```

### Set Permissions
```bash
sudo chown -R www-data:www-data /var/www/stockscanner
sudo chmod -R 755 /var/www/stockscanner
```

### Start Gunicorn Service
```bash
sudo systemctl daemon-reload
sudo systemctl enable stockscanner
sudo systemctl start stockscanner
sudo systemctl status stockscanner
```

---

## 🔒 Step 7: Nginx Configuration

### Create Nginx Configuration
```bash
sudo nano /etc/nginx/sites-available/stockscanner
```

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    client_max_body_size 20M;
    
    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        root /var/www/stockscanner;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        root /var/www/stockscanner;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/var/www/stockscanner/stockscanner.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Enable Site
```bash
sudo ln -s /etc/nginx/sites-available/stockscanner /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## 🔐 Step 8: SSL Certificate (Let's Encrypt)

### Install Certbot
```bash
sudo apt install -y certbot python3-certbot-nginx
```

### Obtain SSL Certificate
```bash
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

### Test Auto-Renewal
```bash
sudo certbot renew --dry-run
```

---

## 📊 Step 9: Background Tasks Setup

### Create Scheduler Service
```bash
sudo nano /etc/systemd/system/stockscanner-scheduler.service
```

```ini
[Unit]
Description=Stock Scanner Background Scheduler
After=network.target mysql.service

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/var/www/stockscanner
Environment="PATH=/var/www/stockscanner/venv/bin"
ExecStart=/var/www/stockscanner/venv/bin/python manage.py run_scheduler
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Start Scheduler Service
```bash
sudo systemctl daemon-reload
sudo systemctl enable stockscanner-scheduler
sudo systemctl start stockscanner-scheduler
sudo systemctl status stockscanner-scheduler
```

---

## 🔥 Step 10: Firewall Configuration

### Configure UFW
```bash
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw enable
sudo ufw status
```

---

## 📝 Step 11: Logging Setup

### Create Log Directories
```bash
sudo mkdir -p /var/log/stockscanner
sudo chown www-data:www-data /var/log/stockscanner
```

### Setup Log Rotation
```bash
sudo nano /etc/logrotate.d/stockscanner
```

```
/var/log/stockscanner/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 www-data www-data
    postrotate
        systemctl reload stockscanner
    endscript
}
```

---

## 🚀 Step 12: Final Testing

### Test Application
```bash
# Check services
sudo systemctl status stockscanner
sudo systemctl status stockscanner-scheduler
sudo systemctl status nginx
sudo systemctl status mysql

# Test Django application
source /var/www/stockscanner/venv/bin/activate
cd /var/www/stockscanner
python manage.py check --deploy

# Test database connection
python manage.py dbshell
```

### Test URLs
- `https://yourdomain.com/` - Should show admin dashboard
- `https://yourdomain.com/admin/` - Django admin
- `https://yourdomain.com/api/admin/status/` - API status

---

## 🔄 Step 13: Maintenance Commands

### Daily Operations
```bash
# Check logs
sudo tail -f /var/log/stockscanner/django.log

# Update stock data manually
cd /var/www/stockscanner
source venv/bin/activate
python manage.py update_nasdaq_now

# Check system status
python manage.py monitor_system
```

### Weekly Maintenance
```bash
# Optimize database
python manage.py optimize_database

# Clean old data
python manage.py cleanup_old_data --days 90

# Update system packages
sudo apt update && sudo apt upgrade -y
```

### Emergency Operations
```bash
# Restart all services
sudo systemctl restart stockscanner
sudo systemctl restart stockscanner-scheduler
sudo systemctl restart nginx

# Check service logs
sudo journalctl -u stockscanner -f
sudo journalctl -u stockscanner-scheduler -f
```

---

## 📱 Step 14: Monitoring Setup (Optional)

### Install System Monitoring
```bash
# Install htop for system monitoring
sudo apt install -y htop

# Monitor processes
htop

# Monitor disk usage
df -h

# Monitor memory usage
free -h
```

### Application Monitoring
```bash
# Check application metrics
curl https://yourdomain.com/api/admin/status/

# Monitor database connections
mysql -u stockscanner_user -p -e "SHOW PROCESSLIST;"
```

---

## 🔧 Troubleshooting

### Common Issues

**1. Permission Errors**
```bash
sudo chown -R www-data:www-data /var/www/stockscanner
sudo chmod -R 755 /var/www/stockscanner
```

**2. Database Connection Issues**
```bash
# Test database connection
mysql -u stockscanner_user -p stockscanner_db

# Check MySQL status
sudo systemctl status mysql
```

**3. Static Files Not Loading**
```bash
# Collect static files again
python manage.py collectstatic --noinput

# Check nginx configuration
sudo nginx -t
```

**4. SSL Certificate Issues**
```bash
# Renew certificate
sudo certbot renew

# Check certificate status
sudo certbot certificates
```

---

## 🎯 Production Checklist

- [ ] Server updated and secured
- [ ] MySQL database created and configured
- [ ] Application deployed and dependencies installed
- [ ] Environment variables configured
- [ ] Database migrations completed
- [ ] Static files collected
- [ ] Gunicorn service running
- [ ] Nginx configured and running
- [ ] SSL certificate installed
- [ ] Background scheduler running
- [ ] Firewall configured
- [ ] Logging setup
- [ ] Application tested and accessible
- [ ] Monitoring configured

---

## 📞 Support

If you encounter issues during deployment:

1. Check the logs: `sudo tail -f /var/log/stockscanner/django.log`
2. Check service status: `sudo systemctl status stockscanner`
3. Test Django deployment: `python manage.py check --deploy`
4. Verify environment variables are set correctly

Your Stock Scanner application should now be running in production! 🎉