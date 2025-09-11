#!/usr/bin/env bash
set -euo pipefail

BASE="${BASE:-https://api.retailtradescanner.com}"
EMAIL="${EMAIL:-}"
PASSWORD="${PASSWORD:-}"
UA="RetailScannerDiag/1.0"
CJ="$(mktemp)"

cleanup(){ rm -f "$CJ"; }
trap cleanup EXIT

req(){
  local method="$1"; shift; local url="$1"; shift; local data="${1:-}"
  if [[ -n "$data" ]]; then
    curl -sS -w "\nHTTP %{http_code}\n" -X "$method" \
      -H 'Accept: application/json' -H 'Content-Type: application/json' \
      -H 'X-Requested-With: XMLHttpRequest' -H "User-Agent: $UA" \
      -b "$CJ" -c "$CJ" \
      --data "$data" "$url"
  else
    curl -sS -w "\nHTTP %{http_code}\n" -X "$method" \
      -H 'Accept: application/json' -H 'X-Requested-With: XMLHttpRequest' \
      -H "User-Agent: $UA" -b "$CJ" -c "$CJ" "$url"
  fi
}

say(){ printf "\n=== %s ===\n" "$*"; }

say Health
req GET "$BASE/health/"

say API Health
req GET "$BASE/api/health/"

say Stocks
req GET "$BASE/api/stocks/?limit=100"

say Trending
req GET "$BASE/api/trending/"

say Market Stats
req GET "$BASE/api/market-stats/"

say News feed
req GET "$BASE/api/news/feed/"

say WordPress News
req GET "$BASE/api/wordpress/news/"

if [[ -n "$EMAIL" && -n "$PASSWORD" ]]; then
  say Login
  LOGIN_RES="$(req POST "$BASE/api/auth/login/" "$(jq -nc --arg u "$EMAIL" --arg p "$PASSWORD" '{username:$u,password:$p}')" || true)"
  echo "$LOGIN_RES"

  say Current Plan
  req GET "$BASE/api/billing/current-plan/"

  say Usage Summary
  req GET "$BASE/api/usage/"

  say Watchlist
  req GET "$BASE/api/watchlist/"

  say Portfolio
  req GET "$BASE/api/portfolio/"

  say Alerts
  req GET "$BASE/api/alerts/"
fi

echo -e "\nDone."

