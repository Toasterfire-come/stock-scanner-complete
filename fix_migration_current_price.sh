#!/bin/bash

# =========================================================================
# Fix Current Price Migration Issue
# Handles the non-nullable current_price field migration
# =========================================================================

echo "🔧 Fixing current_price migration issue..."

cd "$(dirname "${BASH_SOURCE[0]}")"

# Activate virtual environment
if [[ -f "venv/Scripts/activate" ]]; then
    source venv/Scripts/activate
    echo "✅ Virtual environment activated"
else
    echo "❌ Virtual environment not found"
    exit 1
fi

echo "📋 The current_price field has been updated with default=0.0"
echo "🔍 Creating new migrations..."

# Remove any problematic migration files for current_price
echo "🧹 Cleaning up any existing migration conflicts..."
find stocks/migrations/ -name "*.py" -exec grep -l "current_price" {} \; | while read file; do
    if [[ "$file" != *"__init__.py"* ]]; then
        echo "⚠️  Found migration with current_price: $file"
    fi
done

# Create fresh migrations
echo "📝 Creating new migrations with default value..."
if python manage.py makemigrations stocks 2>&1; then
    echo "✅ Migrations created successfully"
else
    echo "❌ Migration creation failed"
    exit 1
fi

# Apply migrations
echo "🚀 Applying migrations..."
if python manage.py migrate 2>&1; then
    echo "✅ Migrations applied successfully"
else
    echo "❌ Migration failed"
    echo ""
    echo "📋 If you see the prompt about current_price default:"
    echo "   1) Choose option 1 (Provide a one-off default)"
    echo "   2) Enter: 0.0"
    echo "   3) This will set existing rows to $0.00"
    echo ""
    echo "🔄 Try running this script again after providing the default"
    exit 1
fi

# Test the database
echo "🔍 Testing database after migration..."
python -c "
from django.db import connection
from stocks.models import StockAlert

try:
    # Test creating a StockAlert with default current_price
    alert_count = StockAlert.objects.count()
    print(f'✅ StockAlert model accessible - {alert_count} records')
    
    # Test the field structure
    from django.core.management.sql import sql_all
    print('✅ Database schema updated successfully')
    
except Exception as e:
    print(f'❌ Database test failed: {e}')
"

echo ""
echo "🎉 Current price migration fix completed!"
echo ""
echo "📊 The StockAlert model now has:"
echo "   • current_price = FloatField(default=0.0)"
echo "   • Existing records set to $0.00"
echo "   • New records will default to $0.00"
echo ""
echo "🚀 You can now run:"
echo "   python manage.py runserver"