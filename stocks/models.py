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
    
    # Current Price Data
    current_price = models.DecimalField(max_digits=15, decimal_places=4, null=True, blank=True)
    price_change_today = models.DecimalField(max_digits=15, decimal_places=4, null=True, blank=True)
    price_change_week = models.DecimalField(max_digits=15, decimal_places=4, null=True, blank=True)
    price_change_month = models.DecimalField(max_digits=15, decimal_places=4, null=True, blank=True)
    price_change_year = models.DecimalField(max_digits=15, decimal_places=4, null=True, blank=True)
    change_percent = models.DecimalField(max_digits=8, decimal_places=4, null=True, blank=True)
    
    # Bid/Ask and Range Data
    bid_price = models.DecimalField(max_digits=15, decimal_places=4, null=True, blank=True)
    ask_price = models.DecimalField(max_digits=15, decimal_places=4, null=True, blank=True)
    bid_ask_spread = models.CharField(max_length=50, blank=True)
    days_range = models.CharField(max_length=50, blank=True)
    days_low = models.DecimalField(max_digits=15, decimal_places=4, null=True, blank=True)
    days_high = models.DecimalField(max_digits=15, decimal_places=4, null=True, blank=True)
    
    # Volume Data
    volume = models.BigIntegerField(null=True, blank=True)
    volume_today = models.BigIntegerField(null=True, blank=True)
    avg_volume_3mon = models.BigIntegerField(null=True, blank=True)
    dvav = models.DecimalField(max_digits=8, decimal_places=4, null=True, blank=True, help_text="Day Volume Over Average Volume")
    shares_available = models.BigIntegerField(null=True, blank=True)
    
    # Market Data
    market_cap = models.BigIntegerField(null=True, blank=True)
    market_cap_change_3mon = models.DecimalField(max_digits=8, decimal_places=4, null=True, blank=True)
    
    # Financial Ratios
    pe_ratio = models.DecimalField(max_digits=15, decimal_places=6, null=True, blank=True)
    pe_change_3mon = models.DecimalField(max_digits=8, decimal_places=4, null=True, blank=True)
    dividend_yield = models.DecimalField(max_digits=8, decimal_places=6, null=True, blank=True)
    
    # Target and Predictions
    one_year_target = models.DecimalField(max_digits=15, decimal_places=4, null=True, blank=True)
    
    # 52 Week Range
    week_52_low = models.DecimalField(max_digits=15, decimal_places=4, null=True, blank=True)
    week_52_high = models.DecimalField(max_digits=15, decimal_places=4, null=True, blank=True)
    
    # Additional Financial Metrics
    earnings_per_share = models.DecimalField(max_digits=15, decimal_places=4, null=True, blank=True)
    book_value = models.DecimalField(max_digits=15, decimal_places=4, null=True, blank=True)
    price_to_book = models.DecimalField(max_digits=8, decimal_places=4, null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['ticker']
        indexes = [
            models.Index(fields=['ticker']),
            models.Index(fields=['market_cap']),
            models.Index(fields=['current_price']),
            models.Index(fields=['volume']),
        ]
    
    def __str__(self):
        return f'{self.ticker} - {self.company_name or self.name}'
    
    @property
    def formatted_price(self):
        """Return formatted price string"""
        if self.current_price:
            return f"${self.current_price:.2f}"
        return "$0.00"
    
    @property
    def formatted_change(self):
        """Return formatted change percentage"""
        if self.change_percent:
            return f"{self.change_percent:+.2f}%"
        return "0.00%"
    
    @property
    def formatted_volume(self):
        """Return formatted volume string"""
        if self.volume:
            return f"{self.volume:,}"
        return "0"
    
    @property
    def formatted_market_cap(self):
        """Return formatted market cap string"""
        if self.market_cap:
            if self.market_cap >= 1e12:
                return f"${self.market_cap/1e12:.2f}T"
            elif self.market_cap >= 1e9:
                return f"${self.market_cap/1e9:.2f}B"
            elif self.market_cap >= 1e6:
                return f"${self.market_cap/1e6:.2f}M"
            else:
                return f"${self.market_cap:,}"
        return "N/A"

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
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
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
