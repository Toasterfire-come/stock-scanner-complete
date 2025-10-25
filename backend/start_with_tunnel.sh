#!/bin/bash
echo "Starting Cloudflare Tunnel..."
cloudflared tunnel run django-api &
TUNNEL_PID=$!

sleep 5

echo "Starting Market Hours Manager..."
./start_market_hours.sh &
MANAGER_PID=$!

echo "Both services started!"
echo "API available at: https://api.retailtradescanner.com"
echo "Press Ctrl+C to stop"

trap 'kill $TUNNEL_PID $MANAGER_PID; exit' INT
wait
