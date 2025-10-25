from django.shortcuts import render
from django.http import JsonResponse, Http404
from django.views.decorators.csrf import csrf_exempt
import json

def homepage(request):
    """Homepage view with API information"""
    context = {
        'title': 'Stock Scanner - NASDAQ Data API',
        'version': '1.0.0',
        'endpoints': [
            {'url': '/admin/', 'description': 'Django Admin Panel'},
            {'url': '/api/stocks/', 'description': 'Stock Data API'},
            {'url': '/api/wordpress/', 'description': 'WordPress Integration API'},
        ]
    }
    return render(request, 'core/homepage.html', context)

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
    """List available screeners with a run link for each."""
    screeners = []
    for key, data in PREDEFINED_SCREENERS.items():
        screeners.append({
            'key': key,
            'title': data.get('title', key.replace('-', ' ').title()),
            'filters': data.get('filters', {}),
            'detail_url': f"/screeners/{key}/"
        })
    return render(request, 'screeners.html', {'screeners': screeners})

def screener_detail(request, key):
    """Detail page for a screener that displays the title and filters and auto-runs on load."""
    config = PREDEFINED_SCREENERS.get(key)
    if not config:
        raise Http404('Screener not found')
    context = {
        'screener_key': key,
        'title': config.get('title', key.replace('-', ' ').title()),
        'filters': config.get('filters', {}),
        'api_url': '/api/market/filter/'
    }
    return render(request, 'screener_detail.html', context)

def stock_detail_page(request, ticker: str):
    ticker = (ticker or '').upper()
    return render(request, 'core/stock_detail.html', {
        'title': f"{ticker} • Stock Detail",
        'ticker': ticker,
    })
