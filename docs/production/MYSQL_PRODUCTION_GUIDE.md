# MySQL Production Setup Guide - Linux

Complete guide for setting up MySQL with Stock Scanner on Linux systems.

## Quick Start

```bash
# Run the complete setup
./setup_linux_complete.sh
```

This single script handles everything automatically!

## Manual Setup (if needed)

### 1. Install MySQL

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install mysql-server mysql-client
```

**CentOS/RHEL/Fedora:**
```bash
# CentOS/RHEL
sudo yum install mysql-server mysql
# Fedora
sudo dnf install mysql-server mysql
```

### 2. Start MySQL Service

```bash
sudo systemctl start mysql
sudo systemctl enable mysql
```

### 3. Secure MySQL

```bash
sudo mysql_secure_installation
```

### 4. Create Database

```bash
mysql -u root -p
```

```sql
CREATE DATABASE stock_scanner_nasdaq CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'stock_scanner'@'localhost' IDENTIFIED BY 'StockScanner2024!';
GRANT ALL PRIVILEGES ON stock_scanner_nasdaq.* TO 'stock_scanner'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### 5. Install Python MySQL Driver

```bash
source venv/bin/activate
pip install mysqlclient>=2.2.0
```

### 6. Configure Django

Create `.env` file:
```env
DEBUG=false
DATABASE_URL=mysql://stock_scanner:StockScanner2024!@localhost:3307/stock_scanner_nasdaq
```

## Production Optimizations

### MySQL Configuration

Edit `/etc/mysql/mysql.conf.d/mysqld.cnf`:

```ini
[mysqld]
# Performance tuning
innodb_buffer_pool_size = 1G
innodb_log_file_size = 256M
max_connections = 200

# Character set
character-set-server = utf8mb4
collation-server = utf8mb4_unicode_ci

# Network
port = 3307

# Security
bind-address = 127.0.0.1
```

### Django Database Settings

The setup script automatically configures:

```python
DATABASES = {
'default': {
'ENGINE': 'django.db.backends.mysql',
'OPTIONS': {
'charset': 'utf8mb4',
'sql_mode': 'STRICT_TRANS_TABLES,NO_ZERO_DATE,NO_ZERO_IN_DATE,ERROR_FOR_DIVISION_BY_ZERO',
'isolation_level': 'READ COMMITTED',
'init_command': "SET foreign_key_checks = 0; SET sql_mode='STRICT_TRANS_TABLES'; SET foreign_key_checks = 1;",
},
'CONN_MAX_AGE': 300,
'CONN_HEALTH_CHECKS': True,
}
}
```

## Backup and Maintenance

### Automated Backup

The setup creates `setup/scripts/backup_database.sh`:

```bash
#!/bin/bash
BACKUP_DIR="./backups"
BACKUP_FILE="$BACKUP_DIR/nasdaq_db_$(date +%Y%m%d_%H%M%S).sql"

mkdir -p "$BACKUP_DIR"
mysqldump -u stock_scanner -pStockScanner2024! stock_scanner_nasdaq > "$BACKUP_FILE"
```

### Manual Backup

```bash
mysqldump -u stock_scanner -p stock_scanner_nasdaq > backup.sql
```

### Restore

```bash
mysql -u stock_scanner -p stock_scanner_nasdaq < backup.sql
```

## Monitoring

### Check Service Status

```bash
sudo systemctl status mysql
```

### Monitor Performance

```bash
mysql -u root -p -e "SHOW PROCESSLIST;"
mysql -u root -p -e "SHOW STATUS LIKE 'Threads_%';"
```

### Database Size

```bash
mysql -u root -p -e "
SELECT 
table_schema AS 'Database',
ROUND(SUM(data_length + index_length) / 1024 / 1024, 2) AS 'Size (MB)'
FROM information_schema.tables 
WHERE table_schema='stock_scanner_nasdaq'
GROUP BY table_schema;
"
```

## Troubleshooting

### Connection Issues

```bash
# Test connection
mysql -u stock_scanner -p stock_scanner_nasdaq -e "SELECT 1;"

# Check MySQL status
sudo systemctl status mysql

# View logs
sudo journalctl -u mysql
```

### Performance Issues

```bash
# Check slow queries
mysql -u root -p -e "SHOW VARIABLES LIKE 'slow_query_log%';"

# Enable slow query log
mysql -u root -p -e "SET GLOBAL slow_query_log = 'ON';"
```

### Disk Space

```bash
# Check MySQL data directory
sudo du -sh /var/lib/mysql/

# Clean binary logs
mysql -u root -p -e "PURGE BINARY LOGS BEFORE DATE(NOW() - INTERVAL 7 DAY);"
```

## Security

### User Management

```sql
-- Create read-only user
CREATE USER 'readonly'@'localhost' IDENTIFIED BY 'ReadOnlyPass2024!';
GRANT SELECT ON stock_scanner_nasdaq.* TO 'readonly'@'localhost';

-- Create backup user
CREATE USER 'backup'@'localhost' IDENTIFIED BY 'BackupPass2024!';
GRANT SELECT, LOCK TABLES ON stock_scanner_nasdaq.* TO 'backup'@'localhost';
```

### SSL Configuration

```bash
# Generate certificates
sudo mysql_ssl_rsa_setup --uid=mysql

# Enable SSL in MySQL config
echo "require_secure_transport = ON" >> /etc/mysql/mysql.conf.d/mysqld.cnf
```

## Complete Integration Test

```bash
# Test the complete stack
source venv/bin/activate
python manage.py check --deploy
python manage.py migrate
python manage.py load_nasdaq_only
python manage.py runserver
```

Visit: http://localhost:8000

## Support

- Setup logs: `setup.log`
- MySQL logs: `/var/log/mysql/error.log`
- Django logs: `logs/stock_scanner.log`