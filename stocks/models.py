from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal

class Stock(models.Model):
    # Basic stock info
    ticker = models.CharField(max_length=10, unique=True)
    symbol = models.CharField(max_length=10, unique=True)  # Keep for compatibility
    company_name = models.CharField(max_length=200)
    name = models.CharField(max_length=200)  # Keep for compatibility
    exchange = models.CharField(max_length=50, default='NASDAQ')
    
    # Price info
    current_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    change_percent = models.DecimalField(max_digits=8, decimal_places=4, null=True, blank=True)
    volume = models.BigIntegerField(null=True, blank=True)
    market_cap = models.BigIntegerField(null=True, blank=True)
    pe_ratio = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    dividend_yield = models.DecimalField(max_digits=8, decimal_places=4, null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f'{self.ticker} - {self.company_name or self.name}'

class StockPrice(models.Model):
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'{self.stock.ticker} - ${self.price} at {self.timestamp}'

class StockAlert(models.Model):
    ALERT_TYPES = [
        ('price_above', 'Price Above'),
        ('price_below', 'Price Below'),
        ('volume_surge', 'Volume Surge'),
        ('price_change', 'Price Change %'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPES)
    target_value = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    triggered_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f'{self.user.username} - {self.stock.ticker} {self.alert_type} {self.target_value}'

class Membership(models.Model):
    PLAN_CHOICES = [
        ('free', 'Free'),
        ('basic', 'Basic - $15'),
        ('pro', 'Pro - $30'),
        ('enterprise', 'Enterprise - $100'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    plan = models.CharField(max_length=50, choices=PLAN_CHOICES, default='free')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f'{self.user.username} - {self.plan}'
