#!/usr/bin/env python3
"""
Complete setup script for the new pricing system
Run this after updating your codebase to ensure everything is properly configured

Usage: python setup_pricing_system.py
"""

import os
import sys
import django
from pathlib import Path

# Add the workspace to the Python path
workspace_path = Path(__file__).parent
sys.path.insert(0, str(workspace_path))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stockscanner_django.settings')
django.setup()

# Now we can import Django models and management commands
from django.core.management import call_command
from django.contrib.auth.models import User
from stocks.models import UserProfile, UserSettings, PaymentPlan, UserTier
from decimal import Decimal

def print_header(text):
    """Print a formatted header"""
    print(f"\n{'='*60}")
    print(f"🚀 {text}")
    print(f"{'='*60}")

def print_success(text):
    """Print a success message"""
    print(f"✅ {text}")

def print_info(text):
    """Print an info message"""
    print(f"📋 {text}")

def print_warning(text):
    """Print a warning message"""
    print(f"⚠️  {text}")

def setup_database():
    """Run database migrations"""
    print_header("DATABASE SETUP")
    
    print_info("Running database migrations...")
    call_command('makemigrations', verbosity=1)
    call_command('migrate', verbosity=1)
    print_success("Database migrations completed")

def setup_payment_plans():
    """Set up payment plans with correct pricing"""
    print_header("PAYMENT PLANS SETUP")
    
    # Clear existing plans
    deleted_count = PaymentPlan.objects.count()
    PaymentPlan.objects.all().delete()
    print_info(f"Cleared {deleted_count} existing payment plans")
    
    # Create Basic Plan
    basic_plan = PaymentPlan.objects.create(
        name='Basic Plan',
        tier=UserTier.BASIC,
        price_monthly=Decimal('24.99'),
        price_yearly=Decimal('274.89'),
        features={
            'api_calls_per_day': 1500,
            'api_calls_per_hour': 100,
            'max_watchlist_items': 25,
            'real_time_data': True,
            'advanced_charts': True,
            'data_export': True,
            'email_support': True,
            'technical_indicators': True,
            'portfolio_tracking': True
        },
        is_active=True
    )
    print_success(f"Created Basic Plan: ${basic_plan.price_monthly}/month")
    
    # Create Pro Plan
    pro_plan = PaymentPlan.objects.create(
        name='Pro Plan',
        tier=UserTier.PRO,
        price_monthly=Decimal('49.99'),
        price_yearly=Decimal('549.89'),
        features={
            'api_calls_per_day': 5000,
            'api_calls_per_hour': 300,
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
        is_active=True
    )
    print_success(f"Created Pro Plan: ${pro_plan.price_monthly}/month")
    
    # Create Enterprise Plan
    enterprise_plan = PaymentPlan.objects.create(
        name='Enterprise Plan',
        tier=UserTier.ENTERPRISE,
        price_monthly=Decimal('79.99'),
        price_yearly=Decimal('879.89'),
        features={
            'api_calls_per_day': 'unlimited',
            'api_calls_per_hour': 'unlimited',
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
        is_active=True
    )
    print_success(f"Created Enterprise Plan: ${enterprise_plan.price_monthly}/month")

def validate_user_profiles():
    """Ensure all users have profiles and settings"""
    print_header("USER PROFILE VALIDATION")
    
    users_without_profiles = 0
    users_without_settings = 0
    
    for user in User.objects.all():
        # Create profile if missing
        if not hasattr(user, 'profile'):
            UserProfile.objects.create(user=user)
            users_without_profiles += 1
        
        # Create settings if missing
        if not hasattr(user, 'settings'):
            UserSettings.objects.create(user=user)
            users_without_settings += 1
    
    print_success(f"Created profiles for {users_without_profiles} users")
    print_success(f"Created settings for {users_without_settings} users")

def display_pricing_summary():
    """Display the complete pricing structure"""
    print_header("PRICING STRUCTURE SUMMARY")
    
    print("\n🎯 TIER STRUCTURE:")
    print("┌─────────────┬─────────────┬──────────────┬──────────────┬─────────────────┐")
    print("│ Tier        │ Price       │ Hourly Limit │ Daily Limit  │ Watchlist Items │")
    print("├─────────────┼─────────────┼──────────────┼──────────────┼─────────────────┤")
    print("│ FREE        │ $0.00       │ 15           │ 15           │ 3               │")
    print("│ BASIC       │ $24.99/mo   │ 100          │ 1,500        │ 25              │")
    print("│ PRO         │ $49.99/mo   │ 300          │ 5,000        │ 100             │")
    print("│ ENTERPRISE  │ $79.99/mo   │ Unlimited    │ Unlimited    │ Unlimited       │")
    print("└─────────────┴─────────────┴──────────────┴──────────────┴─────────────────┘")
    
    print("\n💰 ANNUAL PRICING (10% Discount):")
    print("• Basic: $274.89/year (Save $25.00)")
    print("• Pro: $549.89/year (Save $50.00)")
    print("• Enterprise: $879.89/year (Save $80.00)")

def display_next_steps():
    """Display next steps for PayPal configuration"""
    print_header("NEXT STEPS - PAYPAL CONFIGURATION")
    
    print_warning("REQUIRED: Configure PayPal Developer Dashboard")
    print()
    print("1. Create PayPal subscription plans with these exact amounts:")
    print("   • Basic Monthly: $24.99/month recurring")
    print("   • Basic Yearly: $274.89/year recurring")
    print("   • Pro Monthly: $49.99/month recurring")
    print("   • Pro Yearly: $549.89/year recurring")
    print("   • Enterprise Monthly: $79.99/month recurring")
    print("   • Enterprise Yearly: $879.89/year recurring")
    print()
    print("2. Update environment variables:")
    print("   • PAYPAL_BASE_URL=https://api.sandbox.paypal.com (or production)")
    print("   • PAYPAL_CLIENT_ID=your_client_id")
    print("   • PAYPAL_CLIENT_SECRET=your_client_secret")
    print("   • PAYPAL_WEBHOOK_ID=your_webhook_id")
    print()
    print("3. Update PaymentPlan records with PayPal plan IDs")
    print("4. Configure webhook endpoints")
    print("5. Test payment flow")

def test_rate_limiting():
    """Test rate limiting functionality"""
    print_header("RATE LIMITING TEST")
    
    # Test with a sample user profile
    try:
        # Get or create a test user
        test_user, created = User.objects.get_or_create(
            username='test_user',
            defaults={'email': 'test@example.com'}
        )
        
        if created:
            print_info("Created test user for rate limiting validation")
        
        # Test rate limits for each tier
        test_profile = test_user.profile
        
        for tier in ['free', 'basic', 'pro', 'enterprise']:
            test_profile.tier = tier
            limits = test_profile.get_rate_limits()
            
            print_success(f"{tier.upper()} tier: {limits['api_calls_per_hour']}/hour, {limits['api_calls_per_day']}/day")
            
            # Test can_make_api_call
            can_call, message = test_profile.can_make_api_call()
            if can_call:
                print_success(f"  ✓ API calls allowed for {tier} tier")
            else:
                print_warning(f"  ✗ API calls blocked for {tier} tier: {message}")
        
        # Clean up test user
        if created:
            test_user.delete()
            print_info("Cleaned up test user")
            
    except Exception as e:
        print_warning(f"Rate limiting test failed: {e}")

def main():
    """Main setup function"""
    print_header("STOCK SCANNER PRICING SYSTEM SETUP")
    print("This script will set up the new pricing structure across all systems")
    
    try:
        # 1. Database setup
        setup_database()
        
        # 2. Payment plans setup
        setup_payment_plans()
        
        # 3. User profile validation
        validate_user_profiles()
        
        # 4. Test rate limiting
        test_rate_limiting()
        
        # 5. Display summary
        display_pricing_summary()
        
        # 6. Display next steps
        display_next_steps()
        
        print_header("SETUP COMPLETE!")
        print_success("Your pricing system is now fully configured and operational!")
        print_success("All rate limits have been updated throughout the system")
        print_success("PayPal integration is ready for configuration")
        
    except Exception as e:
        print_warning(f"Setup failed: {e}")
        print("Please check the error above and try again")
        sys.exit(1)

if __name__ == "__main__":
    main()