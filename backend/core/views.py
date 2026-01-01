"""
Core views for API-only backend
No HTML templates - returns JSON responses only
"""
from django.http import JsonResponse
from django.db import connection


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


def health_check(request):
    """Health check endpoint"""
    try:
        # Test database connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"

    return JsonResponse({
        'status': 'ok',
        'database': db_status,
        'api': 'operational'
    })
