"""
Django signals to automatically create memberships for new users
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Membership


@receiver(post_save, sender=User)
def create_user_membership(sender, instance, created, **kwargs):
    """
    Automatically create a free membership when a new user is created
    """
    if created:
        Membership.objects.create(
            user=instance,
            tier='free',
            monthly_price=0.00,
            is_active=True,
            subscription_status='active'
        )


@receiver(post_save, sender=User)
def save_user_membership(sender, instance, **kwargs):
    """
    Save the membership when user is saved
    """
    if hasattr(instance, 'membership'):
        instance.membership.save()
