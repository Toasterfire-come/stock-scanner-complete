#!/bin/bash

# Proxy Refresh Script for TradeScanPro
# Fetches fresh proxies from free sources
# Run daily via cron at 1:00 AM

BACKEND_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROXY_FILE="$BACKEND_DIR/http_proxies.txt"
LOG_FILE="$BACKEND_DIR/logs/proxy_refresh.log"

# Create logs directory if it doesn't exist
mkdir -p "$BACKEND_DIR/logs"

echo "[$(date)] Starting proxy refresh..." | tee -a "$LOG_FILE"

# Fetch proxies from Geonode API
curl -s "https://proxylist.geonode.com/api/proxy-list?anonymityLevel=elite&filterUpTime=90&speed=fast&limit=500&protocols=http%2Chttps" \
    | jq -r '.data[]? | "\(.ip):\(.port)"' > "$PROXY_FILE.new" 2>> "$LOG_FILE"

# Check if we got proxies
PROXY_COUNT=$(wc -l < "$PROXY_FILE.new" 2>/dev/null || echo 0)

if [ "$PROXY_COUNT" -gt 50 ]; then
    mv "$PROXY_FILE.new" "$PROXY_FILE"
    echo "[$(date)] ✅ Proxy refresh successful: $PROXY_COUNT proxies" | tee -a "$LOG_FILE"
else
    echo "[$(date)] ⚠️  Warning: Only $PROXY_COUNT proxies fetched, keeping old list" | tee -a "$LOG_FILE"
    rm -f "$PROXY_FILE.new"
fi

# Backup old proxy file
if [ -f "$PROXY_FILE" ]; then
    cp "$PROXY_FILE" "$PROXY_FILE.backup.$(date +%s)"
fi

# Clean up old backups (keep last 7 days)
find "$BACKEND_DIR" -name "http_proxies.txt.backup.*" -mtime +7 -delete 2>/dev/null

echo "[$(date)] Proxy refresh complete" | tee -a "$LOG_FILE"
