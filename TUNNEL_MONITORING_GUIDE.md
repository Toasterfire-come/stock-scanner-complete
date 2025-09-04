# Cloudflare Tunnel Monitoring & Recovery Guide

## Overview
This guide covers the enhanced monitoring and recovery system for the Stock Scanner API with Cloudflare tunnels.

## What's Been Implemented

### 1. Enhanced Monitoring Script (`tunnel_monitor_enhanced.sh`)
- **QUIC Timeout Detection**: Monitors for QUIC stream timeout errors and automatically restarts when threshold is exceeded
- **DNS Failure Recovery**: Detects and fixes DNS resolution issues automatically
- **Health Check System**: Regular health checks of both local and external endpoints
- **Comprehensive Logging**: All events logged to `/workspace/logs/` for debugging
- **Auto-Recovery**: Automatic restart of failed services with exponential backoff

### 2. Health Check Endpoints
New endpoints added to Django for monitoring:
- `/health/` - Basic health check with system metrics
- `/health/detailed/` - Detailed component status
- `/health/ready/` - Readiness probe for load balancers
- `/health/live/` - Simple liveness check

### 3. Error Handling Middleware
- **Circuit Breaker Pattern**: Prevents cascading failures by temporarily blocking problematic endpoints
- **Enhanced Error Logging**: Detailed error tracking with unique error IDs
- **Graceful Error Responses**: User-friendly error messages with retry information

## Quick Start

### Starting the Enhanced Monitor
```bash
# Start with enhanced monitoring
./tunnel_monitor_enhanced.sh

# Or run in background
nohup ./tunnel_monitor_enhanced.sh > /dev/null 2>&1 &
```

### Testing the System
```bash
# Run comprehensive tests
./test_monitoring.sh

# Check specific health endpoint
curl http://localhost:8000/health/detailed/
```

### Installing as System Service (Linux)
```bash
# Copy service file
sudo cp stock-scanner-tunnel.service /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable auto-start on boot
sudo systemctl enable stock-scanner-tunnel

# Start service
sudo systemctl start stock-scanner-tunnel

# Check status
sudo systemctl status stock-scanner-tunnel
```

## Troubleshooting Common Issues

### 1. QUIC Stream Timeout Errors
**Symptoms**: Logs show "failed to accept QUIC stream: timeout: no recent network activity"

**Solution**: The monitor automatically handles this by:
- Counting timeout occurrences
- Restarting tunnel when threshold (3) is exceeded
- Using optimized tunnel settings to minimize timeouts

### 2. DNS Resolution Failures
**Symptoms**: "Failed to refresh DNS" or "lookup timeout" errors

**Solution**: Monitor automatically:
- Checks DNS health every 60 seconds
- Switches to Cloudflare/Google DNS if issues detected
- Flushes DNS cache and restarts resolver

### 3. Tunnel Connection Drops
**Symptoms**: API becomes unreachable despite services running

**Solution**: 
- Monitor checks health every 30 seconds
- Automatically restarts tunnel if health check fails
- Logs all restart events for analysis

## Monitoring Dashboard

### Key Metrics to Watch
1. **Restart Count**: Check `/workspace/logs/tunnel_monitor.log` for restart frequency
2. **QUIC Timeouts**: Monitor for patterns in timeout occurrences
3. **DNS Failures**: Track DNS resolution issues
4. **Response Times**: Use health endpoints to monitor latency

### Log Files
All logs stored in `/workspace/logs/`:
- `tunnel_monitor.log` - Main monitoring events
- `tunnel_errors.log` - Error-specific logging
- `health_checks.log` - Health check results
- `cloudflared.log` - Cloudflare tunnel output
- `django.log` - Django server logs

### Checking Logs
```bash
# View recent monitoring events
tail -f /workspace/logs/tunnel_monitor.log

# Check for errors
grep ERROR /workspace/logs/tunnel_errors.log

# Monitor health checks
tail -f /workspace/logs/health_checks.log
```

## Performance Optimization

### Tunnel Settings
The enhanced monitor uses optimized settings:
- Compression disabled for lower CPU usage
- Grace period of 30s for smoother restarts
- Metrics endpoint for monitoring
- Transport log level set to warn to reduce noise

### Django Settings
- Circuit breaker prevents cascade failures
- Error tracking identifies problematic endpoints
- Health checks provide early warning of issues

## Manual Recovery Procedures

### If Automatic Recovery Fails

1. **Stop all services**:
```bash
pkill -f cloudflared
pkill -f "manage.py runserver"
```

2. **Clear DNS cache**:
```bash
sudo systemd-resolve --flush-caches
echo "nameserver 1.1.1.1" | sudo tee /etc/resolv.conf
```

3. **Check tunnel status**:
```bash
cloudflared tunnel list
cloudflared tunnel info django-api
```

4. **Restart with monitoring**:
```bash
./tunnel_monitor_enhanced.sh
```

### Emergency DNS Fix
```bash
# If DNS completely fails
sudo rm /etc/resolv.conf
echo "nameserver 1.1.1.1" | sudo tee /etc/resolv.conf
echo "nameserver 8.8.8.8" | sudo tee -a /etc/resolv.conf
sudo systemctl restart systemd-resolved
```

## Maintenance

### Regular Tasks
1. **Weekly**: Review logs for patterns
2. **Monthly**: Clear old log files
3. **Quarterly**: Update Cloudflare tunnel

### Log Rotation
```bash
# Add to crontab for automatic rotation
0 0 * * 0 find /workspace/logs -name "*.log" -mtime +7 -exec gzip {} \;
0 0 1 * * find /workspace/logs -name "*.gz" -mtime +30 -delete
```

## API Endpoints for Monitoring

### External Monitoring Services
Configure your monitoring service to check:
- `https://api.retailtradescanner.com/health/` - Every 1 minute
- `https://api.retailtradescanner.com/health/detailed/` - Every 5 minutes

### Expected Responses
```json
// Basic health check
{
  "status": "healthy",
  "timestamp": "2025-09-04T12:00:00",
  "service": "stock-scanner-api",
  "version": "1.0.0"
}

// Detailed check
{
  "status": "healthy",
  "components": {
    "database": {"status": "healthy", "latency_ms": 5.2},
    "tunnel": {"status": "running"},
    "system": {"cpu_percent": 15.2, "memory_percent": 45.3}
  }
}
```

## Support

### Common Commands
```bash
# Check service status
systemctl status stock-scanner-tunnel

# View recent logs
journalctl -u stock-scanner-tunnel -n 50

# Test tunnel connectivity
curl -I https://api.retailtradescanner.com/

# Check local server
curl http://localhost:8000/health/
```

### Debug Mode
For verbose logging, edit `tunnel_monitor_enhanced.sh`:
```bash
# Change loglevel from 'info' to 'debug'
--loglevel debug
```

## Conclusion
The enhanced monitoring system provides:
- Automatic recovery from common failures
- Comprehensive logging for debugging
- Health endpoints for external monitoring
- Circuit breaker pattern for stability
- DNS failure recovery

This should significantly reduce downtime and improve the reliability of your Stock Scanner API service.