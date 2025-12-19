"""
Create test data for partner analytics dashboard
Creates sample clicks, trials, and revenue for partner code ADAM50
"""
import os
import sys
import django
from datetime import datetime, timedelta
from decimal import Decimal

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stockscanner_django.settings')
django.setup()

from stocks.models import ReferralClickEvent, ReferralTrialEvent, RevenueTracking, DiscountCode
from django.contrib.auth.models import User
from django.utils import timezone

def create_test_data():
    """Create test analytics data for ADAM50 partner code"""

    # Get or create the discount code
    code, created = DiscountCode.objects.get_or_create(
        code='ADAM50',
        defaults={
            'discount_percentage': Decimal('50.00'),
            'discount_fixed_amount': Decimal('0.00'),
            'valid_from': timezone.now() - timedelta(days=90),
            'valid_until': timezone.now() + timedelta(days=365),
            'is_active': True,
            'max_uses': 1000,
            'times_used': 0,
            'description': 'Partner referral code - 50% off first payment'
        }
    )
    if created:
        print(f"[+] Created discount code: {code.code}")
    else:
        print(f"[+] Found existing discount code: {code.code}")

    # Create test clicks (last 30 days)
    print("\nCreating test clicks...")
    clicks_created = 0
    for i in range(50):
        days_ago = i // 2  # Group clicks over 25 days
        timestamp = timezone.now() - timedelta(days=days_ago, hours=i % 24)

        click, created = ReferralClickEvent.objects.get_or_create(
            code='ADAM50',
            session_id=f'test_session_{i}',
            defaults={
                'ip_hash': f'test_hash_{i}',
                'user_agent': 'Mozilla/5.0 (Test Browser)',
                'referrer': 'https://example.com',
                'created_at': timestamp
            }
        )
        if created:
            clicks_created += 1

    print(f"[+] Created {clicks_created} new clicks (total: {ReferralClickEvent.objects.filter(code='ADAM50').count()})")

    # Create test users and trials
    print("\nCreating test trials...")
    trials_created = 0

    for i in range(10):
        days_ago = i * 2  # Spread trials over 20 days
        timestamp = timezone.now() - timedelta(days=days_ago, hours=12)

        # Create test user
        username = f'testuser_{i}'
        email = f'testuser{i}@example.com'

        user, user_created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': email,
                'first_name': f'Test',
                'last_name': f'User {i}',
            }
        )

        # Create trial event
        trial, created = ReferralTrialEvent.objects.get_or_create(
            code='ADAM50',
            user=user,
            defaults={
                'session_id': f'test_session_{i*5}',  # Link to some clicks
                'created_at': timestamp
            }
        )
        if created:
            trials_created += 1

    print(f"[+] Created {trials_created} new trials (total: {ReferralTrialEvent.objects.filter(code='ADAM50').count()})")

    # Create test purchases with revenue tracking
    print("\nCreating test purchases...")
    purchases_created = 0

    for i in range(5):
        days_ago = i * 4  # Spread purchases over 20 days
        timestamp = timezone.now() - timedelta(days=days_ago, hours=14)

        user = User.objects.filter(username=f'testuser_{i}').first()
        if not user:
            continue

        # Purchase amount (Bronze: $24.99, Silver: $49.99)
        amounts = [Decimal('24.99'), Decimal('49.99')]
        amount = amounts[i % 2]
        commission = amount * Decimal('0.50')  # 50% commission
        discount = amount * Decimal('0.50')    # 50% discount to customer

        revenue, created = RevenueTracking.objects.get_or_create(
            user=user,
            discount_code=code,
            defaults={
                'order_id': f'TEST_ORDER_{i}',
                'paypal_order_id': f'PAYPAL_TEST_{i}',
                'plan_name': 'Bronze Monthly' if i % 2 == 0 else 'Silver Monthly',
                'original_amount': amount * 2,  # Original price before discount
                'discount_amount': discount,
                'final_amount': amount,
                'commission_amount': commission,
                'commission_percentage': Decimal('50.00'),
                'payment_status': 'completed',
                'payment_method': 'paypal',
                'currency': 'USD',
                'created_at': timestamp
            }
        )
        if created:
            purchases_created += 1

    print(f"[+] Created {purchases_created} new purchases (total: {RevenueTracking.objects.filter(discount_code__code='ADAM50').count()})")

    # Print summary
    print("\n" + "="*60)
    print("TEST DATA SUMMARY FOR ADAM50")
    print("="*60)

    total_clicks = ReferralClickEvent.objects.filter(code='ADAM50').count()
    total_trials = ReferralTrialEvent.objects.filter(code='ADAM50').count()
    total_purchases = RevenueTracking.objects.filter(discount_code__code='ADAM50').count()
    total_revenue = RevenueTracking.objects.filter(
        discount_code__code='ADAM50',
        payment_status='completed'
    ).aggregate(total=django.db.models.Sum('final_amount'))['total'] or Decimal('0.00')
    total_commission = RevenueTracking.objects.filter(
        discount_code__code='ADAM50',
        payment_status='completed'
    ).aggregate(total=django.db.models.Sum('commission_amount'))['total'] or Decimal('0.00')

    print(f"Total Clicks:     {total_clicks}")
    print(f"Total Trials:     {total_trials}")
    print(f"Total Purchases:  {total_purchases}")
    print(f"Total Revenue:    ${total_revenue}")
    print(f"Total Commission: ${total_commission}")
    print(f"\nClick→Trial Rate: {(total_trials/total_clicks*100):.1f}%" if total_clicks > 0 else "N/A")
    print(f"Trial→Purchase:   {(total_purchases/total_trials*100):.1f}%" if total_trials > 0 else "N/A")
    print("="*60)
    print("\n[SUCCESS] Test data created successfully!")
    print(f"\nLogin with: hamzashehata3000@gmail.com")
    print(f"Visit: http://localhost:3000/partner/analytics")
    print(f"Or: https://tradescanpro.com/partner/analytics\n")

if __name__ == '__main__':
    print("Creating partner analytics test data...")
    print("="*60)

    try:
        create_test_data()
    except Exception as e:
        print(f"\n[ERROR] Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
