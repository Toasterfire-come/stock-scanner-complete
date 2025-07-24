#!/bin/bash

# =========================================================================
# Quick MySQL User Fix - Creates database user and fixes permissions
# Run this BEFORE ultimate_migration_fix.sh
# =========================================================================

echo "🔧 Quick MySQL User Fix"

# Configuration
DB_NAME="stock_scanner_nasdaq"
DB_USER="stock_scanner"
DB_PASS="StockScanner2010"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

success() { echo -e "${GREEN}✅${NC} $1"; }
error() { echo -e "${RED}❌${NC} $1"; }
warning() { echo -e "${YELLOW}⚠️${NC} $1"; }
info() { echo -e "${BLUE}ℹ️${NC} $1"; }

# Find MySQL installation
echo "🔍 Finding MySQL installation..."

MYSQL_PATHS=(
    "/c/Program Files/MySQL/MySQL Server 8.0/bin"
    "/c/Program Files/MySQL/MySQL Server 8.4/bin"
    "/c/Program Files (x86)/MySQL/MySQL Server 8.0/bin"
    "/c/xampp/mysql/bin"
    "/c/Program Files/MySQL/MySQL Server 5.7/bin"
)

MYSQL_FOUND=""
for mysql_path in "${MYSQL_PATHS[@]}"; do
    if [[ -f "$mysql_path/mysql.exe" ]]; then
        MYSQL_FOUND="$mysql_path"
        export PATH="$mysql_path:$PATH"
        success "Found MySQL at: $mysql_path"
        break
    fi
done

if [[ -z "$MYSQL_FOUND" ]]; then
    warning "MySQL not found in common paths, searching..."
    MYSQL_SEARCH=$(find "/c/Program Files" -name "mysql.exe" 2>/dev/null | head -1)
    if [[ -n "$MYSQL_SEARCH" ]]; then
        MYSQL_FOUND=$(dirname "$MYSQL_SEARCH")
        export PATH="$MYSQL_FOUND:$PATH"
        success "Found MySQL at: $MYSQL_FOUND"
    else
        error "MySQL not found. Please install MySQL or add to PATH"
        echo ""
        echo "Install MySQL from: https://dev.mysql.com/downloads/mysql/"
        echo "Or add MySQL to your PATH environment variable"
        exit 1
    fi
fi

# Get MySQL root password from user
echo ""
echo -e "${BLUE}🔐 MySQL Root Password Required${NC}"
echo "Please enter your MySQL root password:"
read -s -p "MySQL root password: " MYSQL_ROOT_PASS
echo ""

# Test MySQL root connection
info "Testing MySQL root connection..."

if mysql -u root -p"$MYSQL_ROOT_PASS" -e "SELECT 1;" 2>/dev/null; then
    success "MySQL root connection successful"
else
    error "Cannot connect to MySQL as root"
    echo ""
    echo "Please check:"
    echo "  1. MySQL service is running: net start mysql"
    echo "  2. Root password is correct"
    echo "  3. MySQL is accessible"
    echo ""
    echo "Common solutions:"
    echo "  - Check if MySQL service is running: net start mysql"
    echo "  - Verify root password in MySQL Workbench"
    echo "  - Try connecting with: mysql -u root -p"
    echo ""
    echo "If you need to reset MySQL root password:"
    echo "  1. Stop MySQL: net stop mysql"
    echo "  2. Start with skip-grant-tables"
    echo "  3. Reset password and restart normally"
    exit 1
fi

# Create database and user
echo ""
info "Creating database '$DB_NAME' and user '$DB_USER'..."

mysql -u root -p"$MYSQL_ROOT_PASS" <<EOF
-- Drop existing user if exists (to reset permissions)
DROP USER IF EXISTS '$DB_USER'@'localhost';

-- Create database if not exists
CREATE DATABASE IF NOT EXISTS $DB_NAME CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Create user with password
CREATE USER '$DB_USER'@'localhost' IDENTIFIED BY '$DB_PASS';

-- Grant all privileges on the database
GRANT ALL PRIVILEGES ON $DB_NAME.* TO '$DB_USER'@'localhost';

-- Grant additional system privileges for migrations
GRANT CREATE, DROP, INDEX, ALTER, REFERENCES ON $DB_NAME.* TO '$DB_USER'@'localhost';

-- Grant SELECT on mysql.* for Django introspection
GRANT SELECT ON mysql.* TO '$DB_USER'@'localhost';

-- Flush privileges to apply changes
FLUSH PRIVILEGES;

-- Show user was created
SELECT User, Host FROM mysql.user WHERE User = '$DB_USER';

-- Show database exists
SHOW DATABASES LIKE '$DB_NAME';

-- Test user can access the database
EOF

if [[ $? -eq 0 ]]; then
    success "Database and user created successfully"
else
    error "Failed to create database and user"
    exit 1
fi

# Test application user connection
echo ""
info "Testing application user connection..."

if mysql -u "$DB_USER" -p"$DB_PASS" -e "USE $DB_NAME; SELECT 'Connection successful' AS test;" 2>/dev/null; then
    success "Application user can connect to database"
    
    # Show current database info
    mysql -u "$DB_USER" -p"$DB_PASS" "$DB_NAME" -e "
    SELECT 
        DATABASE() as current_database,
        USER() as current_user,
        @@version as mysql_version;
    "
else
    error "Application user cannot connect to database"
    echo ""
    echo "Debugging connection..."
    mysql -u root -p"$MYSQL_ROOT_PASS" -e "
    SHOW GRANTS FOR '$DB_USER'@'localhost';
    SELECT User, Host, authentication_string FROM mysql.user WHERE User = '$DB_USER';
    "
    exit 1
fi

# Update .env file
echo ""
info "Updating .env file with database configuration..."

cat > .env <<EOF
# Stock Scanner Configuration
DEBUG=false
SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(50))" 2>/dev/null || echo "temp-secret-key-$(date +%s)")

# Database Configuration (MySQL)
DATABASE_URL=mysql://$DB_USER:$DB_PASS@localhost:3306/$DB_NAME

# Security Settings
ALLOWED_HOSTS=localhost,127.0.0.1

# Stock Scanner Settings
NASDAQ_ONLY=true
USE_YFINANCE_ONLY=true

# Performance Settings
DB_CONN_MAX_AGE=300
DB_CONN_HEALTH_CHECKS=true

# Logging
LOG_LEVEL=INFO
LOG_FILE=$PWD/logs/stock_scanner.log
EOF

success ".env file updated with database configuration"

# Final summary
echo ""
echo -e "${GREEN}🎉 MySQL User Fix Complete!${NC}"
echo "==============================="
echo ""
echo -e "${BLUE}📊 Database Configuration:${NC}"
echo "   • Database: $DB_NAME"
echo "   • User: $DB_USER"
echo "   • Password: $DB_PASS"
echo "   • MySQL Root: [password provided]"
echo ""
echo -e "${GREEN}✅ Ready for migrations!${NC}"
echo ""
echo -e "${BLUE}🚀 Next steps:${NC}"
echo "   ./ultimate_migration_fix.sh"
echo "   python manage.py runserver"
echo ""

success "Database user setup complete!"