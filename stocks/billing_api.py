"""
Billing and Notification Management API Views
Provides comprehensive billing history, payment management, and notification endpoints
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.core.paginator import Paginator
from django.db.models import Q, Sum
import json
import logging
from datetime import datetime, timedelta
from decimal import Decimal

from .models import BillingHistory, NotificationSettings, UserProfile, UsageStats
from .security_utils import secure_api_endpoint

logger = logging.getLogger(__name__)

# Billing endpoints
@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_payment_method_api(request):
    """
    Update user payment method
    POST /api/user/update-payment
    """
    try:
        data = json.loads(request.body) if request.body else {}
        
        user = request.user
        profile, created = UserProfile.objects.get_or_create(user=user)
        
        # Update payment method information
        payment_method = data.get('payment_method', {})
        
        if 'card_last_four' in payment_method:
            profile.card_last_four = payment_method['card_last_four']
        if 'card_type' in payment_method:
            profile.card_type = payment_method['card_type']
        if 'billing_address' in payment_method:
            profile.billing_address = json.dumps(payment_method['billing_address'])
        
        profile.payment_updated_at = timezone.now()
        profile.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Payment method updated successfully',
            'data': {
                'card_type': getattr(profile, 'card_type', ''),
                'card_last_four': getattr(profile, 'card_last_four', ''),
                'updated_at': profile.payment_updated_at.isoformat() if hasattr(profile, 'payment_updated_at') else None
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON format',
            'error_code': 'INVALID_JSON'
        }, status=400)
    except Exception as e:
        logger.error(f"Update payment method error: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Failed to update payment method',
            'error_code': 'PAYMENT_UPDATE_ERROR'
        }, status=500)

@csrf_exempt
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def billing_history_api(request):
    """
    Get user billing history
    GET /api/user/billing-history
    GET /api/billing/history
    """
    try:
        user = request.user
        page = int(request.GET.get('page', 1))
        limit = int(request.GET.get('limit', 20))
        
        # Get billing history records
        billing_records = BillingHistory.objects.filter(user=user).order_by('-created_at')
        
        # Paginate results
        paginator = Paginator(billing_records, limit)
        page_obj = paginator.get_page(page)
        
        billing_data = []
        for record in page_obj:
            billing_data.append({
                'id': record.invoice_id if hasattr(record, 'invoice_id') else f"INV-{record.id}",
                'date': record.created_at.strftime('%Y-%m-%d'),
                'description': getattr(record, 'description', f"Subscription Payment - {record.created_at.strftime('%B %Y')}"),
                'amount': float(record.amount) if hasattr(record, 'amount') else 49.99,
                'status': getattr(record, 'status', 'Paid'),
                'method': getattr(record, 'payment_method', 'Credit Card'),
                'download_url': f"/api/billing/download/{record.invoice_id if hasattr(record, 'invoice_id') else record.id}"
            })
        
        return JsonResponse({
            'success': True,
            'data': billing_data,
            'pagination': {
                'current_page': page,
                'total_pages': paginator.num_pages,
                'total_records': paginator.count,
                'has_next': page_obj.has_next(),
                'has_previous': page_obj.has_previous()
            }
        })
        
    except Exception as e:
        logger.error(f"Billing history error: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Failed to retrieve billing history',
            'error_code': 'BILLING_HISTORY_ERROR'
        }, status=500)

@csrf_exempt
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def download_invoice_api(request, invoice_id):
    """
    Download invoice PDF
    GET /api/billing/download/{invoice_id}
    """
    try:
        user = request.user
        
        # Get billing record
        try:
            if invoice_id.startswith('INV-'):
                billing_record = BillingHistory.objects.get(invoice_id=invoice_id, user=user)
            else:
                billing_record = BillingHistory.objects.get(id=invoice_id, user=user)
        except BillingHistory.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Invoice not found',
                'error_code': 'INVOICE_NOT_FOUND'
            }, status=404)
        
        # Generate PDF content (simplified for demo)
        pdf_content = f"""
        INVOICE {invoice_id}
        
        Date: {billing_record.created_at.strftime('%Y-%m-%d')}
        Amount: ${getattr(billing_record, 'amount', 49.99):.2f}
        Status: {getattr(billing_record, 'status', 'Paid')}
        
        Thank you for your business!
        """
        
        response = HttpResponse(pdf_content.encode('utf-8'), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="invoice_{invoice_id}.pdf"'
        return response
        
    except Exception as e:
        logger.error(f"Download invoice error: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Failed to download invoice',
            'error_code': 'DOWNLOAD_ERROR'
        }, status=500)

@csrf_exempt
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_plan_api(request):
    """
    Get current subscription plan
    GET /api/billing/current-plan
    """
    try:
        user = request.user
        profile, created = UserProfile.objects.get_or_create(user=user)
        
        return JsonResponse({
            'success': True,
            'data': {
                'plan_name': getattr(profile, 'plan_name', 'Free'),
                'plan_type': getattr(profile, 'plan_type', 'free'),
                'is_premium': getattr(profile, 'is_premium', False),
                'billing_cycle': getattr(profile, 'billing_cycle', 'monthly'),
                'next_billing_date': getattr(profile, 'next_billing_date', None),
                'features': {
                    'api_calls_limit': getattr(profile, 'api_calls_limit', 100),
                    'real_time_data': getattr(profile, 'is_premium', False),
                    'portfolio_tracking': True,
                    'alerts': getattr(profile, 'is_premium', False),
                    'advanced_analytics': getattr(profile, 'is_premium', False)
                }
            }
        })
        
    except Exception as e:
        logger.error(f"Current plan error: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Failed to retrieve current plan',
            'error_code': 'CURRENT_PLAN_ERROR'
        }, status=500)

@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_plan_api(request):
    """
    Change subscription plan
    POST /api/billing/change-plan
    """
    try:
        data = json.loads(request.body) if request.body else {}
        
        user = request.user
        profile, created = UserProfile.objects.get_or_create(user=user)
        
        new_plan = data.get('plan_type')
        billing_cycle = data.get('billing_cycle', 'monthly')
        
        if new_plan not in ['free', 'basic', 'pro', 'enterprise']:
            return JsonResponse({
                'success': False,
                'error': 'Invalid plan type',
                'error_code': 'INVALID_PLAN'
            }, status=400)
        
        # Update plan
        profile.plan_type = new_plan
        profile.billing_cycle = billing_cycle
        profile.is_premium = new_plan != 'free'
        profile.plan_changed_at = timezone.now()
        
        # Set API limits based on plan
        plan_limits = {
            'free': 100,
            'basic': 1000,
            'pro': 10000,
            'enterprise': 100000
        }
        profile.api_calls_limit = plan_limits.get(new_plan, 100)
        
        profile.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Plan changed to {new_plan} successfully',
            'data': {
                'plan_type': profile.plan_type,
                'billing_cycle': profile.billing_cycle,
                'is_premium': profile.is_premium,
                'api_calls_limit': profile.api_calls_limit
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON format',
            'error_code': 'INVALID_JSON'
        }, status=400)
    except Exception as e:
        logger.error(f"Change plan error: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Failed to change plan',
            'error_code': 'PLAN_CHANGE_ERROR'
        }, status=500)

@csrf_exempt
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def billing_stats_api(request):
    """
    Get billing statistics
    GET /api/billing/stats
    """
    try:
        user = request.user
        
        # Calculate billing statistics
        total_spent = BillingHistory.objects.filter(user=user).aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0.00')
        
        recent_payments = BillingHistory.objects.filter(
            user=user,
            created_at__gte=timezone.now() - timedelta(days=90)
        ).count()
        
        return JsonResponse({
            'success': True,
            'data': {
                'total_spent': float(total_spent),
                'recent_payments': recent_payments,
                'account_status': 'Active',
                'next_billing_date': (timezone.now() + timedelta(days=30)).isoformat()
            }
        })
        
    except Exception as e:
        logger.error(f"Billing stats error: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Failed to retrieve billing stats',
            'error_code': 'BILLING_STATS_ERROR'
        }, status=500)

# Notification endpoints
@csrf_exempt
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def notification_settings_api(request):
    """
    Get or update notification settings
    GET/POST /api/user/notification-settings
    GET/POST /api/notifications/settings
    """
    try:
        user = request.user
        settings, created = NotificationSettings.objects.get_or_create(user=user)
        
        if request.method == 'GET':
            return JsonResponse({
                'success': True,
                'data': {
                    'trading': {
                        'price_alerts': getattr(settings, 'price_alerts', True),
                        'volume_alerts': getattr(settings, 'volume_alerts', True),
                        'market_hours': getattr(settings, 'market_hours', False)
                    },
                    'portfolio': {
                        'daily_summary': getattr(settings, 'daily_summary', True),
                        'weekly_report': getattr(settings, 'weekly_report', True),
                        'milestone_alerts': getattr(settings, 'milestone_alerts', True)
                    },
                    'news': {
                        'breaking_news': getattr(settings, 'breaking_news', True),
                        'earnings_alerts': getattr(settings, 'earnings_alerts', False),
                        'analyst_ratings': getattr(settings, 'analyst_ratings', False)
                    },
                    'security': {
                        'login_alerts': getattr(settings, 'login_alerts', True),
                        'billing_updates': getattr(settings, 'billing_updates', True),
                        'plan_updates': getattr(settings, 'plan_updates', True)
                    }
                }
            })
        
        elif request.method == 'POST':
            data = json.loads(request.body) if request.body else {}
            
            # Update trading notifications
            if 'trading' in data:
                trading = data['trading']
                if 'price_alerts' in trading:
                    settings.price_alerts = trading['price_alerts']
                if 'volume_alerts' in trading:
                    settings.volume_alerts = trading['volume_alerts']
                if 'market_hours' in trading:
                    settings.market_hours = trading['market_hours']
            
            # Update portfolio notifications
            if 'portfolio' in data:
                portfolio = data['portfolio']
                if 'daily_summary' in portfolio:
                    settings.daily_summary = portfolio['daily_summary']
                if 'weekly_report' in portfolio:
                    settings.weekly_report = portfolio['weekly_report']
                if 'milestone_alerts' in portfolio:
                    settings.milestone_alerts = portfolio['milestone_alerts']
            
            # Update news notifications
            if 'news' in data:
                news = data['news']
                if 'breaking_news' in news:
                    settings.breaking_news = news['breaking_news']
                if 'earnings_alerts' in news:
                    settings.earnings_alerts = news['earnings_alerts']
                if 'analyst_ratings' in news:
                    settings.analyst_ratings = news['analyst_ratings']
            
            # Update security notifications
            if 'security' in data:
                security = data['security']
                if 'login_alerts' in security:
                    settings.login_alerts = security['login_alerts']
                if 'billing_updates' in security:
                    settings.billing_updates = security['billing_updates']
                if 'plan_updates' in security:
                    settings.plan_updates = security['plan_updates']
            
            settings.updated_at = timezone.now()
            settings.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Notification settings updated successfully'
            })
            
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON format',
            'error_code': 'INVALID_JSON'
        }, status=400)
    except Exception as e:
        logger.error(f"Notification settings error: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Failed to manage notification settings',
            'error_code': 'NOTIFICATION_ERROR'
        }, status=500)

# Usage statistics endpoint
@csrf_exempt
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def usage_stats_api(request):
    """
    Get user usage statistics
    GET /api/usage-stats
    """
    try:
        user = request.user
        profile, created = UserProfile.objects.get_or_create(user=user)
        
        # Calculate usage statistics
        today = timezone.now().date()
        this_month = timezone.now().replace(day=1).date()
        
        # Get usage stats if the model exists
        try:
            daily_usage = UsageStats.objects.filter(
                user=user,
                date=today
            ).first()
            
            monthly_usage = UsageStats.objects.filter(
                user=user,
                date__gte=this_month
            ).aggregate(
                total_api_calls=Sum('api_calls'),
                total_requests=Sum('requests')
            )
        except:
            # Fallback if UsageStats model doesn't exist
            daily_usage = None
            monthly_usage = {'total_api_calls': 0, 'total_requests': 0}
        
        return JsonResponse({
            'success': True,
            'data': {
                'daily': {
                    'api_calls': daily_usage.api_calls if daily_usage else 0,
                    'requests': daily_usage.requests if daily_usage else 0,
                    'date': today.isoformat()
                },
                'monthly': {
                    'api_calls': monthly_usage['total_api_calls'] or 0,
                    'requests': monthly_usage['total_requests'] or 0,
                    'limit': getattr(profile, 'api_calls_limit', 100),
                    'remaining': max(0, getattr(profile, 'api_calls_limit', 100) - (monthly_usage['total_api_calls'] or 0))
                },
                'account': {
                    'plan_type': getattr(profile, 'plan_type', 'free'),
                    'is_premium': getattr(profile, 'is_premium', False),
                    'member_since': user.date_joined.isoformat()
                }
            }
        })
        
    except Exception as e:
        logger.error(f"Usage stats error: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Failed to retrieve usage statistics',
            'error_code': 'USAGE_STATS_ERROR'
        }, status=500)