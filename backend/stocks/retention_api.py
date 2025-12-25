"""
Retention & Habits API Endpoints (Phase 9 - MVP2 v3.4)
Handles trading journals, performance reviews, custom indicators, exports, and alerts.
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from datetime import date, timedelta

from .models import (
    TradingJournal, PerformanceReview, UserCustomIndicator,
    TradeExport, AlertTemplate, TriggeredAlert
)
from .services.retention_service import (
    TradingJournalService, PerformanceReviewService,
    UserCustomIndicatorService, TradeExportService, AlertService
)
from .serializers import (
    TradingJournalSerializer, PerformanceReviewSerializer,
    UserCustomIndicatorSerializer, TradeExportSerializer,
    AlertTemplateSerializer, TriggeredAlertSerializer
)


# ============================================================================
# Trading Journal Endpoints
# ============================================================================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_journal_entry(request):
    """Create a new journal entry."""
    result = TradingJournalService.create_entry(request.user, request.data)

    serializer = TradingJournalSerializer(result['entry'])

    return Response({
        'success': True,
        'entry': serializer.data
    })


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_journal_entry(request, entry_id):
    """Update an existing journal entry."""
    result = TradingJournalService.update_entry(request.user, entry_id, request.data)

    if not result['success']:
        return Response(result, status=404)

    serializer = TradingJournalSerializer(result['entry'])

    return Response({
        'success': True,
        'entry': serializer.data
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_my_journal_entries(request):
    """Get authenticated user's journal entries."""
    filters = {}

    if request.GET.get('emotion'):
        filters['emotion'] = request.GET.get('emotion')

    if request.GET.get('followed_plan'):
        filters['followed_plan'] = request.GET.get('followed_plan') == 'true'

    if request.GET.get('tags'):
        filters['tags'] = request.GET.get('tags')

    if request.GET.get('date_from'):
        filters['date_from'] = request.GET.get('date_from')

    if request.GET.get('date_to'):
        filters['date_to'] = request.GET.get('date_to')

    limit = int(request.GET.get('limit', 50))

    result = TradingJournalService.get_user_entries(request.user, filters, limit)

    serializer = TradingJournalSerializer(result['entries'], many=True)

    return Response({
        'success': True,
        'entries': serializer.data,
        'count': len(serializer.data)
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_journal_stats(request):
    """Get emotional statistics from journal entries."""
    result = TradingJournalService.get_emotion_stats(request.user)

    return Response({
        'success': True,
        'stats': result['stats']
    })


# ============================================================================
# Performance Review Endpoints
# ============================================================================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_performance_review(request):
    """Generate a new performance review."""
    review_period = request.data.get('review_period', 'monthly')
    period_start = request.data.get('period_start')
    period_end = request.data.get('period_end')

    # Parse dates if provided as strings
    if period_start and isinstance(period_start, str):
        period_start = date.fromisoformat(period_start)

    if period_end and isinstance(period_end, str):
        period_end = date.fromisoformat(period_end)

    result = PerformanceReviewService.generate_review(
        request.user,
        review_period,
        period_start,
        period_end
    )

    if not result['success']:
        return Response(result, status=400)

    serializer = PerformanceReviewSerializer(result['review'])

    return Response({
        'success': True,
        'review': serializer.data
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_my_performance_reviews(request):
    """Get authenticated user's performance reviews."""
    limit = int(request.GET.get('limit', 12))

    result = PerformanceReviewService.get_user_reviews(request.user, limit)

    serializer = PerformanceReviewSerializer(result['reviews'], many=True)

    return Response({
        'success': True,
        'reviews': serializer.data,
        'count': len(serializer.data)
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_performance_review(request, review_id):
    """Get a specific performance review."""
    try:
        review = PerformanceReview.objects.get(id=review_id, user=request.user)

        serializer = PerformanceReviewSerializer(review)

        return Response({
            'success': True,
            'review': serializer.data
        })
    except PerformanceReview.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Review not found'
        }, status=404)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_review_viewed(request, review_id):
    """Mark a review as viewed."""
    result = PerformanceReviewService.mark_review_viewed(request.user, review_id)

    if not result['success']:
        return Response(result, status=404)

    serializer = PerformanceReviewSerializer(result['review'])

    return Response({
        'success': True,
        'review': serializer.data
    })


# ============================================================================
# Custom Indicator Endpoints
# ============================================================================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_custom_indicator(request):
    """Create a custom indicator."""
    result = UserCustomIndicatorService.create_indicator(request.user, request.data)

    serializer = UserCustomIndicatorSerializer(result['indicator'])

    return Response({
        'success': True,
        'indicator': serializer.data
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_my_custom_indicators(request):
    """Get authenticated user's custom indicators."""
    result = UserCustomIndicatorService.get_user_indicators(request.user)

    serializer = UserCustomIndicatorSerializer(result['indicators'], many=True)

    return Response({
        'success': True,
        'indicators': serializer.data,
        'count': len(serializer.data)
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_public_custom_indicators(request):
    """Get public custom indicators."""
    limit = int(request.GET.get('limit', 50))

    result = UserCustomIndicatorService.get_public_indicators(limit)

    serializer = UserCustomIndicatorSerializer(result['indicators'], many=True)

    return Response({
        'success': True,
        'indicators': serializer.data,
        'count': len(serializer.data)
    })


# ============================================================================
# Trade Export Endpoints
# ============================================================================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def request_trade_export(request):
    """Request a trade data export."""
    export_data = {
        'export_format': request.data.get('export_format', 'csv'),
        'date_from': request.data.get('date_from'),
        'date_to': request.data.get('date_to'),
        'include_paper_trades': request.data.get('include_paper_trades', True),
        'include_live_trades': request.data.get('include_live_trades', False),
        'strategy_filter_id': request.data.get('strategy_filter_id')
    }

    # Parse dates if provided as strings
    if export_data['date_from'] and isinstance(export_data['date_from'], str):
        export_data['date_from'] = date.fromisoformat(export_data['date_from'])

    if export_data['date_to'] and isinstance(export_data['date_to'], str):
        export_data['date_to'] = date.fromisoformat(export_data['date_to'])

    # Default to last 30 days if not provided
    if not export_data['date_to']:
        export_data['date_to'] = date.today()

    if not export_data['date_from']:
        export_data['date_from'] = export_data['date_to'] - timedelta(days=30)

    result = TradeExportService.request_export(request.user, export_data)

    serializer = TradeExportSerializer(result['export'])

    return Response({
        'success': True,
        'export': serializer.data
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_my_exports(request):
    """Get authenticated user's export history."""
    result = TradeExportService.get_user_exports(request.user)

    serializer = TradeExportSerializer(result['exports'], many=True)

    return Response({
        'success': True,
        'exports': serializer.data,
        'count': len(serializer.data)
    })


# ============================================================================
# Alert Template Endpoints
# ============================================================================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_alert(request):
    """Create a custom alert template."""
    result = AlertService.create_alert(request.user, request.data)

    serializer = AlertTemplateSerializer(result['alert'])

    return Response({
        'success': True,
        'alert': serializer.data
    })


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_alert(request, alert_id):
    """Update an alert template."""
    result = AlertService.update_alert(request.user, alert_id, request.data)

    if not result['success']:
        return Response(result, status=404)

    serializer = AlertTemplateSerializer(result['alert'])

    return Response({
        'success': True,
        'alert': serializer.data
    })


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_alert(request, alert_id):
    """Delete an alert template."""
    try:
        alert = AlertTemplate.objects.get(id=alert_id, user=request.user)
        alert.delete()

        return Response({
            'success': True,
            'message': 'Alert deleted'
        })
    except AlertTemplate.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Alert not found'
        }, status=404)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_my_alerts(request):
    """Get authenticated user's alert templates."""
    result = AlertService.get_user_alerts(request.user)

    serializer = AlertTemplateSerializer(result['alerts'], many=True)

    return Response({
        'success': True,
        'alerts': serializer.data,
        'count': len(serializer.data)
    })


# ============================================================================
# Triggered Alert Endpoints
# ============================================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_triggered_alerts(request):
    """Get triggered alerts for authenticated user."""
    is_acknowledged = request.GET.get('is_acknowledged')

    if is_acknowledged == 'true':
        is_acknowledged = True
    elif is_acknowledged == 'false':
        is_acknowledged = False
    else:
        is_acknowledged = None

    limit = int(request.GET.get('limit', 50))

    result = AlertService.get_triggered_alerts(request.user, is_acknowledged, limit)

    serializer = TriggeredAlertSerializer(result['triggers'], many=True)

    return Response({
        'success': True,
        'triggers': serializer.data,
        'count': len(serializer.data)
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def acknowledge_alert(request, trigger_id):
    """Acknowledge a triggered alert."""
    result = AlertService.acknowledge_alert(request.user, trigger_id)

    if not result['success']:
        return Response(result, status=404)

    serializer = TriggeredAlertSerializer(result['trigger'])

    return Response({
        'success': True,
        'trigger': serializer.data
    })
