"""
Simple API endpoints for WordPress integration
These endpoints work without database dependencies for testing
"""

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
import json

@csrf_exempt
@require_http_methods(["GET"])
def simple_status_api(request):
    """
    Simple status API that works without database
    """
    try:
        response_data = {
            'success': True,
            'status': 'operational',
            'data': {
                'api_status': 'online',
                'server_time': timezone.now().isoformat(),
                'django_version': '4.2+',
                'api_version': '1.0',
                'wordpress_compatible': True,
                'message': 'Stock Scanner API is running successfully'
            },
            'endpoints': {
                'stocks': '/api/wordpress/stocks/',
                'news': '/api/wordpress/news/', 
                'status': '/api/wordpress/status/',
                'stock_detail': '/api/wordpress/stocks/{ticker}/'
            }
        }
        
        return JsonResponse(response_data)
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': 'API Error',
            'message': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def simple_stocks_api(request):
    """
    Simple stocks API with sample data for testing
    """
    try:
        # Sample stock data for testing
        sample_stocks = [
            {
                'ticker': 'AAPL',
                'company_name': 'Apple Inc.',
                'current_price': 175.43,
                'price_change': 2.15,
                'price_change_percent': 1.24,
                'volume': 52847392,
                'market_cap': 2789234567890,
                'pe_ratio': 28.5,
                'formatted_price': '$175.43',
                'formatted_change': '+1.24%',
                'formatted_volume': '52,847,392',
                'last_updated': timezone.now().isoformat()
            },
            {
                'ticker': 'MSFT',
                'company_name': 'Microsoft Corporation',
                'current_price': 338.11,
                'price_change': -1.52,
                'price_change_percent': -0.45,
                'volume': 28394857,
                'market_cap': 2512847392847,
                'pe_ratio': 31.2,
                'formatted_price': '$338.11',
                'formatted_change': '-0.45%',
                'formatted_volume': '28,394,857',
                'last_updated': timezone.now().isoformat()
            },
            {
                'ticker': 'GOOGL',
                'company_name': 'Alphabet Inc.',
                'current_price': 138.21,
                'price_change': 0.87,
                'price_change_percent': 0.63,
                'volume': 19284756,
                'market_cap': 1758293847563,
                'pe_ratio': 25.8,
                'formatted_price': '$138.21',
                'formatted_change': '+0.63%',
                'formatted_volume': '19,284,756',
                'last_updated': timezone.now().isoformat()
            },
            {
                'ticker': 'TSLA',
                'company_name': 'Tesla, Inc.',
                'current_price': 242.64,
                'price_change': 8.42,
                'price_change_percent': 3.59,
                'volume': 45827394,
                'market_cap': 769384756293,
                'pe_ratio': 65.4,
                'formatted_price': '$242.64',
                'formatted_change': '+3.59%',
                'formatted_volume': '45,827,394',
                'last_updated': timezone.now().isoformat()
            },
            {
                'ticker': 'NVDA',
                'company_name': 'NVIDIA Corporation',
                'current_price': 875.28,
                'price_change': 12.35,
                'price_change_percent': 1.43,
                'volume': 31847293,
                'market_cap': 2164857392847,
                'pe_ratio': 58.7,
                'formatted_price': '$875.28',
                'formatted_change': '+1.43%',
                'formatted_volume': '31,847,293',
                'last_updated': timezone.now().isoformat()
            }
        ]
        
        # Apply filters from request
        limit = int(request.GET.get('limit', 50))
        search = request.GET.get('search', '')
        
        # Filter by search if provided
        if search:
            sample_stocks = [s for s in sample_stocks if search.upper() in s['ticker'] or search.lower() in s['company_name'].lower()]
        
        # Limit results
        sample_stocks = sample_stocks[:limit]
        
        response_data = {
            'success': True,
            'data': sample_stocks,
            'pagination': {
                'current_page': 1,
                'total_pages': 1,
                'total_stocks': len(sample_stocks),
                'has_next': False,
                'has_previous': False,
            },
            'meta': {
                'search': search,
                'limit': limit,
                'api_version': '1.0',
                'note': 'This is sample data for testing. Connect to real database for live data.'
            }
        }
        
        return JsonResponse(response_data)
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': 'Unable to fetch stock data',
            'message': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def simple_news_api(request):
    """
    Simple news API with sample data for testing
    """
    try:
        # Sample news data for testing
        sample_news = [
            {
                'id': 1,
                'title': 'Apple Reports Strong Q4 Earnings Beat Expectations',
                'summary': 'Apple Inc. reported quarterly earnings that exceeded analyst expectations, driven by strong iPhone sales and services revenue growth.',
                'url': 'https://example.com/apple-earnings',
                'source': 'Financial News',
                'published_date': timezone.now().isoformat(),
                'sentiment_score': 0.8,
                'sentiment_grade': 'A',
                'mentioned_tickers': ['AAPL'],
                'formatted_date': timezone.now().strftime('%B %d, %Y'),
                'sentiment_color': 'green'
            },
            {
                'id': 2,
                'title': 'Tesla Announces New Gigafactory Location',
                'summary': 'Tesla revealed plans for a new Gigafactory that will focus on battery production and vehicle assembly for the European market.',
                'url': 'https://example.com/tesla-gigafactory',
                'source': 'Tech Today',
                'published_date': timezone.now().isoformat(),
                'sentiment_score': 0.6,
                'sentiment_grade': 'B',
                'mentioned_tickers': ['TSLA'],
                'formatted_date': timezone.now().strftime('%B %d, %Y'),
                'sentiment_color': 'lightgreen'
            },
            {
                'id': 3,
                'title': 'Market Volatility Continues Amid Economic Uncertainty',
                'summary': 'Stock markets showed mixed signals today as investors weigh economic indicators and Federal Reserve policy decisions.',
                'url': 'https://example.com/market-volatility',
                'source': 'Market Watch',
                'published_date': timezone.now().isoformat(),
                'sentiment_score': -0.2,
                'sentiment_grade': 'C',
                'mentioned_tickers': ['SPY', 'QQQ'],
                'formatted_date': timezone.now().strftime('%B %d, %Y'),
                'sentiment_color': 'yellow'
            }
        ]
        
        # Apply filters
        limit = int(request.GET.get('limit', 20))
        sentiment = request.GET.get('sentiment', '')
        ticker = request.GET.get('ticker', '')
        
        # Filter by sentiment if provided
        if sentiment:
            sample_news = [n for n in sample_news if n['sentiment_grade'] == sentiment.upper()]
        
        # Filter by ticker if provided
        if ticker:
            sample_news = [n for n in sample_news if ticker.upper() in n['mentioned_tickers']]
        
        # Limit results
        sample_news = sample_news[:limit]
        
        response_data = {
            'success': True,
            'data': sample_news,
            'pagination': {
                'current_page': 1,
                'total_pages': 1,
                'total_articles': len(sample_news),
                'has_next': False,
                'has_previous': False,
            },
            'meta': {
                'sentiment_filter': sentiment,
                'ticker_filter': ticker,
                'limit': limit,
                'api_version': '1.0',
                'note': 'This is sample data for testing. Connect to real database for live data.'
            }
        }
        
        return JsonResponse(response_data)
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': 'Unable to fetch news data',
            'message': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def simple_stock_detail_api(request, ticker):
    """
    Simple stock detail API with sample data
    """
    try:
        # Sample stock details
        stock_details = {
            'AAPL': {
                'ticker': 'AAPL',
                'company_name': 'Apple Inc.',
                'current_price': 175.43,
                'price_change': 2.15,
                'price_change_percent': 1.24,
                'volume': 52847392,
                'market_cap': 2789234567890,
                'pe_ratio': 28.5,
                'formatted_price': '$175.43',
                'formatted_change': '+1.24%',
                'formatted_volume': '52,847,392',
                'formatted_market_cap': '$2.79T'
            },
            'MSFT': {
                'ticker': 'MSFT',
                'company_name': 'Microsoft Corporation',
                'current_price': 338.11,
                'price_change': -1.52,
                'price_change_percent': -0.45,
                'volume': 28394857,
                'market_cap': 2512847392847,
                'pe_ratio': 31.2,
                'formatted_price': '$338.11',
                'formatted_change': '-0.45%',
                'formatted_volume': '28,394,857',
                'formatted_market_cap': '$2.51T'
            }
        }
        
        ticker_upper = ticker.upper()
        if ticker_upper in stock_details:
            stock_data = stock_details[ticker_upper]
            stock_data['last_updated'] = timezone.now().isoformat()
            
            response_data = {
                'success': True,
                'data': stock_data,
                'meta': {
                    'api_version': '1.0',
                    'note': 'This is sample data for testing. Connect to real database for live data.'
                }
            }
            
            return JsonResponse(response_data)
        else:
            return JsonResponse({
                'success': False,
                'error': 'Stock not found',
                'message': f'No sample data available for ticker {ticker}. Try AAPL or MSFT.'
            }, status=404)
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': 'Unable to fetch stock details',
            'message': str(e)
        }, status=500)