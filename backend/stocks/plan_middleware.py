"""
Plan-related middleware: lightweight, safe defaults.

This module provides two middlewares referenced by settings:
 - PlanLimitMiddleware: attaches a derived plan to the request
 - PlanFeatureMiddleware: exposes feature flags based on the plan

Both middlewares are intentionally non-blocking by default to avoid
development or startup failures if database or auth is unavailable.
They can be extended later to enforce stricter rules.
"""

from __future__ import annotations

from typing import Callable, Dict

from django.conf import settings


def _determine_user_plan(request) -> str:
    """
    Determine the user's plan using safe heuristics:
    - Forced mapping via settings.FORCED_PLAN_BY_EMAIL (case-insensitive)
    - User groups (if authenticated): first matching in priority order
    - Default to 'free'
    """
    try:
        if getattr(request, "user", None) and request.user.is_authenticated:
            # Forced mapping by email takes precedence
            email = (getattr(request.user, "email", "") or "").strip().lower()
            forced_map = getattr(settings, "FORCED_PLAN_BY_EMAIL", {}) or {}
            if email and email in forced_map:
                return str(forced_map[email]).strip().lower() or "free"

            # Derive from Django groups if available
            try:
                group_names = {g.name.strip().lower() for g in request.user.groups.all()}
                for candidate in ("enterprise", "gold", "pro", "premium", "silver", "bronze"):
                    if candidate in group_names:
                        return candidate
            except Exception:
                # Groups may not be available yet (e.g., during migrations)
                pass
            return "free"
    except Exception:
        # Never fail request processing due to plan resolution
        return "free"
    return "free"


class PlanLimitMiddleware:
    """Attach basic plan and limit hints to the request.

    This middleware does not enforce hard limits. Enforcement should be
    handled by dedicated rate limiting middleware or views. Here we only
    annotate the request with plan metadata.
    """

    def __init__(self, get_response: Callable):
        self.get_response = get_response

    def __call__(self, request):
        plan_name = _determine_user_plan(request)
        request.plan_name = plan_name

        # Expose simple per-plan hints (can be read by views or templates)
        # Values are conservative defaults and can be overridden later.
        default_limits: Dict[str, int] = {
            "free": int(getattr(settings, "RATE_LIMIT_FREE_USERS", 30)),
            "pro": int(getattr(settings, "RATE_LIMIT_AUTHENTICATED_USERS", 1000)),
            "premium": int(getattr(settings, "RATE_LIMIT_AUTHENTICATED_USERS", 1000)),
            "gold": int(getattr(settings, "RATE_LIMIT_AUTHENTICATED_USERS", 1000)),
            "enterprise": 10_000,
        }
        request.plan_limits = {
            "hourly_api_limit": default_limits.get(plan_name, default_limits["free"]),
        }
        return self.get_response(request)


class PlanFeatureMiddleware:
    """Expose feature flags per plan without blocking requests.

    Downstream code can check request.features.get("feature_name") to show/hide
    UI affordances or enable optional processing.
    """

    def __init__(self, get_response: Callable):
        self.get_response = get_response

    def __call__(self, request):
        plan_name = getattr(request, "plan_name", None) or _determine_user_plan(request)

        # Simple feature gating map. Extend as needed.
        features_by_plan = {
            "free": {
                "advanced_screening": False,
                "developer_tools": False,
                "priority_support": False,
            },
            "pro": {
                "advanced_screening": True,
                "developer_tools": False,
                "priority_support": False,
            },
            "premium": {
                "advanced_screening": True,
                "developer_tools": True,
                "priority_support": True,
            },
            "gold": {
                "advanced_screening": True,
                "developer_tools": True,
                "priority_support": True,
            },
            "enterprise": {
                "advanced_screening": True,
                "developer_tools": True,
                "priority_support": True,
            },
        }

        request.features = features_by_plan.get(plan_name, features_by_plan["free"]).copy()
        request.plan_name = plan_name
        return self.get_response(request)

