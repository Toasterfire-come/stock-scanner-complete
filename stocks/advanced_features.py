"""
Advanced Features Implementation
- Regulatory Compliance & Security
- Tiered API Access with Usage Analytics
- Market Sentiment Analysis
- Comprehensive Portfolio Analytics
"""

import time
import json
import math
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q, Count, Sum, Avg, F, Max, Min
from django.utils import timezone
from django.core.cache import cache
from django.conf import settings
import yfinance as yf
import requests
from bs4 import BeautifulSoup
import re
from textblob import TextBlob

from django.contrib.auth.models import User
from .models import (
    StockAlert, Membership, Portfolio, PortfolioHolding,
    APIUsageTracking, MarketSentiment, PortfolioAnalytics,
    ComplianceLog, SecurityEvent
)

# ==================== MIDDLEWARE & DECORATORS ====================

def get_client_ip(request):
    """Get client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def track_api_usage(view_func):
    """Decorator to track API usage"""
    def wrapper(request, *args, **kwargs):
        start_time = time.time()
        
        # Execute the view
        response = view_func(request, *args, **kwargs)
        
        # Calculate response time
        response_time_ms = int((time.time() - start_time) * 1000)
        
        # Track usage if user is authenticated
        if request.user.is_authenticated:
            try:
                membership = request.user.membership
                
                APIUsageTracking.objects.create(
                    user=request.user,
                    endpoint=request.path,
                    method=request.method,
                    response_time_ms=response_time_ms,
                    status_code=response.status_code,
                    ip_address=get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT', ''),
                    membership_tier=membership.tier
                )
            except Exception as e:
                # Log error but don't break the request
                print(f"API tracking error: {e}")
        
        return response
    return wrapper



def log_compliance_action(user, action_type, description, request, risk_level='low'):
    """Log compliance action"""
    try:
        ComplianceLog.objects.create(
            user=user,
            action_type=action_type,
            description=description,
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            session_id=request.session.session_key or '',
            request_data={
                'path': request.path,
                'method': request.method,
                'timestamp': timezone.now().isoformat()
            },
            risk_level=risk_level
        )
    except Exception as e:
        print(f"Compliance logging error: {e}")

def detect_security_threats(request):
    """Basic security threat detection"""
    threats = []
    user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
    
    # Check for suspicious user agents
    suspicious_agents = ['bot', 'crawler', 'spider', 'scraper', 'hack']
    if any(agent in user_agent for agent in suspicious_agents):
        threats.append('suspicious_user_agent')
    
    # Check for SQL injection patterns
    query_string = request.META.get('QUERY_STRING', '').lower()
    sql_patterns = ['union', 'select', 'drop', 'insert', 'delete', '--', ';']
    if any(pattern in query_string for pattern in sql_patterns):
        threats.append('sql_injection_attempt')
    
    # Check for XSS patterns
    if '<script' in query_string or 'javascript:' in query_string:
        threats.append('xss_attempt')
    
    return threats

# ==================== API USAGE ANALYTICS ====================

@require_http_methods(["GET"])
@login_required
@track_api_usage
def api_usage_analytics(request):
    """Get detailed API usage analytics for user"""
    try:
        user = request.user
        
        # Get time range
        days = int(request.GET.get('days', 30))
        start_date = timezone.now() - timedelta(days=days)
        
        # Get usage data
        usage_data = APIUsageTracking.objects.filter(
            user=user,
            timestamp__gte=start_date
        )
        
        # Calculate metrics
        total_requests = usage_data.count()
        avg_response_time = usage_data.aggregate(Avg('response_time_ms'))['response_time_ms__avg'] or 0
        
        # Endpoint usage breakdown
        endpoint_usage = usage_data.values('endpoint').annotate(
            count=Count('id'),
            avg_response_time=Avg('response_time_ms')
        ).order_by('-count')
        
        # Daily usage trend
        daily_usage = usage_data.extra(
            select={'day': 'date(timestamp)'}
        ).values('day').annotate(
            requests=Count('id')
        ).order_by('day')
        
        # Error rate
        error_count = usage_data.filter(status_code__gte=400).count()
        error_rate = (error_count / total_requests * 100) if total_requests > 0 else 0
        
        # Tier limits and usage
        membership = user.membership
        tier_limits = {
            'free': 15,
            'basic': 100,
            'professional': 500,
            'expert': -1
        }
        
        current_limit = tier_limits.get(membership.tier, 15)
        usage_percentage = (membership.monthly_lookups_used / current_limit * 100) if current_limit > 0 else 0
        
        return JsonResponse({
            'success': True,
            'usage_analytics': {
                'period_days': days,
                'total_requests': total_requests,
                'avg_response_time_ms': round(avg_response_time, 2),
                'error_rate_percent': round(error_rate, 2),
                'membership_tier': membership.tier,
                'monthly_usage': {
                    'used': membership.monthly_lookups_used,
                    'limit': current_limit,
                    'percentage': round(usage_percentage, 1)
                },
                'endpoint_breakdown': list(endpoint_usage),
                'daily_trend': list(daily_usage)
            }
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@require_http_methods(["GET"])
@user_passes_test(lambda u: u.is_staff)
@track_api_usage
def admin_usage_analytics(request):
    """Admin view of all API usage analytics"""
    try:
        days = int(request.GET.get('days', 30))
        start_date = timezone.now() - timedelta(days=days)
        
        # Overall metrics
        total_requests = APIUsageTracking.objects.filter(timestamp__gte=start_date).count()
        unique_users = APIUsageTracking.objects.filter(timestamp__gte=start_date).values('user').distinct().count()
        
        # Usage by tier
        tier_usage = APIUsageTracking.objects.filter(
            timestamp__gte=start_date
        ).values('membership_tier').annotate(
            requests=Count('id'),
            users=Count('user', distinct=True),
            avg_response_time=Avg('response_time_ms')
        ).order_by('-requests')
        
        # Top endpoints
        endpoint_stats = APIUsageTracking.objects.filter(
            timestamp__gte=start_date
        ).values('endpoint').annotate(
            requests=Count('id'),
            avg_response_time=Avg('response_time_ms')
        ).order_by('-requests')[:10]
        
        # Performance metrics
        slow_endpoints = APIUsageTracking.objects.filter(
            timestamp__gte=start_date,
            response_time_ms__gt=5000
        ).values('endpoint').annotate(
            slow_requests=Count('id'),
            avg_slow_time=Avg('response_time_ms')
        ).order_by('-slow_requests')
        
        return JsonResponse({
            'success': True,
            'admin_analytics': {
                'period_days': days,
                'total_requests': total_requests,
                'unique_users': unique_users,
                'requests_per_user': round(total_requests / unique_users, 2) if unique_users > 0 else 0,
                'tier_breakdown': list(tier_usage),
                'top_endpoints': list(endpoint_stats),
                'performance_issues': list(slow_endpoints)
            }
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

# ==================== MARKET SENTIMENT ANALYSIS ====================

def analyze_sentiment_text(text):
    """Analyze sentiment of text using TextBlob"""
    try:
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity  # -1 to 1
        subjectivity = blob.sentiment.subjectivity  # 0 to 1
        return polarity, subjectivity
    except:
        return 0.0, 0.5

def get_stock_news_sentiment(ticker):
    """Get sentiment from stock news"""
    try:
        stock = yf.Ticker(ticker)
        news = stock.news
        
        if not news:
            return 0.0, 0.5, 0
        
        sentiments = []
        for item in news[:10]:  # Analyze first 10 news items
            title = item.get('title', '')
            summary = item.get('summary', '')
            text = f"{title} {summary}"
            
            polarity, subjectivity = analyze_sentiment_text(text)
            sentiments.append(polarity)
        
        avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0.0
        confidence = 1.0 - (sum(abs(s - avg_sentiment) for s in sentiments) / len(sentiments)) if sentiments else 0.5
        
        return avg_sentiment, confidence, len(sentiments)
        
    except Exception as e:
        print(f"News sentiment error: {e}")
        return 0.0, 0.5, 0

def simulate_social_sentiment(ticker):
    """Simulate social media sentiment (in production, integrate with Twitter/Reddit APIs)"""
    # For demo purposes, generate semi-realistic sentiment data
    import random
    
    # Base sentiment influenced by stock performance
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="5d")
        if len(hist) >= 2:
            recent_change = (hist['Close'].iloc[-1] - hist['Close'].iloc[-2]) / hist['Close'].iloc[-2]
            base_sentiment = min(max(recent_change * 2, -0.8), 0.8)  # Scale to -0.8 to 0.8
        else:
            base_sentiment = 0.0
    except:
        base_sentiment = 0.0
    
    # Add some randomness
    sentiment_score = base_sentiment + random.uniform(-0.3, 0.3)
    sentiment_score = min(max(sentiment_score, -1.0), 1.0)
    
    # Generate mention counts
    volume_mentions = random.randint(50, 500)
    positive_ratio = (sentiment_score + 1) / 2  # Convert -1,1 to 0,1
    
    positive_mentions = int(volume_mentions * positive_ratio * random.uniform(0.8, 1.2))
    negative_mentions = int(volume_mentions * (1 - positive_ratio) * random.uniform(0.8, 1.2))
    neutral_mentions = volume_mentions - positive_mentions - negative_mentions
    
    # Ensure non-negative values
    positive_mentions = max(0, positive_mentions)
    negative_mentions = max(0, negative_mentions)
    neutral_mentions = max(0, neutral_mentions)
    
    return {
        'sentiment_score': sentiment_score,
        'confidence_level': random.uniform(0.6, 0.9),
        'volume_mentions': volume_mentions,
        'positive_mentions': positive_mentions,
        'negative_mentions': negative_mentions,
        'neutral_mentions': neutral_mentions,
        'key_phrases': [f"${ticker}", "bullish", "earnings", "growth", "buy"]
    }

@require_http_methods(["GET"])
@track_api_usage
def market_sentiment_api(request, ticker):
    """Get comprehensive market sentiment for a ticker"""
    try:
        ticker = ticker.upper()
        
        # Check cache first
        cache_key = f"sentiment_{ticker}"
        cached_data = cache.get(cache_key)
        if cached_data:
            return JsonResponse(cached_data)
        
        # Get news sentiment
        news_sentiment, news_confidence, news_count = get_stock_news_sentiment(ticker)
        
        # Get social sentiment (simulated - in production use real APIs)
        social_data = simulate_social_sentiment(ticker)
        
        # Store/update sentiment data
        MarketSentiment.objects.update_or_create(
            ticker=ticker,
            sentiment_source='news',
            defaults={
                'sentiment_score': news_sentiment,
                'confidence_level': news_confidence,
                'volume_mentions': news_count,
                'data_timeframe': '24h'
            }
        )
        
        MarketSentiment.objects.update_or_create(
            ticker=ticker,
            sentiment_source='social_aggregate',
            defaults=social_data
        )
        
        # Calculate overall sentiment
        overall_sentiment = (news_sentiment * news_confidence + 
                           social_data['sentiment_score'] * social_data['confidence_level']) / 2
        
        # Determine trend
        if overall_sentiment > 0.2:
            trend = "improving"
        elif overall_sentiment < -0.2:
            trend = "declining"
        else:
            trend = "stable"
        
        response_data = {
            'success': True,
            'ticker': ticker,
            'sentiment_analysis': {
                'overall_sentiment': round(overall_sentiment, 3),
                'sentiment_label': 'Bullish' if overall_sentiment > 0.3 else 'Bearish' if overall_sentiment < -0.3 else 'Neutral',
                'trend': trend,
                'confidence': round((news_confidence + social_data['confidence_level']) / 2, 3),
                'sources': {
                    'news': {
                        'sentiment': round(news_sentiment, 3),
                        'confidence': round(news_confidence, 3),
                        'articles_analyzed': news_count
                    },
                    'social_media': {
                        'sentiment': round(social_data['sentiment_score'], 3),
                        'confidence': round(social_data['confidence_level'], 3),
                        'mentions': social_data['volume_mentions'],
                        'positive_mentions': social_data['positive_mentions'],
                        'negative_mentions': social_data['negative_mentions'],
                        'key_phrases': social_data['key_phrases']
                    }
                },
                'last_updated': timezone.now().isoformat()
            }
        }
        
        # Cache for 30 minutes
        cache.set(cache_key, response_data, 1800)
        
        return JsonResponse(response_data)
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@require_http_methods(["GET"])
@track_api_usage
def sentiment_dashboard_api(request):
    """Get sentiment dashboard with multiple stocks"""
    try:
        # Get popular tickers
        tickers = request.GET.get('tickers', 'AAPL,MSFT,GOOGL,TSLA,NVDA').split(',')
        tickers = [t.strip().upper() for t in tickers[:10]]  # Limit to 10
        
        sentiment_data = []
        for ticker in tickers:
            try:
                # Get latest sentiment data
                latest_sentiment = MarketSentiment.objects.filter(
                    ticker=ticker
                ).order_by('-analyzed_at').first()
                
                if latest_sentiment:
                    sentiment_data.append({
                        'ticker': ticker,
                        'sentiment_score': float(latest_sentiment.sentiment_score),
                        'sentiment_label': latest_sentiment.sentiment_label,
                        'confidence': float(latest_sentiment.confidence_level),
                        'trend': latest_sentiment.sentiment_trend,
                        'last_updated': latest_sentiment.analyzed_at.isoformat()
                    })
                else:
                    # Generate new sentiment data
                    social_data = simulate_social_sentiment(ticker)
                    sentiment_data.append({
                        'ticker': ticker,
                        'sentiment_score': social_data['sentiment_score'],
                        'sentiment_label': 'Bullish' if social_data['sentiment_score'] > 0.3 else 'Bearish' if social_data['sentiment_score'] < -0.3 else 'Neutral',
                        'confidence': social_data['confidence_level'],
                        'trend': 'stable',
                        'last_updated': timezone.now().isoformat()
                    })
            except:
                continue
        
        # Calculate market-wide sentiment
        if sentiment_data:
            avg_sentiment = sum(item['sentiment_score'] for item in sentiment_data) / len(sentiment_data)
            bullish_count = sum(1 for item in sentiment_data if item['sentiment_score'] > 0.2)
            bearish_count = sum(1 for item in sentiment_data if item['sentiment_score'] < -0.2)
        else:
            avg_sentiment = 0.0
            bullish_count = 0
            bearish_count = 0
        
        return JsonResponse({
            'success': True,
            'market_sentiment': {
                'overall_sentiment': round(avg_sentiment, 3),
                'market_mood': 'Bullish' if avg_sentiment > 0.2 else 'Bearish' if avg_sentiment < -0.2 else 'Mixed',
                'bullish_stocks': bullish_count,
                'bearish_stocks': bearish_count,
                'neutral_stocks': len(sentiment_data) - bullish_count - bearish_count
            },
            'individual_stocks': sentiment_data,
            'total_analyzed': len(sentiment_data)
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

# ==================== PORTFOLIO ANALYTICS ====================

def calculate_returns(prices):
    """Calculate returns from price series"""
    if len(prices) < 2:
        return []
    return [(prices[i] - prices[i-1]) / prices[i-1] for i in range(1, len(prices))]

def calculate_sharpe_ratio(returns, risk_free_rate=0.02):
    """Calculate Sharpe ratio"""
    if not returns:
        return 0.0
    
    avg_return = sum(returns) / len(returns)
    if len(returns) < 2:
        return 0.0
    
    variance = sum((r - avg_return) ** 2 for r in returns) / (len(returns) - 1)
    std_dev = math.sqrt(variance)
    
    if std_dev == 0:
        return 0.0
    
    # Annualize
    annualized_return = avg_return * 252  # 252 trading days
    annualized_std = std_dev * math.sqrt(252)
    
    return (annualized_return - risk_free_rate) / annualized_std

def calculate_beta(stock_returns, market_returns):
    """Calculate beta vs market"""
    if len(stock_returns) != len(market_returns) or len(stock_returns) < 2:
        return 1.0
    
    # Calculate covariance and variance
    stock_mean = sum(stock_returns) / len(stock_returns)
    market_mean = sum(market_returns) / len(market_returns)
    
    covariance = sum((stock_returns[i] - stock_mean) * (market_returns[i] - market_mean) 
                    for i in range(len(stock_returns))) / (len(stock_returns) - 1)
    
    market_variance = sum((r - market_mean) ** 2 for r in market_returns) / (len(market_returns) - 1)
    
    if market_variance == 0:
        return 1.0
    
    return covariance / market_variance

def calculate_var(returns, confidence=0.95):
    """Calculate Value at Risk"""
    if not returns:
        return 0.0
    
    sorted_returns = sorted(returns)
    index = int((1 - confidence) * len(sorted_returns))
    
    if index >= len(sorted_returns):
        return sorted_returns[-1]
    
    return sorted_returns[index]

@require_http_methods(["GET"])
@login_required
@track_api_usage
def portfolio_analytics_api(request, portfolio_id):
    """Get comprehensive portfolio analytics"""
    try:
        # Get portfolio
        portfolio = Portfolio.objects.get(id=portfolio_id, user=request.user)
        holdings = portfolio.holdings.all()
        
        if not holdings:
            return JsonResponse({
                'success': False,
                'error': 'Portfolio has no holdings'
            }, status=400)
        
        # Get or create analytics object
        analytics, created = PortfolioAnalytics.objects.get_or_create(
            portfolio=portfolio,
            defaults={'calculation_status': 'pending'}
        )
        
        # Set status to calculating
        analytics.calculation_status = 'calculating'
        analytics.save()
        
        try:
            # Calculate analytics
            total_value = 0
            total_cost = 0
            sector_allocation = {}
            market_cap_allocation = {'large': 0, 'mid': 0, 'small': 0}
            all_returns = []
            portfolio_returns = []
            
            # Get market data (SPY as benchmark)
            spy = yf.Ticker('SPY')
            spy_hist = spy.history(period="1y")
            market_returns = calculate_returns(spy_hist['Close'].tolist()) if len(spy_hist) > 1 else []
            
            performance_attribution = {}
            top_contributors = []
            top_detractors = []
            
            for holding in holdings:
                try:
                    # Get stock data
                    stock = yf.Ticker(holding.ticker)
                    hist = stock.history(period="1y")
                    info = stock.info
                    
                    if len(hist) < 1:
                        continue
                    
                    # Calculate holding metrics
                    current_price = float(holding.current_price)
                    holding_value = float(holding.shares) * current_price
                    holding_cost = float(holding.shares) * float(holding.purchase_price)
                    
                    total_value += holding_value
                    total_cost += holding_cost
                    
                    # Performance attribution
                    holding_return = (holding_value - holding_cost) / holding_cost if holding_cost > 0 else 0
                    performance_attribution[holding.ticker] = {
                        'return_percent': holding_return * 100,
                        'contribution': holding_value - holding_cost,
                        'weight': 0  # Will calculate after getting total_value
                    }
                    
                    if holding_return > 0:
                        top_contributors.append({
                            'ticker': holding.ticker,
                            'return_percent': holding_return * 100,
                            'contribution': holding_value - holding_cost
                        })
                    else:
                        top_detractors.append({
                            'ticker': holding.ticker,
                            'return_percent': holding_return * 100,
                            'contribution': holding_value - holding_cost
                        })
                    
                    # Sector allocation
                    sector = info.get('sector', 'Unknown')
                    if sector not in sector_allocation:
                        sector_allocation[sector] = 0
                    sector_allocation[sector] += holding_value
                    
                    # Market cap allocation
                    market_cap = info.get('marketCap', 0)
                    if market_cap > 200_000_000_000:  # > 200B
                        market_cap_allocation['large'] += holding_value
                    elif market_cap > 10_000_000_000:  # 10B - 200B
                        market_cap_allocation['mid'] += holding_value
                    else:  # < 10B
                        market_cap_allocation['small'] += holding_value
                    
                    # Calculate returns for this stock
                    if len(hist) > 1:
                        stock_returns = calculate_returns(hist['Close'].tolist())
                        all_returns.extend(stock_returns)
                        
                        # Weight by portfolio allocation
                        weight = holding_value / total_value if total_value > 0 else 0
                        weighted_returns = [r * weight for r in stock_returns]
                        portfolio_returns.extend(weighted_returns)
                
                except Exception as e:
                    print(f"Error processing holding {holding.ticker}: {e}")
                    continue
            
            # Update weights in performance attribution
            for ticker in performance_attribution:
                holding = next((h for h in holdings if h.ticker == ticker), None)
                if holding:
                    holding_value = float(holding.shares) * float(holding.current_price)
                    performance_attribution[ticker]['weight'] = (holding_value / total_value * 100) if total_value > 0 else 0
            
            # Convert sector allocation to percentages
            sector_percentages = {}
            for sector, value in sector_allocation.items():
                sector_percentages[sector] = (value / total_value * 100) if total_value > 0 else 0
            
            # Convert market cap allocation to percentages
            market_cap_percentages = {}
            for cap_type, value in market_cap_allocation.items():
                market_cap_percentages[cap_type] = (value / total_value * 100) if total_value > 0 else 0
            
            # Calculate risk metrics
            sharpe_ratio = calculate_sharpe_ratio(portfolio_returns) if portfolio_returns else 0.0
            beta = calculate_beta(portfolio_returns, market_returns) if portfolio_returns and market_returns else 1.0
            var_1d = calculate_var(portfolio_returns) if portfolio_returns else 0.0
            
            # Calculate volatility
            if len(portfolio_returns) > 1:
                mean_return = sum(portfolio_returns) / len(portfolio_returns)
                variance = sum((r - mean_return) ** 2 for r in portfolio_returns) / (len(portfolio_returns) - 1)
                volatility = math.sqrt(variance) * math.sqrt(252)  # Annualized
            else:
                volatility = 0.0
            
            # Calculate diversification metrics
            num_holdings = len(holdings)
            largest_weight = max(performance_attribution[ticker]['weight'] for ticker in performance_attribution) if performance_attribution else 0
            
            # Calculate concentration risk (Herfindahl index)
            concentration_risk = sum((weight/100) ** 2 for weight in [performance_attribution[ticker]['weight'] for ticker in performance_attribution]) if performance_attribution else 1.0
            
            # Sort contributors and detractors
            top_contributors.sort(key=lambda x: x['contribution'], reverse=True)
            top_detractors.sort(key=lambda x: x['contribution'])
            
            # Calculate risk score (1-100)
            risk_factors = [
                min(volatility * 50, 30),  # Volatility component (max 30)
                min(concentration_risk * 40, 25),  # Concentration component (max 25)
                min(abs(beta - 1) * 20, 20),  # Beta component (max 20)
                min(largest_weight / 5, 25)  # Largest position component (max 25)
            ]
            risk_score = min(sum(risk_factors), 100)
            
            # Generate rebalancing suggestions
            rebalancing_suggestions = []
            if largest_weight > 20:
                rebalancing_suggestions.append(f"Consider reducing position in largest holding (currently {largest_weight:.1f}%)")
            if concentration_risk > 0.25:
                rebalancing_suggestions.append("Portfolio is concentrated - consider diversifying across more sectors")
            if len(sector_percentages) < 3:
                rebalancing_suggestions.append("Consider diversifying across more sectors")
            
            # Update analytics object
            analytics.sharpe_ratio = sharpe_ratio
            analytics.beta = beta
            analytics.value_at_risk_1d = var_1d
            analytics.volatility_annualized = volatility
            analytics.sector_concentration_risk = concentration_risk
            analytics.largest_position_weight = largest_weight
            analytics.sector_allocation = sector_percentages
            analytics.market_cap_allocation = market_cap_percentages
            analytics.performance_attribution = performance_attribution
            analytics.top_contributors = top_contributors[:5]
            analytics.top_detractors = top_detractors[:5]
            analytics.rebalancing_needed = len(rebalancing_suggestions) > 0
            analytics.rebalancing_suggestions = rebalancing_suggestions
            analytics.risk_score = int(risk_score)
            analytics.calculation_status = 'completed'
            analytics.save()
            
            return JsonResponse({
                'success': True,
                'portfolio_analytics': {
                    'portfolio_id': portfolio.id,
                    'portfolio_name': portfolio.name,
                    'total_value': round(total_value, 2),
                    'total_cost': round(total_cost, 2),
                    'total_return': round(total_value - total_cost, 2),
                    'total_return_percent': round((total_value - total_cost) / total_cost * 100, 2) if total_cost > 0 else 0,
                    'risk_metrics': {
                        'sharpe_ratio': round(sharpe_ratio, 3),
                        'beta': round(beta, 3),
                        'value_at_risk_1d_percent': round(var_1d * 100, 2),
                        'volatility_annualized_percent': round(volatility * 100, 2),
                        'risk_score': int(risk_score),
                        'risk_level': analytics.get_risk_level()
                    },
                    'diversification': {
                        'sector_allocation': sector_percentages,
                        'market_cap_allocation': market_cap_percentages,
                        'concentration_risk': round(concentration_risk, 3),
                        'largest_position_percent': round(largest_weight, 2),
                        'number_of_holdings': num_holdings
                    },
                    'performance_attribution': performance_attribution,
                    'top_contributors': top_contributors[:5],
                    'top_detractors': top_detractors[:5],
                    'rebalancing': {
                        'needed': analytics.rebalancing_needed,
                        'suggestions': rebalancing_suggestions
                    },
                    'last_calculated': analytics.last_calculated.isoformat()
                }
            })
            
        except Exception as calc_error:
            # Update status to failed
            analytics.calculation_status = 'failed'
            analytics.save()
            raise calc_error
            
    except Portfolio.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Portfolio not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

# ==================== COMPLIANCE & SECURITY ====================

@require_http_methods(["GET"])
@user_passes_test(lambda u: u.is_staff)
def compliance_dashboard_api(request):
    """Admin compliance dashboard"""
    try:
        days = int(request.GET.get('days', 30))
        start_date = timezone.now() - timedelta(days=days)
        
        # Get compliance logs
        compliance_logs = ComplianceLog.objects.filter(timestamp__gte=start_date)
        
        # Compliance metrics
        total_events = compliance_logs.count()
        flagged_events = compliance_logs.filter(compliance_status='flagged').count()
        violations = compliance_logs.filter(compliance_status='violation').count()
        
        # Risk level breakdown
        risk_breakdown = compliance_logs.values('risk_level').annotate(
            count=Count('id')
        ).order_by('risk_level')
        
        # Action type breakdown
        action_breakdown = compliance_logs.values('action_type').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Regulatory framework breakdown
        framework_breakdown = compliance_logs.values('regulatory_framework').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Recent high-risk events
        high_risk_events = compliance_logs.filter(
            risk_level__in=['high', 'critical']
        ).order_by('-timestamp')[:10]
        
        high_risk_data = []
        for event in high_risk_events:
            high_risk_data.append({
                'id': event.id,
                'user': event.user.username,
                'action_type': event.action_type,
                'description': event.description,
                'risk_level': event.risk_level,
                'timestamp': event.timestamp.isoformat(),
                'status': event.compliance_status
            })
        
        # Security events
        security_events = SecurityEvent.objects.filter(detected_at__gte=start_date)
        security_metrics = {
            'total_events': security_events.count(),
            'critical_events': security_events.filter(severity='critical').count(),
            'high_events': security_events.filter(severity='high').count(),
            'blocked_requests': security_events.filter(mitigation_action='blocked').count()
        }
        
        return JsonResponse({
            'success': True,
            'compliance_dashboard': {
                'period_days': days,
                'overview': {
                    'total_events': total_events,
                    'flagged_events': flagged_events,
                    'violations': violations,
                    'compliance_rate': round((total_events - violations) / total_events * 100, 2) if total_events > 0 else 100
                },
                'risk_breakdown': list(risk_breakdown),
                'action_breakdown': list(action_breakdown),
                'framework_breakdown': list(framework_breakdown),
                'high_risk_events': high_risk_data,
                'security_metrics': security_metrics
            }
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@require_http_methods(["POST"])
@csrf_exempt
def report_security_event(request):
    """Report a security event"""
    try:
        data = json.loads(request.body)
        
        event_type = data.get('event_type')
        severity = data.get('severity', 'medium')
        description = data.get('description', '')
        
        # Detect threats
        threats = detect_security_threats(request)
        
        # Create security event
        security_event = SecurityEvent.objects.create(
            event_type=event_type,
            severity=severity,
            source_ip=get_client_ip(request),
            target_user=request.user if request.user.is_authenticated else None,
            target_endpoint=request.path,
            description=description,
            request_data={
                'method': request.method,
                'path': request.path,
                'threats_detected': threats
            },
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            mitigation_action='logged'
        )
        
        # Auto-escalate critical events
        if severity == 'critical':
            security_event.mitigation_action = 'escalated'
            security_event.save()
        
        return JsonResponse({
            'success': True,
            'event_id': security_event.id,
            'severity': severity,
            'mitigation_action': security_event.mitigation_action
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

# ==================== REGULATORY ENDPOINTS ====================

@require_http_methods(["GET"])
@login_required
def gdpr_data_export(request):
    """GDPR Article 20 - Right to data portability"""
    try:
        user = request.user
        
        # Log compliance action
        log_compliance_action(
            user, 'data_export', 
            'User requested GDPR data export', 
            request, 'medium'
        )
        
        # Collect all user data
        user_data = {
            'personal_info': {
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'date_joined': user.date_joined.isoformat()
            },
            'membership_info': {},
            'portfolios': [],
            'api_usage': [],
            'compliance_logs': []
        }
        
        # Membership data
        try:
            membership = user.membership
            user_data['membership_info'] = {
                'tier': membership.tier,
                'monthly_price': float(membership.monthly_price),
                'is_active': membership.is_active,
                'monthly_lookups_used': membership.monthly_lookups_used,
                'created_at': membership.created_at.isoformat()
            }
        except:
            pass
        
        # Portfolio data
        portfolios = Portfolio.objects.filter(user=user)
        for portfolio in portfolios:
            portfolio_data = {
                'name': portfolio.name,
                'description': portfolio.description,
                'created_at': portfolio.created_at.isoformat(),
                'holdings': []
            }
            
            for holding in portfolio.holdings.all():
                portfolio_data['holdings'].append({
                    'ticker': holding.ticker,
                    'company_name': holding.company_name,
                    'shares': float(holding.shares),
                    'purchase_price': float(holding.purchase_price),
                    'purchase_date': holding.purchase_date.isoformat()
                })
            
            user_data['portfolios'].append(portfolio_data)
        
        # API usage data (last 90 days)
        start_date = timezone.now() - timedelta(days=90)
        api_usage = APIUsageTracking.objects.filter(
            user=user,
            timestamp__gte=start_date
        )[:1000]  # Limit to 1000 records
        
        for usage in api_usage:
            user_data['api_usage'].append({
                'endpoint': usage.endpoint,
                'method': usage.method,
                'timestamp': usage.timestamp.isoformat(),
                'status_code': usage.status_code,
                'response_time_ms': usage.response_time_ms
            })
        
        return JsonResponse({
            'success': True,
            'data_export': user_data,
            'export_timestamp': timezone.now().isoformat(),
            'data_retention_policy': '7 years for financial data, 2 years for usage logs'
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@require_http_methods(["POST"])
@csrf_exempt
@login_required
def gdpr_data_deletion(request):
    """GDPR Article 17 - Right to erasure"""
    try:
        user = request.user
        data = json.loads(request.body)
        
        deletion_type = data.get('deletion_type', 'partial')
        
        # Log compliance action
        log_compliance_action(
            user, 'data_deletion', 
            f'User requested {deletion_type} data deletion', 
            request, 'high'
        )
        
        if deletion_type == 'full':
            # Full account deletion
            # Note: In production, you might want to anonymize rather than delete
            # to preserve business intelligence and comply with financial regulations
            
            user.email = f"deleted_user_{user.id}@deleted.com"
            user.username = f"deleted_user_{user.id}"
            user.first_name = ""
            user.last_name = ""
            user.is_active = False
            user.save()
            
            # Anonymize related data
            APIUsageTracking.objects.filter(user=user).delete()
            ComplianceLog.objects.filter(user=user).update(
                user=None,
                description="Data anonymized per GDPR request"
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Account data has been anonymized',
                'deletion_type': 'full'
            })
            
        elif deletion_type == 'partial':
            # Partial deletion - remove specific data types
            data_types = data.get('data_types', [])
            
            deleted_types = []
            
            if 'api_usage' in data_types:
                APIUsageTracking.objects.filter(user=user).delete()
                deleted_types.append('api_usage')
            
            if 'portfolios' in data_types:
                Portfolio.objects.filter(user=user).delete()
                deleted_types.append('portfolios')
            
            return JsonResponse({
                'success': True,
                'message': f'Deleted data types: {", ".join(deleted_types)}',
                'deletion_type': 'partial',
                'deleted_types': deleted_types
            })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
