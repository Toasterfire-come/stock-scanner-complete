"""
Watchlist API - Comprehensive watchlist APIs with import/export functionality.
Provides endpoints for watchlist CRUD operations, performance tracking, import/export,
and real-time performance updates with comprehensive security and validation.
"""

import json
import logging
from decimal import Decimal
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.views.decorators.csrf import csrf_exempt
from .security_utils import (
    secure_api_endpoint, validate_user_input, 
    WATCHLIST_SCHEMA
)
from .watchlist_service import WatchlistService
from .plan_limits import get_limits_for_user, is_within_limit
from .models import UserWatchlist, WatchlistItem, Stock

logger = logging.getLogger(__name__)

@csrf_exempt
@secure_api_endpoint(methods=['POST'])
def create_watchlist(request):
    """
    Create a new watchlist for the user.
    
    POST /api/watchlist/create/
    
    Body:
    {
        "name": "Tech Stocks",
        "description": "Technology sector watchlist"
    }
    """
    try:
        # Validate input
        validated_data = validate_user_input(request.validated_data, WATCHLIST_SCHEMA)
        
        # Enforce per-plan watchlists
        limits = get_limits_for_user(request.user)
        existing = UserWatchlist.objects.filter(user=request.user).count()
        if not is_within_limit(request.user, 'watchlists', existing):
            return JsonResponse({
                'success': False,
                'error': 'Watchlist limit reached for your plan',
                'error_code': 'WATCHLIST_LIMIT'
            }, status=429)
        # Create watchlist
        watchlist = WatchlistService.create_watchlist(
            user=request.user,
            name=validated_data['name'],
            description=validated_data.get('description', '')
        )
        
        return JsonResponse({
            'success': True,
            'data': {
                'watchlist_id': watchlist.id,
                'name': watchlist.name,
                'description': watchlist.description,
                'created_at': watchlist.created_at.isoformat()
            },
            'message': 'Watchlist created successfully'
        })
        
    except ValidationError as e:
        return JsonResponse({
            'success': False,
            'error': str(e),
            'error_code': 'VALIDATION_ERROR'
        }, status=400)
    except Exception as e:
        logger.error(f"Error in create_watchlist: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Failed to create watchlist',
            'error_code': 'CREATION_ERROR'
        }, status=500)

@csrf_exempt
@secure_api_endpoint(methods=['POST'])
def add_stock(request):
    """
    Add a stock to a watchlist.
    
    POST /api/watchlist/add-stock/
    
    Body:
    {
        "watchlist_id": 1,
        "stock_ticker": "AAPL",
        "added_price": 150.00,
        "notes": "Good growth potential",
        "target_price": 180.00,
        "stop_loss": 140.00,
        "price_alert_enabled": true,
        "news_alert_enabled": false
    }
    """
    try:
        # Validate input
        schema = {
            'watchlist_id': {'type': 'integer', 'required': True, 'min_value': 1},
            'stock_ticker': {'type': 'ticker', 'required': True},
            'added_price': {'type': 'decimal', 'min_value': 0.01, 'decimal_places': 4},
            'notes': {'type': 'string', 'max_length': 1000, 'default': ''},
            'target_price': {'type': 'decimal', 'min_value': 0.01, 'decimal_places': 4},
            'stop_loss': {'type': 'decimal', 'min_value': 0.01, 'decimal_places': 4},
            'price_alert_enabled': {'type': 'boolean', 'default': False},
            'news_alert_enabled': {'type': 'boolean', 'default': False}
        }
        validated_data = validate_user_input(request.validated_data, schema)
        
        # Get watchlist
        try:
            watchlist = UserWatchlist.objects.get(
                id=validated_data['watchlist_id'], 
                user=request.user
            )
        except UserWatchlist.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Watchlist not found',
                'error_code': 'WATCHLIST_NOT_FOUND'
            }, status=404)
        
        # Add stock to watchlist
        item = WatchlistService.add_stock_to_watchlist(
            watchlist=watchlist,
            stock_ticker=validated_data['stock_ticker'],
            added_price=validated_data.get('added_price'),
            notes=validated_data.get('notes', ''),
            target_price=validated_data.get('target_price'),
            stop_loss=validated_data.get('stop_loss'),
            price_alert_enabled=validated_data.get('price_alert_enabled', False),
            news_alert_enabled=validated_data.get('news_alert_enabled', False)
        )
        
        return JsonResponse({
            'success': True,
            'data': {
                'item_id': item.id,
                'watchlist_id': watchlist.id,
                'stock_ticker': item.stock.ticker,
                'added_price': float(item.added_price),
                'current_price': float(item.current_price),
                'price_change': float(item.price_change),
                'price_change_percent': float(item.price_change_percent),
                'notes': item.notes,
                'target_price': float(item.target_price) if item.target_price else None,
                'stop_loss': float(item.stop_loss) if item.stop_loss else None,
                'price_alert_enabled': item.price_alert_enabled,
                'news_alert_enabled': item.news_alert_enabled,
                'added_at': item.added_at.isoformat()
            },
            'message': 'Stock added to watchlist successfully'
        })
        
    except ValidationError as e:
        return JsonResponse({
            'success': False,
            'error': str(e),
            'error_code': 'VALIDATION_ERROR'
        }, status=400)
    except Exception as e:
        logger.error(f"Error in add_stock: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Failed to add stock to watchlist',
            'error_code': 'ADD_ERROR'
        }, status=500)

@csrf_exempt
@secure_api_endpoint(methods=['DELETE'])
def remove_stock(request):
    """
    Remove a stock from a watchlist.
    
    DELETE /api/watchlist/remove-stock/
    
    Body:
    {
        "watchlist_id": 1,
        "stock_ticker": "AAPL"
    }
    """
    try:
        # Validate input
        schema = {
            'watchlist_id': {'type': 'integer', 'required': True, 'min_value': 1},
            'stock_ticker': {'type': 'ticker', 'required': True}
        }
        validated_data = validate_user_input(request.validated_data, schema)
        
        # Get watchlist
        try:
            watchlist = UserWatchlist.objects.get(
                id=validated_data['watchlist_id'], 
                user=request.user
            )
        except UserWatchlist.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Watchlist not found',
                'error_code': 'WATCHLIST_NOT_FOUND'
            }, status=404)
        
        # Remove stock from watchlist
        success = WatchlistService.remove_stock_from_watchlist(
            watchlist=watchlist,
            stock_ticker=validated_data['stock_ticker']
        )
        
        if success:
            return JsonResponse({
                'success': True,
                'data': {
                    'watchlist_id': watchlist.id,
                    'stock_ticker': validated_data['stock_ticker']
                },
                'message': 'Stock removed from watchlist successfully'
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Failed to remove stock from watchlist',
                'error_code': 'REMOVE_ERROR'
            }, status=400)
        
    except ValidationError as e:
        return JsonResponse({
            'success': False,
            'error': str(e),
            'error_code': 'VALIDATION_ERROR'
        }, status=400)
    except Exception as e:
        logger.error(f"Error in remove_stock: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Failed to remove stock from watchlist',
            'error_code': 'REMOVE_ERROR'
        }, status=500)

@csrf_exempt
@secure_api_endpoint(methods=['GET'])
def list_watchlists(request):
    """
    Get all watchlists for the user with basic performance metrics.
    
    GET /api/watchlist/list/
    """
    try:
        watchlists = WatchlistService.get_user_watchlists(request.user)
        
        return JsonResponse({
            'success': True,
            'data': {
                'watchlists': watchlists,
                'count': len(watchlists)
            },
            'message': 'Watchlists retrieved successfully'
        })
        
    except Exception as e:
        logger.error(f"Error in list_watchlists: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Failed to retrieve watchlists',
            'error_code': 'RETRIEVAL_ERROR'
        }, status=500)

@csrf_exempt
@secure_api_endpoint(methods=['GET'])
def watchlist_performance(request, watchlist_id):
    """
    Get comprehensive watchlist performance metrics.
    
    GET /api/watchlist/{watchlist_id}/performance/
    """
    try:
        # Validate watchlist access
        try:
            watchlist = UserWatchlist.objects.get(id=watchlist_id, user=request.user)
        except UserWatchlist.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Watchlist not found',
                'error_code': 'WATCHLIST_NOT_FOUND'
            }, status=404)
        
        # Get performance data
        performance = WatchlistService.get_watchlist_performance(watchlist)
        
        return JsonResponse({
            'success': True,
            'data': performance,
            'message': 'Watchlist performance retrieved successfully'
        })
        
    except Exception as e:
        logger.error(f"Error in watchlist_performance: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Failed to retrieve watchlist performance',
            'error_code': 'PERFORMANCE_ERROR'
        }, status=500)

@csrf_exempt
@secure_api_endpoint(methods=['GET'])
def export_csv(request, watchlist_id):
    """
    Export watchlist to CSV format.
    
    GET /api/watchlist/{watchlist_id}/export/csv/
    """
    try:
        # Validate watchlist access
        try:
            watchlist = UserWatchlist.objects.get(id=watchlist_id, user=request.user)
        except UserWatchlist.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Watchlist not found',
                'error_code': 'WATCHLIST_NOT_FOUND'
            }, status=404)
        
        # Export to CSV
        csv_content = WatchlistService.export_watchlist_to_csv(watchlist)
        
        # Create HTTP response with CSV content
        response = HttpResponse(csv_content, content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{watchlist.name}_watchlist.csv"'
        
        return response
        
    except Exception as e:
        logger.error(f"Error in export_csv: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Failed to export watchlist to CSV',
            'error_code': 'EXPORT_ERROR'
        }, status=500)

@csrf_exempt
@secure_api_endpoint(methods=['GET'])
def export_json(request, watchlist_id):
    """
    Export watchlist to JSON format.
    
    GET /api/watchlist/{watchlist_id}/export/json/
    """
    try:
        # Validate watchlist access
        try:
            watchlist = UserWatchlist.objects.get(id=watchlist_id, user=request.user)
        except UserWatchlist.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Watchlist not found',
                'error_code': 'WATCHLIST_NOT_FOUND'
            }, status=404)
        
        # Export to JSON
        json_content = WatchlistService.export_watchlist_to_json(watchlist)
        
        # Create HTTP response with JSON content
        response = HttpResponse(json_content, content_type='application/json')
        response['Content-Disposition'] = f'attachment; filename="{watchlist.name}_watchlist.json"'
        
        return response
        
    except Exception as e:
        logger.error(f"Error in export_json: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Failed to export watchlist to JSON',
            'error_code': 'EXPORT_ERROR'
        }, status=500)

@csrf_exempt
@secure_api_endpoint(methods=['POST'])
def import_csv(request):
    """
    Import watchlist from CSV.
    
    POST /api/watchlist/import/csv/
    
    Body:
    {
        "watchlist_name": "Imported Watchlist",
        "csv_content": "ticker,added_price,notes,target_price,stop_loss,price_alert_enabled,news_alert_enabled\nAAPL,150.00,Good stock,180.00,140.00,true,false\n..."
    }
    """
    try:
        # Validate input
        schema = {
            'watchlist_name': {
                'type': 'string',
                'required': True,
                'min_length': 1,
                'max_length': 100
            },
            'csv_content': {
                'type': 'string',
                'required': True,
                'min_length': 1
            }
        }
        validated_data = validate_user_input(request.validated_data, schema)
        
        # Import watchlist
        result = WatchlistService.import_watchlist_from_csv(
            user=request.user,
            watchlist_name=validated_data['watchlist_name'],
            csv_content=validated_data['csv_content']
        )
        
        return JsonResponse({
            'success': True,
            'data': result,
            'message': 'Watchlist imported successfully'
        })
        
    except ValidationError as e:
        return JsonResponse({
            'success': False,
            'error': str(e),
            'error_code': 'VALIDATION_ERROR'
        }, status=400)
    except Exception as e:
        logger.error(f"Error in import_csv: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Failed to import watchlist',
            'error_code': 'IMPORT_ERROR'
        }, status=500)

@csrf_exempt
@secure_api_endpoint(methods=['POST'])
def import_json(request):
    """
    Import watchlist from JSON.
    
    POST /api/watchlist/import/json/
    
    Body:
    {
        "json_content": "{\"watchlist_info\": {\"name\": \"My Watchlist\", \"description\": \"...\"},\"items\": [...]}"
    }
    """
    try:
        # Validate input
        schema = {
            'json_content': {
                'type': 'string',
                'required': True,
                'min_length': 1
            }
        }
        validated_data = validate_user_input(request.validated_data, schema)
        
        # Import watchlist
        result = WatchlistService.import_watchlist_from_json(
            user=request.user,
            json_content=validated_data['json_content']
        )
        
        return JsonResponse({
            'success': True,
            'data': result,
            'message': 'Watchlist imported successfully'
        })
        
    except ValidationError as e:
        return JsonResponse({
            'success': False,
            'error': str(e),
            'error_code': 'VALIDATION_ERROR'
        }, status=400)
    except Exception as e:
        logger.error(f"Error in import_json: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Failed to import watchlist',
            'error_code': 'IMPORT_ERROR'
        }, status=500)

@csrf_exempt
@secure_api_endpoint(methods=['PUT'])
def update_watchlist(request, watchlist_id):
    """
    Update watchlist information.
    
    PUT /api/watchlist/{watchlist_id}/
    
    Body:
    {
        "name": "Updated Watchlist Name",
        "description": "Updated description"
    }
    """
    try:
        # Validate watchlist access
        try:
            watchlist = UserWatchlist.objects.get(id=watchlist_id, user=request.user)
        except UserWatchlist.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Watchlist not found',
                'error_code': 'WATCHLIST_NOT_FOUND'
            }, status=404)
        
        # Validate input
        schema = {
            'name': {'type': 'string', 'min_length': 1, 'max_length': 100},
            'description': {'type': 'string', 'max_length': 1000}
        }
        validated_data = validate_user_input(request.validated_data, schema)
        
        # Update watchlist fields
        if 'name' in validated_data:
            watchlist.name = validated_data['name']
        if 'description' in validated_data:
            watchlist.description = validated_data['description']
        
        watchlist.save()
        
        return JsonResponse({
            'success': True,
            'data': {
                'watchlist_id': watchlist.id,
                'name': watchlist.name,
                'description': watchlist.description,
                'updated_at': watchlist.updated_at.isoformat()
            },
            'message': 'Watchlist updated successfully'
        })
        
    except ValidationError as e:
        return JsonResponse({
            'success': False,
            'error': str(e),
            'error_code': 'VALIDATION_ERROR'
        }, status=400)
    except Exception as e:
        logger.error(f"Error in update_watchlist: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Failed to update watchlist',
            'error_code': 'UPDATE_ERROR'
        }, status=500)

@csrf_exempt
@secure_api_endpoint(methods=['PUT'])
def update_watchlist_item(request, item_id):
    """
    Update a watchlist item.
    
    PUT /api/watchlist/item/{item_id}/
    
    Body:
    {
        "notes": "Updated notes",
        "target_price": 200.00,
        "stop_loss": 150.00,
        "price_alert_enabled": true,
        "news_alert_enabled": true
    }
    """
    try:
        # Validate item access
        try:
            item = WatchlistItem.objects.get(
                id=item_id, 
                watchlist__user=request.user
            )
        except WatchlistItem.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Watchlist item not found',
                'error_code': 'ITEM_NOT_FOUND'
            }, status=404)
        
        # Validate input
        schema = {
            'notes': {'type': 'string', 'max_length': 1000},
            'target_price': {'type': 'decimal', 'min_value': 0.01, 'decimal_places': 4},
            'stop_loss': {'type': 'decimal', 'min_value': 0.01, 'decimal_places': 4},
            'price_alert_enabled': {'type': 'boolean'},
            'news_alert_enabled': {'type': 'boolean'}
        }
        validated_data = validate_user_input(request.validated_data, schema)
        
        # Update item
        updated_item = WatchlistService.update_watchlist_item(item, **validated_data)
        
        return JsonResponse({
            'success': True,
            'data': {
                'item_id': updated_item.id,
                'watchlist_id': updated_item.watchlist.id,
                'stock_ticker': updated_item.stock.ticker,
                'notes': updated_item.notes,
                'target_price': float(updated_item.target_price) if updated_item.target_price else None,
                'stop_loss': float(updated_item.stop_loss) if updated_item.stop_loss else None,
                'price_alert_enabled': updated_item.price_alert_enabled,
                'news_alert_enabled': updated_item.news_alert_enabled,
                'current_price': float(updated_item.current_price),
                'price_change_percent': float(updated_item.price_change_percent)
            },
            'message': 'Watchlist item updated successfully'
        })
        
    except ValidationError as e:
        return JsonResponse({
            'success': False,
            'error': str(e),
            'error_code': 'VALIDATION_ERROR'
        }, status=400)
    except Exception as e:
        logger.error(f"Error in update_watchlist_item: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Failed to update watchlist item',
            'error_code': 'UPDATE_ERROR'
        }, status=500)

@csrf_exempt
@secure_api_endpoint(methods=['DELETE'])
def delete_watchlist(request, watchlist_id):
    """
    Delete a watchlist and all its items.
    
    DELETE /api/watchlist/{watchlist_id}/
    """
    try:
        # Validate watchlist access
        try:
            watchlist = UserWatchlist.objects.get(id=watchlist_id, user=request.user)
        except UserWatchlist.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Watchlist not found',
                'error_code': 'WATCHLIST_NOT_FOUND'
            }, status=404)
        
        # Delete watchlist
        success = WatchlistService.delete_watchlist(watchlist)
        
        if success:
            return JsonResponse({
                'success': True,
                'data': {
                    'watchlist_id': watchlist_id
                },
                'message': 'Watchlist deleted successfully'
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Failed to delete watchlist',
                'error_code': 'DELETE_ERROR'
            }, status=400)
        
    except Exception as e:
        logger.error(f"Error in delete_watchlist: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Failed to delete watchlist',
            'error_code': 'DELETE_ERROR'
        }, status=500)