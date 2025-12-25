"""
System, Dashboard & Monitoring API (Phases 10 & 11 - MVP2 v3.4)
Handles dashboards, charts, performance monitoring, health checks, and feature flags.
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.response import Response

from .models import (
    UserDashboard, ChartPreset, PerformanceMetric,
    SecurityAuditLog, FeatureFlag, SystemHealthCheck
)
from .services.dashboard_service import (
    DashboardService, ChartPresetService, PerformanceMonitoringService,
    SecurityAuditService, FeatureFlagService
)
from .services.system_service import (
    SystemHealthService, DeploymentService, SetupUtilityService
)


# ============================================================================
# Dashboard Endpoints (Phase 10)
# ============================================================================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_dashboard(request):
    """Create a new dashboard."""
    result = DashboardService.create_dashboard(request.user, request.data)
    return Response({'success': True, 'dashboard_id': result['dashboard'].id})


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_dashboard(request, dashboard_id):
    """Update a dashboard."""
    result = DashboardService.update_dashboard(request.user, dashboard_id, request.data)

    if not result['success']:
        return Response(result, status=404)

    return Response({'success': True})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_my_dashboards(request):
    """Get user's dashboards."""
    result = DashboardService.get_user_dashboards(request.user)
    dashboards = [{
        'id': d.id,
        'name': d.name,
        'layout': d.layout,
        'is_default': d.is_default,
        'visibility': d.visibility
    } for d in result['dashboards']]

    return Response({'success': True, 'dashboards': dashboards})


@api_view(['GET'])
@permission_classes([AllowAny])
def get_public_dashboards(request):
    """Get public dashboard templates."""
    result = DashboardService.get_public_dashboards(limit=20)
    dashboards = [{
        'id': d.id,
        'name': d.name,
        'layout': d.layout,
        'user': d.user.email
    } for d in result['dashboards']]

    return Response({'success': True, 'dashboards': dashboards})


# ============================================================================
# Chart Preset Endpoints (Phase 10)
# ============================================================================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_chart_preset(request):
    """Create a chart preset."""
    result = ChartPresetService.create_preset(request.user, request.data)
    return Response({'success': True, 'preset_id': result['preset'].id})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_my_chart_presets(request):
    """Get user's chart presets."""
    result = ChartPresetService.get_user_presets(request.user)
    presets = [{
        'id': p.id,
        'name': p.name,
        'chart_type': p.chart_type,
        'timeframe': p.timeframe,
        'indicators': p.indicators
    } for p in result['presets']]

    return Response({'success': True, 'presets': presets})


@api_view(['GET'])
@permission_classes([AllowAny])
def get_public_chart_presets(request):
    """Get public chart preset templates."""
    result = ChartPresetService.get_public_presets(limit=50)
    presets = [{
        'id': p.id,
        'name': p.name,
        'description': p.description,
        'chart_type': p.chart_type,
        'clone_count': p.clone_count
    } for p in result['presets']]

    return Response({'success': True, 'presets': presets})


# ============================================================================
# Performance Monitoring Endpoints (Phase 10)
# ============================================================================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def record_performance_metric(request):
    """Record a performance metric (client-side timing)."""
    result = PerformanceMonitoringService.record_metric(
        metric_type=request.data.get('metric_type'),
        value=request.data.get('value'),
        endpoint=request.data.get('endpoint', ''),
        user=request.user
    )

    return Response({'success': True})


@api_view(['GET'])
@permission_classes([IsAdminUser])
def get_performance_report(request):
    """Get performance report (admin only)."""
    metric_type = request.GET.get('metric_type')
    hours = int(request.GET.get('hours', 24))

    result = PerformanceMonitoringService.get_performance_report(metric_type, hours)

    return Response({'success': True, 'report': result['report']})


# ============================================================================
# Feature Flag Endpoints (Phase 10)
# ============================================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_feature_flag(request, flag_name):
    """Check if a feature is enabled for the current user."""
    result = FeatureFlagService.is_enabled(flag_name, request.user)

    return Response({
        'success': True,
        'enabled': result['enabled'],
        'flag_name': flag_name
    })


@api_view(['GET'])
@permission_classes([IsAdminUser])
def get_all_feature_flags(request):
    """Get all feature flags (admin only)."""
    result = FeatureFlagService.get_all_flags()
    flags = [{
        'name': f.name,
        'description': f.description,
        'is_enabled': f.is_enabled,
        'rollout_strategy': f.rollout_strategy
    } for f in result['flags']]

    return Response({'success': True, 'flags': flags})


@api_view(['POST'])
@permission_classes([IsAdminUser])
def toggle_feature_flag(request, flag_name):
    """Toggle a feature flag (admin only)."""
    is_enabled = request.data.get('is_enabled', False)

    result = FeatureFlagService.toggle_flag(flag_name, is_enabled)

    if not result['success']:
        return Response(result, status=404)

    return Response({'success': True})


# ============================================================================
# System Health Endpoints (Phase 11)
# ============================================================================

@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """Public health check endpoint."""
    result = SystemHealthService.run_all_checks()

    return Response({
        'success': True,
        'status': result['overall_status'],
        'checks': result['checks']
    })


@api_view(['GET'])
@permission_classes([IsAdminUser])
def get_health_history(request):
    """Get health check history (admin only)."""
    check_type = request.GET.get('check_type')
    hours = int(request.GET.get('hours', 24))

    result = SystemHealthService.get_recent_checks(check_type, hours)
    checks = [{
        'check_type': c.check_type,
        'status': c.status,
        'response_time_ms': c.response_time_ms,
        'checked_at': c.checked_at.isoformat()
    } for c in result['checks']]

    return Response({'success': True, 'checks': checks})


@api_view(['GET'])
@permission_classes([IsAdminUser])
def get_system_info(request):
    """Get system information (admin only)."""
    result = SetupUtilityService.get_system_info()

    return Response({'success': True, 'info': result['info']})


@api_view(['GET'])
@permission_classes([IsAdminUser])
def verify_setup(request):
    """Verify environment setup (admin only)."""
    result = SetupUtilityService.verify_environment()

    return Response({
        'success': result['success'],
        'checks': result['checks']
    })
