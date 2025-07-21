# emails/models.py
from django.db import models

# Note: StockAlert model is now in the 'stocks' app
# Import it when needed: from stocks.models import StockAlert

class EmailSubscription(models.Model):
    """Model for managing email subscriptions to stock alerts"""
    email = models.EmailField()
    category = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('email', 'category')
    
    def __str__(self):
        return f"{self.email} - {self.category}"
