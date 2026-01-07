"""
API endpoints for AI Backtesting (Phase 4)
"""
from django.http import JsonResponse
from django.utils import timezone
from django.utils.text import slugify
from datetime import datetime, timedelta
import json
import secrets
from .models import BacktestRun, BaselineStrategy
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from .authentication import BearerSessionAuthentication, CsrfExemptSessionAuthentication
# Use Groq-powered service instead of static
try:
    from .services.groq_backtesting_service import GroqBacktestingService as BacktestingService
except ImportError:
    from .services.backtesting_service import BacktestingService

# Backtest limits per tier (NO FREE PLAN - Subscription Required)
BACKTEST_LIMITS = {
    'basic': 2,  # 2 backtests per month (Basic plan - $14.99/mo)
    'plus': -1,  # Unlimited (Plus plan - $24.99/mo)
    # Note: No free tier - subscription required to use backtesting
}

def _generate_unique_backtest_share_slug(backtest: BacktestRun) -> str:
    """
    Generate a unique, human-readable share slug.
    Example: "ema-crossover-1a2b3c"
    """
    base = slugify(backtest.name or "backtest")[:48].strip("-") or "backtest"
    # Try a few times to avoid (rare) collisions
    for _ in range(10):
        token = secrets.token_hex(3)  # 6 hex chars
        slug = f"{base}-{token}"
        if not BacktestRun.objects.filter(share_slug=slug).exists():
            return slug
    # Fallback: longer token
    token = secrets.token_hex(8)
    return f"{base}-{token}"


def _increment_fork_count(original: BacktestRun) -> None:
    try:
        original.fork_count = (original.fork_count or 0) + 1
        original.save(update_fields=["fork_count"])
    except Exception:
        pass


def get_user_backtest_limit(user):
    """Get user's monthly backtest limit based on subscription tier"""
    try:
        from billing.models import Subscription
        subscription = Subscription.objects.get(user=user, status='active')
        tier = subscription.plan_tier
        return BACKTEST_LIMITS.get(tier, 0)  # Return 0 if no valid subscription
    except Subscription.DoesNotExist:
        return 0  # No subscription = no backtests allowed


def get_user_backtests_this_month(user):
    """Count user's backtests created this month"""
    start_of_month = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    return BacktestRun.objects.filter(
        user=user,
        created_at__gte=start_of_month
    ).count()


@api_view(["POST"])
@permission_classes([IsAuthenticated])
@authentication_classes([BearerSessionAuthentication, CsrfExemptSessionAuthentication])
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
        data = getattr(request, "data", None) or {}
        if data == {} and getattr(request, "body", None):
            data = json.loads(request.body)

        user = request.user
        
        # Check backtest limit for authenticated users
        limit = get_user_backtest_limit(user)
        current_count = get_user_backtests_this_month(user)
            
        if limit > 0 and current_count >= limit:
            return JsonResponse({
                'success': False,
                'error': 'Monthly backtest limit reached',
                'error_code': 'LIMIT_REACHED',
                'current_count': current_count,
                'limit': limit,
                'message': f'You have used all {limit} backtests for this month. Upgrade to Plus plan for unlimited backtests.',
                'upgrade_url': '/pricing'
            }, status=403)
        
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
        
        # Get remaining backtests for this month
        remaining = -1  # Unlimited
        if request.user.is_authenticated:
            limit = get_user_backtest_limit(request.user)
            if limit > 0:
                remaining = limit - current_count - 1
        
        return JsonResponse({
            'success': True,
            'backtest_id': backtest.id,
            'status': backtest.status,
            'backtests_remaining': remaining
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


@api_view(["POST"])
@permission_classes([IsAuthenticated])
@authentication_classes([BearerSessionAuthentication, CsrfExemptSessionAuthentication])
def run_backtest(request, backtest_id):
    """Execute a backtest"""
    try:
        backtest = BacktestRun.objects.get(id=backtest_id, user=request.user)
        
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
        # Persist the full metrics payload so the frontend can render advanced metrics.
        try:
            metrics_only = {
                k: v for k, v in (results or {}).items()
                if k not in ("trades_data", "equity_curve") and k is not None
            }
            backtest.metrics_data = metrics_only
        except Exception:
            backtest.metrics_data = None
        backtest.trades_data = results.get('trades_data', [])
        backtest.equity_curve = results.get('equity_curve', [])
        backtest.save()

        # Check for achievement unlocks
        newly_unlocked_achievements = []
        if backtest.user.is_authenticated:
            try:
                from .achievement_system import AchievementChecker
                newly_unlocked_achievements = AchievementChecker.check_all_achievements(
                    backtest.user,
                    backtest
                )
            except Exception:
                # Silently fail if achievement checking fails
                pass

        # Build a results dict that includes advanced metrics when available.
        base_results = {
            'total_return': float(backtest.total_return) if backtest.total_return is not None else 0,
            'annualized_return': float(backtest.annualized_return) if backtest.annualized_return is not None else 0,
            'sharpe_ratio': float(backtest.sharpe_ratio) if backtest.sharpe_ratio is not None else 0,
            'max_drawdown': float(backtest.max_drawdown) if backtest.max_drawdown is not None else 0,
            'win_rate': float(backtest.win_rate) if backtest.win_rate is not None else 0,
            'profit_factor': float(backtest.profit_factor) if backtest.profit_factor is not None else 0,
            'total_trades': backtest.total_trades or 0,
            'winning_trades': backtest.winning_trades or 0,
            'losing_trades': backtest.losing_trades or 0,
            'composite_score': float(backtest.composite_score) if backtest.composite_score is not None else 0,
        }
        if isinstance(backtest.metrics_data, dict):
            # Merge in any additional metrics such as sortino/calmar/var/quality_grade, etc.
            base_results.update(backtest.metrics_data)

        return JsonResponse({
            'success': True,
            'results': base_results,
            'trades': backtest.trades_data or [],
            'equity_curve': backtest.equity_curve or [],
            'achievements_unlocked': newly_unlocked_achievements
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


@api_view(["GET"])
@permission_classes([IsAuthenticated])
@authentication_classes([BearerSessionAuthentication, CsrfExemptSessionAuthentication])
def get_backtest(request, backtest_id):
    """Get backtest results"""
    try:
        backtest = BacktestRun.objects.get(id=backtest_id, user=request.user)
        results_payload = {
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
        }
        if isinstance(backtest.metrics_data, dict):
            results_payload.update(backtest.metrics_data)

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
                'is_public': bool(backtest.is_public),
                'share_slug': backtest.share_slug,
                'public_view_count': backtest.public_view_count,
                'fork_count': backtest.fork_count,
                'forked_from': backtest.forked_from_id,
                'results': {
                    **results_payload
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


@api_view(["GET"])
@permission_classes([IsAuthenticated])
@authentication_classes([BearerSessionAuthentication, CsrfExemptSessionAuthentication])
def list_backtests(request):
    """List all backtests"""
    try:
        category = request.GET.get('category')
        
        backtests = BacktestRun.objects.filter(user=request.user)
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
                    'is_public': bool(b.is_public),
                    'share_slug': b.share_slug,
                    'public_view_count': b.public_view_count,
                    'fork_count': b.fork_count,
                    'forked_from': b.forked_from_id,
                    'composite_score': float(b.composite_score) if b.composite_score else None,
                    'total_return': float(b.total_return) if b.total_return else None,
                    'results': (b.metrics_data if isinstance(b.metrics_data, dict) else None),
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


@api_view(["GET"])
@permission_classes([IsAuthenticated])
@authentication_classes([BearerSessionAuthentication, CsrfExemptSessionAuthentication])
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


@api_view(["GET"])
@permission_classes([IsAuthenticated])
@authentication_classes([BearerSessionAuthentication, CsrfExemptSessionAuthentication])
def get_backtest_limits(request):
    """Get user's backtest limits and usage"""
    try:
        limit = get_user_backtest_limit(request.user)
        used = get_user_backtests_this_month(request.user)

        # Check if user has no subscription
        if limit == 0:
            return JsonResponse({
                'success': False,
                'error': 'Subscription required. Subscribe to Basic or Plus plan to access backtesting.',
                'message': 'You need an active subscription to use backtesting. Basic plan: 2 backtests/month, Plus plan: Unlimited.',
                'upgrade_url': '/pricing'
            }, status=403)

        unlimited = limit == -1
        remaining = -1 if unlimited else max(0, limit - used)

        # Get tier name
        try:
            from billing.models import Subscription
            subscription = Subscription.objects.get(user=request.user, status='active')
            tier = subscription.plan_tier
        except:
            tier = 'none'

        return JsonResponse({
            'success': True,
            'data': {
                'tier': tier,
                'limit': limit,
                'used': used,
                'remaining': remaining,
                'unlimited': unlimited,
                'reset_date': (timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0) + timedelta(days=32)).replace(day=1).isoformat()
            }
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error retrieving backtest limits: {str(e)}'
        }, status=500)


@api_view(["GET"])
@permission_classes([AllowAny])
def get_public_backtest(request, backtest_id):
    """
    Get public backtest results for sharing
    No authentication required - allows viral sharing
    """
    try:
        backtest = BacktestRun.objects.get(id=backtest_id)

        # Only show completed backtests publicly
        if backtest.status != 'completed' or not backtest.is_public:
            return JsonResponse({
                'success': False,
                'error': 'Backtest not available for public viewing'
            }, status=404)

        # Track views
        try:
            backtest.public_view_count = (backtest.public_view_count or 0) + 1
            backtest.save(update_fields=['public_view_count'])
        except Exception:
            pass

        results_payload = {
            'total_return': float(backtest.total_return) if backtest.total_return else None,
            'annualized_return': float(backtest.annualized_return) if backtest.annualized_return else None,
            'sharpe_ratio': float(backtest.sharpe_ratio) if backtest.sharpe_ratio else None,
            'max_drawdown': float(backtest.max_drawdown) if backtest.max_drawdown else None,
            'win_rate': float(backtest.win_rate) if backtest.win_rate else None,
            'profit_factor': float(backtest.profit_factor) if backtest.profit_factor else None,
            'total_trades': backtest.total_trades,
            'composite_score': float(backtest.composite_score) if backtest.composite_score else None,
            # For older records that pre-date metrics_data, fall back to grade from score.
            'quality_grade': get_quality_grade(backtest.composite_score),
        }
        if isinstance(backtest.metrics_data, dict):
            results_payload.update(backtest.metrics_data)

        return JsonResponse({
            'success': True,
            'backtest': {
                'id': backtest.id,
                'name': backtest.name,
                'strategy_text': backtest.strategy_text,
                'category': backtest.category,
                'symbols': backtest.symbols,
                'start_date': str(backtest.start_date),
                'end_date': str(backtest.end_date),
                'initial_capital': float(backtest.initial_capital),
                'share_slug': backtest.share_slug,
                'public_view_count': backtest.public_view_count,
                'fork_count': backtest.fork_count,
                'creator': {
                    'username': getattr(backtest.user, 'username', None),
                },
                'results': results_payload,
                'equity_curve': backtest.equity_curve,
                'created_at': backtest.created_at.isoformat()
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


def get_quality_grade(score):
    """Convert composite score to letter grade"""
    if not score:
        return "N/A"
    if score >= 90:
        return "A+"
    elif score >= 80:
        return "A"
    elif score >= 70:
        return "B"
    elif score >= 60:
        return "C"
    elif score >= 50:
        return "D"
    else:
        return "F"


@api_view(["POST"])
@permission_classes([IsAuthenticated])
@authentication_classes([BearerSessionAuthentication, CsrfExemptSessionAuthentication])
def create_backtest_share_link(request, backtest_id):
    """
    Create (or return existing) public share link for a backtest.
    Sets is_public=True and assigns share_slug if missing.
    """
    try:
        backtest = BacktestRun.objects.get(id=backtest_id, user=request.user)
        if backtest.status != "completed":
            return JsonResponse({
                "success": False,
                "error": "Only completed backtests can be shared"
            }, status=400)

        if not backtest.share_slug:
            backtest.share_slug = _generate_unique_backtest_share_slug(backtest)

        backtest.is_public = True
        if not backtest.shared_at:
            backtest.shared_at = timezone.now()
        backtest.save(update_fields=["share_slug", "is_public", "shared_at"])

        return JsonResponse({
            "success": True,
            "slug": backtest.share_slug,
            "share_url": f"/backtest/{backtest.share_slug}",
        })
    except BacktestRun.DoesNotExist:
        return JsonResponse({
            "success": False,
            "error": "Backtest not found"
        }, status=404)
    except Exception as e:
        return JsonResponse({
            "success": False,
            "error": str(e)
        }, status=500)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
@authentication_classes([BearerSessionAuthentication, CsrfExemptSessionAuthentication])
def revoke_backtest_share_link(request, backtest_id):
    """Make a backtest private again (keeps slug for future reuse)."""
    try:
        backtest = BacktestRun.objects.get(id=backtest_id, user=request.user)
        backtest.is_public = False
        backtest.save(update_fields=["is_public"])
        return JsonResponse({"success": True})
    except BacktestRun.DoesNotExist:
        return JsonResponse({"success": False, "error": "Backtest not found"}, status=404)
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)


@api_view(["GET"])
@permission_classes([AllowAny])
def get_shared_backtest(request, slug):
    """
    Get a shared backtest by share slug (public, no auth).
    This is the endpoint used by `/backtest/:shareSlug`.
    """
    try:
        backtest = BacktestRun.objects.get(share_slug=slug, is_public=True, status="completed")

        # Track views
        try:
            backtest.public_view_count = (backtest.public_view_count or 0) + 1
            backtest.save(update_fields=["public_view_count"])
        except Exception:
            pass

        results_payload = {
            "total_return": float(backtest.total_return) if backtest.total_return else None,
            "annualized_return": float(backtest.annualized_return) if backtest.annualized_return else None,
            "sharpe_ratio": float(backtest.sharpe_ratio) if backtest.sharpe_ratio else None,
            "max_drawdown": float(backtest.max_drawdown) if backtest.max_drawdown else None,
            "win_rate": float(backtest.win_rate) if backtest.win_rate else None,
            "profit_factor": float(backtest.profit_factor) if backtest.profit_factor else None,
            "total_trades": backtest.total_trades,
            "composite_score": float(backtest.composite_score) if backtest.composite_score else None,
            # For older records that pre-date metrics_data, fall back to grade from score.
            "quality_grade": get_quality_grade(backtest.composite_score),
        }
        if isinstance(backtest.metrics_data, dict):
            results_payload.update(backtest.metrics_data)

        return JsonResponse({
            "success": True,
            "backtest": {
                "id": backtest.id,
                "name": backtest.name,
                "strategy_text": backtest.strategy_text,
                "category": backtest.category,
                "symbols": backtest.symbols,
                "start_date": str(backtest.start_date),
                "end_date": str(backtest.end_date),
                "initial_capital": float(backtest.initial_capital),
                "share_slug": backtest.share_slug,
                "public_view_count": backtest.public_view_count,
                "fork_count": backtest.fork_count,
                "creator": {
                    "username": getattr(backtest.user, "username", None),
                },
                "results": results_payload,
                "equity_curve": backtest.equity_curve,
                "created_at": backtest.created_at.isoformat(),
            }
        })
    except BacktestRun.DoesNotExist:
        return JsonResponse({"success": False, "error": "Backtest not found"}, status=404)
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
@authentication_classes([BearerSessionAuthentication, CsrfExemptSessionAuthentication])
def fork_backtest(request, backtest_id):
    """
    Fork a backtest by id. If it's not owned by the user, it must be public.
    Creates a new BacktestRun in 'pending' status with identical strategy inputs.
    """
    try:
        original = BacktestRun.objects.get(id=backtest_id)

        if original.status != "completed":
            return JsonResponse({"success": False, "error": "Only completed backtests can be forked"}, status=400)

        if original.user_id != request.user.id and not original.is_public:
            return JsonResponse({"success": False, "error": "Backtest is private"}, status=403)

        fork = BacktestRun.objects.create(
            user=request.user,
            name=f"{original.name} (Fork)",
            strategy_text=original.strategy_text,
            category=original.category,
            symbols=original.symbols,
            start_date=original.start_date,
            end_date=original.end_date,
            initial_capital=original.initial_capital,
            status="pending",
            is_public=False,
            forked_from=original,
        )
        _increment_fork_count(original)

        return JsonResponse({
            "success": True,
            "fork_backtest_id": fork.id,
            "forked_from": original.id,
        })
    except BacktestRun.DoesNotExist:
        return JsonResponse({"success": False, "error": "Backtest not found"}, status=404)
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
@authentication_classes([BearerSessionAuthentication, CsrfExemptSessionAuthentication])
def fork_shared_backtest(request, slug):
    """Fork a public shared backtest by slug."""
    try:
        original = BacktestRun.objects.get(share_slug=slug, is_public=True, status="completed")
        fork = BacktestRun.objects.create(
            user=request.user,
            name=f"{original.name} (Fork)",
            strategy_text=original.strategy_text,
            category=original.category,
            symbols=original.symbols,
            start_date=original.start_date,
            end_date=original.end_date,
            initial_capital=original.initial_capital,
            status="pending",
            is_public=False,
            forked_from=original,
        )
        _increment_fork_count(original)

        return JsonResponse({
            "success": True,
            "fork_backtest_id": fork.id,
            "forked_from": original.id,
        })
    except BacktestRun.DoesNotExist:
        return JsonResponse({"success": False, "error": "Backtest not found"}, status=404)
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)
