#!/bin/bash
# Deployment script for the Optimized Stock Data Fetcher
# This script helps set up and test the optimized system

set -e  # Exit on any error

echo "🚀 Deploying Optimized Stock Data Fetcher"
echo "========================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check if we're in the right directory
if [ ! -f "manage.py" ]; then
    print_error "This script must be run from the Django project root directory"
    print_info "Please cd to testpath/stockscanner_django/ and run the script again"
    exit 1
fi

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
if (( $(echo "$python_version >= 3.8" | bc -l) )); then
    print_status "Python version: $python_version ✓"
else
    print_error "Python 3.8+ required. Current version: $python_version"
    exit 1
fi

# Install/upgrade pip
print_info "Upgrading pip..."
python3 -m pip install --upgrade pip

# Install optimized requirements
print_info "Installing optimized requirements..."
if [ -f "requirements_optimized.txt" ]; then
    pip install -r requirements_optimized.txt
    print_status "Optimized requirements installed"
else
    print_warning "requirements_optimized.txt not found, installing base requirements"
    pip install -r requirements.txt
    
    # Install essential optimized packages
    print_info "Installing essential optimization packages..."
    pip install aiohttp>=3.8.0 requests>=2.31.0 fake-useragent>=1.4.0 tenacity>=8.2.0
    print_status "Essential packages installed"
fi

# Check if Redis is available (optional)
print_info "Checking Redis availability..."
if command -v redis-cli &> /dev/null; then
    if redis-cli ping &> /dev/null; then
        print_status "Redis is running - caching will be optimized"
    else
        print_warning "Redis is installed but not running"
        print_info "Start Redis with: redis-server"
        print_info "Or install with: sudo apt-get install redis-server (Ubuntu) or brew install redis (macOS)"
    fi
else
    print_warning "Redis not found - will use basic caching"
    print_info "For better performance, install Redis:"
    print_info "  Ubuntu: sudo apt-get install redis-server"
    print_info "  macOS: brew install redis"
    print_info "  Docker: docker run -d -p 6379:6379 redis:alpine"
fi

# Check Django installation
print_info "Checking Django installation..."
python3 manage.py check --deploy 2>/dev/null && print_status "Django configuration OK" || print_warning "Django configuration has warnings"

# Run migrations
print_info "Running database migrations..."
python3 manage.py migrate

# Test the optimized system
print_info "Testing optimized stock data fetcher..."
if [ -f "test_optimized_fetcher.py" ]; then
    python3 test_optimized_fetcher.py --quick
    if [ $? -eq 0 ]; then
        print_status "Quick test passed!"
    else
        print_error "Quick test failed - check output above"
        exit 1
    fi
else
    print_warning "Test script not found, testing manually..."
    
    # Test imports manually
    python3 -c "
from stocks.management.commands.import_stock_data_optimized import Command
from stocks.config import RATE_LIMITS
print('✅ All imports successful')
print(f'✅ Rate limit: {RATE_LIMITS[\"requests_per_minute\"]}/min')
"
    print_status "Manual test passed!"
fi

# Check management command availability
print_info "Verifying management command..."
python3 manage.py help import_stock_data_optimized &> /dev/null && print_status "Optimized command available" || {
    print_error "Optimized command not found"
    exit 1
}

# Display configuration summary
echo ""
echo "📋 CONFIGURATION SUMMARY"
echo "========================"

# Check alternative API providers
python3 -c "
from stocks.alternative_apis import get_provider_status
import os

status = get_provider_status()
configured = [p for p, s in status.items() if s['configured']]

print(f'🔌 Alternative API providers: {len(configured)} configured')
if configured:
    for provider in configured:
        print(f'   ✅ {provider}')
else:
    print('   ⚠️  No alternative APIs configured')
    print('   💡 Set these environment variables for fallback support:')
    print('      - ALPHAVANTAGE_API_KEY')
    print('      - FINNHUB_API_KEY') 
    print('      - IEXCLOUD_API_KEY')
    print('      - POLYGON_API_KEY')
    print('      - TWELVEDATA_API_KEY')
"

# Check current stock count
stock_count=$(python3 -c "
import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stockscanner_django.settings')
django.setup()
from stocks.models import StockAlert
print(StockAlert.objects.count())
" 2>/dev/null || echo "0")

print_info "Current stocks in database: $stock_count"

# Check ticker file
if [ -f "../json/formatted_tickers.json" ]; then
    ticker_count=$(python3 -c "
import json
with open('../json/formatted_tickers.json', 'r') as f:
    data = json.load(f)
print(len(data.get('tickers', [])))
" 2>/dev/null || echo "0")
    print_info "Tickers to process: $ticker_count"
else
    print_warning "Ticker file not found at ../json/formatted_tickers.json"
fi

echo ""
echo "🎉 DEPLOYMENT COMPLETE!"
echo "======================="

echo ""
echo "📋 NEXT STEPS:"
echo "1. Test with a small batch:"
echo "   python3 manage.py import_stock_data_optimized --batch-size 10 --use-cache"
echo ""
echo "2. For regular use:"
echo "   python3 manage.py import_stock_data_optimized --use-cache"
echo ""
echo "3. For large deployments:"
echo "   python3 manage.py import_stock_data_optimized --batch-size 30 --max-workers 3 --use-cache --delay-range 1.5 3.5"
echo ""
echo "4. Get help:"
echo "   python3 manage.py import_stock_data_optimized --help"
echo ""

# Optional: run a test fetch
read -p "🧪 Would you like to run a test fetch with 5 tickers? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_info "Running test fetch..."
    python3 manage.py import_stock_data_optimized --batch-size 5 --max-workers 1 --use-cache --delay-range 2.0 3.0
    print_status "Test fetch completed!"
fi

echo ""
print_status "Optimized Stock Data Fetcher is ready to use!"
print_info "Check OPTIMIZED_STOCK_FETCHER_README.md for detailed documentation"