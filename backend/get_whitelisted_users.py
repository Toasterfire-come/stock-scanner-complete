#!/usr/bin/env python3
"""
Script to extract Premium (Plus/Basic) tier users for whitelist
Plus = Pro tier ($24.99) - formerly Gold
Basic = Basic tier ($9.99)
"""
import os
import sys
import django

# Django setup
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stockscanner_django.settings')
django.setup()

from stocks.models import User
from billing.models import Subscription
from django.db import models

# Get all users with PLUS (Pro) or BASIC subscriptions - they should have whitelist access
# PLUS = what was "Gold" tier, now mapped to Pro ($24.99)
# BASIC = Basic tier ($9.99)
premium_users = Subscription.objects.filter(
    plan_tier__in=['plus', 'basic'],
    status='active'
).select_related('user')

print("Premium tier users (for whitelist):")
print("=" * 60)

whitelisted_emails = []
for sub in premium_users:
    if sub.user and sub.user.email:
        whitelisted_emails.append(sub.user.email)
        print(f"{sub.user.email} - Plan: {sub.plan_tier} ({sub.status})")

# Also get any user with is_staff or is_superuser (admins)
admin_users = User.objects.filter(models.Q(is_staff=True) | models.Q(is_superuser=True))
for user in admin_users:
    if user.email and user.email not in whitelisted_emails:
        whitelisted_emails.append(user.email)
        print(f"{user.email} - Admin/Staff")

print("\n" + "=" * 60)
print(f"Total whitelisted users: {len(whitelisted_emails)}")
print("\n" + "=" * 60)
print("Copy this to frontend/.env as REACT_APP_WHITELISTED_EMAILS:")
print("=" * 60)
if whitelisted_emails:
    print(','.join(whitelisted_emails))
else:
    print("# No premium users found - add manually or leave empty to disable whitelist")
    print("# Example: user1@example.com,admin@company.com")
