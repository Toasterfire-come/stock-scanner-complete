# 🚀 Yahoo Finance Rate Limit Optimizer

## 📋 **What This Script Does**

This comprehensive script tests **5 different strategies** to find the perfect rate limiting configuration for Yahoo Finance:

1. **🔍 Fixed Delays** - Tests various consistent delays (0.1s to 3.0s)
2. **🌐 Direct API Calls** - Tests bypassing yfinance library 
3. **⚡ Concurrent Requests** - Tests multiple threads with rate limiting
4. **💥 Burst Strategy** - Tests rapid bursts followed by longer pauses
5. **🎲 Random Delays** - Tests random delays to avoid pattern detection

## 🎯 **Expected Results**

The script will:
- Test **20+ different configurations**
- Make **500+ requests** to Yahoo Finance
- Measure success rates, response times, and optimal throughput
- Generate **implementation code** for the best strategy
- Save detailed **JSON results** for analysis

## 🚀 **How to Run**

### **Windows Command Prompt:**
```cmd
# Navigate to your project
cd C:\stock-scanner-complete

# Activate virtual environment
venv\Scripts\activate

# Install required packages (if not already installed)
pip install yfinance requests

# Run the optimizer
python yahoo_rate_limit_optimizer.py
```

### **Expected Output:**
```
⚡ Yahoo Finance Rate Limit Optimizer
🎯 Finding the perfect balance to bypass rate limits
📊 This will take approximately 10-15 minutes...

🚀 Starting Yahoo Finance Rate Limit Optimization Tests
============================================================

📊 TEST 1: Fixed Delays with yfinance
🔍 Testing yfinance with 0.1s delay, 30 requests...
   Progress: 10/30 | Success Rate: 85.0%
   Progress: 20/30 | Success Rate: 90.0%
   Progress: 30/30 | Success Rate: 93.3%
   Delay 0.1s: 93.3% success, 2.14 RPS

[... more tests ...]

============================================================
📈 OPTIMIZATION ANALYSIS
============================================================

🏆 TOP 10 STRATEGIES (by success rate + effective RPS):
------------------------------------------------------------
 1. Burst (5 requests, 2.0s pause)
    Success:  98.0% | Effective RPS:  2.45
    Main Error: ConnectionError (1 times)

 2. yfinance with 0.75s delay
    Success:  96.7% | Effective RPS:  1.28
    Main Error: empty_data (1 times)

[... more results ...]

🎯 RECOMMENDED OPTIMAL CONFIGURATION:
----------------------------------------
Method: burst
Success Rate: 98.0%
Effective RPS: 2.45

💻 IMPLEMENTATION CODE:
------------------------------
import time
import yfinance as yf

# Optimal burst configuration
BURST_SIZE = 5
BURST_DELAY = 0.1
PAUSE_BETWEEN_BURSTS = 2.0

def get_stocks_burst(symbols):
    results = []
    for i, symbol in enumerate(symbols):
        ticker = yf.Ticker(symbol)
        results.append(ticker.history(period="1d"))
        
        if (i + 1) % BURST_SIZE == 0:
            time.sleep(PAUSE_BETWEEN_BURSTS)
        else:
            time.sleep(BURST_DELAY)
    
    return results

🔧 FOR DJANGO INTEGRATION:
Update your settings.py:
YFINANCE_RATE_LIMIT = 0.75

💾 Results saved to: yahoo_rate_limit_test_results_20250122_143025.json

✅ Optimization complete!
📧 Share the results and we'll implement the optimal strategy!
```

## 📊 **What to Look For**

### **Key Metrics:**
- **Success Rate**: Percentage of successful requests
- **Effective RPS**: Real requests per second (after filtering failures)
- **Error Types**: What's causing failures
- **Total Time**: How long the strategy takes

### **Optimal Strategy Will Have:**
- ✅ **High Success Rate** (>95%)
- ✅ **Good Throughput** (>1.0 effective RPS)
- ✅ **Low Error Rate**
- ✅ **Consistent Performance**

## 🎯 **Next Steps**

1. **Run the script** and let it complete (10-15 minutes)
2. **Share the JSON results file** with the optimal configuration
3. **I'll implement** the best strategy into your stock scanner platform
4. **Test the implementation** with your live data

## 🚨 **Important Notes**

- The script is **safe** - it only reads data, doesn't modify anything
- Yahoo Finance **may temporarily rate limit** during testing (this is expected)
- Results **vary by time of day** and network conditions
- The script will **automatically retry** failed requests
- **No API keys needed** - Yahoo Finance is free

## 💡 **Pro Tips**

- Run during **off-peak hours** for better results
- Ensure **stable internet connection**
- Don't run **other stock data scripts** simultaneously
- The script **saves progress** so you can analyze results later

**Ready to find the perfect Yahoo Finance rate limit strategy?** 🚀

Run the script and share the results!