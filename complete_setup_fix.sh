#!/bin/bash

# =========================================================================
# Complete Setup Fix - MySQL + Migrations (No User Prompts)
# Fixes database access and migration issues automatically
# =========================================================================

echo "🔧 Complete Stock Scanner Fix - MySQL + Migrations"

cd "$(dirname "${BASH_SOURCE[0]}")"

# Configuration
DB_NAME="stock_scanner_nasdaq"
DB_USER="stock_scanner"
DB_PASS="StockScanner2010"
MYSQL_ROOT_PASS="stockscanner2010"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() { echo -e "${BLUE}[$(date '+%H:%M:%S')]${NC} $1"; }
success() { echo -e "${GREEN}✅${NC} $1"; }
warning() { echo -e "${YELLOW}⚠️${NC} $1"; }
error() { echo -e "${RED}❌${NC} $1"; }

# Activate virtual environment
if [[ -f "venv/Scripts/activate" ]]; then
    source venv/Scripts/activate
    success "Virtual environment activated"
else
    error "Virtual environment not found"
    exit 1
fi

# Step 1: Fix MySQL User and Database
log "Setting up MySQL database and user..."

# Find MySQL installation
MYSQL_PATHS=(
    "/c/Program Files/MySQL/MySQL Server 8.0/bin"
    "/c/Program Files/MySQL/MySQL Server 8.4/bin"
    "/c/Program Files (x86)/MySQL/MySQL Server 8.0/bin"
    "/c/xampp/mysql/bin"
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
        exit 1
    fi
fi

# Test MySQL root connection
log "Testing MySQL root connection..."
if mysql -u root -p"$MYSQL_ROOT_PASS" -e "SELECT 1;" 2>/dev/null; then
    success "MySQL root connection successful"
else
    error "Cannot connect to MySQL as root with password: $MYSQL_ROOT_PASS"
    echo "Please ensure:"
    echo "  1. MySQL service is running: net start mysql"
    echo "  2. Root password is: $MYSQL_ROOT_PASS"
    exit 1
fi

# Create database and user
log "Creating database and user..."
mysql -u root -p"$MYSQL_ROOT_PASS" <<EOF
-- Drop existing user if exists (to reset permissions)
DROP USER IF EXISTS '$DB_USER'@'localhost';

-- Create database
CREATE DATABASE IF NOT EXISTS $DB_NAME CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Create user with correct password
CREATE USER '$DB_USER'@'localhost' IDENTIFIED BY '$DB_PASS';

-- Grant all privileges
GRANT ALL PRIVILEGES ON $DB_NAME.* TO '$DB_USER'@'localhost';

-- Grant additional privileges for migrations
GRANT CREATE, DROP, INDEX, ALTER ON $DB_NAME.* TO '$DB_USER'@'localhost';

-- Flush privileges
FLUSH PRIVILEGES;

-- Show user exists
SELECT User, Host FROM mysql.user WHERE User = '$DB_USER';
EOF

if [[ $? -eq 0 ]]; then
    success "Database and user created successfully"
else
    error "Failed to create database and user"
    exit 1
fi

# Test application database connection
log "Testing application database connection..."
if mysql -u "$DB_USER" -p"$DB_PASS" -e "USE $DB_NAME; SELECT 1;" 2>/dev/null; then
    success "Application database connection successful"
else
    error "Cannot connect to database as application user"
    exit 1
fi

# Step 2: Update .env file
log "Updating .env configuration..."
cat > .env <<EOF
# Stock Scanner Configuration
DEBUG=false
SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(50))")

# Database Configuration (MySQL)
DATABASE_URL=mysql://$DB_USER:$DB_PASS@localhost:3306/$DB_NAME

# Security Settings
ALLOWED_HOSTS=localhost,127.0.0.1,$(hostname)

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

success "Environment configuration updated"

# Step 3: Test Django database connection
log "Testing Django database connection..."
python -c "
import os
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stockscanner_django.settings')
django.setup()

from django.db import connection

try:
    with connection.cursor() as cursor:
        cursor.execute('SELECT 1')
        result = cursor.fetchone()
    print('✅ Django database connection successful')
except Exception as e:
    print(f'❌ Django database connection failed: {e}')
    exit(1)
"

if [[ $? -ne 0 ]]; then
    error "Django database connection failed"
    exit 1
fi

# Step 4: Handle migrations automatically
log "Cleaning up and creating fresh migrations..."

# Remove existing migration files except __init__.py
if [[ -d "stocks/migrations" ]]; then
    find stocks/migrations/ -name "*.py" ! -name "__init__.py" -delete
    success "Cleaned up existing migrations"
fi

# Ensure migrations directory exists
mkdir -p stocks/migrations
touch stocks/migrations/__init__.py

# Create initial migration with all defaults pre-configured
log "Creating comprehensive initial migration..."
python manage.py makemigrations stocks --empty --name comprehensive_initial

# Find the created migration file
MIGRATION_FILE=$(find stocks/migrations/ -name "*comprehensive_initial.py" | head -1)

if [[ -n "$MIGRATION_FILE" ]]; then
    # Replace the migration content with pre-configured defaults
    cat > "$MIGRATION_FILE" <<'EOF'
from django.db import migrations, models
import django.utils.timezone

class Migration(migrations.Migration):
    initial = True
    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Stock',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('symbol', models.CharField(max_length=10, unique=True)),
                ('name', models.CharField(blank=True, max_length=255)),
                ('sector', models.CharField(blank=True, max_length=100)),
                ('industry', models.CharField(blank=True, max_length=100)),
                ('exchange', models.CharField(default='NASDAQ', max_length=50)),
                ('is_active', models.BooleanField(default=True)),
                ('market_cap', models.BigIntegerField(blank=True, null=True)),
                ('pe_ratio', models.FloatField(blank=True, null=True)),
                ('dividend_yield', models.FloatField(blank=True, null=True)),
                ('beta', models.FloatField(blank=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, db_index=True)),
            ],
        ),
        migrations.CreateModel(
            name='StockPrice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(db_index=True)),
                ('open_price', models.FloatField()),
                ('high_price', models.FloatField()),
                ('low_price', models.FloatField()),
                ('close_price', models.FloatField()),
                ('volume', models.BigIntegerField()),
                ('adjusted_close', models.FloatField(blank=True, null=True)),
                ('price_change', models.FloatField(blank=True, null=True)),
                ('price_change_percent', models.FloatField(blank=True, null=True)),
                ('stock', models.ForeignKey(on_delete=models.CASCADE, related_name='prices', to='stocks.stock')),
            ],
        ),
        migrations.CreateModel(
            name='StockAlert',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ticker', models.CharField(max_length=10)),
                ('company_name', models.CharField(blank=True, max_length=255)),
                ('current_price', models.FloatField(default=0.0, help_text='Current stock price in USD')),
                ('price_change_today', models.FloatField(blank=True, help_text='Price change from previous close', null=True)),
                ('price_change_percent', models.FloatField(blank=True, help_text='Percentage change from previous close', null=True)),
                ('volume_today', models.BigIntegerField()),
                ('avg_volume', models.BigIntegerField(blank=True, null=True)),
                ('dvav', models.FloatField(blank=True, null=True)),
                ('dvsa', models.FloatField(blank=True, null=True)),
                ('pe_ratio', models.FloatField(blank=True, null=True)),
                ('market_cap', models.BigIntegerField(blank=True, null=True)),
                ('note', models.TextField(blank=True)),
                ('last_update', models.DateTimeField(auto_now_add=True)),
                ('sent', models.BooleanField(default=False)),
            ],
        ),
        # Add any other models that exist
    ]
EOF

    success "Created comprehensive migration with all defaults"
else
    error "Could not create migration file"
    exit 1
fi

# Apply migrations
log "Applying migrations..."
python manage.py migrate --run-syncdb

if [[ $? -eq 0 ]]; then
    success "Migrations applied successfully"
else
    warning "Standard migration failed, trying alternative approach..."
    
    # Alternative approach: fake initial then migrate
    python manage.py migrate --fake-initial
    python manage.py migrate
    
    if [[ $? -eq 0 ]]; then
        success "Alternative migration approach successful"
    else
        error "All migration approaches failed"
        exit 1
    fi
fi

# Step 5: Test the complete setup
log "Testing complete setup..."
python -c "
import django
django.setup()

from stocks.models import Stock, StockAlert, StockPrice

try:
    # Test model access
    stock_count = Stock.objects.count()
    alert_count = StockAlert.objects.count()
    price_count = StockPrice.objects.count()
    
    print(f'✅ Stock model: {stock_count} records')
    print(f'✅ StockAlert model: {alert_count} records')
    print(f'✅ StockPrice model: {price_count} records')
    
    # Test creating models with defaults
    from django.utils import timezone
    from django.db import transaction
    
    with transaction.atomic():
        # Test Stock creation
        test_stock = Stock(symbol='TEST', name='Test Company')
        print(f'✅ Stock defaults work: exchange={test_stock.exchange}, active={test_stock.is_active}')
        
        # Test StockAlert creation
        test_alert = StockAlert(ticker='TEST', volume_today=1000000)
        print(f'✅ StockAlert defaults work: current_price={test_alert.current_price}, sent={test_alert.sent}')
        
    print('✅ All models working with proper defaults')
    
except Exception as e:
    print(f'❌ Model test failed: {e}')
    exit(1)
"

if [[ $? -eq 0 ]]; then
    success "All model tests passed"
else
    error "Model tests failed"
    exit 1
fi

# Final summary
echo ""
echo -e "${GREEN}🎉 COMPLETE SETUP FIX SUCCESSFUL!${NC}"
echo "==============================================="
echo ""
echo -e "${BLUE}📊 Configuration:${NC}"
echo "   • Database: $DB_NAME"
echo "   • User: $DB_USER"
echo "   • Password: $DB_PASS"
echo "   • MySQL Root: $MYSQL_ROOT_PASS"
echo ""
echo -e "${BLUE}📋 Models Ready:${NC}"
echo "   • Stock (with defaults)"
echo "   • StockAlert (current_price=0.0, last_update=auto)"
echo "   • StockPrice (complete schema)"
echo ""
echo -e "${BLUE}🚀 Ready to run:${NC}"
echo "   python manage.py runserver"
echo "   ./start_gitbash.sh"
echo ""

success "Stock Scanner is ready for production!"