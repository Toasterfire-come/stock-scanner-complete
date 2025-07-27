#!/usr/bin/env python3
"""
Stock Scanner Auto-Scheduler (Windows Compatible)
Automatically starts and manages the stock data collection scheduler
Windows-optimized version with ASCII-only output
"""

import os
import sys
import time
import schedule
import logging
import subprocess
from datetime import datetime
from pathlib import Path

# Setup logging with Windows-compatible encoding
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('stock_scheduler.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class WindowsStockScheduler:
    """Windows-compatible stock scheduler manager"""

    def __init__(self):
        """Initialize the scheduler"""
        self.project_root = Path(__file__).parent.absolute()
        self.manage_py = self.project_root / 'manage.py'
        self.is_running = False

        # Windows environment setup
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stockscanner_django.settings')

        # Ensure UTF-8 encoding for Windows
        if sys.platform.startswith('win'):
            os.environ['PYTHONIOENCODING'] = 'utf-8'

    def check_django_setup(self):
        """Check if Django is properly configured"""
        try:
            import django
            django.setup()
            logger.info("[SUCCESS] Django setup completed")
            return True
        except Exception as e:
            logger.error(f"[ERROR] Django setup failed: {e}")
            return False

    def run_stock_update(self):
        """Execute the stock update command"""
        logger.info("[FETCH] Starting NASDAQ stock data update...")

        try:
            # Use Windows-compatible command execution
            cmd = [sys.executable, str(self.manage_py), 'update_stocks_yfinance', '--nasdaq-focus']

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding='utf-8',
                timeout=300  # 5 minute timeout
            )

            if result.returncode == 0:
                logger.info("[SUCCESS] Stock update completed successfully")
                return True
            else:
                logger.warning(f"[WARNING] Stock update completed with warnings: {result.stderr}")
                return True  # Consider warnings as success

        except subprocess.TimeoutExpired:
            logger.error("[ERROR] Stock update timed out after 5 minutes")
            return False
        except Exception as e:
            logger.error(f"[ERROR] Stock update failed: {e}")
            return False

    def display_status(self):
        """Display current scheduler status"""
        print("=" * 60)
        print("[STATS] STOCK SCHEDULER STATUS")
        print("=" * 60)
        print(f"[DATE] Current Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"[TARGET] Focus: NASDAQ-listed securities")
        print(f"[TIME] Update Interval: Every 5 minutes")
        print(f"[POWER] Status: {'Running' if self.is_running else 'Stopped'}")
        print("=" * 60)

    def start_scheduler(self):
        """Start the scheduling system"""
        print("=" * 60)
        print("[START] STOCK SCANNER AUTO-STARTUP")
        print("=" * 60)
        print(f"[DATE] Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("[TARGET] Target: NASDAQ-listed securities")
        print("[TIME] Schedule: Every 5 minutes")
        print("=" * 60)

        # Check Django setup
        if not self.check_django_setup():
            print("[ERROR] Cannot start scheduler - Django setup failed")
            return False

        # Schedule the stock updates
        schedule.every(5).minutes.do(self.run_stock_update)

        # Run initial update
        print("[FETCH] Running initial stock data update...")
        self.run_stock_update()

        # Start the scheduler loop
        self.is_running = True
        print("[SUCCESS] Scheduler started successfully!")
        print("[INFO] Press Ctrl+C to stop the scheduler")

        try:
            while self.is_running:
                schedule.run_pending()
                time.sleep(10)  # Check every 10 seconds

        except KeyboardInterrupt:
            print("\n[STOP] Scheduler stopped by user")
            self.is_running = False
            return True
        except Exception as e:
            logger.error(f"[ERROR] Scheduler error: {e}")
            self.is_running = False
            return False

    def create_windows_service(self):
        """Create a Windows service for the scheduler"""
        try:
            service_script = self.project_root / 'stock_scheduler_service.py'

            service_content = f'''
import win32serviceutil
import win32service
import win32event
import servicemanager
import sys
import os

# Add project to path
sys.path.insert(0, r"{self.project_root}")

class StockSchedulerService(win32serviceutil.ServiceFramework):
    _svc_name_ = "StockSchedulerService"
    _svc_display_name_ = "Stock Scanner Scheduler Service"
    _svc_description_ = "Automatically updates stock data every 5 minutes"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                            servicemanager.PYS_SERVICE_STARTED,
                            (self._svc_name_, ''))
        self.main()

    def main(self):
        from start_stock_scheduler_windows import WindowsStockScheduler
        scheduler = WindowsStockScheduler()
        scheduler.start_scheduler()

if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(StockSchedulerService)
'''

            with open(service_script, 'w', encoding='utf-8') as f:
                f.write(service_content)

            logger.info("[SUCCESS] Windows service script created")
            logger.info("[TOOL] To install: python stock_scheduler_service.py install")
            return True

        except Exception as e:
            logger.error(f"[ERROR] Failed to create Windows service: {e}")
            return False

def main():
    """Main startup function"""
    print("=" * 60)
    print("[START] STOCK SCANNER AUTO-STARTUP")
    print("=" * 60)
    print(f"[DATE] Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("[TARGET] Target: NASDAQ-listed securities")
    print("[TIME] Schedule: Every 5 minutes")
    print("=" * 60)

    manager = WindowsStockScheduler()

    try:
        # Display current status
        manager.display_status()

        # Check if user wants to install as Windows service
        if len(sys.argv) > 1 and sys.argv[1] == '--service':
            print("[TOOL] Creating Windows service...")
            manager.create_windows_service()
            return

        # Start the scheduler
        success = manager.start_scheduler()

        if success:
            print("[SUCCESS] Stock scheduler completed successfully")
        else:
            print("[ERROR] Stock scheduler encountered errors")

    except KeyboardInterrupt:
        print("\n[STOP] Startup interrupted by user")
    except Exception as e:
        logger.error(f"[ERROR] Startup failed: {e}")
        print(f"[ERROR] Startup failed: {e}")

if __name__ == "__main__":
    main()
