"""
Visitor and checkout analytics API endpoints.
Tracks:
- Visitor events (page views, checkout starts, purchases)
- Checkout progress and completions
- US-based visitors
- Geographic analytics
"""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Dict, Any
import hashlib

from django.db.models import Count, Q, Sum
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from .models import VisitorEvent, CheckoutEvent, User


def _get_country_from_ip(request) -> str:
    """Extract country code from request headers or IP.

    In production, this should use a GeoIP database or service.
    For now, returns 'US' by default or from CloudFlare/proxy headers.
    """
    # Check CloudFlare header
    country = request.META.get('HTTP_CF_IPCOUNTRY', '')
    if country:
        return country.upper()[:2]

    # Check other common headers
    country = request.META.get('HTTP_X_COUNTRY_CODE', '')
    if country:
        return country.upper()[:2]

    # Default to US (in production, use GeoIP lookup)
    return 'US'


def _get_session_id(request) -> str:
    """Get or create session ID"""
    try:
        if not request.session.session_key:
            request.session.save()
        return str(request.session.session_key)
    except Exception:
        return ''


def _hash_ip(request) -> str:
    """Hash IP address for privacy"""
    ip = request.META.get('HTTP_X_FORWARDED_FOR', '').split(',')[0].strip()
    if not ip:
        ip = request.META.get('REMOTE_ADDR', 'unknown')
    try:
        return hashlib.sha256(ip.encode('utf-8')).hexdigest()
    except Exception:
        return 'unknown'


# ----- Tracking Endpoints -----

@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def track_visitor_event(request):
    """Track visitor event (page view, checkout start, purchase)

    POST /api/analytics/visitor/track
    Body:
    {
        "event_type": "page_view" | "checkout_start" | "purchase_complete",
        "page_url": "/pricing/",
        "metadata": {}
    }
    """
    try:
        data = request.data
        event_type = data.get('event_type', 'page_view')
        page_url = data.get('page_url', '')

        # Validate event type
        valid_types = ['page_view', 'checkout_start', 'purchase_complete']
        if event_type not in valid_types:
            return Response({'success': False, 'error': 'Invalid event_type'}, status=400)

        # Create visitor event
        VisitorEvent.objects.create(
            session_id=_get_session_id(request),
            ip_hash=_hash_ip(request),
            country_code=_get_country_from_ip(request),
            event_type=event_type,
            page_url=page_url[:512],
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:1000],
            user=request.user if request.user.is_authenticated else None,
            occurred_at=timezone.now(),
        )

        return Response({'success': True, 'event_type': event_type})
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def track_checkout_event(request):
    """Track checkout progress

    POST /api/analytics/checkout/track
    Body:
    {
        "status": "started" | "payment_info" | "processing" | "completed" | "abandoned",
        "plan_name": "Premium Monthly",
        "amount": 29.99,
        "referral_code": "ADAM50"
    }
    """
    try:
        data = request.data
        status = data.get('status', 'started')
        plan_name = data.get('plan_name', '')
        amount = data.get('amount')
        referral_code = data.get('referral_code', '')

        # Validate status
        valid_statuses = ['started', 'payment_info', 'processing', 'completed', 'abandoned']
        if status not in valid_statuses:
            return Response({'success': False, 'error': 'Invalid status'}, status=400)

        session_id = _get_session_id(request)
        country_code = _get_country_from_ip(request)

        # Find existing checkout or create new one
        checkout, created = CheckoutEvent.objects.get_or_create(
            session_id=session_id,
            status__in=['started', 'payment_info', 'processing'],  # Not completed/abandoned
            defaults={
                'user': request.user if request.user.is_authenticated else None,
                'status': status,
                'plan_name': plan_name[:100],
                'amount': amount,
                'country_code': country_code,
                'referral_code': referral_code[:50],
                'started_at': timezone.now(),
            }
        )

        # Update existing checkout
        if not created:
            checkout.status = status
            checkout.plan_name = plan_name[:100] if plan_name else checkout.plan_name
            checkout.amount = amount if amount is not None else checkout.amount
            checkout.referral_code = referral_code[:50] if referral_code else checkout.referral_code

            # Set completed_at if status is completed
            if status == 'completed' and not checkout.completed_at:
                checkout.completed_at = timezone.now()

            checkout.save()

        # Also track as visitor event
        if status == 'started':
            VisitorEvent.objects.create(
                session_id=session_id,
                ip_hash=_hash_ip(request),
                country_code=country_code,
                event_type='checkout_start',
                page_url='/checkout/',
                user_agent=request.META.get('HTTP_USER_AGENT', '')[:1000],
                user=request.user if request.user.is_authenticated else None,
                occurred_at=timezone.now(),
            )
        elif status == 'completed':
            VisitorEvent.objects.create(
                session_id=session_id,
                ip_hash=_hash_ip(request),
                country_code=country_code,
                event_type='purchase_complete',
                page_url='/checkout/success/',
                user_agent=request.META.get('HTTP_USER_AGENT', '')[:1000],
                user=request.user if request.user.is_authenticated else None,
                occurred_at=timezone.now(),
            )

        return Response({
            'success': True,
            'checkout_id': checkout.id,
            'status': checkout.status,
            'created': created,
        })
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=500)


# ----- Analytics Endpoints -----

@csrf_exempt
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_visitor_analytics(request):
    """Get visitor analytics summary

    GET /api/analytics/visitors/summary?from=2025-01-01&to=2025-01-31&country=US

    Returns:
    - Total visitors (unique sessions)
    - US-based visitors
    - Visitors by country
    - Page views
    - Checkout starts
    - Purchase completions
    """
    try:
        # Date range (default: last 30 days)
        now = timezone.now()
        start_default = now - timedelta(days=30)

        start_str = request.GET.get('from')
        end_str = request.GET.get('to')
        country_filter = request.GET.get('country', '').upper()

        try:
            start = datetime.fromisoformat(start_str.replace('Z', '+00:00')) if start_str else start_default
        except Exception:
            start = start_default

        try:
            end = datetime.fromisoformat(end_str.replace('Z', '+00:00')) if end_str else now
        except Exception:
            end = now

        if timezone.is_naive(start):
            start = timezone.make_aware(start, timezone.utc)
        if timezone.is_naive(end):
            end = timezone.make_aware(end, timezone.utc)

        # Base queryset
        visitors_qs = VisitorEvent.objects.filter(
            occurred_at__gte=start,
            occurred_at__lte=end
        )

        if country_filter:
            visitors_qs = visitors_qs.filter(country_code=country_filter)

        # Total unique visitors (by session)
        total_visitors = visitors_qs.values('session_id').distinct().count()

        # US-based visitors
        us_visitors = visitors_qs.filter(country_code='US').values('session_id').distinct().count()

        # Event counts
        page_views = visitors_qs.filter(event_type='page_view').count()
        checkout_starts = visitors_qs.filter(event_type='checkout_start').count()
        purchases = visitors_qs.filter(event_type='purchase_complete').count()

        # Visitors by country
        by_country = visitors_qs.values('country_code').annotate(
            count=Count('session_id', distinct=True)
        ).order_by('-count')[:20]

        # Conversion rates
        checkout_conversion = (checkout_starts / total_visitors * 100) if total_visitors else 0
        purchase_conversion = (purchases / total_visitors * 100) if total_visitors else 0

        return Response({
            'success': True,
            'period': {
                'from': start.isoformat(),
                'to': end.isoformat(),
            },
            'totals': {
                'total_visitors': total_visitors,
                'us_visitors': us_visitors,
                'us_percentage': round((us_visitors / total_visitors * 100) if total_visitors else 0, 2),
                'page_views': page_views,
                'checkout_starts': checkout_starts,
                'purchases': purchases,
            },
            'conversions': {
                'checkout_rate': round(checkout_conversion, 2),
                'purchase_rate': round(purchase_conversion, 2),
            },
            'by_country': [
                {'country': item['country_code'], 'visitors': item['count']}
                for item in by_country
            ],
        })
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_checkout_analytics(request):
    """Get checkout analytics

    GET /api/analytics/checkout/summary?from=2025-01-01&to=2025-01-31

    Returns:
    - Active checkouts (at checkout now)
    - Completed purchases
    - Abandoned checkouts
    - Average checkout time
    - Revenue by country
    """
    try:
        # Date range
        now = timezone.now()
        start_default = now - timedelta(days=30)

        start_str = request.GET.get('from')
        end_str = request.GET.get('to')

        try:
            start = datetime.fromisoformat(start_str.replace('Z', '+00:00')) if start_str else start_default
        except Exception:
            start = start_default

        try:
            end = datetime.fromisoformat(end_str.replace('Z', '+00:00')) if end_str else now
        except Exception:
            end = now

        if timezone.is_naive(start):
            start = timezone.make_aware(start, timezone.utc)
        if timezone.is_naive(end):
            end = timezone.make_aware(end, timezone.utc)

        # Base queryset
        checkouts_qs = CheckoutEvent.objects.filter(started_at__gte=start, started_at__lte=end)

        # Active checkouts (started/processing, not completed/abandoned, last 1 hour)
        active_cutoff = now - timedelta(hours=1)
        active_checkouts = CheckoutEvent.objects.filter(
            status__in=['started', 'payment_info', 'processing'],
            started_at__gte=active_cutoff
        ).count()

        # Completed purchases
        completed = checkouts_qs.filter(status='completed').count()

        # Abandoned checkouts
        abandoned = checkouts_qs.filter(status='abandoned').count()

        # Total started
        total_started = checkouts_qs.filter(status__in=['started', 'payment_info', 'processing', 'completed', 'abandoned']).count()

        # Completion rate
        completion_rate = (completed / total_started * 100) if total_started else 0

        # Revenue
        revenue_data = checkouts_qs.filter(status='completed').aggregate(
            total_revenue=Sum('amount'),
            avg_order_value=Sum('amount') / Count('id') if checkouts_qs.filter(status='completed').exists() else 0
        )

        total_revenue = float(revenue_data.get('total_revenue') or 0)

        # Revenue by country
        by_country = checkouts_qs.filter(status='completed').values('country_code').annotate(
            revenue=Sum('amount'),
            count=Count('id')
        ).order_by('-revenue')[:10]

        # US revenue
        us_revenue = checkouts_qs.filter(status='completed', country_code='US').aggregate(
            total=Sum('amount')
        )['total'] or 0
        us_revenue = float(us_revenue)

        return Response({
            'success': True,
            'period': {
                'from': start.isoformat(),
                'to': end.isoformat(),
            },
            'totals': {
                'active_checkouts': active_checkouts,
                'completed_purchases': completed,
                'abandoned_checkouts': abandoned,
                'total_started': total_started,
                'completion_rate': round(completion_rate, 2),
            },
            'revenue': {
                'total': round(total_revenue, 2),
                'us_revenue': round(us_revenue, 2),
                'us_percentage': round((us_revenue / total_revenue * 100) if total_revenue else 0, 2),
            },
            'by_country': [
                {
                    'country': item['country_code'],
                    'revenue': round(float(item['revenue'] or 0), 2),
                    'purchases': item['count'],
                }
                for item in by_country
            ],
        })
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_realtime_dashboard(request):
    """Get real-time dashboard metrics

    GET /api/analytics/realtime

    Returns current:
    - Active checkouts (people at checkout now)
    - Recent purchases (last 24h)
    - Active visitors (last 15min)
    - US visitor percentage
    """
    try:
        now = timezone.now()

        # Active checkouts (last 30 minutes, not completed/abandoned)
        active_cutoff = now - timedelta(minutes=30)
        active_checkouts = CheckoutEvent.objects.filter(
            status__in=['started', 'payment_info', 'processing'],
            started_at__gte=active_cutoff
        ).count()

        # Recent purchases (last 24 hours)
        recent_cutoff = now - timedelta(hours=24)
        recent_purchases = CheckoutEvent.objects.filter(
            status='completed',
            completed_at__gte=recent_cutoff
        ).count()

        # Active visitors (last 15 minutes)
        visitor_cutoff = now - timedelta(minutes=15)
        active_visitors = VisitorEvent.objects.filter(
            occurred_at__gte=visitor_cutoff
        ).values('session_id').distinct().count()

        # US visitors (last 15 minutes)
        us_visitors = VisitorEvent.objects.filter(
            occurred_at__gte=visitor_cutoff,
            country_code='US'
        ).values('session_id').distinct().count()

        # US percentage
        us_percentage = (us_visitors / active_visitors * 100) if active_visitors else 0

        # Recent completed purchases (last 10)
        recent_purchases_list = []
        for checkout in CheckoutEvent.objects.filter(status='completed').order_by('-completed_at')[:10]:
            recent_purchases_list.append({
                'amount': float(checkout.amount) if checkout.amount else 0,
                'country': checkout.country_code,
                'completed_at': checkout.completed_at.isoformat() if checkout.completed_at else None,
                'plan': checkout.plan_name,
            })

        return Response({
            'success': True,
            'realtime': {
                'active_checkouts': active_checkouts,
                'active_visitors': active_visitors,
                'us_visitors': us_visitors,
                'us_percentage': round(us_percentage, 2),
            },
            'recent_24h': {
                'purchases': recent_purchases,
            },
            'recent_purchases': recent_purchases_list,
            'updated_at': now.isoformat(),
        })
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=500)
