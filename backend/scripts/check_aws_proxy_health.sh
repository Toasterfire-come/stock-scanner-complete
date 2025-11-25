#!/bin/bash
#
# Check health of AWS proxy pool
#

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

PROXY_FILE="../proxies/aws_proxies.txt"

if [ ! -f "$PROXY_FILE" ]; then
    echo -e "${RED}Error: Proxy file not found: $PROXY_FILE${NC}"
    echo "Run ./setup_aws_proxies.sh first"
    exit 1
fi

echo -e "${BLUE}======================================${NC}"
echo -e "${BLUE}  AWS Proxy Health Check${NC}"
echo -e "${BLUE}======================================${NC}"
echo ""

WORKING=0
FAILED=0
TOTAL=0

while IFS= read -r proxy_url; do
    [ -z "$proxy_url" ] && continue

    TOTAL=$((TOTAL + 1))

    # Extract IP for display
    IP=$(echo "$proxy_url" | grep -oP '(?<=@)[^:]+')

    # Test proxy with Yahoo Finance
    echo -n "Testing $IP ... "

    HTTP_CODE=$(curl -x "$proxy_url" \
        -s -o /dev/null \
        -w "%{http_code}" \
        --max-time 10 \
        --connect-timeout 5 \
        "https://query2.finance.yahoo.com/v10/finance/quoteSummary/AAPL?modules=price" \
        2>/dev/null)

    if [ "$HTTP_CODE" = "200" ]; then
        echo -e "${GREEN}✓ OK${NC} (HTTP $HTTP_CODE)"
        WORKING=$((WORKING + 1))
    else
        echo -e "${RED}✗ FAILED${NC} (HTTP ${HTTP_CODE:-timeout})"
        FAILED=$((FAILED + 1))
    fi
done < "$PROXY_FILE"

echo ""
echo -e "${BLUE}======================================${NC}"
echo -e "${BLUE}  Summary${NC}"
echo -e "${BLUE}======================================${NC}"
echo -e "Total proxies:   $TOTAL"
echo -e "Working:         ${GREEN}$WORKING${NC}"
echo -e "Failed:          ${RED}$FAILED${NC}"
echo -e "Success rate:    $(echo "scale=1; $WORKING * 100 / $TOTAL" | bc)%"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All proxies are healthy!${NC}"
elif [ $WORKING -eq 0 ]; then
    echo -e "${RED}✗ All proxies are down!${NC}"
    echo -e "${YELLOW}Proxies may still be initializing. Wait 2-3 minutes and try again.${NC}"
elif [ $FAILED -lt 3 ]; then
    echo -e "${YELLOW}⚠ Some proxies are down but most are working.${NC}"
else
    echo -e "${YELLOW}⚠ Multiple proxies are down. Consider rotating them:${NC}"
    echo -e "   ./rotate_dead_aws_proxies.sh"
fi
echo ""
