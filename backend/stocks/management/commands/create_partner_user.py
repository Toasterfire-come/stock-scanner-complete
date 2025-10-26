"""
Create or update a partner user with a specific referral code and plan.
Usage:
  python manage.py create_partner_user \
    --email hamzashehata3000@gmail.com \
    --password ADAM5050 \
    --username hamza \
    --plan gold \
    --ref-code ADAM50

If an account already exists for the email, the password and profile will be updated.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from stocks.models import UserProfile
from stocks.services.discount_service import DiscountService


class Command(BaseCommand):
    help = "Create or update a partner user with referral code and plan"

    def add_arguments(self, parser):
        parser.add_argument('--email', required=True, help='User email')
        parser.add_argument('--password', required=True, help='User password')
        parser.add_argument('--username', help='Username (defaults to email local part)')
        parser.add_argument('--plan', default='gold', choices=['free','basic','bronze','silver','pro','gold','enterprise'])
        parser.add_argument('--ref-code', default='ADAM50', help='Referral code to configure for this partner')
        parser.add_argument('--billing-cycle', default='monthly', choices=['monthly','annual'])

    @transaction.atomic
    def handle(self, *args, **options):
        email = options['email'].strip().lower()
        password = options['password']
        username = (options.get('username') or email.split('@')[0]).strip()
        plan = options['plan'].strip().lower()
        ref_code = (options.get('ref_code') or options.get('ref-code') or 'ADAM50').strip().upper()
        billing_cycle = options['billing_cycle']

        User = get_user_model()
        user = User.objects.filter(email__iexact=email).first()
        if user is None:
            user = User.objects.create_user(username=username, email=email, password=password)
            self.stdout.write(self.style.SUCCESS(f"Created user '{username}' with email {email}"))
        else:
            # Update username if needed (avoid collisions)
            if not user.username:
                user.username = username
            user.set_password(password)
            user.save(update_fields=['username', 'password'])
            self.stdout.write(self.style.WARNING(f"Updated existing user '{user.username}' password"))

        profile, _ = UserProfile.objects.get_or_create(user=user)
        # Apply plan on profile
        profile.plan_type = plan
        profile.plan_name = plan.title()
        profile.is_premium = plan not in ['free', 'basic']
        profile.billing_cycle = billing_cycle
        # Sensible API limits for partner
        profile.api_calls_limit = 100000 if plan in ['gold','enterprise'] else 1000
        profile.save()
        self.stdout.write(self.style.SUCCESS(f"Applied plan '{plan}' for {email}"))

        # Ensure referral code exists and normalized to 50% off first payment
        disc, created = DiscountService.get_or_create_referral_code(ref_code)
        if created:
            self.stdout.write(self.style.SUCCESS(f"Created referral code {ref_code}"))
        else:
            self.stdout.write(self.style.SUCCESS(f"Referral code {ref_code} is active"))

        # Final output
        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("✓ Partner user setup complete"))
        self.stdout.write(f"  Email: {email}")
        self.stdout.write(f"  Username: {user.username}")
        self.stdout.write(f"  Plan: {profile.plan_name}")
        self.stdout.write(f"  Referral code: {ref_code}")
