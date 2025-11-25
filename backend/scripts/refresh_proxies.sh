#!/bin/bash
# Quick script to refresh proxy lists

echo "================================"
echo "   Proxy List Refresher"
echo "================================"
echo ""

cd "$(dirname "$0")/.." || exit 1

# Default values
FETCH_LIMIT=500
VALIDATE_LIMIT=150

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --fetch-limit)
            FETCH_LIMIT="$2"
            shift 2
            ;;
        --validate-limit)
            VALIDATE_LIMIT="$2"
            shift 2
            ;;
        --test-only)
            TEST_ONLY=1
            shift
            ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --fetch-limit N       Fetch up to N proxies (default: 500)"
            echo "  --validate-limit N    Validate up to N proxies (default: 150)"
            echo "  --test-only           Only test existing proxies"
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

# Run proxy manager
if [ "$TEST_ONLY" = "1" ]; then
    echo "Testing existing proxies..."
    python3 proxy_manager.py --test
else
    echo "Fetching up to $FETCH_LIMIT proxies..."
    echo "Validating up to $VALIDATE_LIMIT proxies..."
    echo ""
    python3 proxy_manager.py \
        --fetch-limit "$FETCH_LIMIT" \
        --validate-limit "$VALIDATE_LIMIT" \
        --storage-dir ./proxies
fi

echo ""
echo "================================"
echo "   Proxy refresh complete!"
echo "================================"
