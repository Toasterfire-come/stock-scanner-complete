#!/bin/bash
#
# Daily Stock Scanner - Linux Cron Script
# ========================================
# Schedule: Daily at 12:00 AM (midnight)
# Cron: 0 0 * * *
#
# Installation:
# 1. Make executable: chmod +x run_daily_scanner.sh
# 2. Add to crontab: crontab -e
# 3. Add line: 0 0 * * * /path/to/run_daily_scanner.sh >> /path/to/logs/daily_scanner.log 2>&1
#

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BACKEND_DIR="$(dirname "$SCRIPT_DIR")"

# Logging
LOG_DIR="$BACKEND_DIR/logs"
LOG_FILE="$LOG_DIR/daily_scanner_$(date +\%Y\%m\%d).log"

# Create log directory if it doesn't exist
mkdir -p "$LOG_DIR"

# Log start
echo "========================================" | tee -a "$LOG_FILE"
echo "Daily Scanner Started: $(date)" | tee -a "$LOG_FILE"
echo "========================================" | tee -a "$LOG_FILE"

# Activate virtual environment (if exists)
if [ -f "$BACKEND_DIR/venv/bin/activate" ]; then
    source "$BACKEND_DIR/venv/bin/activate"
    echo "Virtual environment activated" | tee -a "$LOG_FILE"
elif [ -f "$BACKEND_DIR/../venv/bin/activate" ]; then
    source "$BACKEND_DIR/../venv/bin/activate"
    echo "Virtual environment activated" | tee -a "$LOG_FILE"
fi

# Change to backend directory
cd "$BACKEND_DIR" || exit 1

# Run the daily scanner
python3 "$SCRIPT_DIR/realtime_daily_with_proxies.py" 2>&1 | tee -a "$LOG_FILE"

# Log completion
echo "" | tee -a "$LOG_FILE"
echo "========================================" | tee -a "$LOG_FILE"
echo "Daily Scanner Completed: $(date)" | tee -a "$LOG_FILE"
echo "========================================" | tee -a "$LOG_FILE"
