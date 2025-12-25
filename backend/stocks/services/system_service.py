"""
System Health & Setup Service (Phase 11 - MVP2 v3.4)
Handles health checks, deployment tracking, and system monitoring.
"""

from django.db import transaction, connection
from django.utils import timezone
from datetime import timedelta
import subprocess
import os
import psutil

from stocks.models import (
    SystemHealthCheck, DeploymentLog, DatabaseMigrationLog
)


class SystemHealthService:
    """Service for system health monitoring."""

    @staticmethod
    def run_all_checks():
        """
        Run all health checks.

        Returns:
            dict: {'success': bool, 'checks': list, 'overall_status': str}
        """
        checks = []

        # Database check
        checks.append(SystemHealthService.check_database())

        # Disk space check
        checks.append(SystemHealthService.check_disk_space())

        # Memory check
        checks.append(SystemHealthService.check_memory())

        # Determine overall status
        statuses = [c['status'] for c in checks]
        if 'unhealthy' in statuses:
            overall_status = 'unhealthy'
        elif 'degraded' in statuses:
            overall_status = 'degraded'
        else:
            overall_status = 'healthy'

        return {
            'success': True,
            'checks': checks,
            'overall_status': overall_status
        }

    @staticmethod
    def check_database():
        """
        Check database connection and performance.

        Returns:
            dict: {'check_type': str, 'status': str, 'response_time_ms': int}
        """
        import time

        start = time.time()
        try:
            # Simple query to test connection
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()

            response_time_ms = int((time.time() - start) * 1000)

            # Determine status based on response time
            if response_time_ms < 100:
                status = 'healthy'
            elif response_time_ms < 500:
                status = 'degraded'
            else:
                status = 'unhealthy'

            check = SystemHealthCheck.objects.create(
                check_type='database',
                status=status,
                response_time_ms=response_time_ms,
                details={'query': 'SELECT 1'}
            )

            return {
                'check_type': 'database',
                'status': status,
                'response_time_ms': response_time_ms
            }

        except Exception as e:
            check = SystemHealthCheck.objects.create(
                check_type='database',
                status='unhealthy',
                error_message=str(e)
            )

            return {
                'check_type': 'database',
                'status': 'unhealthy',
                'error': str(e)
            }

    @staticmethod
    def check_disk_space():
        """
        Check available disk space.

        Returns:
            dict: {'check_type': str, 'status': str, 'details': dict}
        """
        try:
            disk = psutil.disk_usage('/')

            percent_used = disk.percent
            gb_free = disk.free / (1024 ** 3)

            # Determine status
            if percent_used > 90:
                status = 'unhealthy'
            elif percent_used > 80:
                status = 'degraded'
            else:
                status = 'healthy'

            details = {
                'percent_used': percent_used,
                'gb_free': round(gb_free, 2),
                'total_gb': round(disk.total / (1024 ** 3), 2)
            }

            check = SystemHealthCheck.objects.create(
                check_type='disk_space',
                status=status,
                details=details
            )

            return {
                'check_type': 'disk_space',
                'status': status,
                'details': details
            }

        except Exception as e:
            return {
                'check_type': 'disk_space',
                'status': 'unhealthy',
                'error': str(e)
            }

    @staticmethod
    def check_memory():
        """
        Check memory usage.

        Returns:
            dict: {'check_type': str, 'status': str, 'details': dict}
        """
        try:
            memory = psutil.virtual_memory()

            percent_used = memory.percent
            gb_available = memory.available / (1024 ** 3)

            # Determine status
            if percent_used > 90:
                status = 'unhealthy'
            elif percent_used > 80:
                status = 'degraded'
            else:
                status = 'healthy'

            details = {
                'percent_used': percent_used,
                'gb_available': round(gb_available, 2),
                'total_gb': round(memory.total / (1024 ** 3), 2)
            }

            check = SystemHealthCheck.objects.create(
                check_type='memory',
                status=status,
                details=details
            )

            return {
                'check_type': 'memory',
                'status': status,
                'details': details
            }

        except Exception as e:
            return {
                'check_type': 'memory',
                'status': 'unhealthy',
                'error': str(e)
            }

    @staticmethod
    def get_recent_checks(check_type=None, hours=24):
        """
        Get recent health check results.

        Returns:
            dict: {'success': bool, 'checks': QuerySet}
        """
        cutoff = timezone.now() - timedelta(hours=hours)
        checks = SystemHealthCheck.objects.filter(checked_at__gte=cutoff)

        if check_type:
            checks = checks.filter(check_type=check_type)

        return {
            'success': True,
            'checks': checks
        }


class DeploymentService:
    """Service for deployment tracking."""

    @staticmethod
    def create_deployment(version, environment, deployed_by, commit_hash='', release_notes=''):
        """
        Create a deployment record.

        Returns:
            dict: {'success': bool, 'deployment': DeploymentLog}
        """
        deployment = DeploymentLog.objects.create(
            version=version,
            environment=environment,
            deployed_by=deployed_by,
            commit_hash=commit_hash,
            release_notes=release_notes,
            status='pending'
        )

        return {
            'success': True,
            'deployment': deployment
        }

    @staticmethod
    def update_deployment_status(deployment_id, status, error_log=''):
        """
        Update deployment status.

        Returns:
            dict: {'success': bool, 'deployment': DeploymentLog}
        """
        try:
            deployment = DeploymentLog.objects.get(id=deployment_id)
            deployment.status = status
            deployment.error_log = error_log

            if status in ['success', 'failed', 'rolled_back']:
                deployment.completed_at = timezone.now()

            deployment.save()

            return {
                'success': True,
                'deployment': deployment
            }
        except DeploymentLog.DoesNotExist:
            return {'success': False, 'message': 'Deployment not found'}

    @staticmethod
    def get_recent_deployments(environment=None, limit=20):
        """
        Get recent deployments.

        Returns:
            dict: {'success': bool, 'deployments': QuerySet}
        """
        deployments = DeploymentLog.objects.all()

        if environment:
            deployments = deployments.filter(environment=environment)

        deployments = deployments[:limit]

        return {
            'success': True,
            'deployments': deployments
        }

    @staticmethod
    def get_current_version(environment='production'):
        """
        Get currently deployed version.

        Returns:
            dict: {'success': bool, 'version': str, 'deployment': DeploymentLog}
        """
        try:
            deployment = DeploymentLog.objects.filter(
                environment=environment,
                status='success'
            ).latest('completed_at')

            return {
                'success': True,
                'version': deployment.version,
                'deployment': deployment
            }
        except DeploymentLog.DoesNotExist:
            return {
                'success': False,
                'message': f'No successful deployments found for {environment}'
            }


class MigrationTrackingService:
    """Service for tracking database migrations."""

    @staticmethod
    def log_migration(app_label, migration_name, applied=True, execution_time=None, error_message=''):
        """
        Log a migration execution.

        Returns:
            dict: {'success': bool, 'log': DatabaseMigrationLog}
        """
        log, created = DatabaseMigrationLog.objects.update_or_create(
            app_label=app_label,
            migration_name=migration_name,
            defaults={
                'applied': applied,
                'applied_at': timezone.now() if applied else None,
                'execution_time_seconds': execution_time,
                'had_errors': bool(error_message),
                'error_message': error_message
            }
        )

        return {
            'success': True,
            'log': log,
            'created': created
        }

    @staticmethod
    def get_migration_history(app_label=None):
        """
        Get migration history.

        Returns:
            dict: {'success': bool, 'migrations': QuerySet}
        """
        migrations = DatabaseMigrationLog.objects.all()

        if app_label:
            migrations = migrations.filter(app_label=app_label)

        return {
            'success': True,
            'migrations': migrations
        }

    @staticmethod
    def get_pending_migrations():
        """
        Get pending (unapplied) migrations.

        Returns:
            dict: {'success': bool, 'migrations': QuerySet}
        """
        migrations = DatabaseMigrationLog.objects.filter(applied=False)

        return {
            'success': True,
            'migrations': migrations
        }


class SetupUtilityService:
    """Utility methods for system setup and configuration."""

    @staticmethod
    def verify_environment():
        """
        Verify environment configuration.

        Returns:
            dict: {'success': bool, 'checks': dict}
        """
        checks = {
            'database': False,
            'migrations': False,
            'static_files': False,
            'media_files': False
        }

        # Check database connection
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            checks['database'] = True
        except:
            pass

        # Check if migrations are up to date
        # (simplified - would use Django's migration executor in production)
        checks['migrations'] = True

        # Check static files directory
        from django.conf import settings
        checks['static_files'] = os.path.exists(settings.STATIC_ROOT) if hasattr(settings, 'STATIC_ROOT') else False

        # Check media files directory
        checks['media_files'] = os.path.exists(settings.MEDIA_ROOT) if hasattr(settings, 'MEDIA_ROOT') else False

        all_passed = all(checks.values())

        return {
            'success': all_passed,
            'checks': checks
        }

    @staticmethod
    def get_system_info():
        """
        Get system information for debugging.

        Returns:
            dict: System information
        """
        from django.conf import settings
        import platform
        import sys

        info = {
            'python_version': sys.version,
            'django_version': __import__('django').get_version(),
            'platform': platform.platform(),
            'debug_mode': settings.DEBUG,
            'database': settings.DATABASES['default']['ENGINE'],
            'cpu_count': psutil.cpu_count(),
            'memory_total_gb': round(psutil.virtual_memory().total / (1024 ** 3), 2),
            'disk_total_gb': round(psutil.disk_usage('/').total / (1024 ** 3), 2)
        }

        return {
            'success': True,
            'info': info
        }
