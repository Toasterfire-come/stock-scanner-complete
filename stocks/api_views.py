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

def format_decimal(value):
    """Safely format decimal values"""
    if value is None:
        return None
    return float(value)

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
                'current_price': format_decimal(stock.current_price),
                'price_change_today': format_decimal(stock.price_change_today),
                'price_change_week': format_decimal(stock.price_change_week),
                'price_change_month': format_decimal(stock.price_change_month),
                'price_change_year': format_decimal(stock.price_change_year),
                'change_percent': format_decimal(stock.change_percent) or change_percent,
                
                # Bid/Ask and Range
                'bid_price': format_decimal(stock.bid_price),
                'ask_price': format_decimal(stock.ask_price),
                'bid_ask_spread': stock.bid_ask_spread,
                'days_range': stock.days_range,
                'days_low': format_decimal(stock.days_low),
                'days_high': format_decimal(stock.days_high),
                
                # Volume data
                'volume': stock.volume,
                'volume_today': stock.volume_today or stock.volume,
                'avg_volume_3mon': stock.avg_volume_3mon,
                'dvav': format_decimal(stock.dvav),
                'shares_available': stock.shares_available,
                
                # Market data
                'market_cap': stock.market_cap,
                'market_cap_change_3mon': format_decimal(stock.market_cap_change_3mon),
                'formatted_market_cap': stock.formatted_market_cap,
                
                # Financial ratios
                'pe_ratio': format_decimal(stock.pe_ratio),
                'pe_change_3mon': format_decimal(stock.pe_change_3mon),
                'dividend_yield': format_decimal(stock.dividend_yield),
                
                # 52-week range
                'week_52_low': format_decimal(stock.week_52_low),
                'week_52_high': format_decimal(stock.week_52_high),
                
                # Additional metrics
                'one_year_target': format_decimal(stock.one_year_target),
                'earnings_per_share': format_decimal(stock.earnings_per_share),
                'book_value': format_decimal(stock.book_value),
                'price_to_book': format_decimal(stock.price_to_book),
                
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
                'volume_ratio': format_decimal(stock.dvav),
                
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
                'price': format_decimal(price_record.price),
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
            'current_price': format_decimal(stock.current_price),
            'price_change_today': format_decimal(stock.price_change_today),
            'price_change_week': format_decimal(stock.price_change_week),
            'price_change_month': format_decimal(stock.price_change_month),
            'price_change_year': format_decimal(stock.price_change_year),
            'change_percent': format_decimal(stock.change_percent) or change_percent,
            
            # Bid/Ask and daily range
            'bid_price': format_decimal(stock.bid_price),
            'ask_price': format_decimal(stock.ask_price),
            'bid_ask_spread': stock.bid_ask_spread,
            'days_range': stock.days_range,
            'days_low': format_decimal(stock.days_low),
            'days_high': format_decimal(stock.days_high),
            
            # Volume information
            'volume': stock.volume,
            'volume_today': stock.volume_today or stock.volume,
            'avg_volume_3mon': stock.avg_volume_3mon,
            'dvav': format_decimal(stock.dvav),
            'shares_available': stock.shares_available,
            
            # Market capitalization
            'market_cap': stock.market_cap,
            'market_cap_change_3mon': format_decimal(stock.market_cap_change_3mon),
            'formatted_market_cap': stock.formatted_market_cap,
            
            # Financial ratios and metrics
            'pe_ratio': format_decimal(stock.pe_ratio),
            'pe_change_3mon': format_decimal(stock.pe_change_3mon),
            'dividend_yield': format_decimal(stock.dividend_yield),
            'earnings_per_share': format_decimal(stock.earnings_per_share),
            'book_value': format_decimal(stock.book_value),
            'price_to_book': format_decimal(stock.price_to_book),
            
            # 52-week performance
            'week_52_low': format_decimal(stock.week_52_low),
            'week_52_high': format_decimal(stock.week_52_high),
            
            # Targets and predictions
            'one_year_target': format_decimal(stock.one_year_target),
            
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
                'current_price': format_decimal(stock.current_price),
                'price_change_today': format_decimal(stock.price_change_today),
                'change_percent': format_decimal(stock.change_percent),
                'volume': stock.volume,
                'market_cap': stock.market_cap,
                'pe_ratio': format_decimal(stock.pe_ratio),
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
                'current_price': format_decimal(stock.current_price),
                'change_percent': format_decimal(stock.change_percent),
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

if not created and not subscription.is_active:
subscription.is_active = True
subscription.save()

return Response({
'success': True,
'message': 'Subscription successful',
'created': created,
'subscription': {
'email': subscription.email,
'category': subscription.category,
'is_active': subscription.is_active,
'created_at': subscription.created_at.isoformat()
}
})

except json.JSONDecodeError:
return Response({
'success': False,
'error': 'Invalid JSON data'
}, status=status.HTTP_400_BAD_REQUEST)
except Exception as e:
logger.error(f"Error in wordpress_subscription_api: {e}")
return Response({
'success': False,
'error': str(e)
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
'price_change_percent': format_decimal(top_gainer.change_percent) if top_gainer else 0,
'wordpress_url': f"/stock/{top_gainer.ticker.lower()}/" if top_gainer else None
} if top_gainer else None,
'top_loser': {
'ticker': top_loser.ticker if top_loser else None,
'company_name': top_loser.company_name or top_loser.name if top_loser else None,
'price_change_percent': format_decimal(top_loser.change_percent) if top_loser else 0,
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
logger.error(f"Error in stock_statistics_api: {e}")
return Response({
'success': False,
'error': str(e)
}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Helper functions
def calculate_price_change_percent(stock):
"""Calculate price change percentage"""
if not stock.current_price or not stock.price_change_today:
return 0

try:
previous_price = float(stock.current_price) - float(stock.price_change_today)
if previous_price != 0:
return round((float(stock.price_change_today) / previous_price) * 100, 2)
except (ValueError, ZeroDivisionError):
pass

return 0

def calculate_volume_ratio(stock):
"""Calculate volume ratio vs average"""
if not stock.volume_today or not stock.average_volume:
return 0

try:
return round(float(stock.volume_today) / float(stock.average_volume), 2)
except (ValueError, ZeroDivisionError):
return 0

def calculate_price_near_high(stock):
"""Calculate how close price is to 52-week high"""
if not stock.current_price or not stock.fifty_two_week_high:
return 0

try:
return round((float(stock.current_price) / float(stock.fifty_two_week_high)) * 100, 1)
except (ValueError, ZeroDivisionError):
return 0

def calculate_price_near_low(stock):
"""Calculate how far price is from 52-week low"""
if not stock.current_price or not stock.fifty_two_week_low:
return 0

try:
if float(stock.fifty_two_week_low) == 0:
return 0
return round((float(stock.current_price) / float(stock.fifty_two_week_low)) * 100, 1)
except (ValueError, ZeroDivisionError):
return 0

def calculate_technical_rating(stock):
"""Calculate a simple technical rating"""
score = 0

# RSI check
if stock.rsi:
rsi = float(stock.rsi)
if 30 <= rsi <= 70: # Neutral zone
score += 1
elif rsi > 70: # Overbought
score -= 1
elif rsi < 30: # Oversold
score += 2

# Price change check
if stock.price_change_today:
if float(stock.price_change_today) > 0:
score += 1
else:
score -= 1

# Volume check
volume_ratio = calculate_volume_ratio(stock)
if volume_ratio > 1.5: # High volume
score += 1

# Convert to rating
if score >= 2:
return "BULLISH"
elif score <= -2:
return "BEARISH"
else:
return "NEUTRAL"

# CORS handling for WordPress integration
@csrf_exempt
@require_http_methods(["POST"])
def email_signup_api(request):
"""
Handle email subscription signups from WordPress

URL: /api/email-signup/
POST Parameters:
- email: User's email address
- category: Subscription category (e.g., 'popular', 'all', 'earnings')
- name: Optional user name
"""
try:
data = json.loads(request.body)
email = data.get('email', '').strip().lower()
category = data.get('category', 'popular').strip()
name = data.get('name', '').strip()

if not email:
return JsonResponse({
'success': False,
'message': 'Email address is required'
}, status=400)

# Validate email format
if '@' not in email or '.' not in email:
return JsonResponse({
'success': False,
'message': 'Please enter a valid email address'
}, status=400)

# Check if already subscribed
existing = EmailSubscription.objects.filter(email=email, category=category).first()
if existing:
if existing.is_active:
return JsonResponse({
'success': True,
'message': 'You are already subscribed to this list!',
'already_subscribed': True
})
else:
# Reactivate existing subscription
existing.is_active = True
existing.save()
return JsonResponse({
'success': True,
'message': 'Your subscription has been reactivated!',
'reactivated': True
})

# Create new subscription
subscription = EmailSubscription.objects.create(
email=email,
category=category,
is_active=True
)

logger.info(f"New email subscription: {email} -> {category}")

return JsonResponse({
'success': True,
'message': f'Successfully subscribed to {category} stock alerts!',
'subscription_id': subscription.id,
'category': category
})

except json.JSONDecodeError:
return JsonResponse({
'success': False,
'message': 'Invalid data format'
}, status=400)
except Exception as e:
logger.error(f"Email signup error: {str(e)}")
return JsonResponse({
'success': False,
'message': 'An error occurred. Please try again.'
}, status=500)

@api_view(['GET'])
@permission_classes([AllowAny])
def stock_filter_api(request):
"""
Advanced stock filtering based on multiple criteria

URL: /api/stocks/filter/
Parameters:
- min_price: Minimum stock price
- max_price: Maximum stock price
- min_volume: Minimum volume
- max_volume: Maximum volume
- min_market_cap: Minimum market cap
- max_market_cap: Maximum market cap
- min_pe: Minimum P/E ratio
- max_pe: Maximum P/E ratio
- sector: Stock sector
- sort_by: Sort field (price, volume, market_cap, pe_ratio)
- sort_order: asc or desc
- limit: Number of results (default: 50)
"""
try:
# Get filter parameters
min_price = request.GET.get('min_price')
max_price = request.GET.get('max_price')
min_volume = request.GET.get('min_volume')
max_volume = request.GET.get('max_volume')
min_market_cap = request.GET.get('min_market_cap')
max_market_cap = request.GET.get('max_market_cap')
min_pe = request.GET.get('min_pe')
max_pe = request.GET.get('max_pe')
sector = request.GET.get('sector', '').strip()
sort_by = request.GET.get('sort_by', 'current_price')
sort_order = request.GET.get('sort_order', 'desc')
limit = int(request.GET.get('limit', 50))

# Start with all stocks
queryset = Stock.objects.all()

# Apply filters
if min_price:
queryset = queryset.filter(current_price__gte=Decimal(min_price))
if max_price:
queryset = queryset.filter(current_price__lte=Decimal(max_price))
if min_volume:
queryset = queryset.filter(volume__gte=int(min_volume))
if max_volume:
queryset = queryset.filter(volume__lte=int(max_volume))
if min_market_cap:
queryset = queryset.filter(market_cap__gte=int(min_market_cap))
if max_market_cap:
queryset = queryset.filter(market_cap__lte=int(max_market_cap))
if min_pe:
queryset = queryset.filter(pe_ratio__gte=Decimal(min_pe))
if max_pe:
queryset = queryset.filter(pe_ratio__lte=Decimal(max_pe))
if sector:
queryset = queryset.filter(company_name__icontains=sector)

# Apply sorting
sort_field = sort_by
if sort_order == 'desc':
sort_field = f'-{sort_field}'

queryset = queryset.order_by(sort_field)[:limit]

# Format response
stocks = []
for stock in queryset:
stocks.append({
'ticker': stock.ticker,
'company_name': stock.company_name or stock.ticker,
'current_price': round(stock.current_price, 2),
'volume_today': stock.volume_today,
'avg_volume': stock.avg_volume,
'market_cap': stock.market_cap,
'pe_ratio': stock.pe_ratio,
'dvav': stock.dvav,
'dvsa': stock.dvsa,
'last_update': stock.last_update.isoformat() if stock.last_update else None,
'note': stock.note
})

return Response({
'success': True,
'count': len(stocks),
'filters_applied': {
'min_price': min_price,
'max_price': max_price,
'min_volume': min_volume,
'max_volume': max_volume,
'min_market_cap': min_market_cap,
'max_market_cap': max_market_cap,
'min_pe': min_pe,
'max_pe': max_pe,
'sector': sector,
'sort_by': sort_by,
'sort_order': sort_order
},
'stocks': stocks
})

except Exception as e:
logger.error(f"Stock filter error: {str(e)}")
return Response({
'success': False,
'error': 'Failed to filter stocks',
'message': str(e)
}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
def stock_lookup_api(request, ticker):
"""
Detailed stock lookup for a specific ticker

URL: /api/stocks/lookup/<ticker>/
Returns comprehensive data for a single stock
"""
try:
ticker = ticker.upper().strip()

# Check cache first
cache_key = f'stock_lookup_{ticker}'
cached_data = cache.get(cache_key)
if cached_data:
return Response(cached_data)

# Try to get from database first
db_stock = Stock.objects.filter(ticker=ticker).first()

# Get real-time data using stock manager
try:
quote_data = stock_manager.get_stock_quote(ticker)
if not quote_data:
raise Exception("No data available from any API")

# Get additional data from yfinance for detailed info
stock = yf.Ticker(ticker)
info = stock.info
hist = stock.history(period="5d", interval="1d")

# Format comprehensive response
stock_data = {
'ticker': ticker,
'company_name': info.get('longName', info.get('shortName', ticker)),
'sector': info.get('sector', 'Unknown'),
'industry': info.get('industry', 'Unknown'),
'website': info.get('website', ''),
'description': info.get('longBusinessSummary', ''),

# Price data (primary from stock manager, fallback to yfinance info)
'current_price': quote_data.get('price', info.get('currentPrice', info.get('regularMarketPrice', 0))),
'previous_close': quote_data.get('price', 0) - quote_data.get('change', 0) if quote_data.get('change') else info.get('previousClose', 0),
'open': info.get('open', 0),
'day_low': info.get('dayLow', 0),
'day_high': info.get('dayHigh', 0),
'fifty_two_week_low': info.get('fiftyTwoWeekLow', 0),
'fifty_two_week_high': info.get('fiftyTwoWeekHigh', 0),

# Volume data
'volume': info.get('volume', 0),
'avg_volume': info.get('averageVolume', 0),
'avg_volume_10d': info.get('averageVolume10days', 0),

# Market data
'market_cap': info.get('marketCap', 0),
'shares_outstanding': info.get('sharesOutstanding', 0),
'float_shares': info.get('floatShares', 0),

# Financial ratios
'pe_ratio': info.get('trailingPE', 0),
'forward_pe': info.get('forwardPE', 0),
'peg_ratio': info.get('pegRatio', 0),
'price_to_book': info.get('priceToBook', 0),
'price_to_sales': info.get('priceToSalesTrailing12Months', 0),

# Dividends
'dividend_yield': info.get('dividendYield', 0),
'dividend_rate': info.get('dividendRate', 0),

# Performance
'beta': info.get('beta', 0),
'fifty_day_average': info.get('fiftyDayAverage', 0),
'two_hundred_day_average': info.get('twoHundredDayAverage', 0),

# Additional metrics from our database
'dvav': db_stock.dvav if db_stock else None,
'dvsa': db_stock.dvsa if db_stock else None,
'note': db_stock.note if db_stock else '',
'last_update': db_stock.last_updated.isoformat() if db_stock and db_stock.last_updated else None,

# Price history (last 5 days)
'price_history': []
}

# Add price history if available
if not hist.empty:
for date, row in hist.iterrows():
stock_data['price_history'].append({
'date': date.strftime('%Y-%m-%d'),
'open': round(row['Open'], 2),
'high': round(row['High'], 2),
'low': round(row['Low'], 2),
'close': round(row['Close'], 2),
'volume': int(row['Volume'])
})

# Cache the result for 5 minutes
cache.set(cache_key, stock_data, 300)

return Response({
'success': True,
'data': stock_data
})

except Exception as yf_error:
logger.error(f"YFinance error for {ticker}: {str(yf_error)}")

# Fallback to database data only
if db_stock:
fallback_data = {
'ticker': db_stock.ticker,
'company_name': db_stock.company_name or db_stock.ticker,
'current_price': db_stock.current_price,
'volume_today': db_stock.volume_today,
'avg_volume': db_stock.avg_volume,
'market_cap': db_stock.market_cap,
'pe_ratio': db_stock.pe_ratio,
'dvav': db_stock.dvav,
'dvsa': db_stock.dvsa,
'note': db_stock.note,
'last_update': db_stock.last_updated.isoformat() if db_stock.last_updated else None,
'data_source': 'database_only'
}

return Response({
'success': True,
'data': fallback_data,
'warning': 'Limited data available - real-time data unavailable'
})
else:
return Response({
'success': False,
'error': f'Stock {ticker} not found',
'message': 'Stock not found in database and real-time data unavailable'
}, status=status.HTTP_404_NOT_FOUND)

except Exception as e:
logger.error(f"Stock lookup error for {ticker}: {str(e)}")
return Response({
'success': False,
'error': 'Failed to fetch stock data',
'message': str(e)
}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
def stock_news_api(request):
"""
Get financial news and important stocks

URL: /api/news/
Parameters:
- ticker: Get news for specific ticker
- category: news category (market, earnings, analysis)
- limit: Number of articles (default: 20)
"""
try:
ticker = request.GET.get('ticker', '').upper().strip()
category = request.GET.get('category', 'market').strip()
limit = int(request.GET.get('limit', 20))

# Cache key
cache_key = f'stock_news_{ticker}_{category}_{limit}'
cached_news = cache.get(cache_key)
if cached_news:
return Response(cached_news)

news_articles = []
important_stocks = []

# Get important/trending stocks from our database
trending_stocks = Stock.objects.filter(
volume__gt=1000000 # High volume stocks
).order_by('-volume')[:10]

for stock in trending_stocks:
important_stocks.append({
'ticker': stock.ticker,
'company_name': stock.company_name or stock.ticker,
'current_price': stock.current_price,
'volume_today': stock.volume_today,
'note': stock.note
})

# Try to get news from Yahoo Finance
if ticker:
try:
# Use yfinance directly for news (not available in stock manager)
stock = yf.Ticker(ticker)
news = stock.news

for article in news[:limit]:
news_articles.append({
'title': article.get('title', ''),
'summary': article.get('summary', ''),
'url': article.get('link', ''),
'publisher': article.get('publisher', ''),
'publish_time': article.get('providerPublishTime', 0),
'thumbnail': article.get('thumbnail', {}).get('resolutions', [{}])[0].get('url', '') if article.get('thumbnail') else '',
'related_ticker': ticker
})
except Exception as e:
logger.warning(f"Could not fetch news for {ticker}: {str(e)}")

# If no ticker-specific news or general news requested, get market news
if not news_articles or not ticker:
# Sample market news (in production, integrate with real news API)
sample_news = [
{
'title': 'Market Update: Technology Stocks Show Strong Performance',
'summary': 'Major tech stocks including AAPL, MSFT, and GOOGL showed significant gains in today\'s trading session.',
'url': '#',
'publisher': 'Market News',
'publish_time': int(datetime.now().timestamp()),
'thumbnail': '',
'category': 'market'
},
{
'title': 'Earnings Season Outlook: Key Companies to Watch',
'summary': 'Analysts are closely watching upcoming earnings reports from major corporations.',
'url': '#',
'publisher': 'Financial Times',
'publish_time': int((datetime.now() - timedelta(hours=2)).timestamp()),
'thumbnail': '',
'category': 'earnings'
}
]

news_articles.extend(sample_news)

response_data = {
'success': True,
'news': news_articles[:limit],
'important_stocks': important_stocks,
'category': category,
'ticker_specific': bool(ticker),
'count': len(news_articles)
}

# Cache for 10 minutes
cache.set(cache_key, response_data, 600)

return Response(response_data)

except Exception as e:
logger.error(f"News API error: {str(e)}")
return Response({
'success': False,
'error': 'Failed to fetch news',
'message': str(e)
}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@csrf_exempt
@require_http_methods(["GET", "POST", "OPTIONS"])
def cors_handler(request):
"""Handle CORS preflight requests for WordPress"""
response = JsonResponse({'status': 'ok'})
response["Access-Control-Allow-Origin"] = "*"
response["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
response["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
return response