#!/bin/bash
#
# Unified Scanner Controller - Linux
# ===================================
# Runs both daily and intraday scanners intelligently:
# - Daily scanner: Runs once at 12:00 AM (off market hours, ~5 hour runtime)
# - Intraday scanner: Starts at 9:30 AM and runs continuously until market close (4:00 PM)
#   * The intraday scanner manages its own 1-minute loop internally
#   * No need to reschedule - it exits automatically when market closes
#
# Installation:
# 1. Make executable: chmod +x run_all_scanners.sh
# 2. Add to crontab: crontab -e
# 3. Add lines:
#    0 0 * * * /path/to/run_all_scanners.sh --daily >> /path/to/logs/daily_scanner.log 2>&1
#    30 9 * * 1-5 /path/to/run_all_scanners.sh --intraday >> /path/to/logs/intraday_scanner.log 2>&1
#

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BACKEND_DIR="$(dirname "$SCRIPT_DIR")"

# Logging
LOG_DIR="$BACKEND_DIR/logs"
mkdir -p "$LOG_DIR"

# Get mode from command line argument
MODE="${1:-auto}"

# Determine what to run based on time and mode
HOUR=$(TZ=America/New_York date +\%H)
MINUTE=$(TZ=America/New_York date +\%M)
DAY_OF_WEEK=$(date +\%u)  # 1-7 (Monday-Sunday)

# Function to run daily scanner
run_daily_scanner() {
    LOG_FILE="$LOG_DIR/daily_scanner_$(date +\%Y\%m\%d).log"

    echo "========================================" | tee -a "$LOG_FILE"
    echo "Daily Scanner Started: $(date)" | tee -a "$LOG_FILE"
    echo "========================================" | tee -a "$LOG_FILE"

    # Activate virtual environment
    if [ -f "$BACKEND_DIR/venv/bin/activate" ]; then
        source "$BACKEND_DIR/venv/bin/activate"
    elif [ -f "$BACKEND_DIR/../venv/bin/activate" ]; then
        source "$BACKEND_DIR/../venv/bin/activate"
    fi

    # Change to backend directory
    cd "$BACKEND_DIR" || exit 1

    # Run the daily scanner
    python3 "$SCRIPT_DIR/realtime_daily_with_proxies.py" 2>&1 | tee -a "$LOG_FILE"

    echo "" | tee -a "$LOG_FILE"
    echo "========================================" | tee -a "$LOG_FILE"
    echo "Daily Scanner Completed: $(date)" | tee -a "$LOG_FILE"
    echo "========================================" | tee -a "$LOG_FILE"
}

# Function to run intraday scanner
run_intraday_scanner() {
    LOG_FILE="$LOG_DIR/intraday_scanner_$(date +\%Y\%m\%d).log"

    echo "========================================" | tee -a "$LOG_FILE"
    echo "Intraday Scanner Started: $(date)" | tee -a "$LOG_FILE"
    echo "Scanner will run continuously until market close (4:00 PM EST)" | tee -a "$LOG_FILE"
    echo "========================================" | tee -a "$LOG_FILE"

    # Activate virtual environment
    if [ -f "$BACKEND_DIR/venv/bin/activate" ]; then
        source "$BACKEND_DIR/venv/bin/activate"
    elif [ -f "$BACKEND_DIR/../venv/bin/activate" ]; then
        source "$BACKEND_DIR/../venv/bin/activate"
    fi

    # Change to backend directory
    cd "$BACKEND_DIR" || exit 1

    # Run the intraday scanner (it will manage its own loop and exit at market close)
    python3 "$SCRIPT_DIR/scanner_1min_hybrid.py" 2>&1 | tee -a "$LOG_FILE"

    echo "" | tee -a "$LOG_FILE"
    echo "========================================" | tee -a "$LOG_FILE"
    echo "Intraday Scanner Completed: $(date)" | tee -a "$LOG_FILE"
    echo "========================================" | tee -a "$LOG_FILE"
}

# Main execution logic
case "$MODE" in
    --daily)
        # Force run daily scanner (for cron at midnight)
        run_daily_scanner
        ;;
    --intraday)
        # Force run intraday scanner (for cron during market hours)
        run_intraday_scanner
        ;;
    --both)
        # Run both (for testing)
        run_daily_scanner
        run_intraday_scanner
        ;;
    auto|*)
        # Auto mode: determine based on time
        if [ "$HOUR" -eq 0 ]; then
            # Midnight - run daily scanner
            run_daily_scanner
        elif [ "$HOUR" -ge 9 ] && [ "$HOUR" -le 16 ] && [ "$DAY_OF_WEEK" -le 5 ]; then
            # Market hours on weekday - run intraday scanner
            run_intraday_scanner
        else
            # Off hours - do nothing
            echo "$(date): No scanner scheduled at this time" >> "$LOG_DIR/scanners.log"
        fi
        ;;
esac
