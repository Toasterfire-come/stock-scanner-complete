"""
Paper Trading API Endpoints
RESTful API for paper trading operations.
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from decimal import Decimal

from stocks.models import PaperTradingAccount, PaperTrade, Stock
from stocks.services.paper_trading_service import PaperTradingService


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def paper_account(request):
    """
    GET: Retrieve user's paper trading account
    POST: Create a new paper trading account
    """
    if request.method == 'GET':
        # Get or create account
        account = PaperTradingService.get_or_create_account(request.user)

        # Get account summary
        summary = PaperTradingService.get_account_summary(account)

        return Response({
            'success': True,
            'account': {
                'id': account.id,
                'name': account.name,
                'is_active': account.is_active,
                'allow_shorting': account.allow_shorting,
                'max_position_size_pct': float(account.max_position_size_pct),
                'created_at': account.created_at.isoformat(),
                'last_updated': account.last_updated.isoformat(),
                **summary
            }
        })

    elif request.method == 'POST':
        # Create new account
        name = request.data.get('name', 'Paper Trading Account')
        initial_balance = request.data.get('initial_balance', 100000.00)

        try:
            account = PaperTradingService.create_account(
                user=request.user,
                name=name,
                initial_balance=initial_balance
            )

            return Response({
                'success': True,
                'message': 'Paper trading account created successfully',
                'account': {
                    'id': account.id,
                    'name': account.name,
                    'initial_balance': float(account.initial_balance),
                    'cash_balance': float(account.cash_balance),
                    'total_value': float(account.total_value),
                }
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def place_order(request):
    """
    Place a paper trading order.

    POST data:
    - ticker: Stock ticker symbol (required)
    - shares: Number of shares (required)
    - order_type: 'market', 'limit', 'bracket' (default: 'market')
    - side: 'long' or 'short' (default: 'long')
    - limit_price: For limit orders
    - take_profit_price: For bracket orders
    - stop_loss_price: For bracket orders
    - notes: Optional trade notes
    """
    # Get or create account
    account = PaperTradingService.get_or_create_account(request.user)

    # Extract order parameters
    ticker = request.data.get('ticker', '').upper()
    shares = request.data.get('shares')
    order_type = request.data.get('order_type', 'market')
    side = request.data.get('side', 'long')
    notes = request.data.get('notes', '')

    # Validate required fields
    if not ticker:
        return Response({
            'success': False,
            'error': 'Ticker symbol is required'
        }, status=status.HTTP_400_BAD_REQUEST)

    if not shares:
        return Response({
            'success': False,
            'error': 'Number of shares is required'
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Execute based on order type
        if order_type == 'market':
            success, message, trade = PaperTradingService.place_market_order(
                account=account,
                ticker=ticker,
                shares=shares,
                side=side,
                notes=notes
            )

        elif order_type == 'limit':
            limit_price = request.data.get('limit_price')
            if not limit_price:
                return Response({
                    'success': False,
                    'error': 'Limit price is required for limit orders'
                }, status=status.HTTP_400_BAD_REQUEST)

            success, message, trade = PaperTradingService.place_limit_order(
                account=account,
                ticker=ticker,
                shares=shares,
                limit_price=limit_price,
                side=side,
                notes=notes
            )

        elif order_type == 'bracket':
            take_profit_price = request.data.get('take_profit_price')
            stop_loss_price = request.data.get('stop_loss_price')

            if not take_profit_price or not stop_loss_price:
                return Response({
                    'success': False,
                    'error': 'Take profit and stop loss prices are required for bracket orders'
                }, status=status.HTTP_400_BAD_REQUEST)

            success, message, trade = PaperTradingService.place_bracket_order(
                account=account,
                ticker=ticker,
                shares=shares,
                take_profit_price=take_profit_price,
                stop_loss_price=stop_loss_price,
                notes=notes
            )

        else:
            return Response({
                'success': False,
                'error': f'Invalid order type: {order_type}'
            }, status=status.HTTP_400_BAD_REQUEST)

        if success:
            return Response({
                'success': True,
                'message': message,
                'trade': {
                    'id': trade.id,
                    'ticker': trade.stock.ticker,
                    'order_type': trade.order_type,
                    'side': trade.side,
                    'shares': float(trade.shares),
                    'status': trade.status,
                    'entry_price': float(trade.entry_price) if trade.entry_price else None,
                    'created_at': trade.created_at.isoformat(),
                }
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                'success': False,
                'error': message
            }, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def close_position(request, trade_id):
    """
    Close an open position.

    URL: /api/paper-trading/positions/<trade_id>/close/
    POST data:
    - exit_price: Optional exit price (uses current market price if not provided)
    """
    exit_price = request.data.get('exit_price')

    try:
        success, message, trade = PaperTradingService.close_position(
            trade_id=trade_id,
            exit_price=exit_price
        )

        if success:
            return Response({
                'success': True,
                'message': message,
                'trade': {
                    'id': trade.id,
                    'ticker': trade.stock.ticker,
                    'status': trade.status,
                    'entry_price': float(trade.entry_price),
                    'exit_price': float(trade.exit_price) if trade.exit_price else None,
                    'realized_pl': float(trade.realized_pl) if trade.realized_pl else 0.00,
                    'realized_pl_pct': float(trade.realized_pl_pct) if trade.realized_pl_pct else 0.00,
                }
            })
        else:
            return Response({
                'success': False,
                'error': message
            }, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cancel_order(request, trade_id):
    """
    Cancel a pending order.

    URL: /api/paper-trading/orders/<trade_id>/cancel/
    """
    try:
        success, message, trade = PaperTradingService.cancel_order(trade_id)

        if success:
            return Response({
                'success': True,
                'message': message
            })
        else:
            return Response({
                'success': False,
                'error': message
            }, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def open_positions(request):
    """
    Get all open positions for the user's paper trading account.
    """
    account = PaperTradingService.get_or_create_account(request.user)

    positions = PaperTrade.objects.filter(
        account=account,
        status='open'
    ).select_related('stock').order_by('-created_at')

    # Update current values
    for position in positions:
        position.update_current_value()

    positions_data = [
        {
            'id': pos.id,
            'ticker': pos.stock.ticker,
            'company_name': pos.stock.company_name,
            'order_type': pos.order_type,
            'side': pos.side,
            'shares': float(pos.shares),
            'entry_price': float(pos.entry_price),
            'current_price': float(pos.current_price) if pos.current_price else None,
            'entry_value': float(pos.entry_value) if pos.entry_value else 0.00,
            'current_value': float(pos.current_value) if pos.current_value else 0.00,
            'unrealized_pl': float(pos.unrealized_pl) if pos.unrealized_pl else 0.00,
            'unrealized_pl_pct': float(pos.unrealized_pl_pct) if pos.unrealized_pl_pct else 0.00,
            'take_profit_price': float(pos.take_profit_price) if pos.take_profit_price else None,
            'stop_loss_price': float(pos.stop_loss_price) if pos.stop_loss_price else None,
            'filled_at': pos.filled_at.isoformat() if pos.filled_at else None,
            'notes': pos.notes,
        }
        for pos in positions
    ]

    return Response({
        'success': True,
        'positions': positions_data,
        'count': len(positions_data)
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def trade_history(request):
    """
    Get trade history for the user's paper trading account.

    Query params:
    - status: Filter by status (open, closed, cancelled, etc.)
    - limit: Number of trades to return (default: 50, max: 200)
    """
    account = PaperTradingService.get_or_create_account(request.user)

    # Get query parameters
    status_filter = request.GET.get('status')
    limit = min(int(request.GET.get('limit', 50)), 200)

    # Build query
    trades = PaperTrade.objects.filter(account=account).select_related('stock')

    if status_filter:
        trades = trades.filter(status=status_filter)

    trades = trades.order_by('-created_at')[:limit]

    trades_data = [
        {
            'id': trade.id,
            'ticker': trade.stock.ticker,
            'company_name': trade.stock.company_name,
            'order_type': trade.order_type,
            'side': trade.side,
            'status': trade.status,
            'shares': float(trade.shares),
            'entry_price': float(trade.entry_price) if trade.entry_price else None,
            'exit_price': float(trade.exit_price) if trade.exit_price else None,
            'realized_pl': float(trade.realized_pl) if trade.realized_pl else None,
            'realized_pl_pct': float(trade.realized_pl_pct) if trade.realized_pl_pct else None,
            'unrealized_pl': float(trade.unrealized_pl) if trade.unrealized_pl else None,
            'unrealized_pl_pct': float(trade.unrealized_pl_pct) if trade.unrealized_pl_pct else None,
            'created_at': trade.created_at.isoformat(),
            'filled_at': trade.filled_at.isoformat() if trade.filled_at else None,
            'closed_at': trade.closed_at.isoformat() if trade.closed_at else None,
            'holding_period_days': trade.holding_period_days,
            'notes': trade.notes,
        }
        for trade in trades
    ]

    return Response({
        'success': True,
        'trades': trades_data,
        'count': len(trades_data)
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reset_account(request):
    """
    Reset the user's paper trading account to initial state.
    Closes all positions and restores initial balance.
    """
    account = PaperTradingService.get_or_create_account(request.user)

    try:
        success = PaperTradingService.reset_account(account)

        if success:
            return Response({
                'success': True,
                'message': 'Paper trading account reset successfully',
                'account': {
                    'cash_balance': float(account.cash_balance),
                    'total_value': float(account.total_value),
                }
            })
        else:
            return Response({
                'success': False,
                'error': 'Failed to reset account'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def performance_metrics(request):
    """
    Get performance metrics for the user's paper trading account.

    Query params:
    - period_type: 'daily', 'weekly', or 'monthly' (default: 'daily')
    - limit: Number of periods to return (default: 30)
    """
    account = PaperTradingService.get_or_create_account(request.user)

    period_type = request.GET.get('period_type', 'daily')
    limit = min(int(request.GET.get('limit', 30)), 365)

    from stocks.models import PaperTradePerformance

    metrics = PaperTradePerformance.objects.filter(
        account=account,
        period_type=period_type
    ).order_by('-period_start')[:limit]

    metrics_data = [
        {
            'period_start': metric.period_start.isoformat(),
            'period_end': metric.period_end.isoformat(),
            'starting_value': float(metric.starting_value),
            'ending_value': float(metric.ending_value),
            'period_return': float(metric.period_return),
            'period_pl': float(metric.period_pl),
            'trades_opened': metric.trades_opened,
            'trades_closed': metric.trades_closed,
            'winning_trades': metric.winning_trades,
            'losing_trades': metric.losing_trades,
            'period_win_rate': float(metric.period_win_rate),
            'max_gain': float(metric.max_gain),
            'max_loss': float(metric.max_loss),
            'benchmark_return': float(metric.benchmark_return) if metric.benchmark_return else None,
            'alpha': float(metric.alpha) if metric.alpha else None,
        }
        for metric in metrics
    ]

    return Response({
        'success': True,
        'metrics': metrics_data,
        'count': len(metrics_data)
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def leaderboard(request):
    """
    Get paper trading leaderboard showing top performers.

    Query params:
    - period: 'all_time', 'monthly', 'weekly' (default: 'all_time')
    - limit: Number of accounts to return (default: 100)
    """
    period = request.GET.get('period', 'all_time')
    limit = min(int(request.GET.get('limit', 100)), 500)

    # Get top accounts by total return
    accounts = PaperTradingAccount.objects.filter(
        is_active=True
    ).select_related('user').order_by('-total_return')[:limit]

    leaderboard_data = [
        {
            'rank': idx + 1,
            'username': account.user.username,
            'account_name': account.name,
            'total_return': float(account.total_return),
            'total_profit_loss': float(account.total_profit_loss),
            'total_trades': account.total_trades,
            'win_rate': float(account.win_rate),
            'sharpe_ratio': float(account.sharpe_ratio) if account.sharpe_ratio else None,
        }
        for idx, account in enumerate(accounts)
    ]

    return Response({
        'success': True,
        'leaderboard': leaderboard_data,
        'count': len(leaderboard_data)
    })
