"""
Django management command to create or update discount codes
Usage: python manage.py create_discount_code <CODE> <DISCOUNT_PERCENTAGE> [--inactive]
Example: python manage.py create_discount_code CARSONK 20
"""
from django.core.management.base import BaseCommand
from stocks.models import DiscountCode


class Command(BaseCommand):
    help = 'Create or update a discount code'

    def add_arguments(self, parser):
        parser.add_argument('code', type=str, help='Discount code (e.g., CARSONK)')
        parser.add_argument('discount_percentage', type=float, help='Discount percentage (e.g., 20 for 20% off)')
        parser.add_argument('--inactive', action='store_true', help='Create code as inactive')
        parser.add_argument('--all-payments', action='store_true', help='Apply to all payments (not just first)')

    def handle(self, *args, **options):
        code = options['code'].upper().strip()
        discount_percentage = options['discount_percentage']
        is_active = not options['inactive']
        first_payment_only = not options['all_payments']

        # Create or update the discount code
        discount_code, created = DiscountCode.objects.update_or_create(
            code=code,
            defaults={
                'discount_percentage': discount_percentage,
                'is_active': is_active,
                'applies_to_first_payment_only': first_payment_only,
            }
        )

        if created:
            self.stdout.write(self.style.SUCCESS(f'[OK] Created discount code: {code}'))
        else:
            self.stdout.write(self.style.SUCCESS(f'[OK] Updated discount code: {code}'))

        self.stdout.write(self.style.SUCCESS(f'  - Discount: {discount_percentage}%'))
        self.stdout.write(self.style.SUCCESS(f'  - Active: {is_active}'))
        self.stdout.write(self.style.SUCCESS(f'  - First payment only: {first_payment_only}'))
        self.stdout.write(self.style.SUCCESS(f'\nReferral link: https://tradescanpro.com/r/{code}'))
