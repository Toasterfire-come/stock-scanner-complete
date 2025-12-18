"""
Clean Database for Production - Remove Test Data
Removes all user accounts and subscription data, keeping only system accounts
Run: python clean_database_for_production.py
"""

import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stockscanner_django.settings')
django.setup()

from django.contrib.auth import get_user_model
from billing.models import Subscription, Payment, Invoice, PayPalWebhookEvent
from django.db import transaction

User = get_user_model()

def print_header(text):
    """Print section header"""
    print(f"\n{'='*70}")
    print(f"{text}")
    print(f"{'='*70}\n")

def confirm_action(prompt):
    """Get user confirmation"""
    response = input(f"{prompt} (yes/no): ").strip().lower()
    return response == 'yes'

def clean_database():
    """Clean database of all user and subscription data"""

    print_header("Database Cleanup Script - Production Ready")

    print("This script will:")
    print("  - Delete ALL user accounts (except superusers)")
    print("  - Delete ALL subscriptions")
    print("  - Delete ALL payments")
    print("  - Delete ALL invoices")
    print("  - Delete ALL PayPal webhook events")
    print("\nWARNING: This action CANNOT be undone!")

    if not confirm_action("\nDo you want to proceed?"):
        print("\nOperation cancelled.")
        return

    # Double confirmation
    if not confirm_action("\nAre you ABSOLUTELY SURE?"):
        print("\nOperation cancelled.")
        return

    print("\nStarting database cleanup...")

    try:
        with transaction.atomic():
            # Count before deletion
            user_count = User.objects.exclude(is_superuser=True).count()
            subscription_count = Subscription.objects.count()
            payment_count = Payment.objects.count()
            invoice_count = Invoice.objects.count()
            webhook_count = PayPalWebhookEvent.objects.count()

            print(f"\nFound:")
            print(f"  - {user_count} regular users")
            print(f"  - {subscription_count} subscriptions")
            print(f"  - {payment_count} payments")
            print(f"  - {invoice_count} invoices")
            print(f"  - {webhook_count} webhook events")

            # Delete webhook events
            print("\n[1/5] Deleting PayPal webhook events...")
            PayPalWebhookEvent.objects.all().delete()
            print(f"  ✓ Deleted {webhook_count} webhook events")

            # Delete invoices
            print("\n[2/5] Deleting invoices...")
            Invoice.objects.all().delete()
            print(f"  ✓ Deleted {invoice_count} invoices")

            # Delete payments
            print("\n[3/5] Deleting payments...")
            Payment.objects.all().delete()
            print(f"  ✓ Deleted {payment_count} payments")

            # Delete subscriptions
            print("\n[4/5] Deleting subscriptions...")
            Subscription.objects.all().delete()
            print(f"  ✓ Deleted {subscription_count} subscriptions")

            # Delete regular users (keep superusers)
            print("\n[5/5] Deleting regular user accounts...")
            deleted_users = User.objects.exclude(is_superuser=True).delete()
            print(f"  ✓ Deleted {user_count} user accounts")

            # Show remaining superusers
            superusers = User.objects.filter(is_superuser=True)
            print(f"\n  Preserved {superusers.count()} superuser account(s):")
            for user in superusers:
                print(f"    - {user.username} ({user.email})")

            print_header("Database Cleanup Complete!")
            print("Your database is now clean and ready for production.")
            print("\nNext steps:")
            print("  1. Run migrations: python manage.py migrate")
            print("  2. Test authentication flows")
            print("  3. Test PayPal checkout")
            print("  4. Verify all systems are working\n")

    except Exception as e:
        print(f"\n❌ Error during cleanup: {str(e)}")
        print("Changes have been rolled back.")
        raise

def show_statistics():
    """Show current database statistics"""
    print_header("Current Database Statistics")

    total_users = User.objects.count()
    superusers = User.objects.filter(is_superuser=True).count()
    regular_users = User.objects.exclude(is_superuser=True).count()
    subscriptions = Subscription.objects.count()
    payments = Payment.objects.count()
    invoices = Invoice.objects.count()
    webhooks = PayPalWebhookEvent.objects.count()

    print(f"Users:")
    print(f"  - Total users: {total_users}")
    print(f"  - Superusers: {superusers}")
    print(f"  - Regular users: {regular_users}")
    print(f"\nBilling:")
    print(f"  - Active subscriptions: {subscriptions}")
    print(f"  - Total payments: {payments}")
    print(f"  - Invoices: {invoices}")
    print(f"  - Webhook events: {webhooks}\n")

    # Show subscription breakdown
    if subscriptions > 0:
        from billing.models import PlanTier
        print("Subscription breakdown:")
        for tier in PlanTier:
            count = Subscription.objects.filter(plan_tier=tier.value).count()
            if count > 0:
                print(f"  - {tier.label}: {count}")
        print()

def main():
    """Main function"""
    import argparse

    parser = argparse.ArgumentParser(description='Clean database for production')
    parser.add_argument('--stats', action='store_true', help='Show database statistics only')
    parser.add_argument('--clean', action='store_true', help='Clean the database')

    args = parser.parse_args()

    if args.stats:
        show_statistics()
    elif args.clean:
        clean_database()
    else:
        # Show stats and offer to clean
        show_statistics()
        if confirm_action("Do you want to clean the database?"):
            clean_database()
        else:
            print("\nOperation cancelled.")

if __name__ == '__main__':
    main()
