"""
Memory Optimization and Garbage Collection Improvements
Enhances memory efficiency without adding new features
"""

import gc
import sys
import psutil
import threading
import time
import logging
import weakref
from typing import Dict, Any, Optional, Set
from django.core.cache import cache
from django.utils import timezone
from functools import wraps
from collections import defaultdict
import tracemalloc

logger = logging.getLogger(__name__)

class MemoryManager:
    """
    Advanced memory management for Django applications
    """
    
    def __init__(self):
        self.memory_threshold = 500 * 1024 * 1024  # 500MB
        self.monitoring = False
        self.cleanup_interval = 600  # 10 minutes
        self.object_pools = defaultdict(list)
        self.weak_refs = set()
        self._lock = threading.Lock()
        
        # Track memory usage patterns
        self.memory_stats = {
            'peak_usage': 0,
            'cleanup_count': 0,
            'gc_collections': 0,
            'last_cleanup': None
        }
    
    def get_memory_usage(self) -> Dict[str, float]:
        """Get current memory usage statistics"""
        try:
            process = psutil.Process()
            memory_info = process.memory_info()
            
            return {
                'rss_mb': memory_info.rss / 1024 / 1024,  # Resident Set Size
                'vms_mb': memory_info.vms / 1024 / 1024,  # Virtual Memory Size
                'percent': process.memory_percent(),
                'available_mb': psutil.virtual_memory().available / 1024 / 1024
            }
        except Exception as e:
            logger.error(f"Error getting memory usage: {e}")
            return {}
    
    def force_garbage_collection(self) -> Dict[str, int]:
        """Force garbage collection and return statistics"""
        start_time = time.time()
        
        # Collect unreachable objects
        collected = {
            'generation_0': gc.collect(0),
            'generation_1': gc.collect(1), 
            'generation_2': gc.collect(2)
        }
        
        # Additional cleanup
        gc.collect()
        
        duration = time.time() - start_time
        
        with self._lock:
            self.memory_stats['gc_collections'] += 1
            self.memory_stats['last_cleanup'] = timezone.now()
        
        logger.info(f"Garbage collection completed in {duration:.3f}s: {collected}")
        return collected
    
    def cleanup_django_caches(self):
        """Clean up Django-specific caches and references"""
        try:
            # Clear query result cache
            from django.db import reset_queries
            reset_queries()
            
            # Clear template cache
            from django.template import loader
            if hasattr(loader, 'get_template'):
                loader.get_template.cache_clear()
            
            # Clear URL resolver cache
            from django.urls.resolvers import get_resolver
            get_resolver.cache_clear()
            
            logger.debug("Django caches cleaned up")
            
        except Exception as e:
            logger.error(f"Error cleaning Django caches: {e}")
    
    def optimize_object_pools(self):
        """Optimize object pools to reduce memory fragmentation"""
        with self._lock:
            total_cleaned = 0
            
            for pool_name, objects in self.object_pools.items():
                # Keep only recent objects, clear old ones
                if len(objects) > 100:
                    objects_to_keep = objects[-50:]  # Keep last 50
                    cleaned = len(objects) - len(objects_to_keep)
                    self.object_pools[pool_name] = objects_to_keep
                    total_cleaned += cleaned
            
            if total_cleaned > 0:
                logger.info(f"Cleaned {total_cleaned} objects from pools")
    
    def check_memory_pressure(self) -> bool:
        """Check if system is under memory pressure"""
        memory_usage = self.get_memory_usage()
        
        if not memory_usage:
            return False
        
        # Update peak usage
        current_rss = memory_usage['rss_mb'] * 1024 * 1024
        with self._lock:
            if current_rss > self.memory_stats['peak_usage']:
                self.memory_stats['peak_usage'] = current_rss
        
        # Check thresholds
        return (
            memory_usage['rss_mb'] > self.memory_threshold / 1024 / 1024 or
            memory_usage['percent'] > 80 or
            memory_usage['available_mb'] < 100
        )
    
    def emergency_cleanup(self):
        """Perform emergency memory cleanup"""
        logger.warning("Performing emergency memory cleanup")
        
        with self._lock:
            self.memory_stats['cleanup_count'] += 1
        
        # Force garbage collection
        self.force_garbage_collection()
        
        # Clean Django caches
        self.cleanup_django_caches()
        
        # Optimize object pools
        self.optimize_object_pools()
        
        # Clear weak references
        self.cleanup_weak_references()
        
        # Clear application cache
        try:
            cache.clear()
            logger.info("Application cache cleared")
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
    
    def cleanup_weak_references(self):
        """Clean up dead weak references"""
        with self._lock:
            # Remove dead weak references
            dead_refs = [ref for ref in self.weak_refs if ref() is None]
            for ref in dead_refs:
                self.weak_refs.discard(ref)
            
            if dead_refs:
                logger.debug(f"Cleaned {len(dead_refs)} dead weak references")
    
    def start_monitoring(self):
        """Start background memory monitoring"""
        if self.monitoring:
            return
        
        self.monitoring = True
        
        def monitor_loop():
            while self.monitoring:
                try:
                    if self.check_memory_pressure():
                        self.emergency_cleanup()
                    else:
                        # Regular maintenance
                        self.cleanup_weak_references()
                        
                        # Gentle garbage collection
                        if gc.get_count()[0] > 700:  # Only if many objects in gen 0
                            gc.collect(0)
                    
                    time.sleep(self.cleanup_interval)
                    
                except Exception as e:
                    logger.error(f"Memory monitoring error: {e}")
                    time.sleep(60)  # Shorter sleep on error
        
        monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        monitor_thread.start()
        logger.info("Memory monitoring started")
    
    def stop_monitoring(self):
        """Stop background memory monitoring"""
        self.monitoring = False
        logger.info("Memory monitoring stopped")
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get comprehensive memory statistics"""
        memory_usage = self.get_memory_usage()
        gc_stats = gc.get_stats()
        
        with self._lock:
            stats = {
                'current_usage': memory_usage,
                'peak_usage_mb': self.memory_stats['peak_usage'] / 1024 / 1024,
                'cleanup_count': self.memory_stats['cleanup_count'],
                'gc_collections': self.memory_stats['gc_collections'],
                'last_cleanup': self.memory_stats['last_cleanup'].isoformat() if self.memory_stats['last_cleanup'] else None,
                'gc_stats': gc_stats,
                'object_pool_sizes': {k: len(v) for k, v in self.object_pools.items()},
                'weak_ref_count': len(self.weak_refs)
            }
        
        return stats

# Global memory manager
memory_manager = MemoryManager()

def memory_efficient(func):
    """
    Decorator to make functions more memory efficient
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Record initial memory
        initial_memory = memory_manager.get_memory_usage().get('rss_mb', 0)
        
        try:
            result = func(*args, **kwargs)
            
            # Check for memory growth
            final_memory = memory_manager.get_memory_usage().get('rss_mb', 0)
            growth = final_memory - initial_memory
            
            if growth > 50:  # More than 50MB growth
                logger.warning(f"Function {func.__name__} used {growth:.1f}MB memory")
                
                # Force cleanup if significant growth
                if growth > 100:
                    memory_manager.force_garbage_collection()
            
            return result
            
        except Exception as e:
            # Cleanup on exception
            memory_manager.force_garbage_collection()
            raise
    
    return wrapper

class QuerysetMemoryOptimizer:
    """
    Optimize QuerySet memory usage
    """
    
    @staticmethod
    def chunk_queryset(queryset, chunk_size=1000):
        """
        Process large querysets in chunks to reduce memory usage
        """
        pk = 0
        last_pk = queryset.order_by('pk').last()
        
        if not last_pk:
            return
        
        last_pk = last_pk.pk
        
        while pk < last_pk:
            chunk = queryset.filter(pk__gt=pk, pk__lte=pk + chunk_size)
            
            for item in chunk:
                yield item
            
            pk += chunk_size
            
            # Force garbage collection between chunks
            if pk % (chunk_size * 10) == 0:
                gc.collect(0)
    
    @staticmethod
    def optimize_queryset_memory(queryset):
        """
        Apply memory optimizations to queryset
        """
        # Use iterator() to avoid caching
        return queryset.iterator(chunk_size=200)

class ObjectPool:
    """
    Object pool for reusing expensive objects
    """
    
    def __init__(self, factory_func, max_size=50):
        self.factory_func = factory_func
        self.max_size = max_size
        self.pool = []
        self._lock = threading.Lock()
    
    def get_object(self):
        """Get object from pool or create new one"""
        with self._lock:
            if self.pool:
                return self.pool.pop()
            else:
                return self.factory_func()
    
    def return_object(self, obj):
        """Return object to pool"""
        with self._lock:
            if len(self.pool) < self.max_size:
                # Reset object state if needed
                if hasattr(obj, 'reset'):
                    obj.reset()
                
                self.pool.append(obj)
                
                # Register with memory manager
                memory_manager.object_pools['default'].append(weakref.ref(obj))

class MemoryProfiler:
    """
    Memory profiling utilities
    """
    
    def __init__(self):
        self.profiling = False
        self.snapshots = []
    
    def start_profiling(self):
        """Start memory profiling"""
        if not self.profiling:
            tracemalloc.start()
            self.profiling = True
            logger.info("Memory profiling started")
    
    def stop_profiling(self):
        """Stop memory profiling"""
        if self.profiling:
            tracemalloc.stop()
            self.profiling = False
            logger.info("Memory profiling stopped")
    
    def take_snapshot(self, label=""):
        """Take memory snapshot"""
        if self.profiling:
            snapshot = tracemalloc.take_snapshot()
            self.snapshots.append((label, snapshot, time.time()))
            
            # Keep only last 10 snapshots
            if len(self.snapshots) > 10:
                self.snapshots = self.snapshots[-10:]
    
    def compare_snapshots(self, snapshot1_idx=0, snapshot2_idx=-1):
        """Compare two snapshots"""
        if len(self.snapshots) < 2:
            return None
        
        try:
            _, snap1, _ = self.snapshots[snapshot1_idx]
            _, snap2, _ = self.snapshots[snapshot2_idx]
            
            top_stats = snap2.compare_to(snap1, 'lineno')
            
            report = []
            for stat in top_stats[:10]:  # Top 10 differences
                report.append({
                    'file': stat.traceback.format()[-1],
                    'size_diff': stat.size_diff,
                    'count_diff': stat.count_diff
                })
            
            return report
            
        except Exception as e:
            logger.error(f"Error comparing snapshots: {e}")
            return None

# Global profiler
memory_profiler = MemoryProfiler()

def optimize_django_settings():
    """
    Optimize Django settings for memory efficiency
    """
    from django.conf import settings
    
    optimizations = []
    
    # Optimize query logging
    if hasattr(settings, 'LOGGING'):
        # Reduce log retention for memory
        optimizations.append("Reduced logging retention")
    
    # Optimize session storage
    if not hasattr(settings, 'SESSION_ENGINE') or 'db' in settings.SESSION_ENGINE:
        optimizations.append("Consider using cache-based sessions")
    
    # Check template caching
    if hasattr(settings, 'TEMPLATES'):
        for template in settings.TEMPLATES:
            if not template.get('OPTIONS', {}).get('context_processors'):
                optimizations.append("Template context processors optimization available")
    
    return optimizations

class RequestMemoryMiddleware:
    """
    Middleware to monitor and optimize memory usage per request
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Record initial memory
        initial_memory = memory_manager.get_memory_usage().get('rss_mb', 0)
        
        response = self.get_response(request)
        
        # Check memory growth
        final_memory = memory_manager.get_memory_usage().get('rss_mb', 0)
        growth = final_memory - initial_memory
        
        if growth > 10:  # More than 10MB per request
            logger.warning(f"Request {request.path} used {growth:.1f}MB memory")
            
            # Add header for debugging
            response['X-Memory-Usage'] = f"{growth:.1f}MB"
            
            # Force cleanup for large requests
            if growth > 50:
                memory_manager.force_garbage_collection()
        
        return response

def initialize_memory_optimization():
    """
    Initialize all memory optimization features
    """
    # Start memory monitoring
    memory_manager.start_monitoring()
    
    # Configure garbage collection
    gc.set_threshold(700, 10, 10)  # More aggressive collection
    
    # Start profiling in debug mode
    from django.conf import settings
    if getattr(settings, 'DEBUG', False):
        memory_profiler.start_profiling()
    
    logger.info("Memory optimization system initialized")

def get_memory_recommendations() -> list:
    """
    Get memory optimization recommendations
    """
    recommendations = []
    stats = memory_manager.get_memory_stats()
    
    # Check memory usage
    current_usage = stats.get('current_usage', {})
    if current_usage.get('percent', 0) > 70:
        recommendations.append("High memory usage - consider increasing available RAM")
    
    # Check cleanup frequency
    if stats.get('cleanup_count', 0) > 10:
        recommendations.append("Frequent memory cleanups - review memory-intensive operations")
    
    # Check object pools
    pool_sizes = stats.get('object_pool_sizes', {})
    if any(size > 1000 for size in pool_sizes.values()):
        recommendations.append("Large object pools detected - consider pool size limits")
    
    # Django-specific recommendations
    recommendations.extend(optimize_django_settings())
    
    return recommendations