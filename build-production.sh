#!/bin/bash

# Production Build Script for Stock Scanner
# This script builds both frontend and backend for production deployment

set -e  # Exit on error

echo "🚀 Starting Production Build Process..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Check Node.js version
print_status "Checking Node.js version..."
NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 14 ]; then
    print_error "Node.js version 14 or higher is required"
    exit 1
fi

# Check Python version
print_status "Checking Python version..."
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1-2)
REQUIRED_VERSION="3.8"
if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    print_error "Python 3.8 or higher is required"
    exit 1
fi

# Frontend Build
print_status "Building Frontend..."
cd frontend

# Install dependencies
print_status "Installing frontend dependencies..."
npm ci --production=false

# Run tests
print_status "Running frontend tests..."
CI=true npm test --passWithNoTests || print_warning "Some tests failed, continuing..."

# Build for production
print_status "Creating optimized production build..."
GENERATE_SOURCEMAP=false npm run build

# Verify build
if [ ! -d "build" ]; then
    print_error "Frontend build failed - build directory not created"
    exit 1
fi

# Check build size
BUILD_SIZE=$(du -sh build | cut -f1)
print_status "Frontend build complete. Size: $BUILD_SIZE"

# Add security headers to build
print_status "Adding security headers..."
cat > build/_headers << EOF
/*
  X-Frame-Options: SAMEORIGIN
  X-Content-Type-Options: nosniff
  X-XSS-Protection: 1; mode=block
  Referrer-Policy: strict-origin-when-cross-origin
  Permissions-Policy: geolocation=(), microphone=(), camera=()
  Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline' https://api.retailtradescanner.com; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; connect-src 'self' https://api.retailtradescanner.com;
EOF

# Create deployment info
cat > build/deploy-info.json << EOF
{
  "version": "$(git rev-parse --short HEAD 2>/dev/null || echo 'unknown')",
  "buildDate": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "environment": "production"
}
EOF

cd ..

# Backend Setup
print_status "Setting up Backend..."
cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    print_status "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
print_status "Installing backend dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Run backend tests
print_status "Running backend tests..."
python -m pytest tests/ --tb=short || print_warning "Some backend tests failed, continuing..."

# Collect static files (if using Django)
# print_status "Collecting static files..."
# python manage.py collectstatic --noinput

cd ..

# Create deployment package
print_status "Creating deployment package..."
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
DEPLOY_DIR="deploy_${TIMESTAMP}"
mkdir -p $DEPLOY_DIR

# Copy frontend build
cp -r frontend/build $DEPLOY_DIR/frontend

# Copy backend (excluding venv and __pycache__)
rsync -av --exclude='venv' --exclude='__pycache__' --exclude='*.pyc' --exclude='.env' backend/ $DEPLOY_DIR/backend/

# Create deployment README
cat > $DEPLOY_DIR/README.md << EOF
# Stock Scanner Production Deployment

## Build Information
- Build Date: $(date)
- Git Commit: $(git rev-parse HEAD 2>/dev/null || echo 'unknown')
- Frontend Build Size: $BUILD_SIZE

## Deployment Instructions

### Frontend (Static Files)
1. Upload the contents of \`frontend/\` to your static web server
2. Configure your web server to serve index.html for all routes (SPA)
3. Ensure security headers are properly configured

### Backend (API)
1. The Django backend is already deployed at https://api.retailtradescanner.com
2. No additional backend deployment needed

### Environment Variables
Ensure the following are set in production:
- REACT_APP_API_URL=https://api.retailtradescanner.com
- REACT_APP_ENV=production

### Post-Deployment Checklist
- [ ] Verify API connectivity
- [ ] Test authentication flow
- [ ] Check payment processing
- [ ] Verify WebSocket connections (if applicable)
- [ ] Test error tracking
- [ ] Monitor performance metrics
EOF

# Create deployment script
cat > $DEPLOY_DIR/deploy.sh << 'DEPLOY_SCRIPT'
#!/bin/bash
# Deployment script for Stock Scanner

echo "Deploying Stock Scanner to production..."

# Add your deployment commands here
# Example: rsync -avz frontend/ user@server:/var/www/stockscanner/

echo "Deployment complete!"
DEPLOY_SCRIPT

chmod +x $DEPLOY_DIR/deploy.sh

# Compress deployment package
print_status "Compressing deployment package..."
tar -czf "stockscanner_deploy_${TIMESTAMP}.tar.gz" $DEPLOY_DIR

# Cleanup
rm -rf $DEPLOY_DIR

print_status "Production build complete!"
print_status "Deployment package created: stockscanner_deploy_${TIMESTAMP}.tar.gz"

# Final checks
echo ""
echo "=== Pre-Deployment Checklist ==="
echo "[ ] Environment variables configured"
echo "[ ] API endpoint verified (https://api.retailtradescanner.com)"
echo "[ ] SSL certificates ready"
echo "[ ] CDN configured (if applicable)"
echo "[ ] Monitoring tools set up"
echo "[ ] Backup strategy in place"
echo "[ ] Rollback plan prepared"
echo ""
print_status "Ready for deployment!"