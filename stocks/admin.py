from django.contrib import admin
from django.contrib.auth.models import User
from emails.models import EmailSubscription
from .models import (
    StockAlert, Membership, Portfolio, PortfolioHolding, MarketAnalysis, TechnicalIndicator,
    APIUsageTracking, MarketSentiment, PortfolioAnalytics, ComplianceLog, SecurityEvent
)
from django.utils import timezone

# Register your models here.
@admin.register(StockAlert)
class StockAlertAdmin(admin.ModelAdmin):
    list_display = ('ticker', 'company_name', 'current_price', 'volume_today', 'last_update')
    list_filter = ('last_update', 'sent')
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

# ==================== ADVANCED FEATURES ADMIN ====================

@admin.register(APIUsageTracking)
class APIUsageTrackingAdmin(admin.ModelAdmin):
    list_display = ['user', 'endpoint', 'method', 'timestamp', 'response_time_ms', 'status_code', 'membership_tier']
    list_filter = ['method', 'status_code', 'membership_tier', 'timestamp']
    search_fields = ['user__username', 'endpoint', 'ip_address']
    readonly_fields = ['timestamp']
    date_hierarchy = 'timestamp'
    
    def has_add_permission(self, request):
        return False  # These are created automatically

@admin.register(MarketSentiment)
class MarketSentimentAdmin(admin.ModelAdmin):
    list_display = ['ticker', 'sentiment_source', 'sentiment_score', 'sentiment_label', 'confidence_level', 'analyzed_at']
    list_filter = ['sentiment_source', 'sentiment_trend', 'analyzed_at']
    search_fields = ['ticker']
    readonly_fields = ['analyzed_at']
    date_hierarchy = 'analyzed_at'
    
    def sentiment_label(self, obj):
        return obj.sentiment_label
    sentiment_label.short_description = 'Sentiment'

@admin.register(PortfolioAnalytics)
class PortfolioAnalyticsAdmin(admin.ModelAdmin):
    list_display = ['portfolio', 'sharpe_ratio', 'beta', 'risk_score', 'calculation_status', 'last_calculated']
    list_filter = ['calculation_status', 'rebalancing_needed', 'last_calculated']
    search_fields = ['portfolio__name', 'portfolio__user__username']
    readonly_fields = ['last_calculated']
    
    fieldsets = (
        ('Portfolio Info', {
            'fields': ('portfolio', 'calculation_status', 'last_calculated')
        }),
        ('Risk Metrics', {
            'fields': ('sharpe_ratio', 'beta', 'alpha', 'value_at_risk_1d', 'value_at_risk_1w', 'max_drawdown', 'volatility_annualized')
        }),
        ('Performance Metrics', {
            'fields': ('total_return_1m', 'total_return_3m', 'total_return_6m', 'total_return_1y', 'total_return_ytd', 'annualized_return')
        }),
        ('Diversification', {
            'fields': ('sector_concentration_risk', 'geographic_concentration', 'largest_position_weight', 'effective_number_stocks')
        }),
        ('Rebalancing', {
            'fields': ('rebalancing_needed', 'risk_score')
        })
    )

@admin.register(ComplianceLog)
class ComplianceLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'action_type', 'compliance_status', 'risk_level', 'regulatory_framework', 'timestamp']
    list_filter = ['action_type', 'compliance_status', 'risk_level', 'regulatory_framework', 'timestamp']
    search_fields = ['user__username', 'description', 'ip_address']
    readonly_fields = ['timestamp']
    date_hierarchy = 'timestamp'
    
    fieldsets = (
        ('Event Info', {
            'fields': ('user', 'action_type', 'description', 'timestamp')
        }),
        ('Compliance', {
            'fields': ('compliance_status', 'risk_level', 'regulatory_framework')
        }),
        ('Technical Details', {
            'fields': ('ip_address', 'user_agent', 'session_id'),
            'classes': ('collapse',)
        }),
        ('Resolution', {
            'fields': ('resolved_at', 'resolved_by'),
            'classes': ('collapse',)
        })
    )

@admin.register(SecurityEvent)
class SecurityEventAdmin(admin.ModelAdmin):
    list_display = ['event_type', 'severity', 'source_ip', 'target_user', 'mitigation_action', 'detected_at']
    list_filter = ['event_type', 'severity', 'mitigation_action', 'false_positive', 'detected_at']
    search_fields = ['source_ip', 'target_user__username', 'description', 'target_endpoint']
    readonly_fields = ['detected_at']
    date_hierarchy = 'detected_at'
    
    fieldsets = (
        ('Event Details', {
            'fields': ('event_type', 'severity', 'description', 'detected_at')
        }),
        ('Target Info', {
            'fields': ('source_ip', 'target_user', 'target_endpoint')
        }),
        ('Response', {
            'fields': ('mitigation_action', 'resolved_at', 'false_positive')
        }),
        ('Technical Details', {
            'fields': ('user_agent', 'attack_vector'),
            'classes': ('collapse',)
        })
    )
    
    actions = ['mark_as_false_positive', 'escalate_event']
    
    def mark_as_false_positive(self, request, queryset):
        queryset.update(false_positive=True, resolved_at=timezone.now())
        self.message_user(request, f'Marked {queryset.count()} events as false positives.')
    mark_as_false_positive.short_description = 'Mark selected events as false positives'
    
    def escalate_event(self, request, queryset):
        queryset.update(mitigation_action='escalated')
        self.message_user(request, f'Escalated {queryset.count()} events.')
    escalate_event.short_description = 'Escalate selected events'
