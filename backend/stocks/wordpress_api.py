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
from django.db.models import Q
from .models import Stock, StockAlert
from news.models import NewsArticle
import json
import logging
from datetime import datetime, timedelta
from django.utils import timezone

logger = logging.getLogger(__name__)
from utils.stock_data import compute_market_cap_fallback
from utils.instrument_classifier import classify_instrument, filter_fields_by_instrument

def format_decimal_safe(value):
    """Safely format decimal values for WordPress"""
    if value is None:
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return 0.0

@csrf_exempt
@require_http_methods(["GET"])
def wordpress_stocks_api(request):
    """
    WordPress-friendly stocks API endpoint
    Returns stock data in a format optimized for WordPress consumption
    """
    try:
        # Get query parameters
        limit = min(int(request.GET.get('limit', 50)), 200)  # Cap at 200 for performance
        page = int(request.GET.get('page', 1))
        sort_by = request.GET.get('sort', 'volume')  # volume, price, change
        search = request.GET.get('search', '')
        category = request.GET.get('category', '')  # gainers, losers, active

        # Base queryset - FIXED to be more inclusive
        # Start with all stocks, then progressively filter
        stocks_queryset = Stock.objects.all()
        
        # Try to prioritize stocks with price data, but don't exclude all others
        preferred_stocks = stocks_queryset.filter(
            current_price__isnull=False,
            current_price__gt=0
        )
        
        # If we have enough stocks with good data, use them
        # Otherwise, include stocks with ANY useful data
        if preferred_stocks.count() >= limit:
            stocks_queryset = preferred_stocks
        else:
            # More inclusive - get stocks with ANY data
            stocks_queryset = stocks_queryset.filter(
                Q(current_price__isnull=False) |
                Q(volume__isnull=False) |
                Q(market_cap__isnull=False)
            )

        # Apply search filter
        if search:
            stocks_queryset = stocks_queryset.filter(
                Q(ticker__icontains=search) | 
                Q(company_name__icontains=search) |
                Q(symbol__icontains=search)
            )

        # Apply category filter
        if category == 'gainers':
            stocks_queryset = stocks_queryset.filter(change_percent__gt=0)
        elif category == 'losers':
            stocks_queryset = stocks_queryset.filter(change_percent__lt=0)
        elif category == 'active':
            stocks_queryset = stocks_queryset.filter(volume__gt=1000000)

        # Apply sorting
        if sort_by == 'price':
            stocks_queryset = stocks_queryset.order_by('-current_price')
        elif sort_by == 'change':
            stocks_queryset = stocks_queryset.order_by('-change_percent')
        elif sort_by == 'market_cap':
            stocks_queryset = stocks_queryset.order_by('-market_cap')
        else:  # default to volume
            stocks_queryset = stocks_queryset.order_by('-volume')

        # Paginate results
        paginator = Paginator(stocks_queryset, limit)
        stocks_page = paginator.get_page(page)

        # Format data for WordPress
        stocks_data = []
        for stock in stocks_page:
            # Calculate additional WordPress-friendly fields
            price_trend = 'neutral'
            if stock.change_percent:
                if stock.change_percent > 0:
                    price_trend = 'up'
                elif stock.change_percent < 0:
                    price_trend = 'down'
            
            # Compute market cap fallback and format
            derived_market_cap = None
            try:
                derived_market_cap = compute_market_cap_fallback(stock.current_price, getattr(stock, 'shares_available', None))
            except Exception:
                derived_market_cap = None
            mc_val = int(stock.market_cap or (derived_market_cap or 0)) if (stock.market_cap or derived_market_cap) else 0
            if mc_val >= 1_000_000_000_000:
                market_cap_formatted = f"${mc_val/1e12:.2f}T"
            elif mc_val >= 1_000_000_000:
                market_cap_formatted = f"${mc_val/1e9:.2f}B"
            elif mc_val >= 1_000_000:
                market_cap_formatted = f"${mc_val/1e6:.2f}M"
            elif mc_val > 0:
                market_cap_formatted = f"${mc_val:,}"
            else:
                market_cap_formatted = 'N/A'
            
            instrument_type = classify_instrument(
                stock.ticker,
                stock.company_name or stock.name,
                getattr(stock, 'name', None)
            )

            stock_data = {
                'ticker': stock.ticker,
                'symbol': stock.symbol or stock.ticker,
                'company_name': stock.company_name or stock.name or stock.ticker,
                'exchange': stock.exchange or 'N/A',
                'instrument_type': instrument_type,
                
                # Price data (with better fallbacks)
                'current_price': format_decimal_safe(stock.current_price) or 0.0,
                'price_change_today': format_decimal_safe(stock.price_change_today) or 0.0,
                'change_percent': format_decimal_safe(stock.change_percent) or 0.0,
                
                # Volume and market data
                'volume': int(stock.volume) if stock.volume else 0,
                'volume_today': int(stock.volume_today or stock.volume or 0),
                'market_cap': mc_val,
                'market_cap_formatted': market_cap_formatted,
                
                # Financial ratios
                'pe_ratio': format_decimal_safe(stock.pe_ratio) or 0.0,
                'dividend_yield': format_decimal_safe(stock.dividend_yield) or 0.0,
                
                # 52-week range
                'week_52_high': format_decimal_safe(stock.week_52_high) or 0.0,
                'week_52_low': format_decimal_safe(stock.week_52_low) or 0.0,
                
                # Timestamps
                'last_updated': stock.last_updated.isoformat() if stock.last_updated else None,
                'created_at': stock.created_at.isoformat() if stock.created_at else None,
                
                # WordPress-friendly display fields
                'trend': price_trend,
                'formatted_price': stock.formatted_price if hasattr(stock, 'formatted_price') else f"${stock.current_price:.2f}" if stock.current_price else "$0.00",
                'formatted_change': stock.formatted_change if hasattr(stock, 'formatted_change') else f"{stock.change_percent:+.2f}%" if stock.change_percent else "0.00%",
                'formatted_volume': stock.formatted_volume if hasattr(stock, 'formatted_volume') else f"{stock.volume:,}" if stock.volume else "0",
                
                # Status indicators
                'is_gaining': (stock.change_percent or 0) > 0,
                'is_losing': (stock.change_percent or 0) < 0,
                'has_volume': bool(stock.volume and stock.volume > 0),
                
                # WordPress URL-friendly
                'slug': stock.ticker.lower(),
                'permalink': f"/stock/{stock.ticker.lower()}/",
                'api_url': f"/api/stocks/{stock.ticker}/"
            }
            
            # Omit non-applicable fields for instrument type
            stocks_data.append(filter_fields_by_instrument(stock_data, instrument_type))

        return JsonResponse({
            'success': True,
            'data': stocks_data,
            'pagination': {
                'current_page': page,
                'total_pages': paginator.num_pages,
                'total_stocks': paginator.count,
                'has_next': stocks_page.has_next(),
                'has_previous': stocks_page.has_previous(),
                'next_page': page + 1 if stocks_page.has_next() else None,
                'previous_page': page - 1 if stocks_page.has_previous() else None
            },
            'meta': {
                'endpoint': 'wordpress_stocks',
                'sort_by': sort_by,
                'search': search,
                'category': category,
                'limit': limit,
                'api_version': '2.0.0',
                'database_status': 'connected',
                'last_update': datetime.now().isoformat()
            }
        })

    except Exception as e:
        logger.error(f"WordPress stocks API error: {e}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': 'Unable to fetch stock data',
            'message': 'Please try again later or contact support',
            'debug_info': str(e) if hasattr(request, 'user') and request.user.is_staff else None
        }, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class WordPressStockView(View):
    """Class-based view for WordPress stock API with real database integration"""
    
    def get(self, request):
        """Handle GET requests for stock data with real database data"""
        try:
            # Get parameters
            limit = min(int(request.GET.get('limit', 20)), 100)
            ticker_filter = request.GET.get('ticker', '')
            featured_only = request.GET.get('featured', 'false').lower() == 'true'
            
            # Build queryset - FIXED to be more inclusive
            queryset = Stock.objects.all()
            
            # Try to prioritize stocks with price data, but don't exclude all others
            preferred_stocks = queryset.filter(
                current_price__isnull=False,
                current_price__gt=0
            )
            
            # If we have enough stocks with good data, use them
            # Otherwise, include stocks with ANY useful data
            if preferred_stocks.count() >= limit:
                queryset = preferred_stocks
            else:
                # More inclusive - get stocks with ANY data
                queryset = queryset.filter(
                    Q(current_price__isnull=False) |
                    Q(volume__isnull=False) |
                    Q(market_cap__isnull=False)
                )
            
            # Filter by ticker if specified
            if ticker_filter:
                tickers = [t.strip().upper() for t in ticker_filter.split(',')]
                queryset = queryset.filter(ticker__in=tickers)
            
            # Get featured stocks (high market cap or volume)
            if featured_only:
                queryset = queryset.filter(
                    Q(market_cap__gte=10000000000) |  # $10B+ market cap
                    Q(volume__gte=5000000)  # 5M+ volume
                )
            
            # Order by market cap for featured stocks
            stocks = queryset.order_by('-market_cap')[:limit]
            
            # Format data
            stocks_data = []
            for stock in stocks:
                stocks_data.append({
                    'ticker': stock.ticker,
                    'company_name': stock.company_name or stock.name,
                    'current_price': format_decimal_safe(stock.current_price),
                    'change_percent': format_decimal_safe(stock.change_percent),
                    'volume': int(stock.volume) if stock.volume else 0,
                    'market_cap': int(stock.market_cap) if stock.market_cap else 0,
                    'pe_ratio': format_decimal_safe(stock.pe_ratio),
                    'trend': 'up' if (stock.change_percent or 0) > 0 else ('down' if (stock.change_percent or 0) < 0 else 'neutral'),
                    'formatted_price': f"${stock.current_price:.2f}" if stock.current_price else "$0.00",
                    'formatted_change': f"{stock.change_percent:+.2f}%" if stock.change_percent else "0.00%",
                    'last_updated': stock.last_updated.isoformat() if stock.last_updated else None
                })

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
                    'api_version': '2.0.0',
                    'database_status': 'connected',
                    'data_source': 'live_database',
                    'featured_only': featured_only,
                    'ticker_filter': ticker_filter
                }
            })
            
        except Exception as e:
            logger.error(f"WordPress stock view error: {e}", exc_info=True)
            return JsonResponse({
                'success': False,
                'error': 'Unable to fetch stock data',
                'message': str(e) if hasattr(request, 'user') and request.user.is_staff else 'Database error'
            }, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class WordPressNewsView(View):
    """Class-based view for WordPress news API with real database integration"""
    
    def get(self, request):
        """Handle GET requests for news data"""
        try:
            # Get parameters
            raw_limit = request.GET.get('limit', '10')
            if isinstance(raw_limit, str) and raw_limit.lower() == 'all':
                # Allow large cap for bulk loads
                limit = 200
            else:
                limit = min(int(raw_limit or 10), 200)
            sentiment_filter = request.GET.get('sentiment', '')  # positive, negative, neutral
            ticker = request.GET.get('ticker', '')
            
            # Build queryset
            news_queryset = NewsArticle.objects.all().order_by('-published_date')
            
            # Filter by sentiment
            if sentiment_filter:
                if sentiment_filter.lower() == 'positive':
                    news_queryset = news_queryset.filter(sentiment_score__gt=0.1)
                elif sentiment_filter.lower() == 'negative':
                    news_queryset = news_queryset.filter(sentiment_score__lt=-0.1)
                elif sentiment_filter.lower() == 'neutral':
                    news_queryset = news_queryset.filter(sentiment_score__gte=-0.1, sentiment_score__lte=0.1)
            
            # Filter by ticker
            if ticker:
                news_queryset = news_queryset.filter(mentioned_tickers__icontains=ticker.upper())
            
            # Get articles
            articles = news_queryset[:limit]
            
            # Format data for WordPress
            news_data = []
            for article in articles:
                # Determine sentiment category
                sentiment_category = 'neutral'
                if article.sentiment_score:
                    if article.sentiment_score > 0.1:
                        sentiment_category = 'positive'
                    elif article.sentiment_score < -0.1:
                        sentiment_category = 'negative'
                
                news_data.append({
                    'id': article.id,
                    'title': article.title,
                    'summary': article.summary,
                    'url': article.url,
                    'source': article.source or (article.news_source.name if article.news_source else 'Unknown'),
                    'sentiment': sentiment_category,
                    'sentiment_score': format_decimal_safe(article.sentiment_score),
                    'sentiment_grade': article.sentiment_grade or 'N/A',
                    'mentioned_tickers': article.mentioned_tickers,
                    'published_at': article.published_date.isoformat() if article.published_date else None,
                    'created_at': article.created_at.isoformat() if article.created_at else None,
                    'excerpt': article.summary[:150] + '...' if article.summary and len(article.summary) > 150 else article.summary
                })

            return JsonResponse({
                'success': True,
                'data': news_data,
                'meta': {
                    'endpoint': 'wordpress_news',
                    'total_articles': len(news_data),
                    'api_version': '2.0.0',
                    'data_source': 'live_database',
                    'sentiment_filter': sentiment_filter,
                    'ticker_filter': ticker,
                    'last_update': datetime.now().isoformat()
                }
            })
            
        except Exception as e:
            logger.error(f"WordPress news view error: {e}", exc_info=True)
            return JsonResponse({
                'success': False,
                'error': 'Unable to fetch news data',
                'message': str(e) if hasattr(request, 'user') and request.user.is_staff else 'Database error'
            }, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class WordPressAlertsView(View):
    """Class-based view for WordPress alerts API with real database integration"""
    
    def get(self, request):
        """Handle GET requests for alerts data"""
        try:
            # Get parameters
            limit = min(int(request.GET.get('limit', 10)), 50)
            active_only = request.GET.get('active', 'true').lower() == 'true'
            ticker = request.GET.get('ticker', '')
            
            # Build queryset
            alerts_queryset = StockAlert.objects.all().order_by('-created_at')
            
            # Filter by active status
            if active_only:
                alerts_queryset = alerts_queryset.filter(is_active=True)
            
            # Filter by ticker
            if ticker:
                alerts_queryset = alerts_queryset.filter(stock__ticker__iexact=ticker)
            
            # Get recent alerts (last 7 days) or triggered alerts
            recent_date = timezone.now() - timedelta(days=7)
            alerts_queryset = alerts_queryset.filter(
                Q(created_at__gte=recent_date) | Q(triggered_at__isnull=False)
            )
            
            # Get alerts
            alerts = alerts_queryset[:limit]
            
            # Format data for WordPress
            alerts_data = []
            for alert in alerts:
                # Determine severity based on alert type and value
                severity = 'medium'
                if alert.alert_type == 'volume_surge':
                    severity = 'high'
                elif alert.alert_type == 'price_change' and alert.target_value and abs(float(alert.target_value)) > 10:
                    severity = 'high'
                
                alerts_data.append({
                    'id': alert.id,
                    'ticker': alert.stock.ticker,
                    'company_name': alert.stock.company_name or alert.stock.name,
                    'alert_type': alert.alert_type,
                    'target_value': format_decimal_safe(alert.target_value),
                    'current_price': format_decimal_safe(alert.stock.current_price),
                    'message': f"{alert.stock.ticker} {alert.get_alert_type_display()}: {alert.target_value}",
                    'severity': severity,
                    'is_active': alert.is_active,
                    'is_triggered': alert.triggered_at is not None,
                    'created_at': alert.created_at.isoformat() if alert.created_at else None,
                    'triggered_at': alert.triggered_at.isoformat() if alert.triggered_at else None,
                    'user_id': alert.user.id if alert.user else None
                })

            return JsonResponse({
                'success': True,
                'data': alerts_data,
                'meta': {
                    'endpoint': 'wordpress_alerts',
                    'total_alerts': len(alerts_data),
                    'api_version': '2.0.0',
                    'data_source': 'live_database',
                    'active_only': active_only,
                    'ticker_filter': ticker,
                    'last_update': datetime.now().isoformat()
                }
            })
            
        except Exception as e:
            logger.error(f"WordPress alerts view error: {e}", exc_info=True)
            return JsonResponse({
                'success': False,
                'error': 'Unable to fetch alerts data',
                'message': str(e) if hasattr(request, 'user') and request.user.is_staff else 'Database error'
            }, status=500)