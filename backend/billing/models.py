from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid


class PlanTier(models.TextChoices):
    FREE = 'free', 'Free'
    BASIC = 'basic', 'Basic'
    PLUS = 'plus', 'Plus'


class BillingCycle(models.TextChoices):
    MONTHLY = 'monthly', 'Monthly'
    ANNUAL = 'annual', 'Annual'


class Subscription(models.Model):
    """User subscription model"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='subscription')
    
    # Plan details
    plan_tier = models.CharField(max_length=20, choices=PlanTier.choices, default=PlanTier.FREE)
    billing_cycle = models.CharField(max_length=20, choices=BillingCycle.choices, default=BillingCycle.MONTHLY)
    
    # PayPal subscription details
    paypal_subscription_id = models.CharField(max_length=255, blank=True, null=True, unique=True)
    paypal_plan_id = models.CharField(max_length=255, blank=True, null=True)
    
    # Status
    status = models.CharField(max_length=20, default='active', choices=[
        ('active', 'Active'),
        ('cancelled', 'Cancelled'),
        ('suspended', 'Suspended'),
        ('expired', 'Expired'),
    ])
    
    # Dates
    start_date = models.DateTimeField(default=timezone.now)
    current_period_start = models.DateTimeField(default=timezone.now)
    current_period_end = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    
    # Pricing
    monthly_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Discount
    discount_code = models.CharField(max_length=50, blank=True, null=True)
    discount_percentage = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'subscriptions'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.plan_tier} ({self.status})"
    
    @property
    def is_active(self):
        return self.status == 'active'
    
    @property
    def is_trial(self):
        """Check if user is on trial (first month)"""
        if self.current_period_end:
            days_since_start = (timezone.now() - self.start_date).days
            return days_since_start < 30
        return False


class Payment(models.Model):
    """Payment transaction model"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    subscription = models.ForeignKey(Subscription, on_delete=models.SET_NULL, null=True, blank=True, related_name='payments')
    
    # PayPal details
    paypal_order_id = models.CharField(max_length=255, unique=True)
    paypal_payer_id = models.CharField(max_length=255, blank=True, null=True)
    paypal_capture_id = models.CharField(max_length=255, blank=True, null=True)
    
    # Amount details
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Payment details
    status = models.CharField(max_length=20, default='pending', choices=[
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ])
    
    plan_tier = models.CharField(max_length=20, choices=PlanTier.choices)
    billing_cycle = models.CharField(max_length=20, choices=BillingCycle.choices)
    
    # Metadata
    discount_code = models.CharField(max_length=50, blank=True, null=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True, null=True)
    
    # Tax details
    tax_state = models.CharField(max_length=2, blank=True, null=True)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'payments'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - ${self.amount} - {self.status}"


class Invoice(models.Model):
    """Invoice model for payment records"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='invoices')
    payment = models.OneToOneField(Payment, on_delete=models.CASCADE, related_name='invoice')
    
    invoice_number = models.CharField(max_length=50, unique=True)
    
    # PDF storage
    pdf_url = models.URLField(blank=True, null=True)
    pdf_generated = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'invoices'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Invoice {self.invoice_number} - {self.user.username}"
    
    def generate_invoice_number(self):
        """Generate unique invoice number"""
        from datetime import datetime
        timestamp = datetime.now().strftime('%Y%m%d')
        count = Invoice.objects.filter(invoice_number__startswith=f'INV-{timestamp}').count()
        return f'INV-{timestamp}-{count + 1:04d}'


class PayPalWebhookEvent(models.Model):
    """Log PayPal webhook events"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    event_id = models.CharField(max_length=255, unique=True)
    event_type = models.CharField(max_length=100)
    resource_type = models.CharField(max_length=100, blank=True, null=True)
    
    # Raw webhook data
    payload = models.JSONField()
    
    # Processing status
    processed = models.BooleanField(default=False)
    processing_error = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'paypal_webhook_events'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.event_type} - {self.event_id}"
