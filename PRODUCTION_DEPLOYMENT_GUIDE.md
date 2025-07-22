# 🚀 Production Deployment Guide - Stock Scanner Platform

## 📋 **Overview**

This guide provides complete instructions for deploying the Stock Scanner platform to production on **retailtradescanner.com**. The platform includes:

- **Django Backend**: REST APIs, membership system, analytics
- **WordPress Frontend**: 24 professional pages with live widgets
- **4-Tier Membership System**: Free, Basic, Professional, Expert
- **Real-Time Analytics**: Live member counts and revenue tracking
- **Sales Tax Integration**: All 50 US states + DC

---

## 🏗️ **Architecture Overview**

```
📊 Production Stack:
├── Frontend: WordPress (retailtradescanner.com)
├── Backend: Django API (api.retailtradescanner.com)
├── Database: PostgreSQL
├── Cache: Redis
├── Web Server: Nginx
├── App Server: Gunicorn
├── SSL: Let's Encrypt
└── Monitoring: System logs + Django admin
```

---

## 🛠️ **Prerequisites**

### **Server Requirements:**
- **OS**: Ubuntu 20.04+ or CentOS 8+
- **RAM**: 4GB minimum (8GB recommended)
- **Storage**: 50GB SSD
- **CPU**: 2 cores minimum
- **Domain**: retailtradescanner.com (DNS configured)

### **Required Software:**
- Python 3.8+
- PostgreSQL 12+
- Redis 6+
- Nginx
- Node.js (for WordPress asset compilation)

---

## 📦 **Quick Start (Development)**

```bash
# 1. Clone and setup
git clone https://github.com/Toasterfire-come/stock-scanner-complete.git
cd stock-scanner-complete

# 2. Run automated setup
./startup.sh

# 3. Access application
# Django Admin: http://localhost:8000/admin
# Analytics API: http://localhost:8000/api/analytics/public/
```

---

## 🌐 **Production Deployment Steps**

### **Step 1: Server Preparation**

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install essential packages
sudo apt install -y python3 python3-pip python3-venv postgresql postgresql-contrib nginx redis-server git curl wget

# Install Node.js (for WordPress assets)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Create application user
sudo adduser stockscanner
sudo usermod -aG sudo stockscanner
```

### **Step 2: Database Setup**

```bash
# Switch to postgres user
sudo -u postgres psql

# Create database and user
CREATE DATABASE stockscanner_prod;
CREATE USER stockscanner_user WITH PASSWORD 'your_secure_password';
ALTER ROLE stockscanner_user SET client_encoding TO 'utf8';
ALTER ROLE stockscanner_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE stockscanner_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE stockscanner_prod TO stockscanner_user;
\q

# Configure PostgreSQL
sudo nano /etc/postgresql/12/main/postgresql.conf
# Add: listen_addresses = 'localhost'

sudo nano /etc/postgresql/12/main/pg_hba.conf
# Add: local stockscanner_prod stockscanner_user md5

# Restart PostgreSQL
sudo systemctl restart postgresql
```

### **Step 3: Redis Configuration**

```bash
# Configure Redis
sudo nano /etc/redis/redis.conf
# Uncomment: bind 127.0.0.1
# Set: maxmemory 256mb
# Set: maxmemory-policy allkeys-lru

# Start Redis
sudo systemctl enable redis-server
sudo systemctl start redis-server
```

### **Step 4: Application Deployment**

```bash
# Switch to application user
sudo su - stockscanner

# Clone repository
git clone https://github.com/Toasterfire-come/stock-scanner-complete.git
cd stock-scanner-complete

# Create Python virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Create production environment file
cp .env.example .env
nano .env
```

**Production .env Configuration:**
```bash
# Django Core Settings
SECRET_KEY=your-super-secure-secret-key-here
DEBUG=False
ADDITIONAL_HOSTS=retailtradescanner.com,api.retailtradescanner.com

# Database Configuration
DATABASE_URL=postgresql://stockscanner_user:your_secure_password@localhost:5432/stockscanner_prod

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# Email Configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=noreply@retailtradescanner.com
EMAIL_HOST_PASSWORD=your_gmail_app_password

# CORS Configuration
CORS_ALLOWED_ORIGINS=https://retailtradescanner.com,https://www.retailtradescanner.com

# Production Settings
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True

# Stripe Settings (when ready)
# STRIPE_PUBLISHABLE_KEY=pk_live_your_key
# STRIPE_SECRET_KEY=sk_live_your_key
# STRIPE_WEBHOOK_SECRET=whsec_your_webhook
```

### **Step 5: Django Application Setup**

```bash
# Run database migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Setup memberships
python manage.py setup_memberships

# Collect static files
python manage.py collectstatic --noinput

# Test configuration
python manage.py check --deploy
```

### **Step 6: Gunicorn Configuration**

Create Gunicorn configuration file and systemd services for production deployment.

### **Step 7: Nginx Configuration**

Configure Nginx as reverse proxy with SSL termination and security headers.

### **Step 8: SSL Certificate Setup**

Install and configure Let's Encrypt SSL certificates for secure HTTPS.

### **Step 9: WordPress Integration**

Deploy WordPress frontend with Stock Scanner plugin and theme.

### **Step 10: Service Management**

Enable and start all required system services.

---

## 📊 **Monitoring & Maintenance**

### **Log Locations:**
- Django logs: `/home/stockscanner/stock-scanner-complete/logs/django.log`
- Gunicorn logs: `/home/stockscanner/stock-scanner-complete/logs/gunicorn_*.log`
- Nginx logs: `/var/log/nginx/`
- System logs: `journalctl -u stockscanner.service`

### **Health Checks:**
```bash
# Check service status
sudo systemctl status stockscanner.service
sudo systemctl status nginx
sudo systemctl status postgresql
sudo systemctl status redis-server

# Test API endpoints
curl https://api.retailtradescanner.com/health/
curl https://api.retailtradescanner.com/api/analytics/public/
```

### **Backup Procedures:**
```bash
# Database backup
sudo -u postgres pg_dump stockscanner_prod > backup_$(date +%Y%m%d).sql

# Application backup
tar -czf stockscanner_backup_$(date +%Y%m%d).tar.gz /home/stockscanner/stock-scanner-complete
```

---

## 🔒 **Security Considerations**

### **Firewall Configuration:**
```bash
# Configure UFW
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw enable
```

### **Security Best Practices:**
- Use strong passwords and SSH keys
- Keep SSL certificates updated
- Regular security updates
- Monitor logs for suspicious activity
- Implement rate limiting
- Use HTTPS everywhere

---

## ✅ **Production Checklist**

### **Pre-Launch:**
- [ ] SSL certificates installed and working
- [ ] Database properly configured and secured
- [ ] All environment variables set correctly
- [ ] Services starting automatically
- [ ] Backups configured
- [ ] Monitoring in place
- [ ] DNS records configured
- [ ] Firewall properly configured

### **Post-Launch:**
- [ ] All API endpoints responding correctly
- [ ] WordPress integration working
- [ ] Email notifications functional
- [ ] Analytics data displaying correctly
- [ ] Membership system operational
- [ ] Stock data updating properly
- [ ] Payment processing ready (when needed)

---

## 🆘 **Troubleshooting**

### **Common Issues:**

**Service Won't Start:**
```bash
# Check service logs
journalctl -u stockscanner.service
# Check configuration
python manage.py check --deploy
```

**Database Connection Issues:**
```bash
# Test connection
python manage.py dbshell
# Check PostgreSQL status
sudo systemctl status postgresql
```

**API Not Responding:**
```bash
# Check Nginx configuration
sudo nginx -t
# Check Gunicorn process
ps aux | grep gunicorn
```

---

## 📞 **Support**

Your **retailtradescanner.com** platform is now ready for production with:
- ✅ **Real member analytics**
- ✅ **4-tier membership system** 
- ✅ **Automatic sales tax collection**
- ✅ **24 professional WordPress pages**
- ✅ **Complete Django backend**
- ✅ **Production-ready infrastructure**

🎉 **Launch your stock scanning business!** 🚀
