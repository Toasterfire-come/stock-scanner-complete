"""
Security utilities for the stocks application.
Provides decorators and validation functions for secure API endpoints.
"""

import json
import re
import logging
from functools import wraps
from datetime import datetime, timedelta
from decimal import Decimal, InvalidOperation
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone
from django.conf import settings

logger = logging.getLogger(__name__)

def secure_api_endpoint(methods=['POST'], require_auth=True, rate_limit=None):
    """
    Comprehensive security decorator for API endpoints.
    
    Args:
        methods: List of allowed HTTP methods
        require_auth: Whether authentication is required
        rate_limit: Rate limiting configuration (optional)
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Log the API request
            log_api_request(request, view_func.__name__)
            
            try:
                # Apply decorators in proper order
                if require_auth:
                    # Check authentication
                    if not request.user.is_authenticated:
                        return JsonResponse({
                            'success': False,
                            'error': 'Authentication required',
                            'error_code': 'AUTH_REQUIRED'
                        }, status=401)
                
                # Validate HTTP method
                if request.method not in methods:
                    return JsonResponse({
                        'success': False,
                        'error': f'Method {request.method} not allowed',
                        'error_code': 'METHOD_NOT_ALLOWED'
                    }, status=405)
                
                # Rate limiting (if configured)
                if rate_limit and not check_rate_limit(request, rate_limit):
                    return JsonResponse({
                        'success': False,
                        'error': 'Rate limit exceeded',
                        'error_code': 'RATE_LIMIT_EXCEEDED'
                    }, status=429)
                
                # Input validation and sanitization
                if request.method in ['POST', 'PUT', 'PATCH']:
                    try:
                        if hasattr(request, 'body') and request.body:
                            request.validated_data = validate_json_input(request.body)
                        else:
                            request.validated_data = {}
                    except ValidationError as e:
                        return JsonResponse({
                            'success': False,
                            'error': str(e),
                            'error_code': 'INVALID_INPUT'
                        }, status=400)
                
                # Execute the actual view function
                with transaction.atomic():
                    response = view_func(request, *args, **kwargs)
                
                # Log successful API response
                log_api_response(request, view_func.__name__, True)
                return response
                
            except Exception as e:
                # Log error and return standardized error response
                log_api_response(request, view_func.__name__, False, str(e))
                logger.exception(f"Error in {view_func.__name__}: {str(e)}")
                
                return JsonResponse({
                    'success': False,
                    'error': 'Internal server error',
                    'error_code': 'INTERNAL_ERROR'
                }, status=500)
        
        return wrapper
    return decorator

def validate_user_input(data, schema):
    """
    Validate user input against a schema.
    
    Args:
        data: Input data to validate
        schema: Validation schema
    
    Returns:
        dict: Validated and sanitized data
    
    Raises:
        ValidationError: If validation fails
    """
    validated = {}
    
    for field, rules in schema.items():
        value = data.get(field)
        
        # Check required fields
        if rules.get('required', False) and (value is None or value == ''):
            raise ValidationError(f"Field '{field}' is required")
        
        # Skip validation for optional empty fields
        if value is None or value == '':
            if 'default' in rules:
                validated[field] = rules['default']
            continue
        
        # Type validation and conversion
        field_type = rules.get('type', 'string')
        
        if field_type == 'string':
            validated[field] = validate_string(value, rules)
        elif field_type == 'decimal':
            validated[field] = validate_decimal(value, rules)
        elif field_type == 'integer':
            validated[field] = validate_integer(value, rules)
        elif field_type == 'boolean':
            validated[field] = validate_boolean(value)
        elif field_type == 'email':
            validated[field] = validate_email(value)
        elif field_type == 'ticker':
            validated[field] = validate_ticker(value)
        elif field_type == 'datetime':
            validated[field] = validate_datetime(value)
        elif field_type == 'list':
            validated[field] = validate_list(value, rules)
        else:
            validated[field] = value
    
    return validated

def validate_string(value, rules):
    """Validate and sanitize string input"""
    if not isinstance(value, str):
        value = str(value)
    
    # Remove dangerous characters
    value = sanitize_string(value)
    
    # Length validation
    min_length = rules.get('min_length', 0)
    max_length = rules.get('max_length', 1000)
    
    if len(value) < min_length:
        raise ValidationError(f"String too short (min {min_length} characters)")
    if len(value) > max_length:
        raise ValidationError(f"String too long (max {max_length} characters)")
    
    # Pattern validation
    if 'pattern' in rules and not re.match(rules['pattern'], value):
        raise ValidationError(f"String does not match required pattern")
    
    return value

def validate_decimal(value, rules):
    """Validate decimal input"""
    try:
        decimal_value = Decimal(str(value))
    except (InvalidOperation, ValueError):
        raise ValidationError("Invalid decimal value")
    
    # Range validation
    min_val = rules.get('min_value')
    max_val = rules.get('max_value')
    
    if min_val is not None and decimal_value < Decimal(str(min_val)):
        raise ValidationError(f"Value too small (min {min_val})")
    if max_val is not None and decimal_value > Decimal(str(max_val)):
        raise ValidationError(f"Value too large (max {max_val})")
    
    # Precision validation
    max_digits = rules.get('max_digits', 20)
    decimal_places = rules.get('decimal_places', 4)
    
    # Convert to string to check precision
    value_str = str(decimal_value)
    if '.' in value_str:
        integer_part, decimal_part = value_str.split('.')
        if len(decimal_part) > decimal_places:
            raise ValidationError(f"Too many decimal places (max {decimal_places})")
        if len(integer_part) + len(decimal_part) > max_digits:
            raise ValidationError(f"Too many digits (max {max_digits})")
    else:
        if len(value_str) > max_digits:
            raise ValidationError(f"Too many digits (max {max_digits})")
    
    return decimal_value

def validate_integer(value, rules):
    """Validate integer input"""
    try:
        int_value = int(value)
    except (ValueError, TypeError):
        raise ValidationError("Invalid integer value")
    
    # Range validation
    min_val = rules.get('min_value')
    max_val = rules.get('max_value')
    
    if min_val is not None and int_value < min_val:
        raise ValidationError(f"Value too small (min {min_val})")
    if max_val is not None and int_value > max_val:
        raise ValidationError(f"Value too large (max {max_val})")
    
    return int_value

def validate_boolean(value):
    """Validate boolean input"""
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        if value.lower() in ['true', '1', 'yes', 'on']:
            return True
        elif value.lower() in ['false', '0', 'no', 'off']:
            return False
    elif isinstance(value, int):
        return bool(value)
    
    raise ValidationError("Invalid boolean value")

def validate_email(value):
    """Validate email format"""
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, value):
        raise ValidationError("Invalid email format")
    return value.lower()

def validate_ticker(value):
    """Validate stock ticker format"""
    if not isinstance(value, str):
        value = str(value)
    
    value = value.upper().strip()
    
    # Basic ticker validation
    if not re.match(r'^[A-Z]{1,10}$', value):
        raise ValidationError("Invalid ticker format (1-10 uppercase letters only)")
    
    return value

def validate_datetime(value):
    """Validate datetime input"""
    if isinstance(value, datetime):
        return value
    
    if isinstance(value, str):
        # Try parsing common datetime formats
        formats = [
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%d %H:%M',
            '%Y-%m-%d',
            '%Y-%m-%dT%H:%M:%S',
            '%Y-%m-%dT%H:%M:%SZ',
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(value, fmt)
            except ValueError:
                continue
    
    raise ValidationError("Invalid datetime format")

def validate_list(value, rules):
    """Validate list input"""
    if not isinstance(value, list):
        raise ValidationError("Value must be a list")
    
    max_items = rules.get('max_items', 100)
    if len(value) > max_items:
        raise ValidationError(f"Too many items (max {max_items})")
    
    item_type = rules.get('item_type', 'string')
    validated_items = []
    
    for item in value:
        if item_type == 'ticker':
            validated_items.append(validate_ticker(item))
        elif item_type == 'string':
            validated_items.append(validate_string(item, rules.get('item_rules', {})))
        else:
            validated_items.append(item)
    
    return validated_items

def sanitize_string(value):
    """Remove potentially dangerous characters from string"""
    if not isinstance(value, str):
        return value
    
    # Remove null bytes and control characters
    value = ''.join(char for char in value if ord(char) >= 32 or char in '\n\r\t')
    
    # Remove script tags and other dangerous patterns
    dangerous_patterns = [
        r'<script[^>]*>.*?</script>',
        r'javascript:',
        r'vbscript:',
        r'on\w+\s*=',
    ]
    
    for pattern in dangerous_patterns:
        value = re.sub(pattern, '', value, flags=re.IGNORECASE | re.DOTALL)
    
    return value.strip()

def validate_json_input(body):
    """Validate and parse JSON input"""
    try:
        if isinstance(body, bytes):
            body = body.decode('utf-8')
        return json.loads(body)
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        raise ValidationError(f"Invalid JSON: {str(e)}")

def check_rate_limit(request, limit_config):
    """
    Check if request exceeds rate limits.
    
    Args:
        request: Django request object
        limit_config: Rate limit configuration
    
    Returns:
        bool: True if request is within limits
    """
    # Rate limiting is now handled by RateLimitMiddleware
    # This function is kept for backward compatibility
    # The middleware handles rate limiting more efficiently at a global level
    
    # Check if request was authenticated via API key (no rate limiting)
    if hasattr(request, 'api_key_authenticated') and request.api_key_authenticated:
        return True
    
    # For endpoints that use this decorator, always return True
    # as the middleware has already handled rate limiting
    return True

def log_api_request(request, endpoint_name):
    """Log API request for audit trail"""
    logger.info(f"API Request: {endpoint_name} from {request.META.get('REMOTE_ADDR')} "
                f"by {request.user.username if request.user.is_authenticated else 'Anonymous'}")

def log_api_response(request, endpoint_name, success, error_message=None):
    """Log API response for audit trail"""
    status = "SUCCESS" if success else "ERROR"
    message = f"API Response: {endpoint_name} - {status}"
    if error_message:
        message += f" - {error_message}"
    
    if success:
        logger.info(message)
    else:
        logger.error(message)

# Common validation schemas for reuse
PORTFOLIO_SCHEMA = {
    'name': {
        'type': 'string',
        'required': True,
        'min_length': 1,
        'max_length': 100
    },
    'description': {
        'type': 'string',
        'max_length': 1000,
        'default': ''
    },
    'is_public': {
        'type': 'boolean',
        'default': False
    }
}

HOLDING_SCHEMA = {
    'stock_ticker': {
        'type': 'ticker',
        'required': True
    },
    'shares': {
        'type': 'decimal',
        'required': True,
        'min_value': 0.0001,
        'max_value': 1000000,
        'decimal_places': 4
    },
    'average_cost': {
        'type': 'decimal',
        'required': True,
        'min_value': 0.01,
        'max_value': 100000,
        'decimal_places': 4
    },
    'current_price': {
        'type': 'decimal',
        'min_value': 0.01,
        'max_value': 100000,
        'decimal_places': 4
    }
}

WATCHLIST_SCHEMA = {
    'name': {
        'type': 'string',
        'required': True,
        'min_length': 1,
        'max_length': 100
    },
    'description': {
        'type': 'string',
        'max_length': 1000,
        'default': ''
    }
}

TRANSACTION_SCHEMA = {
    'stock_ticker': {
        'type': 'ticker',
        'required': True
    },
    'transaction_type': {
        'type': 'string',
        'required': True,
        'pattern': r'^(buy|sell)$'
    },
    'shares': {
        'type': 'decimal',
        'required': True,
        'min_value': 0.0001,
        'decimal_places': 4
    },
    'price': {
        'type': 'decimal',
        'required': True,
        'min_value': 0.01,
        'decimal_places': 4
    },
    'fees': {
        'type': 'decimal',
        'min_value': 0,
        'decimal_places': 2,
        'default': 0
    },
    'transaction_date': {
        'type': 'datetime',
        'required': True
    },
    'alert_category': {
        'type': 'string',
        'pattern': r'^(earnings|analyst|insider|merger|volume|price|manual)$',
        'default': 'manual'
    }
}