"""
News Fetching Service
Multi-source news aggregation with deduplication.
"""

import hashlib
import feedparser
import requests
from datetime import datetime, timedelta
from django.utils import timezone
from django.db import transaction
import re

from stocks.models import NewsSource, NewsArticle, Stock


class NewsFetchService:
    """
    Fetches news from multiple sources (RSS, API, scraping).
    Handles deduplication, ticker extraction, and content normalization.
    """

    @staticmethod
    def fetch_from_source(source_id, limit=50):
        """
        Fetch news from a specific source.

        Args:
            source_id: NewsSource ID
            limit: Maximum articles to fetch

        Returns:
            dict: {'success': bool, 'articles_created': int, 'articles_deduplicated': int, 'message': str}
        """
        try:
            source = NewsSource.objects.get(id=source_id, is_active=True)
        except NewsSource.DoesNotExist:
            return {'success': False, 'message': 'Source not found or inactive'}

        # Check rate limiting
        if source.last_request_at:
            time_since_last = (timezone.now() - source.last_request_at).total_seconds() / 3600
            if time_since_last < (1.0 / source.requests_per_hour):
                return {'success': False, 'message': 'Rate limit exceeded'}

        # Dispatch to appropriate fetcher
        if source.source_type == 'rss':
            result = NewsFetchService._fetch_rss(source, limit)
        elif source.source_type == 'api':
            result = NewsFetchService._fetch_api(source, limit)
        elif source.source_type == 'scraper':
            result = NewsFetchService._fetch_scraper(source, limit)
        else:
            return {'success': False, 'message': 'Unsupported source type'}

        # Update source statistics
        source.last_request_at = timezone.now()
        if result['success']:
            source.total_articles_fetched += result.get('articles_created', 0)
            source.last_successful_fetch = timezone.now()
        else:
            source.total_fetch_errors += 1
        source.save()

        return result

    @staticmethod
    def _fetch_rss(source, limit):
        """Fetch from RSS feed"""
        try:
            feed = feedparser.parse(source.base_url)

            if not feed.entries:
                return {'success': False, 'message': 'No entries in feed'}

            articles_created = 0
            articles_deduplicated = 0

            for entry in feed.entries[:limit]:
                # Extract article data
                article_data = {
                    'source': source,
                    'url': entry.get('link', ''),
                    'title': entry.get('title', ''),
                    'summary': entry.get('summary', entry.get('description', '')),
                    'author': entry.get('author', ''),
                    'external_id': entry.get('id', ''),
                }

                # Parse published date
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    article_data['published_at'] = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
                else:
                    article_data['published_at'] = timezone.now()

                # Create article (with deduplication)
                created = NewsFetchService._create_article(article_data)
                if created:
                    articles_created += 1
                else:
                    articles_deduplicated += 1

            return {
                'success': True,
                'articles_created': articles_created,
                'articles_deduplicated': articles_deduplicated,
                'message': f'Fetched {articles_created} new articles from RSS'
            }

        except Exception as e:
            return {'success': False, 'message': f'RSS fetch error: {str(e)}'}

    @staticmethod
    def _fetch_api(source, limit):
        """Fetch from REST API"""
        try:
            headers = {}
            if source.api_key_required and source.api_key:
                headers['Authorization'] = f'Bearer {source.api_key}'

            response = requests.get(
                source.base_url,
                headers=headers,
                params={'limit': limit},
                timeout=30
            )
            response.raise_for_status()

            data = response.json()
            articles = data.get('articles', data.get('data', []))

            articles_created = 0
            articles_deduplicated = 0

            for item in articles[:limit]:
                article_data = {
                    'source': source,
                    'url': item.get('url', ''),
                    'title': item.get('title', ''),
                    'summary': item.get('description', item.get('summary', '')),
                    'content': item.get('content', ''),
                    'author': item.get('author', ''),
                    'external_id': item.get('id', ''),
                    'published_at': NewsFetchService._parse_timestamp(item.get('publishedAt', item.get('date'))),
                }

                created = NewsFetchService._create_article(article_data)
                if created:
                    articles_created += 1
                else:
                    articles_deduplicated += 1

            return {
                'success': True,
                'articles_created': articles_created,
                'articles_deduplicated': articles_deduplicated,
                'message': f'Fetched {articles_created} new articles from API'
            }

        except Exception as e:
            return {'success': False, 'message': f'API fetch error: {str(e)}'}

    @staticmethod
    def _fetch_scraper(source, limit):
        """Fetch from web scraper"""
        # Placeholder for scraping logic
        # In production, use BeautifulSoup/Scrapy with scraping_rules
        return {'success': False, 'message': 'Scraper not implemented'}

    @staticmethod
    def _create_article(article_data):
        """
        Create article with deduplication.

        Returns:
            bool: True if created, False if duplicate
        """
        # Generate content hash for deduplication
        hash_content = f"{article_data['title']}{article_data.get('summary', '')}"
        content_hash = hashlib.sha256(hash_content.encode()).hexdigest()

        # Check for duplicate by URL or content hash
        if NewsArticle.objects.filter(url=article_data['url']).exists():
            return False

        if NewsArticle.objects.filter(content_hash=content_hash).exists():
            return False

        # Extract tickers from title and summary
        text = f"{article_data['title']} {article_data.get('summary', '')}"
        tickers = NewsFetchService._extract_tickers(text)

        # Create article
        with transaction.atomic():
            article = NewsArticle.objects.create(
                source=article_data['source'],
                url=article_data['url'],
                title=article_data['title'],
                summary=article_data.get('summary', ''),
                content=article_data.get('content', ''),
                author=article_data.get('author', ''),
                published_at=article_data['published_at'],
                external_id=article_data.get('external_id', ''),
                content_hash=content_hash,
                mentioned_tickers=tickers,
            )

            # Link to stocks
            if tickers:
                stocks = Stock.objects.filter(ticker__in=tickers)
                article.stocks.set(stocks)

        return True

    @staticmethod
    def _extract_tickers(text):
        """
        Extract stock tickers from text.

        Returns:
            list: List of ticker symbols found
        """
        # Pattern: $AAPL or (NASDAQ:AAPL) or similar
        patterns = [
            r'\$([A-Z]{1,5})\b',  # $AAPL
            r'\(([A-Z]{1,5})\)',  # (AAPL)
            r'(?:NYSE|NASDAQ|AMEX):\s*([A-Z]{1,5})\b',  # NYSE: AAPL
        ]

        tickers = set()
        for pattern in patterns:
            matches = re.findall(pattern, text)
            tickers.update(matches)

        # Filter to valid tickers (exist in database)
        valid_tickers = list(Stock.objects.filter(ticker__in=list(tickers)).values_list('ticker', flat=True))

        return valid_tickers

    @staticmethod
    def _parse_timestamp(timestamp_str):
        """Parse various timestamp formats"""
        if not timestamp_str:
            return timezone.now()

        try:
            # Try ISO format
            return datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        except:
            pass

        try:
            # Try common formats
            from dateutil import parser
            return parser.parse(timestamp_str)
        except:
            return timezone.now()

    @staticmethod
    def fetch_all_active_sources(limit=50):
        """
        Fetch from all active news sources.

        Returns:
            dict: {'success': bool, 'total_created': int, 'sources_processed': int, 'results': list}
        """
        sources = NewsSource.objects.filter(is_active=True)

        total_created = 0
        results = []

        for source in sources:
            result = NewsFetchService.fetch_from_source(source.id, limit)
            results.append({
                'source': source.name,
                'result': result
            })
            if result['success']:
                total_created += result.get('articles_created', 0)

        return {
            'success': True,
            'total_created': total_created,
            'sources_processed': len(results),
            'results': results
        }

    @staticmethod
    def fetch_for_ticker(ticker, days_back=7, limit=100):
        """
        Fetch recent news for a specific ticker.

        Args:
            ticker: Stock ticker symbol
            days_back: Number of days to look back
            limit: Maximum articles to return

        Returns:
            QuerySet: NewsArticle queryset
        """
        try:
            stock = Stock.objects.get(ticker=ticker.upper())
        except Stock.DoesNotExist:
            return NewsArticle.objects.none()

        cutoff_date = timezone.now() - timedelta(days=days_back)

        articles = NewsArticle.objects.filter(
            stocks=stock,
            published_at__gte=cutoff_date
        ).select_related('source').prefetch_related('sentiments').order_by('-published_at')[:limit]

        return articles

    @staticmethod
    def get_trending_news(hours=24, limit=50):
        """
        Get trending news (high view count, recent).

        Returns:
            QuerySet: NewsArticle queryset
        """
        cutoff = timezone.now() - timedelta(hours=hours)

        articles = NewsArticle.objects.filter(
            published_at__gte=cutoff
        ).annotate(
            engagement_score=models.F('view_count') + models.F('click_count') * 2
        ).order_by('-engagement_score', '-published_at')[:limit]

        return articles
