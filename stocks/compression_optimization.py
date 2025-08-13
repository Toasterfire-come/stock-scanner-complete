"""
Request/Response Compression and Bandwidth Optimization
Improves network efficiency without adding new features
"""

import gzip
import zlib
import json
import logging
import time
from typing import Dict, Any, Optional, Union
from django.http import HttpResponse, JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.gzip import gzip_page
from django.middleware.gzip import GZipMiddleware
from django.core.serializers.json import DjangoJSONEncoder
from django.conf import settings
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
import io

logger = logging.getLogger(__name__)

class OptimizedJSONEncoder(DjangoJSONEncoder):
    """
    Optimized JSON encoder that reduces response size
    """
    
    def encode(self, o):
        """Encode with optimization"""
        # Remove null values to reduce size
        if isinstance(o, dict):
            o = self._remove_nulls(o)
        elif isinstance(o, list):
            o = [self._remove_nulls(item) if isinstance(item, dict) else item for item in o]
        
        return super().encode(o)
    
    def _remove_nulls(self, data):
        """Remove null/empty values from dictionary"""
        if not isinstance(data, dict):
            return data
        
        cleaned = {}
        for key, value in data.items():
            if value is not None and value != "" and value != []:
                if isinstance(value, dict):
                    cleaned_value = self._remove_nulls(value)
                    if cleaned_value:  # Only add if not empty after cleaning
                        cleaned[key] = cleaned_value
                elif isinstance(value, list):
                    cleaned_list = []
                    for item in value:
                        if isinstance(item, dict):
                            cleaned_item = self._remove_nulls(item)
                            if cleaned_item:
                                cleaned_list.append(cleaned_item)
                        elif item is not None and item != "":
                            cleaned_list.append(item)
                    if cleaned_list:
                        cleaned[key] = cleaned_list
                else:
                    cleaned[key] = value
        
        return cleaned

class CompressedJSONRenderer(JSONRenderer):
    """
    JSON renderer with built-in compression
    """
    
    def render(self, data, accepted_media_type=None, renderer_context=None):
        """Render JSON with optimization"""
        # Use optimized encoder
        ret = json.dumps(
            data,
            cls=OptimizedJSONEncoder,
            ensure_ascii=False,
            separators=(',', ':')  # Compact separators
        )
        
        # Return as bytes for potential compression
        return ret.encode('utf-8')

class SmartCompressionMiddleware:
    """
    Intelligent compression middleware that adapts to content type and size
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.min_compression_size = 500  # Only compress responses larger than 500 bytes
        self.compression_ratio_threshold = 0.1  # Only keep compression if it saves at least 10%
        
        # Track compression statistics
        self.compression_stats = {
            'total_requests': 0,
            'compressed_requests': 0,
            'bytes_saved': 0,
            'compression_time': 0
        }
    
    def __call__(self, request):
        response = self.get_response(request)
        
        self.compression_stats['total_requests'] += 1
        
        # Check if compression should be applied
        if self._should_compress(request, response):
            response = self._compress_response(request, response)
        
        return response
    
    def _should_compress(self, request, response):
        """Determine if response should be compressed"""
        # Check if client accepts compression
        accept_encoding = request.META.get('HTTP_ACCEPT_ENCODING', '')
        
        if 'gzip' not in accept_encoding.lower():
            return False
        
        # Check response size
        if not hasattr(response, 'content') or len(response.content) < self.min_compression_size:
            return False
        
        # Check content type
        content_type = response.get('Content-Type', '')
        compressible_types = [
            'application/json',
            'text/html',
            'text/css',
            'text/javascript',
            'application/javascript',
            'text/xml',
            'application/xml'
        ]
        
        if not any(ct in content_type for ct in compressible_types):
            return False
        
        # Don't compress if already compressed
        if response.get('Content-Encoding'):
            return False
        
        return True
    
    def _compress_response(self, request, response):
        """Compress response content"""
        start_time = time.time()
        
        try:
            original_content = response.content
            original_size = len(original_content)
            
            # Try gzip compression
            compressed_content = gzip.compress(original_content, compresslevel=6)
            compressed_size = len(compressed_content)
            
            # Check if compression is worthwhile
            compression_ratio = (original_size - compressed_size) / original_size
            
            if compression_ratio >= self.compression_ratio_threshold:
                response.content = compressed_content
                response['Content-Encoding'] = 'gzip'
                response['Content-Length'] = str(compressed_size)
                
                # Add compression info header (for debugging)
                if getattr(settings, 'DEBUG', False):
                    response['X-Compression-Ratio'] = f"{compression_ratio:.2%}"
                    response['X-Original-Size'] = str(original_size)
                    response['X-Compressed-Size'] = str(compressed_size)
                
                # Update statistics
                self.compression_stats['compressed_requests'] += 1
                self.compression_stats['bytes_saved'] += (original_size - compressed_size)
                
                logger.debug(f"Compressed response: {original_size} -> {compressed_size} bytes ({compression_ratio:.2%} savings)")
            
        except Exception as e:
            logger.error(f"Compression failed: {e}")
        
        finally:
            compression_time = time.time() - start_time
            self.compression_stats['compression_time'] += compression_time
        
        return response
    
    def get_compression_stats(self):
        """Get compression statistics"""
        total_requests = self.compression_stats['total_requests']
        
        if total_requests == 0:
            return self.compression_stats
        
        return {
            **self.compression_stats,
            'compression_rate': (self.compression_stats['compressed_requests'] / total_requests) * 100,
            'avg_compression_time': self.compression_stats['compression_time'] / max(1, self.compression_stats['compressed_requests']),
            'avg_bytes_saved': self.compression_stats['bytes_saved'] / max(1, self.compression_stats['compressed_requests'])
        }

class ResponseOptimizer:
    """
    Optimize response data for minimal bandwidth usage
    """
    
    @staticmethod
    def optimize_stock_data(stock_data):
        """Optimize stock data for transmission"""
        if isinstance(stock_data, list):
            return [ResponseOptimizer._optimize_single_stock(stock) for stock in stock_data]
        else:
            return ResponseOptimizer._optimize_single_stock(stock_data)
    
    @staticmethod
    def _optimize_single_stock(stock):
        """Optimize single stock data"""
        if not isinstance(stock, dict):
            return stock
        
        optimized = {}
        
        # Use shorter field names to reduce JSON size
        field_mappings = {
            'ticker': 't',
            'company_name': 'n',
            'current_price': 'p',
            'change_percent': 'c',
            'volume': 'v',
            'market_cap': 'm',
            'pe_ratio': 'pe',
            'dividend_yield': 'dy',
            'last_updated': 'u'
        }
        
        for original_key, short_key in field_mappings.items():
            if original_key in stock and stock[original_key] is not None:
                value = stock[original_key]
                
                # Round decimal values to reduce precision
                if isinstance(value, float):
                    if original_key in ['current_price', 'change_percent']:
                        value = round(value, 2)
                    elif original_key in ['pe_ratio', 'dividend_yield']:
                        value = round(value, 3)
                
                optimized[short_key] = value
        
        return optimized
    
    @staticmethod
    def optimize_pagination_data(pagination_data):
        """Optimize pagination metadata"""
        if not isinstance(pagination_data, dict):
            return pagination_data
        
        # Use shorter keys for pagination
        optimized = {}
        pagination_mappings = {
            'count': 'c',
            'total_pages': 'tp',
            'current_page': 'cp',
            'page_size': 'ps',
            'has_next': 'hn',
            'has_previous': 'hp'
        }
        
        for original_key, short_key in pagination_mappings.items():
            if original_key in pagination_data:
                optimized[short_key] = pagination_data[original_key]
        
        return optimized
    
    @staticmethod
    def create_compressed_response(data, status_code=200, optimize_fields=True):
        """Create a compressed, optimized response"""
        if optimize_fields:
            if 'data' in data and isinstance(data['data'], (list, dict)):
                data['data'] = ResponseOptimizer.optimize_stock_data(data['data'])
            
            if 'pagination' in data:
                data['pagination'] = ResponseOptimizer.optimize_pagination_data(data['pagination'])
        
        # Create response with optimized JSON encoder
        response = JsonResponse(
            data,
            encoder=OptimizedJSONEncoder,
            json_dumps_params={'separators': (',', ':')},
            status=status_code
        )
        
        return response

class BandwidthOptimizer:
    """
    Optimize bandwidth usage through various techniques
    """
    
    @staticmethod
    def add_caching_headers(response, cache_time=300):
        """Add appropriate caching headers to reduce bandwidth"""
        response['Cache-Control'] = f'public, max-age={cache_time}'
        response['Vary'] = 'Accept-Encoding'
        
        # Add ETag for conditional requests
        if hasattr(response, 'content'):
            import hashlib
            etag = hashlib.md5(response.content).hexdigest()
            response['ETag'] = f'"{etag}"'
        
        return response
    
    @staticmethod
    def handle_conditional_request(request, response):
        """Handle conditional requests to save bandwidth"""
        # Check If-None-Match header
        if_none_match = request.META.get('HTTP_IF_NONE_MATCH')
        current_etag = response.get('ETag')
        
        if if_none_match and current_etag and if_none_match == current_etag:
            # Return 304 Not Modified
            from django.http import HttpResponseNotModified
            return HttpResponseNotModified()
        
        # Check If-Modified-Since header
        if_modified_since = request.META.get('HTTP_IF_MODIFIED_SINCE')
        last_modified = response.get('Last-Modified')
        
        if if_modified_since and last_modified:
            from django.utils.http import parse_http_date_safe
            from django.utils.timezone import now
            
            try:
                if_modified_timestamp = parse_http_date_safe(if_modified_since)
                last_modified_timestamp = parse_http_date_safe(last_modified)
                
                if (if_modified_timestamp and last_modified_timestamp and 
                    if_modified_timestamp >= last_modified_timestamp):
                    return HttpResponseNotModified()
            except (ValueError, TypeError):
                pass
        
        return response
    
    @staticmethod
    def optimize_json_response(data):
        """Optimize JSON response structure"""
        if isinstance(data, dict):
            # Remove empty collections and null values
            optimized = {}
            for key, value in data.items():
                if value is not None and value != [] and value != {}:
                    if isinstance(value, dict):
                        optimized_value = BandwidthOptimizer.optimize_json_response(value)
                        if optimized_value:
                            optimized[key] = optimized_value
                    elif isinstance(value, list):
                        optimized_list = [
                            BandwidthOptimizer.optimize_json_response(item) 
                            if isinstance(item, dict) else item 
                            for item in value 
                            if item is not None
                        ]
                        if optimized_list:
                            optimized[key] = optimized_list
                    else:
                        optimized[key] = value
            return optimized
        
        return data

class ConditionalResponseMiddleware:
    """
    Middleware to handle conditional requests for bandwidth optimization
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        
        # Add caching headers for API endpoints
        if request.path.startswith('/api/'):
            response = BandwidthOptimizer.add_caching_headers(response, cache_time=180)
            
            # Handle conditional requests
            conditional_response = BandwidthOptimizer.handle_conditional_request(request, response)
            if conditional_response != response:
                return conditional_response
        
        return response

def compress_api_response(func):
    """
    Decorator to automatically compress API responses
    """
    def wrapper(*args, **kwargs):
        response = func(*args, **kwargs)
        
        if isinstance(response, (Response, JsonResponse)):
            # Optimize data structure
            if hasattr(response, 'data'):
                response.data = BandwidthOptimizer.optimize_json_response(response.data)
            
            # Add compression hint
            response['X-Compressible'] = 'true'
        
        return response
    
    return wrapper

def get_compression_recommendations(request=None):
    """
    Get recommendations for improving compression and bandwidth usage
    """
    recommendations = []
    
    # Check if gzip middleware is enabled
    middleware_classes = getattr(settings, 'MIDDLEWARE', [])
    if 'django.middleware.gzip.GZipMiddleware' not in middleware_classes:
        recommendations.append("Enable GZip middleware for automatic compression")
    
    # Check browser support
    if request:
        accept_encoding = request.META.get('HTTP_ACCEPT_ENCODING', '')
        if 'gzip' not in accept_encoding.lower():
            recommendations.append("Client does not support gzip compression")
        if 'br' in accept_encoding.lower():
            recommendations.append("Client supports Brotli compression (better than gzip)")
    
    # Check response size patterns
    # This would require analyzing actual response sizes in practice
    recommendations.append("Consider implementing field selection to reduce response size")
    recommendations.append("Use pagination for large datasets")
    recommendations.append("Implement conditional requests (ETags) to avoid unnecessary transfers")
    
    return recommendations

class ResponseSizeAnalyzer:
    """
    Analyze response sizes to identify optimization opportunities
    """
    
    def __init__(self):
        self.size_stats = {
            'total_responses': 0,
            'total_bytes': 0,
            'size_distribution': {
                'small': 0,    # < 1KB
                'medium': 0,   # 1KB - 10KB
                'large': 0,    # 10KB - 100KB
                'xlarge': 0    # > 100KB
            },
            'endpoint_stats': {}
        }
    
    def analyze_response(self, request, response):
        """Analyze response size and provide insights"""
        if not hasattr(response, 'content'):
            return
        
        size = len(response.content)
        endpoint = request.path
        
        # Update overall stats
        self.size_stats['total_responses'] += 1
        self.size_stats['total_bytes'] += size
        
        # Update size distribution
        if size < 1024:
            self.size_stats['size_distribution']['small'] += 1
        elif size < 10240:
            self.size_stats['size_distribution']['medium'] += 1
        elif size < 102400:
            self.size_stats['size_distribution']['large'] += 1
        else:
            self.size_stats['size_distribution']['xlarge'] += 1
        
        # Update endpoint stats
        if endpoint not in self.size_stats['endpoint_stats']:
            self.size_stats['endpoint_stats'][endpoint] = {
                'count': 0,
                'total_bytes': 0,
                'avg_bytes': 0,
                'max_bytes': 0
            }
        
        endpoint_stats = self.size_stats['endpoint_stats'][endpoint]
        endpoint_stats['count'] += 1
        endpoint_stats['total_bytes'] += size
        endpoint_stats['avg_bytes'] = endpoint_stats['total_bytes'] / endpoint_stats['count']
        endpoint_stats['max_bytes'] = max(endpoint_stats['max_bytes'], size)
    
    def get_insights(self):
        """Get insights and recommendations"""
        if self.size_stats['total_responses'] == 0:
            return {'message': 'No data available'}
        
        avg_response_size = self.size_stats['total_bytes'] / self.size_stats['total_responses']
        
        insights = {
            'average_response_size': avg_response_size,
            'total_bandwidth': self.size_stats['total_bytes'],
            'size_distribution': self.size_stats['size_distribution'],
            'recommendations': []
        }
        
        # Generate recommendations
        large_responses = self.size_stats['size_distribution']['large'] + self.size_stats['size_distribution']['xlarge']
        total_responses = self.size_stats['total_responses']
        
        if large_responses / total_responses > 0.1:  # More than 10% are large
            insights['recommendations'].append("Consider implementing pagination for large responses")
        
        if avg_response_size > 50000:  # Average > 50KB
            insights['recommendations'].append("Average response size is large - consider field selection")
        
        # Find endpoints with largest responses
        largest_endpoints = sorted(
            self.size_stats['endpoint_stats'].items(),
            key=lambda x: x[1]['avg_bytes'],
            reverse=True
        )[:3]
        
        for endpoint, stats in largest_endpoints:
            if stats['avg_bytes'] > 20000:  # > 20KB average
                insights['recommendations'].append(f"Optimize {endpoint} - average {stats['avg_bytes']:.0f} bytes")
        
        insights['largest_endpoints'] = {
            endpoint: stats for endpoint, stats in largest_endpoints
        }
        
        return insights

# Global analyzer instance
response_analyzer = ResponseSizeAnalyzer()

def initialize_compression_optimization():
    """
    Initialize compression and bandwidth optimization
    """
    logger.info("Compression and bandwidth optimization initialized")
    
    # Log configuration
    middleware_classes = getattr(settings, 'MIDDLEWARE', [])
    if 'django.middleware.gzip.GZipMiddleware' in middleware_classes:
        logger.info("GZip middleware detected")
    else:
        logger.warning("GZip middleware not detected - consider enabling for better compression")