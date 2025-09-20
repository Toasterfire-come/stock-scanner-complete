from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Count

from .models import UserActivity, APICallLog


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_activity_feed_api(request):
    items = UserActivity.objects.filter(user=request.user).order_by('-timestamp')[:100]
    data = [{
        'action_type': a.action_type,
        'details': a.details,
        'timestamp': a.timestamp.isoformat()
    } for a in items]
    return Response({'success': True, 'data': data})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def analytics_user_insights_api(request):
    # Simple insights powered by APICallLog counts
    recent = APICallLog.objects.filter(user=request.user).values('endpoint_type').annotate(count=Count('id')).order_by('-count')
    top_endpoints = list(recent[:5])
    return Response({
        'success': True,
        'insights': {
            'top_endpoint_types': top_endpoints,
            'activity_count': UserActivity.objects.filter(user=request.user).count()
        }
    })

