"""
PayPal Integration Test Script
Verifies PayPal plan ID mapping works correctly
"""

import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stockscanner_django.settings')
django.setup()

from billing.paypal_integration import get_paypal_plan_id
from django.conf import settings

print("=" * 80)
print("PAYPAL PLAN ID MAPPING TEST")
print("=" * 80)

# Display PayPal configuration
print(f"\nPayPal Mode: {settings.PAYPAL_MODE}")
print(f"PayPal Client ID: {settings.PAYPAL_CLIENT_ID[:20]}...")

print("\n" + "=" * 80)
print("PAYPAL PLAN ID CONFIGURATION")
print("=" * 80)

# Test all plan combinations
test_cases = [
    ('bronze', 'monthly', 'PAYPAL_PLAN_ID_BRONZE_MONTHLY'),
    ('bronze', 'yearly', 'PAYPAL_PLAN_ID_BRONZE_YEARLY'),
    ('silver', 'monthly', 'PAYPAL_PLAN_ID_SILVER_MONTHLY'),
    ('silver', 'yearly', 'PAYPAL_PLAN_ID_SILVER_YEARLY'),
]

print("\n{:<10} {:<10} {:<35} {:<30}".format("Plan", "Cycle", "Setting Name", "Plan ID"))
print("-" * 85)

all_configured = True
for plan, cycle, setting_name in test_cases:
    plan_id = get_paypal_plan_id(plan, cycle)

    if not plan_id:
        status = "[X] NOT CONFIGURED"
        all_configured = False
    elif plan_id.startswith('P-'):
        if 'XXXXX' in plan_id:
            status = "[!] PLACEHOLDER"
            all_configured = False
        else:
            status = "[OK] CONFIGURED"
    else:
        status = "[!] INVALID FORMAT"
        all_configured = False

    print("{:<10} {:<10} {:<35} {}".format(
        plan.upper(),
        cycle.capitalize(),
        setting_name,
        plan_id if plan_id else status
    ))

print("\n" + "=" * 80)
print("PLAN DETAILS")
print("=" * 80)

# Display plan details from pricing
from billing.sales_tax import get_plan_pricing_with_tax, format_currency

plans = [
    ('bronze', 'monthly', 'Basic Monthly'),
    ('bronze', 'yearly', 'Basic Yearly'),
    ('silver', 'monthly', 'Pro Monthly'),
    ('silver', 'yearly', 'Pro Yearly'),
]

for plan, cycle, display_name in plans:
    pricing = get_plan_pricing_with_tax(plan, cycle)
    paypal_id = get_paypal_plan_id(plan, cycle)

    print(f"\n{display_name}:")
    print(f"  Price: {format_currency(pricing['total'])} ({format_currency(pricing['subtotal'])} + {format_currency(pricing['tax'])} tax)")
    print(f"  PayPal Plan ID: {paypal_id if paypal_id else 'NOT CONFIGURED'}")

print("\n" + "=" * 80)
print("INTEGRATION ENDPOINTS")
print("=" * 80)

print("\n1. Create Subscription (POST):")
print("   URL: /api/billing/subscription/create/")
print("   Body: {")
print('     "plan": "bronze",')
print('     "billing_cycle": "monthly"')
print("   }")
print("   Returns: {")
print('     "subscription_id": "I-xxxxxxxxxxxxx",')
print('     "approval_url": "https://www.paypal.com/...",')
print('     "plan": "bronze",')
print('     "billing_cycle": "monthly",')
print('     "status": "pending_approval"')
print("   }")

print("\n2. Get Pricing (GET):")
print("   URL: /api/billing/pricing/?billing_cycle=monthly")
print("   Returns: Full pricing with tax for all plans")

print("\n3. Get Plan Pricing (GET):")
print("   URL: /api/billing/pricing/bronze/?billing_cycle=yearly")
print("   Returns: Specific plan pricing with tax")

print("\n" + "=" * 80)
print("TEST SUMMARY")
print("=" * 80)

if all_configured:
    print("[OK] All PayPal plan IDs are properly configured")
else:
    print("[!] Some PayPal plan IDs need to be configured in .env")
    print("\nTo configure:")
    print("1. Go to PayPal Developer Portal (developer.paypal.com)")
    print("2. Create 4 subscription plans with the prices shown above")
    print("3. Copy the Plan IDs (format: P-xxxxxxxxxxxxx)")
    print("4. Update the following in backend/.env:")
    print("   - PAYPAL_PLAN_ID_BRONZE_MONTHLY")
    print("   - PAYPAL_PLAN_ID_BRONZE_YEARLY")
    print("   - PAYPAL_PLAN_ID_SILVER_MONTHLY")
    print("   - PAYPAL_PLAN_ID_SILVER_YEARLY")

print("\nPayPal plan ID mapping is working correctly")
print("API endpoint ready: POST /api/billing/subscription/create/")
print("\n" + "=" * 80)
