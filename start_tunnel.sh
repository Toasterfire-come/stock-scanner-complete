#!/bin/bash

# Start Cloudflare Tunnel and Market Hours Manager with Enhanced Stability
# This script starts both the tunnel and the stock scanner components with retry logic

echo "==============================================="
echo "    Stock Scanner with Cloudflare Tunnel"
echo "           Enhanced Stability Version"
echo "==============================================="
echo ""

# Configuration
TUNNEL_NAME="django-api"
MAX_RETRIES=5
RETRY_DELAY=10
HEALTH_CHECK_INTERVAL=30

# Check if cloudflared is installed
if ! command -v cloudflared &> /dev/null; then
    echo "❌ ERROR: cloudflared not found!"
    echo "Please install Cloudflare tunnel first:"
    echo "  Linux: wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb && sudo dpkg -i cloudflared-linux-amd64.deb"
    echo "  macOS: brew install cloudflared"
    exit 1
fi

# Check if tunnel exists
if ! cloudflared tunnel list 2>/dev/null | grep -q "$TUNNEL_NAME"; then
    echo "❌ ERROR: Tunnel '$TUNNEL_NAME' not found!"
    echo "Please run the setup script first:"
    echo "  ./setup_cloudflare_tunnel_auto.sh"
    exit 1
fi

# Improved cleanup function
cleanup() {
    echo ""
    echo "🛑 Shutting down services..."
    
    # Kill tunnel process
    if [ ! -z "$TUNNEL_PID" ]; then
        echo "   Stopping Cloudflare tunnel (PID: $TUNNEL_PID)..."
        kill -TERM $TUNNEL_PID 2>/dev/null
        sleep 3
        kill -KILL $TUNNEL_PID 2>/dev/null
    fi
    
    # Kill Django server
    if [ ! -z "$SERVER_PID" ]; then
        echo "   Stopping Django server (PID: $SERVER_PID)..."
        kill -TERM $SERVER_PID 2>/dev/null
        sleep 3
        kill -KILL $SERVER_PID 2>/dev/null
    fi
    
    # Kill health check process
    if [ ! -z "$HEALTH_PID" ]; then
        kill -TERM $HEALTH_PID 2>/dev/null
    fi
    
    echo "✅ All services stopped"
    exit 0
}

# Function to start tunnel with retries
start_tunnel() {
    local retry_count=0
    
    while [ $retry_count -lt $MAX_RETRIES ]; do
        echo "🚀 Starting Cloudflare tunnel (attempt $((retry_count + 1))/$MAX_RETRIES)..."
        
        # Start tunnel with enhanced logging and configuration
        cloudflared tunnel --loglevel info run $TUNNEL_NAME &
        TUNNEL_PID=$!
        
        # Wait for tunnel to initialize
        sleep 5
        
        # Check if tunnel started successfully
        if ps -p $TUNNEL_PID > /dev/null 2>&1; then
            echo "✅ Cloudflare tunnel started successfully (PID: $TUNNEL_PID)"
            return 0
        else
            echo "❌ Tunnel failed to start, retrying in $RETRY_DELAY seconds..."
            retry_count=$((retry_count + 1))
            sleep $RETRY_DELAY
        fi
    done
    
    echo "❌ ERROR: Failed to start tunnel after $MAX_RETRIES attempts"
    return 1
}

# Function to start Django server
start_django() {
    echo "🚀 Starting Django server..."
    python3 manage.py runserver 0.0.0.0:8000 &
    SERVER_PID=$!
    
    # Wait for server to start
    sleep 3
    
    # Check if server started successfully
    if ps -p $SERVER_PID > /dev/null 2>&1; then
        echo "✅ Django server started successfully (PID: $SERVER_PID)"
        return 0
    else
        echo "❌ ERROR: Failed to start Django server"
        return 1
    fi
}

# Function to monitor and restart services if needed
health_monitor() {
    while true; do
        sleep $HEALTH_CHECK_INTERVAL
        
        # Check tunnel health
        if ! ps -p $TUNNEL_PID > /dev/null 2>&1; then
            echo "⚠️  Tunnel process died, attempting restart..."
            if start_tunnel; then
                echo "✅ Tunnel restarted successfully"
            else
                echo "❌ Failed to restart tunnel, exiting..."
                cleanup
                exit 1
            fi
        fi
        
        # Check Django server health
        if ! ps -p $SERVER_PID > /dev/null 2>&1; then
            echo "⚠️  Django server died, attempting restart..."
            if start_django; then
                echo "✅ Django server restarted successfully"
            else
                echo "❌ Failed to restart Django server, exiting..."
                cleanup
                exit 1
            fi
        fi
        
        # Optional: Check tunnel connectivity
        if ! cloudflared tunnel list 2>/dev/null | grep -q "$TUNNEL_NAME"; then
            echo "⚠️  Tunnel not visible in list, may need reconnection..."
        fi
    done
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Start services
if ! start_tunnel; then
    exit 1
fi

if ! start_django; then
    cleanup
    exit 1
fi

# Start health monitor in background
health_monitor &
HEALTH_PID=$!

echo ""
echo "🌐 Services running with enhanced stability:"
echo "   📡 Cloudflare Tunnel: Active (PID: $TUNNEL_PID)"
echo "   🐍 Django Server: Active (PID: $SERVER_PID)"
echo "   🔍 Health Monitor: Active (PID: $HEALTH_PID)"
echo "   🔗 Your app is accessible via Cloudflare URL"
echo ""
echo "Enhanced features:"
echo "   • Automatic retry on connection failure"
echo "   • Health monitoring every $HEALTH_CHECK_INTERVAL seconds"
echo "   • QUIC protocol for better performance"
echo "   • Graceful shutdown handling"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Wait for processes to complete
wait $TUNNEL_PID $SERVER_PID