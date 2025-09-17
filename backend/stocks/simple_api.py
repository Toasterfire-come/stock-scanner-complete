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
        """Return real stock data from database with fallback"""
        try:
            # Import here to avoid circular imports
            from .models import Stock
            from django.db.models import Q
            
            # Get recent stocks from database
            stocks = Stock.objects.filter(
                current_price__isnull=False,
                current_price__gt=0
            ).exclude(
                ticker__isnull=True
            ).order_by('-last_updated')[:10]
            
            # If no stocks in database, provide informative message
            if not stocks.exists():
                return JsonResponse({
                    'success': False,
                    'error': 'No stock data available',
                    'message': 'Database is empty. Please run the stock data retrieval script to populate with real data.',
                    'meta': {
                        'endpoint': 'simple_stocks',
                        'total_stocks': 0,
                        'api_version': '1.0.0',
                        'database_required': True,
                        'suggestion': 'Run: python enhanced_stock_retrieval_working.py -test -save-to-db'
                    }
                }, status=200)
            
            # Format real stock data
            stock_data = []
            for stock in stocks:
                stock_data.append({
                    'ticker': stock.ticker,
                    'company_name': stock.company_name or stock.name or stock.ticker,
                    'current_price': float(stock.current_price) if stock.current_price else 0.0,
                    'change_percent': float(stock.change_percent) if stock.change_percent else 0.0,
                    'volume': int(stock.volume) if stock.volume else 0,
                    'market_cap': int(stock.market_cap) if stock.market_cap else 0,
                    'trend': 'up' if (stock.change_percent and stock.change_percent > 0) else 'down',
                    'formatted_price': f"${float(stock.current_price):.2f}" if stock.current_price else "$0.00",
                    'formatted_change': f"{float(stock.change_percent):+.2f}%" if stock.change_percent else "0.00%",
                    'last_updated': stock.last_updated.isoformat() if stock.last_updated else None
                })

            return JsonResponse({
                'success': True,
                'data': stock_data,
                'meta': {
                    'endpoint': 'simple_stocks',
                    'total_stocks': len(stock_data),
                    'api_version': '1.0.0',
                    'database_required': True,
                    'data_source': 'real_time_database'
                }
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': 'Unable to fetch stock data',
                'message': str(e),
                'meta': {
                    'endpoint': 'simple_stocks',
                    'database_required': True
                }
            }, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class SimpleNewsView(View):
    """Simple news API with sample data"""
    
    def get(self, request):
        """Return real news data from database with fallback"""
        try:
            # Import here to avoid dependencies
            from news.models import NewsArticle
            
            # Get recent news from database
            news_articles = NewsArticle.objects.filter(
                is_active=True
            ).order_by('-published_at')[:10]
            
            # If no news in database, provide informative message
            if not news_articles.exists():
                return JsonResponse({
                    'success': False,
                    'error': 'No news data available',
                    'message': 'Database is empty. Please run the news scraper to populate with real news data.',
                    'meta': {
                        'endpoint': 'simple_news',
                        'total_articles': 0,
                        'api_version': '1.0.0',
                        'database_required': True,
                        'suggestion': 'Run: python news_scraper_with_restart.py'
                    }
                }, status=200)
            
            # Format real news data
            news_data = []
            for article in news_articles:
                news_data.append({
                    'id': article.id,
                    'title': article.title,
                    'summary': article.summary or article.content[:200] + '...' if article.content else '',
                    'sentiment': article.sentiment or 'neutral',
                    'score': float(article.sentiment_score) if article.sentiment_score else 0.0,
                    'published_at': article.published_at.isoformat() if article.published_at else None,
                    'source': article.source or 'Unknown',
                    'url': article.url if hasattr(article, 'url') else None,
                    'relevance_score': float(article.relevance_score) if hasattr(article, 'relevance_score') and article.relevance_score else 50.0
                })

            return JsonResponse({
                'success': True,
                'data': news_data,
                'meta': {
                    'endpoint': 'simple_news',
                    'total_articles': len(news_data),
                    'api_version': '1.0.0',
                    'database_required': True,
                    'data_source': 'real_time_database'
                }
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': 'Unable to fetch news data',
                'message': str(e),
                'meta': {
                    'endpoint': 'simple_news',
                    'database_required': True
                }
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