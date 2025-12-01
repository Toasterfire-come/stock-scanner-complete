"""
Lightweight market endpoints without DRF/yfinance dependencies for Windows environments.

Provides: top_gainers_api, top_losers_api, most_active_api
"""

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone

from .models import Stock


def _fmt_decimal(v):
    try:
        return float(v) if v is not None else None
    except Exception:
        return None


@csrf_exempt
@require_http_methods(["GET"])
def top_gainers_api(request):
    try:
        try:
            limit = max(1, min(int(request.GET.get('limit', 10)), 100))
        except (TypeError, ValueError):
            limit = 10
        qs = Stock.objects.exclude(price_change_percent__isnull=True).order_by('-price_change_percent')[:limit]
        data = [{
            'ticker': s.ticker,
            'name': getattr(s, 'name', None) or getattr(s, 'company_name', None),
            'current_price': _fmt_decimal(s.current_price),
            'price_change': _fmt_decimal(getattr(s, 'price_change', None)),
            'price_change_percent': _fmt_decimal(getattr(s, 'price_change_percent', None)),
            'volume': s.volume,
            'market_cap': _fmt_decimal(s.market_cap),
        } for s in qs]
        return JsonResponse({'top_gainers': data, 'count': len(data), 'timestamp': timezone.now().isoformat()})
    except Exception as e:
        return JsonResponse({'error': 'Failed to retrieve top gainers', 'details': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def top_losers_api(request):
    try:
        try:
            limit = max(1, min(int(request.GET.get('limit', 10)), 100))
        except (TypeError, ValueError):
            limit = 10
        qs = Stock.objects.exclude(price_change_percent__isnull=True).order_by('price_change_percent')[:limit]
        data = [{
            'ticker': s.ticker,
            'name': getattr(s, 'name', None) or getattr(s, 'company_name', None),
            'current_price': _fmt_decimal(s.current_price),
            'price_change': _fmt_decimal(getattr(s, 'price_change', None)),
            'price_change_percent': _fmt_decimal(getattr(s, 'price_change_percent', None)),
            'volume': s.volume,
            'market_cap': _fmt_decimal(s.market_cap),
        } for s in qs]
        return JsonResponse({'top_losers': data, 'count': len(data), 'timestamp': timezone.now().isoformat()})
    except Exception as e:
        return JsonResponse({'error': 'Failed to retrieve top losers', 'details': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def most_active_api(request):
    try:
        try:
            limit = max(1, min(int(request.GET.get('limit', 10)), 100))
        except (TypeError, ValueError):
            limit = 10
        qs = Stock.objects.exclude(volume__isnull=True).order_by('-volume')[:limit]
        data = [{
            'ticker': s.ticker,
            'name': getattr(s, 'name', None) or getattr(s, 'company_name', None),
            'current_price': _fmt_decimal(s.current_price),
            'volume': s.volume,
            'price_change': _fmt_decimal(getattr(s, 'price_change', None)),
            'price_change_percent': _fmt_decimal(getattr(s, 'price_change_percent', None)),
            'market_cap': _fmt_decimal(s.market_cap),
        } for s in qs]
        return JsonResponse({'most_active': data, 'count': len(data), 'timestamp': timezone.now().isoformat()})
    except Exception as e:
        return JsonResponse({'error': 'Failed to retrieve most active stocks', 'details': str(e)}, status=500)
