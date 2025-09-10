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
