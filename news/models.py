from django.db import models

class NewsSource(models.Model):
    name = models.CharField(max_length=100, unique=True)
    url = models.URLField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

class NewsArticle(models.Model):
    title = models.CharField(max_length=500)
    summary = models.TextField(blank=True)
    url = models.URLField(unique=True)
    source = models.CharField(max_length=100)  # Keep for compatibility
    news_source = models.ForeignKey(NewsSource, on_delete=models.SET_NULL, null=True, blank=True)
    published_date = models.DateTimeField()
    published_at = models.DateTimeField()  # Keep for compatibility
    sentiment_score = models.DecimalField(max_digits=5, decimal_places=4, null=True, blank=True)
    sentiment_grade = models.CharField(max_length=1, null=True, blank=True)
    mentioned_tickers = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title[:100]
