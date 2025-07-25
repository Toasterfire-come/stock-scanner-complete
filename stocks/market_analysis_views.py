"""
Market Analysis API Views
Comprehensive market analysis and technical indicators
"""

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Avg, Count
from django.utils import timezone
from datetime import datetime, timedelta
import json
import yfinance as yf
import numpy as np

from django.contrib.auth.models import User
from .models import MarketAnalysis, TechnicalIndicator, Membership

@require_http_methods(["GET"])
def market_analysis_list_api(request):
"""Get market analysis articles"""
try:
analysis_type = request.GET.get('type', '')
sector = request.GET.get('sector', '')

analyses = MarketAnalysis.objects.all()

# Filter by type if specified
if analysis_type:
analyses = analyses.filter(analysis_type=analysis_type)

# Filter by sector if specified
if sector:
analyses = analyses.filter(sector__icontains=sector)

# Filter premium content based on user membership
user = request.user
if not user.is_authenticated or user.membership.tier in ['free', 'basic']:
analyses = analyses.filter(is_premium=False)

# Paginate results
analyses = analyses[:20]

analysis_data = []
for analysis in analyses:
analysis_data.append({
'id': analysis.id,
'title': analysis.title,
'content': analysis.content[:200] + '...' if len(analysis.content) > 200 else analysis.content,
'analysis_type': analysis.analysis_type,
'analysis_type_display': analysis.get_analysis_type_display(),
'tickers': analysis.tickers.split(',') if analysis.tickers else [],
'sector': analysis.sector,
'author': analysis.author.username,
'is_premium': analysis.is_premium,
'views': analysis.views,
'created_at': analysis.created_at.isoformat()
})

return JsonResponse({
'success': True,
'analyses': analysis_data
})

except Exception as e:
return JsonResponse({
'success': False,
'error': str(e)
}, status=500)

@require_http_methods(["GET"])
def market_analysis_detail_api(request, analysis_id):
"""Get detailed market analysis"""
try:
analysis = MarketAnalysis.objects.get(id=analysis_id)

# Check premium access
user = request.user
if analysis.is_premium:
if not user.is_authenticated or user.membership.tier in ['free', 'basic']:
return JsonResponse({
'success': False,
'error': 'Premium membership required',
'premium_required': True
}, status=403)

# Increment view count
analysis.increment_views()

return JsonResponse({
'success': True,
'analysis': {
'id': analysis.id,
'title': analysis.title,
'content': analysis.content,
'analysis_type': analysis.analysis_type,
'analysis_type_display': analysis.get_analysis_type_display(),
'tickers': analysis.tickers.split(',') if analysis.tickers else [],
'sector': analysis.sector,
'author': analysis.author.username,
'is_premium': analysis.is_premium,
'views': analysis.views,
'created_at': analysis.created_at.isoformat(),
'updated_at': analysis.updated_at.isoformat()
}
})

except MarketAnalysis.DoesNotExist:
return JsonResponse({
'success': False,
'error': 'Analysis not found'
}, status=404)
except Exception as e:
return JsonResponse({
'success': False,
'error': str(e)
}, status=500)

@require_http_methods(["GET"])
@login_required
def technical_indicators_api(request, ticker):
"""Get technical indicators for a stock"""
try:
# Check membership usage limits
membership = request.user.membership
if not membership.can_make_lookup():
return JsonResponse({
'success': False,
'error': 'Monthly lookup limit reached. Please upgrade your plan.',
'limit_reached': True
}, status=403)

ticker = ticker.upper()

# Get or calculate technical indicators
indicators = TechnicalIndicator.objects.filter(ticker=ticker)

# If indicators are old or don't exist, recalculate
if not indicators.exists() or indicators.first().calculated_at < timezone.now() - timedelta(hours=1):
# Calculate new indicators
try:
ticker_data = yf.Ticker(ticker)
hist = ticker_data.history(period="1y")

if hist.empty:
return JsonResponse({
'success': False,
'error': f'No data available for ticker {ticker}'
}, status=400)

# Calculate various technical indicators
close_prices = hist['Close']

# Simple Moving Averages
sma_20 = close_prices.rolling(window=20).mean().iloc[-1]
sma_50 = close_prices.rolling(window=50).mean().iloc[-1]
sma_200 = close_prices.rolling(window=200).mean().iloc[-1]

# Exponential Moving Averages
ema_12 = close_prices.ewm(span=12).mean().iloc[-1]
ema_26 = close_prices.ewm(span=26).mean().iloc[-1]

# RSI
delta = close_prices.diff()
gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
rs = gain / loss
rsi = 100 - (100 / (1 + rs)).iloc[-1]

# MACD
macd = ema_12 - ema_26

# Bollinger Bands
sma_20_series = close_prices.rolling(window=20).mean()
std_20 = close_prices.rolling(window=20).std()
bollinger_upper = (sma_20_series + (std_20 * 2)).iloc[-1]
bollinger_lower = (sma_20_series - (std_20 * 2)).iloc[-1]

# Current price
current_price = close_prices.iloc[-1]

# Determine signals
def get_signal(current, sma):
if current > sma * 1.02:
return 'buy'
elif current < sma * 0.98:
return 'sell'
else:
return 'hold'

# Clear old indicators
TechnicalIndicator.objects.filter(ticker=ticker).delete()

# Create new indicators
indicator_data = [
('sma_20', sma_20, get_signal(current_price, sma_20)),
('sma_50', sma_50, get_signal(current_price, sma_50)),
('sma_200', sma_200, get_signal(current_price, sma_200)),
('ema_12', ema_12, get_signal(current_price, ema_12)),
('ema_26', ema_26, get_signal(current_price, ema_26)),
('rsi', rsi, 'buy' if rsi < 30 else 'sell' if rsi > 70 else 'hold'),
('macd', macd, 'buy' if macd > 0 else 'sell'),
('bollinger_upper', bollinger_upper, 'sell' if current_price > bollinger_upper else 'neutral'),
('bollinger_lower', bollinger_lower, 'buy' if current_price < bollinger_lower else 'neutral'),
]

for indicator_type, value, signal in indicator_data:
TechnicalIndicator.objects.create(
ticker=ticker,
indicator_type=indicator_type,
value=value,
signal=signal,
confidence=75 # Default confidence
)

# Increment usage
membership.monthly_lookups_used += 1
membership.save()

except Exception as calc_error:
return JsonResponse({
'success': False,
'error': f'Error calculating indicators: {str(calc_error)}'
}, status=500)

# Get updated indicators
indicators = TechnicalIndicator.objects.filter(ticker=ticker)

indicator_data = []
for indicator in indicators:
indicator_data.append({
'indicator_type': indicator.indicator_type,
'indicator_name': indicator.get_indicator_type_display(),
'value': float(indicator.value),
'signal': indicator.signal,
'signal_display': indicator.get_signal_display(),
'confidence': indicator.confidence,
'calculated_at': indicator.calculated_at.isoformat()
})

return JsonResponse({
'success': True,
'ticker': ticker,
'indicators': indicator_data
})

except Exception as e:
return JsonResponse({
'success': False,
'error': str(e)
}, status=500)

@require_http_methods(["GET"])
def market_overview_api(request):
"""Get market overview and top movers"""
try:
# Major market indices
indices = ['SPY', 'QQQ', 'DIA', 'IWM']
index_data = []

for index in indices:
try:
ticker_data = yf.Ticker(index)
hist = ticker_data.history(period="2d")
if len(hist) >= 2:
current = hist['Close'].iloc[-1]
previous = hist['Close'].iloc[-2]
change = current - previous
change_percent = (change / previous) * 100

index_data.append({
'symbol': index,
'name': {
'SPY': 'S&P 500',
'QQQ': 'NASDAQ',
'DIA': 'Dow Jones',
'IWM': 'Russell 2000'
}.get(index, index),
'price': round(current, 2),
'change': round(change, 2),
'change_percent': round(change_percent, 2)
})
except:
continue

# Top gainers and losers (simulated data for demo)
top_gainers = [
{'symbol': 'NVDA', 'name': 'NVIDIA Corp', 'price': 445.50, 'change_percent': 8.5},
{'symbol': 'AMD', 'name': 'Advanced Micro Devices', 'price': 142.30, 'change_percent': 6.2},
{'symbol': 'TSLA', 'name': 'Tesla Inc', 'price': 248.75, 'change_percent': 5.8},
]

top_losers = [
{'symbol': 'NFLX', 'name': 'Netflix Inc', 'price': 485.20, 'change_percent': -4.2},
{'symbol': 'META', 'name': 'Meta Platforms', 'price': 298.45, 'change_percent': -3.8},
{'symbol': 'GOOGL', 'name': 'Alphabet Inc', 'price': 132.85, 'change_percent': -2.9},
]

return JsonResponse({
'success': True,
'market_overview': {
'indices': index_data,
'top_gainers': top_gainers,
'top_losers': top_losers,
'last_updated': timezone.now().isoformat()
}
})

except Exception as e:
return JsonResponse({
'success': False,
'error': str(e)
}, status=500)

@require_http_methods(["GET"])
def sector_analysis_api(request):
"""Get sector performance analysis"""
try:
# Sector ETFs and their performance
sectors = {
'XLK': 'Technology',
'XLF': 'Financial',
'XLV': 'Healthcare',
'XLE': 'Energy',
'XLI': 'Industrial',
'XLY': 'Consumer Discretionary',
'XLP': 'Consumer Staples',
'XLB': 'Materials',
'XLU': 'Utilities',
'XLRE': 'Real Estate'
}

sector_data = []
for etf, sector_name in sectors.items():
try:
ticker_data = yf.Ticker(etf)
hist = ticker_data.history(period="5d")
if len(hist) >= 2:
current = hist['Close'].iloc[-1]
week_ago = hist['Close'].iloc[0]
change_percent = ((current - week_ago) / week_ago) * 100

sector_data.append({
'etf': etf,
'sector': sector_name,
'price': round(current, 2),
'change_percent_5d': round(change_percent, 2),
'trend': 'up' if change_percent > 0 else 'down'
})
except:
continue

# Sort by performance
sector_data.sort(key=lambda x: x['change_percent_5d'], reverse=True)

return JsonResponse({
'success': True,
'sectors': sector_data,
'last_updated': timezone.now().isoformat()
})

except Exception as e:
return JsonResponse({
'success': False,
'error': str(e)
}, status=500)
