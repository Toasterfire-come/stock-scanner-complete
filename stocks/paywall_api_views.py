"""
Django API Views with WordPress Paywall Integration
Provides tiered access to stock data based on WordPress user subscription levels
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.cache import cache
from django.utils import timezone
from datetime import datetime, timedelta
import json
import logging
import requests
from urllib.parse import urljoin

from .models import StockAlert
from emails.models import EmailSubscription
from .api_views import (
calculate_price_change_percent, 
calculate_volume_ratio, 
calculate_technical_rating
)

logger = logging.getLogger(__name__)

class PaywallIntegration:
"""WordPress Paywall Integration Helper"""

def __init__(self, wordpress_url=None, api_key=None):
self.wordpress_url = wordpress_url
self.api_key = api_key

def verify_user_access(self, user_token, required_level='basic'):
"""
Verify user access level with Paid Membership Pro API

Args:
user_token: WordPress user token/session
required_level: 'free', 'basic', 'premium', 'pro'

Returns:
dict: {'has_access': bool, 'user_level': str, 'expires': datetime}
"""
if not self.wordpress_url:
# No paywall configured - allow access
return {'has_access': True, 'user_level': 'free', 'expires': None}

try:
# Call Paid Membership Pro REST API
api_url = urljoin(self.wordpress_url, '/wp-json/pmp/v1/member/verify')

headers = {
'Authorization': f'Bearer {user_token}',
'Content-Type': 'application/json'
}

if self.api_key:
headers['X-API-Key'] = self.api_key

response = requests.get(api_url, headers=headers, timeout=10)

if response.status_code == 200:
data = response.json()

# Paid Membership Pro specific fields
membership_level = data.get('membership_level', {})
level_id = membership_level.get('id', 0)
level_name = membership_level.get('name', 'free').lower()

# Map PMP level IDs to our access levels
pmp_level_mapping = {
0: 'free', # No membership
1: 'basic', # Basic membership
2: 'premium', # Premium membership 
3: 'pro', # Pro membership
4: 'pro', # VIP membership (treat as pro)
}

# Alternative: map by level name if ID mapping doesn't work
name_mapping = {
'free': 'free',
'basic': 'basic',
'starter': 'basic',
'premium': 'premium',
'pro': 'pro',
'professional': 'pro',
'vip': 'pro',
'enterprise': 'pro'
}

# Determine user level
user_level = pmp_level_mapping.get(level_id)
if not user_level:
user_level = name_mapping.get(level_name, 'free')

# Get expiration date
expires = data.get('expires_at') or membership_level.get('enddate')

# Check if membership is active
is_active = data.get('is_active', True)
if not is_active:
user_level = 'free'

# Define access hierarchy
access_levels = {
'free': 0,
'basic': 1, 
'premium': 2,
'pro': 3
}

required_access = access_levels.get(required_level, 0)
user_access = access_levels.get(user_level, 0)

has_access = user_access >= required_access

return {
'has_access': has_access,
'user_level': user_level,
'expires': expires,
'required_level': required_level,
'membership_id': level_id,
'membership_name': level_name,
'is_active': is_active
}

else:
# API error - try alternative PMP endpoint
return self._try_alternative_pmp_verification(user_token, required_level)

except Exception as e:
logger.error(f"PMP verification error: {e}")
# On error, default to no access for security
return {'has_access': False, 'user_level': 'free', 'expires': None}

def _try_alternative_pmp_verification(self, user_token, required_level):
"""
Alternative verification method for Paid Membership Pro
Uses WordPress user meta to check membership
"""
try:
# Try WordPress user endpoint with PMP meta
api_url = urljoin(self.wordpress_url, '/wp-json/wp/v2/users/me')

headers = {
'Authorization': f'Bearer {user_token}',
'Content-Type': 'application/json'
}

response = requests.get(api_url, headers=headers, timeout=10)

if response.status_code == 200:
user_data = response.json()

# Check user meta for PMP membership
meta = user_data.get('meta', {})
pmp_membership_level = meta.get('pmp_membership_level', [0])

if isinstance(pmp_membership_level, list):
level_id = pmp_membership_level[0] if pmp_membership_level else 0
else:
level_id = pmp_membership_level

# Map level ID to access level
level_mapping = {
0: 'free',
1: 'basic',
2: 'premium', 
3: 'pro'
}

user_level = level_mapping.get(int(level_id), 'free')

# Define access hierarchy
access_levels = {
'free': 0,
'basic': 1,
'premium': 2,
'pro': 3
}

required_access = access_levels.get(required_level, 0)
user_access = access_levels.get(user_level, 0)

has_access = user_access >= required_access

return {
'has_access': has_access,
'user_level': user_level,
'expires': None,
'required_level': required_level,
'membership_id': level_id
}

return {'has_access': False, 'user_level': 'free', 'expires': None}

except Exception as e:
logger.error(f"Alternative PMP verification error: {e}")
return {'has_access': False, 'user_level': 'free', 'expires': None}

def get_paywall_integration():
"""Get configured paywall integration instance"""
# These can be set via Django settings or environment variables
from django.conf import settings

wordpress_url = getattr(settings, 'WORDPRESS_PAYWALL_URL', None)
api_key = getattr(settings, 'WORDPRESS_PAYWALL_API_KEY', None)

return PaywallIntegration(wordpress_url, api_key)

@api_view(['GET'])
@permission_classes([AllowAny])
def protected_stock_list_api(request):
"""
Get list of stocks with paywall protection

Access Levels:
- Free: Basic ticker, price, change (limited to 10 stocks)
- Basic: + Volume, Market Cap (limited to 50 stocks) 
- Premium: + Technical indicators, full data (limited to 200 stocks)
- Pro: Unlimited access, real-time updates, advanced metrics
"""
try:
# Get user token from header
user_token = request.headers.get('X-WP-Token') or request.GET.get('wp_token')

# Verify access level
paywall = get_paywall_integration()
access_info = paywall.verify_user_access(user_token, 'free')

user_level = access_info['user_level']

# Define limits and fields based on subscription level
level_config = {
'free': {
'limit': 10,
'fields': ['ticker', 'company_name', 'current_price', 'price_change_today', 'price_change_percent'],
'cache_time': 300 # 5 minutes
},
'basic': {
'limit': 50, 
'fields': ['ticker', 'company_name', 'current_price', 'price_change_today', 'price_change_percent', 
'volume_today', 'market_cap', 'last_update'],
'cache_time': 120 # 2 minutes
},
'premium': {
'limit': 200,
'fields': ['ticker', 'company_name', 'current_price', 'price_change_today', 'price_change_percent',
'volume_today', 'average_volume', 'market_cap', 'pe_ratio', 'dvav', 'dvsa', 
'technical_rating', 'last_update', 'note'],
'cache_time': 60 # 1 minute
},
'pro': {
'limit': None, # Unlimited
'fields': 'all', # All fields
'cache_time': 30 # 30 seconds - real-time
}
}

config = level_config.get(user_level, level_config['free'])

# Get request parameters
limit = int(request.GET.get('limit', config['limit'] or 50))
search = request.GET.get('search', '').strip()
category = request.GET.get('category', '').strip()

# Apply subscription limits
if config['limit'] and limit > config['limit']:
limit = config['limit']

# Check cache first
cache_key = f"stock_list_{user_level}_{limit}_{search}_{category}"
cached_data = cache.get(cache_key)

if cached_data:
# Add subscription info to cached response
cached_data['subscription'] = {
'level': user_level,
'expires': access_info.get('expires'),
'limits': {
'max_stocks': config['limit'],
'cache_time': config['cache_time']
}
}
return Response(cached_data)

# Build queryset
queryset = StockAlert.objects.all()

if search:
from django.db.models import Q
queryset = queryset.filter(
Q(ticker__icontains=search) | Q(company_name__icontains=search)
)

if category == 'gainers':
queryset = queryset.filter(price_change_today__gt=0).order_by('-price_change_today')
elif category == 'losers':
queryset = queryset.filter(price_change_today__lt=0).order_by('price_change_today')
elif category == 'high_volume':
queryset = queryset.order_by('-volume_today')
else:
queryset = queryset.order_by('-last_update')

# Apply limit
if limit:
stocks = queryset[:limit]
else:
stocks = queryset

# Format data based on subscription level
stock_data = []
for stock in stocks:
stock_info = format_stock_data(stock, config['fields'])
stock_data.append(stock_info)

response_data = {
'success': True,
'count': len(stock_data),
'data': stock_data,
'subscription': {
'level': user_level,
'has_access': True,
'expires': access_info.get('expires'),
'limits': {
'max_stocks': config['limit'],
'cache_time': config['cache_time'],
'available_fields': config['fields'] if config['fields'] != 'all' else 'unlimited'
}
},
'timestamp': timezone.now().isoformat()
}

# Cache the response
cache.set(cache_key, response_data, config['cache_time'])

return Response(response_data)

except Exception as e:
logger.error(f"Error in protected_stock_list_api: {e}")
return Response({
'success': False,
'error': str(e),
'subscription': {'level': 'free', 'has_access': False}
}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
def protected_stock_detail_api(request, ticker):
"""
Get detailed stock information with paywall protection

Access Levels:
- Free: Basic info only
- Basic: + Financial metrics
- Premium: + Technical analysis 
- Pro: + Advanced analytics, alerts, predictions
"""
try:
user_token = request.headers.get('X-WP-Token') or request.GET.get('wp_token')

# Verify access
paywall = get_paywall_integration()
access_info = paywall.verify_user_access(user_token, 'free')

user_level = access_info['user_level']

ticker = ticker.upper()

# Get stock from database
try:
stock = StockAlert.objects.get(ticker=ticker)
except StockAlert.DoesNotExist:
return Response({
'success': False,
'error': f'Stock {ticker} not found',
'subscription': {'level': user_level, 'has_access': False}
}, status=status.HTTP_404_NOT_FOUND)

# Define access levels for detailed data
level_fields = {
'free': ['ticker', 'company_name', 'current_price', 'price_change_today', 'price_change_percent'],
'basic': ['ticker', 'company_name', 'current_price', 'price_change_today', 'price_change_percent',
'volume_today', 'market_cap', 'pe_ratio', 'last_update'],
'premium': ['ticker', 'company_name', 'current_price', 'price_change_today', 'price_change_percent',
'volume_today', 'average_volume', 'market_cap', 'pe_ratio', 'dvav', 'dvsa', 
'fifty_two_week_high', 'fifty_two_week_low', 'beta', 'rsi', 'technical_rating',
'volume_ratio', 'price_near_high', 'price_near_low', 'last_update', 'note'],
'pro': 'all' # All fields plus advanced calculations
}

allowed_fields = level_fields.get(user_level, level_fields['free'])

# Format stock data
stock_data = format_stock_data(stock, allowed_fields)

# Add pro-level features
if user_level == 'pro':
stock_data.update({
'ai_sentiment': calculate_ai_sentiment(stock),
'price_prediction': calculate_price_prediction(stock),
'risk_score': calculate_risk_score(stock),
'trading_signals': get_trading_signals(stock),
'related_stocks': get_related_stocks(stock.ticker)[:5]
})

response_data = {
'success': True,
'data': stock_data,
'subscription': {
'level': user_level,
'has_access': True,
'expires': access_info.get('expires'),
'upgrade_benefits': get_upgrade_benefits(user_level)
},
'timestamp': timezone.now().isoformat()
}

return Response(response_data)

except Exception as e:
logger.error(f"Error in protected_stock_detail_api for {ticker}: {e}")
return Response({
'success': False,
'error': str(e),
'subscription': {'level': 'free', 'has_access': False}
}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
def premium_market_analytics_api(request):
"""
Advanced market analytics - Premium/Pro only
"""
try:
user_token = request.headers.get('X-WP-Token') or request.GET.get('wp_token')

paywall = get_paywall_integration()
access_info = paywall.verify_user_access(user_token, 'premium')

if not access_info['has_access']:
return Response({
'success': False,
'error': 'Premium subscription required',
'subscription': {
'level': access_info['user_level'],
'has_access': False,
'required_level': 'premium',
'upgrade_url': '/pricing/'
}
}, status=status.HTTP_403_FORBIDDEN)

# Premium analytics
analytics_data = {
'market_sentiment': calculate_market_sentiment(),
'sector_performance': get_sector_performance(),
'volatility_index': calculate_volatility_index(),
'momentum_leaders': get_momentum_leaders(10),
'technical_breakouts': get_technical_breakouts(),
'earnings_calendar': get_upcoming_earnings(),
'insider_activity': get_insider_activity() if access_info['user_level'] == 'pro' else None
}

return Response({
'success': True,
'data': analytics_data,
'subscription': {
'level': access_info['user_level'],
'has_access': True,
'expires': access_info.get('expires')
},
'timestamp': timezone.now().isoformat()
})

except Exception as e:
logger.error(f"Error in premium_market_analytics_api: {e}")
return Response({
'success': False,
'error': str(e)
}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_exempt
def premium_stock_alerts_api(request):
"""
Create custom stock alerts - Premium/Pro only
"""
try:
user_token = request.headers.get('X-WP-Token') or request.GET.get('wp_token')

paywall = get_paywall_integration()
access_info = paywall.verify_user_access(user_token, 'premium')

if not access_info['has_access']:
return Response({
'success': False,
'error': 'Premium subscription required for custom alerts',
'subscription': {
'level': access_info['user_level'],
'has_access': False,
'required_level': 'premium'
}
}, status=status.HTTP_403_FORBIDDEN)

data = json.loads(request.body)

# Create custom alert logic here
alert_created = create_custom_alert(data, access_info['user_level'])

return Response({
'success': True,
'message': 'Custom alert created successfully',
'alert_id': alert_created['id'],
'subscription': {
'level': access_info['user_level'],
'has_access': True
}
})

except Exception as e:
logger.error(f"Error in premium_stock_alerts_api: {e}")
return Response({
'success': False,
'error': str(e)
}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Helper functions

def format_stock_data(stock, allowed_fields):
"""Format stock data based on allowed fields for subscription level"""
base_data = {
'ticker': stock.ticker,
'company_name': stock.company_name,
'current_price': float(stock.current_price) if stock.current_price else 0,
'price_change_today': float(stock.price_change_today) if stock.price_change_today else 0,
'price_change_percent': calculate_price_change_percent(stock),
'volume_today': int(stock.volume_today) if stock.volume_today else 0,
'average_volume': int(stock.average_volume) if stock.average_volume else 0,
'dvav': float(stock.dvav) if stock.dvav else 0,
'dvsa': float(stock.dvsa) if stock.dvsa else 0,
'pe_ratio': float(stock.pe_ratio) if stock.pe_ratio else 0,
'market_cap': int(stock.market_cap) if stock.market_cap else 0,
'shares_outstanding': int(stock.shares_outstanding) if stock.shares_outstanding else 0,
'dividend_yield': float(stock.dividend_yield) if stock.dividend_yield else 0,
'fifty_two_week_high': float(stock.fifty_two_week_high) if stock.fifty_two_week_high else 0,
'fifty_two_week_low': float(stock.fifty_two_week_low) if stock.fifty_two_week_low else 0,
'beta': float(stock.beta) if stock.beta else 0,
'rsi': float(stock.rsi) if stock.rsi else 0,
'last_update': stock.last_update.isoformat() if stock.last_update else None,
'note': stock.note or '',
'technical_rating': calculate_technical_rating(stock),
'volume_ratio': calculate_volume_ratio(stock),
'wordpress_url': f"/stock/{stock.ticker.lower()}/"
}

if allowed_fields == 'all':
return base_data

# Filter fields based on subscription
filtered_data = {}
for field in allowed_fields:
if field in base_data:
filtered_data[field] = base_data[field]

return filtered_data

def get_upgrade_benefits(current_level):
"""Get upgrade benefits for current subscription level"""
benefits = {
'free': {
'upgrade_to': 'basic',
'benefits': [
'Access to 50 stocks (vs 10)',
'Volume and market cap data',
'Faster data updates (2min vs 5min)',
'Email support'
]
},
'basic': {
'upgrade_to': 'premium', 
'benefits': [
'Access to 200 stocks (vs 50)',
'Technical indicators (RSI, DVAV, DVSA)',
'Trading signals and ratings',
'Real-time alerts',
'Priority support'
]
},
'premium': {
'upgrade_to': 'pro',
'benefits': [
'Unlimited stock access',
'AI sentiment analysis',
'Price predictions',
'Advanced analytics dashboard',
'Custom alerts',
'Insider trading data',
'API access',
'White-label options'
]
}
}

return benefits.get(current_level, {})

# Placeholder functions for advanced features
def calculate_ai_sentiment(stock):
"""Calculate AI sentiment score - placeholder"""
return {'score': 0.65, 'trend': 'bullish', 'confidence': 0.8}

def calculate_price_prediction(stock):
"""Calculate price prediction - placeholder"""
return {
'1_day': float(stock.current_price) * 1.02 if stock.current_price else 0,
'1_week': float(stock.current_price) * 1.05 if stock.current_price else 0,
'1_month': float(stock.current_price) * 1.12 if stock.current_price else 0
}

def calculate_risk_score(stock):
"""Calculate risk score - placeholder"""
return {'score': 3.2, 'level': 'moderate', 'factors': ['volatility', 'volume']}

def get_trading_signals(stock):
"""Get trading signals - placeholder"""
return {
'signal': 'BUY',
'strength': 0.75,
'indicators': ['RSI_oversold', 'volume_breakout']
}

def get_related_stocks(ticker):
"""Get related stocks - placeholder"""
return ['AAPL', 'MSFT', 'GOOGL'][:3]

def calculate_market_sentiment():
"""Calculate overall market sentiment"""
return {'score': 0.6, 'trend': 'bullish'}

def get_sector_performance():
"""Get sector performance data"""
return {'technology': 2.1, 'healthcare': 1.5, 'finance': -0.8}

def calculate_volatility_index():
"""Calculate market volatility index"""
return {'vix': 18.5, 'trend': 'decreasing'}

def get_momentum_leaders(count):
"""Get momentum leaders"""
return []

def get_technical_breakouts():
"""Get technical breakouts"""
return []

def get_upcoming_earnings():
"""Get upcoming earnings"""
return []

def get_insider_activity():
"""Get insider trading activity"""
return []

def create_custom_alert(data, user_level):
"""Create custom alert"""
return {'id': 'alert_123', 'status': 'created'}