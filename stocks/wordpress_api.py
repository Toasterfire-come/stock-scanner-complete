"""
WordPress Integration API Views
Provides clean, simple endpoints for WordPress consumption
"""

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.views import View
from django.utils.decorators import method_decorator
from django.core.paginator import Paginator
from .models import Stock
import json
import logging

logger = logging.getLogger(__name__)

@csrf_exempt
@require_http_methods(["GET"])
def wordpress_stocks_api(request):
    """
    WordPress-friendly stocks API endpoint
    Returns stock data in a format optimized for WordPress consumption
    """
    try:
        # Get query parameters
        limit = int(request.GET.get('limit', 50))
        page = int(request.GET.get('page', 1))
        sort_by = request.GET.get('sort', 'volume')  # volume, price, change
        search = request.GET.get('search', '')

        # Base queryset
        stocks_queryset = Stock.objects.all()

        # Apply search filter
        if search:
            stocks_queryset = stocks_queryset.filter(ticker__icontains=search)

        # Apply sorting
        if sort_by == 'price':
            stocks_queryset = stocks_queryset.order_by('-current_price')
        elif sort_by == 'change':
            stocks_queryset = stocks_queryset.order_by('-change_percent')
        else:  # default to volume
            stocks_queryset = stocks_queryset.order_by('-volume')

        # Paginate results
        paginator = Paginator(stocks_queryset, limit)
        stocks_page = paginator.get_page(page)

        # Format data for WordPress
        stocks_data = []
        for stock in stocks_page:
            stocks_data.append({
                'ticker': stock.ticker,
                'company_name': stock.company_name,
                'current_price': float(stock.current_price) if stock.current_price else 0,
                'change_percent': float(stock.change_percent) if stock.change_percent else 0,
                'volume': int(stock.volume) if stock.volume else 0,
                'market_cap': float(stock.market_cap) if stock.market_cap else 0,
                'pe_ratio': float(stock.pe_ratio) if stock.pe_ratio else None,
                'dividend_yield': float(stock.dividend_yield) if stock.dividend_yield else None,
                'last_updated': stock.last_updated.isoformat() if stock.last_updated else None,
                'trend': 'up' if stock.change_percent and stock.change_percent > 0 else 'down',
                'formatted_price': f"${stock.current_price:.2f}" if stock.current_price else "$0.00",
                'formatted_change': f"{stock.change_percent:+.2f}%" if stock.change_percent else "0.00%"
            })

        return JsonResponse({
            'success': True,
            'data': stocks_data,
            'pagination': {
                'current_page': page,
                'total_pages': paginator.num_pages,
                'total_stocks': paginator.count,
                'has_next': stocks_page.has_next(),
                'has_previous': stocks_page.has_previous(),
            },
            'meta': {
                'endpoint': 'wordpress_stocks',
                'sort_by': sort_by,
                'search': search,
                'limit': limit
            }
        })

    except Exception as e:
        logger.error(f"WordPress stocks API error: {e}")
        return JsonResponse({
            'success': False,
            'error': 'Unable to fetch stock data',
            'message': 'Please try again later or contact support'
        }, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class WordPressStockView(View):
    """Class-based view for WordPress stock API"""
    
    def get(self, request):
        """Handle GET requests for stock data"""
        try:
            # Sample stock data for testing
            stocks_data = [
                {
                    'ticker': 'AAPL',
                    'company_name': 'Apple Inc.',
                    'current_price': 175.25,
                    'change_percent': 2.34,
                    'volume': 45678900,
                    'market_cap': 2750000000000,
                    'trend': 'up',
                    'formatted_price': '$175.25',
                    'formatted_change': '+2.34%'
                },
                {
                    'ticker': 'MSFT',
                    'company_name': 'Microsoft Corporation',
                    'current_price': 412.80,
                    'change_percent': -0.87,
                    'volume': 23456780,
                    'market_cap': 3100000000000,
                    'trend': 'down',
                    'formatted_price': '$412.80',
                    'formatted_change': '-0.87%'
                },
                {
                    'ticker': 'GOOGL',
                    'company_name': 'Alphabet Inc.',
                    'current_price': 142.65,
                    'change_percent': 1.56,
                    'volume': 34567890,
                    'market_cap': 1800000000000,
                    'trend': 'up',
                    'formatted_price': '$142.65',
                    'formatted_change': '+1.56%'
                }
            ]

            return JsonResponse({
                'success': True,
                'data': stocks_data,
                'pagination': {
                    'current_page': 1,
                    'total_pages': 1,
                    'total_stocks': len(stocks_data),
                    'has_next': False,
                    'has_previous': False,
                },
                'meta': {
                    'endpoint': 'wordpress_stocks',
                    'api_version': '1.0.0',
                    'database_status': 'connected'
                }
            })
            
        except Exception as e:
            logger.error(f"WordPress stock view error: {e}")
            return JsonResponse({
                'success': False,
                'error': 'Unable to fetch stock data',
                'message': str(e)
            }, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class WordPressNewsView(View):
    """Class-based view for WordPress news API"""
    
    def get(self, request):
        """Handle GET requests for news data"""
        try:
            news_data = [
                {
                    'id': 1,
                    'title': 'Tech Stocks Rally on Strong Earnings',
                    'summary': 'Major technology companies report better-than-expected quarterly results.',
                    'sentiment': 'positive',
                    'score': 0.85,
                    'published_at': '2025-01-25T14:30:00Z',
                    'source': 'MarketWatch'
                },
                {
                    'id': 2,
                    'title': 'Federal Reserve Hints at Rate Stability',
                    'summary': 'Central bank signals potential pause in interest rate adjustments.',
                    'sentiment': 'neutral',
                    'score': 0.12,
                    'published_at': '2025-01-25T12:15:00Z',
                    'source': 'Reuters'
                }
            ]

            return JsonResponse({
                'success': True,
                'data': news_data,
                'meta': {
                    'endpoint': 'wordpress_news',
                    'total_articles': len(news_data),
                    'api_version': '1.0.0'
                }
            })
            
        except Exception as e:
            logger.error(f"WordPress news view error: {e}")
            return JsonResponse({
                'success': False,
                'error': 'Unable to fetch news data',
                'message': str(e)
            }, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class WordPressAlertsView(View):
    """Class-based view for WordPress alerts API"""
    
    def get(self, request):
        """Handle GET requests for alerts data"""
        try:
            alerts_data = [
                {
                    'id': 1,
                    'ticker': 'AAPL',
                    'alert_type': 'price_target',
                    'message': 'AAPL reached target price of $175',
                    'severity': 'medium',
                    'triggered_at': '2025-01-25T15:30:00Z'
                },
                {
                    'id': 2,
                    'ticker': 'TSLA',
                    'alert_type': 'volume_surge',
                    'message': 'TSLA volume 300% above average',
                    'severity': 'high',
                    'triggered_at': '2025-01-25T14:45:00Z'
                }
            ]

            return JsonResponse({
                'success': True,
                'data': alerts_data,
                'meta': {
                    'endpoint': 'wordpress_alerts',
                    'total_alerts': len(alerts_data),
                    'api_version': '1.0.0'
                }
            })
            
        except Exception as e:
            logger.error(f"WordPress alerts view error: {e}")
            return JsonResponse({
                'success': False,
                'error': 'Unable to fetch alerts data',
                'message': str(e)
            }, status=500)