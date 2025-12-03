"""
Custom throttle classes for different API endpoint types
"""
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle


class StockDataThrottle(UserRateThrottle):
    """
    Throttle for stock data endpoints.
    Authenticated users: 1000 requests/hour
    """
    rate = '1000/hour'


class RealtimeDataThrottle(UserRateThrottle):
    """
    Throttle for realtime data endpoints.
    Authenticated users: 60 requests/minute to prevent abuse
    """
    rate = '60/minute'


class PublicEndpointThrottle(AnonRateThrottle):
    """
    Throttle for public endpoints.
    Anonymous users: 10 requests/minute
    """
    rate = '10/minute'


class AlertCreationThrottle(UserRateThrottle):
    """
    Throttle for alert creation.
    Authenticated users: 10 alerts/hour to prevent spam
    """
    rate = '10/hour'


class SearchThrottle(UserRateThrottle):
    """
    Throttle for search endpoints.
    Authenticated users: 100 searches/hour
    """
    rate = '100/hour'


class ScreenerThrottle(UserRateThrottle):
    """
    Throttle for screener execution.
    Authenticated users: 30 executions/hour (resource intensive)
    """
    rate = '30/hour'


class PortfolioThrottle(UserRateThrottle):
    """
    Throttle for portfolio operations.
    Authenticated users: 200 requests/hour
    """
    rate = '200/hour'


class WatchlistThrottle(UserRateThrottle):
    """
    Throttle for watchlist operations.
    Authenticated users: 200 requests/hour
    """
    rate = '200/hour'


class BurstThrottle(UserRateThrottle):
    """
    Short burst throttle for rapid requests.
    Authenticated users: 60 requests/minute
    """
    rate = '60/minute'
