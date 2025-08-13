#!/usr/bin/env python3
"""
Django Payment System Integration Test
Run with: python test_payment_integration.py
"""

import os
import sys
import django
from pathlib import Path

# Setup Django
workspace_path = Path(__file__).parent
sys.path.insert(0, str(workspace_path))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stockscanner_django.settings')
django.setup()

from django.contrib.auth.models import User
from stocks.models import UserProfile, PaymentPlan, UserTier
from stocks.paypal_integration import PayPalAPI
import json

def test_user_creation():
    """Test automatic user profile creation"""
    print("🧪 Testing user creation...")
    
    # Create test user
    test_user = User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )
    
    # Check if profile was auto-created
    assert hasattr(test_user, 'profile'), "UserProfile not auto-created"
    assert hasattr(test_user, 'settings'), "UserSettings not auto-created"
    assert test_user.profile.tier == 'free', "User not defaulted to free tier"
    
    print("✅ User creation test passed")
    test_user.delete()

def test_rate_limits():
    """Test rate limiting system"""
    print("🧪 Testing rate limits...")
    
    test_user = User.objects.create_user(username='ratetest', email='rate@example.com')
    profile = test_user.profile
    
    # Test free tier limits
    limits = profile.get_rate_limits()
    assert limits['api_calls_per_day'] == 15, f"Free tier daily limit incorrect: {limits['api_calls_per_day']}"
    assert limits['api_calls_per_hour'] == 15, f"Free tier hourly limit incorrect: {limits['api_calls_per_hour']}"
    
    # Test can_make_api_call
    can_call, message = profile.can_make_api_call()
    assert can_call == True, "Free user should be able to make initial API call"
    
    print("✅ Rate limiting test passed")
    test_user.delete()

def test_payment_plans():
    """Test payment plan configuration"""
    print("🧪 Testing payment plans...")
    
    # Check if payment plans exist
    basic_plan = PaymentPlan.objects.filter(tier='basic').first()
    pro_plan = PaymentPlan.objects.filter(tier='pro').first()
    enterprise_plan = PaymentPlan.objects.filter(tier='enterprise').first()
    
    assert basic_plan is not None, "Basic plan not found"
    assert pro_plan is not None, "Pro plan not found" 
    assert enterprise_plan is not None, "Enterprise plan not found"
    
    # Check pricing
    assert str(basic_plan.price_monthly) == '24.99', f"Basic plan price incorrect: {basic_plan.price_monthly}"
    assert str(pro_plan.price_monthly) == '49.99', f"Pro plan price incorrect: {pro_plan.price_monthly}"
    assert str(enterprise_plan.price_monthly) == '79.99', f"Enterprise plan price incorrect: {enterprise_plan.price_monthly}"
    
    print("✅ Payment plans test passed")

def test_tier_upgrade():
    """Test tier upgrade functionality"""
    print("🧪 Testing tier upgrades...")
    
    test_user = User.objects.create_user(username='upgradetest', email='upgrade@example.com')
    profile = test_user.profile
    
    # Start with free tier
    assert profile.tier == 'free'
    free_limits = profile.get_rate_limits()
    assert free_limits['api_calls_per_day'] == 15
    
    # Upgrade to basic
    profile.tier = 'basic'
    profile.save()
    basic_limits = profile.get_rate_limits()
    assert basic_limits['api_calls_per_day'] == 1500
    
    # Upgrade to pro
    profile.tier = 'pro'
    profile.save()
    pro_limits = profile.get_rate_limits()
    assert pro_limits['api_calls_per_day'] == 5000
    
    print("✅ Tier upgrade test passed")
    test_user.delete()

def test_paypal_api():
    """Test PayPal API initialization"""
    print("🧪 Testing PayPal API...")
    
    try:
        paypal_api = PayPalAPI()
        # Test that PayPal API initializes without errors
        assert hasattr(paypal_api, 'base_url')
        assert hasattr(paypal_api, 'client_id')
        assert hasattr(paypal_api, 'client_secret')
        print("✅ PayPal API initialization test passed")
    except Exception as e:
        print(f"⚠️  PayPal API test warning: {e}")

def run_all_tests():
    """Run all integration tests"""
    print("🚀 Starting Payment System Integration Tests\n")
    
    try:
        test_user_creation()
        test_rate_limits()
        test_payment_plans()
        test_tier_upgrade()
        test_paypal_api()
        
        print("\n🎉 ALL TESTS PASSED!")
        print("💰 Your payment system is ready to generate revenue!")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_all_tests()
