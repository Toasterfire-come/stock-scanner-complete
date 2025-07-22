from django.contrib import admin
from django.contrib.auth.models import User
from emails.models import EmailSubscription
from .models import StockAlert, Membership, Portfolio, PortfolioHolding, MarketAnalysis, TechnicalIndicator
from django.utils import timezone

# Register your models here.
@admin.register(StockAlert)
class StockAlertAdmin(admin.ModelAdmin):
    list_display = ('ticker', 'company_name', 'current_price', 'volume_today', 'last_update')
    list_filter = ('last_update', 'sector')
    search_fields = ('ticker', 'company_name')
    readonly_fields = ('last_update',)
    
    def changelist_view(self, request, extra_context=None):
        # Add analytics data to the changelist view
        extra_context = extra_context or {}
        
        # Calculate real member statistics from database
        total_users = User.objects.count()
        email_subs = EmailSubscription.objects.filter(is_active=True).count()
        
        # Get real membership data
        total_members = Membership.objects.filter(is_active=True).count()
        
        # If no memberships exist, count all users as members
        if total_members == 0:
            total_members = total_users
        
        # Calculate real monthly revenue
        monthly_revenue = 0.00
        tier_pricing = {
            'free': 0.00,
            'basic': 9.99,
            'professional': 29.99,
            'expert': 49.99
        }
        
        for tier_code, price in tier_pricing.items():
            tier_count = Membership.objects.filter(tier=tier_code, is_active=True).count()
            monthly_revenue += tier_count * price
        
        avg_spending = round(monthly_revenue / total_members, 2) if total_members > 0 else 0.00
        
        extra_context.update({
            'show_analytics': True,
            'total_members': total_members,
            'monthly_revenue': monthly_revenue,
            'avg_spending_per_person': avg_spending,
            'email_subscribers': email_subs,
            'projected_annual': round(monthly_revenue * 12, 2)
        })
        return super().changelist_view(request, extra_context=extra_context)

@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ('user', 'tier', 'monthly_price', 'is_active', 'subscription_status', 'monthly_lookups_used', 'created_at')
    list_filter = ('tier', 'is_active', 'subscription_status', 'created_at')
    search_fields = ('user__username', 'user__email', 'stripe_customer_id')
    readonly_fields = ('created_at', 'updated_at', 'pricing_info', 'tier_limits')
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'tier', 'monthly_price', 'is_active')
        }),
        ('Subscription Details', {
            'fields': ('stripe_customer_id', 'stripe_subscription_id', 'subscription_status')
        }),
        ('Usage Tracking', {
            'fields': ('monthly_lookups_used', 'last_reset_date', 'tier_limits')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def pricing_info(self, obj):
        """Display pricing information"""
        return f"${obj.pricing_info:.2f}/month"
    pricing_info.short_description = "Tier Price"
    
         def tier_limits(self, obj):
         """Display lookup limits"""
         limits = obj.tier_limits
         if limits == -1:
             return "Unlimited"
         return f"{limits} lookups/month"
     tier_limits.short_description = "Monthly Limit"

@admin.register(Portfolio)
class PortfolioAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'total_value', 'total_gain_loss_percent', 'holdings_count', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at', 'updated_at')
    search_fields = ('name', 'user__username', 'user__email')
    readonly_fields = ('total_value', 'total_gain_loss', 'total_gain_loss_percent', 'holdings_count', 'created_at', 'updated_at')
    
    def holdings_count(self, obj):
        return obj.holdings.count()
    holdings_count.short_description = "Holdings"

@admin.register(PortfolioHolding)
class PortfolioHoldingAdmin(admin.ModelAdmin):
    list_display = ('portfolio', 'ticker', 'company_name', 'shares', 'purchase_price', 'current_price', 'gain_loss_percent', 'last_updated')
    list_filter = ('purchase_date', 'last_updated', 'portfolio__user')
    search_fields = ('ticker', 'company_name', 'portfolio__name', 'portfolio__user__username')
    readonly_fields = ('total_cost', 'total_value', 'gain_loss', 'gain_loss_percent', 'last_updated')

@admin.register(MarketAnalysis)
class MarketAnalysisAdmin(admin.ModelAdmin):
    list_display = ('title', 'analysis_type', 'author', 'is_premium', 'views', 'created_at')
    list_filter = ('analysis_type', 'is_premium', 'sector', 'created_at')
    search_fields = ('title', 'content', 'tickers', 'sector')
    readonly_fields = ('views', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Content', {
            'fields': ('title', 'content', 'analysis_type', 'tickers', 'sector')
        }),
        ('Publication', {
            'fields': ('author', 'is_premium', 'views')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(TechnicalIndicator)
class TechnicalIndicatorAdmin(admin.ModelAdmin):
    list_display = ('ticker', 'indicator_type', 'value', 'signal', 'confidence', 'calculated_at')
    list_filter = ('indicator_type', 'signal', 'calculated_at')
    search_fields = ('ticker',)
    readonly_fields = ('calculated_at',)
