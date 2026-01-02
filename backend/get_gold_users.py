#!/usr/bin/env python3
"""
Script to extract Gold/Pro tier users for whitelist
"""
import os
import sys
import django

# Django setup
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stockscanner_django.settings')
django.setup()

from stocks.models import User
from billing.models import UserSubscription

# Get all users with premium subscriptions (gold, silver, or pro)
premium_users = UserSubscription.objects.filter(
    plan__in=['gold', 'silver', 'pro', 'basic']
).select_related('user')

print("Premium tier users (for whitelist):")
print("=" * 60)

whitelisted_emails = []
for sub in premium_users:
    if sub.user and sub.user.email:
        whitelisted_emails.append(sub.user.email)
        print(f"{sub.user.email} - Plan: {sub.plan}")

print("\n" + "=" * 60)
print(f"Total premium users: {len(whitelisted_emails)}")
print("\n" + "=" * 60)
print("Copy this to frontend/.env as REACT_APP_WHITELISTED_EMAILS:")
print("=" * 60)
print(','.join(whitelisted_emails))
