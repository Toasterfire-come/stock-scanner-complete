#!/bin/bash

# Simplified Start Script - Cloudflare Tunnel + Django Only
# This script starts tunnel and Django server without problematic components

echo "==============================================="
echo "    Stock Scanner (Simplified) with Tunnel"
echo "==============================================="
echo ""

# Check if cloudflared is installed
if ! command -v cloudflared &> /dev/null; then
    echo "❌ ERROR: cloudflared not found!"
    echo "Please install Cloudflare tunnel first"
    exit 1
fi

# Check if tunnel exists
TUNNEL_NAME="django-api"
if ! cloudflared tunnel list 2>/dev/null | grep -q "$TUNNEL_NAME"; then
    echo "❌ ERROR: Tunnel '$TUNNEL_NAME' not found!"
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
    
    # Kill simplified manager
    if [ ! -z "$MANAGER_PID" ]; then
        echo "   Stopping Simplified Manager (PID: $MANAGER_PID)..."
        kill -TERM $MANAGER_PID 2>/dev/null
        wait $MANAGER_PID 2>/dev/null
    fi
    
    echo "✅ All services stopped"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

echo "🚀 Starting Cloudflare tunnel..."
cloudflared tunnel --protocol http2 --edge-ip-version 4 run $TUNNEL_NAME &
TUNNEL_PID=$!

# Wait a moment for tunnel to start
sleep 3

echo "✅ Cloudflare tunnel started (PID: $TUNNEL_PID)"
echo ""

echo "🚀 Starting Simplified Market Hours Manager (Django only)..."
python3 market_hours_manager_simple.py &
MANAGER_PID=$!

# Wait a moment for manager to start
sleep 2

echo "✅ Simplified Manager started (PID: $MANAGER_PID)"
echo ""
echo "🌐 Services running:"
echo "   📡 Cloudflare Tunnel: Active"
echo "   🐍 Django Server: Active"
echo "   🔗 API accessible at: https://api.retailtradescanner.com"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Wait for processes to complete
wait $TUNNEL_PID $MANAGER_PID