"""
Billing Models
Handles subscriptions, payments, and billing records
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Subscription(models.Model):
    """
    User subscription model for different plan tiers
    """
    PLAN_CHOICES = [
        ('bronze', 'Bronze'),
        ('silver', 'Silver'),
        ('gold', 'Gold'),
    ]

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('cancelled', 'Cancelled'),
        ('expired', 'Expired'),
        ('trial', 'Trial'),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='subscription'
    )

    # Plan details
    plan = models.CharField(max_length=20, choices=PLAN_CHOICES, default='bronze')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')

    # Billing cycle
    billing_cycle = models.CharField(
        max_length=20,
        choices=[('monthly', 'Monthly'), ('yearly', 'Yearly')],
        default='monthly'
    )

    # Timestamps
    started_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)

    # Payment gateway integration
    stripe_customer_id = models.CharField(max_length=255, blank=True, null=True)
    stripe_subscription_id = models.CharField(max_length=255, blank=True, null=True)

    # Renewal settings
    auto_renew = models.BooleanField(default=True)
    next_billing_date = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['plan']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.get_plan_display()} ({self.status})"

    def is_active(self):
        """Check if subscription is currently active"""
        return self.status == 'active' and (
            not self.expires_at or self.expires_at > timezone.now()
        )


class PaymentHistory(models.Model):
    """
    Payment transaction history
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='payment_history'
    )

    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')

    # Payment details
    payment_method = models.CharField(max_length=50)
    payment_status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('completed', 'Completed'),
            ('failed', 'Failed'),
            ('refunded', 'Refunded'),
        ],
        default='pending'
    )

    # Transaction identifiers
    transaction_id = models.CharField(max_length=255, unique=True)
    stripe_payment_intent_id = models.CharField(max_length=255, blank=True, null=True)

    # Metadata
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Payment histories'
        indexes = [
            models.Index(fields=['user', 'payment_status']),
            models.Index(fields=['transaction_id']),
        ]

    def __str__(self):
        return f"{self.user.username} - ${self.amount} ({self.payment_status})"
