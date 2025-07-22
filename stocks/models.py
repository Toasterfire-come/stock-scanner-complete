from django.db import models
from django.contrib.auth.models import User

class StockAlert(models.Model):
    ticker = models.CharField(max_length=10)
    company_name = models.CharField(max_length=255, blank=True)  # <- New field
    current_price = models.FloatField()
    volume_today = models.BigIntegerField()
    avg_volume = models.BigIntegerField(null=True, blank=True)
    dvav = models.FloatField(null=True, blank=True)
    dvsa = models.FloatField(null=True, blank=True)
    pe_ratio = models.FloatField(null=True, blank=True)
    market_cap = models.BigIntegerField(null=True, blank=True)
    note = models.TextField(blank=True)
    last_update = models.DateTimeField()
    sent = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.ticker} - {self.note or 'No Note'}"

class Membership(models.Model):
    """Track user memberships and subscription tiers"""
    TIER_CHOICES = [
        ('free', 'Free'),
        ('basic', 'Basic'),
        ('professional', 'Professional'),
        ('expert', 'Expert'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='membership')
    tier = models.CharField(max_length=20, choices=TIER_CHOICES, default='free')
    monthly_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Subscription tracking
    stripe_customer_id = models.CharField(max_length=100, blank=True, null=True)
    stripe_subscription_id = models.CharField(max_length=100, blank=True, null=True)
    subscription_status = models.CharField(max_length=20, default='active')
    
    # Usage tracking
    monthly_lookups_used = models.IntegerField(default=0)
    last_reset_date = models.DateField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.get_tier_display()}"
    
    @property
    def tier_limits(self):
        """Get lookup limits for the current tier"""
        limits = {
            'free': 15,
            'basic': 100,
            'professional': 500,
            'expert': -1  # unlimited
        }
        return limits.get(self.tier, 15)
    
    @property
    def pricing_info(self):
        """Get pricing information for the tier"""
        pricing = {
            'free': 0.00,
            'basic': 9.99,
            'professional': 29.99,
            'expert': 49.99
        }
        return pricing.get(self.tier, 0.00)
    
    def reset_monthly_usage(self):
        """Reset monthly usage counter"""
        from datetime import date
        self.monthly_lookups_used = 0
        self.last_reset_date = date.today()
        self.save()
    
    def can_make_lookup(self):
        """Check if user can make another lookup this month"""
        if self.tier == 'expert':
            return True
        return self.monthly_lookups_used < self.tier_limits

class Portfolio(models.Model):
    """User portfolio for tracking investments"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='portfolios')
    name = models.CharField(max_length=100, default='My Portfolio')
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.name}"
    
    @property
    def total_value(self):
        """Calculate total portfolio value"""
        return sum(holding.total_value for holding in self.holdings.all())
    
    @property
    def total_gain_loss(self):
        """Calculate total gain/loss"""
        return sum(holding.gain_loss for holding in self.holdings.all())
    
    @property
    def total_gain_loss_percent(self):
        """Calculate total gain/loss percentage"""
        total_cost = sum(holding.total_cost for holding in self.holdings.all())
        if total_cost == 0:
            return 0
        return (self.total_gain_loss / total_cost) * 100

class PortfolioHolding(models.Model):
    """Individual stock holdings in a portfolio"""
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name='holdings')
    ticker = models.CharField(max_length=10)
    company_name = models.CharField(max_length=255, blank=True)
    shares = models.DecimalField(max_digits=15, decimal_places=4)
    purchase_price = models.DecimalField(max_digits=12, decimal_places=4)
    purchase_date = models.DateField()
    current_price = models.DecimalField(max_digits=12, decimal_places=4, default=0)
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('portfolio', 'ticker')
        ordering = ['-last_updated']
    
    def __str__(self):
        return f"{self.portfolio.name} - {self.ticker} ({self.shares} shares)"
    
    @property
    def total_cost(self):
        """Total cost basis"""
        return self.shares * self.purchase_price
    
    @property
    def total_value(self):
        """Current total value"""
        return self.shares * self.current_price
    
    @property
    def gain_loss(self):
        """Gain or loss amount"""
        return self.total_value - self.total_cost
    
    @property
    def gain_loss_percent(self):
        """Gain or loss percentage"""
        if self.total_cost == 0:
            return 0
        return (self.gain_loss / self.total_cost) * 100

class MarketAnalysis(models.Model):
    """Market analysis and insights"""
    title = models.CharField(max_length=200)
    content = models.TextField()
    analysis_type = models.CharField(max_length=50, choices=[
        ('technical', 'Technical Analysis'),
        ('fundamental', 'Fundamental Analysis'),
        ('market_overview', 'Market Overview'),
        ('sector_analysis', 'Sector Analysis'),
        ('earnings', 'Earnings Analysis'),
    ])
    tickers = models.CharField(max_length=500, blank=True, help_text="Comma-separated list of tickers")
    sector = models.CharField(max_length=100, blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    is_premium = models.BooleanField(default=False, help_text="Premium content for paid members")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    views = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} ({self.get_analysis_type_display()})"
    
    def increment_views(self):
        """Increment view count"""
        self.views += 1
        self.save(update_fields=['views'])

class TechnicalIndicator(models.Model):
    """Technical indicators for stocks"""
    ticker = models.CharField(max_length=10, db_index=True)
    indicator_type = models.CharField(max_length=50, choices=[
        ('sma_20', '20-Day SMA'),
        ('sma_50', '50-Day SMA'),
        ('sma_200', '200-Day SMA'),
        ('ema_12', '12-Day EMA'),
        ('ema_26', '26-Day EMA'),
        ('rsi', 'RSI (14)'),
        ('macd', 'MACD'),
        ('bollinger_upper', 'Bollinger Upper'),
        ('bollinger_lower', 'Bollinger Lower'),
        ('support', 'Support Level'),
        ('resistance', 'Resistance Level'),
    ])
    value = models.DecimalField(max_digits=12, decimal_places=4)
    signal = models.CharField(max_length=20, choices=[
        ('buy', 'Buy'),
        ('sell', 'Sell'),
        ('hold', 'Hold'),
        ('neutral', 'Neutral'),
    ], default='neutral')
    confidence = models.IntegerField(default=50, help_text="Confidence level 0-100")
    calculated_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('ticker', 'indicator_type')
        ordering = ['-calculated_at']
    
    def __str__(self):
        return f"{self.ticker} - {self.get_indicator_type_display()}: {self.value}"
