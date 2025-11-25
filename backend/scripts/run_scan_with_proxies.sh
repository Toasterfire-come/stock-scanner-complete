#!/bin/bash
# Run stock scanner with automatic proxy support

echo "================================"
echo "  Stock Scanner with Proxies"
echo "================================"
echo ""

cd "$(dirname "$0")/.." || exit 1

# Default values
REFRESH_PROXIES=0
LIMIT=""
THREADS=16

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --refresh)
            REFRESH_PROXIES=1
            shift
            ;;
        --limit)
            LIMIT="--limit $2"
            shift 2
            ;;
        --threads)
            THREADS="$2"
            shift 2
            ;;
        --no-proxies)
            NO_PROXIES="--no-proxies"
            shift
            ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --refresh             Refresh proxy list before scanning"
            echo "  --limit N             Scan only N stocks (for testing)"
            echo "  --threads N           Use N worker threads (default: 16)"
            echo "  --no-proxies          Disable proxy usage"
            echo "  --help                Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Build command
CMD="python3 enhanced_scanner_with_proxies.py --threads $THREADS $LIMIT $NO_PROXIES"

if [ "$REFRESH_PROXIES" = "1" ]; then
    CMD="$CMD --refresh-proxies --fetch-limit 300 --validate-limit 100"
fi

# Run scanner
echo "Running: $CMD"
echo ""
$CMD

EXIT_CODE=$?

echo ""
echo "================================"
echo "  Scan complete!"
echo "================================"

exit $EXIT_CODE
