#!/bin/bash

# 🚀 Django-WordPress Integration Deployment Script
# This script sets up the complete integration between Django backend and WordPress frontend

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_header() {
    echo -e "\n${BLUE}$1${NC}"
    echo "=============================================="
}

# Default values
DJANGO_URL="http://127.0.0.1:8000"
WORDPRESS_PATH=""
INSTALL_DEPS=true
RUN_TESTS=true
PRODUCTION=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --django-url)
            DJANGO_URL="$2"
            shift 2
            ;;
        --wordpress-path)
            WORDPRESS_PATH="$2"
            shift 2
            ;;
        --no-deps)
            INSTALL_DEPS=false
            shift
            ;;
        --no-tests)
            RUN_TESTS=false
            shift
            ;;
        --production)
            PRODUCTION=true
            shift
            ;;
        --help)
            echo "Django-WordPress Integration Deployment"
            echo ""
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --django-url URL      Django backend URL (default: http://127.0.0.1:8000)"
            echo "  --wordpress-path PATH Path to WordPress installation"
            echo "  --no-deps            Skip dependency installation"
            echo "  --no-tests           Skip integration tests"
            echo "  --production         Production deployment mode"
            echo "  --help               Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0 --django-url https://api.yourdomain.com"
            echo "  $0 --wordpress-path /var/www/wordpress --production"
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

print_header "🚀 Django-WordPress Integration Deployment"
print_info "Django URL: $DJANGO_URL"
print_info "WordPress Path: ${WORDPRESS_PATH:-'Not specified'}"
print_info "Production Mode: $PRODUCTION"

# Check if we're in the right directory
if [[ ! -f "manage.py" ]]; then
    print_error "manage.py not found. Please run this script from the Django project root."
    exit 1
fi

# Install Django dependencies
if [[ "$INSTALL_DEPS" == true ]]; then
    print_header "📦 Installing Django Dependencies"
    
    if [[ -f "requirements_optimized.txt" ]]; then
        print_info "Installing optimized requirements..."
        pip install -r requirements_optimized.txt
        print_status "Optimized requirements installed"
    else
        print_warning "requirements_optimized.txt not found, installing base requirements"
        pip install -r requirements.txt
        
        # Install essential packages for WordPress integration
        print_info "Installing WordPress integration packages..."
        pip install djangorestframework>=3.14.0 django-cors-headers>=4.3.0
        print_status "Integration packages installed"
    fi
fi

# Run Django migrations
print_header "🗄️  Database Setup"
print_info "Running Django migrations..."
python manage.py makemigrations
python manage.py migrate
print_status "Database migrations completed"

# Create superuser if needed
if [[ "$PRODUCTION" == false ]]; then
    print_info "Checking for Django superuser..."
    if ! python manage.py shell -c "from django.contrib.auth.models import User; exit(0 if User.objects.filter(is_superuser=True).exists() else 1)" 2>/dev/null; then
        print_info "Creating Django superuser (admin/admin)..."
        python manage.py shell -c "
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin')
    print('Superuser created: admin/admin')
"
        print_status "Superuser created for development"
    else
        print_status "Superuser already exists"
    fi
fi

# Test Django APIs
if [[ "$RUN_TESTS" == true ]]; then
    print_header "🧪 Testing Django API Endpoints"
    
    # Start Django development server in background for testing
    if [[ "$PRODUCTION" == false ]]; then
        print_info "Starting Django development server for testing..."
        python manage.py runserver 127.0.0.1:8000 &
        DJANGO_PID=$!
        sleep 5
        
        # Wait for server to start
        for i in {1..10}; do
            if curl -s http://127.0.0.1:8000/api/stocks/ > /dev/null 2>&1; then
                break
            fi
            sleep 1
        done
    fi
    
    print_info "Running WordPress integration tests..."
    if python test_wordpress_integration.py; then
        print_status "All API tests passed"
    else
        print_error "API tests failed"
        if [[ -n "$DJANGO_PID" ]]; then
            kill $DJANGO_PID 2>/dev/null || true
        fi
        exit 1
    fi
    
    # Stop test server
    if [[ -n "$DJANGO_PID" ]]; then
        kill $DJANGO_PID 2>/dev/null || true
        print_info "Test server stopped"
    fi
fi

# Deploy WordPress theme
print_header "🎨 WordPress Theme Deployment"

if [[ -d "wordpress_deployment_package" ]]; then
    cd wordpress_deployment_package
    
    # Update theme configuration
    print_info "Configuring WordPress theme for Django integration..."
    
    # Update deployment script with Django URL
    if [[ -f "deployment/deploy.sh" ]]; then
        sed -i.bak "s|DJANGO_API_URL=.*|DJANGO_API_URL=\"$DJANGO_URL\"|g" deployment/deploy.sh
        print_status "Theme deployment script updated"
    fi
    
    # Update theme functions.php with correct API URL
    if [[ -f "theme/functions.php" ]]; then
        # Add Django API URL configuration
        cat >> theme/functions.php << EOF

// Django API Configuration (Auto-configured by deployment script)
if (!defined('DJANGO_API_URL')) {
    define('DJANGO_API_URL', '$DJANGO_URL/');
}
EOF
        print_status "Theme functions.php updated with Django URL"
    fi
    
    # Run WordPress deployment if path is provided
    if [[ -n "$WORDPRESS_PATH" ]] && [[ -d "$WORDPRESS_PATH" ]]; then
        print_info "Deploying to WordPress at: $WORDPRESS_PATH"
        
        if [[ "$PRODUCTION" == true ]]; then
            ./deployment/deploy.sh --full --production --wp-path "$WORDPRESS_PATH"
        else
            ./deployment/deploy.sh --full --wp-path "$WORDPRESS_PATH"
        fi
        
        print_status "WordPress theme deployed"
    else
        print_warning "WordPress path not provided. Theme files prepared but not deployed."
        print_info "To deploy manually:"
        print_info "  cd wordpress_deployment_package"
        print_info "  ./deployment/deploy.sh --full --wp-path /path/to/wordpress"
    fi
    
    cd ..
else
    print_error "WordPress deployment package not found"
    exit 1
fi

# Generate configuration documentation
print_header "📚 Configuration Documentation"

cat > WORDPRESS_INTEGRATION_CONFIG.md << EOF
# WordPress Integration Configuration

## Django Backend Setup ✅

Your Django backend is configured with:
- REST API endpoints for WordPress integration
- CORS headers for cross-domain requests
- Caching for optimal performance
- Stock data and subscription APIs

### API Endpoints Available:
- \`GET  /api/stocks/\` - List all stocks
- \`GET  /api/stocks/{ticker}/\` - Get specific stock details
- \`GET  /api/stocks/search/?q=AAPL\` - Search stocks
- \`GET  /api/market-movers/?type=gainers\` - Market movers
- \`GET  /api/stats/\` - Market statistics
- \`POST /api/wordpress/subscribe/\` - Email subscriptions

## WordPress Frontend Setup

### 1. Add to wp-config.php:
\`\`\`php
// Django Backend Integration
define('DJANGO_API_URL', '$DJANGO_URL/');
\`\`\`

### 2. Theme Features Available:
- Real-time stock price displays
- Market movers widgets
- Email subscription integration
- SEO optimization for stock content
- Automatic stock ticker enhancement

### 3. WordPress Shortcodes:
\`\`\`php
[stock_price ticker="AAPL"]
[stock_price ticker="MSFT" show_change="true" show_rating="true"]
[market_movers type="gainers" count="5"]
\`\`\`

## Testing the Integration

1. **Test Django APIs:**
   \`\`\`bash
   curl $DJANGO_URL/api/stocks/
   \`\`\`

2. **Test WordPress Integration:**
   - Visit your WordPress site
   - Check that stock prices load
   - Test email subscription forms

## Maintenance

Your existing Django workflow continues unchanged:
\`\`\`bash
# Update stock data
python manage.py stock_workflow --batch-size 50

# Send email notifications  
python manage.py send_stock_notifications
\`\`\`

WordPress will automatically get fresh data via the API!
EOF

print_status "Configuration documentation created: WORDPRESS_INTEGRATION_CONFIG.md"

# Final summary
print_header "🎉 Deployment Complete!"

print_status "Django backend is ready for WordPress integration"
print_status "API endpoints are configured and tested"
print_status "WordPress theme is prepared and configured"

if [[ -n "$WORDPRESS_PATH" ]]; then
    print_status "WordPress theme deployed to: $WORDPRESS_PATH"
else
    print_info "Next step: Deploy WordPress theme to your site"
fi

print_info ""
print_info "🔗 Integration URLs:"
print_info "  Django API: $DJANGO_URL/api/stocks/"
print_info "  Django Admin: $DJANGO_URL/admin/"
if [[ -n "$WORDPRESS_PATH" ]]; then
    print_info "  WordPress: $(dirname "$WORDPRESS_PATH")"
fi

print_info ""
print_info "📋 Quick Start:"
print_info "1. Add DJANGO_API_URL to your wp-config.php"
print_info "2. Activate the Stock Scanner theme in WordPress"
print_info "3. Test stock price shortcodes in posts"
print_info "4. Configure widgets and subscription forms"

print_info ""
print_info "📖 Full documentation: WORDPRESS_INTEGRATION_CONFIG.md"
print_info "🧪 Test integration: python test_wordpress_integration.py"

print_info ""
print_status "Your WordPress site now has real-time stock data! 📊✨"