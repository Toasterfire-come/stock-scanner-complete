"""
Django management command to test rate limiting functionality
"""
from django.core.management.base import BaseCommand
from django.test import Client
from django.contrib.auth.models import User, Group
from django.core.cache import cache
import json


class Command(BaseCommand):
    help = 'Test rate limiting functionality for different user types'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear-cache',
            action='store_true',
            help='Clear rate limit cache before testing',
        )

    def handle(self, *args, **options):
        if options['clear_cache']:
            cache.clear()
            self.stdout.write(self.style.SUCCESS('Cache cleared'))

        # Create test client
        client = Client()

        # Test free endpoints (no rate limiting)
        self.stdout.write('\n' + '='*60)
        self.stdout.write('Testing FREE endpoints (no rate limiting)')
        self.stdout.write('='*60)

        free_endpoints = [
            '/health/',
            '/api/health/',
            '/health/detailed/',
            '/health/ready/',
            '/health/live/',
            '/docs/',
            '/',
        ]

        for endpoint in free_endpoints:
            self.stdout.write(f'\nTesting {endpoint}:')
            success_count = 0
            
            for i in range(20):
                response = client.get(endpoint)
                if response.status_code == 200:
                    success_count += 1
                elif response.status_code == 429:
                    self.stdout.write(
                        self.style.ERROR(f'  ❌ Rate limited at request {i+1}')
                    )
                    break
            
            if success_count == 20:
                self.stdout.write(
                    self.style.SUCCESS(f'  ✅ No rate limiting ({success_count}/20 successful)')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'  ⚠️  Only {success_count}/20 successful')
                )

        # Test rate-limited endpoints
        self.stdout.write('\n' + '='*60)
        self.stdout.write('Testing RATE LIMITED endpoints')
        self.stdout.write('='*60)

        limited_endpoints = [
            '/api/stocks/',
            '/api/search/?search=AAPL',
        ]

        for endpoint in limited_endpoints:
            self.stdout.write(f'\nTesting {endpoint}:')
            success_count = 0
            rate_limited = False
            
            # Clear cache for this test
            cache.clear()
            
            for i in range(120):  # Try to exceed the 100 request limit
                response = client.get(endpoint)
                if response.status_code == 200:
                    success_count += 1
                elif response.status_code == 429:
                    rate_limited = True
                    self.stdout.write(
                        self.style.SUCCESS(f'  ✅ Rate limited after {success_count} requests')
                    )
                    
                    # Check response content
                    try:
                        data = json.loads(response.content)
                        self.stdout.write(f"  Message: {data.get('message', 'N/A')}")
                        self.stdout.write(f"  Retry after: {data.get('retry_after', 'N/A')} seconds")
                    except:
                        pass
                    break
            
            if not rate_limited:
                self.stdout.write(
                    self.style.ERROR(f'  ❌ Not rate limited after {success_count} requests!')
                )

        # Test authenticated user (higher limits)
        self.stdout.write('\n' + '='*60)
        self.stdout.write('Testing AUTHENTICATED user (higher limits)')
        self.stdout.write('='*60)

        # Create test user
        test_user, created = User.objects.get_or_create(
            username='test_rate_limit_user',
            defaults={'email': 'test@example.com'}
        )
        if created:
            test_user.set_password('testpass123')
            test_user.save()

        # Login
        client.force_login(test_user)
        
        # Clear cache for authenticated test
        cache.clear()

        endpoint = '/api/stocks/'
        self.stdout.write(f'\nTesting {endpoint} as authenticated user:')
        success_count = 0
        
        for i in range(200):  # Test up to 200 requests
            response = client.get(endpoint)
            if response.status_code == 200:
                success_count += 1
            elif response.status_code == 429:
                self.stdout.write(
                    self.style.SUCCESS(f'  ✅ Rate limited after {success_count} requests (expected ~1000/hour)')
                )
                break
            
            if i == 150:
                self.stdout.write(f'  Progress: {success_count} successful requests so far...')
        
        if success_count >= 200:
            self.stdout.write(
                self.style.SUCCESS(f'  ✅ Higher limit for authenticated users ({success_count} requests without limiting)')
            )

        # Test premium user (no limits)
        self.stdout.write('\n' + '='*60)
        self.stdout.write('Testing PREMIUM user (no limits)')
        self.stdout.write('='*60)

        # Create premium group
        premium_group, _ = Group.objects.get_or_create(name='premium')
        test_user.groups.add(premium_group)
        
        # Clear cache for premium test
        cache.clear()

        self.stdout.write(f'\nTesting {endpoint} as premium user:')
        success_count = 0
        
        for i in range(200):
            response = client.get(endpoint)
            if response.status_code == 200:
                success_count += 1
            elif response.status_code == 429:
                self.stdout.write(
                    self.style.ERROR(f'  ❌ Premium user was rate limited after {success_count} requests!')
                )
                break
            
            if i == 150:
                self.stdout.write(f'  Progress: {success_count} successful requests so far...')
        
        if success_count >= 200:
            self.stdout.write(
                self.style.SUCCESS(f'  ✅ No rate limiting for premium users ({success_count} requests)')
            )

        # Cleanup
        test_user.delete()
        
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('Rate limiting tests completed'))
        self.stdout.write('='*60)