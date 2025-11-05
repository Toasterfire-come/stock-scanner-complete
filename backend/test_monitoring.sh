#!/bin/bash

# ===============================================
#   Test Monitoring and Health Check System
# ===============================================

echo ""
echo "==============================================="
echo "    Testing Stock Scanner Monitoring System"
echo "==============================================="
echo ""

# Configuration
API_URL="https://api.tradescanpro.com"
LOCAL_URL="http://localhost:8000"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test function
test_endpoint() {
    local url=$1
    local name=$2
    
    echo -n "Testing $name... "
    
    response=$(curl -s -o /dev/null -w "%{http_code}" --max-time 5 "$url")
    
    if [ "$response" = "200" ]; then
        echo -e "${GREEN}✓ OK (HTTP $response)${NC}"
        return 0
    elif [ "$response" = "000" ]; then
        echo -e "${RED}✗ TIMEOUT${NC}"
        return 1
    else
        echo -e "${YELLOW}⚠ HTTP $response${NC}"
        return 1
    fi
}

# Test function with JSON output
test_endpoint_json() {
    local url=$1
    local name=$2
    
    echo ""
    echo "Testing $name:"
    echo "URL: $url"
    
    response=$(curl -s --max-time 5 "$url")
    http_code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 5 "$url")
    
    if [ "$http_code" = "200" ]; then
        echo -e "${GREEN}Status: OK (HTTP $http_code)${NC}"
        echo "Response:"
        echo "$response" | python3 -m json.tool 2>/dev/null || echo "$response"
    else
        echo -e "${RED}Status: FAILED (HTTP $http_code)${NC}"
        [ ! -z "$response" ] && echo "Response: $response"
    fi
}

echo "1. Testing Local Health Endpoints"
echo "================================="
test_endpoint "$LOCAL_URL/health/" "Basic Health Check"
test_endpoint "$LOCAL_URL/health/live/" "Liveness Check"
test_endpoint "$LOCAL_URL/health/ready/" "Readiness Check"
test_endpoint "$LOCAL_URL/health/detailed/" "Detailed Health Check"

echo ""
echo "2. Testing External API Endpoints"
echo "================================="
test_endpoint "$API_URL/" "Root Endpoint"
test_endpoint "$API_URL/health/" "Health Check"
test_endpoint "$API_URL/stocks/" "Stocks List"

echo ""
echo "3. Detailed Health Information"
echo "================================="
test_endpoint_json "$LOCAL_URL/health/detailed/" "Detailed Health Status"

echo ""
echo "4. Testing Cloudflare Tunnel"
echo "================================="
if pgrep -f cloudflared > /dev/null; then
    echo -e "${GREEN}✓ Cloudflared process is running${NC}"
    
    # Get process info
    pid=$(pgrep -f cloudflared | head -1)
    echo "  PID: $pid"
    
    # Check memory usage
    if [ ! -z "$pid" ]; then
        mem=$(ps -o rss= -p $pid | awk '{print int($1/1024)}')
        echo "  Memory: ${mem}MB"
    fi
else
    echo -e "${RED}✗ Cloudflared process not found${NC}"
fi

echo ""
echo "5. Testing Django Server"
echo "================================="
if pgrep -f "manage.py runserver" > /dev/null; then
    echo -e "${GREEN}✓ Django server is running${NC}"
    
    # Get process info
    pid=$(pgrep -f "manage.py runserver" | head -1)
    echo "  PID: $pid"
    
    # Check memory usage
    if [ ! -z "$pid" ]; then
        mem=$(ps -o rss= -p $pid | awk '{print int($1/1024)}')
        echo "  Memory: ${mem}MB"
    fi
else
    echo -e "${RED}✗ Django server not found${NC}"
fi

echo ""
echo "6. DNS Resolution Test"
echo "================================="
dns_domains=("region1.v2.argotunnel.com" "api.cloudflare.com" "1.1.1.1")
for domain in "${dns_domains[@]}"; do
    echo -n "Resolving $domain... "
    if timeout 3 nslookup "$domain" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ OK${NC}"
    else
        echo -e "${RED}✗ FAILED${NC}"
    fi
done

echo ""
echo "7. Log Files Check"
echo "================================="
LOG_DIR="/workspace/logs"
if [ -d "$LOG_DIR" ]; then
    echo "Log directory exists: $LOG_DIR"
    echo "Recent log files:"
    ls -lh "$LOG_DIR" 2>/dev/null | tail -5
    
    if [ -f "$LOG_DIR/tunnel_monitor.log" ]; then
        echo ""
        echo "Last 5 lines from tunnel monitor log:"
        tail -5 "$LOG_DIR/tunnel_monitor.log"
    fi
else
    echo -e "${YELLOW}⚠ Log directory not found${NC}"
fi

echo ""
echo "==============================================="
echo "    Monitoring Test Complete"
echo "==============================================="