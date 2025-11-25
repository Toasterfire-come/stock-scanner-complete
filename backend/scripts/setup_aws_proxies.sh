#!/bin/bash
#
# AWS Lightsail Rotating Proxy Setup
# Easy one-command setup for rotating proxies using AWS credits
#

set -e

# Configuration
NUM_PROXIES=${NUM_PROXIES:-10}
INSTANCE_PLAN="nano_2_0"  # $3.50/month each
PROXY_USER="proxyuser"
PROXY_PASSWORD=${PROXY_PASSWORD:-"$(openssl rand -base64 12)"}

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}======================================${NC}"
echo -e "${BLUE}  AWS Lightsail Rotating Proxies${NC}"
echo -e "${BLUE}======================================${NC}"
echo ""

# Check prerequisites
echo -e "${YELLOW}Checking prerequisites...${NC}"

if ! command -v aws &> /dev/null; then
    echo -e "${RED}❌ AWS CLI not found${NC}"
    echo "Install: brew install awscli (macOS) or see https://aws.amazon.com/cli/"
    exit 1
fi

if ! aws sts get-caller-identity &> /dev/null; then
    echo -e "${RED}❌ AWS credentials not configured${NC}"
    echo "Run: aws configure"
    exit 1
fi

echo -e "${GREEN}✓ AWS CLI configured${NC}"

# Generate proxy install script
cat > /tmp/install_proxy.sh << 'EOF'
#!/bin/bash
set -e

# Update system
apt-get update -qq
DEBIAN_FRONTEND=noninteractive apt-get upgrade -y -qq

# Install Squid proxy
apt-get install -y -qq squid apache2-utils

# Backup original config
cp /etc/squid/squid.conf /etc/squid/squid.conf.bak

# Create Squid configuration
cat > /etc/squid/squid.conf << 'SQUID_CONFIG'
# Port configuration
http_port 3128

# Authentication
auth_param basic program /usr/lib/squid/basic_ncsa_auth /etc/squid/passwd
auth_param basic realm AWS Proxy
auth_param basic credentialsttl 2 hours
acl authenticated proxy_auth REQUIRED

# Access rules
http_access allow authenticated
http_access deny all

# Anonymize headers (hide proxy)
forwarded_for delete
request_header_access X-Forwarded-For deny all
request_header_access Via deny all
request_header_access Cache-Control deny all

# Performance tuning
cache deny all
dns_v4_first on

# Logging
access_log /var/log/squid/access.log squid
cache_log /var/log/squid/cache.log
SQUID_CONFIG

# Create password file
htpasswd -bc /etc/squid/passwd PROXY_USER_REPLACE PROXY_PASS_REPLACE

# Set permissions
chmod 640 /etc/squid/passwd
chown root:proxy /etc/squid/passwd

# Restart Squid
systemctl restart squid
systemctl enable squid

# Configure firewall
ufw --force enable
ufw allow 3128/tcp
ufw allow 22/tcp

echo "Proxy setup complete!"
EOF

# Replace placeholders
sed -i "s/PROXY_USER_REPLACE/$PROXY_USER/g" /tmp/install_proxy.sh
sed -i "s/PROXY_PASS_REPLACE/$PROXY_PASSWORD/g" /tmp/install_proxy.sh

echo ""
echo -e "${YELLOW}Creating $NUM_PROXIES proxy servers...${NC}"
echo ""

# Regions to distribute across (5 regions for better geo-distribution)
REGIONS=("us-east-1" "us-west-2" "eu-west-1" "ap-southeast-1" "ap-northeast-1")

# Create instances
for i in $(seq 1 $NUM_PROXIES); do
    # Rotate through regions
    REGION_INDEX=$(( ($i - 1) % ${#REGIONS[@]} ))
    REGION="${REGIONS[$REGION_INDEX]}"
    INSTANCE_NAME="proxy-server-$i"

    echo -e "Creating ${GREEN}$INSTANCE_NAME${NC} in ${BLUE}$REGION${NC}..."

    # Create Lightsail instance
    aws lightsail create-instances \
        --region $REGION \
        --instance-names $INSTANCE_NAME \
        --availability-zone ${REGION}a \
        --blueprint-id ubuntu_22_04 \
        --bundle-id $INSTANCE_PLAN \
        --user-data file:///tmp/install_proxy.sh \
        --tags key=Project,value=ProxyPool key=AutoCreated,value=true \
        --no-cli-pager \
        > /dev/null 2>&1

    if [ $? -eq 0 ]; then
        echo -e "  ${GREEN}✓${NC} Instance created"
    else
        echo -e "  ${RED}✗${NC} Failed to create instance"
    fi

    # Small delay to avoid rate limiting
    sleep 1
done

# Cleanup temp file
rm /tmp/install_proxy.sh

echo ""
echo -e "${YELLOW}Waiting for instances to initialize...${NC}"
echo -e "${YELLOW}This takes ~3 minutes (installing software)${NC}"
sleep 180

echo ""
echo -e "${YELLOW}Collecting proxy information...${NC}"
echo ""

# Create output directory
mkdir -p ../proxies

# Create output files
OUTPUT_FILE="../proxies/aws_proxies.txt"
JSON_FILE="../proxies/aws_proxies.json"
CONFIG_FILE="../proxies/aws_config.txt"

> $OUTPUT_FILE
PROXY_ARRAY=""

# Collect proxy IPs
for i in $(seq 1 $NUM_PROXIES); do
    REGION_INDEX=$(( ($i - 1) % ${#REGIONS[@]} ))
    REGION="${REGIONS[$REGION_INDEX]}"
    INSTANCE_NAME="proxy-server-$i"

    # Get public IP
    PUBLIC_IP=$(aws lightsail get-instance \
        --region $REGION \
        --instance-name $INSTANCE_NAME \
        --query 'instance.publicIpAddress' \
        --output text 2>/dev/null || echo "")

    if [ -n "$PUBLIC_IP" ] && [ "$PUBLIC_IP" != "None" ]; then
        PROXY_URL="http://${PROXY_USER}:${PROXY_PASSWORD}@${PUBLIC_IP}:3128"
        echo "$PROXY_URL" >> $OUTPUT_FILE

        if [ -n "$PROXY_ARRAY" ]; then
            PROXY_ARRAY="${PROXY_ARRAY},"
        fi
        PROXY_ARRAY="${PROXY_ARRAY}\"${PROXY_URL}\""

        echo -e "  ${GREEN}✓${NC} Proxy $i: ${BLUE}$PUBLIC_IP${NC} ($REGION)"
    else
        echo -e "  ${YELLOW}⚠${NC} Proxy $i: Still initializing..."
    fi
done

# Save JSON format
echo "[$PROXY_ARRAY]" | python3 -m json.tool > $JSON_FILE 2>/dev/null || echo "[$PROXY_ARRAY]" > $JSON_FILE

# Save configuration
cat > $CONFIG_FILE << EOF
AWS Proxy Pool Configuration
==============================
Created: $(date)
Number of proxies: $NUM_PROXIES
Username: $PROXY_USER
Password: $PROXY_PASSWORD
Monthly cost: \$$(echo "$NUM_PROXIES * 3.5" | bc) (~\$3.50 per proxy)

Proxy files:
- $OUTPUT_FILE (text list)
- $JSON_FILE (JSON format)

To test a proxy:
  curl -x "http://$PROXY_USER:$PROXY_PASSWORD@[IP]:3128" https://api.ipify.org

To use with scanner:
  python3 enhanced_scanner_with_proxies.py

To check proxy health:
  ./check_aws_proxy_health.sh

To delete all proxies:
  ./delete_aws_proxies.sh
EOF

echo ""
echo -e "${GREEN}======================================${NC}"
echo -e "${GREEN}  Setup Complete!${NC}"
echo -e "${GREEN}======================================${NC}"
echo ""
echo -e "${BLUE}Proxies created:${NC} $NUM_PROXIES"
echo -e "${BLUE}Monthly cost:${NC} ~\$$(echo "$NUM_PROXIES * 3.5" | bc) (covered by AWS credits)"
echo ""
echo -e "${BLUE}Files created:${NC}"
echo -e "  • $OUTPUT_FILE"
echo -e "  • $JSON_FILE"
echo -e "  • $CONFIG_FILE"
echo ""
echo -e "${BLUE}Proxy credentials:${NC}"
echo -e "  Username: ${GREEN}$PROXY_USER${NC}"
echo -e "  Password: ${GREEN}$PROXY_PASSWORD${NC}"
echo ""
echo -e "${YELLOW}⚠️  Save these credentials! They're needed to use the proxies.${NC}"
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo -e "  1. Test: ${GREEN}./check_aws_proxy_health.sh${NC}"
echo -e "  2. Scan: ${GREEN}python3 ../enhanced_scanner_with_proxies.py --limit 100${NC}"
echo ""
