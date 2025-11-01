"""
Partner analytics endpoints and referral redirect.
- /api/partner/analytics/summary
- /api/partner/analytics/timeseries
- /api/r/<code>
"""
from __future__ import annotations

from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, Any, List, Tuple

from django.conf import settings
from django.db.models import Sum
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


def _resolve_partner_code(request, raw_code: str | None) -> Tuple[str | None, str | None, int]:
    """Resolve partner code either from query param or inferred mapping.

    Returns (code, error_message, status_code).
    """
    try:
        code = (raw_code or '').upper().strip()
    except Exception:
        code = ''

    if code:
        ok, msg = _enforce_partner_access(request, code)
        if ok:
            return code, None, 200
        return None, msg or 'Not authorized for this partner code', 403

    # Attempt to infer from authenticated user's email
    user = getattr(request, 'user', None)
    email = (getattr(user, 'email', '') or '').lower().strip()
    mapping = getattr(settings, 'PARTNER_CODE_BY_EMAIL', {}) or {}
    inferred = (mapping.get(email) or '').upper().strip()

    if inferred:
        ok, msg = _enforce_partner_access(request, inferred)
        if ok:
            return inferred, None, 200
        return None, msg or 'Not authorized for inferred partner code', 403

    if getattr(user, 'is_staff', False):
        return None, 'code is required for staff users', 400

    return None, 'Partner referral access is not configured for this account', 404


def _dec_to_float(value: Decimal | float | int | None) -> float:
    if isinstance(value, Decimal):
        return float(value)
    if value is None:
        return 0.0
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


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
        raw_code = request.GET.get('code')
        code, error_msg, status_code = _resolve_partner_code(request, raw_code)
        if not code:
            return Response({'success': False, 'error': error_msg}, status=status_code)
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
        purchases_qs = RevenueTracking.objects.filter(
            discount_code__code=code,
            payment_date__gte=start,
            payment_date__lte=end,
        )
        purchases = purchases_qs.count()
        # Conversion rates
        trial_conv = (trials / clicks) * 100 if clicks else 0.0
        purchase_conv = (purchases / clicks) * 100 if clicks else 0.0

        # Revenue aggregates for window
        window_revenue_totals = purchases_qs.aggregate(
            total_revenue=Sum('final_amount'),
            total_commission=Sum('commission_amount'),
            total_discount=Sum('discount_amount'),
        )

        # Lifetime aggregates
        lifetime_clicks = ReferralClickEvent.objects.filter(code=code).count()
        lifetime_trials = ReferralTrialEvent.objects.filter(code=code).count()
        lifetime_purchases_qs = RevenueTracking.objects.filter(discount_code__code=code)
        lifetime_purchases = lifetime_purchases_qs.count()
        lifetime_revenue_totals = lifetime_purchases_qs.aggregate(
            total_revenue=Sum('final_amount'),
            total_commission=Sum('commission_amount'),
            total_discount=Sum('discount_amount'),
        )

        # Recent referral purchases (most recent 10)
        recent_purchases = []
        for entry in purchases_qs.select_related('user').order_by('-payment_date')[:10]:
            user = getattr(entry, 'user', None)
            profile = None
            if user:
                try:
                    profile = user.userprofile
                except Exception:
                    profile = None
            display_name = ''
            if user:
                full_name = f"{user.first_name} {user.last_name}".strip()
                display_name = full_name or user.username or (user.email or 'Referral')
            recent_purchases.append({
                'id': entry.id,
                'user': {
                    'id': getattr(user, 'id', None),
                    'name': display_name,
                    'email': getattr(user, 'email', None),
                },
                'plan': 'premium' if getattr(profile, 'is_premium', False) else 'trial',
                'final_amount': _dec_to_float(entry.final_amount),
                'commission_amount': _dec_to_float(entry.commission_amount),
                'discount_amount': _dec_to_float(entry.discount_amount),
                'payment_date': entry.payment_date.isoformat() if entry.payment_date else None,
                'status': 'paid' if _dec_to_float(entry.commission_amount) > 0 else 'pending',
            })

        discount_obj = DiscountCode.objects.filter(code=code).first()
        discount_meta = None
        if discount_obj:
            discount_meta = {
                'code': discount_obj.code,
                'discount_percentage': _dec_to_float(discount_obj.discount_percentage),
                'is_active': discount_obj.is_active,
                'first_payment_only': discount_obj.applies_to_first_payment_only,
            }

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
            'revenue': {
                'window': {
                    'total_revenue': _dec_to_float(window_revenue_totals.get('total_revenue')),
                    'total_commission': _dec_to_float(window_revenue_totals.get('total_commission')),
                    'total_discount': _dec_to_float(window_revenue_totals.get('total_discount')),
                },
                'lifetime': {
                    'total_revenue': _dec_to_float(lifetime_revenue_totals.get('total_revenue')),
                    'total_commission': _dec_to_float(lifetime_revenue_totals.get('total_commission')),
                    'total_discount': _dec_to_float(lifetime_revenue_totals.get('total_discount')),
                },
                'pending_commission': _dec_to_float(window_revenue_totals.get('total_commission')),
            },
            'lifetime': {
                'clicks': lifetime_clicks,
                'trials': lifetime_trials,
                'purchases': lifetime_purchases,
            },
            'recent_referrals': recent_purchases,
            'discount': discount_meta,
        })
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=500)


# ----- Analytics: timeseries -----

@csrf_exempt
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def partner_analytics_timeseries_api(request):
    try:
        raw_code = request.GET.get('code')
        code, error_msg, status_code = _resolve_partner_code(request, raw_code)
        if not code:
            return Response({'success': False, 'error': error_msg}, status=status_code)
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
