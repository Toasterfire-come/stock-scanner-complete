from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal
import json
from django.utils import timezone

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
    
    # Valuation & technical metrics (stored as JSON for flexibility)
    valuation_json = models.JSONField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['ticker']
        indexes = [
            # Single field indexes
            models.Index(fields=['ticker']),
            models.Index(fields=['market_cap']),
            models.Index(fields=['current_price']),
            models.Index(fields=['volume']),
            models.Index(fields=['last_updated']),
            models.Index(fields=['change_percent']),
            models.Index(fields=['exchange']),
            models.Index(fields=['pe_ratio']),
            models.Index(fields=['price_change_today']),
            # Composite indexes for common query patterns (security improvements)
            models.Index(fields=['exchange', 'volume']),
            models.Index(fields=['exchange', 'market_cap']),
            models.Index(fields=['exchange', 'current_price']),
            models.Index(fields=['exchange', 'last_updated']),
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


class StockFundamentals(models.Model):
    """
    Comprehensive fundamental data model for stock valuation (Phase 2 MVP).
    Stores 50+ dedicated fields for valuation analysis.
    """
    stock = models.OneToOneField(Stock, on_delete=models.CASCADE, related_name='fundamentals', primary_key=True)
    
    # Price & Valuation Metrics
    pe_ratio = models.DecimalField(max_digits=15, decimal_places=4, null=True, blank=True, help_text="Price to Earnings ratio")
    forward_pe = models.DecimalField(max_digits=15, decimal_places=4, null=True, blank=True, help_text="Forward P/E ratio")
    peg_ratio = models.DecimalField(max_digits=15, decimal_places=4, null=True, blank=True, help_text="PEG ratio")
    price_to_sales = models.DecimalField(max_digits=15, decimal_places=4, null=True, blank=True, help_text="Price to Sales ratio")
    price_to_book = models.DecimalField(max_digits=15, decimal_places=4, null=True, blank=True, help_text="Price to Book ratio")
    ev_to_revenue = models.DecimalField(max_digits=15, decimal_places=4, null=True, blank=True, help_text="Enterprise Value to Revenue")
    ev_to_ebitda = models.DecimalField(max_digits=15, decimal_places=4, null=True, blank=True, help_text="Enterprise Value to EBITDA")
    enterprise_value = models.BigIntegerField(null=True, blank=True, help_text="Enterprise Value")
    
    # Profitability Metrics
    gross_margin = models.DecimalField(max_digits=8, decimal_places=4, null=True, blank=True, help_text="Gross profit margin")
    operating_margin = models.DecimalField(max_digits=8, decimal_places=4, null=True, blank=True, help_text="Operating margin")
    profit_margin = models.DecimalField(max_digits=8, decimal_places=4, null=True, blank=True, help_text="Net profit margin")
    roe = models.DecimalField(max_digits=8, decimal_places=4, null=True, blank=True, help_text="Return on Equity")
    roa = models.DecimalField(max_digits=8, decimal_places=4, null=True, blank=True, help_text="Return on Assets")
    roic = models.DecimalField(max_digits=8, decimal_places=4, null=True, blank=True, help_text="Return on Invested Capital")
    
    # Growth Metrics
    revenue_growth_yoy = models.DecimalField(max_digits=8, decimal_places=4, null=True, blank=True, help_text="YoY revenue growth")
    revenue_growth_3y = models.DecimalField(max_digits=8, decimal_places=4, null=True, blank=True, help_text="3-year revenue CAGR")
    revenue_growth_5y = models.DecimalField(max_digits=8, decimal_places=4, null=True, blank=True, help_text="5-year revenue CAGR")
    earnings_growth_yoy = models.DecimalField(max_digits=8, decimal_places=4, null=True, blank=True, help_text="YoY earnings growth")
    earnings_growth_5y = models.DecimalField(max_digits=8, decimal_places=4, null=True, blank=True, help_text="5-year EPS CAGR")
    fcf_growth_yoy = models.DecimalField(max_digits=8, decimal_places=4, null=True, blank=True, help_text="YoY free cash flow growth")
    
    # Financial Health Metrics
    current_ratio = models.DecimalField(max_digits=8, decimal_places=4, null=True, blank=True, help_text="Current ratio")
    quick_ratio = models.DecimalField(max_digits=8, decimal_places=4, null=True, blank=True, help_text="Quick ratio")
    debt_to_equity = models.DecimalField(max_digits=15, decimal_places=4, null=True, blank=True, help_text="Debt to equity ratio")
    debt_to_assets = models.DecimalField(max_digits=8, decimal_places=4, null=True, blank=True, help_text="Debt to assets ratio")
    interest_coverage = models.DecimalField(max_digits=15, decimal_places=4, null=True, blank=True, help_text="Interest coverage ratio")
    altman_z_score = models.DecimalField(max_digits=8, decimal_places=4, null=True, blank=True, help_text="Altman Z-Score")
    piotroski_f_score = models.IntegerField(null=True, blank=True, help_text="Piotroski F-Score (0-9)")
    
    # Cash Flow Metrics
    operating_cash_flow = models.BigIntegerField(null=True, blank=True, help_text="Operating cash flow")
    free_cash_flow = models.BigIntegerField(null=True, blank=True, help_text="Free cash flow")
    fcf_per_share = models.DecimalField(max_digits=15, decimal_places=4, null=True, blank=True, help_text="FCF per share")
    fcf_yield = models.DecimalField(max_digits=8, decimal_places=4, null=True, blank=True, help_text="FCF yield")
    cash_conversion = models.DecimalField(max_digits=8, decimal_places=4, null=True, blank=True, help_text="Cash conversion ratio")
    
    # Dividend Metrics
    dividend_yield = models.DecimalField(max_digits=8, decimal_places=4, null=True, blank=True, help_text="Dividend yield")
    dividend_payout_ratio = models.DecimalField(max_digits=8, decimal_places=4, null=True, blank=True, help_text="Dividend payout ratio")
    years_dividend_growth = models.IntegerField(null=True, blank=True, help_text="Consecutive years of dividend growth")
    
    # Calculated Valuations (Fair Values)
    dcf_value = models.DecimalField(max_digits=15, decimal_places=4, null=True, blank=True, help_text="DCF fair value")
    epv_value = models.DecimalField(max_digits=15, decimal_places=4, null=True, blank=True, help_text="EPV fair value")
    graham_number = models.DecimalField(max_digits=15, decimal_places=4, null=True, blank=True, help_text="Graham Number")
    peg_fair_value = models.DecimalField(max_digits=15, decimal_places=4, null=True, blank=True, help_text="PEG-based fair value")
    relative_value_score = models.DecimalField(max_digits=8, decimal_places=4, null=True, blank=True, help_text="Relative value vs sector")
    
    # Composite Scores
    valuation_score = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, help_text="Composite valuation score (0-100)")
    valuation_status = models.CharField(max_length=50, blank=True, help_text="Status: significantly_undervalued, undervalued, fair_value, etc.")
    recommendation = models.CharField(max_length=20, blank=True, help_text="STRONG BUY, BUY, HOLD, SELL, STRONG SELL")
    confidence = models.CharField(max_length=10, blank=True, help_text="high, medium, low")
    strength_score = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, help_text="Financial strength score (0-100)")
    strength_grade = models.CharField(max_length=2, blank=True, help_text="Strength grade: A, B, C, D, F")
    
    # Metadata
    sector = models.CharField(max_length=100, blank=True, help_text="Company sector")
    industry = models.CharField(max_length=100, blank=True, help_text="Company industry")
    last_updated = models.DateTimeField(auto_now=True)
    data_quality = models.CharField(max_length=20, default='complete', help_text="Data quality: complete, partial, insufficient")
    
    class Meta:
        indexes = [
            models.Index(fields=['valuation_score']),
            models.Index(fields=['valuation_status']),
            models.Index(fields=['strength_score']),
            models.Index(fields=['sector']),
            models.Index(fields=['last_updated']),
        ]
        verbose_name_plural = "Stock fundamentals"
    
    def __str__(self):
        return f'{self.stock.ticker} - Fundamentals'
    
    @property
    def is_undervalued(self):
        """Check if stock is undervalued (score >= 55)"""
        return self.valuation_score and self.valuation_score >= 55
    
    @property
    def margin_of_safety(self):
        """Calculate margin of safety based on fair values"""
        if not self.stock.current_price:
            return None
        fair_values = [v for v in [self.dcf_value, self.epv_value, self.graham_number, self.peg_fair_value] if v]
        if not fair_values:
            return None
        avg_fair = sum(fair_values) / len(fair_values)
        return ((avg_fair / float(self.stock.current_price)) - 1) * 100


class StockPrice(models.Model):
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, db_index=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            # Performance: Composite index for time-series queries
            models.Index(fields=['stock', 'timestamp']),
            models.Index(fields=['timestamp']),
        ]

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

# DEPRECATED: This model is being replaced by billing.models.Subscription
# TODO: Migrate existing Membership data to Subscription model, then remove this
#
# class Membership(models.Model):
#     PLAN_CHOICES = [
#         ('free', 'Free'),
#         ('basic', 'Basic - $15'),
#         ('pro', 'Pro - $30'),
#         ('enterprise', 'Enterprise - $100'),
#     ]
#
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     plan = models.CharField(max_length=50, choices=PLAN_CHOICES, default='free')
#     is_active = models.BooleanField(default=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     expires_at = models.DateTimeField(null=True, blank=True)
#
#     def __str__(self):
#         return f'{self.user.username} - {self.plan}'

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


# Indicators
class CustomIndicator(models.Model):
    """User-defined custom indicators (formula or JS mode)."""
    MODE_CHOICES = [
        ('formula', 'Formula'),
        ('js', 'JavaScript'),
    ]
    PRIVACY_CHOICES = [
        ('private', 'Private'),
        ('unlisted', 'Unlisted'),
        ('public', 'Public'),
    ]

    id = models.CharField(max_length=64, primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='custom_indicators')
    name = models.CharField(max_length=150)
    mode = models.CharField(max_length=16, choices=MODE_CHOICES, default='formula')
    formula = models.TextField(blank=True)
    js_code = models.TextField(blank=True)
    params = models.JSONField(default=list, help_text="Parameter schema array")
    palette = models.JSONField(default=dict, help_text="Color configuration for rendering")
    privacy = models.CharField(max_length=16, choices=PRIVACY_CHOICES, default='private')
    version = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['user', '-updated_at']),
            models.Index(fields=['privacy', '-updated_at']),
        ]

    def __str__(self):
        return f"{self.name} v{self.version} ({self.mode})"

# Screeners
class Screener(models.Model):
    """Saved stock screener definitions with JSON criteria."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='screeners', null=True, blank=True)
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    criteria = models.JSONField(default=list, help_text="Array of criteria objects or a criteria mapping")
    is_public = models.BooleanField(default=False)
    last_run = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['is_public', '-updated_at']),
            models.Index(fields=['user', '-updated_at']),
        ]

    def __str__(self):
        owner = self.user.username if self.user else 'anon'
        return f"{self.name} ({owner})"

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

    # SMS preferences
    sms_enabled = models.BooleanField(default=False, help_text="Enable SMS notifications")
    sms_verified = models.BooleanField(default=False, help_text="Phone verified for SMS")
    sms_price_alerts = models.BooleanField(default=False, help_text="SMS for price alerts")
    sms_breaking_news = models.BooleanField(default=False, help_text="SMS for breaking news")
    sms_milestone_alerts = models.BooleanField(default=False, help_text="SMS for portfolio milestones")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Notification Settings - {self.user.username}"


class SMSMessage(models.Model):
    """Queued SMS messages (local provider marks as sent)."""
    STATUS_CHOICES = [
        ('queued', 'Queued'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sms_messages')
    to_number = models.CharField(max_length=32)
    body = models.CharField(max_length=1600)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='queued')
    error = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"SMS to {self.to_number} ({self.status})"


class SMSVerification(models.Model):
    """Verification code for SMS phone number."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='sms_verification')
    phone_number = models.CharField(max_length=32)
    code_plain = models.CharField(max_length=12)
    expires_at = models.DateTimeField()
    attempts = models.IntegerField(default=0)
    verified_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['expires_at']),
        ]

    def __str__(self):
        return f"SMSVerify {self.user.username} {self.phone_number}"


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


# Partner referral analytics
class ReferralClickEvent(models.Model):
    """Tracks referral clicks for partner codes (e.g., ADAM50)."""
    code = models.CharField(max_length=50, db_index=True)
    session_id = models.CharField(max_length=64, blank=True, db_index=True)
    ip_hash = models.CharField(max_length=64, blank=True, db_index=True)
    user_agent = models.TextField(blank=True)
    occurred_at = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        indexes = [
            models.Index(fields=['code', 'occurred_at']),
            models.Index(fields=['ip_hash', 'occurred_at']),
        ]


class ReferralTrialEvent(models.Model):
    """Tracks trial start events attributed to a referral code."""
    code = models.CharField(max_length=50, db_index=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    occurred_at = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        indexes = [
            models.Index(fields=['code', 'occurred_at']),
            models.Index(fields=['user', 'occurred_at']),
        ]

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


# ============================================================================
# PHASE 4: AI BACKTESTING SYSTEM
# ============================================================================

class BacktestRun(models.Model):
    """AI-powered backtesting with natural language strategy input"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    CATEGORY_CHOICES = [
        ('day_trading', 'Day Trading'),
        ('swing_trading', 'Swing Trading'),
        ('long_term', 'Long Term'),
    ]
    
    # User & Strategy
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='backtest_runs')
    name = models.CharField(max_length=200, help_text="Strategy name")
    strategy_text = models.TextField(help_text="Natural language strategy description")
    generated_code = models.TextField(blank=True, help_text="AI-generated Python code")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='day_trading')
    
    # Backtest Parameters
    symbols = models.JSONField(help_text="List of symbols to test")
    start_date = models.DateField(help_text="Backtest start date")
    end_date = models.DateField(help_text="Backtest end date")
    initial_capital = models.DecimalField(max_digits=15, decimal_places=2, default=10000.00)
    
    # Execution
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    error_message = models.TextField(blank=True)
    
    # Results
    total_return = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Total return percentage")
    annualized_return = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    sharpe_ratio = models.DecimalField(max_digits=8, decimal_places=4, null=True, blank=True)
    max_drawdown = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    win_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Percentage of winning trades")
    profit_factor = models.DecimalField(max_digits=8, decimal_places=4, null=True, blank=True)
    total_trades = models.IntegerField(null=True, blank=True)
    winning_trades = models.IntegerField(null=True, blank=True)
    losing_trades = models.IntegerField(null=True, blank=True)
    
    # Composite Score (0-100)
    composite_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, 
                                         help_text="Overall strategy score 0-100")
    
    # Trade Details
    trades_data = models.JSONField(null=True, blank=True, help_text="Individual trade records")
    equity_curve = models.JSONField(null=True, blank=True, help_text="Portfolio value over time")
    
    # Visibility & Sharing
    is_public = models.BooleanField(default=False)
    is_baseline = models.BooleanField(default=False, help_text="Official baseline strategy")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['status']),
            models.Index(fields=['category', '-composite_score']),
            models.Index(fields=['-composite_score']),
            models.Index(fields=['is_baseline']),
        ]
    
    def __str__(self):
        return f"{self.name} by {self.user.username} - {self.status}"


class BaselineStrategy(models.Model):
    """Pre-built baseline strategies for comparison"""
    CATEGORY_CHOICES = BacktestRun.CATEGORY_CHOICES
    
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    strategy_code = models.TextField(help_text="Python strategy implementation")
    
    # Average Results (pre-computed)
    avg_total_return = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    avg_sharpe_ratio = models.DecimalField(max_digits=8, decimal_places=4, null=True, blank=True)
    avg_max_drawdown = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['category', 'name']
        verbose_name_plural = "Baseline strategies"
    
    def __str__(self):
        return f"{self.name} ({self.category})"


# ============================================================================
# PHASE 5: VALUE HUNTER PORTFOLIO
# ============================================================================

class ValueHunterWeek(models.Model):
    """Weekly Value Hunter portfolio performance"""
    week_number = models.IntegerField(help_text="ISO week number")
    year = models.IntegerField()
    week_start = models.DateField(help_text="Monday of the week")
    week_end = models.DateField(help_text="Friday of the week")
    
    # Capital
    starting_capital = models.DecimalField(max_digits=15, decimal_places=2, default=10000.00)
    ending_capital = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    
    # Returns
    weekly_return = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, 
                                       help_text="Weekly return percentage")
    cumulative_return = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True,
                                          help_text="Cumulative return since inception")
    
    # Benchmark Comparison (S&P 500)
    benchmark_return = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    alpha = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True,
                               help_text="Weekly alpha vs benchmark")
    
    # Status
    status = models.CharField(max_length=20, default='pending', 
                            choices=[('pending', 'Pending'), ('active', 'Active'), 
                                   ('completed', 'Completed')])
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    executed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-year', '-week_number']
        unique_together = ['year', 'week_number']
        indexes = [
            models.Index(fields=['-year', '-week_number']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"Value Hunter Week {self.week_number} {self.year}"


class ValueHunterPosition(models.Model):
    """Individual stock positions in Value Hunter portfolio"""
    week = models.ForeignKey(ValueHunterWeek, on_delete=models.CASCADE, related_name='positions')
    symbol = models.CharField(max_length=10, db_index=True)
    stock = models.ForeignKey(Stock, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Selection Criteria
    valuation_score = models.DecimalField(max_digits=5, decimal_places=2, 
                                         help_text="Valuation score at selection")
    rank = models.IntegerField(help_text="Rank in top 10 (1-10)")
    
    # Position Details
    shares = models.DecimalField(max_digits=15, decimal_places=4)
    entry_price = models.DecimalField(max_digits=15, decimal_places=4)
    exit_price = models.DecimalField(max_digits=15, decimal_places=4, null=True, blank=True)
    
    # Entry/Exit Times
    entry_datetime = models.DateTimeField(help_text="Entry time (Monday 9:35 AM ET)")
    exit_datetime = models.DateTimeField(null=True, blank=True, help_text="Exit time (Friday 3:55 PM ET)")
    
    # Performance
    return_percent = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    return_amount = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    
    class Meta:
        ordering = ['week', 'rank']
        unique_together = ['week', 'symbol']
        indexes = [
            models.Index(fields=['week', 'rank']),
            models.Index(fields=['symbol']),
        ]
    
    def __str__(self):
        return f"{self.symbol} - Week {self.week.week_number} {self.week.year} (Rank #{self.rank})"




# ============================================================================
# PAPER TRADING SYSTEM MODELS
# Append this to stocks/models.py
# ============================================================================

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class PaperTradingAccount(models.Model):
    """
    Virtual trading account for paper trading simulation.
    Separate ledger from real portfolio data.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='paper_accounts')
    name = models.CharField(max_length=100, default='Paper Trading Account')

    # Account Balance
    initial_balance = models.DecimalField(max_digits=15, decimal_places=2, default=100000.00,
                                         help_text="Starting virtual cash")
    cash_balance = models.DecimalField(max_digits=15, decimal_places=2, default=100000.00,
                                      help_text="Current available cash")
    equity_value = models.DecimalField(max_digits=15, decimal_places=2, default=0.00,
                                      help_text="Current value of open positions")
    total_value = models.DecimalField(max_digits=15, decimal_places=2, default=100000.00,
                                     help_text="Cash + Equity")

    # Performance Metrics
    total_return = models.DecimalField(max_digits=10, decimal_places=2, default=0.00,
                                      help_text="Total return percentage")
    total_profit_loss = models.DecimalField(max_digits=15, decimal_places=2, default=0.00,
                                           help_text="Total P/L in dollars")
    realized_pl = models.DecimalField(max_digits=15, decimal_places=2, default=0.00,
                                     help_text="Realized profit/loss from closed trades")
    unrealized_pl = models.DecimalField(max_digits=15, decimal_places=2, default=0.00,
                                       help_text="Unrealized profit/loss from open positions")

    # Trading Statistics
    total_trades = models.IntegerField(default=0)
    winning_trades = models.IntegerField(default=0)
    losing_trades = models.IntegerField(default=0)
    win_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00,
                                  help_text="Percentage of winning trades")

    # Risk Metrics
    max_drawdown = models.DecimalField(max_digits=10, decimal_places=2, default=0.00,
                                      help_text="Maximum peak-to-trough decline")
    sharpe_ratio = models.DecimalField(max_digits=8, decimal_places=4, null=True, blank=True,
                                      help_text="Risk-adjusted return metric")

    # Account Settings
    is_active = models.BooleanField(default=True)
    allow_shorting = models.BooleanField(default=False, help_text="Allow short selling (Pro tier)")
    max_position_size_pct = models.DecimalField(max_digits=5, decimal_places=2, default=25.00,
                                               help_text="Max position size as % of account")

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    last_trade_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['-total_return']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.name} (${self.total_value:,.2f})"

    def update_balances(self):
        """Recalculate account balances based on open positions"""
        from decimal import Decimal

        # Get open positions
        open_positions = self.paper_trades.filter(status='open')

        # Calculate equity value
        equity_total = Decimal('0.00')
        unrealized_total = Decimal('0.00')

        for position in open_positions:
            position.update_current_value()
            equity_total += position.current_value or Decimal('0.00')
            unrealized_total += position.unrealized_pl or Decimal('0.00')

        self.equity_value = equity_total
        self.unrealized_pl = unrealized_total
        self.total_value = self.cash_balance + self.equity_value

        # Calculate total return
        if self.initial_balance > 0:
            self.total_return = ((self.total_value - self.initial_balance) / self.initial_balance) * 100

        self.total_profit_loss = self.realized_pl + self.unrealized_pl

        # Update win rate
        if self.total_trades > 0:
            self.win_rate = (self.winning_trades / self.total_trades) * 100

        self.save()


class PaperTrade(models.Model):
    """
    Individual paper trade with support for multiple order types.
    Deterministic fill simulation based on market data.
    """
    ORDER_TYPES = [
        ('market', 'Market Order'),
        ('limit', 'Limit Order'),
        ('stop', 'Stop Order'),
        ('stop_limit', 'Stop-Limit Order'),
        # Pro tier advanced orders
        ('trailing_stop', 'Trailing Stop'),
        ('bracket', 'Bracket Order'),
        ('oco', 'One-Cancels-Other'),
    ]

    TRADE_SIDES = [
        ('long', 'Long'),
        ('short', 'Short'),  # Pro tier only
    ]

    TRADE_STATUS = [
        ('pending', 'Pending'),      # Order placed but not filled
        ('open', 'Open'),            # Position is active
        ('closed', 'Closed'),        # Position closed
        ('cancelled', 'Cancelled'),  # Order cancelled before fill
        ('rejected', 'Rejected'),    # Order rejected (insufficient funds, etc.)
    ]

    # Relationships
    account = models.ForeignKey('PaperTradingAccount', on_delete=models.CASCADE, related_name='paper_trades')
    stock = models.ForeignKey('Stock', on_delete=models.CASCADE)

    # Order Details
    order_type = models.CharField(max_length=20, choices=ORDER_TYPES, default='market')
    side = models.CharField(max_length=10, choices=TRADE_SIDES, default='long')
    status = models.CharField(max_length=20, choices=TRADE_STATUS, default='pending')

    # Quantity & Pricing
    shares = models.DecimalField(max_digits=15, decimal_places=4, help_text="Number of shares")
    entry_price = models.DecimalField(max_digits=15, decimal_places=4, null=True, blank=True,
                                     help_text="Actual fill price")
    exit_price = models.DecimalField(max_digits=15, decimal_places=4, null=True, blank=True,
                                    help_text="Actual exit price")
    current_price = models.DecimalField(max_digits=15, decimal_places=4, null=True, blank=True,
                                       help_text="Current market price for open positions")

    # Order Parameters
    limit_price = models.DecimalField(max_digits=15, decimal_places=4, null=True, blank=True,
                                     help_text="Limit price for limit/stop-limit orders")
    stop_price = models.DecimalField(max_digits=15, decimal_places=4, null=True, blank=True,
                                    help_text="Stop price for stop/stop-limit orders")
    trailing_amount = models.DecimalField(max_digits=15, decimal_places=4, null=True, blank=True,
                                         help_text="Trailing amount for trailing stop (Pro)")
    trailing_percent = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True,
                                          help_text="Trailing percentage for trailing stop (Pro)")

    # Bracket Order Parameters (Pro tier)
    take_profit_price = models.DecimalField(max_digits=15, decimal_places=4, null=True, blank=True,
                                           help_text="Take profit price for bracket orders")
    stop_loss_price = models.DecimalField(max_digits=15, decimal_places=4, null=True, blank=True,
                                         help_text="Stop loss price for bracket orders")

    # Position Values
    entry_value = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True,
                                     help_text="Total entry cost (shares × entry_price)")
    current_value = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True,
                                       help_text="Current position value")
    exit_value = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True,
                                    help_text="Total exit proceeds")

    # Performance
    unrealized_pl = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True,
                                       help_text="Unrealized profit/loss for open positions")
    unrealized_pl_pct = models.DecimalField(max_digits=8, decimal_places=4, null=True, blank=True,
                                           help_text="Unrealized P/L percentage")
    realized_pl = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True,
                                     help_text="Realized profit/loss for closed positions")
    realized_pl_pct = models.DecimalField(max_digits=8, decimal_places=4, null=True, blank=True,
                                         help_text="Realized P/L percentage")

    # Fees (simulated)
    commission = models.DecimalField(max_digits=10, decimal_places=2, default=0.00,
                                    help_text="Simulated commission fees")

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, help_text="When order was placed")
    filled_at = models.DateTimeField(null=True, blank=True, help_text="When order was filled")
    closed_at = models.DateTimeField(null=True, blank=True, help_text="When position was closed")
    holding_period_days = models.IntegerField(null=True, blank=True, help_text="Days held")

    # Notes
    notes = models.TextField(blank=True, help_text="Trade notes/strategy")

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['account', 'status']),
            models.Index(fields=['stock', '-created_at']),
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['account', 'stock', 'status']),
        ]

    def __str__(self):
        status_display = self.get_status_display()
        return f"{self.stock.ticker} - {self.side.upper()} {self.shares} @ ${self.entry_price or 'N/A'} ({status_display})"

    def update_current_value(self):
        """Update current value and unrealized P/L for open positions"""
        if self.status == 'open' and self.entry_price:
            # Get current stock price
            self.current_price = self.stock.current_price

            if self.current_price:
                self.current_value = self.shares * self.current_price

                # Calculate unrealized P/L based on side
                if self.side == 'long':
                    self.unrealized_pl = (self.current_price - self.entry_price) * self.shares
                else:  # short
                    self.unrealized_pl = (self.entry_price - self.current_price) * self.shares

                # Calculate unrealized P/L percentage
                if self.entry_value and self.entry_value > 0:
                    self.unrealized_pl_pct = (self.unrealized_pl / self.entry_value) * 100

                self.save()

    def execute_market_order(self):
        """
        Execute market order with deterministic fill.
        Uses current stock price from database.
        """
        if self.status != 'pending':
            return False

        # Get current price
        current_price = self.stock.current_price
        if not current_price:
            self.status = 'rejected'
            self.save()
            return False

        # Calculate required funds
        required_funds = self.shares * current_price

        # Check if account has sufficient funds
        if required_funds > self.account.cash_balance:
            self.status = 'rejected'
            self.save()
            return False

        # Fill the order
        self.entry_price = current_price
        self.entry_value = required_funds
        self.current_price = current_price
        self.current_value = required_funds
        self.status = 'open'
        self.filled_at = timezone.now()

        # Deduct from account cash
        self.account.cash_balance -= required_funds
        self.account.last_trade_at = self.filled_at
        self.account.save()

        self.save()
        return True

    def close_position(self, exit_price=None):
        """
        Close an open position.
        If exit_price not provided, uses current market price.
        """
        if self.status != 'open':
            return False

        # Use provided exit price or current market price
        if exit_price is None:
            exit_price = self.stock.current_price

        if not exit_price:
            return False

        self.exit_price = exit_price
        self.exit_value = self.shares * exit_price
        self.closed_at = timezone.now()

        # Calculate realized P/L
        if self.side == 'long':
            self.realized_pl = (exit_price - self.entry_price) * self.shares - self.commission
        else:  # short
            self.realized_pl = (self.entry_price - exit_price) * self.shares - self.commission

        if self.entry_value and self.entry_value > 0:
            self.realized_pl_pct = (self.realized_pl / self.entry_value) * 100

        # Calculate holding period
        if self.filled_at:
            holding_period = self.closed_at - self.filled_at
            self.holding_period_days = holding_period.days

        # Update status
        self.status = 'closed'

        # Return cash to account
        self.account.cash_balance += self.exit_value
        self.account.realized_pl += self.realized_pl
        self.account.total_trades += 1

        if self.realized_pl > 0:
            self.account.winning_trades += 1
        elif self.realized_pl < 0:
            self.account.losing_trades += 1

        self.account.save()
        self.save()

        # Update account balances
        self.account.update_balances()

        return True


class PaperTradePerformance(models.Model):
    """
    Aggregated performance metrics for paper trading accounts.
    Tracks daily/weekly/monthly statistics.
    """
    PERIOD_TYPES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    ]

    account = models.ForeignKey('PaperTradingAccount', on_delete=models.CASCADE, related_name='performance_records')
    period_type = models.CharField(max_length=10, choices=PERIOD_TYPES)
    period_start = models.DateField()
    period_end = models.DateField()

    # Period Performance
    starting_value = models.DecimalField(max_digits=15, decimal_places=2)
    ending_value = models.DecimalField(max_digits=15, decimal_places=2)
    period_return = models.DecimalField(max_digits=10, decimal_places=2,
                                       help_text="Return percentage for this period")
    period_pl = models.DecimalField(max_digits=15, decimal_places=2,
                                   help_text="Profit/loss in dollars for this period")

    # Trading Activity
    trades_opened = models.IntegerField(default=0)
    trades_closed = models.IntegerField(default=0)
    winning_trades = models.IntegerField(default=0)
    losing_trades = models.IntegerField(default=0)
    period_win_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)

    # Risk Metrics
    max_gain = models.DecimalField(max_digits=15, decimal_places=2, default=0.00,
                                  help_text="Largest single winning trade")
    max_loss = models.DecimalField(max_digits=15, decimal_places=2, default=0.00,
                                  help_text="Largest single losing trade")
    volatility = models.DecimalField(max_digits=8, decimal_places=4, null=True, blank=True,
                                    help_text="Standard deviation of returns")

    # Benchmark Comparison
    benchmark_return = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True,
                                          help_text="S&P 500 return for same period")
    alpha = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True,
                               help_text="Excess return vs benchmark")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-period_start']
        unique_together = ['account', 'period_type', 'period_start']
        indexes = [
            models.Index(fields=['account', 'period_type', '-period_start']),
            models.Index(fields=['-period_return']),
        ]

    def __str__(self):
        return f"{self.account.name} - {self.period_type} ({self.period_start} to {self.period_end})"



# ============================================================================
# SMS ALERT SYSTEM MODELS (MVP2 v3.4)
# Append this to stocks/models.py
# ============================================================================

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class SMSAlertRule(models.Model):
    """
    SMS Alert Rules supporting single and multi-condition alerts.
    Uses TextBelt for SMS delivery (no email).
    """
    ALERT_TYPES = [
        ('price_above', 'Price Above'),
        ('price_below', 'Price Below'),
        ('price_crosses_above', 'Price Crosses Above'),
        ('price_crosses_below', 'Price Crosses Below'),
        ('volume_surge', 'Volume Surge'),
        ('volume_above', 'Volume Above'),
        ('price_change_percent', 'Price Change %'),
        ('rsi_above', 'RSI Above'),
        ('rsi_below', 'RSI Below'),
        ('macd_cross_bullish', 'MACD Bullish Cross'),
        ('macd_cross_bearish', 'MACD Bearish Cross'),
        ('sma_cross_above', 'SMA Cross Above'),
        ('sma_cross_below', 'SMA Cross Below'),
        ('gap_up', 'Gap Up %'),
        ('gap_down', 'Gap Down %'),
    ]

    CONDITION_OPERATORS = [
        ('and', 'AND - All conditions must be true'),
        ('or', 'OR - Any condition can be true'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sms_alerts')
    name = models.CharField(max_length=200, help_text="Alert name/description")

    # Target
    stock = models.ForeignKey('Stock', on_delete=models.CASCADE, null=True, blank=True,
                             help_text="Specific stock (leave blank for watchlist alerts)")
    watchlist = models.ForeignKey('UserWatchlist', on_delete=models.CASCADE, null=True, blank=True,
                                  help_text="Apply alert to all stocks in watchlist")

    # Multi-Condition Support (Pro tier)
    is_multi_condition = models.BooleanField(default=False,
                                            help_text="Whether this is a multi-condition alert (Pro tier)")
    condition_operator = models.CharField(max_length=10, choices=CONDITION_OPERATORS, default='and',
                                         help_text="How to combine multiple conditions (Pro tier)")

    # SMS Delivery
    phone_number = models.CharField(max_length=20, help_text="Phone number for SMS (E.164 format)")

    # Status & Tracking
    is_active = models.BooleanField(default=True)
    trigger_count = models.IntegerField(default=0, help_text="Number of times this alert has triggered")
    last_triggered_at = models.DateTimeField(null=True, blank=True)
    last_checked_at = models.DateTimeField(null=True, blank=True)

    # One-time vs Recurring
    is_one_time = models.BooleanField(default=False,
                                     help_text="Deactivate after first trigger")
    max_triggers_per_day = models.IntegerField(default=10,
                                              help_text="Maximum triggers per day (prevent spam)")

    # Webhook Support
    webhook_url = models.URLField(blank=True, help_text="Optional webhook to call when alert triggers")
    webhook_enabled = models.BooleanField(default=False)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['stock', 'is_active']),
            models.Index(fields=['watchlist', 'is_active']),
            models.Index(fields=['-last_checked_at']),
        ]

    def __str__(self):
        target = self.stock.ticker if self.stock else f"Watchlist: {self.watchlist.name}"
        return f"{self.user.username} - {self.name} ({target})"

    def can_trigger_today(self):
        """Check if alert can trigger based on daily limit"""
        if not self.last_triggered_at:
            return True

        today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)

        # Count triggers today
        triggers_today = SMSAlertHistory.objects.filter(
            alert_rule=self,
            sent_at__gte=today_start
        ).count()

        return triggers_today < self.max_triggers_per_day


class SMSAlertCondition(models.Model):
    """
    Individual conditions for multi-condition alerts (Pro tier).
    Single-condition alerts (Basic tier) have exactly one condition.
    """
    ALERT_TYPES = SMSAlertRule.ALERT_TYPES

    alert_rule = models.ForeignKey(SMSAlertRule, on_delete=models.CASCADE, related_name='conditions')

    # Condition Details
    condition_type = models.CharField(max_length=30, choices=ALERT_TYPES)
    target_value = models.DecimalField(max_digits=15, decimal_places=4,
                                      help_text="Target value for comparison")

    # For indicator-based alerts (RSI, MACD, SMA)
    indicator_period = models.IntegerField(null=True, blank=True,
                                          help_text="Period for indicator calculation (e.g., 14 for RSI)")

    # For cross alerts (SMA cross)
    comparison_period = models.IntegerField(null=True, blank=True,
                                           help_text="Second period for cross comparisons (e.g., SMA 50 vs SMA 200)")

    # Status Tracking
    last_met_at = models.DateTimeField(null=True, blank=True,
                                      help_text="When this condition was last met")
    previous_value = models.DecimalField(max_digits=15, decimal_places=4, null=True, blank=True,
                                        help_text="Previous value for cross detection")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['alert_rule', 'condition_type']),
        ]

    def __str__(self):
        return f"{self.alert_rule.name} - {self.get_condition_type_display()}: {self.target_value}"


class SMSAlertHistory(models.Model):
    """
    History of SMS alerts sent via TextBelt.
    Tracks delivery status and retry attempts.
    """
    DELIVERY_STATUS = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('failed', 'Failed'),
        ('retry', 'Retrying'),
    ]

    alert_rule = models.ForeignKey(SMSAlertRule, on_delete=models.CASCADE, related_name='history')
    stock = models.ForeignKey('Stock', on_delete=models.SET_NULL, null=True, blank=True)

    # Alert Content
    message = models.TextField(help_text="SMS message content")
    phone_number = models.CharField(max_length=20)

    # Trigger Details
    trigger_price = models.DecimalField(max_digits=15, decimal_places=4, null=True, blank=True)
    trigger_volume = models.BigIntegerField(null=True, blank=True)
    condition_values = models.JSONField(null=True, blank=True,
                                       help_text="Values of all conditions when triggered")

    # Delivery Status
    status = models.CharField(max_length=20, choices=DELIVERY_STATUS, default='pending')
    textbelt_id = models.CharField(max_length=100, blank=True,
                                  help_text="TextBelt message ID")
    textbelt_quota = models.IntegerField(null=True, blank=True,
                                        help_text="Remaining TextBelt quota")
    delivery_attempts = models.IntegerField(default=0)
    max_attempts = models.IntegerField(default=3)

    # Error Tracking
    error_message = models.TextField(blank=True)
    last_attempt_at = models.DateTimeField(null=True, blank=True)

    # Webhook
    webhook_sent = models.BooleanField(default=False)
    webhook_response = models.TextField(blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['alert_rule', '-created_at']),
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['phone_number', '-created_at']),
        ]

    def __str__(self):
        return f"{self.alert_rule.name} - {self.status} ({self.created_at.strftime('%Y-%m-%d %H:%M')})"

    def should_retry(self):
        """Check if message should be retried"""
        return (
            self.status in ['pending', 'failed', 'retry'] and
            self.delivery_attempts < self.max_attempts
        )


class SMSAlertQuota(models.Model):
    """
    Track SMS quota usage per user.
    Free tier has limits, Pro tier has higher limits.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='sms_quota')

    # Quota Limits (monthly)
    monthly_limit = models.IntegerField(default=50, help_text="Monthly SMS limit")
    current_usage = models.IntegerField(default=0, help_text="SMS sent this month")

    # Tracking
    last_reset_at = models.DateTimeField(auto_now_add=True, help_text="Last monthly reset")
    total_sent = models.IntegerField(default=0, help_text="Total SMS sent all-time")

    # Status
    is_blocked = models.BooleanField(default=False, help_text="Block SMS if quota exceeded or abuse detected")
    block_reason = models.CharField(max_length=200, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "SMS Alert Quotas"

    def __str__(self):
        return f"{self.user.username} - {self.current_usage}/{self.monthly_limit} SMS"

    def can_send_sms(self):
        """Check if user can send SMS (within quota and not blocked)"""
        if self.is_blocked:
            return False

        # Reset monthly quota if needed
        now = timezone.now()
        if (now - self.last_reset_at).days >= 30:
            self.current_usage = 0
            self.last_reset_at = now
            self.save()

        return self.current_usage < self.monthly_limit

    def increment_usage(self):
        """Increment SMS usage counter"""
        self.current_usage += 1
        self.total_sent += 1
        self.save()


class TextBeltConfig(models.Model):
    """
    TextBelt configuration for self-hosted instance.
    Singleton model - only one instance should exist.
    """
    # TextBelt Server
    api_url = models.URLField(default='http://localhost:8080/text',
                             help_text="TextBelt API endpoint URL")
    api_key = models.CharField(max_length=200, blank=True,
                              help_text="Optional API key (for paid plans)")

    # Self-Hosted Settings
    is_self_hosted = models.BooleanField(default=True,
                                        help_text="Whether using self-hosted TextBelt")
    max_retries = models.IntegerField(default=3)
    retry_delay_seconds = models.IntegerField(default=60)

    # Rate Limiting
    max_sms_per_minute = models.IntegerField(default=10,
                                            help_text="Rate limit for SMS sending")

    # Monitoring
    total_sent = models.IntegerField(default=0)
    total_failed = models.IntegerField(default=0)
    last_sent_at = models.DateTimeField(null=True, blank=True)

    # Status
    is_enabled = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "TextBelt Configuration"
        verbose_name_plural = "TextBelt Configuration"

    def __str__(self):
        status = "Enabled" if self.is_enabled else "Disabled"
        return f"TextBelt Config ({status}) - {self.total_sent} sent"

    @classmethod
    def get_config(cls):
        """Get or create singleton config"""
        config, created = cls.objects.get_or_create(pk=1)
        return config



# ============================================================================
# TWO-FACTOR AUTHENTICATION (2FA) SYSTEM MODELS
# Append this to stocks/models.py
# SMS-based 2FA using TextBelt integration
# ============================================================================

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import secrets
import string


class TwoFactorAuth(models.Model):
    """
    Two-Factor Authentication configuration per user.
    SMS-based 2FA using TextBelt.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='twofa')

    # 2FA Status
    is_enabled = models.BooleanField(default=False, help_text="Whether 2FA is enabled")
    phone_number = models.CharField(max_length=20, help_text="Phone number for 2FA (E.164 format)")
    verified_at = models.DateTimeField(null=True, blank=True, help_text="When phone was verified")

    # Backup Codes
    backup_codes = models.JSONField(default=list, help_text="List of backup codes (hashed)")
    backup_codes_count = models.IntegerField(default=10, help_text="Number of unused backup codes")

    # Security Settings
    require_on_login = models.BooleanField(default=True, help_text="Require 2FA on every login")
    require_on_sensitive = models.BooleanField(default=True,
                                              help_text="Require 2FA for sensitive operations")
    trusted_devices_enabled = models.BooleanField(default=True,
                                                  help_text="Allow trusted device feature")

    # Statistics
    total_verifications = models.IntegerField(default=0)
    failed_attempts = models.IntegerField(default=0)
    last_verified_at = models.DateTimeField(null=True, blank=True)
    last_failed_at = models.DateTimeField(null=True, blank=True)

    # Lockout Protection
    is_locked = models.BooleanField(default=False)
    locked_until = models.DateTimeField(null=True, blank=True)
    consecutive_failures = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Two-Factor Authentication"
        verbose_name_plural = "Two-Factor Authentication"

    def __str__(self):
        status = "Enabled" if self.is_enabled else "Disabled"
        return f"{self.user.username} - 2FA {status}"

    def is_locked_out(self):
        """Check if account is currently locked"""
        if not self.is_locked:
            return False
        if self.locked_until and timezone.now() < self.locked_until:
            return True
        # Auto-unlock if time passed
        self.is_locked = False
        self.locked_until = None
        self.consecutive_failures = 0
        self.save()
        return False

    def lock_account(self, duration_minutes=30):
        """Lock account due to too many failed attempts"""
        self.is_locked = True
        self.locked_until = timezone.now() + timedelta(minutes=duration_minutes)
        self.save()


class TwoFactorCode(models.Model):
    """
    Generated 2FA codes sent via SMS.
    Short-lived codes (5 minutes) for verification.
    """
    CODE_TYPES = [
        ('login', 'Login Verification'),
        ('enable', 'Enable 2FA'),
        ('disable', 'Disable 2FA'),
        ('sensitive', 'Sensitive Operation'),
        ('recovery', 'Account Recovery'),
    ]

    twofa = models.ForeignKey(TwoFactorAuth, on_delete=models.CASCADE, related_name='codes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, help_text="Redundant for quick queries")

    # Code Details
    code = models.CharField(max_length=10, help_text="6-digit verification code")
    code_type = models.CharField(max_length=20, choices=CODE_TYPES, default='login')

    # Validity
    expires_at = models.DateTimeField(help_text="Code expiration time")
    is_used = models.BooleanField(default=False)
    used_at = models.DateTimeField(null=True, blank=True)

    # Delivery
    phone_number = models.CharField(max_length=20)
    sms_sent = models.BooleanField(default=False)
    sms_sent_at = models.DateTimeField(null=True, blank=True)
    textbelt_id = models.CharField(max_length=100, blank=True)

    # Attempt Tracking
    verification_attempts = models.IntegerField(default=0)
    max_attempts = models.IntegerField(default=3)

    # IP Tracking
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_used', '-created_at']),
            models.Index(fields=['code', 'is_used']),
            models.Index(fields=['-expires_at']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.code_type} - {'Used' if self.is_used else 'Active'}"

    def is_valid(self):
        """Check if code is still valid"""
        if self.is_used:
            return False
        if timezone.now() > self.expires_at:
            return False
        if self.verification_attempts >= self.max_attempts:
            return False
        return True

    def mark_used(self):
        """Mark code as used"""
        self.is_used = True
        self.used_at = timezone.now()
        self.save()

    @staticmethod
    def generate_code(length=6):
        """Generate random numeric code"""
        return ''.join(secrets.choice(string.digits) for _ in range(length))


class TrustedDevice(models.Model):
    """
    Trusted devices that don't require 2FA for a period.
    """
    twofa = models.ForeignKey(TwoFactorAuth, on_delete=models.CASCADE, related_name='trusted_devices')
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    # Device Identification
    device_name = models.CharField(max_length=200, help_text="User-friendly device name")
    device_fingerprint = models.CharField(max_length=64, unique=True,
                                         help_text="Hashed device fingerprint")

    # Device Details
    user_agent = models.TextField(help_text="Browser user agent")
    ip_address = models.GenericIPAddressField()
    location = models.CharField(max_length=200, blank=True, help_text="Approximate location")

    # Trust Settings
    is_active = models.BooleanField(default=True)
    trust_expires_at = models.DateTimeField(help_text="When trust expires (default 30 days)")

    # Usage Tracking
    last_used_at = models.DateTimeField(auto_now=True)
    total_uses = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-last_used_at']
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['device_fingerprint']),
            models.Index(fields=['-trust_expires_at']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.device_name}"

    def is_trusted(self):
        """Check if device is still trusted"""
        if not self.is_active:
            return False
        if timezone.now() > self.trust_expires_at:
            # Auto-expire
            self.is_active = False
            self.save()
            return False
        return True

    def extend_trust(self, days=30):
        """Extend trust period"""
        self.trust_expires_at = timezone.now() + timedelta(days=days)
        self.save()


class TwoFactorAuditLog(models.Model):
    """
    Audit log for all 2FA activities.
    Tracks all authentication attempts and configuration changes.
    """
    EVENT_TYPES = [
        ('enabled', '2FA Enabled'),
        ('disabled', '2FA Disabled'),
        ('code_sent', 'Code Sent'),
        ('code_verified', 'Code Verified'),
        ('code_failed', 'Code Verification Failed'),
        ('backup_used', 'Backup Code Used'),
        ('backup_generated', 'Backup Codes Generated'),
        ('device_trusted', 'Device Trusted'),
        ('device_revoked', 'Device Trust Revoked'),
        ('account_locked', 'Account Locked'),
        ('account_unlocked', 'Account Unlocked'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='twofa_audit_log')
    twofa = models.ForeignKey(TwoFactorAuth, on_delete=models.SET_NULL, null=True, blank=True)

    # Event Details
    event_type = models.CharField(max_length=30, choices=EVENT_TYPES)
    event_description = models.TextField(blank=True)
    success = models.BooleanField(default=True)

    # Context
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    device_fingerprint = models.CharField(max_length=64, blank=True)

    # Additional Data
    metadata = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['event_type', '-created_at']),
            models.Index(fields=['success', '-created_at']),
        ]

    def __str__(self):
        status = "✓" if self.success else "✗"
        return f"{status} {self.user.username} - {self.get_event_type_display()} ({self.created_at.strftime('%Y-%m-%d %H:%M')})"



# ============================================================================
# OPTIONS ANALYTICS MODELS (MVP2 v3.4 - Pro Tier)
# Append this to stocks/models.py
# Intraday options chains, Greeks, and IV surfaces
# ============================================================================

from django.db import models
from django.utils import timezone
from decimal import Decimal


class OptionsChain(models.Model):
    """
    Options chain snapshot for a stock.
    Stores calls and puts for all available expirations.
    """
    stock = models.ForeignKey('Stock', on_delete=models.CASCADE, related_name='options_chains')

    # Chain Details
    snapshot_date = models.DateField(help_text="Date of this chain snapshot")
    snapshot_time = models.DateTimeField(help_text="Exact time of snapshot")
    underlying_price = models.DecimalField(max_digits=15, decimal_places=4,
                                          help_text="Stock price at snapshot time")

    # Data Source
    data_source = models.CharField(max_length=50, default='yfinance',
                                   help_text="Source of options data")

    # Metadata
    total_contracts = models.IntegerField(default=0, help_text="Total number of contracts")
    expirations_count = models.IntegerField(default=0, help_text="Number of expiration dates")

    # Update Tracking
    is_current = models.BooleanField(default=True, help_text="Whether this is the most recent chain")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-snapshot_time']
        indexes = [
            models.Index(fields=['stock', '-snapshot_time']),
            models.Index(fields=['stock', 'is_current']),
            models.Index(fields=['snapshot_date']),
        ]
        unique_together = ['stock', 'snapshot_time']

    def __str__(self):
        return f"{self.stock.ticker} Options Chain - {self.snapshot_time.strftime('%Y-%m-%d %H:%M')}"


class OptionsContract(models.Model):
    """
    Individual options contract with pricing and Greeks.
    """
    CONTRACT_TYPES = [
        ('call', 'Call'),
        ('put', 'Put'),
    ]

    chain = models.ForeignKey(OptionsChain, on_delete=models.CASCADE, related_name='contracts')
    stock = models.ForeignKey('Stock', on_delete=models.CASCADE)

    # Contract Identification
    contract_symbol = models.CharField(max_length=50, unique=True,
                                      help_text="OCC option symbol")
    contract_type = models.CharField(max_length=10, choices=CONTRACT_TYPES)
    strike = models.DecimalField(max_digits=15, decimal_places=4, help_text="Strike price")
    expiration = models.DateField(help_text="Expiration date")

    # Days to Expiration
    dte = models.IntegerField(help_text="Days to expiration")

    # Pricing
    last_price = models.DecimalField(max_digits=15, decimal_places=4, null=True, blank=True)
    bid = models.DecimalField(max_digits=15, decimal_places=4, null=True, blank=True)
    ask = models.DecimalField(max_digits=15, decimal_places=4, null=True, blank=True)
    mark = models.DecimalField(max_digits=15, decimal_places=4, null=True, blank=True,
                              help_text="Mid price (bid + ask) / 2")

    # Volume & Interest
    volume = models.BigIntegerField(null=True, blank=True, help_text="Trading volume")
    open_interest = models.BigIntegerField(null=True, blank=True)

    # Implied Volatility
    implied_volatility = models.DecimalField(max_digits=8, decimal_places=6, null=True, blank=True,
                                            help_text="IV as decimal (e.g., 0.25 = 25%)")

    # Greeks
    delta = models.DecimalField(max_digits=8, decimal_places=6, null=True, blank=True)
    gamma = models.DecimalField(max_digits=8, decimal_places=6, null=True, blank=True)
    theta = models.DecimalField(max_digits=8, decimal_places=6, null=True, blank=True)
    vega = models.DecimalField(max_digits=8, decimal_places=6, null=True, blank=True)
    rho = models.DecimalField(max_digits=8, decimal_places=6, null=True, blank=True)

    # Moneyness
    in_the_money = models.BooleanField(default=False)
    intrinsic_value = models.DecimalField(max_digits=15, decimal_places=4, default=0)
    extrinsic_value = models.DecimalField(max_digits=15, decimal_places=4, default=0,
                                         help_text="Time value")

    # Calculated Fields
    break_even = models.DecimalField(max_digits=15, decimal_places=4, null=True, blank=True)
    probability_itm = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True,
                                         help_text="Probability of being in-the-money at expiration")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['expiration', 'strike']
        indexes = [
            models.Index(fields=['chain', 'contract_type', 'expiration']),
            models.Index(fields=['stock', 'expiration', 'strike']),
            models.Index(fields=['contract_symbol']),
            models.Index(fields=['expiration', 'strike']),
        ]

    def __str__(self):
        return f"{self.stock.ticker} ${self.strike} {self.contract_type.upper()} {self.expiration}"


class ImpliedVolatilitySurface(models.Model):
    """
    IV Surface data for visualization.
    Stores IV values across strikes and expirations.
    """
    stock = models.ForeignKey('Stock', on_delete=models.CASCADE, related_name='iv_surfaces')

    # Surface Details
    snapshot_date = models.DateField()
    snapshot_time = models.DateTimeField()
    underlying_price = models.DecimalField(max_digits=15, decimal_places=4)

    # Surface Data (JSON format for flexibility)
    # Structure: {
    #   'expirations': [date1, date2, ...],
    #   'strikes': [strike1, strike2, ...],
    #   'call_iv': [[iv11, iv12, ...], [iv21, iv22, ...], ...],
    #   'put_iv': [[iv11, iv12, ...], [iv21, iv22, ...], ...]
    # }
    surface_data = models.JSONField(help_text="IV surface grid data")

    # Statistics
    avg_iv = models.DecimalField(max_digits=8, decimal_places=6, help_text="Average IV across surface")
    min_iv = models.DecimalField(max_digits=8, decimal_places=6, help_text="Minimum IV")
    max_iv = models.DecimalField(max_digits=8, decimal_places=6, help_text="Maximum IV")

    # IV Skew Metrics
    atm_iv = models.DecimalField(max_digits=8, decimal_places=6, null=True, blank=True,
                                 help_text="At-the-money IV")
    put_call_iv_ratio = models.DecimalField(max_digits=8, decimal_places=4, null=True, blank=True,
                                           help_text="Ratio of put IV to call IV")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-snapshot_time']
        indexes = [
            models.Index(fields=['stock', '-snapshot_time']),
            models.Index(fields=['snapshot_date']),
        ]

    def __str__(self):
        return f"{self.stock.ticker} IV Surface - {self.snapshot_time.strftime('%Y-%m-%d %H:%M')}"


class OptionsScreenerResult(models.Model):
    """
    Saved options screener results.
    Pre-calculated unusual options activity, high IV, etc.
    """
    SCREENER_TYPES = [
        ('unusual_volume', 'Unusual Volume'),
        ('high_iv', 'High Implied Volatility'),
        ('iv_rank_high', 'IV Rank > 80%'),
        ('cheap_options', 'Low Premium Options'),
        ('high_gamma', 'High Gamma'),
        ('earnings_plays', 'Earnings Plays'),
    ]

    stock = models.ForeignKey('Stock', on_delete=models.CASCADE, related_name='options_screener_results')
    contract = models.ForeignKey(OptionsContract, on_delete=models.CASCADE, null=True, blank=True)

    # Screener Details
    screener_type = models.CharField(max_length=30, choices=SCREENER_TYPES)
    scan_date = models.DateField()
    scan_time = models.DateTimeField()

    # Metrics that triggered the screener
    trigger_metrics = models.JSONField(default=dict,
                                      help_text="Metrics that caused this to appear in screener")

    # Score (0-100)
    score = models.DecimalField(max_digits=5, decimal_places=2,
                               help_text="Screener relevance score")

    # Ranking
    rank = models.IntegerField(help_text="Rank within this screener type")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-scan_time', '-score']
        indexes = [
            models.Index(fields=['screener_type', '-scan_time']),
            models.Index(fields=['stock', 'screener_type']),
            models.Index(fields=['-score']),
        ]

    def __str__(self):
        return f"{self.stock.ticker} - {self.get_screener_type_display()} (Score: {self.score})"


class OptionsAnalytics(models.Model):
    """
    Aggregated options analytics for a stock.
    Daily summary of options activity and metrics.
    """
    stock = models.ForeignKey('Stock', on_delete=models.CASCADE, related_name='options_analytics')

    # Date
    date = models.DateField()

    # Volume Metrics
    total_call_volume = models.BigIntegerField(default=0)
    total_put_volume = models.BigIntegerField(default=0)
    put_call_volume_ratio = models.DecimalField(max_digits=8, decimal_places=4, default=0,
                                                help_text="Put volume / Call volume")

    # Open Interest Metrics
    total_call_oi = models.BigIntegerField(default=0, help_text="Total call open interest")
    total_put_oi = models.BigIntegerField(default=0, help_text="Total put open interest")
    put_call_oi_ratio = models.DecimalField(max_digits=8, decimal_places=4, default=0)

    # IV Metrics
    avg_call_iv = models.DecimalField(max_digits=8, decimal_places=6, null=True, blank=True)
    avg_put_iv = models.DecimalField(max_digits=8, decimal_places=6, null=True, blank=True)
    iv_30_day = models.DecimalField(max_digits=8, decimal_places=6, null=True, blank=True,
                                   help_text="30-day implied volatility")
    iv_rank = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True,
                                  help_text="IV Rank (0-100)")
    iv_percentile = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    # Popular Strikes
    most_active_call_strike = models.DecimalField(max_digits=15, decimal_places=4, null=True, blank=True)
    most_active_put_strike = models.DecimalField(max_digits=15, decimal_places=4, null=True, blank=True)

    # Unusual Activity Flags
    unusual_call_volume = models.BooleanField(default=False)
    unusual_put_volume = models.BooleanField(default=False)
    iv_spike = models.BooleanField(default=False, help_text="Significant IV increase")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date']
        unique_together = ['stock', 'date']
        indexes = [
            models.Index(fields=['stock', '-date']),
            models.Index(fields=['-put_call_volume_ratio']),
            models.Index(fields=['-iv_rank']),
        ]

    def __str__(self):
        return f"{self.stock.ticker} Options Analytics - {self.date}"


class OptionsWatchlist(models.Model):
    """
    User watchlist for specific options contracts.
    Track specific strikes/expirations of interest.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='options_watchlists')
    name = models.CharField(max_length=100, default='My Options Watchlist')

    # Settings
    is_default = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.name}"


class OptionsWatchlistItem(models.Model):
    """
    Individual options contract in watchlist.
    """
    watchlist = models.ForeignKey(OptionsWatchlist, on_delete=models.CASCADE, related_name='items')
    contract = models.ForeignKey(OptionsContract, on_delete=models.CASCADE)

    # Tracking
    added_at = models.DateTimeField(auto_now_add=True)
    added_price = models.DecimalField(max_digits=15, decimal_places=4,
                                     help_text="Contract price when added")
    added_iv = models.DecimalField(max_digits=8, decimal_places=6, null=True, blank=True,
                                  help_text="IV when added")

    # Alerts
    target_price = models.DecimalField(max_digits=15, decimal_places=4, null=True, blank=True)
    alert_on_volume = models.BooleanField(default=False)
    alert_on_iv_change = models.BooleanField(default=False)

    # Notes
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-added_at']
        unique_together = ['watchlist', 'contract']

    def __str__(self):
        return f"{self.watchlist.name} - {self.contract.contract_symbol}"


# ============================================================================
# News & Sentiment System (MVP2 v3.4)
# ============================================================================

class NewsSource(models.Model):
    """
    News source configuration and tracking.
    Manages different news providers (RSS, API, scraping).
    """
    SOURCE_TYPES = [
        ('rss', 'RSS Feed'),
        ('api', 'REST API'),
        ('scraper', 'Web Scraper'),
    ]

    name = models.CharField(max_length=100, unique=True, help_text="Source name (e.g., Reuters, Bloomberg)")
    source_type = models.CharField(max_length=20, choices=SOURCE_TYPES)
    base_url = models.URLField(help_text="Base URL for the source")

    # API Configuration
    api_key_required = models.BooleanField(default=False)
    api_key = models.CharField(max_length=255, blank=True, help_text="Encrypted API key")

    # Scraping Configuration
    scraping_rules = models.JSONField(default=dict, blank=True,
                                     help_text="CSS selectors and extraction rules")

    # Source Quality
    reliability_score = models.DecimalField(max_digits=3, decimal_places=2, default=1.0,
                                           help_text="0.0-1.0 reliability rating")

    # Rate Limiting
    requests_per_hour = models.IntegerField(default=100)
    last_request_at = models.DateTimeField(null=True, blank=True)

    # Statistics
    total_articles_fetched = models.IntegerField(default=0)
    total_fetch_errors = models.IntegerField(default=0)
    last_successful_fetch = models.DateTimeField(null=True, blank=True)

    # Status
    is_active = models.BooleanField(default=True)
    is_premium = models.BooleanField(default=False, help_text="Requires Pro subscription")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.get_source_type_display()})"


class NewsArticle(models.Model):
    """
    News article with content and metadata.
    Supports multiple stocks per article.
    """
    # Article Identification
    source = models.ForeignKey(NewsSource, on_delete=models.CASCADE, related_name='articles')
    external_id = models.CharField(max_length=255, blank=True,
                                   help_text="External ID from source")
    url = models.URLField(unique=True, help_text="Article URL")

    # Content
    title = models.CharField(max_length=500)
    summary = models.TextField(blank=True, help_text="Article summary/snippet")
    content = models.TextField(blank=True, help_text="Full article content")

    # Metadata
    author = models.CharField(max_length=200, blank=True)
    published_at = models.DateTimeField(help_text="Original publication time")

    # Related Entities
    stocks = models.ManyToManyField('Stock', related_name='news_articles', blank=True)
    mentioned_tickers = models.JSONField(default=list,
                                        help_text="List of ticker symbols mentioned")

    # Categories & Tags
    category = models.CharField(max_length=50, blank=True,
                               help_text="earnings, merger, lawsuit, etc.")
    tags = models.JSONField(default=list, help_text="Article tags/keywords")

    # Engagement Metrics
    view_count = models.IntegerField(default=0)
    click_count = models.IntegerField(default=0)

    # Processing Status
    is_processed = models.BooleanField(default=False,
                                      help_text="Whether sentiment analysis is complete")
    processing_errors = models.TextField(blank=True)

    # Content Hash (for deduplication)
    content_hash = models.CharField(max_length=64, db_index=True,
                                   help_text="SHA-256 hash for duplicate detection")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-published_at']
        indexes = [
            models.Index(fields=['-published_at', 'is_processed']),
            models.Index(fields=['content_hash']),
            models.Index(fields=['source', '-published_at']),
        ]

    def __str__(self):
        return f"{self.title[:50]}... ({self.source.name})"


class SentimentAnalysis(models.Model):
    """
    NLP sentiment analysis results for news articles.
    Supports multiple sentiment engines and aspect-based sentiment.
    """
    SENTIMENT_CHOICES = [
        ('very_positive', 'Very Positive'),
        ('positive', 'Positive'),
        ('neutral', 'Neutral'),
        ('negative', 'Negative'),
        ('very_negative', 'Very Negative'),
    ]

    ANALYSIS_ENGINES = [
        ('vader', 'VADER (NLTK)'),
        ('textblob', 'TextBlob'),
        ('transformers', 'HuggingFace Transformers'),
        ('finbert', 'FinBERT (Financial)'),
    ]

    article = models.ForeignKey(NewsArticle, on_delete=models.CASCADE, related_name='sentiments')
    stock = models.ForeignKey('Stock', on_delete=models.CASCADE, related_name='news_sentiments',
                             null=True, blank=True, help_text="Stock-specific sentiment")

    # Sentiment Scores
    sentiment_label = models.CharField(max_length=20, choices=SENTIMENT_CHOICES)
    sentiment_score = models.DecimalField(max_digits=5, decimal_places=4,
                                         help_text="Score from -1.0 (negative) to +1.0 (positive)")
    confidence = models.DecimalField(max_digits=5, decimal_places=4,
                                    help_text="Confidence in analysis (0.0-1.0)")

    # Detailed Scores (for engines that provide them)
    positive_score = models.DecimalField(max_digits=5, decimal_places=4, null=True, blank=True)
    negative_score = models.DecimalField(max_digits=5, decimal_places=4, null=True, blank=True)
    neutral_score = models.DecimalField(max_digits=5, decimal_places=4, null=True, blank=True)

    # Analysis Engine
    analysis_engine = models.CharField(max_length=30, choices=ANALYSIS_ENGINES, default='vader')
    engine_version = models.CharField(max_length=20, blank=True)

    # Aspect-Based Sentiment (JSON structure)
    # Example: {"revenue": 0.8, "earnings": 0.6, "guidance": -0.3}
    aspect_sentiments = models.JSONField(default=dict, blank=True,
                                        help_text="Sentiment for specific aspects")

    # Entity Recognition
    entities_mentioned = models.JSONField(default=list, blank=True,
                                         help_text="Named entities (people, companies, etc.)")

    # Keywords & Themes
    key_phrases = models.JSONField(default=list, blank=True,
                                  help_text="Important phrases extracted")

    analyzed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-analyzed_at']
        indexes = [
            models.Index(fields=['stock', '-analyzed_at']),
            models.Index(fields=['sentiment_label', '-analyzed_at']),
        ]
        unique_together = ['article', 'stock', 'analysis_engine']

    def __str__(self):
        stock_info = f" - {self.stock.ticker}" if self.stock else ""
        return f"{self.article.title[:40]}{stock_info} [{self.sentiment_label}]"


class NewsFeed(models.Model):
    """
    User's personalized news feed configuration.
    Controls which sources, categories, and stocks to track.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='news_feed')

    # Followed Entities
    followed_stocks = models.ManyToManyField('Stock', related_name='news_followers', blank=True)
    followed_sources = models.ManyToManyField(NewsSource, related_name='followers', blank=True)

    # Category Preferences
    enabled_categories = models.JSONField(default=list,
                                         help_text="List of enabled news categories")

    # Sentiment Filters
    min_sentiment_score = models.DecimalField(max_digits=5, decimal_places=4, default=-1.0,
                                             help_text="Filter out articles below this score")
    exclude_neutral = models.BooleanField(default=False)

    # Notification Settings
    email_notifications = models.BooleanField(default=False)
    sms_notifications = models.BooleanField(default=False)
    notification_frequency = models.CharField(max_length=20, default='realtime',
                                             choices=[
                                                 ('realtime', 'Real-time'),
                                                 ('hourly', 'Hourly Digest'),
                                                 ('daily', 'Daily Digest'),
                                             ])

    # Alert Thresholds
    alert_on_very_positive = models.BooleanField(default=True)
    alert_on_very_negative = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s News Feed"


class NewsAlert(models.Model):
    """
    News-based alerts for significant sentiment changes or breaking news.
    """
    ALERT_TYPES = [
        ('breaking', 'Breaking News'),
        ('sentiment_spike', 'Sentiment Spike'),
        ('sentiment_drop', 'Sentiment Drop'),
        ('high_volume', 'High Article Volume'),
        ('keyword_match', 'Keyword Match'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='news_alerts')
    stock = models.ForeignKey('Stock', on_delete=models.CASCADE, related_name='news_alerts')
    article = models.ForeignKey(NewsArticle, on_delete=models.CASCADE, null=True, blank=True)

    # Alert Details
    alert_type = models.CharField(max_length=30, choices=ALERT_TYPES)
    message = models.TextField(help_text="Alert message text")

    # Trigger Data
    sentiment_score = models.DecimalField(max_digits=5, decimal_places=4, null=True, blank=True)
    trigger_data = models.JSONField(default=dict,
                                   help_text="Additional data about what triggered the alert")

    # Delivery
    is_read = models.BooleanField(default=False)
    email_sent = models.BooleanField(default=False)
    sms_sent = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read', '-created_at']),
            models.Index(fields=['stock', '-created_at']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.stock.ticker} - {self.get_alert_type_display()}"


class SentimentTimeseries(models.Model):
    """
    Aggregated sentiment over time for a stock.
    Pre-calculated for performance (1-hour, 1-day intervals).
    """
    INTERVAL_CHOICES = [
        ('1h', '1 Hour'),
        ('4h', '4 Hours'),
        ('1d', '1 Day'),
        ('1w', '1 Week'),
    ]

    stock = models.ForeignKey('Stock', on_delete=models.CASCADE, related_name='sentiment_timeseries')
    interval = models.CharField(max_length=10, choices=INTERVAL_CHOICES)

    # Time Period
    period_start = models.DateTimeField()
    period_end = models.DateTimeField()

    # Aggregated Sentiment
    avg_sentiment_score = models.DecimalField(max_digits=5, decimal_places=4)
    weighted_sentiment = models.DecimalField(max_digits=5, decimal_places=4,
                                            help_text="Weighted by source reliability")

    # Article Counts
    total_articles = models.IntegerField(default=0)
    positive_articles = models.IntegerField(default=0)
    negative_articles = models.IntegerField(default=0)
    neutral_articles = models.IntegerField(default=0)

    # Sentiment Distribution
    sentiment_std_dev = models.DecimalField(max_digits=5, decimal_places=4, null=True, blank=True,
                                           help_text="Standard deviation of sentiment scores")

    # Volume Metrics
    article_volume_change = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True,
                                               help_text="% change in article volume vs previous period")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-period_start']
        indexes = [
            models.Index(fields=['stock', 'interval', '-period_start']),
        ]
        unique_together = ['stock', 'interval', 'period_start']

    def __str__(self):
        return f"{self.stock.ticker} - {self.get_interval_display()} - {self.period_start.date()}"
