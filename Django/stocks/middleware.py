"""
Middleware for handling both HTML and API responses
Enables WordPress compatibility while maintaining HTML interface
"""

import json
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin


class APICompatibilityMiddleware(MiddlewareMixin):
    """
    Middleware to handle both HTML and API responses based on request headers
    """
    
    def process_request(self, request):
        """
        Determine if request should be treated as API call
        """
        # Check for API indicators
        is_api_request = (
            # WordPress/AJAX requests
            request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest' or
            # Accept header indicates JSON
            'application/json' in request.META.get('HTTP_ACCEPT', '') or
            # URL starts with /api/
            request.path.startswith('/api/') or
            # Explicit API parameter
            request.GET.get('format') == 'json' or
            request.POST.get('format') == 'json' or
            # Revenue endpoints (always API for WordPress)
            request.path.startswith('/revenue/')
        )
        
        # Add flag to request for views to check
        request.is_api_request = is_api_request
        
        return None


class CORSMiddleware(MiddlewareMixin):
    """
    Middleware to handle CORS for WordPress integration
    """
    
    def process_response(self, request, response):
        """
        Add CORS headers for API requests
        """
        if hasattr(request, 'is_api_request') and request.is_api_request:
            response["Access-Control-Allow-Origin"] = "*"
            response["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
            response["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-Requested-With"
            response["Access-Control-Max-Age"] = "86400"
        
        return response
    
    def process_request(self, request):
        """
        Handle OPTIONS requests for CORS preflight
        """
        if request.method == "OPTIONS":
            response = JsonResponse({})
            response["Access-Control-Allow-Origin"] = "*"
            response["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
            response["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-Requested-With"
            response["Access-Control-Max-Age"] = "86400"
            return response
        
        return None