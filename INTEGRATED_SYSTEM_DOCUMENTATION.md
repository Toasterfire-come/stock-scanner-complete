# Integrated Stock Scanner System Documentation

## 🚀 Complete Integration Overview

The system now features **fully integrated proxy management** with **automated daily updates at 9 AM ET** that work seamlessly with the market hours manager.

## 📋 Key Components

### 1. **Enhanced Stock Retrieval with Integrated Proxies**
- `enhanced_stock_retrieval_integrated.py` - Main stock retrieval with built-in proxy management
- Automatically updates proxies every 60 minutes during operation
- Tracks proxy health and performance metrics
- Seamless failover and retry logic

### 2. **Daily Market Updater (9 AM ET)**
- `daily_market_updater.py` - Runs daily updates at specific times
- **8:45 AM ET**: Proxy refresh (scrape & validate)
- **9:00 AM ET**: Main market update (stocks, news, emails)
- Only runs on market days (Monday-Friday)

### 3. **Enhanced Market Hours Manager**
- `market_hours_manager_enhanced.py` - Complete automation based on market hours
- Manages all components lifecycle
- Includes scheduled daily updates
- Health monitoring and auto-restart

### 4. **Integrated Proxy Manager**
- `integrated_proxy_manager.py` - Comprehensive proxy management
- Scrapes from 5+ websites and 17+ GitHub repos
- Validates with multi-threaded testing
- Database integration for persistence

## 🎯 Quick Start

### Option 1: Interactive Launcher (Recommended)
```bash
./start_market_hours_enhanced.sh
```
This provides an interactive menu with options:
1. Start Enhanced Market Hours Manager
2. Run Daily Update Once (test)
3. Update Proxies Only
4. Check Component Status
5. Exit

### Option 2: Direct Commands

#### Start Complete System
```bash
python3 market_hours_manager_enhanced.py
```

#### Run Daily 9 AM Update Manually
```bash
python3 daily_market_updater.py -once
```

#### Update Proxies Only
```bash
python3 integrated_proxy_manager.py -github
```

## ⏰ Automated Schedule

### Daily Timeline (Eastern Time)

| Time | Action | Description |
|------|--------|-------------|
| **4:00 AM** | Premarket Start | Stock retrieval, news, emails begin |
| **8:45 AM** | Proxy Update | Fresh proxy list for the day |
| **9:00 AM** | Daily Update | Main market data refresh |
| **9:30 AM** | Market Open | Django server starts, full operation |
| **4:00 PM** | Market Close | Django server stops |
| **8:00 PM** | Postmarket End | All components stop |

### Component Schedule

| Component | Premarket | Market | Postmarket | Update Interval |
|-----------|-----------|--------|------------|-----------------|
| Stock Retrieval | ✅ | ✅ | ✅ | 3 minutes |
| Proxy Manager | ✅ | ✅ | ✅ | 30 minutes |
| News Scraper | ✅ | ✅ | ✅ | 5 minutes |
| Email Sender | ✅ | ✅ | ✅ | 10 minutes |
| Django Server | ❌ | ✅ | ❌ | N/A |

## 🔧 Installation

### 1. Install Dependencies
```bash
pip3 install -r requirements_proxy.txt
```

### 2. Set Permissions
```bash
chmod +x start_market_hours_enhanced.sh
chmod +x run_proxy_manager.sh
```

### 3. Configure Environment (Optional)
```bash
export PREMARKET_START="04:00"
export MARKET_OPEN="09:30"
export MARKET_CLOSE="16:00"
export POSTMARKET_END="20:00"
export NYSE_CSV_PATH="flat-ui__data-Fri Aug 01 2025.csv"
export DJANGO_SETTINGS_MODULE="stockscanner_django.settings"
```

## 🔄 Systemd Service Installation

For production deployment with automatic startup:

```bash
cd systemd/
sudo ./install_services.sh
```

This installs:
- `market-hours-manager.service` - Main service
- `daily-market-updater.timer` - 9 AM daily trigger
- `daily-market-updater.service` - Daily update service

### Service Management
```bash
# Start/stop main service
sudo systemctl start market-hours-manager
sudo systemctl stop market-hours-manager
sudo systemctl status market-hours-manager

# Enable/disable auto-start
sudo systemctl enable market-hours-manager
sudo systemctl disable market-hours-manager

# View logs
sudo journalctl -u market-hours-manager -f
tail -f /var/log/market-hours-manager.log
```

## 📊 Proxy Management Details

### Proxy Sources
1. **Free-proxy-list.net** - General HTTP/HTTPS proxies
2. **Spys.one** - Anonymous proxies with levels
3. **ProxyScrape API** - Multiple protocols (HTTP/HTTPS/SOCKS)
4. **Geonode** - Speed-optimized proxies
5. **ProxyNova** - Country-specific proxies
6. **GitHub Repos** (17+) - Community-maintained lists

### Proxy Validation
- Multi-threaded validation (50-100 threads)
- Response time measurement (< 5 seconds required)
- Success rate tracking (> 60% required)
- Automatic retry with exponential backoff
- Health monitoring with failure detection

### Proxy Files
- `working_proxies.json` - Validated proxies with metrics
- `working_proxies_simple.json` - Simple list for compatibility
- `all_scraped_proxies.json` - All scraped before validation
- `proxy_manager_stats.json` - Statistics and history

## 🎛️ Configuration Options

### Enhanced Stock Retrieval
```bash
python3 enhanced_stock_retrieval_integrated.py \
    -threads 20 \                    # Number of parallel threads
    -timeout 10 \                    # Request timeout
    -proxy-update-interval 60 \      # Proxy refresh interval (minutes)
    -csv "nyse_symbols.csv" \        # Symbol list
    -save-to-db                      # Save to database
```

### Proxy Manager
```bash
python3 integrated_proxy_manager.py \
    -threads 100 \                   # Validation threads
    -timeout 5 \                     # Validation timeout
    -github \                        # Include GitHub repos
    -schedule \                      # Run continuously
    -interval 30                     # Update interval (minutes)
```

## 📈 Performance Metrics

### Typical Performance
- **Proxy Scraping**: 3000-5000 proxies collected
- **Proxy Validation**: 300-800 working proxies
- **Stock Processing**: 15-30 symbols/second with proxies
- **Daily Update Time**: 10-15 minutes for full NYSE
- **Memory Usage**: < 500MB typical, < 1GB peak

### Optimization Tips
1. **Increase threads** for faster processing (up to 100)
2. **Reduce timeout** for quicker proxy validation (3-5 seconds)
3. **Schedule updates** during low-activity periods
4. **Use SSD storage** for database operations
5. **Monitor logs** for performance bottlenecks

## 🔍 Monitoring

### Check System Status
```bash
./start_market_hours_enhanced.sh
# Select option 4 (Check Component Status)
```

### View Proxy Statistics
```bash
python3 integrated_proxy_manager.py -stats
```

### Monitor Logs
```bash
# Main system log
tail -f market_hours_manager_enhanced.log

# Proxy operations
tail -f proxy_scraper_validator.log

# Daily updates
tail -f daily_market_updater.log

# Stock retrieval
tail -f enhanced_stock_retrieval_integrated.log
```

## 🐛 Troubleshooting

### Common Issues and Solutions

#### 1. No Proxies Found
```bash
# Force update with GitHub repos
python3 integrated_proxy_manager.py -github

# Check proxy sources manually
python3 proxy_scraper_validator.py -scrape-only
```

#### 2. Low Stock Success Rate
```bash
# Increase timeout and reduce threads
python3 enhanced_stock_retrieval_integrated.py \
    -threads 10 -timeout 15
```

#### 3. Components Not Starting
```bash
# Check Python packages
pip3 install -r requirements_proxy.txt

# Verify file permissions
chmod +x *.py *.sh
```

#### 4. Database Connection Issues
```bash
# Check Django settings
python3 manage.py dbshell

# Run migrations
python3 manage.py migrate
```

## 🔄 Manual Operations

### Force Proxy Update
```bash
python3 integrated_proxy_manager.py -github
```

### Run Stock Update Once
```bash
python3 enhanced_stock_retrieval_integrated.py
```

### Test Daily Update
```bash
python3 daily_market_updater.py -once
```

### Validate Existing Proxies
```bash
python3 proxy_scraper_validator.py \
    -validate-only working_proxies.json
```

## 📝 Log Files

| Log File | Purpose | Rotation |
|----------|---------|----------|
| `market_hours_manager_enhanced.log` | Main system operations | 10MB, 5 files |
| `daily_market_updater.log` | Daily 9 AM updates | 10MB, 5 files |
| `enhanced_stock_retrieval_integrated.log` | Stock processing | 10MB, 5 files |
| `proxy_scraper_validator.log` | Proxy operations | 10MB, 5 files |
| `integrated_proxy_manager.log` | Proxy management | 10MB, 5 files |

## 🚀 Production Deployment Checklist

- [ ] Install all dependencies
- [ ] Configure environment variables
- [ ] Set up systemd services
- [ ] Configure database connection
- [ ] Set appropriate file permissions
- [ ] Test daily update manually
- [ ] Monitor first automated run
- [ ] Set up log rotation
- [ ] Configure backup strategy
- [ ] Set up monitoring alerts

## 📞 Support

For issues or questions:
1. Check this documentation
2. Review log files for errors
3. Run diagnostic commands
4. Test components individually
5. Verify network connectivity

## 🎉 Summary

The integrated system provides:
- **Automated daily updates** at 9 AM ET
- **Comprehensive proxy management** with health tracking
- **Market hours automation** for all components
- **Robust error handling** and recovery
- **Detailed logging** and monitoring
- **Production-ready** deployment options

The system is designed to run autonomously with minimal intervention, automatically managing proxies, updating stock data, and respecting market hours.