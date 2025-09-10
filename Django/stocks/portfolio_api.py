"""
Portfolio API - Secure portfolio management APIs.
Provides endpoints for portfolio CRUD operations, performance tracking, alert ROI analysis,
and CSV import functionality with comprehensive security and validation.
"""

import json
import logging
from decimal import Decimal
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.views.decorators.csrf import csrf_exempt
from .security_utils import (
    secure_api_endpoint, validate_user_input, 
    PORTFOLIO_SCHEMA, HOLDING_SCHEMA, TRANSACTION_SCHEMA
)
from .portfolio_service import PortfolioService
from .models import UserPortfolio, PortfolioHolding, Stock, StockAlert

logger = logging.getLogger(__name__)

@csrf_exempt
@secure_api_endpoint(methods=['POST'])
def create_portfolio(request):
    """
    Create a new portfolio for the user.
    
    POST /api/portfolio/create/
    
    Body:
    {
        "name": "My Portfolio",
        "description": "Portfolio description",
        "is_public": false
    }
    """
    try:
        # Validate input
        validated_data = validate_user_input(request.validated_data, PORTFOLIO_SCHEMA)
        
        # Create portfolio
        portfolio = PortfolioService.create_portfolio(
            user=request.user,
            name=validated_data['name'],
            description=validated_data.get('description', ''),
            is_public=validated_data.get('is_public', False)
        )
        
        return JsonResponse({
            'success': True,
            'data': {
                'portfolio_id': portfolio.id,
                'name': portfolio.name,
                'description': portfolio.description,
                'is_public': portfolio.is_public,
                'created_at': portfolio.created_at.isoformat()
            },
            'message': 'Portfolio created successfully'
        })
        
    except ValidationError as e:
        return JsonResponse({
            'success': False,
            'error': str(e),
            'error_code': 'VALIDATION_ERROR'
        }, status=400)
    except Exception as e:
        logger.error(f"Error in create_portfolio: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Failed to create portfolio',
            'error_code': 'CREATION_ERROR'
        }, status=500)

@csrf_exempt
@secure_api_endpoint(methods=['POST'])
def add_holding(request):
    """
    Add a stock holding to a portfolio.
    
    POST /api/portfolio/add-holding/
    
    Body:
    {
        "portfolio_id": 1,
        "stock_ticker": "AAPL",
        "shares": 100.0,
        "average_cost": 150.00,
        "current_price": 165.00,
        "alert_id": null
    }
    """
    try:
        # Validate input
        schema = {
            'portfolio_id': {'type': 'integer', 'required': True, 'min_value': 1},
            'alert_id': {'type': 'integer', 'min_value': 1},
            **HOLDING_SCHEMA
        }
        validated_data = validate_user_input(request.validated_data, schema)
        
        # Get portfolio
        try:
            portfolio = UserPortfolio.objects.get(
                id=validated_data['portfolio_id'], 
                user=request.user
            )
        except UserPortfolio.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Portfolio not found',
                'error_code': 'PORTFOLIO_NOT_FOUND'
            }, status=404)
        
        # Get alert if provided
        from_alert = None
        if validated_data.get('alert_id'):
            try:
                from_alert = StockAlert.objects.get(
                    id=validated_data['alert_id'],
                    user=request.user
                )
            except StockAlert.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'error': 'Alert not found',
                    'error_code': 'ALERT_NOT_FOUND'
                }, status=404)
        
        # Add holding
        holding = PortfolioService.add_holding(
            portfolio=portfolio,
            stock_ticker=validated_data['stock_ticker'],
            shares=validated_data['shares'],
            average_cost=validated_data['average_cost'],
            current_price=validated_data.get('current_price'),
            from_alert=from_alert
        )
        
        return JsonResponse({
            'success': True,
            'data': {
                'holding_id': holding.id,
                'portfolio_id': portfolio.id,
                'stock_ticker': holding.stock.ticker,
                'shares': float(holding.shares),
                'average_cost': float(holding.average_cost),
                'current_price': float(holding.current_price),
                'market_value': float(holding.market_value),
                'unrealized_gain_loss': float(holding.unrealized_gain_loss),
                'unrealized_gain_loss_percent': float(holding.unrealized_gain_loss_percent),
                'date_added': holding.date_added.isoformat()
            },
            'message': 'Holding added successfully'
        })
        
    except ValidationError as e:
        return JsonResponse({
            'success': False,
            'error': str(e),
            'error_code': 'VALIDATION_ERROR'
        }, status=400)
    except Exception as e:
        logger.error(f"Error in add_holding: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Failed to add holding',
            'error_code': 'HOLDING_ERROR'
        }, status=500)

@csrf_exempt
@secure_api_endpoint(methods=['POST'])
def sell_holding(request):
    """
    Sell shares from a portfolio holding.
    
    POST /api/portfolio/sell-holding/
    
    Body:
    {
        "portfolio_id": 1,
        "stock_ticker": "AAPL",
        "shares": 50.0,
        "sale_price": 170.00,
        "fees": 5.00
    }
    """
    try:
        # Validate input
        schema = {
            'portfolio_id': {'type': 'integer', 'required': True, 'min_value': 1},
            'stock_ticker': {'type': 'ticker', 'required': True},
            'shares': {'type': 'decimal', 'required': True, 'min_value': 0.0001, 'decimal_places': 4},
            'sale_price': {'type': 'decimal', 'required': True, 'min_value': 0.01, 'decimal_places': 4},
            'fees': {'type': 'decimal', 'min_value': 0, 'decimal_places': 2, 'default': 0}
        }
        validated_data = validate_user_input(request.validated_data, schema)
        
        # Get portfolio
        try:
            portfolio = UserPortfolio.objects.get(
                id=validated_data['portfolio_id'], 
                user=request.user
            )
        except UserPortfolio.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Portfolio not found',
                'error_code': 'PORTFOLIO_NOT_FOUND'
            }, status=404)
        
        # Sell holding
        result = PortfolioService.sell_holding(
            portfolio=portfolio,
            stock_ticker=validated_data['stock_ticker'],
            shares=validated_data['shares'],
            sale_price=validated_data['sale_price'],
            fees=validated_data.get('fees', Decimal('0'))
        )
        
        return JsonResponse({
            'success': True,
            'data': {
                'transaction_id': result['transaction_id'],
                'portfolio_id': portfolio.id,
                'stock_ticker': validated_data['stock_ticker'],
                'shares_sold': float(result['shares_sold']),
                'sale_price': float(result['sale_price']),
                'total_proceeds': float(result['total_proceeds']),
                'cost_basis': float(result['cost_basis']),
                'realized_gain_loss': float(result['realized_gain_loss']),
                'realized_gain_loss_percent': float(result['realized_gain_loss_percent']),
                'holding_period_days': result['holding_period_days'],
                'fees': float(result['fees'])
            },
            'message': 'Shares sold successfully'
        })
        
    except ValidationError as e:
        return JsonResponse({
            'success': False,
            'error': str(e),
            'error_code': 'VALIDATION_ERROR'
        }, status=400)
    except Exception as e:
        logger.error(f"Error in sell_holding: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Failed to sell holding',
            'error_code': 'SELL_ERROR'
        }, status=500)

@csrf_exempt
@secure_api_endpoint(methods=['GET'])
def list_portfolios(request):
    """
    Get all portfolios for the user with basic performance metrics.
    
    GET /api/portfolio/list/
    """
    try:
        portfolios = PortfolioService.get_user_portfolios(request.user)
        
        return JsonResponse({
            'success': True,
            'data': {
                'portfolios': portfolios,
                'count': len(portfolios)
            },
            'message': 'Portfolios retrieved successfully'
        })
        
    except Exception as e:
        logger.error(f"Error in list_portfolios: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Failed to retrieve portfolios',
            'error_code': 'RETRIEVAL_ERROR'
        }, status=500)

@csrf_exempt
@secure_api_endpoint(methods=['GET'])
def portfolio_performance(request, portfolio_id):
    """
    Get comprehensive portfolio performance metrics.
    
    GET /api/portfolio/{portfolio_id}/performance/
    """
    try:
        # Validate portfolio access
        try:
            portfolio = UserPortfolio.objects.get(id=portfolio_id, user=request.user)
        except UserPortfolio.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Portfolio not found',
                'error_code': 'PORTFOLIO_NOT_FOUND'
            }, status=404)
        
        # Get performance data
        performance = PortfolioService.get_portfolio_performance(portfolio)
        
        return JsonResponse({
            'success': True,
            'data': performance,
            'message': 'Portfolio performance retrieved successfully'
        })
        
    except Exception as e:
        logger.error(f"Error in portfolio_performance: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Failed to retrieve portfolio performance',
            'error_code': 'PERFORMANCE_ERROR'
        }, status=500)

@csrf_exempt
@secure_api_endpoint(methods=['POST'])
def import_csv(request):
    """
    Import portfolio holdings from CSV.
    
    POST /api/portfolio/import-csv/
    
    Body:
    {
        "portfolio_name": "Imported Portfolio",
        "csv_content": "ticker,shares,average_cost,current_price\nAAPL,100,150.00,165.00\n..."
    }
    """
    try:
        # Validate input
        schema = {
            'portfolio_name': {
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
        
        # Import portfolio
        result = PortfolioService.import_portfolio_from_csv(
            user=request.user,
            portfolio_name=validated_data['portfolio_name'],
            csv_content=validated_data['csv_content']
        )
        
        return JsonResponse({
            'success': True,
            'data': result,
            'message': 'Portfolio imported successfully'
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
            'error': 'Failed to import portfolio',
            'error_code': 'IMPORT_ERROR'
        }, status=500)

@csrf_exempt
@secure_api_endpoint(methods=['GET'])
def alert_roi(request):
    """
    Get ROI and performance metrics for alert-based trades across all portfolios.
    
    GET /api/portfolio/alert-roi/
    """
    try:
        # Get all user portfolios
        portfolios = UserPortfolio.objects.filter(user=request.user)
        
        # Aggregate alert performance across all portfolios
        total_alert_performance = {
            'total_alert_transactions': 0,
            'total_manual_transactions': 0,
            'alert_success_rate': 0,
            'manual_success_rate': 0,
            'categories': {},
            'portfolios': []
        }
        
        for portfolio in portfolios:
            portfolio_performance = PortfolioService.calculate_alert_roi(portfolio)
            
            # Add to totals
            total_alert_performance['total_alert_transactions'] += portfolio_performance.get('total_alert_transactions', 0)
            total_alert_performance['total_manual_transactions'] += portfolio_performance.get('total_manual_transactions', 0)
            
            # Merge category data
            for category, data in portfolio_performance.get('categories', {}).items():
                if category not in total_alert_performance['categories']:
                    total_alert_performance['categories'][category] = {
                        'total_transactions': 0,
                        'profitable_trades': 0,
                        'total_realized_gain_loss': 0,
                        'average_holding_period': 0,
                        'success_rate': 0,
                        'average_roi': 0
                    }
                
                total_alert_performance['categories'][category]['total_transactions'] += data.get('total_transactions', 0)
                total_alert_performance['categories'][category]['profitable_trades'] += data.get('profitable_trades', 0)
                total_alert_performance['categories'][category]['total_realized_gain_loss'] += data.get('total_realized_gain_loss', 0)
            
            # Add portfolio-specific data
            total_alert_performance['portfolios'].append({
                'portfolio_id': portfolio.id,
                'portfolio_name': portfolio.name,
                'performance': portfolio_performance
            })
        
        # Calculate overall success rates
        if total_alert_performance['total_alert_transactions'] > 0:
            total_profitable_alerts = sum(
                data.get('profitable_trades', 0) 
                for data in total_alert_performance['categories'].values()
            )
            total_alert_performance['alert_success_rate'] = (
                total_profitable_alerts / total_alert_performance['total_alert_transactions'] * 100
            )
        
        # Calculate category averages
        for category_data in total_alert_performance['categories'].values():
            total = category_data['total_transactions']
            if total > 0:
                category_data['success_rate'] = (category_data['profitable_trades'] / total) * 100
                category_data['average_roi'] = category_data['total_realized_gain_loss'] / total
        
        return JsonResponse({
            'success': True,
            'data': total_alert_performance,
            'message': 'Alert ROI data retrieved successfully'
        })
        
    except Exception as e:
        logger.error(f"Error in alert_roi: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Failed to retrieve alert ROI data',
            'error_code': 'ROI_ERROR'
        }, status=500)

@csrf_exempt
@secure_api_endpoint(methods=['DELETE'])
def delete_portfolio(request, portfolio_id):
    """
    Delete a portfolio and all its holdings/transactions.
    
    DELETE /api/portfolio/{portfolio_id}/
    """
    try:
        # Validate portfolio access
        try:
            portfolio = UserPortfolio.objects.get(id=portfolio_id, user=request.user)
        except UserPortfolio.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Portfolio not found',
                'error_code': 'PORTFOLIO_NOT_FOUND'
            }, status=404)
        
        portfolio_name = portfolio.name
        portfolio.delete()
        
        return JsonResponse({
            'success': True,
            'data': {
                'portfolio_id': portfolio_id,
                'portfolio_name': portfolio_name
            },
            'message': 'Portfolio deleted successfully'
        })
        
    except Exception as e:
        logger.error(f"Error in delete_portfolio: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Failed to delete portfolio',
            'error_code': 'DELETE_ERROR'
        }, status=500)

@csrf_exempt
@secure_api_endpoint(methods=['PUT'])
def update_portfolio(request, portfolio_id):
    """
    Update portfolio information.
    
    PUT /api/portfolio/{portfolio_id}/
    
    Body:
    {
        "name": "Updated Portfolio Name",
        "description": "Updated description",
        "is_public": true
    }
    """
    try:
        # Validate portfolio access
        try:
            portfolio = UserPortfolio.objects.get(id=portfolio_id, user=request.user)
        except UserPortfolio.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Portfolio not found',
                'error_code': 'PORTFOLIO_NOT_FOUND'
            }, status=404)
        
        # Validate input
        schema = {
            'name': {'type': 'string', 'min_length': 1, 'max_length': 100},
            'description': {'type': 'string', 'max_length': 1000},
            'is_public': {'type': 'boolean'}
        }
        validated_data = validate_user_input(request.validated_data, schema)
        
        # Update portfolio fields
        if 'name' in validated_data:
            portfolio.name = validated_data['name']
        if 'description' in validated_data:
            portfolio.description = validated_data['description']
        if 'is_public' in validated_data:
            portfolio.is_public = validated_data['is_public']
        
        portfolio.save()
        
        return JsonResponse({
            'success': True,
            'data': {
                'portfolio_id': portfolio.id,
                'name': portfolio.name,
                'description': portfolio.description,
                'is_public': portfolio.is_public,
                'updated_at': portfolio.updated_at.isoformat()
            },
            'message': 'Portfolio updated successfully'
        })
        
    except ValidationError as e:
        return JsonResponse({
            'success': False,
            'error': str(e),
            'error_code': 'VALIDATION_ERROR'
        }, status=400)
    except Exception as e:
        logger.error(f"Error in update_portfolio: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Failed to update portfolio',
            'error_code': 'UPDATE_ERROR'
        }, status=500)