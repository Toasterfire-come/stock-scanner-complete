"""
Stock Quote API Views
Handles stock quote and real-time data endpoints
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from django.core.cache import cache
import yfinance as yf
import logging

from .models import Stock, UserProfile

logger = logging.getLogger(__name__)

def track_api_usage(user, endpoint):
    """Helper function to track API usage"""
    if user and user.is_authenticated:
        try:
            profile, created = UserProfile.objects.get_or_create(
                user=user,
                defaults={'plan': 'free', 'is_premium': False}
            )
            return profile.increment_api_usage()
        except Exception as e:
            logger.error(f"Usage tracking error: {e}")
    return True

@api_view(['GET'])
@permission_classes([AllowAny])
def stock_quote_api(request, symbol):
    """
    Get stock quote for specific symbol
    URL: /api/stocks/{symbol}/quote/
    Headers: X-User-ID, X-User-Plan (for usage tracking)
    """
    try:
        # Get user for usage tracking
        user = getattr(request, 'user', None)
        user_id = request.META.get('HTTP_X_USER_ID')
        
        # Track API usage
        if not track_api_usage(user, f'stock_quote_{symbol}'):
            return Response({
                'success': False,
                'error': 'API usage limit exceeded',
                'rate_limit_warning': True
            }, status=status.HTTP_429_TOO_MANY_REQUESTS)
        
        symbol = symbol.upper()
        
        # Check cache first
        cache_key = f"quote_{symbol}"
        cached_data = cache.get(cache_key)
        if cached_data:
            cached_data['cached'] = True
            return Response(cached_data)
        
        # Try to get from database first
        try:
            stock = Stock.objects.get(ticker=symbol)
            
            # If data is recent (less than 5 minutes old), return it
            if stock.last_updated and (timezone.now() - stock.last_updated).total_seconds() < 300:
                quote_data = {
                    'success': True,
                    'symbol': stock.ticker,
                    'price': float(stock.current_price) if stock.current_price else None,
                    'change': float(stock.price_change_today) if stock.price_change_today else None,
                    'change_percent': float(stock.change_percent) if stock.change_percent else None,
                    'volume': stock.volume,
                    'timestamp': stock.last_updated.isoformat(),
                    'rate_limit_warning': False,
                    'source': 'database'
                }
                
                # Cache for 1 minute
                cache.set(cache_key, quote_data, 60)
                return Response(quote_data)
                
        except Stock.DoesNotExist:
            pass
        
        # Get fresh data from yfinance
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            history = ticker.history(period="1d", interval="1m")
            
            if history.empty:
                return Response({
                    'success': False,
                    'error': f'No data available for symbol {symbol}',
                    'symbol': symbol
                }, status=status.HTTP_404_NOT_FOUND)
            
            latest = history.iloc[-1]
            current_price = float(latest['Close'])
            open_price = float(latest['Open'])
            change = current_price - open_price
            change_percent = (change / open_price * 100) if open_price != 0 else 0
            
            quote_data = {
                'success': True,
                'symbol': symbol,
                'price': current_price,
                'change': change,
                'change_percent': round(change_percent, 2),
                'volume': int(latest['Volume']),
                'timestamp': timezone.now().isoformat(),
                'rate_limit_warning': False,
                'source': 'yfinance',
                'market_data': {
                    'open': float(latest['Open']),
                    'high': float(latest['High']),
                    'low': float(latest['Low']),
                    'previous_close': info.get('previousClose'),
                    'market_cap': info.get('marketCap'),
                    'pe_ratio': info.get('trailingPE')
                }
            }
            
            # Update database if stock exists
            try:
                stock = Stock.objects.get(ticker=symbol)
                stock.current_price = current_price
                stock.price_change_today = change
                stock.change_percent = change_percent
                stock.volume = int(latest['Volume'])
                stock.save()
            except Stock.DoesNotExist:
                # Create new stock record
                Stock.objects.create(
                    ticker=symbol,
                    symbol=symbol,
                    company_name=info.get('longName', symbol),
                    name=info.get('longName', symbol),
                    current_price=current_price,
                    price_change_today=change,
                    change_percent=change_percent,
                    volume=int(latest['Volume']),
                    market_cap=info.get('marketCap'),
                    pe_ratio=info.get('trailingPE')
                )
            
            # Cache for 1 minute
            cache.set(cache_key, quote_data, 60)
            return Response(quote_data)
            
        except Exception as yf_error:
            logger.error(f"yfinance error for {symbol}: {yf_error}")
            return Response({
                'success': False,
                'error': f'Unable to fetch data for {symbol}',
                'symbol': symbol
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    except Exception as e:
        logger.error(f"Stock quote API error for {symbol}: {e}", exc_info=True)
        return Response({
            'success': False,
            'error': 'Internal server error',
            'symbol': symbol
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
def realtime_data_api(request, ticker):
    """
    Get comprehensive real-time data for ticker
    URL: /api/realtime/{ticker}/
    """
    try:
        # Get user for usage tracking
        user = getattr(request, 'user', None)
        
        # Track API usage
        if not track_api_usage(user, f'realtime_{ticker}'):
            return Response({
                'success': False,
                'error': 'API usage limit exceeded',
                'rate_limit_warning': True
            }, status=status.HTTP_429_TOO_MANY_REQUESTS)
        
        ticker = ticker.upper()
        
        # Check cache first
        cache_key = f"realtime_{ticker}"
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)
        
        # Get real-time data from yfinance
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            history = stock.history(period="1d", interval="1m")
            
            if history.empty:
                return Response({
                    'success': False,
                    'error': f'No real-time data available for {ticker}',
                    'ticker': ticker
                }, status=status.HTTP_404_NOT_FOUND)
            
            latest = history.iloc[-1]
            
            # Determine market status
            market_status = 'closed'
            if info.get('regularMarketTime'):
                market_status = 'open'
            
            realtime_data = {
                'success': True,
                'ticker': ticker,
                'company_name': info.get('longName', 'Unknown Company'),
                'current_price': float(latest['Close']),
                'volume': int(latest['Volume']),
                'market_cap': info.get('marketCap'),
                'pe_ratio': info.get('trailingPE'),
                'dividend_yield': info.get('dividendYield'),
                'last_updated': timezone.now().isoformat(),
                'market_status': market_status,
                'extended_data': {
                    'open': float(latest['Open']),
                    'high': float(latest['High']),
                    'low': float(latest['Low']),
                    'previous_close': info.get('previousClose'),
                    'day_range': f"{float(latest['Low']):.2f} - {float(latest['High']):.2f}",
                    'week_52_high': info.get('fiftyTwoWeekHigh'),
                    'week_52_low': info.get('fiftyTwoWeekLow'),
                    'avg_volume': info.get('averageVolume'),
                    'earnings_per_share': info.get('trailingEps'),
                    'beta': info.get('beta'),
                    'book_value': info.get('bookValue'),
                    'price_to_book': info.get('priceToBook')
                },
                'financial_ratios': {
                    'pe_ratio': info.get('trailingPE'),
                    'forward_pe': info.get('forwardPE'),
                    'peg_ratio': info.get('pegRatio'),
                    'price_to_sales': info.get('priceToSalesTrailing12Months'),
                    'price_to_book': info.get('priceToBook'),
                    'debt_to_equity': info.get('debtToEquity')
                }
            }
            
            # Cache for 30 seconds
            cache.set(cache_key, realtime_data, 30)
            return Response(realtime_data)
            
        except Exception as yf_error:
            logger.error(f"yfinance error for realtime {ticker}: {yf_error}")
            return Response({
                'success': False,
                'error': f'Unable to fetch real-time data for {ticker}',
                'ticker': ticker
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    except Exception as e:
        logger.error(f"Realtime API error for {ticker}: {e}", exc_info=True)
        return Response({
            'success': False,
            'error': 'Internal server error',
            'ticker': ticker
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
def batch_quotes_api(request):
    """
    Get quotes for multiple symbols at once
    URL: /api/stocks/quotes/batch/
    Query params: symbols=AAPL,GOOGL,MSFT
    """
    try:
        # Get user for usage tracking
        user = getattr(request, 'user', None)
        
        symbols_param = request.GET.get('symbols', '')
        if not symbols_param:
            return Response({
                'success': False,
                'error': 'symbols parameter is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        symbols = [s.strip().upper() for s in symbols_param.split(',') if s.strip()]
        if len(symbols) > 50:  # Limit batch size
            return Response({
                'success': False,
                'error': 'Maximum 50 symbols allowed per batch request'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Track API usage (count as multiple calls)
        for symbol in symbols:
            if not track_api_usage(user, f'batch_quote_{symbol}'):
                return Response({
                    'success': False,
                    'error': 'API usage limit exceeded',
                    'rate_limit_warning': True
                }, status=status.HTTP_429_TOO_MANY_REQUESTS)
        
        quotes = {}
        errors = []
        
        for symbol in symbols:
            try:
                # Check cache first
                cache_key = f"quote_{symbol}"
                cached_data = cache.get(cache_key)
                
                if cached_data:
                    quotes[symbol] = cached_data
                    continue
                
                # Get fresh data
                ticker = yf.Ticker(symbol)
                history = ticker.history(period="1d", interval="1m")
                
                if not history.empty:
                    latest = history.iloc[-1]
                    info = ticker.info
                    
                    current_price = float(latest['Close'])
                    open_price = float(latest['Open'])
                    change = current_price - open_price
                    change_percent = (change / open_price * 100) if open_price != 0 else 0
                    
                    quote_data = {
                        'symbol': symbol,
                        'price': current_price,
                        'change': change,
                        'change_percent': round(change_percent, 2),
                        'volume': int(latest['Volume']),
                        'timestamp': timezone.now().isoformat()
                    }
                    
                    quotes[symbol] = quote_data
                    cache.set(cache_key, quote_data, 60)
                else:
                    errors.append(f"No data for {symbol}")
                    
            except Exception as e:
                logger.error(f"Batch quote error for {symbol}: {e}")
                errors.append(f"Error fetching {symbol}: {str(e)}")
        
        return Response({
            'success': True,
            'quotes': quotes,
            'requested_symbols': symbols,
            'successful_count': len(quotes),
            'errors': errors,
            'timestamp': timezone.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Batch quotes API error: {e}", exc_info=True)
        return Response({
            'success': False,
            'error': 'Internal server error'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)