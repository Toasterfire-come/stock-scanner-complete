"""
Safe parameter handling for API views to prevent SQL injection
"""
from typing import Dict, Optional

# Whitelist of allowed sort fields
ALLOWED_SORT_FIELDS = {
    'ticker': 'ticker',
    'symbol': 'ticker',  # Alias
    'price': 'current_price',
    'current_price': 'current_price',
    'volume': 'volume',
    'market_cap': 'market_cap',
    'change': 'change_percent',
    'change_percent': 'change_percent',
    'name': 'company_name',
    'company_name': 'company_name',
    'last_updated': 'last_updated',
    'pe_ratio': 'pe_ratio',
    'dividend_yield': 'dividend_yield',
    'week_52_high': 'week_52_high',
    'week_52_low': 'week_52_low',
    'exchange': 'exchange',
    'sector': 'sector',
    'industry': 'industry',
}

# Whitelist of allowed filter fields
ALLOWED_FILTER_FIELDS = {
    'exchange': 'exchange',
    'sector': 'sector',
    'industry': 'industry',
    'market_cap_min': 'market_cap__gte',
    'market_cap_max': 'market_cap__lte',
    'price_min': 'current_price__gte',
    'price_max': 'current_price__lte',
    'volume_min': 'volume__gte',
    'volume_max': 'volume__lte',
    'change_min': 'change_percent__gte',
    'change_max': 'change_percent__lte',
    'pe_ratio_min': 'pe_ratio__gte',
    'pe_ratio_max': 'pe_ratio__lte',
}


def get_safe_sort_field(sort_by: str, sort_order: str = 'asc') -> str:
    """
    Get safe sort field from user input to prevent SQL injection.
    
    Args:
        sort_by: User-provided sort field name
        sort_order: Sort order ('asc' or 'desc')
        
    Returns:
        Safe database field name with optional descending prefix
        
    Example:
        >>> get_safe_sort_field('price', 'desc')
        '-current_price'
        >>> get_safe_sort_field('invalid_field', 'asc')
        'ticker'
    """
    # Default to ticker if invalid
    if sort_by not in ALLOWED_SORT_FIELDS:
        sort_by = 'ticker'
    
    field = ALLOWED_SORT_FIELDS[sort_by]
    
    # Add descending prefix if needed
    if sort_order and sort_order.lower() == 'desc':
        field = f'-{field}'
    
    return field


def get_safe_filter_params(request) -> Dict[str, any]:
    """
    Extract and validate filter parameters from request.
    
    Args:
        request: Django request object
        
    Returns:
        Dictionary of safe filter parameters
        
    Example:
        >>> params = get_safe_filter_params(request)
        >>> Stock.objects.filter(**params)
    """
    filters = {}
    
    for param, field in ALLOWED_FILTER_FIELDS.items():
        value = request.GET.get(param)
        if value:
            # Validate numeric values
            if 'min' in param or 'max' in param:
                try:
                    value = float(value)
                except (ValueError, TypeError):
                    continue
            
            # Validate string values (prevent injection)
            elif isinstance(value, str):
                # Limit length and remove dangerous characters
                value = value[:100].replace(';', '').replace('--', '')
            
            filters[field] = value
    
    return filters


def sanitize_search_input(value: str, max_length: int = 50) -> str:
    """
    Sanitize search input to prevent XSS and SQL injection.
    
    Args:
        value: User-provided search input
        max_length: Maximum allowed length
        
    Returns:
        Sanitized search string
        
    Example:
        >>> sanitize_search_input("AAPL<script>alert('xss')</script>")
        'AAPL'
    """
    if not value:
        return ''
    
    # Remove HTML tags
    import re
    value = re.sub(r'<[^>]*>', '', value)
    
    # Allow only alphanumeric, spaces, and common symbols
    value = re.sub(r'[^a-zA-Z0-9\s\-_\.]', '', value)
    
    # Limit length
    return value[:max_length].strip()


def get_safe_limit(limit: Optional[int], default: int = 50, max_limit: int = 1000) -> int:
    """
    Get safe pagination limit.
    
    Args:
        limit: User-provided limit
        default: Default limit if not provided
        max_limit: Maximum allowed limit
        
    Returns:
        Safe integer limit
        
    Example:
        >>> get_safe_limit(999999, default=50, max_limit=100)
        100
    """
    if limit is None:
        return default
    
    try:
        limit = int(limit)
    except (ValueError, TypeError):
        return default
    
    # Ensure within bounds
    if limit < 1:
        return default
    if limit > max_limit:
        return max_limit
    
    return limit
