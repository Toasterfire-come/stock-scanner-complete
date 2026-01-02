#!/bin/bash

# ===============================================
#   Enhanced Cloudflare Tunnel Monitor
#   Handles QUIC timeouts and DNS failures
# ===============================================

echo ""
echo "==============================================="
echo "    Enhanced Cloudflare Tunnel Monitor"
echo "      With Auto-Recovery & Logging"
echo "==============================================="
echo ""

# Configuration
TUNNEL_NAME="django-api"
LOG_DIR="/workspace/logs"
LOG_FILE="$LOG_DIR/tunnel_monitor.log"
ERROR_LOG="$LOG_DIR/tunnel_errors.log"
HEALTH_LOG="$LOG_DIR/health_checks.log"
MAX_RETRIES=5
RETRY_DELAY=10
HEALTH_CHECK_INTERVAL=30
DNS_CHECK_INTERVAL=60
QUIC_TIMEOUT_THRESHOLD=3
DNS_FAILURE_THRESHOLD=2
API_URL="https://api.retailtradescanner.com"
LOCAL_URL="http://localhost:8000"

# Create log directory if it doesn't exist
mkdir -p "$LOG_DIR"

# Initialize counters
QUIC_TIMEOUT_COUNT=0
DNS_FAILURE_COUNT=0
RESTART_COUNT=0

# Logging function
log_message() {
    local level=$1
    shift
    local message="$@"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] [$level] $message" | tee -a "$LOG_FILE"
    
    if [ "$level" = "ERROR" ]; then
        echo "[$timestamp] $message" >> "$ERROR_LOG"
    fi
}

# DNS health check
check_dns() {
    local domains=("region1.v2.argotunnel.com" "api.cloudflare.com" "protocol-v2.argotunnel.com" "cfd-features.argotunnel.com")
    local failed=0
    
    for domain in "${domains[@]}"; do
        if ! timeout 5 nslookup "$domain" >/dev/null 2>&1; then
            log_message "WARN" "DNS resolution failed for $domain"
            failed=$((failed + 1))
        fi
    done
    
    if [ $failed -ge 2 ]; then
        DNS_FAILURE_COUNT=$((DNS_FAILURE_COUNT + 1))
        log_message "ERROR" "Multiple DNS failures detected (count: $DNS_FAILURE_COUNT)"
        return 1
    else
        DNS_FAILURE_COUNT=0
        return 0
    fi
}

# Fix DNS issues
fix_dns() {
    log_message "INFO" "Attempting to fix DNS resolution..."
    
    # Try multiple DNS fixes
    # 1. Flush DNS cache
    if command -v systemd-resolve &> /dev/null; then
        sudo systemd-resolve --flush-caches 2>/dev/null || true
    fi
    
    # 2. Restart DNS service
    if systemctl is-active --quiet systemd-resolved; then
        sudo systemctl restart systemd-resolved 2>/dev/null || true
    fi
    
    # 3. Update resolv.conf with Cloudflare DNS
    if [ -w /etc/resolv.conf ]; then
        echo "nameserver 1.1.1.1" | sudo tee /etc/resolv.conf.tmp > /dev/null
        echo "nameserver 1.0.0.1" | sudo tee -a /etc/resolv.conf.tmp > /dev/null
        echo "nameserver 8.8.8.8" | sudo tee -a /etc/resolv.conf.tmp > /dev/null
        sudo mv /etc/resolv.conf.tmp /etc/resolv.conf
    fi
    
    sleep 5
    
    # Verify DNS is working
    if check_dns; then
        log_message "INFO" "DNS resolution fixed"
        return 0
    else
        log_message "ERROR" "DNS resolution still failing"
        return 1
    fi
}

# Check tunnel health via API
check_tunnel_health() {
    # Check if tunnel process is running
    if [ ! -z "$TUNNEL_PID" ] && ! ps -p $TUNNEL_PID > /dev/null 2>&1; then
        log_message "ERROR" "Tunnel process not running (PID: $TUNNEL_PID)"
        return 1
    fi
    
    # Check local Django server
    if ! curl -s -f -o /dev/null -w "%{http_code}" --max-time 5 "$LOCAL_URL/api/health/" > /dev/null 2>&1; then
        log_message "WARN" "Local Django server not responding"
        return 1
    fi
    
    # Check external API endpoint
    local response=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 -I "$API_URL/")
    if [ "$response" = "200" ]; then
        echo "[$timestamp] API responding (HTTP $response)" >> "$HEALTH_LOG"
        QUIC_TIMEOUT_COUNT=0
        return 0
    else
        log_message "WARN" "API not responding properly (HTTP $response)"
        return 1
    fi
}

# Parse tunnel logs for issues
monitor_tunnel_logs() {
    if [ ! -z "$TUNNEL_PID" ]; then
        # Check recent logs for QUIC timeout errors
        local recent_errors=$(timeout 2 tail -n 50 /proc/$TUNNEL_PID/fd/2 2>/dev/null | grep -c "QUIC stream: timeout" || echo 0)
        
        if [ $recent_errors -gt 0 ]; then
            QUIC_TIMEOUT_COUNT=$((QUIC_TIMEOUT_COUNT + recent_errors))
            log_message "WARN" "QUIC timeout errors detected (total: $QUIC_TIMEOUT_COUNT)"
            
            if [ $QUIC_TIMEOUT_COUNT -ge $QUIC_TIMEOUT_THRESHOLD ]; then
                log_message "ERROR" "QUIC timeout threshold exceeded, tunnel restart required"
                return 1
            fi
        fi
    fi
    return 0
}

# Start Cloudflare Tunnel with optimized settings
start_tunnel() {
    local retry_count=0
    
    while [ $retry_count -lt $MAX_RETRIES ]; do
        log_message "INFO" "Starting Cloudflare tunnel (attempt $((retry_count + 1))/$MAX_RETRIES)..."
        
        # Kill any existing tunnel processes
        pkill -f "cloudflared.*tunnel.*run.*$TUNNEL_NAME" 2>/dev/null || true
        sleep 2
        
        # Start tunnel with optimized settings for stability
        cloudflared tunnel \
            --loglevel info \
            --transport-loglevel warn \
            --metrics localhost:2000 \
            --grace-period 30s \
            --compression-quality 0 \
            --no-autoupdate \
            run "$TUNNEL_NAME" \
            2>&1 | tee -a "$LOG_DIR/cloudflared.log" &
        
        TUNNEL_PID=$!
        
        # Wait for tunnel to stabilize
        sleep 8
        
        if ps -p $TUNNEL_PID > /dev/null 2>&1; then
            # Verify tunnel is actually working
            sleep 5
            if check_tunnel_health; then
                log_message "INFO" "Cloudflare tunnel started successfully (PID: $TUNNEL_PID)"
                RESTART_COUNT=$((RESTART_COUNT + 1))
                QUIC_TIMEOUT_COUNT=0
                return 0
            else
                log_message "WARN" "Tunnel started but health check failed, retrying..."
                kill -TERM $TUNNEL_PID 2>/dev/null || true
            fi
        fi
        
        retry_count=$((retry_count + 1))
        if [ $retry_count -lt $MAX_RETRIES ]; then
            log_message "INFO" "Retrying in $RETRY_DELAY seconds..."
            sleep $RETRY_DELAY
        fi
    done
    
    log_message "ERROR" "Failed to start tunnel after $MAX_RETRIES attempts"
    return 1
}

# Start Django server
start_django() {
    log_message "INFO" "Starting Django server..."
    
    # Kill any existing Django processes on port 8000
    lsof -ti:8000 | xargs kill -9 2>/dev/null || true
    sleep 2
    
    # Start Django with proper error handling
    cd /workspace
    python3 manage.py runserver 0.0.0.0:8000 >> "$LOG_DIR/django.log" 2>&1 &
    SERVER_PID=$!
    
    sleep 3
    
    if ps -p $SERVER_PID > /dev/null 2>&1; then
        log_message "INFO" "Django server started successfully (PID: $SERVER_PID)"
        return 0
    else
        log_message "ERROR" "Failed to start Django server"
        return 1
    fi
}

# Cleanup function
cleanup() {
    log_message "INFO" "Shutting down services..."
    
    if [ ! -z "$TUNNEL_PID" ]; then
        log_message "INFO" "Stopping Cloudflare tunnel (PID: $TUNNEL_PID)..."
        kill -TERM $TUNNEL_PID 2>/dev/null || true
        sleep 2
        kill -KILL $TUNNEL_PID 2>/dev/null || true
    fi
    
    if [ ! -z "$SERVER_PID" ]; then
        log_message "INFO" "Stopping Django server (PID: $SERVER_PID)..."
        kill -TERM $SERVER_PID 2>/dev/null || true
        sleep 2
        kill -KILL $SERVER_PID 2>/dev/null || true
    fi
    
    if [ ! -z "$MONITOR_PID" ]; then
        kill -TERM $MONITOR_PID 2>/dev/null || true
    fi
    
    log_message "INFO" "All services stopped. Total restarts during session: $RESTART_COUNT"
    exit 0
}

# Main monitoring loop
main_monitor() {
    local dns_check_counter=0
    
    while true; do
        sleep $HEALTH_CHECK_INTERVAL
        
        # Increment DNS check counter
        dns_check_counter=$((dns_check_counter + HEALTH_CHECK_INTERVAL))
        
        # Check DNS periodically
        if [ $dns_check_counter -ge $DNS_CHECK_INTERVAL ]; then
            dns_check_counter=0
            if ! check_dns; then
                if [ $DNS_FAILURE_COUNT -ge $DNS_FAILURE_THRESHOLD ]; then
                    log_message "ERROR" "DNS failures exceeded threshold, attempting fix..."
                    fix_dns
                fi
            fi
        fi
        
        # Monitor tunnel logs for QUIC timeouts
        if ! monitor_tunnel_logs; then
            log_message "ERROR" "Tunnel issues detected, restarting..."
            if start_tunnel; then
                log_message "INFO" "Tunnel restarted successfully"
            else
                log_message "ERROR" "Failed to restart tunnel, exiting..."
                cleanup
                exit 1
            fi
        fi
        
        # Check tunnel health
        if ! check_tunnel_health; then
            log_message "WARN" "Health check failed, investigating..."
            
            # Check if tunnel process died
            if [ ! -z "$TUNNEL_PID" ] && ! ps -p $TUNNEL_PID > /dev/null 2>&1; then
                log_message "ERROR" "Tunnel process died, restarting..."
                if start_tunnel; then
                    log_message "INFO" "Tunnel restarted successfully"
                else
                    log_message "ERROR" "Failed to restart tunnel"
                    cleanup
                    exit 1
                fi
            fi
            
            # Check if Django died
            if [ ! -z "$SERVER_PID" ] && ! ps -p $SERVER_PID > /dev/null 2>&1; then
                log_message "ERROR" "Django server died, restarting..."
                if start_django; then
                    log_message "INFO" "Django server restarted successfully"
                else
                    log_message "ERROR" "Failed to restart Django server"
                    cleanup
                    exit 1
                fi
            fi
        fi
        
        # Log statistics every 10 checks
        if [ $((RESTART_COUNT % 10)) -eq 0 ] && [ $RESTART_COUNT -gt 0 ]; then
            log_message "INFO" "Statistics - Restarts: $RESTART_COUNT, QUIC timeouts: $QUIC_TIMEOUT_COUNT, DNS failures: $DNS_FAILURE_COUNT"
        fi
    done
}

# Trap signals
trap cleanup SIGINT SIGTERM

# Check prerequisites
if ! command -v cloudflared &> /dev/null; then
    log_message "ERROR" "cloudflared not found! Please install Cloudflare tunnel first."
    exit 1
fi

if ! cloudflared tunnel list 2>/dev/null | grep -q "$TUNNEL_NAME"; then
    log_message "ERROR" "Tunnel '$TUNNEL_NAME' not found! Please run setup script first."
    exit 1
fi

# Start services
log_message "INFO" "Starting Stock Scanner with Enhanced Monitoring..."

if ! start_tunnel; then
    log_message "ERROR" "Failed to start tunnel"
    exit 1
fi

if ! start_django; then
    log_message "ERROR" "Failed to start Django"
    cleanup
    exit 1
fi

# Start monitoring in background
main_monitor &
MONITOR_PID=$!

log_message "INFO" "Services running with enhanced monitoring:"
log_message "INFO" "  Cloudflare Tunnel: PID $TUNNEL_PID"
log_message "INFO" "  Django Server: PID $SERVER_PID"
log_message "INFO" "  Monitor: PID $MONITOR_PID"
log_message "INFO" "  Logs: $LOG_DIR"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Wait for processes
wait $TUNNEL_PID $SERVER_PID