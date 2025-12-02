# YFinance Data Collection Scripts

## Overview

Two optimized yfinance data collection scripts designed to bypass rate limiting through advanced proxy techniques.

### 1. **Real-Time Scanner** (`realtime_scanner_ultra_fast.py`)
- **Goal**: Scan 5130+ tickers in under 160 seconds
- **Target Rate**: ~0.031s per ticker
- **Accuracy**: 95%+ success rate
- **Fields Collected**: 17 real-time fields (prices, volume, bid/ask)
- **Use Case**: High-frequency updates during market hours

### 2. **Daily Fundamentals Scanner** (`daily_fundamentals_scanner.py`)
- **Goal**: Comprehensive fundamental data collection
- **Max Time**: 2 hours for 5000+ tickers
- **Accuracy**: 95%+ success rate with complete data
- **Fields Collected**: 66+ fields (fundamentals, valuation, scores)
- **Use Case**: Daily updates for comprehensive stock analysis

---

## 🔥 Key Features

### Rate Limit Bypass Techniques

1. **SOCKS5h Proxy Support**
   - Forces DNS resolution through proxy (prevents DNS leakage)
   - Automatic conversion from `socks5://` to `socks5h://`
   - Eliminates "Real IP (DNS) + Proxy IP (HTTP) = FLAGGED" issue

2. **curl_cffi Integration**
   - Browser-like TLS fingerprinting
   - Mimics real browser cipher suites and HTTP/2 support
   - Significantly reduces detection by Yahoo's anti-bot systems

3. **Per-Request Proxy Rotation**
   - New proxy for every ticker request
   - Prevents pattern detection from session reuse
   - Smart proxy health monitoring and rotation

4. **Random Delays & User-Agent Rotation**
   - Random delays between requests (0.01-2s depending on scanner)
   - 5+ browser user agents in rotation
   - Realistic browser headers (Accept, DNT, Sec-Fetch-*)

5. **Intelligent Retry Logic**
   - Exponential backoff on failures
   - Automatic proxy switching on errors
   - Tracks proxy health and removes failing proxies

---

## 📋 Requirements

### Install Required Packages

```bash
# Install from requirements file
pip install -r requirements_proxy_enhanced.txt

# Or install manually
pip install yfinance>=0.2.25
pip install requests>=2.31.0
pip install PySocks>=1.7.1
pip install "requests[socks]>=2.31.0"
pip install curl_cffi>=0.6.0
pip install python-dotenv>=1.0.0
```

### System Requirements

- Python 3.8+
- Django 4.2+
- MySQL/MariaDB database
- Minimum 4GB RAM (8GB recommended)
- Multi-core CPU (for concurrent processing)

---

## 🚀 Setup

### 1. Configure Proxies

#### Option A: HTTP Proxies (Free/Existing)
Use your existing `working_proxies.json`:

```json
{
  "proxies": [
    "http://45.131.7.107:80",
    "http://199.34.230.148:80",
    "http://216.24.57.62:80"
  ]
}
```

#### Option B: SOCKS5 Proxies (Recommended)
Create `backend/socks5_proxies.json`:

```json
{
  "proxies": [
    "socks5://username:password@proxy1.provider.com:1080",
    "socks5://username:password@proxy2.provider.com:1080",
    "socks5://proxy3.provider.com:1080"
  ]
}
```

**Recommended SOCKS5 Providers**:
- **Bright Data** (formerly Luminati) - Premium residential SOCKS5
- **Smartproxy** - Affordable residential SOCKS5
- **Oxylabs** - Enterprise-grade SOCKS5
- **IPRoyal** - Budget-friendly SOCKS5
- **Soax** - Rotating residential SOCKS5

#### Option C: Environment Variables

```bash
# For real-time scanner
export REALTIME_PROXIES="socks5://user:pass@proxy1:1080,socks5://user:pass@proxy2:1080"

# For daily scanner
export DAILY_PROXIES="http://proxy1:80,http://proxy2:80,socks5://proxy3:1080"
```

#### Option D: Mix HTTP and SOCKS5
The scripts automatically detect and handle both proxy types:

```json
{
  "proxies": [
    "http://45.131.7.107:80",
    "socks5://user:pass@premium.proxy.com:1080",
    "http://199.34.230.148:80",
    "socks5://user:pass@premium2.proxy.com:1080"
  ]
}
```

---

### 2. Test Your Proxies

Use the proxy configuration helper to test and validate your proxies:

```bash
# Test proxies from working_proxies.json
python backend/proxy_config_helper.py \
  --test backend/working_proxies.json \
  --output backend/healthy_proxies.json \
  --timeout 5 \
  --workers 20 \
  --min-speed 10

# Test only proxies that work with Yahoo Finance
python backend/proxy_config_helper.py \
  --test backend/working_proxies.json \
  --output backend/yahoo_proxies.json \
  --yahoo-only \
  --min-speed 5

# Test SOCKS5 proxies
python backend/proxy_config_helper.py \
  --test backend/socks5_proxies.json \
  --output backend/healthy_socks5.json \
  --timeout 10
```

**Proxy Test Output**:
```
================================================================================
PROXY TEST RESULTS
================================================================================
Total tested: 50
Working: 32/50 (64.0%)
Failed: 18
Yahoo Finance compatible: 28/50 (56.0%)
✓ Saved 32 working proxies to backend/healthy_proxies.json
```

---

### 3. Configure Database

Ensure your Django settings are configured for MySQL:

```python
# backend/stockscanner/settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'stockscanner',
        'USER': 'root',
        'PASSWORD': '',
        'HOST': '127.0.0.1',
        'PORT': '3306',
    }
}
```

---

## 🎯 Usage

### Real-Time Scanner (Ultra-Fast)

**Goal**: Update prices every 1-3 minutes during market hours

```bash
# Run the scanner
python backend/realtime_scanner_ultra_fast.py

# Expected output:
# ================================================================================
# ULTRA-FAST REAL-TIME STOCK SCANNER
# ================================================================================
# Config: 250 threads, 2.5s timeout, 2 retries
# Target: 5130 tickers in 160s (32.06 tickers/sec)
# Starting scan at 2025-12-02 09:30:15
# --------------------------------------------------------------------------------
# Progress: 100/5130 (1.9%) | Rate: 38.46 tickers/sec | Success: 97.0% | ETA: 131s
# Progress: 200/5130 (3.9%) | Rate: 40.00 tickers/sec | Success: 96.5% | ETA: 123s
# ...
# ================================================================================
# SCAN COMPLETE
# ================================================================================
# Total time: 158.42s
# Average rate: 32.38 tickers/sec
# Success: 4909/5130 (95.69%)
# Failed: 221/5130 (4.31%)
# DB Updated: 4909
# ✓ TIME TARGET MET: 158.42s <= 160s
# ✓ SUCCESS RATE TARGET MET: 95.69% >= 95.0%
```

### Daily Fundamentals Scanner

**Goal**: Comprehensive daily updates (typically run once per day)

```bash
# Run the scanner
python backend/daily_fundamentals_scanner.py

# Expected output:
# ================================================================================
# DAILY FUNDAMENTALS STOCK SCANNER
# ================================================================================
# Config: 100 threads, 8.0s timeout, 3 retries
# Target: 5130 tickers in 7200s (0.71 tickers/sec)
# Starting scan at 2025-12-02 01:00:00
# --------------------------------------------------------------------------------
# Progress: 50/5130 (1.0%) | Rate: 0.85 tickers/sec | Success: 98.0% | ETA: 99.4 min
# Progress: 100/5130 (2.0%) | Rate: 0.87 tickers/sec | Success: 97.0% | ETA: 96.6 min
# ...
# ================================================================================
# SCAN COMPLETE
# ================================================================================
# Total time: 98.45 minutes (5907.23s)
# Average rate: 0.87 tickers/sec
# Success: 4976/5130 (97.00%)
# Failed: 154/5130 (3.00%)
# DB Updated: 4976
# ✓ TIME TARGET MET: 98.45min <= 120.0min
# ✓ SUCCESS RATE TARGET MET: 97.00% >= 95.0%
```

---

## ⚙️ Configuration

### Real-Time Scanner Config

Edit `realtime_scanner_ultra_fast.py`:

```python
@dataclass
class ScanConfig:
    max_threads: int = 250  # Aggressive concurrency
    timeout: float = 2.5  # Quick timeout
    max_retries: int = 2  # Minimal retries
    retry_delay: float = 0.1  # Fast retry
    target_time: int = 160  # Target completion time (seconds)
    min_success_rate: float = 0.95  # 95% minimum
    use_socks5h: bool = True  # Use SOCKS5h to prevent DNS leakage
    rotate_per_request: bool = True  # Rotate proxy every request
    random_delay_range: tuple = (0.01, 0.05)  # Minimal delay
```

### Daily Scanner Config

Edit `daily_fundamentals_scanner.py`:

```python
@dataclass
class ScanConfig:
    max_threads: int = 100  # Moderate concurrency
    timeout: float = 8.0  # Longer timeout
    max_retries: int = 3  # More retries
    retry_delay: float = 0.5  # Moderate retry delay
    target_time: int = 7200  # 2 hours maximum
    min_success_rate: float = 0.95  # 95% minimum
    use_socks5h: bool = True  # Use SOCKS5h to prevent DNS leakage
    rotate_per_request: bool = True  # Rotate proxy every request
    random_delay_range: tuple = (0.5, 2.0)  # Random delay
```

---

## 📊 Data Fields

### Real-Time Scanner (17 Fields)

**Critical Priority** (sub-minute updates):
- `current_price` - Current stock price
- `price_change` - Price change amount
- `price_change_percent` - Price change percentage
- `change_percent` - Change percent (compatibility)
- `volume` - Current volume
- `volume_today` - Today's volume
- `dvav` - Day Volume / Average Volume ratio

**Medium Priority** (minute updates):
- `bid_price` - Current bid price
- `ask_price` - Current ask price
- `bid_ask_spread` - Bid-ask spread
- `days_low` - Today's low price
- `days_high` - Today's high price
- `days_range` - Today's price range

**Low Priority** (hourly updates):
- `price_change_week` - Weekly price change
- `price_change_month` - Monthly price change
- `price_change_year` - Yearly price change

### Daily Fundamentals Scanner (66+ Fields)

**Basic Info** (16 fields):
- Company name, exchange, market cap, volume metrics
- 52-week range, target price, book value
- EPS, P/E ratio, dividend yield, etc.

**Fundamentals** (50+ fields stored in `valuation_json`):
- **Valuation**: P/E, Forward P/E, PEG, P/S, P/B, EV/Revenue, EV/EBITDA
- **Profitability**: Gross margin, operating margin, profit margin, ROE, ROA, ROIC
- **Growth**: Revenue growth (YoY, 3Y, 5Y), earnings growth, FCF growth
- **Financial Health**: Current ratio, quick ratio, debt/equity, interest coverage
- **Cash Flow**: Operating cash flow, free cash flow, FCF per share, FCF yield
- **Dividends**: Dividend yield, payout ratio, years of dividend growth
- **Fair Values**: DCF value, EPV value, Graham number, PEG fair value
- **Scores**: Valuation score, recommendation, confidence, strength grade

---

## 🔧 Troubleshooting

### Issue 1: Rate Limiting Detected

**Symptoms**:
```
Failed: 2000/5130 (39.0%)
Total proxy failures: 450
```

**Solutions**:
1. Add more proxies to your proxy pool
2. Use SOCKS5 proxies instead of HTTP
3. Increase random delay range: `random_delay_range: tuple = (1.0, 3.0)`
4. Reduce thread count: `max_threads: int = 50`
5. Check if proxies are residential (datacenter IPs are often blocked)

### Issue 2: All Proxies Failing

**Symptoms**:
```
Healthy proxies: 0/50
All proxies failed, resetting failure counts
```

**Solutions**:
1. Test proxies with the configuration helper:
   ```bash
   python backend/proxy_config_helper.py --test backend/working_proxies.json --yahoo-only
   ```
2. Try running without proxies temporarily to verify script works
3. Check proxy provider status and credentials
4. Ensure SOCKS5 proxies are in correct format: `socks5://user:pass@host:port`

### Issue 3: DNS Leakage

**Symptoms**:
- High failure rate despite using proxies
- Yahoo Finance detecting real IP address

**Solutions**:
1. Ensure `use_socks5h: bool = True` in config
2. Use SOCKS5 proxies (automatically converted to SOCKS5h)
3. Verify DNS not leaking:
   ```python
   # The scripts automatically convert socks5:// to socks5h://
   # socks5h:// forces DNS through proxy
   ```

### Issue 4: Slow Performance

**Symptoms**:
```
Total time: 450.00s (target was 160s)
Average rate: 11.40 tickers/sec
```

**Solutions**:
1. Increase thread count: `max_threads: int = 300`
2. Reduce timeout: `timeout: float = 2.0`
3. Reduce retries: `max_retries: int = 1`
4. Use faster proxies (test with `--min-speed 5`)
5. Reduce random delay: `random_delay_range: tuple = (0, 0.01)`

### Issue 5: Database Connection Errors

**Symptoms**:
```
DB Failed: 500
Database error for AAPL: (1040, 'Too many connections')
```

**Solutions**:
1. Reduce thread count to avoid overwhelming database
2. Increase MySQL max_connections:
   ```sql
   SET GLOBAL max_connections = 500;
   ```
3. Use connection pooling in Django settings
4. Check MySQL process list: `SHOW PROCESSLIST;`

---

## 🚦 Scheduling

### Cron Jobs

**Real-Time Scanner** (every 2 minutes during market hours):
```bash
# Edit crontab
crontab -e

# Add this line (runs Mon-Fri, 9:30 AM - 4:00 PM EST)
*/2 9-16 * * 1-5 cd /home/user/stock-scanner-complete && /usr/bin/python3 backend/realtime_scanner_ultra_fast.py >> /var/log/realtime_scanner.log 2>&1
```

**Daily Fundamentals Scanner** (once daily at 1 AM):
```bash
# Edit crontab
crontab -e

# Add this line (runs every day at 1:00 AM)
0 1 * * * cd /home/user/stock-scanner-complete && /usr/bin/python3 backend/daily_fundamentals_scanner.py >> /var/log/daily_scanner.log 2>&1
```

### Systemd Service (Linux)

Create `/etc/systemd/system/realtime-scanner.service`:

```ini
[Unit]
Description=Real-Time Stock Scanner
After=network.target mysql.service

[Service]
Type=simple
User=www-data
WorkingDirectory=/home/user/stock-scanner-complete
Environment="PATH=/usr/bin:/usr/local/bin"
ExecStart=/usr/bin/python3 backend/realtime_scanner_ultra_fast.py
Restart=on-failure
RestartSec=300

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable realtime-scanner.service
sudo systemctl start realtime-scanner.service
sudo systemctl status realtime-scanner.service
```

---

## 📈 Performance Tips

### 1. Optimize Proxy Pool
- Use 50+ proxies for best results
- Mix HTTP and SOCKS5 proxies
- Prefer residential over datacenter proxies
- Test proxies regularly and remove dead ones

### 2. Tune Concurrency
- **Real-Time**: 200-300 threads for <160s target
- **Daily**: 50-100 threads for stable operation
- Monitor system resources (CPU, memory, network)

### 3. Database Optimization
- Use indexes on `ticker`, `last_updated`, `exchange`
- Enable query cache in MySQL
- Use bulk operations where possible
- Consider read replicas for high-traffic sites

### 4. Network Optimization
- Use a VPS/dedicated server with good network
- Ensure adequate bandwidth (100+ Mbps recommended)
- Use proxies geographically close to Yahoo Finance servers
- Monitor network latency

---

## 🔐 Security Notes

1. **Proxy Credentials**: Store SOCKS5 credentials in environment variables, not in code
2. **Database**: Use strong passwords and limit network access
3. **Rate Limits**: Respect Yahoo Finance ToS and rate limits
4. **Monitoring**: Log all activity for auditing
5. **Proxies**: Use reputable proxy providers to avoid malicious proxies

---

## 📝 Changelog

### v1.0.0 (2025-12-02)
- Initial release with dual scanner approach
- SOCKS5h support for DNS leak prevention
- curl_cffi integration for TLS fingerprinting
- Per-request proxy rotation
- Intelligent retry logic with exponential backoff
- Comprehensive proxy health monitoring
- Support for 66+ fundamental fields
- Real-time and daily scanning modes

---

## 🤝 Support

For issues or questions:
1. Check the troubleshooting section above
2. Test proxies with `proxy_config_helper.py`
3. Review logs for specific error messages
4. Verify yfinance package is up to date: `pip install --upgrade yfinance`

---

## 📚 Additional Resources

- **YFinance Documentation**: https://pypi.org/project/yfinance/
- **SOCKS5 Proxy Guide**: https://www.python-requests.org/en/master/user/advanced/#socks
- **curl_cffi Documentation**: https://github.com/yifeikong/curl_cffi
- **Proxy Providers**: See `socks5_proxies.json` for recommended providers

---

## License

MIT License - Use at your own risk. Ensure compliance with Yahoo Finance Terms of Service.
