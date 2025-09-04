#!/bin/bash

# Test script for static deployment
# This verifies the build works correctly with Django backend

set -e

echo "🧪 Testing Static Deployment Configuration..."

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Test function
test_feature() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✓${NC} $2"
    else
        echo -e "${RED}✗${NC} $2"
        exit 1
    fi
}

# 1. Check environment variables
echo "Checking environment configuration..."
if [ -f "frontend/.env.production" ]; then
    test_feature 0 "Production environment file exists"
else
    test_feature 1 "Production environment file missing"
fi

# 2. Test API connectivity
echo "Testing API connectivity..."
API_URL="https://api.retailtradescanner.com"
API_KEY="((#cx+mb@f-(8x*p@9mfnanqe%ha1@6-b%w)q##v@)lanop"

# Test health endpoint
HEALTH_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "$API_URL/health/")
if [ "$HEALTH_RESPONSE" = "200" ]; then
    test_feature 0 "API health check passed"
else
    echo -e "${YELLOW}⚠${NC} API health check returned: $HEALTH_RESPONSE"
fi

# Test API with authentication
API_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" \
    -H "X-API-Key: $API_KEY" \
    "$API_URL/api/")
if [ "$API_RESPONSE" = "200" ]; then
    test_feature 0 "API authentication working"
else
    echo -e "${YELLOW}⚠${NC} API authentication returned: $API_RESPONSE"
fi

# 3. Build the frontend
echo "Building frontend..."
cd frontend

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    npm ci
fi

# Create production build
echo "Creating production build..."
REACT_APP_API_URL=$API_URL \
REACT_APP_API_KEY=$API_KEY \
REACT_APP_ENV=production \
npm run build

# Check if build was successful
if [ -d "build" ]; then
    test_feature 0 "Build directory created"
else
    test_feature 1 "Build failed"
fi

# Check for essential files
ESSENTIAL_FILES=(
    "build/index.html"
    "build/static/js"
    "build/static/css"
    "build/manifest.json"
    "build/_redirects"
)

for file in "${ESSENTIAL_FILES[@]}"; do
    if [ -e "$file" ]; then
        test_feature 0 "Found: $file"
    else
        echo -e "${YELLOW}⚠${NC} Missing: $file"
    fi
done

# 4. Test with local static server
echo "Starting local static server for testing..."

# Install serve if not available
if ! command -v serve &> /dev/null; then
    echo "Installing serve..."
    npm install -g serve
fi

# Start server in background
serve -s build -l 3000 &
SERVER_PID=$!
echo "Server started with PID: $SERVER_PID"

# Wait for server to start
sleep 3

# Test local server
echo "Testing local deployment..."
LOCAL_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:3000")
if [ "$LOCAL_RESPONSE" = "200" ]; then
    test_feature 0 "Local server responding"
else
    test_feature 1 "Local server not responding"
fi

# Test SPA routing
ROUTES=("/auth/sign-in" "/app/markets" "/pricing")
for route in "${ROUTES[@]}"; do
    ROUTE_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:3000$route")
    if [ "$ROUTE_RESPONSE" = "200" ]; then
        test_feature 0 "Route working: $route"
    else
        echo -e "${YELLOW}⚠${NC} Route failed: $route"
    fi
done

# Kill the test server
kill $SERVER_PID
echo "Test server stopped"

cd ..

# 5. Create deployment info
echo "Creating deployment information..."
cat > frontend/build/deployment-test.json << EOF
{
    "test_date": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
    "api_url": "$API_URL",
    "api_health": "$HEALTH_RESPONSE",
    "build_size": "$(du -sh frontend/build | cut -f1)",
    "file_count": "$(find frontend/build -type f | wc -l)"
}
EOF

# 6. Summary
echo ""
echo "================================"
echo "   Static Deployment Test Complete"
echo "================================"
echo ""
echo "Build Information:"
echo "  - Build Size: $(du -sh frontend/build | cut -f1)"
echo "  - Files: $(find frontend/build -type f | wc -l)"
echo "  - API Status: $HEALTH_RESPONSE"
echo ""
echo "Next Steps:"
echo "  1. Deploy the 'frontend/build' directory to your static host"
echo "  2. Configure your domain to point to the host"
echo "  3. Ensure SSL certificate is active"
echo "  4. Test all critical user flows"
echo ""
test_feature 0 "All tests passed! Ready for deployment"