"""
API endpoints for Achievement System
"""
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
import json

from .achievement_system import (
    get_user_achievements,
    mark_achievement_shared,
    AchievementChecker,
    Achievement
)


@login_required
@require_http_methods(["GET"])
def get_achievements(request):
    """
    Get all achievements for the current user
    Returns both unlocked and locked achievements
    """
    try:
        achievements_data = get_user_achievements(request.user)

        return JsonResponse({
            'success': True,
            'achievements': achievements_data
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@login_required
@require_http_methods(["POST"])
def share_achievement(request, achievement_id):
    """
    Mark an achievement as shared on social media
    """
    try:
        success = mark_achievement_shared(request.user, achievement_id)

        if not success:
            return JsonResponse({
                'success': False,
                'error': 'Achievement not found or not unlocked'
            }, status=404)

        # Check if this was the "first share" - unlock shareholder badge
        shareholder_unlocked = False
        if not Achievement.objects.filter(
            user=request.user,
            achievement_id='shareholder'
        ).exists():
            # Unlock shareholder achievement
            Achievement.objects.create(
                user=request.user,
                achievement_id='shareholder'
            )
            shareholder_unlocked = True

        return JsonResponse({
            'success': True,
            'message': 'Achievement shared successfully',
            'new_achievement_unlocked': shareholder_unlocked
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["GET"])
def get_achievement_progress(request):
    """
    Get progress toward locked achievements
    (Future enhancement - currently just returns stats)
    """
    try:
        from .models import BacktestRun

        # Calculate progress stats
        total_backtests = BacktestRun.objects.filter(
            user=request.user,
            status='completed'
        ).count()

        profitable_backtests = BacktestRun.objects.filter(
            user=request.user,
            status='completed',
            total_return__gt=0
        ).count()

        grade_a_backtests = BacktestRun.objects.filter(
            user=request.user,
            status='completed',
            composite_score__gte=80
        ).count()

        highest_return = BacktestRun.objects.filter(
            user=request.user,
            status='completed'
        ).order_by('-total_return').first()

        highest_sharpe = BacktestRun.objects.filter(
            user=request.user,
            status='completed'
        ).order_by('-sharpe_ratio').first()

        progress = {
            'total_backtests': total_backtests,
            'profitable_backtests': profitable_backtests,
            'grade_a_backtests': grade_a_backtests,
            'highest_return': float(highest_return.total_return) if highest_return and highest_return.total_return else 0,
            'highest_sharpe': float(highest_sharpe.sharpe_ratio) if highest_sharpe and highest_sharpe.sharpe_ratio else 0,
            'progress_to_10_backtests': min(100, (total_backtests / 10) * 100),
            'progress_to_5_consecutive': 0  # Complex calculation, TODO
        }

        return JsonResponse({
            'success': True,
            'progress': progress
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
