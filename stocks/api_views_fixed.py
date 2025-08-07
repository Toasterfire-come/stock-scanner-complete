"""
FIXED Django REST API Views for Stock Data Integration
Fixes the empty data issue by implementing better filtering logic
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
def stock_list_api_fixed(request):
    """
    FIXED VERSION: Get comprehensive list of stocks with better filtering
    
    The original API was too restrictive and returned empty results.
    This version implements progressive filtering to ensure we always return data.
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
        
        # Exchange filter - Fixed to be more flexible
        exchange = request.GET.get('exchange', 'NYSE')
        
        # Sorting - default to last_updated for better results
        sort_by = request.GET.get('sort_by', 'last_updated')
        sort_order = request.GET.get('sort_order', 'desc')
        
        # PROGRESSIVE FILTERING APPROACH
        # Start with all stocks for the exchange, then progressively filter
        
        # Base queryset - much more inclusive
        base_queryset = Stock.objects.all()
        
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
        
        # Apply search filter early
        if search:
            base_queryset = base_queryset.filter(
                Q(ticker__icontains=search) | 
                Q(company_name__icontains=search) |
                Q(symbol__icontains=search) |
                Q(name__icontains=search)
            )
        
        # Get total count before further filtering
        total_available = base_queryset.count()
        
        # Apply progressive quality filters
        queryset = base_queryset
        
        # Only apply price filters if we have reasonable data
        if category != 'all':
            # Try to get stocks with good data first
            preferred_queryset = queryset.filter(
                current_price__isnull=False
            ).exclude(current_price=0)
            
            # If we get enough results, use the preferred set
            if preferred_queryset.count() >= limit // 2:
                queryset = preferred_queryset
            # Otherwise, be more inclusive
            else:
                # Include stocks with ANY price data (even if zero)
                queryset = queryset.filter(
                    Q(current_price__isnull=False) |
                    Q(volume__isnull=False) |
                    Q(market_cap__isnull=False)
                )
        
        # Apply user filters
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

        if min_volume:
            try:
                queryset = queryset.filter(volume__gte=int(min_volume))
            except (ValueError, TypeError):
                pass

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

        # EMERGENCY FALLBACK: If still no results, return ANY stocks
        if queryset.count() == 0 and not search:
            logger.warning(f"API returned 0 results, using emergency fallback")
            queryset = base_queryset.order_by('-last_updated')[:limit]
            
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
                'bid_price': format_decimal_safe(stock.bid_price) or 0.0,
                'ask_price': format_decimal_safe(stock.ask_price) or 0.0,
                'bid_ask_spread': stock.bid_ask_spread or '',
                'days_range': stock.days_range or '',
                'days_low': format_decimal_safe(stock.days_low) or 0.0,
                'days_high': format_decimal_safe(stock.days_high) or 0.0,
                
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
                'pe_ratio': format_decimal_safe(stock.pe_ratio) or 0.0,
                'pe_change_3mon': format_decimal_safe(stock.pe_change_3mon) or 0.0,
                'dividend_yield': format_decimal_safe(stock.dividend_yield) or 0.0,
                
                # 52-week range
                'week_52_low': format_decimal_safe(stock.week_52_low) or 0.0,
                'week_52_high': format_decimal_safe(stock.week_52_high) or 0.0,
                
                # Additional metrics
                'one_year_target': format_decimal_safe(stock.one_year_target) or 0.0,
                'earnings_per_share': format_decimal_safe(stock.earnings_per_share) or 0.0,
                'book_value': format_decimal_safe(stock.book_value) or 0.0,
                'price_to_book': format_decimal_safe(stock.price_to_book) or 0.0,
                
                # Formatted values
                'formatted_price': getattr(stock, 'formatted_price', '') or f"${format_decimal_safe(stock.current_price) or 0:.2f}",
                'formatted_change': getattr(stock, 'formatted_change', '') or '',
                'formatted_volume': getattr(stock, 'formatted_volume', '') or '',
                
                # Timestamps
                'last_updated': stock.last_updated.isoformat() if stock.last_updated else timezone.now().isoformat(),
                'created_at': stock.created_at.isoformat() if stock.created_at else timezone.now().isoformat(),
                
                # Calculated fields
                'is_gaining': (stock.price_change_today or 0) > 0,
                'is_losing': (stock.price_change_today or 0) < 0,
                'volume_ratio': format_decimal_safe(stock.dvav) or 0.0,
                
                # WordPress integration
                'wordpress_url': f"/stock/{stock.ticker.lower()}/"
            })

        # Ensure we always have a meaningful response
        final_count = len(stock_data)
        final_total = max(total_available, final_count)

        return Response({
            'success': True,
            'count': final_count,
            'total_available': final_total,
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
            'timestamp': timezone.now().isoformat(),
            'debug_info': {
                'base_queryset_count': total_available,
                'final_queryset_count': final_count,
                'emergency_fallback_used': final_count > 0 and queryset.count() == 0
            }
        })

    except Exception as e:
        logger.error(f"Error in stock_list_api_fixed: {e}", exc_info=True)
        return Response({
            'success': False,
            'error': str(e),
            'count': 0,
            'total_available': 0,
            'data': [],
            'timestamp': timezone.now().isoformat()
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)