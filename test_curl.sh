#!/bin/bash

# Simple curl-based endpoint testing for Stock Scanner API
# Usage: ./test_curl.sh [base_url]

BASE_URL="${1:-http://localhost:8000}"
TEMP_FILE="/tmp/api_test_response.json"

echo "🧪 Testing Stock Scanner API Endpoints"
echo "Base URL: $BASE_URL"
echo "=================================="

# Function to test endpoint
test_endpoint() {
    local endpoint="$1"
    local method="${2:-GET}"
    local description="$3"
    
    echo -n "Testing $description ($method $endpoint)... "
    
    if [ "$method" = "GET" ]; then
        response=$(curl -s -w "%{http_code}" -H "Accept: application/json" \
                   -H "User-Agent: CurlTester/1.0" \
                   "$BASE_URL$endpoint" -o "$TEMP_FILE")
    else
        response=$(curl -s -w "%{http_code}" -X "$method" \
                   -H "Content-Type: application/json" \
                   -H "Accept: application/json" \
                   "$BASE_URL$endpoint" -o "$TEMP_FILE")
    fi
    
    if [ "$response" = "200" ]; then
        echo "✅ OK"
        # Check if response is valid JSON
        if jq empty "$TEMP_FILE" 2>/dev/null; then
            echo "   📄 Valid JSON response"
        else
            echo "   🌐 HTML response"
        fi
    elif [ "$response" = "404" ]; then
        echo "❌ NOT FOUND"
    elif [ "$response" = "405" ]; then
        echo "⚠️  METHOD NOT ALLOWED"
    else
        echo "❌ Error (HTTP $response)"
    fi
}

# Core endpoints
echo -e "\n📍 Core Endpoints:"
test_endpoint "/" "GET" "Homepage"
test_endpoint "/health/" "GET" "Health Check"
test_endpoint "/api/health/" "GET" "API Health Check"
test_endpoint "/docs/" "GET" "API Documentation"

# Stock data endpoints
echo -e "\n📊 Stock Data Endpoints:"
test_endpoint "/api/stocks/" "GET" "Stock List"
test_endpoint "/api/stock/AAPL/" "GET" "Apple Stock Data"
test_endpoint "/api/trending/" "GET" "Trending Stocks"
test_endpoint "/api/search/?q=apple" "GET" "Stock Search"
# NASDAQ endpoint removed

# Revenue endpoints
echo -e "\n💰 Revenue Endpoints:"
test_endpoint "/revenue/revenue-analytics/?format=json" "GET" "Revenue Analytics"

# Portfolio/Watchlist endpoints
echo -e "\n💼 Management Endpoints:"
test_endpoint "/api/portfolio/list/" "GET" "Portfolio List"
test_endpoint "/api/watchlist/list/" "GET" "Watchlist List"

# News endpoints
echo -e "\n📰 News Endpoints:"
test_endpoint "/api/news/feed/" "GET" "News Feed"

# Error handling
echo -e "\n❌ Error Handling:"
test_endpoint "/api/nonexistent/" "GET" "Non-existent Endpoint"

echo -e "\n=================================="
echo "✅ Endpoint testing complete!"
echo "💡 For detailed testing, run: python3 test_endpoints.py"

# Cleanup
rm -f "$TEMP_FILE"