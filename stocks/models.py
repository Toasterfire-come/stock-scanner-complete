from django.db import models
from django.contrib.auth.models import User

class StockAlert(models.Model):
    ticker = models.CharField(max_length=10)
    company_name = models.CharField(max_length=255, blank=True)  # <- New field
    current_price = models.FloatField()
    volume_today = models.BigIntegerField()
    avg_volume = models.BigIntegerField(null=True, blank=True)
    dvav = models.FloatField(null=True, blank=True)
    dvsa = models.FloatField(null=True, blank=True)
    pe_ratio = models.FloatField(null=True, blank=True)
    market_cap = models.BigIntegerField(null=True, blank=True)
    note = models.TextField(blank=True)
    last_update = models.DateTimeField()
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
