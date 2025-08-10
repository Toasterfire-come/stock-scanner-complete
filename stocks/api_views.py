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
from django.contrib.auth.models import User

from .models import Stock, StockAlert, StockPrice
from emails.models import EmailSubscription
# import yfinance as yf  # Disabled: DB-only mode
# import requests  # Disabled: DB-only mode
# from bs4 import BeautifulSoup  # Disabled: DB-only mode

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
    Get comprehensive list of stocks with full data and filtering - FIXED VERSION

    URL: /api/stocks/
    Parameters:
    - limit: Number of stocks to return (default: 50, max: 1000)
    - search: Search by ticker or company name
    - category: Filter by category (gainers, losers, high_volume, large_cap, small_cap, all)
    - min_price: Minimum price filter
    - max_price: Maximum price filter
    - min_volume: Minimum volume filter
    - min_market_cap: Minimum market cap filter
    - max_market_cap: Maximum market cap filter
    - min_pe: Minimum P/E ratio
    - max_pe: Maximum P/E ratio
    - exchange: Filter by exchange (omit or 'all' to include all)
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
        
        # Exchange filter - do not default to NYSE; allow 'all' to include everything
        exchange = request.GET.get('exchange', '').strip()
        if exchange.lower() in ('all', ''):
            exchange = None
        
        # Sorting - default to last_updated for better results
        sort_by = request.GET.get('sort_by', 'last_updated')
        sort_order = request.GET.get('sort_order', 'desc')
        
        # Detect base request (no filters/search)
        is_base_request = (
            (not search) and (not category) and
            not any([min_price, max_price, min_volume, min_market_cap, max_market_cap, min_pe, max_pe]) and
            (exchange is None)
        )
        
        # Add intelligent caching to reduce database load
        cache_key = f"stocks_api_{category}_{sort_by}_{sort_order}_{limit}_{min_price}_{max_price}_{min_market_cap}_{max_market_cap}_{min_pe}_{max_pe}_{search}"
        cached_result = cache.get(cache_key)
        
        if cached_result:
            logger.info(f"Returning cached result for key: {cache_key}")
            return Response(cached_result, status=status.HTTP_200_OK)

        # Base queryset with better filtering
        base_queryset = Stock.objects.exclude(
            ticker__isnull=True
        ).exclude(
            ticker__exact=''
        ).exclude(
            current_price__isnull=True
        ).exclude(
            current_price__lte=0
        ).filter(
            # Only include stocks updated within the last 30 days
            last_updated__gte=timezone.now() - timedelta(days=30)
        )
        
        # Apply exchange filter (case insensitive, flexible)
        if exchange:
            # Try exact match first, then broader matches
            exchange_queries = [
                Q(exchange__iexact=exchange),
                Q(exchange__icontains=exchange),
                Q(exchange__icontains=exchange.upper()),
                Q(exchange__icontains=exchange.lower())
            ]
            
            exchange_query = exchange_queries[0]
            for eq in exchange_queries[1:]:
                exchange_query |= eq
            
            base_queryset = base_queryset.filter(exchange_query)
        
        # Apply search filter early (only if search has content)
        if search:
            base_queryset = base_queryset.filter(
                Q(ticker__icontains=search) | 
                Q(company_name__icontains=search) |
                Q(symbol__icontains=search) |
                Q(name__icontains=search)
            )
        
        # Get total count before further filtering
        total_available = base_queryset.count()
        
        # If it's the base request with no filters/search, return all stocks without extra filtering
        if is_base_request:
            queryset = base_queryset
            # Base request should return all stocks
            limit = total_available
        else:
            # Apply progressive quality filters
            queryset = base_queryset
            
            # Only apply strict price filters for specific categories
            if category == 'all':
                # Show all stocks including those without complete data
                queryset = base_queryset
            else:
                # Try to get stocks with good data first
                preferred_queryset = queryset.filter(
                    current_price__isnull=False
                ).exclude(current_price=0)
                
                # If we get enough results, use the preferred set
                if preferred_queryset.count() >= limit // 2:
                    queryset = preferred_queryset
                # Otherwise, be more inclusive
                else:
                    # Include stocks with ANY useful data (even if price is zero)
                    queryset = queryset.filter(
                        Q(current_price__isnull=False) |
                        Q(volume__isnull=False) |
                        Q(market_cap__isnull=False)
                    )
        
        # Search filter already applied above to base_queryset
        # No need to reapply here

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

        # Apply category filters with market hours awareness
        if category == 'gainers':
            # Try current day first, then fall back to most recent available data
            queryset = queryset.filter(price_change_today__gt=0)
            if queryset.count() == 0:
                logger.info("No gainers found for today, checking recent price changes...")
                queryset = base_queryset.filter(
                    Q(price_change_today__gt=0) |
                    Q(change_percent__gt=0) |
                    Q(price_change_week__gt=0)
                ).exclude(current_price__isnull=True).order_by('-last_updated')
                
        elif category == 'losers':
            # Try current day first, then fall back to most recent available data
            queryset = queryset.filter(price_change_today__lt=0)
            if queryset.count() == 0:
                logger.info("No losers found for today (market may be closed), checking recent price changes...")
                # Use weekly or monthly data when daily data is not available
                queryset = base_queryset.filter(
                    Q(price_change_today__lt=0) |
                    Q(change_percent__lt=0) |
                    Q(price_change_week__lt=0) |
                    Q(price_change_month__lt=0)
                ).exclude(current_price__isnull=True)
                
                # If still no results, get stocks with the most negative changes available
                if queryset.count() == 0:
                    logger.info("No negative price changes found, getting stocks with lowest prices...")
                    queryset = base_queryset.filter(
                        current_price__isnull=False,
                        current_price__gt=0
                    ).order_by('current_price')  # Lowest priced stocks
                    
        elif category == 'high_volume':
            queryset = queryset.filter(volume__isnull=False).exclude(volume=0)
            # If no high volume stocks found, get any stocks with volume data
            if queryset.count() == 0:
                queryset = base_queryset.filter(volume__isnull=False).order_by('-volume', '-last_updated')
                
        elif category == 'large_cap':
            queryset = queryset.filter(market_cap__gte=10000000000)  # $10B+
            # If no large cap found, try lower threshold
            if queryset.count() == 0:
                queryset = base_queryset.filter(market_cap__gte=5000000000).order_by('-market_cap', '-last_updated')
                
        elif category == 'small_cap':
            queryset = queryset.filter(market_cap__lt=2000000000, market_cap__gt=0)  # < $2B
            # If no small cap found, try different range
            if queryset.count() == 0:
                queryset = base_queryset.filter(market_cap__lt=5000000000, market_cap__gt=0).order_by('market_cap', '-last_updated')

        # Apply sorting with fallbacks
        sort_field = sort_by
        if sort_order == 'desc':
            sort_field = f'-{sort_by}'
            
        # Handle sorting with fallbacks
        try:
            if sort_by == 'change_percent':
                if sort_order == 'desc':
                    queryset = queryset.order_by('-change_percent', '-last_updated')
                else:
                    queryset = queryset.order_by('change_percent', '-last_updated')
            elif sort_by == 'volume':
                queryset = queryset.order_by(sort_field, '-last_updated')
            elif sort_by == 'last_updated':
                queryset = queryset.order_by(sort_field, '-id')
            else:
                queryset = queryset.order_by(sort_field, '-last_updated')
        except:
            # Fallback sorting
            queryset = queryset.order_by('-last_updated', '-id')

        # EMERGENCY FALLBACK: If still no results, return most recent stocks
        if queryset.count() == 0 and not search:
            logger.warning(f"API returned 0 results for category '{category}', using emergency fallback with recent stocks")
            # Try to get stocks updated in the last 7 days first
            recent_cutoff = timezone.now() - timedelta(days=7)
            queryset = base_queryset.filter(last_updated__gte=recent_cutoff).order_by('-last_updated')
            if queryset.count() == 0:
                # If no recent stocks, get any stocks with valid price data
                queryset = base_queryset.exclude(current_price__isnull=True).order_by('-last_updated')
            queryset = queryset[:limit]

        # Limit results
        stocks = queryset[:limit]

        # Format comprehensive data
        stock_data = []
        for stock in stocks:
            change_percent = calculate_change_percent(stock.current_price, stock.price_change_today)
            
            record = {
                # Basic info
                'ticker': stock.ticker,
                'symbol': stock.symbol or stock.ticker,
                'company_name': stock.company_name or stock.name or stock.ticker,
                'name': stock.name or stock.company_name or stock.ticker,
                'exchange': stock.exchange,
                
                # Price data (with better fallbacks)
                'current_price': format_decimal_safe(stock.current_price) or 0.0,
                'price_change_today': format_decimal_safe(stock.price_change_today) or 0.0,
                'price_change_week': format_decimal_safe(stock.price_change_week) or 0.0,
                'price_change_month': format_decimal_safe(stock.price_change_month) or 0.0,
                'price_change_year': format_decimal_safe(stock.price_change_year) or 0.0,
                'change_percent': format_decimal_safe(stock.change_percent) or change_percent or 0.0,
                
                # Bid/Ask and Range
                'bid_price': format_decimal_safe(stock.bid_price),
                'ask_price': format_decimal_safe(stock.ask_price),
                'bid_ask_spread': stock.bid_ask_spread,
                'days_range': stock.days_range,
                'days_low': format_decimal_safe(stock.days_low),
                'days_high': format_decimal_safe(stock.days_high),
                
                # Volume data
                'volume': int(stock.volume) if stock.volume else 0,
                'volume_today': int(stock.volume_today or stock.volume) if (stock.volume_today or stock.volume) else 0,
                'avg_volume_3mon': int(stock.avg_volume_3mon) if stock.avg_volume_3mon else 0,
                'dvav': format_decimal_safe(stock.dvav) or 0.0,
                'shares_available': int(stock.shares_available) if stock.shares_available else 0,
                
                # Market data
                'market_cap': int(stock.market_cap) if stock.market_cap else 0,
                'market_cap_change_3mon': format_decimal_safe(stock.market_cap_change_3mon) or 0.0,
                'formatted_market_cap': getattr(stock, 'formatted_market_cap', '') or '',
                
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
            }
            
            # Remove None-valued fields for a cleaner payload
            cleaned_record = {k: v for k, v in record.items() if v is not None}
            stock_data.append(cleaned_record)

        # Ensure we always have a meaningful response
        final_count = len(stock_data)
        final_total = max(total_available, final_count)

        filters_raw = {
            'search': search,
            'category': category,
            'min_price': min_price,
            'max_price': max_price,
            'min_volume': min_volume,
            'min_market_cap': min_market_cap,
            'max_market_cap': max_market_cap,
            'min_pe': min_pe,
            'max_pe': max_pe,
            'exchange': exchange or 'all',
            'sort_by': sort_by,
            'sort_order': sort_order
        }
        # Remove empty strings and None from filters for a cleaner report
        filters_applied = {k: v for k, v in filters_raw.items() if v not in (None, '')}

        # Cache the final response
        cache.set(cache_key, {
            'success': True,
            'count': final_count,
            'total_available': final_total,
            'filters_applied': filters_applied,
            'data': stock_data,
            'timestamp': timezone.now().isoformat()
        }, 300) # Cache for 5 minutes

        return Response({
            'success': True,
            'count': final_count,
            'total_available': final_total,
            'filters_applied': filters_applied,
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
            # Fallback: try to fetch minimal info via yfinance for well-known tickers
            try:
                import yfinance as yf
                yf_ticker = yf.Ticker(ticker)
                info = yf_ticker.fast_info if hasattr(yf_ticker, 'fast_info') else {}
                if not info:
                    info = {}
                current_price = float(info.get('last_price') or info.get('last_trade') or 0) or None
                market_cap = info.get('market_cap') or None
                currency = info.get('currency') or 'USD'
                if current_price is not None:
                    return Response({
                        'success': True,
                        'data': {
                            'ticker': ticker,
                            'symbol': ticker,
                            'company_name': ticker,
                            'name': ticker,
                            'exchange': info.get('exchange', 'N/A'),
                            'current_price': current_price,
                            'market_cap': int(market_cap) if market_cap else None,
                            'currency': currency,
                            'note': 'Live fallback (yfinance). Add to DB for full details.'
                        },
                        'timestamp': timezone.now().isoformat()
                    })
            except Exception:
                pass
            return Response({
                'success': False,
                'error': f'Stock {ticker} not found',
                'available_endpoints': [
                    '/api/stocks/',
                    '/api/stocks/search/'
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
            
            # Price history (recent)
            'recent_prices': price_history,
            
            # Additional metadata
            'last_updated': stock.last_updated.isoformat() if getattr(stock, 'last_updated', None) else None,
        }

        return Response({
            'success': True,
            'data': stock_data,
            'timestamp': timezone.now().isoformat()
        })

    except Exception as e:
        logger.error(f"Error in stock_detail_api: {e}", exc_info=True)
        return Response({
            'success': False,
            'error': str(e),
            'ticker': ticker
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
                'company_name': stock.company_name or stock.name or stock.ticker,
                'current_price': format_decimal_safe(stock.current_price) or 0.0,
                'change_percent': format_decimal_safe(stock.change_percent) or 0.0,
                'market_cap': int(stock.market_cap) if stock.market_cap else 0,
                'exchange': stock.exchange or 'N/A',
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
        category = (data.get('category') or '').strip()

        if not email:
            return Response({
                'success': False,
                'error': 'Email is required'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Ensure a user is associated because the model requires a user FK
        default_username = f"wp_{email.split('@')[0]}"
        user, _ = User.objects.get_or_create(username=default_username, defaults={'email': email})

        # Create or update subscription (model has no category field; we ignore it here or could store elsewhere if added later)
        subscription, created = EmailSubscription.objects.get_or_create(
            user=user,
            email=email,
            defaults={'is_active': True}
        )

        return Response({
            'success': True,
            'message': 'Subscription created successfully' if created else 'Subscription updated',
            'data': {
                'email': email,
                'category': category or None,
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

@api_view(['GET'])
@permission_classes([AllowAny])
def market_stats_api(request):
    """
    Get overall market statistics
    """
    try:
        # Get market statistics from database
        total_stocks = Stock.objects.count()
        nyse_stocks = Stock.objects.filter(exchange__iexact='NYSE').count()
        
        # Calculate market trends
        gainers = Stock.objects.filter(price_change_today__gt=0).count()
        losers = Stock.objects.filter(price_change_today__lt=0).count()
        unchanged = Stock.objects.filter(price_change_today=0).count()
        
        # Get top performers
        top_gainers = Stock.objects.filter(
            price_change_today__gt=0
        ).order_by('-change_percent')[:5].values(
            'ticker', 'name', 'current_price', 'price_change_today', 'change_percent'
        )
        
        top_losers = Stock.objects.filter(
            price_change_today__lt=0
        ).order_by('change_percent')[:5].values(
            'ticker', 'name', 'current_price', 'price_change_today', 'change_percent'
        )
        
        # Most active by volume
        most_active = Stock.objects.exclude(
            volume__isnull=True
        ).order_by('-volume')[:5].values(
            'ticker', 'name', 'current_price', 'volume'
        )
        
        stats = {
            'market_overview': {
                'total_stocks': total_stocks,
                'nyse_stocks': nyse_stocks,
                'gainers': gainers,
                'losers': losers,
                'unchanged': unchanged
            },
            'top_gainers': list(top_gainers),
            'top_losers': list(top_losers),
            'most_active': list(most_active),
            'last_updated': timezone.now().isoformat()
        }
        
        return Response(stats, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Market stats API error: {e}")
        return Response(
            {'error': 'Failed to retrieve market statistics'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([AllowAny])
def filter_stocks_api(request):
    """
    Filter stocks based on various criteria
    """
    try:
        queryset = Stock.objects.all()
        
        # Apply filters
        min_price = request.GET.get('min_price')
        max_price = request.GET.get('max_price')
        min_volume = request.GET.get('min_volume')
        max_volume = request.GET.get('max_volume')
        sector = request.GET.get('sector')
        exchange = request.GET.get('exchange')
        
        if min_price:
            queryset = queryset.filter(current_price__gte=float(min_price))
        if max_price:
            queryset = queryset.filter(current_price__lte=float(max_price))
        if min_volume:
            queryset = queryset.filter(volume__gte=int(min_volume))
        if max_volume:
            queryset = queryset.filter(volume__lte=int(max_volume))
        if sector:
            queryset = queryset.filter(sector__icontains=sector)
        if exchange:
            queryset = queryset.filter(exchange__icontains=exchange)
        
        # Order by
        order_by = request.GET.get('order_by', 'ticker')
        if order_by in ['ticker', 'current_price', 'volume', 'price_change_percent']:
            queryset = queryset.order_by(order_by)
        
        # Pagination
        limit = int(request.GET.get('limit', 100))
        offset = int(request.GET.get('offset', 0))
        
        stocks = queryset[offset:offset + limit]
        
        result = []
        for stock in stocks:
            result.append({
                'ticker': stock.ticker,
                'name': stock.name or stock.company_name or stock.ticker,
                'current_price': format_decimal_safe(stock.current_price) or 0.0,
                'price_change': format_decimal_safe(stock.price_change_today) or 0.0,
                'price_change_percent': format_decimal_safe(stock.change_percent) or 0.0,
                'volume': int(stock.volume) if stock.volume else 0,
                'market_cap': format_decimal_safe(stock.market_cap) or 0.0,
                'exchange': stock.exchange or ''
            })
        
        return Response({
            'stocks': result,
            'total_count': queryset.count(),
            'filters_applied': {
                'min_price': min_price,
                'max_price': max_price,
                'min_volume': min_volume,
                'max_volume': max_volume,
                'sector': sector,
                'exchange': exchange
            }
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Filter stocks API error: {e}")
        return Response(
            {'error': 'Failed to filter stocks'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([AllowAny])
def realtime_stock_api(request, ticker):
    """
    Get current stock data from the database only
    """
    try:
        db_stock = Stock.objects.get(Q(ticker__iexact=ticker) | Q(symbol__iexact=ticker))
        data = {
            'ticker': db_stock.ticker,
            'company_name': db_stock.company_name or db_stock.name,
            'current_price': float(db_stock.current_price or 0.0),
            'open_price': None,
            'high_price': None,
            'low_price': None,
            'volume': int(db_stock.volume or 0),
            'market_cap': int(db_stock.market_cap or 0),
            'pe_ratio': float(db_stock.pe_ratio or 0) if db_stock.pe_ratio is not None else None,
            'dividend_yield': float(db_stock.dividend_yield or 0) if db_stock.dividend_yield is not None else None,
            'last_updated': db_stock.last_updated.isoformat() if db_stock.last_updated else timezone.now().isoformat(),
            'market_status': 'unknown'
        }
        return Response(data, status=status.HTTP_200_OK)
    except Stock.DoesNotExist:
        return Response(
            {'error': f'Stock {ticker} not found in database'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(f"Real-time stock API error for {ticker}: {e}")
        return Response(
            {'error': 'Failed to retrieve stock data'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([AllowAny])
def trending_stocks_api(request):
    """
    Get trending stocks based on volume and price changes
    """
    try:
        # Get top trending by volume - prioritize NYSE
        high_volume_stocks = Stock.objects.filter(
            exchange__iexact='NYSE'
        ).exclude(
            volume__isnull=True
        ).exclude(volume=0).order_by('-volume')[:10]
        
        # If not enough NYSE stocks, include other exchanges
        if len(high_volume_stocks) < 5:
            additional_stocks = Stock.objects.exclude(
                exchange__iexact='NYSE'
            ).exclude(
                volume__isnull=True
            ).exclude(volume=0).order_by('-volume')[:10-len(high_volume_stocks)]
            high_volume_stocks = list(high_volume_stocks) + list(additional_stocks)
        
        # Get top gainers (prefer positive changes, prioritize NYSE)
        top_gainers = Stock.objects.filter(
            exchange__iexact='NYSE',
            change_percent__gt=0
        ).order_by('-change_percent')[:10]
        
        # If not enough NYSE gainers, include other exchanges
        if len(top_gainers) < 5:
            additional_gainers = Stock.objects.filter(
                change_percent__gt=0
            ).exclude(
                exchange__iexact='NYSE'
            ).order_by('-change_percent')[:10-len(top_gainers)]
            top_gainers = list(top_gainers) + list(additional_gainers)
        
        # If still no gainers, get stocks with the best changes (even if negative)
        if len(top_gainers) == 0:
            top_gainers = Stock.objects.exclude(
                change_percent__isnull=True
            ).order_by('-change_percent')[:10]
        
        # Get most active (FIXED - more inclusive filtering)
        # Try NYSE stocks with good volume data first
        most_active = Stock.objects.filter(
            exchange__iexact='NYSE'
        ).exclude(
            volume__isnull=True
        ).exclude(volume=0).order_by('-volume')[:10]
        
        # If not enough NYSE active stocks, include other exchanges
        if len(most_active) < 5:
            additional_active = Stock.objects.exclude(
                exchange__iexact='NYSE'
            ).exclude(
                volume__isnull=True
            ).exclude(volume=0).order_by('-volume')[:10-len(most_active)]
            most_active = list(most_active) + list(additional_active)
        
        # Fallback for most active if volume filter is too restrictive
        if len(most_active) < 5:
            fallback_active = Stock.objects.exclude(
                volume__isnull=True
            ).exclude(volume=0).order_by('-volume')[:10]
            most_active = list(most_active) + [s for s in fallback_active if s not in most_active][:10]
        
        def format_stock_data(stocks):
            return [{
                'ticker': stock.ticker,
                'name': stock.name or stock.company_name or stock.ticker,
                'current_price': format_decimal_safe(stock.current_price) or 0.0,
                'price_change_today': format_decimal_safe(stock.price_change_today) or 0.0,
                'change_percent': format_decimal_safe(stock.change_percent) or 0.0,
                'volume': int(stock.volume) if stock.volume else 0,
                'market_cap': format_decimal_safe(stock.market_cap) or 0.0
            } for stock in stocks]
        
        trending_data = {
            'high_volume': format_stock_data(high_volume_stocks),
            'top_gainers': format_stock_data(top_gainers),
            'most_active': format_stock_data(most_active),
            'last_updated': timezone.now().isoformat()
        }
        
        return Response(trending_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Trending stocks API error: {e}")
        return Response(
            {'error': 'Failed to retrieve trending stocks'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def create_alert_api(request):
    """
    Create a new stock price alert
    GET: Returns endpoint information
    POST: Creates a new alert
    """
    if request.method == 'GET':
        return Response({
            'endpoint': '/api/alerts/create/',
            'method': 'POST',
            'description': 'Create a new stock price alert',
            'required_fields': {
                'ticker': 'Stock symbol (e.g., AAPL)',
                'target_price': 'Alert trigger price (number)',
                'alert_type': 'Type of alert ("above" or "below")',
                'email': 'Email address for notifications (optional)'
            },
            'example_request': {
                'ticker': 'AAPL',
                'target_price': 200.00,
                'alert_type': 'above',
                'email': 'user@example.com'
            },
            'usage': 'Send POST request with JSON data to create an alert'
        }, status=status.HTTP_200_OK)
    
    # Handle POST request
    try:
        data = json.loads(request.body)
        
        # Support both legacy fields and model fields
        required_fields = ['ticker', 'target_price', 'condition', 'email']
        for field in required_fields:
            if field not in data:
                return Response(
                    {'error': f'Missing required field: {field}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Validate condition
        if data['condition'] not in ['above', 'below']:
            return Response(
                {'error': 'Condition must be "above" or "below"'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if stock exists
        try:
            stock = Stock.objects.get(ticker=data['ticker'].upper())
        except Stock.DoesNotExist:
            return Response(
                {'error': f'Stock {data["ticker"]} not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Map to model: find or create a system user for alerts
        system_user, _ = User.objects.get_or_create(username='system_alerts', defaults={'is_staff': False, 'is_superuser': False})
        
        # Translate condition to alert_type if needed
        condition = data['condition']
        if condition == 'above':
            alert_type = 'price_above'
        elif condition == 'below':
            alert_type = 'price_below'
        else:
            alert_type = 'price_change'
        
        target_value = Decimal(str(data['target_price']))
        
        # Create alert
        alert = StockAlert.objects.create(
            user=system_user,
            stock=stock,
            alert_type=alert_type,
            target_value=target_value,
            is_active=True
        )
        
        return Response({
            'alert_id': alert.id,
            'message': f'Alert created for {stock.ticker}',
            'details': {
                'ticker': stock.ticker,
                'target_value': float(alert.target_value),
                'alert_type': alert.alert_type,
                'created_at': alert.created_at.isoformat()
            }
        }, status=status.HTTP_201_CREATED)
        
    except json.JSONDecodeError:
        return Response(
            {'error': 'Invalid JSON data'},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        logger.error(f"Create alert API error: {e}")
        return Response(
            {'error': 'Failed to create alert'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

# Helper functions - moved to utils for better organization
