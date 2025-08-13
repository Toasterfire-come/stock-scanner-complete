from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal
import json
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from datetime import timedelta

# Import the optimized manager
from .query_optimization import OptimizedStockManager

class Stock(models.Model):
    # Use optimized manager for performance
    objects = OptimizedStockManager()
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

# New Portfolio Tracking Models

class UserProfile(models.Model):
    """Extended user profile with social features"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    username = models.CharField(max_length=50, unique=True, null=True, blank=True, help_text="Public username for social features")
    bio = models.TextField(max_length=500, blank=True, help_text="User biography")
    avatar_url = models.URLField(blank=True, help_text="Profile picture URL")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['username']),
        ]
    
    def __str__(self):
        return f'{self.user.username} - {self.username or "No public username"}'

class UserPortfolio(models.Model):
    """User stock portfolios with performance tracking"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='portfolios')
    name = models.CharField(max_length=100, help_text="Portfolio name")
    description = models.TextField(blank=True, help_text="Portfolio description")
    is_public = models.BooleanField(default=False, help_text="Whether portfolio is publicly viewable")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Performance metrics (calculated fields)
    total_value = models.DecimalField(max_digits=20, decimal_places=2, default=0, help_text="Current total portfolio value")
    total_cost = models.DecimalField(max_digits=20, decimal_places=2, default=0, help_text="Total cost basis")
    total_return = models.DecimalField(max_digits=20, decimal_places=2, default=0, help_text="Total return amount")
    total_return_percent = models.DecimalField(max_digits=8, decimal_places=4, default=0, help_text="Total return percentage")
    
    # Social features
    followers_count = models.PositiveIntegerField(default=0, help_text="Number of followers")
    likes_count = models.PositiveIntegerField(default=0, help_text="Number of likes")
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['is_public', 'total_return_percent']),
            models.Index(fields=['followers_count']),
        ]
    
    def __str__(self):
        return f'{self.user.username} - {self.name}'
    
    @property
    def performance_since_inception(self):
        """Calculate performance since portfolio creation"""
        if self.total_cost > 0:
            return (self.total_return / self.total_cost) * 100
        return 0

class PortfolioHolding(models.Model):
    """Individual stock positions within portfolios"""
    portfolio = models.ForeignKey(UserPortfolio, on_delete=models.CASCADE, related_name='holdings')
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    shares = models.DecimalField(max_digits=15, decimal_places=4, help_text="Number of shares held")
    average_cost = models.DecimalField(max_digits=12, decimal_places=4, help_text="Average cost per share")
    current_price = models.DecimalField(max_digits=12, decimal_places=4, help_text="Current price per share")
    date_added = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    
    # Alert tracking
    from_alert = models.ForeignKey(StockAlert, on_delete=models.SET_NULL, null=True, blank=True, help_text="Alert that triggered this position")
    alert_action_date = models.DateTimeField(null=True, blank=True, help_text="When alert action was taken")
    
    # Calculated performance fields
    market_value = models.DecimalField(max_digits=20, decimal_places=2, default=0, help_text="Current market value")
    unrealized_gain_loss = models.DecimalField(max_digits=20, decimal_places=2, default=0, help_text="Unrealized gain/loss")
    unrealized_gain_loss_percent = models.DecimalField(max_digits=8, decimal_places=4, default=0, help_text="Unrealized gain/loss percentage")
    
    class Meta:
        unique_together = ('portfolio', 'stock')
        ordering = ['-date_added']
        indexes = [
            models.Index(fields=['portfolio', 'stock']),
            models.Index(fields=['from_alert']),
            models.Index(fields=['unrealized_gain_loss_percent']),
        ]
    
    def __str__(self):
        return f'{self.portfolio.name} - {self.stock.ticker} ({self.shares} shares)'
    
    def update_performance(self):
        """Update calculated performance metrics"""
        self.market_value = self.shares * self.current_price
        cost_basis = self.shares * self.average_cost
        self.unrealized_gain_loss = self.market_value - cost_basis
        if cost_basis > 0:
            self.unrealized_gain_loss_percent = (self.unrealized_gain_loss / cost_basis) * 100
        self.save()

class TradeTransaction(models.Model):
    """Record of buy/sell transactions with alert tracking"""
    TRANSACTION_TYPES = [
        ('buy', 'Buy'),
        ('sell', 'Sell'),
    ]
    
    ALERT_CATEGORIES = [
        ('earnings', 'Earnings Alert'),
        ('analyst', 'Analyst Rating'),
        ('insider', 'Insider Trading'),
        ('merger', 'Merger/Acquisition'),
        ('volume', 'Volume Surge'),
        ('price', 'Price Alert'),
        ('manual', 'Manual Trade'),
    ]
    
    portfolio = models.ForeignKey(UserPortfolio, on_delete=models.CASCADE, related_name='transactions')
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    shares = models.DecimalField(max_digits=15, decimal_places=4, help_text="Number of shares")
    price = models.DecimalField(max_digits=12, decimal_places=4, help_text="Price per share")
    total_amount = models.DecimalField(max_digits=20, decimal_places=2, help_text="Total transaction amount")
    fees = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Transaction fees")
    transaction_date = models.DateTimeField(help_text="When the transaction occurred")
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Alert tracking
    from_alert = models.ForeignKey(StockAlert, on_delete=models.SET_NULL, null=True, blank=True)
    alert_category = models.CharField(max_length=20, choices=ALERT_CATEGORIES, default='manual')
    
    # Performance tracking
    realized_gain_loss = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True, help_text="Realized gain/loss for sell transactions")
    holding_period_days = models.PositiveIntegerField(null=True, blank=True, help_text="Days held for sell transactions")
    
    class Meta:
        ordering = ['-transaction_date']
        indexes = [
            models.Index(fields=['portfolio', 'transaction_date']),
            models.Index(fields=['stock', 'transaction_date']),
            models.Index(fields=['from_alert']),
            models.Index(fields=['alert_category', 'transaction_date']),
        ]
    
    def __str__(self):
        return f'{self.portfolio.name} - {self.transaction_type.upper()} {self.shares} {self.stock.ticker} @ ${self.price}'

# Watchlist Models

class UserWatchlist(models.Model):
    """User watchlists with performance metrics"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='watchlists')
    name = models.CharField(max_length=100, help_text="Watchlist name")
    description = models.TextField(blank=True, help_text="Watchlist description")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Performance tracking
    total_return_percent = models.DecimalField(max_digits=8, decimal_places=4, default=0, help_text="Average return since addition")
    best_performer = models.CharField(max_length=10, blank=True, help_text="Best performing stock ticker")
    worst_performer = models.CharField(max_length=10, blank=True, help_text="Worst performing stock ticker")
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['total_return_percent']),
        ]
    
    def __str__(self):
        return f'{self.user.username} - {self.name}'

class WatchlistItem(models.Model):
    """Individual stocks in watchlists with tracking data"""
    watchlist = models.ForeignKey(UserWatchlist, on_delete=models.CASCADE, related_name='items')
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)
    added_price = models.DecimalField(max_digits=12, decimal_places=4, help_text="Price when added to watchlist")
    current_price = models.DecimalField(max_digits=12, decimal_places=4, help_text="Current stock price")
    price_change = models.DecimalField(max_digits=12, decimal_places=4, default=0, help_text="Price change since addition")
    price_change_percent = models.DecimalField(max_digits=8, decimal_places=4, default=0, help_text="Price change percentage")
    notes = models.TextField(blank=True, help_text="User notes about this stock")
    
    # Alert settings
    target_price = models.DecimalField(max_digits=12, decimal_places=4, null=True, blank=True, help_text="Target price")
    stop_loss = models.DecimalField(max_digits=12, decimal_places=4, null=True, blank=True, help_text="Stop loss price")
    price_alert_enabled = models.BooleanField(default=False, help_text="Enable price alerts")
    news_alert_enabled = models.BooleanField(default=False, help_text="Enable news alerts")
    
    class Meta:
        unique_together = ('watchlist', 'stock')
        ordering = ['-added_at']
        indexes = [
            models.Index(fields=['watchlist', 'stock']),
            models.Index(fields=['price_change_percent']),
            models.Index(fields=['target_price']),
        ]
    
    def __str__(self):
        return f'{self.watchlist.name} - {self.stock.ticker}'
    
    def update_performance(self):
        """Update price change metrics"""
        self.price_change = self.current_price - self.added_price
        if self.added_price > 0:
            self.price_change_percent = (self.price_change / self.added_price) * 100
        self.save()

# News Personalization Models

class UserInterests(models.Model):
    """User preferences for news personalization"""
    NEWS_FREQUENCY_CHOICES = [
        ('realtime', 'Real-time'),
        ('hourly', 'Hourly'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='interests')
    followed_stocks = models.JSONField(default=list, help_text="List of stock tickers user follows")
    followed_sectors = models.JSONField(default=list, help_text="List of sectors user follows")
    preferred_categories = models.JSONField(default=list, help_text="Preferred news categories")
    news_frequency = models.CharField(max_length=20, choices=NEWS_FREQUENCY_CHOICES, default='daily')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['news_frequency']),
        ]
    
    def __str__(self):
        return f'{self.user.username} - Interests'

class PersonalizedNews(models.Model):
    """Personalized news articles for each user"""
    NEWS_CATEGORIES = [
        ('earnings', 'Earnings'),
        ('analyst', 'Analyst Rating'),
        ('insider', 'Insider Trading'),
        ('merger', 'Merger/Acquisition'),
        ('ipo', 'IPO'),
        ('dividend', 'Dividend'),
        ('guidance', 'Guidance'),
        ('partnership', 'Partnership'),
        ('regulation', 'Regulation'),
        ('general', 'General News'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='personalized_news')
    title = models.CharField(max_length=500, help_text="News article title")
    content = models.TextField(help_text="News article content/summary")
    url = models.URLField(help_text="Original article URL")
    source = models.CharField(max_length=100, help_text="News source")
    relevance_score = models.DecimalField(max_digits=5, decimal_places=2, help_text="Relevance score 0-100")
    related_stocks = models.JSONField(default=list, help_text="List of related stock tickers")
    category = models.CharField(max_length=20, choices=NEWS_CATEGORIES, default='general')
    published_at = models.DateTimeField(help_text="When article was published")
    created_at = models.DateTimeField(auto_now_add=True)
    
    # User engagement tracking
    read_at = models.DateTimeField(null=True, blank=True, help_text="When user read the article")
    clicked = models.BooleanField(default=False, help_text="Whether user clicked the article")
    
    class Meta:
        ordering = ['-published_at']
        indexes = [
            models.Index(fields=['user', 'published_at']),
            models.Index(fields=['relevance_score']),
            models.Index(fields=['category', 'published_at']),
            models.Index(fields=['clicked', 'read_at']),
        ]
    
    def __str__(self):
        return f'{self.user.username} - {self.title[:50]}...'

# Social Features

class PortfolioFollowing(models.Model):
    """Track users following other users' portfolios"""
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following')
    followed_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers')
    followed_portfolio = models.ForeignKey(UserPortfolio, on_delete=models.CASCADE, null=True, blank=True)
    followed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('follower', 'followed_user')
        indexes = [
            models.Index(fields=['follower', 'followed_user']),
            models.Index(fields=['followed_user', 'followed_at']),
        ]
    
    def __str__(self):
        return f'{self.follower.username} follows {self.followed_user.username}'

class DiscountCode(models.Model):
    """
    Model to track discount codes and their usage
    """
    code = models.CharField(max_length=20, unique=True, db_index=True)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    is_active = models.BooleanField(default=True)
    applies_to_first_payment_only = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.code} ({self.discount_percentage}% off)"

class UserDiscountUsage(models.Model):
    """
    Track which users have used which discount codes
    This creates a permanent link between user and discount for revenue tracking
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='discount_usage')
    discount_code = models.ForeignKey(DiscountCode, on_delete=models.CASCADE, related_name='user_usage')
    first_used_date = models.DateTimeField(auto_now_add=True)
    total_savings = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    class Meta:
        unique_together = ('user', 'discount_code')
        
    def __str__(self):
        return f"{self.user.username} used {self.discount_code.code}"

class RevenueTracking(models.Model):
    """
    Track monthly revenue and commission calculations
    """
    REVENUE_TYPES = [
        ('regular', 'Regular Revenue'),
        ('discount_generated', 'Discount Code Generated Revenue'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='revenue_tracking')
    discount_code = models.ForeignKey(DiscountCode, on_delete=models.SET_NULL, null=True, blank=True)
    revenue_type = models.CharField(max_length=20, choices=REVENUE_TYPES, default='regular')
    
    # Financial tracking
    original_amount = models.DecimalField(max_digits=10, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    final_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Temporal tracking
    payment_date = models.DateTimeField()
    month_year = models.CharField(max_length=7, db_index=True)  # Format: "2024-01"
    
    # Commission tracking
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2, default=20.00)  # 20%
    commission_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        # Auto-calculate commission if this is discount-generated revenue
        if self.revenue_type == 'discount_generated' and self.discount_code:
            self.commission_amount = (self.final_amount * self.commission_rate) / 100
        
        # Auto-set month_year from payment_date
        if self.payment_date:
            self.month_year = self.payment_date.strftime('%Y-%m')
            
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.user.username} - ${self.final_amount} ({self.month_year})"

class MonthlyRevenueSummary(models.Model):
    """
    Aggregated monthly revenue data for efficient reporting
    """
    month_year = models.CharField(max_length=7, unique=True, db_index=True)
    
    # Total revenue breakdown
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    regular_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    discount_generated_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    
    # Discount-specific tracking
    total_discount_savings = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    total_commission_owed = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    
    # User counts
    total_paying_users = models.IntegerField(default=0)
    new_discount_users = models.IntegerField(default=0)
    existing_discount_users = models.IntegerField(default=0)
    
    # Metadata
    last_updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Revenue Summary {self.month_year}: ${self.total_revenue}"

# ===== USER SUBSCRIPTION AND PAYMENT MODELS =====

class UserTier(models.TextChoices):
    """User subscription tiers with different features and rate limits"""
    FREE = 'free', 'Free'
    BASIC = 'basic', 'Basic'
    PRO = 'pro', 'Pro'
    ENTERPRISE = 'enterprise', 'Enterprise'

class UserProfile(models.Model):
    """Extended user profile with subscription and settings"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    tier = models.CharField(max_length=20, choices=UserTier.choices, default=UserTier.FREE)
    subscription_active = models.BooleanField(default=False)
    subscription_start = models.DateTimeField(null=True, blank=True)
    subscription_end = models.DateTimeField(null=True, blank=True)
    paypal_subscription_id = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Frontend optimization preferences
    enable_frontend_optimization = models.BooleanField(default=True)
    enable_client_side_charts = models.BooleanField(default=True)
    enable_progressive_loading = models.BooleanField(default=True)
    max_cache_size_mb = models.IntegerField(default=50)  # Browser cache limit
    
    # API usage tracking
    api_calls_today = models.IntegerField(default=0)
    api_calls_this_month = models.IntegerField(default=0)
    last_api_call = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'user_profiles'
        
    def __str__(self):
        return f"{self.user.username} - {self.tier}"
    
    @property
    def is_subscription_active(self):
        """Check if subscription is currently active"""
        if not self.subscription_active:
            return False
        if self.subscription_end and timezone.now() > self.subscription_end:
            return False
        return True
    
    def get_rate_limits(self):
        """Get rate limits based on user tier"""
        limits = {
            UserTier.FREE: {
                'api_calls_per_hour': 15,
                'api_calls_per_day': 15,
                'max_watchlist_items': 3,
                'real_time_data': False,
                'advanced_charts': False,
                'data_export': False,
                'price_monthly': 0.00,
                'price_yearly': 0.00
            },
            UserTier.BASIC: {
                'api_calls_per_hour': 100,
                'api_calls_per_day': 1500,
                'max_watchlist_items': 25,
                'real_time_data': True,
                'advanced_charts': True,
                'data_export': True,
                'price_monthly': 24.99,
                'price_yearly': 274.89  # 10% annual discount
            },
            UserTier.PRO: {
                'api_calls_per_hour': 300,
                'api_calls_per_day': 5000,
                'max_watchlist_items': 100,
                'real_time_data': True,
                'advanced_charts': True,
                'data_export': True,
                'price_monthly': 49.99,
                'price_yearly': 549.89  # 10% annual discount
            },
            UserTier.ENTERPRISE: {
                'api_calls_per_hour': 9999,  # Effectively unlimited
                'api_calls_per_day': 999999,  # Effectively unlimited
                'max_watchlist_items': 9999,  # Effectively unlimited
                'real_time_data': True,
                'advanced_charts': True,
                'data_export': True,
                'price_monthly': 79.99,
                'price_yearly': 879.89  # 10% annual discount
            }
        }
        return limits.get(self.tier, limits[UserTier.FREE])
    
    def can_make_api_call(self):
        """Check if user can make another API call based on their tier limits"""
        limits = self.get_rate_limits()
        
        # Check daily limit
        if self.api_calls_today >= limits['api_calls_per_day']:
            return False, "Daily API limit exceeded"
        
        # Check hourly limit (simplified - would need more sophisticated tracking)
        
        if self.last_api_call:
            one_hour_ago = timezone.now() - timedelta(hours=1)
            if self.last_api_call > one_hour_ago:
                # In a real implementation, you'd track hourly calls more precisely
                estimated_hourly_calls = min(self.api_calls_today, limits['api_calls_per_hour'])
                if estimated_hourly_calls >= limits['api_calls_per_hour']:
                    return False, "Hourly API limit exceeded"
        
        return True, "OK"
    
    def increment_api_usage(self):
        """Increment API usage counters"""
        self.api_calls_today += 1
        self.api_calls_this_month += 1
        self.last_api_call = timezone.now()
        self.save(update_fields=['api_calls_today', 'api_calls_this_month', 'last_api_call'])

class PaymentPlan(models.Model):
    """Available payment plans"""
    name = models.CharField(max_length=50)
    tier = models.CharField(max_length=20, choices=UserTier.choices)
    price_monthly = models.DecimalField(max_digits=10, decimal_places=2)
    price_yearly = models.DecimalField(max_digits=10, decimal_places=2)
    paypal_plan_id_monthly = models.CharField(max_length=100, blank=True)
    paypal_plan_id_yearly = models.CharField(max_length=100, blank=True)
    features = models.JSONField(default=dict)  # Store plan features as JSON
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'payment_plans'
        
    def __str__(self):
        return f"{self.name} - ${self.price_monthly}/month"

class PaymentTransaction(models.Model):
    """Track all payment transactions"""
    TRANSACTION_STATUS = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    plan = models.ForeignKey(PaymentPlan, on_delete=models.CASCADE)
    paypal_transaction_id = models.CharField(max_length=100, unique=True)
    paypal_subscription_id = models.CharField(max_length=100, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    status = models.CharField(max_length=20, choices=TRANSACTION_STATUS, default='pending')
    billing_cycle = models.CharField(max_length=10, choices=[('monthly', 'Monthly'), ('yearly', 'Yearly')])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # PayPal webhook data
    webhook_data = models.JSONField(default=dict, blank=True)
    
    class Meta:
        db_table = 'payment_transactions'
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.user.username} - {self.plan.name} - {self.status}"

class UserAPIUsage(models.Model):
    """Detailed API usage tracking for analytics and billing"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='api_usage')
    endpoint = models.CharField(max_length=200)
    method = models.CharField(max_length=10)
    timestamp = models.DateTimeField(auto_now_add=True)
    response_time_ms = models.IntegerField()
    status_code = models.IntegerField()
    user_tier = models.CharField(max_length=20, choices=UserTier.choices)
    
    # Frontend optimization specific tracking
    frontend_optimized = models.BooleanField(default=False)
    data_size_bytes = models.IntegerField(default=0)
    cache_hit = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'user_api_usage'
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['endpoint', 'timestamp']),
            models.Index(fields=['user_tier', 'timestamp']),
        ]

class UserSettings(models.Model):
    """User-specific settings for frontend optimization and features"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='settings')
    
    # Frontend optimization settings
    enable_virtual_scrolling = models.BooleanField(default=True)
    enable_fuzzy_search = models.BooleanField(default=True)
    enable_real_time_charts = models.BooleanField(default=True)
    chart_theme = models.CharField(max_length=20, choices=[('light', 'Light'), ('dark', 'Dark')], default='light')
    items_per_page = models.IntegerField(default=50, validators=[MinValueValidator(10), MaxValueValidator(200)])
    
    # Data preferences
    default_watchlist_view = models.CharField(max_length=20, choices=[('grid', 'Grid'), ('list', 'List'), ('chart', 'Chart')], default='grid')
    auto_refresh_interval = models.IntegerField(default=30, help_text="Seconds between auto-refresh")
    enable_notifications = models.BooleanField(default=True)
    
    # Privacy settings
    share_usage_analytics = models.BooleanField(default=True)
    enable_performance_tracking = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_settings'
        
    def __str__(self):
        return f"Settings for {self.user.username}"

# ===== SIGNALS FOR AUTO-CREATION =====

from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_user_profile_and_settings(sender, instance, created, **kwargs):
    """Automatically create UserProfile and UserSettings when a new user is created"""
    if created:
        UserProfile.objects.create(user=instance)
        UserSettings.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile_and_settings(sender, instance, **kwargs):
    """Save UserProfile and UserSettings when user is saved"""
    if hasattr(instance, 'profile'):
        instance.profile.save()
    else:
        UserProfile.objects.create(user=instance)
        
    if hasattr(instance, 'settings'):
        instance.settings.save()
    else:
        UserSettings.objects.create(user=instance)
