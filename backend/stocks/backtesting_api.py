"""
API endpoints for AI Backtesting (Phase 4)
"""
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import datetime, timedelta
import json
from .models import BacktestRun, BaselineStrategy
from .services.backtesting_service import BacktestingService


@csrf_exempt
@require_http_methods(["POST"])
def create_backtest(request):
    """
    Create a new backtest run
    
    POST data:
    - name: str
    - strategy_text: str
    - category: str (day_trading, swing_trading, long_term)
    - symbols: list[str]
    - start_date: str (YYYY-MM-DD)
    - end_date: str (YYYY-MM-DD)
    - initial_capital: float (optional, default 10000)
    """
    try:
        data = json.loads(request.body)
        
        # Get or create anonymous user if not authenticated
        user = request.user if request.user.is_authenticated else None
        if not user:
            from django.contrib.auth.models import User
            user, _ = User.objects.get_or_create(username='anonymous')
        
        # Validate required fields
        required_fields = ['name', 'strategy_text', 'category', 'symbols', 'start_date', 'end_date']
        for field in required_fields:
            if field not in data:
                return JsonResponse({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }, status=400)
        
        # Parse dates
        start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
        end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
        
        # Create backtest run
        backtest = BacktestRun.objects.create(
            user=user,
            name=data['name'],
            strategy_text=data['strategy_text'],
            category=data['category'],
            symbols=data['symbols'],
            start_date=start_date,
            end_date=end_date,
            initial_capital=data.get('initial_capital', 10000.00),
            status='pending'
        )
        
        return JsonResponse({
            'success': True,
            'backtest_id': backtest.id,
            'status': backtest.status
        })
    
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def run_backtest(request, backtest_id):
    """Execute a backtest"""
    try:
        backtest = BacktestRun.objects.get(id=backtest_id)
        
        # Check if already completed
        if backtest.status == 'completed':
            return JsonResponse({
                'success': False,
                'error': 'Backtest already completed'
            }, status=400)
        
        # Update status
        backtest.status = 'processing'
        backtest.save()
        
        # Run backtest
        service = BacktestingService()
        results = service.run_backtest(backtest)
        
        if 'error' in results:
            backtest.status = 'failed'
            backtest.error_message = results['error']
            backtest.save()
            return JsonResponse({
                'success': False,
                'error': results['error']
            }, status=500)
        
        # Update backtest with results
        backtest.status = 'completed'
        backtest.completed_at = timezone.now()
        backtest.total_return = results.get('total_return')
        backtest.annualized_return = results.get('annualized_return')
        backtest.sharpe_ratio = results.get('sharpe_ratio')
        backtest.max_drawdown = results.get('max_drawdown')
        backtest.win_rate = results.get('win_rate')
        backtest.profit_factor = results.get('profit_factor')
        backtest.total_trades = results.get('total_trades')
        backtest.winning_trades = results.get('winning_trades')
        backtest.losing_trades = results.get('losing_trades')
        backtest.composite_score = results.get('composite_score')
        backtest.trades_data = results.get('trades_data', [])
        backtest.equity_curve = results.get('equity_curve', [])
        backtest.save()
        
        return JsonResponse({
            'success': True,
            'results': {
                'total_return': float(backtest.total_return) if backtest.total_return else 0,
                'annualized_return': float(backtest.annualized_return) if backtest.annualized_return else 0,
                'sharpe_ratio': float(backtest.sharpe_ratio) if backtest.sharpe_ratio else 0,
                'max_drawdown': float(backtest.max_drawdown) if backtest.max_drawdown else 0,
                'win_rate': float(backtest.win_rate) if backtest.win_rate else 0,
                'profit_factor': float(backtest.profit_factor) if backtest.profit_factor else 0,
                'total_trades': backtest.total_trades or 0,
                'winning_trades': backtest.winning_trades or 0,
                'losing_trades': backtest.losing_trades or 0,
                'composite_score': float(backtest.composite_score) if backtest.composite_score else 0
            }
        })
    
    except BacktestRun.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Backtest not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_backtest(request, backtest_id):
    """Get backtest results"""
    try:
        backtest = BacktestRun.objects.get(id=backtest_id)
        
        return JsonResponse({
            'success': True,
            'backtest': {
                'id': backtest.id,
                'name': backtest.name,
                'strategy_text': backtest.strategy_text,
                'generated_code': backtest.generated_code,
                'category': backtest.category,
                'symbols': backtest.symbols,
                'start_date': str(backtest.start_date),
                'end_date': str(backtest.end_date),
                'initial_capital': float(backtest.initial_capital),
                'status': backtest.status,
                'error_message': backtest.error_message,
                'results': {
                    'total_return': float(backtest.total_return) if backtest.total_return else None,
                    'annualized_return': float(backtest.annualized_return) if backtest.annualized_return else None,
                    'sharpe_ratio': float(backtest.sharpe_ratio) if backtest.sharpe_ratio else None,
                    'max_drawdown': float(backtest.max_drawdown) if backtest.max_drawdown else None,
                    'win_rate': float(backtest.win_rate) if backtest.win_rate else None,
                    'profit_factor': float(backtest.profit_factor) if backtest.profit_factor else None,
                    'total_trades': backtest.total_trades,
                    'winning_trades': backtest.winning_trades,
                    'losing_trades': backtest.losing_trades,
                    'composite_score': float(backtest.composite_score) if backtest.composite_score else None
                },
                'trades': backtest.trades_data,
                'equity_curve': backtest.equity_curve,
                'created_at': backtest.created_at.isoformat(),
                'completed_at': backtest.completed_at.isoformat() if backtest.completed_at else None
            }
        })
    
    except BacktestRun.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Backtest not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def list_backtests(request):
    """List all backtests"""
    try:
        category = request.GET.get('category')
        
        backtests = BacktestRun.objects.all()
        if category:
            backtests = backtests.filter(category=category)
        
        backtests = backtests.order_by('-created_at')[:50]
        
        return JsonResponse({
            'success': True,
            'backtests': [
                {
                    'id': b.id,
                    'name': b.name,
                    'category': b.category,
                    'status': b.status,
                    'composite_score': float(b.composite_score) if b.composite_score else None,
                    'total_return': float(b.total_return) if b.total_return else None,
                    'created_at': b.created_at.isoformat()
                }
                for b in backtests
            ]
        })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def list_baseline_strategies(request):
    """List all baseline strategies"""
    try:
        strategies = BaselineStrategy.objects.filter(is_active=True).order_by('category', 'name')
        
        return JsonResponse({
            'success': True,
            'strategies': [
                {
                    'id': s.id,
                    'name': s.name,
                    'description': s.description,
                    'category': s.category,
                    'avg_total_return': float(s.avg_total_return) if s.avg_total_return else None,
                    'avg_sharpe_ratio': float(s.avg_sharpe_ratio) if s.avg_sharpe_ratio else None,
                    'avg_max_drawdown': float(s.avg_max_drawdown) if s.avg_max_drawdown else None
                }
                for s in strategies
            ]
        })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
