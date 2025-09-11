# Proxy Manager Documentation

## Overview

The Proxy Manager is a comprehensive system for scraping, validating, and managing HTTP/HTTPS proxies from multiple sources. It integrates seamlessly with the enhanced stock retrieval system and uses similar methods for reliability and performance.

## Features

### 1. **Multi-Source Proxy Scraping**
- **Free-proxy-list.net**: Popular free proxy list website
- **Spys.one**: Anonymous proxy lists with various anonymity levels
- **ProxyScrape**: API-based proxy provider with multiple protocols
- **Geonode**: JSON API with speed-sorted proxies
- **ProxyNova**: Country-specific proxy lists
- **GitHub Repositories**: 17+ popular proxy list repositories

### 2. **Advanced Validation**
- Multi-threaded validation (default: 50 threads)
- Response time measurement
- Success rate tracking
- Automatic retry with exponential backoff
- Health monitoring and proxy rotation

### 3. **Integration with Stock Scraper**
- Same proxy format as `enhanced_stock_retrieval_working.py`
- Automatic proxy health tracking
- Failure detection and recovery
- Load balancing across healthy proxies

## Installation

```bash
# Install required packages
pip3 install -r requirements_proxy.txt

# Make run script executable
chmod +x run_proxy_manager.sh
```

## Usage

### Quick Start

```bash
# Run single scrape and validation
./run_proxy_manager.sh scrape

# Run in scheduler mode (every 30 minutes)
./run_proxy_manager.sh schedule

# Check proxy statistics
./run_proxy_manager.sh stats

# Run maintenance on existing proxies
./run_proxy_manager.sh maintenance
```

### Direct Script Usage

#### 1. Proxy Scraper and Validator

```bash
# Basic scrape and validate
python3 proxy_scraper_validator.py

# With custom parameters
python3 proxy_scraper_validator.py -threads 100 -timeout 5 -output my_proxies.json

# Include GitHub repositories
python3 proxy_scraper_validator.py -github-repos

# Scrape only (no validation)
python3 proxy_scraper_validator.py -scrape-only

# Validate existing proxies
python3 proxy_scraper_validator.py -validate-only all_scraped_proxies.json

# Scheduler mode (runs every 30 minutes)
python3 proxy_scraper_validator.py -schedule
```

#### 2. Integrated Proxy Manager

```bash
# Single run with all features
python3 integrated_proxy_manager.py

# Scheduler mode with custom interval
python3 integrated_proxy_manager.py -schedule -interval 60

# Maintenance mode
python3 integrated_proxy_manager.py -maintenance

# Show statistics
python3 integrated_proxy_manager.py -stats
```

### Integration with Stock Scraper

The proxy manager creates output files that are directly compatible with `enhanced_stock_retrieval_working.py`:

```python
# In enhanced_stock_retrieval_working.py
proxies = load_proxies_direct('working_proxies.json')
```

## Output Files

### 1. **working_proxies.json** (Detailed Format)
```json
[
  {
    "proxy": "http://1.2.3.4:8080",
    "response_time": 1.234,
    "last_validated": "2025-09-11T10:30:00",
    "success_rate": 0.95
  }
]
```

### 2. **working_proxies_simple.json** (Simple List)
```json
[
  "http://1.2.3.4:8080",
  "http://5.6.7.8:3128"
]
```

### 3. **working_proxies.txt** (Plain Text)
```
http://1.2.3.4:8080
http://5.6.7.8:3128
```

### 4. **all_scraped_proxies.json** (All Scraped)
Contains all proxies before validation

### 5. **proxy_manager_stats.json** (Statistics)
```json
{
  "last_scrape": "2025-09-11T10:30:00",
  "last_validation": "2025-09-11T10:35:00",
  "total_scraped": 5000,
  "total_working": 500,
  "validation_history": []
}
```

## Configuration

### Command Line Arguments

| Argument | Default | Description |
|----------|---------|-------------|
| `-threads` | 50 | Number of validation threads |
| `-timeout` | 10 | Request timeout in seconds |
| `-output` | working_proxies.json | Output file name |
| `-schedule` | False | Run in scheduler mode |
| `-interval` | 30 | Schedule interval (minutes) |
| `-github-repos` | False | Include GitHub repositories |
| `-min-success-rate` | 0.6 | Minimum proxy success rate |
| `-max-response-time` | 5.0 | Maximum response time (seconds) |

### Environment Variables

```bash
# Set default proxy file for stock scraper
export PROXY_FILE_PATH="working_proxies.json"

# Set validation parameters
export PROXY_THREADS=100
export PROXY_TIMEOUT=5
```

## Advanced Features

### 1. Proxy Health Tracking

The system tracks proxy health with:
- Success/failure counts
- Response time history
- Automatic blocking of failed proxies
- Cooldown period for retry (5 minutes default)

### 2. Proxy Manager API

```python
from utils.proxy_utils import ProxyManager

# Initialize manager
manager = ProxyManager(proxy_file='working_proxies.json')

# Get healthy proxy
proxy = manager.get_healthy_proxy()

# Mark results
manager.mark_proxy_success(proxy, response_time=1.5)
manager.mark_proxy_failure(proxy, reason="Connection timeout")

# Get statistics
stats = manager.get_proxy_stats()
print(f"Success rate: {stats['success_rate']:.1f}%")
```

### 3. Stock Scraper Integration

```python
from integrated_proxy_manager import create_stock_integration_wrapper

# Create proxy provider
proxy_provider = create_stock_integration_wrapper()

# Get proxy for stock scraping
proxy = proxy_provider.get_proxy()

# Use proxy and report result
try:
    # ... use proxy for request ...
    proxy_provider.mark_success(proxy, response_time=2.0)
except Exception as e:
    proxy_provider.mark_failure(proxy)
```

## Scheduling

### Using Cron

```bash
# Run every 30 minutes
*/30 * * * * /workspace/run_proxy_manager.sh scrape >> /var/log/proxy_manager.log 2>&1

# Run maintenance every 2 hours
0 */2 * * * /workspace/run_proxy_manager.sh maintenance >> /var/log/proxy_maintenance.log 2>&1
```

### Using Systemd

Create `/etc/systemd/system/proxy-manager.service`:

```ini
[Unit]
Description=Proxy Manager Service
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/workspace
ExecStart=/usr/bin/python3 /workspace/integrated_proxy_manager.py -schedule
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

## Performance Optimization

### 1. Thread Tuning

- **Validation**: 50-100 threads recommended
- **Stock Scraping**: 15-30 threads with proxies
- **Maintenance**: 20 threads for health checks

### 2. Response Time Optimization

```python
# Set aggressive timeouts for fast proxies
args.timeout = 5
args.max_response_time = 3.0
```

### 3. Memory Management

- Rotating log files (10MB max, 5 backups)
- Limited validation history (last 100 entries)
- Efficient deduplication algorithms

## Troubleshooting

### Common Issues

1. **No proxies found**
   - Check internet connection
   - Some sources may be temporarily down
   - Try including GitHub repos: `-github-repos`

2. **Low success rate**
   - Increase timeout: `-timeout 15`
   - Reduce thread count: `-threads 25`
   - Check if proxies are region-locked

3. **Integration issues**
   - Ensure `working_proxies.json` exists
   - Check file permissions
   - Verify JSON format

### Debug Mode

```bash
# Enable debug logging
export PYTHONUNBUFFERED=1
python3 proxy_scraper_validator.py 2>&1 | tee debug.log
```

## Best Practices

1. **Regular Updates**: Run scraper every 30-60 minutes
2. **Maintenance**: Run health checks every 2 hours
3. **Monitoring**: Check logs for blocked proxies
4. **Backup**: Keep multiple proxy sources
5. **Rate Limiting**: Respect source websites

## Integration Example

### Complete Stock Scraper Integration

```python
# In enhanced_stock_retrieval_working.py

# Import proxy manager
from integrated_proxy_manager import create_stock_integration_wrapper

# Initialize at startup
proxy_provider = create_stock_integration_wrapper()

# In process_symbol_with_retry function
def process_symbol_with_retry(symbol, ticker_number, timeout=10):
    proxy = proxy_provider.get_proxy()
    
    try:
        # Use proxy for request
        result = process_with_proxy(symbol, proxy, timeout)
        proxy_provider.mark_success(proxy)
        return result
    except Exception as e:
        proxy_provider.mark_failure(proxy)
        raise
```

## API Endpoints (Future Enhancement)

The system is designed to support REST API endpoints:

```python
# GET /api/proxies
# Returns list of working proxies

# GET /api/proxies/stats
# Returns proxy statistics

# POST /api/proxies/validate
# Triggers validation cycle

# GET /api/proxies/health
# Returns health status of all proxies
```

## Contributing

To add new proxy sources:

1. Create scraper function in `proxy_scraper_validator.py`
2. Add to `scrape_all_sources()` function
3. Test with `python3 proxy_scraper_validator.py -scrape-only`

## License

This proxy manager uses the same license as the stock scanner project.

## Support

For issues or questions:
1. Check logs in `proxy_scraper_validator.log`
2. Review `proxy_manager_stats.json` for statistics
3. Run maintenance mode to diagnose proxy health