#!/bin/bash
#
# Delete all AWS proxy instances
#

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}======================================${NC}"
echo -e "${YELLOW}  Delete AWS Proxy Pool${NC}"
echo -e "${YELLOW}======================================${NC}"
echo ""
echo -e "${RED}WARNING: This will delete ALL proxy instances!${NC}"
echo -e "${YELLOW}This action cannot be undone.${NC}"
echo ""
read -p "Are you sure? (type 'yes' to confirm): " confirm

if [ "$confirm" != "yes" ]; then
    echo "Aborted."
    exit 0
fi

echo ""
echo -e "${YELLOW}Finding proxy instances...${NC}"

# Regions
REGIONS=("us-east-1" "us-west-2" "eu-west-1" "ap-southeast-1" "ap-northeast-1")

TOTAL_DELETED=0

for REGION in "${REGIONS[@]}"; do
    echo ""
    echo -e "Checking region: ${BLUE}$REGION${NC}"

    # Get proxy instances in this region
    INSTANCES=$(aws lightsail get-instances \
        --region $REGION \
        --query "instances[?starts_with(name, 'proxy-server-')].name" \
        --output text 2>/dev/null)

    if [ -z "$INSTANCES" ]; then
        echo "  No proxy instances found"
        continue
    fi

    # Delete each instance
    for INSTANCE in $INSTANCES; do
        echo -n "  Deleting $INSTANCE ... "

        aws lightsail delete-instance \
            --region $REGION \
            --instance-name $INSTANCE \
            --no-cli-pager \
            > /dev/null 2>&1

        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✓${NC}"
            TOTAL_DELETED=$((TOTAL_DELETED + 1))
        else
            echo -e "${RED}✗${NC}"
        fi
    done
done

echo ""
echo -e "${GREEN}======================================${NC}"
echo -e "${GREEN}  Complete${NC}"
echo -e "${GREEN}======================================${NC}"
echo -e "Instances deleted: $TOTAL_DELETED"
echo ""

# Clean up local files
if [ -f "../proxies/aws_proxies.txt" ]; then
    rm ../proxies/aws_proxies.txt
    rm ../proxies/aws_proxies.json
    rm ../proxies/aws_config.txt
    echo -e "${GREEN}✓${NC} Local proxy files removed"
fi

echo ""
echo -e "${GREEN}All AWS proxy instances have been deleted.${NC}"
echo ""
