"""
Upgrade VIP Accounts to Plus Plan
Simple script to upgrade specific accounts without database cleaning
Run: python upgrade_vip_accounts.py
"""

import os
import sys
import django
from decimal import Decimal

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stockscanner_django.settings')
django.setup()

from django.contrib.auth import get_user_model
from billing.models import Subscription, PlanTier, BillingCycle
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

# VIP email to upgrade
VIP_EMAIL = 'carter.kiefer2010@outlook.com'

def main():
    print("="*70)
    print("VIP Account Upgrade to Plus Plan (Unlimited)")
    print("="*70)

    # Find all users with this email (case-insensitive)
    users = User.objects.filter(email__iexact=VIP_EMAIL)
    print(f"\nFound {users.count()} user(s) matching '{VIP_EMAIL}':")

    for user in users:
        print(f"\n  ID: {user.id}")
        print(f"  Email: {user.email}")
        print(f"  Username: {user.username}")
        print(f"  Last Login: {user.last_login}")
        print(f"  Is Active: {user.is_active}")

        # Get or create subscription
        subscription, created = Subscription.objects.get_or_create(
            user=user,
            defaults={
                'plan_tier': PlanTier.PLUS,
                'billing_cycle': BillingCycle.ANNUAL,
                'status': 'active',
                'monthly_price': Decimal('0.00'),  # Complimentary
                'current_period_start': timezone.now(),
                'current_period_end': timezone.now() + timedelta(days=3650),  # 10 years
            }
        )

        if not created:
            # Update existing subscription
            subscription.plan_tier = PlanTier.PLUS
            subscription.billing_cycle = BillingCycle.ANNUAL
            subscription.status = 'active'
            subscription.monthly_price = Decimal('0.00')
            subscription.current_period_end = timezone.now() + timedelta(days=3650)
            subscription.save()
            print(f"  [OK] Updated existing subscription")
        else:
            print(f"  [OK] Created new Plus subscription")

        print(f"\n  Subscription Details:")
        print(f"    Plan: {subscription.get_plan_tier_display()}")
        print(f"    Cycle: {subscription.get_billing_cycle_display()}")
        print(f"    Status: {subscription.status}")
        print(f"    Price: ${subscription.monthly_price}")
        print(f"    Expires: {subscription.current_period_end.strftime('%Y-%m-%d')}")

    print("\n" + "="*70)
    print("VIP Account Upgrade Complete!")
    print("="*70)

    # Show all current subscriptions
    print("\nAll Active Plus Subscriptions:")
    plus_subs = Subscription.objects.filter(plan_tier=PlanTier.PLUS, status='active')
    for sub in plus_subs:
        print(f"  - {sub.user.email}: Expires {sub.current_period_end.strftime('%Y-%m-%d') if sub.current_period_end else 'Never'}")

if __name__ == '__main__':
    main()
