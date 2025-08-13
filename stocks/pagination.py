"""
Custom Pagination Classes for Stock Scanner API
Provides efficient pagination with performance optimizations
"""

from rest_framework.pagination import PageNumberPagination, LimitOffsetPagination
from rest_framework.response import Response
from collections import OrderedDict
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)

class StockPagination(PageNumberPagination):
    """
    Optimized pagination for stock data with caching
    """
    page_size = 50
    page_size_query_param = 'limit'
    max_page_size = 1000
    page_query_param = 'page'
    
    def get_paginated_response(self, data):
        """
        Enhanced paginated response with performance metrics
        """
        # Calculate additional metadata
        total_pages = self.page.paginator.num_pages
        current_page = self.page.number
        
        return Response(OrderedDict([
            ('status', 'success'),
            ('pagination', {
                'count': self.page.paginator.count,
                'total_pages': total_pages,
                'current_page': current_page,
                'page_size': self.get_page_size(self.request),
                'next': self.get_next_link(),
                'previous': self.get_previous_link(),
                'has_next': self.page.has_next(),
                'has_previous': self.page.has_previous(),
            }),
            ('data', data),
            ('timestamp', self.get_timestamp()),
        ]))
    
    def get_timestamp(self):
        """Return current timestamp for response tracking"""
        from django.utils import timezone
        return timezone.now().isoformat()

class SearchPagination(PageNumberPagination):
    """
    Pagination optimized for search results
    """
    page_size = 25
    page_size_query_param = 'limit'
    max_page_size = 100
    
    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('status', 'success'),
            ('search_results', {
                'total_found': self.page.paginator.count,
                'page': self.page.number,
                'pages': self.page.paginator.num_pages,
                'per_page': self.get_page_size(self.request),
            }),
            ('data', data),
        ]))

class PortfolioPagination(PageNumberPagination):
    """
    Pagination for portfolio and user-specific data
    """
    page_size = 20
    page_size_query_param = 'limit'
    max_page_size = 100

class NewsPagination(PageNumberPagination):
    """
    Pagination for news articles
    """
    page_size = 15
    page_size_query_param = 'limit'
    max_page_size = 50

class CachedPaginationMixin:
    """
    Mixin to add caching capabilities to pagination
    """
    cache_timeout = 300  # 5 minutes default
    
    def get_cache_key(self, request):
        """Generate cache key for paginated results"""
        query_params = request.GET.copy()
        # Remove cache-busting parameters
        query_params.pop('_', None)
        query_params.pop('timestamp', None)
        
        # Sort parameters for consistent cache keys
        sorted_params = sorted(query_params.items())
        cache_key = f"pagination_{request.path}_{hash(str(sorted_params))}"
        return cache_key
    
    def get_cached_response(self, request):
        """Get cached response if available"""
        if not hasattr(self, 'cache_timeout'):
            return None
            
        cache_key = self.get_cache_key(request)
        cached_data = cache.get(cache_key)
        
        if cached_data:
            logger.info(f"Cache hit for pagination: {cache_key}")
            return cached_data
        
        return None
    
    def cache_response(self, request, response_data):
        """Cache the response data"""
        if not hasattr(self, 'cache_timeout'):
            return
            
        cache_key = self.get_cache_key(request)
        cache.set(cache_key, response_data, self.cache_timeout)
        logger.info(f"Cached pagination response: {cache_key}")

class OptimizedStockPagination(StockPagination, CachedPaginationMixin):
    """
    Stock pagination with caching for better performance
    """
    cache_timeout = 180  # 3 minutes for stock data

class OptimizedSearchPagination(SearchPagination, CachedPaginationMixin):
    """
    Search pagination with caching
    """
    cache_timeout = 600  # 10 minutes for search results