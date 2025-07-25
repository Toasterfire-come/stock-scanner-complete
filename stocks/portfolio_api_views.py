"""
Portfolio Tracker API Views
Comprehensive portfolio management functionality
"""

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Avg, Count
from django.utils import timezone
from datetime import datetime, timedelta
import json
import yfinance as yf

from django.contrib.auth.models import User
from .models import Portfolio, PortfolioHolding, Membership
from .performance_optimizations import OptimizedQueries, EfficientSerializer, PerformanceOptimizer

@require_http_methods(["GET"])
@login_required
def portfolio_list_api(request):
"""Get user's portfolios - OPTIMIZED"""
try:
# Use optimized query with caching
cache_key = PerformanceOptimizer.get_cache_key("portfolios", request.user.id)

def compute_portfolios():
portfolios = Portfolio.objects.filter(
user=request.user, 
is_active=True
).prefetch_related('holdings').only(
'id', 'name', 'description', 'created_at', 'updated_at'
)

return [EfficientSerializer.serialize_portfolio(p) for p in portfolios]

portfolio_data = PerformanceOptimizer.get_cached_or_compute(
cache_key, compute_portfolios, timeout=300
)

return JsonResponse({
'success': True,
'portfolios': portfolio_data,
'cached': True
})

except Exception as e:
return JsonResponse({
'success': False,
'error': str(e)
}, status=500)

@require_http_methods(["POST"])
@csrf_exempt
@login_required
def portfolio_create_api(request):
"""Create new portfolio"""
try:
data = json.loads(request.body)

portfolio = Portfolio.objects.create(
user=request.user,
name=data.get('name', 'My Portfolio'),
description=data.get('description', '')
)

return JsonResponse({
'success': True,
'portfolio': {
'id': portfolio.id,
'name': portfolio.name,
'description': portfolio.description,
'total_value': 0.0,
'total_gain_loss': 0.0,
'total_gain_loss_percent': 0.0,
'holdings_count': 0
}
})

except Exception as e:
return JsonResponse({
'success': False,
'error': str(e)
}, status=500)

@require_http_methods(["GET"])
@login_required
def portfolio_detail_api(request, portfolio_id):
"""Get detailed portfolio information"""
try:
portfolio = Portfolio.objects.get(id=portfolio_id, user=request.user)

holdings_data = []
for holding in portfolio.holdings.all():
# Update current price
try:
ticker_data = yf.Ticker(holding.ticker)
current_price = ticker_data.history(period="1d")['Close'].iloc[-1]
holding.current_price = current_price
holding.save()
except:
pass # Use existing price if update fails

holdings_data.append({
'id': holding.id,
'ticker': holding.ticker,
'company_name': holding.company_name,
'shares': float(holding.shares),
'purchase_price': float(holding.purchase_price),
'current_price': float(holding.current_price),
'purchase_date': holding.purchase_date.isoformat(),
'total_cost': float(holding.total_cost),
'total_value': float(holding.total_value),
'gain_loss': float(holding.gain_loss),
'gain_loss_percent': float(holding.gain_loss_percent),
'last_updated': holding.last_updated.isoformat()
})

return JsonResponse({
'success': True,
'portfolio': {
'id': portfolio.id,
'name': portfolio.name,
'description': portfolio.description,
'total_value': float(portfolio.total_value),
'total_gain_loss': float(portfolio.total_gain_loss),
'total_gain_loss_percent': float(portfolio.total_gain_loss_percent),
'holdings': holdings_data
}
})

except Portfolio.DoesNotExist:
return JsonResponse({
'success': False,
'error': 'Portfolio not found'
}, status=404)
except Exception as e:
return JsonResponse({
'success': False,
'error': str(e)
}, status=500)

@require_http_methods(["POST"])
@csrf_exempt
@login_required
def portfolio_add_holding_api(request, portfolio_id):
"""Add stock holding to portfolio"""
try:
# Check membership usage limits
membership = request.user.membership
if not membership.can_make_lookup():
return JsonResponse({
'success': False,
'error': 'Monthly lookup limit reached. Please upgrade your plan.',
'limit_reached': True
}, status=403)

portfolio = Portfolio.objects.get(id=portfolio_id, user=request.user)
data = json.loads(request.body)

ticker = data.get('ticker', '').upper()
shares = float(data.get('shares', 0))
purchase_price = float(data.get('purchase_price', 0))
purchase_date = datetime.strptime(data.get('purchase_date'), '%Y-%m-%d').date()

# Get company name and current price
try:
ticker_data = yf.Ticker(ticker)
info = ticker_data.info
current_price = ticker_data.history(period="1d")['Close'].iloc[-1]
company_name = info.get('longName', ticker)

# Increment usage
membership.monthly_lookups_used += 1
membership.save()

except Exception as e:
return JsonResponse({
'success': False,
'error': f'Unable to fetch data for ticker {ticker}'
}, status=400)

# Create or update holding
holding, created = PortfolioHolding.objects.get_or_create(
portfolio=portfolio,
ticker=ticker,
defaults={
'company_name': company_name,
'shares': shares,
'purchase_price': purchase_price,
'purchase_date': purchase_date,
'current_price': current_price
}
)

if not created:
# Update existing holding (average cost)
total_shares = holding.shares + shares
total_cost = (holding.shares * holding.purchase_price) + (shares * purchase_price)
holding.shares = total_shares
holding.purchase_price = total_cost / total_shares
holding.current_price = current_price
holding.save()

return JsonResponse({
'success': True,
'holding': {
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
})

except Portfolio.DoesNotExist:
return JsonResponse({
'success': False,
'error': 'Portfolio not found'
}, status=404)
except Exception as e:
return JsonResponse({
'success': False,
'error': str(e)
}, status=500)
