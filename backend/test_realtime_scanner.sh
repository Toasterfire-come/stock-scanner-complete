#!/bin/bash

# Test Realtime (1-min) Scanner
echo "========================================="
echo "  Testing Realtime (1-min) Scanner"
echo "========================================="
echo ""

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR" || exit 1

SCANNER="$SCRIPT_DIR/stock_retrieval/scanner_1min_hybrid.py"

if [ ! -f "$SCANNER" ]; then
    echo "❌ ERROR: Scanner not found at $SCANNER"
    exit 1
fi

echo "📍 Scanner location: $SCANNER"
echo "📁 Working directory: $SCRIPT_DIR"
echo ""

# Check market hours
current_time=$(TZ='America/New_York' date '+%H:%M')
current_hour=$(TZ='America/New_York' date '+%H')
current_minute=$(TZ='America/New_York' date '+%M')
day_of_week=$(TZ='America/New_York' date '+%u')

# Remove leading zeros
current_hour=$((10#$current_hour))
current_minute=$((10#$current_minute))

echo "⏰ Current time: $current_time EST (Day: $day_of_week)"
echo ""

# Check if market hours
is_market_hours=false
if [ "$day_of_week" -le 5 ]; then
    if [ "$current_hour" -gt 9 ] && [ "$current_hour" -lt 16 ]; then
        is_market_hours=true
    elif [ "$current_hour" -eq 9 ] && [ "$current_minute" -ge 30 ]; then
        is_market_hours=true
    fi
fi

if [ "$is_market_hours" = "true" ]; then
    echo "🟢 Market is OPEN - Scanner will fetch real-time data"
else
    echo "🔴 Market is CLOSED - Scanner may have limited data"
    echo "   (Scanner is designed to auto-exit when market is closed)"
fi

echo ""
echo "🚀 Starting Realtime Scanner (running for 90 seconds)..."
echo "   This will update real-time prices and volume"
echo "   Log output below:"
echo ""
echo "-------------------------------------------"

# Set PYTHONPATH to include parent directory
export PYTHONPATH="$SCRIPT_DIR:$PYTHONPATH"

# Run scanner with timeout
timeout 90s python3 -c "import sys; sys.path.insert(0, '$SCRIPT_DIR'); exec(open('$SCANNER').read())" 2>&1 || {
    exit_code=$?
    if [ $exit_code -eq 124 ]; then
        echo ""
        echo "-------------------------------------------"
        echo ""
        echo "✅ Scanner test complete (stopped after 90 seconds)"
        echo ""
        echo "📊 Check the output above for:"
        echo "   - Stocks processed"
        echo "   - WebSocket connection status"
        echo "   - Price updates"
        echo "   - Error messages (if any)"
        exit 0
    else
        echo ""
        echo "-------------------------------------------"
        echo ""
        echo "❌ Scanner failed with exit code: $exit_code"
        exit 1
    fi
}

echo ""
echo "-------------------------------------------"
echo ""
echo "✅ Scanner completed successfully"
