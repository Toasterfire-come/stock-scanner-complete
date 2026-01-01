from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import json
from decimal import Decimal

class NewsSource(models.Model):
    """News source configuration and metadata"""
    SOURCE_TYPES = [
        ('rss', 'RSS Feed'),
        ('api', 'API'),
        ('web_scraping', 'Web Scraping'),
        ('social_media', 'Social Media'),
        ('press_release', 'Press Release'),
    ]

    name = models.CharField(max_length=100, unique=True, help_text="Source name (e.g., Reuters, Bloomberg)")
    domain = models.CharField(max_length=200, unique=True, help_text="Source domain (e.g., reuters.com)")
    source_type = models.CharField(max_length=20, choices=SOURCE_TYPES, default='rss')
    api_endpoint = models.URLField(blank=True, help_text="API endpoint for programmatic access")
    api_key = models.CharField(max_length=500, blank=True, help_text="API key for authenticated access")
    rss_url = models.URLField(blank=True, help_text="RSS feed URL")
    is_active = models.BooleanField(default=True, help_text="Whether this source is actively monitored")
    reliability_score = models.DecimalField(max_digits=3, decimal_places=2, default=0.50, help_text="Source reliability score (0-1)")
    fetch_interval_minutes = models.PositiveIntegerField(default=15, help_text="How often to fetch from this source")
    last_fetched_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-reliability_score', 'name']
        indexes = [
            models.Index(fields=['is_active', 'last_fetched_at']),
            models.Index(fields=['source_type']),
            models.Index(fields=['domain']),
        ]

    def __str__(self):
        return f"{self.name} ({self.domain})"

class NewsArticle(models.Model):
    """Individual news article with full content and metadata"""
    ARTICLE_TYPES = [
        ('news', 'News Article'),
        ('analysis', 'Analysis'),
        ('opinion', 'Opinion'),
        ('press_release', 'Press Release'),
        ('earnings', 'Earnings Report'),
        ('transcript', 'Earnings Call Transcript'),
    ]

    # Basic article info
    title = models.CharField(max_length=500, help_text="Article headline")
    slug = models.SlugField(max_length=600, unique=True, help_text="URL-friendly identifier")
    content = models.TextField(help_text="Full article content")
    summary = models.TextField(blank=True, help_text="Article summary/excerpt")
    url = models.URLField(unique=True, help_text="Original article URL")
    article_type = models.CharField(max_length=20, choices=ARTICLE_TYPES, default='news')

    # Source and authorship
    source = models.ForeignKey(NewsSource, on_delete=models.CASCADE, related_name='articles')
    author = models.CharField(max_length=200, blank=True, help_text="Article author")
    author_bio = models.TextField(blank=True, help_text="Author biography")

    # Publication dates
    published_date = models.DateTimeField(help_text="When article was originally published")
    discovered_at = models.DateTimeField(auto_now_add=True, help_text="When we first discovered this article")
    last_updated = models.DateTimeField(auto_now=True)

    # Content metadata
    word_count = models.PositiveIntegerField(default=0)
    reading_time_minutes = models.PositiveIntegerField(default=0, help_text="Estimated reading time")
    language = models.CharField(max_length=10, default='en', help_text="Article language code")

    # Media
    image_url = models.URLField(blank=True, help_text="Featured image URL")
    video_url = models.URLField(blank=True, help_text="Video URL if applicable")

    # Stock mentions and relevance
    mentioned_tickers = models.JSONField(default=list, help_text="List of stock tickers mentioned")
    mentioned_companies = models.JSONField(default=list, help_text="List of company names mentioned")
    primary_ticker = models.CharField(max_length=10, blank=True, help_text="Most relevant stock ticker")
    relevance_score = models.DecimalField(max_digits=5, decimal_places=4, default=0, help_text="Overall relevance score")

    # NLP Analysis Results
    sentiment_score = models.DecimalField(max_digits=5, decimal_places=4, null=True, blank=True, help_text="Sentiment score (-1 to 1)")
    sentiment_confidence = models.DecimalField(max_digits=5, decimal_places=4, null=True, blank=True, help_text="Sentiment analysis confidence")
    sentiment_label = models.CharField(max_length=20, blank=True, help_text="Sentiment classification")

    # Topic classification
    topics = models.JSONField(default=list, help_text="Detected topics/categories")
    entities = models.JSONField(default=list, help_text="Named entities extracted")
    keywords = models.JSONField(default=list, help_text="Important keywords with weights")

    # Engagement metrics
    view_count = models.PositiveIntegerField(default=0)
    share_count = models.PositiveIntegerField(default=0)
    like_count = models.PositiveIntegerField(default=0)

    # Processing flags
    is_processed = models.BooleanField(default=False, help_text="Whether NLP processing is complete")
    is_active = models.BooleanField(default=True, help_text="Whether article is published/active")

    class Meta:
        ordering = ['-published_date']
        indexes = [
            models.Index(fields=['published_date']),
            models.Index(fields=['source', 'published_date']),
            models.Index(fields=['primary_ticker', 'published_date']),
            models.Index(fields=['sentiment_score']),
            models.Index(fields=['relevance_score']),
            models.Index(fields=['is_processed']),
            models.Index(fields=['is_active']),
            models.Index(fields=['slug']),
        ]

    def __str__(self):
        return f"{self.title[:50]}... ({self.source.name})"

    @property
    def sentiment_category(self):
        """Return human-readable sentiment category"""
        if self.sentiment_score is None:
            return 'neutral'
        if self.sentiment_score > 0.1:
            return 'positive'
        elif self.sentiment_score < -0.1:
            return 'negative'
        else:
            return 'neutral'

    def calculate_reading_time(self):
        """Calculate estimated reading time"""
        words_per_minute = 200  # Average reading speed
        self.reading_time_minutes = max(1, self.word_count // words_per_minute)
        self.save()

class NewsSentimentAnalysis(models.Model):
    """Detailed sentiment analysis results for news articles"""
    article = models.OneToOneField(NewsArticle, on_delete=models.CASCADE, related_name='detailed_sentiment')

    # Overall sentiment
    overall_sentiment = models.DecimalField(max_digits=5, decimal_places=4, help_text="Overall sentiment score")
    overall_confidence = models.DecimalField(max_digits=5, decimal_places=4, help_text="Overall confidence score")

    # Sentence-level sentiment
    sentence_sentiments = models.JSONField(default=list, help_text="Sentiment scores for individual sentences")

    # Aspect-based sentiment
    aspect_sentiments = models.JSONField(default=dict, help_text="Sentiment by aspect (price, earnings, etc.)")

    # Emotional analysis
    emotions = models.JSONField(default=dict, help_text="Detected emotions with intensities")

    # Subjectivity analysis
    subjectivity_score = models.DecimalField(max_digits=5, decimal_places=4, null=True, blank=True, help_text="Subjectivity vs objectivity score")

    # Sarcasm detection
    sarcasm_probability = models.DecimalField(max_digits=5, decimal_places=4, null=True, blank=True, help_text="Probability of sarcasm")

    # Model metadata
    model_used = models.CharField(max_length=100, help_text="NLP model used for analysis")
    model_version = models.CharField(max_length=50, help_text="Model version")
    processing_time_seconds = models.DecimalField(max_digits=8, decimal_places=4, help_text="Time taken for analysis")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['overall_sentiment']),
            models.Index(fields=['overall_confidence']),
        ]

    def __str__(self):
        return f"Sentiment Analysis for {self.article.title[:30]}..."

class NewsTopicClassification(models.Model):
    """Topic classification results for news articles"""
    article = models.OneToOneField(NewsArticle, on_delete=models.CASCADE, related_name='topic_classification')

    # Primary topic
    primary_topic = models.CharField(max_length=100, help_text="Most relevant topic")
    primary_topic_confidence = models.DecimalField(max_digits=5, decimal_places=4, help_text="Confidence in primary topic")

    # All topics with scores
    all_topics = models.JSONField(default=dict, help_text="All detected topics with confidence scores")

    # Industry classification
    industry_categories = models.JSONField(default=list, help_text="Relevant industry categories")

    # Market impact classification
    market_impact_level = models.CharField(max_length=20, choices=[
        ('low', 'Low Impact'),
        ('medium', 'Medium Impact'),
        ('high', 'High Impact'),
        ('critical', 'Critical Impact'),
    ], default='low')

    # Event type classification
    event_types = models.JSONField(default=list, help_text="Types of events mentioned")

    # Model metadata
    model_used = models.CharField(max_length=100, help_text="Classification model used")
    model_version = models.CharField(max_length=50, help_text="Model version")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['primary_topic']),
            models.Index(fields=['market_impact_level']),
        ]

    def __str__(self):
        return f"Topic Classification for {self.article.title[:30]}..."

class NewsEntityExtraction(models.Model):
    """Named entity extraction results"""
    article = models.OneToOneField(NewsArticle, on_delete=models.CASCADE, related_name='entity_extraction')

    # Extracted entities by type
    organizations = models.JSONField(default=list, help_text="Company and organization names")
    people = models.JSONField(default=list, help_text="Person names")
    locations = models.JSONField(default=list, help_text="Location names")
    dates = models.JSONField(default=list, help_text="Date references")
    monetary_values = models.JSONField(default=list, help_text="Monetary amounts mentioned")
    percentages = models.JSONField(default=list, help_text="Percentage values mentioned")

    # Stock-specific entities
    stock_tickers = models.JSONField(default=list, help_text="Stock ticker symbols")
    stock_names = models.JSONField(default=list, help_text="Full company names")

    # Financial metrics
    financial_metrics = models.JSONField(default=dict, help_text="Extracted financial figures")

    # Model metadata
    model_used = models.CharField(max_length=100, help_text="NER model used")
    model_version = models.CharField(max_length=50, help_text="Model version")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"Entity Extraction for {self.article.title[:30]}..."

class NewsRealtimeFeed(models.Model):
    """Real-time news feed configuration and status"""
    FEED_TYPES = [
        ('websocket', 'WebSocket'),
        ('sse', 'Server-Sent Events'),
        ('polling', 'HTTP Polling'),
        ('webhook', 'Webhook'),
    ]

    name = models.CharField(max_length=100, unique=True, help_text="Feed name")
    feed_type = models.CharField(max_length=20, choices=FEED_TYPES, default='websocket')
    endpoint_url = models.URLField(help_text="Feed endpoint URL")
    api_key = models.CharField(max_length=500, blank=True, help_text="API key for authenticated feeds")
    is_active = models.BooleanField(default=True, help_text="Whether feed is active")
    priority = models.PositiveIntegerField(default=1, help_text="Processing priority (higher = more important)")

    # Connection settings
    reconnect_interval_seconds = models.PositiveIntegerField(default=30, help_text="Reconnection interval")
    max_reconnect_attempts = models.PositiveIntegerField(default=5, help_text="Max reconnection attempts")

    # Filtering
    tickers_filter = models.JSONField(default=list, blank=True, help_text="Only process articles mentioning these tickers")
    sources_filter = models.JSONField(default=list, blank=True, help_text="Only accept articles from these sources")

    # Status tracking
    last_connected_at = models.DateTimeField(null=True, blank=True)
    last_message_at = models.DateTimeField(null=True, blank=True)
    connection_status = models.CharField(max_length=20, default='disconnected', help_text="Current connection status")
    error_count = models.PositiveIntegerField(default=0, help_text="Consecutive error count")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-priority', 'name']
        indexes = [
            models.Index(fields=['is_active', 'priority']),
            models.Index(fields=['feed_type']),
            models.Index(fields=['connection_status']),
        ]

    def __str__(self):
        return f"{self.name} ({self.feed_type})"

class NewsIngestionLog(models.Model):
    """Log of news ingestion activities"""
    LOG_TYPES = [
        ('fetch', 'Feed Fetch'),
        ('parse', 'Article Parse'),
        ('process', 'NLP Processing'),
        ('store', 'Database Store'),
        ('error', 'Error'),
        ('duplicate', 'Duplicate Detection'),
    ]

    feed = models.ForeignKey(NewsRealtimeFeed, on_delete=models.CASCADE, null=True, blank=True, related_name='logs')
    article = models.ForeignKey(NewsArticle, on_delete=models.CASCADE, null=True, blank=True, related_name='ingestion_logs')
    log_type = models.CharField(max_length=20, choices=LOG_TYPES)
    message = models.TextField(help_text="Log message")
    metadata = models.JSONField(default=dict, help_text="Additional log data")
    processing_time_ms = models.PositiveIntegerField(null=True, blank=True, help_text="Processing time in milliseconds")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['log_type', 'created_at']),
            models.Index(fields=['feed', 'created_at']),
            models.Index(fields=['article']),
        ]

    def __str__(self):
        return f"{self.log_type}: {self.message[:50]}..."

class UserNewsPreferences(models.Model):
    """User preferences for news personalization"""
    FREQUENCY_CHOICES = [
        ('realtime', 'Real-time'),
        ('hourly', 'Hourly'),
        ('daily', 'Daily Digest'),
        ('weekly', 'Weekly Summary'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='news_preferences')

    # Content preferences
    preferred_sources = models.JSONField(default=list, help_text="Preferred news sources")
    preferred_topics = models.JSONField(default=list, help_text="Preferred topics")
    followed_tickers = models.JSONField(default=list, help_text="Tickers to follow closely")
    blocked_sources = models.JSONField(default=list, help_text="Blocked news sources")

    # Delivery preferences
    notification_frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, default='daily')
    email_digest = models.BooleanField(default=True, help_text="Send email digests")
    push_notifications = models.BooleanField(default=False, help_text="Send push notifications")
    sms_alerts = models.BooleanField(default=False, help_text="Send SMS alerts for breaking news")

    # Alert thresholds
    sentiment_threshold = models.DecimalField(max_digits=3, decimal_places=2, default=0.5, help_text="Minimum sentiment score for alerts")
    relevance_threshold = models.DecimalField(max_digits=3, decimal_places=2, default=0.7, help_text="Minimum relevance score")

    # Reading preferences
    articles_per_digest = models.PositiveIntegerField(default=10, help_text="Articles per email digest")
    include_summaries = models.BooleanField(default=True, help_text="Include article summaries")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['notification_frequency']),
        ]

    def __str__(self):
        return f"News Preferences for {self.user.username}"

class NewsAnalytics(models.Model):
    """Analytics and insights from news data"""
    date = models.DateField(help_text="Date for analytics")
    ticker = models.CharField(max_length=10, help_text="Stock ticker")

    # Sentiment metrics
    avg_sentiment = models.DecimalField(max_digits=5, decimal_places=4, null=True, blank=True)
    sentiment_volatility = models.DecimalField(max_digits=5, decimal_places=4, null=True, blank=True)
    article_count = models.PositiveIntegerField(default=0)

    # Topic distribution
    top_topics = models.JSONField(default=list, help_text="Most discussed topics")
    topic_sentiments = models.JSONField(default=dict, help_text="Sentiment by topic")

    # Source reliability
    source_distribution = models.JSONField(default=dict, help_text="Articles by source")
    avg_source_reliability = models.DecimalField(max_digits=5, decimal_places=4, null=True, blank=True)

    # Market impact indicators
    breaking_news_count = models.PositiveIntegerField(default=0)
    high_impact_articles = models.PositiveIntegerField(default=0)

    # Trend analysis
    sentiment_trend = models.CharField(max_length=20, blank=True, help_text="Sentiment trend direction")
    volume_trend = models.CharField(max_length=20, blank=True, help_text="Article volume trend")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('date', 'ticker')
        ordering = ['-date', 'ticker']
        indexes = [
            models.Index(fields=['date', 'ticker']),
            models.Index(fields=['avg_sentiment']),
            models.Index(fields=['article_count']),
        ]

    def __str__(self):
        return f"News Analytics: {self.ticker} on {self.date}"
