from django.shortcuts import render
from django.http import JsonResponse
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.middleware.csrf import get_token
from django.views.decorators.http import require_http_methods
from django.db import connection
from django.conf import settings
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
'title': 'Stock Scanner - NYSE Data API',
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
    
    try:
        return render(request, 'core/homepage.html', context)
    except Exception:
        # Fallback JSON if template path or rendering fails
        return JsonResponse({
            'success': True,
            'data': {
                'title': context['title'],
                'version': context['version'],
                'endpoints': context['endpoints']
            }
        })

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
    
    try:
        return render(request, 'api/documentation.html')
    except Exception as e:
        # Fallback to JSON docs if template rendering fails
        return JsonResponse({
            'success': True,
            'data': {
                'title': 'Stock Scanner API Documentation',
                'base_url': request.build_absolute_uri('/'),
                'endpoints': endpoints_data,
                'timestamp': datetime.datetime.now().isoformat(),
                'warning': 'Template render failed; returning JSON documentation'
            }
        })

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

# Alias for /api/endpoint-status/ expected by frontend
@csrf_exempt
@require_http_methods(["GET", "HEAD", "OPTIONS"])
def endpoint_status_api(request):
    request.is_api_request = True
    return endpoint_status(request)

@csrf_exempt
@require_http_methods(["GET", "POST"])
def kill_switch(request):
    """
    Kill switch endpoint that reboots the host machine after a short delay.
    Requires correct password and feature flag enabled.
    """
    # Validate feature flag
    if not getattr(settings, 'KILL_SWITCH_ENABLED', False):
        if request.method == 'GET' and not getattr(request, 'is_api_request', False):
            return render(request, 'core/kill_switch.html', {
                'enabled': False,
                'error': 'Kill switch disabled'
            })
        return JsonResponse({'success': False, 'error': 'Kill switch disabled'}, status=403)

    # Validate configuration
    expected_password = str(getattr(settings, 'KILL_SWITCH_PASSWORD', '') or '')
    if not expected_password:
        if request.method == 'GET' and not getattr(request, 'is_api_request', False):
            return render(request, 'core/kill_switch.html', {
                'enabled': True,
                'error': 'Kill switch not configured'
            })
        return JsonResponse({'success': False, 'error': 'Kill switch not configured'}, status=500)

    # If GET from browser, render form
    if request.method == 'GET' and not getattr(request, 'is_api_request', False):
        return render(request, 'core/kill_switch.html', {'enabled': True})

    # Extract provided password and possible delay override
    provided_password = None
    delay_override_value = None
    content_type = request.META.get('CONTENT_TYPE', '')
    json_payload = None
    if 'application/json' in content_type:
        try:
            json_payload = json.loads((request.body or b'{}').decode('utf-8') or '{}')
            provided_password = json_payload.get('password') or json_payload.get('pass') or json_payload.get('token')
            delay_override_value = json_payload.get('delay')
        except Exception:
            provided_password = None
    if not provided_password:
        provided_password = (
            request.POST.get('password')
            or request.POST.get('pass')
            or request.POST.get('token')
            or request.headers.get('X-App-Password')
        )
    provided_password = '' if provided_password is None else str(provided_password)

    # Constant-time compare
    import hmac
    if not hmac.compare_digest(provided_password, expected_password):
        if not getattr(request, 'is_api_request', False):
            return render(request, 'core/kill_switch.html', {
                'enabled': True,
                'error': 'Unauthorized - invalid password'
            }, status=403)
        return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=403)

    # Determine delay (allow request override)
    try:
        default_delay_seconds = int(getattr(settings, 'KILL_SWITCH_DELAY_SECONDS', 5))
    except Exception:
        default_delay_seconds = 5
    # try POST form override if not provided via JSON
    if delay_override_value is None:
        delay_override_value = request.POST.get('delay') if hasattr(request, 'POST') else None
    try:
        delay_seconds = int(delay_override_value) if delay_override_value not in (None, '') else default_delay_seconds
    except Exception:
        delay_seconds = default_delay_seconds
    if delay_seconds < 0:
        delay_seconds = 0

    # Trigger reboot in background
    def _perform_reboot():
        import time
        import subprocess
        import platform
        import os
        time.sleep(delay_seconds)
        try:
            system_name = platform.system().lower()
            if system_name.startswith('win'):
                cmd = ['shutdown', '/r', '/t', '0', '/f']
            else:
                if (os.path.exists('/bin/systemctl') or os.path.exists('/usr/bin/systemctl')):
                    cmd = ['systemctl', 'reboot', '--force']
                else:
                    cmd = ['shutdown', '-r', 'now']
            subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            # Swallow any errors; nothing else we can do at this point
            pass

    import threading
    threading.Thread(target=_perform_reboot, daemon=True).start()

    if not getattr(request, 'is_api_request', False):
        return render(request, 'core/kill_switch.html', {
            'enabled': True,
            'success': True,
            'message': f'Reboot scheduled in {delay_seconds} seconds'
        })
    return JsonResponse({'success': True, 'message': f'Reboot scheduled in {delay_seconds} seconds'})

# CSRF token endpoint for cross-site SPA
@ensure_csrf_cookie
@require_http_methods(["GET", "HEAD", "OPTIONS"])  # Allow preflight
def csrf(request):
    """
    Return a CSRF token in JSON and ensure the CSRF cookie is set.
    Frontend can call this endpoint with credentials to receive the cookie,
    and then send the token back in the X-CSRFToken header on subsequent requests.
    """
    token = get_token(request)
    return JsonResponse({'csrfToken': token})

# Lightweight robots.txt and sitemap.xml to avoid 404s
@require_http_methods(["GET"]) 
def robots_txt(request):
    content = """User-agent: *\nAllow: /\nDisallow: /api/\nSitemap: {base}/sitemap.xml\n""".format(base=request.build_absolute_uri('/').rstrip('/'))
    return HttpResponse(content, content_type="text/plain")

@require_http_methods(["GET"]) 
def sitemap_xml(request):
    base = request.build_absolute_uri('/').rstrip('/')
    content = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>{base}/</loc></url>
  <url><loc>{base}/pricing</loc></url>
  <url><loc>{base}/checkout/subscribe</loc></url>
  <url><loc>{base}/features</loc></url>
  <url><loc>{base}/contact</loc></url>
</urlset>
"""
    return HttpResponse(content, content_type="application/xml")

# Legal content (simple JSON; could be backed by DB or CMS in future)
@require_http_methods(["GET"]) 
def terms_api(request):
    return JsonResponse({
        'title': 'Terms of Service',
        'sections': [
            {'heading': 'Use of Service', 'body': 'Do not misuse the service or attempt to disrupt operations.'},
            {'heading': 'No Financial Advice', 'body': 'Information provided is for educational purposes only and not investment advice.'}
        ]
    })

@require_http_methods(["GET"]) 
def privacy_api(request):
    return JsonResponse({
        'title': 'Privacy Policy',
        'intro': 'How we collect, use, and protect your personal information',
        'sections': [
            {'heading': 'Information We Collect', 'body': 'We collect information you provide directly to us when you create an account, use our services, or contact support.'},
            {'heading': 'How We Use Your Information', 'list': [
                'Provide and maintain our stock analysis services',
                'Personalize your experience and recommendations',
                'Communicate with you about your account and our services',
                'Improve and enhance our platform',
                'Ensure security and prevent fraud']},
            {'heading': 'Data Security', 'body': 'We implement appropriate security measures to protect your personal information.'},
            {'heading': 'Cookies and Tracking', 'body': 'We use cookies and similar technologies to enhance your browsing experience.'}
        ],
        'last_updated': '2025-01-01'
    })
