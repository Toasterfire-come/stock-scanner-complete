"""
Centralized plan limits and helpers.

This module defines per-plan limits for various resources and provides
helpers to retrieve effective limits for a given user/profile and to
check whether a given count exceeds the plan limit.
"""

from __future__ import annotations

from typing import Dict, Any

try:
    from django.contrib.auth.models import User  # type: ignore
except Exception:  # pragma: no cover - during migrations
    User = object  # type: ignore

try:
    from .models import UserProfile  # type: ignore
except Exception:  # pragma: no cover - model may not be ready during early migrations
    UserProfile = None  # type: ignore


DEFAULT_LIMITS_BY_PLAN: Dict[str, Dict[str, Any]] = {
    # Reasonable defaults; can be tuned per business requirements
    "free": {
        "monthly_api": 100,
        "alerts": 0,
        "watchlists": 1,
        "portfolios": 1,
        "screeners": 1,
        "import_rows_max": 200,
        "json_import_items_max": 200,
        "max_screener_criteria": 25,
    },
    "basic": {
        "monthly_api": 1000,
        "alerts": 20,
        "watchlists": 3,
        "portfolios": 2,
        "screeners": 5,
        "import_rows_max": 1000,
        "json_import_items_max": 1000,
        "max_screener_criteria": 50,
    },
    "bronze": {
        "monthly_api": 1500,
        "alerts": 50,
        "watchlists": 5,
        "portfolios": 3,
        "screeners": 10,
        "import_rows_max": 1500,
        "json_import_items_max": 1500,
        "max_screener_criteria": 60,
    },
    "silver": {
        "monthly_api": 5000,
        "alerts": 100,
        "watchlists": 10,
        "portfolios": 5,
        "screeners": 20,
        "import_rows_max": 5000,
        "json_import_items_max": 5000,
        "max_screener_criteria": 80,
    },
    "pro": {
        "monthly_api": 5000,
        "alerts": 100,
        "watchlists": 10,
        "portfolios": 5,
        "screeners": 20,
        "import_rows_max": 5000,
        "json_import_items_max": 5000,
        "max_screener_criteria": 80,
    },
    "gold": {
        "monthly_api": 100000,
        "alerts": float("inf"),
        "watchlists": float("inf"),
        "portfolios": float("inf"),
        "screeners": float("inf"),
        "import_rows_max": 50000,
        "json_import_items_max": 50000,
        "max_screener_criteria": 200,
    },
    "enterprise": {
        "monthly_api": 100000,
        "alerts": float("inf"),
        "watchlists": float("inf"),
        "portfolios": float("inf"),
        "screeners": float("inf"),
        "import_rows_max": 200000,
        "json_import_items_max": 200000,
        "max_screener_criteria": 500,
    },
}


def _get_user_profile(user: User):  # type: ignore
    if UserProfile is None:
        return None
    try:
        profile = getattr(user, "profile", None)
        if profile:
            return profile
        profile, _ = UserProfile.objects.get_or_create(user=user)
        return profile
    except Exception:
        return None


def get_limits_for_user(user: User) -> Dict[str, Any]:  # type: ignore
    """Return plan limits for the given user based on their profile.plan_type.

    Falls back to 'free' when the profile is unavailable.
    """
    try:
        profile = _get_user_profile(user)
        plan = str(getattr(profile, "plan_type", "free") or "free").lower()
        return DEFAULT_LIMITS_BY_PLAN.get(plan, DEFAULT_LIMITS_BY_PLAN["free"]).copy()
    except Exception:
        return DEFAULT_LIMITS_BY_PLAN["free"].copy()


def is_within_limit(user: User, kind: str, current_count: int) -> bool:  # type: ignore
    """Check if current_count is within user's plan limit for a given kind.

    kind in {"alerts", "watchlists", "portfolios", "screeners"}.
    """
    limits = get_limits_for_user(user)
    try:
        cap = limits.get(kind)
        if cap is None:
            return True
        if cap == float("inf"):
            return True
        return int(current_count) < int(cap)
    except Exception:
        return True

