import hashlib
import json
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from .models import WebhookEvent


class WebhookIdempotencyMiddleware(MiddlewareMixin):
    """
    Protects webhook endpoints by rejecting duplicate event_ids.
    Expects headers:
      - X-Webhook-Source: stripe|paypal|custom
      - X-Webhook-Event-Id: unique event id
      - X-Webhook-Signature: optional signature
    Apply only to specific webhook paths via settings or simple prefix match.
    """

    WEBHOOK_PATH_PREFIXES = (
        '/paypal/webhook/',
        '/api/referrals/webhook',
    )

    def process_request(self, request):
        path = request.path or ''
        if not any(path.startswith(p) for p in self.WEBHOOK_PATH_PREFIXES):
            return None

        source = (request.META.get('HTTP_X_WEBHOOK_SOURCE') or '').lower() or (
            'paypal' if path.startswith('/paypal/webhook/') else 'custom'
        )
        event_id = request.META.get('HTTP_X_WEBHOOK_EVENT_ID') or ''
        signature = request.META.get('HTTP_X_WEBHOOK_SIGNATURE') or ''
        if not event_id:
            # Some providers use id field in JSON
            try:
                data = json.loads(request.body or '{}')
                event_id = str(data.get('id') or data.get('event_id') or '')
            except Exception:
                event_id = ''

        if not event_id:
            return JsonResponse({'success': False, 'error': 'Missing event id'}, status=400)

        # Compute payload hash for reference
        try:
            payload_hash = hashlib.sha256(request.body or b'').hexdigest()
        except Exception:
            payload_hash = ''

        # Idempotency check
        exists = WebhookEvent.objects.filter(event_id=event_id).exists()
        if exists:
            return JsonResponse({'success': True, 'idempotent': True})

        WebhookEvent.objects.create(
            source=source or 'custom',
            event_id=event_id,
            signature=signature,
            payload_hash=payload_hash,
            status='received'
        )
        return None
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