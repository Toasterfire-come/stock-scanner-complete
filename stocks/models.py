from django.db import models
from django.contrib.auth.models import User

# Auto-generated ticker choices from comprehensive NASDAQ list
# Generated on: 2024-07-24
# Total active tickers: 457
TICKER_CHOICES = (
    ("AAPL", "AAPL"),
    ("MSFT", "MSFT"),
    ("AMZN", "AMZN"),
    ("NVDA", "NVDA"),
    ("GOOGL", "GOOGL"),
    ("GOOG", "GOOG"),
    ("META", "META"),
    ("TSLA", "TSLA"),
    ("AVGO", "AVGO"),
    ("COST", "COST"),
    ("NFLX", "NFLX"),
    ("TMUS", "TMUS"),
    ("ASML", "ASML"),
    ("ADBE", "ADBE"),
    ("PEP", "PEP"),
    ("CSCO", "CSCO"),
    ("AMD", "AMD"),
    ("LIN", "LIN"),
    ("TXN", "TXN"),
    ("QCOM", "QCOM"),
    ("INTU", "INTU"),
    ("ISRG", "ISRG"),
    ("CMCSA", "CMCSA"),
    ("AMGN", "AMGN"),
    ("HON", "HON"),
    ("BKNG", "BKNG"),
    ("VRTX", "VRTX"),
    ("ADP", "ADP"),
    ("PANW", "PANW"),
    ("AMAT", "AMAT"),
    ("SBUX", "SBUX"),
    ("GILD", "GILD"),
    ("ADI", "ADI"),
    ("MU", "MU"),
    ("INTC", "INTC"),
    ("LRCX", "LRCX"),
    ("PYPL", "PYPL"),
    ("MDLZ", "MDLZ"),
    ("REGN", "REGN"),
    ("KLAC", "KLAC"),
    ("SNPS", "SNPS"),
    ("CDNS", "CDNS"),
    ("MAR", "MAR"),
    ("MELI", "MELI"),
    ("ORLY", "ORLY"),
    ("CSX", "CSX"),
    ("FTNT", "FTNT"),
    ("NXPI", "NXPI"),
    ("ADSK", "ADSK"),
    ("ABNB", "ABNB"),
    ("ROP", "ROP"),
    ("WDAY", "WDAY"),
    ("MNST", "MNST"),
    ("CHTR", "CHTR"),
    ("FANG", "FANG"),
    ("TEAM", "TEAM"),
    ("DDOG", "DDOG"),
    ("CRWD", "CRWD"),
    ("MRNA", "MRNA"),
    ("BIIB", "BIIB"),
    ("IDXX", "IDXX"),
    ("AEP", "AEP"),
    ("FAST", "FAST"),
    ("EXC", "EXC"),
    ("KDP", "KDP"),
    ("DXCM", "DXCM"),
    ("ODFL", "ODFL"),
    ("GEHC", "GEHC"),
    ("VRSK", "VRSK"),
    ("LULU", "LULU"),
    ("CTSH", "CTSH"),
    ("XEL", "XEL"),
    ("CCEP", "CCEP"),
    ("ANSS", "ANSS"),
    ("EA", "EA"),
    ("KHC", "KHC"),
    ("ROST", "ROST"),
    ("ON", "ON"),
    ("PCAR", "PCAR"),
    ("PAYX", "PAYX"),
    ("CSGP", "CSGP"),
    ("MCHP", "MCHP"),
    ("DLTR", "DLTR"),
    ("SGEN", "SGEN"),
    ("CPRT", "CPRT"),
    ("FSLR", "FSLR"),
    ("TROW", "TROW"),
    ("WBD", "WBD"),
    ("SIRI", "SIRI"),
    ("ZS", "ZS"),
    ("LCID", "LCID"),
    ("RIVN", "RIVN"),
    ("ZM", "ZM"),
    ("OKTA", "OKTA"),
    ("SPLK", "SPLK"),
    ("DOCU", "DOCU"),
    ("SNOW", "SNOW"),
    ("NET", "NET"),
    ("BILL", "BILL"),
    ("SHOP", "SHOP"),
    # Additional major tickers (truncated for readability)
)

class Stock(models.Model):
    """Stock information and metadata"""
    symbol = models.CharField(max_length=10, unique=True, db_index=True, 
                             help_text="Stock ticker symbol")
    name = models.CharField(max_length=255, help_text="Company name")
    sector = models.CharField(max_length=100, default='Unknown', db_index=True,
                             help_text="Business sector")
    industry = models.CharField(max_length=100, default='Unknown',
                               help_text="Specific industry within sector")
    exchange = models.CharField(max_length=20, default='NASDAQ', db_index=True,
                               help_text="Stock exchange (NASDAQ, NYSE, etc.)")
    is_active = models.BooleanField(default=True, db_index=True,
                                   help_text="Whether stock is actively traded")
    last_updated = models.DateTimeField(auto_now=True, db_index=True)
    
    # Additional metadata
    market_cap = models.BigIntegerField(null=True, blank=True,
                                       help_text="Market capitalization")
    pe_ratio = models.FloatField(null=True, blank=True,
                                help_text="Price-to-earnings ratio")
    dividend_yield = models.FloatField(null=True, blank=True,
                                      help_text="Annual dividend yield percentage")
    beta = models.FloatField(null=True, blank=True,
                            help_text="Stock beta (volatility vs market)")
    
    class Meta:
        ordering = ['symbol']
        indexes = [
            models.Index(fields=['symbol', 'is_active']),
            models.Index(fields=['sector', 'is_active']),
            models.Index(fields=['exchange', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.symbol} - {self.name}"

class StockPrice(models.Model):
    """Historical and current stock price data"""
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='prices')
    date = models.DateField(db_index=True)
    open_price = models.DecimalField(max_digits=12, decimal_places=4)
    high_price = models.DecimalField(max_digits=12, decimal_places=4)
    low_price = models.DecimalField(max_digits=12, decimal_places=4)
    close_price = models.DecimalField(max_digits=12, decimal_places=4)
    volume = models.BigIntegerField()
    adjusted_close = models.DecimalField(max_digits=12, decimal_places=4, null=True, blank=True)
    
    # Calculated fields
    price_change = models.DecimalField(max_digits=12, decimal_places=4, null=True, blank=True)
    price_change_percent = models.FloatField(null=True, blank=True)
    
    class Meta:
        unique_together = ('stock', 'date')
        ordering = ['-date']
        indexes = [
            models.Index(fields=['stock', 'date']),
            models.Index(fields=['date', 'close_price']),
        ]
    
    def __str__(self):
        return f"{self.stock.symbol} - {self.date}: ${self.close_price}"

class StockAlert(models.Model):
    ticker = models.CharField(max_length=10, default='UNKNOWN')
    company_name = models.CharField(max_length=255, blank=True, default='')
    current_price = models.FloatField(default=0.0, help_text="Current stock price in USD")
    price_change_today = models.FloatField(null=True, blank=True, help_text="Price change from previous close")
    price_change_percent = models.FloatField(null=True, blank=True, help_text="Percentage change from previous close")
    volume_today = models.BigIntegerField(default=0)
    avg_volume = models.BigIntegerField(null=True, blank=True)
    dvav = models.FloatField(null=True, blank=True)
    dvsa = models.FloatField(null=True, blank=True)
    pe_ratio = models.FloatField(null=True, blank=True)
    market_cap = models.BigIntegerField(null=True, blank=True)
    note = models.TextField(blank=True, default='')
    last_update = models.DateTimeField(auto_now_add=True)
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
    ticker = models.CharField(max_length=10, default='UNKNOWN')
    company_name = models.CharField(max_length=255, blank=True, default='')
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

# ==================== NEW ADVANCED FEATURES ====================

class APIUsageTracking(models.Model):
    """Track API usage for analytics and billing"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='api_usage')
    endpoint = models.CharField(max_length=200, db_index=True)
    method = models.CharField(max_length=10, choices=[
        ('GET', 'GET'),
        ('POST', 'POST'),
        ('PUT', 'PUT'),
        ('DELETE', 'DELETE'),
        ('PATCH', 'PATCH')
    ])
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    response_time_ms = models.IntegerField(help_text="Response time in milliseconds")
    status_code = models.IntegerField()
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    request_size_bytes = models.IntegerField(default=0)
    response_size_bytes = models.IntegerField(default=0)
    membership_tier = models.CharField(max_length=20, db_index=True)

    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['endpoint', 'timestamp']),
            models.Index(fields=['membership_tier', 'timestamp']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.endpoint} ({self.timestamp})"

class MarketSentiment(models.Model):
    """Market sentiment analysis for stocks"""
    ticker = models.CharField(max_length=10, db_index=True)
    sentiment_source = models.CharField(max_length=50, choices=[
        ('twitter', 'Twitter'),
        ('reddit', 'Reddit'),
        ('news', 'Financial News'),
        ('analyst_reports', 'Analyst Reports'),
        ('options_flow', 'Options Flow'),
        ('social_aggregate', 'Social Media Aggregate'),
        ('professional', 'Professional Analysis')
    ])
    sentiment_score = models.FloatField(help_text="Score from -1.0 (very bearish) to 1.0 (very bullish)")
    confidence_level = models.FloatField(help_text="Confidence level from 0.0 to 1.0")
    volume_mentions = models.IntegerField(default=0, help_text="Number of mentions/posts analyzed")
    positive_mentions = models.IntegerField(default=0)
    negative_mentions = models.IntegerField(default=0)
    neutral_mentions = models.IntegerField(default=0)
    key_phrases = models.JSONField(default=list, help_text="Most mentioned phrases/keywords")
    sentiment_trend = models.CharField(max_length=20, choices=[
        ('improving', 'Improving'),
        ('declining', 'Declining'),
        ('stable', 'Stable'),
        ('volatile', 'Volatile')
    ], default='stable')
    analyzed_at = models.DateTimeField(auto_now_add=True, db_index=True)
    data_timeframe = models.CharField(max_length=20, default='24h', help_text="Timeframe of analyzed data")
    
    class Meta:
        ordering = ['-analyzed_at']
        unique_together = ('ticker', 'sentiment_source', 'analyzed_at')
        indexes = [
            models.Index(fields=['ticker', 'analyzed_at']),
            models.Index(fields=['sentiment_score', 'analyzed_at']),
        ]
    
    def __str__(self):
        return f"{self.ticker} - {self.get_sentiment_source_display()}: {self.sentiment_score:.2f}"
    
    @property
    def sentiment_label(self):
        """Human-readable sentiment label"""
        if self.sentiment_score >= 0.3:
            return "Bullish"
        elif self.sentiment_score <= -0.3:
            return "Bearish"
        else:
            return "Neutral"

class PortfolioAnalytics(models.Model):
    """Advanced portfolio analytics and metrics"""
    portfolio = models.OneToOneField(Portfolio, on_delete=models.CASCADE, related_name='analytics')
    
    # Risk Metrics
    sharpe_ratio = models.FloatField(null=True, blank=True, help_text="Risk-adjusted return measure")
    beta = models.FloatField(null=True, blank=True, help_text="Market sensitivity")
    alpha = models.FloatField(null=True, blank=True, help_text="Excess return vs market")
    value_at_risk_1d = models.FloatField(null=True, blank=True, help_text="1-day VaR at 95% confidence")
    value_at_risk_1w = models.FloatField(null=True, blank=True, help_text="1-week VaR at 95% confidence")
    max_drawdown = models.FloatField(null=True, blank=True, help_text="Maximum historical loss")
    volatility_annualized = models.FloatField(null=True, blank=True, help_text="Annualized volatility")
    
    # Performance Metrics
    total_return_1m = models.FloatField(null=True, blank=True)
    total_return_3m = models.FloatField(null=True, blank=True)
    total_return_6m = models.FloatField(null=True, blank=True)
    total_return_1y = models.FloatField(null=True, blank=True)
    total_return_ytd = models.FloatField(null=True, blank=True)
    annualized_return = models.FloatField(null=True, blank=True)
    
    # Diversification Metrics
    sector_concentration_risk = models.FloatField(null=True, blank=True, help_text="0-1, higher means more concentrated")
    geographic_concentration = models.FloatField(null=True, blank=True)
    largest_position_weight = models.FloatField(null=True, blank=True)
    effective_number_stocks = models.FloatField(null=True, blank=True, help_text="Diversification measure")
    
    # Allocation Data
    sector_allocation = models.JSONField(default=dict, help_text="Sector breakdown percentages")
    market_cap_allocation = models.JSONField(default=dict, help_text="Large/Mid/Small cap breakdown")
    geographic_allocation = models.JSONField(default=dict, help_text="Geographic region breakdown")
    
    # Attribution Analysis
    performance_attribution = models.JSONField(default=dict, help_text="Performance attribution by holding")
    top_contributors = models.JSONField(default=list, help_text="Top 5 performance contributors")
    top_detractors = models.JSONField(default=list, help_text="Top 5 performance detractors")
    
    # Rebalancing Suggestions
    rebalancing_needed = models.BooleanField(default=False)
    rebalancing_suggestions = models.JSONField(default=list, help_text="Suggested portfolio adjustments")
    risk_score = models.IntegerField(default=50, help_text="Overall portfolio risk score 1-100")
    
    # Metadata
    last_calculated = models.DateTimeField(auto_now=True)
    calculation_status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('calculating', 'Calculating'),
        ('completed', 'Completed'),
        ('failed', 'Failed')
    ], default='pending')
    
    class Meta:
        ordering = ['-last_calculated']
    
    def __str__(self):
        return f"Analytics for {self.portfolio.name}"
    
    def get_risk_level(self):
        """Get human-readable risk level"""
        if self.risk_score <= 30:
            return "Conservative"
        elif self.risk_score <= 60:
            return "Moderate"
        elif self.risk_score <= 80:
            return "Aggressive"
        else:
            return "Very Aggressive"

class ComplianceLog(models.Model):
    """Regulatory compliance and security audit log"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='compliance_logs')
    action_type = models.CharField(max_length=50, choices=[
        ('login', 'User Login'),
        ('logout', 'User Logout'),
        ('password_change', 'Password Change'),
        ('profile_update', 'Profile Update'),
        ('payment_processed', 'Payment Processed'),
        ('data_export', 'Data Export'),
        ('api_access', 'API Access'),
        ('data_deletion', 'Data Deletion'),
        ('consent_given', 'Privacy Consent Given'),
        ('consent_withdrawn', 'Privacy Consent Withdrawn'),
        ('suspicious_activity', 'Suspicious Activity Detected'),
        ('security_violation', 'Security Policy Violation'),
        ('admin_action', 'Admin Action Performed')
    ])
    description = models.TextField()
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    session_id = models.CharField(max_length=40, blank=True)
    request_data = models.JSONField(default=dict, help_text="Relevant request data for audit")
    compliance_status = models.CharField(max_length=20, choices=[
        ('compliant', 'Compliant'),
        ('flagged', 'Flagged for Review'),
        ('violation', 'Policy Violation'),
        ('resolved', 'Resolved')
    ], default='compliant')
    risk_level = models.CharField(max_length=10, choices=[
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical')
    ], default='low')
    regulatory_framework = models.CharField(max_length=20, choices=[
        ('gdpr', 'GDPR'),
        ('ccpa', 'CCPA'),
        ('finra', 'FINRA'),
        ('sox', 'Sarbanes-Oxley'),
        ('mifid', 'MiFID II'),
        ('pci_dss', 'PCI DSS'),
        ('general', 'General Security')
    ], default='general')
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='resolved_compliance_logs')
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['action_type', 'timestamp']),
            models.Index(fields=['compliance_status', 'risk_level']),
            models.Index(fields=['regulatory_framework', 'timestamp']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.get_action_type_display()} ({self.timestamp})"

class SecurityEvent(models.Model):
    """Security events and threat detection"""
    event_type = models.CharField(max_length=50, choices=[
        ('failed_login', 'Failed Login Attempt'),
        ('brute_force', 'Brute Force Attack'),
        ('unusual_access', 'Unusual Access Pattern'),
        ('data_breach_attempt', 'Data Breach Attempt'),
        ('sql_injection', 'SQL Injection Attempt'),
        ('xss_attempt', 'XSS Attack Attempt'),
        ('rate_limit_exceeded', 'Rate Limit Exceeded'),
        ('unauthorized_api_access', 'Unauthorized API Access'),
        ('suspicious_geolocation', 'Suspicious Geographic Location'),
        ('account_takeover', 'Potential Account Takeover'),
        ('malware_detected', 'Malware Detection'),
        ('phishing_attempt', 'Phishing Attempt')
    ])
    severity = models.CharField(max_length=10, choices=[
        ('info', 'Informational'),
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical')
    ])
    source_ip = models.GenericIPAddressField()
    target_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='security_events')
    target_endpoint = models.CharField(max_length=200, blank=True)
    description = models.TextField()
    request_data = models.JSONField(default=dict)
    geolocation = models.JSONField(default=dict, help_text="IP geolocation data")
    user_agent = models.TextField(blank=True)
    attack_vector = models.CharField(max_length=100, blank=True)
    mitigation_action = models.CharField(max_length=50, choices=[
        ('none', 'No Action'),
        ('logged', 'Logged Only'),
        ('blocked', 'Request Blocked'),
        ('rate_limited', 'Rate Limited'),
        ('account_locked', 'Account Locked'),
        ('ip_banned', 'IP Address Banned'),
        ('escalated', 'Escalated to Admin')
    ], default='logged')
    detected_at = models.DateTimeField(auto_now_add=True, db_index=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    false_positive = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-detected_at']
        indexes = [
            models.Index(fields=['severity', 'detected_at']),
            models.Index(fields=['source_ip', 'detected_at']),
            models.Index(fields=['event_type', 'detected_at']),
        ]
    
    def __str__(self):
        return f"{self.get_event_type_display()} - {self.severity} ({self.detected_at})"
