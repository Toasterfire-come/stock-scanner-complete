"""
Production Database Migration & Cleanup Script
- Preserves specific user accounts
- Upgrades preserved accounts to Plus plan with unlimited limits
- Migrates plan data from Bronze/Silver/Gold to Basic/Plus
- Removes all other test data
Run: python migrate_and_clean_database.py
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
from billing.models import Subscription, Payment, Invoice, PayPalWebhookEvent, PlanTier, BillingCycle
from django.db import transaction
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

# VIP users to preserve and upgrade
PRESERVED_EMAILS = [
    'carter.kiefer2010@outlook.com',
    'hamzashehata3000@gmail.com'  # Will be skipped if doesn't exist
]

class Colors:
    """ANSI color codes"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    """Print section header"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.RESET}\n")

def confirm_action(prompt):
    """Get user confirmation"""
    response = input(f"{Colors.YELLOW}{prompt} (yes/no): {Colors.RESET}").strip().lower()
    return response == 'yes'

def migrate_plan_tiers():
    """Migrate old plan tiers to new ones"""
    print_header("Step 1: Migrating Plan Tiers")

    plan_migration = {
        'bronze': 'basic',
        'silver': 'plus',
        'gold': 'plus',  # Gold users get Plus plan
    }

    subscriptions = Subscription.objects.all()
    migrated_count = 0

    for subscription in subscriptions:
        old_tier = subscription.plan_tier
        if old_tier in plan_migration:
            new_tier = plan_migration[old_tier]
            subscription.plan_tier = new_tier
            subscription.save()
            migrated_count += 1
            print(f"  {Colors.CYAN}Migrated:{Colors.RESET} {subscription.user.email if hasattr(subscription.user, 'email') else subscription.user.username} - {old_tier} -> {new_tier}")

    print(f"\n{Colors.GREEN}[OK] Migrated {migrated_count} subscriptions{Colors.RESET}")

def upgrade_preserved_users():
    """Upgrade preserved users to Plus plan with unlimited limits"""
    print_header("Step 2: Upgrading VIP Accounts to Plus Plan (Unlimited)")

    for email in PRESERVED_EMAILS:
        try:
            # Case-insensitive email lookup
            user = User.objects.get(email__iexact=email)
            print(f"\n{Colors.CYAN}Processing: {email}{Colors.RESET}")

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
                print(f"  {Colors.GREEN}[OK] Updated existing subscription{Colors.RESET}")
            else:
                print(f"  {Colors.GREEN}[OK] Created new Plus subscription{Colors.RESET}")

            print(f"  {Colors.MAGENTA}Plan: Plus (Unlimited){Colors.RESET}")
            print(f"  {Colors.MAGENTA}Status: Active{Colors.RESET}")
            print(f"  {Colors.MAGENTA}Expires: {subscription.current_period_end.strftime('%Y-%m-%d')}{Colors.RESET}")

        except User.DoesNotExist:
            print(f"  {Colors.RED}[X] User not found: {email}{Colors.RESET}")
        except Exception as e:
            print(f"  {Colors.RED}[X] Error: {str(e)}{Colors.RESET}")

def clean_database(auto_confirm=False):
    """Clean database except for preserved users and superusers"""
    print_header("Step 3: Cleaning Database (Preserving VIP Accounts)")

    # Get preserved user IDs (case-insensitive)
    from django.db.models import Q
    q_filters = Q()
    for email in PRESERVED_EMAILS:
        q_filters |= Q(email__iexact=email)
    preserved_users = User.objects.filter(q_filters)
    preserved_user_ids = list(preserved_users.values_list('id', flat=True))
    superuser_ids = list(User.objects.filter(is_superuser=True).values_list('id', flat=True))
    protected_user_ids = preserved_user_ids + superuser_ids

    print(f"\n{Colors.CYAN}Protected Accounts:{Colors.RESET}")
    for user in User.objects.filter(id__in=protected_user_ids):
        role = "Superuser" if user.is_superuser else "VIP"
        print(f"  - {user.email or user.username} ({role})")

    # Count records to be deleted
    users_to_delete = User.objects.exclude(id__in=protected_user_ids)
    user_count = users_to_delete.count()

    # Subscriptions and payments for deleted users
    subscriptions_to_delete = Subscription.objects.exclude(user_id__in=protected_user_ids)
    payments_to_delete = Payment.objects.exclude(user_id__in=protected_user_ids)
    invoices_to_delete = Invoice.objects.exclude(user_id__in=protected_user_ids)

    subscription_count = subscriptions_to_delete.count()
    payment_count = payments_to_delete.count()
    invoice_count = invoices_to_delete.count()
    webhook_count = PayPalWebhookEvent.objects.count()

    print(f"\n{Colors.YELLOW}Records to be deleted:{Colors.RESET}")
    print(f"  - {user_count} regular users (preserving {len(protected_user_ids)} protected accounts)")
    print(f"  - {subscription_count} subscriptions")
    print(f"  - {payment_count} payments")
    print(f"  - {invoice_count} invoices")
    print(f"  - {webhook_count} webhook events")

    if not auto_confirm:
        if not confirm_action("\nProceed with deletion?"):
            print(f"\n{Colors.RED}Operation cancelled{Colors.RESET}")
            return False

    try:
        with transaction.atomic():
            # Delete webhook events (no user reference)
            PayPalWebhookEvent.objects.all().delete()
            print(f"\n{Colors.GREEN}[OK] Deleted {webhook_count} webhook events{Colors.RESET}")

            # Delete invoices for non-protected users
            invoices_to_delete.delete()
            print(f"{Colors.GREEN}[OK] Deleted {invoice_count} invoices{Colors.RESET}")

            # Delete payments for non-protected users
            payments_to_delete.delete()
            print(f"{Colors.GREEN}[OK] Deleted {payment_count} payments{Colors.RESET}")

            # Delete subscriptions for non-protected users
            subscriptions_to_delete.delete()
            print(f"{Colors.GREEN}[OK] Deleted {subscription_count} subscriptions{Colors.RESET}")

            # Delete non-protected users
            users_to_delete.delete()
            print(f"{Colors.GREEN}[OK] Deleted {user_count} user accounts{Colors.RESET}")

            return True

    except Exception as e:
        print(f"\n{Colors.RED}[X] Error during cleanup: {str(e)}{Colors.RESET}")
        print(f"{Colors.RED}Changes have been rolled back{Colors.RESET}")
        return False

def show_final_statistics():
    """Show final database statistics"""
    print_header("Step 4: Final Database Statistics")

    total_users = User.objects.count()
    superusers = User.objects.filter(is_superuser=True).count()
    vip_users = User.objects.filter(email__in=PRESERVED_EMAILS).count()
    regular_users = total_users - superusers - vip_users

    subscriptions = Subscription.objects.count()
    plus_subs = Subscription.objects.filter(plan_tier=PlanTier.PLUS).count()
    basic_subs = Subscription.objects.filter(plan_tier=PlanTier.BASIC).count()
    free_subs = Subscription.objects.filter(plan_tier=PlanTier.FREE).count()

    payments = Payment.objects.count()
    invoices = Invoice.objects.count()
    webhooks = PayPalWebhookEvent.objects.count()

    print(f"{Colors.CYAN}Users:{Colors.RESET}")
    print(f"  - Total: {total_users}")
    print(f"  - Superusers: {superusers}")
    print(f"  - VIP Accounts: {vip_users}")
    print(f"  - Regular users: {regular_users}")

    print(f"\n{Colors.CYAN}Subscriptions:{Colors.RESET}")
    print(f"  - Total: {subscriptions}")
    print(f"  - Plus plan: {plus_subs}")
    print(f"  - Basic plan: {basic_subs}")
    print(f"  - Free plan: {free_subs}")

    print(f"\n{Colors.CYAN}Billing Records:{Colors.RESET}")
    print(f"  - Payments: {payments}")
    print(f"  - Invoices: {invoices}")
    print(f"  - Webhook events: {webhooks}")

    print(f"\n{Colors.MAGENTA}VIP Account Details:{Colors.RESET}")
    for email in PRESERVED_EMAILS:
        try:
            user = User.objects.get(email=email)
            subscription = Subscription.objects.filter(user=user).first()
            if subscription:
                print(f"\n  {Colors.BOLD}{email}{Colors.RESET}")
                print(f"    Plan: {subscription.get_plan_tier_display()}")
                print(f"    Cycle: {subscription.get_billing_cycle_display()}")
                print(f"    Status: {subscription.status}")
                print(f"    Expires: {subscription.current_period_end.strftime('%Y-%m-%d') if subscription.current_period_end else 'Never'}")
            else:
                print(f"\n  {Colors.BOLD}{email}{Colors.RESET}")
                print(f"    {Colors.YELLOW}No subscription found{Colors.RESET}")
        except User.DoesNotExist:
            print(f"\n  {Colors.BOLD}{email}{Colors.RESET}")
            print(f"    {Colors.RED}User not found{Colors.RESET}")

def main():
    """Main function"""
    import argparse
    parser = argparse.ArgumentParser(description='Migrate and clean database')
    parser.add_argument('--auto-confirm', action='store_true', help='Skip confirmations (USE WITH CAUTION)')
    args = parser.parse_args()

    print(f"\n{Colors.BOLD}{'='*70}{Colors.RESET}")
    print(f"{Colors.BOLD}Production Database Migration & Cleanup{Colors.RESET}")
    print(f"{Colors.BOLD}{'='*70}{Colors.RESET}")

    print(f"\n{Colors.CYAN}This script will:{Colors.RESET}")
    print(f"  1. Migrate plan tiers (Bronze->Basic, Silver/Gold->Plus)")
    print(f"  2. Upgrade VIP accounts to Plus plan with unlimited access:")
    for email in PRESERVED_EMAILS:
        print(f"     - {email}")
    print(f"  3. Remove all other test user data")
    print(f"  4. Show final statistics")

    print(f"\n{Colors.YELLOW}WARNING: This action CANNOT be undone!{Colors.RESET}")

    if not args.auto_confirm:
        if not confirm_action("\nDo you want to proceed?"):
            print(f"\n{Colors.RED}Operation cancelled{Colors.RESET}")
            return

        # Double confirmation
        if not confirm_action("\nAre you ABSOLUTELY SURE?"):
            print(f"\n{Colors.RED}Operation cancelled{Colors.RESET}")
            return
    else:
        print(f"\n{Colors.CYAN}Auto-confirm mode enabled - proceeding without prompts{Colors.RESET}")

    try:
        with transaction.atomic():
            # Step 1: Migrate plan tiers
            migrate_plan_tiers()

            # Step 2: Upgrade VIP accounts
            upgrade_preserved_users()

            # Step 3: Clean database
            success = clean_database(auto_confirm=args.auto_confirm)

            if not success:
                return

        # Step 4: Show final statistics
        show_final_statistics()

        print_header("Migration & Cleanup Complete!")

        print(f"{Colors.GREEN}[OK] Database is ready for production{Colors.RESET}")
        print(f"\n{Colors.CYAN}Next steps:{Colors.RESET}")
        print(f"  1. Test VIP account logins")
        print(f"  2. Verify Plus plan features are working")
        print(f"  3. Test new user registration")
        print(f"  4. Test PayPal checkout flow")
        print(f"  5. Run backend API tests\n")

    except Exception as e:
        print(f"\n{Colors.RED}[X] Error: {str(e)}{Colors.RESET}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
