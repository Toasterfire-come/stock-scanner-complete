from django.contrib import admin
from .models import (
    Stock, StockPrice, StockAlert,
    UserProfile, UserPortfolio, PortfolioHolding, TradeTransaction,
    UserWatchlist, WatchlistItem, UserInterests, PersonalizedNews,
    PortfolioFollowing, DiscountCode, UserDiscountUsage,
    RevenueTracking, MonthlyRevenueSummary,
    PaperTradingAccount, PaperTrade, PaperTradePerformance,
    SMSAlertRule, SMSAlertCondition, SMSAlertHistory, SMSAlertQuota, TextBeltConfig
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
