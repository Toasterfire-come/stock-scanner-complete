from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db import connection
import json
import datetime

def homepage(request):
    """
    Homepage view - supports both HTML and API responses
    HTML: Full homepage template
    API: Basic API information
    """
    context = {
        'title': 'Stock Scanner - NASDAQ Data API',
        'version': '1.0.0',
        'endpoints': [
            {'url': '/admin/', 'description': 'Django Admin Panel'},
            {'url': '/api/stocks/', 'description': 'Stock Data API'},
            {'url': '/docs/', 'description': 'API Documentation'},
            {'url': '/revenue/revenue-analytics/', 'description': 'Revenue Analytics'},
        ]
    }
    
    # Check if this is an API request
    if getattr(request, 'is_api_request', False):
        return JsonResponse({
            'success': True,
            'data': {
                'title': context['title'],
                'version': context['version'],
                'endpoints': context['endpoints'],
                'timestamp': datetime.datetime.now().isoformat()
            }
        })
    
    return render(request, 'core/homepage.html', context)

def api_documentation(request):
    """
    API documentation page - supports both HTML and API responses
    HTML: Full documentation template
    API: Structured endpoint data
    """
    endpoints_data = {
        'stock_endpoints': [
            {'method': 'GET', 'path': '/api/stocks/', 'description': 'List all stocks'},
            {'method': 'GET', 'path': '/api/stock/{ticker}/', 'description': 'Get stock details'},
            {'method': 'GET', 'path': '/api/search/', 'description': 'Search stocks'},
            {'method': 'GET', 'path': '/api/trending/', 'description': 'Get trending stocks'},
            {'method': 'GET', 'path': '/api/realtime/{ticker}/', 'description': 'Real-time stock data'},
        ],
        'analytics_endpoints': [
            {'method': 'GET', 'path': '/revenue/revenue-analytics/', 'description': 'Revenue analytics'},
            {'method': 'GET', 'path': '/api/health/', 'description': 'Health check'},
            {'method': 'GET', 'path': '/api/statistics/', 'description': 'Market statistics'},
        ],
        'management_endpoints': [
            {'method': 'POST', 'path': '/api/alerts/create/', 'description': 'Create price alert'},
            {'method': 'POST', 'path': '/revenue/initialize-codes/', 'description': 'Initialize discount codes'},
        ]
    }
    
    # Check if this is an API request
    if getattr(request, 'is_api_request', False):
        return JsonResponse({
            'success': True,
            'data': {
                'title': 'Stock Scanner API Documentation',
                'base_url': request.build_absolute_uri('/'),
                'endpoints': endpoints_data,
                'timestamp': datetime.datetime.now().isoformat()
            }
        })
    
    return render(request, 'api/documentation.html')

@csrf_exempt
@require_http_methods(["GET", "HEAD", "OPTIONS"])
def health_check(request):
    """
    Health check endpoint - always returns JSON
    Compatible with both WordPress and direct access
    """
    try:
        # Test database connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            db_status = 'connected'
    except Exception as e:
        db_status = f'error: {str(e)}'
    
    health_data = {
        'status': 'healthy' if db_status == 'connected' else 'degraded',
        'database': db_status,
        'version': '1.0.0',
        'timestamp': datetime.datetime.now().isoformat(),
        'endpoints': {
            'stocks': '/api/stocks/',
            'health': '/api/health/',
            'revenue': '/revenue/revenue-analytics/',
            'docs': '/docs/',
            'trending': '/api/trending/',
            'search': '/api/search/',
        },
        'features': {
            'wordpress_integration': True,
            'real_time_data': True,
            'alerts': True,
            'analytics': True,
        }
    }
    
    return JsonResponse(health_data)
