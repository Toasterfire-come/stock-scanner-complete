"""
Advanced Compression and Minification Middleware
Automatic compression of responses and static assets for optimal performance
"""

import gzip
import re
import hashlib
from io import BytesIO
from typing import Dict, List, Optional, Tuple

from django.http import HttpResponse, StreamingHttpResponse
from django.utils.cache import get_conditional_response
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from django.core.cache import cache

class CompressionMiddleware(MiddlewareMixin):
    """
    Advanced compression middleware with intelligent compression strategies
    """
    
    # MIME types that should be compressed
    COMPRESSIBLE_TYPES = {
        'text/html',
        'text/css',
        'text/javascript',
        'application/javascript',
        'application/json',
        'text/xml',
        'application/xml',
        'text/plain',
        'image/svg+xml',
    }
    
    # Minimum size for compression (bytes)
    MIN_COMPRESSION_SIZE = 200
    
    def __init__(self, get_response):
        super().__init__(get_response)
        self.get_response = get_response
    
    def process_response(self, request, response):
        """
        Compress response if appropriate
        """
        # Skip compression for certain conditions
        if not self._should_compress(request, response):
            return response
        
        # Get accepted encodings
        accepted_encodings = self._get_accepted_encodings(request)
        
        if 'gzip' in accepted_encodings:
            return self._compress_response(response, 'gzip')
        elif 'deflate' in accepted_encodings:
            return self._compress_response(response, 'deflate')
        
        return response
    
    def _should_compress(self, request, response) -> bool:
        """
        Determine if response should be compressed
        """
        # Don't compress if already compressed
        if response.get('Content-Encoding'):
            return False
        
        # Don't compress small responses
        if len(response.content) < self.MIN_COMPRESSION_SIZE:
            return False
        
        # Only compress appropriate content types
        content_type = response.get('Content-Type', '').split(';')[0]
        if content_type not in self.COMPRESSIBLE_TYPES:
            return False
        
        # Don't compress if client doesn't support it
        if not request.META.get('HTTP_ACCEPT_ENCODING'):
            return False
        
        # Don't compress streaming responses
        if isinstance(response, StreamingHttpResponse):
            return False
        
        return True
    
    def _get_accepted_encodings(self, request) -> List[str]:
        """
        Parse accepted encodings from request headers
        """
        accept_encoding = request.META.get('HTTP_ACCEPT_ENCODING', '')
        encodings = []
        
        for encoding in accept_encoding.split(','):
            encoding = encoding.strip().lower()
            if encoding:
                encodings.append(encoding.split(';')[0])
        
        return encodings
    
    def _compress_response(self, response, encoding) -> HttpResponse:
        """
        Compress response content
        """
        if encoding == 'gzip':
            compressed_content = self._gzip_compress(response.content)
            response.content = compressed_content
            response['Content-Encoding'] = 'gzip'
            response['Content-Length'] = str(len(compressed_content))
        
        # Add Vary header for proper caching
        vary_header = response.get('Vary', '')
        if 'Accept-Encoding' not in vary_header:
            if vary_header:
                response['Vary'] = f"{vary_header}, Accept-Encoding"
            else:
                response['Vary'] = 'Accept-Encoding'
        
        return response
    
    def _gzip_compress(self, content: bytes) -> bytes:
        """
        Compress content using gzip
        """
        buffer = BytesIO()
        with gzip.GzipFile(fileobj=buffer, mode='wb', compresslevel=6) as gz_file:
            gz_file.write(content)
        return buffer.getvalue()

class CSSMinifier:
    """
    CSS minification utilities
    """
    
    @staticmethod
    def minify(css_content: str) -> str:
        """
        Minify CSS content
        """
        # Remove comments
        css_content = re.sub(r'/\*.*?\*/', '', css_content, flags=re.DOTALL)
        
        # Remove unnecessary whitespace
        css_content = re.sub(r'\s+', ' ', css_content)
        
        # Remove whitespace around specific characters
        css_content = re.sub(r'\s*([{}:;,>+~])\s*', r'\1', css_content)
        
        # Remove trailing semicolons before closing braces
        css_content = re.sub(r';\s*}', '}', css_content)
        
        # Remove empty rules
        css_content = re.sub(r'[^{}]+{\s*}', '', css_content)
        
        return css_content.strip()
    
    @staticmethod
    def minify_inline(html_content: str) -> str:
        """
        Minify inline CSS in HTML content
        """
        def minify_css_match(match):
            css_content = match.group(1)
            return f"<style>{CSSMinifier.minify(css_content)}</style>"
        
        return re.sub(
            r'<style[^>]*>(.*?)</style>',
            minify_css_match,
            html_content,
            flags=re.DOTALL | re.IGNORECASE
        )

class JSMinifier:
    """
    JavaScript minification utilities
    """
    
    @staticmethod
    def minify(js_content: str) -> str:
        """
        Basic JavaScript minification
        """
        # Remove single-line comments (but preserve URLs)
        js_content = re.sub(r'(?<!:)//.*$', '', js_content, flags=re.MULTILINE)
        
        # Remove multi-line comments
        js_content = re.sub(r'/\*.*?\*/', '', js_content, flags=re.DOTALL)
        
        # Remove unnecessary whitespace
        js_content = re.sub(r'\s+', ' ', js_content)
        
        # Remove whitespace around operators and punctuation
        js_content = re.sub(r'\s*([=+\-*/(){}\[\];,])\s*', r'\1', js_content)
        
        return js_content.strip()
    
    @staticmethod
    def minify_inline(html_content: str) -> str:
        """
        Minify inline JavaScript in HTML content
        """
        def minify_js_match(match):
            js_content = match.group(1)
            return f"<script>{JSMinifier.minify(js_content)}</script>"
        
        return re.sub(
            r'<script[^>]*>(.*?)</script>',
            minify_js_match,
            html_content,
            flags=re.DOTALL | re.IGNORECASE
        )

class HTMLOptimizer:
    """
    HTML optimization utilities
    """
    
    @staticmethod
    def minify(html_content: str, preserve_whitespace_tags: List[str] = None) -> str:
        """
        Minify HTML content while preserving important whitespace
        """
        if preserve_whitespace_tags is None:
            preserve_whitespace_tags = ['pre', 'textarea', 'script', 'style']
        
        # Store whitespace-sensitive content
        preserved_content = {}
        placeholder_pattern = "<!--PRESERVE_{}_-->"
        
        # Preserve content in whitespace-sensitive tags
        for tag in preserve_whitespace_tags:
            pattern = f'<{tag}[^>]*>.*?</{tag}>'
            matches = re.findall(pattern, html_content, flags=re.DOTALL | re.IGNORECASE)
            
            for i, match in enumerate(matches):
                placeholder = placeholder_pattern.format(f"{tag}_{i}")
                preserved_content[placeholder] = match
                html_content = html_content.replace(match, placeholder, 1)
        
        # Remove HTML comments (except preserved placeholders)
        html_content = re.sub(r'<!--(?!PRESERVE_).*?-->', '', html_content, flags=re.DOTALL)
        
        # Remove unnecessary whitespace between tags
        html_content = re.sub(r'>\s+<', '><', html_content)
        
        # Remove leading/trailing whitespace from lines
        html_content = '\n'.join(line.strip() for line in html_content.split('\n'))
        
        # Remove empty lines
        html_content = re.sub(r'\n\s*\n', '\n', html_content)
        
        # Restore preserved content
        for placeholder, content in preserved_content.items():
            html_content = html_content.replace(placeholder, content)
        
        return html_content.strip()

class ResponseOptimizationMiddleware(MiddlewareMixin):
    """
    Middleware for automatic response optimization and minification
    """
    
    def __init__(self, get_response):
        super().__init__(get_response)
        self.get_response = get_response
    
    def process_response(self, request, response):
        """
        Optimize response content based on content type
        """
        # Only optimize in production or when explicitly enabled
        if not getattr(settings, 'ENABLE_RESPONSE_OPTIMIZATION', not settings.DEBUG):
            return response
        
        content_type = response.get('Content-Type', '').split(';')[0]
        
        # Check if content should be optimized
        if content_type == 'text/html':
            response = self._optimize_html_response(response)
        elif content_type == 'text/css':
            response = self._optimize_css_response(response)
        elif content_type in ['text/javascript', 'application/javascript']:
            response = self._optimize_js_response(response)
        
        return response
    
    def _optimize_html_response(self, response):
        """
        Optimize HTML response
        """
        try:
            content = response.content.decode('utf-8')
            
            # Minify inline CSS and JavaScript
            content = CSSMinifier.minify_inline(content)
            content = JSMinifier.minify_inline(content)
            
            # Minify HTML
            content = HTMLOptimizer.minify(content)
            
            # Update response
            response.content = content.encode('utf-8')
            response['Content-Length'] = str(len(response.content))
            
        except (UnicodeDecodeError, Exception):
            # If optimization fails, return original response
            pass
        
        return response
    
    def _optimize_css_response(self, response):
        """
        Optimize CSS response
        """
        try:
            content = response.content.decode('utf-8')
            content = CSSMinifier.minify(content)
            
            response.content = content.encode('utf-8')
            response['Content-Length'] = str(len(response.content))
            
        except (UnicodeDecodeError, Exception):
            pass
        
        return response
    
    def _optimize_js_response(self, response):
        """
        Optimize JavaScript response
        """
        try:
            content = response.content.decode('utf-8')
            content = JSMinifier.minify(content)
            
            response.content = content.encode('utf-8')
            response['Content-Length'] = str(len(response.content))
            
        except (UnicodeDecodeError, Exception):
            pass
        
        return response

class StaticFilesOptimizer:
    """
    Utilities for optimizing static files
    """
    
    @staticmethod
    def get_optimized_content(file_path: str, content_type: str) -> Tuple[str, str]:
        """
        Get optimized content for static files with caching
        """
        # Generate cache key
        with open(file_path, 'rb') as f:
            file_content = f.read()
            file_hash = hashlib.md5(file_content).hexdigest()
        
        cache_key = f"optimized_{content_type}_{file_hash}"
        cached_content = cache.get(cache_key)
        
        if cached_content:
            return cached_content, file_hash
        
        # Optimize based on content type
        content_str = file_content.decode('utf-8')
        
        if content_type == 'text/css':
            optimized_content = CSSMinifier.minify(content_str)
        elif content_type in ['text/javascript', 'application/javascript']:
            optimized_content = JSMinifier.minify(content_str)
        else:
            optimized_content = content_str
        
        # Cache optimized content for 1 hour
        cache.set(cache_key, optimized_content, 3600)
        
        return optimized_content, file_hash

# Settings for enabling optimizations
OPTIMIZATION_SETTINGS = {
    'ENABLE_COMPRESSION': True,
    'ENABLE_RESPONSE_OPTIMIZATION': not settings.DEBUG,
    'COMPRESSION_MIN_SIZE': 200,
    'COMPRESSION_LEVEL': 6,
}

# Example usage in settings.py:
"""
MIDDLEWARE = [
    # ... other middleware
    'utils.compression_middleware.CompressionMiddleware',
    'utils.compression_middleware.ResponseOptimizationMiddleware',
    # ... more middleware
]

# Enable optimizations
ENABLE_RESPONSE_OPTIMIZATION = True
ENABLE_COMPRESSION = True
"""