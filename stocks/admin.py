from django.contrib import admin
from .models import (
    Stock, StockPrice, StockAlert, Membership,
    UserProfile, UserPortfolio, PortfolioHolding, TradeTransaction,
    UserWatchlist, WatchlistItem, UserInterests, PersonalizedNews,
    PortfolioFollowing, UserFollow, DiscountCode, UserDiscountUsage,
    RevenueTracking, MonthlyRevenueSummary
)

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

@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ['user', 'plan', 'is_active', 'created_at', 'expires_at']
    list_filter = ['plan', 'is_active', 'created_at']
    search_fields = ['user__username']

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

@admin.register(UserFollow)
class UserFollowAdmin(admin.ModelAdmin):
    list_display = ('follower', 'followed_user', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('follower__username', 'followed_user__username')

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
