import json
import subprocess
import logging
from datetime import datetime, timedelta
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.management import call_command
from django.utils.decorators import method_decorator
from django.views import View
from django.utils import timezone
from stocks.models import StockAlert
from emails.models import EmailSubscription
import io
import sys
import schedule

logger = logging.getLogger(__name__)

@require_http_methods(["GET"])
def admin_status(request):
    """Get comprehensive system status for admin dashboard"""
    try:
        # Get database statistics
        total_stocks = StockAlert.objects.count()
        unsent_notifications = StockAlert.objects.filter(sent=False).count()
        
        # Get latest update
        latest_stock = StockAlert.objects.filter(last_update__isnull=False).order_by('-last_update').first()
        last_update = latest_stock.last_update.strftime('%Y-%m-%d %H:%M') if latest_stock else None
        
        # Calculate success rate (placeholder - could be enhanced with actual metrics)
        success_rate = 95 if total_stocks > 0 else 0
        
        # Get subscription count
        total_subscriptions = EmailSubscription.objects.filter(is_active=True).count()
        
        # Get news statistics
        try:
            from news.models import NewsArticle
            total_news = NewsArticle.objects.filter(is_active=True).count()
            recent_news = NewsArticle.objects.filter(
                published_date__gte=timezone.now() - timedelta(hours=24),
                is_active=True
            ).count()
        except Exception:
            total_news = 0
            recent_news = 0
        
        # Get scheduler information
        scheduler_jobs = len(schedule.jobs)
        next_run = None
        if schedule.jobs:
            next_job = min(schedule.jobs, key=lambda x: x.next_run)
            next_run = next_job.next_run.strftime('%Y-%m-%d %H:%M:%S') if next_job.next_run else None
        
        # System health checks
        system_health = {
            'database': 'healthy' if total_stocks > 0 else 'warning',
            'news_scraper': 'healthy' if recent_news > 0 else 'warning',
            'email_system': 'healthy' if total_subscriptions > 0 else 'info',
            'scheduler': 'healthy' if scheduler_jobs > 0 else 'warning'
        }
        
        return JsonResponse({
            'total_stocks': total_stocks,
            'unsent_notifications': unsent_notifications,
            'success_rate': success_rate,
            'last_update': last_update,
            'total_subscriptions': total_subscriptions,
            'total_news': total_news,
            'recent_news': recent_news,
            'scheduler_jobs': scheduler_jobs,
            'next_scheduled_run': next_run,
            'system_health': system_health,
            'status': 'success'
        })
        
    except Exception as e:
        logger.error(f"Error getting admin status: {e}")
        return JsonResponse({
            'total_stocks': 0,
            'unsent_notifications': 0,
            'success_rate': 0,
            'last_update': None,
            'total_subscriptions': 0,
            'total_news': 0,
            'recent_news': 0,
            'scheduler_jobs': 0,
            'next_scheduled_run': None,
            'system_health': {'database': 'error', 'news_scraper': 'error', 'email_system': 'error', 'scheduler': 'error'},
            'error': str(e),
            'status': 'error'
        }, status=500)

@require_http_methods(["GET"])
def recent_news(request):
    """Get recent news articles for the admin dashboard"""
    try:
        from news.models import NewsArticle
        
        # Get recent articles (last 7 days, limit 10)
        articles = NewsArticle.objects.filter(
            is_active=True,
            published_date__gte=timezone.now() - timedelta(days=7)
        ).order_by('-published_date')[:10]
        
        article_data = []
        for article in articles:
            article_data.append({
                'headline': article.headline,
                'url': article.url,
                'sentiment_grade': article.sentiment_grade,
                'sentiment_score': article.sentiment_score,
                'published_date': article.published_date.strftime('%Y-%m-%d %H:%M'),
                'mentioned_tickers': article.mentioned_tickers,
                'source': article.source
            })
        
        return JsonResponse({
            'articles': article_data,
            'count': len(article_data),
            'status': 'success'
        })
        
    except Exception as e:
        logger.error(f"Error getting recent news: {e}")
        return JsonResponse({
            'articles': [],
            'count': 0,
            'error': str(e),
            'status': 'error'
        }, status=500)

@require_http_methods(["POST"])
@csrf_exempt
def load_nasdaq_data(request):
    """Load NASDAQ ticker data"""
    try:
        # Capture command output
        output = io.StringIO()
        call_command('load_nasdaq_only', stdout=output)
        result = output.getvalue()
        
        return JsonResponse({
            'message': 'NASDAQ data loaded successfully',
            'output': result,
            'status': 'success'
        })
        
    except Exception as e:
        logger.error(f"Error loading NASDAQ data: {e}")
        return JsonResponse({
            'message': f'Failed to load NASDAQ data: {str(e)}',
            'status': 'error'
        }, status=500)

@require_http_methods(["POST"])
@csrf_exempt
def update_stocks(request):
    """Update stock data using yfinance"""
    try:
        # Capture command output
        output = io.StringIO()
        call_command('update_stocks_yfinance', stdout=output)
        result = output.getvalue()
        
        return JsonResponse({
            'message': 'Stock data updated successfully',
            'output': result,
            'status': 'success'
        })
        
    except Exception as e:
        logger.error(f"Error updating stocks: {e}")
        return JsonResponse({
            'message': f'Failed to update stocks: {str(e)}',
            'status': 'error'
        }, status=500)

@require_http_methods(["POST"])
@csrf_exempt
def scrape_news(request):
    """Scrape news data"""
    try:
        from news.scraper import update_news_data
        
        success = update_news_data()
        
        if success:
            return JsonResponse({
                'message': 'News data scraped successfully',
                'status': 'success'
            })
        else:
            return JsonResponse({
                'message': 'News scraping completed with warnings',
                'status': 'warning'
            })
        
    except Exception as e:
        logger.error(f"Error scraping news: {e}")
        return JsonResponse({
            'message': f'Failed to scrape news: {str(e)}',
            'status': 'error'
        }, status=500)

@require_http_methods(["POST"])
@csrf_exempt
def send_notifications(request):
    """Send pending notifications"""
    try:
        # Capture command output
        output = io.StringIO()
        call_command('send_stock_notifications', stdout=output)
        result = output.getvalue()
        
        return JsonResponse({
            'message': 'Notifications sent successfully',
            'output': result,
            'status': 'success'
        })
        
    except Exception as e:
        logger.error(f"Error sending notifications: {e}")
        return JsonResponse({
            'message': f'Failed to send notifications: {str(e)}',
            'status': 'error'
        }, status=500)

@require_http_methods(["POST"])
@csrf_exempt
def optimize_database(request):
    """Optimize database performance"""
    try:
        # Capture command output
        output = io.StringIO()
        call_command('optimize_database', stdout=output)
        result = output.getvalue()
        
        return JsonResponse({
            'message': 'Database optimized successfully',
            'output': result,
            'status': 'success'
        })
        
    except Exception as e:
        logger.error(f"Error optimizing database: {e}")
        return JsonResponse({
            'message': f'Failed to optimize database: {str(e)}',
            'status': 'error'
        }, status=500)

@require_http_methods(["GET"])
def api_providers_status(request):
    """Get API providers status - Simplified for Yahoo Finance"""
    try:
        # Test Yahoo Finance connection
        import yfinance as yf
        
        # Test with a simple ticker
        test_ticker = yf.Ticker("AAPL")
        test_data = test_ticker.history(period="1d")
        yahoo_status = 'active' if len(test_data) > 0 else 'inactive'
        
        providers = {
            'yahoo_finance': {
                'status': yahoo_status,
                'description': 'Yahoo Finance (Primary - Free)',
                'last_test': timezone.now().strftime('%Y-%m-%d %H:%M:%S'),
                'rate_limit': 'No official limit'
            },
            'news_scraper': {
                'status': 'active',
                'description': 'Yahoo Finance News Scraper',
                'last_update': timezone.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        }
        
        return JsonResponse(providers)
    except Exception as e:
        logger.error(f"Error getting API providers status: {e}")
        return JsonResponse({
            'yahoo_finance': {
                'status': 'error',
                'description': 'Yahoo Finance (Primary - Free)',
                'error': str(e)
            }
        }, status=500)

@require_http_methods(["POST"])
@csrf_exempt
def update_nasdaq_now(request):
    """Manually trigger NASDAQ data update (same as scheduled updates)"""
    try:
        # Capture command output
        output = io.StringIO()
        call_command('update_nasdaq_now', stdout=output)
        result = output.getvalue()
        
        return JsonResponse({
            'message': 'NASDAQ data updated successfully',
            'output': result,
            'status': 'success'
        })
        
    except Exception as e:
        logger.error(f"Error updating NASDAQ data: {e}")
        return JsonResponse({
            'message': f'Failed to update NASDAQ data: {str(e)}',
            'status': 'error'
        }, status=500)

# WordPress Integration Endpoints
@require_http_methods(["GET"])
def wordpress_stock_data(request):
    """Get stock data formatted for WordPress consumption"""
    try:
        # Get recent stock alerts
        stocks = StockAlert.objects.filter(
            current_price__gt=0
        ).order_by('-last_update')[:50]
        
        stock_data = []
        for stock in stocks:
            stock_data.append({
                'ticker': stock.ticker,
                'company_name': stock.company_name,
                'current_price': float(stock.current_price) if stock.current_price else 0,
                'price_change': float(stock.price_change_today) if stock.price_change_today else 0,
                'price_change_percent': float(stock.price_change_percent) if stock.price_change_percent else 0,
                'volume': int(stock.volume_today) if stock.volume_today else 0,
                'market_cap': int(stock.market_cap) if stock.market_cap else 0,
                'last_update': stock.last_update.isoformat() if stock.last_update else None
            })
        
        return JsonResponse({
            'stocks': stock_data,
            'count': len(stock_data),
            'last_updated': timezone.now().isoformat(),
            'status': 'success'
        })
        
    except Exception as e:
        logger.error(f"Error getting WordPress stock data: {e}")
        return JsonResponse({
            'stocks': [],
            'count': 0,
            'error': str(e),
            'status': 'error'
        }, status=500)

@require_http_methods(["GET"])
def wordpress_news_data(request):
    """Get news data formatted for WordPress consumption"""
    try:
        from news.models import NewsArticle
        
        # Get recent news
        articles = NewsArticle.objects.filter(
            is_active=True
        ).order_by('-published_date')[:20]
        
        news_data = []
        for article in articles:
            news_data.append({
                'headline': article.headline,
                'url': article.url,
                'content': article.content[:200] + '...' if len(article.content) > 200 else article.content,
                'sentiment_grade': article.sentiment_grade,
                'sentiment_score': article.sentiment_score,
                'published_date': article.published_date.isoformat(),
                'mentioned_tickers': article.mentioned_tickers,
                'source': article.source,
                'is_market_relevant': article.is_market_relevant
            })
        
        return JsonResponse({
            'articles': news_data,
            'count': len(news_data),
            'last_updated': timezone.now().isoformat(),
            'status': 'success'
        })
        
    except Exception as e:
        logger.error(f"Error getting WordPress news data: {e}")
        return JsonResponse({
            'articles': [],
            'count': 0,
            'error': str(e),
            'status': 'error'
        }, status=500)