"""
Django Admin Interface for Stock Scanner
Comprehensive admin interface for user management, subscriptions, and monitoring
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from django.db.models import Count, Sum, Avg
from datetime import timedelta
import json

from .models import (
    Stock, StockPrice, StockAlert, UserWatchlist, NewsItem, Portfolio, PortfolioHolding,
    UserProfile, UserSettings, PaymentPlan, PaymentTransaction, UserAPIUsage,
    UserTier
)

# ===== USER MANAGEMENT =====

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fields = (
        'tier', 'subscription_active', 'subscription_start', 'subscription_end',
        'paypal_subscription_id', 'enable_frontend_optimization', 
        'enable_client_side_charts', 'enable_progressive_loading',
        'max_cache_size_mb', 'api_calls_today', 'api_calls_this_month'
    )
    readonly_fields = ('api_calls_today', 'api_calls_this_month')

class UserSettingsInline(admin.StackedInline):
    model = UserSettings
    can_delete = False
    verbose_name_plural = 'Settings'
    fields = (
        'enable_virtual_scrolling', 'enable_fuzzy_search', 'enable_real_time_charts',
        'chart_theme', 'items_per_page', 'default_watchlist_view',
        'auto_refresh_interval', 'enable_notifications', 'share_usage_analytics'
    )

class CustomUserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline, UserSettingsInline)
    list_display = (
        'username', 'email', 'first_name', 'last_name', 'get_tier',
        'get_subscription_status', 'get_api_usage_today', 'date_joined', 'is_active'
    )
    list_filter = (
        'is_active', 'is_staff', 'date_joined', 'profile__tier', 'profile__subscription_active'
    )
    search_fields = ('username', 'email', 'first_name', 'last_name')
    
    def get_tier(self, obj):
        if hasattr(obj, 'profile'):
            tier = obj.profile.tier
            colors = {
                'free': 'gray',
                'basic': 'blue', 
                'pro': 'green',
                'enterprise': 'purple'
            }
            return format_html(
                '<span style="color: {}; font-weight: bold;">{}</span>',
                colors.get(tier, 'black'),
                tier.upper()
            )
        return 'No Profile'
    get_tier.short_description = 'Tier'
    
    def get_subscription_status(self, obj):
        if hasattr(obj, 'profile'):
            if obj.profile.is_subscription_active:
                return format_html('<span style="color: green;">✓ Active</span>')
            else:
                return format_html('<span style="color: red;">✗ Inactive</span>')
        return 'Unknown'
    get_subscription_status.short_description = 'Subscription'
    
    def get_api_usage_today(self, obj):
        if hasattr(obj, 'profile'):
            usage = obj.profile.api_calls_today
            limits = obj.profile.get_rate_limits()
            daily_limit = limits.get('api_calls_per_day', 1000)
            percentage = (usage / daily_limit) * 100 if daily_limit > 0 else 0
            
            color = 'red' if percentage > 80 else 'orange' if percentage > 60 else 'green'
            return format_html(
                '<span style="color: {};">{}/{} ({}%)</span>',
                color, usage, daily_limit, int(percentage)
            )
        return '0'
    get_api_usage_today.short_description = 'API Usage Today'

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

# ===== SUBSCRIPTION MANAGEMENT =====

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'tier', 'subscription_active', 'subscription_start', 
        'subscription_end', 'api_calls_today', 'api_calls_this_month'
    )
    list_filter = ('tier', 'subscription_active', 'enable_frontend_optimization')
    search_fields = ('user__username', 'user__email', 'paypal_subscription_id')
    readonly_fields = ('created_at', 'updated_at', 'last_api_call')
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'tier', 'created_at', 'updated_at')
        }),
        ('Subscription', {
            'fields': (
                'subscription_active', 'subscription_start', 'subscription_end',
                'paypal_subscription_id'
            )
        }),
        ('Frontend Optimization', {
            'fields': (
                'enable_frontend_optimization', 'enable_client_side_charts',
                'enable_progressive_loading', 'max_cache_size_mb'
            )
        }),
        ('API Usage', {
            'fields': ('api_calls_today', 'api_calls_this_month', 'last_api_call')
        })
    )
    
    actions = ['reset_daily_usage', 'reset_monthly_usage', 'upgrade_to_basic', 'upgrade_to_pro']
    
    def reset_daily_usage(self, request, queryset):
        updated = queryset.update(api_calls_today=0)
        self.message_user(request, f'Reset daily usage for {updated} users.')
    reset_daily_usage.short_description = 'Reset daily API usage'
    
    def reset_monthly_usage(self, request, queryset):
        updated = queryset.update(api_calls_this_month=0)
        self.message_user(request, f'Reset monthly usage for {updated} users.')
    reset_monthly_usage.short_description = 'Reset monthly API usage'
    
    def upgrade_to_basic(self, request, queryset):
        updated = queryset.update(tier='basic')
        self.message_user(request, f'Upgraded {updated} users to Basic tier.')
    upgrade_to_basic.short_description = 'Upgrade to Basic tier'
    
    def upgrade_to_pro(self, request, queryset):
        updated = queryset.update(tier='pro')
        self.message_user(request, f'Upgraded {updated} users to Pro tier.')
    upgrade_to_pro.short_description = 'Upgrade to Pro tier'

@admin.register(PaymentPlan)
class PaymentPlanAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'tier', 'price_monthly', 'price_yearly', 'get_yearly_savings',
        'is_active', 'created_at'
    )
    list_filter = ('tier', 'is_active')
    search_fields = ('name', 'tier')
    
    fieldsets = (
        ('Plan Information', {
            'fields': ('name', 'tier', 'is_active')
        }),
        ('Pricing', {
            'fields': ('price_monthly', 'price_yearly')
        }),
        ('PayPal Integration', {
            'fields': ('paypal_plan_id_monthly', 'paypal_plan_id_yearly')
        }),
        ('Features', {
            'fields': ('features',)
        })
    )
    
    def get_yearly_savings(self, obj):
        savings = (obj.price_monthly * 12) - obj.price_yearly
        return f'${savings:.2f}'
    get_yearly_savings.short_description = 'Yearly Savings'

@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'get_plan_name', 'amount', 'currency', 'status',
        'billing_cycle', 'created_at'
    )
    list_filter = ('status', 'billing_cycle', 'currency', 'created_at')
    search_fields = (
        'user__username', 'user__email', 'paypal_transaction_id',
        'paypal_subscription_id'
    )
    readonly_fields = ('created_at', 'updated_at', 'webhook_data')
    
    fieldsets = (
        ('Transaction Information', {
            'fields': (
                'user', 'plan', 'amount', 'currency', 'status', 'billing_cycle'
            )
        }),
        ('PayPal Details', {
            'fields': (
                'paypal_transaction_id', 'paypal_subscription_id'
            )
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
        ('Webhook Data', {
            'fields': ('webhook_data',),
            'classes': ('collapse',)
        })
    )
    
    def get_plan_name(self, obj):
        return obj.plan.name if obj.plan else 'Recurring Payment'
    get_plan_name.short_description = 'Plan'

# ===== API USAGE MONITORING =====

@admin.register(UserAPIUsage)
class UserAPIUsageAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'endpoint', 'method', 'status_code', 'response_time_ms',
        'user_tier', 'frontend_optimized', 'timestamp'
    )
    list_filter = (
        'method', 'status_code', 'user_tier', 'frontend_optimized', 'timestamp'
    )
    search_fields = ('user__username', 'endpoint')
    readonly_fields = ('timestamp',)
    date_hierarchy = 'timestamp'
    
    def has_add_permission(self, request):
        return False  # Don't allow manual creation
    
    def has_change_permission(self, request, obj=None):
        return False  # Don't allow editing

# ===== STOCK DATA MANAGEMENT =====

@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = (
        'ticker', 'company_name', 'current_price', 'change_percent',
        'volume', 'market_cap', 'last_updated'
    )
    list_filter = ('exchange', 'last_updated')
    search_fields = ('ticker', 'symbol', 'company_name', 'name')
    readonly_fields = ('last_updated',)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('ticker', 'symbol', 'company_name', 'name', 'exchange')
        }),
        ('Price Data', {
            'fields': (
                'current_price', 'change_percent', 'days_high', 'days_low',
                'fifty_two_week_high', 'fifty_two_week_low'
            )
        }),
        ('Volume and Market Data', {
            'fields': (
                'volume', 'average_volume', 'market_cap', 'shares_available',
                'pe_ratio', 'dividend_yield'
            )
        }),
        ('Timestamps', {
            'fields': ('last_updated',)
        })
    )

@admin.register(UserWatchlist)
class UserWatchlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'stock', 'added_date')
    list_filter = ('added_date',)
    search_fields = ('user__username', 'stock__ticker', 'stock__company_name')

@admin.register(StockAlert)
class StockAlertAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'stock', 'alert_type', 'threshold_value', 'is_active',
        'created_date', 'triggered_date'
    )
    list_filter = ('alert_type', 'is_active', 'created_date')
    search_fields = ('user__username', 'stock__ticker')

# ===== PORTFOLIO MANAGEMENT =====

@admin.register(Portfolio)
class PortfolioAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'get_total_value', 'created_date')
    search_fields = ('user__username', 'name')
    
    def get_total_value(self, obj):
        # Calculate total portfolio value
        holdings = obj.holdings.all()
        total = sum(holding.shares * holding.stock.current_price for holding in holdings)
        return f'${total:.2f}'
    get_total_value.short_description = 'Total Value'

@admin.register(PortfolioHolding)
class PortfolioHoldingAdmin(admin.ModelAdmin):
    list_display = (
        'portfolio', 'stock', 'shares', 'purchase_price', 'get_current_value',
        'get_gain_loss', 'purchase_date'
    )
    list_filter = ('purchase_date',)
    search_fields = ('portfolio__name', 'stock__ticker')
    
    def get_current_value(self, obj):
        value = obj.shares * obj.stock.current_price
        return f'${value:.2f}'
    get_current_value.short_description = 'Current Value'
    
    def get_gain_loss(self, obj):
        current_value = obj.shares * obj.stock.current_price
        cost_basis = obj.shares * obj.purchase_price
        gain_loss = current_value - cost_basis
        color = 'green' if gain_loss >= 0 else 'red'
        return format_html(
            '<span style="color: {};">${:.2f}</span>',
            color, gain_loss
        )
    get_gain_loss.short_description = 'Gain/Loss'

# ===== NEWS MANAGEMENT =====

@admin.register(NewsItem)
class NewsItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'source', 'published_date', 'stock')
    list_filter = ('source', 'published_date')
    search_fields = ('title', 'content', 'stock__ticker')
    date_hierarchy = 'published_date'

# ===== SYSTEM MONITORING =====

class SystemStatsAdmin(admin.ModelAdmin):
    """Custom admin view for system statistics"""
    change_list_template = 'admin/system_stats.html'
    
    def changelist_view(self, request, extra_context=None):
        # Calculate system statistics
        from django.db.models import Q
        
        # User statistics
        total_users = User.objects.count()
        active_users = User.objects.filter(last_login__gte=timezone.now() - timedelta(days=30)).count()
        premium_users = UserProfile.objects.filter(tier__in=['basic', 'pro', 'enterprise']).count()
        
        # API usage statistics
        today = timezone.now().date()
        api_calls_today = UserAPIUsage.objects.filter(timestamp__date=today).count()
        api_calls_this_month = UserAPIUsage.objects.filter(
            timestamp__gte=timezone.now().replace(day=1)
        ).count()
        
        # Revenue statistics
        monthly_revenue = PaymentTransaction.objects.filter(
            status='completed',
            created_at__gte=timezone.now().replace(day=1)
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        # Frontend optimization statistics
        optimized_calls = UserAPIUsage.objects.filter(
            timestamp__date=today,
            frontend_optimized=True
        ).count()
        optimization_rate = (optimized_calls / api_calls_today * 100) if api_calls_today > 0 else 0
        
        extra_context = extra_context or {}
        extra_context.update({
            'total_users': total_users,
            'active_users': active_users,
            'premium_users': premium_users,
            'api_calls_today': api_calls_today,
            'api_calls_this_month': api_calls_this_month,
            'monthly_revenue': monthly_revenue,
            'optimization_rate': optimization_rate,
            'optimized_calls': optimized_calls
        })
        
        return super().changelist_view(request, extra_context=extra_context)
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False

# Register the system stats view
admin.site.register(UserProfile, SystemStatsAdmin)

# ===== ADMIN SITE CUSTOMIZATION =====

admin.site.site_header = 'Stock Scanner Pro Administration'
admin.site.site_title = 'Stock Scanner Pro Admin'
admin.site.index_title = 'Welcome to Stock Scanner Pro Administration'

# Custom admin actions
def export_users_csv(modeladmin, request, queryset):
    """Export selected users to CSV"""
    import csv
    from django.http import HttpResponse
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="users.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Username', 'Email', 'Tier', 'Subscription Active', 'API Calls Today'])
    
    for user in queryset:
        profile = getattr(user, 'profile', None)
        writer.writerow([
            user.username,
            user.email,
            profile.tier if profile else 'free',
            profile.subscription_active if profile else False,
            profile.api_calls_today if profile else 0
        ])
    
    return response
export_users_csv.short_description = 'Export selected users to CSV'

# Add the action to the User admin
CustomUserAdmin.actions = list(CustomUserAdmin.actions or []) + [export_users_csv]
