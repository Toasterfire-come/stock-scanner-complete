"""
Django management command to initialize REF50 discount code
Usage: python manage.py initialize_ref50
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from stocks.services.discount_service import DiscountService
from stocks.models import DiscountCode, UserDiscountUsage, RevenueTracking


class Command(BaseCommand):
    help = 'Initialize the REF50 discount code and revenue tracking system'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force recreation of REF50 code if it exists',
        )
        parser.add_argument(
            '--demo-data',
            action='store_true',
            help='Create demo revenue data for testing',
        )
    
    def handle(self, *args, **options):
        self.stdout.write('Initializing REF50 discount code system...')
        
        # Initialize REF50 code
        code, created = DiscountService.initialize_ref50_code()
        
        if created:
            self.stdout.write(
                self.style.SUCCESS(f'✓ REF50 code created successfully: {code.discount_percentage}% off')
            )
        else:
            if options['force']:
                code.discount_percentage = 50.00
                code.is_active = True
                code.applies_to_first_payment_only = True
                code.save()
                self.stdout.write(
                    self.style.SUCCESS('✓ REF50 code updated successfully')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'✓ REF50 code already exists: {code.discount_percentage}% off')
                )
        
        # Show current status
        self.stdout.write('\nCurrent REF50 Status:')
        self.stdout.write(f'  Code: {code.code}')
        self.stdout.write(f'  Discount: {code.discount_percentage}%')
        self.stdout.write(f'  Active: {code.is_active}')
        self.stdout.write(f'  First payment only: {code.applies_to_first_payment_only}')
        self.stdout.write(f'  Times used: {code.user_usage.count()}')
        
        # Create demo data if requested
        if options['demo_data']:
            self.create_demo_data(code)
        
        # Generate current month summary
        current_month = timezone.now().strftime('%Y-%m')
        summary = DiscountService.update_monthly_summary(current_month)
        
        self.stdout.write('\nCurrent Month Summary:')
        self.stdout.write(f'  Month: {summary.month_year}')
        self.stdout.write(f'  Total Revenue: ${summary.total_revenue}')
        self.stdout.write(f'  Discount Generated Revenue: ${summary.discount_generated_revenue}')
        self.stdout.write(f'  Commission Owed: ${summary.total_commission_owed}')
        self.stdout.write(f'  Total Users: {summary.total_paying_users}')
        self.stdout.write(f'  New Discount Users: {summary.new_discount_users}')
        
        self.stdout.write(
            self.style.SUCCESS('\n✓ REF50 system initialization complete!')
        )
    
    def create_demo_data(self, ref50_code):
        """Create demo revenue data for testing"""
        from django.utils import timezone
        from decimal import Decimal
        import random
        
        self.stdout.write('\nCreating demo data...')
        
        # Create some test users if they don't exist
        demo_users = []
        for i in range(5):
            username = f'demo_user_{i+1}'
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': f'{username}@example.com',
                    'first_name': f'Demo',
                    'last_name': f'User {i+1}'
                }
            )
            demo_users.append(user)
            if created:
                self.stdout.write(f'  Created demo user: {username}')
        
        # Create demo revenue records
        current_month = timezone.now()
        original_prices = [9.99, 19.99, 29.99, 49.99]
        
        for i, user in enumerate(demo_users):
            price = random.choice(original_prices)
            
            # First payment with discount (if odd index)
            if i % 2 == 1:
                DiscountService.record_payment(
                    user=user,
                    original_amount=Decimal(str(price)),
                    discount_code=ref50_code,
                    payment_date=current_month
                )
                self.stdout.write(f'  Created discounted payment for {user.username}: ${price} -> ${price/2}')
                
                # Second payment (full price, but still tracked as discount-generated)
                DiscountService.record_payment(
                    user=user,
                    original_amount=Decimal(str(price)),
                    discount_code=ref50_code,
                    payment_date=current_month
                )
                self.stdout.write(f'  Created full-price payment for {user.username}: ${price} (discount user)')
            else:
                # Regular payment
                DiscountService.record_payment(
                    user=user,
                    original_amount=Decimal(str(price)),
                    payment_date=current_month
                )
                self.stdout.write(f'  Created regular payment for {user.username}: ${price}')
        
        self.stdout.write('✓ Demo data created successfully!')