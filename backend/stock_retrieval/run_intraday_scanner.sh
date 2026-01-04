#!/bin/bash
#
# Intraday Stock Scanner - Linux Cron Script
# ===========================================
# Starts the intraday scanner which runs continuously during market hours
# The scanner manages its own 1-minute update loop and exits at market close
#
# Schedule: Once at market open (9:30 AM EST weekdays)
# Cron: 30 9 * * 1-5
#
# Installation:
# 1. Make executable: chmod +x run_intraday_scanner.sh
# 2. Add to crontab: crontab -e
# 3. Add line:
#    30 9 * * 1-5 /path/to/run_intraday_scanner.sh >> /path/to/logs/intraday_scanner.log 2>&1
#

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BACKEND_DIR="$(dirname "$SCRIPT_DIR")"

# Logging
LOG_DIR="$BACKEND_DIR/logs"
LOG_FILE="$LOG_DIR/intraday_scanner_$(date +\%Y\%m\%d).log"

# Create log directory if it doesn't exist
mkdir -p "$LOG_DIR"

# Log start
echo "========================================" | tee -a "$LOG_FILE"
echo "Intraday Scanner Started: $(date)" | tee -a "$LOG_FILE"
echo "Scanner will run continuously until market close (4:00 PM EST)" | tee -a "$LOG_FILE"
echo "========================================" | tee -a "$LOG_FILE"

# Activate virtual environment (if exists)
if [ -f "$BACKEND_DIR/venv/bin/activate" ]; then
    source "$BACKEND_DIR/venv/bin/activate"
elif [ -f "$BACKEND_DIR/../venv/bin/activate" ]; then
    source "$BACKEND_DIR/../venv/bin/activate"
fi

# Change to backend directory
cd "$BACKEND_DIR" || exit 1

# Set PYTHONPATH to include backend directory for Django imports
export PYTHONPATH="$BACKEND_DIR:$PYTHONPATH"

# Run the intraday scanner (manages its own loop and exits at market close)
python3 "$SCRIPT_DIR/scanner_1min_hybrid.py" 2>&1 | tee -a "$LOG_FILE"

# Log completion
echo "" | tee -a "$LOG_FILE"
echo "========================================" | tee -a "$LOG_FILE"
echo "Intraday Scanner Completed: $(date)" | tee -a "$LOG_FILE"
echo "========================================" | tee -a "$LOG_FILE"
