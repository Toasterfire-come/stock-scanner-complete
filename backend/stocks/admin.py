from django.contrib import admin
from .models import (
    Stock, StockPrice, StockAlert,
    UserProfile, UserPortfolio, PortfolioHolding, TradeTransaction,
    UserWatchlist, WatchlistItem, UserInterests, PersonalizedNews,
    PortfolioFollowing, DiscountCode, UserDiscountUsage,
    RevenueTracking, MonthlyRevenueSummary,
    PaperTradingAccount, PaperTrade, PaperTradePerformance,
    SMSAlertRule, SMSAlertCondition, SMSAlertHistory, SMSAlertQuota, TextBeltConfig,
    TwoFactorAuth, TwoFactorCode, TrustedDevice, TwoFactorAuditLog,
    OptionsChain, OptionsContract, ImpliedVolatilitySurface,
    OptionsScreenerResult, OptionsAnalytics, OptionsWatchlist, OptionsWatchlistItem,
    NewsSource, NewsArticle, SentimentAnalysis, NewsFeed, NewsAlert, SentimentTimeseries,
    TradingStrategy, StrategyScore, StrategyRating, StrategyClone, StrategyLeaderboard,
    LearningPath, Lesson, UserLessonProgress,
    IndicatorExplanation, FeatureWalkthrough, UserWalkthroughProgress,
    KnowledgeBaseArticle, UserKBFeedback
)
# Note: Membership model has been deprecated in favor of billing.models.Subscription

# Basic models
@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ['ticker', 'company_name', 'current_price', 'change_percent', 'volume', 'last_updated']
    list_filter = ['exchange', 'last_updated']
    search_fields = ['ticker', 'company_name']
    readonly_fields = ['created_at', 'last_updated']

@admin.register(StockPrice)
class StockPriceAdmin(admin.ModelAdmin):
    list_display = ['stock', 'price', 'timestamp']
    list_filter = ['timestamp']
    search_fields = ['stock__ticker']

@admin.register(StockAlert)
class StockAlertAdmin(admin.ModelAdmin):
    list_display = ['user', 'stock', 'alert_type', 'target_value', 'is_active', 'created_at']
    list_filter = ['alert_type', 'is_active', 'created_at']
    search_fields = ['user__username', 'stock__ticker']

# Membership model has been deprecated - use billing.models.Subscription instead
# To manage subscriptions, use the billing app admin interface

# User Profile
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'username', 'created_at', 'updated_at']
    search_fields = ['user__username', 'username']
    readonly_fields = ['created_at', 'updated_at']

# Portfolio models
@admin.register(UserPortfolio)
class UserPortfolioAdmin(admin.ModelAdmin):
    list_display = ['user', 'name', 'is_public', 'total_value', 'total_return_percent', 'created_at']
    list_filter = ['is_public', 'created_at']
    search_fields = ['user__username', 'name']
    readonly_fields = ['created_at', 'updated_at', 'followers_count', 'likes_count']

@admin.register(PortfolioHolding)
class PortfolioHoldingAdmin(admin.ModelAdmin):
    list_display = ['portfolio', 'stock', 'shares', 'average_cost', 'current_price', 'unrealized_gain_loss_percent', 'date_added']
    list_filter = ['date_added', 'from_alert']
    search_fields = ['portfolio__name', 'stock__ticker', 'portfolio__user__username']
    readonly_fields = ['date_added', 'last_updated', 'market_value', 'unrealized_gain_loss', 'unrealized_gain_loss_percent']

@admin.register(TradeTransaction)
class TradeTransactionAdmin(admin.ModelAdmin):
    list_display = ['portfolio', 'stock', 'transaction_type', 'shares', 'price', 'total_amount', 'transaction_date']
    list_filter = ['transaction_type', 'alert_category', 'transaction_date']
    search_fields = ['portfolio__name', 'stock__ticker', 'portfolio__user__username']
    readonly_fields = ['created_at']

# Watchlist models
@admin.register(UserWatchlist)
class UserWatchlistAdmin(admin.ModelAdmin):
    list_display = ['user', 'name', 'total_return_percent', 'best_performer', 'worst_performer', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'name']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(WatchlistItem)
class WatchlistItemAdmin(admin.ModelAdmin):
    list_display = ['watchlist', 'stock', 'added_price', 'current_price', 'price_change_percent', 'price_alert_enabled', 'added_at']
    list_filter = ['price_alert_enabled', 'news_alert_enabled', 'added_at']
    search_fields = ['watchlist__name', 'stock__ticker', 'watchlist__user__username']
    readonly_fields = ['added_at', 'price_change', 'price_change_percent']

# News personalization models
@admin.register(UserInterests)
class UserInterestsAdmin(admin.ModelAdmin):
    list_display = ['user', 'news_frequency', 'created_at', 'updated_at']
    list_filter = ['news_frequency', 'created_at']
    search_fields = ['user__username']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(PersonalizedNews)
class PersonalizedNewsAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'source', 'category', 'relevance_score', 'clicked', 'published_at']
    list_filter = ['category', 'source', 'clicked', 'published_at']
    search_fields = ['user__username', 'title', 'source']
    readonly_fields = ['created_at']

# Social features
@admin.register(PortfolioFollowing)
class PortfolioFollowingAdmin(admin.ModelAdmin):
    list_display = ['follower', 'followed_user', 'followed_portfolio', 'followed_at']
    list_filter = ['followed_at']
    search_fields = ['follower__username', 'followed_user__username']
    readonly_fields = ['followed_at']

@admin.register(DiscountCode)
class DiscountCodeAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_percentage', 'is_active', 'applies_to_first_payment_only', 'created_at', 'usage_count')
    list_filter = ('is_active', 'applies_to_first_payment_only', 'created_at')
    search_fields = ('code',)
    readonly_fields = ('created_at',)

    def usage_count(self, obj):
        return obj.user_usage.count()
    usage_count.short_description = 'Times Used'

@admin.register(UserDiscountUsage)
class UserDiscountUsageAdmin(admin.ModelAdmin):
    list_display = ('user', 'discount_code', 'first_used_date', 'total_savings')
    list_filter = ('discount_code', 'first_used_date')
    search_fields = ('user__username', 'user__email', 'discount_code__code')
    readonly_fields = ('first_used_date',)

@admin.register(RevenueTracking)
class RevenueTrackingAdmin(admin.ModelAdmin):
    list_display = ('user', 'revenue_type', 'final_amount', 'discount_code', 'commission_amount', 'month_year', 'payment_date')
    list_filter = ('revenue_type', 'month_year', 'discount_code', 'payment_date')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('commission_amount', 'month_year', 'created_at')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'discount_code')

@admin.register(MonthlyRevenueSummary)
class MonthlyRevenueSummaryAdmin(admin.ModelAdmin):
    list_display = (
        'month_year', 'total_revenue', 'discount_generated_revenue',
        'total_commission_owed', 'total_paying_users', 'new_discount_users'
    )
    list_filter = ('month_year',)
    readonly_fields = ('last_updated',)

    def has_add_permission(self, request):
        # These are auto-generated, so disable manual addition
        return False


# ============================================================================
# Paper Trading Admin
# ============================================================================

@admin.register(PaperTradingAccount)
class PaperTradingAccountAdmin(admin.ModelAdmin):
    list_display = ['user', 'name', 'total_value', 'total_return', 'total_trades', 'win_rate', 'is_active', 'created_at']
    list_filter = ['is_active', 'allow_shorting', 'created_at']
    search_fields = ['user__username', 'name']
    readonly_fields = ['created_at', 'last_updated', 'last_trade_at', 'total_return', 'win_rate', 'sharpe_ratio']
    
    fieldsets = (
        ('Account Info', {
            'fields': ('user', 'name', 'is_active')
        }),
        ('Balances', {
            'fields': ('initial_balance', 'cash_balance', 'equity_value', 'total_value')
        }),
        ('Performance', {
            'fields': ('total_return', 'total_profit_loss', 'realized_pl', 'unrealized_pl')
        }),
        ('Trading Statistics', {
            'fields': ('total_trades', 'winning_trades', 'losing_trades', 'win_rate')
        }),
        ('Risk Metrics', {
            'fields': ('max_drawdown', 'sharpe_ratio')
        }),
        ('Settings', {
            'fields': ('allow_shorting', 'max_position_size_pct')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'last_updated', 'last_trade_at')
        }),
    )


@admin.register(PaperTrade)
class PaperTradeAdmin(admin.ModelAdmin):
    list_display = ['id', 'account', 'stock', 'order_type', 'side', 'status', 'shares', 'entry_price', 'realized_pl', 'created_at']
    list_filter = ['order_type', 'side', 'status', 'created_at', 'filled_at', 'closed_at']
    search_fields = ['account__user__username', 'stock__ticker', 'notes']
    readonly_fields = ['created_at', 'filled_at', 'closed_at', 'holding_period_days']
    
    fieldsets = (
        ('Trade Info', {
            'fields': ('account', 'stock', 'order_type', 'side', 'status')
        }),
        ('Quantity & Pricing', {
            'fields': ('shares', 'entry_price', 'exit_price', 'current_price')
        }),
        ('Order Parameters', {
            'fields': ('limit_price', 'stop_price', 'trailing_amount', 'trailing_percent')
        }),
        ('Bracket Order (Pro)', {
            'fields': ('take_profit_price', 'stop_loss_price'),
            'classes': ('collapse',)
        }),
        ('Position Values', {
            'fields': ('entry_value', 'current_value', 'exit_value')
        }),
        ('Performance', {
            'fields': ('unrealized_pl', 'unrealized_pl_pct', 'realized_pl', 'realized_pl_pct')
        }),
        ('Fees', {
            'fields': ('commission',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'filled_at', 'closed_at', 'holding_period_days')
        }),
        ('Notes', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
    )


@admin.register(PaperTradePerformance)
class PaperTradePerformanceAdmin(admin.ModelAdmin):
    list_display = ['account', 'period_type', 'period_start', 'period_end', 'period_return', 'period_win_rate', 'trades_closed']
    list_filter = ['period_type', 'period_start']
    search_fields = ['account__user__username', 'account__name']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Period Info', {
            'fields': ('account', 'period_type', 'period_start', 'period_end')
        }),
        ('Performance', {
            'fields': ('starting_value', 'ending_value', 'period_return', 'period_pl')
        }),
        ('Trading Activity', {
            'fields': ('trades_opened', 'trades_closed', 'winning_trades', 'losing_trades', 'period_win_rate')
        }),
        ('Risk Metrics', {
            'fields': ('max_gain', 'max_loss', 'volatility')
        }),
        ('Benchmark', {
            'fields': ('benchmark_return', 'alpha'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at',)
        }),
    )


# ============================================================================
# SMS Alert System Admin
# ============================================================================

@admin.register(SMSAlertRule)
class SMSAlertRuleAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'name', 'stock', 'watchlist', 'is_active', 'trigger_count', 'created_at']
    list_filter = ['is_active', 'is_multi_condition', 'is_one_time', 'created_at']
    search_fields = ['user__username', 'name', 'stock__ticker', 'phone_number']
    readonly_fields = ['trigger_count', 'last_triggered_at', 'last_checked_at', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Alert Info', {
            'fields': ('user', 'name', 'stock', 'watchlist')
        }),
        ('Conditions', {
            'fields': ('is_multi_condition', 'condition_operator')
        }),
        ('Delivery', {
            'fields': ('phone_number', 'webhook_enabled', 'webhook_url')
        }),
        ('Status & Limits', {
            'fields': ('is_active', 'is_one_time', 'max_triggers_per_day')
        }),
        ('Statistics', {
            'fields': ('trigger_count', 'last_triggered_at', 'last_checked_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(SMSAlertCondition)
class SMSAlertConditionAdmin(admin.ModelAdmin):
    list_display = ['id', 'alert_rule', 'condition_type', 'target_value', 'indicator_period']
    list_filter = ['condition_type']
    search_fields = ['alert_rule__name', 'alert_rule__user__username']
    readonly_fields = ['last_met_at', 'created_at']


@admin.register(SMSAlertHistory)
class SMSAlertHistoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'alert_rule', 'stock', 'status', 'delivery_attempts', 'created_at']
    list_filter = ['status', 'webhook_sent', 'created_at']
    search_fields = ['alert_rule__name', 'stock__ticker', 'phone_number', 'textbelt_id']
    readonly_fields = ['created_at', 'sent_at', 'delivered_at']
    
    fieldsets = (
        ('Alert Info', {
            'fields': ('alert_rule', 'stock', 'phone_number', 'message')
        }),
        ('Trigger Details', {
            'fields': ('trigger_price', 'trigger_volume', 'condition_values')
        }),
        ('Delivery Status', {
            'fields': ('status', 'textbelt_id', 'textbelt_quota', 'delivery_attempts', 'max_attempts')
        }),
        ('Error Tracking', {
            'fields': ('error_message', 'last_attempt_at')
        }),
        ('Webhook', {
            'fields': ('webhook_sent', 'webhook_response'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'sent_at', 'delivered_at')
        }),
    )


@admin.register(SMSAlertQuota)
class SMSAlertQuotaAdmin(admin.ModelAdmin):
    list_display = ['user', 'current_usage', 'monthly_limit', 'total_sent', 'is_blocked']
    list_filter = ['is_blocked', 'last_reset_at']
    search_fields = ['user__username']
    readonly_fields = ['total_sent', 'created_at', 'updated_at']
    
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Quota', {
            'fields': ('monthly_limit', 'current_usage', 'last_reset_at', 'total_sent')
        }),
        ('Status', {
            'fields': ('is_blocked', 'block_reason')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(TextBeltConfig)
class TextBeltConfigAdmin(admin.ModelAdmin):
    list_display = ['id', 'is_enabled', 'is_self_hosted', 'total_sent', 'total_failed', 'last_sent_at']
    readonly_fields = ['total_sent', 'total_failed', 'last_sent_at', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Server Configuration', {
            'fields': ('api_url', 'api_key', 'is_self_hosted')
        }),
        ('Retry Settings', {
            'fields': ('max_retries', 'retry_delay_seconds')
        }),
        ('Rate Limiting', {
            'fields': ('max_sms_per_minute',)
        }),
        ('Monitoring', {
            'fields': ('total_sent', 'total_failed', 'last_sent_at')
        }),
        ('Status', {
            'fields': ('is_enabled',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )

    def has_add_permission(self, request):
        # Only allow one config instance
        return not TextBeltConfig.objects.exists()

    def has_delete_permission(self, request, obj=None):
        # Don't allow deletion of config
        return False


# ============================================================================
# Two-Factor Authentication Admin
# ============================================================================

@admin.register(TwoFactorAuth)
class TwoFactorAuthAdmin(admin.ModelAdmin):
    list_display = ['user', 'is_enabled', 'phone_number', 'backup_codes_count', 'total_verifications', 'is_locked']
    list_filter = ['is_enabled', 'require_on_login', 'trusted_devices_enabled', 'is_locked']
    search_fields = ['user__username', 'phone_number']
    readonly_fields = ['verified_at', 'total_verifications', 'failed_attempts', 'last_verified_at', 'last_failed_at', 'locked_until', 'created_at', 'updated_at']
    
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('2FA Status', {
            'fields': ('is_enabled', 'phone_number', 'verified_at')
        }),
        ('Backup Codes', {
            'fields': ('backup_codes_count',),
            'description': 'Backup codes are hashed and cannot be viewed'
        }),
        ('Security Settings', {
            'fields': ('require_on_login', 'require_on_sensitive', 'trusted_devices_enabled')
        }),
        ('Statistics', {
            'fields': ('total_verifications', 'failed_attempts', 'last_verified_at', 'last_failed_at')
        }),
        ('Lockout Protection', {
            'fields': ('is_locked', 'locked_until', 'consecutive_failures'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(TwoFactorCode)
class TwoFactorCodeAdmin(admin.ModelAdmin):
    list_display = ['user', 'code_type', 'code', 'is_used', 'expires_at', 'sms_sent', 'created_at']
    list_filter = ['code_type', 'is_used', 'sms_sent', 'created_at']
    search_fields = ['user__username', 'code', 'phone_number']
    readonly_fields = ['used_at', 'sms_sent_at', 'created_at']
    
    fieldsets = (
        ('Code Details', {
            'fields': ('user', 'code_type', 'code')
        }),
        ('Validity', {
            'fields': ('expires_at', 'is_used', 'used_at')
        }),
        ('Delivery', {
            'fields': ('phone_number', 'sms_sent', 'sms_sent_at', 'textbelt_id')
        }),
        ('Security', {
            'fields': ('verification_attempts', 'max_attempts', 'ip_address')
        }),
        ('Timestamp', {
            'fields': ('created_at',)
        }),
    )


# ============================================================================
# Strategy Ranking & Scoring Admin (registered at end of file with Education models)
# ============================================================================


@admin.register(TrustedDevice)
class TrustedDeviceAdmin(admin.ModelAdmin):
    list_display = ['user', 'device_name', 'ip_address', 'is_active', 'last_used_at', 'trust_expires_at']
    list_filter = ['is_active', 'trust_expires_at', 'created_at']
    search_fields = ['user__username', 'device_name', 'ip_address', 'device_fingerprint']
    readonly_fields = ['last_used_at', 'total_uses', 'created_at']
    
    fieldsets = (
        ('Device Info', {
            'fields': ('user', 'device_name', 'device_fingerprint')
        }),
        ('Details', {
            'fields': ('user_agent', 'ip_address', 'location')
        }),
        ('Trust Status', {
            'fields': ('is_active', 'trust_expires_at')
        }),
        ('Usage', {
            'fields': ('last_used_at', 'total_uses')
        }),
        ('Timestamp', {
            'fields': ('created_at',)
        }),
    )


@admin.register(TwoFactorAuditLog)
class TwoFactorAuditLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'event_type', 'success', 'ip_address', 'created_at']
    list_filter = ['event_type', 'success', 'created_at']
    search_fields = ['user__username', 'event_description', 'ip_address']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Event', {
            'fields': ('user', 'twofa', 'event_type', 'success')
        }),
        ('Details', {
            'fields': ('event_description',)
        }),
        ('Context', {
            'fields': ('ip_address', 'user_agent', 'device_fingerprint')
        }),
        ('Metadata', {
            'fields': ('metadata',),
            'classes': ('collapse',)
        }),
        ('Timestamp', {
            'fields': ('created_at',)
        }),
    )
    
    def has_add_permission(self, request):
        # Audit logs should only be created by system
        return False
    
    def has_change_permission(self, request, obj=None):
        # Audit logs should be immutable
        return False


# ============================================================================
# Options Analytics System Admin
# ============================================================================

@admin.register(OptionsChain)
class OptionsChainAdmin(admin.ModelAdmin):
    list_display = ['stock', 'snapshot_date', 'underlying_price', 'total_contracts', 'snapshot_time']
    list_filter = ['snapshot_date', 'is_current']
    search_fields = ['stock__ticker']
    readonly_fields = ['snapshot_time', 'total_contracts', 'created_at', 'updated_at']

    fieldsets = (
        ('Chain Info', {
            'fields': ('stock', 'snapshot_date', 'underlying_price', 'total_contracts', 'expirations_count')
        }),
        ('Data Source', {
            'fields': ('data_source', 'is_current')
        }),
        ('Timestamps', {
            'fields': ('snapshot_time', 'created_at', 'updated_at')
        }),
    )


@admin.register(OptionsContract)
class OptionsContractAdmin(admin.ModelAdmin):
    list_display = ['contract_symbol', 'contract_type', 'strike', 'expiration', 'dte', 'last_price', 'implied_volatility', 'in_the_money']
    list_filter = ['contract_type', 'in_the_money', 'expiration']
    search_fields = ['contract_symbol', 'chain__stock__ticker', 'stock__ticker']
    readonly_fields = ['created_at']

    fieldsets = (
        ('Contract Details', {
            'fields': ('chain', 'stock', 'contract_symbol', 'contract_type', 'strike', 'expiration', 'dte')
        }),
        ('Pricing', {
            'fields': ('last_price', 'bid', 'ask', 'mark')
        }),
        ('Volume & OI', {
            'fields': ('volume', 'open_interest')
        }),
        ('Implied Volatility', {
            'fields': ('implied_volatility',)
        }),
        ('Greeks', {
            'fields': ('delta', 'gamma', 'theta', 'vega', 'rho')
        }),
        ('Moneyness', {
            'fields': ('in_the_money', 'intrinsic_value', 'extrinsic_value', 'break_even', 'probability_itm')
        }),
        ('Timestamps', {
            'fields': ('created_at',)
        }),
    )


@admin.register(ImpliedVolatilitySurface)
class ImpliedVolatilitySurfaceAdmin(admin.ModelAdmin):
    list_display = ['stock', 'snapshot_date', 'underlying_price', 'avg_iv', 'atm_iv', 'put_call_iv_ratio']
    list_filter = ['snapshot_date']
    search_fields = ['stock__ticker']
    readonly_fields = ['snapshot_time', 'created_at']

    fieldsets = (
        ('Surface Info', {
            'fields': ('stock', 'snapshot_date', 'underlying_price')
        }),
        ('Surface Data', {
            'fields': ('surface_data',),
            'description': 'JSON grid of IV values by strike and expiration'
        }),
        ('Statistics', {
            'fields': ('avg_iv', 'min_iv', 'max_iv', 'atm_iv', 'put_call_iv_ratio')
        }),
        ('Timestamps', {
            'fields': ('snapshot_time', 'created_at')
        }),
    )


@admin.register(OptionsScreenerResult)
class OptionsScreenerResultAdmin(admin.ModelAdmin):
    list_display = ['stock', 'screener_type', 'score', 'scan_date', 'rank']
    list_filter = ['screener_type', 'scan_date']
    search_fields = ['stock__ticker']
    readonly_fields = ['scan_time', 'created_at']

    fieldsets = (
        ('Screener Info', {
            'fields': ('stock', 'contract', 'screener_type', 'scan_date')
        }),
        ('Ranking', {
            'fields': ('score', 'rank')
        }),
        ('Metrics', {
            'fields': ('trigger_metrics',),
            'description': 'JSON metrics that triggered this result'
        }),
        ('Timestamps', {
            'fields': ('scan_time', 'created_at')
        }),
    )


@admin.register(OptionsAnalytics)
class OptionsAnalyticsAdmin(admin.ModelAdmin):
    list_display = ['stock', 'date', 'total_call_volume', 'total_put_volume', 'put_call_volume_ratio']
    list_filter = ['date', 'unusual_call_volume', 'unusual_put_volume', 'iv_spike']
    search_fields = ['stock__ticker']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Daily Analytics', {
            'fields': ('stock', 'date')
        }),
        ('Volume Metrics', {
            'fields': ('total_call_volume', 'total_put_volume', 'put_call_volume_ratio')
        }),
        ('Open Interest', {
            'fields': ('total_call_oi', 'total_put_oi', 'put_call_oi_ratio')
        }),
        ('Implied Volatility', {
            'fields': ('avg_call_iv', 'avg_put_iv', 'iv_30_day', 'iv_rank', 'iv_percentile')
        }),
        ('Popular Strikes', {
            'fields': ('most_active_call_strike', 'most_active_put_strike')
        }),
        ('Unusual Activity Flags', {
            'fields': ('unusual_call_volume', 'unusual_put_volume', 'iv_spike')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(OptionsWatchlist)
class OptionsWatchlistAdmin(admin.ModelAdmin):
    list_display = ['user', 'name', 'is_default', 'items_count', 'created_at']
    list_filter = ['is_default', 'created_at']
    search_fields = ['user__username', 'name']
    readonly_fields = ['created_at', 'updated_at', 'items_count']

    def items_count(self, obj):
        return obj.items.count()
    items_count.short_description = 'Items'

    fieldsets = (
        ('Watchlist Info', {
            'fields': ('user', 'name', 'is_default')
        }),
        ('Statistics', {
            'fields': ('items_count',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(OptionsWatchlistItem)
class OptionsWatchlistItemAdmin(admin.ModelAdmin):
    list_display = ['watchlist', 'contract_symbol', 'contract_type', 'strike', 'expiration', 'added_at']
    list_filter = ['added_at']
    search_fields = ['watchlist__name', 'contract__contract_symbol', 'contract__chain__stock__ticker']
    readonly_fields = ['added_at', 'contract_symbol', 'contract_type', 'strike', 'expiration']

    def contract_symbol(self, obj):
        return obj.contract.contract_symbol
    contract_symbol.short_description = 'Contract'

    def contract_type(self, obj):
        return obj.contract.contract_type
    contract_type.short_description = 'Type'

    def strike(self, obj):
        return obj.contract.strike
    strike.short_description = 'Strike'

    def expiration(self, obj):
        return obj.contract.expiration
    expiration.short_description = 'Expiration'

    fieldsets = (
        ('Watchlist Item', {
            'fields': ('watchlist', 'contract', 'notes')
        }),
        ('Timestamps', {
            'fields': ('added_at',)
        }),
    )


# ============================================================================
# News & Sentiment System Admin
# ============================================================================

@admin.register(NewsSource)
class NewsSourceAdmin(admin.ModelAdmin):
    list_display = ['name', 'source_type', 'is_active', 'is_premium', 'reliability_score', 'total_articles_fetched', 'last_successful_fetch']
    list_filter = ['source_type', 'is_active', 'is_premium']
    search_fields = ['name', 'base_url']
    readonly_fields = ['total_articles_fetched', 'total_fetch_errors', 'last_request_at', 'last_successful_fetch', 'created_at', 'updated_at']

    fieldsets = (
        ('Source Info', {
            'fields': ('name', 'source_type', 'base_url')
        }),
        ('API Configuration', {
            'fields': ('api_key_required', 'api_key'),
            'classes': ('collapse',)
        }),
        ('Scraping Configuration', {
            'fields': ('scraping_rules',),
            'classes': ('collapse',)
        }),
        ('Quality & Settings', {
            'fields': ('reliability_score', 'requests_per_hour')
        }),
        ('Statistics', {
            'fields': ('total_articles_fetched', 'total_fetch_errors', 'last_request_at', 'last_successful_fetch')
        }),
        ('Status', {
            'fields': ('is_active', 'is_premium')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(NewsArticle)
class NewsArticleAdmin(admin.ModelAdmin):
    list_display = ['title_short', 'source', 'published_at', 'is_processed', 'view_count', 'click_count']
    list_filter = ['source', 'is_processed', 'category', 'published_at']
    search_fields = ['title', 'summary', 'author', 'mentioned_tickers']
    readonly_fields = ['content_hash', 'view_count', 'click_count', 'created_at', 'updated_at']
    filter_horizontal = ['stocks']

    def title_short(self, obj):
        return obj.title[:60] + '...' if len(obj.title) > 60 else obj.title
    title_short.short_description = 'Title'

    fieldsets = (
        ('Article Info', {
            'fields': ('source', 'external_id', 'url')
        }),
        ('Content', {
            'fields': ('title', 'summary', 'content', 'author')
        }),
        ('Publication', {
            'fields': ('published_at',)
        }),
        ('Related Entities', {
            'fields': ('stocks', 'mentioned_tickers')
        }),
        ('Classification', {
            'fields': ('category', 'tags')
        }),
        ('Engagement', {
            'fields': ('view_count', 'click_count')
        }),
        ('Processing', {
            'fields': ('is_processed', 'processing_errors', 'content_hash')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(SentimentAnalysis)
class SentimentAnalysisAdmin(admin.ModelAdmin):
    list_display = ['article_title', 'stock', 'sentiment_label', 'sentiment_score', 'confidence', 'analysis_engine', 'analyzed_at']
    list_filter = ['sentiment_label', 'analysis_engine', 'analyzed_at']
    search_fields = ['article__title', 'stock__ticker']
    readonly_fields = ['analyzed_at']

    def article_title(self, obj):
        return obj.article.title[:50] + '...' if len(obj.article.title) > 50 else obj.article.title
    article_title.short_description = 'Article'

    fieldsets = (
        ('Analysis Target', {
            'fields': ('article', 'stock')
        }),
        ('Sentiment Scores', {
            'fields': ('sentiment_label', 'sentiment_score', 'confidence')
        }),
        ('Detailed Scores', {
            'fields': ('positive_score', 'negative_score', 'neutral_score'),
            'classes': ('collapse',)
        }),
        ('Analysis Engine', {
            'fields': ('analysis_engine', 'engine_version')
        }),
        ('Advanced Analysis', {
            'fields': ('aspect_sentiments', 'entities_mentioned', 'key_phrases'),
            'classes': ('collapse',)
        }),
        ('Timestamp', {
            'fields': ('analyzed_at',)
        }),
    )


@admin.register(NewsFeed)
class NewsFeedAdmin(admin.ModelAdmin):
    list_display = ['user', 'notification_frequency', 'email_notifications', 'sms_notifications', 'created_at']
    list_filter = ['notification_frequency', 'email_notifications', 'sms_notifications']
    search_fields = ['user__username']
    readonly_fields = ['created_at', 'updated_at']
    filter_horizontal = ['followed_stocks', 'followed_sources']

    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Followed Entities', {
            'fields': ('followed_stocks', 'followed_sources')
        }),
        ('Preferences', {
            'fields': ('enabled_categories', 'min_sentiment_score', 'exclude_neutral')
        }),
        ('Notifications', {
            'fields': ('email_notifications', 'sms_notifications', 'notification_frequency')
        }),
        ('Alert Thresholds', {
            'fields': ('alert_on_very_positive', 'alert_on_very_negative')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(NewsAlert)
class NewsAlertAdmin(admin.ModelAdmin):
    list_display = ['user', 'stock', 'alert_type', 'sentiment_score', 'is_read', 'email_sent', 'sms_sent', 'created_at']
    list_filter = ['alert_type', 'is_read', 'email_sent', 'sms_sent', 'created_at']
    search_fields = ['user__username', 'stock__ticker', 'message']
    readonly_fields = ['created_at', 'read_at']

    fieldsets = (
        ('Alert Info', {
            'fields': ('user', 'stock', 'article', 'alert_type')
        }),
        ('Message', {
            'fields': ('message',)
        }),
        ('Trigger Data', {
            'fields': ('sentiment_score', 'trigger_data')
        }),
        ('Delivery Status', {
            'fields': ('is_read', 'email_sent', 'sms_sent')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'read_at')
        }),
    )


@admin.register(SentimentTimeseries)
class SentimentTimeseriesAdmin(admin.ModelAdmin):
    list_display = ['stock', 'interval', 'period_start', 'avg_sentiment_score', 'total_articles', 'positive_articles', 'negative_articles']
    list_filter = ['interval', 'period_start']
    search_fields = ['stock__ticker']
    readonly_fields = ['created_at']

    fieldsets = (
        ('Timeseries Info', {
            'fields': ('stock', 'interval', 'period_start', 'period_end')
        }),
        ('Sentiment Metrics', {
            'fields': ('avg_sentiment_score', 'weighted_sentiment', 'sentiment_std_dev')
        }),
        ('Article Counts', {
            'fields': ('total_articles', 'positive_articles', 'negative_articles', 'neutral_articles')
        }),
        ('Volume Metrics', {
            'fields': ('article_volume_change',)
        }),
        ('Timestamp', {
            'fields': ('created_at',)
        }),
    )


# ==================== STRATEGY RANKING & SCORING SYSTEM ====================
# Admin for strategy marketplace models

@admin.register(TradingStrategy)
class TradingStrategyAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'strategy_type', 'status', 'visibility', 'total_trades', 'win_rate', 'annual_return', 'clone_count', 'is_featured', 'created_at']
    list_filter = ['strategy_type', 'status', 'visibility', 'is_featured', 'is_verified', 'created_at']
    search_fields = ['name', 'description', 'user__email']
    readonly_fields = ['total_trades', 'winning_trades', 'losing_trades', 'clone_count', 'view_count', 'annual_return', 'sharpe_ratio', 'max_drawdown', 'win_rate', 'profit_factor', 'created_at', 'updated_at', 'last_traded_at']

    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'name', 'description', 'strategy_type', 'status', 'visibility')
        }),
        ('Strategy Configuration', {
            'fields': ('strategy_code', 'configuration', 'entry_rules', 'exit_rules'),
            'classes': ('collapse',)
        }),
        ('Risk Management', {
            'fields': ('max_position_size', 'max_portfolio_risk', 'stop_loss_pct', 'take_profit_pct')
        }),
        ('Paper Trading Integration', {
            'fields': ('paper_account', 'total_trades', 'winning_trades', 'losing_trades')
        }),
        ('Performance Metrics (Cached)', {
            'fields': ('annual_return', 'sharpe_ratio', 'max_drawdown', 'win_rate', 'profit_factor')
        }),
        ('Community Features', {
            'fields': ('is_featured', 'is_verified', 'clone_count', 'view_count')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'last_traded_at')
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'paper_account')


@admin.register(StrategyScore)
class StrategyScoreAdmin(admin.ModelAdmin):
    list_display = ['strategy', 'total_score', 'performance_score', 'risk_score', 'consistency_score', 'efficiency_score', 'community_score', 'is_sufficient_data', 'verification_status', 'last_calculated_at']
    list_filter = ['is_sufficient_data', 'verification_status', 'last_calculated_at']
    search_fields = ['strategy__name', 'strategy__user__email']
    readonly_fields = ['last_calculated_at', 'calculation_engine_version']

    fieldsets = (
        ('Strategy', {
            'fields': ('strategy',)
        }),
        ('Component Scores (0-100 scale)', {
            'fields': ('performance_score', 'risk_score', 'consistency_score', 'efficiency_score', 'community_score')
        }),
        ('Composite Score', {
            'fields': ('total_score', 'score_breakdown'),
            'classes': ('wide',)
        }),
        ('Validation', {
            'fields': ('min_trades_threshold', 'is_sufficient_data', 'verification_status')
        }),
        ('Metadata', {
            'fields': ('last_calculated_at', 'calculation_engine_version')
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('strategy')


@admin.register(StrategyRating)
class StrategyRatingAdmin(admin.ModelAdmin):
    list_display = ['strategy', 'user', 'rating', 'created_at', 'updated_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['strategy__name', 'user__email', 'review']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Rating', {
            'fields': ('strategy', 'user', 'rating', 'review')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('strategy', 'user')


@admin.register(StrategyClone)
class StrategyCloneAdmin(admin.ModelAdmin):
    list_display = ['cloned_strategy', 'original_strategy', 'user', 'is_modified', 'cloned_at']
    list_filter = ['is_modified', 'cloned_at']
    search_fields = ['original_strategy__name', 'cloned_strategy__name', 'user__email']
    readonly_fields = ['cloned_at']

    fieldsets = (
        ('Clone Relationship', {
            'fields': ('original_strategy', 'cloned_strategy', 'user')
        }),
        ('Customizations', {
            'fields': ('customizations', 'is_modified'),
            'classes': ('wide',)
        }),
        ('Timestamp', {
            'fields': ('cloned_at',)
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('original_strategy', 'cloned_strategy', 'user')


@admin.register(StrategyLeaderboard)
class StrategyLeaderboardAdmin(admin.ModelAdmin):
    list_display = ['rank', 'strategy', 'category', 'timeframe', 'score', 'calculated_at']
    list_filter = ['category', 'timeframe', 'calculated_at']
    search_fields = ['strategy__name']
    readonly_fields = ['calculated_at']

    fieldsets = (
        ('Leaderboard Entry', {
            'fields': ('strategy', 'category', 'timeframe', 'rank', 'score')
        }),
        ('Snapshot Data', {
            'fields': ('snapshot_data',),
            'classes': ('wide',)
        }),
        ('Timestamp', {
            'fields': ('calculated_at',)
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('strategy')
