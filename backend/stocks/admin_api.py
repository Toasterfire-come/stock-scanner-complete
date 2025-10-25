"""
Admin API endpoints for metrics and admin operations
"""
from datetime import timedelta
from decimal import Decimal

from django.contrib.auth.models import User
from django.db.models import Count, Sum
from django.utils import timezone
from django.http import JsonResponse

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from .models import StockAlert, BillingHistory, UserProfile


def _forbidden():
    return JsonResponse({"success": False, "error": "FORBIDDEN"}, status=403)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def admin_metrics_api(request):
    """
    GET /api/admin/metrics/
    Returns basic platform metrics. Requires staff user.
    """
    user = request.user
    if not getattr(user, "is_staff", False):
        return _forbidden()

    now = timezone.now()
    last_30d = now - timedelta(days=30)
    last_7d = now - timedelta(days=7)

    total_users = User.objects.count()
    new_users_7d = User.objects.filter(date_joined__gte=last_7d).count()

    alerts_total = StockAlert.objects.count()
    alerts_active = StockAlert.objects.filter(is_active=True).count()

    rev = BillingHistory.objects.filter(created_at__gte=last_30d).aggregate(total=Sum("amount"))
    revenue_30d = rev.get("total") or Decimal("0.00")

    # Plan breakdown from UserProfile.plan_type (fallback if missing)
    plan_breakdown = list(
        UserProfile.objects.values("plan_type").annotate(count=Count("id")).order_by()
    )

    # Simple 7-day signup trend
    signup_trend = []
    for i in range(7, -1, -1):
        day_start = (now - timedelta(days=i)).replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)
        cnt = User.objects.filter(date_joined__gte=day_start, date_joined__lt=day_end).count()
        signup_trend.append({"date": day_start.date().isoformat(), "count": cnt})

    data = {
        "users": {"total": total_users, "new_7d": new_users_7d},
        "alerts": {"total": alerts_total, "active": alerts_active},
        "revenue": {"last_30d": str(revenue_30d)},
        "plans": plan_breakdown,
        "signups": signup_trend,
        "generated_at": now.isoformat(),
    }
    return JsonResponse({"success": True, "data": data})
