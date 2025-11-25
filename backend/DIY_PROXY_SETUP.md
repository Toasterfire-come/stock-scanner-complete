# DIY Proxy Setup Guide

**⚠️ WARNING:** This is significantly more complex than using a paid service. Only do this if you have specific requirements that paid services can't meet.

---

## Prerequisites

- Domain name ($10-15/year)
- Cloud provider account (AWS/GCP/DigitalOcean)
- Basic Linux/networking knowledge
- 4-6 hours for initial setup

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Your Application                        │
└────────────────┬────────────────────────────────────────────┘
                 │
                 │ Rotates between
                 ▼
    ┌────────────────────────────────────────────────────┐
    │         DNS Load Balancer / Round Robin            │
    │   proxy1.yourdomain.com → 45.12.34.56 (Server A)   │
    │   proxy2.yourdomain.com → 78.90.12.34 (Server B)   │
    │   proxy3.yourdomain.com → 23.45.67.89 (Server C)   │
    │   ... (7 more servers)                             │
    └────────────────────────────────────────────────────┘
                 │
                 │ Each proxy has own IP
                 ▼
    ┌────────────────────────────────────────────────────┐
    │              Yahoo Finance API                      │
    │   Sees requests from 10 different IPs               │
    │   Each IP: ~100 requests/hour = OK                  │
    │   Total capacity: 1000 requests/hour                │
    └────────────────────────────────────────────────────┘
```

---

## Step 1: Provision Cloud Servers

### Using DigitalOcean (Cheapest)

```bash
# Install doctl (DigitalOcean CLI)
brew install doctl  # macOS
# or
snap install doctl  # Linux

# Authenticate
doctl auth init

# Create 10 droplets
for i in {1..10}; do
  doctl compute droplet create \
    proxy-server-$i \
    --region nyc1 \
    --size s-1vcpu-1gb \
    --image ubuntu-22-04-x64 \
    --ssh-keys YOUR_SSH_KEY_ID \
    --wait
done

# Get IP addresses
doctl compute droplet list --format Name,PublicIPv4
```

**Cost:** 10 × $6/month = $60/month

### Using AWS EC2 (More IPs Available)

```bash
# Install AWS CLI
brew install awscli

# Configure
aws configure

# Create 10 t2.micro instances
for i in {1..10}; do
  aws ec2 run-instances \
    --image-id ami-0c55b159cbfafe1f0 \
    --instance-type t2.micro \
    --key-name your-key-pair \
    --security-group-ids sg-xxxxxxxx \
    --subnet-id subnet-xxxxxxxx \
    --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=proxy-$i}]"
done

# Get IPs
aws ec2 describe-instances \
  --filters "Name=tag:Name,Values=proxy-*" \
  --query 'Reservations[].Instances[].[Tags[?Key==`Name`].Value | [0], PublicIpAddress]' \
  --output table
```

**Cost:** 10 × $8/month = $80/month

---

## Step 2: Configure DNS

### A Records Approach

```
# Add A records to your domain:
proxy1.yourdomain.com → 45.12.34.56
proxy2.yourdomain.com → 78.90.12.34
proxy3.yourdomain.com → 23.45.67.89
proxy4.yourdomain.com → 34.56.78.90
proxy5.yourdomain.com → 56.78.90.12
proxy6.yourdomain.com → 78.90.12.34
proxy7.yourdomain.com → 90.12.34.56
proxy8.yourdomain.com → 12.34.56.78
proxy9.yourdomain.com → 34.56.78.90
proxy10.yourdomain.com → 56.78.90.12
```

### DNS Round Robin (Alternative)

```
# Multiple A records for same subdomain
proxy.yourdomain.com → 45.12.34.56
proxy.yourdomain.com → 78.90.12.34
proxy.yourdomain.com → 23.45.67.89
... (7 more IPs)

# DNS will rotate automatically
```

---

## Step 3: Install Proxy Software on Each Server

### Option A: Squid Proxy (HTTP/HTTPS)

SSH into each server and run:

```bash
#!/bin/bash

# Update system
sudo apt update && sudo apt upgrade -y

# Install Squid
sudo apt install squid apache2-utils -y

# Backup original config
sudo cp /etc/squid/squid.conf /etc/squid/squid.conf.bak

# Configure Squid
sudo cat > /etc/squid/squid.conf <<EOF
# Port configuration
http_port 3128

# Access control
acl localnet src 0.0.0.0/0  # Allow all (restrict in production!)

# Authentication (optional but recommended)
auth_param basic program /usr/lib/squid/basic_ncsa_auth /etc/squid/passwd
auth_param basic realm proxy
acl authenticated proxy_auth REQUIRED

# Rules
http_access allow authenticated
http_access deny all

# Anonymize
forwarded_for delete
request_header_access X-Forwarded-For deny all
request_header_access Via deny all
request_header_access Cache-Control deny all

# Cache (optional, saves bandwidth)
cache_dir ufs /var/spool/squid 1000 16 256

# Logging
access_log /var/log/squid/access.log squid
EOF

# Create user/password for proxy auth
sudo htpasswd -c /etc/squid/passwd your_username
# Enter password when prompted

# Restart Squid
sudo systemctl restart squid
sudo systemctl enable squid

# Open firewall
sudo ufw allow 3128/tcp
sudo ufw enable

echo "Proxy server ready on port 3128"
```

### Option B: TinyProxy (Lightweight)

```bash
#!/bin/bash

# Install TinyProxy
sudo apt update
sudo apt install tinyproxy -y

# Configure
sudo cat > /etc/tinyproxy/tinyproxy.conf <<EOF
User tinyproxy
Group tinyproxy
Port 8888
Timeout 600
LogLevel Info
MaxClients 100
MinSpareServers 5
MaxSpareServers 20
StartServers 10
Allow 0.0.0.0/0  # Restrict this in production!
ViaProxyName "tinyproxy"
DisableViaHeader Yes
EOF

# Restart
sudo systemctl restart tinyproxy
sudo systemctl enable tinyproxy

# Firewall
sudo ufw allow 8888/tcp

echo "TinyProxy ready on port 8888"
```

---

## Step 4: Test Your Proxies

```bash
# Test each proxy
for i in {1..10}; do
  echo "Testing proxy$i.yourdomain.com..."

  curl -x http://your_username:your_password@proxy$i.yourdomain.com:3128 \
       -s https://api.ipify.org

  echo ""
done
```

Expected output: Different IP for each proxy server.

---

## Step 5: Integrate with Your Scanner

### Update Proxy Configuration

```python
# backend/config/diy_proxies.py

DIY_PROXIES = [
    "http://your_username:your_password@proxy1.yourdomain.com:3128",
    "http://your_username:your_password@proxy2.yourdomain.com:3128",
    "http://your_username:your_password@proxy3.yourdomain.com:3128",
    "http://your_username:your_password@proxy4.yourdomain.com:3128",
    "http://your_username:your_password@proxy5.yourdomain.com:3128",
    "http://your_username:your_password@proxy6.yourdomain.com:3128",
    "http://your_username:your_password@proxy7.yourdomain.com:3128",
    "http://your_username:your_password@proxy8.yourdomain.com:3128",
    "http://your_username:your_password@proxy9.yourdomain.com:3128",
    "http://your_username:your_password@proxy10.yourdomain.com:3128",
]

# Save to file for scanner
import json
with open('proxies/diy_proxies.json', 'w') as f:
    json.dump(DIY_PROXIES, f)
```

### Use with Scanner

```bash
# scanner will automatically load from proxies/diy_proxies.json
python3 enhanced_scanner_with_proxies.py
```

---

## Step 6: Monitoring & Maintenance

### Monitor Proxy Health

```bash
#!/bin/bash
# check_proxy_health.sh

for i in {1..10}; do
  echo "Checking proxy$i..."

  response=$(curl -x http://user:pass@proxy$i.yourdomain.com:3128 \
                  -s -w "%{http_code}" \
                  -o /dev/null \
                  https://api.ipify.org)

  if [ "$response" = "200" ]; then
    echo "  ✅ proxy$i: OK"
  else
    echo "  ❌ proxy$i: FAILED (HTTP $response)"
  fi
done
```

### Rotate Burned IPs

When a proxy gets rate-limited:

```bash
# Destroy old droplet
doctl compute droplet delete proxy-server-5 -f

# Create new one
doctl compute droplet create \
  proxy-server-5 \
  --region nyc1 \
  --size s-1vcpu-1gb \
  --image ubuntu-22-04-x64 \
  --wait

# Get new IP
NEW_IP=$(doctl compute droplet get proxy-server-5 --format PublicIPv4 --no-header)

# Update DNS
# (Use your DNS provider's API or manually update)

# Install proxy software (from Step 3)
ssh root@$NEW_IP < install_proxy.sh
```

---

## Cost Breakdown

### Initial Setup
- Domain: $12/year
- Time (4 hours × $50/hr): $200
- **Total: $212**

### Monthly Ongoing
- 10 × VPS ($6/mo): $60/month
- Monitoring time (1 hr/mo): $50/month
- **Total: $110/month**

### Annual Cost
- Year 1: $212 + ($110 × 12) = $1,532
- Year 2+: ($110 × 12) = $1,320/year

**Compare to Paid Service:**
- Paid service: $100 × 12 = $1,200/year
- No setup time
- No maintenance
- Better IP quality (residential)

**Verdict:** DIY costs MORE when you factor in your time!

---

## Limitations of DIY Approach

### 1. Datacenter IPs Are Easier to Detect

```
Your DIY proxies: Datacenter IPs
Yahoo sees:
  - IP range: Known cloud provider (AWS/GCP/DO)
  - Reverse DNS: digitalocean.com, amazonaws.com
  - Detection: "This is a proxy/bot"
  - Success rate: 70-80%

Paid residential proxies: Home ISP IPs
Yahoo sees:
  - IP range: Comcast, AT&T, Verizon (normal users)
  - Reverse DNS: Residential ISP
  - Detection: "This looks like a real person"
  - Success rate: 95-99%
```

### 2. Limited IP Pool

- Your setup: 10 IPs
- Paid service: 50,000+ IPs
- When your 10 get burned, you're stuck

### 3. Maintenance Burden

- Monitor health daily
- Rotate burned IPs weekly
- Security updates monthly
- Debugging issues: Ongoing

---

## Alternative: Hybrid Approach

Best of both worlds:

```python
# Use DIY for primary, paid as backup
proxies = [
    # Your 10 DIY proxies (cheap)
    *load_diy_proxies(),

    # Paid service for overflow (expensive but reliable)
    *load_paid_proxies() if need_backup else []
]
```

---

## Recommendation

**Unless you have specific reasons (compliance, data residency, etc.):**

1. **<1000 stocks/day:** Use direct connection (no proxies) - **FREE**
2. **1000-2000 stocks/day:** Use batching - **FREE**
3. **>2000 stocks/day:** Use paid proxy service - **$100-200/month**

**Only do DIY if:**
- ✓ You need specific geographic locations
- ✓ You have compliance requirements
- ✓ You enjoy infrastructure management
- ✓ You value control over convenience
- ✓ You're already managing servers

---

## Summary

| Approach | Cost/Month | Setup Time | Success Rate | Maintenance |
|----------|------------|------------|--------------|-------------|
| **Direct** | $0 | 0 min | 98% | None |
| **Batching** | $0 | 5 min | 95% | None |
| **DIY Proxies** | $60-80 | 4 hours | 70-80% | High |
| **Paid Proxies** | $100-200 | 5 min | 95-99% | None |

**Bottom Line:** DIY is more work and often more expensive than paid services when you factor in your time.
