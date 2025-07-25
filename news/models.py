from django.db import models

class NewsArticle(models.Model):
    title = models.CharField(max_length=500)
    url = models.URLField()
    source = models.CharField(max_length=100)
    published_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
