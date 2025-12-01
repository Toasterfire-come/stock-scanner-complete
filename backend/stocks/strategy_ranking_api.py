# app/backend/stocks/strategy_ranking_api.py
"""
Strategy Ranking System API
Phase 6 Implementation - TradeScanPro
"""

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count, Sum, F, Q
import json
from datetime import datetime, timedelta
from decimal import Decimal


# In-memory storage for MVP (in production, these would be database models)
STRATEGY_RANKINGS = {}
STRATEGY_CLONES = {}


def calculate_composite_score(strategy_data):
    """
    Calculate composite score for a strategy
    Score Components (0-100 scale):
    - Performance (30%)
    - Risk Management (25%)
    - Consistency (20%)
    - Trade Efficiency (15%)
    - Community Validation (10%)
    """
    
    # Performance Score (30 points max)
    annual_return = strategy_data.get('annual_return', 0)
    total_return_vs_benchmark = strategy_data.get('total_return_vs_benchmark', 0)
    profit_factor = strategy_data.get('profit_factor', 1)
    
    perf_score = min(10, annual_return / 5) if annual_return > 0 else 0  # Up to 10 pts for 50%+ return
    perf_score += min(10, total_return_vs_benchmark / 3)  # Up to 10 pts for 30%+ vs benchmark
    perf_score += min(10, (profit_factor - 1) * 5)  # Up to 10 pts for profit factor 3+
    perf_score = min(30, perf_score)
    
    # Risk Management Score (25 points max)
    sharpe_ratio = strategy_data.get('sharpe_ratio', 0)
    max_drawdown = strategy_data.get('max_drawdown', 50)  # Lower is better
    recovery_factor = strategy_data.get('recovery_factor', 0)
    
    risk_score = min(10, sharpe_ratio * 5)  # Up to 10 pts for sharpe 2+
    risk_score += max(0, 10 - (max_drawdown / 5))  # Up to 10 pts for drawdown under 50%
    risk_score += min(5, recovery_factor / 2)  # Up to 5 pts for recovery factor 10+
    risk_score = min(25, risk_score)
    
    # Consistency Score (20 points max)
    win_rate = strategy_data.get('win_rate', 50)
    consec_wins_losses_ratio = strategy_data.get('consec_wins_losses_ratio', 1)
    monthly_return_stability = strategy_data.get('monthly_return_stability', 0)  # Higher is better
    
    cons_score = min(8, (win_rate - 40) / 5)  # Up to 8 pts for 80%+ win rate
    cons_score += min(7, consec_wins_losses_ratio * 3.5)  # Up to 7 pts for ratio 2+
    cons_score += min(5, monthly_return_stability * 5)  # Up to 5 pts for stability
    cons_score = min(20, cons_score)
    
    # Trade Efficiency Score (15 points max)
    avg_win_loss_ratio = strategy_data.get('avg_win_loss_ratio', 1)
    trade_frequency = strategy_data.get('trade_frequency', 0)  # Optimal around 5-20 trades/month
    commission_impact = strategy_data.get('commission_impact', 5)  # Lower is better
    
    eff_score = min(7, (avg_win_loss_ratio - 0.5) * 7)  # Up to 7 pts for 1.5+ ratio
    eff_score += min(5, 5 if 5 <= trade_frequency <= 20 else max(0, 5 - abs(trade_frequency - 12.5) / 5))
    eff_score += max(0, 3 - commission_impact / 2)  # Up to 3 pts for low commission impact
    eff_score = min(15, eff_score)
    
    # Community Validation Score (10 points max)
    clone_count = strategy_data.get('clone_count', 0)
    user_rating = strategy_data.get('user_rating', 0)  # 0-5 scale
    discussion_count = strategy_data.get('discussion_count', 0)
    
    comm_score = min(4, clone_count / 25)  # Up to 4 pts for 100+ clones
    comm_score += min(4, user_rating * 0.8)  # Up to 4 pts for 5-star rating
    comm_score += min(2, discussion_count / 50)  # Up to 2 pts for 100+ discussions
    comm_score = min(10, comm_score)
    
    total_score = perf_score + risk_score + cons_score + eff_score + comm_score
    
    return {
        'total_score': round(total_score, 1),
        'performance_score': round(perf_score, 1),
        'risk_score': round(risk_score, 1),
        'consistency_score': round(cons_score, 1),
        'efficiency_score': round(eff_score, 1),
        'community_score': round(comm_score, 1),
        'max_scores': {
            'performance': 30,
            'risk': 25,
            'consistency': 20,
            'efficiency': 15,
            'community': 10,
            'total': 100
        }
    }


@csrf_exempt
@require_http_methods(["GET"])
def get_strategy_leaderboard(request):
    """
    GET /api/strategy-ranking/leaderboard/
    
    Query Parameters:
    - category: all, day_trading, swing_trading, long_term
    - timeframe: 1m, 3m, 6m, 1y, all
    - min_score: minimum composite score filter
    - min_trades: minimum trades filter
    - verified_only: true/false
    - sort_by: score, returns, risk_adjusted, popularity
    - page: page number
    - limit: results per page
    """
    
    category = request.GET.get('category', 'all')
    timeframe = request.GET.get('timeframe', '3m')
    min_score = float(request.GET.get('min_score', 0))
    min_trades = int(request.GET.get('min_trades', 0))
    verified_only = request.GET.get('verified_only', 'false').lower() == 'true'
    sort_by = request.GET.get('sort_by', 'score')
    page = int(request.GET.get('page', 1))
    limit = int(request.GET.get('limit', 20))
    
    # Sample strategies for MVP demo
    sample_strategies = [
        {
            'id': 1,
            'name': 'Momentum Breakout Pro',
            'creator': 'TraderJohn',
            'category': 'day_trading',
            'description': 'High-momentum breakout strategy with tight risk management',
            'annual_return': 45.2,
            'total_return_vs_benchmark': 25.8,
            'profit_factor': 2.3,
            'sharpe_ratio': 1.8,
            'max_drawdown': 12.5,
            'recovery_factor': 8.2,
            'win_rate': 62,
            'consec_wins_losses_ratio': 1.5,
            'monthly_return_stability': 0.7,
            'avg_win_loss_ratio': 1.8,
            'trade_frequency': 15,
            'commission_impact': 2.1,
            'clone_count': 156,
            'user_rating': 4.6,
            'discussion_count': 89,
            'total_trades': 245,
            'is_verified': True,
            'created_at': '2024-01-15'
        },
        {
            'id': 2,
            'name': 'Value Hunter Weekly',
            'creator': 'ValueInvestor99',
            'category': 'swing_trading',
            'description': 'Weekly value-based swing trading with fundamental filters',
            'annual_return': 32.5,
            'total_return_vs_benchmark': 18.3,
            'profit_factor': 2.1,
            'sharpe_ratio': 1.5,
            'max_drawdown': 15.2,
            'recovery_factor': 6.5,
            'win_rate': 58,
            'consec_wins_losses_ratio': 1.3,
            'monthly_return_stability': 0.8,
            'avg_win_loss_ratio': 2.1,
            'trade_frequency': 8,
            'commission_impact': 1.2,
            'clone_count': 98,
            'user_rating': 4.4,
            'discussion_count': 67,
            'total_trades': 156,
            'is_verified': True,
            'created_at': '2024-02-20'
        },
        {
            'id': 3,
            'name': 'RSI Reversal Master',
            'creator': 'TechTrader',
            'category': 'day_trading',
            'description': 'RSI-based reversal strategy with volume confirmation',
            'annual_return': 38.7,
            'total_return_vs_benchmark': 22.1,
            'profit_factor': 1.9,
            'sharpe_ratio': 1.6,
            'max_drawdown': 18.3,
            'recovery_factor': 5.8,
            'win_rate': 55,
            'consec_wins_losses_ratio': 1.2,
            'monthly_return_stability': 0.6,
            'avg_win_loss_ratio': 1.6,
            'trade_frequency': 22,
            'commission_impact': 3.5,
            'clone_count': 72,
            'user_rating': 4.2,
            'discussion_count': 45,
            'total_trades': 312,
            'is_verified': True,
            'created_at': '2024-03-10'
        },
        {
            'id': 4,
            'name': 'Dividend Growth Long',
            'creator': 'DividendKing',
            'category': 'long_term',
            'description': 'Long-term dividend growth with capital appreciation',
            'annual_return': 18.5,
            'total_return_vs_benchmark': 8.2,
            'profit_factor': 2.8,
            'sharpe_ratio': 1.2,
            'max_drawdown': 8.5,
            'recovery_factor': 12.5,
            'win_rate': 72,
            'consec_wins_losses_ratio': 2.1,
            'monthly_return_stability': 0.9,
            'avg_win_loss_ratio': 2.5,
            'trade_frequency': 3,
            'commission_impact': 0.5,
            'clone_count': 234,
            'user_rating': 4.8,
            'discussion_count': 156,
            'total_trades': 45,
            'is_verified': True,
            'created_at': '2023-11-05'
        },
        {
            'id': 5,
            'name': 'MACD Crossover Alpha',
            'creator': 'AlgoMaster',
            'category': 'swing_trading',
            'description': 'MACD crossover with multi-timeframe confirmation',
            'annual_return': 28.3,
            'total_return_vs_benchmark': 14.5,
            'profit_factor': 1.7,
            'sharpe_ratio': 1.3,
            'max_drawdown': 20.1,
            'recovery_factor': 4.5,
            'win_rate': 52,
            'consec_wins_losses_ratio': 1.1,
            'monthly_return_stability': 0.5,
            'avg_win_loss_ratio': 1.4,
            'trade_frequency': 12,
            'commission_impact': 2.8,
            'clone_count': 45,
            'user_rating': 3.9,
            'discussion_count': 32,
            'total_trades': 198,
            'is_verified': False,
            'created_at': '2024-04-01'
        }
    ]
    
    # Apply filters
    filtered_strategies = sample_strategies
    
    if category != 'all':
        filtered_strategies = [s for s in filtered_strategies if s['category'] == category]
    
    if verified_only:
        filtered_strategies = [s for s in filtered_strategies if s['is_verified']]
    
    if min_trades > 0:
        filtered_strategies = [s for s in filtered_strategies if s['total_trades'] >= min_trades]
    
    # Calculate scores for each strategy
    for strategy in filtered_strategies:
        score_data = calculate_composite_score(strategy)
        strategy['composite_score'] = score_data['total_score']
        strategy['score_breakdown'] = score_data
    
    # Apply score filter
    if min_score > 0:
        filtered_strategies = [s for s in filtered_strategies if s['composite_score'] >= min_score]
    
    # Sort
    if sort_by == 'score':
        filtered_strategies.sort(key=lambda x: x['composite_score'], reverse=True)
    elif sort_by == 'returns':
        filtered_strategies.sort(key=lambda x: x['annual_return'], reverse=True)
    elif sort_by == 'risk_adjusted':
        filtered_strategies.sort(key=lambda x: x['sharpe_ratio'], reverse=True)
    elif sort_by == 'popularity':
        filtered_strategies.sort(key=lambda x: x['clone_count'], reverse=True)
    
    # Paginate
    total_count = len(filtered_strategies)
    start_idx = (page - 1) * limit
    end_idx = start_idx + limit
    paginated_strategies = filtered_strategies[start_idx:end_idx]
    
    return JsonResponse({
        'success': True,
        'data': {
            'strategies': paginated_strategies,
            'pagination': {
                'page': page,
                'limit': limit,
                'total_count': total_count,
                'total_pages': (total_count + limit - 1) // limit
            },
            'filters': {
                'category': category,
                'timeframe': timeframe,
                'min_score': min_score,
                'min_trades': min_trades,
                'verified_only': verified_only,
                'sort_by': sort_by
            }
        }
    })


@csrf_exempt
@require_http_methods(["GET"])
def get_strategy_detail(request, strategy_id):
    """
    GET /api/strategy-ranking/<strategy_id>/
    Get detailed strategy information including full score breakdown
    """
    
    # For MVP, return sample data
    sample_strategy = {
        'id': strategy_id,
        'name': 'Momentum Breakout Pro',
        'creator': 'TraderJohn',
        'category': 'day_trading',
        'description': 'High-momentum breakout strategy with tight risk management. Uses volume confirmation and ATR-based stops.',
        'annual_return': 45.2,
        'total_return_vs_benchmark': 25.8,
        'profit_factor': 2.3,
        'sharpe_ratio': 1.8,
        'max_drawdown': 12.5,
        'recovery_factor': 8.2,
        'win_rate': 62,
        'consec_wins_losses_ratio': 1.5,
        'monthly_return_stability': 0.7,
        'avg_win_loss_ratio': 1.8,
        'trade_frequency': 15,
        'commission_impact': 2.1,
        'clone_count': 156,
        'user_rating': 4.6,
        'discussion_count': 89,
        'total_trades': 245,
        'is_verified': True,
        'created_at': '2024-01-15',
        'rules': {
            'entry': [
                'Price breaks above 20-day high',
                'Volume > 150% of 20-day average',
                'RSI between 50-70'
            ],
            'exit': [
                'Stop loss: 2x ATR below entry',
                'Take profit: 3x ATR above entry',
                'Trailing stop: 1.5x ATR'
            ],
            'filters': [
                'Market cap > $1B',
                'Average volume > 1M shares',
                'No earnings within 5 days'
            ]
        },
        'monthly_returns': [
            {'month': '2024-01', 'return': 5.2},
            {'month': '2024-02', 'return': 3.8},
            {'month': '2024-03', 'return': -1.2},
            {'month': '2024-04', 'return': 7.5},
            {'month': '2024-05', 'return': 4.1},
            {'month': '2024-06', 'return': 2.9}
        ]
    }
    
    score_data = calculate_composite_score(sample_strategy)
    sample_strategy['composite_score'] = score_data['total_score']
    sample_strategy['score_breakdown'] = score_data
    
    return JsonResponse({
        'success': True,
        'data': sample_strategy
    })


@csrf_exempt
@require_http_methods(["POST"])
def clone_strategy(request, strategy_id):
    """
    POST /api/strategy-ranking/<strategy_id>/clone/
    Clone a strategy to user's account
    """
    
    try:
        data = json.loads(request.body) if request.body else {}
    except json.JSONDecodeError:
        data = {}
    
    new_name = data.get('name', f'Clone of Strategy {strategy_id}')
    keep_symbols = data.get('keep_symbols', True)
    keep_timeframe = data.get('keep_timeframe', True)
    keep_parameters = data.get('keep_parameters', True)
    
    # For MVP, simulate clone creation
    clone_id = f"clone_{strategy_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    return JsonResponse({
        'success': True,
        'data': {
            'clone_id': clone_id,
            'original_strategy_id': strategy_id,
            'name': new_name,
            'settings': {
                'keep_symbols': keep_symbols,
                'keep_timeframe': keep_timeframe,
                'keep_parameters': keep_parameters
            },
            'message': 'Strategy cloned successfully. You can now customize and backtest it.'
        }
    })


@csrf_exempt
@require_http_methods(["POST"])
def rate_strategy(request, strategy_id):
    """
    POST /api/strategy-ranking/<strategy_id>/rate/
    Rate a strategy (1-5 stars)
    """
    
    try:
        data = json.loads(request.body)
        rating = data.get('rating')
        comment = data.get('comment', '')
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON body'
        }, status=400)
    
    if not rating or not (1 <= rating <= 5):
        return JsonResponse({
            'success': False,
            'error': 'Rating must be between 1 and 5'
        }, status=400)
    
    return JsonResponse({
        'success': True,
        'data': {
            'strategy_id': strategy_id,
            'rating': rating,
            'comment': comment,
            'message': 'Rating submitted successfully'
        }
    })


@csrf_exempt
@require_http_methods(["GET"])
def get_leaderboard_categories(request):
    """
    GET /api/strategy-ranking/categories/
    Get available leaderboard categories and filters
    """
    
    return JsonResponse({
        'success': True,
        'data': {
            'categories': [
                {'value': 'all', 'label': 'All Strategies'},
                {'value': 'day_trading', 'label': 'Day Trading'},
                {'value': 'swing_trading', 'label': 'Swing Trading'},
                {'value': 'long_term', 'label': 'Long-Term'}
            ],
            'timeframes': [
                {'value': '1m', 'label': '1 Month'},
                {'value': '3m', 'label': '3 Months'},
                {'value': '6m', 'label': '6 Months'},
                {'value': '1y', 'label': '1 Year'},
                {'value': 'all', 'label': 'All Time'}
            ],
            'sort_options': [
                {'value': 'score', 'label': 'Composite Score'},
                {'value': 'returns', 'label': 'Returns'},
                {'value': 'risk_adjusted', 'label': 'Risk-Adjusted Returns'},
                {'value': 'popularity', 'label': 'Popularity'}
            ],
            'score_components': {
                'performance': {'weight': 30, 'description': 'Return metrics and profit factor'},
                'risk': {'weight': 25, 'description': 'Sharpe ratio, drawdown, recovery'},
                'consistency': {'weight': 20, 'description': 'Win rate and return stability'},
                'efficiency': {'weight': 15, 'description': 'Trade quality and costs'},
                'community': {'weight': 10, 'description': 'Clones, ratings, discussions'}
            }
        }
    })
