"""
Performance Optimizations for Stock Scanner
Caching, database optimization, and efficient data handling
"""

from django.core.cache import cache
from django.db.models import Prefetch, Q, Count, Sum
from django.utils import timezone
from datetime import timedelta
import json
import hashlib

class PerformanceOptimizer:
"""Centralized performance optimization utilities"""

@staticmethod
def get_cache_key(prefix, *args):
"""Generate consistent cache keys"""
key_string = f"{prefix}:{'_'.join(str(arg) for arg in args)}"
return hashlib.md5(key_string.encode()).hexdigest()[:32]

@staticmethod
def cache_with_timeout(key, data, timeout=300):
"""Cache data with consistent timeout"""
cache.set(key, data, timeout)
return data

@staticmethod
def get_cached_or_compute(key, compute_func, timeout=300):
"""Get from cache or compute and cache"""
data = cache.get(key)
if data is None:
data = compute_func()
cache.set(key, data, timeout)
return data

# Optimized database queries
class OptimizedQueries:
"""Efficient database query patterns"""

@staticmethod
def get_user_portfolios_optimized(user):
"""Efficiently get user portfolios with holdings"""
from .models import Portfolio

cache_key = PerformanceOptimizer.get_cache_key("user_portfolios", user.id)

def compute_portfolios():
return Portfolio.objects.filter(
user=user, 
is_active=True
).prefetch_related(
Prefetch('holdings', queryset=Portfolio.objects.select_related())
).select_related('user')

return PerformanceOptimizer.get_cached_or_compute(
cache_key, compute_portfolios, timeout=300
)

@staticmethod
def get_market_analysis_optimized(analysis_type=None, limit=20):
"""Efficiently get market analysis with minimal queries"""
from .models import MarketAnalysis

cache_key = PerformanceOptimizer.get_cache_key(
"market_analysis", analysis_type or "all", limit
)

def compute_analysis():
queryset = MarketAnalysis.objects.select_related('author')
if analysis_type:
queryset = queryset.filter(analysis_type=analysis_type)
return list(queryset[:limit])

return PerformanceOptimizer.get_cached_or_compute(
cache_key, compute_analysis, timeout=600
)

@staticmethod
def get_stock_alerts_optimized(filters=None, limit=50):
"""Efficiently get stock alerts with filters"""
from .models import StockAlert

cache_key = PerformanceOptimizer.get_cache_key(
"stock_alerts", json.dumps(filters or {}), limit
)

def compute_alerts():
queryset = StockAlert.objects.all()

if filters:
if 'min_price' in filters:
queryset = queryset.filter(current_price__gte=filters['min_price'])
if 'max_price' in filters:
queryset = queryset.filter(current_price__lte=filters['max_price'])
if 'min_volume' in filters:
queryset = queryset.filter(volume_today__gte=filters['min_volume'])
if 'sector' in filters:
queryset = queryset.filter(sector__icontains=filters['sector'])

return list(queryset.only(
'ticker', 'company_name', 'current_price', 
'volume_today', 'market_cap', 'pe_ratio'
)[:limit])

return PerformanceOptimizer.get_cached_or_compute(
cache_key, compute_alerts, timeout=180
)

@staticmethod
def get_membership_analytics_optimized():
"""Efficiently calculate membership analytics"""
from .models import Membership
from emails.models import EmailSubscription
from django.contrib.auth.models import User

cache_key = "membership_analytics"

def compute_analytics():
# Use aggregation for efficiency
membership_counts = Membership.objects.filter(
is_active=True
).values('tier').annotate(count=Count('id'))

# Convert to dictionary
tier_counts = {item['tier']: item['count'] for item in membership_counts}

# Calculate revenue efficiently
tier_pricing = {
'free': 0.00,
'basic': 9.99,
'professional': 29.99,
'expert': 49.99
}

total_revenue = sum(
tier_counts.get(tier, 0) * price 
for tier, price in tier_pricing.items()
)

total_members = sum(tier_counts.values())

return {
'total_members': total_members,
'monthly_revenue': total_revenue,
'avg_spending_per_person': total_revenue / total_members if total_members > 0 else 0,
'membership_distribution': tier_counts,
'email_subscribers': EmailSubscription.objects.filter(is_active=True).count()
}

return PerformanceOptimizer.get_cached_or_compute(
cache_key, compute_analytics, timeout=900 # 15 minutes
)

# Pagination helper
class EfficientPagination:
"""Memory-efficient pagination"""

@staticmethod
def paginate_queryset(queryset, page=1, per_page=20):
"""Efficiently paginate querysets"""
offset = (page - 1) * per_page

# Use only() to fetch only needed fields
items = list(queryset[offset:offset + per_page])

# Get total count efficiently (cached)
cache_key = PerformanceOptimizer.get_cache_key(
"count", str(queryset.query)
)
total_count = cache.get(cache_key)
if total_count is None:
total_count = queryset.count()
cache.set(cache_key, total_count, 300)

return {
'items': items,
'total_count': total_count,
'page': page,
'per_page': per_page,
'total_pages': (total_count + per_page - 1) // per_page,
'has_next': offset + per_page < total_count,
'has_previous': page > 1
}

# Data serialization helper
class EfficientSerializer:
"""Efficient data serialization for APIs"""

@staticmethod
def serialize_stock_alert(stock):
"""Efficiently serialize stock alert"""
return {
'ticker': stock.ticker,
'company_name': stock.company_name,
'price': float(stock.current_price),
'volume': stock.volume_today,
'market_cap': stock.market_cap,
'pe_ratio': float(stock.pe_ratio) if stock.pe_ratio else None
}

@staticmethod
def serialize_portfolio(portfolio):
"""Efficiently serialize portfolio"""
return {
'id': portfolio.id,
'name': portfolio.name,
'total_value': float(portfolio.total_value),
'total_gain_loss': float(portfolio.total_gain_loss),
'total_gain_loss_percent': float(portfolio.total_gain_loss_percent),
'holdings_count': portfolio.holdings.count()
}

@staticmethod
def serialize_holding(holding):
"""Efficiently serialize portfolio holding"""
return {
'id': holding.id,
'ticker': holding.ticker,
'company_name': holding.company_name,
'shares': float(holding.shares),
'purchase_price': float(holding.purchase_price),
'current_price': float(holding.current_price),
'total_value': float(holding.total_value),
'gain_loss': float(holding.gain_loss),
'gain_loss_percent': float(holding.gain_loss_percent)
}

# Rate limiting and request optimization
class RequestOptimizer:
"""Optimize API requests and rate limiting"""

@staticmethod
def check_rate_limit(user, endpoint, limit_per_hour=100):
"""Efficient rate limiting"""
cache_key = PerformanceOptimizer.get_cache_key(
"rate_limit", user.id, endpoint, timezone.now().hour
)

current_count = cache.get(cache_key, 0)
if current_count >= limit_per_hour:
return False, limit_per_hour - current_count

cache.set(cache_key, current_count + 1, 3600) # 1 hour
return True, limit_per_hour - current_count - 1

@staticmethod
def batch_stock_updates(tickers, batch_size=10):
"""Efficiently update multiple stocks in batches"""
import yfinance as yf
from .models import StockAlert

updated_count = 0

# Process in batches to avoid memory issues
for i in range(0, len(tickers), batch_size):
batch_tickers = tickers[i:i + batch_size]

try:
# Fetch data for multiple tickers at once
data = yf.download(
' '.join(batch_tickers),
period="1d",
group_by='ticker'
)

# Bulk update in database
updates = []
for ticker in batch_tickers:
try:
if len(batch_tickers) > 1:
ticker_data = data[ticker]
else:
ticker_data = data

current_price = ticker_data['Close'].iloc[-1]
volume = ticker_data['Volume'].iloc[-1]

updates.append(StockAlert(
ticker=ticker,
current_price=current_price,
volume_today=volume,
last_update=timezone.now()
))

except (KeyError, IndexError):
continue

# Bulk update
if updates:
StockAlert.objects.bulk_update(
updates, 
['current_price', 'volume_today', 'last_update'],
batch_size=batch_size
)
updated_count += len(updates)

except Exception:
continue

return updated_count

# Memory optimization
class MemoryOptimizer:
"""Memory usage optimization"""

@staticmethod
def clear_expired_cache():
"""Clear expired cache entries"""
# Django cache handles this automatically, but we can add custom logic
expired_keys = []

# Clear old technical indicators
from .models import TechnicalIndicator
old_indicators = TechnicalIndicator.objects.filter(
calculated_at__lt=timezone.now() - timedelta(hours=6)
)
old_indicators.delete()

return len(expired_keys)

@staticmethod
def optimize_queryset_memory(queryset, chunk_size=1000):
"""Process large querysets in memory-efficient chunks"""
for chunk in queryset.iterator(chunk_size=chunk_size):
yield chunk
