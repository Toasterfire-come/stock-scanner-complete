#!/usr/bin/env python3
"""
Market Hours Manager - Automated Start/Stop Script
Manages all stock scanner components based on market hours:
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
    'market_hours_manager.log',
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

class MarketHoursManager:
    """Manages all stock scanner components based on market hours"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.absolute()
        self.python_exe = sys.executable
        self.processes = {}
        self.is_running = True
        
        # Market hours in Eastern Time
        self.eastern_tz = pytz.timezone('US/Eastern')
        
        # Market hours configuration - configurable via environment variables
        self.premarket_start = os.getenv('PREMARKET_START', "04:00")  # 4:00 AM ET
        self.market_open = os.getenv('MARKET_OPEN', "09:30")      # 9:30 AM ET
        self.market_close = os.getenv('MARKET_CLOSE', "16:00")     # 4:00 PM ET
        self.postmarket_end = os.getenv('POSTMARKET_END', "20:00")   # 8:00 PM ET
        
        # Component configurations
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
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
    def signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.is_running = False
        self.stop_all_components()
        sys.exit(0)
        
    def get_current_market_phase(self):
        """Determine current market phase based on Eastern Time"""
        now_et = datetime.now(self.eastern_tz)
        current_time = now_et.strftime("%H:%M")
        
        # Check if it's a weekday (Monday=0, Sunday=6)
        if now_et.weekday() >= 5:  # Saturday or Sunday
            return 'closed'
            
        if self.premarket_start <= current_time < self.market_open:
            return 'premarket'
        elif self.market_open <= current_time < self.market_close:
            return 'market'
        elif self.market_close <= current_time < self.postmarket_end:
            return 'postmarket'
        else:
            return 'closed'
            
    def is_component_active(self, component_name, market_phase):
        """Check if component should be active during current market phase"""
        component = self.components.get(component_name)
        if not component:
            return False
            
        return market_phase in component['active_during']
        
    def start_component(self, component_name):
        """Start a specific component"""
        component = self.components.get(component_name)
        if not component:
            logger.error(f"Unknown component: {component_name}")
            return False
            
        if component['process'] and component['process'].poll() is None:
            logger.info(f"Component {component_name} is already running")
            return True
            
        try:
            # Build command
            if 'script' in component:
                cmd = [self.python_exe, component['script']] + component['args']
            else:
                cmd = component['command'] + component['args']
                
            # Change to project directory
            logger.info(f"Starting {component_name}: {' '.join(cmd)}")
            
            # Start process - redirect to DEVNULL to avoid PIPE deadlocks
            process = subprocess.Popen(
                cmd,
                cwd=self.project_root,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                text=True
            )
            
            component['process'] = process
            self.processes[component_name] = process
            
            logger.info(f"Started {component_name} with PID {process.pid}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start {component_name}: {e}")
            return False
            
    def stop_component(self, component_name):
        """Stop a specific component"""
        component = self.components.get(component_name)
        if not component or not component['process']:
            return True
            
        try:
            process = component['process']
            if process.poll() is None:  # Process is still running
                logger.info(f"Stopping {component_name} (PID: {process.pid})")
                
                # Try graceful shutdown first
                process.terminate()
                
                # Wait for graceful shutdown
                try:
                    process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    logger.warning(f"Force killing {component_name}")
                    process.kill()
                    process.wait()
                    
                logger.info(f"Stopped {component_name}")
                
            component['process'] = None
            if component_name in self.processes:
                del self.processes[component_name]
                
            return True
            
        except Exception as e:
            logger.error(f"Failed to stop {component_name}: {e}")
            return False
            
    def stop_all_components(self):
        """Stop all running components"""
        logger.info("Stopping all components...")
        for component_name in list(self.components.keys()):
            self.stop_component(component_name)
            
    def check_component_health(self, component_name):
        """Check if component is healthy and restart if needed"""
        component = self.components.get(component_name)
        if not component:
            return False
            
        process = component['process']
        if not process:
            return False
            
        # Check if process is still running
        if process.poll() is not None:
            logger.warning(f"Component {component_name} has stopped unexpectedly")
            component['process'] = None
            return False
            
        return True
        
    def run_scheduled_component(self, component_name):
        """Legacy function - no longer used since all components are now continuous processes"""
        logger.warning(f"run_scheduled_component called for {component_name} - this is no longer used")
        pass
            
    def manage_components(self):
        """Main component management logic"""
        current_phase = self.get_current_market_phase()
        now_et = datetime.now(self.eastern_tz)
        
        logger.info(f"Current market phase: {current_phase} ({now_et.strftime('%Y-%m-%d %H:%M:%S %Z')})")
        
        # Handle market closed period specially
        if current_phase == 'closed':
            # Check if we've already handled this closed period
            if not hasattr(self, '_last_closed_handling') or \
               (datetime.now() - self._last_closed_handling).total_seconds() > 3600:  # Once per hour
                self.handle_market_closed()
                self._last_closed_handling = datetime.now()
            return
        
        for component_name, component in self.components.items():
            should_be_active = self.is_component_active(component_name, current_phase)
            is_currently_running = self.check_component_health(component_name)
                
            if should_be_active and not is_currently_running:
                logger.info(f"Starting {component_name} for {current_phase} phase")
                self.start_component(component_name)
            elif not should_be_active and is_currently_running:
                logger.info(f"Stopping {component_name} (not active during {current_phase})")
                self.stop_component(component_name)
                
    def setup_scheduled_tasks(self):
        """Setup scheduled tasks for component management"""
        # Component management every 1 minute
        schedule.every(1).minutes.do(self.manage_components)
        
    def run_scheduler(self):
        """Run the scheduled tasks in a separate thread"""
        while self.is_running:
            try:
                schedule.run_pending()
                time.sleep(1)
            except Exception as e:
                logger.error(f"Scheduler error: {e}")
                time.sleep(5)
                
    def display_status(self):
        """Display current status of all components"""
        current_phase = self.get_current_market_phase()
        now_et = datetime.now(self.eastern_tz)
        
        logger.info("="*60)
        logger.info("MARKET HOURS MANAGER - STATUS")
        logger.info("="*60)
        logger.info(f"Current Time (ET): {now_et.strftime('%Y-%m-%d %H:%M:%S %Z')}")
        logger.info(f"Market Phase: {current_phase.upper()}")
        logger.info("-"*60)
        logger.info("Component Status:")
        
        for component_name, component in self.components.items():
            is_active = self.is_component_active(component_name, current_phase)
            is_running = self.check_component_health(component_name)
            
            status = "RUNNING" if is_running else "STOPPED"
            should_status = "SHOULD RUN" if is_active else "SHOULD STOP"
            
            logger.info(f"  {component_name:20} | {status:8} | {should_status}")
            
        logger.info("="*60)
        
    def run(self):
        """Main execution loop"""
        logger.info("Market Hours Manager starting...")
        
        # Display initial status
        self.display_status()
        
        # Setup scheduled tasks
        self.setup_scheduled_tasks()
        
        # Start scheduler thread
        scheduler_thread = threading.Thread(target=self.run_scheduler, daemon=True)
        scheduler_thread.start()
        
        # Initial component management
        self.manage_components()
        
        # Main loop
        try:
            while self.is_running:
                time.sleep(30)  # Check every 30 seconds
                
                # Display status every 5 minutes
                if datetime.now().minute % 5 == 0 and datetime.now().second < 30:
                    self.display_status()
                    
        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt")
        finally:
            self.stop_all_components()
            logger.info("Market Hours Manager stopped")

    def handle_market_closed(self):
        """Handle market closed period - ensure fallback data is available"""
        logger.info("Market is closed - ensuring fallback data availability")
        
        # Stop all active components
        for component_name in list(self.components.keys()):
            self.stop_component(component_name)
        
        # Populate fallback data to ensure API functionality
        try:
            import subprocess
            result = subprocess.run([
                self.python_exe, 
                os.path.join(self.project_root, 'populate_fallback_data.py')
            ], capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                logger.info("Fallback data populated successfully")
            else:
                logger.error(f"Failed to populate fallback data: {result.stderr}")
        except Exception as e:
            logger.error(f"Error running fallback data script: {e}")
        
        logger.info("Market closed period handling complete")

def main():
    """Main entry point"""
    try:
        manager = MarketHoursManager()
        manager.run()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()