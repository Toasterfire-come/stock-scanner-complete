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
    
    # Kill Django server
    if [ ! -z "$SERVER_PID" ]; then
        echo "   Stopping Django server (PID: $SERVER_PID)..."
        kill -TERM $SERVER_PID 2>/dev/null
        wait $SERVER_PID 2>/dev/null
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

echo "🚀 Starting Django server..."
python3 manage.py runserver 0.0.0.0:8000 &
SERVER_PID=$!

# Wait a moment for server to start
sleep 3

# Check if server started successfully
if ! ps -p $SERVER_PID > /dev/null 2>&1; then
    echo "❌ ERROR: Failed to start Django server"
    cleanup
    exit 1
fi

echo "✅ Django server started (PID: $SERVER_PID)"
echo ""
echo "🌐 Services running:"
echo "   📡 Cloudflare Tunnel: Active"
echo "   🐍 Django Server: Active"
echo "   🔗 Your app is accessible via Cloudflare URL"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Wait for processes to complete
wait $TUNNEL_PID $MANAGER_PID