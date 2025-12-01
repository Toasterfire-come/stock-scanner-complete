"""
API endpoints for Strategy Ranking System (Phase 6)
"""
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db.models import Count, Avg, Q
import json
from .models import BacktestRun, BaselineStrategy


@csrf_exempt
@require_http_methods(["GET"])
def get_leaderboard(request):
    """
    Get strategy leaderboard by category
    
    Query params:
    - category: day_trading, swing_trading, long_term (optional)
    - limit: number of results (default 50)
    """
    try:
        category = request.GET.get('category')
        limit = int(request.GET.get('limit', 50))
        
        # Build query
        queryset = BacktestRun.objects.filter(
            status='completed',
            composite_score__isnull=False
        )
        
        if category:
            queryset = queryset.filter(category=category)
        
        # Order by composite score
        strategies = queryset.order_by('-composite_score')[:limit]
        
        return JsonResponse({
            'success': True,
            'leaderboard': [
                {
                    'id': s.id,
                    'rank': idx + 1,
                    'name': s.name,
                    'category': s.category,
                    'composite_score': float(s.composite_score) if s.composite_score else 0,
                    'total_return': float(s.total_return) if s.total_return else 0,
                    'sharpe_ratio': float(s.sharpe_ratio) if s.sharpe_ratio else 0,
                    'win_rate': float(s.win_rate) if s.win_rate else 0,
                    'total_trades': s.total_trades or 0,
                    'user': s.user.username,
                    'is_baseline': s.is_baseline,
                    'is_public': s.is_public,
                    'created_at': s.created_at.isoformat()
                }
                for idx, s in enumerate(strategies)
            ],
            'total': queryset.count()
        })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_category_stats(request):
    """Get statistics for each strategy category"""
    try:
        categories = ['day_trading', 'swing_trading', 'long_term']
        stats = []
        
        for category in categories:
            category_strategies = BacktestRun.objects.filter(
                category=category,
                status='completed',
                composite_score__isnull=False
            )
            
            if category_strategies.exists():
                stats.append({
                    'category': category,
                    'total_strategies': category_strategies.count(),
                    'avg_composite_score': float(category_strategies.aggregate(
                        Avg('composite_score')
                    )['composite_score__avg'] or 0),
                    'avg_return': float(category_strategies.aggregate(
                        Avg('total_return')
                    )['total_return__avg'] or 0),
                    'avg_sharpe': float(category_strategies.aggregate(
                        Avg('sharpe_ratio')
                    )['sharpe_ratio__avg'] or 0),
                    'avg_win_rate': float(category_strategies.aggregate(
                        Avg('win_rate')
                    )['win_rate__avg'] or 0),
                    'top_strategy': _get_top_strategy(category_strategies)
                })
            else:
                stats.append({
                    'category': category,
                    'total_strategies': 0,
                    'avg_composite_score': 0,
                    'avg_return': 0,
                    'avg_sharpe': 0,
                    'avg_win_rate': 0,
                    'top_strategy': None
                })
        
        return JsonResponse({
            'success': True,
            'category_stats': stats
        })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


def _get_top_strategy(queryset):
    """Helper to get top strategy from queryset"""
    top = queryset.order_by('-composite_score').first()
    if top:
        return {
            'id': top.id,
            'name': top.name,
            'composite_score': float(top.composite_score),
            'user': top.user.username
        }
    return None


@csrf_exempt
@require_http_methods(["POST"])
def clone_strategy(request):
    """
    Clone an existing strategy for reuse
    
    POST data:
    - backtest_id: ID of strategy to clone
    - new_name: Name for cloned strategy (optional)
    """
    try:
        data = json.loads(request.body)
        backtest_id = data.get('backtest_id')
        
        if not backtest_id:
            return JsonResponse({
                'success': False,
                'error': 'backtest_id is required'
            }, status=400)
        
        # Get original backtest
        original = BacktestRun.objects.get(id=backtest_id)
        
        # Get user
        user = request.user if request.user.is_authenticated else None
        if not user:
            from django.contrib.auth.models import User
            user, _ = User.objects.get_or_create(username='anonymous')
        
        # Create clone
        new_name = data.get('new_name', f"{original.name} (Clone)")
        
        cloned = BacktestRun.objects.create(
            user=user,
            name=new_name,
            strategy_text=original.strategy_text,
            generated_code=original.generated_code,
            category=original.category,
            symbols=original.symbols,
            start_date=original.start_date,
            end_date=original.end_date,
            initial_capital=original.initial_capital,
            status='pending'
        )
        
        return JsonResponse({
            'success': True,
            'cloned_strategy': {
                'id': cloned.id,
                'name': cloned.name,
                'original_id': original.id,
                'status': cloned.status
            }
        })
    
    except BacktestRun.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Strategy not found'
        }, status=404)
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
@require_http_methods(["GET"])
def compare_strategies(request):
    """
    Compare multiple strategies side-by-side
    
    Query params:
    - ids: comma-separated strategy IDs (e.g., "1,2,3")
    """
    try:
        ids_param = request.GET.get('ids', '')
        if not ids_param:
            return JsonResponse({
                'success': False,
                'error': 'ids parameter is required'
            }, status=400)
        
        strategy_ids = [int(id.strip()) for id in ids_param.split(',')]
        strategies = BacktestRun.objects.filter(id__in=strategy_ids, status='completed')
        
        comparison = []
        for strategy in strategies:
            comparison.append({
                'id': strategy.id,
                'name': strategy.name,
                'category': strategy.category,
                'metrics': {
                    'composite_score': float(strategy.composite_score) if strategy.composite_score else 0,
                    'total_return': float(strategy.total_return) if strategy.total_return else 0,
                    'annualized_return': float(strategy.annualized_return) if strategy.annualized_return else 0,
                    'sharpe_ratio': float(strategy.sharpe_ratio) if strategy.sharpe_ratio else 0,
                    'max_drawdown': float(strategy.max_drawdown) if strategy.max_drawdown else 0,
                    'win_rate': float(strategy.win_rate) if strategy.win_rate else 0,
                    'profit_factor': float(strategy.profit_factor) if strategy.profit_factor else 0,
                    'total_trades': strategy.total_trades or 0
                },
                'user': strategy.user.username,
                'created_at': strategy.created_at.isoformat()
            })
        
        return JsonResponse({
            'success': True,
            'strategies': comparison
        })
    
    except ValueError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid strategy IDs format'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_user_rankings(request):
    """Get leaderboard of users by their best strategies"""
    try:
        from django.contrib.auth.models import User
        
        # Get best strategy for each user
        users_data = []
        for user in User.objects.all():
            best_strategy = BacktestRun.objects.filter(
                user=user,
                status='completed',
                composite_score__isnull=False
            ).order_by('-composite_score').first()
            
            if best_strategy:
                total_strategies = BacktestRun.objects.filter(user=user, status='completed').count()
                users_data.append({
                    'user': user.username,
                    'best_score': float(best_strategy.composite_score),
                    'best_strategy_name': best_strategy.name,
                    'best_strategy_id': best_strategy.id,
                    'total_strategies': total_strategies
                })
        
        # Sort by best score
        users_data.sort(key=lambda x: x['best_score'], reverse=True)
        
        # Add ranks
        for idx, user_data in enumerate(users_data):
            user_data['rank'] = idx + 1
        
        return JsonResponse({
            'success': True,
            'user_rankings': users_data[:50]  # Top 50 users
        })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
