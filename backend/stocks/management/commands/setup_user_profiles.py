from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from stocks.models import UserProfile


class Command(BaseCommand):
    help = 'Create UserProfile instances for existing users'
    
    def handle(self, *args, **options):
        users_without_profile = User.objects.filter(profile__isnull=True)
        created_count = 0
        
        for user in users_without_profile:
            profile, created = UserProfile.objects.get_or_create(
                user=user,
                defaults={
                    'plan_type': 'free',
                    'plan_name': 'Free Plan',
                    'api_calls_limit': 30,
                    'screeners_limit': 1,
                    'alerts_limit': 0,
                    'watchlists_limit': 1,
                    'portfolios_limit': 1,
                }
            )
            if created:
                created_count += 1
                self.stdout.write(f'Created profile for user: {user.username}')
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} user profiles')
        )