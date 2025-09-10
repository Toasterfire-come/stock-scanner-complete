#!/bin/bash

# ===============================================
#   Start Cloudflare Tunnel with Config File
#   Optimized for stability
# ===============================================

echo ""
echo "==============================================="
echo "    Starting Cloudflare Tunnel with"
echo "    Optimized Configuration"
echo "==============================================="
echo ""

# Configuration
CONFIG_FILE="/workspace/cloudflared_config.yml"
LOG_FILE="/workspace/logs/cloudflared_direct.log"
TUNNEL_NAME="django-api"

# Create logs directory
mkdir -p /workspace/logs

# Function to setup DNS
setup_dns() {
    echo "Setting up reliable DNS..."
    
    # Backup current resolv.conf
    sudo cp /etc/resolv.conf /etc/resolv.conf.backup 2>/dev/null || true
    
    # Set Cloudflare and Google DNS
    echo "nameserver 1.1.1.1" | sudo tee /etc/resolv.conf > /dev/null
    echo "nameserver 1.0.0.1" | sudo tee -a /etc/resolv.conf > /dev/null
    echo "nameserver 8.8.8.8" | sudo tee -a /etc/resolv.conf > /dev/null
    echo "nameserver 8.8.4.4" | sudo tee -a /etc/resolv.conf > /dev/null
    
    echo "DNS configured with reliable servers"
}

# Function to test DNS
test_dns() {
    echo "Testing DNS resolution..."
    
    for domain in "cloudflare.com" "google.com" "region1.v2.argotunnel.com"; do
        if nslookup "$domain" >/dev/null 2>&1; then
            echo "  ✓ $domain resolves"
        else
            echo "  ✗ $domain failed to resolve"
            return 1
        fi
    done
    
    return 0
}

# Function to start tunnel
start_tunnel() {
    echo "Starting Cloudflare tunnel with optimized config..."
    
    # Kill any existing tunnel
    pkill -f cloudflared 2>/dev/null || true
    sleep 2
    
    # Start tunnel with config file
    if [ -f "$CONFIG_FILE" ]; then
        cloudflared tunnel --config "$CONFIG_FILE" run >> "$LOG_FILE" 2>&1 &
        TUNNEL_PID=$!
        echo "Tunnel started with PID: $TUNNEL_PID"
    else
        echo "ERROR: Config file not found at $CONFIG_FILE"
        echo "Starting with command-line options instead..."
        
        cloudflared tunnel \
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
            run "$TUNNEL_NAME" >> "$LOG_FILE" 2>&1 &
        
        TUNNEL_PID=$!
        echo "Tunnel started with PID: $TUNNEL_PID (fallback mode)"
    fi
    
    return 0
}

# Function to start Django
start_django() {
    echo "Starting Django server..."
    
    # Kill any existing Django server
    pkill -f "manage.py runserver" 2>/dev/null || true
    sleep 2
    
    # Start Django
    cd /workspace
    python3 manage.py runserver 0.0.0.0:8000 >> /workspace/logs/django_direct.log 2>&1 &
    DJANGO_PID=$!
    
    echo "Django started with PID: $DJANGO_PID"
    return 0
}

# Function to send keepalive requests
keepalive_loop() {
    echo "Starting keepalive loop..."
    
    while true; do
        # Send health check every 30 seconds to keep connection active
        curl -s -o /dev/null http://localhost:8000/health/ 2>/dev/null || true
        
        # Also ping the tunnel metrics endpoint if available
        curl -s -o /dev/null http://localhost:2000/metrics 2>/dev/null || true
        
        sleep 30
    done
}

# Cleanup function
cleanup() {
    echo ""
    echo "Shutting down services..."
    
    [ ! -z "$KEEPALIVE_PID" ] && kill $KEEPALIVE_PID 2>/dev/null
    [ ! -z "$TUNNEL_PID" ] && kill $TUNNEL_PID 2>/dev/null
    [ ! -z "$DJANGO_PID" ] && kill $DJANGO_PID 2>/dev/null
    
    echo "Services stopped"
    exit 0
}

# Trap signals
trap cleanup SIGINT SIGTERM

# Main execution
echo "Step 1: Setting up DNS..."
setup_dns

echo ""
echo "Step 2: Testing DNS..."
if ! test_dns; then
    echo "WARNING: DNS tests failed, but continuing..."
fi

echo ""
echo "Step 3: Starting services..."
start_tunnel
sleep 5

start_django
sleep 3

echo ""
echo "Step 4: Starting keepalive loop..."
keepalive_loop &
KEEPALIVE_PID=$!

echo ""
echo "==============================================="
echo "Services Running:"
echo "  Tunnel PID: $TUNNEL_PID"
echo "  Django PID: $DJANGO_PID"
echo "  Keepalive PID: $KEEPALIVE_PID"
echo "  Logs: /workspace/logs/"
echo ""
echo "This configuration includes:"
echo "  • Reliable DNS servers"
echo "  • Keep-alive connections"
echo "  • Active health checks"
echo "  • Optimized QUIC settings"
echo ""
echo "Press Ctrl+C to stop"
echo "==============================================="
echo ""

# Monitor logs for errors
tail -f "$LOG_FILE" | grep -E "(ERR|WARN|failed)" &

# Wait for processes
wait $TUNNEL_PID $DJANGO_PID