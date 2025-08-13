"""
Database Query Optimization for Stock Scanner
Provides optimized queries with select_related, prefetch_related, and performance monitoring
"""

from django.db import models, connection
from django.core.cache import cache
from django.utils import timezone
from datetime import timedelta
import logging
import time
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)

class PerformanceQuerySet(models.QuerySet):
    """
    QuerySet with automatic performance optimizations and monitoring
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._query_start_time = None
        self._query_name = None
    
    def with_performance_monitoring(self, query_name: str):
        """Enable performance monitoring for this query"""
        self._query_name = query_name
        return self
    
    def _fetch_all(self):
        """Override to add performance monitoring"""
        if self._query_name:
            start_time = time.time()
            
        super()._fetch_all()
        
        if self._query_name:
            duration = time.time() - start_time
            if duration > 0.1:  # Log slow queries (>100ms)
                logger.warning(f"Slow query '{self._query_name}': {duration:.3f}s")
            
            # Cache query performance stats
            stats_key = f"query_stats_{self._query_name}"
            stats = cache.get(stats_key, {'count': 0, 'total_time': 0, 'avg_time': 0})
            stats['count'] += 1
            stats['total_time'] += duration
            stats['avg_time'] = stats['total_time'] / stats['count']
            cache.set(stats_key, stats, 3600)  # Cache for 1 hour

class OptimizedStockQuerySet(PerformanceQuerySet):
    """
    Optimized QuerySet for Stock model with intelligent prefetching
    """
    
    def with_full_data(self):
        """Get stocks with all related data optimized"""
        return self.select_related().prefetch_related(
            'stockprice_set',
            'stockalert_set',
            'portfolioholding_set'
        ).with_performance_monitoring('stock_full_data')
    
    def active_stocks(self):
        """Get stocks that are actively updated"""
        cutoff = timezone.now() - timedelta(days=7)
        return self.filter(
            last_updated__gte=cutoff,
            current_price__isnull=False,
            current_price__gt=0
        ).with_performance_monitoring('active_stocks')
    
    def by_exchange(self, exchange: str):
        """Get stocks filtered by exchange with optimizations"""
        return self.filter(
            exchange__iexact=exchange
        ).order_by('market_cap').reverse().with_performance_monitoring(f'stocks_by_exchange_{exchange}')
    
    def gainers(self, limit: int = 50):
        """Get top gainers with optimization"""
        return self.active_stocks().filter(
            change_percent__gt=0
        ).order_by('-change_percent')[:limit].with_performance_monitoring('top_gainers')
    
    def losers(self, limit: int = 50):
        """Get top losers with optimization"""
        return self.active_stocks().filter(
            change_percent__lt=0
        ).order_by('change_percent')[:limit].with_performance_monitoring('top_losers')
    
    def high_volume(self, limit: int = 50):
        """Get high volume stocks with optimization"""
        return self.active_stocks().filter(
            volume__isnull=False,
            avg_volume_3mon__isnull=False
        ).extra(
            select={'volume_ratio': 'volume / GREATEST(avg_volume_3mon, 1)'}
        ).order_by('-volume_ratio')[:limit].with_performance_monitoring('high_volume')
    
    def by_market_cap_range(self, min_cap: int = None, max_cap: int = None):
        """Filter by market cap range with optimization"""
        queryset = self.active_stocks()
        
        if min_cap:
            queryset = queryset.filter(market_cap__gte=min_cap)
        if max_cap:
            queryset = queryset.filter(market_cap__lte=max_cap)
            
        return queryset.order_by('-market_cap').with_performance_monitoring('market_cap_filtered')
    
    def search_optimized(self, query: str, limit: int = 50):
        """Optimized search with relevance scoring"""
        if not query or len(query) < 2:
            return self.none()
        
        # Use database-specific optimizations
        if connection.vendor == 'mysql':
            return self._mysql_search(query, limit)
        else:
            return self._generic_search(query, limit)
    
    def _mysql_search(self, query: str, limit: int):
        """MySQL-optimized search using MATCH AGAINST"""
        return self.extra(
            select={
                'relevance': """
                MATCH(ticker, company_name, symbol, name) AGAINST (%s IN BOOLEAN MODE) +
                CASE 
                    WHEN ticker = %s THEN 100
                    WHEN ticker LIKE %s THEN 50
                    WHEN company_name LIKE %s THEN 25
                    ELSE 0
                END
                """
            },
            select_params=[f"{query}*", query, f"{query}%", f"%{query}%"],
            where=["MATCH(ticker, company_name, symbol, name) AGAINST (%s IN BOOLEAN MODE) OR ticker LIKE %s OR company_name LIKE %s"],
            params=[f"{query}*", f"{query}%", f"%{query}%"]
        ).order_by('-relevance')[:limit].with_performance_monitoring('mysql_search')
    
    def _generic_search(self, query: str, limit: int):
        """Generic search fallback"""
        from django.db.models import Q, Case, When, IntegerField
        
        q_exact_ticker = Q(ticker__iexact=query)
        q_starts_ticker = Q(ticker__istartswith=query)
        q_contains_name = Q(company_name__icontains=query)
        q_contains_symbol = Q(symbol__icontains=query)
        
        return self.filter(
            q_exact_ticker | q_starts_ticker | q_contains_name | q_contains_symbol
        ).annotate(
            relevance=Case(
                When(q_exact_ticker, then=100),
                When(q_starts_ticker, then=50),
                When(q_contains_name, then=25),
                default=10,
                output_field=IntegerField()
            )
        ).order_by('-relevance')[:limit].with_performance_monitoring('generic_search')

class OptimizedPortfolioQuerySet(PerformanceQuerySet):
    """
    Optimized QuerySet for Portfolio operations
    """
    
    def with_holdings(self):
        """Get portfolios with optimized holdings prefetch"""
        return self.prefetch_related(
            models.Prefetch(
                'holdings',
                queryset=self.model.holdings.related.related_model.objects.select_related('stock')
            )
        ).with_performance_monitoring('portfolio_with_holdings')
    
    def public_portfolios(self):
        """Get public portfolios with user data"""
        return self.filter(is_public=True).select_related('user').with_performance_monitoring('public_portfolios')
    
    def top_performing(self, limit: int = 20):
        """Get top performing portfolios"""
        return self.public_portfolios().filter(
            total_return_percent__gt=0
        ).order_by('-total_return_percent')[:limit].with_performance_monitoring('top_performing_portfolios')

class CachedQueryMixin:
    """
    Mixin to add intelligent caching to querysets
    """
    
    def cached(self, timeout: int = 300, cache_key_suffix: str = None):
        """Cache the queryset results"""
        if not cache_key_suffix:
            cache_key_suffix = str(hash(str(self.query)))[:8]
        
        cache_key = f"queryset_{self.model._meta.label_lower}_{cache_key_suffix}"
        
        # Try to get from cache
        cached_result = cache.get(cache_key)
        if cached_result is not None:
            logger.debug(f"Cache hit for queryset: {cache_key}")
            return cached_result
        
        # Execute query and cache result
        result = list(self)
        cache.set(cache_key, result, timeout)
        logger.debug(f"Cached queryset result: {cache_key}")
        
        return result

class OptimizedStockManager(models.Manager):
    """
    Manager with optimized queries for Stock model
    """
    
    def get_queryset(self):
        return OptimizedStockQuerySet(self.model, using=self._db)
    
    def active_stocks(self):
        return self.get_queryset().active_stocks()
    
    def by_exchange(self, exchange: str):
        return self.get_queryset().by_exchange(exchange)
    
    def gainers(self, limit: int = 50):
        return self.get_queryset().gainers(limit)
    
    def losers(self, limit: int = 50):
        return self.get_queryset().losers(limit)
    
    def high_volume(self, limit: int = 50):
        return self.get_queryset().high_volume(limit)
    
    def search(self, query: str, limit: int = 50):
        return self.get_queryset().search_optimized(query, limit)
    
    def market_overview_data(self):
        """Get optimized data for market overview"""
        cache_key = 'market_overview_data'
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return cached_data
        
        # Use raw SQL for complex aggregations
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_stocks,
                    COUNT(CASE WHEN current_price > 0 THEN 1 END) as active_stocks,
                    COUNT(CASE WHEN change_percent > 0 THEN 1 END) as gainers,
                    COUNT(CASE WHEN change_percent < 0 THEN 1 END) as losers,
                    SUM(CASE WHEN volume IS NOT NULL THEN volume ELSE 0 END) as total_volume,
                    AVG(CASE WHEN change_percent IS NOT NULL THEN change_percent END) as avg_change
                FROM stocks_stock 
                WHERE last_updated >= %s AND current_price > 0
            """, [timezone.now() - timedelta(days=1)])
            
            row = cursor.fetchone()
            
        data = {
            'total_stocks': row[0] or 0,
            'active_stocks': row[1] or 0,
            'gainers_count': row[2] or 0,
            'losers_count': row[3] or 0,
            'total_volume': row[4] or 0,
            'avg_change_percent': row[5] or 0,
            'last_updated': timezone.now()
        }
        
        # Cache for 5 minutes
        cache.set(cache_key, data, 300)
        return data

class QueryOptimizer:
    """
    Utility class for query optimization and analysis
    """
    
    @staticmethod
    def analyze_query_performance():
        """Analyze query performance from cache"""
        query_stats = {}
        
        # Get all query stats from cache
        cache_keys = cache.keys('query_stats_*') if hasattr(cache, 'keys') else []
        
        for key in cache_keys:
            stats = cache.get(key)
            if stats:
                query_name = key.replace('query_stats_', '')
                query_stats[query_name] = stats
        
        return query_stats
    
    @staticmethod
    def reset_query_stats():
        """Reset query performance statistics"""
        cache_keys = cache.keys('query_stats_*') if hasattr(cache, 'keys') else []
        for key in cache_keys:
            cache.delete(key)
    
    @staticmethod
    def get_slow_queries(threshold: float = 0.1):
        """Get queries that exceed the time threshold"""
        stats = QueryOptimizer.analyze_query_performance()
        slow_queries = {}
        
        for query_name, data in stats.items():
            if data.get('avg_time', 0) > threshold:
                slow_queries[query_name] = data
        
        return slow_queries
    
    @staticmethod
    def optimize_database_settings():
        """Suggest database optimization settings"""
        suggestions = []
        
        # Check for common performance issues
        with connection.cursor() as cursor:
            # Check if indexes are being used
            cursor.execute("SHOW PROCESSLIST" if connection.vendor == 'mysql' else "SELECT 1")
            
            suggestions.append({
                'type': 'index',
                'message': 'Consider adding indexes on frequently queried fields',
                'fields': ['ticker', 'market_cap', 'change_percent', 'last_updated']
            })
            
            suggestions.append({
                'type': 'cache',
                'message': 'Implement query result caching for expensive operations',
                'queries': ['market_overview_data', 'top_gainers', 'search_results']
            })
        
        return suggestions

class DatabaseConnection:
    """
    Context manager for database connections with performance monitoring
    """
    
    def __init__(self, query_name: str = None):
        self.query_name = query_name
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        return connection.cursor()
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.query_name and self.start_time:
            duration = time.time() - self.start_time
            if duration > 0.05:  # Log queries >50ms
                logger.info(f"Database query '{self.query_name}': {duration:.3f}s")

# Monkey patch to add performance monitoring to Django's QuerySet
original_execute = models.sql.compiler.SQLCompiler.execute_sql

def execute_sql_with_monitoring(self, result_type=None, chunked_fetch=False, chunk_size=0):
    """Enhanced execute_sql with performance monitoring"""
    start_time = time.time()
    result = original_execute(self, result_type, chunked_fetch, chunk_size)
    duration = time.time() - start_time
    
    if duration > 0.1:  # Log slow SQL queries
        logger.warning(f"Slow SQL query: {duration:.3f}s - {str(self.query)[:200]}...")
    
    return result

# Apply the monkey patch
models.sql.compiler.SQLCompiler.execute_sql = execute_sql_with_monitoring