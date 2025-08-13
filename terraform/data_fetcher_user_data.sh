#!/bin/bash

# Stock Scanner Pro - Data Fetcher User Data Script
# This script sets up the data fetching service for stock market data

set -e

# Variables passed from Terraform
DB_ENDPOINT="${db_endpoint}"
CACHE_ENDPOINT="${cache_endpoint}"

# System Configuration
LOG_FILE="/var/log/data-fetcher-setup.log"
exec > >(tee -a $LOG_FILE)
exec 2>&1

echo "=== Stock Scanner Pro Data Fetcher Setup Started: $(date) ==="

# Update system
echo "Updating system packages..."
yum update -y

# Install required packages
echo "Installing required packages..."
yum install -y \
    python3 \
    python3-pip \
    python3-dev \
    postgresql-devel \
    redis \
    git \
    wget \
    curl \
    cron \
    amazon-cloudwatch-agent \
    gcc \
    python3-devel

# Install Python packages
echo "Installing Python packages..."
pip3 install --upgrade pip

# Install data processing and API libraries
pip3 install \
    requests \
    pandas \
    numpy \
    psycopg2-binary \
    redis \
    schedule \
    yfinance \
    alpha-vantage \
    python-dotenv \
    sqlalchemy \
    aiohttp \
    asyncio \
    beautifulsoup4 \
    lxml \
    python-dateutil \
    pytz \
    boto3

# Create application directory
echo "Creating application directory..."
mkdir -p /opt/stock-data-fetcher
cd /opt/stock-data-fetcher

# Create configuration file
echo "Creating configuration file..."
cat > /opt/stock-data-fetcher/config.py << EOF
import os
from urllib.parse import urlparse

# Database Configuration
DB_ENDPOINT = "${db_endpoint}"
db_parts = DB_ENDPOINT.split(':')
DB_HOST = db_parts[0]
DB_PORT = int(db_parts[1]) if len(db_parts) > 1 else 5432
DB_NAME = "stockscanner"
DB_USER = "admin"
DB_PASSWORD = "ChangeMe123!"

# Redis Configuration
REDIS_HOST = "${cache_endpoint}"
REDIS_PORT = 6379
REDIS_DB = 0

# API Configuration
ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY', '')
FINNHUB_API_KEY = os.getenv('FINNHUB_API_KEY', '')
POLYGON_API_KEY = os.getenv('POLYGON_API_KEY', '')

# Data Collection Settings
FETCH_INTERVAL = 300  # 5 minutes
MARKET_OPEN_HOUR = 9
MARKET_CLOSE_HOUR = 16
TIMEZONE = 'US/Eastern'

# Stock Symbols to Track
DEFAULT_SYMBOLS = [
    'AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA', 'META', 'NVDA', 'NFLX',
    'SPY', 'QQQ', 'IWM', 'DIA', 'VTI', 'GLD', 'SLV', 'USO',
    'BRK.B', 'V', 'JPM', 'JNJ', 'WMT', 'PG', 'UNH', 'HD',
    'MA', 'DIS', 'ADBE', 'CRM', 'PYPL', 'INTC', 'CMCSA', 'VZ'
]

# Logging Configuration
LOG_LEVEL = 'INFO'
LOG_FILE = '/var/log/stock-data-fetcher.log'
EOF

# Create main data fetcher script
echo "Creating main data fetcher script..."
cat > /opt/stock-data-fetcher/data_fetcher.py << 'EOF'
#!/usr/bin/env python3

import requests
import json
import time
import logging
import schedule
import psycopg2
import redis
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import pytz
from config import *
import sys
import signal
import threading
from sqlalchemy import create_engine, text
import asyncio
import aiohttp

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class StockDataFetcher:
    def __init__(self):
        self.db_connection = None
        self.redis_client = None
        self.running = True
        self.setup_connections()
        self.setup_database()
        
    def setup_connections(self):
        """Setup database and Redis connections"""
        try:
            # Database connection
            db_url = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
            self.engine = create_engine(db_url, pool_size=5, max_overflow=10)
            
            # Redis connection
            self.redis_client = redis.Redis(
                host=REDIS_HOST,
                port=REDIS_PORT,
                db=REDIS_DB,
                decode_responses=True,
                socket_timeout=5,
                socket_connect_timeout=5
            )
            
            # Test connections
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            self.redis_client.ping()
            
            logger.info("Database and Redis connections established successfully")
            
        except Exception as e:
            logger.error(f"Failed to setup connections: {e}")
            raise
    
    def setup_database(self):
        """Setup database tables"""
        try:
            with self.engine.connect() as conn:
                # Create stocks table
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS stocks (
                        id SERIAL PRIMARY KEY,
                        symbol VARCHAR(10) NOT NULL,
                        name VARCHAR(255),
                        exchange VARCHAR(50),
                        sector VARCHAR(100),
                        industry VARCHAR(100),
                        market_cap BIGINT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(symbol)
                    )
                """))
                
                # Create stock_prices table
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS stock_prices (
                        id SERIAL PRIMARY KEY,
                        symbol VARCHAR(10) NOT NULL,
                        price DECIMAL(10,4) NOT NULL,
                        change_amount DECIMAL(10,4),
                        change_percent DECIMAL(8,4),
                        volume BIGINT,
                        open_price DECIMAL(10,4),
                        high_price DECIMAL(10,4),
                        low_price DECIMAL(10,4),
                        close_price DECIMAL(10,4),
                        timestamp TIMESTAMP NOT NULL,
                        is_realtime BOOLEAN DEFAULT true,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        INDEX(symbol, timestamp),
                        INDEX(symbol, is_realtime)
                    )
                """))
                
                # Create stock_historical table
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS stock_historical (
                        id SERIAL PRIMARY KEY,
                        symbol VARCHAR(10) NOT NULL,
                        date DATE NOT NULL,
                        open_price DECIMAL(10,4),
                        high_price DECIMAL(10,4),
                        low_price DECIMAL(10,4),
                        close_price DECIMAL(10,4),
                        volume BIGINT,
                        adjusted_close DECIMAL(10,4),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(symbol, date)
                    )
                """))
                
                # Create market_indices table
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS market_indices (
                        id SERIAL PRIMARY KEY,
                        symbol VARCHAR(10) NOT NULL,
                        name VARCHAR(100) NOT NULL,
                        value DECIMAL(10,4) NOT NULL,
                        change_amount DECIMAL(10,4),
                        change_percent DECIMAL(8,4),
                        timestamp TIMESTAMP NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        INDEX(symbol, timestamp)
                    )
                """))
                
                # Create news articles table
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS news_articles (
                        id SERIAL PRIMARY KEY,
                        title VARCHAR(500) NOT NULL,
                        summary TEXT,
                        url VARCHAR(1000),
                        source VARCHAR(100),
                        published_at TIMESTAMP,
                        category VARCHAR(50),
                        symbols TEXT, -- JSON array of related symbols
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        INDEX(published_at),
                        INDEX(category)
                    )
                """))
                
                conn.commit()
                logger.info("Database tables created/verified successfully")
                
        except Exception as e:
            logger.error(f"Failed to setup database: {e}")
            raise
    
    def is_market_open(self):
        """Check if the market is currently open"""
        et = pytz.timezone(TIMEZONE)
        now = datetime.now(et)
        
        # Check if it's a weekday
        if now.weekday() >= 5:  # Saturday=5, Sunday=6
            return False
        
        # Check if it's within market hours
        market_open = now.replace(hour=MARKET_OPEN_HOUR, minute=30, second=0, microsecond=0)
        market_close = now.replace(hour=MARKET_CLOSE_HOUR, minute=0, second=0, microsecond=0)
        
        return market_open <= now <= market_close
    
    def fetch_stock_data(self, symbols):
        """Fetch real-time stock data"""
        try:
            logger.info(f"Fetching data for {len(symbols)} symbols")
            
            # Use yfinance for real-time data
            tickers = yf.Tickers(' '.join(symbols))
            
            for symbol in symbols:
                try:
                    ticker = yf.Ticker(symbol)
                    info = ticker.info
                    hist = ticker.history(period="1d", interval="1m")
                    
                    if not hist.empty:
                        latest = hist.iloc[-1]
                        
                        # Calculate change
                        prev_close = info.get('previousClose', latest['Close'])
                        change_amount = latest['Close'] - prev_close
                        change_percent = (change_amount / prev_close) * 100 if prev_close else 0
                        
                        # Store in database
                        self.store_stock_price({
                            'symbol': symbol,
                            'price': latest['Close'],
                            'change_amount': change_amount,
                            'change_percent': change_percent,
                            'volume': latest['Volume'],
                            'open_price': latest['Open'],
                            'high_price': latest['High'],
                            'low_price': latest['Low'],
                            'close_price': latest['Close'],
                            'timestamp': datetime.now()
                        })
                        
                        # Cache in Redis
                        self.cache_stock_data(symbol, {
                            'price': float(latest['Close']),
                            'change': float(change_amount),
                            'change_percent': float(change_percent),
                            'volume': int(latest['Volume']),
                            'timestamp': datetime.now().isoformat()
                        })
                        
                except Exception as e:
                    logger.error(f"Error fetching data for {symbol}: {e}")
                    continue
            
            logger.info("Stock data fetch completed")
            
        except Exception as e:
            logger.error(f"Error in fetch_stock_data: {e}")
    
    def fetch_historical_data(self, symbol, period="1y"):
        """Fetch historical stock data"""
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period)
            
            for date, row in hist.iterrows():
                self.store_historical_data({
                    'symbol': symbol,
                    'date': date.date(),
                    'open_price': row['Open'],
                    'high_price': row['High'],
                    'low_price': row['Low'],
                    'close_price': row['Close'],
                    'volume': row['Volume'],
                    'adjusted_close': row['Close']  # yfinance doesn't have adj close in basic history
                })
            
            logger.info(f"Historical data updated for {symbol}")
            
        except Exception as e:
            logger.error(f"Error fetching historical data for {symbol}: {e}")
    
    def fetch_market_indices(self):
        """Fetch major market indices data"""
        indices = {
            '^GSPC': 'S&P 500',
            '^IXIC': 'NASDAQ Composite',
            '^DJI': 'Dow Jones Industrial Average',
            '^RUT': 'Russell 2000'
        }
        
        try:
            for symbol, name in indices.items():
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period="1d", interval="1m")
                
                if not hist.empty:
                    latest = hist.iloc[-1]
                    prev_close = hist.iloc[-2]['Close'] if len(hist) > 1 else latest['Close']
                    
                    change_amount = latest['Close'] - prev_close
                    change_percent = (change_amount / prev_close) * 100 if prev_close else 0
                    
                    self.store_market_index({
                        'symbol': symbol,
                        'name': name,
                        'value': latest['Close'],
                        'change_amount': change_amount,
                        'change_percent': change_percent,
                        'timestamp': datetime.now()
                    })
            
            logger.info("Market indices data updated")
            
        except Exception as e:
            logger.error(f"Error fetching market indices: {e}")
    
    def store_stock_price(self, data):
        """Store stock price data in database"""
        try:
            with self.engine.connect() as conn:
                conn.execute(text("""
                    INSERT INTO stock_prices (
                        symbol, price, change_amount, change_percent, volume,
                        open_price, high_price, low_price, close_price, timestamp
                    ) VALUES (
                        :symbol, :price, :change_amount, :change_percent, :volume,
                        :open_price, :high_price, :low_price, :close_price, :timestamp
                    )
                """), data)
                conn.commit()
        except Exception as e:
            logger.error(f"Error storing stock price data: {e}")
    
    def store_historical_data(self, data):
        """Store historical stock data in database"""
        try:
            with self.engine.connect() as conn:
                conn.execute(text("""
                    INSERT INTO stock_historical (
                        symbol, date, open_price, high_price, low_price,
                        close_price, volume, adjusted_close
                    ) VALUES (
                        :symbol, :date, :open_price, :high_price, :low_price,
                        :close_price, :volume, :adjusted_close
                    ) ON CONFLICT (symbol, date) DO UPDATE SET
                        open_price = EXCLUDED.open_price,
                        high_price = EXCLUDED.high_price,
                        low_price = EXCLUDED.low_price,
                        close_price = EXCLUDED.close_price,
                        volume = EXCLUDED.volume,
                        adjusted_close = EXCLUDED.adjusted_close
                """), data)
                conn.commit()
        except Exception as e:
            logger.error(f"Error storing historical data: {e}")
    
    def store_market_index(self, data):
        """Store market index data in database"""
        try:
            with self.engine.connect() as conn:
                conn.execute(text("""
                    INSERT INTO market_indices (
                        symbol, name, value, change_amount, change_percent, timestamp
                    ) VALUES (
                        :symbol, :name, :value, :change_amount, :change_percent, :timestamp
                    )
                """), data)
                conn.commit()
        except Exception as e:
            logger.error(f"Error storing market index data: {e}")
    
    def cache_stock_data(self, symbol, data):
        """Cache stock data in Redis"""
        try:
            cache_key = f"stock_data:{symbol}"
            self.redis_client.setex(cache_key, 300, json.dumps(data))  # 5 minute expiry
        except Exception as e:
            logger.error(f"Error caching data for {symbol}: {e}")
    
    def run_data_collection(self):
        """Main data collection routine"""
        logger.info("Starting data collection cycle")
        
        # Fetch real-time data for tracked symbols
        self.fetch_stock_data(DEFAULT_SYMBOLS)
        
        # Fetch market indices
        self.fetch_market_indices()
        
        # Update market status in cache
        market_open = self.is_market_open()
        self.redis_client.setex("market_status", 300, "open" if market_open else "closed")
        
        logger.info("Data collection cycle completed")
    
    def run_historical_update(self):
        """Update historical data (run daily)"""
        logger.info("Starting historical data update")
        
        for symbol in DEFAULT_SYMBOLS:
            self.fetch_historical_data(symbol, period="5d")  # Get last 5 days
        
        logger.info("Historical data update completed")
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.running = False
    
    def run(self):
        """Main run loop"""
        # Register signal handlers
        signal.signal(signal.SIGTERM, self.signal_handler)
        signal.signal(signal.SIGINT, self.signal_handler)
        
        # Schedule jobs
        schedule.every(5).minutes.do(self.run_data_collection)
        schedule.every().day.at("06:00").do(self.run_historical_update)
        
        logger.info("Stock data fetcher started")
        
        # Initial data collection
        self.run_data_collection()
        self.run_historical_update()
        
        # Main loop
        while self.running:
            try:
                schedule.run_pending()
                time.sleep(10)
            except KeyboardInterrupt:
                logger.info("Received keyboard interrupt, shutting down...")
                break
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                time.sleep(30)  # Wait before retrying
        
        logger.info("Stock data fetcher stopped")

if __name__ == "__main__":
    fetcher = StockDataFetcher()
    fetcher.run()
EOF

# Create systemd service
echo "Creating systemd service..."
cat > /etc/systemd/system/stock-data-fetcher.service << 'EOF'
[Unit]
Description=Stock Scanner Pro Data Fetcher
After=network.target

[Service]
Type=simple
User=ec2-user
WorkingDirectory=/opt/stock-data-fetcher
ExecStart=/usr/bin/python3 /opt/stock-data-fetcher/data_fetcher.py
Restart=always
RestartSec=30
Environment=PYTHONPATH=/opt/stock-data-fetcher
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Create backup script
echo "Creating backup script..."
cat > /opt/stock-data-fetcher/backup.py << 'EOF'
#!/usr/bin/env python3

import boto3
import psycopg2
import os
import gzip
import json
from datetime import datetime
from config import *

def backup_database():
    """Backup database to S3"""
    try:
        # Create database dump
        dump_file = f"/tmp/stockscanner_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql"
        
        os.system(f"""
            PGPASSWORD="{DB_PASSWORD}" pg_dump \
                -h {DB_HOST} \
                -p {DB_PORT} \
                -U {DB_USER} \
                -d {DB_NAME} \
                --no-password \
                > {dump_file}
        """)
        
        # Compress the dump
        compressed_file = f"{dump_file}.gz"
        with open(dump_file, 'rb') as f_in:
            with gzip.open(compressed_file, 'wb') as f_out:
                f_out.writelines(f_in)
        
        # Upload to S3 (if configured)
        try:
            s3 = boto3.client('s3')
            bucket_name = os.getenv('BACKUP_S3_BUCKET')
            if bucket_name:
                s3.upload_file(
                    compressed_file,
                    bucket_name,
                    f"database-backups/{os.path.basename(compressed_file)}"
                )
                print(f"Database backup uploaded to S3: {compressed_file}")
        except Exception as e:
            print(f"Failed to upload to S3: {e}")
        
        # Cleanup local files
        os.remove(dump_file)
        os.remove(compressed_file)
        
        print("Database backup completed successfully")
        
    except Exception as e:
        print(f"Database backup failed: {e}")

if __name__ == "__main__":
    backup_database()
EOF

# Set up cron job for backup
echo "Setting up backup cron job..."
echo "0 2 * * * /usr/bin/python3 /opt/stock-data-fetcher/backup.py >> /var/log/backup.log 2>&1" | crontab -

# Configure CloudWatch agent for data fetcher
echo "Configuring CloudWatch agent..."
cat > /opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json << 'EOF'
{
    "metrics": {
        "namespace": "StockScannerPro/DataFetcher",
        "metrics_collected": {
            "cpu": {
                "measurement": [
                    "cpu_usage_idle",
                    "cpu_usage_iowait",
                    "cpu_usage_user",
                    "cpu_usage_system"
                ],
                "metrics_collection_interval": 60
            },
            "disk": {
                "measurement": [
                    "used_percent"
                ],
                "metrics_collection_interval": 60,
                "resources": [
                    "*"
                ]
            },
            "mem": {
                "measurement": [
                    "mem_used_percent"
                ],
                "metrics_collection_interval": 60
            },
            "processes": {
                "measurement": [
                    "running",
                    "sleeping",
                    "dead"
                ]
            }
        }
    },
    "logs": {
        "logs_collected": {
            "files": {
                "collect_list": [
                    {
                        "file_path": "/var/log/stock-data-fetcher.log",
                        "log_group_name": "/aws/ec2/stockscanner/data-fetcher",
                        "log_stream_name": "{instance_id}/application.log"
                    },
                    {
                        "file_path": "/var/log/data-fetcher-setup.log",
                        "log_group_name": "/aws/ec2/stockscanner/data-fetcher-setup",
                        "log_stream_name": "{instance_id}/setup.log"
                    },
                    {
                        "file_path": "/var/log/backup.log",
                        "log_group_name": "/aws/ec2/stockscanner/backup",
                        "log_stream_name": "{instance_id}/backup.log"
                    }
                ]
            }
        }
    }
}
EOF

# Start CloudWatch agent
/opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl \
    -a fetch-config \
    -m ec2 \
    -c file:/opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json \
    -s

# Set permissions
chown -R ec2-user:ec2-user /opt/stock-data-fetcher
chmod +x /opt/stock-data-fetcher/*.py

# Enable and start the service
systemctl daemon-reload
systemctl enable stock-data-fetcher.service
systemctl start stock-data-fetcher.service

# Configure automatic security updates
echo "Configuring automatic security updates..."
yum install -y yum-cron
sed -i 's/update_cmd = default/update_cmd = security/' /etc/yum/yum-cron.conf
sed -i 's/apply_updates = no/apply_updates = yes/' /etc/yum/yum-cron.conf
systemctl enable yum-cron
systemctl start yum-cron

# Configure firewall
echo "Configuring firewall..."
systemctl start firewalld
systemctl enable firewalld
firewall-cmd --permanent --add-service=ssh
firewall-cmd --reload

# Create monitoring script
cat > /usr/local/bin/data-fetcher-monitor.sh << 'EOF'
#!/bin/bash

# Monitor the data fetcher service
while true; do
    if ! systemctl is-active --quiet stock-data-fetcher; then
        echo "$(date): Data fetcher service is not running, attempting to restart..." >> /var/log/data-fetcher-monitor.log
        systemctl restart stock-data-fetcher
    fi
    
    # Check log file size
    if [ -f /var/log/stock-data-fetcher.log ]; then
        LOG_SIZE=$(stat -c%s /var/log/stock-data-fetcher.log)
        if [ $LOG_SIZE -gt 104857600 ]; then  # 100MB
            echo "$(date): Log file too large, rotating..." >> /var/log/data-fetcher-monitor.log
            mv /var/log/stock-data-fetcher.log /var/log/stock-data-fetcher.log.old
            systemctl restart stock-data-fetcher
        fi
    fi
    
    sleep 300  # Check every 5 minutes
done
EOF

chmod +x /usr/local/bin/data-fetcher-monitor.sh

# Create systemd service for monitoring
cat > /etc/systemd/system/data-fetcher-monitor.service << 'EOF'
[Unit]
Description=Data Fetcher Monitoring Service
After=network.target

[Service]
Type=simple
ExecStart=/usr/local/bin/data-fetcher-monitor.sh
Restart=always
RestartSec=30

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable data-fetcher-monitor.service
systemctl start data-fetcher-monitor.service

# Verify services are running
echo "Verifying services..."
systemctl status stock-data-fetcher
systemctl status data-fetcher-monitor
systemctl status amazon-cloudwatch-agent

# Create deployment marker
echo "Creating deployment marker..."
echo "Data Fetcher deployment completed at: $(date)" > /opt/stock-data-fetcher/deployment.txt
echo "Instance ID: $(curl -s http://169.254.169.254/latest/meta-data/instance-id)" >> /opt/stock-data-fetcher/deployment.txt
echo "Instance Type: $(curl -s http://169.254.169.254/latest/meta-data/instance-type)" >> /opt/stock-data-fetcher/deployment.txt

echo "=== Stock Scanner Pro Data Fetcher Setup Completed: $(date) ==="
echo "=== Data fetcher is ready and collecting market data ==="