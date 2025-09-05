#!/bin/bash

# ===============================================
#   Stock Scanner + Cloudflare Tunnel
#   Fully Resilient, Portable, and Self-Healing
# ===============================================

echo ""
echo "==============================================="
echo "    Stock Scanner with Cloudflare Tunnel"
echo "    Resilient to Errors & System Sleep"
echo "==============================================="
echo ""

# -------------------------------
# Configuration
# -------------------------------
TUNNEL_NAME="django-api"
MAX_RETRIES=10
RETRY_DELAY=5
HEALTH_CHECK_INTERVAL=20
KEEPALIVE_INTERVAL=15
DNS_CHECK_INTERVAL=60
ERROR_THRESHOLD=3

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
LOG_DIR="$SCRIPT_DIR/logs"
LOG_FILE="$LOG_DIR/tunnel_resilient.log"

mkdir -p "$LOG_DIR"

CONSECUTIVE_ERRORS=0
TOTAL_RESTARTS=0
LAST_DNS_CHECK=0
LAST_KEEPALIVE=0

# -------------------------------
# Logging Function
# -------------------------------
log_message() {
    local level=$1
    shift
    local message="$@"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] [$level] $message" | tee -a "$LOG_FILE"
}

# -------------------------------
# DNS Fix
# -------------------------------
fix_dns() {
    log_message "INFO" "Fixing DNS configuration..."

    if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
        # Windows DNS reset
        ipconfig /flushdns 2>/dev/null || true

        netsh interface ipv4 set dnsservers name="Wi-Fi" static 1.1.1.1 primary || true
        netsh interface ipv4 add dnsservers name="Wi-Fi" 8.8.8.8 index=2 || true

        netsh interface ipv4 set dnsservers name="Ethernet" static 1.1.1.1 primary || true
        netsh interface ipv4 add dnsservers name="Ethernet" 8.8.8.8 index=2 || true

    else
        # Linux / macOS DNS reset
        if command -v resolvectl &>/dev/null; then
            sudo resolvectl flush-caches 2>/dev/null || true
        elif command -v systemd-resolve &>/dev/null; then
            sudo systemd-resolve --flush-caches 2>/dev/null || true
        elif [ -w /etc/resolv.conf ]; then
            echo "nameserver 1.1.1.1" | sudo tee /etc/resolv.conf >/dev/null
            echo "nameserver 8.8.8.8" | sudo tee -a /etc/resolv.conf >/dev/null
        else
            log_message "WARN" "No DNS tools found — skipping DNS fix"
        fi
    fi

    sleep 2
    log_message "INFO" "DNS configuration refreshed"
}

# -------------------------------
# DNS Check
# -------------------------------
check_dns() {
    local test_domains=("cloudflare.com" "google.com" "region1.v2.argotunnel.com")
    local failed=0

    for domain in "${test_domains[@]}"; do
        if ! nslookup "$domain" >/dev/null 2>&1; then
            failed=$((failed + 1))
        fi
    done

    if [ $failed -ge 2 ]; then
        log_message "WARN" "DNS check failed for multiple domains"
        return 1
    fi

    return 0
}

# -------------------------------
# Prevent Windows Sleep
# -------------------------------
prevent_sleep() {
    if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
        powershell.exe -Command "
            powercfg -change -monitor-timeout-ac 0
            powercfg -change -disk-timeout-ac 0
            powercfg -change -standby-timeout-ac 0
            powercfg -change -hibernate-timeout-ac 0
        " 2>/dev/null || true &
        SLEEP_PREVENT_PID=$!
        log_message "INFO" "Windows sleep prevention activated"
    fi
}

restore_sleep() {
    if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
        powershell.exe -Command "
            powercfg -change -monitor-timeout-ac 30
            powercfg -change -disk-timeout-ac 20
            powercfg -change -standby-timeout-ac 30
            powercfg -change -hibernate-timeout-ac 180
        " 2>/dev/null || true
        log_message "INFO" "Windows sleep settings restored"
    fi
}

# -------------------------------
# Check for Cloudflared
# -------------------------------
check_cloudflared() {
    if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
        if [ -f "$SCRIPT_DIR/cloudflared.exe" ]; then
            CLOUDFLARED_CMD="$SCRIPT_DIR/cloudflared.exe"
        elif command -v cloudflared.exe &>/dev/null; then
            CLOUDFLARED_CMD="cloudflared.exe"
        else
            echo "❌ ERROR: cloudflared.exe not found!"
            exit 1
        fi
    else
        if command -v cloudflared &>/dev/null; then
            CLOUDFLARED_CMD="cloudflared"
        else
            echo "❌ ERROR: cloudflared not found!"
            exit 1
        fi
    fi
    log_message "INFO" "Using cloudflared command: $CLOUDFLARED_CMD"
}

check_tunnel_exists() {
    if ! $CLOUDFLARED_CMD tunnel list 2>/dev/null | grep -q "$TUNNEL_NAME"; then
        log_message "ERROR" "Tunnel '$TUNNEL_NAME' not found!"
        echo "Please run the setup script first:"
        echo "  ./setup_cloudflare_tunnel_auto.sh"
        exit 1
    fi
}

# -------------------------------
# Cleanup Function
# -------------------------------
cleanup() {
    log_message "INFO" "Shutting down services..."

    if [ ! -z "$TUNNEL_PID" ]; then
        kill -TERM $TUNNEL_PID 2>/dev/null || true
        sleep 2
        kill -KILL $TUNNEL_PID 2>/dev/null || true
    fi

    if [ ! -z "$SERVER_PID" ]; then
        kill -TERM $SERVER_PID 2>/dev/null || true
        sleep 2
        kill -KILL $SERVER_PID 2>/dev/null || true
    fi

    if [ ! -z "$HEALTH_PID" ]; then
        kill -TERM $HEALTH_PID 2>/dev/null || true
    fi

    restore_sleep
    log_message "INFO" "All services stopped. Total restarts: $TOTAL_RESTARTS"
    echo "✅ All services stopped"
    exit 0
}

# -------------------------------
# Start Cloudflare Tunnel
# -------------------------------
start_tunnel() {
    local retry_count=0
    while [ $retry_count -lt $MAX_RETRIES ]; do
        log_message "INFO" "Starting Cloudflare tunnel (attempt $((retry_count + 1))/$MAX_RETRIES)..."
        pkill -f cloudflared 2>/dev/null || true
        sleep 2

        $CLOUDFLARED_CMD tunnel \
            --loglevel info \
            --protocol quic \
            --edge-ip-version auto \
            run "$TUNNEL_NAME" \
            >> "$LOG_DIR/cloudflared.log" 2>&1 &
        TUNNEL_PID=$!

        sleep 8
        if ps -p $TUNNEL_PID >/dev/null 2>&1; then
            log_message "INFO" "Cloudflare tunnel started successfully (PID: $TUNNEL_PID)"
            CONSECUTIVE_ERRORS=0
            TOTAL_RESTARTS=$((TOTAL_RESTARTS + 1))
            return 0
        else
            log_message "WARN" "Tunnel failed to start"
            CONSECUTIVE_ERRORS=$((CONSECUTIVE_ERRORS + 1))
            if [ $CONSECUTIVE_ERRORS -ge $ERROR_THRESHOLD ]; then
                fix_dns
                CONSECUTIVE_ERRORS=0
            fi
        fi
        retry_count=$((retry_count + 1))
        [ $retry_count -lt $MAX_RETRIES ] && sleep $RETRY_DELAY
    done
    log_message "ERROR" "Failed to start tunnel after $MAX_RETRIES attempts"
    return 1
}

# -------------------------------
# Start Django Server
# -------------------------------
start_django() {
    log_message "INFO" "Starting Django server..."

    cd "$SCRIPT_DIR"
    if [ ! -f "manage.py" ]; then
        log_message "ERROR" "manage.py not found in $SCRIPT_DIR — aborting."
        return 1
    fi

    python3 manage.py runserver 0.0.0.0:8000 2>&1 | tee /dev/tty &
    SERVER_PID=$!

    sleep 3
    if ps -p $SERVER_PID >/dev/null 2>&1; then
        log_message "INFO" "Django server started successfully (PID: $SERVER_PID)"
        return 0
    else
        log_message "ERROR" "Failed to start Django server. See above logs for details."
        return 1
    fi
}

# -------------------------------
# Health Monitor
# -------------------------------
send_keepalive() {
    curl -s -o /dev/null http://localhost:8000/health/ 2>/dev/null || true
    curl -s -o /dev/null http://localhost:2000/metrics 2>/dev/null || true
}

health_monitor() {
    local current_time
    while true; do
        sleep $HEALTH_CHECK_INTERVAL
        current_time=$(date +%s)

        if [ $((current_time - LAST_DNS_CHECK)) -ge $DNS_CHECK_INTERVAL ]; then
            LAST_DNS_CHECK=$current_time
            if ! check_dns; then
                log_message "WARN" "DNS check failed, fixing..."
                fix_dns
            fi
        fi

        if [ $((current_time - LAST_KEEPALIVE)) -ge $KEEPALIVE_INTERVAL ]; then
            LAST_KEEPALIVE=$current_time
            send_keepalive
        fi

        if ! ps -p $TUNNEL_PID >/dev/null 2>&1; then
            log_message "ERROR" "Tunnel process died, restarting..."
            start_tunnel || cleanup
        fi

        if ! ps -p $SERVER_PID >/dev/null 2>&1; then
            log_message "ERROR" "Django server died, restarting..."
            start_django || cleanup
        fi
    done
}

# -------------------------------
# Trap signals
# -------------------------------
trap cleanup SIGINT SIGTERM

# -------------------------------
# Main Execution
# -------------------------------
log_message "INFO" "Starting Stock Scanner Tunnel - Resilient Version"

check_cloudflared
check_tunnel_exists
fix_dns
prevent_sleep

start_tunnel || cleanup
start_django || cleanup

health_monitor &
HEALTH_PID=$!

LAST_DNS_CHECK=$(date +%s)
LAST_KEEPALIVE=$(date +%s)

echo ""
echo "🌐 Services running with enhanced resilience:"
echo "   📡 Cloudflare Tunnel: Active (PID: $TUNNEL_PID)"
echo "   🐍 Django Server: Active (PID: $SERVER_PID)"
echo "   🔍 Health Monitor: Active (PID: $HEALTH_PID)"
echo "   🔗 Your app is accessible via Cloudflare URL"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

wait $TUNNEL_PID $SERVER_PID