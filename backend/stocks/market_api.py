from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.utils import timezone
from datetime import datetime
import pytz

from .models import Stock


@api_view(['GET'])
@permission_classes([AllowAny])
def market_status_api(request):
    """
    GET /api/market/market-status
    Returns whether the market is open based on US/Eastern regular hours.
    """
    try:
        eastern = pytz.timezone('US/Eastern')
        now_et = datetime.now(eastern)
        is_weekday = now_et.weekday() < 5
        open_time = now_et.replace(hour=9, minute=30, second=0, microsecond=0)
        close_time = now_et.replace(hour=16, minute=0, second=0, microsecond=0)
        is_open = is_weekday and (open_time <= now_et < close_time)
        return Response({
            'success': True,
            'market': {
                'status': 'open' if is_open else 'closed',
                'open': open_time.isoformat(),
                'close': close_time.isoformat(),
                'now': now_et.isoformat()
            }
        })
    except Exception:
        return Response({'success': True, 'market': {'status': 'unknown'}}, status=200)


@api_view(['GET'])
@permission_classes([AllowAny])
def sectors_performance_api(request):
    """
    GET /api/market/sectors/performance
    Without a stored sector field, provide a single aggregate bucket labeled 'Unspecified'.
    """
    try:
        stocks = Stock.objects.exclude(change_percent__isnull=True)
        count = stocks.count()
        avg_change = 0.0
        if count:
            # Approximate average change percent
            vals = list(stocks.values_list('change_percent', flat=True)[:1000])
            nums = [float(v) for v in vals if v is not None]
            avg_change = sum(nums) / len(nums) if nums else 0.0
        data = [
            {
                'sector': 'Unspecified',
                'avg_change_percent': round(avg_change, 2),
                'count': count
            }
        ]
        return Response({'success': True, 'sectors': data, 'timestamp': timezone.now().isoformat()})
    except Exception:
        return Response({'success': True, 'sectors': [], 'timestamp': timezone.now().isoformat()})

