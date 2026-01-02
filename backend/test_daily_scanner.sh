#!/bin/bash

# Test Daily Scanner
echo "========================================="
echo "  Testing Daily Scanner"
echo "========================================="
echo ""

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR" || exit 1

SCANNER="$SCRIPT_DIR/stock_retrieval/realtime_daily_with_proxies.py"

if [ ! -f "$SCANNER" ]; then
    echo "❌ ERROR: Scanner not found at $SCANNER"
    exit 1
fi

echo "📍 Scanner location: $SCANNER"
echo "📁 Working directory: $SCRIPT_DIR"
echo ""

# Check if proxy file exists
PROXY_FILE="$SCRIPT_DIR/stock_retrieval/http_proxies.txt"
if [ ! -f "$PROXY_FILE" ]; then
    echo "⚠️  WARNING: Proxy file not found: $PROXY_FILE"
    echo "   Scanner will run without proxies"
fi

echo "🚀 Starting Daily Scanner (running for 30 seconds)..."
echo "   This will update daily data for stocks"
echo "   Log output below:"
echo ""
echo "-------------------------------------------"

# Set PYTHONPATH to include parent directory
export PYTHONPATH="$SCRIPT_DIR:$PYTHONPATH"

# Run scanner with timeout
timeout 30s python3 -c "import sys; sys.path.insert(0, '$SCRIPT_DIR'); exec(open('$SCANNER').read())" 2>&1 || {
    exit_code=$?
    if [ $exit_code -eq 124 ]; then
        echo ""
        echo "-------------------------------------------"
        echo ""
        echo "✅ Scanner test complete (stopped after 30 seconds)"
        echo ""
        echo "📊 Check the output above for:"
        echo "   - Stocks processed"
        echo "   - Success rate"
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
