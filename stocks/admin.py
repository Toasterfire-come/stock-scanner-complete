from django.contrib import admin
from django.contrib.auth.models import User
from emails.models import EmailSubscription
from .models import StockAlert
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
        
        # Calculate member statistics
        total_users = User.objects.count()
        email_subs = EmailSubscription.objects.filter(is_active=True).count()
        
        # Simulated membership data for demo
        total_members = 142
        monthly_revenue = 1847.53
        avg_spending = round(monthly_revenue / total_members, 2)
        
        extra_context.update({
            'show_analytics': True,
            'total_members': total_members,
            'monthly_revenue': monthly_revenue,
            'avg_spending_per_person': avg_spending,
            'email_subscribers': email_subs,
            'projected_annual': round(monthly_revenue * 12, 2)
        })
        return super().changelist_view(request, extra_context=extra_context)
