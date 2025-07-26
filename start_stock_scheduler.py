#!/usr/bin/env python3
"""
Stock Scanner Auto-Startup Script
Automatically starts the 5-minute NASDAQ stock data scheduler
"""

import os
import sys
import subprocess
import time
import logging
from pathlib import Path
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('stock_scheduler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class StockSchedulerManager:
    def __init__(self):
        self.project_root = Path(__file__).parent.absolute()
        self.manage_py = self.project_root / 'manage.py'
        self.venv_python = self.project_root / 'venv' / 'Scripts' / 'python.exe'  # Windows
        if not self.venv_python.exists():
            self.venv_python = self.project_root / 'venv' / 'bin' / 'python'  # Linux/Mac
        
        # Use system python if venv not found
        if not self.venv_python.exists():
            self.venv_python = 'python'
    
    def check_environment(self):
        """Check if the environment is properly set up"""
        logger.info("🔍 Checking environment setup...")
        
        # Check if manage.py exists
        if not self.manage_py.exists():
            logger.error(f"❌ manage.py not found at {self.manage_py}")
            return False
        
        # Check if virtual environment exists
        if isinstance(self.venv_python, Path) and not self.venv_python.exists():
            logger.warning("⚠️  Virtual environment not found, using system Python")
        
        # Check database connection
        try:
            result = subprocess.run([
                str(self.venv_python), str(self.manage_py), 'check', '--deploy'
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                logger.info("✅ Django environment check passed")
                return True
            else:
                logger.error(f"❌ Django check failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("❌ Django check timed out")
            return False
        except Exception as e:
            logger.error(f"❌ Error checking Django environment: {e}")
            return False
    
    def run_initial_data_load(self):
        """Run initial NASDAQ data load if needed"""
        logger.info("📊 Checking if initial data load is needed...")
        
        try:
            # Check if we have stock data
            result = subprocess.run([
                str(self.venv_python), str(self.manage_py), 'shell', '-c',
                'from stocks.models import Stock; print(Stock.objects.count())'
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                stock_count = int(result.stdout.strip())
                logger.info(f"📈 Found {stock_count} stocks in database")
                
                if stock_count < 50:  # If less than 50 stocks, load NASDAQ data
                    logger.info("📥 Loading NASDAQ ticker data...")
                    load_result = subprocess.run([
                        str(self.venv_python), str(self.manage_py), 'load_nasdaq_only'
                    ], timeout=300)  # 5 minute timeout
                    
                    if load_result.returncode == 0:
                        logger.info("✅ NASDAQ data loaded successfully")
                    else:
                        logger.warning("⚠️  NASDAQ data load had issues, continuing anyway")
                else:
                    logger.info("✅ Sufficient stock data found, skipping initial load")
            
        except Exception as e:
            logger.warning(f"⚠️  Could not check/load initial data: {e}")
    
    def start_scheduler(self):
        """Start the stock data scheduler"""
        logger.info("🚀 Starting NASDAQ stock data scheduler...")
        logger.info("🕐 Schedule: Updates every 5 minutes")
        logger.info("🎯 Target: NASDAQ-listed securities only")
        logger.info("⚡ Mode: Multithreaded processing")
        
        try:
            # Start the scheduler with startup mode (runs initial update then schedules)
            process = subprocess.Popen([
                str(self.venv_python), str(self.manage_py), 
                'update_stocks_yfinance', '--startup', '--nasdaq-only'
            ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            
            logger.info(f"📅 Scheduler started with PID: {process.pid}")
            
            # Monitor the process
            try:
                while True:
                    output = process.stdout.readline()
                    if output:
                        print(output.strip())
                    
                    # Check if process is still running
                    if process.poll() is not None:
                        break
                    
                    time.sleep(1)
                    
            except KeyboardInterrupt:
                logger.info("⏹️  Stopping scheduler...")
                process.terminate()
                process.wait()
                logger.info("✅ Scheduler stopped")
            
        except Exception as e:
            logger.error(f"❌ Failed to start scheduler: {e}")
            return False
        
        return True
    
    def create_systemd_service(self):
        """Create a systemd service file for Linux systems"""
        service_content = f"""[Unit]
Description=Stock Scanner NASDAQ Data Scheduler
After=network.target mysql.service
Wants=network.target

[Service]
Type=simple
User={os.getenv('USER', 'root')}
WorkingDirectory={self.project_root}
Environment=PYTHONPATH={self.project_root}
ExecStart={self.venv_python} {self.manage_py} update_stocks_yfinance --startup --nasdaq-only
Restart=always
RestartSec=30
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
"""
        
        service_file = Path('/etc/systemd/system/stock-scanner.service')
        try:
            with open(service_file, 'w') as f:
                f.write(service_content)
            
            logger.info(f"✅ Systemd service created at {service_file}")
            logger.info("🔧 To enable and start the service:")
            logger.info("   sudo systemctl enable stock-scanner.service")
            logger.info("   sudo systemctl start stock-scanner.service")
            logger.info("   sudo systemctl status stock-scanner.service")
            
            return True
            
        except PermissionError:
            logger.warning("⚠️  Cannot create systemd service (permission denied)")
            logger.info("💡 Run with sudo to create system service")
            return False
        except Exception as e:
            logger.error(f"❌ Failed to create systemd service: {e}")
            return False
    
    def create_windows_service(self):
        """Create a Windows service or scheduled task"""
        try:
            import winreg
            # Create a batch file for Windows Task Scheduler
            batch_content = f"""@echo off
cd /d "{self.project_root}"
"{self.venv_python}" "{self.manage_py}" update_stocks_yfinance --startup --nasdaq-only
"""
            
            batch_file = self.project_root / 'start_stock_scheduler.bat'
            with open(batch_file, 'w') as f:
                f.write(batch_content)
            
            logger.info(f"✅ Windows batch file created at {batch_file}")
            logger.info("🔧 To create a scheduled task:")
            logger.info("   1. Open Task Scheduler")
            logger.info("   2. Create Basic Task")
            logger.info(f"   3. Set action to run: {batch_file}")
            logger.info("   4. Set trigger to 'At startup'")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to create Windows service: {e}")
            return False

def main():
    """Main startup function"""
    print("=" * 70)
    print("🚀 STOCK SCANNER AUTO-STARTUP")
    print("=" * 70)
    print(f"📅 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🎯 Target: NASDAQ-listed securities")
    print("🕐 Schedule: Every 5 minutes")
    print("=" * 70)
    
    manager = StockSchedulerManager()
    
    # Check environment
    if not manager.check_environment():
        logger.error("❌ Environment check failed, exiting")
        sys.exit(1)
    
    # Check command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == '--create-service':
            if os.name == 'nt':  # Windows
                manager.create_windows_service()
            else:  # Linux/Unix
                manager.create_systemd_service()
            return
        elif sys.argv[1] == '--check-only':
            logger.info("✅ Environment check completed successfully")
            return
    
    # Run initial data load if needed
    manager.run_initial_data_load()
    
    # Start the scheduler
    success = manager.start_scheduler()
    
    if not success:
        logger.error("❌ Failed to start scheduler")
        sys.exit(1)

if __name__ == "__main__":
    main()