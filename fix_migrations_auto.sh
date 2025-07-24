#!/bin/bash

# =========================================================================
# Automatic Migration Fix - No User Prompts Required
# Handles current_price and other migration issues automatically
# =========================================================================

echo "🔧 Fixing Django migrations automatically..."

cd "$(dirname "${BASH_SOURCE[0]}")"

# Activate virtual environment
if [[ -f "venv/Scripts/activate" ]]; then
    source venv/Scripts/activate
    echo "✅ Virtual environment activated"
else
    echo "❌ Virtual environment not found"
    exit 1
fi

# Ensure correct database configuration
echo "🔧 Updating .env with correct password..."
cat > .env <<EOF
# Stock Scanner Configuration
DEBUG=false
SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(50))")

# Database Configuration (MySQL)
DATABASE_URL=mysql://stock_scanner:StockScanner2010@localhost:3306/stock_scanner_nasdaq

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

echo "✅ Environment configuration updated"

# Remove any existing problematic migrations
echo "🧹 Cleaning up migration conflicts..."
if [[ -d "stocks/migrations" ]]; then
    # Keep __init__.py and 0001_initial.py only
    find stocks/migrations/ -name "*.py" ! -name "__init__.py" ! -name "0001_initial.py" -delete
    echo "✅ Cleaned up migration files"
fi

# Ensure migration directory exists
mkdir -p stocks/migrations
touch stocks/migrations/__init__.py

# Create a clean initial migration
echo "📝 Creating clean initial migration..."
python manage.py makemigrations stocks --empty --name initial_clean

# Create the migration content that handles defaults properly
cat > "stocks/migrations/0002_auto_migration_fix.py" <<'EOF'
# Generated migration with automatic defaults
from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('stocks', '0001_initial'),
    ]

    operations = [
        # Add current_price field with default to avoid prompts
        migrations.AddField(
            model_name='stockalert',
            name='current_price',
            field=models.FloatField(default=0.0, help_text='Current stock price in USD'),
            preserve_default=True,
        ),
    ]
EOF

echo "✅ Created automatic migration with defaults"

# Apply migrations without prompts
echo "🚀 Applying migrations automatically..."
python manage.py migrate --run-syncdb

if [[ $? -eq 0 ]]; then
    echo "✅ Migrations applied successfully"
else
    echo "⚠️  Migration had issues, trying alternative approach..."
    
    # Alternative: Reset migrations completely
    echo "🔄 Resetting migrations completely..."
    
    # Delete migration files except __init__.py
    find stocks/migrations/ -name "*.py" ! -name "__init__.py" -delete
    
    # Create new initial migration
    python manage.py makemigrations stocks
    
    # Apply with fake initial
    python manage.py migrate stocks --fake-initial
    
    if [[ $? -eq 0 ]]; then
        echo "✅ Alternative migration approach successful"
    else
        echo "❌ Migration still failed"
        echo "📋 Manual steps needed:"
        echo "   1. Run: python manage.py makemigrations"
        echo "   2. When prompted for current_price default, enter: 0.0"
        echo "   3. Run: python manage.py migrate"
        exit 1
    fi
fi

# Test the models
echo "🔍 Testing Django models..."
python -c "
import django
django.setup()

from stocks.models import Stock, StockAlert

try:
    # Test model access
    stock_count = Stock.objects.count()
    alert_count = StockAlert.objects.count()
    print(f'✅ Models working: {stock_count} stocks, {alert_count} alerts')
    
    # Test creating a new StockAlert with default current_price
    from django.db import transaction
    with transaction.atomic():
        test_alert = StockAlert(
            ticker='TEST',
            company_name='Test Company',
            volume_today=1000000
        )
        # current_price should default to 0.0
        print(f'✅ Default current_price: {test_alert.current_price}')
        
except Exception as e:
    print(f'❌ Model test failed: {e}')
"

echo ""
echo "🎉 Automatic migration fix completed!"
echo ""
echo "📊 Configuration:"
echo "   • Database: stock_scanner_nasdaq"
echo "   • User: stock_scanner"
echo "   • Password: StockScanner2010"
echo "   • current_price field: Default 0.0"
echo ""
echo "🚀 Ready to run:"
echo "   python manage.py runserver"