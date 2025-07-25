#!/bin/bash

# Stock Scanner Environment Setup Script
# This script helps configure environment variables for production deployment

set -e

echo "🔧 Stock Scanner Environment Setup"
echo "=================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Function to generate secure password
generate_password() {
    openssl rand -base64 32 | tr -d "=+/" | cut -c1-25
}

# Function to generate Django secret key
generate_django_secret() {
    python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())' 2>/dev/null || \
    openssl rand -base64 50 | tr -d "=+/" | cut -c1-50
}

# Check if .env already exists
if [ -f ".env" ]; then
    print_warning ".env file already exists!"
    read -p "Do you want to backup the existing .env file? (y/n): " backup_choice
    if [ "$backup_choice" = "y" ] || [ "$backup_choice" = "Y" ]; then
        cp .env ".env.backup.$(date +%Y%m%d_%H%M%S)"
        print_info "Backed up existing .env file"
    fi
    
    read -p "Do you want to overwrite the existing .env file? (y/n): " overwrite_choice
    if [ "$overwrite_choice" != "y" ] && [ "$overwrite_choice" != "Y" ]; then
        print_info "Exiting without changes"
        exit 0
    fi
fi

print_step "Starting environment configuration..."

# Copy template
if [ ! -f ".env.template" ]; then
    print_error ".env.template file not found!"
    exit 1
fi

cp .env.template .env
print_info "Created .env from template"

# Get domain information
print_step "Domain Configuration"
read -p "Enter your primary domain (e.g., yourdomain.com): " PRIMARY_DOMAIN
read -p "Enter your API subdomain (e.g., api.yourdomain.com): " API_DOMAIN

if [ -z "$PRIMARY_DOMAIN" ]; then
    print_error "Primary domain is required!"
    exit 1
fi

if [ -z "$API_DOMAIN" ]; then
    API_DOMAIN="api.$PRIMARY_DOMAIN"
    print_info "Using default API domain: $API_DOMAIN"
fi

# Generate secure passwords and keys
print_step "Generating secure credentials..."
DJANGO_SECRET=$(generate_django_secret)
DB_PASSWORD=$(generate_password)
WP_DB_PASSWORD=$(generate_password)
WP_ADMIN_PASSWORD=$(generate_password)
DJANGO_API_KEY=$(generate_password)

print_info "Generated secure credentials"

# Get admin email
print_step "Admin Configuration"
read -p "Enter admin email address: " ADMIN_EMAIL
if [ -z "$ADMIN_EMAIL" ]; then
    ADMIN_EMAIL="admin@$PRIMARY_DOMAIN"
    print_info "Using default admin email: $ADMIN_EMAIL"
fi

# Get organization info
print_step "Organization Information"
read -p "Enter your organization/company name: " ORG_NAME
read -p "Enter organization description: " ORG_DESC
read -p "Enter organization address (optional): " ORG_ADDRESS
read -p "Enter organization phone (optional): " ORG_PHONE

if [ -z "$ORG_NAME" ]; then
    ORG_NAME="Stock Scanner Pro"
fi

if [ -z "$ORG_DESC" ]; then
    ORG_DESC="Professional stock market analysis and trading tools platform"
fi

# Update .env file with actual values
print_step "Updating environment file..."

# Core Django settings
sed -i "s|DJANGO_SECRET_KEY=.*|DJANGO_SECRET_KEY=$DJANGO_SECRET|g" .env
sed -i "s|ALLOWED_HOSTS=.*|ALLOWED_HOSTS=$PRIMARY_DOMAIN,www.$PRIMARY_DOMAIN,$API_DOMAIN,127.0.0.1,localhost|g" .env

# Database passwords
sed -i "s|DB_PASSWORD=.*|DB_PASSWORD=$DB_PASSWORD|g" .env
sed -i "s|WP_DB_PASSWORD=.*|WP_DB_PASSWORD=$WP_DB_PASSWORD|g" .env

# WordPress integration
sed -i "s|WORDPRESS_URL=.*|WORDPRESS_URL=https://$PRIMARY_DOMAIN|g" .env
sed -i "s|WORDPRESS_API_URL=.*|WORDPRESS_API_URL=https://$PRIMARY_DOMAIN/wp-json/wp/v2|g" .env
sed -i "s|DJANGO_API_URL=.*|DJANGO_API_URL=https://$API_DOMAIN|g" .env
sed -i "s|DJANGO_API_KEY=.*|DJANGO_API_KEY=$DJANGO_API_KEY|g" .env
sed -i "s|WP_ADMIN_PASSWORD=.*|WP_ADMIN_PASSWORD=$WP_ADMIN_PASSWORD|g" .env
sed -i "s|WP_ADMIN_EMAIL=.*|WP_ADMIN_EMAIL=$ADMIN_EMAIL|g" .env

# Admin settings
sed -i "s|ADMIN_EMAIL=.*|ADMIN_EMAIL=$ADMIN_EMAIL|g" .env
sed -i "s|SUPPORT_EMAIL=.*|SUPPORT_EMAIL=support@$PRIMARY_DOMAIN|g" .env
sed -i "s|EMAIL_HOST_USER=.*|EMAIL_HOST_USER=noreply@$PRIMARY_DOMAIN|g" .env
sed -i "s|DEFAULT_FROM_EMAIL=.*|DEFAULT_FROM_EMAIL=Stock Scanner <noreply@$PRIMARY_DOMAIN>|g" .env

# CORS settings
sed -i "s|CORS_ALLOWED_ORIGINS=.*|CORS_ALLOWED_ORIGINS=https://$PRIMARY_DOMAIN,https://www.$PRIMARY_DOMAIN|g" .env

# Domain settings
sed -i "s|PRIMARY_DOMAIN=.*|PRIMARY_DOMAIN=$PRIMARY_DOMAIN|g" .env
sed -i "s|API_SUBDOMAIN=.*|API_SUBDOMAIN=$API_DOMAIN|g" .env

# Organization info
sed -i "s|ORGANIZATION_NAME=.*|ORGANIZATION_NAME=$ORG_NAME|g" .env
sed -i "s|ORGANIZATION_DESCRIPTION=.*|ORGANIZATION_DESCRIPTION=$ORG_DESC|g" .env
sed -i "s|ORGANIZATION_LOGO_URL=.*|ORGANIZATION_LOGO_URL=https://$PRIMARY_DOMAIN/images/logo.png|g" .env
sed -i "s|ORGANIZATION_EMAIL=.*|ORGANIZATION_EMAIL=contact@$PRIMARY_DOMAIN|g" .env

if [ ! -z "$ORG_ADDRESS" ]; then
    sed -i "s|ORGANIZATION_ADDRESS=.*|ORGANIZATION_ADDRESS=$ORG_ADDRESS|g" .env
fi

if [ ! -z "$ORG_PHONE" ]; then
    sed -i "s|ORGANIZATION_PHONE=.*|ORGANIZATION_PHONE=$ORG_PHONE|g" .env
fi

print_info "Environment file updated successfully"

# Optional: Set up additional services
print_step "Optional Service Configuration"

# Google Analytics
read -p "Enter Google Analytics ID (optional, e.g., GA-XXXXXXXXX-X): " GA_ID
if [ ! -z "$GA_ID" ]; then
    sed -i "s|GOOGLE_ANALYTICS_ID=.*|GOOGLE_ANALYTICS_ID=$GA_ID|g" .env
fi

# Google Tag Manager
read -p "Enter Google Tag Manager ID (optional, e.g., GTM-XXXXXXX): " GTM_ID
if [ ! -z "$GTM_ID" ]; then
    sed -i "s|GOOGLE_TAG_MANAGER_ID=.*|GOOGLE_TAG_MANAGER_ID=$GTM_ID|g" .env
fi

# Social media
read -p "Enter Twitter handle (optional, e.g., @yourhandle): " TWITTER_HANDLE
if [ ! -z "$TWITTER_HANDLE" ]; then
    sed -i "s|TWITTER_SITE=.*|TWITTER_SITE=$TWITTER_HANDLE|g" .env
fi

# Set secure file permissions
chmod 600 .env
print_info "Set secure permissions on .env file (600)"

# Create credentials summary
print_step "Creating credentials summary..."
cat > .env.summary << EOF
Stock Scanner Environment Setup Summary
======================================
Generated on: $(date)

Domain Configuration:
- Primary Domain: $PRIMARY_DOMAIN
- API Domain: $API_DOMAIN
- WordPress URL: https://$PRIMARY_DOMAIN
- Django API URL: https://$API_DOMAIN

Database Credentials:
- Django DB Password: $DB_PASSWORD
- WordPress DB Password: $WP_DB_PASSWORD

WordPress Admin:
- Username: admin
- Password: $WP_ADMIN_PASSWORD
- Email: $ADMIN_EMAIL

API Integration:
- Django API Key: $DJANGO_API_KEY

Organization:
- Name: $ORG_NAME
- Description: $ORG_DESC
EOF

if [ ! -z "$ORG_ADDRESS" ]; then
    echo "- Address: $ORG_ADDRESS" >> .env.summary
fi

if [ ! -z "$ORG_PHONE" ]; then
    echo "- Phone: $ORG_PHONE" >> .env.summary
fi

echo "" >> .env.summary
echo "IMPORTANT SECURITY NOTES:" >> .env.summary
echo "1. Keep this file secure and never commit to version control" >> .env.summary
echo "2. Use these credentials for your production setup" >> .env.summary
echo "3. Change default passwords after initial setup" >> .env.summary
echo "4. Enable 2FA where possible" >> .env.summary
echo "5. Regularly rotate passwords and API keys" >> .env.summary

chmod 600 .env.summary

echo ""
echo "=================================="
print_info "✅ Environment setup completed!"
echo "=================================="
echo ""
echo "📋 Next Steps:"
echo "1. Review the generated .env file"
echo "2. Check .env.summary for credentials"
echo "3. Run the production deployment script:"
echo "   ./deploy_production.sh"
echo ""
echo "📁 Files created:"
echo "   .env - Environment configuration"
echo "   .env.summary - Credentials summary"
echo ""
print_warning "SECURITY REMINDER:"
print_warning "- Never commit .env files to version control"
print_warning "- Store credentials securely"
print_warning "- Use strong passwords in production"
print_warning "- Enable SSL/HTTPS for all domains"
echo ""
print_info "Setup complete! Your Stock Scanner environment is ready for deployment."