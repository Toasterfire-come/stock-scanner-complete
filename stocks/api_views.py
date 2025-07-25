"""
Django REST API Views for Stock Data Integration
Provides comprehensive real-time stock data endpoints with full filtering capabilities
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.cache import cache
from django.db.models import Q, F
from django.utils import timezone
from datetime import datetime, timedelta
import json
import logging
from decimal import Decimal

from .models import Stock, StockAlert, StockPrice
from emails.models import EmailSubscription
import yfinance as yf
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

def format_decimal_safe(value):
    """Safely format decimal values"""
    if value is None:
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None

def calculate_change_percent(current_price, price_change):
    """Calculate percentage change"""
    if not current_price or not price_change:
        return 0.0
    try:
        return float((price_change / (current_price - price_change)) * 100)
    except (ZeroDivisionError, TypeError):
        return 0.0

@api_view(['GET'])
@permission_classes([AllowAny])
def stock_list_api(request):
    """
    Get comprehensive list of stocks with full data and filtering

    URL: /api/stocks/
    Parameters:
    - limit: Number of stocks to return (default: 50, max: 1000)
    - search: Search by ticker or company name
    - category: Filter by category (gainers, losers, high_volume, large_cap, small_cap)
    - min_price: Minimum price filter
    - max_price: Maximum price filter
    - min_volume: Minimum volume filter
    - min_market_cap: Minimum market cap filter
    - max_market_cap: Maximum market cap filter
    - min_pe: Minimum P/E ratio
    - max_pe: Maximum P/E ratio
    - exchange: Filter by exchange (default: NASDAQ)
    - sort_by: Sort field (price, volume, market_cap, change_percent, pe_ratio)
    - sort_order: Sort order (asc, desc) default: desc
    """
    try:
        # Parse parameters
        limit = min(int(request.GET.get('limit', 50)), 1000)
        search = request.GET.get('search', '').strip()
        category = request.GET.get('category', '').strip()
        
        # Price filters
        min_price = request.GET.get('min_price')
        max_price = request.GET.get('max_price')
        
        # Volume filters
        min_volume = request.GET.get('min_volume')
        
        # Market cap filters
        min_market_cap = request.GET.get('min_market_cap')
        max_market_cap = request.GET.get('max_market_cap')
        
        # P/E ratio filters
        min_pe = request.GET.get('min_pe')
        max_pe = request.GET.get('max_pe')
        
        # Exchange filter
        exchange = request.GET.get('exchange', 'NASDAQ')
        
        # Sorting
        sort_by = request.GET.get('sort_by', 'last_updated')
        sort_order = request.GET.get('sort_order', 'desc')
        
        # Base queryset
        queryset = Stock.objects.filter(exchange__iexact=exchange)

        # Apply search filter
        if search:
            queryset = queryset.filter(
                Q(ticker__icontains=search) | 
                Q(company_name__icontains=search) |
                Q(symbol__icontains=search) |
                Q(name__icontains=search)
            )

        # Apply price filters
        if min_price:
            try:
                queryset = queryset.filter(current_price__gte=Decimal(min_price))
            except (ValueError, TypeError):
                pass
                
        if max_price:
            try:
                queryset = queryset.filter(current_price__lte=Decimal(max_price))
            except (ValueError, TypeError):
                pass

        # Apply volume filters
        if min_volume:
            try:
                queryset = queryset.filter(volume__gte=int(min_volume))
            except (ValueError, TypeError):
                pass

        # Apply market cap filters
        if min_market_cap:
            try:
                queryset = queryset.filter(market_cap__gte=int(min_market_cap))
            except (ValueError, TypeError):
                pass
                
        if max_market_cap:
            try:
                queryset = queryset.filter(market_cap__lte=int(max_market_cap))
            except (ValueError, TypeError):
                pass

        # Apply P/E ratio filters
        if min_pe:
            try:
                queryset = queryset.filter(pe_ratio__gte=Decimal(min_pe))
            except (ValueError, TypeError):
                pass
                
        if max_pe:
            try:
                queryset = queryset.filter(pe_ratio__lte=Decimal(max_pe))
            except (ValueError, TypeError):
                pass

        # Apply category filters
        if category == 'gainers':
            queryset = queryset.filter(price_change_today__gt=0)
        elif category == 'losers':
            queryset = queryset.filter(price_change_today__lt=0)
        elif category == 'high_volume':
            queryset = queryset.filter(volume__isnull=False).exclude(volume=0)
        elif category == 'large_cap':
            queryset = queryset.filter(market_cap__gte=10000000000)  # $10B+
        elif category == 'small_cap':
            queryset = queryset.filter(market_cap__lt=2000000000, market_cap__gt=0)  # < $2B

        # Apply sorting
        sort_field = sort_by
        if sort_order == 'desc':
            sort_field = f'-{sort_by}'
            
        # Handle special sorting cases
        if sort_by == 'change_percent':
            if sort_order == 'desc':
                queryset = queryset.order_by('-change_percent')
            else:
                queryset = queryset.order_by('change_percent')
        else:
            try:
                queryset = queryset.order_by(sort_field)
            except:
                queryset = queryset.order_by('-last_updated')

        # Limit results
        stocks = queryset[:limit]

        # Format comprehensive data
        stock_data = []
        for stock in stocks:
            change_percent = calculate_change_percent(stock.current_price, stock.price_change_today)
            
            stock_data.append({
                # Basic info
                'ticker': stock.ticker,
                'symbol': stock.symbol or stock.ticker,
                'company_name': stock.company_name or stock.name,
                'name': stock.name or stock.company_name,
                'exchange': stock.exchange,
                
                # Price data
                'current_price': format_decimal_safe(stock.current_price),
                'price_change_today': format_decimal_safe(stock.price_change_today),
                'price_change_week': format_decimal_safe(stock.price_change_week),
                'price_change_month': format_decimal_safe(stock.price_change_month),
                'price_change_year': format_decimal_safe(stock.price_change_year),
                'change_percent': format_decimal_safe(stock.change_percent) or change_percent,
                
                # Bid/Ask and Range
                'bid_price': format_decimal_safe(stock.bid_price),
                'ask_price': format_decimal_safe(stock.ask_price),
                'bid_ask_spread': stock.bid_ask_spread,
                'days_range': stock.days_range,
                'days_low': format_decimal_safe(stock.days_low),
                'days_high': format_decimal_safe(stock.days_high),
                
                # Volume data
                'volume': stock.volume,
                'volume_today': stock.volume_today or stock.volume,
                'avg_volume_3mon': stock.avg_volume_3mon,
                'dvav': format_decimal_safe(stock.dvav),
                'shares_available': stock.shares_available,
                
                # Market data
                'market_cap': stock.market_cap,
                'market_cap_change_3mon': format_decimal_safe(stock.market_cap_change_3mon),
                'formatted_market_cap': stock.formatted_market_cap,
                
                # Financial ratios
                'pe_ratio': format_decimal_safe(stock.pe_ratio),
                'pe_change_3mon': format_decimal_safe(stock.pe_change_3mon),
                'dividend_yield': format_decimal_safe(stock.dividend_yield),
                
                # 52-week range
                'week_52_low': format_decimal_safe(stock.week_52_low),
                'week_52_high': format_decimal_safe(stock.week_52_high),
                
                # Additional metrics
                'one_year_target': format_decimal_safe(stock.one_year_target),
                'earnings_per_share': format_decimal_safe(stock.earnings_per_share),
                'book_value': format_decimal_safe(stock.book_value),
                'price_to_book': format_decimal_safe(stock.price_to_book),
                
                # Formatted values
                'formatted_price': stock.formatted_price,
                'formatted_change': stock.formatted_change,
                'formatted_volume': stock.formatted_volume,
                
                # Timestamps
                'last_updated': stock.last_updated.isoformat() if stock.last_updated else None,
                'created_at': stock.created_at.isoformat() if stock.created_at else None,
                
                # Calculated fields
                'is_gaining': (stock.price_change_today or 0) > 0,
                'is_losing': (stock.price_change_today or 0) < 0,
                'volume_ratio': format_decimal_safe(stock.dvav),
                
                # WordPress integration
                'wordpress_url': f"/stock/{stock.ticker.lower()}/"
            })

        return Response({
            'success': True,
            'count': len(stock_data),
            'total_available': queryset.count() if len(stock_data) < limit else len(stock_data),
            'filters_applied': {
                'search': search,
                'category': category,
                'min_price': min_price,
                'max_price': max_price,
                'min_volume': min_volume,
                'min_market_cap': min_market_cap,
                'max_market_cap': max_market_cap,
                'min_pe': min_pe,
                'max_pe': max_pe,
                'exchange': exchange,
                'sort_by': sort_by,
                'sort_order': sort_order
            },
            'data': stock_data,
            'timestamp': timezone.now().isoformat()
        })

    except Exception as e:
        logger.error(f"Error in stock_list_api: {e}", exc_info=True)
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
def stock_detail_api(request, ticker):
    """
    Get comprehensive detailed information for a specific stock

    URL: /api/stocks/{ticker}/
    Returns: Full stock data with real-time information
    """
    try:
        ticker = ticker.upper()

        # Get stock from database
        try:
            stock = Stock.objects.get(Q(ticker=ticker) | Q(symbol=ticker))
        except Stock.DoesNotExist:
            return Response({
                'success': False,
                'error': f'Stock {ticker} not found',
                'available_endpoints': [
                    '/api/stocks/',
                    '/api/stocks/search/',
                    '/api/stocks/nasdaq/'
                ]
            }, status=status.HTTP_404_NOT_FOUND)

        # Calculate additional metrics
        change_percent = calculate_change_percent(stock.current_price, stock.price_change_today)
        
        # Get recent price history if available
        recent_prices = StockPrice.objects.filter(
            stock=stock
        ).order_by('-timestamp')[:10]
        
        price_history = []
        for price_record in recent_prices:
            price_history.append({
                'price': format_decimal_safe(price_record.price),
                'timestamp': price_record.timestamp.isoformat()
            })

        # Format comprehensive detailed data
        stock_data = {
            # Basic identification
            'ticker': stock.ticker,
            'symbol': stock.symbol or stock.ticker,
            'company_name': stock.company_name or stock.name,
            'name': stock.name or stock.company_name,
            'exchange': stock.exchange,
            
            # Current price data
            'current_price': format_decimal_safe(stock.current_price),
            'price_change_today': format_decimal_safe(stock.price_change_today),
            'price_change_week': format_decimal_safe(stock.price_change_week),
            'price_change_month': format_decimal_safe(stock.price_change_month),
            'price_change_year': format_decimal_safe(stock.price_change_year),
            'change_percent': format_decimal_safe(stock.change_percent) or change_percent,
            
            # Bid/Ask and daily range
            'bid_price': format_decimal_safe(stock.bid_price),
            'ask_price': format_decimal_safe(stock.ask_price),
            'bid_ask_spread': stock.bid_ask_spread,
            'days_range': stock.days_range,
            'days_low': format_decimal_safe(stock.days_low),
            'days_high': format_decimal_safe(stock.days_high),
            
            # Volume information
            'volume': stock.volume,
            'volume_today': stock.volume_today or stock.volume,
            'avg_volume_3mon': stock.avg_volume_3mon,
            'dvav': format_decimal_safe(stock.dvav),
            'shares_available': stock.shares_available,
            
            # Market capitalization
            'market_cap': stock.market_cap,
            'market_cap_change_3mon': format_decimal_safe(stock.market_cap_change_3mon),
            'formatted_market_cap': stock.formatted_market_cap,
            
            # Financial ratios and metrics
            'pe_ratio': format_decimal_safe(stock.pe_ratio),
            'pe_change_3mon': format_decimal_safe(stock.pe_change_3mon),
            'dividend_yield': format_decimal_safe(stock.dividend_yield),
            'earnings_per_share': format_decimal_safe(stock.earnings_per_share),
            'book_value': format_decimal_safe(stock.book_value),
            'price_to_book': format_decimal_safe(stock.price_to_book),
            
            # 52-week performance
            'week_52_low': format_decimal_safe(stock.week_52_low),
            'week_52_high': format_decimal_safe(stock.week_52_high),
            
            # Targets and predictions
            'one_year_target': format_decimal_safe(stock.one_year_target),
            
            # Formatted display values
            'formatted_price': stock.formatted_price,
            'formatted_change': stock.formatted_change,
            'formatted_volume': stock.formatted_volume,
            
            # Timestamps
            'last_updated': stock.last_updated.isoformat() if stock.last_updated else None,
            'created_at': stock.created_at.isoformat() if stock.created_at else None,
            
            # Calculated indicators
            'is_gaining': (stock.price_change_today or 0) > 0,
            'is_losing': (stock.price_change_today or 0) < 0,
            'volume_above_average': stock.dvav and stock.dvav > 1,
            'price_near_52_week_high': False,
            'price_near_52_week_low': False,
            
            # Recent price history
            'price_history': price_history,
            'price_history_count': len(price_history),
            
            # Additional metadata
            'data_quality': {
                'has_price': stock.current_price is not None,
                'has_volume': stock.volume is not None,
                'has_market_cap': stock.market_cap is not None,
                'has_pe_ratio': stock.pe_ratio is not None,
                'last_update_age_minutes': (
                    (timezone.now() - stock.last_updated).total_seconds() / 60
                    if stock.last_updated else None
                )
            }
        }
        
        # Calculate price position indicators
        if stock.current_price and stock.week_52_high and stock.week_52_low:
            current = float(stock.current_price)
            high_52 = float(stock.week_52_high)
            low_52 = float(stock.week_52_low)
            
            stock_data['price_near_52_week_high'] = current >= (high_52 * 0.95)
            stock_data['price_near_52_week_low'] = current <= (low_52 * 1.05)
            stock_data['price_position_52_week'] = ((current - low_52) / (high_52 - low_52)) * 100 if high_52 != low_52 else 0

        return Response({
            'success': True,
            'data': stock_data,
            'timestamp': timezone.now().isoformat()
        })

    except Exception as e:
        logger.error(f"Error in stock_detail_api for {ticker}: {e}", exc_info=True)
        return Response({
            'success': False,
            'error': str(e),
            'ticker': ticker
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
def nasdaq_stocks_api(request):
    """
    Get all NASDAQ-listed stocks with comprehensive data
    
    URL: /api/stocks/nasdaq/
    """
    try:
        # Import NASDAQ tickers
        import sys
        from pathlib import Path
        sys.path.append(str(Path(__file__).parent.parent.parent / 'data' / 'nasdaq_only'))
        
        try:
            from nasdaq_only_tickers_20250724_184741 import NASDAQ_ONLY_TICKERS
        except ImportError:
            NASDAQ_ONLY_TICKERS = []
        
        # Filter stocks to NASDAQ only
        nasdaq_stocks = Stock.objects.filter(
            ticker__in=NASDAQ_ONLY_TICKERS,
            exchange__iexact='NASDAQ'
        ).order_by('ticker')
        
        # Parse limit
        limit = min(int(request.GET.get('limit', 500)), 1000)
        nasdaq_stocks = nasdaq_stocks[:limit]
        
        stock_data = []
        for stock in nasdaq_stocks:
            stock_data.append({
                'ticker': stock.ticker,
                'company_name': stock.company_name or stock.name,
                'current_price': format_decimal_safe(stock.current_price),
                'price_change_today': format_decimal_safe(stock.price_change_today),
                'change_percent': format_decimal_safe(stock.change_percent),
                'volume': stock.volume,
                'market_cap': stock.market_cap,
                'pe_ratio': format_decimal_safe(stock.pe_ratio),
                'formatted_price': stock.formatted_price,
                'formatted_change': stock.formatted_change,
                'formatted_market_cap': stock.formatted_market_cap,
                'last_updated': stock.last_updated.isoformat() if stock.last_updated else None,
                'is_gaining': (stock.price_change_today or 0) > 0
            })
        
        return Response({
            'success': True,
            'exchange': 'NASDAQ',
            'count': len(stock_data),
            'total_nasdaq_tickers': len(NASDAQ_ONLY_TICKERS),
            'data': stock_data,
            'timestamp': timezone.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in nasdaq_stocks_api: {e}", exc_info=True)
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
def stock_search_api(request):
    """
    Advanced stock search with multiple criteria
    
    URL: /api/stocks/search/
    """
    try:
        query = request.GET.get('q', '').strip()
        if not query:
            return Response({
                'success': False,
                'error': 'Search query parameter "q" is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Search in multiple fields
        stocks = Stock.objects.filter(
            Q(ticker__icontains=query) |
            Q(symbol__icontains=query) |
            Q(company_name__icontains=query) |
            Q(name__icontains=query)
        ).order_by('ticker')[:50]
        
        search_results = []
        for stock in stocks:
            search_results.append({
                'ticker': stock.ticker,
                'company_name': stock.company_name or stock.name,
                'current_price': format_decimal_safe(stock.current_price),
                'change_percent': format_decimal_safe(stock.change_percent),
                'market_cap': stock.market_cap,
                'exchange': stock.exchange,
                'match_type': 'ticker' if query.upper() in stock.ticker else 'company',
                'url': f'/api/stocks/{stock.ticker}/'
            })
        
        return Response({
            'success': True,
            'query': query,
            'count': len(search_results),
            'results': search_results,
            'timestamp': timezone.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in stock_search_api: {e}", exc_info=True)
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_exempt
def wordpress_subscription_api(request):
    """
    Handle email subscriptions from WordPress

    URL: /api/wordpress/subscribe/
    Method: POST
    Data: {"email": "user@example.com", "category": "dvsa-50"}
    """
    try:
        data = json.loads(request.body)
        email = data.get('email', '').strip()
        category = data.get('category', '').strip()

        if not email or not category:
            return Response({
                'success': False,
                'error': 'Email and category are required'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Create or update subscription
        subscription, created = EmailSubscription.objects.get_or_create(
            email=email,
            category=category,
            defaults={'is_active': True}
        )

        return Response({
            'success': True,
            'message': 'Subscription created successfully' if created else 'Subscription updated',
            'data': {
                'email': email,
                'category': category,
                'is_active': subscription.is_active
            }
        })

    except Exception as e:
        logger.error(f"WordPress subscription error: {e}", exc_info=True)
        return Response({
            'success': False,
            'error': 'Unable to process subscription'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
def stock_statistics_api(request):
    """
    Get overall market statistics for WordPress dashboard

    URL: /api/stats/
    """
    try:
        # Cache key
        cache_key = "stock_statistics"
        cached_stats = cache.get(cache_key)

        if cached_stats:
            return Response(cached_stats)

        # Calculate statistics
        total_stocks = Stock.objects.count()
        gainers = Stock.objects.filter(price_change_today__gt=0).count()
        losers = Stock.objects.filter(price_change_today__lt=0).count()
        unchanged = total_stocks - gainers - losers

        # Recent updates
        recent_updates = Stock.objects.filter(
            last_updated__gte=timezone.now() - timedelta(hours=24)
        ).count()

        # Top performers
        top_gainer = Stock.objects.filter(
            price_change_today__gt=0
        ).order_by('-price_change_today').first()

        top_loser = Stock.objects.filter(
            price_change_today__lt=0
        ).order_by('price_change_today').first()

        most_active = Stock.objects.filter(
            volume__gt=0
        ).order_by('-volume').first()

        # Email subscriptions
        active_subscriptions = EmailSubscription.objects.filter(is_active=True).count()

        stats_data = {
            'success': True,
            'market_overview': {
                'total_stocks': total_stocks,
                'gainers': gainers,
                'losers': losers,
                'unchanged': unchanged,
                'gainer_percentage': round((gainers / total_stocks * 100), 1) if total_stocks > 0 else 0,
                'recent_updates': recent_updates
            },
            'top_performers': {
                'top_gainer': {
                    'ticker': top_gainer.ticker if top_gainer else None,
                    'company_name': top_gainer.company_name or top_gainer.name if top_gainer else None,
                    'price_change_percent': format_decimal_safe(top_gainer.change_percent) if top_gainer else 0,
                    'wordpress_url': f"/stock/{top_gainer.ticker.lower()}/" if top_gainer else None
                } if top_gainer else None,
                'top_loser': {
                    'ticker': top_loser.ticker if top_loser else None,
                    'company_name': top_loser.company_name or top_loser.name if top_loser else None,
                    'price_change_percent': format_decimal_safe(top_loser.change_percent) if top_loser else 0,
                    'wordpress_url': f"/stock/{top_loser.ticker.lower()}/" if top_loser else None
                } if top_loser else None,
                'most_active': {
                    'ticker': most_active.ticker if most_active else None,
                    'company_name': most_active.company_name or most_active.name if most_active else None,
                    'volume_today': int(most_active.volume) if most_active and most_active.volume else 0,
                    'wordpress_url': f"/stock/{most_active.ticker.lower()}/" if most_active else None
                } if most_active else None
            },
            'subscriptions': {
                'active_count': active_subscriptions
            },
            'timestamp': timezone.now().isoformat()
        }

        # Cache for 5 minutes
        cache.set(cache_key, stats_data, 300)
        return Response(stats_data)

    except Exception as e:
        logger.error(f"Error in stock_statistics_api: {e}", exc_info=True)
        return Response({
            'success': False,
            'error': 'Unable to fetch stock statistics'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Helper functions - moved to utils for better organization
