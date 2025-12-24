"""
News & Sentiment API Endpoints
RESTful API for news aggregation, sentiment analysis, and personalized feeds.
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.core.paginator import Paginator
from django.db.models import Q, Avg, Count
from datetime import datetime, timedelta
from django.utils import timezone

from stocks.models import (
    NewsSource, NewsArticle, SentimentAnalysis, NewsFeed,
    NewsAlert, SentimentTimeseries, Stock
)
from stocks.services.news_service import NewsFetchService
from stocks.services.sentiment_service import SentimentAnalysisService


@api_view(['GET'])
@permission_classes([AllowAny])
def get_news_feed(request):
    """
    Get paginated news feed with optional filtering.

    Query params:
    - ticker: Filter by stock ticker
    - source: Filter by source ID
    - category: Filter by category
    - sentiment: Filter by sentiment label (positive, negative, neutral, very_positive, very_negative)
    - days: Days to look back (default: 7)
    - page: Page number (default: 1)
    - page_size: Items per page (default: 20, max: 100)
    """
    # Filters
    ticker = request.GET.get('ticker')
    source_id = request.GET.get('source')
    category = request.GET.get('category')
    sentiment_filter = request.GET.get('sentiment')
    days = int(request.GET.get('days', 7))

    # Pagination
    page = int(request.GET.get('page', 1))
    page_size = min(int(request.GET.get('page_size', 20)), 100)

    # Build query
    cutoff = timezone.now() - timedelta(days=days)
    articles = NewsArticle.objects.filter(
        published_at__gte=cutoff
    ).select_related('source').prefetch_related('stocks', 'sentiments')

    if ticker:
        articles = articles.filter(stocks__ticker=ticker.upper())

    if source_id:
        articles = articles.filter(source_id=source_id)

    if category:
        articles = articles.filter(category=category)

    if sentiment_filter:
        articles = articles.filter(sentiments__sentiment_label=sentiment_filter).distinct()

    articles = articles.order_by('-published_at')

    # Paginate
    paginator = Paginator(articles, page_size)
    page_obj = paginator.get_page(page)

    # Serialize
    articles_data = []
    for article in page_obj:
        # Get primary sentiment (most recent)
        primary_sentiment = article.sentiments.first()

        articles_data.append({
            'id': article.id,
            'title': article.title,
            'summary': article.summary,
            'url': article.url,
            'source': {
                'id': article.source.id,
                'name': article.source.name,
                'type': article.source.source_type,
            },
            'author': article.author,
            'published_at': article.published_at.isoformat(),
            'category': article.category,
            'tags': article.tags,
            'tickers': article.mentioned_tickers,
            'sentiment': {
                'label': primary_sentiment.sentiment_label if primary_sentiment else None,
                'score': float(primary_sentiment.sentiment_score) if primary_sentiment else None,
                'confidence': float(primary_sentiment.confidence) if primary_sentiment else None,
            } if primary_sentiment else None,
            'view_count': article.view_count,
            'click_count': article.click_count,
        })

    return Response({
        'success': True,
        'articles': articles_data,
        'pagination': {
            'current_page': page,
            'total_pages': paginator.num_pages,
            'total_items': paginator.count,
            'page_size': page_size,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous(),
        }
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def get_article_detail(request, article_id):
    """
    Get detailed view of a single article with all sentiment analyses.
    """
    try:
        article = NewsArticle.objects.select_related('source').prefetch_related(
            'stocks', 'sentiments', 'sentiments__stock'
        ).get(id=article_id)
    except NewsArticle.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Article not found'
        }, status=status.HTTP_404_NOT_FOUND)

    # Increment view count
    article.view_count += 1
    article.save(update_fields=['view_count'])

    # Get all sentiments
    sentiments_data = []
    for sentiment in article.sentiments.all():
        sentiments_data.append({
            'stock': sentiment.stock.ticker if sentiment.stock else None,
            'label': sentiment.sentiment_label,
            'score': float(sentiment.sentiment_score),
            'confidence': float(sentiment.confidence),
            'positive_score': float(sentiment.positive_score) if sentiment.positive_score else None,
            'negative_score': float(sentiment.negative_score) if sentiment.negative_score else None,
            'neutral_score': float(sentiment.neutral_score) if sentiment.neutral_score else None,
            'engine': sentiment.analysis_engine,
            'key_phrases': sentiment.key_phrases,
            'entities': sentiment.entities_mentioned,
            'aspects': sentiment.aspect_sentiments,
            'analyzed_at': sentiment.analyzed_at.isoformat(),
        })

    return Response({
        'success': True,
        'article': {
            'id': article.id,
            'title': article.title,
            'summary': article.summary,
            'content': article.content,
            'url': article.url,
            'source': {
                'id': article.source.id,
                'name': article.source.name,
                'type': article.source.source_type,
                'reliability_score': float(article.source.reliability_score),
            },
            'author': article.author,
            'published_at': article.published_at.isoformat(),
            'category': article.category,
            'tags': article.tags,
            'tickers': article.mentioned_tickers,
            'stocks': [{'ticker': s.ticker, 'name': s.company_name} for s in article.stocks.all()],
            'sentiments': sentiments_data,
            'view_count': article.view_count,
            'click_count': article.click_count,
        }
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def track_article_click(request, article_id):
    """
    Track article click for engagement metrics.
    """
    try:
        article = NewsArticle.objects.get(id=article_id)
        article.click_count += 1
        article.save(update_fields=['click_count'])

        return Response({
            'success': True,
            'message': 'Click tracked'
        })
    except NewsArticle.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Article not found'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_stock_news(request, ticker):
    """
    Get news for a specific stock with sentiment.

    Query params:
    - days: Days to look back (default: 7)
    - limit: Maximum articles (default: 50, max: 200)
    """
    ticker = ticker.upper()
    days = int(request.GET.get('days', 7))
    limit = min(int(request.GET.get('limit', 50)), 200)

    articles = NewsFetchService.fetch_for_ticker(ticker, days, limit)

    articles_data = []
    for article in articles:
        # Get stock-specific sentiment
        stock_sentiment = article.sentiments.filter(stock__ticker=ticker).first()

        articles_data.append({
            'id': article.id,
            'title': article.title,
            'summary': article.summary,
            'url': article.url,
            'source': article.source.name,
            'published_at': article.published_at.isoformat(),
            'sentiment': {
                'label': stock_sentiment.sentiment_label if stock_sentiment else None,
                'score': float(stock_sentiment.sentiment_score) if stock_sentiment else None,
            } if stock_sentiment else None,
        })

    return Response({
        'success': True,
        'ticker': ticker,
        'articles': articles_data,
        'count': len(articles_data)
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def get_sentiment_summary(request, ticker):
    """
    Get aggregated sentiment summary for a stock.

    Query params:
    - days: Days to look back (default: 7)
    """
    ticker = ticker.upper()
    days = int(request.GET.get('days', 7))

    summary = SentimentAnalysisService.get_stock_sentiment_summary(ticker, days)

    return Response(summary)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_sentiment_timeseries(request, ticker):
    """
    Get sentiment timeseries data for charting.

    Query params:
    - interval: '1h', '4h', '1d', '1w' (default: '1d')
    - days: Days to look back (default: 30)
    """
    ticker = ticker.upper()
    interval = request.GET.get('interval', '1d')
    days = int(request.GET.get('days', 30))

    try:
        stock = Stock.objects.get(ticker=ticker)
    except Stock.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Stock not found'
        }, status=status.HTTP_404_NOT_FOUND)

    cutoff = timezone.now() - timedelta(days=days)

    timeseries = SentimentTimeseries.objects.filter(
        stock=stock,
        interval=interval,
        period_start__gte=cutoff
    ).order_by('period_start')

    data_points = []
    for point in timeseries:
        data_points.append({
            'timestamp': point.period_start.isoformat(),
            'avg_sentiment': float(point.avg_sentiment_score),
            'weighted_sentiment': float(point.weighted_sentiment),
            'total_articles': point.total_articles,
            'positive_count': point.positive_articles,
            'negative_count': point.negative_articles,
            'neutral_count': point.neutral_articles,
        })

    return Response({
        'success': True,
        'ticker': ticker,
        'interval': interval,
        'data': data_points,
        'count': len(data_points)
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def get_trending_news(request):
    """
    Get trending news based on engagement.

    Query params:
    - hours: Hours to look back (default: 24)
    - limit: Maximum articles (default: 50)
    """
    hours = int(request.GET.get('hours', 24))
    limit = min(int(request.GET.get('limit', 50)), 200)

    articles = NewsFetchService.get_trending_news(hours, limit)

    articles_data = []
    for article in articles:
        primary_sentiment = article.sentiments.first()

        articles_data.append({
            'id': article.id,
            'title': article.title,
            'summary': article.summary,
            'url': article.url,
            'source': article.source.name,
            'published_at': article.published_at.isoformat(),
            'tickers': article.mentioned_tickers,
            'view_count': article.view_count,
            'click_count': article.click_count,
            'sentiment': {
                'label': primary_sentiment.sentiment_label if primary_sentiment else None,
                'score': float(primary_sentiment.sentiment_score) if primary_sentiment else None,
            } if primary_sentiment else None,
        })

    return Response({
        'success': True,
        'articles': articles_data,
        'count': len(articles_data)
    })


@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def news_feed_settings(request):
    """
    Get or update user's personalized news feed settings.

    GET: Retrieve current settings
    PUT: Update settings
        - followed_tickers: List of ticker symbols
        - followed_sources: List of source IDs
        - enabled_categories: List of categories
        - min_sentiment_score: Minimum sentiment score (-1.0 to 1.0)
        - exclude_neutral: Boolean
        - email_notifications: Boolean
        - sms_notifications: Boolean
        - notification_frequency: 'realtime', 'hourly', 'daily'
    """
    feed, created = NewsFeed.objects.get_or_create(user=request.user)

    if request.method == 'GET':
        return Response({
            'success': True,
            'settings': {
                'followed_stocks': [s.ticker for s in feed.followed_stocks.all()],
                'followed_sources': [s.id for s in feed.followed_sources.all()],
                'enabled_categories': feed.enabled_categories,
                'min_sentiment_score': float(feed.min_sentiment_score),
                'exclude_neutral': feed.exclude_neutral,
                'email_notifications': feed.email_notifications,
                'sms_notifications': feed.sms_notifications,
                'notification_frequency': feed.notification_frequency,
                'alert_on_very_positive': feed.alert_on_very_positive,
                'alert_on_very_negative': feed.alert_on_very_negative,
            }
        })

    else:  # PUT
        # Update followed stocks
        if 'followed_tickers' in request.data:
            tickers = request.data['followed_tickers']
            stocks = Stock.objects.filter(ticker__in=tickers)
            feed.followed_stocks.set(stocks)

        # Update followed sources
        if 'followed_sources' in request.data:
            source_ids = request.data['followed_sources']
            sources = NewsSource.objects.filter(id__in=source_ids)
            feed.followed_sources.set(sources)

        # Update other settings
        if 'enabled_categories' in request.data:
            feed.enabled_categories = request.data['enabled_categories']

        if 'min_sentiment_score' in request.data:
            feed.min_sentiment_score = request.data['min_sentiment_score']

        if 'exclude_neutral' in request.data:
            feed.exclude_neutral = request.data['exclude_neutral']

        if 'email_notifications' in request.data:
            feed.email_notifications = request.data['email_notifications']

        if 'sms_notifications' in request.data:
            feed.sms_notifications = request.data['sms_notifications']

        if 'notification_frequency' in request.data:
            feed.notification_frequency = request.data['notification_frequency']

        if 'alert_on_very_positive' in request.data:
            feed.alert_on_very_positive = request.data['alert_on_very_positive']

        if 'alert_on_very_negative' in request.data:
            feed.alert_on_very_negative = request.data['alert_on_very_negative']

        feed.save()

        return Response({
            'success': True,
            'message': 'News feed settings updated'
        })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def news_alerts(request):
    """
    Get user's news alerts.

    Query params:
    - unread_only: Show only unread alerts (default: false)
    - limit: Maximum alerts (default: 50)
    """
    unread_only = request.GET.get('unread_only', 'false').lower() == 'true'
    limit = min(int(request.GET.get('limit', 50)), 200)

    alerts = NewsAlert.objects.filter(user=request.user)

    if unread_only:
        alerts = alerts.filter(is_read=False)

    alerts = alerts.select_related('stock', 'article').order_by('-created_at')[:limit]

    alerts_data = []
    for alert in alerts:
        alerts_data.append({
            'id': alert.id,
            'ticker': alert.stock.ticker,
            'alert_type': alert.alert_type,
            'message': alert.message,
            'sentiment_score': float(alert.sentiment_score) if alert.sentiment_score else None,
            'article': {
                'id': alert.article.id,
                'title': alert.article.title,
                'url': alert.article.url,
            } if alert.article else None,
            'is_read': alert.is_read,
            'created_at': alert.created_at.isoformat(),
        })

    return Response({
        'success': True,
        'alerts': alerts_data,
        'count': len(alerts_data)
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_alert_read(request, alert_id):
    """Mark a news alert as read."""
    try:
        alert = NewsAlert.objects.get(id=alert_id, user=request.user)
        alert.is_read = True
        alert.read_at = timezone.now()
        alert.save()

        return Response({
            'success': True,
            'message': 'Alert marked as read'
        })
    except NewsAlert.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Alert not found'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([AllowAny])
def list_news_sources(request):
    """
    Get list of all active news sources.

    Query params:
    - premium_only: Show only premium sources (default: false)
    """
    premium_only = request.GET.get('premium_only', 'false').lower() == 'true'

    sources = NewsSource.objects.filter(is_active=True)

    if premium_only:
        sources = sources.filter(is_premium=True)

    sources = sources.order_by('name')

    sources_data = []
    for source in sources:
        sources_data.append({
            'id': source.id,
            'name': source.name,
            'type': source.source_type,
            'reliability_score': float(source.reliability_score),
            'is_premium': source.is_premium,
            'total_articles': source.total_articles_fetched,
        })

    return Response({
        'success': True,
        'sources': sources_data,
        'count': len(sources_data)
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def trigger_news_fetch(request):
    """
    Trigger manual news fetch from all sources (Admin/Pro only).

    Requires staff permission.
    """
    if not request.user.is_staff:
        return Response({
            'success': False,
            'error': 'Staff permission required'
        }, status=status.HTTP_403_FORBIDDEN)

    limit = min(int(request.data.get('limit', 50)), 200)

    result = NewsFetchService.fetch_all_active_sources(limit)

    return Response(result)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def trigger_sentiment_analysis(request):
    """
    Trigger manual sentiment analysis on unprocessed articles (Admin/Pro only).

    Requires staff permission.
    """
    if not request.user.is_staff:
        return Response({
            'success': False,
            'error': 'Staff permission required'
        }, status=status.HTTP_403_FORBIDDEN)

    engine = request.data.get('engine', 'vader')
    limit = min(int(request.data.get('limit', 100)), 500)

    result = SentimentAnalysisService.analyze_unprocessed_articles(engine, limit)

    return Response(result)
