# Ubuntu Production Deployment Guide
**Complete Step-by-Step Guide from Clean Ubuntu Server to Production**
**Project:** Trade Scan Pro Stock Scanner
**Date:** December 30, 2025

---

## 🎯 OVERVIEW

This guide takes you from a **clean Ubuntu 22.04 LTS server** to a **fully deployed production application** with:
- Django backend running with Gunicorn
- MySQL database
- Cloudflare Tunnel for secure HTTPS
- React frontend served via Nginx
- Automated scanners and tasks
- SSL/TLS encryption
- Production-ready configuration

**Estimated Time:** 2-3 hours
**Difficulty:** Intermediate

---

## 📋 PREREQUISITES

### What You Need
- Ubuntu 22.04 LTS server (VPS, cloud instance, or dedicated server)
- Minimum 2GB RAM, 20GB disk space
- Root or sudo access
- Domain name (e.g., tradescanpro.com)
- Cloudflare account (free tier works)

### What You Should Have Ready
- GitHub repository access or project files
- MySQL root password (you'll create this)
- Cloudflare account credentials
- Domain DNS access

---

## 🚀 PART 1: SERVER SETUP

### Step 1: Update System

```bash
# Connect to your server via SSH
ssh root@your-server-ip

# Update package lists and upgrade system
sudo apt update && sudo apt upgrade -y

# Install essential build tools
sudo apt install -y build-essential software-properties-common curl wget git
```

---

### Step 2: Install Python 3.11+

```bash
# Add deadsnakes PPA for latest Python
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update

# Install Python 3.11
sudo apt install -y python3.11 python3.11-venv python3.11-dev python3-pip

# Set Python 3.11 as default (optional)
sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1

# Verify Python version
python3 --version  # Should show Python 3.11.x

# Upgrade pip
python3 -m pip install --upgrade pip
```

---

### Step 3: Install MySQL 8.0

```bash
# Install MySQL server
sudo apt install -y mysql-server

# Secure MySQL installation
sudo mysql_secure_installation

# When prompted:
# - Set root password: [Choose a strong password]
# - Remove anonymous users: Yes
# - Disallow root login remotely: Yes
# - Remove test database: Yes
# - Reload privilege tables: Yes

# Start MySQL service
sudo systemctl start mysql
sudo systemctl enable mysql

# Verify MySQL is running
sudo systemctl status mysql
```

---

### Step 4: Create Database and User

```bash
# Login to MySQL as root
sudo mysql -u root -p

# In MySQL prompt, run:
```

```sql
-- Create database
CREATE DATABASE stock_scanner CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Create user with strong password
CREATE USER 'stockscanner'@'localhost' IDENTIFIED BY 'YourStrongPassword123!';

-- Grant all privileges
GRANT ALL PRIVILEGES ON stock_scanner.* TO 'stockscanner'@'localhost';

-- Flush privileges
FLUSH PRIVILEGES;

-- Exit
EXIT;
```

```bash
# Test connection
mysql -u stockscanner -p stock_scanner
# Enter password when prompted
# If successful, exit with: EXIT;
```

---

### Step 5: Install Node.js (for frontend build)

```bash
# Install Node.js 18.x LTS
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Verify installation
node --version  # Should show v18.x.x
npm --version   # Should show 9.x.x or higher
```

---

### Step 6: Install Nginx

```bash
# Install Nginx web server
sudo apt install -y nginx

# Start and enable Nginx
sudo systemctl start nginx
sudo systemctl enable nginx

# Verify Nginx is running
sudo systemctl status nginx

# Allow Nginx through firewall
sudo ufw allow 'Nginx Full'
sudo ufw allow OpenSSH
sudo ufw enable
```

---

## 🗂️ PART 2: PROJECT DEPLOYMENT

### Step 7: Create Project Structure

```bash
# Create application directory
sudo mkdir -p /var/www/tradescanpro
sudo chown -R $USER:$USER /var/www/tradescanpro
cd /var/www/tradescanpro

# Clone your repository (or upload files)
git clone https://github.com/your-username/stock-scanner-complete.git .

# OR if uploading manually:
# scp -r /path/to/local/stock-scanner-complete root@server:/var/www/tradescanpro/
```

---

### Step 8: Setup Backend Environment

```bash
cd /var/www/tradescanpro/backend

# Create Python virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Install additional production packages
pip install gunicorn pymysql cryptography
```

---

### Step 9: Configure Backend Environment Variables

```bash
# Create .env file
nano .env
```

**Add the following** (replace with your actual values):

```bash
# Django Settings
DEBUG=False
SECRET_KEY=your-very-long-random-secret-key-here-generate-with-python
DJANGO_SETTINGS_MODULE=stockscanner_django.settings
ALLOWED_HOSTS=api.tradescanpro.com,tradescanpro.com,your-server-ip

# Database
DB_NAME=stock_scanner
DB_USER=stockscanner
DB_PASSWORD=YourStrongPassword123!
DB_HOST=localhost
DB_PORT=3306

# Security
CSRF_TRUSTED_ORIGINS=https://tradescanpro.com,https://www.tradescanpro.com
FRONTEND_URL=https://tradescanpro.com

# Cloudflare Tunnel
CLOUDFLARE_TUNNEL_TOKEN=your-cloudflare-tunnel-token

# Optional: Email settings
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-specific-password
```

**To generate a secure SECRET_KEY:**
```bash
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

**Save and exit:** `Ctrl+X`, then `Y`, then `Enter`

---

### Step 10: Run Django Migrations

```bash
# Still in /var/www/tradescanpro/backend with venv activated

# Make migrations
python manage.py makemigrations

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
# Follow prompts to create admin account

# Collect static files
python manage.py collectstatic --noinput

# Test Django is working
python manage.py check --deploy
```

---

### Step 11: Build Frontend

```bash
cd /var/www/tradescanpro/frontend

# Install dependencies
npm install

# Create production .env file
nano .env.production
```

**Add:**
```bash
REACT_APP_BACKEND_URL=https://api.tradescanpro.com
REACT_APP_FRONTEND_URL=https://tradescanpro.com
NODE_ENV=production
```

```bash
# Build production bundle
npm run build

# Verify build folder exists
ls -lah build/
```

---

## 🔧 PART 3: PRODUCTION SERVICES

### Step 12: Configure Gunicorn

```bash
# Create Gunicorn config
sudo nano /etc/systemd/system/gunicorn.service
```

**Add:**
```ini
[Unit]
Description=Gunicorn daemon for Trade Scan Pro
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/tradescanpro/backend
Environment="PATH=/var/www/tradescanpro/backend/venv/bin"
ExecStart=/var/www/tradescanpro/backend/venv/bin/gunicorn \
    --workers 4 \
    --bind unix:/var/www/tradescanpro/backend/gunicorn.sock \
    --timeout 120 \
    --access-logfile /var/log/gunicorn/access.log \
    --error-logfile /var/log/gunicorn/error.log \
    stockscanner_django.wsgi:application

[Install]
WantedBy=multi-user.target
```

```bash
# Create log directory
sudo mkdir -p /var/log/gunicorn
sudo chown -R www-data:www-data /var/log/gunicorn

# Set permissions
sudo chown -R www-data:www-data /var/www/tradescanpro
sudo chmod -R 755 /var/www/tradescanpro

# Start Gunicorn
sudo systemctl start gunicorn
sudo systemctl enable gunicorn

# Check status
sudo systemctl status gunicorn

# View logs if needed
sudo journalctl -u gunicorn -f
```

---

### Step 13: Configure Nginx

```bash
# Create Nginx site configuration
sudo nano /etc/nginx/sites-available/tradescanpro
```

**Add:**
```nginx
# Frontend - tradescanpro.com
server {
    listen 80;
    server_name tradescanpro.com www.tradescanpro.com;

    root /var/www/tradescanpro/frontend/build;
    index index.html;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/x-javascript application/xml+rss application/json;

    # Frontend routes
    location / {
        try_files $uri $uri/ /index.html;
        add_header Cache-Control "public, max-age=3600";
    }

    # Static files
    location /static/ {
        alias /var/www/tradescanpro/frontend/build/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
}

# Backend API - api.tradescanpro.com
server {
    listen 80;
    server_name api.tradescanpro.com;

    client_max_body_size 10M;

    # Proxy to Gunicorn
    location / {
        proxy_pass http://unix:/var/www/tradescanpro/backend/gunicorn.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
        proxy_connect_timeout 120s;
        proxy_send_timeout 120s;
        proxy_read_timeout 120s;
    }

    # Django static files
    location /static/ {
        alias /var/www/tradescanpro/backend/staticfiles/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Django media files
    location /media/ {
        alias /var/www/tradescanpro/backend/media/;
        expires 30d;
        add_header Cache-Control "public";
    }
}
```

```bash
# Enable the site
sudo ln -s /etc/nginx/sites-available/tradescanpro /etc/nginx/sites-enabled/

# Remove default site
sudo rm /etc/nginx/sites-enabled/default

# Test Nginx configuration
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx
```

---

### Step 14: Setup Cloudflare Tunnel

```bash
# Download cloudflared
wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
sudo dpkg -i cloudflared-linux-amd64.deb

# Login to Cloudflare (will open browser)
cloudflared tunnel login

# Create tunnel
cloudflared tunnel create tradescanpro-tunnel

# Note the tunnel ID shown in output

# Create tunnel configuration
sudo mkdir -p /etc/cloudflared
sudo nano /etc/cloudflared/config.yml
```

**Add:**
```yaml
tunnel: your-tunnel-id-here
credentials-file: /root/.cloudflared/your-tunnel-id.json

ingress:
  # API subdomain
  - hostname: api.tradescanpro.com
    service: http://localhost:80
    originRequest:
      noTLSVerify: true

  # Main domain
  - hostname: tradescanpro.com
    service: http://localhost:80
    originRequest:
      noTLSVerify: true

  # WWW subdomain
  - hostname: www.tradescanpro.com
    service: http://localhost:80
    originRequest:
      noTLSVerify: true

  # Catch-all
  - service: http_status:404
```

```bash
# Create DNS records
cloudflared tunnel route dns tradescanpro-tunnel tradescanpro.com
cloudflared tunnel route dns tradescanpro-tunnel www.tradescanpro.com
cloudflared tunnel route dns tradescanpro-tunnel api.tradescanpro.com

# Install as service
sudo cloudflared service install
sudo systemctl start cloudflared
sudo systemctl enable cloudflared

# Check status
sudo systemctl status cloudflared
```

---

## 🤖 PART 4: AUTOMATED TASKS

### Step 15: Setup Cron Jobs for Scanners

```bash
# Edit crontab
crontab -e

# Add these lines:
```

```cron
# 1-minute scanner (market hours only: 9:30 AM - 4:00 PM EST, Mon-Fri)
*/1 9-16 * * 1-5 cd /var/www/tradescanpro/backend && /var/www/tradescanpro/backend/venv/bin/python manage.py run_realtime_scanner >> /var/log/scanner-1min.log 2>&1

# Daily scanner (6 AM EST)
0 6 * * * cd /var/www/tradescanpro/backend && /var/www/tradescanpro/backend/venv/bin/python manage.py run_daily_scanner >> /var/log/scanner-daily.log 2>&1

# Weekly scanner (Sunday 7 AM EST)
0 7 * * 0 cd /var/www/tradescanpro/backend && /var/www/tradescanpro/backend/venv/bin/python manage.py run_weekly_scanner >> /var/log/scanner-weekly.log 2>&1

# Cleanup old data (daily at midnight)
0 0 * * * cd /var/www/tradescanpro/backend && /var/www/tradescanpro/backend/venv/bin/python manage.py cleanup_old_data >> /var/log/cleanup.log 2>&1
```

```bash
# Create log files
sudo touch /var/log/scanner-{1min,daily,weekly}.log /var/log/cleanup.log
sudo chown www-data:www-data /var/log/scanner-*.log /var/log/cleanup.log
```

---

## 🔐 PART 5: SSL & SECURITY

### Step 16: Configure Firewall

```bash
# Configure UFW firewall
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw enable

# Verify rules
sudo ufw status
```

---

### Step 17: Harden Security

```bash
# Disable root SSH login
sudo nano /etc/ssh/sshd_config
```

**Find and change:**
```
PermitRootLogin no
PasswordAuthentication no
```

```bash
# Restart SSH
sudo systemctl restart sshd

# Install fail2ban for brute-force protection
sudo apt install -y fail2ban

# Configure fail2ban
sudo cp /etc/fail2ban/jail.conf /etc/fail2ban/jail.local
sudo systemctl start fail2ban
sudo systemctl enable fail2ban
```

---

## 📊 PART 6: MONITORING & MAINTENANCE

### Step 18: Setup Log Rotation

```bash
# Create logrotate config
sudo nano /etc/logrotate.d/tradescanpro
```

**Add:**
```
/var/log/scanner-*.log /var/log/cleanup.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 www-data www-data
    sharedscripts
}

/var/log/gunicorn/*.log {
    daily
    rotate 7
    compress
    delaycompress
    notifempty
    create 0640 www-data www-data
    sharedscripts
    postrotate
        systemctl reload gunicorn
    endscript
}
```

---

### Step 19: Create Monitoring Script

```bash
# Create health check script
sudo nano /usr/local/bin/check-tradescanpro.sh
```

**Add:**
```bash
#!/bin/bash

# Check Gunicorn
if ! systemctl is-active --quiet gunicorn; then
    echo "ERROR: Gunicorn is down!"
    sudo systemctl restart gunicorn
fi

# Check Nginx
if ! systemctl is-active --quiet nginx; then
    echo "ERROR: Nginx is down!"
    sudo systemctl restart nginx
fi

# Check Cloudflare Tunnel
if ! systemctl is-active --quiet cloudflared; then
    echo "ERROR: Cloudflare tunnel is down!"
    sudo systemctl restart cloudflared
fi

# Check MySQL
if ! systemctl is-active --quiet mysql; then
    echo "ERROR: MySQL is down!"
    sudo systemctl restart mysql
fi

echo "$(date): All services running"
```

```bash
# Make executable
sudo chmod +x /usr/local/bin/check-tradescanpro.sh

# Add to crontab (check every 5 minutes)
crontab -e
```

**Add:**
```cron
*/5 * * * * /usr/local/bin/check-tradescanpro.sh >> /var/log/health-check.log 2>&1
```

---

## ✅ PART 7: VERIFICATION & TESTING

### Step 20: Verify All Services

```bash
# Check all services are running
sudo systemctl status gunicorn
sudo systemctl status nginx
sudo systemctl status cloudflared
sudo systemctl status mysql

# Check logs for errors
sudo journalctl -u gunicorn -n 50
sudo journalctl -u nginx -n 50
sudo journalctl -u cloudflared -n 50

# Test database connection
mysql -u stockscanner -p stock_scanner -e "SELECT COUNT(*) FROM auth_user;"

# Test API endpoint
curl -I https://api.tradescanpro.com/api/health/

# Test frontend
curl -I https://tradescanpro.com/
```

---

### Step 21: Test Frontend-Backend Integration

```bash
# Visit your site
# https://tradescanpro.com

# Open browser DevTools (F12)
# Network tab → Should see successful API calls to api.tradescanpro.com
# Console tab → Should have no errors

# Test key features:
# 1. Sign up / Sign in
# 2. View stock data
# 3. Run a screener
# 4. Check pricing page
# 5. Test Pay-Per-Use plan display
```

---

## 🚀 PART 8: FINAL CONFIGURATION

### Step 22: Optimize Database

```bash
# Login to MySQL
sudo mysql -u root -p

# Run optimization
```

```sql
USE stock_scanner;

-- Optimize all tables
OPTIMIZE TABLE auth_user, stocks_stock, stocks_screener, stocks_alert;

-- Create indexes for performance
CREATE INDEX idx_stock_symbol ON stocks_stock(symbol);
CREATE INDEX idx_stock_last_updated ON stocks_stock(last_updated);
CREATE INDEX idx_screener_user ON stocks_screener(user_id);
CREATE INDEX idx_alert_user ON stocks_alert(user_id);

EXIT;
```

---

### Step 23: Setup Backups

```bash
# Create backup script
sudo nano /usr/local/bin/backup-tradescanpro.sh
```

**Add:**
```bash
#!/bin/bash

BACKUP_DIR="/var/backups/tradescanpro"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup database
mysqldump -u stockscanner -pYourStrongPassword123! stock_scanner | gzip > $BACKUP_DIR/db_$DATE.sql.gz

# Backup media files
tar -czf $BACKUP_DIR/media_$DATE.tar.gz /var/www/tradescanpro/backend/media/

# Keep only last 7 days of backups
find $BACKUP_DIR -name "db_*.sql.gz" -mtime +7 -delete
find $BACKUP_DIR -name "media_*.tar.gz" -mtime +7 -delete

echo "$(date): Backup completed"
```

```bash
# Make executable
sudo chmod +x /usr/local/bin/backup-tradescanpro.sh

# Schedule daily backups (3 AM)
crontab -e
```

**Add:**
```cron
0 3 * * * /usr/local/bin/backup-tradescanpro.sh >> /var/log/backup.log 2>&1
```

---

## 📝 POST-DEPLOYMENT CHECKLIST

### Essential Checks ✅

- [ ] All services running (Gunicorn, Nginx, Cloudflare, MySQL)
- [ ] Frontend accessible at https://tradescanpro.com
- [ ] API accessible at https://api.tradescanpro.com
- [ ] SSL/TLS working (padlock in browser)
- [ ] No console errors in browser DevTools
- [ ] Can sign up / sign in
- [ ] Pricing page displays correctly (Basic, Pro, Pay-Per-Use)
- [ ] Scanners running via cron
- [ ] Health checks working
- [ ] Backups scheduled
- [ ] Firewall configured
- [ ] fail2ban active

---

## 🔧 TROUBLESHOOTING

### Service Won't Start

```bash
# Check service status
sudo systemctl status servicename

# View detailed logs
sudo journalctl -u servicename -xe

# Restart service
sudo systemctl restart servicename
```

### Database Connection Errors

```bash
# Verify MySQL is running
sudo systemctl status mysql

# Test connection
mysql -u stockscanner -p

# Check Django database settings
cd /var/www/tradescanpro/backend
source venv/bin/activate
python manage.py dbshell
```

### Cloudflare Tunnel Issues

```bash
# Check tunnel status
sudo systemctl status cloudflared

# View logs
sudo journalctl -u cloudflared -f

# Restart tunnel
sudo systemctl restart cloudflared
```

### Nginx 502 Bad Gateway

```bash
# Check Gunicorn is running
sudo systemctl status gunicorn

# Check socket file exists
ls -l /var/www/tradescanpro/backend/gunicorn.sock

# Check Nginx error log
sudo tail -f /var/log/nginx/error.log
```

---

## 🎯 PERFORMANCE OPTIMIZATION

### Enable HTTP/2

```bash
# Edit Nginx config
sudo nano /etc/nginx/sites-available/tradescanpro
```

**Change `listen 80` to:**
```nginx
listen 443 ssl http2;
```

### Configure MySQL for Performance

```bash
sudo nano /etc/mysql/mysql.conf.d/mysqld.cnf
```

**Add under `[mysqld]`:**
```ini
# Performance tuning
innodb_buffer_pool_size = 1G
innodb_log_file_size = 256M
max_connections = 200
query_cache_size = 32M
```

```bash
# Restart MySQL
sudo systemctl restart mysql
```

---

## 📚 USEFUL COMMANDS

### Check Disk Usage
```bash
df -h
du -sh /var/www/tradescanpro/*
```

### Monitor Resource Usage
```bash
htop  # Install: sudo apt install htop
```

### View Active Connections
```bash
sudo netstat -tulpn | grep LISTEN
```

### Update Application
```bash
cd /var/www/tradescanpro
git pull
cd backend
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart gunicorn
```

---

## 🎉 DEPLOYMENT COMPLETE!

Your Trade Scan Pro application is now **LIVE IN PRODUCTION** on Ubuntu!

**Access your application:**
- Frontend: https://tradescanpro.com
- API: https://api.tradescanpro.com
- Admin: https://tradescanpro.com/admin

**Next Steps:**
1. Monitor logs for first 24-48 hours
2. Test all features with real users
3. Set up error monitoring (Sentry recommended)
4. Configure email notifications
5. Set up automated alerts

---

**Deployment Date:** December 30, 2025
**Guide Version:** 1.0
**Estimated Completion Time:** 2-3 hours
**Difficulty:** Intermediate

**🎯 Your production deployment is complete and ready for users!**
