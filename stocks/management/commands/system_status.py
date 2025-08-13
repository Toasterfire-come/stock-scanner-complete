"""
Django management command for comprehensive system status reporting
Usage: python manage.py system_status [--format=table] [--save-report]
"""

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from django.db import connection
import logging
import json
import os
import platform
import sys

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Generate comprehensive system status report for Stock Scanner'

    def add_arguments(self, parser):
        parser.add_argument(
            '--format',
            choices=['table', 'json', 'markdown'],
            default='table',
            help='Output format (default: table)'
        )
        parser.add_argument(
            '--save-report',
            action='store_true',
            help='Save report to file with timestamp'
        )
        parser.add_argument(
            '--include-metrics',
            action='store_true',
            help='Include detailed performance metrics'
        )

    def handle(self, *args, **options):
        """Generate comprehensive system status report"""
        
        self.stdout.write("📊 Generating Stock Scanner System Status Report...")
        self.stdout.write(f"⏰ Report generated at: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        try:
            # Collect all system information
            status_data = self._collect_system_status(options)
            
            # Format and display report
            if options['format'] == 'json':
                output = self._format_json(status_data)
            elif options['format'] == 'markdown':
                output = self._format_markdown(status_data)
            else:
                output = self._format_table(status_data)
            
            self.stdout.write(output)
            
            # Save report if requested
            if options['save_report']:
                self._save_report(output, options['format'])
                
        except Exception as e:
            logger.error(f"System status report failed: {e}")
            raise CommandError(f"Report generation failed: {e}")

    def _collect_system_status(self, options):
        """Collect comprehensive system status information"""
        
        status_data = {
            'timestamp': timezone.now().isoformat(),
            'system_info': self._get_system_info(),
            'django_info': self._get_django_info(),
            'database_info': self._get_database_info(),
            'optimization_status': self._get_optimization_status(),
            'performance_metrics': self._get_performance_metrics() if options['include_metrics'] else None
        }
        
        return status_data

    def _get_system_info(self):
        """Get system and environment information"""
        
        return {
            'platform': platform.platform(),
            'python_version': sys.version,
            'architecture': platform.architecture()[0],
            'processor': platform.processor() or 'Unknown',
            'hostname': platform.node(),
            'user': os.environ.get('USER', os.environ.get('USERNAME', 'Unknown')),
            'working_directory': os.getcwd(),
            'environment_variables': {
                'DEBUG': os.environ.get('DEBUG', 'Not set'),
                'DJANGO_SETTINGS_MODULE': os.environ.get('DJANGO_SETTINGS_MODULE', 'Not set'),
                'DATABASE_URL': 'Set' if os.environ.get('DATABASE_URL') else 'Not set',
                'REDIS_URL': 'Set' if os.environ.get('REDIS_URL') else 'Not set',
            }
        }

    def _get_django_info(self):
        """Get Django application information"""
        
        from django.conf import settings
        from django import get_version
        
        django_info = {
            'version': get_version(),
            'debug_mode': settings.DEBUG,
            'secret_key_set': bool(getattr(settings, 'SECRET_KEY', None)),
            'installed_apps_count': len(settings.INSTALLED_APPS),
            'middleware_count': len(settings.MIDDLEWARE),
            'allowed_hosts': settings.ALLOWED_HOSTS if not settings.DEBUG else ['*'],
            'time_zone': settings.TIME_ZONE,
            'language_code': settings.LANGUAGE_CODE,
        }
        
        # Check optimization systems
        optimization_apps = [app for app in settings.INSTALLED_APPS if 'stock' in app.lower()]
        django_info['stock_apps'] = optimization_apps
        
        return django_info

    def _get_database_info(self):
        """Get database connection and configuration information"""
        
        try:
            db_info = {
                'engine': connection.vendor,
                'connection_status': 'Connected' if connection.is_usable() else 'Disconnected',
                'database_name': connection.settings_dict.get('NAME', 'Unknown'),
                'host': connection.settings_dict.get('HOST', 'localhost'),
                'port': connection.settings_dict.get('PORT', 'default'),
                'autocommit': connection.get_autocommit(),
            }
            
            # Get table information
            with connection.cursor() as cursor:
                if connection.vendor == 'mysql':
                    cursor.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = DATABASE()")
                    table_count = cursor.fetchone()[0]
                elif connection.vendor == 'postgresql':
                    cursor.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public'")
                    table_count = cursor.fetchone()[0]
                else:
                    table_count = 'Unknown'
                
                db_info['table_count'] = table_count
            
            return db_info
            
        except Exception as e:
            return {
                'status': 'Error',
                'error': str(e),
                'connection_status': 'Failed'
            }

    def _get_optimization_status(self):
        """Get optimization systems status"""
        
        optimization_status = {
            'systems_available': {},
            'integration_status': {},
            'configuration': {}
        }
        
        # Check if optimization modules are available
        optimization_modules = [
            'database_resilience',
            'memory_optimization', 
            'enhanced_error_handling',
            'compression_optimization',
            'graceful_shutdown',
            'monitoring',
            'database_indexes'
        ]
        
        for module_name in optimization_modules:
            try:
                module = __import__(f'stocks.{module_name}', fromlist=[module_name])
                optimization_status['systems_available'][module_name] = 'Available'
            except ImportError:
                optimization_status['systems_available'][module_name] = 'Not Available'
        
        # Check Django settings integration
        from django.conf import settings
        
        optimization_status['integration_status'] = {
            'rest_framework_configured': hasattr(settings, 'REST_FRAMEWORK'),
            'caches_configured': hasattr(settings, 'CACHES') and len(settings.CACHES) > 1,
            'logging_configured': hasattr(settings, 'LOGGING'),
            'optimization_settings': hasattr(settings, 'OPTIMIZATION_SETTINGS'),
            'performance_monitoring': hasattr(settings, 'PERFORMANCE_MONITORING'),
        }
        
        return optimization_status

    def _get_performance_metrics(self):
        """Get current performance metrics"""
        
        try:
            # Import monitoring systems
            from stocks.monitoring import SystemHealthChecker
            from stocks.memory_optimization import memory_manager
            
            checker = SystemHealthChecker()
            health_data = checker.run_all_checks()
            
            metrics = {
                'health_status': health_data.get('status', 'unknown'),
                'memory_usage': memory_manager.get_memory_usage(),
                'health_checks': {
                    name: check.get('status', 'unknown') 
                    for name, check in health_data.get('checks', {}).items()
                }
            }
            
            # Database metrics
            try:
                from stocks.database_indexes import get_database_optimization_status
                metrics['database_optimization'] = get_database_optimization_status()
            except:
                metrics['database_optimization'] = 'Not available'
            
            return metrics
            
        except Exception as e:
            return {'error': str(e)}

    def _format_table(self, status_data):
        """Format status data as a table"""
        
        output = []
        output.append("\n" + "="*80)
        output.append("📊 STOCK SCANNER SYSTEM STATUS REPORT")
        output.append("="*80)
        
        # System Information
        output.append("\n🖥️  SYSTEM INFORMATION")
        output.append("-" * 40)
        sys_info = status_data['system_info']
        output.append(f"Platform: {sys_info['platform']}")
        output.append(f"Python: {sys_info['python_version'].split()[0]}")
        output.append(f"Architecture: {sys_info['architecture']}")
        output.append(f"Hostname: {sys_info['hostname']}")
        output.append(f"Working Dir: {sys_info['working_directory']}")
        
        # Django Information
        output.append("\n🐍 DJANGO INFORMATION")
        output.append("-" * 40)
        django_info = status_data['django_info']
        output.append(f"Django Version: {django_info['version']}")
        output.append(f"Debug Mode: {django_info['debug_mode']}")
        output.append(f"Apps Installed: {django_info['installed_apps_count']}")
        output.append(f"Middleware: {django_info['middleware_count']}")
        output.append(f"Time Zone: {django_info['time_zone']}")
        
        # Database Information
        output.append("\n🗄️  DATABASE INFORMATION")
        output.append("-" * 40)
        db_info = status_data['database_info']
        if 'error' in db_info:
            output.append(f"❌ Status: {db_info['error']}")
        else:
            output.append(f"Engine: {db_info['engine']}")
            output.append(f"Status: {db_info['connection_status']}")
            output.append(f"Database: {db_info['database_name']}")
            output.append(f"Tables: {db_info['table_count']}")
        
        # Optimization Status
        output.append("\n⚡ OPTIMIZATION SYSTEMS")
        output.append("-" * 40)
        opt_status = status_data['optimization_status']
        
        for system, status in opt_status['systems_available'].items():
            status_icon = "✅" if status == "Available" else "❌"
            output.append(f"{status_icon} {system.replace('_', ' ').title()}: {status}")
        
        # Integration Status
        output.append("\n🔧 INTEGRATION STATUS")
        output.append("-" * 40)
        for feature, status in opt_status['integration_status'].items():
            status_icon = "✅" if status else "❌"
            output.append(f"{status_icon} {feature.replace('_', ' ').title()}: {'Configured' if status else 'Not Configured'}")
        
        # Performance Metrics (if available)
        if status_data['performance_metrics']:
            output.append("\n📈 PERFORMANCE METRICS")
            output.append("-" * 40)
            metrics = status_data['performance_metrics']
            
            if 'health_status' in metrics:
                status_icon = {"healthy": "✅", "warning": "⚠️", "critical": "❌"}.get(metrics['health_status'], "❓")
                output.append(f"{status_icon} Overall Health: {metrics['health_status']}")
            
            if 'memory_usage' in metrics and isinstance(metrics['memory_usage'], dict):
                mem = metrics['memory_usage']
                output.append(f"💾 Memory Usage: {mem.get('rss_mb', 0):.1f} MB ({mem.get('percent', 0):.1f}%)")
        
        output.append("\n" + "="*80)
        output.append(f"⏰ Report generated: {status_data['timestamp']}")
        output.append("="*80)
        
        return "\n".join(output)

    def _format_json(self, status_data):
        """Format status data as JSON"""
        return json.dumps(status_data, indent=2, default=str)

    def _format_markdown(self, status_data):
        """Format status data as Markdown"""
        
        output = []
        output.append("# 📊 Stock Scanner System Status Report")
        output.append(f"\n**Generated:** {status_data['timestamp']}")
        
        # System Information
        output.append("\n## 🖥️ System Information")
        sys_info = status_data['system_info']
        output.append(f"- **Platform:** {sys_info['platform']}")
        output.append(f"- **Python:** {sys_info['python_version'].split()[0]}")
        output.append(f"- **Architecture:** {sys_info['architecture']}")
        output.append(f"- **Hostname:** {sys_info['hostname']}")
        
        # Django Information
        output.append("\n## 🐍 Django Information")
        django_info = status_data['django_info']
        output.append(f"- **Version:** {django_info['version']}")
        output.append(f"- **Debug Mode:** {django_info['debug_mode']}")
        output.append(f"- **Apps:** {django_info['installed_apps_count']} installed")
        
        # Database Information
        output.append("\n## 🗄️ Database Information")
        db_info = status_data['database_info']
        if 'error' not in db_info:
            output.append(f"- **Engine:** {db_info['engine']}")
            output.append(f"- **Status:** {db_info['connection_status']}")
            output.append(f"- **Tables:** {db_info['table_count']}")
        
        # Optimization Systems
        output.append("\n## ⚡ Optimization Systems")
        opt_status = status_data['optimization_status']
        
        for system, status in opt_status['systems_available'].items():
            icon = "✅" if status == "Available" else "❌"
            output.append(f"- {icon} **{system.replace('_', ' ').title()}:** {status}")
        
        return "\n".join(output)

    def _save_report(self, output, format_type):
        """Save report to file"""
        
        timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
        filename = f"system_status_report_{timestamp}.{format_type}"
        
        try:
            with open(filename, 'w') as f:
                f.write(output)
            
            self.stdout.write(f"💾 Report saved to: {filename}")
            
        except Exception as e:
            self.stdout.write(f"❌ Failed to save report: {e}")