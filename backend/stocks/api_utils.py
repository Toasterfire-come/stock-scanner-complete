"""
API Utility Functions for Stock Scanner
Provides input validation, sanitization, and standardized error responses
"""

import re
from django.utils.html import escape
from rest_framework.response import Response
from rest_framework import status


# Allowed sort fields (whitelist to prevent SQL injection)
ALLOWED_SORT_FIELDS = {
    'price': 'current_price',
    'volume': 'volume',
    'market_cap': 'market_cap',
    'change': 'change_percent',
    'change_percent': 'change_percent',
    'ticker': 'ticker',
    'company_name': 'company_name',
    'pe_ratio': 'pe_ratio',
    'last_updated': 'last_updated',
}


def sanitize_search_input(value, max_length=50):
    """
    Sanitize search input to prevent XSS and injection attacks

    Args:
        value: Input string to sanitize
        max_length: Maximum allowed length

    Returns:
        Sanitized string
    """
    if not value:
        return ''

    # Remove HTML tags
    value = escape(str(value))

    # Allow only alphanumeric, spaces, and common symbols
    value = re.sub(r'[^a-zA-Z0-9\s\-_\.]', '', value)

    # Limit length
    return value[:max_length].strip()


def sanitize_sort_field(sort_by, default='last_updated'):
    """
    Sanitize sort field to prevent SQL injection

    Args:
        sort_by: Requested sort field
        default: Default sort field if invalid

    Returns:
        Safe sort field name
    """
    if not sort_by or sort_by not in ALLOWED_SORT_FIELDS:
        return ALLOWED_SORT_FIELDS[default]

    return ALLOWED_SORT_FIELDS[sort_by]


def validate_positive_integer(value, default=None, max_value=None):
    """
    Validate and return a positive integer

    Args:
        value: Value to validate
        default: Default value if invalid
        max_value: Maximum allowed value

    Returns:
        Validated integer or default
    """
    try:
        val = int(value)
        if val < 0:
            return default
        if max_value and val > max_value:
            return max_value
        return val
    except (ValueError, TypeError):
        return default


def validate_decimal(value, default=None):
    """
    Validate and return a decimal value

    Args:
        value: Value to validate
        default: Default value if invalid

    Returns:
        Validated float or default
    """
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def error_response(message, status_code=400, errors=None):
    """
    Standard error response format

    Args:
        message: Error message
        status_code: HTTP status code
        errors: Additional error details (optional)

    Returns:
        DRF Response object with standardized error format
    """
    return Response({
        'success': False,
        'error': {
            'message': message,
            'code': status_code,
            'details': errors or []
        }
    }, status=status_code)


def success_response(data, message='Success', status_code=200):
    """
    Standard success response format

    Args:
        data: Response data
        message: Success message
        status_code: HTTP status code

    Returns:
        DRF Response object with standardized success format
    """
    return Response({
        'success': True,
        'message': message,
        'data': data
    }, status=status_code)


def get_client_ip(request):
    """
    Get client IP address from request

    Args:
        request: Django request object

    Returns:
        Client IP address string
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
