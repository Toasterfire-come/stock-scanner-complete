"""
Django REST API Views for WordPress Integration
Provides real-time stock data endpoints for WordPress frontend
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.cache import cache
from django.db.models import Q
from django.utils import timezone
from datetime import datetime, timedelta
import json
import logging

from .models import StockAlert
from emails.models import EmailSubscription

logger = logging.getLogger(__name__)

@api_view(['GET'])
@permission_classes([AllowAny])
def stock_list_api(request):
    """
    Get list of all stocks with basic info for WordPress
    
    URL: /api/stocks/
    Parameters:
    - limit: Number of stocks to return (default: 50)
    - search: Search by ticker or company name
    - category: Filter by category (gainers, losers, high_volume)
    """
    try:
        limit = int(request.GET.get('limit', 50))
        search = request.GET.get('search', '').strip()
        category = request.GET.get('category', '').strip()
        
        # Base queryset
        queryset = StockAlert.objects.all()
        
        # Apply search filter
        if search:
            queryset = queryset.filter(
                Q(ticker__icontains=search) | Q(company_name__icontains=search)
            )
        
        # Apply category filter
        if category == 'gainers':
            queryset = queryset.filter(price_change_today__gt=0).order_by('-price_change_today')
        elif category == 'losers':
            queryset = queryset.filter(price_change_today__lt=0).order_by('price_change_today')
        elif category == 'high_volume':
            queryset = queryset.order_by('-volume_today')
        else:
            queryset = queryset.order_by('-last_update')
        
        # Limit results
        stocks = queryset[:limit]
        
        # Format data for WordPress
        stock_data = []
        for stock in stocks:
            stock_data.append({
                'ticker': stock.ticker,
                'company_name': stock.company_name,
                'current_price': float(stock.current_price) if stock.current_price else 0,
                'price_change_today': float(stock.price_change_today) if stock.price_change_today else 0,
                'price_change_percent': calculate_price_change_percent(stock),
                'volume_today': int(stock.volume_today) if stock.volume_today else 0,
                'dvav': float(stock.dvav) if stock.dvav else 0,
                'dvsa': float(stock.dvsa) if stock.dvsa else 0,
                'pe_ratio': float(stock.pe_ratio) if stock.pe_ratio else 0,
                'market_cap': int(stock.market_cap) if stock.market_cap else 0,
                'last_update': stock.last_update.isoformat() if stock.last_update else None,
                'note': stock.note or '',
                'is_gaining': stock.price_change_today > 0 if stock.price_change_today else False,
                'wordpress_url': f"/stock/{stock.ticker.lower()}/"
            })
        
        return Response({
            'success': True,
            'count': len(stock_data),
            'data': stock_data,
            'timestamp': timezone.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in stock_list_api: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
def stock_detail_api(request, ticker):
    """
    Get detailed information for a specific stock
    
    URL: /api/stocks/{ticker}/
    """
    try:
        ticker = ticker.upper()
        
        # Get stock from database
        try:
            stock = StockAlert.objects.get(ticker=ticker)
        except StockAlert.DoesNotExist:
            return Response({
                'success': False,
                'error': f'Stock {ticker} not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Format detailed data
        stock_data = {
            'ticker': stock.ticker,
            'company_name': stock.company_name,
            'current_price': float(stock.current_price) if stock.current_price else 0,
            'price_change_today': float(stock.price_change_today) if stock.price_change_today else 0,
            'price_change_percent': calculate_price_change_percent(stock),
            'volume_today': int(stock.volume_today) if stock.volume_today else 0,
            'average_volume': int(stock.average_volume) if stock.average_volume else 0,
            'dvav': float(stock.dvav) if stock.dvav else 0,
            'dvsa': float(stock.dvsa) if stock.dvsa else 0,
            'pe_ratio': float(stock.pe_ratio) if stock.pe_ratio else 0,
            'market_cap': int(stock.market_cap) if stock.market_cap else 0,
            'shares_outstanding': int(stock.shares_outstanding) if stock.shares_outstanding else 0,
            'dividend_yield': float(stock.dividend_yield) if stock.dividend_yield else 0,
            'fifty_two_week_high': float(stock.fifty_two_week_high) if stock.fifty_two_week_high else 0,
            'fifty_two_week_low': float(stock.fifty_two_week_low) if stock.fifty_two_week_low else 0,
            'beta': float(stock.beta) if stock.beta else 0,
            'rsi': float(stock.rsi) if stock.rsi else 0,
            'last_update': stock.last_update.isoformat() if stock.last_update else None,
            'note': stock.note or '',
            'sent': stock.sent,
            'created_at': stock.created_at.isoformat() if stock.created_at else None,
            
            # Additional calculated fields
            'is_gaining': stock.price_change_today > 0 if stock.price_change_today else False,
            'volume_ratio': calculate_volume_ratio(stock),
            'price_near_high': calculate_price_near_high(stock),
            'price_near_low': calculate_price_near_low(stock),
            'technical_rating': calculate_technical_rating(stock),
            
            # WordPress integration
            'wordpress_url': f"/stock/{stock.ticker.lower()}/",
            'related_posts_url': f"/wp/search/?q={stock.ticker}",
        }
        
        return Response({
            'success': True,
            'data': stock_data,
            'timestamp': timezone.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in stock_detail_api for {ticker}: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
def market_movers_api(request):
    """
    Get market movers (gainers, losers, most active)
    
    URL: /api/market-movers/
    Parameters:
    - type: gainers, losers, or volume (default: gainers)
    - limit: Number of stocks to return (default: 10)
    """
    try:
        mover_type = request.GET.get('type', 'gainers').lower()
        limit = int(request.GET.get('limit', 10))
        
        # Cache key for this request
        cache_key = f"market_movers_{mover_type}_{limit}"
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return Response(cached_data)
        
        # Get stocks based on type
        if mover_type == 'gainers':
            stocks = StockAlert.objects.filter(
                price_change_today__gt=0
            ).order_by('-price_change_today')[:limit]
        elif mover_type == 'losers':
            stocks = StockAlert.objects.filter(
                price_change_today__lt=0
            ).order_by('price_change_today')[:limit]
        elif mover_type == 'volume':
            stocks = StockAlert.objects.filter(
                volume_today__gt=0
            ).order_by('-volume_today')[:limit]
        else:
            return Response({
                'success': False,
                'error': 'Invalid type. Use: gainers, losers, or volume'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Format data
        movers_data = []
        for stock in stocks:
            movers_data.append({
                'ticker': stock.ticker,
                'company_name': stock.company_name,
                'current_price': float(stock.current_price) if stock.current_price else 0,
                'price_change_today': float(stock.price_change_today) if stock.price_change_today else 0,
                'price_change_percent': calculate_price_change_percent(stock),
                'volume_today': int(stock.volume_today) if stock.volume_today else 0,
                'volume_ratio': calculate_volume_ratio(stock),
                'last_update': stock.last_update.isoformat() if stock.last_update else None,
                'wordpress_url': f"/stock/{stock.ticker.lower()}/"
            })
        
        response_data = {
            'success': True,
            'type': mover_type,
            'count': len(movers_data),
            'data': movers_data,
            'timestamp': timezone.now().isoformat()
        }
        
        # Cache for 2 minutes
        cache.set(cache_key, response_data, 120)
        
        return Response(response_data)
        
    except Exception as e:
        logger.error(f"Error in market_movers_api: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
def stock_search_api(request):
    """
    Search stocks by ticker or company name
    
    URL: /api/stocks/search/
    Parameters:
    - q: Search query (required)
    - limit: Number of results (default: 20)
    """
    try:
        query = request.GET.get('q', '').strip()
        limit = int(request.GET.get('limit', 20))
        
        if not query:
            return Response({
                'success': False,
                'error': 'Search query (q) is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Search stocks
        stocks = StockAlert.objects.filter(
            Q(ticker__icontains=query) | Q(company_name__icontains=query)
        ).order_by('-last_update')[:limit]
        
        # Format results
        search_results = []
        for stock in stocks:
            search_results.append({
                'ticker': stock.ticker,
                'company_name': stock.company_name,
                'current_price': float(stock.current_price) if stock.current_price else 0,
                'price_change_today': float(stock.price_change_today) if stock.price_change_today else 0,
                'price_change_percent': calculate_price_change_percent(stock),
                'last_update': stock.last_update.isoformat() if stock.last_update else None,
                'wordpress_url': f"/stock/{stock.ticker.lower()}/"
            })
        
        return Response({
            'success': True,
            'query': query,
            'count': len(search_results),
            'data': search_results,
            'timestamp': timezone.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in stock_search_api: {e}")
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
        total_stocks = StockAlert.objects.count()
        gainers = StockAlert.objects.filter(price_change_today__gt=0).count()
        losers = StockAlert.objects.filter(price_change_today__lt=0).count()
        unchanged = total_stocks - gainers - losers
        
        # Recent updates
        recent_updates = StockAlert.objects.filter(
            last_update__gte=timezone.now() - timedelta(hours=24)
        ).count()
        
        # Top performers
        top_gainer = StockAlert.objects.filter(
            price_change_today__gt=0
        ).order_by('-price_change_today').first()
        
        top_loser = StockAlert.objects.filter(
            price_change_today__lt=0
        ).order_by('price_change_today').first()
        
        most_active = StockAlert.objects.filter(
            volume_today__gt=0
        ).order_by('-volume_today').first()
        
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
                    'company_name': top_gainer.company_name if top_gainer else None,
                    'price_change_percent': calculate_price_change_percent(top_gainer) if top_gainer else 0,
                    'wordpress_url': f"/stock/{top_gainer.ticker.lower()}/" if top_gainer else None
                } if top_gainer else None,
                'top_loser': {
                    'ticker': top_loser.ticker if top_loser else None,
                    'company_name': top_loser.company_name if top_loser else None,
                    'price_change_percent': calculate_price_change_percent(top_loser) if top_loser else 0,
                    'wordpress_url': f"/stock/{top_loser.ticker.lower()}/" if top_loser else None
                } if top_loser else None,
                'most_active': {
                    'ticker': most_active.ticker if most_active else None,
                    'company_name': most_active.company_name if most_active else None,
                    'volume_today': int(most_active.volume_today) if most_active and most_active.volume_today else 0,
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
        if 30 <= rsi <= 70:  # Neutral zone
            score += 1
        elif rsi > 70:  # Overbought
            score -= 1
        elif rsi < 30:  # Oversold
            score += 2
    
    # Price change check
    if stock.price_change_today:
        if float(stock.price_change_today) > 0:
            score += 1
        else:
            score -= 1
    
    # Volume check
    volume_ratio = calculate_volume_ratio(stock)
    if volume_ratio > 1.5:  # High volume
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
@require_http_methods(["GET", "POST", "OPTIONS"])
def cors_handler(request):
    """Handle CORS preflight requests for WordPress"""
    response = JsonResponse({'status': 'ok'})
    response["Access-Control-Allow-Origin"] = "*"
    response["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return response