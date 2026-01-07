"""
Minimal enterprise endpoints for contact, quote request, and solutions listing.
Includes basic validation and simple rate limiting using cache keys.
"""

from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.core.cache import cache
from django.utils import timezone
from django.conf import settings


def _rate_limit_ok(key: str, max_count: int = 5, window_seconds: int = 300) -> bool:
    try:
        data = cache.get(key)
    except Exception:
        data = None
    if not data:
        try:
            cache.set(key, { 'count': 1, 'first': timezone.now().timestamp() }, window_seconds)
        except Exception:
            pass
        return True
    count = int(data.get('count', 0))
    if count >= max_count:
        return False
    data['count'] = count + 1
    try:
        cache.set(key, data, window_seconds)
    except Exception:
        pass
    return True


def _sanitize_text(s: str, max_len: int = 2000) -> str:
    if not isinstance(s, str):
        return ''
    s = s.strip()
    if len(s) > max_len:
        s = s[:max_len]
    return s


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def enterprise_contact_api(request):
    """
    Handle enterprise contact submissions.
    Body: { name, email, company, message }
    """
    try:
        data = getattr(request, 'data', {}) or {}
        name = _sanitize_text(data.get('name', ''), 200)
        email = _sanitize_text(data.get('email', ''), 254)
        company = _sanitize_text(data.get('company', ''), 200)
        message = _sanitize_text(data.get('message', ''), 2000)

        if not name or not email or not message:
            return Response({ 'success': False, 'message': 'name, email and message are required' }, status=status.HTTP_400_BAD_REQUEST)
        try:
            validate_email(email)
        except ValidationError:
            return Response({ 'success': False, 'message': 'invalid email' }, status=status.HTTP_400_BAD_REQUEST)

        # Simple abuse control by IP
        ip = request.META.get('HTTP_X_FORWARDED_FOR', '').split(',')[0] or request.META.get('REMOTE_ADDR', '127.0.0.1')
        if not _rate_limit_ok(f"enterprise_contact_{ip}"):
            return Response({ 'success': False, 'message': 'Too many requests, please try again later' }, status=status.HTTP_429_TOO_MANY_REQUESTS)

        # Wire to email service or store for later processing; for now, just acknowledge
        return Response({ 'success': True, 'message': 'Thank you, our team will contact you shortly.' })
    except Exception:
        return Response({ 'success': False, 'message': 'internal error' }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def enterprise_quote_request_api(request):
    """
    Handle enterprise quote requests.
    Body: { name, email, company, requirements, budget }
    """
    try:
        data = getattr(request, 'data', {}) or {}
        name = _sanitize_text(data.get('name', ''), 200)
        email = _sanitize_text(data.get('email', ''), 254)
        company = _sanitize_text(data.get('company', ''), 200)
        requirements = _sanitize_text(data.get('requirements', ''), 4000)
        budget = _sanitize_text(data.get('budget', ''), 100)

        if not name or not email or not company or not requirements:
            return Response({ 'success': False, 'message': 'name, email, company, requirements are required' }, status=status.HTTP_400_BAD_REQUEST)
        try:
            validate_email(email)
        except ValidationError:
            return Response({ 'success': False, 'message': 'invalid email' }, status=status.HTTP_400_BAD_REQUEST)

        ip = request.META.get('HTTP_X_FORWARDED_FOR', '').split(',')[0] or request.META.get('REMOTE_ADDR', '127.0.0.1')
        if not _rate_limit_ok(f"enterprise_quote_{ip}"):
            return Response({ 'success': False, 'message': 'Too many requests, please try again later' }, status=status.HTTP_429_TOO_MANY_REQUESTS)

        return Response({ 'success': True, 'message': 'Your request has been received. We will follow up shortly.' })
    except Exception:
        return Response({ 'success': False, 'message': 'internal error' }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def enterprise_solutions_api(request):
    """
    Return a minimal solutions list for UI rendering.
    """
    try:
        solutions = [
            { 'id': 'data-feed', 'title': 'Data Feed API', 'status': 'available' },
            { 'id': 'white-label', 'title': 'White Label Portal', 'status': 'beta' },
            { 'id': 'analytics', 'title': 'Custom Analytics', 'status': 'coming_soon' },
        ]
        return Response({ 'success': True, 'data': { 'solutions': solutions, 'timestamp': timezone.now().isoformat() } })
    except Exception:
        return Response({ 'success': False, 'data': { 'solutions': [] } }, status=status.HTTP_200_OK)
