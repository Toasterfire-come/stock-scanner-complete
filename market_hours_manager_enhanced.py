#!/usr/bin/env python3
"""
Enhanced Market Hours Manager with Integrated Proxy Management
Manages all stock scanner components based on market hours with daily updates:
- Daily proxy update at 8:45 AM ET
- Daily stock update at 9:00 AM ET
- Premarket: 4:00 AM - 9:30 AM ET (starts retrieval, news, emails)
- Regular Market: 9:30 AM - 4:00 PM ET (full operation + server)
- Postmarket: 4:00 PM - 8:00 PM ET (continues operation)
- After Hours: 8:00 PM - 4:00 AM ET (stops all components)
"""

import os
import sys
import time
import logging
import subprocess
import signal
import schedule
import threading
from datetime import datetime, timezone, timedelta
from pathlib import Path
import pytz

# Setup logging with rotation
from logging.handlers import RotatingFileHandler

# Configure logger with rotation to avoid unbounded log growth  
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create handlers
file_handler = RotatingFileHandler(
    'market_hours_manager_enhanced.log',
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5
)
console_handler = logging.StreamHandler()

# Create formatter
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Add handlers to logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# Prevent propagation to avoid duplicate messages
logger.propagate = False


class EnhancedMarketHoursManager:
    """Enhanced manager with integrated proxy and daily updates"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.absolute()
        self.python_exe = sys.executable
        self.processes = {}
        self.is_running = True
        
        # Market hours in Eastern Time
        self.eastern_tz = pytz.timezone('US/Eastern')
        
        # Market hours configuration - configurable via environment variables
        self.premarket_start = os.getenv('PREMARKET_START', "04:00")  # 4:00 AM ET
        self.proxy_update_time = "08:45"  # 8:45 AM ET - Proxy update
        self.daily_update_time = "09:00"  # 9:00 AM ET - Main daily update
        self.market_open = os.getenv('MARKET_OPEN', "09:30")      # 9:30 AM ET
        self.market_close = os.getenv('MARKET_CLOSE', "16:00")     # 4:00 PM ET
        self.postmarket_end = os.getenv('POSTMARKET_END', "20:00")   # 8:00 PM ET
        
        # Track last run times
        self.last_proxy_update = None
        self.last_daily_update = None
        self.last_market_phase = None
        
        # Component configurations
        self.components = {
            'stock_retrieval_integrated': {
                'script': 'enhanced_stock_retrieval_integrated.py',
                'args': ['-schedule', '-proxy-update-interval', '60'],
                'active_during': ['premarket', 'market', 'postmarket'],
                'process': None
            },
            'proxy_manager': {
                'script': 'integrated_proxy_manager.py',
                'args': ['-schedule', '-interval', '30'],
                'active_during': ['premarket', 'market', 'postmarket'],
                'process': None,
                'standalone': True  # Runs as separate service
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
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
    def signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        logger.info("Received shutdown signal. Stopping all components...")
        self.is_running = False
        self.stop_all_components()
        sys.exit(0)
    
    def get_current_et_time(self):
        """Get current time in Eastern timezone"""
        return datetime.now(self.eastern_tz)
    
    def is_market_day(self):
        """Check if today is a market day (Monday-Friday)"""
        current_time = self.get_current_et_time()
        # 0 = Monday, 4 = Friday
        return current_time.weekday() < 5
    
    def get_market_phase(self):
        """Determine current market phase"""
        if not self.is_market_day():
            return 'closed'
        
        current_time = self.get_current_et_time()
        current_time_str = current_time.strftime("%H:%M")
        
        if current_time_str < self.premarket_start:
            return 'closed'
        elif current_time_str < self.market_open:
            return 'premarket'
        elif current_time_str < self.market_close:
            return 'market'
        elif current_time_str < self.postmarket_end:
            return 'postmarket'
        else:
            return 'closed'
    
    def start_component(self, name, config):
        """Start a single component"""
        try:
            # Check if already running
            if config.get('process') and config['process'].poll() is None:
                logger.debug(f"{name} is already running")
                return
            
            # Build command
            if 'script' in config:
                script_path = self.project_root / config['script']
                if not script_path.exists():
                    logger.warning(f"Script not found: {config['script']}")
                    return
                cmd = [self.python_exe, str(script_path)] + config.get('args', [])
            elif 'command' in config:
                cmd = config['command'] + config.get('args', [])
            else:
                logger.error(f"Invalid config for {name}")
                return
            
            # Start process
            logger.info(f"Starting {name}: {' '.join(cmd)}")
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                cwd=str(self.project_root)
            )
            
            config['process'] = process
            self.processes[name] = process
            logger.info(f"Started {name} (PID: {process.pid})")
            
        except Exception as e:
            logger.error(f"Failed to start {name}: {e}")
    
    def stop_component(self, name, config):
        """Stop a single component"""
        try:
            process = config.get('process')
            if process and process.poll() is None:
                logger.info(f"Stopping {name} (PID: {process.pid})")
                process.terminate()
                try:
                    process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    logger.warning(f"Force killing {name}")
                    process.kill()
                config['process'] = None
                if name in self.processes:
                    del self.processes[name]
                logger.info(f"Stopped {name}")
        except Exception as e:
            logger.error(f"Error stopping {name}: {e}")
    
    def stop_all_components(self):
        """Stop all running components"""
        logger.info("Stopping all components...")
        for name, config in self.components.items():
            self.stop_component(name, config)
    
    def update_components_for_phase(self, phase):
        """Start/stop components based on market phase"""
        logger.info(f"Updating components for {phase} phase")
        
        for name, config in self.components.items():
            should_run = phase in config.get('active_during', [])
            is_running = config.get('process') and config['process'].poll() is None
            
            if should_run and not is_running:
                self.start_component(name, config)
            elif not should_run and is_running:
                self.stop_component(name, config)
    
    def run_proxy_update(self):
        """Run daily proxy update at 8:45 AM"""
        current_time = self.get_current_et_time()
        
        # Check if already run today
        if self.last_proxy_update and self.last_proxy_update.date() == current_time.date():
            return
        
        logger.info("="*60)
        logger.info(f"DAILY PROXY UPDATE - {current_time.strftime('%Y-%m-%d %H:%M:%S ET')}")
        logger.info("="*60)
        
        try:
            # Run integrated proxy manager for comprehensive update
            cmd = [
                self.python_exe,
                str(self.project_root / 'integrated_proxy_manager.py'),
                '-threads', '100',
                '-timeout', '5',
                '-github'  # Include GitHub repos
            ]
            
            logger.info(f"Running: {' '.join(cmd)}")
            
            # Run synchronously and wait for completion
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=str(self.project_root),
                timeout=600  # 10 minute timeout
            )
            
            if result.returncode == 0:
                logger.info("Proxy update completed successfully")
                self.last_proxy_update = current_time
                
                # Log summary from output
                for line in result.stdout.split('\n'):
                    if 'Working Proxies:' in line or 'Success Rate:' in line:
                        logger.info(f"  {line.strip()}")
            else:
                logger.error(f"Proxy update failed: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            logger.error("Proxy update timed out")
        except Exception as e:
            logger.error(f"Error running proxy update: {e}")
    
    def run_daily_update(self):
        """Run daily market update at 9:00 AM"""
        current_time = self.get_current_et_time()
        
        # Check if already run today
        if self.last_daily_update and self.last_daily_update.date() == current_time.date():
            return
        
        logger.info("="*60)
        logger.info(f"DAILY MARKET UPDATE - {current_time.strftime('%Y-%m-%d %H:%M:%S ET')}")
        logger.info("="*60)
        
        try:
            # Run the daily market updater
            cmd = [
                self.python_exe,
                str(self.project_root / 'daily_market_updater.py'),
                '-once'  # Run once
            ]
            
            logger.info(f"Running: {' '.join(cmd)}")
            
            # Run in background as it might take a while
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                cwd=str(self.project_root)
            )
            
            # Log output in a separate thread
            def log_output():
                for line in process.stdout:
                    logger.info(f"[DAILY] {line.rstrip()}")
            
            output_thread = threading.Thread(target=log_output)
            output_thread.start()
            
            self.last_daily_update = current_time
            logger.info("Daily update started in background")
            
        except Exception as e:
            logger.error(f"Error running daily update: {e}")
    
    def check_component_health(self):
        """Check health of running components and restart if needed"""
        for name, config in self.components.items():
            process = config.get('process')
            if process:
                # Check if process is still running
                if process.poll() is not None:
                    logger.warning(f"{name} has stopped unexpectedly (exit code: {process.returncode})")
                    
                    # Check if it should be running
                    current_phase = self.get_market_phase()
                    if current_phase in config.get('active_during', []):
                        logger.info(f"Restarting {name}...")
                        config['process'] = None
                        self.start_component(name, config)
    
    def run(self):
        """Main run loop"""
        logger.info("Enhanced Market Hours Manager Started")
        logger.info(f"Proxy Update Time: {self.proxy_update_time} ET")
        logger.info(f"Daily Update Time: {self.daily_update_time} ET")
        logger.info(f"Market Hours: {self.market_open} - {self.market_close} ET")
        logger.info("Press Ctrl+C to stop")
        
        # Schedule daily updates
        schedule.every().day.at(self.proxy_update_time).do(self.run_proxy_update)
        schedule.every().day.at(self.daily_update_time).do(self.run_daily_update)
        
        # Initial setup
        current_phase = self.get_market_phase()
        self.update_components_for_phase(current_phase)
        self.last_market_phase = current_phase
        
        # Check if we should run daily updates immediately
        current_time = self.get_current_et_time()
        current_time_str = current_time.strftime("%H:%M")
        
        if self.is_market_day():
            if current_time_str >= self.proxy_update_time and not self.last_proxy_update:
                self.run_proxy_update()
            if current_time_str >= self.daily_update_time and not self.last_daily_update:
                self.run_daily_update()
        
        # Main loop
        last_health_check = time.time()
        
        while self.is_running:
            try:
                # Check for market phase changes
                current_phase = self.get_market_phase()
                if current_phase != self.last_market_phase:
                    logger.info(f"Market phase changed: {self.last_market_phase} -> {current_phase}")
                    self.update_components_for_phase(current_phase)
                    self.last_market_phase = current_phase
                
                # Run scheduled tasks
                schedule.run_pending()
                
                # Periodic health check (every 5 minutes)
                if time.time() - last_health_check > 300:
                    self.check_component_health()
                    last_health_check = time.time()
                
                # Log status every hour
                current_time = self.get_current_et_time()
                if current_time.minute == 0 and current_time.second < 30:
                    running_components = [name for name, config in self.components.items() 
                                         if config.get('process') and config['process'].poll() is None]
                    logger.info(f"Status - Phase: {current_phase}, Running: {', '.join(running_components)}")
                
                time.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                time.sleep(60)


def main():
    """Main function"""
    manager = EnhancedMarketHoursManager()
    
    try:
        # Check for required files
        required_files = [
            'enhanced_stock_retrieval_integrated.py',
            'integrated_proxy_manager.py',
            'daily_market_updater.py'
        ]
        
        missing_files = []
        for file in required_files:
            if not (manager.project_root / file).exists():
                missing_files.append(file)
        
        if missing_files:
            logger.error(f"Missing required files: {', '.join(missing_files)}")
            logger.error("Please ensure all components are installed")
            sys.exit(1)
        
        # Start the manager
        manager.run()
        
    except KeyboardInterrupt:
        logger.info("Manager stopped by user")
        manager.stop_all_components()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        manager.stop_all_components()
        sys.exit(1)


if __name__ == "__main__":
    main()