"""
Strategy Ranking & Scoring API
Provides endpoints for strategy leaderboards, cloning, and ratings.
Database-backed with composite scoring engine.
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q, Avg, Count
from django.utils import timezone
from datetime import timedelta

from stocks.models import (
    TradingStrategy, StrategyScore, StrategyRating,
    StrategyClone, StrategyLeaderboard
)
from stocks.services.strategy_scoring_service import StrategyScoring
from stocks.services.strategy_cloning_service import StrategyCloning


@api_view(['GET'])
@permission_classes([AllowAny])
def get_strategy_leaderboard(request):
    """
    Get paginated strategy leaderboard with filtering.

    Query params:
        - category: overall, momentum, mean_reversion, breakout, swing, day_trading, options, rookies
        - timeframe: daily, weekly, monthly, all_time (default: all_time)
        - page: page number (default: 1)
        - limit: results per page (default: 20, max: 100)
        - min_trades: minimum trades threshold (default: 30)
        - search: search by strategy name

    Returns:
        {
            'success': True,
            'strategies': [...],
            'pagination': {...},
            'filters': {...}
        }
    """
    category = request.GET.get('category', 'overall')
    timeframe = request.GET.get('timeframe', 'all_time')
    page = int(request.GET.get('page', 1))
    limit = min(int(request.GET.get('limit', 20)), 100)
    min_trades = int(request.GET.get('min_trades', 30))
    search = request.GET.get('search', '').strip()

    # Check if leaderboard needs refresh (older than 1 hour)
    latest_entry = StrategyLeaderboard.objects.filter(
        category=category,
        timeframe=timeframe
    ).order_by('-calculated_at').first()

    if not latest_entry or (timezone.now() - latest_entry.calculated_at) > timedelta(hours=1):
        # Refresh leaderboard
        StrategyScoring.update_leaderboards(category=category, timeframe=timeframe)

    # Get leaderboard entries
    leaderboard = StrategyLeaderboard.objects.filter(
        category=category,
        timeframe=timeframe
    ).select_related('strategy', 'strategy__user', 'strategy__score')

    # Apply search filter
    if search:
        leaderboard = leaderboard.filter(
            Q(strategy__name__icontains=search) |
            Q(strategy__description__icontains=search)
        )

    # Apply min_trades filter
    leaderboard = leaderboard.filter(strategy__total_trades__gte=min_trades)

    total_count = leaderboard.count()

    # Pagination
    start = (page - 1) * limit
    end = start + limit
    leaderboard = leaderboard[start:end]

    # Serialize strategies
    strategies = []
    for entry in leaderboard:
        strat = entry.strategy
        score = strat.score

        strategies.append({
            'id': strat.id,
            'rank': entry.rank,
            'name': strat.name,
            'description': strat.description[:200] + '...' if len(strat.description) > 200 else strat.description,
            'strategy_type': strat.strategy_type,
            'user': {
                'id': strat.user.id,
                'email': strat.user.email
            },
            'score': {
                'total': float(score.total_score),
                'performance': float(score.performance_score),
                'risk': float(score.risk_score),
                'consistency': float(score.consistency_score),
                'efficiency': float(score.efficiency_score),
                'community': float(score.community_score)
            },
            'metrics': {
                'annual_return': float(strat.annual_return) if strat.annual_return else None,
                'sharpe_ratio': float(strat.sharpe_ratio) if strat.sharpe_ratio else None,
                'max_drawdown': float(strat.max_drawdown) if strat.max_drawdown else None,
                'win_rate': float(strat.win_rate) if strat.win_rate else None,
                'total_trades': strat.total_trades
            },
            'community': {
                'clone_count': strat.clone_count,
                'view_count': strat.view_count,
                'avg_rating': StrategyRating.objects.filter(strategy=strat).aggregate(Avg('rating'))['rating__avg'],
                'rating_count': StrategyRating.objects.filter(strategy=strat).count()
            },
            'is_featured': strat.is_featured,
            'is_verified': strat.is_verified,
            'created_at': strat.created_at
        })

    return Response({
        'success': True,
        'strategies': strategies,
        'pagination': {
            'page': page,
            'limit': limit,
            'total': total_count,
            'total_pages': (total_count + limit - 1) // limit
        },
        'filters': {
            'category': category,
            'timeframe': timeframe,
            'min_trades': min_trades,
            'search': search
        }
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def get_strategy_detail(request, strategy_id):
    """
    Get full strategy details including score breakdown.

    Returns:
        {
            'success': True,
            'strategy': {...},
            'score_breakdown': {...},
            'user_rating': {...} (if authenticated)
        }
    """
    try:
        strategy = TradingStrategy.objects.select_related(
            'user', 'score', 'paper_account'
        ).get(id=strategy_id)
    except TradingStrategy.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Strategy not found'
        }, status=status.HTTP_404_NOT_FOUND)

    # Check visibility
    if strategy.visibility == 'private':
        # Only owner can view private strategies
        if not request.user.is_authenticated or request.user != strategy.user:
            return Response({
                'success': False,
                'message': 'Strategy is private'
            }, status=status.HTTP_403_FORBIDDEN)

    # Increment view count
    strategy.view_count += 1
    strategy.save(update_fields=['view_count'])

    # Get ratings
    ratings = StrategyRating.objects.filter(strategy=strategy)
    avg_rating = ratings.aggregate(Avg('rating'))['rating__avg']

    # Get clone lineage
    lineage = StrategyCloning.get_clone_lineage(strategy_id)

    # Build response
    strategy_data = {
        'id': strategy.id,
        'name': strategy.name,
        'description': strategy.description,
        'strategy_type': strategy.strategy_type,
        'status': strategy.status,
        'visibility': strategy.visibility,
        'user': {
            'id': strategy.user.id,
            'email': strategy.user.email
        },
        'configuration': {
            'max_position_size': float(strategy.max_position_size),
            'max_portfolio_risk': float(strategy.max_portfolio_risk),
            'stop_loss_pct': float(strategy.stop_loss_pct) if strategy.stop_loss_pct else None,
            'take_profit_pct': float(strategy.take_profit_pct) if strategy.take_profit_pct else None,
            'entry_rules': strategy.entry_rules,
            'exit_rules': strategy.exit_rules
        },
        'metrics': {
            'total_trades': strategy.total_trades,
            'winning_trades': strategy.winning_trades,
            'losing_trades': strategy.losing_trades,
            'win_rate': float(strategy.win_rate) if strategy.win_rate else None,
            'annual_return': float(strategy.annual_return) if strategy.annual_return else None,
            'sharpe_ratio': float(strategy.sharpe_ratio) if strategy.sharpe_ratio else None,
            'max_drawdown': float(strategy.max_drawdown) if strategy.max_drawdown else None,
            'profit_factor': float(strategy.profit_factor) if strategy.profit_factor else None
        },
        'community': {
            'clone_count': strategy.clone_count,
            'view_count': strategy.view_count,
            'avg_rating': float(avg_rating) if avg_rating else None,
            'rating_count': ratings.count(),
            'is_clone': lineage['is_clone'],
            'clone_source': lineage['clone_source'],
            'total_clones': lineage['clone_count']
        },
        'is_featured': strategy.is_featured,
        'is_verified': strategy.is_verified,
        'created_at': strategy.created_at,
        'updated_at': strategy.updated_at
    }

    # Add score breakdown if available
    score_breakdown = None
    if hasattr(strategy, 'score') and strategy.score:
        score_breakdown = {
            'total_score': float(strategy.score.total_score),
            'components': {
                'performance': {
                    'score': float(strategy.score.performance_score),
                    'weight': 0.30,
                    'details': strategy.score.score_breakdown.get('performance', {})
                },
                'risk': {
                    'score': float(strategy.score.risk_score),
                    'weight': 0.25,
                    'details': strategy.score.score_breakdown.get('risk', {})
                },
                'consistency': {
                    'score': float(strategy.score.consistency_score),
                    'weight': 0.20,
                    'details': strategy.score.score_breakdown.get('consistency', {})
                },
                'efficiency': {
                    'score': float(strategy.score.efficiency_score),
                    'weight': 0.15,
                    'details': strategy.score.score_breakdown.get('efficiency', {})
                },
                'community': {
                    'score': float(strategy.score.community_score),
                    'weight': 0.10,
                    'details': strategy.score.score_breakdown.get('community', {})
                }
            },
            'is_sufficient_data': strategy.score.is_sufficient_data,
            'verification_status': strategy.score.verification_status,
            'last_calculated': strategy.score.last_calculated_at
        }

    # Get user's rating if authenticated
    user_rating = None
    if request.user.is_authenticated:
        try:
            rating = StrategyRating.objects.get(strategy=strategy, user=request.user)
            user_rating = {
                'rating': rating.rating,
                'review': rating.review,
                'created_at': rating.created_at
            }
        except StrategyRating.DoesNotExist:
            pass

    return Response({
        'success': True,
        'strategy': strategy_data,
        'score_breakdown': score_breakdown,
        'user_rating': user_rating
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def clone_strategy(request, strategy_id):
    """
    Clone a strategy with optional customizations.

    Body:
        {
            "name": "My Custom Strategy (optional)",
            "description": "...",
            "max_position_size": 10.0,
            "max_portfolio_risk": 2.0,
            "stop_loss_pct": 5.0,
            "take_profit_pct": 10.0,
            "initial_balance": 100000.0,
            "create_paper_account": true
        }

    Returns:
        {
            'success': True,
            'cloned_strategy_id': int,
            'message': str
        }
    """
    customizations = request.data.copy()
    create_paper_account = customizations.pop('create_paper_account', True)

    result = StrategyCloning.clone_strategy(
        original_strategy_id=strategy_id,
        user=request.user,
        customizations=customizations,
        create_paper_account=create_paper_account
    )

    if result['success']:
        return Response(result, status=status.HTTP_201_CREATED)
    else:
        return Response(result, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def rate_strategy(request, strategy_id):
    """
    Rate a strategy (1-5 stars) with optional review.

    Body:
        {
            "rating": 5,
            "review": "Excellent strategy! Highly recommend." (optional)
        }

    Returns:
        {
            'success': True,
            'message': str
        }
    """
    try:
        strategy = TradingStrategy.objects.get(id=strategy_id)
    except TradingStrategy.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Strategy not found'
        }, status=status.HTTP_404_NOT_FOUND)

    # Validate rating
    rating_value = request.data.get('rating')
    if not rating_value or not isinstance(rating_value, int) or not 1 <= rating_value <= 5:
        return Response({
            'success': False,
            'message': 'Rating must be an integer between 1 and 5'
        }, status=status.HTTP_400_BAD_REQUEST)

    review_text = request.data.get('review', '').strip()

    # Update or create rating
    rating, created = StrategyRating.objects.update_or_create(
        strategy=strategy,
        user=request.user,
        defaults={
            'rating': rating_value,
            'review': review_text
        }
    )

    # Recalculate community score
    if hasattr(strategy, 'score'):
        StrategyScoring.calculate_all_scores(strategy.id)

    action = 'created' if created else 'updated'

    return Response({
        'success': True,
        'message': f'Rating {action} successfully',
        'rating': {
            'rating': rating.rating,
            'review': rating.review,
            'created_at': rating.created_at,
            'updated_at': rating.updated_at
        }
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def get_leaderboard_categories(request):
    """
    Get available leaderboard categories and filters.

    Returns:
        {
            'success': True,
            'categories': [...],
            'timeframes': [...],
            'strategy_types': [...]
        }
    """
    categories = [
        {'value': 'overall', 'label': 'Overall', 'description': 'All strategies'},
        {'value': 'momentum', 'label': 'Momentum', 'description': 'Momentum-based strategies'},
        {'value': 'mean_reversion', 'label': 'Mean Reversion', 'description': 'Mean reversion strategies'},
        {'value': 'breakout', 'label': 'Breakout', 'description': 'Breakout strategies'},
        {'value': 'swing', 'label': 'Swing Trading', 'description': 'Swing trading strategies'},
        {'value': 'day_trading', 'label': 'Day Trading', 'description': 'Day trading strategies'},
        {'value': 'options', 'label': 'Options', 'description': 'Options-based strategies'},
        {'value': 'rookies', 'label': 'Rookies', 'description': 'Strategies less than 90 days old'}
    ]

    timeframes = [
        {'value': 'daily', 'label': 'Daily', 'description': 'Top performers today'},
        {'value': 'weekly', 'label': 'Weekly', 'description': 'Top performers this week'},
        {'value': 'monthly', 'label': 'Monthly', 'description': 'Top performers this month'},
        {'value': 'all_time', 'label': 'All Time', 'description': 'All-time top performers'}
    ]

    strategy_types = [
        {'value': 'momentum', 'label': 'Momentum'},
        {'value': 'mean_reversion', 'label': 'Mean Reversion'},
        {'value': 'breakout', 'label': 'Breakout'},
        {'value': 'swing', 'label': 'Swing Trading'},
        {'value': 'day_trading', 'label': 'Day Trading'},
        {'value': 'options', 'label': 'Options Strategy'},
        {'value': 'custom', 'label': 'Custom'}
    ]

    return Response({
        'success': True,
        'categories': categories,
        'timeframes': timeframes,
        'strategy_types': strategy_types
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_my_strategies(request):
    """
    Get authenticated user's strategies.

    Returns:
        {
            'success': True,
            'strategies': [...],
            'cloned_strategies': [...]
        }
    """
    # User's own strategies
    strategies = TradingStrategy.objects.filter(
        user=request.user
    ).select_related('score', 'paper_account').order_by('-created_at')

    # User's cloned strategies
    clones = StrategyCloning.get_user_clones(request.user)

    strategies_data = []
    for strat in strategies:
        strategies_data.append({
            'id': strat.id,
            'name': strat.name,
            'strategy_type': strat.strategy_type,
            'status': strat.status,
            'visibility': strat.visibility,
            'total_trades': strat.total_trades,
            'win_rate': float(strat.win_rate) if strat.win_rate else None,
            'annual_return': float(strat.annual_return) if strat.annual_return else None,
            'clone_count': strat.clone_count,
            'total_score': float(strat.score.total_score) if hasattr(strat, 'score') else None,
            'created_at': strat.created_at
        })

    clones_data = []
    for clone in clones:
        clones_data.append({
            'clone_id': clone.id,
            'original_strategy': {
                'id': clone.original_strategy.id,
                'name': clone.original_strategy.name
            },
            'cloned_strategy': {
                'id': clone.cloned_strategy.id,
                'name': clone.cloned_strategy.name,
                'status': clone.cloned_strategy.status,
                'total_trades': clone.cloned_strategy.total_trades
            },
            'is_modified': clone.is_modified,
            'cloned_at': clone.cloned_at
        })

    return Response({
        'success': True,
        'strategies': strategies_data,
        'cloned_strategies': clones_data,
        'total_strategies': len(strategies_data),
        'total_clones': len(clones_data)
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def recalculate_strategy_score(request, strategy_id):
    """
    Manually trigger score recalculation for a strategy.
    Only strategy owner can trigger this.

    Returns:
        {
            'success': True,
            'total_score': float,
            'breakdown': {...}
        }
    """
    try:
        strategy = TradingStrategy.objects.get(id=strategy_id)
    except TradingStrategy.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Strategy not found'
        }, status=status.HTTP_404_NOT_FOUND)

    # Check ownership
    if strategy.user != request.user:
        return Response({
            'success': False,
            'message': 'You can only recalculate scores for your own strategies'
        }, status=status.HTTP_403_FORBIDDEN)

    # Calculate scores
    result = StrategyScoring.calculate_all_scores(strategy_id)

    if result['success']:
        return Response({
            'success': True,
            'total_score': result['total_score'],
            'breakdown': result['breakdown'],
            'message': 'Score recalculated successfully'
        })
    else:
        return Response(result, status=status.HTTP_400_BAD_REQUEST)
