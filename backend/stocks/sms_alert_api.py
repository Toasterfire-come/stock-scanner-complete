"""
SMS Alert API Endpoints
RESTful API for managing SMS alerts via TextBelt.
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from decimal import Decimal

from stocks.models import (
    SMSAlertRule,
    SMSAlertCondition,
    SMSAlertHistory,
    SMSAlertQuota,
    Stock,
    UserWatchlist
)
from stocks.services.textbelt_service import TextBeltService
from stocks.services.alert_evaluation_service import AlertEvaluationService


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def alert_rules(request):
    """
    GET: List user's alert rules
    POST: Create new alert rule
    """
    if request.method == 'GET':
        alerts = SMSAlertRule.objects.filter(user=request.user).prefetch_related('conditions')

        alerts_data = [
            {
                'id': alert.id,
                'name': alert.name,
                'ticker': alert.stock.ticker if alert.stock else None,
                'watchlist_id': alert.watchlist.id if alert.watchlist else None,
                'watchlist_name': alert.watchlist.name if alert.watchlist else None,
                'is_multi_condition': alert.is_multi_condition,
                'condition_operator': alert.condition_operator,
                'phone_number': alert.phone_number,
                'is_active': alert.is_active,
                'trigger_count': alert.trigger_count,
                'last_triggered_at': alert.last_triggered_at.isoformat() if alert.last_triggered_at else None,
                'is_one_time': alert.is_one_time,
                'max_triggers_per_day': alert.max_triggers_per_day,
                'webhook_enabled': alert.webhook_enabled,
                'webhook_url': alert.webhook_url if alert.webhook_enabled else None,
                'conditions': [
                    {
                        'id': cond.id,
                        'type': cond.condition_type,
                        'type_display': cond.get_condition_type_display(),
                        'target_value': float(cond.target_value),
                        'indicator_period': cond.indicator_period,
                        'comparison_period': cond.comparison_period,
                    }
                    for cond in alert.conditions.all()
                ],
                'created_at': alert.created_at.isoformat(),
            }
            for alert in alerts.order_by('-created_at')
        ]

        return Response({
            'success': True,
            'alerts': alerts_data,
            'count': len(alerts_data)
        })

    elif request.method == 'POST':
        # Create new alert rule
        name = request.data.get('name')
        ticker = request.data.get('ticker')
        watchlist_id = request.data.get('watchlist_id')
        phone_number = request.data.get('phone_number')
        conditions = request.data.get('conditions', [])

        # Validation
        if not name:
            return Response({'success': False, 'error': 'Alert name is required'},
                          status=status.HTTP_400_BAD_REQUEST)

        if not phone_number:
            return Response({'success': False, 'error': 'Phone number is required'},
                          status=status.HTTP_400_BAD_REQUEST)

        if not ticker and not watchlist_id:
            return Response({'success': False, 'error': 'Either ticker or watchlist is required'},
                          status=status.HTTP_400_BAD_REQUEST)

        if not conditions:
            return Response({'success': False, 'error': 'At least one condition is required'},
                          status=status.HTTP_400_BAD_REQUEST)

        # Check tier limits
        is_multi_condition = len(conditions) > 1
        if is_multi_condition:
            # Check if user has Pro tier
            user_profile = getattr(request.user, 'profile', None)
            if not user_profile or user_profile.plan_type != 'pro':
                return Response({
                    'success': False,
                    'error': 'Multi-condition alerts require Pro tier subscription'
                }, status=status.HTTP_403_FORBIDDEN)

        try:
            with transaction.atomic():
                # Get stock or watchlist
                stock = None
                watchlist = None

                if ticker:
                    stock = Stock.objects.get(ticker=ticker.upper())
                elif watchlist_id:
                    watchlist = UserWatchlist.objects.get(id=watchlist_id, user=request.user)

                # Create alert rule
                alert_rule = SMSAlertRule.objects.create(
                    user=request.user,
                    name=name,
                    stock=stock,
                    watchlist=watchlist,
                    is_multi_condition=is_multi_condition,
                    condition_operator=request.data.get('condition_operator', 'and'),
                    phone_number=phone_number,
                    is_one_time=request.data.get('is_one_time', False),
                    max_triggers_per_day=request.data.get('max_triggers_per_day', 10),
                    webhook_enabled=request.data.get('webhook_enabled', False),
                    webhook_url=request.data.get('webhook_url', '')
                )

                # Create conditions
                for cond_data in conditions:
                    SMSAlertCondition.objects.create(
                        alert_rule=alert_rule,
                        condition_type=cond_data['type'],
                        target_value=Decimal(str(cond_data['target_value'])),
                        indicator_period=cond_data.get('indicator_period'),
                        comparison_period=cond_data.get('comparison_period')
                    )

                return Response({
                    'success': True,
                    'message': 'Alert created successfully',
                    'alert_id': alert_rule.id
                }, status=status.HTTP_201_CREATED)

        except Stock.DoesNotExist:
            return Response({'success': False, 'error': f'Stock {ticker} not found'},
                          status=status.HTTP_404_NOT_FOUND)
        except UserWatchlist.DoesNotExist:
            return Response({'success': False, 'error': 'Watchlist not found'},
                          status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'success': False, 'error': str(e)},
                          status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def alert_rule_detail(request, alert_id):
    """
    GET: Get alert rule details
    PUT: Update alert rule
    DELETE: Delete alert rule
    """
    try:
        alert = SMSAlertRule.objects.get(id=alert_id, user=request.user)
    except SMSAlertRule.DoesNotExist:
        return Response({'success': False, 'error': 'Alert not found'},
                       status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        return Response({
            'success': True,
            'alert': {
                'id': alert.id,
                'name': alert.name,
                'ticker': alert.stock.ticker if alert.stock else None,
                'watchlist_id': alert.watchlist.id if alert.watchlist else None,
                'is_multi_condition': alert.is_multi_condition,
                'condition_operator': alert.condition_operator,
                'phone_number': alert.phone_number,
                'is_active': alert.is_active,
                'trigger_count': alert.trigger_count,
                'last_triggered_at': alert.last_triggered_at.isoformat() if alert.last_triggered_at else None,
                'conditions': [
                    {
                        'id': cond.id,
                        'type': cond.condition_type,
                        'target_value': float(cond.target_value),
                        'indicator_period': cond.indicator_period,
                        'comparison_period': cond.comparison_period,
                    }
                    for cond in alert.conditions.all()
                ]
            }
        })

    elif request.method == 'PUT':
        # Update alert
        alert.name = request.data.get('name', alert.name)
        alert.phone_number = request.data.get('phone_number', alert.phone_number)
        alert.is_active = request.data.get('is_active', alert.is_active)
        alert.is_one_time = request.data.get('is_one_time', alert.is_one_time)
        alert.max_triggers_per_day = request.data.get('max_triggers_per_day', alert.max_triggers_per_day)
        alert.webhook_enabled = request.data.get('webhook_enabled', alert.webhook_enabled)
        alert.webhook_url = request.data.get('webhook_url', alert.webhook_url)
        alert.save()

        return Response({'success': True, 'message': 'Alert updated successfully'})

    elif request.method == 'DELETE':
        alert.delete()
        return Response({'success': True, 'message': 'Alert deleted successfully'})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_alert(request, alert_id):
    """Toggle alert active status"""
    try:
        alert = SMSAlertRule.objects.get(id=alert_id, user=request.user)
    except SMSAlertRule.DoesNotExist:
        return Response({'success': False, 'error': 'Alert not found'},
                       status=status.HTTP_404_NOT_FOUND)

    alert.is_active = not alert.is_active
    alert.save()

    return Response({
        'success': True,
        'is_active': alert.is_active,
        'message': f'Alert {"activated" if alert.is_active else "deactivated"}'
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def alert_history(request):
    """Get SMS alert delivery history for user"""
    # Get user's alerts
    user_alerts = SMSAlertRule.objects.filter(user=request.user)

    # Get history for these alerts
    history = SMSAlertHistory.objects.filter(
        alert_rule__in=user_alerts
    ).select_related('alert_rule', 'stock').order_by('-created_at')[:100]

    history_data = [
        {
            'id': h.id,
            'alert_name': h.alert_rule.name,
            'ticker': h.stock.ticker if h.stock else None,
            'message': h.message,
            'status': h.status,
            'trigger_price': float(h.trigger_price) if h.trigger_price else None,
            'trigger_volume': h.trigger_volume,
            'delivery_attempts': h.delivery_attempts,
            'error_message': h.error_message,
            'webhook_sent': h.webhook_sent,
            'created_at': h.created_at.isoformat(),
            'sent_at': h.sent_at.isoformat() if h.sent_at else None,
        }
        for h in history
    ]

    return Response({
        'success': True,
        'history': history_data,
        'count': len(history_data)
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def quota_status(request):
    """Get user's SMS quota status"""
    quota_info = TextBeltService.get_quota_status(request.user)

    return Response({
        'success': True,
        'quota': quota_info
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def test_alert(request, alert_id):
    """
    Test an alert by manually triggering it.
    Sends a test SMS without checking conditions.
    """
    try:
        alert = SMSAlertRule.objects.get(id=alert_id, user=request.user)
    except SMSAlertRule.DoesNotExist:
        return Response({'success': False, 'error': 'Alert not found'},
                       status=status.HTTP_404_NOT_FOUND)

    # Get stock for test
    if alert.stock:
        stock = alert.stock
    elif alert.watchlist:
        # Use first stock in watchlist
        first_item = alert.watchlist.items.first()
        if not first_item:
            return Response({'success': False, 'error': 'Watchlist is empty'},
                           status=status.HTTP_400_BAD_REQUEST)
        stock = first_item.stock
    else:
        return Response({'success': False, 'error': 'Alert has no stock or watchlist'},
                       status=status.HTTP_400_BAD_REQUEST)

    # Prepare test trigger data
    trigger_data = {
        'price': float(stock.current_price) if stock.current_price else 0.0,
        'volume': stock.volume or 0,
        'change_percent': float(stock.change_percent) if stock.change_percent else 0.0,
        'conditions': [{'type': 'test', 'met': True}]
    }

    # Send test SMS
    result = TextBeltService.send_alert_sms(
        alert_rule=alert,
        stock=stock,
        trigger_data=trigger_data
    )

    if result['success']:
        return Response({
            'success': True,
            'message': f'Test SMS sent to {alert.phone_number}',
            'textbelt_id': result.get('textbelt_id')
        })
    else:
        return Response({
            'success': False,
            'error': result.get('error')
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def available_conditions(request):
    """Get list of available alert condition types"""
    conditions = [
        {
            'type': cond_type,
            'display': cond_display,
            'requires_period': cond_type in ['rsi_above', 'rsi_below', 'sma_cross_above', 'sma_cross_below'],
            'requires_comparison': cond_type in ['sma_cross_above', 'sma_cross_below'],
            'tier': 'pro' if cond_type in ['rsi_above', 'rsi_below', 'macd_cross_bullish', 'macd_cross_bearish', 'sma_cross_above', 'sma_cross_below'] else 'basic'
        }
        for cond_type, cond_display in SMSAlertRule.ALERT_TYPES
    ]

    return Response({
        'success': True,
        'conditions': conditions
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def alert_summary(request):
    """Get user's alert summary"""
    summary = AlertEvaluationService.get_user_alert_summary(request.user)

    return Response({
        'success': True,
        **summary
    })


@api_view(['POST'])
@permission_classes([])  # No auth required for cron job
def check_alerts_cron(request):
    """
    Cron endpoint to check all active alerts.
    Should be called every minute by a scheduler.

    Security: Should be protected by API key or internal network only.
    """
    # Optional: Check for API key
    api_key = request.META.get('HTTP_X_API_KEY')
    expected_key = getattr(settings, 'ALERT_CRON_API_KEY', None)

    if expected_key and api_key != expected_key:
        return Response({'success': False, 'error': 'Unauthorized'},
                       status=status.HTTP_401_UNAUTHORIZED)

    # Run alert checks
    stats = AlertEvaluationService.check_all_active_alerts()

    return Response({
        'success': True,
        'message': 'Alert check completed',
        'stats': stats
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def textbelt_status(request):
    """Check TextBelt server status"""
    result = TextBeltService.test_textbelt_connection()

    return Response({
        'success': result['success'],
        'message': result['message'],
        'config': result.get('config', {})
    })
