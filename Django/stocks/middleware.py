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
    Middleware to handle CORS for WordPress integration.
    Note: We now defer CORS headers to django-cors-headers to avoid wildcard
    origins when credentials are used. This middleware only handles OPTIONS
    fallbacks without setting wildcard origins.
    """

    def process_response(self, request, response):
        # Do not set Access-Control-Allow-Origin here; let django-cors-headers manage it
        # Keep max-age hint for non-complex responses if desired (optional)
        return response

    def process_request(self, request):
        # Handle bare OPTIONS with minimal headers; allow django-cors-headers to add the rest
        if request.method == "OPTIONS":
            return JsonResponse({})
        return None