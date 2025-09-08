"""
Alerts API: list, create, toggle, and delete user price alerts

Routes:
- GET    /api/alerts/
- POST   /api/alerts/create/
- POST   /api/alerts/{alertId}/toggle/
- POST   /api/alerts/{alertId}/delete/
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.core.cache import cache
from django.conf import settings

from decimal import Decimal, InvalidOperation
import logging
import json
import re
import time

from .models import Stock, StockAlert


logger = logging.getLogger(__name__)


def _serialize_alert(alert, user_email: str):
    """Serialize a StockAlert to the UI's expected camelCase shape."""
    try:
        current_price_value = float(alert.stock.current_price) if alert.stock.current_price is not None else None
    except Exception:
        current_price_value = None

    # Map model alert_type to UI condition
    if alert.alert_type == 'price_above':
        condition = 'above'
    elif alert.alert_type == 'price_below':
        condition = 'below'
    else:
        condition = 'above'

    return {
        'id': alert.id,
        'ticker': alert.stock.ticker,
        'currentPrice': current_price_value,
        'targetPrice': float(alert.target_value),
        'condition': condition,
        'email': user_email,
        'isActive': bool(alert.is_active),
        'isTriggered': alert.triggered_at is not None,
        'createdAt': alert.created_at.isoformat() if alert.created_at else None,
        'triggeredAt': alert.triggered_at.isoformat() if alert.triggered_at else None,
    }


def _attach_rate_limit_headers(request, resp: Response):
    """Attach optional rate limit headers to the response for consistency."""
    try:
        window = int(getattr(settings, 'RATE_LIMIT_WINDOW', 3600))
        if getattr(getattr(request, 'user', None), 'is_authenticated', False):
            ident = f"user_{getattr(request.user, 'id', '0')}"
            limit = int(getattr(settings, 'RATE_LIMIT_AUTHENTICATED_USERS', 1000))
        else:
            ip = request.META.get('HTTP_X_FORWARDED_FOR', '').split(',')[0] or request.META.get('REMOTE_ADDR', '0.0.0.0')
            ident = f"ip_{ip}"
            limit = int(getattr(settings, 'RATE_LIMIT_FREE_USERS', 100))

        cache_key = f"rate_limit_{ident}"
        data = cache.get(cache_key) or {}
        requests_list = data.get('requests') or []
        used = len(requests_list)
        if requests_list:
            earliest = min(requests_list)
            reset = max(1, int(earliest + window - time.time()))
        else:
            reset = window

        resp['X-RateLimit-Used'] = str(used)
        resp['X-RateLimit-Limit'] = str(limit)
        resp['X-RateLimit-Reset'] = str(reset)
    except Exception:
        # Never let headers calculation break the response
        pass


def _validate_ticker(raw_ticker: str) -> str:
    ticker = (raw_ticker or '').strip().upper()
    if not ticker:
        raise ValueError('Ticker is required')
    # Allow only A–Z, '.' and '-' per spec; limit length sensibly (<= 10)
    if not re.fullmatch(r'[A-Z][A-Z\.\-]{0,9}', ticker):
        raise ValueError('Ticker must be uppercase letters with optional . or -')
    return ticker


def _validate_target_price(value) -> Decimal:
    try:
        target = Decimal(str(value))
    except (InvalidOperation, TypeError):
        raise ValueError('target_price must be a number')
    if target <= 0:
        raise ValueError('target_price must be greater than 0')
    return target


def _validate_condition(value: str) -> str:
    if value not in ('above', 'below'):
        raise ValueError('condition must be "above" or "below"')
    return value


def _validate_email_or_fallback(provided_email: str, fallback_email: str) -> str:
    email = (provided_email or fallback_email or '').strip()
    if not email:
        raise ValueError('email is required')
    try:
        validate_email(email)
    except ValidationError:
        raise ValueError('email is invalid')
    return email


@csrf_exempt
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def alerts_list_api(request):
    """List alerts for the authenticated user."""
    try:
        alerts = StockAlert.objects.select_related('stock').filter(user=request.user).order_by('-created_at')
        items = [_serialize_alert(alert, request.user.email or '') for alert in alerts]
        resp = Response({'alerts': items}, status=status.HTTP_200_OK)
        _attach_rate_limit_headers(request, resp)
        return resp
    except Exception as e:
        logger.error(f"Alerts list error: {e}")
        # Per spec, return empty list on failures
        resp = Response({'alerts': []}, status=status.HTTP_200_OK)
        _attach_rate_limit_headers(request, resp)
        return resp


@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def alerts_create_api(request):
    """Create a new price alert for the authenticated user."""
    try:
        data = getattr(request, 'data', None)
        if data is None or data == {}:
            data = json.loads(request.body) if request.body else {}

        ticker = _validate_ticker(data.get('ticker'))
        target_price = _validate_target_price(data.get('target_price'))
        condition = _validate_condition((data.get('condition') or '').strip())
        email = _validate_email_or_fallback(data.get('email'), getattr(request.user, 'email', ''))

        try:
            stock = Stock.objects.get(ticker=ticker)
        except Stock.DoesNotExist:
            return Response({'message': 'invalid input: unknown ticker'}, status=status.HTTP_400_BAD_REQUEST)

        alert_type = 'price_above' if condition == 'above' else 'price_below'

        # Duplicate check: same user, stock, alert_type, target_value
        exists = StockAlert.objects.filter(
            user=request.user,
            stock=stock,
            alert_type=alert_type,
            target_value=target_price
        ).exists()
        if exists:
            return Response({'message': 'duplicate alert'}, status=status.HTTP_409_CONFLICT)

        alert = StockAlert.objects.create(
            user=request.user,
            stock=stock,
            alert_type=alert_type,
            target_value=target_price,
            is_active=True
        )

        payload = {
            'success': True,
            'alert_id': alert.id,
            'alert': _serialize_alert(alert, email),
        }
        resp = Response(payload, status=status.HTTP_201_CREATED)
        _attach_rate_limit_headers(request, resp)
        return resp

    except ValueError as ve:
        return Response({'message': str(ve)}, status=status.HTTP_400_BAD_REQUEST)
    except json.JSONDecodeError:
        return Response({'message': 'invalid input: bad json'}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Create alert error: {e}")
        return Response({'message': 'internal error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def alerts_toggle_api(request, alert_id: int):
    """Toggle or set active state for a user's alert."""
    try:
        try:
            alert = StockAlert.objects.select_related('stock').get(id=alert_id, user=request.user)
        except StockAlert.DoesNotExist:
            return Response({'message': 'not found'}, status=status.HTTP_404_NOT_FOUND)

        # Optional body: {"isActive": true|false}
        desired_state = None
        try:
            data = getattr(request, 'data', None)
            if data is None or data == {}:
                data = json.loads(request.body) if request.body else {}
            if isinstance(data, dict) and 'isActive' in data:
                desired_state = bool(data.get('isActive'))
        except Exception:
            desired_state = None

        if desired_state is None:
            alert.is_active = not alert.is_active
        else:
            alert.is_active = desired_state
        alert.save()

        payload = {'success': True, 'alert': _serialize_alert(alert, request.user.email or '')}
        resp = Response(payload, status=status.HTTP_200_OK)
        _attach_rate_limit_headers(request, resp)
        return resp
    except Exception as e:
        logger.error(f"Toggle alert error: {e}")
        return Response({'message': 'internal error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def alerts_delete_api(request, alert_id: int):
    """Delete a user's alert."""
    try:
        try:
            alert = StockAlert.objects.get(id=alert_id, user=request.user)
        except StockAlert.DoesNotExist:
            return Response({'message': 'not found'}, status=status.HTTP_404_NOT_FOUND)

        alert.delete()
        resp = Response({'success': True}, status=status.HTTP_200_OK)
        _attach_rate_limit_headers(request, resp)
        return resp
    except Exception as e:
        logger.error(f"Delete alert error: {e}")
        return Response({'message': 'internal error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

