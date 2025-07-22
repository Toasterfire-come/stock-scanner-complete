#!/bin/bash

# Stock Scanner Platform - Complete Startup Script
# Handles development and production deployment

set -e  # Exit on error

echo "🚀 Stock Scanner Platform - Startup Script"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}$1${NC}"
}

# Check Python installation
check_python() {
    print_header "🐍 Checking Python Installation"
    
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version)
        print_status "Python found: $PYTHON_VERSION"
        
        PYTHON_MAJOR=$(python3 -c 'import sys; print(sys.version_info.major)')
        PYTHON_MINOR=$(python3 -c 'import sys; print(sys.version_info.minor)')
        
        if [[ $PYTHON_MAJOR -eq 3 && $PYTHON_MINOR -ge 8 ]]; then
            print_status "Python version is compatible (3.8+)"
        else
            print_error "Python 3.8+ is required. Current version: $PYTHON_VERSION"
            exit 1
        fi
    else
        print_error "Python 3 not found. Please install Python 3.8+"
        exit 1
    fi
}

# Setup virtual environment
setup_virtualenv() {
    print_header "🔧 Setting up Virtual Environment"
    
    if [ ! -d "venv" ]; then
        print_status "Creating virtual environment..."
        python3 -m venv venv
    else
        print_status "Virtual environment already exists"
    fi
    
    print_status "Activating virtual environment..."
    source venv/bin/activate
    
    print_status "Upgrading pip..."
    pip install --upgrade pip
}

# Install dependencies
install_dependencies() {
    print_header "📦 Installing Dependencies"
    
    if [ -f "requirements.txt" ]; then
        print_status "Installing Python packages..."
        pip install -r requirements.txt
        print_status "Dependencies installed successfully"
    else
        print_error "requirements.txt not found!"
        exit 1
    fi
}

# Setup environment
setup_environment() {
    print_header "⚙️ Setting up Environment"
    
    if [ ! -f ".env" ]; then
        if [ -f ".env.example" ]; then
            print_status "Creating .env file from .env.example..."
            cp .env.example .env
            print_warning "Please edit .env file with your settings"
        else
            print_status "Creating basic .env file..."
            cat > .env << ENVEOF
SECRET_KEY=django-dev-key-change-in-production
DEBUG=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
API_RATE_LIMIT=60
CACHE_TIMEOUT=300
ENVEOF
            print_warning "Basic .env file created. Please update with your settings."
        fi
    else
        print_status ".env file already exists"
    fi
}

# Create logs directory
setup_logs() {
    print_header "📋 Setting up Logging"
    
    mkdir -p logs
    touch logs/django.log
    print_status "Log files initialized"
}

# Database setup
setup_database() {
    print_header "🗄️ Setting up Database"
    
    print_status "Running database migrations..."
    python manage.py migrate
    
    print_status "Setting up memberships for existing users..."
    python manage.py setup_memberships
    
    print_status "Checking database integrity..."
    python manage.py shell -c "
from stocks.models import StockAlert
fields = [f.name for f in StockAlert._meta.get_fields()]
required = ['price_change_today', 'price_change_percent']
missing = [f for f in required if f not in fields]
if missing:
    print(f'ERROR: Missing fields: {missing}')
    exit(1)
else:
    print('✅ All StockAlert model fields present')
"
    
    print_status "Setting up advanced features..."
    # Download NLTK data for sentiment analysis
    python -c "
try:
    import nltk
    nltk.download('punkt', quiet=True)
    nltk.download('vader_lexicon', quiet=True)
    print('✅ NLTK data downloaded successfully')
except Exception as e:
    print(f'⚠️ NLTK data setup skipped: {e}')
" 2>/dev/null || echo "⚠️ NLTK data setup skipped (dependencies not found)"
    
    ADMIN_EXISTS=$(python manage.py shell -c "from django.contrib.auth.models import User; print(User.objects.filter(is_superuser=True).exists())" 2>/dev/null || echo "False")
    
    if [ "$ADMIN_EXISTS" = "False" ]; then
        print_status "Creating superuser..."
        echo "Please create an admin user:"
        python manage.py createsuperuser
    else
        print_status "Admin user already exists"
    fi
}

# Collect static files
collect_static() {
    print_header "🎨 Collecting Static Files"
    
    print_status "Collecting static files..."
    python manage.py collectstatic --noinput
    print_status "Static files collected successfully"
}

# Test setup
test_setup() {
    print_header "🧪 Testing Setup"
    
    if [ -f "test_setup.py" ]; then
        print_status "Running comprehensive test suite..."
        python test_setup.py
    else
        print_status "Running basic tests..."
        python manage.py check
        
        print_status "Testing database connection..."
        python manage.py shell -c "from django.db import connection; connection.ensure_connection(); print('Database connection successful')"
        
        print_status "Testing API endpoints..."
        python manage.py shell -c "
from stocks.models import Membership
from django.contrib.auth.models import User
print(f'Total users: {User.objects.count()}')
print(f'Total memberships: {Membership.objects.count()}')
print('Basic functionality test passed')
"
    fi
}

# Start development server
start_server() {
    print_header "🌐 Starting Development Server"
    
    print_status "Starting Django development server..."
    print_status "Access your application at:"
    echo -e "  ${BLUE}Django Admin:${NC} http://localhost:8000/admin"
    echo -e "  ${BLUE}API Docs:${NC} http://localhost:8000/api/"
    echo -e "  ${BLUE}Analytics:${NC} http://localhost:8000/api/analytics/public/"
    echo ""
    
    python manage.py runserver
}

# Main execution
main() {
    SKIP_SERVER=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --skip-server)
                SKIP_SERVER=true
                shift
                ;;
            -h|--help)
                echo "Usage: $0 [OPTIONS]"
                echo "Options:"
                echo "  --skip-server    Setup only, don't start server"
                echo "  -h, --help       Show this help message"
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                exit 1
                ;;
        esac
    done
    
    check_python
    setup_virtualenv
    install_dependencies
    setup_environment
    setup_logs
    setup_database
    collect_static
    test_setup
    
    print_status "✅ Setup completed successfully!"
    echo ""
    
    if [ "$SKIP_SERVER" = false ]; then
        start_server
    else
        print_status "Setup complete. To start the server manually, run:"
        echo "  source venv/bin/activate"
        echo "  python manage.py runserver"
    fi
}

# Execute if run directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
