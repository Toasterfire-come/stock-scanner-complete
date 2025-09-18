"""
Updated Portfolio API - RESTful portfolio management endpoints
Provides GET /api/portfolio, POST /api/portfolio/add, DELETE /api/portfolio/{id}
"""

from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.core.paginator import Paginator
from django.db.models import Sum, F
import json
import logging
from decimal import Decimal
import uuid

from .models import UserPortfolio, PortfolioHolding, Stock
from .security_utils import secure_api_endpoint
from .authentication import CsrfExemptSessionAuthentication, BearerSessionAuthentication

logger = logging.getLogger(__name__)

def _effective_user(request):
    try:
        from django.conf import settings as django_settings
        testing = getattr(django_settings, 'TESTING_DISABLE_AUTH', False)
    except Exception:
        testing = False
    if testing:
        try:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            if getattr(request, 'user', None) and getattr(request.user, 'is_authenticated', False):
                return request.user
            user, _ = User.objects.get_or_create(
                username='test_user',
                defaults={'email': 'carter.kiefer2010@outlook.com', 'is_active': True}
            )
            return user
        except Exception:
            pass
    return request.user

@csrf_exempt
@api_view(['GET'])
@permission_classes([AllowAny])
def portfolio_api(request):
    """
    Get user's portfolio holdings
    GET /api/portfolio
    """
    try:
        # Skip auth check in testing mode
        try:
            from django.conf import settings as django_settings
            testing = getattr(django_settings, 'TESTING_DISABLE_AUTH', False)
        except Exception:
            testing = False
        if not testing:
            if not getattr(request, 'user', None) or not request.user.is_authenticated:
                return JsonResponse({
                    'success': False,
                    'error': 'Authentication required',
                    'error_code': 'AUTH_REQUIRED'
                }, status=401)
        user = _effective_user(request)
        
        # Get all portfolio holdings for the user
        holdings = PortfolioHolding.objects.filter(
            portfolio__user=user
        ).select_related('stock', 'portfolio')
        
        portfolio_data = []
        for holding in holdings:
            # Calculate current values
            current_price = float(getattr(holding.stock, 'current_price', 0) or getattr(holding, 'current_price', 0))
            shares = float(holding.shares)
            avg_cost = float(holding.average_cost)
            
            total_value = current_price * shares
            total_cost = avg_cost * shares
            gain_loss = total_value - total_cost
            gain_loss_percent = (gain_loss / total_cost * 100) if total_cost > 0 else 0
            
            portfolio_data.append({
                'id': str(holding.id),  # Use UUID format as per spec
                'symbol': holding.stock.ticker,
                'shares': shares,
                'avg_cost': avg_cost,
                'current_price': current_price,
                'total_value': round(total_value, 2),
                'gain_loss': round(gain_loss, 2),
                'gain_loss_percent': round(gain_loss_percent, 2),
                'portfolio_name': holding.portfolio.name,
                'added_date': holding.date_added.isoformat() if hasattr(holding, 'date_added') and holding.date_added else timezone.now().isoformat()
            })
        
        # Calculate portfolio summary
        total_portfolio_value = sum(item['total_value'] for item in portfolio_data)
        total_gain_loss = sum(item['gain_loss'] for item in portfolio_data)
        total_cost = total_portfolio_value - total_gain_loss
        overall_gain_loss_percent = (total_gain_loss / total_cost * 100) if total_cost > 0 else 0
        
        return JsonResponse({
            'success': True,
            'data': portfolio_data,
            'summary': {
                'total_value': round(total_portfolio_value, 2),
                'total_gain_loss': round(total_gain_loss, 2),
                'total_gain_loss_percent': round(overall_gain_loss_percent, 2),
                'total_holdings': len(portfolio_data)
            }
        })
        
    except Exception as e:
        logger.error(f"Portfolio API error: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Failed to retrieve portfolio',
            'error_code': 'PORTFOLIO_ERROR'
        }, status=500)

@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
@authentication_classes([BearerSessionAuthentication, CsrfExemptSessionAuthentication])
def portfolio_add_api(request):
    """
    Add a stock to portfolio
    POST /api/portfolio/add
    """
    try:
        try:
            from django.conf import settings as django_settings
            testing = getattr(django_settings, 'TESTING_DISABLE_AUTH', False)
        except Exception:
            testing = False
        if not testing:
            if not getattr(request, 'user', None) or not request.user.is_authenticated:
                return JsonResponse({
                    'success': False,
                    'error': 'Authentication required',
                    'error_code': 'AUTH_REQUIRED'
                }, status=401)
        data = json.loads(request.body) if request.body else {}
        user = _effective_user(request)
        
        symbol = data.get('symbol', '').upper()
        shares = data.get('shares', 0)
        avg_cost = data.get('avg_cost', 0)
        portfolio_name = data.get('portfolio_name', 'My Portfolio')
        
        if not symbol:
            return JsonResponse({
                'success': False,
                'error': 'Stock symbol is required',
                'error_code': 'MISSING_SYMBOL'
            }, status=400)
        
        if not shares or shares <= 0:
            return JsonResponse({
                'success': False,
                'error': 'Valid number of shares is required',
                'error_code': 'INVALID_SHARES'
            }, status=400)
        
        if not avg_cost or avg_cost <= 0:
            return JsonResponse({
                'success': False,
                'error': 'Valid average cost is required',
                'error_code': 'INVALID_COST'
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
        
        # Get or create user's portfolio
        portfolio, created = UserPortfolio.objects.get_or_create(
            user=user,
            name=portfolio_name,
            defaults={'description': f'Portfolio for {user.username}', 'is_public': False}
        )
        
        # Check if holding already exists
        existing_holding = PortfolioHolding.objects.filter(
            portfolio=portfolio,
            stock=stock
        ).first()
        
        if existing_holding:
            # Update existing holding (average cost calculation)
            current_total_cost = float(existing_holding.shares) * float(existing_holding.average_cost)
            new_total_cost = float(shares) * float(avg_cost)
            total_shares = float(existing_holding.shares) + float(shares)
            new_avg_cost = (current_total_cost + new_total_cost) / total_shares
            
            existing_holding.shares = total_shares
            existing_holding.average_cost = new_avg_cost
            existing_holding.updated_at = timezone.now()
            existing_holding.save()
            
            holding_id = existing_holding.id
            action = 'updated'
        else:
            # Create new holding
            safe_current_price = float(getattr(stock, 'current_price', 0) or avg_cost)
            new_holding = PortfolioHolding.objects.create(
                portfolio=portfolio,
                stock=stock,
                shares=shares,
                average_cost=avg_cost,
                current_price=safe_current_price,
                date_added=timezone.now()
            )
            holding_id = new_holding.id
            action = 'added'
        
        return JsonResponse({
            'success': True,
            'message': f'Stock {symbol} {action} to portfolio successfully',
            'data': {
                'id': str(holding_id),
                'symbol': symbol,
                'shares': float(shares),
                'avg_cost': float(avg_cost),
                'portfolio_name': portfolio.name,
                'action': action
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON format',
            'error_code': 'INVALID_JSON'
        }, status=400)
    except Exception as e:
        logger.error(f"Portfolio add error: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Failed to add stock to portfolio',
            'error_code': 'PORTFOLIO_ADD_ERROR'
        }, status=500)

@csrf_exempt
@api_view(['DELETE'])
@permission_classes([AllowAny])
@authentication_classes([BearerSessionAuthentication, CsrfExemptSessionAuthentication])
def portfolio_delete_api(request, holding_id):
    """
    Remove a holding from portfolio
    DELETE /api/portfolio/{id}
    """
    try:
        try:
            from django.conf import settings as django_settings
            testing = getattr(django_settings, 'TESTING_DISABLE_AUTH', False)
        except Exception:
            testing = False
        if not testing:
            if not getattr(request, 'user', None) or not request.user.is_authenticated:
                return JsonResponse({
                    'success': False,
                    'error': 'Authentication required',
                    'error_code': 'AUTH_REQUIRED'
                }, status=401)
        user = _effective_user(request)
        
        # Find the holding
        try:
            holding = PortfolioHolding.objects.get(
                id=holding_id,
                portfolio__user=user
            )
        except PortfolioHolding.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Portfolio holding not found',
                'error_code': 'HOLDING_NOT_FOUND'
            }, status=404)
        
        symbol = holding.stock.ticker
        shares = holding.shares
        
        # Delete the holding
        holding.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'Removed {shares} shares of {symbol} from portfolio',
            'data': {
                'id': str(holding_id),
                'symbol': symbol,
                'shares': float(shares)
            }
        })
        
    except Exception as e:
        logger.error(f"Portfolio delete error: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Failed to remove holding from portfolio',
            'error_code': 'PORTFOLIO_DELETE_ERROR'
        }, status=500)