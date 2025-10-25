#!/bin/bash

# DNS Resolution Fix Script for Cloudflare Tunnel
# Addresses DNS lookup timeouts for argotunnel.com and related domains

echo "=================================================="
echo "    DNS Resolution Fix for Cloudflare Tunnel"
echo "=================================================="
echo ""

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    SUDO=""
else
    SUDO="sudo"
fi

echo "🔍 Diagnosing DNS resolution issues..."

# Test current DNS resolution
echo "Testing DNS resolution for Cloudflare tunnel domains..."
for domain in "region1.v2.argotunnel.com" "region2.v2.argotunnel.com" "api.cloudflare.com" "1.1.1.1"; do
    echo -n "  Testing $domain: "
    if nslookup $domain >/dev/null 2>&1; then
        echo "✅ OK"
    else
        echo "❌ FAILED"
    fi
done

echo ""
echo "🔧 Applying DNS optimizations..."

# 1. Configure systemd-resolved for better DNS handling
if systemctl is-active --quiet systemd-resolved; then
    echo "📝 Configuring systemd-resolved..."
    
    $SUDO mkdir -p /etc/systemd/resolved.conf.d/
    
    cat << EOF | $SUDO tee /etc/systemd/resolved.conf.d/cloudflare-tunnel.conf
[Resolve]
DNS=1.1.1.1 8.8.8.8 1.0.0.1 8.8.4.4
FallbackDNS=9.9.9.9 149.112.112.112
Domains=~cloudflare.com ~argotunnel.com
DNSStubListener=yes
Cache=yes
CacheFromLocalhost=no
DNSOverTLS=yes
DNSSEC=allow-downgrade
EOF

    echo "   Restarting systemd-resolved..."
    $SUDO systemctl restart systemd-resolved
fi

# 2. Update /etc/resolv.conf with optimized settings
echo "📝 Updating /etc/resolv.conf..."

# Backup current resolv.conf
$SUDO cp /etc/resolv.conf /etc/resolv.conf.backup.$(date +%Y%m%d_%H%M%S)

# Create optimized resolv.conf
cat << EOF | $SUDO tee /etc/resolv.conf
# Cloudflare Tunnel Optimized DNS Configuration
nameserver 1.1.1.1
nameserver 8.8.8.8
nameserver 1.0.0.1
nameserver 8.8.4.4

# DNS search options
options timeout:2 attempts:3 rotate single-request-reopen
options inet6 edns0 trust-ad

# Search domains
search cloudflare.com argotunnel.com
EOF

# 3. Add static DNS entries for critical Cloudflare domains
echo "📝 Adding static DNS entries..."

# Backup hosts file
$SUDO cp /etc/hosts /etc/hosts.backup.$(date +%Y%m%d_%H%M%S)

# Add Cloudflare tunnel endpoints to hosts file
cat << 'EOF' | $SUDO tee -a /etc/hosts

# Cloudflare Tunnel DNS Optimization - Added by fix_dns_resolution.sh
198.41.192.7    region1.v2.argotunnel.com
198.41.200.73   region2.v2.argotunnel.com
198.41.200.113  region3.v2.argotunnel.com
198.41.192.77   region4.v2.argotunnel.com
104.16.132.229  api.cloudflare.com
104.16.133.229  dash.cloudflare.com
1.1.1.1         one.one.one.one
EOF

# 4. Configure network timeouts
echo "📝 Optimizing network timeouts..."

# Set kernel network parameters for better connection handling
cat << EOF | $SUDO tee /etc/sysctl.d/99-cloudflare-tunnel.conf
# Cloudflare Tunnel Network Optimizations
net.core.rmem_default = 262144
net.core.rmem_max = 16777216
net.core.wmem_default = 262144
net.core.wmem_max = 16777216
net.ipv4.tcp_rmem = 4096 87380 16777216
net.ipv4.tcp_wmem = 4096 65536 16777216
net.ipv4.tcp_congestion_control = bbr
net.ipv4.tcp_window_scaling = 1
net.ipv4.tcp_timestamps = 1
net.ipv4.tcp_sack = 1
net.ipv4.tcp_fin_timeout = 15
net.ipv4.tcp_keepalive_time = 300
net.ipv4.tcp_keepalive_probes = 5
net.ipv4.tcp_keepalive_intvl = 15
net.core.netdev_max_backlog = 30000
net.ipv4.tcp_max_syn_backlog = 30000
net.ipv4.tcp_max_tw_buckets = 2000000
net.ipv4.tcp_tw_reuse = 1
net.ipv4.tcp_slow_start_after_idle = 0
net.ipv4.ip_local_port_range = 10240 65535
EOF

# Apply the settings
$SUDO sysctl -p /etc/sysctl.d/99-cloudflare-tunnel.conf

# 5. Create a DNS monitoring script
echo "📝 Creating DNS monitoring script..."

cat << 'EOF' > dns_monitor.sh
#!/bin/bash

# DNS Health Monitor for Cloudflare Tunnel
LOG_FILE="/var/log/dns_monitor.log"
CHECK_INTERVAL=60

log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

check_dns() {
    local domain=$1
    local timeout=5
    
    if timeout $timeout nslookup $domain >/dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

restart_dns_services() {
    log_message "Restarting DNS services due to failures..."
    sudo systemctl restart systemd-resolved 2>/dev/null
    sudo systemctl restart networking 2>/dev/null || true
    sleep 5
}

# Main monitoring loop
log_message "DNS monitoring started"

while true; do
    failed_checks=0
    
    for domain in "region1.v2.argotunnel.com" "api.cloudflare.com" "1.1.1.1"; do
        if ! check_dns "$domain"; then
            log_message "DNS check failed for $domain"
            failed_checks=$((failed_checks + 1))
        fi
    done
    
    if [ $failed_checks -ge 2 ]; then
        log_message "Multiple DNS failures detected, attempting recovery..."
        restart_dns_services
    fi
    
    sleep $CHECK_INTERVAL
done
EOF

chmod +x dns_monitor.sh

# 6. Test the fixes
echo ""
echo "🧪 Testing DNS resolution after fixes..."

for domain in "region1.v2.argotunnel.com" "region2.v2.argotunnel.com" "api.cloudflare.com"; do
    echo -n "  Testing $domain: "
    if timeout 5 nslookup $domain >/dev/null 2>&1; then
        echo "✅ OK"
    else
        echo "❌ Still failing"
    fi
done

echo ""
echo "✅ DNS optimization complete!"
echo ""
echo "Applied fixes:"
echo "  • Configured optimized DNS servers (1.1.1.1, 8.8.8.8)"
echo "  • Added static DNS entries for Cloudflare domains"
echo "  • Optimized network kernel parameters"
echo "  • Configured DNS timeouts and retry logic"
echo "  • Created DNS health monitoring script"
echo ""
echo "To monitor DNS health: ./dns_monitor.sh"
echo "To revert changes: restore /etc/resolv.conf and /etc/hosts from backups"
echo ""
echo "Restart the tunnel service to apply all changes:"
echo "  ./start_tunnel.sh"