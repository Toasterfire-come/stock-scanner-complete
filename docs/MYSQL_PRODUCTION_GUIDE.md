# MySQL Production Setup Guide

## 🚀 Complete MySQL Production Configuration for Stock Scanner

This guide covers the complete setup of MySQL as the production database for the Stock Scanner application on Windows.

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Setup](#quick-setup)
3. [Manual Setup](#manual-setup)
4. [Configuration Details](#configuration-details)
5. [Production Optimizations](#production-optimizations)
6. [Backup & Monitoring](#backup--monitoring)
7. [Troubleshooting](#troubleshooting)
8. [Security Best Practices](#security-best-practices)

---

## ✅ Prerequisites

### Required Software
- **Python 3.8+** with pip
- **MySQL Server 8.0+** ([Download](https://dev.mysql.com/downloads/mysql/))
- **Visual Studio Build Tools** (for mysqlclient compilation)
- **Git** for version control

### System Requirements
- **Windows 10/11**
- **4GB+ RAM** (8GB recommended for production)
- **20GB+ free disk space**
- **Administrator privileges** for service management

---

## 🚀 Quick Setup

### Option 1: Automated Setup (Recommended)
```cmd
# Clone and navigate to project
git clone https://github.com/Toasterfire-come/stock-scanner-complete.git
cd stock-scanner-complete

# Run comprehensive setup
setup.bat
# Choose option 2 (MySQL Production) when prompted
```

### Option 2: MySQL-Only Setup
```cmd
# If you already have the project set up
setup_mysql_windows.bat
```

---

## 🔧 Manual Setup

### Step 1: Install MySQL Server

1. **Download MySQL**: Go to [MySQL Downloads](https://dev.mysql.com/downloads/mysql/)
2. **Install with Custom Configuration**:
   - Choose **Server only** or **Custom** installation
   - Set root password: `StockScannerRoot2024!`
   - Enable **Start MySQL Server at System Startup**
   - Add MySQL to Windows PATH

### Step 2: Configure MySQL Service

```cmd
# Start MySQL service
net start mysql

# Or use specific version
net start mysql80
net start mysql84

# Check service status
sc query mysql
```

### Step 3: Create Production Database

```sql
-- Connect as root
mysql -u root -p

-- Create production database
CREATE DATABASE stock_scanner_production 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

-- Create production user
CREATE USER 'stock_scanner_prod'@'localhost' 
IDENTIFIED BY 'StockScannerProd2024!';

-- Grant privileges
GRANT ALL PRIVILEGES ON stock_scanner_production.* 
TO 'stock_scanner_prod'@'localhost';

GRANT CREATE, DROP, INDEX, ALTER ON stock_scanner_production.* 
TO 'stock_scanner_prod'@'localhost';

FLUSH PRIVILEGES;

-- Verify setup
SHOW DATABASES;
SELECT User, Host FROM mysql.user WHERE User = 'stock_scanner_prod';
```

### Step 4: Install Python MySQL Drivers

```cmd
# Activate virtual environment
venv\Scripts\activate.bat

# Install MySQL drivers (try in order)
pip install mysqlclient
# If fails, try:
pip install PyMySQL
# If both fail:
python install_windows_safe.py
```

### Step 5: Configure Environment

Create or update `.env` file:

```env
# MySQL Production Database
DATABASE_URL=mysql://stock_scanner_prod:StockScannerProd2024!@localhost:3306/stock_scanner_production
DB_ENGINE=django.db.backends.mysql
DB_NAME=stock_scanner_production
DB_USER=stock_scanner_prod
DB_PASSWORD=StockScannerProd2024!
DB_HOST=localhost
DB_PORT=3306

# Connection Pooling
DB_CONN_MAX_AGE=300
DB_CONN_HEALTH_CHECKS=true

# Production Settings
DEBUG=false
ALLOWED_HOSTS=localhost,127.0.0.1,yourdomain.com
SECRET_KEY=your-production-secret-key
```

### Step 6: Run Django Migrations

```cmd
# Make migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic --noinput

# Test Django
python manage.py runserver
```

---

## ⚙️ Configuration Details

### Django Settings Integration

The `stockscanner_django/settings.py` automatically detects MySQL when `DATABASE_URL` starts with `mysql://`:

```python
# MySQL production optimizations are applied automatically
DATABASES['default']['OPTIONS'] = {
    'charset': 'utf8mb4',
    'sql_mode': 'STRICT_TRANS_TABLES,NO_ZERO_DATE,NO_ZERO_IN_DATE,ERROR_FOR_DIVISION_BY_ZERO',
    'isolation_level': 'READ COMMITTED',
    'init_command': "SET foreign_key_checks = 0; SET sql_mode='STRICT_TRANS_TABLES'; SET foreign_key_checks = 1;",
}

# Connection pooling
DATABASES['default']['CONN_MAX_AGE'] = 300
DATABASES['default']['CONN_HEALTH_CHECKS'] = True
```

### MySQL Configuration Optimization

For production performance, consider updating `my.ini`:

```ini
[mysqld]
# Performance tuning for Stock Scanner
innodb_buffer_pool_size = 256M
max_connections = 100
query_cache_size = 32M
query_cache_type = 1

# Logging
slow_query_log = 1
slow_query_log_file = "slow-queries.log"
long_query_time = 2

# Character set
character-set-server = utf8mb4
collation-server = utf8mb4_unicode_ci

# Security
local_infile = 0
skip_show_database
```

---

## 🚀 Production Optimizations

### 1. Connection Pooling
```env
# Optimize connection reuse
DB_CONN_MAX_AGE=300          # Keep connections for 5 minutes
DB_CONN_HEALTH_CHECKS=true   # Check connection health
```

### 2. Index Optimization
```sql
-- Add indexes for common queries
CREATE INDEX idx_stock_symbol ON stocks_stock(symbol);
CREATE INDEX idx_stock_sector ON stocks_stock(sector);
CREATE INDEX idx_alert_user ON stocks_stockalert(user_id);
CREATE INDEX idx_alert_active ON stocks_stockalert(is_active);
```

### 3. Query Optimization
```sql
-- Analyze table performance
ANALYZE TABLE stocks_stock;
ANALYZE TABLE stocks_stockalert;

-- Check slow queries
SELECT * FROM INFORMATION_SCHEMA.PROCESSLIST 
WHERE TIME > 5;
```

### 4. Memory Configuration
```sql
-- Check current memory usage
SHOW VARIABLES LIKE 'innodb_buffer_pool_size';
SHOW STATUS LIKE 'Innodb_buffer_pool_pages_data';

-- Optimize for available RAM (example for 8GB system)
-- Set innodb_buffer_pool_size = 2G in my.ini
```

---

## 📊 Backup & Monitoring

### Automated Backup Script (`backup_database.bat`)

```cmd
@echo off
set BACKUP_DIR=backups
set TIMESTAMP=%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%

if not exist %BACKUP_DIR% mkdir %BACKUP_DIR%

mysqldump -u stock_scanner_prod -pStockScannerProd2024! ^
  stock_scanner_production > %BACKUP_DIR%\backup_%TIMESTAMP%.sql

echo Backup completed: %BACKUP_DIR%\backup_%TIMESTAMP%.sql
```

### Monitoring Script (`mysql_health_check.bat`)

```cmd
@echo off
echo MySQL Health Check
echo ==================

echo Service Status:
sc query mysql

echo Database Connection:
mysql -u stock_scanner_prod -pStockScannerProd2024! ^
  -e "SELECT 'Connection OK' as Status;" stock_scanner_production

echo Database Size:
mysql -u stock_scanner_prod -pStockScannerProd2024! ^
  -e "SELECT ROUND(SUM(data_length + index_length) / 1024 / 1024, 2) AS 'Size (MB)' 
      FROM information_schema.tables 
      WHERE table_schema = 'stock_scanner_production';" 

echo Table Count:
mysql -u stock_scanner_prod -pStockScannerProd2024! ^
  -e "SELECT COUNT(*) as 'Total Tables' 
      FROM information_schema.tables 
      WHERE table_schema = 'stock_scanner_production';"
```

### Django Management Commands

Use `django_mysql_manager.bat` for common tasks:

1. **Run Migrations** - Apply database schema changes
2. **Create Superuser** - Create admin account
3. **Start Django Server** - Launch the application
4. **Django Shell** - Interactive Python shell with Django
5. **Database Shell** - Direct MySQL command line
6. **Collect Static Files** - Gather static assets
7. **Test Django Settings** - Verify configuration

---

## 🛠️ Troubleshooting

### Common Issues

#### 1. "mysql command not found"
```cmd
# Add MySQL to PATH or use full path
"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe" --version
```

#### 2. "Access denied for user"
```cmd
# Reset root password
mysql -u root --skip-password
ALTER USER 'root'@'localhost' IDENTIFIED BY 'StockScannerRoot2024!';
FLUSH PRIVILEGES;
```

#### 3. "Can't connect to MySQL server"
```cmd
# Check if service is running
net start mysql

# Check port 3306 is available
netstat -an | findstr 3306
```

#### 4. "mysqlclient failed to install"
```cmd
# Install Visual Studio Build Tools
# Or use PyMySQL alternative
pip install PyMySQL
# Add to Django settings:
import pymysql
pymysql.install_as_MySQLdb()
```

#### 5. Django settings error
```cmd
# Fix environment configuration
python fix_django_settings_error.py
```

### Performance Issues

#### Slow Queries
```sql
-- Enable slow query log
SET GLOBAL slow_query_log = 'ON';
SET GLOBAL long_query_time = 1;

-- Check slow queries
SELECT * FROM mysql.slow_log ORDER BY start_time DESC LIMIT 10;
```

#### High Memory Usage
```sql
-- Check buffer pool usage
SHOW STATUS LIKE 'Innodb_buffer_pool_pages_%';

-- Optimize buffer pool size
-- Adjust innodb_buffer_pool_size in my.ini
```

### Database Connection Pool Issues
```cmd
# Reset connections
python manage.py shell
>>> from django.db import connection
>>> connection.close()

# Or restart Django server
```

---

## 🔐 Security Best Practices

### 1. Password Security
- Use strong passwords (minimum 16 characters)
- Change default passwords immediately
- Store passwords securely (use environment variables)
- Rotate passwords regularly

### 2. User Privileges
```sql
-- Create read-only user for reporting
CREATE USER 'stock_scanner_read'@'localhost' 
IDENTIFIED BY 'ReadOnlyPass2024!';

GRANT SELECT ON stock_scanner_production.* 
TO 'stock_scanner_read'@'localhost';

-- Limit production user privileges
REVOKE ALL ON *.* FROM 'stock_scanner_prod'@'localhost';
GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, DROP, INDEX, ALTER 
ON stock_scanner_production.* 
TO 'stock_scanner_prod'@'localhost';
```

### 3. Network Security
```sql
-- Bind to localhost only (in my.ini)
bind-address = 127.0.0.1

-- Disable remote root login
DELETE FROM mysql.user WHERE User='root' AND Host NOT IN ('localhost', '127.0.0.1', '::1');
FLUSH PRIVILEGES;
```

### 4. SSL/TLS Configuration
```sql
-- Check SSL status
SHOW VARIABLES LIKE 'have_ssl';

-- Enable SSL in my.ini
ssl-cert = /path/to/server-cert.pem
ssl-key = /path/to/server-key.pem
ssl-ca = /path/to/ca-cert.pem
```

### 5. Backup Security
- Encrypt backup files
- Store backups in secure location
- Test backup restoration regularly
- Implement backup retention policy

---

## 📈 Production Deployment Checklist

### Pre-Deployment
- [ ] MySQL Server installed and configured
- [ ] Production database and user created
- [ ] SSL certificates configured (if applicable)
- [ ] Firewall rules configured
- [ ] Backup strategy implemented

### Application Configuration
- [ ] `.env` file configured with production settings
- [ ] `DEBUG=false` in production
- [ ] `ALLOWED_HOSTS` configured correctly
- [ ] Static files configuration
- [ ] Error logging configured

### Security
- [ ] Strong passwords implemented
- [ ] User privileges minimized
- [ ] SSL/TLS enabled
- [ ] Network access restricted
- [ ] Regular security updates planned

### Monitoring
- [ ] Health check scripts installed
- [ ] Backup automation configured
- [ ] Performance monitoring enabled
- [ ] Log rotation configured
- [ ] Alert systems configured

### Performance
- [ ] MySQL configuration optimized
- [ ] Connection pooling enabled
- [ ] Database indexes created
- [ ] Query performance tested
- [ ] Resource monitoring enabled

---

## 📞 Support

### Useful Commands Reference

```cmd
# Service Management
net start mysql                    # Start MySQL service
net stop mysql                     # Stop MySQL service
net restart mysql                  # Restart MySQL service
sc query mysql                     # Check service status

# Database Management
mysql -u root -p                   # Connect as root
mysql -u stock_scanner_prod -p     # Connect as production user
mysqldump [options] database       # Backup database
mysql database < backup.sql       # Restore database

# Django Management
python manage.py migrate           # Apply migrations
python manage.py createsuperuser   # Create admin user
python manage.py dbshell           # Database shell
python manage.py runserver         # Start development server

# Health Checks
mysql_health_check.bat             # Database health check
backup_database.bat                # Manual backup
mysql_service_manager.bat          # Service management menu
django_mysql_manager.bat           # Django management menu
```

### Getting Help

1. **Check logs**: `logs/stock_scanner_production.log`
2. **Run health check**: `mysql_health_check.bat`
3. **Test Django settings**: `python fix_django_settings_error.py`
4. **Review configuration**: Check `.env` file
5. **Community support**: GitHub Issues

### Documentation Links

- [Official MySQL Documentation](https://dev.mysql.com/doc/)
- [Django Database Documentation](https://docs.djangoproject.com/en/stable/ref/databases/)
- [Stock Scanner GitHub Repository](https://github.com/Toasterfire-come/stock-scanner-complete/)

---

*This guide ensures a robust, secure, and performant MySQL production setup for the Stock Scanner application.*