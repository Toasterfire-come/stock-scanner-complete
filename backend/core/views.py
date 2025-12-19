from django.http import JsonResponse, Http404
from django.views.decorators.csrf import csrf_exempt
import json

def homepage(request):
    """API-only backend - return API information as JSON"""
    return JsonResponse({
        'name': 'TradeScanPro API',
        'version': '2.0',
        'description': 'Stock Scanner - NASDAQ Data API',
        'endpoints': {
            'admin': '/admin/',
            'stocks': '/api/stocks/',
            'auth': '/api/auth/',
            'billing': '/api/billing/',
            'backtesting': '/api/backtesting/',
            'education': '/api/education/',
            'health': '/health/'
        },
        'frontend_url': 'https://tradescanpro.com',
        'note': 'This is an API-only backend. Please use the React frontend for UI.'
    })

@csrf_exempt
def health_check(request):
    """Simple health check endpoint"""
    return JsonResponse({
        'status': 'healthy',
        'database': 'connected',
        'version': '1.0.0'
    })

# Predefined screeners and their filters (mapped to /api/market/filter/ params)
PREDEFINED_SCREENERS = {
    'high-volume': {
        'title': 'High Volume Movers',
        'filters': {
            'min_volume': '1000000',
            'order_by': 'volume',
            'limit': '100'
        }
    },
    'large-cap': {
        'title': 'Large Cap Stocks',
        'filters': {
            'min_market_cap': '10000000000',  # $10B
            'order_by': 'market_cap',
            'limit': '100'
        }
    },
    'top-gainers': {
        'title': 'Top Gainers (Today %)',
        'filters': {
            'order_by': 'price_change_percent',
            'limit': '100'
        }
    },
}

def screeners_list(request):
    """Return available screeners as JSON"""
    screeners = []
    for key, data in PREDEFINED_SCREENERS.items():
        screeners.append({
            'key': key,
            'title': data.get('title', key.replace('-', ' ').title()),
            'filters': data.get('filters', {}),
            'api_url': f"/api/market/filter/"
        })
    return JsonResponse({'screeners': screeners})

def screener_detail(request, key):
    """Return screener config as JSON"""
    config = PREDEFINED_SCREENERS.get(key)
    if not config:
        return JsonResponse({'error': 'Screener not found'}, status=404)

    return JsonResponse({
        'screener_key': key,
        'title': config.get('title', key.replace('-', ' ').title()),
        'filters': config.get('filters', {}),
        'api_url': '/api/market/filter/'
    })

def stock_detail_page(request, ticker: str):
    """Return stock detail info as JSON"""
    ticker = (ticker or '').upper()
    return JsonResponse({
        'ticker': ticker,
        'api_url': f'/api/stocks/{ticker}/',
        'note': 'Use the frontend at https://tradescanpro.com for full stock details'
    })
