from django.db import models
from django.utils import timezone


class NewsArticle(models.Model):
    """Model for storing scraped news articles"""
    headline = models.CharField(max_length=500, help_text="Article headline")
    url = models.URLField(max_length=1000, unique=True, help_text="Article URL")
    content = models.TextField(blank=True, help_text="Article content/summary")
    source = models.CharField(max_length=100, default='Yahoo Finance', help_text="News source")
    
    # Sentiment analysis
    sentiment_grade = models.CharField(max_length=2, default='N/A', help_text="Sentiment grade (A-F)")
    sentiment_score = models.IntegerField(default=0, help_text="Sentiment score (0-100)")
    sentiment_compound = models.FloatField(default=0.0, help_text="Raw compound sentiment score")
    
    # Metadata
    published_date = models.DateTimeField(default=timezone.now, help_text="Article publication date")
    scraped_date = models.DateTimeField(auto_now_add=True, help_text="When article was scraped")
    is_active = models.BooleanField(default=True, help_text="Whether article is active")
    
    # Stock relevance
    mentioned_tickers = models.JSONField(default=list, help_text="List of stock tickers mentioned")
    is_market_relevant = models.BooleanField(default=True, help_text="Whether article is market relevant")
    
    class Meta:
        ordering = ['-published_date']
        indexes = [
            models.Index(fields=['published_date', 'is_active']),
            models.Index(fields=['sentiment_grade', 'published_date']),
            models.Index(fields=['source', 'published_date']),
        ]
    
    def __str__(self):
        return f"{self.headline[:100]}... - {self.sentiment_grade}"


class NewsSource(models.Model):
    """Model for managing news sources"""
    name = models.CharField(max_length=100, unique=True)
    base_url = models.URLField()
    is_active = models.BooleanField(default=True)
    last_scraped = models.DateTimeField(null=True, blank=True)
    scrape_frequency_hours = models.IntegerField(default=6, help_text="How often to scrape in hours")
    
    def __str__(self):
        return self.name
