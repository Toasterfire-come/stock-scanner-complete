#!/bin/bash

# TradeScanPro Cron Job Installation Script
# Installs all scanner cron jobs automatically

BACKEND_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_BIN=$(which python3 || which python)
LOG_DIR="$BACKEND_DIR/logs"

# Create logs directory
mkdir -p "$LOG_DIR"

echo "Installing TradeScanPro cron jobs..."
echo "Backend directory: $BACKEND_DIR"
echo "Python binary: $PYTHON_BIN"
echo "Log directory: $LOG_DIR"

# Create temporary cron file
TEMP_CRON=$(mktemp)

# Get existing cron jobs
crontab -l > "$TEMP_CRON" 2>/dev/null || echo "# TradeScanPro Cron Jobs" > "$TEMP_CRON"

# Remove existing TradeScanPro jobs
sed -i '/# TradeScanPro/d' "$TEMP_CRON"
sed -i '/refresh_proxies/d' "$TEMP_CRON"
sed -i '/realtime_daily_yfinance/d' "$TEMP_CRON"
sed -i '/scanner_10min_metrics/d' "$TEMP_CRON"
sed -i '/scanner_1min_hybrid/d' "$TEMP_CRON"

# Add new cron jobs
cat >> "$TEMP_CRON" << EOF

# ===============================================
# TradeScanPro Automated Scanner Jobs
# Installed: $(date)
# ===============================================

# Refresh proxies daily at 1:00 AM
0 1 * * * $BACKEND_DIR/refresh_proxies.sh >> $LOG_DIR/proxy_refresh.log 2>&1

# Daily scanner at 2:00 AM (comprehensive update)
0 2 * * * cd $BACKEND_DIR && $PYTHON_BIN realtime_daily_yfinance.py >> $LOG_DIR/daily_scanner.log 2>&1

# 10-minute scanner during market hours (9:30 AM - 4:00 PM ET, Mon-Fri)
# Start at 9:30 AM
30 9 * * 1-5 cd $BACKEND_DIR && $PYTHON_BIN scanner_10min_metrics_improved.py >> $LOG_DIR/10min_scanner.log 2>&1
# Every 10 minutes from 9:40 AM to 3:50 PM
40,50 9 * * 1-5 cd $BACKEND_DIR && $PYTHON_BIN scanner_10min_metrics_improved.py >> $LOG_DIR/10min_scanner.log 2>&1
*/10 10-15 * * 1-5 cd $BACKEND_DIR && $PYTHON_BIN scanner_10min_metrics_improved.py >> $LOG_DIR/10min_scanner.log 2>&1
0,10,20,30,40,50 16 * * 1-5 cd $BACKEND_DIR && $PYTHON_BIN scanner_10min_metrics_improved.py >> $LOG_DIR/10min_scanner.log 2>&1

# 1-minute scanner during market hours (background process)
# Start at 9:25 AM (5 min before market open)
25 9 * * 1-5 cd $BACKEND_DIR && nohup $PYTHON_BIN scanner_1min_hybrid.py >> $LOG_DIR/1min_scanner.log 2>&1 &
# Stop at 4:05 PM (5 min after market close)
5 16 * * 1-5 pkill -f scanner_1min_hybrid.py

# ===============================================

EOF

# Install new cron jobs
crontab "$TEMP_CRON"

# Clean up
rm "$TEMP_CRON"

echo "✅ Cron jobs installed successfully!"
echo ""
echo "Installed jobs:"
crontab -l | grep -A 20 "TradeScanPro"
echo ""
echo "To view all cron jobs: crontab -l"
echo "To edit cron jobs: crontab -e"
echo "To remove all cron jobs: crontab -r"
echo ""
echo "Logs will be written to: $LOG_DIR"
