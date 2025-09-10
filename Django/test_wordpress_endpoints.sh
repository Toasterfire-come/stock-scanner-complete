#!/bin/bash

# WordPress-style endpoint tester for Django backend
# - Starts the Django server (if not running)
# - Tests endpoints using the same HTTP methods WordPress uses
# - Summarizes pass/fail results
#
# Usage:
#   ./test_wordpress_endpoints.sh [BASE_URL]
#
# Default BASE_URL is http://localhost:8000

set -u

BASE_URL="${1:-http://localhost:8000}"
PYTHON_CMD="python3"
SERVER_PID=""
TMP_DIR="$(mktemp -d)"
RESULTS_FILE="$TMP_DIR/results.txt"

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

pass_count=0
fail_count=0

echo -e "${BLUE}==========================================${NC}"
echo -e "${BLUE} WordPress Endpoint Test Runner${NC}"
echo -e "${BLUE} Base URL: ${BASE_URL}${NC}"
echo -e "${BLUE}==========================================${NC}"

# Cleanup on exit
cleanup() {
  if [ -n "$SERVER_PID" ] && ps -p "$SERVER_PID" > /dev/null 2>&1; then
    echo -e "\n${YELLOW}Stopping Django server (PID: $SERVER_PID)...${NC}"
    kill -TERM "$SERVER_PID" 2>/dev/null || true
    wait "$SERVER_PID" 2>/dev/null || true
  fi
  rm -rf "$TMP_DIR" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

# Ensure python command exists
if ! command -v $PYTHON_CMD >/dev/null 2>&1; then
  if command -v python >/dev/null 2>&1; then
    PYTHON_CMD=python
  else
    echo -e "${RED}ERROR: python3/python not found in PATH${NC}"
    exit 1
  fi
fi

# Start server if not responding
echo -n "Checking server availability... "
if curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/api/health/" | grep -qE '^(200|301|302)$'; then
  echo -e "${GREEN}already running${NC}"
else
  echo -e "${YELLOW}starting server${NC}"
  $PYTHON_CMD manage.py runserver 0.0.0.0:8000 >/dev/null 2>&1 &
  SERVER_PID=$!
  # Wait for server to come up
  for i in {1..30}; do
    sleep 1
    if curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/api/health/" | grep -qE '^(200|301|302)$'; then
      echo -e "${GREEN}Server started (PID: $SERVER_PID)${NC}"
      break
    fi
    if [ "$i" -eq 30 ]; then
      echo -e "${RED}ERROR: Server failed to start${NC}"
      exit 1
    fi
  done
fi

record_result() {
  local name="$1"; shift
  local status="$1"; shift
  if [ "$status" = "PASS" ]; then
    pass_count=$((pass_count+1))
    echo -e "${GREEN}✔ $name${NC}" | tee -a "$RESULTS_FILE"
  else
    fail_count=$((fail_count+1))
    echo -e "${RED}✖ $name${NC}" | tee -a "$RESULTS_FILE"
  fi
}

# GET tester
get_test() {
  local path="$1"; shift
  local name="$1"; shift
  local expect_code="${1:-200}"
  local http_code
  http_code=$(curl -s -w "%{http_code}" -H "Accept: application/json" "$BASE_URL$path" -o "$TMP_DIR/body.json")
  if [ "$http_code" = "$expect_code" ]; then
    record_result "$name (GET $path)" "PASS"
  else
    echo "  Expected: $expect_code, Got: $http_code" | tee -a "$RESULTS_FILE"
    [ -s "$TMP_DIR/body.json" ] && head -c 400 "$TMP_DIR/body.json" && echo
    record_result "$name (GET $path)" "FAIL"
  fi
}

# POST JSON tester
post_test() {
  local path="$1"; shift
  local name="$1"; shift
  local json_body="$1"; shift
  local expect_code="${1:-200}"
  local http_code
  http_code=$(curl -s -w "%{http_code}" -X POST \
    -H "Content-Type: application/json" -H "Accept: application/json" \
    -d "$json_body" "$BASE_URL$path" -o "$TMP_DIR/body.json")
  if [ "$http_code" = "$expect_code" ]; then
    record_result "$name (POST $path)" "PASS"
  else
    echo "  Expected: $expect_code, Got: $http_code" | tee -a "$RESULTS_FILE"
    [ -s "$TMP_DIR/body.json" ] && head -c 400 "$TMP_DIR/body.json" && echo
    record_result "$name (POST $path)" "FAIL"
  fi
}

echo -e "\n${BLUE}Health & Core (as WP would call)${NC}"
get_test "/api/health/" "API Health"
get_test "/" "Homepage" 200

echo -e "\n${BLUE}WordPress-optimized endpoints (GET)${NC}"
get_test "/api/wordpress/stocks/?limit=5" "WP Stocks (limit)"
get_test "/api/wordpress/stocks/?category=gainers&limit=5" "WP Stocks (gainers)"
get_test "/api/wordpress/stocks/?search=AAPL&limit=5" "WP Stocks (search)"
get_test "/api/wordpress/news/?limit=5" "WP News"

echo -e "\n${BLUE}WP-style backend calls (GET)${NC}"
get_test "/api/stocks/?limit=10" "Stock List"
get_test "/api/stock/AAPL/" "Stock Detail AAPL"
get_test "/api/stocks/search/?q=AAPL" "Stock Search"
get_test "/api/trending/" "Trending Stocks"

echo -e "\n${BLUE}WordPress subscribe (POST)${NC}"
post_test "/api/wordpress/subscribe/" "WP Subscribe" '{"email":"test@example.com","category":"dvsa-50"}' 200

# Secure endpoints (expect 401 without auth)
echo -e "\n${BLUE}Secure endpoints (expect 401 Unauthorized)${NC}"
get_test "/api/portfolio/list/" "Portfolio List (secure)" 401
get_test "/api/watchlist/list/" "Watchlist List (secure)" 401
get_test "/api/news/feed/" "News Feed (secure)" 401

# Summary
echo -e "\n${BLUE}==========================================${NC}"
echo -e "${BLUE} Test Summary${NC}"
echo -e "${GREEN}  Passed: $pass_count${NC}"
echo -e "${RED}  Failed: $fail_count${NC}"
echo -e "${BLUE} Results saved to: $RESULTS_FILE${NC}"
echo -e "${BLUE}==========================================${NC}"

# Exit non-zero if any failed
[ "$fail_count" -eq 0 ] || exit 1