"""
Monitoring, logging, and analytics service
"""
import os
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from prometheus_client import Counter, Histogram, Gauge, generate_latest
import time
from functools import wraps
import traceback
import psutil
import asyncio

# Initialize Sentry for error tracking
if os.getenv('SENTRY_DSN'):
    sentry_sdk.init(
        dsn=os.getenv('SENTRY_DSN'),
        integrations=[FastApiIntegration()],
        traces_sample_rate=float(os.getenv('SENTRY_TRACES_SAMPLE_RATE', 0.1)),
        environment=os.getenv('ENVIRONMENT', 'development')
    )

# Prometheus metrics
request_count = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

request_duration = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration',
    ['method', 'endpoint']
)

active_users = Gauge(
    'active_users_total',
    'Number of active users'
)

subscription_count = Gauge(
    'subscription_count',
    'Number of active subscriptions',
    ['plan']
)

api_calls = Counter(
    'api_calls_total',
    'Total API calls',
    ['user_id', 'endpoint']
)

payment_transactions = Counter(
    'payment_transactions_total',
    'Total payment transactions',
    ['status', 'plan']
)

class PerformanceMonitor:
    """
    Monitor application performance
    """
    
    @staticmethod
    def track_execution_time(func_name: str = None):
        """
        Decorator to track function execution time
        """
        def decorator(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = await func(*args, **kwargs)
                    execution_time = time.time() - start_time
                    
                    # Log slow operations
                    if execution_time > 1.0:
                        logging.warning(
                            f"Slow operation: {func_name or func.__name__} "
                            f"took {execution_time:.2f} seconds"
                        )
                    
                    # Track in metrics
                    request_duration.labels(
                        method='function',
                        endpoint=func_name or func.__name__
                    ).observe(execution_time)
                    
                    return result
                except Exception as e:
                    execution_time = time.time() - start_time
                    logging.error(
                        f"Error in {func_name or func.__name__}: {str(e)} "
                        f"(executed in {execution_time:.2f} seconds)"
                    )
                    raise
            
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    execution_time = time.time() - start_time
                    
                    if execution_time > 1.0:
                        logging.warning(
                            f"Slow operation: {func_name or func.__name__} "
                            f"took {execution_time:.2f} seconds"
                        )
                    
                    return result
                except Exception as e:
                    execution_time = time.time() - start_time
                    logging.error(
                        f"Error in {func_name or func.__name__}: {str(e)} "
                        f"(executed in {execution_time:.2f} seconds)"
                    )
                    raise
            
            if asyncio.iscoroutinefunction(func):
                return async_wrapper
            else:
                return sync_wrapper
        return decorator
    
    @staticmethod
    def get_system_metrics() -> Dict[str, Any]:
        """
        Get system resource metrics
        """
        return {
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory': {
                'total': psutil.virtual_memory().total,
                'available': psutil.virtual_memory().available,
                'percent': psutil.virtual_memory().percent,
                'used': psutil.virtual_memory().used
            },
            'disk': {
                'total': psutil.disk_usage('/').total,
                'used': psutil.disk_usage('/').used,
                'free': psutil.disk_usage('/').free,
                'percent': psutil.disk_usage('/').percent
            },
            'network': {
                'bytes_sent': psutil.net_io_counters().bytes_sent,
                'bytes_recv': psutil.net_io_counters().bytes_recv,
                'packets_sent': psutil.net_io_counters().packets_sent,
                'packets_recv': psutil.net_io_counters().packets_recv
            }
        }

class AuditLogger:
    """
    Audit logging for security and compliance
    """
    
    def __init__(self):
        self.logger = logging.getLogger('audit')
        handler = logging.FileHandler('audit.log')
        handler.setFormatter(
            logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
        )
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
    
    def log_user_action(
        self,
        user_id: int,
        action: str,
        resource: str,
        resource_id: Optional[int] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Log user action for audit trail
        """
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'user_id': user_id,
            'action': action,
            'resource': resource,
            'resource_id': resource_id,
            'ip_address': ip_address,
            'user_agent': user_agent,
            'metadata': metadata or {}
        }
        
        self.logger.info(json.dumps(log_entry))
    
    def log_security_event(
        self,
        event_type: str,
        severity: str,
        description: str,
        user_id: Optional[int] = None,
        ip_address: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Log security-related events
        """
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'event_type': event_type,
            'severity': severity,
            'description': description,
            'user_id': user_id,
            'ip_address': ip_address,
            'metadata': metadata or {}
        }
        
        if severity in ['HIGH', 'CRITICAL']:
            self.logger.critical(json.dumps(log_entry))
            # Send alert
            self._send_security_alert(log_entry)
        else:
            self.logger.warning(json.dumps(log_entry))
    
    def log_payment_event(
        self,
        user_id: int,
        event_type: str,
        amount: float,
        currency: str,
        status: str,
        payment_method: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Log payment-related events for compliance
        """
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'user_id': user_id,
            'event_type': event_type,
            'amount': amount,
            'currency': currency,
            'status': status,
            'payment_method': payment_method,
            'metadata': metadata or {}
        }
        
        self.logger.info(json.dumps(log_entry))
        
        # Track in metrics
        payment_transactions.labels(
            status=status,
            plan=metadata.get('plan', 'unknown')
        ).inc()
    
    def _send_security_alert(self, log_entry: Dict[str, Any]):
        """
        Send security alert to administrators
        """
        # Implement alert mechanism (email, Slack, PagerDuty, etc.)
        pass

class Analytics:
    """
    Business analytics and reporting
    """
    
    @staticmethod
    async def get_user_analytics(
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """
        Get user analytics for the specified period
        """
        # This would query the database in production
        return {
            'new_users': 0,
            'active_users': 0,
            'churned_users': 0,
            'retention_rate': 0.0,
            'average_session_duration': 0,
            'top_features': [],
            'user_growth_rate': 0.0
        }
    
    @staticmethod
    async def get_revenue_analytics(
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """
        Get revenue analytics for the specified period
        """
        return {
            'total_revenue': 0.0,
            'recurring_revenue': 0.0,
            'new_revenue': 0.0,
            'churn_rate': 0.0,
            'average_revenue_per_user': 0.0,
            'lifetime_value': 0.0,
            'revenue_by_plan': {},
            'payment_success_rate': 0.0
        }
    
    @staticmethod
    async def get_api_usage_analytics(
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """
        Get API usage analytics
        """
        return {
            'total_requests': 0,
            'unique_users': 0,
            'average_requests_per_user': 0,
            'top_endpoints': [],
            'error_rate': 0.0,
            'average_response_time': 0.0,
            'peak_usage_times': []
        }
    
    @staticmethod
    async def generate_monthly_report() -> Dict[str, Any]:
        """
        Generate comprehensive monthly report
        """
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=30)
        
        user_analytics = await Analytics.get_user_analytics(start_date, end_date)
        revenue_analytics = await Analytics.get_revenue_analytics(start_date, end_date)
        api_analytics = await Analytics.get_api_usage_analytics(start_date, end_date)
        
        return {
            'period': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat()
            },
            'users': user_analytics,
            'revenue': revenue_analytics,
            'api_usage': api_analytics,
            'health_score': Analytics._calculate_health_score(
                user_analytics, revenue_analytics, api_analytics
            )
        }
    
    @staticmethod
    def _calculate_health_score(
        user_analytics: Dict[str, Any],
        revenue_analytics: Dict[str, Any],
        api_analytics: Dict[str, Any]
    ) -> float:
        """
        Calculate overall platform health score (0-100)
        """
        score = 50.0  # Base score
        
        # User growth factor
        if user_analytics['user_growth_rate'] > 0:
            score += min(user_analytics['user_growth_rate'] * 10, 20)
        
        # Revenue factor
        if revenue_analytics['churn_rate'] < 5:
            score += 15
        
        # API reliability factor
        if api_analytics['error_rate'] < 1:
            score += 15
        
        return min(max(score, 0), 100)

class ErrorHandler:
    """
    Centralized error handling and recovery
    """
    
    @staticmethod
    def handle_error(
        error: Exception,
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Handle and log errors with context
        """
        error_id = str(datetime.utcnow().timestamp())
        
        error_details = {
            'error_id': error_id,
            'type': type(error).__name__,
            'message': str(error),
            'traceback': traceback.format_exc(),
            'context': context or {},
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Log to file
        logging.error(json.dumps(error_details))
        
        # Send to Sentry if configured
        if os.getenv('SENTRY_DSN'):
            sentry_sdk.capture_exception(error)
        
        # Return user-friendly error response
        return {
            'error': True,
            'error_id': error_id,
            'message': 'An error occurred. Please try again later.',
            'support_message': f'If the problem persists, please contact support with error ID: {error_id}'
        }
    
    @staticmethod
    def create_error_response(
        status_code: int,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create standardized error response
        """
        return {
            'error': True,
            'status_code': status_code,
            'message': message,
            'details': details or {},
            'timestamp': datetime.utcnow().isoformat()
        }