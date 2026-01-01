"""
Email Subscription Models
Handles newsletter subscriptions and email preferences
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class EmailSubscription(models.Model):
    """
    Email subscription model for newsletter and alerts
    """
    email = models.EmailField(unique=True)
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='email_subscription'
    )

    # Subscription preferences
    subscribed_to_newsletter = models.BooleanField(default=True)
    subscribed_to_alerts = models.BooleanField(default=False)
    subscribed_to_reports = models.BooleanField(default=False)

    # Status tracking
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)

    # Timestamps
    subscribed_at = models.DateTimeField(default=timezone.now)
    last_email_sent = models.DateTimeField(null=True, blank=True)
    unsubscribed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-subscribed_at']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['is_active', 'is_verified']),
        ]

    def __str__(self):
        return f"{self.email} ({'Active' if self.is_active else 'Inactive'})"

    def unsubscribe(self):
        """Unsubscribe user from all emails"""
        self.is_active = False
        self.unsubscribed_at = timezone.now()
        self.subscribed_to_newsletter = False
        self.subscribed_to_alerts = False
        self.subscribed_to_reports = False
        self.save()
