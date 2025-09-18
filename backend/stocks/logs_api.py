"""
Logging & Monitoring API Views
Accepts client-side logs, performance metrics, and security events
"""

from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
try:
    from .throttling import SafeUserRateThrottle as UserRateThrottle, SafeAnonRateThrottle as AnonRateThrottle
except Exception:
    from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
import json
import logging

logger = logging.getLogger(__name__)


def _safe_json(body_bytes):
    try:
        return json.loads(body_bytes or b'{}')
    except Exception:
        return {}


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([UserRateThrottle, AnonRateThrottle])
def client_logs_api(request):
    """
    POST /api/logs/client/
    Accept client-side error logs
    """
    data = _safe_json(request.body)
    level = (data.get('level') or 'error').lower()
    message = data.get('message') or 'client log'
    context = data.get('context') or {}
    meta = {
        'ip': request.META.get('REMOTE_ADDR'),
        'ua': request.META.get('HTTP_USER_AGENT'),
        'at': timezone.now().isoformat(),
    }
    try:
        log_line = {
            'type': 'client',
            'level': level,
            'message': message,
            'context': context,
            'meta': meta,
        }
        # Log to server logs; in production this could go to an external sink
        getattr(logger, level if hasattr(logger, level) else 'warning')(f"CLIENT_LOG {json.dumps(log_line)[:2000]}")
        return JsonResponse({'success': True})
    except Exception as e:
        logger.error(f"client_logs_api failed: {e}")
        return JsonResponse({'success': False, 'error': 'LOG_WRITE_FAILED'}, status=500)


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([UserRateThrottle, AnonRateThrottle])
def metrics_logs_api(request):
    """
    POST /api/logs/metrics/
    Accept performance metrics from clients
    """
    data = _safe_json(request.body)
    try:
        logger.info(f"METRICS_LOG {json.dumps(data)[:2000]}")
        return JsonResponse({'success': True})
    except Exception as e:
        logger.error(f"metrics_logs_api failed: {e}")
        return JsonResponse({'success': False, 'error': 'LOG_WRITE_FAILED'}, status=500)


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([UserRateThrottle, AnonRateThrottle])
def security_logs_api(request):
    """
    POST /api/logs/security/
    Accept client-side security warnings/violations
    """
    data = _safe_json(request.body)
    try:
        logger.warning(f"SECURITY_LOG {json.dumps(data)[:2000]}")
        return JsonResponse({'success': True})
    except Exception as e:
        logger.error(f"security_logs_api failed: {e}")
        return JsonResponse({'success': False, 'error': 'LOG_WRITE_FAILED'}, status=500)

