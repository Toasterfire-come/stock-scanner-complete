"""
Management command to set up membership system
Creates free memberships for existing users
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from stocks.models import Membership


class Command(BaseCommand):
help = 'Set up membership system - create free memberships for existing users'

def handle(self, *args, **options):
self.stdout.write(self.style.SUCCESS('Setting up membership system...'))

# Get all users without memberships
users_without_memberships = User.objects.filter(membership__isnull=True)

created_count = 0
for user in users_without_memberships:
membership, created = Membership.objects.get_or_create(
user=user,
defaults={
'tier': 'free',
'monthly_price': 0.00,
'is_active': True,
'subscription_status': 'active'
}
)
if created:
created_count += 1
self.stdout.write(f'Created free membership for {user.username}')

total_memberships = Membership.objects.count()
self.stdout.write(
self.style.SUCCESS(
f'Setup complete! Created {created_count} new memberships. '
f'Total memberships: {total_memberships}'
)
)

# Show membership distribution
self.stdout.write('\nMembership distribution:')
for tier_code, tier_name in Membership.TIER_CHOICES:
count = Membership.objects.filter(tier=tier_code, is_active=True).count()
self.stdout.write(f' {tier_name}: {count} members')
