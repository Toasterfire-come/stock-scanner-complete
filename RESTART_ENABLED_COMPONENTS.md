# Restart-Enabled Components

This document explains the enhanced components with built-in restart and scheduling capabilities, modeled after the `enhanced_stock_retrieval_working.py` script.

## Overview

All components now include:
- **Built-in scheduling** using the `schedule` library
- **Graceful shutdown** handling with signal handlers
- **Error recovery** and automatic restart capabilities
- **Command-line arguments** for configuration
- **Comprehensive logging** with separate log files

## Components

### 1. News Scraper with Restart (`news_scraper_with_restart.py`)

Enhanced version of the news scraper with scheduling and restart capabilities.

#### Features
- **Continuous Operation**: Runs in scheduler mode with `-schedule` argument
- **Configurable Intervals**: Use `-interval N` to set minutes between runs (default: 5)
- **Test Mode**: Use `-test` to limit to 10 articles per feed
- **Graceful Shutdown**: Handles Ctrl+C and SIGTERM signals properly
- **Error Recovery**: Continues running even if individual scraping attempts fail

#### Usage
```bash
# Run once
python3 news_scraper_with_restart.py

# Run continuously every 5 minutes
python3 news_scraper_with_restart.py -schedule

# Run continuously every 3 minutes
python3 news_scraper_with_restart.py -schedule -interval 3

# Test mode with limited articles
python3 news_scraper_with_restart.py -test

# Combined test and schedule mode
python3 news_scraper_with_restart.py -schedule -test -interval 2
```

#### Arguments
- `-schedule`: Enable continuous scheduling mode
- `-test`: Test mode - only scrape 10 articles per feed
- `-limit N`: Number of articles per feed (default: 50)
- `-interval N`: Schedule interval in minutes (default: 5)

#### Log File
`news_scraper_with_restart.log`

---

### 2. Email Sender with Restart (`email_sender_with_restart.py`)

Enhanced version of the email sender with scheduling and restart capabilities.

#### Features
- **Continuous Operation**: Runs in scheduler mode with `-schedule` argument
- **Configurable Intervals**: Use `-interval N` to set minutes between runs (default: 10)
- **Test Mode**: Use `-test` to limit processing (stops after 3 emails)
- **Improved Error Handling**: Better categorization and error recovery
- **Alert Limiting**: Use `-max-alerts N` to limit number of alerts processed

#### Usage
```bash
# Run once
python3 email_sender_with_restart.py

# Run continuously every 10 minutes
python3 email_sender_with_restart.py -schedule

# Run continuously every 15 minutes
python3 email_sender_with_restart.py -schedule -interval 15

# Test mode with limited processing
python3 email_sender_with_restart.py -test

# Limit number of alerts processed
python3 email_sender_with_restart.py -max-alerts 50
```

#### Arguments
- `-schedule`: Enable continuous scheduling mode
- `-test`: Test mode - process only a few alerts (stops after 3 emails)
- `-interval N`: Schedule interval in minutes (default: 10)
- `-max-alerts N`: Maximum number of alerts to process (for testing)

#### Log File
`email_sender_with_restart.log`

---

### 3. Stock Retrieval (Existing) (`enhanced_stock_retrieval_working.py`)

The original restart-enabled script that serves as the model for the others.

#### Usage
```bash
# Run once
python3 enhanced_stock_retrieval_working.py

# Run continuously every 3 minutes
python3 enhanced_stock_retrieval_working.py -schedule

# Test mode with first 100 tickers
python3 enhanced_stock_retrieval_working.py -test

# Combined mode
python3 enhanced_stock_retrieval_working.py -schedule -test
```

#### Log File
`enhanced_stock_retrieval_working.log`

## Market Hours Manager Integration

The Market Hours Manager now uses these restart-enabled versions:

```python
self.components = {
    'stock_retrieval': {
        'script': 'enhanced_stock_retrieval_working.py',
        'args': ['-schedule'],
        'active_during': ['premarket', 'market', 'postmarket'],
        'process': None
    },
    'news_scraper': {
        'script': 'news_scraper_with_restart.py',
        'args': ['-schedule', '-interval', '5'],
        'active_during': ['premarket', 'market', 'postmarket'],
        'process': None
    },
    'email_sender': {
        'script': 'email_sender_with_restart.py',
        'args': ['-schedule', '-interval', '10'],
        'active_during': ['premarket', 'market', 'postmarket'],
        'process': None
    },
    'django_server': {
        'command': ['python', 'manage.py', 'runserver', '0.0.0.0:8000'],
        'args': [],
        'active_during': ['market'],  # Only during regular market hours
        'process': None
    }
}
```

## Benefits of Restart-Enabled Components

### 1. **Self-Managing**
- Each component manages its own scheduling internally
- No external cron jobs or task schedulers needed
- Built-in error recovery and restart capabilities

### 2. **Graceful Shutdown**
- Proper signal handling (SIGINT, SIGTERM)
- Clean process termination
- Data integrity preservation

### 3. **Error Recovery**
- Individual operation failures don't stop the entire component
- Automatic retry mechanisms
- Comprehensive error logging

### 4. **Resource Efficiency**
- Single process per component instead of multiple scheduled tasks
- Better memory management
- Reduced system overhead

### 5. **Monitoring and Debugging**
- Separate log files for each component
- Detailed operation tracking
- Easy debugging and troubleshooting

## Signal Handling

All restart-enabled components handle these signals:

- **SIGINT (Ctrl+C)**: Graceful shutdown with cleanup
- **SIGTERM**: Graceful shutdown for process management

```python
def signal_handler(signum, frame):
    """Handle interrupt signals gracefully"""
    global shutdown_flag
    print("\nReceived interrupt signal. Shutting down gracefully...")
    shutdown_flag = True

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)
```

## Error Handling

Each component includes comprehensive error handling:

```python
try:
    # Main operation
    result = perform_operation()
    logger.info("Operation completed successfully")
    return True
except Exception as e:
    logger.error(f"Error in operation: {e}")
    return False
```

## Production Deployment

### Systemd Services (Linux)

Create individual service files for each component:

```ini
[Unit]
Description=Stock Scanner News Scraper
After=network.target

[Service]
Type=simple
User=stockscanner
WorkingDirectory=/path/to/stockscanner
ExecStart=/usr/bin/python3 /path/to/stockscanner/news_scraper_with_restart.py -schedule
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Docker Deployment

```dockerfile
FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .

# Example for news scraper
CMD ["python", "news_scraper_with_restart.py", "-schedule"]
```

## Migration from Django Management Commands

### Before (Django Management Commands)
```bash
# Old way - external scheduling required
*/5 * * * * cd /path/to/project && python manage.py scrape_news
*/10 * * * * cd /path/to/project && python manage.py send_stock_emails
```

### After (Restart-Enabled Components)
```bash
# New way - self-managing processes
python3 news_scraper_with_restart.py -schedule
python3 email_sender_with_restart.py -schedule
```

## Troubleshooting

### Component Won't Start
1. Check if all dependencies are installed
2. Verify Django settings are properly configured
3. Check log files for specific error messages
4. Ensure database connectivity

### Component Stops Unexpectedly
1. Check system resources (memory, disk space)
2. Review log files for error patterns
3. Verify database connection stability
4. Check for conflicting processes

### Performance Issues
1. Adjust interval settings for less frequent execution
2. Enable test mode to limit processing
3. Monitor system resources during operation
4. Review database query performance

## Best Practices

1. **Always use `-schedule` in production** for continuous operation
2. **Monitor log files regularly** for error patterns
3. **Test with `-test` mode** before production deployment
4. **Use appropriate intervals** based on your needs and system capacity
5. **Implement proper monitoring** to track component health
6. **Keep log files manageable** with log rotation