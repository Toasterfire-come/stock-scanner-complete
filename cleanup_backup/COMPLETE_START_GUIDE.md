# Complete Yahoo Finance API Optimizer Start Guide

## Table of Contents
1. [Prerequisites & System Setup](#prerequisites--system-setup)
2. [Repository Setup](#repository-setup)
3. [Environment Configuration](#environment-configuration)
4. [Running the Optimizer](#running-the-optimizer)
5. [Understanding Results](#understanding-results)
6. [Production Deployment](#production-deployment)
7. [Troubleshooting](#troubleshooting)
8. [Advanced Configuration](#advanced-configuration)

---

## Prerequisites & System Setup

### Step 1: Check Your Operating System
```bash
# Linux/macOS
uname -a

# Windows (PowerShell)
Get-ComputerInfo | Select-Object WindowsProductName, WindowsVersion
```

### Step 2: Install Python 3.7+

#### Ubuntu/Debian:
```bash
# Update package manager
sudo apt update

# Install Python 3 and pip
sudo apt install python3 python3-pip python3-venv

# Verify installation
python3 --version
pip3 --version
```

#### CentOS/RHEL/Fedora:
```bash
# For CentOS/RHEL 8+
sudo dnf install python3 python3-pip

# For older versions
sudo yum install python3 python3-pip

# Verify installation
python3 --version
pip3 --version
```

#### macOS:
```bash
# Install Homebrew (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python
brew install python3

# Verify installation
python3 --version
pip3 --version
```

#### Windows:
1. Download Python from https://python.org/downloads/
2. **IMPORTANT**: Check "Add Python to PATH" during installation
3. Open Command Prompt and verify:
```cmd
python --version
pip --version
```

### Step 3: Install Git (if not installed)

#### Linux:
```bash
# Ubuntu/Debian
sudo apt install git

# CentOS/RHEL/Fedora
sudo dnf install git # or sudo yum install git
```

#### macOS:
```bash
# Install via Homebrew
brew install git

# Or install Xcode Command Line Tools
xcode-select --install
```

#### Windows:
Download and install from: https://git-scm.com/download/win

### Step 4: Verify Prerequisites
```bash
# Check all required tools
python3 --version # Should be 3.7+
pip3 --version # Should be present
git --version # Should be present

# Check internet connectivity
ping -c 4 google.com # Linux/macOS
ping google.com # Windows
```

---

## Repository Setup

### Step 5: Clone the Repository
```bash
# Navigate to your desired directory
cd ~/Projects # Linux/macOS
cd C:\Projects # Windows

# Clone the repository
git clone https://github.com/Toasterfire-come/stock-scanner-complete.git

# Navigate into the project
cd stock-scanner-complete

# Verify you're in the right directory
ls -la # Linux/macOS
dir # Windows

# You should see files like README.md, manage.py, requirements.txt
```

### Step 6: Create Python Virtual Environment
```bash
# Create virtual environment
python3 -m venv yahoo_optimizer_env

# Activate virtual environment
# Linux/macOS:
source yahoo_optimizer_env/bin/activate

# Windows (Command Prompt):
yahoo_optimizer_env\Scripts\activate.bat

# Windows (PowerShell):
yahoo_optimizer_env\Scripts\Activate.ps1

# Verify activation (you should see (yahoo_optimizer_env) in your prompt)
which python # Linux/macOS
where python # Windows
```

### Step 7: Install Required Dependencies
```bash
# Upgrade pip first
python -m pip install --upgrade pip

# Install core dependencies
pip install requests urllib3

# Install optional dependencies for enhanced features
pip install fake-useragent

# Verify installations
python -c "import requests; print('Requests:', requests.__version__)"
python -c "import urllib3; print('urllib3:', urllib3.__version__)"
```

---

## Environment Configuration

### Step 8: Create Necessary Directories
```bash
# Create logs directory
mkdir -p logs

# Create results directory
mkdir -p results

# Verify directory structure
ls -la # Linux/macOS
dir # Windows
```

### Step 9: Set File Permissions (Linux/macOS only)
```bash
# Make the optimizer script executable
chmod +x scripts/utils/yahoo_finance_api_optimizer_v2.py

# Verify permissions
ls -la scripts/utils/yahoo_finance_api_optimizer_v2.py
```

### Step 10: Test Basic Python Setup
```bash
# Test Python imports
python -c "
import requests
import json
import time
import statistics
print(' All core modules imported successfully')
"
```

---

## Running the Optimizer

### Step 11: Basic Test Run
```bash
# Navigate to project root (if not already there)
cd /path/to/stock-scanner-complete

# Run the optimizer with default settings
python scripts/utils/yahoo_finance_api_optimizer_v2.py
```

### Step 12: Monitor the Output
You should see output like:
```
======================================================================
ENHANCED YAHOO FINANCE API OPTIMIZER v2.0
======================================================================
Testing 4 delay configurations with 50 requests each
User Agents: 20 rotating agents
Test Symbols: 42 symbols
======================================================================

TEST 1/4: Delay 0.5s
--------------------------------------------------
Testing direct requests with 0.5s delay, 50 requests...
Progress: 1/50 | Success Rate: 100.0%
Progress: 10/50 | Success Rate: 90.0%
Progress: 20/50 | Success Rate: 85.0%
```

### Step 13: Wait for Completion
The optimizer will run 4 tests (0.5s, 1.0s, 1.5s, 2.0s delays) with 50 requests each.
Total expected runtime: 5-10 minutes depending on your internet connection.

### Step 14: Check Results Location
After completion, you'll see:
```
Results saved to: yahoo_finance_api_test_results_20240123_143022.json
Testing completed successfully!
```

---

## Understanding Results

### Step 15: Review the Generated Report
The optimizer will display a comprehensive report:
```
COMPREHENSIVE TEST RESULTS
======================================================================
Delay 0.5s: 78.0% success | 1.45 RPS | Quality: 0.89 | Avg Time: 245ms
Delay 1.0s: 92.0% success | 0.98 RPS | Quality: 0.91 | Avg Time: 198ms
Delay 1.5s: 96.0% success | 0.66 RPS | Quality: 0.93 | Avg Time: 167ms
Delay 2.0s: 98.0% success | 0.49 RPS | Quality: 0.94 | Avg Time: 152ms

OPTIMAL CONFIGURATION
--------------------------------------------------
Best Delay: 1.5s
Success Rate: 96.0%
Requests/Second: 0.66
Data Quality: 0.93
Average Response Time: 167ms
```

### Step 16: Interpret Key Metrics
- **Success Rate**: Percentage of successful API calls
- **RPS**: Requests per second (throughput)
- **Data Quality**: Score from 0-1 measuring data completeness
- **Response Time**: Average time per API call

### Step 17: Check the JSON Results File
```bash
# View the detailed results
cat yahoo_finance_api_test_results_*.json | head -50

# Or use a JSON viewer
python -m json.tool yahoo_finance_api_test_results_*.json | head -50
```

---

## Production Deployment

### Step 18: Choose Your Optimal Settings
Based on the test results, choose your delay setting:
- **High Speed** (lower delay): Better for real-time applications
- **High Reliability** (higher delay): Better for batch processing

### Step 19: Implement in Your Application
```python
import requests
import time
import random

class YahooFinanceAPI:
def __init__(self, delay=1.5): # Use your optimal delay
self.delay = delay
self.session = requests.Session()
self.user_agents = [
'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
# Add more user agents from the optimizer
]

def get_stock_data(self, symbol):
# Rotate user agent
self.session.headers.update({
'User-Agent': random.choice(self.user_agents)
})

url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
response = self.session.get(url, timeout=15)

if response.status_code == 200:
return response.json()
else:
raise Exception(f"API call failed: {response.status_code}")

def wait_between_requests(self):
time.sleep(self.delay)

# Usage example
api = YahooFinanceAPI(delay=1.5) # Use your optimal delay
data = api.get_stock_data('AAPL')
api.wait_between_requests()
```

### Step 20: Set Up Production Monitoring
```bash
# Create a monitoring script
cat > monitor_api_health.py << 'EOF'
#!/usr/bin/env python3
import requests
import time
import json
from datetime import datetime

def test_api_health():
try:
url = "https://query1.finance.yahoo.com/v8/finance/chart/AAPL"
response = requests.get(url, timeout=10)

result = {
'timestamp': datetime.now().isoformat(),
'status_code': response.status_code,
'response_time': response.elapsed.total_seconds(),
'success': response.status_code == 200
}

print(json.dumps(result, indent=2))
return result['success']

except Exception as e:
print(f"Error: {e}")
return False

if __name__ == "__main__":
test_api_health()
EOF

chmod +x monitor_api_health.py
```

---

## Troubleshooting

### Common Issues and Solutions

#### Issue 1: "requests module not found"
```bash
# Solution: Install requests
pip install requests

# Verify installation
python -c "import requests; print('OK')"
```

#### Issue 2: "Permission denied" (Linux/macOS)
```bash
# Solution: Fix permissions
chmod +x scripts/utils/yahoo_finance_api_optimizer_v2.py

# Or run with python explicitly
python scripts/utils/yahoo_finance_api_optimizer_v2.py
```

#### Issue 3: "No module named 'urllib3'"
```bash
# Solution: Install urllib3
pip install urllib3

# Or reinstall requests (includes urllib3)
pip uninstall requests urllib3
pip install requests
```

#### Issue 4: Low Success Rates
**Possible causes:**
- Internet connection issues
- Yahoo Finance temporary restrictions
- System firewall blocking requests

**Solutions:**
```bash
# Test internet connectivity
ping finance.yahoo.com

# Check firewall settings (varies by system)
# Temporarily disable firewall to test

# Try with longer delays
python scripts/utils/yahoo_finance_api_optimizer_v2.py
# Look for higher success rates with longer delays
```

#### Issue 5: SSL Certificate Errors
```bash
# Solution: Update certificates
pip install --upgrade certifi

# Or disable SSL verification (not recommended for production)
# Add verify=False to requests.get() calls
```

#### Issue 6: "fake-useragent" not found
```bash
# Solution: Install optional dependency
pip install fake-useragent

# Or modify the script to use built-in user agents only
```

### Step 21: Enable Debug Logging
```python
# Add to your script for detailed debugging
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Step 22: Test Network Connectivity
```bash
# Test specific Yahoo Finance endpoint
curl -I "https://query1.finance.yahoo.com/v8/finance/chart/AAPL"

# Should return "HTTP/2 200" or similar success status
```

---

## Advanced Configuration

### Step 23: Customize Test Parameters
You can modify the optimizer for your specific needs:

```python
# Edit the script to change default settings
optimizer = EnhancedYahooAPIOptimizer(
timeout=20, # Increase timeout for slow connections
max_retries=5, # More retries for unreliable connections
pool_size=20 # Larger pool for high-volume applications
)

# Custom delay testing
results = optimizer.run_comprehensive_test(
delays=[0.3, 0.7, 1.2, 2.5], # Your custom delays
num_requests=100 # More requests for better accuracy
)
```

### Step 24: Set Up Automated Testing
```bash
# Create a daily test script
cat > daily_api_test.sh << 'EOF'
#!/bin/bash
cd /path/to/stock-scanner-complete
source yahoo_optimizer_env/bin/activate
python scripts/utils/yahoo_finance_api_optimizer_v2.py > "logs/daily_test_$(date +%Y%m%d).log" 2>&1
EOF

chmod +x daily_api_test.sh

# Add to crontab for daily execution
# crontab -e
# Add line: 0 2 * * * /path/to/daily_api_test.sh
```

### Step 25: Integration with Django Application
```python
# In your Django settings.py
YAHOO_API_CONFIG = {
'delay': 1.5, # From your test results
'timeout': 15,
'max_retries': 3,
'user_agents': [
# Copy user agents from optimizer results
]
}

# In your Django app
from django.conf import settings
import requests
import time

class YahooFinanceService:
def __init__(self):
self.config = settings.YAHOO_API_CONFIG
self.session = requests.Session()

def fetch_stock_data(self, symbol):
# Implementation using your optimized settings
pass
```

### Step 26: Production Monitoring Setup
```python
# Create a health check endpoint
# health_check.py
import requests
import json
from datetime import datetime, timedelta

def create_health_report():
"""Generate API health report"""
test_symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN']
results = []

for symbol in test_symbols:
start_time = time.time()
try:
url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
response = requests.get(url, timeout=10)

results.append({
'symbol': symbol,
'status': 'success' if response.status_code == 200 else 'failed',
'response_time': time.time() - start_time,
'status_code': response.status_code
})
except Exception as e:
results.append({
'symbol': symbol,
'status': 'error',
'error': str(e),
'response_time': time.time() - start_time
})

return {
'timestamp': datetime.now().isoformat(),
'overall_health': all(r['status'] == 'success' for r in results),
'test_results': results
}

if __name__ == "__main__":
report = create_health_report()
print(json.dumps(report, indent=2))
```

---

## Quick Start Summary

For users who want to get started immediately:

1. **Install Python 3.7+** and **git**
2. **Clone repository**: `git clone https://github.com/Toasterfire-come/stock-scanner-complete.git`
3. **Create virtual environment**: `python3 -m venv yahoo_optimizer_env`
4. **Activate environment**: `source yahoo_optimizer_env/bin/activate` (Linux/macOS) or `yahoo_optimizer_env\Scripts\activate` (Windows)
5. **Install dependencies**: `pip install requests urllib3`
6. **Run optimizer**: `python scripts/utils/yahoo_finance_api_optimizer_v2.py`
7. **Wait 5-10 minutes** for completion
8. **Use recommended delay** from results in your production code

---

## Support

If you encounter any issues:

1. **Check the troubleshooting section** above
2. **Review the log files** in the `logs/` directory
3. **Test your internet connection** to finance.yahoo.com
4. **Verify all dependencies** are installed correctly
5. **Try running with longer delays** if success rates are low

---

## Updates and Maintenance

### Keep Your Optimizer Updated:
```bash
# Pull latest changes
git pull origin main

# Update dependencies
pip install --upgrade requests urllib3

# Run a fresh test
python scripts/utils/yahoo_finance_api_optimizer_v2.py
```

### Regular Health Checks:
- Run the optimizer monthly to check for API changes
- Monitor your production success rates
- Adjust delays if success rates drop below 90%

---

** You're now ready to use the Yahoo Finance API Optimizer in production!**

Remember: The optimal delay from your test results is your key to reliable, high-quality data extraction from Yahoo Finance.