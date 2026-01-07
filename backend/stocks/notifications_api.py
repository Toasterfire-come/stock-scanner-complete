"""
Notification History and Management API Views
Provides notification history and mark as read functionality
"""

from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.core.paginator import Paginator
from django.db.models import Q
import json
import logging
from datetime import datetime, timedelta

from .models import NotificationHistory, NotificationSettings
from .security_utils import secure_api_endpoint
from .authentication import CsrfExemptSessionAuthentication, BearerSessionAuthentication

logger = logging.getLogger(__name__)

@csrf_exempt
@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([BearerSessionAuthentication, CsrfExemptSessionAuthentication])
def notification_history_api(request):
    """
    Get user notification history
    GET /api/notifications/history
    """
    try:
        user = request.user
        page = int(request.GET.get('page', 1))
        limit = int(request.GET.get('limit', 20))
        notification_type = request.GET.get('type', None)
        is_read = request.GET.get('is_read', None)
        
        # Build query
        notifications = NotificationHistory.objects.filter(user=user)
        
        if notification_type:
            notifications = notifications.filter(notification_type=notification_type)
        
        if is_read is not None:
            is_read_bool = is_read.lower() in ['true', '1', 'yes']
            notifications = notifications.filter(is_read=is_read_bool)
        
        notifications = notifications.order_by('-created_at')
        
        # Paginate results
        paginator = Paginator(notifications, limit)
        page_obj = paginator.get_page(page)
        
        notification_data = []
        for notification in page_obj:
            notification_data.append({
                'id': notification.id,
                'title': getattr(notification, 'title', 'Notification'),
                'message': getattr(notification, 'message', ''),
                'type': getattr(notification, 'notification_type', 'general'),
                'is_read': getattr(notification, 'is_read', False),
                'created_at': notification.created_at.isoformat(),
                'read_at': notification.read_at.isoformat() if hasattr(notification, 'read_at') and notification.read_at else None,
                'metadata': json.loads(getattr(notification, 'metadata', '{}')) if hasattr(notification, 'metadata') else {}
            })
        
        return JsonResponse({
            'success': True,
            'data': notification_data,
            'pagination': {
                'current_page': page,
                'total_pages': paginator.num_pages,
                'total_records': paginator.count,
                'has_next': page_obj.has_next(),
                'has_previous': page_obj.has_previous()
            },
            'summary': {
                'total_unread': NotificationHistory.objects.filter(user=user, is_read=False).count() if hasattr(NotificationHistory, 'objects') else 0
            }
        })
        
    except Exception as e:
        logger.error(f"Notification history error: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Failed to retrieve notification history',
            'error_code': 'NOTIFICATION_HISTORY_ERROR'
        }, status=500)

@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([BearerSessionAuthentication, CsrfExemptSessionAuthentication])
def mark_notifications_read_api(request):
    """
    Mark notifications as read
    POST /api/notifications/mark-read
    """
    try:
        data = json.loads(request.body) if request.body else {}
        user = request.user
        
        notification_ids = data.get('notification_ids', [])
        mark_all = data.get('mark_all', False)
        
        if mark_all:
            # Mark all unread notifications as read
            updated_count = NotificationHistory.objects.filter(
                user=user, 
                is_read=False
            ).update(
                is_read=True, 
                read_at=timezone.now()
            )
        elif notification_ids:
            # Mark specific notifications as read
            updated_count = NotificationHistory.objects.filter(
                user=user,
                id__in=notification_ids,
                is_read=False
            ).update(
                is_read=True,
                read_at=timezone.now()
            )
        else:
            return JsonResponse({
                'success': False,
                'error': 'No notification IDs provided and mark_all not specified',
                'error_code': 'MISSING_NOTIFICATION_IDS'
            }, status=400)
        
        return JsonResponse({
            'success': True,
            'message': f'Marked {updated_count} notifications as read',
            'data': {
                'updated_count': updated_count,
                'remaining_unread': NotificationHistory.objects.filter(user=user, is_read=False).count() if hasattr(NotificationHistory, 'objects') else 0
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON format',
            'error_code': 'INVALID_JSON'
        }, status=400)
    except Exception as e:
        logger.error(f"Mark notifications read error: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Failed to mark notifications as read',
            'error_code': 'MARK_READ_ERROR'
        }, status=500)

@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_notification_api(request):
    """
    Create a new notification (internal use)
    POST /api/notifications/create
    """
    try:
        data = json.loads(request.body) if request.body else {}
        user = request.user
        
        title = data.get('title', '')
        message = data.get('message', '')
        notification_type = data.get('type', 'general')
        metadata = data.get('metadata', {})
        
        if not title or not message:
            return JsonResponse({
                'success': False,
                'error': 'Title and message are required',
                'error_code': 'MISSING_REQUIRED_FIELDS'
            }, status=400)
        
        # Create notification
        notification = NotificationHistory.objects.create(
            user=user,
            title=title,
            message=message,
            notification_type=notification_type,
            metadata=json.dumps(metadata) if metadata else '{}',
            is_read=False,
            created_at=timezone.now()
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Notification created successfully',
            'data': {
                'id': notification.id,
                'title': notification.title,
                'message': notification.message,
                'type': notification.notification_type,
                'created_at': notification.created_at.isoformat()
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON format',
            'error_code': 'INVALID_JSON'
        }, status=400)
    except Exception as e:
        logger.error(f"Create notification error: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Failed to create notification',
            'error_code': 'CREATE_NOTIFICATION_ERROR'
        }, status=500)