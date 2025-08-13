"""
Django management command for comprehensive system health checks
Usage: python manage.py system_health [--detailed] [--json]
"""

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
import logging
import json
import sys

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Perform comprehensive system health checks for Stock Scanner'

    def add_arguments(self, parser):
        parser.add_argument(
            '--detailed',
            action='store_true',
            help='Show detailed health information including metrics'
        )
        parser.add_argument(
            '--json',
            action='store_true',
            help='Output results in JSON format'
        )
        parser.add_argument(
            '--critical-only',
            action='store_true',
            help='Only show critical issues'
        )

    def handle(self, *args, **options):
        """Execute system health check"""
        
        if not options['json']:
            self.stdout.write("🏥 Starting Stock Scanner System Health Check...")
            self.stdout.write(f"⏰ Started at: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        try:
            # Import here to avoid import issues if modules aren't ready
            from stocks.monitoring import SystemHealthChecker
            
            checker = SystemHealthChecker()
            
            if options['detailed']:
                health_data = checker.run_all_checks()
            else:
                health_data = self._run_basic_checks(checker)
            
            if options['json']:
                self._output_json(health_data)
            else:
                self._output_formatted(health_data, options)
                
        except ImportError as e:
            raise CommandError(f"Failed to import health check modules: {e}")
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            raise CommandError(f"Health check failed: {e}")

    def _run_basic_checks(self, checker):
        """Run basic health checks"""
        
        basic_checks = {
            'status': 'healthy',
            'timestamp': timezone.now().isoformat(),
            'checks': {}
        }
        
        # Run critical checks only
        critical_check_methods = [
            ('database', checker.check_database),
            ('cache', checker.check_cache),
            ('memory', checker.check_memory),
        ]
        
        for check_name, check_method in critical_check_methods:
            try:
                result = check_method()
                basic_checks['checks'][check_name] = result
                
                if result['status'] == 'critical':
                    basic_checks['status'] = 'critical'
                elif result['status'] == 'warning' and basic_checks['status'] == 'healthy':
                    basic_checks['status'] = 'warning'
                    
            except Exception as e:
                logger.error(f"Health check '{check_name}' failed: {e}")
                basic_checks['checks'][check_name] = {
                    'status': 'critical',
                    'message': f"Check failed: {str(e)}",
                    'timestamp': timezone.now().isoformat()
                }
                basic_checks['status'] = 'critical'
        
        return basic_checks

    def _output_json(self, health_data):
        """Output health data in JSON format"""
        self.stdout.write(json.dumps(health_data, indent=2, default=str))

    def _output_formatted(self, health_data, options):
        """Output health data in formatted text"""
        
        overall_status = health_data.get('status', 'unknown')
        
        # Overall status
        status_emoji = {
            'healthy': '✅',
            'warning': '⚠️',
            'critical': '❌',
            'unknown': '❓'
        }
        
        self.stdout.write(f"\n{status_emoji.get(overall_status, '❓')} Overall System Status: {overall_status.upper()}")
        
        # Individual checks
        checks = health_data.get('checks', {})
        
        if not options['critical_only']:
            self.stdout.write("\n📋 Health Check Results:")
        
        for check_name, check_result in checks.items():
            check_status = check_result.get('status', 'unknown')
            check_message = check_result.get('message', 'No message')
            
            # Skip non-critical if critical-only mode
            if options['critical_only'] and check_status not in ['critical', 'warning']:
                continue
            
            emoji = status_emoji.get(check_status, '❓')
            check_display_name = check_name.replace('_', ' ').title()
            
            self.stdout.write(f"  {emoji} {check_display_name}: {check_message}")
            
            # Show metrics if available and detailed mode
            if options.get('detailed') and 'metrics' in check_result:
                metrics = check_result['metrics']
                if isinstance(metrics, dict):
                    for metric_name, metric_value in metrics.items():
                        if isinstance(metric_value, (int, float)):
                            self.stdout.write(f"    📊 {metric_name}: {metric_value}")
        
        # Summary information
        if 'summary' in health_data:
            summary = health_data['summary']
            self.stdout.write(f"\n📊 Summary:")
            self.stdout.write(f"  • Total checks: {summary.get('total_checks', 0)}")
            self.stdout.write(f"  • Healthy: {summary.get('healthy_count', 0)}")
            self.stdout.write(f"  • Warnings: {summary.get('warning_count', 0)}")
            self.stdout.write(f"  • Critical: {summary.get('critical_count', 0)}")
        
        # Recommendations
        if not options['critical_only']:
            self._show_recommendations(health_data, overall_status)
        
        # Exit code based on status
        if overall_status == 'critical':
            self.stdout.write(f"\n❌ System has critical issues!")
            sys.exit(1)
        elif overall_status == 'warning':
            self.stdout.write(f"\n⚠️  System has warnings but is operational")
        else:
            self.stdout.write(f"\n✅ System is healthy!")

    def _show_recommendations(self, health_data, overall_status):
        """Show recommendations based on health check results"""
        
        recommendations = []
        
        # Generate recommendations based on checks
        checks = health_data.get('checks', {})
        
        for check_name, check_result in checks.items():
            if check_result.get('status') == 'critical':
                if check_name == 'database':
                    recommendations.append("🔧 Check database connection and configuration")
                elif check_name == 'cache':
                    recommendations.append("🔧 Verify cache service is running (Redis/Memcached)")
                elif check_name == 'memory':
                    recommendations.append("🔧 Consider increasing available memory or optimizing usage")
                elif check_name == 'disk_space':
                    recommendations.append("🔧 Free up disk space or expand storage")
            
            elif check_result.get('status') == 'warning':
                if check_name == 'memory':
                    recommendations.append("💡 Monitor memory usage and consider optimization")
                elif check_name == 'performance':
                    recommendations.append("💡 Review slow queries and optimize database indexes")
        
        # Generic recommendations based on overall status
        if overall_status == 'critical':
            recommendations.extend([
                "🚨 Investigate critical issues immediately",
                "📞 Consider alerting system administrators",
                "🔄 Run health check again after fixes"
            ])
        elif overall_status == 'warning':
            recommendations.extend([
                "👀 Monitor system closely",
                "📈 Consider performance optimizations",
                "🔄 Schedule regular health checks"
            ])
        else:
            recommendations.extend([
                "✅ System is healthy - maintain current monitoring",
                "📅 Schedule regular optimization maintenance",
                "📊 Consider setting up automated health monitoring"
            ])
        
        if recommendations:
            self.stdout.write(f"\n💡 Recommendations:")
            for rec in recommendations:
                self.stdout.write(f"  {rec}")

    def _format_metric_value(self, value):
        """Format metric values for display"""
        if isinstance(value, float):
            if value < 1:
                return f"{value:.3f}"
            elif value < 100:
                return f"{value:.1f}"
            else:
                return f"{value:,.0f}"
        elif isinstance(value, int):
            return f"{value:,}"
        else:
            return str(value)