#!/usr/bin/env bash
set -euo pipefail

BASE_URL=${1:-http://127.0.0.1:8000}

endpoints=(
  "/"
  "/health/"
  "/docs/"
  "/schema/"
  "/redoc/"
  "/openapi.json"
  "/endpoint-status/"
  "/status/simple/"
  "/admin/"
  "/api/"
  "/api/stocks/"
  "/api/stocks/nasdaq/"
  "/api/stocks/search/?q=AAPL"
  "/api/stocks/AAPL/"
  "/api/market/stats/"
  "/api/market/filter/?min_price=1&max_price=100&limit=2"
  "/api/realtime/AAPL/"
  "/api/trending/"
  "/api/alerts/create/"
  "/api/portfolio/list/"
  "/api/watchlist/list/"
  "/api/news/feed/"
  "/api/simple/stocks/"
  "/api/simple/news/"
  "/api/wordpress/"
  "/api/wordpress/stocks/"
  "/api/wordpress/news/"
  "/api/wordpress/alerts/"
  "/api/admin/status/"
  "/api/admin/api-providers/"
  "/api/admin/execute/"
  "/api/auth/user/"
  "/api/auth/login/"
  "/api/billing/paypal-status/"
  "/api/billing/create-paypal-order/"
  "/api/billing/capture-paypal-order/"
  "/api/usage/track/"
  "/api/revenue/validate-discount/"
)

printf "\nCURLING %d ENDPOINTS against %s\n" "${#endpoints[@]}" "$BASE_URL"
echo "====================================="

for path in "${endpoints[@]}"; do
  url="${BASE_URL}${path}"
  method="GET"
  data=""
  case "$path" in
    */alerts/create/*|*/create-paypal-order/*|*/capture-paypal-order/*|*/usage/track/*|*/revenue/validate-discount/*)
      method="POST"
      ;;
    */api/admin/execute/*)
      method="POST"
      ;;
    */api/auth/login/*)
      method="POST"
      ;;
  esac

  if [[ "$path" == *"/alerts/create/"* ]]; then
    data='{"ticker":"AAPL","target_price":150,"condition":"above","email":"test@example.com"}'
  elif [[ "$path" == *"/capture-paypal-order/"* ]]; then
    data='{"orderID":"TEST-ORDER-1234"}'
  elif [[ "$path" == *"/create-paypal-order/"* ]]; then
    data='{"amount":10,"currency":"USD"}'
  elif [[ "$path" == *"/usage/track/"* ]]; then
    data='{"event":"test","meta":{"source":"curl"}}'
  elif [[ "$path" == *"/revenue/validate-discount/"* ]]; then
    data='{"code":"WELCOME10","amount":100}'
  elif [[ "$path" == *"/api/admin/execute/"* ]]; then
    data='{"action":"noop"}'
  elif [[ "$path" == *"/api/auth/login/"* ]]; then
    data='{"username":"invalid","password":"invalid"}'
  fi

  if [[ "$method" == "POST" ]]; then
    status=$(curl -sS -o /dev/null -w "%{http_code}" -X POST -H 'Content-Type: application/json' --data "$data" "$url")
  else
    status=$(curl -sS -o /dev/null -w "%{http_code}" "$url")
  fi

  printf "%3s %s\n" "$status" "$path"
done

