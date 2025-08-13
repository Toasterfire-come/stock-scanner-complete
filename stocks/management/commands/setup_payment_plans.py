"""
Django management command to set up payment plans with correct pricing
Usage: python manage.py setup_payment_plans
"""

from django.core.management.base import BaseCommand
from stocks.models import PaymentPlan, UserTier
from decimal import Decimal

class Command(BaseCommand):
    help = 'Set up payment plans with correct pricing and features'
    
    def handle(self, *args, **options):
        """Set up all payment plans"""
        
        self.stdout.write(self.style.SUCCESS('Setting up payment plans...'))
        
        # Delete existing plans
        PaymentPlan.objects.all().delete()
        self.stdout.write('Cleared existing payment plans')
        
        # Basic Plan - $24.99/month, 1500 API calls/day
        basic_plan, created = PaymentPlan.objects.get_or_create(
            tier=UserTier.BASIC,
            defaults={
                'name': 'Basic Plan',
                'price_monthly': Decimal('24.99'),
                'price_yearly': Decimal('274.89'),  # 10% annual discount
                'features': {
                    'api_calls_per_month': 1500,
                    'max_watchlist_items': 25,
                    'real_time_data': True,
                    'advanced_charts': True,
                    'data_export': True,
                    'email_support': True,
                    'technical_indicators': True,
                    'portfolio_tracking': True
                },
                'is_active': True
            }
        )
        if created:
            self.stdout.write(f'Created Basic Plan: ${basic_plan.price_monthly}/month')
        
        # Pro Plan - $49.99/month, 5000 API calls/day
        pro_plan, created = PaymentPlan.objects.get_or_create(
            tier=UserTier.PRO,
            defaults={
                'name': 'Pro Plan',
                'price_monthly': Decimal('49.99'),
                'price_yearly': Decimal('549.89'),  # 10% annual discount
                'features': {
                    'api_calls_per_month': 5000,
                    'max_watchlist_items': 100,
                    'real_time_data': True,
                    'advanced_charts': True,
                    'data_export': True,
                    'email_support': True,
                    'priority_support': True,
                    'technical_indicators': True,
                    'portfolio_tracking': True,
                    'advanced_analytics': True,
                    'custom_alerts': True,
                    'api_access': True
                },
                'is_active': True
            }
        )
        if created:
            self.stdout.write(f'Created Pro Plan: ${pro_plan.price_monthly}/month')
        
        # Enterprise Plan - $79.99/month, unlimited API calls
        enterprise_plan, created = PaymentPlan.objects.get_or_create(
            tier=UserTier.ENTERPRISE,
            defaults={
                'name': 'Enterprise Plan',
                'price_monthly': Decimal('79.99'),
                'price_yearly': Decimal('879.89'),  # 10% annual discount
                'features': {
                    'api_calls_per_month': 'unlimited',
                    'max_watchlist_items': 'unlimited',
                    'real_time_data': True,
                    'advanced_charts': True,
                    'data_export': True,
                    'email_support': True,
                    'priority_support': True,
                    'phone_support': True,
                    'technical_indicators': True,
                    'portfolio_tracking': True,
                    'advanced_analytics': True,
                    'custom_alerts': True,
                    'api_access': True,
                    'white_label': True,
                    'custom_integrations': True,
                    'dedicated_support': True,
                    'sla_guarantee': True
                },
                'is_active': True
            }
        )
        if created:
            self.stdout.write(f'Created Enterprise Plan: ${enterprise_plan.price_monthly}/month')
        
        # Display plan summary
        self.stdout.write(self.style.SUCCESS('\n=== PAYMENT PLANS SUMMARY ==='))
        
        plans = PaymentPlan.objects.filter(is_active=True).order_by('price_monthly')
        
        for plan in plans:
            annual_savings = (plan.price_monthly * 12) - plan.price_yearly
            self.stdout.write(
                f"\n{plan.name} ({plan.tier.upper()})\n"
                f"  Monthly: ${plan.price_monthly}\n"
                f"  Yearly: ${plan.price_yearly} (Save ${annual_savings:.2f})\n"
                f"  API Calls: {plan.features.get('api_calls_per_month', 'N/A')}/month\n"
                f"  Watchlist Items: {plan.features.get('max_watchlist_items', 'N/A')}\n"
                f"  Real-time Data: {plan.features.get('real_time_data', False)}"
            )
        
        # Display FREE tier info
        self.stdout.write(
            f"\nFREE TIER\n"
            f"  Monthly: $0.00\n"
            f"  API Calls: 15/month\n"
            f"  Watchlist Items: 3\n"
            f"  Real-time Data: False"
        )
        
        self.stdout.write(self.style.SUCCESS('\n✅ Payment plans setup complete!'))
        
        # Show PayPal setup reminder
        self.stdout.write(
            self.style.WARNING('\n⚠️  NEXT STEPS:')
        )
        self.stdout.write(
            '1. Create corresponding plans in PayPal Developer Dashboard\n'
            '2. Update PaymentPlan records with PayPal plan IDs\n'
            '3. Configure PayPal webhook endpoints\n'
            '4. Update environment variables with PayPal credentials'
        )
        
        self.stdout.write(
            self.style.HTTP_INFO('\n📝 PayPal Plan Creation Guide:')
        )
        self.stdout.write(
            '   Basic Monthly: $24.99/month recurring\n'
            '   Basic Yearly: $274.89/year recurring\n'
            '   Pro Monthly: $49.99/month recurring\n'
            '   Pro Yearly: $549.89/year recurring\n'
            '   Enterprise Monthly: $79.99/month recurring\n'
            '   Enterprise Yearly: $879.89/year recurring'
        )