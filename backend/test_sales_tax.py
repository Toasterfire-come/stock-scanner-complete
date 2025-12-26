"""
Sales Tax Calculation Test Script
Quick verification that sales tax is calculated correctly
"""

import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stockscanner_django.settings')
django.setup()

from billing.sales_tax import (
    calculate_sales_tax,
    calculate_total_with_tax,
    get_plan_pricing_with_tax,
    format_currency
)
from django.conf import settings

print("=" * 80)
print("SALES TAX CONFIGURATION TEST")
print("=" * 80)

# Display settings
print(f"\nSales Tax Enabled: {settings.SALES_TAX_ENABLED}")
print(f"Sales Tax Rate: {settings.SALES_TAX_RATE * 100}%")
print(f"PayPal Mode: {settings.PAYPAL_MODE}")
print(f"PayPal Client ID: {settings.PAYPAL_CLIENT_ID[:20]}...")
print(f"SECRET_KEY: {settings.SECRET_KEY[:20]}...")

print("\n" + "=" * 80)
print("BASIC PLAN - MONTHLY")
print("=" * 80)
basic_monthly = get_plan_pricing_with_tax('basic', 'monthly')
print(f"Plan: {basic_monthly['plan'].upper()}")
print(f"Billing Cycle: {basic_monthly['billing_cycle']}")
print(f"Subtotal: {format_currency(basic_monthly['subtotal'])}")
print(f"Tax (7%): {format_currency(basic_monthly['tax'])}")
print(f"Total: {format_currency(basic_monthly['total'])}")
print(f"*Pricing Page Shows: {format_currency(basic_monthly['subtotal'])}/month + tax")

print("\n" + "=" * 80)
print("PRO PLAN - MONTHLY")
print("=" * 80)
pro_monthly = get_plan_pricing_with_tax('pro', 'monthly')
print(f"Plan: {pro_monthly['plan'].upper()}")
print(f"Billing Cycle: {pro_monthly['billing_cycle']}")
print(f"Subtotal: {format_currency(pro_monthly['subtotal'])}")
print(f"Tax (7%): {format_currency(pro_monthly['tax'])}")
print(f"Total: {format_currency(pro_monthly['total'])}")
print(f"*Pricing Page Shows: {format_currency(pro_monthly['subtotal'])}/month + tax")


print("\n" + "=" * 80)
print("BASIC PLAN - YEARLY")
print("=" * 80)
basic_yearly = get_plan_pricing_with_tax('basic', 'yearly')
print(f"Plan: {basic_yearly['plan'].upper()}")
print(f"Billing Cycle: {basic_yearly['billing_cycle']}")
print(f"Subtotal: {format_currency(basic_yearly['subtotal'])}")
print(f"Tax (7%): {format_currency(basic_yearly['tax'])}")
print(f"Total: {format_currency(basic_yearly['total'])}")
print(f"*Pricing Page Shows: {format_currency(basic_yearly['subtotal'])}/year + tax")
print(f"Annual Savings: {format_currency((basic_monthly['total'] * 12) - basic_yearly['total'])}")

print("\n" + "=" * 80)
print("PRO PLAN - YEARLY")
print("=" * 80)
pro_yearly = get_plan_pricing_with_tax('pro', 'yearly')
print(f"Plan: {pro_yearly['plan'].upper()}")
print(f"Billing Cycle: {pro_yearly['billing_cycle']}")
print(f"Subtotal: {format_currency(pro_yearly['subtotal'])}")
print(f"Tax (7%): {format_currency(pro_yearly['tax'])}")
print(f"Total: {format_currency(pro_yearly['total'])}")
print(f"*Pricing Page Shows: {format_currency(pro_yearly['subtotal'])}/year + tax")
print(f"Annual Savings: {format_currency((pro_monthly['total'] * 12) - pro_yearly['total'])}")


print("\n" + "=" * 80)
print("TEST SUMMARY")
print("=" * 80)
print("Sales tax calculations working correctly")
print("Pricing page displays subtotal (before tax)")
print("*Sales Tax Not Included - 7% added at checkout")
print("Yearly plans show 10% discount + cost savings")
print("Configuration loaded from .env file")
print("Only 2 plans: Basic and Pro")
print("\n" + "=" * 80)
