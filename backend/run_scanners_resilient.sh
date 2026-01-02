#!/bin/bash

# ===============================================
#   Stock Scanner Manager - Resilient Version
#   Manages Daily & Realtime Scanners
# ===============================================

echo ""
echo "==============================================="
echo "    Stock Scanner Manager - Resilient"
echo "    Daily Scanner + Realtime (1-min) Scanner"
echo "==============================================="
echo ""

# -------------------------------
# Configuration
# -------------------------------
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
LOG_DIR="$SCRIPT_DIR/logs"
DAILY_LOG="$LOG_DIR/daily_scanner_$(date +%Y%m%d).log"
REALTIME_LOG="$LOG_DIR/realtime_scanner_$(date +%Y%m%d).log"
MANAGER_LOG="$LOG_DIR/scanner_manager.log"
ERROR_LOG="$LOG_DIR/scanner_errors.log"

mkdir -p "$LOG_DIR"

# Scanner scripts
DAILY_SCANNER="$SCRIPT_DIR/stock_retrieval/realtime_daily_with_proxies.py"
REALTIME_SCANNER="$SCRIPT_DIR/stock_retrieval/scanner_1min_hybrid.py"

# Schedule configuration (Chicago/Central Time - 1 hour behind EST)
DAILY_SCANNER_HOUR=15        # 3:30 PM CST = 4:30 PM EST (run once daily)
DAILY_SCANNER_MINUTE=30

REALTIME_START_HOUR=8        # 8:30 AM CST = 9:30 AM EST
REALTIME_START_MINUTE=30
REALTIME_END_HOUR=15         # 3:00 PM CST = 4:00 PM EST
REALTIME_END_MINUTE=0

# Process tracking
DAILY_SCANNER_PID=""
REALTIME_SCANNER_PID=""
HEALTH_MONITOR_PID=""

# State tracking
DAILY_SCANNER_RAN_TODAY=false
REALTIME_SCANNER_RUNNING=false
LAST_CHECK_MINUTE=""

# Error tracking
CONSECUTIVE_ERRORS=0
MAX_CONSECUTIVE_ERRORS=5

# -------------------------------
# Logging
# -------------------------------
log_message() {
    local level=$1
    shift
    local message="$*"
    local timestamp
    timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    local line="[$timestamp] [$level] $message"

    echo "$line" >> "$MANAGER_LOG"

    if [ "$level" = "ERROR" ]; then
        echo "$line" | tee -a "$ERROR_LOG" >&2
    else
        echo "$line"
    fi
}

# -------------------------------
# Windows/Unix compatibility
# -------------------------------
is_windows() {
    [[ "$OSTYPE" == msys* || "$OSTYPE" == cygwin* ]]
}

kill_process() {
    local pid=$1
    if [ -z "$pid" ]; then
        return
    fi

    if is_windows; then
        taskkill //F //PID "$pid" 2>/dev/null || true
    else
        kill -TERM "$pid" 2>/dev/null || true
        sleep 2
        kill -KILL "$pid" 2>/dev/null || true
    fi
}

is_process_running() {
    local pid=$1
    if [ -z "$pid" ]; then
        return 1
    fi
    ps -p "$pid" >/dev/null 2>&1
}

# -------------------------------
# Market Hours Check (EST/EDT)
# -------------------------------
get_current_time_est() {
    # Use system local time (assumes system is set to EST)
    date '+%H:%M'
}

get_current_hour_est() {
    date '+%H'
}

get_current_minute_est() {
    date '+%M'
}

get_current_day_of_week() {
    # 1=Monday, 7=Sunday
    date '+%u'
}

is_weekday() {
    local day
    day=$(get_current_day_of_week)
    [ "$day" -le 5 ]  # Monday-Friday
}

is_market_hours() {
    if ! is_weekday; then
        return 1
    fi

    local hour minute
    hour=$(get_current_hour_est)
    minute=$(get_current_minute_est)

    # Remove leading zeros
    hour=$((10#$hour))
    minute=$((10#$minute))

    # Market hours: 9:30 AM - 4:00 PM EST
    if [ "$hour" -lt 9 ]; then
        return 1
    elif [ "$hour" -eq 9 ] && [ "$minute" -lt 30 ]; then
        return 1
    elif [ "$hour" -ge 16 ]; then
        return 1
    fi

    return 0
}

should_run_daily_scanner() {
    if [ "$DAILY_SCANNER_RAN_TODAY" = "true" ]; then
        return 1
    fi

    if ! is_weekday; then
        return 1
    fi

    local hour minute
    hour=$(get_current_hour_est)
    minute=$(get_current_minute_est)

    hour=$((10#$hour))
    minute=$((10#$minute))

    # Run daily scanner at configured time
    if [ "$hour" -eq "$DAILY_SCANNER_HOUR" ] && [ "$minute" -eq "$DAILY_SCANNER_MINUTE" ]; then
        return 0
    fi

    return 1
}

# -------------------------------
# Start Daily Scanner
# -------------------------------
start_daily_scanner() {
    log_message "INFO" "Starting Daily Scanner..."

    if [ ! -f "$DAILY_SCANNER" ]; then
        log_message "ERROR" "Daily scanner script not found: $DAILY_SCANNER"
        return 1
    fi

    # Start scanner in background with PYTHONPATH set
    cd "$SCRIPT_DIR" || return 1
    export PYTHONPATH="$SCRIPT_DIR:$PYTHONPATH"
    python "$DAILY_SCANNER" >> "$DAILY_LOG" 2>&1 &
    DAILY_SCANNER_PID=$!

    log_message "INFO" "Daily scanner started (PID: $DAILY_SCANNER_PID)"
    DAILY_SCANNER_RAN_TODAY=true

    # Wait for completion (runs in background, we just track it)
    return 0
}

# -------------------------------
# Start Realtime Scanner
# -------------------------------
start_realtime_scanner() {
    log_message "INFO" "Starting Realtime (1-min) Scanner..."

    if [ ! -f "$REALTIME_SCANNER" ]; then
        log_message "ERROR" "Realtime scanner script not found: $REALTIME_SCANNER"
        return 1
    fi

    # Start scanner in background with PYTHONPATH set
    cd "$SCRIPT_DIR" || return 1
    export PYTHONPATH="$SCRIPT_DIR:$PYTHONPATH"
    python "$REALTIME_SCANNER" >> "$REALTIME_LOG" 2>&1 &
    REALTIME_SCANNER_PID=$!

    log_message "INFO" "Realtime scanner started (PID: $REALTIME_SCANNER_PID)"
    REALTIME_SCANNER_RUNNING=true

    return 0
}

# -------------------------------
# Stop Realtime Scanner
# -------------------------------
stop_realtime_scanner() {
    if [ -z "$REALTIME_SCANNER_PID" ]; then
        return
    fi

    log_message "INFO" "Stopping Realtime Scanner (PID: $REALTIME_SCANNER_PID)..."
    kill_process "$REALTIME_SCANNER_PID"
    REALTIME_SCANNER_PID=""
    REALTIME_SCANNER_RUNNING=false
    log_message "INFO" "Realtime scanner stopped"
}

# -------------------------------
# Health Check
# -------------------------------
check_scanner_health() {
    # Check if daily scanner is still running (if started today)
    if [ -n "$DAILY_SCANNER_PID" ] && [ "$DAILY_SCANNER_RAN_TODAY" = "true" ]; then
        if ! is_process_running "$DAILY_SCANNER_PID"; then
            log_message "INFO" "Daily scanner completed (PID: $DAILY_SCANNER_PID)"
            DAILY_SCANNER_PID=""
        fi
    fi

    # Check if realtime scanner should be running
    if is_market_hours; then
        if [ "$REALTIME_SCANNER_RUNNING" = "true" ]; then
            # Should be running, check if it's alive
            if [ -n "$REALTIME_SCANNER_PID" ]; then
                if ! is_process_running "$REALTIME_SCANNER_PID"; then
                    log_message "WARN" "Realtime scanner died during market hours, restarting..."
                    REALTIME_SCANNER_RUNNING=false
                    start_realtime_scanner || {
                        CONSECUTIVE_ERRORS=$((CONSECUTIVE_ERRORS + 1))
                        log_message "ERROR" "Failed to restart realtime scanner (error count: $CONSECUTIVE_ERRORS)"
                    }
                fi
            else
                # Should be running but PID is empty
                log_message "WARN" "Realtime scanner PID missing, restarting..."
                REALTIME_SCANNER_RUNNING=false
                start_realtime_scanner
            fi
        else
            # Should be running but isn't
            log_message "INFO" "Market is open, starting realtime scanner..."
            start_realtime_scanner
        fi
    else
        # Market closed, stop realtime scanner if running
        if [ "$REALTIME_SCANNER_RUNNING" = "true" ]; then
            log_message "INFO" "Market closed, stopping realtime scanner..."
            stop_realtime_scanner
        fi
    fi
}

# -------------------------------
# Scheduler Loop
# -------------------------------
scheduler_loop() {
    log_message "INFO" "Scanner scheduler started"

    while true; do
        local current_minute
        current_minute=$(get_current_time_est)

        # Only check once per minute
        if [ "$current_minute" != "$LAST_CHECK_MINUTE" ]; then
            LAST_CHECK_MINUTE="$current_minute"

            local hour minute day_of_week
            hour=$(get_current_hour_est)
            minute=$(get_current_minute_est)
            day_of_week=$(get_current_day_of_week)

            log_message "DEBUG" "Time check: $current_minute EST (Day: $day_of_week)"

            # Reset daily flag at midnight
            if [ "$hour" = "00" ] && [ "$minute" = "00" ]; then
                log_message "INFO" "New day started, resetting daily scanner flag"
                DAILY_SCANNER_RAN_TODAY=false
            fi

            # Check if daily scanner should run
            if should_run_daily_scanner; then
                log_message "INFO" "Daily scanner scheduled time reached"
                start_daily_scanner || {
                    CONSECUTIVE_ERRORS=$((CONSECUTIVE_ERRORS + 1))
                    log_message "ERROR" "Failed to start daily scanner (error count: $CONSECUTIVE_ERRORS)"
                }
            fi

            # Health check for all scanners
            check_scanner_health

            # Reset error counter on successful check
            if [ $CONSECUTIVE_ERRORS -gt 0 ]; then
                CONSECUTIVE_ERRORS=0
            fi
        fi

        # Check every 30 seconds
        sleep 30

        # Emergency stop if too many errors
        if [ $CONSECUTIVE_ERRORS -ge $MAX_CONSECUTIVE_ERRORS ]; then
            log_message "ERROR" "Too many consecutive errors ($CONSECUTIVE_ERRORS), stopping scheduler"
            cleanup
            exit 1
        fi
    done
}

# -------------------------------
# Cleanup
# -------------------------------
cleanup() {
    log_message "INFO" "Shutting down scanner manager..."

    if [ -n "$DAILY_SCANNER_PID" ]; then
        log_message "INFO" "Stopping daily scanner..."
        kill_process "$DAILY_SCANNER_PID"
    fi

    if [ -n "$REALTIME_SCANNER_PID" ]; then
        log_message "INFO" "Stopping realtime scanner..."
        kill_process "$REALTIME_SCANNER_PID"
    fi

    if [ -n "$HEALTH_MONITOR_PID" ]; then
        kill -TERM "$HEALTH_MONITOR_PID" 2>/dev/null || true
    fi

    log_message "INFO" "Scanner manager stopped"
    echo "✅ All scanners stopped"
    exit 0
}

# -------------------------------
# Trap signals
# -------------------------------
trap cleanup SIGINT SIGTERM

# -------------------------------
# Main
# -------------------------------
main() {
    log_message "INFO" "=== Stock Scanner Manager Starting ==="
    log_message "INFO" "Daily Scanner: Runs at $DAILY_SCANNER_HOUR:$(printf '%02d' $DAILY_SCANNER_MINUTE) EST"
    log_message "INFO" "Realtime Scanner: Runs during market hours (9:30 AM - 4:00 PM EST)"
    log_message "INFO" "Current time: $(get_current_time_est) EST"

    # Verify scanner scripts exist
    if [ ! -f "$DAILY_SCANNER" ]; then
        log_message "ERROR" "Daily scanner not found: $DAILY_SCANNER"
        exit 1
    fi

    if [ ! -f "$REALTIME_SCANNER" ]; then
        log_message "ERROR" "Realtime scanner not found: $REALTIME_SCANNER"
        exit 1
    fi

    echo ""
    echo "📊 Scanner Status:"
    echo "   Daily Scanner:    Scheduled for $DAILY_SCANNER_HOUR:$(printf '%02d' $DAILY_SCANNER_MINUTE) EST"
    echo "   Realtime Scanner: Market hours (9:30 AM - 4:00 PM EST)"
    echo "   Current Time:     $(get_current_time_est) EST"
    echo ""

    # Check if we should start realtime scanner immediately
    if is_market_hours; then
        echo "🟢 Market is currently OPEN - Starting realtime scanner..."
        start_realtime_scanner
    else
        echo "🔴 Market is currently CLOSED"
    fi

    echo ""
    echo "Press Ctrl+C to stop all scanners"
    echo ""

    # Start scheduler loop
    scheduler_loop
}

# Run main
main
