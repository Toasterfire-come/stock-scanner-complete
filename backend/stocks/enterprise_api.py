from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.core.cache import cache
from django.utils import timezone

from .models import EnterpriseInquiry, UserProfile


@api_view(['POST'])
@permission_classes([AllowAny])
def enterprise_contact_api(request):
    body = getattr(request, 'data', None) or {}
    try:
        inquiry = EnterpriseInquiry.objects.create(
            company_name=(body.get('company_name') or '').strip(),
            contact_email=(body.get('contact_email') or '').strip(),
            contact_name=(body.get('contact_name') or '').strip(),
            phone=(body.get('phone') or '').strip(),
            message=(body.get('message') or '').strip(),
            solution_type=(body.get('solution_type') or 'general').strip()
        )
        return Response({'success': True, 'id': inquiry.id})
    except Exception as e:
        return Response({'success': False, 'error': 'Invalid payload'}, status=400)


@api_view(['GET'])
@permission_classes([AllowAny])
def enterprise_solutions_api(request):
    return Response({
        'success': True,
        'solutions': [
            {'id': 'white_label', 'name': 'White-label Platform', 'description': 'Custom branded UI & APIs'},
            {'id': 'data_feed', 'name': 'Market Data Feed', 'description': 'Low-latency streaming data'},
            {'id': 'custom_analytics', 'name': 'Custom Analytics', 'description': 'Bespoke analytics & reporting'}
        ]
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def enterprise_quote_request_api(request):
    body = getattr(request, 'data', None) or {}
    inquiry = EnterpriseInquiry.objects.create(
        company_name=(body.get('company_name') or '').strip(),
        contact_email=(body.get('contact_email') or '').strip(),
        contact_name=(body.get('contact_name') or '').strip(),
        phone=(body.get('phone') or '').strip(),
        message=(body.get('requirements') or body.get('message') or '').strip(),
        solution_type='quote'
    )
    return Response({'success': True, 'id': inquiry.id})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def white_label_config_get_api(request):
    key = f"white_label:{request.user.id}"
    cfg = cache.get(key) or {
        'enabled': False,
        'brand_name': 'Trade Scan Pro',
        'primary_color': '#0ea5e9'
    }
    return Response({'success': True, 'config': cfg})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def white_label_config_create_api(request):
    body = getattr(request, 'data', None) or {}
    # Allow only gold/enterprise to save
    try:
        profile = UserProfile.objects.get(user=request.user)
        allowed = profile.plan_type in ['gold', 'enterprise']
    except UserProfile.DoesNotExist:
        allowed = False
    if not allowed:
        return Response({'success': False, 'error': 'Upgrade required'}, status=403)
    key = f"white_label:{request.user.id}"
    cfg = {
        'enabled': bool(body.get('enabled', True)),
        'brand_name': (body.get('brand_name') or 'Trade Scan Pro').strip(),
        'primary_color': (body.get('primary_color') or '#0ea5e9').strip()
    }
    cache.set(key, cfg, timeout=60 * 60 * 24 * 30)
    return Response({'success': True, 'config': cfg})

