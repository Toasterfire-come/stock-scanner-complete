"""
Partner analytics endpoints and referral redirect.
- /api/partner/analytics/summary
- /api/partner/analytics/timeseries
- /api/r/<code>
"""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Dict, Any, List

from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.shortcuts import redirect
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from .models import ReferralClickEvent, ReferralTrialEvent, RevenueTracking, DiscountCode


# ----- Utilities -----

def _parse_dt(s: str | None, default: datetime) -> datetime:
    if not s:
        return default
    try:
        # Accept ISO or YYYY-MM-DD
        return datetime.fromisoformat(s.replace('Z', '+00:00'))
    except Exception:
        try:
            return datetime.strptime(s, '%Y-%m-%d')
        except Exception:
            return default


def _enforce_partner_access(request, code: str) -> tuple[bool, str | None]:
    """Check that the authenticated user's email is mapped to the partner code.
    Staff users are allowed for convenience.
    """
    try:
        user = getattr(request, 'user', None)
        if user and getattr(user, 'is_staff', False):
            return True, None
        email = (getattr(user, 'email', '') or '').lower().strip()
        mapping = getattr(settings, 'PARTNER_CODE_BY_EMAIL', {}) or {}
        allowed_code = mapping.get(email)
        if allowed_code and allowed_code.upper().strip() == (code or '').upper().strip():
            return True, None
        return False, 'Not authorized for this partner code'
    except Exception as e:
        return False, f'Access check failed: {e}'


# ----- Redirect: /r/<code> -----

@csrf_exempt
@require_http_methods(["GET"])  # type: ignore
@authentication_classes([])
@permission_classes([AllowAny])
def referral_redirect(request, code: str):
    """Set referral cookie and record click, then redirect to destination.
    Accepts optional query param 'to' as redirect target; defaults to '/pricing/'.
    Keeps cookie ~60 days.
    """
    try:
        # Normalize code
        code = (code or '').upper().strip()
        # Compute ip hash
        ip = request.META.get('HTTP_X_FORWARDED_FOR') or request.META.get('REMOTE_ADDR') or 'unknown'
        try:
            import hashlib
            ip_hash = hashlib.sha256(ip.encode('utf-8')).hexdigest()
        except Exception:
            ip_hash = 'unknown'
        # Ensure session exists for session_id capture
        try:
            if not getattr(request, 'session', None) or not request.session.session_key:
                request.session.save()
        except Exception:
            pass
        session_id = str(getattr(request, 'session', None) and request.session.session_key or '')
        # Persist click
        try:
            ReferralClickEvent.objects.create(
                code=code,
                session_id=session_id,
                ip_hash=ip_hash,
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                occurred_at=timezone.now(),
            )
        except Exception:
            pass
        # Build redirect
        dest = request.GET.get('to') or '/pricing/'
        resp = redirect(dest)
        # Set referral cookie ~60 days
        try:
            resp.set_cookie('ref', code, max_age=60 * 60 * 24 * 60, samesite='Lax')
        except Exception:
            pass
        return resp
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# ----- Analytics: summary -----

@csrf_exempt
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def partner_analytics_summary_api(request):
    try:
        code = (request.GET.get('code') or '').upper().strip()
        if not code:
            return Response({'success': False, 'error': 'code is required'}, status=400)
        ok, msg = _enforce_partner_access(request, code)
        if not ok:
            return Response({'success': False, 'error': msg}, status=403)
        now = timezone.now()
        start_default = now - timedelta(days=30)
        start = _parse_dt(request.GET.get('from'), start_default)
        end = _parse_dt(request.GET.get('to'), now)
        # Normalize to timezone-aware UTC
        if timezone.is_naive(start):
            start = timezone.make_aware(start, timezone.utc)
        if timezone.is_naive(end):
            end = timezone.make_aware(end, timezone.utc)
        # Clicks
        clicks = ReferralClickEvent.objects.filter(code=code, occurred_at__gte=start, occurred_at__lte=end).count()
        # Trials (unique users)
        trials_qs = ReferralTrialEvent.objects.filter(code=code, occurred_at__gte=start, occurred_at__lte=end)
        trials = trials_qs.count()
        unique_trial_users = trials_qs.exclude(user__isnull=True).values('user').distinct().count()
        # Purchases via discount code
        purchases = RevenueTracking.objects.filter(
            discount_code__code=code,
            payment_date__gte=start,
            payment_date__lte=end,
        ).count()
        # Conversion rates
        trial_conv = (trials / clicks) * 100 if clicks else 0.0
        purchase_conv = (purchases / clicks) * 100 if clicks else 0.0
        return Response({
            'success': True,
            'code': code,
            'window': {
                'from': start.isoformat(),
                'to': end.isoformat(),
            },
            'totals': {
                'clicks': clicks,
                'trials': trials,
                'unique_trial_users': unique_trial_users,
                'purchases': purchases,
                'trial_conversion_percent': round(trial_conv, 2),
                'purchase_conversion_percent': round(purchase_conv, 2),
            },
        })
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=500)


# ----- Analytics: timeseries -----

@csrf_exempt
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def partner_analytics_timeseries_api(request):
    try:
        code = (request.GET.get('code') or '').upper().strip()
        if not code:
            return Response({'success': False, 'error': 'code is required'}, status=400)
        ok, msg = _enforce_partner_access(request, code)
        if not ok:
            return Response({'success': False, 'error': msg}, status=403)
        now = timezone.now()
        start_default = now - timedelta(days=30)
        start = _parse_dt(request.GET.get('from'), start_default)
        end = _parse_dt(request.GET.get('to'), now)
        interval = (request.GET.get('interval') or 'day').lower()
        if timezone.is_naive(start):
            start = timezone.make_aware(start, timezone.utc)
        if timezone.is_naive(end):
            end = timezone.make_aware(end, timezone.utc)
        # Build buckets
        buckets: List[datetime] = []
        cursor = start
        step = timedelta(days=1) if interval in ['day', 'daily'] else timedelta(weeks=1)
        while cursor <= end:
            buckets.append(cursor)
            cursor = cursor + step
        # Preload events
        clicks = ReferralClickEvent.objects.filter(code=code, occurred_at__gte=start, occurred_at__lte=end)
        trials = ReferralTrialEvent.objects.filter(code=code, occurred_at__gte=start, occurred_at__lte=end)
        purchases = RevenueTracking.objects.filter(discount_code__code=code, payment_date__gte=start, payment_date__lte=end)
        # Aggregate per bucket
        series = []
        for i, b in enumerate(buckets):
            b_end = buckets[i + 1] if i + 1 < len(buckets) else end
            c = clicks.filter(occurred_at__gte=b, occurred_at__lt=b_end).count()
            t = trials.filter(occurred_at__gte=b, occurred_at__lt=b_end).count()
            p = purchases.filter(payment_date__gte=b, payment_date__lt=b_end).count()
            series.append({
                't': b.isoformat(),
                'clicks': c,
                'trials': t,
                'purchases': p,
            })
        return Response({'success': True, 'code': code, 'interval': interval, 'series': series, 'from': start.isoformat(), 'to': end.isoformat()})
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=500)
