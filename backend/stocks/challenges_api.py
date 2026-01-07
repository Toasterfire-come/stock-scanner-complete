"""
Weekly Challenges API (Phase: Viral Engagement)

Minimal implementation:
- current weekly challenge (no DB required)
- placeholder leaderboard endpoint
"""

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone


def _current_week_key():
    now = timezone.now()
    iso = now.isocalendar()
    return int(iso.year), int(iso.week)


def _get_current_challenge_payload():
    year, week = _current_week_key()
    # Keep deterministic for the week
    return {
        "id": f"{year}-W{week}",
        "title": "Momentum Week",
        "description": "Create a momentum strategy and beat the benchmark return.",
        "rules": [
            "Backtest any US equity symbol(s)",
            "Timeframe: last 1 year",
            "Goal: maximize composite score with positive return",
        ],
        "target": {
            "metric": "total_return",
            "threshold": 15.0,
            "unit": "%",
        },
        "period": {
            "year": year,
            "week": week,
        },
        "status": "active",
    }


@csrf_exempt
@require_http_methods(["GET"])
def get_current_challenge(request):
    return JsonResponse({"success": True, "challenge": _get_current_challenge_payload()})


@csrf_exempt
@require_http_methods(["GET"])
def get_challenge_leaderboard(request):
    """
    Placeholder: returns empty leaderboard until backed by DB submissions.
    """
    challenge = _get_current_challenge_payload()
    return JsonResponse({
        "success": True,
        "challenge": challenge,
        "leaderboard": [],
    })

