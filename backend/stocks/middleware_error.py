"""
Enhanced error handling middleware for production stability
"""
import logging
import traceback
import json
from datetime import datetime
from django.http import JsonResponse
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db import DatabaseError, OperationalError
import time

logger = logging.getLogger(__name__)


class EnhancedErrorHandlingMiddleware:
    """
    Middleware to handle errors gracefully and provide better logging
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.error_count = {}
        self.last_error_time = {}
        
    def __call__(self, request):
        try:
            # Add request ID for tracking
            request.request_id = f"{int(time.time() * 1000)}-{id(request)}"
            
            # Log incoming request
            if settings.DEBUG:
                logger.info(f"Request {request.request_id}: {request.method} {request.path}")
            
            response = self.get_response(request)
            
            # Log response status
            if response.status_code >= 400:
                logger.warning(f"Request {request.request_id} returned {response.status_code}")
            
            return response
            
        except Exception as e:
            return self.handle_exception(request, e)
    
    def handle_exception(self, request, exception):
        """
        Handle different types of exceptions with appropriate responses
        """
        error_id = f"ERR-{int(time.time() * 1000)}"
        path = request.path
        
        # Track error frequency
        self.track_error_frequency(path, exception)
        
        # Log the full exception
        logger.error(
            f"Error {error_id} on {request.method} {path}: {str(exception)}",
            exc_info=True,
            extra={
                'request_id': getattr(request, 'request_id', 'unknown'),
                'user': getattr(request.user, 'username', 'anonymous'),
                'ip': self.get_client_ip(request)
            }
        )
        
        # Determine response based on exception type
        if isinstance(exception, OperationalError):
            # Database connection issues
            return self.database_error_response(error_id, "Database connection error")
        
        elif isinstance(exception, DatabaseError):
            # Other database errors
            return self.database_error_response(error_id, "Database error occurred")
        
        elif isinstance(exception, ObjectDoesNotExist):
            # Object not found
            return JsonResponse({
                'error': 'Resource not found',
                'error_id': error_id,
                'path': path
            }, status=404)
        
        elif isinstance(exception, ValueError):
            # Invalid input
            return JsonResponse({
                'error': 'Invalid input provided',
                'error_id': error_id,
                'message': str(exception) if settings.DEBUG else 'Invalid input'
            }, status=400)
        
        elif isinstance(exception, ConnectionError):
            # Network/connection issues
            return JsonResponse({
                'error': 'Connection error',
                'error_id': error_id,
                'message': 'Service temporarily unavailable'
            }, status=503)
        
        else:
            # Generic error
            return self.generic_error_response(error_id, exception)
    
    def database_error_response(self, error_id, message):
        """
        Handle database errors with retry information
        """
        return JsonResponse({
            'error': message,
            'error_id': error_id,
            'retry_after': 30,
            'message': 'The service is experiencing database issues. Please try again later.'
        }, status=503, headers={'Retry-After': '30'})
    
    def generic_error_response(self, error_id, exception):
        """
        Handle generic errors
        """
        if settings.DEBUG:
            # In debug mode, show full error
            return JsonResponse({
                'error': 'Internal server error',
                'error_id': error_id,
                'exception': str(exception),
                'traceback': traceback.format_exc()
            }, status=500)
        else:
            # In production, hide details
            return JsonResponse({
                'error': 'Internal server error',
                'error_id': error_id,
                'message': 'An unexpected error occurred. Please try again later.'
            }, status=500)
    
    def track_error_frequency(self, path, exception):
        """
        Track error frequency for monitoring
        """
        error_key = f"{path}:{type(exception).__name__}"
        current_time = time.time()
        
        # Initialize or increment error count
        if error_key not in self.error_count:
            self.error_count[error_key] = 0
            self.last_error_time[error_key] = current_time
        
        self.error_count[error_key] += 1
        
        # Check if errors are happening too frequently
        time_diff = current_time - self.last_error_time[error_key]
        if time_diff < 60 and self.error_count[error_key] > 10:
            logger.critical(
                f"High error rate detected: {error_key} - {self.error_count[error_key]} errors in {time_diff:.1f} seconds"
            )
        
        # Reset counter after 5 minutes
        if time_diff > 300:
            self.error_count[error_key] = 1
            self.last_error_time[error_key] = current_time
    
    def get_client_ip(self, request):
        """
        Get client IP address from request
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class CircuitBreakerMiddleware:
    """
    Circuit breaker pattern to prevent cascading failures
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.failure_count = {}
        self.circuit_open = {}
        self.last_failure_time = {}
        self.threshold = 5  # Number of failures before opening circuit
        self.timeout = 60   # Seconds before attempting to close circuit
        # Exclude health check endpoints from circuit breaker
        self.excluded_paths = [
            '/api/health/',
            '/api/health/detailed/',
            '/api/health/ready/',
            '/api/health/live/',
            '/health/',
        ]

    def __call__(self, request):
        endpoint = request.path

        # Skip circuit breaker for health check endpoints
        if any(endpoint.startswith(excluded) for excluded in self.excluded_paths):
            return self.get_response(request)

        # Check if circuit is open
        if self.is_circuit_open(endpoint):
            return JsonResponse({
                'error': 'Service temporarily unavailable',
                'message': 'This endpoint is experiencing issues. Please try again later.',
                'retry_after': self.timeout
            }, status=503, headers={'Retry-After': str(self.timeout)})
        
        try:
            response = self.get_response(request)
            
            # Reset failure count on success
            if response.status_code < 500:
                self.reset_failure_count(endpoint)
            else:
                self.record_failure(endpoint)
            
            return response
            
        except Exception as e:
            self.record_failure(endpoint)
            raise
    
    def is_circuit_open(self, endpoint):
        """
        Check if circuit is open for endpoint
        """
        if endpoint not in self.circuit_open:
            return False
        
        if not self.circuit_open[endpoint]:
            return False
        
        # Check if timeout has passed
        time_since_failure = time.time() - self.last_failure_time.get(endpoint, 0)
        if time_since_failure > self.timeout:
            logger.info(f"Circuit breaker closing for {endpoint}")
            self.circuit_open[endpoint] = False
            self.failure_count[endpoint] = 0
            return False
        
        return True
    
    def record_failure(self, endpoint):
        """
        Record a failure for an endpoint
        """
        if endpoint not in self.failure_count:
            self.failure_count[endpoint] = 0
        
        self.failure_count[endpoint] += 1
        self.last_failure_time[endpoint] = time.time()
        
        if self.failure_count[endpoint] >= self.threshold:
            if not self.circuit_open.get(endpoint, False):
                logger.warning(f"Circuit breaker opening for {endpoint} after {self.failure_count[endpoint]} failures")
                self.circuit_open[endpoint] = True
    
    def reset_failure_count(self, endpoint):
        """
        Reset failure count for successful request
        """
        if endpoint in self.failure_count:
            self.failure_count[endpoint] = 0
        if endpoint in self.circuit_open:
            self.circuit_open[endpoint] = False