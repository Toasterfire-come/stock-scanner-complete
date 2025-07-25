# Stock Scanner Production Deployment Checklist

## Pre-Deployment Requirements

### Server Setup
- [ ] VPS/Server with Ubuntu 20.04+ or CentOS 8+
- [ ] Minimum 2GB RAM (4GB+ recommended)
- [ ] 20GB+ SSD storage
- [ ] Root or sudo access
- [ ] Domain name purchased and configured
- [ ] DNS records pointing to server IP

### Required Software
- [ ] Python 3.9+
- [ ] MySQL 8.0+
- [ ] Nginx
- [ ] PHP 8.0+
- [ ] Git
- [ ] SSL certificate (Let's Encrypt)

---

## Deployment Steps

### 1. Initial Server Setup
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y nginx mysql-server php8.0-fpm php8.0-mysql \
  php8.0-xml php8.0-curl php8.0-gd php8.0-mbstring php8.0-zip \
  python3 python3-pip python3-venv git curl wget unzip

# Install Python packages
sudo pip3 install --upgrade pip gunicorn
```

### 2. Database Setup
```sql
-- Create databases
CREATE DATABASE stockscanner_production CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE wordpress_stockscanner CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Create users
CREATE USER 'django_user'@'localhost' IDENTIFIED BY 'secure_password_here';
CREATE USER 'wp_user'@'localhost' IDENTIFIED BY 'secure_password_here';

-- Grant permissions
GRANT ALL PRIVILEGES ON stockscanner_production.* TO 'django_user'@'localhost';
GRANT ALL PRIVILEGES ON wordpress_stockscanner.* TO 'wp_user'@'localhost';
FLUSH PRIVILEGES;
```

### 3. Django Deployment
- [ ] Clone repository to `/var/www/stockscanner`
- [ ] Create virtual environment
- [ ] Install Python dependencies
- [ ] Configure production settings
- [ ] Run migrations
- [ ] Collect static files
- [ ] Create superuser
- [ ] Load NASDAQ data

### 4. WordPress Setup
- [ ] Download and extract WordPress to `/var/www/html`
- [ ] Configure `wp-config.php`
- [ ] Install Stock Scanner theme
- [ ] Install Stock Scanner plugin
- [ ] Complete WordPress installation
- [ ] Configure theme settings

### 5. Web Server Configuration
- [ ] Configure Nginx virtual hosts
- [ ] Set up SSL certificates
- [ ] Configure systemd service for Django
- [ ] Test all endpoints

### 6. Security Setup
- [ ] Configure firewall (UFW)
- [ ] Set proper file permissions
- [ ] Enable security headers
- [ ] Configure fail2ban (optional)

---

## Configuration Files

### Environment Variables
Create `/etc/environment`:
```bash
DJANGO_SECRET_KEY=your-super-secret-key
DB_PASSWORD=your-database-password
DJANGO_SETTINGS_MODULE=stockscanner_django.settings_production
```

### Systemd Service
File: `/etc/systemd/system/stockscanner.service`
```ini
[Unit]
Description=Stock Scanner Django App
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/stockscanner
Environment=DJANGO_SETTINGS_MODULE=stockscanner_django.settings_production
ExecStart=/var/www/stockscanner/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:8000 stockscanner_django.wsgi:application
Restart=always

[Install]
WantedBy=multi-user.target
```

### Nginx Configuration
File: `/etc/nginx/sites-available/stockscanner`
```nginx
# WordPress (yourdomain.com)
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

# Django API (api.yourdomain.com)
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

---

## Post-Deployment Testing

### API Endpoints
Test these URLs:
- [ ] `https://api.yourdomain.com/api/admin/status/`
- [ ] `https://api.yourdomain.com/api/wordpress/stocks/`
- [ ] `https://api.yourdomain.com/api/wordpress/news/`
- [ ] `https://api.yourdomain.com/admin-dashboard/`

### WordPress Integration
- [ ] Theme activated and configured
- [ ] Plugin activated
- [ ] Shortcodes working: `[stock_scanner_stocks]`
- [ ] API connection successful
- [ ] Search functionality working

### System Health
- [ ] Django service running: `systemctl status stockscanner`
- [ ] Nginx running: `systemctl status nginx`
- [ ] MySQL running: `systemctl status mysql`
- [ ] SSL certificates valid
- [ ] Firewall configured
- [ ] Backups working
- [ ] Logs accessible

---

## Monitoring Setup

### Log Files
- Django: `/var/log/stockscanner/django.log`
- Nginx: `/var/log/nginx/access.log`, `/var/log/nginx/error.log`
- System: `/var/log/syslog`

### Health Checks
Create `/usr/local/bin/stockscanner-health.sh`:
```bash
#!/bin/bash
systemctl is-active --quiet stockscanner || systemctl restart stockscanner
systemctl is-active --quiet nginx || systemctl restart nginx
systemctl is-active --quiet mysql || systemctl restart mysql

curl -f https://api.yourdomain.com/api/admin/status/ > /dev/null 2>&1 || \
  echo "API DOWN at $(date)" >> /var/log/stockscanner/health.log
```

Add to crontab: `*/5 * * * * /usr/local/bin/stockscanner-health.sh`

### Backup Script
Create `/usr/local/bin/stockscanner-backup.sh`:
```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups"

mkdir -p $BACKUP_DIR

# Database backups
mysqldump -u root stockscanner_production > $BACKUP_DIR/django_$DATE.sql
mysqldump -u root wordpress_stockscanner > $BACKUP_DIR/wordpress_$DATE.sql

# File backups
tar -czf $BACKUP_DIR/files_$DATE.tar.gz /var/www/stockscanner /var/www/html

# Cleanup old backups (keep 7 days)
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete
```

Add to crontab: `0 2 * * * /usr/local/bin/stockscanner-backup.sh`

---

## Troubleshooting

### Common Issues

1. **Django won't start**
   ```bash
   sudo journalctl -u stockscanner -f
   sudo systemctl restart stockscanner
   ```

2. **WordPress can't connect to API**
   - Check CORS settings in Django
   - Verify API URL in WordPress settings
   - Check SSL certificates

3. **Database connection errors**
   ```bash
   sudo mysql -u django_user -p stockscanner_production
   ```

4. **Permission issues**
   ```bash
   sudo chown -R www-data:www-data /var/www/
   sudo chmod -R 755 /var/www/
   ```

5. **SSL certificate issues**
   ```bash
   sudo certbot renew --dry-run
   sudo systemctl reload nginx
   ```

### Performance Optimization

1. **Enable caching**
   - Install Redis for Django
   - Use WordPress caching plugins
   - Enable Nginx gzip compression

2. **Database optimization**
   ```sql
   OPTIMIZE TABLE stocks_stock;
   OPTIMIZE TABLE stocks_stockprice;
   ```

3. **Monitor resource usage**
   ```bash
   htop
   df -h
   free -h
   ```

---

## Security Checklist

- [ ] Strong passwords for all accounts
- [ ] SSH key authentication (disable password auth)
- [ ] Firewall configured and enabled
- [ ] SSL certificates installed and auto-renewing
- [ ] Regular security updates
- [ ] Backup system working
- [ ] Log monitoring in place
- [ ] Fail2ban configured (optional)
- [ ] Database users have minimal required permissions
- [ ] WordPress security plugins installed

---

## Maintenance Tasks

### Daily
- [ ] Check system status
- [ ] Monitor logs for errors
- [ ] Verify backups completed

### Weekly
- [ ] Update system packages
- [ ] Review security logs
- [ ] Test backup restoration
- [ ] Monitor disk usage

### Monthly
- [ ] Review SSL certificate expiration
- [ ] Update WordPress and plugins
- [ ] Database optimization
- [ ] Performance review

---

## Emergency Contacts

- **Domain Registrar**: [Your registrar support]
- **VPS Provider**: [Your VPS provider support]
- **SSL Provider**: [Let's Encrypt or your SSL provider]
- **Developer**: [Your contact information]

---

## Important URLs

- **WordPress Site**: https://yourdomain.com
- **WordPress Admin**: https://yourdomain.com/wp-admin
- **Django Admin**: https://api.yourdomain.com/admin-dashboard/
- **API Status**: https://api.yourdomain.com/api/admin/status/
- **Django Admin Panel**: https://api.yourdomain.com/admin/

---

## Notes

- Replace `yourdomain.com` with your actual domain
- Update all passwords and security keys
- Test thoroughly before going live
- Keep this checklist updated with any changes