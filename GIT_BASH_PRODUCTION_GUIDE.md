# 🚀 Stock Scanner Git Bash Production Deployment Guide

This guide covers deploying the Stock Scanner Django application to production using Git Bash on Windows with a Linux VPS/server.

## 📋 Prerequisites

- **Local Development**: Windows with Git Bash installed
- **Production Server**: Ubuntu 20.04+ or CentOS 7+ VPS/server
- **Domain**: Domain name pointing to your server IP
- **SSH Access**: SSH key or password access to your server

---

## 🖥️ Part 1: Local Development Setup (Git Bash)

### Step 1: Clone and Setup Locally

```bash
# Clone the repository
git clone https://github.com/Toasterfire-come/stock-scanner-complete.git
cd stock-scanner-complete

# Run the Git Bash setup script
./start_django_gitbash.sh
```

### Step 2: Test Locally

Your application should be running at:
- **Main Dashboard**: http://127.0.0.1:8000/
- **Admin Panel**: http://127.0.0.1:8000/admin/
- **Login**: admin / admin123

---

## 🌐 Part 2: Production Server Setup

### Step 1: Connect to Your Server

```bash
# From Git Bash, connect to your server
ssh root@your-server-ip
# or
ssh username@your-server-ip
```

### Step 2: Server Preparation

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y python3 python3-pip python3-venv python3-dev
sudo apt install -y mysql-server mysql-client libmysqlclient-dev
sudo apt install -y nginx redis-server git curl wget unzip
sudo apt install -y supervisor certbot python3-certbot-nginx
```

### Step 3: Database Setup

```bash
# Secure MySQL
sudo mysql_secure_installation

# Create database
sudo mysql -u root -p
```

```sql
CREATE DATABASE stockscanner_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'stockscanner_user'@'localhost' IDENTIFIED BY 'your_secure_password';
GRANT ALL PRIVILEGES ON stockscanner_db.* TO 'stockscanner_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### Step 4: Application Deployment

```bash
# Create application directory
sudo mkdir -p /var/www/stockscanner
sudo chown $USER:$USER /var/www/stockscanner
cd /var/www/stockscanner

# Clone from your repository
git clone https://github.com/Toasterfire-come/stock-scanner-complete.git .

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn
```

### Step 5: Environment Configuration

```bash
# Create production environment file
cat > .env << 'EOF'
DEBUG=False
SECRET_KEY=your-super-secret-production-key-here
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,your-server-ip

# Database
DATABASE_URL=mysql://stockscanner_user:your_secure_password@localhost:3306/stockscanner_db

# Email (Gmail example)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=Stock Scanner <your-email@gmail.com>

# Security
SECURE_SSL_REDIRECT=True
SECURE_PROXY_SSL_HEADER=HTTP_X_FORWARDED_PROTO,https
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True

# Scheduler
SCHEDULER_ENABLED=True
NASDAQ_UPDATE_INTERVAL=10
EOF

# Generate a secure secret key
python3 -c "from django.core.management.utils import get_random_secret_key; print('SECRET_KEY=' + get_random_secret_key())"
# Copy the output and update your .env file
```

### Step 6: Django Setup

```bash
# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Load NASDAQ data
python manage.py load_nasdaq_only

# Collect static files
sudo mkdir -p /var/www/stockscanner/static
python manage.py collectstatic --noinput

# Set permissions
sudo chown -R www-data:www-data /var/www/stockscanner
sudo chmod -R 755 /var/www/stockscanner
```

---

## ⚙️ Part 3: Production Services Setup

### Step 1: Gunicorn Service

```bash
# Create systemd service
sudo tee /etc/systemd/system/stockscanner.service << 'EOF'
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
EOF

# Start and enable service
sudo systemctl daemon-reload
sudo systemctl enable stockscanner
sudo systemctl start stockscanner
sudo systemctl status stockscanner
```

### Step 2: Background Scheduler Service

```bash
# Create scheduler service
sudo tee /etc/systemd/system/stockscanner-scheduler.service << 'EOF'
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
EOF

# Start and enable scheduler
sudo systemctl daemon-reload
sudo systemctl enable stockscanner-scheduler
sudo systemctl start stockscanner-scheduler
sudo systemctl status stockscanner-scheduler
```

### Step 3: Nginx Configuration

```bash
# Create Nginx site configuration
sudo tee /etc/nginx/sites-available/stockscanner << 'EOF'
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
EOF

# Enable site
sudo ln -s /etc/nginx/sites-available/stockscanner /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Step 4: SSL Certificate

```bash
# Install SSL certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Test auto-renewal
sudo certbot renew --dry-run
```

### Step 5: Firewall Setup

```bash
# Configure UFW firewall
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw enable
sudo ufw status
```

---

## 🔄 Part 4: Deployment Workflow (Git Bash to Production)

### From Git Bash (Local Development)

```bash
# 1. Make your changes locally
git add .
git commit -m "Your changes"
git push origin main

# 2. Connect to production server
ssh username@your-server-ip

# 3. Update production (on server)
cd /var/www/stockscanner
git pull origin main

# 4. Update dependencies if needed
source venv/bin/activate
pip install -r requirements.txt

# 5. Run migrations if needed
python manage.py migrate

# 6. Collect static files
python manage.py collectstatic --noinput

# 7. Restart services
sudo systemctl restart stockscanner
sudo systemctl restart stockscanner-scheduler

# 8. Check status
sudo systemctl status stockscanner
sudo systemctl status stockscanner-scheduler
```

### Automated Deployment Script

Create this script on your server for easier deployments:

```bash
# Create deployment script
sudo tee /var/www/stockscanner/deploy.sh << 'EOF'
#!/bin/bash
echo "🚀 Deploying Stock Scanner updates..."

# Pull latest changes
git pull origin main

# Activate virtual environment
source venv/bin/activate

# Install/update dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Restart services
sudo systemctl restart stockscanner
sudo systemctl restart stockscanner-scheduler

# Check status
echo "✅ Checking service status..."
sudo systemctl status stockscanner --no-pager
sudo systemctl status stockscanner-scheduler --no-pager

echo "🎉 Deployment complete!"
echo "🌐 Check your site: https://yourdomain.com"
EOF

chmod +x /var/www/stockscanner/deploy.sh
```

Now you can deploy with: `./deploy.sh`

---

## 📊 Part 5: Monitoring and Maintenance

### Daily Monitoring

```bash
# Check application logs
sudo journalctl -u stockscanner -f

# Check scheduler logs
sudo journalctl -u stockscanner-scheduler -f

# Check system resources
htop
df -h
free -h

# Check stock data updates
curl https://yourdomain.com/api/admin/status/
```

### Weekly Maintenance

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Optimize database
cd /var/www/stockscanner
source venv/bin/activate
python manage.py optimize_database

# Clean old data
python manage.py cleanup_old_data --days 90

# Check SSL certificate
sudo certbot certificates
```

### Backup Strategy

```bash
# Create backup script
sudo tee /var/www/stockscanner/backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/var/backups/stockscanner"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
sudo mkdir -p $BACKUP_DIR

# Backup database
mysqldump -u stockscanner_user -p stockscanner_db > $BACKUP_DIR/db_backup_$DATE.sql

# Backup application files
tar -czf $BACKUP_DIR/app_backup_$DATE.tar.gz /var/www/stockscanner --exclude=venv --exclude=.git

# Keep only last 7 days of backups
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete

echo "✅ Backup completed: $DATE"
EOF

chmod +x /var/www/stockscanner/backup.sh

# Add to crontab for daily backups
echo "0 2 * * * /var/www/stockscanner/backup.sh" | sudo crontab -
```

---

## 🛠️ Troubleshooting

### Common Issues

**1. Service won't start**
```bash
sudo journalctl -u stockscanner -n 50
sudo systemctl restart stockscanner
```

**2. Database connection issues**
```bash
mysql -u stockscanner_user -p stockscanner_db
sudo systemctl status mysql
```

**3. Static files not loading**
```bash
python manage.py collectstatic --noinput
sudo nginx -t
sudo systemctl restart nginx
```

**4. SSL certificate issues**
```bash
sudo certbot renew
sudo systemctl restart nginx
```

### Emergency Commands

```bash
# Stop all services
sudo systemctl stop stockscanner
sudo systemctl stop stockscanner-scheduler
sudo systemctl stop nginx

# Start all services
sudo systemctl start mysql
sudo systemctl start nginx
sudo systemctl start stockscanner
sudo systemctl start stockscanner-scheduler

# Check all services
sudo systemctl status mysql nginx stockscanner stockscanner-scheduler
```

---

## 🎯 Production Checklist

- [ ] Server updated and secured
- [ ] MySQL database created and configured
- [ ] Application deployed from Git repository
- [ ] Environment variables configured
- [ ] Database migrations completed
- [ ] Static files collected
- [ ] Gunicorn service running
- [ ] Background scheduler running
- [ ] Nginx configured and running
- [ ] SSL certificate installed and auto-renewing
- [ ] Firewall configured
- [ ] Monitoring setup
- [ ] Backup strategy implemented
- [ ] Deployment workflow tested

---

## 🌟 Final Notes

Your Stock Scanner application is now running in production with:

- **Automatic NASDAQ data updates** every 10 minutes
- **WordPress integration** ready via API endpoints
- **Secure HTTPS** with auto-renewing SSL certificates
- **Professional monitoring** and logging
- **Easy deployment workflow** from Git Bash to production

**Access your production application:**
- Main site: https://yourdomain.com
- Admin panel: https://yourdomain.com/admin/
- API status: https://yourdomain.com/api/admin/status/

🎉 **Congratulations! Your Stock Scanner is live in production!**