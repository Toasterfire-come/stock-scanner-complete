"""
Comprehensive Health Checks and System Monitoring for Stock Scanner
Provides production-ready monitoring endpoints with detailed system metrics
"""

from django.http import JsonResponse
from django.db import connection, connections
from django.core.cache import cache
from django.utils import timezone
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
import psutil
import time
import logging
from datetime import timedelta
from typing import Dict, Any, List
import json

logger = logging.getLogger(__name__)

class SystemHealthChecker:
    """
    Comprehensive system health checking with detailed metrics
    """
    
    def __init__(self):
        self.checks = {}
        self.start_time = time.time()
    
    def run_all_checks(self) -> Dict[str, Any]:
        """Run all health checks and return comprehensive status"""
        health_data = {
            'status': 'healthy',
            'timestamp': timezone.now().isoformat(),
            'checks': {},
            'metrics': {},
            'summary': {}
        }
        
        # Run individual checks
        checks = [
            ('database', self.check_database),
            ('cache', self.check_cache),
            ('disk_space', self.check_disk_space),
            ('memory', self.check_memory),
            ('api_endpoints', self.check_api_endpoints),
            ('stock_data', self.check_stock_data),
            ('performance', self.check_performance)
        ]
        
        for check_name, check_func in checks:
            try:
                result = check_func()
                health_data['checks'][check_name] = result
                
                # Update overall status
                if result['status'] == 'critical':
                    health_data['status'] = 'critical'
                elif result['status'] == 'warning' and health_data['status'] == 'healthy':
                    health_data['status'] = 'warning'
                    
            except Exception as e:
                logger.error(f"Health check '{check_name}' failed: {e}")
                health_data['checks'][check_name] = {
                    'status': 'critical',
                    'message': f"Check failed: {str(e)}",
                    'timestamp': timezone.now().isoformat()
                }
                health_data['status'] = 'critical'
        
        # Generate summary
        health_data['summary'] = self.generate_summary(health_data['checks'])
        
        return health_data
    
    def check_database(self) -> Dict[str, Any]:
        """Check database connectivity and performance"""
        try:
            start_time = time.time()
            
            # Test connection
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
            
            connection_time = (time.time() - start_time) * 1000
            
            # Check for active connections
            with connection.cursor() as cursor:
                if connection.vendor == 'mysql':
                    cursor.execute("SHOW STATUS LIKE 'Threads_connected'")
                    active_connections = cursor.fetchone()[1] if cursor.rowcount > 0 else 0
                else:
                    active_connections = 'N/A'
            
            # Determine status
            if connection_time > 1000:  # >1 second
                db_status = 'critical'
                message = f"Database connection slow: {connection_time:.2f}ms"
            elif connection_time > 100:  # >100ms
                db_status = 'warning'
                message = f"Database connection acceptable: {connection_time:.2f}ms"
            else:
                db_status = 'healthy'
                message = f"Database connection healthy: {connection_time:.2f}ms"
            
            return {
                'status': db_status,
                'message': message,
                'metrics': {
                    'connection_time_ms': round(connection_time, 2),
                    'active_connections': active_connections,
                    'vendor': connection.vendor
                },
                'timestamp': timezone.now().isoformat()
            }
            
        except Exception as e:
            return {
                'status': 'critical',
                'message': f"Database check failed: {str(e)}",
                'timestamp': timezone.now().isoformat()
            }
    
    def check_cache(self) -> Dict[str, Any]:
        """Check cache system health"""
        try:
            test_key = 'health_check_cache_test'
            test_value = f'test_{int(time.time())}'
            
            start_time = time.time()
            
            # Test cache write
            cache.set(test_key, test_value, 60)
            
            # Test cache read
            retrieved_value = cache.get(test_key)
            
            cache_time = (time.time() - start_time) * 1000
            
            # Clean up
            cache.delete(test_key)
            
            if retrieved_value != test_value:
                return {
                    'status': 'critical',
                    'message': 'Cache read/write test failed',
                    'timestamp': timezone.now().isoformat()
                }
            
            # Determine status based on response time
            if cache_time > 100:  # >100ms
                cache_status = 'warning'
                message = f"Cache slow: {cache_time:.2f}ms"
            else:
                cache_status = 'healthy'
                message = f"Cache healthy: {cache_time:.2f}ms"
            
            return {
                'status': cache_status,
                'message': message,
                'metrics': {
                    'response_time_ms': round(cache_time, 2),
                    'backend': getattr(cache, '_cache', {}).get('_backend', 'unknown')
                },
                'timestamp': timezone.now().isoformat()
            }
            
        except Exception as e:
            return {
                'status': 'critical',
                'message': f"Cache check failed: {str(e)}",
                'timestamp': timezone.now().isoformat()
            }
    
    def check_disk_space(self) -> Dict[str, Any]:
        """Check available disk space"""
        try:
            disk_usage = psutil.disk_usage('/')
            
            # Calculate percentages
            used_percent = (disk_usage.used / disk_usage.total) * 100
            free_percent = 100 - used_percent
            
            # Determine status
            if free_percent < 5:  # <5% free
                disk_status = 'critical'
                message = f"Critical: Only {free_percent:.1f}% disk space remaining"
            elif free_percent < 15:  # <15% free
                disk_status = 'warning'
                message = f"Warning: {free_percent:.1f}% disk space remaining"
            else:
                disk_status = 'healthy'
                message = f"Disk space healthy: {free_percent:.1f}% free"
            
            return {
                'status': disk_status,
                'message': message,
                'metrics': {
                    'total_gb': round(disk_usage.total / (1024**3), 2),
                    'used_gb': round(disk_usage.used / (1024**3), 2),
                    'free_gb': round(disk_usage.free / (1024**3), 2),
                    'used_percent': round(used_percent, 1),
                    'free_percent': round(free_percent, 1)
                },
                'timestamp': timezone.now().isoformat()
            }
            
        except Exception as e:
            return {
                'status': 'warning',
                'message': f"Disk space check failed: {str(e)}",
                'timestamp': timezone.now().isoformat()
            }
    
    def check_memory(self) -> Dict[str, Any]:
        """Check system memory usage"""
        try:
            memory = psutil.virtual_memory()
            
            # Determine status
            if memory.percent > 90:
                memory_status = 'critical'
                message = f"Critical: {memory.percent:.1f}% memory usage"
            elif memory.percent > 80:
                memory_status = 'warning'
                message = f"Warning: {memory.percent:.1f}% memory usage"
            else:
                memory_status = 'healthy'
                message = f"Memory usage healthy: {memory.percent:.1f}%"
            
            return {
                'status': memory_status,
                'message': message,
                'metrics': {
                    'total_gb': round(memory.total / (1024**3), 2),
                    'used_gb': round(memory.used / (1024**3), 2),
                    'available_gb': round(memory.available / (1024**3), 2),
                    'percent_used': round(memory.percent, 1)
                },
                'timestamp': timezone.now().isoformat()
            }
            
        except Exception as e:
            return {
                'status': 'warning',
                'message': f"Memory check failed: {str(e)}",
                'timestamp': timezone.now().isoformat()
            }
    
    def check_api_endpoints(self) -> Dict[str, Any]:
        """Check critical API endpoints"""
        try:
            from django.test import Client
            from django.urls import reverse
            
            client = Client()
            endpoints_to_check = [
                ('/', 'Homepage'),
                ('/api/stocks/', 'Stock List API'),
                ('/health/', 'Health Check'),
            ]
            
            failed_endpoints = []
            slow_endpoints = []
            
            for endpoint, name in endpoints_to_check:
                try:
                    start_time = time.time()
                    response = client.get(endpoint)
                    response_time = (time.time() - start_time) * 1000
                    
                    if response.status_code >= 500:
                        failed_endpoints.append(f"{name} ({endpoint})")
                    elif response_time > 2000:  # >2 seconds
                        slow_endpoints.append(f"{name}: {response_time:.0f}ms")
                        
                except Exception as e:
                    failed_endpoints.append(f"{name}: {str(e)}")
            
            # Determine status
            if failed_endpoints:
                api_status = 'critical'
                message = f"Failed endpoints: {', '.join(failed_endpoints)}"
            elif slow_endpoints:
                api_status = 'warning'
                message = f"Slow endpoints: {', '.join(slow_endpoints)}"
            else:
                api_status = 'healthy'
                message = "All critical endpoints responding"
            
            return {
                'status': api_status,
                'message': message,
                'metrics': {
                    'endpoints_checked': len(endpoints_to_check),
                    'failed_count': len(failed_endpoints),
                    'slow_count': len(slow_endpoints)
                },
                'timestamp': timezone.now().isoformat()
            }
            
        except Exception as e:
            return {
                'status': 'warning',
                'message': f"API endpoint check failed: {str(e)}",
                'timestamp': timezone.now().isoformat()
            }
    
    def check_stock_data(self) -> Dict[str, Any]:
        """Check stock data freshness and availability"""
        try:
            from .models import Stock
            
            # Check total stock count
            total_stocks = Stock.objects.count()
            
            # Check recently updated stocks
            cutoff_time = timezone.now() - timedelta(hours=24)
            recent_stocks = Stock.objects.filter(last_updated__gte=cutoff_time).count()
            
            # Check stocks with current prices
            priced_stocks = Stock.objects.filter(
                current_price__isnull=False,
                current_price__gt=0
            ).count()
            
            # Calculate percentages
            recent_percent = (recent_stocks / total_stocks * 100) if total_stocks > 0 else 0
            priced_percent = (priced_stocks / total_stocks * 100) if total_stocks > 0 else 0
            
            # Determine status
            if recent_percent < 10 or priced_percent < 50:
                data_status = 'critical'
                message = f"Stale data: {recent_percent:.1f}% recent, {priced_percent:.1f}% priced"
            elif recent_percent < 50 or priced_percent < 80:
                data_status = 'warning'
                message = f"Data quality concerns: {recent_percent:.1f}% recent, {priced_percent:.1f}% priced"
            else:
                data_status = 'healthy'
                message = f"Data quality good: {recent_percent:.1f}% recent, {priced_percent:.1f}% priced"
            
            return {
                'status': data_status,
                'message': message,
                'metrics': {
                    'total_stocks': total_stocks,
                    'recent_stocks': recent_stocks,
                    'priced_stocks': priced_stocks,
                    'recent_percent': round(recent_percent, 1),
                    'priced_percent': round(priced_percent, 1)
                },
                'timestamp': timezone.now().isoformat()
            }
            
        except Exception as e:
            return {
                'status': 'warning',
                'message': f"Stock data check failed: {str(e)}",
                'timestamp': timezone.now().isoformat()
            }
    
    def check_performance(self) -> Dict[str, Any]:
        """Check system performance metrics"""
        try:
            # Get CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Get load average (Unix systems)
            try:
                load_avg = psutil.getloadavg()
                load_1min = load_avg[0]
            except (AttributeError, OSError):
                load_1min = None
            
            # Get process count
            process_count = len(psutil.pids())
            
            # Check query performance from cache
            query_stats = cache.get('system_stats', {})
            avg_query_time = query_stats.get('avg_query_time', 0)
            
            # Determine status
            performance_issues = []
            
            if cpu_percent > 90:
                performance_issues.append(f"High CPU: {cpu_percent:.1f}%")
            
            if load_1min and load_1min > psutil.cpu_count() * 2:
                performance_issues.append(f"High load: {load_1min:.2f}")
            
            if avg_query_time > 0.5:
                performance_issues.append(f"Slow queries: {avg_query_time:.3f}s avg")
            
            if performance_issues:
                perf_status = 'warning'
                message = f"Performance concerns: {', '.join(performance_issues)}"
            else:
                perf_status = 'healthy'
                message = f"Performance healthy: CPU {cpu_percent:.1f}%"
            
            return {
                'status': perf_status,
                'message': message,
                'metrics': {
                    'cpu_percent': round(cpu_percent, 1),
                    'load_1min': round(load_1min, 2) if load_1min else None,
                    'process_count': process_count,
                    'avg_query_time': round(avg_query_time, 3) if avg_query_time else 0
                },
                'timestamp': timezone.now().isoformat()
            }
            
        except Exception as e:
            return {
                'status': 'warning',
                'message': f"Performance check failed: {str(e)}",
                'timestamp': timezone.now().isoformat()
            }
    
    def generate_summary(self, checks: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary statistics from health checks"""
        total_checks = len(checks)
        healthy_count = sum(1 for check in checks.values() if check['status'] == 'healthy')
        warning_count = sum(1 for check in checks.values() if check['status'] == 'warning')
        critical_count = sum(1 for check in checks.values() if check['status'] == 'critical')
        
        return {
            'total_checks': total_checks,
            'healthy': healthy_count,
            'warning': warning_count,
            'critical': critical_count,
            'success_rate': round((healthy_count / total_checks * 100), 1) if total_checks > 0 else 0
        }

@api_view(['GET'])
@permission_classes([AllowAny])
def health_check_detailed(request):
    """
    Comprehensive health check endpoint with detailed metrics
    """
    checker = SystemHealthChecker()
    health_data = checker.run_all_checks()
    
    # Determine HTTP status code
    if health_data['status'] == 'critical':
        http_status = status.HTTP_503_SERVICE_UNAVAILABLE
    elif health_data['status'] == 'warning':
        http_status = status.HTTP_200_OK  # Still operational
    else:
        http_status = status.HTTP_200_OK
    
    return Response(health_data, status=http_status)

@api_view(['GET'])
@permission_classes([AllowAny])
def health_check_simple(request):
    """
    Simple health check for load balancers
    """
    try:
        # Quick database check
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        
        return Response({
            'status': 'healthy',
            'timestamp': timezone.now().isoformat(),
            'service': 'stock-scanner-api'
        })
        
    except Exception as e:
        return Response({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': timezone.now().isoformat(),
            'service': 'stock-scanner-api'
        }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

@api_view(['GET'])
@permission_classes([AllowAny])
def system_metrics(request):
    """
    Detailed system metrics endpoint
    """
    try:
        # Collect comprehensive metrics
        metrics = {
            'timestamp': timezone.now().isoformat(),
            'system': {
                'cpu_percent': psutil.cpu_percent(interval=1),
                'memory': {
                    'total': psutil.virtual_memory().total,
                    'used': psutil.virtual_memory().used,
                    'percent': psutil.virtual_memory().percent
                },
                'disk': {
                    'total': psutil.disk_usage('/').total,
                    'used': psutil.disk_usage('/').used,
                    'percent': (psutil.disk_usage('/').used / psutil.disk_usage('/').total) * 100
                }
            },
            'database': {
                'connections': 'N/A',  # Would need specific DB queries
                'vendor': connection.vendor
            },
            'cache': {
                'backend': str(type(cache._cache._cache)),
                'test_successful': True
            },
            'application': {
                'debug_mode': settings.DEBUG,
                'allowed_hosts': settings.ALLOWED_HOSTS,
                'version': '1.0.0'  # You can define this
            }
        }
        
        # Test cache
        try:
            cache.set('metrics_test', 'test', 10)
            cache.get('metrics_test')
            metrics['cache']['test_successful'] = True
        except:
            metrics['cache']['test_successful'] = False
        
        return Response(metrics)
        
    except Exception as e:
        return Response({
            'error': f'Failed to collect metrics: {str(e)}',
            'timestamp': timezone.now().isoformat()
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def performance_metrics(request):
    """
    Performance metrics for monitoring and optimization
    """
    try:
        from .query_optimization import QueryOptimizer
        
        # Get query performance stats
        query_stats = QueryOptimizer.analyze_query_performance()
        slow_queries = QueryOptimizer.get_slow_queries(threshold=0.1)
        
        # Get system performance data
        system_stats = cache.get('system_stats', {})
        
        metrics = {
            'timestamp': timezone.now().isoformat(),
            'queries': {
                'total_tracked': len(query_stats),
                'slow_queries': len(slow_queries),
                'performance_data': query_stats,
                'slow_query_details': slow_queries
            },
            'system': system_stats,
            'recommendations': QueryOptimizer.optimize_database_settings()
        }
        
        return Response(metrics)
        
    except Exception as e:
        return Response({
            'error': f'Failed to collect performance metrics: {str(e)}',
            'timestamp': timezone.now().isoformat()
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class HealthCheckMiddleware:
    """
    Middleware to automatically update system health metrics
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.last_update = None
    
    def __call__(self, request):
        # Update metrics every 60 seconds
        now = time.time()
        if not self.last_update or (now - self.last_update) > 60:
            self.update_system_metrics()
            self.last_update = now
        
        response = self.get_response(request)
        return response
    
    def update_system_metrics(self):
        """Update system metrics in cache"""
        try:
            metrics = {
                'cpu_percent': psutil.cpu_percent(),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_percent': (psutil.disk_usage('/').used / psutil.disk_usage('/').total) * 100,
                'timestamp': timezone.now().isoformat(),
                'active_connections': self.get_active_connections()
            }
            
            cache.set('system_stats', metrics, 300)  # Cache for 5 minutes
            
        except Exception as e:
            logger.error(f"Failed to update system metrics: {e}")
    
    def get_active_connections(self):
        """Get number of active database connections"""
        try:
            with connection.cursor() as cursor:
                if connection.vendor == 'mysql':
                    cursor.execute("SHOW STATUS LIKE 'Threads_connected'")
                    result = cursor.fetchone()
                    return int(result[1]) if result else 0
                else:
                    return 'N/A'
        except:
            return 'N/A'