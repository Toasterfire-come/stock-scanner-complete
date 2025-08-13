"""
Enhanced Error Handling and Exception Recovery
Improves system resilience without adding new features
"""

import logging
import traceback
import sys
import threading
import time
from typing import Dict, Any, Optional, Callable, Type, Union
from functools import wraps
from contextlib import contextmanager
from django.http import JsonResponse
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.db import IntegrityError, OperationalError, DatabaseError
from rest_framework import status
from rest_framework.response import Response
from django.utils import timezone
from django.core.cache import cache
import json

logger = logging.getLogger(__name__)

class ErrorRecoveryManager:
    """
    Manages error recovery strategies and failure tracking
    """
    
    def __init__(self):
        self.error_counts = {}
        self.error_patterns = {}
        self.recovery_strategies = {}
        self.circuit_breakers = {}
        self._lock = threading.Lock()
        
        # Error thresholds
        self.max_retries = 3
        self.circuit_breaker_threshold = 5
        self.circuit_breaker_timeout = 300  # 5 minutes
    
    def record_error(self, error_type: str, context: str = ""):
        """Record error occurrence for pattern analysis"""
        with self._lock:
            key = f"{error_type}:{context}"
            
            if key not in self.error_counts:
                self.error_counts[key] = {
                    'count': 0,
                    'first_seen': timezone.now(),
                    'last_seen': timezone.now(),
                    'consecutive_failures': 0
                }
            
            self.error_counts[key]['count'] += 1
            self.error_counts[key]['last_seen'] = timezone.now()
            self.error_counts[key]['consecutive_failures'] += 1
    
    def record_success(self, error_type: str, context: str = ""):
        """Record successful operation to reset failure counters"""
        with self._lock:
            key = f"{error_type}:{context}"
            
            if key in self.error_counts:
                self.error_counts[key]['consecutive_failures'] = 0
    
    def should_circuit_break(self, error_type: str, context: str = "") -> bool:
        """Check if circuit breaker should be triggered"""
        key = f"{error_type}:{context}"
        
        with self._lock:
            if key not in self.error_counts:
                return False
            
            error_info = self.error_counts[key]
            
            # Check if circuit is already open
            if key in self.circuit_breakers:
                breaker_time = self.circuit_breakers[key]
                if (timezone.now() - breaker_time).total_seconds() < self.circuit_breaker_timeout:
                    return True
                else:
                    # Reset circuit breaker
                    del self.circuit_breakers[key]
                    error_info['consecutive_failures'] = 0
            
            # Trigger circuit breaker if threshold exceeded
            if error_info['consecutive_failures'] >= self.circuit_breaker_threshold:
                self.circuit_breakers[key] = timezone.now()
                logger.error(f"Circuit breaker triggered for {key}")
                return True
        
        return False
    
    def get_error_stats(self) -> Dict[str, Any]:
        """Get error statistics"""
        with self._lock:
            stats = {
                'total_error_types': len(self.error_counts),
                'active_circuit_breakers': len(self.circuit_breakers),
                'error_summary': {},
                'circuit_breakers': {}
            }
            
            # Summary of top errors
            sorted_errors = sorted(
                self.error_counts.items(),
                key=lambda x: x[1]['count'],
                reverse=True
            )
            
            for key, info in sorted_errors[:10]:
                stats['error_summary'][key] = {
                    'count': info['count'],
                    'consecutive_failures': info['consecutive_failures'],
                    'last_seen': info['last_seen'].isoformat()
                }
            
            # Active circuit breakers
            for key, trigger_time in self.circuit_breakers.items():
                remaining = self.circuit_breaker_timeout - (timezone.now() - trigger_time).total_seconds()
                if remaining > 0:
                    stats['circuit_breakers'][key] = {
                        'triggered_at': trigger_time.isoformat(),
                        'remaining_seconds': int(remaining)
                    }
            
            return stats

# Global error recovery manager
error_recovery = ErrorRecoveryManager()

class CustomException(Exception):
    """Base class for custom exceptions with enhanced context"""
    
    def __init__(self, message: str, error_code: str = None, context: Dict = None, recoverable: bool = True):
        super().__init__(message)
        self.error_code = error_code or self.__class__.__name__
        self.context = context or {}
        self.recoverable = recoverable
        self.timestamp = timezone.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for API responses"""
        return {
            'error_code': self.error_code,
            'message': str(self),
            'context': self.context,
            'recoverable': self.recoverable,
            'timestamp': self.timestamp.isoformat()
        }

class DatabaseConnectionError(CustomException):
    """Database connection related errors"""
    pass

class ExternalServiceError(CustomException):
    """External service related errors"""
    pass

class ValidationError(CustomException):
    """Data validation errors"""
    pass

class RateLimitError(CustomException):
    """Rate limiting errors"""
    def __init__(self, message: str, retry_after: int = None, **kwargs):
        super().__init__(message, **kwargs)
        self.retry_after = retry_after

def resilient_operation(
    max_retries: int = 3,
    delay: float = 1.0,
    backoff_factor: float = 2.0,
    exceptions: tuple = (Exception,),
    circuit_breaker: bool = True
):
    """
    Decorator for resilient operations with retry logic and circuit breaker
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            operation_name = f"{func.__module__}.{func.__name__}"
            
            # Check circuit breaker
            if circuit_breaker and error_recovery.should_circuit_break('operation', operation_name):
                raise CustomException(
                    f"Circuit breaker open for {operation_name}",
                    error_code="CIRCUIT_BREAKER_OPEN",
                    recoverable=False
                )
            
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    result = func(*args, **kwargs)
                    
                    # Record success
                    if attempt > 0:
                        error_recovery.record_success('operation', operation_name)
                        logger.info(f"Operation {operation_name} succeeded after {attempt} retries")
                    
                    return result
                    
                except exceptions as e:
                    last_exception = e
                    error_recovery.record_error('operation', operation_name)
                    
                    if attempt < max_retries:
                        sleep_time = delay * (backoff_factor ** attempt)
                        logger.warning(f"Operation {operation_name} failed (attempt {attempt + 1}), retrying in {sleep_time}s: {e}")
                        time.sleep(sleep_time)
                    else:
                        logger.error(f"Operation {operation_name} failed after {max_retries} retries: {e}")
                
                except Exception as e:
                    # Non-retryable exceptions
                    logger.error(f"Non-retryable error in {operation_name}: {e}")
                    raise
            
            # All retries exhausted
            if last_exception:
                if isinstance(last_exception, CustomException):
                    raise last_exception
                else:
                    raise CustomException(
                        f"Operation failed after {max_retries} retries: {str(last_exception)}",
                        error_code="OPERATION_FAILED",
                        context={'original_error': str(last_exception)}
                    )
        
        return wrapper
    return decorator

@contextmanager
def error_context(operation: str, **context):
    """
    Context manager for enhanced error tracking
    """
    start_time = time.time()
    
    try:
        yield
        
        # Record successful operation
        error_recovery.record_success('context', operation)
        
    except Exception as e:
        # Record error with context
        error_recovery.record_error('context', operation)
        
        # Enhance exception with context
        if hasattr(e, 'context'):
            e.context.update(context)
            e.context['operation'] = operation
            e.context['duration'] = time.time() - start_time
        
        # Log error with full context
        logger.error(
            f"Error in {operation}: {e}",
            extra={
                'operation': operation,
                'context': context,
                'duration': time.time() - start_time,
                'error_type': type(e).__name__
            }
        )
        
        raise

class ErrorHandler:
    """
    Centralized error handling for different types of exceptions
    """
    
    @staticmethod
    def handle_database_error(e: Exception, context: str = "") -> Dict[str, Any]:
        """Handle database-related errors"""
        if isinstance(e, OperationalError):
            error_recovery.record_error('database', 'operational')
            return {
                'error_code': 'DATABASE_OPERATIONAL_ERROR',
                'message': 'Database connection issue. Please try again later.',
                'recoverable': True,
                'retry_after': 30
            }
        
        elif isinstance(e, IntegrityError):
            error_recovery.record_error('database', 'integrity')
            return {
                'error_code': 'DATABASE_INTEGRITY_ERROR',
                'message': 'Data integrity constraint violation.',
                'recoverable': False
            }
        
        elif isinstance(e, DatabaseError):
            error_recovery.record_error('database', 'general')
            return {
                'error_code': 'DATABASE_ERROR',
                'message': 'Database error occurred.',
                'recoverable': True,
                'retry_after': 10
            }
        
        else:
            return ErrorHandler.handle_generic_error(e, context)
    
    @staticmethod
    def handle_validation_error(e: Exception, context: str = "") -> Dict[str, Any]:
        """Handle validation errors"""
        error_recovery.record_error('validation', context)
        
        return {
            'error_code': 'VALIDATION_ERROR',
            'message': str(e),
            'recoverable': True,
            'details': getattr(e, 'error_dict', None) or getattr(e, 'message_dict', None)
        }
    
    @staticmethod
    def handle_permission_error(e: Exception, context: str = "") -> Dict[str, Any]:
        """Handle permission/authorization errors"""
        error_recovery.record_error('permission', context)
        
        return {
            'error_code': 'PERMISSION_DENIED',
            'message': 'Insufficient permissions for this operation.',
            'recoverable': False
        }
    
    @staticmethod
    def handle_rate_limit_error(e: Exception, context: str = "") -> Dict[str, Any]:
        """Handle rate limiting errors"""
        error_recovery.record_error('rate_limit', context)
        
        retry_after = getattr(e, 'retry_after', 60)
        
        return {
            'error_code': 'RATE_LIMIT_EXCEEDED',
            'message': 'Rate limit exceeded. Please try again later.',
            'recoverable': True,
            'retry_after': retry_after
        }
    
    @staticmethod
    def handle_generic_error(e: Exception, context: str = "") -> Dict[str, Any]:
        """Handle generic errors"""
        error_recovery.record_error('generic', context)
        
        # Don't expose internal errors in production
        from django.conf import settings
        
        if getattr(settings, 'DEBUG', False):
            message = str(e)
            details = {
                'traceback': traceback.format_exc(),
                'type': type(e).__name__
            }
        else:
            message = 'An internal error occurred. Please try again later.'
            details = None
        
        return {
            'error_code': 'INTERNAL_ERROR',
            'message': message,
            'recoverable': True,
            'details': details
        }

def custom_exception_handler(exc, context):
    """
    Custom exception handler for DRF
    """
    from rest_framework.views import exception_handler
    
    # Call DRF's default handler first
    response = exception_handler(exc, context)
    
    if response is not None:
        # DRF handled the exception
        error_data = ErrorHandler.handle_generic_error(exc, str(context.get('view', '')))
        
        custom_response_data = {
            'success': False,
            'error': error_data,
            'timestamp': timezone.now().isoformat()
        }
        
        response.data = custom_response_data
        return response
    
    # Handle custom exceptions
    if isinstance(exc, CustomException):
        error_data = exc.to_dict()
        
        response_data = {
            'success': False,
            'error': error_data,
            'timestamp': timezone.now().isoformat()
        }
        
        return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
    
    # Handle database errors
    elif isinstance(exc, (DatabaseError, OperationalError, IntegrityError)):
        error_data = ErrorHandler.handle_database_error(exc, str(context.get('view', '')))
        
        response_data = {
            'success': False,
            'error': error_data,
            'timestamp': timezone.now().isoformat()
        }
        
        return Response(response_data, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    
    # Handle validation errors
    elif isinstance(exc, ValidationError):
        error_data = ErrorHandler.handle_validation_error(exc, str(context.get('view', '')))
        
        response_data = {
            'success': False,
            'error': error_data,
            'timestamp': timezone.now().isoformat()
        }
        
        return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
    
    # Handle unexpected errors
    else:
        logger.exception(f"Unhandled exception in {context.get('view', 'unknown')}: {exc}")
        
        error_data = ErrorHandler.handle_generic_error(exc, str(context.get('view', '')))
        
        response_data = {
            'success': False,
            'error': error_data,
            'timestamp': timezone.now().isoformat()
        }
        
        return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ErrorReportingMiddleware:
    """
    Middleware for comprehensive error reporting
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        try:
            response = self.get_response(request)
            
            # Check for error responses
            if hasattr(response, 'status_code') and response.status_code >= 400:
                self.log_error_response(request, response)
            
            return response
            
        except Exception as e:
            # Log unhandled exceptions
            logger.exception(f"Unhandled exception in middleware for {request.path}: {e}")
            
            # Return error response
            error_data = ErrorHandler.handle_generic_error(e, request.path)
            
            response_data = {
                'success': False,
                'error': error_data,
                'timestamp': timezone.now().isoformat()
            }
            
            return JsonResponse(response_data, status=500)
    
    def log_error_response(self, request, response):
        """Log error response details"""
        logger.warning(
            f"Error response {response.status_code} for {request.method} {request.path}",
            extra={
                'status_code': response.status_code,
                'method': request.method,
                'path': request.path,
                'user': getattr(request, 'user', None),
                'ip': self.get_client_ip(request)
            }
        )
    
    def get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

class RecoveryStrategies:
    """
    Pre-defined recovery strategies for common errors
    """
    
    @staticmethod
    def database_reconnect_strategy():
        """Strategy for database connection issues"""
        from django.db import connection
        
        try:
            connection.close()
            # Force new connection on next query
            logger.info("Database connection reset")
            return True
        except Exception as e:
            logger.error(f"Failed to reset database connection: {e}")
            return False
    
    @staticmethod
    def cache_clear_strategy():
        """Strategy for cache-related issues"""
        try:
            cache.clear()
            logger.info("Cache cleared successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to clear cache: {e}")
            return False
    
    @staticmethod
    def memory_cleanup_strategy():
        """Strategy for memory pressure issues"""
        try:
            import gc
            collected = gc.collect()
            logger.info(f"Garbage collection freed {collected} objects")
            return True
        except Exception as e:
            logger.error(f"Failed to perform garbage collection: {e}")
            return False

def auto_recover(error_type: str, max_attempts: int = 3):
    """
    Decorator for automatic error recovery
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                    
                except Exception as e:
                    if attempt < max_attempts - 1:
                        # Attempt recovery
                        recovered = False
                        
                        if 'database' in error_type.lower():
                            recovered = RecoveryStrategies.database_reconnect_strategy()
                        elif 'cache' in error_type.lower():
                            recovered = RecoveryStrategies.cache_clear_strategy()
                        elif 'memory' in error_type.lower():
                            recovered = RecoveryStrategies.memory_cleanup_strategy()
                        
                        if recovered:
                            logger.info(f"Recovery successful for {error_type}, retrying...")
                            time.sleep(1)  # Brief pause before retry
                        else:
                            logger.warning(f"Recovery failed for {error_type}")
                            break
                    else:
                        raise
            
            return func(*args, **kwargs)
        
        return wrapper
    return decorator

def get_error_summary() -> Dict[str, Any]:
    """
    Get comprehensive error summary for monitoring
    """
    stats = error_recovery.get_error_stats()
    
    # Add additional metrics
    stats.update({
        'system_health': {
            'memory_usage': _get_memory_usage(),
            'active_connections': _get_active_connections(),
            'cache_status': _get_cache_status()
        },
        'recommendations': _get_error_recommendations(stats)
    })
    
    return stats

def _get_memory_usage():
    """Get current memory usage"""
    try:
        import psutil
        return psutil.virtual_memory().percent
    except:
        return None

def _get_active_connections():
    """Get active database connections"""
    try:
        from django.db import connection
        return len(connection.queries)
    except:
        return None

def _get_cache_status():
    """Get cache status"""
    try:
        cache.set('health_check', 'ok', 10)
        return cache.get('health_check') == 'ok'
    except:
        return False

def _get_error_recommendations(stats):
    """Get recommendations based on error patterns"""
    recommendations = []
    
    if stats['active_circuit_breakers'] > 0:
        recommendations.append("Circuit breakers active - investigate failing services")
    
    error_summary = stats.get('error_summary', {})
    
    for error_key, info in error_summary.items():
        if info['consecutive_failures'] > 3:
            recommendations.append(f"High failure rate for {error_key} - review implementation")
    
    return recommendations

def initialize_error_handling():
    """
    Initialize enhanced error handling system
    """
    # Configure logging for errors
    error_logger = logging.getLogger('stocks.errors')
    error_logger.setLevel(logging.WARNING)
    
    logger.info("Enhanced error handling system initialized")