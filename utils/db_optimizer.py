"""
Database Performance Optimization Utilities
Advanced query optimization and connection management for Stock Scanner API
"""

import time
import logging
from functools import wraps
from typing import List, Dict, Any, Optional, Union
from contextlib import contextmanager

from django.db import connection, transaction
from django.db.models import QuerySet, Prefetch
from django.core.cache import cache
from django.conf import settings

logger = logging.getLogger(__name__)

class QueryOptimizer:
    """
    Advanced database query optimization utilities
    """
    
    @staticmethod
    def log_slow_queries(threshold_ms: int = 100):
        """
        Decorator to log slow database queries
        """
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                result = func(*args, **kwargs)
                
                execution_time = (time.time() - start_time) * 1000
                if execution_time > threshold_ms:
                    logger.warning(
                        f"Slow query in {func.__name__}: {execution_time:.2f}ms"
                    )
                
                return result
            return wrapper
        return decorator
    
    @staticmethod
    def optimize_queryset(queryset: QuerySet, 
                         select_related: List[str] = None,
                         prefetch_related: List[str] = None,
                         only_fields: List[str] = None,
                         defer_fields: List[str] = None) -> QuerySet:
        """
        Apply common query optimizations to a QuerySet
        """
        optimized_qs = queryset
        
        # Use select_related for foreign key relationships
        if select_related:
            optimized_qs = optimized_qs.select_related(*select_related)
        
        # Use prefetch_related for many-to-many or reverse foreign keys
        if prefetch_related:
            optimized_qs = optimized_qs.prefetch_related(*prefetch_related)
        
        # Only load specific fields if specified
        if only_fields:
            optimized_qs = optimized_qs.only(*only_fields)
        
        # Defer heavy fields if specified
        if defer_fields:
            optimized_qs = optimized_qs.defer(*defer_fields)
        
        return optimized_qs
    
    @staticmethod
    def batch_process(queryset: QuerySet, 
                     batch_size: int = 1000,
                     processor_func: callable = None):
        """
        Process large datasets in batches to prevent memory issues
        """
        total_count = queryset.count()
        processed = 0
        
        while processed < total_count:
            batch = queryset[processed:processed + batch_size]
            
            if processor_func:
                processor_func(batch)
            
            processed += batch_size
            
            # Optional: yield progress for monitoring
            yield {
                'processed': processed,
                'total': total_count,
                'percentage': (processed / total_count) * 100
            }

class ConnectionOptimizer:
    """
    Database connection optimization utilities
    """
    
    @staticmethod
    @contextmanager
    def optimized_connection():
        """
        Context manager for optimized database connections
        """
        # Store original settings
        original_autocommit = connection.get_autocommit()
        
        try:
            # Disable autocommit for better performance in bulk operations
            connection.set_autocommit(False)
            
            with transaction.atomic():
                yield connection
                
        finally:
            # Restore original autocommit setting
            connection.set_autocommit(original_autocommit)
    
    @staticmethod
    def execute_raw_query(query: str, params: List[Any] = None) -> List[Dict]:
        """
        Execute raw SQL with proper connection handling
        """
        with connection.cursor() as cursor:
            cursor.execute(query, params or [])
            
            if cursor.description:
                columns = [col[0] for col in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            return []

class StockDataOptimizer:
    """
    Specific optimizations for stock data operations
    """
    
    @staticmethod
    @QueryOptimizer.log_slow_queries(threshold_ms=50)
    def get_trending_stocks(limit: int = 10) -> List[Dict]:
        """
        Optimized query for trending stocks with caching
        """
        cache_key = f"trending_stocks_{limit}"
        cached_result = cache.get(cache_key)
        
        if cached_result:
            return cached_result
        
        # Optimized raw query for performance
        query = """
        SELECT 
            s.symbol,
            s.company_name,
            s.current_price,
            s.price_change,
            s.volume,
            s.market_cap,
            CASE 
                WHEN s.price_change > 0 THEN 'up'
                WHEN s.price_change < 0 THEN 'down'
                ELSE 'neutral'
            END as trend_direction
        FROM stocks s
        WHERE s.is_active = true
        AND s.volume > 1000000  -- High volume filter
        ORDER BY 
            ABS(s.price_change_percent) DESC,
            s.volume DESC
        LIMIT %s
        """
        
        result = ConnectionOptimizer.execute_raw_query(query, [limit])
        
        # Cache for 3 minutes
        cache.set(cache_key, result, 180)
        
        return result
    
    @staticmethod
    def bulk_update_stock_prices(stock_updates: List[Dict]):
        """
        Efficiently update multiple stock prices in bulk
        """
        if not stock_updates:
            return
        
        # Use raw SQL for maximum performance
        with ConnectionOptimizer.optimized_connection():
            with connection.cursor() as cursor:
                # Prepare bulk update query
                query = """
                UPDATE stocks 
                SET 
                    current_price = %s,
                    price_change = %s,
                    price_change_percent = %s,
                    volume = %s,
                    last_updated = NOW()
                WHERE symbol = %s
                """
                
                # Prepare data for executemany
                update_data = [
                    (
                        update['price'],
                        update['change'],
                        update['change_percent'],
                        update['volume'],
                        update['symbol']
                    )
                    for update in stock_updates
                ]
                
                cursor.executemany(query, update_data)
                
                logger.info(f"Bulk updated {len(stock_updates)} stock prices")

class PerformanceAnalyzer:
    """
    Database performance analysis and monitoring
    """
    
    @staticmethod
    def analyze_query_performance():
        """
        Analyze current database query performance
        """
        if settings.DEBUG:
            queries = connection.queries
            total_time = sum(float(q['time']) for q in queries)
            
            slow_queries = [
                q for q in queries 
                if float(q['time']) > 0.1  # Queries taking > 100ms
            ]
            
            analysis = {
                'total_queries': len(queries),
                'total_time': f"{total_time:.3f}s",
                'slow_queries': len(slow_queries),
                'avg_time_per_query': f"{total_time / len(queries):.3f}s" if queries else "0s"
            }
            
            if slow_queries:
                analysis['slowest_query'] = max(
                    slow_queries, key=lambda x: float(x['time'])
                )
            
            return analysis
        
        return {'error': 'Query analysis only available in DEBUG mode'}
    
    @staticmethod
    def get_database_stats():
        """
        Get current database statistics
        """
        with connection.cursor() as cursor:
            # Get table sizes and row counts
            cursor.execute("""
                SELECT 
                    table_name,
                    table_rows,
                    ROUND((data_length + index_length) / 1024 / 1024, 2) AS size_mb
                FROM information_schema.tables 
                WHERE table_schema = DATABASE()
                ORDER BY (data_length + index_length) DESC
            """)
            
            return cursor.fetchall()

# Decorator for automatic query optimization
def optimize_db_access(select_related=None, prefetch_related=None, cache_timeout=None):
    """
    Decorator that automatically optimizes database access
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Apply caching if specified
            if cache_timeout:
                cache_key = f"{func.__name__}_{hash(str(args) + str(kwargs))}"
                cached_result = cache.get(cache_key)
                if cached_result:
                    return cached_result
            
            # Execute function
            result = func(*args, **kwargs)
            
            # Apply QuerySet optimizations if result is a QuerySet
            if isinstance(result, QuerySet):
                result = QueryOptimizer.optimize_queryset(
                    result,
                    select_related=select_related,
                    prefetch_related=prefetch_related
                )
            
            # Cache result if specified
            if cache_timeout and result is not None:
                cache.set(cache_key, result, cache_timeout)
            
            return result
        return wrapper
    return decorator

# Performance monitoring context manager
@contextmanager
def monitor_db_performance(operation_name: str = "Database Operation"):
    """
    Context manager to monitor database performance
    """
    start_time = time.time()
    start_queries = len(connection.queries) if settings.DEBUG else 0
    
    try:
        yield
    finally:
        execution_time = time.time() - start_time
        end_queries = len(connection.queries) if settings.DEBUG else 0
        query_count = end_queries - start_queries
        
        logger.info(
            f"{operation_name} completed in {execution_time:.3f}s "
            f"with {query_count} queries"
        )
        
        if execution_time > 1.0:  # Log slow operations
            logger.warning(
                f"Slow {operation_name}: {execution_time:.3f}s with {query_count} queries"
            )

# Example usage:
"""
from utils.db_optimizer import optimize_db_access, monitor_db_performance, StockDataOptimizer

# Optimized view with caching and query optimization
@optimize_db_access(
    select_related=['category', 'exchange'],
    prefetch_related=['tags'],
    cache_timeout=300
)
def get_stocks_with_details():
    return Stock.objects.filter(is_active=True)

# Monitor database performance
def heavy_database_operation():
    with monitor_db_performance("Heavy Operation"):
        # Your database operations here
        stocks = StockDataOptimizer.get_trending_stocks(50)
        return stocks
"""