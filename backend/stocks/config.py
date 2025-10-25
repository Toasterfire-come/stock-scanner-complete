# Stock Data Fetcher Configuration
# Customize these settings based on your needs and infrastructure

# Proxy Configuration
PROXY_SOURCES = {
# Free proxy APIs (less reliable, use for testing only)
"free_proxy_list": "https://api.proxyscrape.com/v2/?request=get&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all",
"proxy_list": "https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt",

# Paid proxy services (recommended for production)
# Uncomment and configure with your credentials
# "scrapeops": {
# "endpoint": "https://proxy.scrapeops.io/v1/",
# "api_key": "YOUR_SCRAPEOPS_API_KEY",
# },
# "bright_data": {
# "endpoint": "http://brd-customer-YOUR_CUSTOMER_ID-zone-YOUR_ZONE:YOUR_PASSWORD@brd.superproxy.io:22225",
# },
# "smartproxy": {
# "endpoint": "http://user-YOUR_USERNAME:YOUR_PASSWORD@gate.smartproxy.com:10000",
# }
}

# Residential proxy pools for better success rates
RESIDENTIAL_PROXIES = [
# Add your residential proxy endpoints here
# Format: "http://username:password@endpoint:port"
]

# Data center proxies (faster but more likely to be detected)
DATACENTER_PROXIES = [
# Add your datacenter proxy endpoints here
# Format: "http://ip:port" or "http://username:password@ip:port"
]

# User agents for rotation - comprehensive list
USER_AGENTS = {
"chrome": [
"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
],
"firefox": [
"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
"Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0",
"Mozilla/5.0 (X11; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0",
],
"safari": [
"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
"Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1",
]
}

# Rate limiting configuration - conservative settings for Yahoo Finance
RATE_LIMITS = {
"requests_per_minute": 60, # Conservative limit
"requests_per_hour": 1000, # Hourly limit
"concurrent_requests": 3, # Simultaneous requests
"delay_between_requests": (1.0, 3.0), # Random delay range in seconds
"batch_delay": (10.0, 20.0), # Delay between batches
"exponential_backoff_base": 2, # Base for exponential backoff
"max_backoff_delay": 300, # Maximum backoff delay in seconds
}

# Cache configuration
CACHE_CONFIG = {
"default_timeout": 3600, # 1 hour default cache timeout
"max_cache_size": 10000, # Maximum number of cached items
"cache_prefix": "stock_data_", # Prefix for cache keys
"use_compression": True, # Compress cached data
}

# Retry configuration
RETRY_CONFIG = {
"max_retries": 4, # Maximum number of retry attempts
"backoff_factor": 2, # Exponential backoff factor
"retry_on_status": [429, 500, 502, 503, 504, 520, 521, 522, 524], # HTTP status codes to retry
"timeout": 30, # Request timeout in seconds
"connect_timeout": 10, # Connection timeout in seconds
}

# Performance optimization settings
PERFORMANCE_CONFIG = {
"batch_size": 50, # Default batch size for processing
"max_workers": 3, # Default number of worker threads
"session_pool_size": 20, # HTTP session pool size
"session_pool_connections": 10, # Number of connections per session
"memory_limit_mb": 512, # Memory limit per worker in MB
}

# Logging configuration
LOGGING_CONFIG = {
"level": "INFO", # Logging level
"format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
"file_rotation": "daily", # Log file rotation
"max_file_size": "100MB", # Maximum log file size
"backup_count": 7, # Number of backup log files
}

# Yahoo Finance specific settings
YAHOO_FINANCE_CONFIG = {
"period": "3mo", # Historical data period
"interval": "1d", # Data interval
"timeout": 15, # Request timeout
"verify_ssl": True, # SSL verification
"auto_adjust": True, # Auto-adjust prices
"prepost": False, # Include pre/post market data
"threads": True, # Use threading for multiple tickers
}

# Database optimization settings
DATABASE_CONFIG = {
"bulk_create_batch_size": 1000, # Batch size for bulk database operations
"use_transactions": True, # Use database transactions
"connection_pool_size": 10, # Database connection pool size
"query_timeout": 30, # Database query timeout
}

# Error handling configuration
ERROR_HANDLING_CONFIG = {
"ignore_errors": [
"No data found for ticker",
"No price data found",
"Invalid ticker symbol",
],
"critical_errors": [
"Database connection failed",
"Authentication failed",
"Rate limit exceeded for extended period",
],
"retry_errors": [
"Too Many Requests",
"Timeout",
"Connection error",
"Server error",
],
}

# Monitoring and alerting configuration
MONITORING_CONFIG = {
"success_rate_threshold": 0.85, # Minimum success rate (85%)
"max_consecutive_failures": 10, # Maximum consecutive failures before alert
"performance_threshold": 60, # Maximum seconds per ticker
"memory_threshold": 0.9, # Memory usage threshold (90%)
"alert_channels": [], # List of alert channels (email, slack, etc.)
}

# Feature flags for experimental features
FEATURE_FLAGS = {
"use_async_processing": False, # Use asyncio for processing
"use_machine_learning": False, # Use ML for request optimization
"use_distributed_cache": False, # Use distributed caching (Redis cluster)
"use_proxy_rotation": False, # Enable automatic proxy rotation
"use_request_fingerprinting": True, # Use advanced request fingerprinting
}

# Development and testing settings
DEV_CONFIG = {
"test_mode": False, # Enable test mode with limited tickers
"test_tickers": ["AAPL", "GOOGL", "MSFT", "TSLA"], # Test ticker list
"debug_requests": False, # Log detailed request information
"save_raw_responses": False, # Save raw API responses for debugging
"mock_responses": False, # Use mock responses for testing
}