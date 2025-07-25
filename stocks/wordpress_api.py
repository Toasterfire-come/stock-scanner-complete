"""
WordPress Integration API Views
Provides clean, simple endpoints for WordPress consumption
"""

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from .models import Stock
import json
import logging

logger = logging.getLogger(__name__)

@csrf_exempt
@require_http_methods(["GET"])
def wordpress_stocks_api(request):
"""
WordPress-friendly stocks API endpoint
Returns stock data in a format optimized for WordPress consumption
"""
try:
# Get query parameters
limit = int(request.GET.get('limit', 50))
page = int(request.GET.get('page', 1))
sort_by = request.GET.get('sort', 'volume') # volume, price, change
search = request.GET.get('search', '')

# Base queryset
stocks = Stock.objects.all()

# Apply search filter
if search:
stocks = stocks.filter(ticker__icontains=search)

# Apply sorting
if sort_by == 'volume':
stocks = stocks.order_by('-volume')
elif sort_by == 'price':
stocks = stocks.order_by('-current_price')
elif sort_by == 'change':
stocks = stocks.order_by('-price_change_percent')
else:
stocks = stocks.order_by('-volume')

# Paginate results
paginator = Paginator(stocks, limit)
page_obj = paginator.get_page(page)

# Format data for WordPress
stock_data = []
for stock in page_obj:
try:
stock_data.append({
'ticker': stock.ticker,
'company_name': stock.company_name or stock.ticker,
'current_price': float(stock.current_price) if stock.current_price else 0.0,
'price_change': float(stock.price_change) if stock.price_change else 0.0,
'price_change_percent': float(stock.price_change_percent) if stock.price_change_percent else 0.0,
'volume': int(stock.volume) if stock.volume else 0,
'market_cap': float(stock.market_cap) if stock.market_cap else 0.0,
'pe_ratio': float(stock.pe_ratio) if stock.pe_ratio else 0.0,
'last_updated': stock.last_updated.isoformat() if stock.last_updated else None,
'formatted_price': f"${stock.current_price:.2f}" if stock.current_price else "$0.00",
'formatted_change': f"{stock.price_change_percent:+.2f}%" if stock.price_change_percent else "0.00%",
'formatted_volume': f"{stock.volume:,}" if stock.volume else "0",
})
except Exception as e:
logger.warning(f"Error formatting stock {stock.ticker}: {e}")
continue

response_data = {
'success': True,
'data': stock_data,
'pagination': {
'current_page': page,
'total_pages': paginator.num_pages,
'total_stocks': paginator.count,
'has_next': page_obj.has_next(),
'has_previous': page_obj.has_previous(),
},
'meta': {
'sort_by': sort_by,
'search': search,
'limit': limit,
'api_version': '1.0'
}
}

return JsonResponse(response_data)

except Exception as e:
logger.error(f"WordPress stocks API error: {e}")
return JsonResponse({
'success': False,
'error': 'Unable to fetch stock data',
'message': 'Please try again later'
}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def wordpress_news_api(request):
"""
WordPress-friendly news API endpoint
Returns news data in a format optimized for WordPress consumption
"""
try:
# Import here to avoid circular imports
from news.models import NewsArticle

# Get query parameters
limit = int(request.GET.get('limit', 20))
page = int(request.GET.get('page', 1))
sentiment = request.GET.get('sentiment', '') # A, B, C, D, F
ticker = request.GET.get('ticker', '')

# Base queryset
articles = NewsArticle.objects.all().order_by('-published_date')

# Apply filters
if sentiment:
articles = articles.filter(sentiment_grade=sentiment.upper())

if ticker:
articles = articles.filter(mentioned_tickers__icontains=ticker)

# Paginate results
paginator = Paginator(articles, limit)
page_obj = paginator.get_page(page)

# Format data for WordPress
news_data = []
for article in page_obj:
try:
news_data.append({
'id': article.id,
'title': article.title,
'summary': article.summary[:200] + '...' if len(article.summary) > 200 else article.summary,
'url': article.url,
'source': article.source.name if article.source else 'Unknown',
'published_date': article.published_date.isoformat() if article.published_date else None,
'sentiment_score': float(article.sentiment_score) if article.sentiment_score else 0.0,
'sentiment_grade': article.sentiment_grade or 'C',
'mentioned_tickers': article.mentioned_tickers.split(',') if article.mentioned_tickers else [],
'formatted_date': article.published_date.strftime('%B %d, %Y') if article.published_date else 'Unknown',
'sentiment_color': {
'A': 'green',
'B': 'lightgreen', 
'C': 'yellow',
'D': 'orange',
'F': 'red'
}.get(article.sentiment_grade, 'gray')
})
except Exception as e:
logger.warning(f"Error formatting article {article.id}: {e}")
continue

response_data = {
'success': True,
'data': news_data,
'pagination': {
'current_page': page,
'total_pages': paginator.num_pages,
'total_articles': paginator.count,
'has_next': page_obj.has_next(),
'has_previous': page_obj.has_previous(),
},
'meta': {
'sentiment_filter': sentiment,
'ticker_filter': ticker,
'limit': limit,
'api_version': '1.0'
}
}

return JsonResponse(response_data)

except Exception as e:
logger.error(f"WordPress news API error: {e}")
return JsonResponse({
'success': False,
'error': 'Unable to fetch news data',
'message': 'Please try again later'
}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def wordpress_status_api(request):
"""
WordPress-friendly status API endpoint
Returns system status for WordPress dashboard
"""
try:
from django.utils import timezone
from datetime import timedelta

# Get basic counts
total_stocks = Stock.objects.count()

# Try to get news count safely
try:
from news.models import NewsArticle
total_news = NewsArticle.objects.count()
recent_news = NewsArticle.objects.filter(
published_date__gte=timezone.now() - timedelta(days=7)
).count()
except:
total_news = 0
recent_news = 0

# Get stocks with recent updates
recent_stocks = Stock.objects.filter(
last_updated__gte=timezone.now() - timedelta(hours=24)
).count()

# Calculate data freshness
if total_stocks > 0:
data_freshness = (recent_stocks / total_stocks) * 100
else:
data_freshness = 0

response_data = {
'success': True,
'status': 'operational',
'data': {
'total_stocks': total_stocks,
'total_news': total_news,
'recent_news_7_days': recent_news,
'recent_stock_updates_24h': recent_stocks,
'data_freshness_percent': round(data_freshness, 2),
'last_updated': timezone.now().isoformat(),
'api_status': 'online',
'database_status': 'connected'
},
'meta': {
'api_version': '1.0',
'wordpress_compatible': True
}
}

return JsonResponse(response_data)

except Exception as e:
logger.error(f"WordPress status API error: {e}")
return JsonResponse({
'success': False,
'error': 'Unable to fetch status',
'message': str(e)
}, status=500)


@csrf_exempt 
@require_http_methods(["GET"])
def wordpress_stock_detail_api(request, ticker):
"""
WordPress-friendly individual stock detail API
"""
try:
stock = Stock.objects.get(ticker=ticker.upper())

stock_data = {
'success': True,
'data': {
'ticker': stock.ticker,
'company_name': stock.company_name or stock.ticker,
'current_price': float(stock.current_price) if stock.current_price else 0.0,
'price_change': float(stock.price_change) if stock.price_change else 0.0,
'price_change_percent': float(stock.price_change_percent) if stock.price_change_percent else 0.0,
'volume': int(stock.volume) if stock.volume else 0,
'market_cap': float(stock.market_cap) if stock.market_cap else 0.0,
'pe_ratio': float(stock.pe_ratio) if stock.pe_ratio else 0.0,
'last_updated': stock.last_updated.isoformat() if stock.last_updated else None,
'formatted_price': f"${stock.current_price:.2f}" if stock.current_price else "$0.00",
'formatted_change': f"{stock.price_change_percent:+.2f}%" if stock.price_change_percent else "0.00%",
'formatted_volume': f"{stock.volume:,}" if stock.volume else "0",
'formatted_market_cap': f"${stock.market_cap/1e9:.2f}B" if stock.market_cap and stock.market_cap > 1e9 else f"${stock.market_cap/1e6:.2f}M" if stock.market_cap else "N/A"
},
'meta': {
'api_version': '1.0'
}
}

return JsonResponse(stock_data)

except Stock.DoesNotExist:
return JsonResponse({
'success': False,
'error': 'Stock not found',
'message': f'No stock found with ticker {ticker}'
}, status=404)

except Exception as e:
logger.error(f"WordPress stock detail API error: {e}")
return JsonResponse({
'success': False,
'error': 'Unable to fetch stock details',
'message': 'Please try again later'
}, status=500)