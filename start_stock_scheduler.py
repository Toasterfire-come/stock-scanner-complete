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
        
        # Always use system Python (no virtual environment)
        self.venv_python = sys.executable

    def check_environment(self):
        """Check if the environment is properly set up"""
        logger.info("[SEARCH] Checking environment setup...")

        # Check if manage.py exists
        if not self.manage_py.exists():
            logger.error(f"[ERROR] manage.py not found at {self.manage_py}")
            return False

        # Using system Python installation
        logger.info(f"[INFO] Using Python: {self.venv_python}")

        # Check database connection
        try:
            result = subprocess.run([
                str(self.venv_python), str(self.manage_py), 'check', '--deploy'
            ], capture_output=True, text=True, timeout=30)

            if result.returncode == 0:
                logger.info("[SUCCESS] Django environment check passed")
                return True
            else:
                logger.error(f"[ERROR] Django check failed: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            logger.error("[ERROR] Django check timed out")
            return False
        except Exception as e:
            logger.error(f"[ERROR] Error checking Django environment: {e}")
            return False

    def run_initial_data_load(self):
        """Run initial NASDAQ data load if needed"""
        logger.info("[STATS] Checking if initial data load is needed...")

        try:
            # Check if we have stock data
            result = subprocess.run([
                str(self.venv_python), str(self.manage_py), 'shell', '-c',
                'from stocks.models import Stock; print(Stock.objects.count())'
            ], capture_output=True, text=True, timeout=30)

            if result.returncode == 0:
                stock_count = int(result.stdout.strip())
                logger.info(f"[PROGRESS] Found {stock_count} stocks in database")

                if stock_count < 50:  # If less than 50 stocks, load NASDAQ data
                    logger.info("[FETCH] Loading NASDAQ ticker data...")
                    load_result = subprocess.run([
                        str(self.venv_python), str(self.manage_py), 'load_nasdaq_only'
                    ], timeout=300)  # 5 minute timeout

                    if load_result.returncode == 0:
                        logger.info("[SUCCESS] NASDAQ data loaded successfully")
                    else:
                        logger.warning("[WARNING]  NASDAQ data load had issues, continuing anyway")
                else:
                    logger.info("[SUCCESS] Sufficient stock data found, skipping initial load")

        except Exception as e:
            logger.warning(f"[WARNING]  Could not check/load initial data: {e}")

    def start_scheduler(self):
        """Start the stock data scheduler"""
        logger.info("[START] Starting NASDAQ stock data scheduler...")
        logger.info("[TIME] Schedule: Updates every 5 minutes")
        logger.info("[TARGET] Target: NASDAQ-listed securities only")
        logger.info("[POWER] Mode: Multithreaded processing")

        try:
            # Start the scheduler with startup mode (runs initial update then schedules)
            # Updated to 3500 stocks limit with enhanced error handling
            process = subprocess.Popen([
                str(self.venv_python), str(self.manage_py),
                'update_stocks_yfinance', '--startup', '--nasdaq-only', '--limit', '3500'
            ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

            logger.info(f"[DATE] Scheduler started with PID: {process.pid}")

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
                logger.info("[STOP]  Stopping scheduler...")
                process.terminate()
                process.wait()
                logger.info("[SUCCESS] Scheduler stopped")

        except Exception as e:
            logger.error(f"[ERROR] Failed to start scheduler: {e}")
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
ExecStart={self.venv_python} {self.manage_py} update_stocks_yfinance --startup --nasdaq-only --limit 3500
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

            logger.info(f"[SUCCESS] Systemd service created at {service_file}")
            logger.info("[TOOL] To enable and start the service:")
            logger.info("   sudo systemctl enable stock-scanner.service")
            logger.info("   sudo systemctl start stock-scanner.service")
            logger.info("   sudo systemctl status stock-scanner.service")

            return True

        except PermissionError:
            logger.warning("[WARNING]  Cannot create systemd service (permission denied)")
            logger.info("[INFO] Run with sudo to create system service")
            return False
        except Exception as e:
            logger.error(f"[ERROR] Failed to create systemd service: {e}")
            return False

    def create_windows_service(self):
        """Create a Windows service or scheduled task"""
        try:
            import winreg
            # Create a batch file for Windows Task Scheduler
            batch_content = f"""@echo off
cd /d "{self.project_root}"
"{self.venv_python}" "{self.manage_py}" update_stocks_yfinance --startup --nasdaq-only --limit 3500
"""

            batch_file = self.project_root / 'start_stock_scheduler.bat'
            with open(batch_file, 'w') as f:
                f.write(batch_content)

            logger.info(f"[SUCCESS] Windows batch file created at {batch_file}")
            logger.info("[TOOL] To create a scheduled task:")
            logger.info("   1. Open Task Scheduler")
            logger.info("   2. Create Basic Task")
            logger.info(f"   3. Set action to run: {batch_file}")
            logger.info("   4. Set trigger to 'At startup'")

            return True

        except Exception as e:
            logger.error(f"[ERROR] Failed to create Windows service: {e}")
            return False

def main():
    """Main startup function"""
    print("=" * 70)
    print(">> STOCK SCANNER AUTO-STARTUP")
    print("=" * 70)
    print(f">> Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(">> Target: NASDAQ-listed securities")
    print(">> Schedule: Every 5 minutes")
    print("=" * 70)

    manager = StockSchedulerManager()

    # Check environment
    if not manager.check_environment():
        logger.error("[ERROR] Environment check failed, exiting")
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
            logger.info("[SUCCESS] Environment check completed successfully")
            return

    # Run initial data load if needed
    manager.run_initial_data_load()

    # Start the scheduler
    success = manager.start_scheduler()

    if not success:
        logger.error("[ERROR] Failed to start scheduler")
        sys.exit(1)

if __name__ == "__main__":
    import sys
    
    # Check for background mode argument
    background_mode = "--background" in sys.argv or "--daemon" in sys.argv
    
    if background_mode:
        print("[BACKGROUND] Starting Stock Scanner in background mode...")
        print("[BACKGROUND] Process will run silently - check stock_scheduler.log for updates")
        print("[BACKGROUND] To stop: Use Task Manager to end this Python process")
        
        # Minimize console output in background mode
        import logging
        logging.getLogger().setLevel(logging.WARNING)
        
        # Redirect stdout to log file for background operation
        log_file = open('stock_scheduler_background.log', 'a')
        sys.stdout = log_file
        sys.stderr = log_file
    
    main()
