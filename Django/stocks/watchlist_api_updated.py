"""
Updated Watchlist API - RESTful watchlist management endpoints
Provides GET /api/watchlist, POST /api/watchlist/add, DELETE /api/watchlist/{id}
"""

from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.core.paginator import Paginator
import json
import logging

from .models import UserWatchlist, WatchlistItem, Stock
from .security_utils import secure_api_endpoint
from .authentication import CsrfExemptSessionAuthentication, BearerSessionAuthentication

logger = logging.getLogger(__name__)

@csrf_exempt
@api_view(['GET'])
@permission_classes([AllowAny])
def watchlist_api(request):
    """
    Get user's watchlist
    GET /api/watchlist
    """
    try:
        if not getattr(request, 'user', None) or not request.user.is_authenticated:
            return JsonResponse({
                'success': False,
                'error': 'Authentication required',
                'error_code': 'AUTH_REQUIRED'
            }, status=401)
        user = request.user
        
        # Get all watchlist items for the user
        watchlist_items = WatchlistItem.objects.filter(
            watchlist__user=user
        ).select_related('stock', 'watchlist')
        
        watchlist_data = []
        for item in watchlist_items:
            stock = item.stock
            
            # Calculate price change percentage
            current_price = float(getattr(stock, 'current_price', 0) or 0)
            price_change = float(getattr(stock, 'price_change', 0) or 0)
            price_change_percent = float(getattr(stock, 'price_change_percent', 0) or 0)
            
            watchlist_data.append({
                'id': str(item.id),
                'symbol': stock.ticker,
                'company_name': getattr(stock, 'company_name', stock.ticker),
                'current_price': current_price,
                'price_change': price_change,
                'price_change_percent': price_change_percent,
                'volume': getattr(stock, 'volume', 0) or 0,
                'market_cap': getattr(stock, 'market_cap', 0) or 0,
                'watchlist_name': item.watchlist.name,
                'added_date': item.created_at.isoformat() if hasattr(item, 'created_at') else timezone.now().isoformat(),
                'notes': getattr(item, 'notes', ''),
                'alert_price': getattr(item, 'alert_price', None)
            })
        
        # Sort by most recent first
        watchlist_data.sort(key=lambda x: x['added_date'], reverse=True)
        
        return JsonResponse({
            'success': True,
            'data': watchlist_data,
            'summary': {
                'total_items': len(watchlist_data),
                'gainers': len([item for item in watchlist_data if item['price_change'] > 0]),
                'losers': len([item for item in watchlist_data if item['price_change'] < 0]),
                'unchanged': len([item for item in watchlist_data if item['price_change'] == 0])
            }
        })
        
    except Exception as e:
        logger.error(f"Watchlist API error: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Failed to retrieve watchlist',
            'error_code': 'WATCHLIST_ERROR'
        }, status=500)

@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
@authentication_classes([BearerSessionAuthentication, CsrfExemptSessionAuthentication])
def watchlist_add_api(request):
    """
    Add a stock to watchlist
    POST /api/watchlist/add
    """
    try:
        if not getattr(request, 'user', None) or not request.user.is_authenticated:
            return JsonResponse({
                'success': False,
                'error': 'Authentication required',
                'error_code': 'AUTH_REQUIRED'
            }, status=401)
        data = json.loads(request.body) if request.body else {}
        user = request.user
        
        symbol = data.get('symbol', '').upper()
        watchlist_name = data.get('watchlist_name', 'My Watchlist')
        notes = data.get('notes', '')
        alert_price = data.get('alert_price', None)
        
        if not symbol:
            return JsonResponse({
                'success': False,
                'error': 'Stock symbol is required',
                'error_code': 'MISSING_SYMBOL'
            }, status=400)
        
        # Get or create stock
        try:
            stock = Stock.objects.get(ticker=symbol)
        except Stock.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': f'Stock {symbol} not found',
                'error_code': 'STOCK_NOT_FOUND'
            }, status=404)
        
        # Get or create user's watchlist
        watchlist, created = UserWatchlist.objects.get_or_create(
            user=user,
            name=watchlist_name,
            defaults={'description': f'Watchlist for {user.username}'}
        )
        
        # Check if item already exists in watchlist
        existing_item = WatchlistItem.objects.filter(
            watchlist=watchlist,
            stock=stock
        ).first()
        
        if existing_item:
            return JsonResponse({
                'success': False,
                'error': f'Stock {symbol} is already in your watchlist',
                'error_code': 'STOCK_ALREADY_IN_WATCHLIST'
            }, status=400)
        
        # Create new watchlist item
        new_item = WatchlistItem.objects.create(
            watchlist=watchlist,
            stock=stock,
            notes=notes,
            target_price=alert_price if alert_price is not None else None,
            added_price=float(getattr(stock, 'current_price', 0) or 0),
            current_price=float(getattr(stock, 'current_price', 0) or 0),
            added_at=timezone.now()
        )
        
        return JsonResponse({
            'success': True,
            'message': f'Stock {symbol} added to watchlist successfully',
            'data': {
                'id': str(new_item.id),
                'symbol': symbol,
                'company_name': getattr(stock, 'company_name', symbol),
                'current_price': float(new_item.current_price),
                'watchlist_name': watchlist.name,
                'notes': notes,
                'alert_price': float(alert_price) if alert_price else None,
                'added_date': new_item.added_at.isoformat()
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON format',
            'error_code': 'INVALID_JSON'
        }, status=400)
    except Exception as e:
        logger.error(f"Watchlist add error: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Failed to add stock to watchlist',
            'error_code': 'WATCHLIST_ADD_ERROR'
        }, status=500)

@csrf_exempt
@api_view(['DELETE'])
@permission_classes([AllowAny])
@authentication_classes([BearerSessionAuthentication, CsrfExemptSessionAuthentication])
def watchlist_delete_api(request, item_id):
    """
    Remove a stock from watchlist
    DELETE /api/watchlist/{id}
    """
    try:
        if not getattr(request, 'user', None) or not request.user.is_authenticated:
            return JsonResponse({
                'success': False,
                'error': 'Authentication required',
                'error_code': 'AUTH_REQUIRED'
            }, status=401)
        user = request.user
        
        # Find the watchlist item
        try:
            item = WatchlistItem.objects.get(
                id=item_id,
                watchlist__user=user
            )
        except WatchlistItem.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Watchlist item not found',
                'error_code': 'ITEM_NOT_FOUND'
            }, status=404)
        
        symbol = item.stock.ticker
        watchlist_name = item.watchlist.name
        
        # Delete the item
        item.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'Removed {symbol} from watchlist',
            'data': {
                'id': str(item_id),
                'symbol': symbol,
                'watchlist_name': watchlist_name
            }
        })
        
    except Exception as e:
        logger.error(f"Watchlist delete error: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Failed to remove item from watchlist',
            'error_code': 'WATCHLIST_DELETE_ERROR'
        }, status=500)