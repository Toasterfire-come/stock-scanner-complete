#!/bin/bash

# ===============================================
#   Stock Scanner with Cloudflare Tunnel
#   Resilient Version - Handles Sleep & Errors
# ===============================================

echo ""
echo "==============================================="
echo "    Stock Scanner with Cloudflare Tunnel"
echo "    Resilient to Errors & System Sleep"
echo "==============================================="
echo ""

# Configuration
TUNNEL_NAME="django-api"
MAX_RETRIES=10
RETRY_DELAY=5
HEALTH_CHECK_INTERVAL=20  # Reduced to detect issues faster
KEEPALIVE_INTERVAL=15     # Send keepalive pings
DNS_CHECK_INTERVAL=60     # Check DNS health
ERROR_THRESHOLD=3         # Number of consecutive errors before action
LOG_DIR="/workspace/logs"
LOG_FILE="$LOG_DIR/tunnel_resilient.log"

# Create log directory
mkdir -p "$LOG_DIR"

# Initialize counters
CONSECUTIVE_ERRORS=0
TOTAL_RESTARTS=0
LAST_DNS_CHECK=0
LAST_KEEPALIVE=0

# Logging function
log_message() {
    local level=$1
    shift
    local message="$@"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] [$level] $message" | tee -a "$LOG_FILE"
}

# Function to fix DNS issues
fix_dns() {
    log_message "INFO" "Fixing DNS configuration..."
    
    # For Windows Git Bash / MINGW
    if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
        # Windows DNS fix
        ipconfig /flushdns 2>/dev/null || true
        
        # Try to use Cloudflare DNS via netsh
        netsh interface ip set dns "Wi-Fi" static 1.1.1.1 primary 2>/dev/null || true
        netsh interface ip add dns "Wi-Fi" 8.8.8.8 index=2 2>/dev/null || true
        
        # Also try for Ethernet
        netsh interface ip set dns "Ethernet" static 1.1.1.1 primary 2>/dev/null || true
        netsh interface ip add dns "Ethernet" 8.8.8.8 index=2 2>/dev/null || true
    else
        # Linux/Mac DNS fix
        if [ -w /etc/resolv.conf ]; then
            echo "nameserver 1.1.1.1" | sudo tee /etc/resolv.conf > /dev/null
            echo "nameserver 8.8.8.8" | sudo tee -a /etc/resolv.conf > /dev/null
        fi
        
        # Flush DNS cache on Linux
        if command -v systemd-resolve &> /dev/null; then
            sudo systemd-resolve --flush-caches 2>/dev/null || true
        fi
    fi
    
    sleep 2
}

# Function to check DNS
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

# Function to prevent Windows sleep (Windows only)
prevent_sleep() {
    if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
        # Use PowerShell to prevent sleep
        powershell.exe -Command "
            \$host.UI.RawUI.WindowTitle = 'Tunnel Monitor - DO NOT CLOSE'
            Write-Host 'Preventing system sleep...'
            
            # Create a power request to prevent sleep
            Add-Type @'
            using System;
            using System.Runtime.InteropServices;
            
            public class PowerRequest {
                [DllImport(\"kernel32.dll\", SetLastError = true)]
                public static extern IntPtr PowerCreateRequest(ref POWER_REQUEST_CONTEXT Context);
                
                [DllImport(\"kernel32.dll\", SetLastError = true)]
                public static extern bool PowerSetRequest(IntPtr PowerRequestHandle, int RequestType);
                
                [StructLayout(LayoutKind.Sequential, CharSet = CharSet.Unicode)]
                public struct POWER_REQUEST_CONTEXT {
                    public uint Version;
                    public uint Flags;
                    public string SimpleReasonString;
                }
                
                public static void PreventSleep() {
                    POWER_REQUEST_CONTEXT prc = new POWER_REQUEST_CONTEXT();
                    prc.Version = 0;
                    prc.Flags = 0x00000001;
                    prc.SimpleReasonString = \"Stock Scanner Tunnel Active\";
                    
                    IntPtr handle = PowerCreateRequest(ref prc);
                    if (handle != IntPtr.Zero) {
                        PowerSetRequest(handle, 1); // Display required
                        PowerSetRequest(handle, 2); // System required
                    }
                }
            }
'@
            
            [PowerRequest]::PreventSleep()
            
            # Alternative method using powercfg
            powercfg -change -monitor-timeout-ac 0
            powercfg -change -disk-timeout-ac 0
            powercfg -change -standby-timeout-ac 0
            powercfg -change -hibernate-timeout-ac 0
            
            Write-Host 'Sleep prevention active'
        " 2>/dev/null || true &
        
        SLEEP_PREVENT_PID=$!
        log_message "INFO" "Windows sleep prevention activated"
    fi
}

# Function to restore sleep settings (Windows only)
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

# Check if cloudflared is installed
check_cloudflared() {
    if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
        # Windows: Check for cloudflared.exe in current directory or PATH
        if [ -f "./cloudflared.exe" ]; then
            CLOUDFLARED_CMD="./cloudflared.exe"
        elif [ -f "/workspace/cloudflared.exe" ]; then
            CLOUDFLARED_CMD="/workspace/cloudflared.exe"
        elif command -v cloudflared.exe &> /dev/null; then
            CLOUDFLARED_CMD="cloudflared.exe"
        elif command -v cloudflared &> /dev/null; then
            CLOUDFLARED_CMD="cloudflared"
        else
            echo "❌ ERROR: cloudflared not found!"
            echo "Please download cloudflared.exe from:"
            echo "  https://github.com/cloudflare/cloudflared/releases/latest"
            exit 1
        fi
    else
        # Linux/Mac
        if command -v cloudflared &> /dev/null; then
            CLOUDFLARED_CMD="cloudflared"
        else
            echo "❌ ERROR: cloudflared not found!"
            exit 1
        fi
    fi
    
    log_message "INFO" "Using cloudflared command: $CLOUDFLARED_CMD"
}

# Check if tunnel exists
check_tunnel_exists() {
    if ! $CLOUDFLARED_CMD tunnel list 2>/dev/null | grep -q "$TUNNEL_NAME"; then
        log_message "ERROR" "Tunnel '$TUNNEL_NAME' not found!"
        echo "Please run the setup script first:"
        echo "  ./setup_cloudflare_tunnel_auto.sh"
        exit 1
    fi
}

# Cleanup function
cleanup() {
    log_message "INFO" "Shutting down services..."
    
    # Kill tunnel process
    if [ ! -z "$TUNNEL_PID" ]; then
        if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
            taskkill //F //PID $TUNNEL_PID 2>/dev/null || true
        else
            kill -TERM $TUNNEL_PID 2>/dev/null || true
            sleep 2
            kill -KILL $TUNNEL_PID 2>/dev/null || true
        fi
    fi
    
    # Kill Django process
    if [ ! -z "$SERVER_PID" ]; then
        if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
            taskkill //F //PID $SERVER_PID 2>/dev/null || true
        else
            kill -TERM $SERVER_PID 2>/dev/null || true
            sleep 2
            kill -KILL $SERVER_PID 2>/dev/null || true
        fi
    fi
    
    # Kill monitor process
    if [ ! -z "$HEALTH_PID" ]; then
        kill -TERM $HEALTH_PID 2>/dev/null || true
    fi
    
    # Restore Windows sleep settings
    restore_sleep
    
    log_message "INFO" "All services stopped. Total restarts during session: $TOTAL_RESTARTS"
    echo "✅ All services stopped"
    exit 0
}

# Start Cloudflare Tunnel with enhanced settings
start_tunnel() {
    local retry_count=0
    
    while [ $retry_count -lt $MAX_RETRIES ]; do
        log_message "INFO" "Starting Cloudflare tunnel (attempt $((retry_count + 1))/$MAX_RETRIES)..."
        
        # Kill any existing tunnel processes
        if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
            taskkill //F //IM cloudflared.exe 2>/dev/null || true
        else
            pkill -f cloudflared 2>/dev/null || true
        fi
        sleep 2
        
        # Start tunnel with resilient settings
        $CLOUDFLARED_CMD tunnel \
            --loglevel info \
            --transport-loglevel warn \
            --metrics localhost:2000 \
            --grace-period 30s \
            --compression-quality 0 \
            --no-autoupdate \
            --protocol quic \
            --edge-ip-version auto \
            --heartbeat-interval 30s \
            --heartbeat-count 5 \
            --retries 10 \
            run "$TUNNEL_NAME" \
            >> "$LOG_DIR/cloudflared.log" 2>&1 &
        
        TUNNEL_PID=$!
        
        sleep 8
        
        # Check if process is running
        if ps -p $TUNNEL_PID > /dev/null 2>&1; then
            log_message "INFO" "Cloudflare tunnel started successfully (PID: $TUNNEL_PID)"
            CONSECUTIVE_ERRORS=0
            TOTAL_RESTARTS=$((TOTAL_RESTARTS + 1))
            return 0
        else
            log_message "WARN" "Tunnel failed to start"
            CONSECUTIVE_ERRORS=$((CONSECUTIVE_ERRORS + 1))
            
            # If multiple failures, try fixing DNS
            if [ $CONSECUTIVE_ERRORS -ge $ERROR_THRESHOLD ]; then
                fix_dns
                CONSECUTIVE_ERRORS=0
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
    
    # Kill any existing Django processes
    if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
        taskkill //F //IM python.exe 2>/dev/null || true
        taskkill //F //IM python3.exe 2>/dev/null || true
    else
        pkill -f "manage.py runserver" 2>/dev/null || true
    fi
    sleep 2
    
    # Start Django
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

# Send keepalive requests
send_keepalive() {
    # Send health check to keep connection active
    curl -s -o /dev/null http://localhost:8000/health/ 2>/dev/null || true
    
    # Also check tunnel metrics
    curl -s -o /dev/null http://localhost:2000/metrics 2>/dev/null || true
}

# Enhanced health monitor loop
health_monitor() {
    local current_time
    
    while true; do
        sleep $HEALTH_CHECK_INTERVAL
        current_time=$(date +%s)
        
        # Check and fix DNS periodically
        if [ $((current_time - LAST_DNS_CHECK)) -ge $DNS_CHECK_INTERVAL ]; then
            LAST_DNS_CHECK=$current_time
            if ! check_dns; then
                log_message "WARN" "DNS check failed, attempting fix..."
                fix_dns
            fi
        fi
        
        # Send keepalive to prevent connection timeout
        if [ $((current_time - LAST_KEEPALIVE)) -ge $KEEPALIVE_INTERVAL ]; then
            LAST_KEEPALIVE=$current_time
            send_keepalive
        fi
        
        # Check tunnel process
        if ! ps -p $TUNNEL_PID > /dev/null 2>&1; then
            log_message "ERROR" "Tunnel process died, attempting restart..."
            if start_tunnel; then
                log_message "INFO" "Tunnel restarted successfully"
            else
                log_message "ERROR" "Failed to restart tunnel"
                cleanup
                exit 1
            fi
        fi
        
        # Check Django process
        if ! ps -p $SERVER_PID > /dev/null 2>&1; then
            log_message "ERROR" "Django server died, attempting restart..."
            if start_django; then
                log_message "INFO" "Django server restarted successfully"
            else
                log_message "ERROR" "Failed to restart Django server"
                cleanup
                exit 1
            fi
        fi
        
        # Check tunnel connectivity
        if ! $CLOUDFLARED_CMD tunnel list 2>/dev/null | grep -q "$TUNNEL_NAME"; then
            log_message "WARN" "Tunnel not visible in list, may need reconnection..."
            CONSECUTIVE_ERRORS=$((CONSECUTIVE_ERRORS + 1))
            
            if [ $CONSECUTIVE_ERRORS -ge $ERROR_THRESHOLD ]; then
                log_message "ERROR" "Too many errors, restarting tunnel..."
                if start_tunnel; then
                    log_message "INFO" "Tunnel restarted after errors"
                fi
            fi
        else
            CONSECUTIVE_ERRORS=0
        fi
        
        # Log statistics periodically
        if [ $((TOTAL_RESTARTS % 10)) -eq 0 ] && [ $TOTAL_RESTARTS -gt 0 ]; then
            log_message "INFO" "Session stats - Restarts: $TOTAL_RESTARTS, Consecutive errors: $CONSECUTIVE_ERRORS"
        fi
    done
}

# Trap signals
trap cleanup SIGINT SIGTERM

# Main execution
log_message "INFO" "Starting Stock Scanner Tunnel - Resilient Version"

# Check prerequisites
check_cloudflared
check_tunnel_exists

# Fix DNS proactively
fix_dns

# Prevent Windows from sleeping
prevent_sleep

# Start services
if ! start_tunnel; then
    cleanup
    exit 1
fi

if ! start_django; then
    cleanup
    exit 1
fi

# Start health monitor in background
health_monitor &
HEALTH_PID=$!

# Initialize timestamps
LAST_DNS_CHECK=$(date +%s)
LAST_KEEPALIVE=$(date +%s)

echo ""
echo "🌐 Services running with enhanced resilience:"
echo "   📡 Cloudflare Tunnel: Active (PID: $TUNNEL_PID)"
echo "   🐍 Django Server: Active (PID: $SERVER_PID)"
echo "   🔍 Health Monitor: Active (PID: $HEALTH_PID)"
echo "   🔗 Your app is accessible via Cloudflare URL"
echo ""
echo "Enhanced Features:"
echo "   • Automatic error recovery"
echo "   • DNS failure detection & fixing"
echo "   • Keep-alive to prevent timeouts"
echo "   • Windows sleep prevention (if on Windows)"
echo "   • Detailed logging to $LOG_DIR"
echo "   • Health checks every $HEALTH_CHECK_INTERVAL seconds"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Keep the script running
wait $TUNNEL_PID $SERVER_PID