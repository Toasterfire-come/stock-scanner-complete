"""
Graceful Shutdown and Resource Cleanup
Ensures proper cleanup without adding new features
"""

import signal
import sys
import threading
import time
import logging
import atexit
from typing import Callable, List, Dict, Any
from django.core.management.base import BaseCommand
from django.db import connection, connections
from django.core.cache import cache
from django.utils import timezone
import weakref

logger = logging.getLogger(__name__)

class GracefulShutdownManager:
    """
    Manages graceful shutdown and resource cleanup
    """
    
    def __init__(self):
        self.shutdown_hooks = []
        self.cleanup_tasks = []
        self.is_shutting_down = False
        self.shutdown_timeout = 30  # seconds
        self.active_threads = weakref.WeakSet()
        self.background_tasks = []
        self._lock = threading.Lock()
        
        # Register signal handlers
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)
        
        # Register atexit handler
        atexit.register(self.cleanup_on_exit)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        signal_name = 'SIGTERM' if signum == signal.SIGTERM else 'SIGINT'
        logger.info(f"Received {signal_name}, initiating graceful shutdown...")
        
        self.initiate_shutdown()
    
    def register_shutdown_hook(self, func: Callable, *args, **kwargs):
        """Register a function to be called during shutdown"""
        with self._lock:
            self.shutdown_hooks.append((func, args, kwargs))
    
    def register_cleanup_task(self, func: Callable, *args, **kwargs):
        """Register a cleanup task"""
        with self._lock:
            self.cleanup_tasks.append((func, args, kwargs))
    
    def register_thread(self, thread: threading.Thread):
        """Register a thread for tracking"""
        self.active_threads.add(thread)
    
    def register_background_task(self, task_info: Dict[str, Any]):
        """Register background task for monitoring"""
        with self._lock:
            self.background_tasks.append(task_info)
    
    def initiate_shutdown(self):
        """Initiate graceful shutdown process"""
        if self.is_shutting_down:
            return
        
        with self._lock:
            self.is_shutting_down = True
        
        logger.info("Starting graceful shutdown process...")
        
        shutdown_start = time.time()
        
        try:
            # Step 1: Stop accepting new requests (handled by web server)
            logger.info("Step 1: Stopping new request acceptance")
            
            # Step 2: Execute shutdown hooks
            logger.info("Step 2: Executing shutdown hooks")
            self._execute_shutdown_hooks()
            
            # Step 3: Wait for active threads to complete
            logger.info("Step 3: Waiting for active threads")
            self._wait_for_threads()
            
            # Step 4: Stop background tasks
            logger.info("Step 4: Stopping background tasks")
            self._stop_background_tasks()
            
            # Step 5: Cleanup resources
            logger.info("Step 5: Cleaning up resources")
            self._cleanup_resources()
            
            # Step 6: Close database connections
            logger.info("Step 6: Closing database connections")
            self._close_database_connections()
            
            shutdown_time = time.time() - shutdown_start
            logger.info(f"Graceful shutdown completed in {shutdown_time:.2f} seconds")
            
        except Exception as e:
            logger.error(f"Error during graceful shutdown: {e}")
        
        finally:
            # Force exit if shutdown takes too long
            if time.time() - shutdown_start > self.shutdown_timeout:
                logger.warning("Shutdown timeout exceeded, forcing exit")
                sys.exit(1)
    
    def _execute_shutdown_hooks(self):
        """Execute all registered shutdown hooks"""
        for func, args, kwargs in self.shutdown_hooks:
            try:
                logger.debug(f"Executing shutdown hook: {func.__name__}")
                func(*args, **kwargs)
            except Exception as e:
                logger.error(f"Error in shutdown hook {func.__name__}: {e}")
    
    def _wait_for_threads(self):
        """Wait for active threads to complete"""
        max_wait = 15  # seconds
        start_time = time.time()
        
        while self.active_threads and (time.time() - start_time) < max_wait:
            alive_threads = [t for t in self.active_threads if t.is_alive()]
            if not alive_threads:
                break
            
            logger.info(f"Waiting for {len(alive_threads)} threads to complete...")
            time.sleep(1)
        
        # Log remaining threads
        remaining_threads = [t for t in self.active_threads if t.is_alive()]
        if remaining_threads:
            logger.warning(f"{len(remaining_threads)} threads still active after timeout")
            for thread in remaining_threads:
                logger.warning(f"Active thread: {thread.name}")
    
    def _stop_background_tasks(self):
        """Stop background tasks"""
        for task_info in self.background_tasks:
            try:
                task_name = task_info.get('name', 'unknown')
                stop_method = task_info.get('stop_method')
                
                if stop_method and callable(stop_method):
                    logger.debug(f"Stopping background task: {task_name}")
                    stop_method()
                
            except Exception as e:
                logger.error(f"Error stopping background task: {e}")
    
    def _cleanup_resources(self):
        """Execute cleanup tasks"""
        for func, args, kwargs in self.cleanup_tasks:
            try:
                logger.debug(f"Executing cleanup task: {func.__name__}")
                func(*args, **kwargs)
            except Exception as e:
                logger.error(f"Error in cleanup task {func.__name__}: {e}")
    
    def _close_database_connections(self):
        """Close all database connections"""
        try:
            # Close default connection
            connection.close()
            
            # Close all configured connections
            connections.close_all()
            
            logger.info("Database connections closed")
            
        except Exception as e:
            logger.error(f"Error closing database connections: {e}")
    
    def cleanup_on_exit(self):
        """Cleanup function called on normal exit"""
        if not self.is_shutting_down:
            logger.info("Performing cleanup on exit...")
            self._cleanup_resources()

# Global shutdown manager
shutdown_manager = GracefulShutdownManager()

class ResourceCleanupManager:
    """
    Manages cleanup of various system resources
    """
    
    def __init__(self):
        self.registered_resources = []
        self.cleanup_stats = {
            'cache_cleared': False,
            'connections_closed': False,
            'temp_files_cleaned': False,
            'memory_freed': False
        }
    
    def register_resource(self, resource_type: str, cleanup_func: Callable, *args, **kwargs):
        """Register a resource for cleanup"""
        self.registered_resources.append({
            'type': resource_type,
            'cleanup_func': cleanup_func,
            'args': args,
            'kwargs': kwargs
        })
    
    def cleanup_cache(self):
        """Cleanup cache resources"""
        try:
            cache.clear()
            self.cleanup_stats['cache_cleared'] = True
            logger.info("Cache cleared successfully")
        except Exception as e:
            logger.error(f"Failed to clear cache: {e}")
    
    def cleanup_temp_files(self):
        """Cleanup temporary files"""
        import tempfile
        import os
        import shutil
        
        try:
            temp_dir = tempfile.gettempdir()
            app_temp_pattern = "stock_scanner_"
            
            cleaned_files = 0
            for item in os.listdir(temp_dir):
                if item.startswith(app_temp_pattern):
                    item_path = os.path.join(temp_dir, item)
                    try:
                        if os.path.isfile(item_path):
                            os.unlink(item_path)
                            cleaned_files += 1
                        elif os.path.isdir(item_path):
                            shutil.rmtree(item_path)
                            cleaned_files += 1
                    except Exception as e:
                        logger.warning(f"Could not clean temp file {item}: {e}")
            
            if cleaned_files > 0:
                logger.info(f"Cleaned {cleaned_files} temporary files")
            
            self.cleanup_stats['temp_files_cleaned'] = True
            
        except Exception as e:
            logger.error(f"Error cleaning temporary files: {e}")
    
    def cleanup_memory(self):
        """Force garbage collection and memory cleanup"""
        try:
            import gc
            
            # Force garbage collection
            collected = gc.collect()
            
            # Clear weak references
            gc.collect()
            
            self.cleanup_stats['memory_freed'] = True
            logger.info(f"Memory cleanup: {collected} objects collected")
            
        except Exception as e:
            logger.error(f"Error during memory cleanup: {e}")
    
    def cleanup_log_handlers(self):
        """Cleanup logging handlers"""
        try:
            # Get all loggers
            loggers = [logging.getLogger(name) for name in logging.root.manager.loggerDict]
            loggers.append(logging.getLogger())  # root logger
            
            handlers_closed = 0
            for logger_obj in loggers:
                for handler in logger_obj.handlers[:]:  # Copy list to avoid modification during iteration
                    try:
                        handler.close()
                        logger_obj.removeHandler(handler)
                        handlers_closed += 1
                    except Exception as e:
                        logger.warning(f"Error closing log handler: {e}")
            
            if handlers_closed > 0:
                logger.info(f"Closed {handlers_closed} log handlers")
                
        except Exception as e:
            logger.error(f"Error cleaning log handlers: {e}")
    
    def cleanup_all_resources(self):
        """Cleanup all registered resources"""
        logger.info("Starting comprehensive resource cleanup...")
        
        # Execute registered resource cleanups
        for resource in self.registered_resources:
            try:
                resource['cleanup_func'](*resource['args'], **resource['kwargs'])
                logger.debug(f"Cleaned up {resource['type']} resource")
            except Exception as e:
                logger.error(f"Error cleaning {resource['type']} resource: {e}")
        
        # Execute built-in cleanups
        self.cleanup_cache()
        self.cleanup_memory()
        self.cleanup_temp_files()
        self.cleanup_log_handlers()
        
        logger.info("Resource cleanup completed")
        return self.cleanup_stats

# Global resource cleanup manager
resource_cleanup = ResourceCleanupManager()

class ThreadPoolManager:
    """
    Manages thread pools for graceful shutdown
    """
    
    def __init__(self):
        self.thread_pools = {}
        self.active_workers = {}
    
    def register_thread_pool(self, name: str, pool):
        """Register a thread pool for management"""
        self.thread_pools[name] = pool
    
    def shutdown_all_pools(self, wait_timeout: int = 10):
        """Shutdown all thread pools gracefully"""
        for name, pool in self.thread_pools.items():
            try:
                logger.info(f"Shutting down thread pool: {name}")
                
                if hasattr(pool, 'shutdown'):
                    pool.shutdown(wait=True, timeout=wait_timeout)
                elif hasattr(pool, 'close'):
                    pool.close()
                    if hasattr(pool, 'join'):
                        pool.join(timeout=wait_timeout)
                
                logger.info(f"Thread pool {name} shut down successfully")
                
            except Exception as e:
                logger.error(f"Error shutting down thread pool {name}: {e}")

# Global thread pool manager
thread_pool_manager = ThreadPoolManager()

def graceful_shutdown_decorator(func):
    """
    Decorator to register functions for graceful shutdown
    """
    shutdown_manager.register_shutdown_hook(func)
    return func

def cleanup_resource_decorator(func):
    """
    Decorator to register functions for resource cleanup
    """
    shutdown_manager.register_cleanup_task(func)
    return func

class GracefulShutdownMiddleware:
    """
    Middleware to handle graceful shutdown for requests
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Check if shutdown is in progress
        if shutdown_manager.is_shutting_down:
            from django.http import HttpResponse
            return HttpResponse(
                "Server is shutting down, please try again later",
                status=503,
                content_type="text/plain"
            )
        
        return self.get_response(request)

class HealthyShutdownMonitor:
    """
    Monitor system health during shutdown
    """
    
    def __init__(self):
        self.monitoring = False
        self.health_metrics = {}
    
    def start_monitoring(self):
        """Start monitoring during shutdown"""
        self.monitoring = True
        
        def monitor_loop():
            while self.monitoring:
                try:
                    self.health_metrics = {
                        'active_threads': len([t for t in shutdown_manager.active_threads if t.is_alive()]),
                        'db_connections_open': self._check_db_connections(),
                        'cache_responsive': self._check_cache_health(),
                        'memory_usage': self._get_memory_usage(),
                        'timestamp': timezone.now().isoformat()
                    }
                    
                    time.sleep(2)  # Check every 2 seconds during shutdown
                    
                except Exception as e:
                    logger.error(f"Error in shutdown monitoring: {e}")
                    break
        
        monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        monitor_thread.start()
        shutdown_manager.register_thread(monitor_thread)
    
    def stop_monitoring(self):
        """Stop monitoring"""
        self.monitoring = False
    
    def _check_db_connections(self):
        """Check database connection status"""
        try:
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            return True
        except:
            return False
    
    def _check_cache_health(self):
        """Check cache responsiveness"""
        try:
            cache.set('shutdown_health_check', 'ok', 10)
            return cache.get('shutdown_health_check') == 'ok'
        except:
            return False
    
    def _get_memory_usage(self):
        """Get current memory usage"""
        try:
            import psutil
            return psutil.virtual_memory().percent
        except:
            return None
    
    def get_health_metrics(self):
        """Get current health metrics"""
        return self.health_metrics

# Global shutdown monitor
shutdown_monitor = HealthyShutdownMonitor()

class DjangoManagementCommandShutdown(BaseCommand):
    """
    Django management command with graceful shutdown
    """
    help = 'Base command with graceful shutdown support'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--shutdown-timeout',
            type=int,
            default=30,
            help='Shutdown timeout in seconds'
        )
    
    def handle(self, *args, **options):
        # Set shutdown timeout
        shutdown_manager.shutdown_timeout = options['shutdown_timeout']
        
        # Start shutdown monitoring
        shutdown_monitor.start_monitoring()
        
        try:
            # Call the actual command implementation
            self.execute_command(*args, **options)
            
        except KeyboardInterrupt:
            self.stdout.write("Received interrupt signal, shutting down gracefully...")
            shutdown_manager.initiate_shutdown()
        
        finally:
            shutdown_monitor.stop_monitoring()
    
    def execute_command(self, *args, **options):
        """Override this method in subclasses"""
        raise NotImplementedError("Subclasses must implement execute_command")

def initialize_graceful_shutdown():
    """
    Initialize graceful shutdown system
    """
    # Register built-in cleanup tasks
    resource_cleanup.register_resource('cache', resource_cleanup.cleanup_cache)
    resource_cleanup.register_resource('memory', resource_cleanup.cleanup_memory)
    resource_cleanup.register_resource('temp_files', resource_cleanup.cleanup_temp_files)
    
    # Register with shutdown manager
    shutdown_manager.register_cleanup_task(resource_cleanup.cleanup_all_resources)
    
    logger.info("Graceful shutdown system initialized")

def get_shutdown_status():
    """
    Get current shutdown status and metrics
    """
    return {
        'is_shutting_down': shutdown_manager.is_shutting_down,
        'active_threads': len([t for t in shutdown_manager.active_threads if t.is_alive()]),
        'registered_hooks': len(shutdown_manager.shutdown_hooks),
        'registered_cleanup_tasks': len(shutdown_manager.cleanup_tasks),
        'health_metrics': shutdown_monitor.get_health_metrics(),
        'cleanup_stats': resource_cleanup.cleanup_stats
    }

# Auto-register essential cleanup functions
@cleanup_resource_decorator
def cleanup_django_cache():
    """Cleanup Django cache on shutdown"""
    try:
        cache.clear()
        logger.info("Django cache cleared during shutdown")
    except Exception as e:
        logger.error(f"Error clearing Django cache: {e}")

@cleanup_resource_decorator  
def cleanup_database_connections():
    """Cleanup database connections on shutdown"""
    try:
        from django.db import connections
        connections.close_all()
        logger.info("Database connections closed during shutdown")
    except Exception as e:
        logger.error(f"Error closing database connections: {e}")

@graceful_shutdown_decorator
def stop_background_monitoring():
    """Stop background monitoring tasks"""
    try:
        # Stop memory monitoring
        from .memory_optimization import memory_manager
        memory_manager.stop_monitoring()
        
        # Stop database health monitoring
        from .database_resilience import health_monitor
        health_monitor.stop_monitoring()
        
        logger.info("Background monitoring stopped")
    except Exception as e:
        logger.error(f"Error stopping background monitoring: {e}")

# Initialize on module import
initialize_graceful_shutdown()