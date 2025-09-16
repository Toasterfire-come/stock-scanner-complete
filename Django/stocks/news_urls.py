"""
News URL Configuration
Dedicated URL patterns for news personalization endpoints.
"""

from django.urls import path
from . import news_personalization_service
from news.models import NewsArticle
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .security_utils import secure_api_endpoint, validate_user_input
from django.utils import timezone
from django.db.models import Q

app_name = 'news'

# News API endpoints
@csrf_exempt
@secure_api_endpoint(methods=['GET'])
def get_personalized_feed(request):
    """Get news feed. If no personalized items, return all available news."""
    try:
        raw_limit = request.GET.get('limit')
        category = request.GET.get('category', None)

        # Interpret limit: 'all' or missing => no cap; else int
        if raw_limit is None or raw_limit.lower() == 'all':
            limit = None
        else:
            try:
                limit = max(1, int(raw_limit))
            except Exception:
                limit = 20

        # Try personalized feed first
        pf_limit = limit if limit is not None else 1000
        feed = news_personalization_service.NewsPersonalizationService.get_personalized_feed(
            user=request.user,
            limit=pf_limit,
            category=category
        )

        if feed:
            return JsonResponse({
                'success': True,
                'data': {
                    'news_items': feed if limit is None else feed[:limit],
                    'count': len(feed) if limit is None else min(len(feed), limit)
                },
                'message': 'News feed retrieved successfully'
            })

        # Fallback: return all news articles available (dedupe by URL)
        qs = NewsArticle.objects.exclude(Q(url__isnull=True) | Q(url__exact='')).order_by('-published_date')
        if category:
            qs = qs.filter(sentiment_grade__iexact=category[:1])  # optional mapping
        articles = list(qs if limit is None else qs[:limit])

        def parse_tickers(s: str):
            if not s:
                return []
            return [t.strip().upper() for t in s.split(',') if t.strip()]

        seen = set()
        items = []
        for a in articles:
            if a.url and a.url in seen:
                continue
            if a.url:
                seen.add(a.url)
            items.append({
            'id': a.id,
            'title': a.title,
            'content': a.summary,
            'url': a.url,
            'source': a.source or (a.news_source.name if a.news_source else 'Unknown'),
            'sentiment_score': float(a.sentiment_score) if a.sentiment_score is not None else None,
            'sentiment_grade': a.sentiment_grade,
            'tickers': parse_tickers(a.mentioned_tickers),
            'mentioned_tickers': a.mentioned_tickers,
            'published_at': a.published_date.isoformat() if a.published_date else None,
            'created_at': a.created_at.isoformat() if a.created_at else None,
        })

        return JsonResponse({
            'success': True,
            'data': {
                'news_items': items,
                'count': len(items)
            },
            'message': 'All news retrieved successfully' if items else 'No news available'
        })

    except Exception:
        # As a last resort, return empty set with 200
        return JsonResponse({
            'success': True,
            'data': {
                'news_items': [],
                'count': 0
            },
            'message': 'No news available'
        }, status=200)

@csrf_exempt
@secure_api_endpoint(methods=['POST'])
def mark_news_read(request):
    """Mark a news article as read."""
    try:
        schema = {
            'news_id': {'type': 'integer', 'required': True, 'min_value': 1}
        }
        validated_data = validate_user_input(request.validated_data, schema)
        
        success = news_personalization_service.NewsPersonalizationService.mark_news_read(
            user=request.user,
            news_id=validated_data['news_id']
        )
        
        return JsonResponse({
            'success': success,
            'message': 'News marked as read' if success else 'Failed to mark news as read'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': 'Failed to mark news as read',
            'error_code': 'NEWS_ERROR'
        }, status=500)

@csrf_exempt
@secure_api_endpoint(methods=['POST'])
def mark_news_clicked(request):
    """Mark a news article as clicked."""
    try:
        schema = {
            'news_id': {'type': 'integer', 'required': True, 'min_value': 1}
        }
        validated_data = validate_user_input(request.validated_data, schema)
        
        success = news_personalization_service.NewsPersonalizationService.mark_news_clicked(
            user=request.user,
            news_id=validated_data['news_id']
        )
        
        return JsonResponse({
            'success': success,
            'message': 'News marked as clicked' if success else 'Failed to mark news as clicked'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': 'Failed to mark news as clicked',
            'error_code': 'NEWS_ERROR'
        }, status=500)

@csrf_exempt
@secure_api_endpoint(methods=['POST'])
def update_preferences(request):
    """Update user news preferences."""
    try:
        schema = {
            'followed_stocks': {'type': 'list', 'item_type': 'ticker', 'max_items': 100},
            'followed_sectors': {'type': 'list', 'item_type': 'string', 'max_items': 20},
            'preferred_categories': {'type': 'list', 'item_type': 'string', 'max_items': 10},
            'news_frequency': {'type': 'string', 'pattern': r'^(realtime|hourly|daily|weekly)$'}
        }
        validated_data = validate_user_input(request.validated_data, schema)
        
        interests = news_personalization_service.NewsPersonalizationService.setup_user_interests(
            user=request.user,
            followed_stocks=validated_data.get('followed_stocks'),
            followed_sectors=validated_data.get('followed_sectors'),
            preferred_categories=validated_data.get('preferred_categories'),
            news_frequency=validated_data.get('news_frequency')
        )
        
        return JsonResponse({
            'success': True,
            'data': {
                'followed_stocks': interests.followed_stocks,
                'followed_sectors': interests.followed_sectors,
                'preferred_categories': interests.preferred_categories,
                'news_frequency': interests.news_frequency
            },
            'message': 'News preferences updated successfully'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': 'Failed to update news preferences',
            'error_code': 'NEWS_ERROR'
        }, status=500)

@csrf_exempt
@secure_api_endpoint(methods=['GET'])
def get_analytics(request):
    """Get news consumption analytics for the user."""
    try:
        analytics = news_personalization_service.NewsPersonalizationService.get_news_analytics(request.user)
        
        return JsonResponse({
            'success': True,
            'data': analytics,
            'message': 'News analytics retrieved successfully'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': 'Failed to retrieve news analytics',
            'error_code': 'NEWS_ERROR'
        }, status=500)

@csrf_exempt
@secure_api_endpoint(methods=['POST'])
def sync_portfolio_stocks(request):
    """Sync user's portfolio stocks to news interests."""
    try:
        news_personalization_service.NewsPersonalizationService.sync_portfolio_stocks(request.user)
        
        return JsonResponse({
            'success': True,
            'message': 'Portfolio stocks synced to news interests successfully'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': 'Failed to sync portfolio stocks',
            'error_code': 'NEWS_ERROR'
        }, status=500)

urlpatterns = [
    # News feed management
    path('feed/', get_personalized_feed, name='feed'),
    path('mark-read/', mark_news_read, name='mark_read'),
    path('mark-clicked/', mark_news_clicked, name='mark_clicked'),
    
    # News preferences
    path('preferences/', update_preferences, name='preferences'),
    path('sync-portfolio/', sync_portfolio_stocks, name='sync_portfolio'),
    
    # Analytics
    path('analytics/', get_analytics, name='analytics'),
    
    # Ticker-scoped news endpoint
    path('ticker/<str:ticker>/', csrf_exempt(secure_api_endpoint(methods=['GET'])(
        lambda request, ticker: (
            (lambda items: JsonResponse({
                'success': True,
                'data': { 'news_items': items, 'count': len(items) },
                'timestamp': timezone.now().isoformat()
            }))([
                {
                    'id': a.id,
                    'title': a.title,
                    'content': a.summary,
                    'url': a.url,
                    'source': a.source or (a.news_source.name if a.news_source else 'Unknown'),
                    'sentiment_score': float(a.sentiment_score) if a.sentiment_score is not None else None,
                    'sentiment_grade': a.sentiment_grade,
                    'tickers': [t.strip() for t in (a.mentioned_tickers or '').split(',') if t.strip()],
                    'published_at': a.published_date.isoformat() if a.published_date else None,
                } for a in NewsArticle.objects.filter(mentioned_tickers__icontains=ticker.upper()).order_by('-published_date')[:500]
            ])
        )
    )), name='ticker_news'),
]