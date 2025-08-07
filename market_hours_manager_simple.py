#!/usr/bin/env python3
"""
Simplified Market Hours Manager - Django Server Only
Runs only the Django server without news scraper and email components
"""

import os
import sys
import time
import logging
import subprocess
import signal
import psutil
from datetime import datetime
import pytz

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('market_hours_manager_simple.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SimpleMarketHoursManager:
    def __init__(self):
        self.processes = {}
        self.running = True
        
        # Simplified components - only Django server
        self.components = {
            'django_server': {
                'script': 'python',
                'args': ['manage.py', 'runserver', '0.0.0.0:8000'],
                'phases': ['premarket', 'market', 'postmarket', 'after_hours']
            }
        }
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

    def signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        logger.info(f"Received signal {signum}, shutting down...")
        self.running = False
        self.stop_all_components()
        sys.exit(0)

    def get_current_market_phase(self):
        """Determine current market phase in Eastern Time"""
        eastern = pytz.timezone('US/Eastern')
        now = datetime.now(eastern)
        current_time = now.time()
        
        # Market hours in Eastern Time
        premarket_start = datetime.strptime('04:00', '%H:%M').time()
        market_open = datetime.strptime('09:30', '%H:%M').time()
        market_close = datetime.strptime('16:00', '%H:%M').time()
        postmarket_end = datetime.strptime('20:00', '%H:%M').time()
        
        if premarket_start <= current_time < market_open:
            return 'premarket'
        elif market_open <= current_time < market_close:
            return 'market'
        elif market_close <= current_time < postmarket_end:
            return 'postmarket'
        else:
            return 'after_hours'

    def start_component(self, component_name, config):
        """Start a component"""
        try:
            # Build command
            cmd = [config['script']] + config['args']
            
            logger.info(f"Starting {component_name}: {' '.join(cmd)}")
            
            # Start process
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            self.processes[component_name] = process
            logger.info(f"Started {component_name} with PID {process.pid}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start {component_name}: {e}")
            return False

    def stop_component(self, component_name):
        """Stop a component"""
        if component_name in self.processes:
            process = self.processes[component_name]
            try:
                # Terminate gracefully
                process.terminate()
                try:
                    process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()
                
                logger.info(f"Stopped {component_name}")
                del self.processes[component_name]
                
            except Exception as e:
                logger.error(f"Error stopping {component_name}: {e}")

    def stop_all_components(self):
        """Stop all running components"""
        for component_name in list(self.processes.keys()):
            self.stop_component(component_name)

    def check_component_health(self, component_name):
        """Check if component is still running"""
        if component_name not in self.processes:
            return False
        
        process = self.processes[component_name]
        return process.poll() is None

    def manage_components(self):
        """Manage components based on current market phase"""
        current_phase = self.get_current_market_phase()
        logger.info(f"Current market phase: {current_phase}")
        
        # Start Django server if not running
        if not self.check_component_health('django_server'):
            config = self.components['django_server']
            if current_phase in config['phases']:
                logger.info(f"Starting django_server for {current_phase} phase")
                self.start_component('django_server', config)

    def display_status(self):
        """Display current status"""
        print("\n" + "="*50)
        print("SIMPLIFIED MARKET HOURS MANAGER STATUS")
        print("="*50)
        
        current_phase = self.get_current_market_phase()
        print(f"Current Phase: {current_phase}")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        print("\nComponent Status:")
        print("-" * 30)
        
        for component_name in self.components.keys():
            if self.check_component_health(component_name):
                pid = self.processes[component_name].pid
                print(f"✅ {component_name}: Running (PID: {pid})")
            else:
                print(f"❌ {component_name}: Stopped")
        
        print("\n" + "="*50)

    def run(self):
        """Main execution loop"""
        logger.info("Simplified Market Hours Manager starting...")
        
        try:
            while self.running:
                self.manage_components()
                
                # Display status every 5 minutes
                if int(time.time()) % 300 == 0:
                    self.display_status()
                
                time.sleep(60)  # Check every minute
                
        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
        finally:
            self.stop_all_components()
            logger.info("Simplified Market Hours Manager stopped")

if __name__ == "__main__":
    manager = SimpleMarketHoursManager()
    manager.run()