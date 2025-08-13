#!/bin/bash

# Stock Scanner Pro - Web Server User Data Script
# This script sets up WordPress, PHP, and all necessary components

set -e

# Variables passed from Terraform
DB_ENDPOINT="${db_endpoint}"
CACHE_ENDPOINT="${cache_endpoint}"

# System Configuration
LOG_FILE="/var/log/user-data.log"
exec > >(tee -a $LOG_FILE)
exec 2>&1

echo "=== Stock Scanner Pro Web Server Setup Started: $(date) ==="

# Update system
echo "Updating system packages..."
yum update -y

# Install required packages
echo "Installing required packages..."
yum install -y \
    httpd \
    php \
    php-mysqlnd \
    php-gd \
    php-xml \
    php-mbstring \
    php-json \
    php-curl \
    php-zip \
    php-intl \
    php-redis \
    mariadb \
    wget \
    unzip \
    git \
    nodejs \
    npm \
    amazon-cloudwatch-agent

# Install PHP 8.1 (more recent version)
echo "Installing PHP 8.1..."
amazon-linux-extras install -y php8.1

# Start and enable Apache
echo "Starting and enabling Apache..."
systemctl start httpd
systemctl enable httpd

# Configure PHP
echo "Configuring PHP..."
PHP_INI="/etc/php.ini"
sed -i 's/memory_limit = 128M/memory_limit = 256M/' $PHP_INI
sed -i 's/upload_max_filesize = 2M/upload_max_filesize = 64M/' $PHP_INI
sed -i 's/post_max_size = 8M/post_max_size = 64M/' $PHP_INI
sed -i 's/max_execution_time = 30/max_execution_time = 300/' $PHP_INI
sed -i 's/max_input_time = 60/max_input_time = 300/' $PHP_INI

# Download and install WordPress
echo "Downloading and installing WordPress..."
cd /tmp
wget https://wordpress.org/latest.tar.gz
tar xzf latest.tar.gz
cp -R wordpress/* /var/www/html/
chown -R apache:apache /var/www/html
chmod -R 755 /var/www/html

# Create WordPress configuration
echo "Creating WordPress configuration..."
cd /var/www/html
cp wp-config-sample.php wp-config.php

# Extract database info
DB_HOST=$(echo $DB_ENDPOINT | cut -d: -f1)
DB_PORT=$(echo $DB_ENDPOINT | cut -d: -f2)

# Configure WordPress database connection
sed -i "s/database_name_here/stockscanner/" wp-config.php
sed -i "s/username_here/admin/" wp-config.php
sed -i "s/password_here/ChangeMe123!/" wp-config.php
sed -i "s/localhost/$DB_HOST/" wp-config.php

# Add Redis configuration
cat >> wp-config.php << 'EOF'

// Redis Cache Configuration
define('WP_REDIS_HOST', '${cache_endpoint}');
define('WP_REDIS_PORT', 6379);
define('WP_REDIS_TIMEOUT', 1);
define('WP_REDIS_READ_TIMEOUT', 1);
define('WP_REDIS_DATABASE', 0);

// WordPress Security Keys
define('AUTH_KEY',         'put your unique phrase here');
define('SECURE_AUTH_KEY',  'put your unique phrase here');
define('LOGGED_IN_KEY',    'put your unique phrase here');
define('NONCE_KEY',        'put your unique phrase here');
define('AUTH_SALT',        'put your unique phrase here');
define('SECURE_AUTH_SALT', 'put your unique phrase here');
define('LOGGED_IN_SALT',   'put your unique phrase here');
define('NONCE_SALT',       'put your unique phrase here');

// WordPress Performance
define('WP_CACHE', true);
define('AUTOMATIC_UPDATER_DISABLED', true);
define('WP_POST_REVISIONS', 3);
define('AUTOSAVE_INTERVAL', 300);

// WordPress Memory
define('WP_MEMORY_LIMIT', '256M');
define('WP_MAX_MEMORY_LIMIT', '512M');

// WordPress Debugging (disable in production)
define('WP_DEBUG', false);
define('WP_DEBUG_LOG', false);
define('WP_DEBUG_DISPLAY', false);

EOF

# Install WordPress CLI
echo "Installing WordPress CLI..."
curl -O https://raw.githubusercontent.com/wp-cli/wp-cli/master/utils/wp-cli-bash
chmod +x wp-cli-bash
mv wp-cli-bash /usr/local/bin/wp

# Create WordPress database tables (wait for DB to be ready)
echo "Waiting for database to be ready..."
while ! mysqladmin ping -h $DB_HOST -u admin -pChangeMe123! --silent; do
    echo "Waiting for database connection..."
    sleep 10
done

# Install WordPress core
echo "Installing WordPress core..."
cd /var/www/html
sudo -u apache wp core install \
    --url="http://localhost" \
    --title="Stock Scanner Pro" \
    --admin_user="admin" \
    --admin_password="admin123" \
    --admin_email="admin@stockscannerpro.com" \
    --skip-email

# Install and activate Redis plugin
echo "Installing Redis object cache plugin..."
sudo -u apache wp plugin install redis-cache --activate

# Configure Apache Virtual Host
echo "Configuring Apache Virtual Host..."
cat > /etc/httpd/conf.d/stockscanner.conf << 'EOF'
<VirtualHost *:80>
    DocumentRoot /var/www/html
    ServerName stockscannerpro.com
    
    <Directory /var/www/html>
        AllowOverride All
        Require all granted
    </Directory>
    
    # Enable mod_rewrite
    RewriteEngine On
    
    # Health check endpoint
    RewriteRule ^/health$ /health.php [L]
    
    # Security headers
    Header always set X-Content-Type-Options nosniff
    Header always set X-Frame-Options DENY
    Header always set X-XSS-Protection "1; mode=block"
    Header always set Strict-Transport-Security "max-age=63072000; includeSubDomains; preload"
    Header always set Referrer-Policy "strict-origin-when-cross-origin"
    
    # Compression
    LoadModule deflate_module modules/mod_deflate.so
    <Location />
        SetOutputFilter DEFLATE
        SetEnvIfNoCase Request_URI \
            \.(?:gif|jpe?g|png)$ no-gzip dont-vary
        SetEnvIfNoCase Request_URI \
            \.(?:exe|t?gz|zip|bz2|sit|rar)$ no-gzip dont-vary
    </Location>
    
    # Caching
    ExpiresActive On
    ExpiresByType text/css "access plus 1 month"
    ExpiresByType application/javascript "access plus 1 month"
    ExpiresByType image/png "access plus 1 month"
    ExpiresByType image/jpg "access plus 1 month"
    ExpiresByType image/jpeg "access plus 1 month"
    ExpiresByType image/gif "access plus 1 month"
    ExpiresByType image/ico "access plus 1 month"
    ExpiresByType image/icon "access plus 1 month"
    ExpiresByType text/html "access plus 5 minutes"
    
    LogLevel warn
    ErrorLog /var/log/httpd/stockscanner_error.log
    CustomLog /var/log/httpd/stockscanner_access.log combined
</VirtualHost>
EOF

# Create health check endpoint
echo "Creating health check endpoint..."
cat > /var/www/html/health.php << 'EOF'
<?php
header('Content-Type: application/json');

$health = array(
    'status' => 'healthy',
    'timestamp' => date('c'),
    'version' => '1.0.0',
    'checks' => array()
);

// Check database connection
try {
    $db_host = DB_HOST;
    $db_user = DB_USER;
    $db_pass = DB_PASSWORD;
    $db_name = DB_NAME;
    
    $pdo = new PDO("mysql:host=$db_host;dbname=$db_name", $db_user, $db_pass);
    $health['checks']['database'] = 'healthy';
} catch (Exception $e) {
    $health['checks']['database'] = 'unhealthy';
    $health['status'] = 'unhealthy';
}

// Check Redis connection
try {
    if (class_exists('Redis')) {
        $redis = new Redis();
        $redis->connect(WP_REDIS_HOST, WP_REDIS_PORT);
        $redis->ping();
        $health['checks']['cache'] = 'healthy';
        $redis->close();
    } else {
        $health['checks']['cache'] = 'unavailable';
    }
} catch (Exception $e) {
    $health['checks']['cache'] = 'unhealthy';
}

// Check file system
$health['checks']['filesystem'] = is_writable('/var/www/html/wp-content') ? 'healthy' : 'unhealthy';

// Check memory usage
$memory_usage = memory_get_usage(true);
$memory_limit = ini_get('memory_limit');
$health['checks']['memory'] = array(
    'usage' => $memory_usage,
    'limit' => $memory_limit,
    'status' => $memory_usage < (0.8 * $memory_limit) ? 'healthy' : 'warning'
);

http_response_code($health['status'] === 'healthy' ? 200 : 503);
echo json_encode($health);
?>
EOF

# Enable Apache modules
echo "Enabling Apache modules..."
echo "LoadModule rewrite_module modules/mod_rewrite.so" >> /etc/httpd/conf/httpd.conf
echo "LoadModule headers_module modules/mod_headers.so" >> /etc/httpd/conf/httpd.conf
echo "LoadModule expires_module modules/mod_expires.so" >> /etc/httpd/conf/httpd.conf

# Configure log rotation
echo "Configuring log rotation..."
cat > /etc/logrotate.d/stockscanner << 'EOF'
/var/log/httpd/stockscanner_*.log {
    daily
    rotate 14
    compress
    delaycompress
    missingok
    notifempty
    sharedscripts
    postrotate
        /bin/systemctl reload httpd.service > /dev/null 2>/dev/null || true
    endscript
}
EOF

# Install and configure CloudWatch agent
echo "Configuring CloudWatch agent..."
cat > /opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json << 'EOF'
{
    "metrics": {
        "namespace": "StockScannerPro/WebServer",
        "metrics_collected": {
            "cpu": {
                "measurement": [
                    "cpu_usage_idle",
                    "cpu_usage_iowait",
                    "cpu_usage_user",
                    "cpu_usage_system"
                ],
                "metrics_collection_interval": 60
            },
            "disk": {
                "measurement": [
                    "used_percent"
                ],
                "metrics_collection_interval": 60,
                "resources": [
                    "*"
                ]
            },
            "mem": {
                "measurement": [
                    "mem_used_percent"
                ],
                "metrics_collection_interval": 60
            }
        }
    },
    "logs": {
        "logs_collected": {
            "files": {
                "collect_list": [
                    {
                        "file_path": "/var/log/httpd/access_log",
                        "log_group_name": "/aws/ec2/stockscanner/apache/access",
                        "log_stream_name": "{instance_id}/access.log"
                    },
                    {
                        "file_path": "/var/log/httpd/error_log",
                        "log_group_name": "/aws/ec2/stockscanner/apache/error",
                        "log_stream_name": "{instance_id}/error.log"
                    },
                    {
                        "file_path": "/var/log/user-data.log",
                        "log_group_name": "/aws/ec2/stockscanner/user-data",
                        "log_stream_name": "{instance_id}/user-data.log"
                    }
                ]
            }
        }
    }
}
EOF

# Start CloudWatch agent
/opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl \
    -a fetch-config \
    -m ec2 \
    -c file:/opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json \
    -s

# Create system service for application monitoring
echo "Creating application monitoring service..."
cat > /etc/systemd/system/stockscanner-monitor.service << 'EOF'
[Unit]
Description=Stock Scanner Pro Monitoring Service
After=network.target

[Service]
Type=simple
User=apache
ExecStart=/usr/local/bin/stockscanner-monitor.sh
Restart=always
RestartSec=30

[Install]
WantedBy=multi-user.target
EOF

# Create monitoring script
cat > /usr/local/bin/stockscanner-monitor.sh << 'EOF'
#!/bin/bash

while true; do
    # Check if Apache is running
    if ! systemctl is-active --quiet httpd; then
        echo "Apache is not running, attempting to restart..."
        systemctl restart httpd
    fi
    
    # Check disk space
    DISK_USAGE=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')
    if [ $DISK_USAGE -gt 85 ]; then
        echo "Disk usage is high: ${DISK_USAGE}%"
        # Clean up old logs
        find /var/log -name "*.log" -mtime +7 -delete
    fi
    
    # Check memory usage
    MEMORY_USAGE=$(free | grep Mem | awk '{printf "%.0f", $3/$2 * 100.0}')
    if [ $MEMORY_USAGE -gt 90 ]; then
        echo "Memory usage is high: ${MEMORY_USAGE}%"
        # Restart Apache if memory is critically high
        if [ $MEMORY_USAGE -gt 95 ]; then
            systemctl restart httpd
        fi
    fi
    
    sleep 60
done
EOF

chmod +x /usr/local/bin/stockscanner-monitor.sh
systemctl enable stockscanner-monitor.service
systemctl start stockscanner-monitor.service

# Set up automatic security updates
echo "Configuring automatic security updates..."
yum install -y yum-cron
sed -i 's/update_cmd = default/update_cmd = security/' /etc/yum/yum-cron.conf
sed -i 's/apply_updates = no/apply_updates = yes/' /etc/yum/yum-cron.conf
systemctl enable yum-cron
systemctl start yum-cron

# Configure firewall (minimal since we're behind ALB)
echo "Configuring firewall..."
systemctl start firewalld
systemctl enable firewalld
firewall-cmd --permanent --add-service=http
firewall-cmd --permanent --add-service=https
firewall-cmd --permanent --add-service=ssh
firewall-cmd --reload

# Restart Apache to apply all configurations
echo "Restarting Apache..."
systemctl restart httpd

# Verify services are running
echo "Verifying services..."
systemctl status httpd
systemctl status amazon-cloudwatch-agent
systemctl status stockscanner-monitor

# Final permissions check
chown -R apache:apache /var/www/html
chmod -R 755 /var/www/html
chmod 644 /var/www/html/wp-config.php

# Create deployment marker
echo "Creating deployment marker..."
echo "Deployment completed at: $(date)" > /var/www/html/deployment.txt
echo "Instance ID: $(curl -s http://169.254.169.254/latest/meta-data/instance-id)" >> /var/www/html/deployment.txt
echo "Instance Type: $(curl -s http://169.254.169.254/latest/meta-data/instance-type)" >> /var/www/html/deployment.txt
echo "Availability Zone: $(curl -s http://169.254.169.254/latest/meta-data/placement/availability-zone)" >> /var/www/html/deployment.txt

echo "=== Stock Scanner Pro Web Server Setup Completed: $(date) ==="
echo "=== Server is ready to serve traffic ==="