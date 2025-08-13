"""
Database Connection Resilience and Retry Mechanisms
Enhances database reliability without adding new features
"""

import time
import logging
import functools
from typing import Callable, Any, Optional
from django.db import connection, transaction, OperationalError, InterfaceError
from django.core.cache import cache
from django.utils import timezone
from contextlib import contextmanager
import threading

logger = logging.getLogger(__name__)

class DatabaseResilienceManager:
    """
    Manages database connection resilience with automatic retry and recovery
    """
    
    def __init__(self):
        self.connection_failures = 0
        self.last_failure_time = None
        self.failure_threshold = 5
        self.backoff_time = 60  # seconds
        self._lock = threading.Lock()
    
    def is_connection_healthy(self) -> bool:
        """Check if database connection is healthy"""
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
            
            # Reset failure count on successful connection
            with self._lock:
                self.connection_failures = 0
                self.last_failure_time = None
            
            return True
            
        except (OperationalError, InterfaceError) as e:
            logger.error(f"Database connection health check failed: {e}")
            
            with self._lock:
                self.connection_failures += 1
                self.last_failure_time = time.time()
            
            return False
    
    def should_retry_connection(self) -> bool:
        """Determine if connection retry should be attempted"""
        with self._lock:
            if self.connection_failures < self.failure_threshold:
                return True
            
            if self.last_failure_time:
                time_since_failure = time.time() - self.last_failure_time
                return time_since_failure > self.backoff_time
            
            return True
    
    def close_connection(self):
        """Safely close database connection"""
        try:
            connection.close()
            logger.info("Database connection closed gracefully")
        except Exception as e:
            logger.error(f"Error closing database connection: {e}")

# Global resilience manager instance
db_resilience = DatabaseResilienceManager()

def database_retry(max_retries: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """
    Decorator for database operations with retry logic
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    # Check connection health before retry
                    if attempt > 0:
                        if not db_resilience.should_retry_connection():
                            logger.warning(f"Skipping retry for {func.__name__} due to connection failures")
                            break
                        
                        # Close and reconnect on retry
                        db_resilience.close_connection()
                        time.sleep(delay * (backoff ** attempt))
                    
                    result = func(*args, **kwargs)
                    
                    # Log successful recovery
                    if attempt > 0:
                        logger.info(f"Database operation {func.__name__} succeeded after {attempt} retries")
                    
                    return result
                    
                except (OperationalError, InterfaceError) as e:
                    last_exception = e
                    logger.warning(f"Database operation {func.__name__} failed (attempt {attempt + 1}): {e}")
                    
                    if attempt == max_retries:
                        logger.error(f"Database operation {func.__name__} failed after {max_retries} retries")
                        break
                
                except Exception as e:
                    # Non-database errors should not be retried
                    logger.error(f"Non-database error in {func.__name__}: {e}")
                    raise
            
            # Raise the last exception if all retries failed
            if last_exception:
                raise last_exception
            
            return None
        
        return wrapper
    return decorator

@contextmanager
def resilient_transaction():
    """
    Context manager for resilient database transactions
    """
    max_retries = 3
    retry_count = 0
    
    while retry_count <= max_retries:
        try:
            with transaction.atomic():
                yield
                break  # Success, exit retry loop
                
        except (OperationalError, InterfaceError) as e:
            retry_count += 1
            
            if retry_count > max_retries:
                logger.error(f"Transaction failed after {max_retries} retries: {e}")
                raise
            
            logger.warning(f"Transaction failed (attempt {retry_count}), retrying: {e}")
            
            # Close connection and wait before retry
            db_resilience.close_connection()
            time.sleep(1.0 * retry_count)
        
        except Exception as e:
            # Non-database errors should not be retried
            logger.error(f"Non-database error in transaction: {e}")
            raise

class ConnectionPoolManager:
    """
    Enhanced connection pool management
    """
    
    def __init__(self):
        self.max_connections = 20
        self.active_connections = 0
        self._lock = threading.Lock()
    
    @contextmanager
    def get_connection(self):
        """Get database connection with pool management"""
        connection_acquired = False
        
        try:
            with self._lock:
                if self.active_connections >= self.max_connections:
                    logger.warning("Connection pool exhausted, waiting...")
                    time.sleep(0.1)
                
                self.active_connections += 1
                connection_acquired = True
            
            # Health check before using connection
            if not db_resilience.is_connection_healthy():
                db_resilience.close_connection()
            
            yield connection
            
        finally:
            if connection_acquired:
                with self._lock:
                    self.active_connections = max(0, self.active_connections - 1)

# Global connection pool manager
connection_pool = ConnectionPoolManager()

class DatabaseMetrics:
    """
    Track database performance metrics without external dependencies
    """
    
    def __init__(self):
        self.query_count = 0
        self.slow_queries = 0
        self.connection_errors = 0
        self.total_query_time = 0.0
        self._lock = threading.Lock()
    
    def record_query(self, duration: float):
        """Record query execution metrics"""
        with self._lock:
            self.query_count += 1
            self.total_query_time += duration
            
            if duration > 0.1:  # Slow query threshold
                self.slow_queries += 1
    
    def record_connection_error(self):
        """Record connection error"""
        with self._lock:
            self.connection_errors += 1
    
    def get_metrics(self) -> dict:
        """Get current metrics"""
        with self._lock:
            avg_time = self.total_query_time / max(1, self.query_count)
            
            return {
                'query_count': self.query_count,
                'slow_queries': self.slow_queries,
                'connection_errors': self.connection_errors,
                'average_query_time': round(avg_time, 3),
                'slow_query_percentage': round((self.slow_queries / max(1, self.query_count)) * 100, 2)
            }
    
    def reset_metrics(self):
        """Reset all metrics"""
        with self._lock:
            self.query_count = 0
            self.slow_queries = 0
            self.connection_errors = 0
            self.total_query_time = 0.0

# Global metrics instance
db_metrics = DatabaseMetrics()

@contextmanager
def monitored_query(query_name: str = "unknown"):
    """
    Context manager for monitoring query performance
    """
    start_time = time.time()
    
    try:
        yield
    except (OperationalError, InterfaceError):
        db_metrics.record_connection_error()
        raise
    finally:
        duration = time.time() - start_time
        db_metrics.record_query(duration)
        
        if duration > 0.1:
            logger.warning(f"Slow query '{query_name}': {duration:.3f}s")

def get_database_status() -> dict:
    """
    Get comprehensive database status
    """
    status = {
        'connection_healthy': db_resilience.is_connection_healthy(),
        'connection_failures': db_resilience.connection_failures,
        'active_connections': connection_pool.active_connections,
        'metrics': db_metrics.get_metrics(),
        'last_check': timezone.now().isoformat()
    }
    
    return status

class QueryOptimizer:
    """
    Runtime query optimization utilities
    """
    
    @staticmethod
    def analyze_query_plan(query: str) -> dict:
        """
        Analyze query execution plan (MySQL specific)
        """
        try:
            with connection.cursor() as cursor:
                # Get query execution plan
                cursor.execute(f"EXPLAIN {query}")
                plan = cursor.fetchall()
                
                analysis = {
                    'has_index_usage': any('index' in str(row).lower() for row in plan),
                    'estimated_rows': sum(int(row[8]) if row[8] and str(row[8]).isdigit() else 0 for row in plan),
                    'plan_complexity': len(plan),
                    'recommendations': []
                }
                
                # Add recommendations based on plan
                for row in plan:
                    if 'Using filesort' in str(row):
                        analysis['recommendations'].append('Consider adding index for ORDER BY clause')
                    if 'Using temporary' in str(row):
                        analysis['recommendations'].append('Query using temporary table - consider optimization')
                
                return analysis
                
        except Exception as e:
            logger.error(f"Error analyzing query plan: {e}")
            return {'error': str(e)}
    
    @staticmethod
    def suggest_indexes(table_name: str, frequent_columns: list) -> list:
        """
        Suggest database indexes based on usage patterns
        """
        suggestions = []
        
        try:
            with connection.cursor() as cursor:
                # Check existing indexes
                cursor.execute(f"SHOW INDEX FROM {table_name}")
                existing_indexes = cursor.fetchall()
                
                existing_columns = set(row[4] for row in existing_indexes)
                
                # Suggest missing indexes
                for column in frequent_columns:
                    if column not in existing_columns:
                        suggestions.append(f"CREATE INDEX idx_{table_name}_{column} ON {table_name}({column})")
                
                return suggestions
                
        except Exception as e:
            logger.error(f"Error suggesting indexes: {e}")
            return []

# Apply database resilience to existing managers
def enhance_existing_managers():
    """
    Enhance existing model managers with resilience
    """
    from django.db import models
    
    # Monkey patch QuerySet to add resilience
    original_iterator = models.QuerySet.__iter__
    
    @database_retry(max_retries=2)
    def resilient_iterator(self):
        with monitored_query(f"queryset_{self.model._meta.label}"):
            return original_iterator(self)
    
    models.QuerySet.__iter__ = resilient_iterator
    
    # Monkey patch save method
    original_save = models.Model.save
    
    @database_retry(max_retries=2)
    def resilient_save(self, *args, **kwargs):
        with monitored_query(f"save_{self._meta.label}"):
            return original_save(self, *args, **kwargs)
    
    models.Model.save = resilient_save

# Automatic connection health monitoring
class ConnectionHealthMonitor:
    """
    Background connection health monitoring
    """
    
    def __init__(self):
        self.monitoring = False
        self.check_interval = 300  # 5 minutes
    
    def start_monitoring(self):
        """Start background health monitoring"""
        if self.monitoring:
            return
        
        self.monitoring = True
        import threading
        
        def monitor_loop():
            while self.monitoring:
                try:
                    status = get_database_status()
                    
                    # Cache status for health endpoints
                    cache.set('db_health_status', status, 60)
                    
                    if not status['connection_healthy']:
                        logger.error("Database connection health check failed")
                    
                    time.sleep(self.check_interval)
                    
                except Exception as e:
                    logger.error(f"Health monitoring error: {e}")
                    time.sleep(30)  # Shorter retry on error
        
        monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        monitor_thread.start()
        logger.info("Database health monitoring started")
    
    def stop_monitoring(self):
        """Stop background health monitoring"""
        self.monitoring = False
        logger.info("Database health monitoring stopped")

# Global health monitor
health_monitor = ConnectionHealthMonitor()

# Initialize enhancements
def initialize_database_resilience():
    """
    Initialize all database resilience features
    """
    enhance_existing_managers()
    health_monitor.start_monitoring()
    logger.info("Database resilience system initialized")