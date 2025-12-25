"""
Strategy Scoring Service
Composite scoring engine with normalization and anti-overfitting controls.
Based on strategy_ranking_api.py algorithm.
"""

from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from django.db.models import Avg, Count
from datetime import timedelta
import math

from stocks.models import TradingStrategy, StrategyScore, StrategyRating, StrategyLeaderboard, PaperTrade


class StrategyScoring:
    """
    Composite scoring engine for strategy ranking.
    Normalizes metrics across 5 weighted components.
    """

    # Component weights (must sum to 1.0)
    WEIGHTS = {
        'performance': 0.30,  # Annual return, profit factor, vs benchmark
        'risk': 0.25,         # Sharpe ratio, max drawdown, recovery factor
        'consistency': 0.20,  # Win rate, return stability
        'efficiency': 0.15,   # Win/loss ratio, trade frequency, commission impact
        'community': 0.10,    # Clone count, ratings, engagement
    }

    # Normalization thresholds (for 0-100 scale)
    EXCELLENT_THRESHOLDS = {
        'annual_return': 50.0,        # 50%+ annual return = max score
        'sharpe_ratio': 3.0,          # 3.0+ Sharpe = excellent
        'profit_factor': 3.0,         # 3.0+ profit factor = excellent
        'win_rate': 70.0,             # 70%+ win rate = max score
        'max_drawdown': 10.0,         # <10% drawdown = excellent
        'avg_win_loss_ratio': 3.0,   # 3:1 win/loss = excellent
        'recovery_factor': 5.0,       # 5.0+ recovery = excellent
    }

    @staticmethod
    def calculate_all_scores(strategy_id):
        """
        Calculate all score components and composite score for a strategy.

        Returns:
            dict: {'success': bool, 'score_id': int, 'total_score': float, 'breakdown': dict}
        """
        try:
            strategy = TradingStrategy.objects.get(id=strategy_id)
        except TradingStrategy.DoesNotExist:
            return {'success': False, 'message': 'Strategy not found'}

        # Check minimum trades threshold
        if strategy.total_trades < 30:
            return {
                'success': False,
                'message': f'Insufficient trades for scoring (need 30, have {strategy.total_trades})'
            }

        # Update cached performance from paper trading
        strategy.update_performance_cache()

        # Get or create score record
        score, created = StrategyScore.objects.get_or_create(strategy=strategy)

        # Calculate each component
        perf_result = StrategyScoring._calculate_performance_score(strategy)
        risk_result = StrategyScoring._calculate_risk_score(strategy)
        cons_result = StrategyScoring._calculate_consistency_score(strategy)
        eff_result = StrategyScoring._calculate_efficiency_score(strategy)
        comm_result = StrategyScoring._calculate_community_score(strategy)

        # Update component scores
        score.performance_score = Decimal(str(perf_result['score']))
        score.risk_score = Decimal(str(risk_result['score']))
        score.consistency_score = Decimal(str(cons_result['score']))
        score.efficiency_score = Decimal(str(eff_result['score']))
        score.community_score = Decimal(str(comm_result['score']))

        # Store detailed breakdown
        score.score_breakdown = {
            'performance': perf_result,
            'risk': risk_result,
            'consistency': cons_result,
            'efficiency': eff_result,
            'community': comm_result,
        }

        # Mark as having sufficient data
        score.is_sufficient_data = True

        # Calculate composite score
        score.calculate_composite_score()

        return {
            'success': True,
            'score_id': score.id,
            'total_score': float(score.total_score),
            'breakdown': score.score_breakdown,
            'created': created
        }

    @staticmethod
    def _calculate_performance_score(strategy):
        """
        Performance Score (30% weight) - 0-100 scale
        Components: annual_return, profit_factor, vs_benchmark
        """
        score_components = []
        details = {}

        # 1. Annual Return (50% of performance score = 15 points max)
        if strategy.annual_return:
            annual_ret = float(strategy.annual_return)
            # Normalize to 0-50 scale (50%+ return = max)
            annual_score = min(50, (annual_ret / StrategyScoring.EXCELLENT_THRESHOLDS['annual_return']) * 50)
            score_components.append(annual_score)
            details['annual_return'] = {
                'value': annual_ret,
                'score': annual_score,
                'max': 50
            }
        else:
            details['annual_return'] = {'value': None, 'score': 0, 'max': 50}

        # 2. Profit Factor (30% of performance score = 9 points max)
        if strategy.profit_factor:
            pf = float(strategy.profit_factor)
            # Normalize to 0-30 scale
            pf_score = min(30, (pf / StrategyScoring.EXCELLENT_THRESHOLDS['profit_factor']) * 30)
            score_components.append(pf_score)
            details['profit_factor'] = {
                'value': pf,
                'score': pf_score,
                'max': 30
            }
        else:
            details['profit_factor'] = {'value': None, 'score': 0, 'max': 30}

        # 3. vs Benchmark (20% of performance score = 6 points max)
        # TODO: Compare to S&P 500 performance over same period
        # For now, give partial credit based on positive returns
        if strategy.annual_return and float(strategy.annual_return) > 10.0:
            benchmark_score = 20  # Beating typical market return
            details['vs_benchmark'] = {
                'value': 'above_market',
                'score': benchmark_score,
                'max': 20
            }
            score_components.append(benchmark_score)
        else:
            details['vs_benchmark'] = {'value': 'below_market', 'score': 0, 'max': 20}

        total = sum(score_components)

        return {
            'score': min(100, total),  # Cap at 100
            'details': details,
            'weight': StrategyScoring.WEIGHTS['performance']
        }

    @staticmethod
    def _calculate_risk_score(strategy):
        """
        Risk Score (25% weight) - 0-100 scale
        Components: sharpe_ratio, max_drawdown, recovery_factor
        """
        score_components = []
        details = {}

        # 1. Sharpe Ratio (50% of risk score = 50 points max)
        if strategy.sharpe_ratio:
            sharpe = float(strategy.sharpe_ratio)
            # Normalize to 0-50 scale (3.0+ = max)
            sharpe_score = min(50, (sharpe / StrategyScoring.EXCELLENT_THRESHOLDS['sharpe_ratio']) * 50)
            score_components.append(sharpe_score)
            details['sharpe_ratio'] = {
                'value': sharpe,
                'score': sharpe_score,
                'max': 50
            }
        else:
            details['sharpe_ratio'] = {'value': None, 'score': 0, 'max': 50}

        # 2. Max Drawdown (30% of risk score = 30 points max)
        # Lower drawdown = higher score (inverted)
        if strategy.max_drawdown:
            dd = abs(float(strategy.max_drawdown))
            # Inverted: <10% = max score, >50% = min score
            if dd < StrategyScoring.EXCELLENT_THRESHOLDS['max_drawdown']:
                dd_score = 30
            elif dd > 50:
                dd_score = 0
            else:
                # Linear decay from 30 to 0 as drawdown goes from 10% to 50%
                dd_score = 30 * (1 - ((dd - 10) / 40))
            score_components.append(dd_score)
            details['max_drawdown'] = {
                'value': -dd,
                'score': dd_score,
                'max': 30
            }
        else:
            details['max_drawdown'] = {'value': None, 'score': 0, 'max': 30}

        # 3. Recovery Factor (20% of risk score = 20 points max)
        # Recovery Factor = Net Profit / Max Drawdown
        if strategy.annual_return and strategy.max_drawdown:
            ret = float(strategy.annual_return)
            dd = abs(float(strategy.max_drawdown))
            if dd > 0:
                recovery = ret / dd
                recovery_score = min(20, (recovery / StrategyScoring.EXCELLENT_THRESHOLDS['recovery_factor']) * 20)
                score_components.append(recovery_score)
                details['recovery_factor'] = {
                    'value': recovery,
                    'score': recovery_score,
                    'max': 20
                }
            else:
                details['recovery_factor'] = {'value': None, 'score': 0, 'max': 20}
        else:
            details['recovery_factor'] = {'value': None, 'score': 0, 'max': 20}

        total = sum(score_components)

        return {
            'score': min(100, total),
            'details': details,
            'weight': StrategyScoring.WEIGHTS['risk']
        }

    @staticmethod
    def _calculate_consistency_score(strategy):
        """
        Consistency Score (20% weight) - 0-100 scale
        Components: win_rate, return_stability
        """
        score_components = []
        details = {}

        # 1. Win Rate (60% of consistency score = 60 points max)
        if strategy.win_rate:
            wr = float(strategy.win_rate)
            # Normalize to 0-60 scale (70%+ = max)
            wr_score = min(60, (wr / StrategyScoring.EXCELLENT_THRESHOLDS['win_rate']) * 60)
            score_components.append(wr_score)
            details['win_rate'] = {
                'value': wr,
                'score': wr_score,
                'max': 60
            }
        else:
            details['win_rate'] = {'value': None, 'score': 0, 'max': 60}

        # 2. Return Stability (40% of consistency score = 40 points max)
        # Measured by coefficient of variation of trade returns
        if strategy.paper_account:
            trades = PaperTrade.objects.filter(
                account=strategy.paper_account,
                status='closed'
            )
            if trades.count() >= 10:
                returns = [float(t.realized_pnl_pct) for t in trades if t.realized_pnl_pct]
                if len(returns) >= 10:
                    mean_return = sum(returns) / len(returns)
                    variance = sum((r - mean_return) ** 2 for r in returns) / len(returns)
                    std_dev = math.sqrt(variance)

                    # Coefficient of Variation (lower = more stable)
                    cv = (std_dev / abs(mean_return)) if mean_return != 0 else float('inf')

                    # Inverted: CV < 0.5 = max score, CV > 2.0 = min score
                    if cv < 0.5:
                        stability_score = 40
                    elif cv > 2.0:
                        stability_score = 0
                    else:
                        stability_score = 40 * (1 - ((cv - 0.5) / 1.5))

                    score_components.append(stability_score)
                    details['return_stability'] = {
                        'cv': cv,
                        'score': stability_score,
                        'max': 40
                    }
                else:
                    details['return_stability'] = {'cv': None, 'score': 0, 'max': 40}
            else:
                details['return_stability'] = {'cv': None, 'score': 0, 'max': 40}
        else:
            details['return_stability'] = {'cv': None, 'score': 0, 'max': 40}

        total = sum(score_components)

        return {
            'score': min(100, total),
            'details': details,
            'weight': StrategyScoring.WEIGHTS['consistency']
        }

    @staticmethod
    def _calculate_efficiency_score(strategy):
        """
        Efficiency Score (15% weight) - 0-100 scale
        Components: win_loss_ratio, trade_frequency, commission_impact
        """
        score_components = []
        details = {}

        # 1. Win/Loss Ratio (50% of efficiency score = 50 points max)
        if strategy.paper_account:
            trades = PaperTrade.objects.filter(
                account=strategy.paper_account,
                status='closed'
            )
            wins = [t for t in trades if t.realized_pnl and float(t.realized_pnl) > 0]
            losses = [t for t in trades if t.realized_pnl and float(t.realized_pnl) < 0]

            if len(wins) > 0 and len(losses) > 0:
                avg_win = sum(float(t.realized_pnl) for t in wins) / len(wins)
                avg_loss = abs(sum(float(t.realized_pnl) for t in losses) / len(losses))

                if avg_loss > 0:
                    wl_ratio = avg_win / avg_loss
                    wl_score = min(50, (wl_ratio / StrategyScoring.EXCELLENT_THRESHOLDS['avg_win_loss_ratio']) * 50)
                    score_components.append(wl_score)
                    details['win_loss_ratio'] = {
                        'value': wl_ratio,
                        'score': wl_score,
                        'max': 50
                    }
                else:
                    details['win_loss_ratio'] = {'value': None, 'score': 0, 'max': 50}
            else:
                details['win_loss_ratio'] = {'value': None, 'score': 0, 'max': 50}
        else:
            details['win_loss_ratio'] = {'value': None, 'score': 0, 'max': 50}

        # 2. Trade Frequency (30% of efficiency score = 30 points max)
        # Optimal: 1-5 trades per week (not too frequent, not too rare)
        if strategy.paper_account:
            account_age_days = (timezone.now() - strategy.paper_account.created_at).days
            if account_age_days > 0:
                trades_per_week = (strategy.total_trades / account_age_days) * 7

                # Optimal range: 1-5 trades/week = max score
                if 1 <= trades_per_week <= 5:
                    freq_score = 30
                elif trades_per_week < 1:
                    freq_score = trades_per_week * 30  # Linear scaling below optimal
                else:
                    # Penalty for overtrading (>5 trades/week)
                    freq_score = max(0, 30 - ((trades_per_week - 5) * 3))

                score_components.append(freq_score)
                details['trade_frequency'] = {
                    'trades_per_week': trades_per_week,
                    'score': freq_score,
                    'max': 30
                }
            else:
                details['trade_frequency'] = {'trades_per_week': None, 'score': 0, 'max': 30}
        else:
            details['trade_frequency'] = {'trades_per_week': None, 'score': 0, 'max': 30}

        # 3. Commission Impact (20% of efficiency score = 20 points max)
        # Lower commission/slippage drag = higher score
        # For paper trading, assume low impact and give partial credit
        commission_score = 15  # Default for paper trading
        details['commission_impact'] = {
            'value': 'low',
            'score': commission_score,
            'max': 20
        }
        score_components.append(commission_score)

        total = sum(score_components)

        return {
            'score': min(100, total),
            'details': details,
            'weight': StrategyScoring.WEIGHTS['efficiency']
        }

    @staticmethod
    def _calculate_community_score(strategy):
        """
        Community Score (10% weight) - 0-100 scale
        Components: clone_count, avg_rating, view_count
        """
        score_components = []
        details = {}

        # 1. Clone Count (50% of community score = 50 points max)
        # Normalize: 10+ clones = max score
        clone_score = min(50, (strategy.clone_count / 10) * 50)
        score_components.append(clone_score)
        details['clone_count'] = {
            'value': strategy.clone_count,
            'score': clone_score,
            'max': 50
        }

        # 2. Average Rating (40% of community score = 40 points max)
        ratings = StrategyRating.objects.filter(strategy=strategy)
        if ratings.exists():
            avg_rating = ratings.aggregate(Avg('rating'))['rating__avg']
            # Convert 1-5 star to 0-40 scale
            rating_score = ((avg_rating - 1) / 4) * 40  # 5 stars = 40 points
            score_components.append(rating_score)
            details['avg_rating'] = {
                'value': avg_rating,
                'count': ratings.count(),
                'score': rating_score,
                'max': 40
            }
        else:
            details['avg_rating'] = {'value': None, 'count': 0, 'score': 0, 'max': 40}

        # 3. View Count (10% of community score = 10 points max)
        # Normalize: 100+ views = max score
        view_score = min(10, (strategy.view_count / 100) * 10)
        score_components.append(view_score)
        details['view_count'] = {
            'value': strategy.view_count,
            'score': view_score,
            'max': 10
        }

        total = sum(score_components)

        return {
            'score': min(100, total),
            'details': details,
            'weight': StrategyScoring.WEIGHTS['community']
        }

    @staticmethod
    def update_leaderboards(category='overall', timeframe='all_time'):
        """
        Update leaderboard rankings for a specific category and timeframe.

        Args:
            category: 'overall', 'momentum', 'mean_reversion', etc.
            timeframe: 'daily', 'weekly', 'monthly', 'all_time'

        Returns:
            dict: {'success': bool, 'strategies_ranked': int}
        """
        # Filter strategies by category
        strategies = TradingStrategy.objects.filter(
            visibility='public',
            status__in=['paper_trading', 'live']
        )

        if category == 'rookies':
            cutoff = timezone.now() - timedelta(days=90)
            strategies = strategies.filter(created_at__gte=cutoff)
        elif category != 'overall':
            strategies = strategies.filter(strategy_type=category)

        # Get strategies with scores
        strategies = strategies.filter(score__is_sufficient_data=True)

        # Order by total score
        strategies = strategies.select_related('score').order_by('-score__total_score')

        # Update or create leaderboard entries
        with transaction.atomic():
            # Clear existing entries for this category/timeframe
            StrategyLeaderboard.objects.filter(
                category=category,
                timeframe=timeframe
            ).delete()

            # Create new entries
            for rank, strategy in enumerate(strategies, start=1):
                StrategyLeaderboard.objects.create(
                    strategy=strategy,
                    timeframe=timeframe,
                    category=category,
                    rank=rank,
                    score=strategy.score.total_score,
                    snapshot_data={
                        'annual_return': float(strategy.annual_return) if strategy.annual_return else None,
                        'sharpe_ratio': float(strategy.sharpe_ratio) if strategy.sharpe_ratio else None,
                        'win_rate': float(strategy.win_rate) if strategy.win_rate else None,
                        'total_trades': strategy.total_trades,
                    }
                )

        return {
            'success': True,
            'strategies_ranked': strategies.count(),
            'category': category,
            'timeframe': timeframe
        }

    @staticmethod
    def batch_update_scores(limit=100):
        """
        Batch update scores for strategies with sufficient trades.

        Returns:
            dict: {'success': bool, 'updated': int, 'errors': int}
        """
        strategies = TradingStrategy.objects.filter(
            total_trades__gte=30,
            status__in=['paper_trading', 'live']
        )[:limit]

        updated = 0
        errors = 0

        for strategy in strategies:
            result = StrategyScoring.calculate_all_scores(strategy.id)
            if result['success']:
                updated += 1
            else:
                errors += 1

        return {
            'success': True,
            'updated': updated,
            'errors': errors,
            'message': f'Updated {updated} scores with {errors} errors'
        }
