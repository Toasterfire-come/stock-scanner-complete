from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal
import uuid
from django.utils import timezone
from datetime import timedelta

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
    CONDITION_CHOICES = [
        ('above', 'Price Above'),
        ('below', 'Price Below'),
    ]
    
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    target_price = models.DecimalField(max_digits=10, decimal_places=2)
    condition = models.CharField(max_length=10, choices=CONDITION_CHOICES)
    email = models.EmailField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    triggered_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f'{self.email} - {self.stock.ticker} {self.condition} {self.target_price}'

# New Authentication and Billing Models
class UserProfile(models.Model):
    PLAN_CHOICES = [
        ('free', 'Free'),
        ('bronze', 'Bronze'),
        ('silver', 'Silver'),
        ('gold', 'Gold'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    plan = models.CharField(max_length=20, choices=PLAN_CHOICES, default='free')
    is_premium = models.BooleanField(default=False)
    
    # API Usage limits
    monthly_api_calls = models.IntegerField(default=0)
    daily_api_calls = models.IntegerField(default=0)
    last_api_call = models.DateTimeField(null=True, blank=True)
    last_daily_reset = models.DateField(null=True, blank=True)
    last_monthly_reset = models.DateField(null=True, blank=True)
    
    # Subscription info
    paypal_subscription_id = models.CharField(max_length=100, blank=True)
    subscription_active = models.BooleanField(default=False)
    subscription_end_date = models.DateTimeField(null=True, blank=True)
    trial_used = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.user.username} - {self.plan}'
    
    def get_plan_limits(self):
        """Get API limits for current plan"""
        limits = {
            'free': {'monthly': 15, 'daily': 15},
            'bronze': {'monthly': 2000, 'daily': 100},
            'silver': {'monthly': 10000, 'daily': 500},
            'gold': {'monthly': -1, 'daily': -1},  # -1 means unlimited
        }
        return limits.get(self.plan, limits['free'])
    
    def can_make_api_call(self):
        """Check if user can make an API call"""
        limits = self.get_plan_limits()
        
        # Reset counters if needed
        today = timezone.now().date()
        if self.last_daily_reset != today:
            self.daily_api_calls = 0
            self.last_daily_reset = today
            
        if self.last_monthly_reset is None or self.last_monthly_reset.month != today.month:
            self.monthly_api_calls = 0
            self.last_monthly_reset = today
            
        # Check limits (-1 means unlimited)
        if limits['daily'] != -1 and self.daily_api_calls >= limits['daily']:
            return False
        if limits['monthly'] != -1 and self.monthly_api_calls >= limits['monthly']:
            return False
            
        return True
    
    def increment_api_usage(self):
        """Increment API usage counters"""
        if self.can_make_api_call():
            self.daily_api_calls += 1
            self.monthly_api_calls += 1
            self.last_api_call = timezone.now()
            self.save()
            return True
        return False

class APIToken(models.Model):
    """API Token for authentication"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=255, unique=True, default=uuid.uuid4)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_used = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f'{self.user.username} - {str(self.token)[:8]}...'

class BillingHistory(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    PLAN_CHOICES = [
        ('bronze', 'Bronze'),
        ('silver', 'Silver'),
        ('gold', 'Gold'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    plan_type = models.CharField(max_length=20, choices=PLAN_CHOICES)
    billing_cycle = models.CharField(max_length=20, choices=[('monthly', 'Monthly'), ('annual', 'Annual')])
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    paypal_order_id = models.CharField(max_length=100, unique=True)
    paypal_payment_id = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    discount_code = models.CharField(max_length=50, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f'{self.user.username} - {self.plan_type} - ${self.amount}'

class UsageStats(models.Model):
    """Track daily usage statistics"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    endpoint = models.CharField(max_length=100)
    api_calls = models.IntegerField(default=0)
    
    class Meta:
        unique_together = ['user', 'date', 'endpoint']
    
    def __str__(self):
        return f'{self.user.username} - {self.date} - {self.endpoint}: {self.api_calls}'

# Keep existing Membership model for backward compatibility
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