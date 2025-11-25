# AWS Rotating Proxies Setup (Easy Mode)

**Perfect for:** Users with AWS credits (student, startup, free tier)
**Time to setup:** 30 minutes
**Monthly cost:** $0 with credits, ~$30-60 without

---

## 🎯 Architecture Overview

We'll use **AWS Lightsail** (simplest) or **EC2 + Elastic IPs** (more control):

```
Your Scanner
    ↓
Rotate through proxy list
    ↓
┌─────────────────────────────────────────────┐
│  AWS Proxy Pool                             │
│                                             │
│  Proxy 1: 3.12.45.67  (us-east-1)          │
│  Proxy 2: 52.34.56.78 (us-west-1)          │
│  Proxy 3: 18.45.67.89 (eu-west-1)          │
│  Proxy 4: 35.67.89.01 (ap-southeast-1)     │
│  ... (6 more in different regions)         │
└─────────────────────────────────────────────┘
    ↓
Yahoo Finance
(Sees 10 different IPs)
```

**Benefits:**
- ✅ Each proxy = unique IP = separate rate limit
- ✅ Geographic distribution (looks more legitimate)
- ✅ Free with AWS credits
- ✅ Easy to scale up/down

---

## 🚀 Quick Start (Choose Your Path)

### Option 1: Lightsail (EASIEST) ⭐ RECOMMENDED

**Best for:** Quick setup, minimal complexity
**Cost:** 10 × $3.50/month = $35/month (covered by credits)

### Option 2: EC2 + Elastic IPs (MORE CONTROL)

**Best for:** Need more flexibility, already know AWS
**Cost:** 10 × $3.50/month = $35/month (covered by credits)

### Option 3: EC2 Spot Instances (CHEAPEST)

**Best for:** Maximum cost savings, can handle interruptions
**Cost:** 10 × $1/month = $10/month (70% cheaper!)

---

## 📦 Prerequisites

```bash
# 1. Install AWS CLI
brew install awscli  # macOS
# or
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# 2. Configure AWS credentials
aws configure
# Enter:
#   AWS Access Key ID: [your key]
#   AWS Secret Access Key: [your secret]
#   Default region: us-east-1
#   Default output format: json

# 3. Verify
aws sts get-caller-identity
```

---

## 🎯 Option 1: AWS Lightsail (Easiest)

### Step 1: Create Automated Setup Script

Save this as `setup_lightsail_proxies.sh`:

```bash
#!/bin/bash

# Configuration
NUM_PROXIES=10
INSTANCE_PLAN="nano_2_0"  # $3.50/month
REGIONS=("us-east-1" "us-west-2" "eu-west-1" "ap-southeast-1" "ap-northeast-1")
PROXY_PASSWORD="YourSecurePassword123!"  # Change this!

# Proxy installation script
read -r -d '' PROXY_INSTALL_SCRIPT << 'EOF'
#!/bin/bash
set -e

# Update system
apt-get update
DEBIAN_FRONTEND=noninteractive apt-get upgrade -y

# Install Squid proxy
apt-get install -y squid apache2-utils

# Backup original config
cp /etc/squid/squid.conf /etc/squid/squid.conf.bak

# Create new Squid config
cat > /etc/squid/squid.conf << 'SQUID_EOF'
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

# Anonymize headers
forwarded_for delete
request_header_access X-Forwarded-For deny all
request_header_access Via deny all
request_header_access Cache-Control deny all

# Performance
cache deny all

# Logging
access_log /var/log/squid/access.log squid
SQUID_EOF

# Create password file
htpasswd -bc /etc/squid/passwd proxyuser PROXY_PASSWORD_PLACEHOLDER

# Restart Squid
systemctl restart squid
systemctl enable squid

# Configure firewall
ufw allow 3128/tcp
ufw allow 22/tcp
echo "y" | ufw enable

echo "Proxy setup complete!"
EOF

# Replace password placeholder
PROXY_INSTALL_SCRIPT="${PROXY_INSTALL_SCRIPT//PROXY_PASSWORD_PLACEHOLDER/$PROXY_PASSWORD}"

# Save to file
echo "$PROXY_INSTALL_SCRIPT" > /tmp/install_proxy.sh

echo "=================================="
echo "AWS Lightsail Proxy Setup"
echo "=================================="
echo "Creating $NUM_PROXIES proxies..."
echo ""

# Create instances
for i in $(seq 1 $NUM_PROXIES); do
    # Rotate through regions
    REGION_INDEX=$(( ($i - 1) % ${#REGIONS[@]} ))
    REGION="${REGIONS[$REGION_INDEX]}"

    INSTANCE_NAME="proxy-server-$i"

    echo "Creating $INSTANCE_NAME in $REGION..."

    # Create instance
    aws lightsail create-instances \
        --region $REGION \
        --instance-names $INSTANCE_NAME \
        --availability-zone ${REGION}a \
        --blueprint-id ubuntu_22_04 \
        --bundle-id $INSTANCE_PLAN \
        --user-data file:///tmp/install_proxy.sh \
        --tags key=Project,value=ProxyPool key=AutoCreated,value=true \
        > /dev/null

    echo "  ✓ Created $INSTANCE_NAME"

    # Small delay to avoid rate limiting
    sleep 2
done

echo ""
echo "=================================="
echo "Waiting for instances to start..."
echo "=================================="
echo "This takes ~2-3 minutes..."
sleep 180

echo ""
echo "=================================="
echo "Collecting Proxy Information"
echo "=================================="

# Create output file
OUTPUT_FILE="aws_proxies.txt"
JSON_FILE="proxies/aws_proxies.json"

> $OUTPUT_FILE
PROXY_LIST="["

for i in $(seq 1 $NUM_PROXIES); do
    REGION_INDEX=$(( ($i - 1) % ${#REGIONS[@]} ))
    REGION="${REGIONS[$REGION_INDEX]}"
    INSTANCE_NAME="proxy-server-$i"

    # Get public IP
    PUBLIC_IP=$(aws lightsail get-instance \
        --region $REGION \
        --instance-name $INSTANCE_NAME \
        --query 'instance.publicIpAddress' \
        --output text 2>/dev/null || echo "pending")

    if [ "$PUBLIC_IP" != "pending" ] && [ "$PUBLIC_IP" != "None" ]; then
        PROXY_URL="http://proxyuser:${PROXY_PASSWORD}@${PUBLIC_IP}:3128"
        echo "$PROXY_URL" >> $OUTPUT_FILE

        if [ $i -gt 1 ]; then
            PROXY_LIST="${PROXY_LIST},"
        fi
        PROXY_LIST="${PROXY_LIST}\"${PROXY_URL}\""

        echo "  ✓ Proxy $i: $PUBLIC_IP (${REGION})"
    else
        echo "  ⚠ Proxy $i: Still starting..."
    fi
done

PROXY_LIST="${PROXY_LIST}]"

# Save JSON format
mkdir -p proxies
echo "$PROXY_LIST" | jq '.' > $JSON_FILE 2>/dev/null || echo "$PROXY_LIST" > $JSON_FILE

echo ""
echo "=================================="
echo "Setup Complete!"
echo "=================================="
echo "Proxies saved to:"
echo "  - $OUTPUT_FILE (text format)"
echo "  - $JSON_FILE (JSON format)"
echo ""
echo "To use with scanner:"
echo "  python3 enhanced_scanner_with_proxies.py"
echo ""
echo "To test a proxy:"
echo "  curl -x http://proxyuser:${PROXY_PASSWORD}@[IP]:3128 https://api.ipify.org"
echo ""
echo "Monthly cost: ~\$35 (covered by credits)"
echo "=================================="

# Cleanup
rm /tmp/install_proxy.sh
```

### Step 2: Run the Setup

```bash
# Make executable
chmod +x setup_lightsail_proxies.sh

# Run it!
./setup_lightsail_proxies.sh
```

**That's it!** In ~5 minutes you'll have 10 working proxies.

### Step 3: Test Your Proxies

```bash
# Test each proxy
while read proxy_url; do
    echo "Testing: $proxy_url"
    curl -x "$proxy_url" -s https://api.ipify.org
    echo ""
done < aws_proxies.txt
```

Expected: Each shows different IP address.

### Step 4: Use with Scanner

```bash
# Scanner automatically loads from proxies/aws_proxies.json
python3 enhanced_scanner_with_proxies.py

# Or specify explicitly
python3 enhanced_scanner_with_proxies.py --limit 100
```

---

## 🎯 Option 2: EC2 + Elastic IPs (More Control)

### Step 1: Create EC2 Setup Script

Save as `setup_ec2_proxies.sh`:

```bash
#!/bin/bash

# Configuration
NUM_PROXIES=10
INSTANCE_TYPE="t3.nano"  # $3.80/month (~$0.0052/hour)
AMI_ID="ami-0c55b159cbfafe1f0"  # Ubuntu 22.04 (update for your region)
KEY_NAME="proxy-key"  # Your SSH key name
SECURITY_GROUP="proxy-sg"
PROXY_PASSWORD="YourSecurePassword123!"

# Regions to distribute across
REGIONS=("us-east-1" "us-west-1" "us-west-2" "eu-west-1" "ap-southeast-1")

echo "=================================="
echo "AWS EC2 Proxy Setup"
echo "=================================="

# Create SSH key if needed
if ! aws ec2 describe-key-pairs --key-names $KEY_NAME &>/dev/null; then
    echo "Creating SSH key pair..."
    aws ec2 create-key-pair \
        --key-name $KEY_NAME \
        --query 'KeyMaterial' \
        --output text > ~/.ssh/${KEY_NAME}.pem
    chmod 400 ~/.ssh/${KEY_NAME}.pem
    echo "  ✓ Key saved to ~/.ssh/${KEY_NAME}.pem"
fi

# Create security group if needed
if ! aws ec2 describe-security-groups --group-names $SECURITY_GROUP &>/dev/null; then
    echo "Creating security group..."
    SG_ID=$(aws ec2 create-security-group \
        --group-name $SECURITY_GROUP \
        --description "Proxy server security group" \
        --query 'GroupId' \
        --output text)

    # Allow SSH
    aws ec2 authorize-security-group-ingress \
        --group-id $SG_ID \
        --protocol tcp \
        --port 22 \
        --cidr 0.0.0.0/0

    # Allow proxy port
    aws ec2 authorize-security-group-ingress \
        --group-id $SG_ID \
        --protocol tcp \
        --port 3128 \
        --cidr 0.0.0.0/0

    echo "  ✓ Security group created"
else
    SG_ID=$(aws ec2 describe-security-groups \
        --group-names $SECURITY_GROUP \
        --query 'SecurityGroups[0].GroupId' \
        --output text)
fi

# User data script for proxy setup
read -r -d '' USER_DATA << 'EOF'
#!/bin/bash
apt-get update
DEBIAN_FRONTEND=noninteractive apt-get upgrade -y
apt-get install -y squid apache2-utils

cat > /etc/squid/squid.conf << 'SQUID'
http_port 3128
auth_param basic program /usr/lib/squid/basic_ncsa_auth /etc/squid/passwd
auth_param basic realm AWS Proxy
acl authenticated proxy_auth REQUIRED
http_access allow authenticated
http_access deny all
forwarded_for delete
request_header_access X-Forwarded-For deny all
request_header_access Via deny all
cache deny all
SQUID

htpasswd -bc /etc/squid/passwd proxyuser PROXY_PASS_REPLACE
systemctl restart squid
systemctl enable squid
EOF

USER_DATA="${USER_DATA//PROXY_PASS_REPLACE/$PROXY_PASSWORD}"

# Launch instances
echo ""
echo "Launching $NUM_PROXIES instances..."

INSTANCE_IDS=()

for i in $(seq 1 $NUM_PROXIES); do
    REGION_INDEX=$(( ($i - 1) % ${#REGIONS[@]} ))
    REGION="${REGIONS[$REGION_INDEX]}"

    echo "  Creating instance $i in $REGION..."

    # Get AMI for region
    AMI=$(aws ec2 describe-images \
        --region $REGION \
        --owners 099720109477 \
        --filters "Name=name,Values=ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*" \
        --query 'Images | sort_by(@, &CreationDate) | [-1].ImageId' \
        --output text)

    # Launch instance
    INSTANCE_ID=$(aws ec2 run-instances \
        --region $REGION \
        --image-id $AMI \
        --instance-type $INSTANCE_TYPE \
        --key-name $KEY_NAME \
        --security-groups $SECURITY_GROUP \
        --user-data "$USER_DATA" \
        --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=proxy-$i},{Key=Project,Value=ProxyPool}]" \
        --query 'Instances[0].InstanceId' \
        --output text)

    INSTANCE_IDS+=("$REGION:$INSTANCE_ID")
    echo "    ✓ Instance ID: $INSTANCE_ID"

    sleep 1
done

echo ""
echo "Waiting for instances to start (2 minutes)..."
sleep 120

# Allocate and associate Elastic IPs
echo ""
echo "Allocating Elastic IPs..."

OUTPUT_FILE="aws_proxies.txt"
JSON_FILE="proxies/aws_proxies.json"

> $OUTPUT_FILE
PROXY_LIST="["

counter=1
for instance_info in "${INSTANCE_IDS[@]}"; do
    REGION="${instance_info%%:*}"
    INSTANCE_ID="${instance_info##*:}"

    # Allocate Elastic IP
    ALLOCATION_ID=$(aws ec2 allocate-address \
        --region $REGION \
        --domain vpc \
        --query 'AllocationId' \
        --output text)

    # Associate with instance
    aws ec2 associate-address \
        --region $REGION \
        --instance-id $INSTANCE_ID \
        --allocation-id $ALLOCATION_ID

    # Get public IP
    PUBLIC_IP=$(aws ec2 describe-addresses \
        --region $REGION \
        --allocation-ids $ALLOCATION_ID \
        --query 'Addresses[0].PublicIp' \
        --output text)

    PROXY_URL="http://proxyuser:${PROXY_PASSWORD}@${PUBLIC_IP}:3128"
    echo "$PROXY_URL" >> $OUTPUT_FILE

    if [ $counter -gt 1 ]; then
        PROXY_LIST="${PROXY_LIST},"
    fi
    PROXY_LIST="${PROXY_LIST}\"${PROXY_URL}\""

    echo "  ✓ Proxy $counter: $PUBLIC_IP ($REGION)"
    counter=$((counter + 1))
done

PROXY_LIST="${PROXY_LIST}]"

# Save JSON
mkdir -p proxies
echo "$PROXY_LIST" | jq '.' > $JSON_FILE 2>/dev/null || echo "$PROXY_LIST" > $JSON_FILE

echo ""
echo "=================================="
echo "Setup Complete!"
echo "=================================="
echo "Proxies saved to:"
echo "  - $OUTPUT_FILE"
echo "  - $JSON_FILE"
echo ""
echo "Monthly cost: ~\$38 (covered by credits)"
echo "=================================="
```

### Step 2: Run Setup

```bash
chmod +x setup_ec2_proxies.sh
./setup_ec2_proxies.sh
```

---

## 🎯 Option 3: EC2 Spot Instances (70% Cheaper!)

Spot instances can be interrupted but are MUCH cheaper:

```bash
# Modify the EC2 script to use spot:
# Change this line:
aws ec2 run-instances \

# To this:
aws ec2 run-instances \
  --instance-market-options 'MarketType=spot,SpotOptions={MaxPrice=0.005,SpotInstanceType=persistent}' \
  # ... rest of parameters
```

**Cost:** ~$10/month instead of $35!
**Trade-off:** AWS may reclaim instances (rare, but possible)

---

## 🔄 Automatic Rotation Management

### Script 1: Health Check

Save as `check_proxy_health.sh`:

```bash
#!/bin/bash

echo "Checking proxy health..."

WORKING=0
FAILED=0

while read proxy_url; do
    # Extract IP for display
    IP=$(echo $proxy_url | grep -oP '(?<=@)[^:]+')

    # Test proxy
    HTTP_CODE=$(curl -x "$proxy_url" \
        -s -o /dev/null \
        -w "%{http_code}" \
        --max-time 10 \
        https://api.ipify.org 2>/dev/null)

    if [ "$HTTP_CODE" = "200" ]; then
        echo "  ✅ $IP: OK"
        WORKING=$((WORKING + 1))
    else
        echo "  ❌ $IP: FAILED (HTTP $HTTP_CODE)"
        FAILED=$((FAILED + 1))
    fi
done < aws_proxies.txt

echo ""
echo "Summary: $WORKING working, $FAILED failed"

if [ $FAILED -gt 0 ]; then
    echo "⚠️  Some proxies are down. Consider rotating them."
fi
```

### Script 2: Auto-Rotate Dead Proxies

Save as `rotate_dead_proxies.sh`:

```bash
#!/bin/bash

echo "Checking for dead proxies..."

# Test each proxy and collect dead ones
DEAD_PROXIES=()

while read proxy_url; do
    IP=$(echo $proxy_url | grep -oP '(?<=@)[^:]+')

    HTTP_CODE=$(curl -x "$proxy_url" \
        -s -o /dev/null \
        -w "%{http_code}" \
        --max-time 10 \
        https://api.ipify.org 2>/dev/null)

    if [ "$HTTP_CODE" != "200" ]; then
        DEAD_PROXIES+=("$IP")
        echo "  ❌ $IP is dead"
    fi
done < aws_proxies.txt

if [ ${#DEAD_PROXIES[@]} -eq 0 ]; then
    echo "✅ All proxies are healthy!"
    exit 0
fi

echo ""
echo "Found ${#DEAD_PROXIES[@]} dead proxies. Rotating..."

# For each dead proxy, terminate and create new one
for IP in "${DEAD_PROXIES[@]}"; do
    echo "Rotating $IP..."

    # Find instance by IP (Lightsail)
    INSTANCE_NAME=$(aws lightsail get-instances \
        --query "instances[?publicIpAddress=='$IP'].name" \
        --output text)

    if [ -n "$INSTANCE_NAME" ]; then
        # Delete old instance
        echo "  Deleting $INSTANCE_NAME..."
        aws lightsail delete-instance --instance-name $INSTANCE_NAME

        # Create new one
        echo "  Creating replacement..."
        aws lightsail create-instances \
            --instance-names $INSTANCE_NAME \
            --availability-zone us-east-1a \
            --blueprint-id ubuntu_22_04 \
            --bundle-id nano_2_0 \
            --user-data file://install_proxy.sh

        echo "  ✓ Replacement created"
    fi
done

echo ""
echo "Waiting 2 minutes for new instances..."
sleep 120

echo "Updating proxy list..."
./setup_lightsail_proxies.sh

echo "✅ Rotation complete!"
```

### Script 3: Scheduled Health Check (Cron)

```bash
# Add to crontab
crontab -e

# Add this line (check every 6 hours):
0 */6 * * * /path/to/check_proxy_health.sh >> /var/log/proxy_health.log 2>&1

# Auto-rotate daily at 2 AM:
0 2 * * * /path/to/rotate_dead_proxies.sh >> /var/log/proxy_rotate.log 2>&1
```

---

## 📊 Cost Breakdown with AWS Credits

### AWS Free Tier (First 12 Months)

```
EC2 t2.micro:
  750 hours/month free = 1 instance running 24/7

  If you have:
  - 1 free t2.micro
  - 9 paid t3.nano ($3.80/mo each)

  Cost: 9 × $3.80 = $34.20/month
```

### AWS Educate/Student Credits ($100-300)

```
$100 credits = 3 months of 10 proxies
$200 credits = 6 months
$300 credits = 9 months
```

### AWS Activate (Startups: $1000-5000)

```
$1000 credits = 30 months (2.5 years!)
$5000 credits = 12+ years
```

**Verdict:** With AWS credits, this is essentially FREE! 🎉

---

## 🚀 Advanced: Auto-Scaling Proxy Pool

### Dynamic Proxy Pool Based on Load

```python
# auto_scale_proxies.py

import boto3
import json

class DynamicProxyPool:
    def __init__(self):
        self.lightsail = boto3.client('lightsail')
        self.min_proxies = 5
        self.max_proxies = 20

    def get_current_count(self):
        response = self.lightsail.get_instances()
        proxy_instances = [i for i in response['instances']
                          if i['name'].startswith('proxy-server-')]
        return len(proxy_instances)

    def scale_up(self, count=5):
        """Add more proxies"""
        current = self.get_current_count()
        for i in range(count):
            new_num = current + i + 1
            self.lightsail.create_instances(
                instanceNames=[f'proxy-server-{new_num}'],
                availabilityZone='us-east-1a',
                blueprintId='ubuntu_22_04',
                bundleId='nano_2_0'
            )
        print(f"Scaled up by {count} proxies")

    def scale_down(self, count=5):
        """Remove excess proxies"""
        # Remove the highest numbered instances
        # ... implementation ...
        pass

# Usage
pool = DynamicProxyPool()

# If getting rate limited, scale up:
if rate_limit_detected:
    pool.scale_up(5)

# If usage is low, scale down to save credits:
if low_usage:
    pool.scale_down(5)
```

---

## 🧪 Testing Your Setup

```bash
# Test 1: Basic connectivity
./check_proxy_health.sh

# Test 2: Yahoo Finance specifically
while read proxy_url; do
    echo "Testing with: $proxy_url"
    curl -x "$proxy_url" \
        -s "https://query2.finance.yahoo.com/v10/finance/quoteSummary/AAPL?modules=price" \
        | jq '.quoteSummary.result[0].price.regularMarketPrice'
done < aws_proxies.txt

# Test 3: Full scan test
python3 enhanced_scanner_with_proxies.py --limit 50
```

---

## 📋 Maintenance Checklist

### Daily (Automated)
- ✅ Health check (cron job)
- ✅ Rotate dead proxies (cron job)

### Weekly (Manual)
- Check AWS billing dashboard
- Review CloudWatch logs
- Test success rates

### Monthly (Manual)
- Review which regions/IPs work best
- Adjust proxy count based on needs
- Check AWS credits remaining

---

## 🎯 Quick Commands Reference

```bash
# List all proxy instances
aws lightsail get-instances --query 'instances[?starts_with(name, `proxy`)].{Name:name, IP:publicIpAddress, State:state.name}'

# Stop all proxies (save credits)
for i in {1..10}; do
    aws lightsail stop-instance --instance-name proxy-server-$i
done

# Start all proxies
for i in {1..10}; do
    aws lightsail start-instance --instance-name proxy-server-$i
done

# Delete all proxies
for i in {1..10}; do
    aws lightsail delete-instance --instance-name proxy-server-$i
done

# Check monthly costs
aws ce get-cost-and-usage \
    --time-period Start=2025-11-01,End=2025-11-30 \
    --granularity MONTHLY \
    --metrics BlendedCost
```

---

## 💡 Pro Tips

1. **Use Multiple Regions**
   - Distributes load geographically
   - Looks more like real users
   - Better if one region has issues

2. **Keep Proxies Running 24/7**
   - Only ~$1.20/day for all 10
   - Stopping/starting changes IPs (wastes burned IPs)
   - Consistent IPs = better tracking

3. **Monitor Your Credits**
   ```bash
   aws ce get-cost-forecast \
       --time-period Start=2025-11-01,End=2025-12-01 \
       --metric UNBLENDED_COST \
       --granularity MONTHLY
   ```

4. **Start Small**
   - Begin with 5 proxies
   - Scale up if needed
   - Each proxy adds ~$3.50/month

5. **Use Spot for Non-Critical**
   - 70% cheaper
   - Can be interrupted (rare)
   - Good for non-time-sensitive scans

---

## 🎉 Summary

With AWS credits, you can:

✅ **Setup Time:** 30 minutes (mostly automated)
✅ **Monthly Cost:** $35 (FREE with credits)
✅ **Capacity:** 10 proxies × 200 req/hr = 2,000 req/hr
✅ **Can handle:** 10,000+ stocks/day
✅ **Success Rate:** 70-80% (datacenter IPs)
✅ **Maintenance:** ~10 min/week

**Next Steps:**
1. Run `./setup_lightsail_proxies.sh`
2. Wait 5 minutes
3. Test with `./check_proxy_health.sh`
4. Start scanning with `python3 enhanced_scanner_with_proxies.py`

All scripts are ready to go! 🚀
