"""
Simple API Views
Provides sample data without requiring database connections
"""

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.views import View
from django.utils.decorators import method_decorator
import json


@method_decorator(csrf_exempt, name='dispatch')
class SimpleStockView(View):
    """Simple stock API with sample data"""
    
    def get(self, request):
        """Return sample stock data"""
        try:
            sample_stocks = [
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
                'data': sample_stocks,
                'meta': {
                    'endpoint': 'simple_stocks',
                    'total_stocks': len(sample_stocks),
                    'api_version': '1.0.0',
                    'database_required': False
                }
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': 'Unable to fetch stock data',
                'message': str(e)
            }, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class SimpleNewsView(View):
    """Simple news API with sample data"""
    
    def get(self, request):
        """Return sample news data"""
        try:
            sample_news = [
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
                'data': sample_news,
                'meta': {
                    'endpoint': 'simple_news',
                    'total_articles': len(sample_news),
                    'api_version': '1.0.0',
                    'database_required': False
                }
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': 'Unable to fetch news data',
                'message': str(e)
            }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def simple_status_api(request):
    """Simple status API that works without database"""
    try:
        response_data = {
            'success': True,
            'status': 'operational',
            'data': {
                'api_status': 'online',
                'database_status': 'not_required',
                'sample_mode': True,
                'endpoints_available': [
                    '/api/simple/stocks/',
                    '/api/simple/news/',
                    '/api/wordpress/stocks/',
                    '/api/wordpress/news/',
                    '/api/wordpress/alerts/'
                ]
            },
            'meta': {
                'api_version': '1.0.0',
                'database_required': False
            }
        }

        return JsonResponse(response_data)

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': 'API Error',
            'message': str(e)
        }, status=500)