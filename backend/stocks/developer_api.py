from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.utils import timezone
from django.core.cache import cache
import secrets

from .models import APIKey, UserProfile
from .billing_api import usage_stats_api


def _user(request):
    u = getattr(request, 'user', None)
    if u and getattr(u, 'is_authenticated', False):
        return u
    return None


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_keys_list_api(request):
    user = _user(request)
    keys = APIKey.objects.filter(user=user).order_by('-created_at')
    return Response({
        'success': True,
        'data': [{
            'id': k.id,
            'name': k.name,
            'key': k.key,
            'is_active': k.is_active,
            'created_at': k.created_at.isoformat(),
            'last_used': k.last_used.isoformat() if k.last_used else None
        } for k in keys]
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_keys_create_api(request):
    user = _user(request)
    body = getattr(request, 'data', None) or {}
    name = (body.get('name') or 'Default Key').strip()
    key = secrets.token_hex(32)
    k = APIKey.objects.create(user=user, name=name, key=key)
    return Response({'success': True, 'id': k.id, 'key': k.key, 'name': k.name})


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def api_keys_delete_api(request, key_id: int):
    user = _user(request)
    try:
        k = APIKey.objects.get(id=key_id, user=user)
    except APIKey.DoesNotExist:
        return Response({'success': False, 'error': 'Not found'}, status=404)
    k.is_active = False
    k.save(update_fields=['is_active'])
    return Response({'success': True})


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def api_keys_root_api(request):
    if request.method == 'GET':
        return api_keys_list_api(request)
    if request.method == 'POST':
        return api_keys_create_api(request)
    return Response({'success': False, 'error': 'Method not allowed'}, status=405)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def developer_usage_stats_api(request):
    # Delegate to existing usage stats
    return usage_stats_api(request)


@api_view(['GET'])
@permission_classes([AllowAny])
def developer_documentation_api(request):
    doc = {
        'success': True,
        'title': 'Trade Scan Pro Developer API',
        'endpoints': [
            '/api/developer/api-keys/ [GET, POST]',
            '/api/developer/api-keys/{id}/ [DELETE]',
            '/api/developer/usage-stats/ [GET]',
            '/api/developer/documentation/ [GET]'
        ]
    }
    return Response(doc)

