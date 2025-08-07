#!/bin/bash

# Start Cloudflare Tunnel and Market Hours Manager
# This script starts both the tunnel and the stock scanner components

echo "==============================================="
echo "    Stock Scanner with Cloudflare Tunnel"
echo "==============================================="
echo ""

# Check if cloudflared is installed
if ! command -v cloudflared &> /dev/null; then
    echo "❌ ERROR: cloudflared not found!"
    echo "Please install Cloudflare tunnel first:"
    echo "  Linux: wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb && sudo dpkg -i cloudflared-linux-amd64.deb"
    echo "  macOS: brew install cloudflared"
    exit 1
fi

# Check if tunnel exists
TUNNEL_NAME="django-api"
if ! cloudflared tunnel list 2>/dev/null | grep -q "$TUNNEL_NAME"; then
    echo "❌ ERROR: Tunnel '$TUNNEL_NAME' not found!"
    echo "Please run the setup script first:"
    echo "  ./setup_cloudflare_tunnel_auto.sh"
    exit 1
fi

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down services..."
    
    # Kill tunnel process
    if [ ! -z "$TUNNEL_PID" ]; then
        echo "   Stopping Cloudflare tunnel (PID: $TUNNEL_PID)..."
        kill -TERM $TUNNEL_PID 2>/dev/null
        wait $TUNNEL_PID 2>/dev/null
    fi
    
    # Kill market hours manager
    if [ ! -z "$MANAGER_PID" ]; then
        echo "   Stopping Market Hours Manager (PID: $MANAGER_PID)..."
        kill -TERM $MANAGER_PID 2>/dev/null
        wait $MANAGER_PID 2>/dev/null
    fi
    
    echo "✅ All services stopped"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

echo "🚀 Starting Cloudflare tunnel..."
cloudflared tunnel run $TUNNEL_NAME &
TUNNEL_PID=$!

# Wait a moment for tunnel to start
sleep 3

# Check if tunnel started successfully
if ! ps -p $TUNNEL_PID > /dev/null 2>&1; then
    echo "❌ ERROR: Failed to start Cloudflare tunnel"
    exit 1
fi

echo "✅ Cloudflare tunnel started (PID: $TUNNEL_PID)"
echo ""

echo "🚀 Starting Market Hours Manager..."
python3 market_hours_manager.py &
MANAGER_PID=$!

# Wait a moment for manager to start
sleep 2

# Check if manager started successfully
if ! ps -p $MANAGER_PID > /dev/null 2>&1; then
    echo "❌ ERROR: Failed to start Market Hours Manager"
    cleanup
    exit 1
fi

echo "✅ Market Hours Manager started (PID: $MANAGER_PID)"
echo ""
echo "🌐 Services running:"
echo "   📡 Cloudflare Tunnel: Active"
echo "   ⏰ Market Hours Manager: Active"
echo "   🔗 Your app is accessible via Cloudflare URL"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Wait for processes to complete
wait $TUNNEL_PID $MANAGER_PID