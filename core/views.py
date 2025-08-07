from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db import connection
import json
import datetime
import pytz

def _get_market_status_et(now_utc: datetime.datetime | None = None):
    """Return market open/closed status based on US/Eastern pre/post market.
    Open window: Weekdays 04:00–20:00 ET.
    """
    eastern = pytz.timezone('US/Eastern')
    now = now_utc or datetime.datetime.utcnow().replace(tzinfo=pytz.UTC)
    now_et = now.astimezone(eastern)
    hhmm = now_et.strftime('%H:%M')
    is_weekday = now_et.weekday() < 5
    is_open_window = is_weekday and ('04:00' <= hhmm < '20:00')
    return {
        'is_open': is_open_window,
        'now_et': now_et,
        'phase': (
            'premarket' if '04:00' <= hhmm < '09:30' else
            'market' if '09:30' <= hhmm < '16:00' else
            'postmarket' if '16:00' <= hhmm < '20:00' else
            'closed'
        )
    }

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
    
    # Market status flags for UI banner
    status = _get_market_status_et()
    context.update({
        'market_is_closed': not status['is_open'],
        'market_phase': status['phase'],
        'market_now_et': status['now_et'],
        'market_status_message': 'Market is closed. Information will not be updated until the market reopens.' if not status['is_open'] else ''
    })
    
    # Check if this is an API request
    if getattr(request, 'is_api_request', False):
        return JsonResponse({
            'success': True,
            'data': {
                'title': context['title'],
                'version': context['version'],
                'endpoints': context['endpoints'],
                'timestamp': datetime.datetime.now().isoformat(),
                'market': {
                    'is_open': status['is_open'],
                    'phase': status['phase'],
                    'now_et': status['now_et'].isoformat(),
                }
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
            {'method': 'GET', 'path': '/api/nasdaq/', 'description': 'NASDAQ stocks'},
            {'method': 'GET', 'path': '/api/filter/', 'description': 'Filter stocks'},
            {'method': 'GET', 'path': '/api/market-stats/', 'description': 'Market statistics'},
        ],
        'portfolio_endpoints': [
            {'method': 'GET', 'path': '/api/portfolio/list/', 'description': 'List portfolios'},
            {'method': 'POST', 'path': '/api/portfolio/create/', 'description': 'Create portfolio'},
            {'method': 'POST', 'path': '/api/portfolio/add-holding/', 'description': 'Add holding'},
            {'method': 'POST', 'path': '/api/portfolio/sell-holding/', 'description': 'Sell holding'},
            {'method': 'GET', 'path': '/api/portfolio/{id}/performance/', 'description': 'Portfolio performance'},
        ],
        'watchlist_endpoints': [
            {'method': 'GET', 'path': '/api/watchlist/list/', 'description': 'List watchlists'},
            {'method': 'POST', 'path': '/api/watchlist/create/', 'description': 'Create watchlist'},
            {'method': 'POST', 'path': '/api/watchlist/add-stock/', 'description': 'Add stock to watchlist'},
            {'method': 'POST', 'path': '/api/watchlist/remove-stock/', 'description': 'Remove stock'},
            {'method': 'GET', 'path': '/api/watchlist/{id}/performance/', 'description': 'Watchlist performance'},
        ],
        'news_endpoints': [
            {'method': 'GET', 'path': '/api/news/feed/', 'description': 'Personalized news feed'},
            {'method': 'POST', 'path': '/api/news/mark-read/', 'description': 'Mark news as read'},
            {'method': 'POST', 'path': '/api/news/preferences/', 'description': 'Update news preferences'},
            {'method': 'GET', 'path': '/api/news/analytics/', 'description': 'News analytics'},
        ],
        'analytics_endpoints': [
            {'method': 'GET', 'path': '/revenue/revenue-analytics/', 'description': 'Revenue analytics'},
            {'method': 'GET', 'path': '/api/health/', 'description': 'Health check'},
            {'method': 'GET', 'path': '/api/statistics/', 'description': 'Market statistics'},
        ],
        'management_endpoints': [
            {'method': 'POST', 'path': '/api/alerts/create/', 'description': 'Create price alert'},
            {'method': 'POST', 'path': '/revenue/initialize-codes/', 'description': 'Initialize discount codes'},
            {'method': 'POST', 'path': '/api/subscription/', 'description': 'WordPress subscription'},
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

@csrf_exempt
@require_http_methods(["GET", "HEAD", "OPTIONS"])
def endpoint_status(request):
    """
    Endpoint status check - tests all major endpoints
    Compatible with both WordPress and direct access
    """
    import requests
    from django.conf import settings
    
    base_url = request.build_absolute_uri('/').rstrip('/')
    
    endpoints_to_test = [
        {'name': 'Homepage', 'url': f'{base_url}/', 'method': 'GET'},
        {'name': 'Health Check', 'url': f'{base_url}/api/health/', 'method': 'GET'},
        {'name': 'Stock List', 'url': f'{base_url}/api/stocks/', 'method': 'GET'},
        {'name': 'Trending Stocks', 'url': f'{base_url}/api/trending/', 'method': 'GET'},
        {'name': 'Search Stocks', 'url': f'{base_url}/api/search/?q=AAPL', 'method': 'GET'},
        {'name': 'Revenue Analytics', 'url': f'{base_url}/revenue/revenue-analytics/?format=json', 'method': 'GET'},
        {'name': 'Portfolio List', 'url': f'{base_url}/api/portfolio/list/', 'method': 'GET'},
        {'name': 'Watchlist List', 'url': f'{base_url}/api/watchlist/list/', 'method': 'GET'},
        {'name': 'News Feed', 'url': f'{base_url}/api/news/feed/', 'method': 'GET'},
        {'name': 'API Documentation', 'url': f'{base_url}/docs/', 'method': 'GET'},
    ]
    
    status_results = []
    
    for endpoint in endpoints_to_test:
        try:
            # Test each endpoint
            response = requests.get(endpoint['url'], timeout=5, headers={
                'User-Agent': 'Django-Endpoint-Test/1.0'
            })
            
            status_results.append({
                'name': endpoint['name'],
                'url': endpoint['url'],
                'status': 'success' if response.status_code < 400 else 'error',
                'status_code': response.status_code,
                'response_time': response.elapsed.total_seconds()
            })
            
        except Exception as e:
            status_results.append({
                'name': endpoint['name'],
                'url': endpoint['url'],
                'status': 'error',
                'error': str(e),
                'status_code': 0,
                'response_time': 0
            })
    
    # Check if this is an API request
    is_api_request = (
        request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest' or
        'application/json' in request.META.get('HTTP_ACCEPT', '') or
        request.GET.get('format') == 'json' or
        getattr(request, 'is_api_request', False)
    )
    
    if is_api_request:
        return JsonResponse({
            'success': True,
            'data': {
                'endpoints': status_results,
                'total_tested': len(endpoints_to_test),
                'successful': len([r for r in status_results if r['status'] == 'success']),
                'failed': len([r for r in status_results if r['status'] == 'error']),
                'timestamp': datetime.datetime.now().isoformat()
            }
        })
    else:
        context = {
            'endpoints': status_results,
            'total_tested': len(endpoints_to_test),
            'successful': len([r for r in status_results if r['status'] == 'success']),
            'failed': len([r for r in status_results if r['status'] == 'error']),
            'title': 'Endpoint Status Check'
        }
        return render(request, 'core/endpoint_status.html', context)
