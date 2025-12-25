"""
Dashboard & UX Service (Phase 10 - MVP2 v3.4)
Handles dashboards, chart presets, performance monitoring, and feature flags.
"""

from django.db import transaction
from django.db.models import Avg, Count
from django.utils import timezone
from datetime import timedelta

from stocks.models import (
    UserDashboard, ChartPreset, PerformanceMetric,
    SecurityAuditLog, NavigationAnalytics, FeatureFlag
)


class DashboardService:
    """Service for managing user dashboards."""

    @staticmethod
    def create_dashboard(user, dashboard_data):
        """
        Create a new dashboard for a user.

        Args:
            user: User object
            dashboard_data: dict with name, layout, visibility

        Returns:
            dict: {'success': bool, 'dashboard': UserDashboard}
        """
        # If setting as default, unset other defaults
        is_default = dashboard_data.get('is_default', False)
        if is_default:
            UserDashboard.objects.filter(user=user, is_default=True).update(is_default=False)

        dashboard = UserDashboard.objects.create(
            user=user,
            name=dashboard_data.get('name', 'My Dashboard'),
            layout=dashboard_data.get('layout', {}),
            visibility=dashboard_data.get('visibility', 'private'),
            is_default=is_default
        )

        return {
            'success': True,
            'dashboard': dashboard
        }

    @staticmethod
    def update_dashboard(user, dashboard_id, dashboard_data):
        """
        Update an existing dashboard.

        Returns:
            dict: {'success': bool, 'dashboard': UserDashboard}
        """
        try:
            dashboard = UserDashboard.objects.get(id=dashboard_id, user=user)
        except UserDashboard.DoesNotExist:
            return {'success': False, 'message': 'Dashboard not found'}

        # Handle default flag
        if dashboard_data.get('is_default') and not dashboard.is_default:
            UserDashboard.objects.filter(user=user, is_default=True).update(is_default=False)

        # Update fields
        if 'name' in dashboard_data:
            dashboard.name = dashboard_data['name']
        if 'layout' in dashboard_data:
            dashboard.layout = dashboard_data['layout']
        if 'visibility' in dashboard_data:
            dashboard.visibility = dashboard_data['visibility']
        if 'is_default' in dashboard_data:
            dashboard.is_default = dashboard_data['is_default']

        dashboard.save()

        return {
            'success': True,
            'dashboard': dashboard
        }

    @staticmethod
    def get_user_dashboards(user):
        """
        Get all dashboards for a user.

        Returns:
            dict: {'success': bool, 'dashboards': QuerySet}
        """
        dashboards = UserDashboard.objects.filter(user=user)

        return {
            'success': True,
            'dashboards': dashboards
        }

    @staticmethod
    def get_public_dashboards(limit=20):
        """
        Get public dashboard templates.

        Returns:
            dict: {'success': bool, 'dashboards': QuerySet}
        """
        dashboards = UserDashboard.objects.filter(visibility='public').order_by('-updated_at')[:limit]

        return {
            'success': True,
            'dashboards': dashboards
        }


class ChartPresetService:
    """Service for managing chart presets."""

    @staticmethod
    def create_preset(user, preset_data):
        """
        Create a chart preset.

        Returns:
            dict: {'success': bool, 'preset': ChartPreset}
        """
        preset = ChartPreset.objects.create(
            user=user,
            name=preset_data.get('name'),
            description=preset_data.get('description', ''),
            chart_type=preset_data.get('chart_type', 'candlestick'),
            timeframe=preset_data.get('timeframe', '1d'),
            indicators=preset_data.get('indicators', []),
            drawing_tools=preset_data.get('drawing_tools', []),
            color_scheme=preset_data.get('color_scheme', {}),
            is_public=preset_data.get('is_public', False)
        )

        return {
            'success': True,
            'preset': preset
        }

    @staticmethod
    def get_user_presets(user):
        """
        Get user's chart presets.

        Returns:
            dict: {'success': bool, 'presets': QuerySet}
        """
        presets = ChartPreset.objects.filter(user=user)

        return {
            'success': True,
            'presets': presets
        }

    @staticmethod
    def get_public_presets(limit=50):
        """
        Get public chart preset templates.

        Returns:
            dict: {'success': bool, 'presets': QuerySet}
        """
        presets = ChartPreset.objects.filter(is_public=True).order_by('-clone_count')[:limit]

        return {
            'success': True,
            'presets': presets
        }


class PerformanceMonitoringService:
    """Service for performance monitoring and optimization."""

    @staticmethod
    def record_metric(metric_type, value, endpoint='', user=None, request_data=None):
        """
        Record a performance metric.

        Returns:
            dict: {'success': bool, 'metric': PerformanceMetric}
        """
        metric = PerformanceMetric.objects.create(
            metric_type=metric_type,
            endpoint=endpoint,
            value=value,
            user=user,
            request_data=request_data or {}
        )

        return {
            'success': True,
            'metric': metric
        }

    @staticmethod
    def get_performance_report(metric_type=None, hours=24):
        """
        Get performance report for analysis.

        Returns:
            dict: {'success': bool, 'report': dict}
        """
        cutoff = timezone.now() - timedelta(hours=hours)
        metrics = PerformanceMetric.objects.filter(recorded_at__gte=cutoff)

        if metric_type:
            metrics = metrics.filter(metric_type=metric_type)

        # Calculate aggregates
        report = {
            'period_hours': hours,
            'total_requests': metrics.count(),
            'avg_response_time': metrics.aggregate(Avg('value'))['value__avg'],
            'by_endpoint': {}
        }

        # Group by endpoint
        for endpoint in metrics.values_list('endpoint', flat=True).distinct():
            endpoint_metrics = metrics.filter(endpoint=endpoint)
            report['by_endpoint'][endpoint] = {
                'count': endpoint_metrics.count(),
                'avg': endpoint_metrics.aggregate(Avg('value'))['value__avg']
            }

        return {
            'success': True,
            'report': report
        }


class SecurityAuditService:
    """Service for security auditing."""

    @staticmethod
    def log_event(user, event_type, severity='info', ip_address=None, user_agent='', endpoint='', details=None):
        """
        Log a security event.

        Returns:
            dict: {'success': bool, 'log': SecurityAuditLog}
        """
        log = SecurityAuditLog.objects.create(
            user=user,
            event_type=event_type,
            severity=severity,
            ip_address=ip_address,
            user_agent=user_agent,
            endpoint=endpoint,
            details=details or {}
        )

        return {
            'success': True,
            'log': log
        }

    @staticmethod
    def get_recent_events(user=None, event_type=None, severity=None, limit=100):
        """
        Get recent security events.

        Returns:
            dict: {'success': bool, 'events': QuerySet}
        """
        events = SecurityAuditLog.objects.all()

        if user:
            events = events.filter(user=user)
        if event_type:
            events = events.filter(event_type=event_type)
        if severity:
            events = events.filter(severity=severity)

        events = events[:limit]

        return {
            'success': True,
            'events': events
        }


class NavigationAnalyticsService:
    """Service for tracking navigation patterns."""

    @staticmethod
    def record_navigation(user, session_id, from_page, to_page, time_on_page, action=''):
        """
        Record a navigation event.

        Returns:
            dict: {'success': bool, 'record': NavigationAnalytics}
        """
        record = NavigationAnalytics.objects.create(
            user=user,
            session_id=session_id,
            from_page=from_page,
            to_page=to_page,
            time_on_page=time_on_page,
            action=action
        )

        return {
            'success': True,
            'record': record
        }

    @staticmethod
    def get_user_journey(session_id):
        """
        Get full user journey for a session.

        Returns:
            dict: {'success': bool, 'journey': list}
        """
        journey = NavigationAnalytics.objects.filter(session_id=session_id).order_by('timestamp')

        return {
            'success': True,
            'journey': list(journey)
        }

    @staticmethod
    def get_popular_paths(limit=10):
        """
        Get most common navigation paths.

        Returns:
            dict: {'success': bool, 'paths': list}
        """
        # Get most common from_page -> to_page combinations
        paths = NavigationAnalytics.objects.values('from_page', 'to_page').annotate(
            count=Count('id')
        ).order_by('-count')[:limit]

        return {
            'success': True,
            'paths': list(paths)
        }


class FeatureFlagService:
    """Service for managing feature flags."""

    @staticmethod
    def create_flag(name, description, created_by, rollout_strategy='all', **config):
        """
        Create a feature flag.

        Returns:
            dict: {'success': bool, 'flag': FeatureFlag}
        """
        flag = FeatureFlag.objects.create(
            name=name,
            description=description,
            created_by=created_by,
            rollout_strategy=rollout_strategy,
            rollout_percentage=config.get('rollout_percentage', 0),
            whitelisted_users=config.get('whitelisted_users', []),
            tier_requirement=config.get('tier_requirement', '')
        )

        return {
            'success': True,
            'flag': flag
        }

    @staticmethod
    def is_enabled(flag_name, user):
        """
        Check if a feature is enabled for a user.

        Returns:
            dict: {'success': bool, 'enabled': bool}
        """
        try:
            flag = FeatureFlag.objects.get(name=flag_name)
            enabled = flag.is_enabled_for_user(user)

            return {
                'success': True,
                'enabled': enabled,
                'flag': flag
            }
        except FeatureFlag.DoesNotExist:
            # Feature doesn't exist, default to disabled
            return {
                'success': False,
                'enabled': False,
                'message': 'Feature flag not found'
            }

    @staticmethod
    def toggle_flag(flag_name, is_enabled):
        """
        Enable or disable a feature flag.

        Returns:
            dict: {'success': bool, 'flag': FeatureFlag}
        """
        try:
            flag = FeatureFlag.objects.get(name=flag_name)
            flag.is_enabled = is_enabled
            flag.save()

            return {
                'success': True,
                'flag': flag
            }
        except FeatureFlag.DoesNotExist:
            return {'success': False, 'message': 'Feature flag not found'}

    @staticmethod
    def get_all_flags():
        """
        Get all feature flags.

        Returns:
            dict: {'success': bool, 'flags': QuerySet}
        """
        flags = FeatureFlag.objects.all()

        return {
            'success': True,
            'flags': flags
        }
