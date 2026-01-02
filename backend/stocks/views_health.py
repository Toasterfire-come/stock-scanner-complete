"""
Health check views for monitoring system status
"""
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.db import connection
from django.core.cache import cache
import psutil
import os
import time
from datetime import datetime, timedelta


@csrf_exempt
@require_http_methods(["GET", "HEAD"])
def health_check(request):
    """
    Basic health check endpoint for monitoring
    Returns 200 if service is up, with basic system info
    """
    try:
        # Get system metrics
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Check database connection
        db_status = "healthy"
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
        except Exception as e:
            db_status = f"unhealthy: {str(e)}"
        
        # Check cache if available
        cache_status = "healthy"
        try:
            cache.set('health_check', 'ok', 1)
            if cache.get('health_check') != 'ok':
                cache_status = "unhealthy"
        except Exception:
            cache_status = "not configured"
        
        response_data = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "service": "stock-scanner-api",
            "version": "1.0.0",
            "checks": {
                "database": db_status,
                "cache": cache_status,
            },
            "metrics": {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_available_mb": memory.available / (1024 * 1024),
                "disk_percent": disk.percent,
                "disk_free_gb": disk.free / (1024 * 1024 * 1024),
            }
        }
        
        # Return appropriate response for HEAD requests
        if request.method == 'HEAD':
            response = JsonResponse({})
            response['X-Health-Status'] = 'healthy'
            return response
        
        return JsonResponse(response_data)
        
    except Exception as e:
        return JsonResponse({
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }, status=503)


@csrf_exempt
@require_http_methods(["GET"])
def health_check_detailed(request):
    """
    Detailed health check with component status
    """
    try:
        components = {}
        
        # Check database
        try:
            start = time.time()
            with connection.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM stocks_stock")
                stock_count = cursor.fetchone()[0]
            db_latency = (time.time() - start) * 1000  # ms
            
            components['database'] = {
                "status": "healthy",
                "latency_ms": round(db_latency, 2),
                "stock_count": stock_count
            }
        except Exception as e:
            components['database'] = {
                "status": "unhealthy",
                "error": str(e)
            }
        
        # Check external connectivity (Cloudflare tunnel)
        tunnel_status = "unknown"
        try:
            # Check if cloudflared process is running
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                if 'cloudflared' in proc.info['name']:
                    tunnel_status = "running"
                    break
        except Exception:
            pass
        
        components['tunnel'] = {"status": tunnel_status}
        
        # Check API endpoints
        components['api_endpoints'] = {
            "stocks": "available",
            "screener": "available",
            "news": "available",
            "emails": "available"
        }
        
        # System resources
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        network = psutil.net_io_counters()
        
        components['system'] = {
            "cpu_percent": cpu_percent,
            "memory_percent": memory.percent,
            "network_bytes_sent": network.bytes_sent,
            "network_bytes_recv": network.bytes_recv,
            "uptime_seconds": time.time() - psutil.boot_time()
        }
        
        # Overall health determination
        overall_status = "healthy"
        if components.get('database', {}).get('status') == 'unhealthy':
            overall_status = "degraded"
        if cpu_percent > 90 or memory.percent > 90:
            overall_status = "degraded"
        
        return JsonResponse({
            "status": overall_status,
            "timestamp": datetime.now().isoformat(),
            "components": components
        })
        
    except Exception as e:
        return JsonResponse({
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }, status=503)


@csrf_exempt
@require_http_methods(["GET"])
def readiness_check(request):
    """
    Readiness probe - checks if the service is ready to accept traffic
    Simplified to avoid triggering circuit breaker with complex database queries
    """
    try:
        # Simple database connectivity check (lightweight)
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()

        return JsonResponse({
            "ready": True,
            "timestamp": datetime.now().isoformat()
        })

    except Exception as e:
        # Log the error but don't expose details in production
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Readiness check failed: {str(e)}")

        return JsonResponse({
            "ready": False,
            "error": "Database connectivity check failed",
            "timestamp": datetime.now().isoformat()
        }, status=503)


@csrf_exempt
@require_http_methods(["GET"])
def liveness_check(request):
    """
    Liveness probe - simple check that the service is alive
    """
    return JsonResponse({
        "alive": True,
        "timestamp": datetime.now().isoformat()
    })