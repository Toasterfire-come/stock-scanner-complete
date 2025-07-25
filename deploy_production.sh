#!/bin/bash

# Stock Scanner Production Deployment Script
# This script sets up the complete production environment

set -e  # Exit on any error

echo "🚀 Starting Stock Scanner Production Deployment..."
echo "================================================="

# Configuration
DOMAIN="yourdomain.com"
API_DOMAIN="api.yourdomain.com"
PROJECT_DIR="/var/www/stockscanner"
WP_DIR="/var/www/html"
DB_NAME="stockscanner_production"
WP_DB_NAME="wordpress_stockscanner"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   print_error "This script should not be run as root for security reasons"
   exit 1
fi

# Check if sudo is available
if ! command -v sudo &> /dev/null; then
    print_error "sudo is required but not installed"
    exit 1
fi

print_status "Updating system packages..."
sudo apt update && sudo apt upgrade -y

print_status "Installing required packages..."
sudo apt install -y nginx mysql-server php8.0-fpm php8.0-mysql php8.0-xml php8.0-curl php8.0-gd php8.0-mbstring php8.0-zip python3 python3-pip python3-venv git curl wget unzip

print_status "Installing Python packages..."
sudo pip3 install --upgrade pip
sudo pip3 install gunicorn

print_status "Creating project directory..."
sudo mkdir -p $PROJECT_DIR
sudo chown -R $USER:$USER $PROJECT_DIR

print_status "Setting up MySQL databases..."
sudo mysql -e "CREATE DATABASE IF NOT EXISTS $DB_NAME CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
sudo mysql -e "CREATE DATABASE IF NOT EXISTS $WP_DB_NAME CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
sudo mysql -e "CREATE USER IF NOT EXISTS 'django_user'@'localhost' IDENTIFIED BY 'django_secure_password';"
sudo mysql -e "CREATE USER IF NOT EXISTS 'wp_user'@'localhost' IDENTIFIED BY 'wp_secure_password';"
sudo mysql -e "GRANT ALL PRIVILEGES ON $DB_NAME.* TO 'django_user'@'localhost';"
sudo mysql -e "GRANT ALL PRIVILEGES ON $WP_DB_NAME.* TO 'wp_user'@'localhost';"
sudo mysql -e "FLUSH PRIVILEGES;"

print_status "Copying Django project..."
if [ -d "$PROJECT_DIR" ]; then
    sudo rm -rf $PROJECT_DIR/*
fi
sudo cp -r . $PROJECT_DIR/
sudo chown -R $USER:$USER $PROJECT_DIR

print_status "Setting up Python virtual environment..."
cd $PROJECT_DIR
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

print_status "Configuring Django settings..."
export DJANGO_SETTINGS_MODULE=stockscanner_django.settings_production
export DJANGO_SECRET_KEY=$(python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')
export DB_PASSWORD="django_secure_password"

print_status "Running Django migrations..."
python manage.py migrate
python manage.py collectstatic --noinput

print_status "Creating Django superuser..."
echo "Please create a Django admin user:"
python manage.py createsuperuser

print_status "Loading initial NASDAQ data..."
python manage.py load_nasdaq_only

print_status "Setting up WordPress..."
sudo mkdir -p $WP_DIR
cd /tmp
wget https://wordpress.org/latest.tar.gz
tar xzf latest.tar.gz
sudo cp -r wordpress/* $WP_DIR/
sudo rm -rf wordpress latest.tar.gz

print_status "Setting WordPress permissions..."
sudo chown -R www-data:www-data $WP_DIR
sudo chmod -R 755 $WP_DIR

print_status "Installing WordPress theme..."
sudo cp -r $PROJECT_DIR/wordpress_theme/stock-scanner-theme $WP_DIR/wp-content/themes/
sudo chown -R www-data:www-data $WP_DIR/wp-content/themes/stock-scanner-theme

print_status "Installing WordPress plugin..."
sudo mkdir -p $WP_DIR/wp-content/plugins
sudo cp -r $PROJECT_DIR/wordpress_plugin/stock-scanner-integration $WP_DIR/wp-content/plugins/
sudo chown -R www-data:www-data $WP_DIR/wp-content/plugins/stock-scanner-integration

print_status "Creating WordPress configuration..."
sudo tee $WP_DIR/wp-config.php > /dev/null <<EOF
<?php
define('DB_NAME', '$WP_DB_NAME');
define('DB_USER', 'wp_user');
define('DB_PASSWORD', 'wp_secure_password');
define('DB_HOST', 'localhost');
define('DB_CHARSET', 'utf8mb4');
define('DB_COLLATE', '');

define('AUTH_KEY',         '$(openssl rand -base64 32)');
define('SECURE_AUTH_KEY',  '$(openssl rand -base64 32)');
define('LOGGED_IN_KEY',    '$(openssl rand -base64 32)');
define('NONCE_KEY',        '$(openssl rand -base64 32)');
define('AUTH_SALT',        '$(openssl rand -base64 32)');
define('SECURE_AUTH_SALT', '$(openssl rand -base64 32)');
define('LOGGED_IN_SALT',   '$(openssl rand -base64 32)');
define('NONCE_SALT',       '$(openssl rand -base64 32)');

define('WP_HOME', 'https://$DOMAIN');
define('WP_SITEURL', 'https://$DOMAIN');

define('DJANGO_API_URL', 'https://$API_DOMAIN');
define('DJANGO_API_KEY', 'your-django-api-key');

define('DISALLOW_FILE_EDIT', true);
define('FORCE_SSL_ADMIN', true);
define('WP_AUTO_UPDATE_CORE', true);

\$table_prefix = 'wp_';
define('WP_DEBUG', false);

if (!defined('ABSPATH')) {
    define('ABSPATH', __DIR__ . '/');
}

require_once ABSPATH . 'wp-settings.php';
EOF

print_status "Configuring Nginx..."
sudo tee /etc/nginx/sites-available/stockscanner > /dev/null <<EOF
# WordPress site
server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name $DOMAIN www.$DOMAIN;
    
    # SSL configuration will be added by Certbot
    
    root $WP_DIR;
    index index.php index.html;
    
    location / {
        try_files \$uri \$uri/ /index.php?\$args;
    }
    
    location ~ \.php\$ {
        fastcgi_pass unix:/var/run/php/php8.0-fpm.sock;
        fastcgi_index index.php;
        fastcgi_param SCRIPT_FILENAME \$document_root\$fastcgi_script_name;
        include fastcgi_params;
    }
    
    location ~ /\.ht {
        deny all;
    }
}

# Django API
server {
    listen 80;
    server_name $API_DOMAIN;
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name $API_DOMAIN;
    
    # SSL configuration will be added by Certbot
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    location /static/ {
        alias $PROJECT_DIR/static/;
        expires 30d;
    }
}
EOF

print_status "Enabling Nginx site..."
sudo ln -sf /etc/nginx/sites-available/stockscanner /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t && sudo systemctl restart nginx

print_status "Creating systemd service for Django..."
sudo tee /etc/systemd/system/stockscanner.service > /dev/null <<EOF
[Unit]
Description=Stock Scanner Django App
After=network.target

[Service]
User=$USER
Group=$USER
WorkingDirectory=$PROJECT_DIR
Environment=DJANGO_SETTINGS_MODULE=stockscanner_django.settings_production
Environment=DJANGO_SECRET_KEY=$DJANGO_SECRET_KEY
Environment=DB_PASSWORD=django_secure_password
ExecStart=$PROJECT_DIR/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:8000 stockscanner_django.wsgi:application
Restart=always

[Install]
WantedBy=multi-user.target
EOF

print_status "Starting Django service..."
sudo systemctl daemon-reload
sudo systemctl enable stockscanner
sudo systemctl start stockscanner

print_status "Creating log directories..."
sudo mkdir -p /var/log/stockscanner
sudo chown $USER:$USER /var/log/stockscanner

print_status "Setting up SSL certificates..."
sudo apt install -y certbot python3-certbot-nginx
print_warning "Run the following command to get SSL certificates:"
echo "sudo certbot --nginx -d $DOMAIN -d www.$DOMAIN -d $API_DOMAIN"

print_status "Setting up firewall..."
sudo ufw --force enable
sudo ufw allow 22
sudo ufw allow 80
sudo ufw allow 443

print_status "Creating backup script..."
sudo tee /usr/local/bin/stockscanner-backup.sh > /dev/null <<'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups"

mkdir -p $BACKUP_DIR

# Database backups
mysqldump -u root stockscanner_production > $BACKUP_DIR/django_$DATE.sql
mysqldump -u root wordpress_stockscanner > $BACKUP_DIR/wordpress_$DATE.sql

# File backups
tar -czf $BACKUP_DIR/files_$DATE.tar.gz /var/www/stockscanner /var/www/html

# Keep only last 7 days
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete

echo "Backup completed: $DATE"
EOF

sudo chmod +x /usr/local/bin/stockscanner-backup.sh

print_status "Adding backup to crontab..."
(crontab -l 2>/dev/null; echo "0 2 * * * /usr/local/bin/stockscanner-backup.sh") | crontab -

print_status "Creating health check script..."
sudo tee /usr/local/bin/stockscanner-health.sh > /dev/null <<EOF
#!/bin/bash
# Check if services are running
systemctl is-active --quiet stockscanner || systemctl restart stockscanner
systemctl is-active --quiet nginx || systemctl restart nginx
systemctl is-active --quiet mysql || systemctl restart mysql

# Check API endpoint
curl -f https://$API_DOMAIN/api/admin/status/ > /dev/null 2>&1 || echo "API DOWN at \$(date)" >> /var/log/stockscanner/health.log
EOF

sudo chmod +x /usr/local/bin/stockscanner-health.sh

print_status "Adding health check to crontab..."
(crontab -l 2>/dev/null; echo "*/5 * * * * /usr/local/bin/stockscanner-health.sh") | crontab -

echo ""
echo "================================================="
print_status "✅ Production deployment completed!"
echo "================================================="
echo ""
echo "📋 Next Steps:"
echo "1. Run SSL certificate setup:"
echo "   sudo certbot --nginx -d $DOMAIN -d www.$DOMAIN -d $API_DOMAIN"
echo ""
echo "2. Update DNS records to point to this server:"
echo "   $DOMAIN -> $(curl -s ifconfig.me)"
echo "   $API_DOMAIN -> $(curl -s ifconfig.me)"
echo ""
echo "3. Complete WordPress setup:"
echo "   https://$DOMAIN/wp-admin/install.php"
echo ""
echo "4. Access admin dashboard:"
echo "   https://$API_DOMAIN/admin-dashboard/"
echo ""
echo "📊 System Status:"
echo "   Django: $(systemctl is-active stockscanner)"
echo "   Nginx: $(systemctl is-active nginx)"
echo "   MySQL: $(systemctl is-active mysql)"
echo ""
echo "📁 Important Files:"
echo "   Django: $PROJECT_DIR"
echo "   WordPress: $WP_DIR"
echo "   Logs: /var/log/stockscanner/"
echo "   Backups: /backups/"
echo ""
print_warning "Remember to:"
print_warning "- Change default passwords"
print_warning "- Update domain names in configuration files"
print_warning "- Set up monitoring and alerts"
print_warning "- Test all functionality before going live"