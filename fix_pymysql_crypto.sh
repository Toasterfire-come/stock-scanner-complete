#!/bin/bash

# =========================================================================
# Quick Fix for PyMySQL Cryptography Error
# Installs cryptography package required for MySQL authentication
# =========================================================================

echo "🔧 Fixing PyMySQL cryptography requirement..."

cd "$(dirname "${BASH_SOURCE[0]}")"

# Check if virtual environment exists
if [[ -f "venv/Scripts/activate" ]]; then
    source venv/Scripts/activate
    echo "✅ Virtual environment activated"
else
    echo "❌ Virtual environment not found - please run setup first"
    exit 1
fi

# Install cryptography
echo "📦 Installing cryptography package..."
if pip install --no-cache-dir cryptography>=41.0.0; then
    echo "✅ Cryptography installed successfully"
else
    echo "❌ Failed to install cryptography"
    echo "Try running as Administrator or using:"
    echo "pip install --no-cache-dir --user cryptography>=41.0.0"
    exit 1
fi

# Test Django connection
echo "🔍 Testing Django database connection..."
if python manage.py check --database default 2>/dev/null; then
    echo "✅ Database connection test passed"
else
    echo "⚠️  Database connection still has issues"
    echo "Check your MySQL configuration:"
    echo "  - MySQL service running: net start mysql"
    echo "  - Root password: stockscanner2010"
    echo "  - Database exists: stock_scanner_nasdaq"
fi

# Test PyMySQL specifically
echo "🐍 Testing PyMySQL with cryptography..."
python -c "
import pymysql
try:
    pymysql.install_as_MySQLdb()
    print('✅ PyMySQL configured successfully')
    
    # Test connection with your credentials
    conn = pymysql.connect(
        host='localhost',
        user='stock_scanner',
        password='StockScanner2010',
        database='stock_scanner_nasdaq'
    )
    conn.close()
    print('✅ Database connection successful')
except Exception as e:
    print(f'⚠️  Connection issue: {e}')
    print('Check if MySQL database is properly configured')
"

echo ""
echo "🎉 Cryptography fix completed!"
echo ""
echo "🚀 Now try running Django commands:"
echo "   python manage.py makemigrations"
echo "   python manage.py migrate"
echo "   python manage.py runserver"