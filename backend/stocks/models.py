from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal
import json

class Stock(models.Model):
    # Basic stock info
    ticker = models.CharField(max_length=10, unique=True)
    symbol = models.CharField(max_length=10, unique=True)  # Keep for compatibility
    company_name = models.CharField(max_length=200)
    name = models.CharField(max_length=200)  # Keep for compatibility
    exchange = models.CharField(max_length=50, default='NASDAQ')
    
    # Current Price Data
    current_price = models.DecimalField(max_digits=15, decimal_places=4, null=True, blank=True)
    price_change = models.DecimalField(max_digits=15, decimal_places=4, null=True, blank=True, help_text="Price change amount")
    price_change_percent = models.DecimalField(max_digits=8, decimal_places=4, null=True, blank=True, help_text="Price change percentage")
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
            models.Index(fields=['last_updated']),
            models.Index(fields=['change_percent']),
            models.Index(fields=['exchange']),
            models.Index(fields=['pe_ratio']),
            models.Index(fields=['price_change_today']),
            # Composite indexes for common query patterns
            models.Index(fields=['exchange', 'last_updated']),
            models.Index(fields=['current_price', 'last_updated']),
            models.Index(fields=['market_cap', 'last_updated']),
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

# New Portfolio Tracking Models

class UserProfile(models.Model):
    """Extended user profile with social features and billing information"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    username = models.CharField(max_length=50, unique=True, null=True, blank=True, help_text="Public username for social features")
    bio = models.TextField(max_length=500, blank=True, help_text="User biography")
    avatar_url = models.URLField(blank=True, help_text="Profile picture URL")
    
    # Contact information
    phone = models.CharField(max_length=20, blank=True, help_text="User phone number")
    company = models.CharField(max_length=100, blank=True, help_text="User company")
    
    # Subscription and billing information
    is_premium = models.BooleanField(default=False, help_text="Whether user has premium subscription")
    plan_type = models.CharField(max_length=20, default='free', help_text="Current subscription plan")
    plan_name = models.CharField(max_length=50, default='Free', help_text="Display name of current plan")
    billing_cycle = models.CharField(max_length=20, default='monthly', help_text="Billing cycle (monthly/yearly)")
    auto_renew = models.BooleanField(default=True, help_text="Whether subscription auto-renews at next_billing_date")
    subscription_status = models.CharField(max_length=20, default='active', help_text="Subscription status: active, canceled, past_due")
    api_calls_limit = models.IntegerField(default=100, help_text="API calls limit per month")
    next_billing_date = models.DateTimeField(null=True, blank=True, help_text="Next billing date")
    
    # Payment information
    card_last_four = models.CharField(max_length=4, blank=True, help_text="Last 4 digits of payment card")
    card_type = models.CharField(max_length=20, blank=True, help_text="Type of payment card (Visa, MasterCard, etc.)")
    billing_address = models.TextField(blank=True, help_text="Billing address as JSON")
    payment_updated_at = models.DateTimeField(null=True, blank=True, help_text="When payment method was last updated")
    plan_changed_at = models.DateTimeField(null=True, blank=True, help_text="When plan was last changed")
    
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


class BillingHistory(models.Model):
    """User billing and payment history"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='billing_history')
    invoice_id = models.CharField(max_length=100, unique=True, help_text="Unique invoice identifier")
    amount = models.DecimalField(max_digits=10, decimal_places=2, help_text="Payment amount")
    description = models.CharField(max_length=200, help_text="Payment description")
    status = models.CharField(max_length=50, default='Paid', help_text="Payment status")
    payment_method = models.CharField(max_length=100, default='Credit Card', help_text="Payment method used")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['invoice_id']),
        ]
    
    def __str__(self):
        return f"{self.invoice_id} - {self.user.username} - ${self.amount}"


class NotificationSettings(models.Model):
    """User notification preferences"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='notification_settings')
    
    # Trading notifications
    price_alerts = models.BooleanField(default=True, help_text="Price movement alerts")
    volume_alerts = models.BooleanField(default=True, help_text="Volume spike alerts")
    market_hours = models.BooleanField(default=False, help_text="Market hours notifications")
    
    # Portfolio notifications
    daily_summary = models.BooleanField(default=True, help_text="Daily portfolio summary")
    weekly_report = models.BooleanField(default=True, help_text="Weekly performance report")
    milestone_alerts = models.BooleanField(default=True, help_text="Portfolio milestone alerts")
    
    # News notifications
    breaking_news = models.BooleanField(default=True, help_text="Breaking market news")
    earnings_alerts = models.BooleanField(default=False, help_text="Earnings announcement alerts")
    analyst_ratings = models.BooleanField(default=False, help_text="Analyst rating changes")
    
    # Security notifications
    login_alerts = models.BooleanField(default=True, help_text="Login attempt notifications")
    billing_updates = models.BooleanField(default=True, help_text="Billing and payment updates")
    plan_updates = models.BooleanField(default=True, help_text="Plan change notifications")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Notification Settings - {self.user.username}"


class NotificationHistory(models.Model):
    """User notification history"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200, help_text="Notification title")
    message = models.TextField(help_text="Notification message")
    notification_type = models.CharField(max_length=50, default='general', help_text="Type of notification")
    is_read = models.BooleanField(default=False, help_text="Whether notification has been read")
    metadata = models.TextField(blank=True, help_text="Additional notification data as JSON")
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True, help_text="When notification was read")
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['user', 'is_read']),
            models.Index(fields=['notification_type']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.user.username}"


class UsageStats(models.Model):
    """Daily user usage statistics"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='usage_stats')
    date = models.DateField(help_text="Usage date")
    api_calls = models.IntegerField(default=0, help_text="Number of API calls made")
    requests = models.IntegerField(default=0, help_text="Total requests made")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'date']
        ordering = ['-date']
        indexes = [
            models.Index(fields=['user', '-date']),
            models.Index(fields=['date']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.date} - {self.api_calls} calls"


# Referrals

class ReferralAccount(models.Model):
    """Referral account for each inviter (can be real user or external uid)."""
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='referral_account')
    inviter_uid = models.CharField(max_length=64, db_index=True, help_text="External inviter identifier for non-auth flows")
    referral_code = models.CharField(max_length=16, unique=True, db_index=True)
    rewards_months_granted = models.IntegerField(default=0)
    free_months_redeemed = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['inviter_uid']),
        ]

    def __str__(self):
        return f"Referral {self.inviter_uid or getattr(self.user, 'username', 'anon')} ({self.referral_code})"


class ReferralInvite(models.Model):
    """Tracks invites and payment status for referral program."""
    STATUS_CHOICES = [
        ('invited', 'Invited'),
        ('accepted', 'Accepted'),
        ('paid', 'Paid'),
    ]

    inviter = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='sent_referral_invites')
    inviter_uid = models.CharField(max_length=64, db_index=True)
    invitee_email = models.EmailField(db_index=True)
    invitee_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='referral_origin')
    referral_code = models.CharField(max_length=16, db_index=True)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default='invited')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    paid_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('invitee_email', 'referral_code')
        indexes = [
            models.Index(fields=['inviter_uid', 'status']),
            models.Index(fields=['referral_code', 'status']),
        ]

    def __str__(self):
        return f"Invite {self.invitee_email} via {self.referral_code} [{self.status}]"


class ReferralRedemption(models.Model):
    """Tracks consumption of paid referrals for free months."""
    inviter_uid = models.CharField(max_length=64, db_index=True)
    months = models.PositiveIntegerField(default=1)
    invites_consumed = models.PositiveIntegerField(default=3)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['inviter_uid', 'created_at']),
        ]

    def __str__(self):
        return f"Redeemed {self.months}m using {self.invites_consumed} invites for {self.inviter_uid}"
