"""
Create hamzashehata3000@gmail.com VIP Account with Plus Unlimited
Run: python create_hamza_vip_account.py
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

# VIP account details
VIP_EMAIL = 'hamzashehata3000@gmail.com'
VIP_USERNAME = 'hamzashehata3000'
VIP_PASSWORD = 'HamzaVIP@2024'  # Temporary password - user should change

def main():
    print("="*70)
    print("Creating VIP Account: hamzashehata3000@gmail.com")
    print("="*70)

    # Check if user already exists
    existing_user = User.objects.filter(email__iexact=VIP_EMAIL).first()

    if existing_user:
        print(f"\n[INFO] User already exists:")
        print(f"  ID: {existing_user.id}")
        print(f"  Email: {existing_user.email}")
        print(f"  Username: {existing_user.username}")
        user = existing_user
    else:
        # Create new user
        try:
            user = User.objects.create_user(
                username=VIP_USERNAME,
                email=VIP_EMAIL,
                password=VIP_PASSWORD,
                is_active=True
            )
            print(f"\n[OK] Created new user:")
            print(f"  ID: {user.id}")
            print(f"  Email: {user.email}")
            print(f"  Username: {user.username}")
            print(f"  Password: {VIP_PASSWORD}")
            print(f"  [NOTE] User should change password on first login")
        except Exception as e:
            print(f"\n[X] Error creating user: {str(e)}")
            return

    # Get or create Plus subscription with unlimited access
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
        # Update existing subscription to Plus unlimited
        subscription.plan_tier = PlanTier.PLUS
        subscription.billing_cycle = BillingCycle.ANNUAL
        subscription.status = 'active'
        subscription.monthly_price = Decimal('0.00')
        subscription.current_period_end = timezone.now() + timedelta(days=3650)
        subscription.save()
        print(f"\n[OK] Updated existing subscription to Plus unlimited")
    else:
        print(f"\n[OK] Created new Plus unlimited subscription")

    print(f"\nSubscription Details:")
    print(f"  Plan: {subscription.get_plan_tier_display()}")
    print(f"  Cycle: {subscription.get_billing_cycle_display()}")
    print(f"  Status: {subscription.status}")
    print(f"  Price: ${subscription.monthly_price} (Complimentary)")
    print(f"  Expires: {subscription.current_period_end.strftime('%Y-%m-%d')}")

    print("\n" + "="*70)
    print("VIP Account Created Successfully!")
    print("="*70)

    # Show all VIP accounts
    print("\nAll VIP Plus Accounts:")
    vip_emails = ['carter.kiefer2010@outlook.com', 'hamzashehata3000@gmail.com']
    for email in vip_emails:
        users = User.objects.filter(email__iexact=email)
        for user in users:
            sub = Subscription.objects.filter(user=user, plan_tier=PlanTier.PLUS).first()
            if sub:
                print(f"  - {user.email} (ID: {user.id}): Expires {sub.current_period_end.strftime('%Y-%m-%d')}")

if __name__ == '__main__':
    main()
