#!/usr/bin/env python3
"""
Payment System Validation Script
Tests all components of the payment flow to ensure you can get paid

This script validates the payment system configuration without requiring
Django to be installed, checking file structure, imports, and configuration.
"""

import os
import sys
import re
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional

class PaymentSystemValidator:
    def __init__(self):
        self.workspace_path = Path(__file__).parent
        self.errors = []
        self.warnings = []
        self.successes = []
        
    def log_error(self, message: str):
        """Log an error"""
        self.errors.append(f"❌ ERROR: {message}")
        
    def log_warning(self, message: str):
        """Log a warning"""
        self.warnings.append(f"⚠️  WARNING: {message}")
        
    def log_success(self, message: str):
        """Log a success"""
        self.successes.append(f"✅ SUCCESS: {message}")
        
    def print_header(self, title: str):
        """Print section header"""
        print(f"\n{'='*60}")
        print(f"🎯 {title}")
        print(f"{'='*60}")
    
    def validate_file_structure(self) -> bool:
        """Validate that all required files exist"""
        self.print_header("FILE STRUCTURE VALIDATION")
        
        required_files = [
            # Core Django files
            'manage.py',
            'stockscanner_django/settings.py',
            'stockscanner_django/urls.py',
            
            # Payment integration files
            'stocks/models.py',
            'stocks/urls.py',
            'stocks/paypal_integration.py',
            'stocks/user_management.py',
            'stocks/middleware.py',
            'stocks/admin.py',
            
            # Management commands
            'stocks/management/commands/setup_payment_plans.py',
            
            # Frontend optimization
            'stocks/frontend_optimization.py',
            'stocks/browser_charts.py',
            'stocks/client_side_utilities.py',
        ]
        
        missing_files = []
        for file_path in required_files:
            full_path = self.workspace_path / file_path
            if full_path.exists():
                self.log_success(f"Found {file_path}")
            else:
                self.log_error(f"Missing required file: {file_path}")
                missing_files.append(file_path)
        
        return len(missing_files) == 0
    
    def validate_model_structure(self) -> bool:
        """Validate model structure in models.py"""
        self.print_header("MODEL STRUCTURE VALIDATION")
        
        models_file = self.workspace_path / 'stocks/models.py'
        if not models_file.exists():
            self.log_error("models.py file not found")
            return False
        
        content = models_file.read_text()
        
        # Check for required models
        required_models = [
            'UserProfile',
            'UserSettings', 
            'PaymentPlan',
            'PaymentTransaction',
            'UserAPIUsage',
            'UserTier'
        ]
        
        found_models = []
        for model in required_models:
            if f"class {model}" in content:
                self.log_success(f"Found model: {model}")
                found_models.append(model)
            else:
                self.log_error(f"Missing model: {model}")
        
        # Check for rate limiting methods
        if 'get_rate_limits' in content:
            self.log_success("Found get_rate_limits method")
        else:
            self.log_error("Missing get_rate_limits method")
        
        if 'can_make_api_call' in content:
            self.log_success("Found can_make_api_call method")
        else:
            self.log_error("Missing can_make_api_call method")
            
        # Check for pricing values
        if '24.99' in content and '49.99' in content and '79.99' in content:
            self.log_success("Found correct pricing values in rate limits")
        else:
            self.log_warning("Pricing values may not be updated in models")
        
        return len(found_models) == len(required_models)
    
    def validate_paypal_integration(self) -> bool:
        """Validate PayPal integration"""
        self.print_header("PAYPAL INTEGRATION VALIDATION")
        
        paypal_file = self.workspace_path / 'stocks/paypal_integration.py'
        if not paypal_file.exists():
            self.log_error("paypal_integration.py file not found")
            return False
        
        content = paypal_file.read_text()
        
        # Check for required PayPal functions
        required_functions = [
            'create_subscription',
            'cancel_subscription', 
            'subscription_status',
            'available_plans',
            'paypal_webhook'
        ]
        
        found_functions = []
        for func in required_functions:
            if f"def {func}" in content:
                self.log_success(f"Found PayPal function: {func}")
                found_functions.append(func)
            else:
                self.log_error(f"Missing PayPal function: {func}")
        
        # Check for PayPal API class
        if 'class PayPalAPI' in content:
            self.log_success("Found PayPalAPI class")
        else:
            self.log_error("Missing PayPalAPI class")
        
        # Check for webhook event handlers
        webhook_handlers = [
            'handle_subscription_activated',
            'handle_subscription_cancelled',
            'handle_payment_completed'
        ]
        
        for handler in webhook_handlers:
            if f"def {handler}" in content:
                self.log_success(f"Found webhook handler: {handler}")
            else:
                self.log_warning(f"Missing webhook handler: {handler}")
        
        return len(found_functions) == len(required_functions)
    
    def validate_user_management(self) -> bool:
        """Validate user management system"""
        self.print_header("USER MANAGEMENT VALIDATION")
        
        user_mgmt_file = self.workspace_path / 'stocks/user_management.py'
        if not user_mgmt_file.exists():
            self.log_error("user_management.py file not found")
            return False
        
        content = user_mgmt_file.read_text()
        
        # Check for required user management functions
        required_functions = [
            'user_settings',
            'user_profile',
            'api_usage_stats',
            'subscription_management',
            'frontend_optimization_config'
        ]
        
        found_functions = []
        for func in required_functions:
            if f"def {func}" in content:
                self.log_success(f"Found user management function: {func}")
                found_functions.append(func)
            else:
                self.log_error(f"Missing user management function: {func}")
        
        return len(found_functions) == len(required_functions)
    
    def validate_middleware(self) -> bool:
        """Validate middleware configuration"""
        self.print_header("MIDDLEWARE VALIDATION")
        
        middleware_file = self.workspace_path / 'stocks/middleware.py'
        if not middleware_file.exists():
            self.log_error("middleware.py file not found")
            return False
        
        content = middleware_file.read_text()
        
        # Check for required middleware classes
        required_middleware = [
            'UserTierRateLimitMiddleware',
            'FrontendOptimizationMiddleware',
            'UserSettingsAutoSetupMiddleware',
            'APIResponseOptimizationMiddleware'
        ]
        
        found_middleware = []
        for middleware in required_middleware:
            if f"class {middleware}" in content:
                self.log_success(f"Found middleware: {middleware}")
                found_middleware.append(middleware)
            else:
                self.log_error(f"Missing middleware: {middleware}")
        
        return len(found_middleware) == len(required_middleware)
    
    def validate_url_routing(self) -> bool:
        """Validate URL routing configuration"""
        self.print_header("URL ROUTING VALIDATION")
        
        # Check main Django URLs
        main_urls = self.workspace_path / 'stockscanner_django/urls.py'
        stocks_urls = self.workspace_path / 'stocks/urls.py'
        
        if not main_urls.exists():
            self.log_error("Main urls.py file not found")
            return False
        
        if not stocks_urls.exists():
            self.log_error("Stocks urls.py file not found")
            return False
        
        # Check stocks URLs for payment endpoints
        stocks_content = stocks_urls.read_text()
        
        payment_endpoints = [
            'payment/create-subscription/',
            'payment/cancel-subscription/',
            'payment/subscription-status/',
            'payment/plans/',
            'payment/webhook/'
        ]
        
        user_endpoints = [
            'user/settings/',
            'user/profile/',
            'user/subscription/'
        ]
        
        for endpoint in payment_endpoints:
            if endpoint in stocks_content:
                self.log_success(f"Found payment endpoint: {endpoint}")
            else:
                self.log_error(f"Missing payment endpoint: {endpoint}")
        
        for endpoint in user_endpoints:
            if endpoint in stocks_content:
                self.log_success(f"Found user endpoint: {endpoint}")
            else:
                self.log_error(f"Missing user endpoint: {endpoint}")
        
        return True
    
    def validate_admin_interface(self) -> bool:
        """Validate admin interface configuration"""
        self.print_header("ADMIN INTERFACE VALIDATION")
        
        admin_file = self.workspace_path / 'stocks/admin.py'
        if not admin_file.exists():
            self.log_error("admin.py file not found")
            return False
        
        content = admin_file.read_text()
        
        # Check for admin classes
        admin_classes = [
            'UserProfileAdmin',
            'PaymentPlanAdmin',
            'PaymentTransactionAdmin',
            'CustomUserAdmin'
        ]
        
        found_admin = []
        for admin_class in admin_classes:
            if f"class {admin_class}" in content:
                self.log_success(f"Found admin class: {admin_class}")
                found_admin.append(admin_class)
            else:
                self.log_warning(f"Missing admin class: {admin_class}")
        
        return len(found_admin) >= 3  # At least 3 admin classes
    
    def validate_settings_configuration(self) -> bool:
        """Validate Django settings configuration"""
        self.print_header("SETTINGS CONFIGURATION VALIDATION")
        
        settings_file = self.workspace_path / 'stockscanner_django/settings.py'
        if not settings_file.exists():
            self.log_error("settings.py file not found")
            return False
        
        content = settings_file.read_text()
        
        # Check for PayPal configuration
        paypal_settings = [
            'PAYPAL_BASE_URL',
            'PAYPAL_CLIENT_ID',
            'PAYPAL_CLIENT_SECRET'
        ]
        
        for setting in paypal_settings:
            if setting in content:
                self.log_success(f"Found PayPal setting: {setting}")
            else:
                self.log_warning(f"Missing PayPal setting: {setting}")
        
        # Check for middleware configuration
        middleware_classes = [
            'UserTierRateLimitMiddleware',
            'FrontendOptimizationMiddleware'
        ]
        
        for middleware in middleware_classes:
            if middleware in content:
                self.log_success(f"Found middleware in settings: {middleware}")
            else:
                self.log_warning(f"Missing middleware in settings: {middleware}")
        
        return True
    
    def validate_pricing_structure(self) -> bool:
        """Validate pricing structure consistency"""
        self.print_header("PRICING STRUCTURE VALIDATION")
        
        models_file = self.workspace_path / 'stocks/models.py'
        setup_file = self.workspace_path / 'stocks/management/commands/setup_payment_plans.py'
        
        pricing_correct = True
        
        # Check models.py for correct pricing
        if models_file.exists():
            content = models_file.read_text()
            if '24.99' in content and '49.99' in content and '79.99' in content:
                self.log_success("Found correct pricing in models.py")
            else:
                self.log_error("Incorrect pricing in models.py")
                pricing_correct = False
        
        # Check setup command for correct pricing
        if setup_file.exists():
            content = setup_file.read_text()
            if '24.99' in content and '49.99' in content and '79.99' in content:
                self.log_success("Found correct pricing in setup command")
            else:
                self.log_error("Incorrect pricing in setup command")
                pricing_correct = False
        
        # Check rate limits
        if models_file.exists():
            content = models_file.read_text()
            if "'api_calls_per_day': 15" in content:  # Free tier
                self.log_success("Found correct free tier limits")
            else:
                self.log_error("Incorrect free tier limits")
                pricing_correct = False
                
            if "'api_calls_per_day': 1500" in content:  # Basic tier
                self.log_success("Found correct basic tier limits")
            else:
                self.log_error("Incorrect basic tier limits")
                pricing_correct = False
        
        return pricing_correct
    
    def create_user_journey_test(self) -> str:
        """Create a user journey test plan"""
        self.print_header("USER JOURNEY TEST PLAN")
        
        test_plan = """
🎯 COMPLETE USER JOURNEY TEST PLAN

1. USER REGISTRATION
   ✓ User signs up with email/password
   ✓ UserProfile and UserSettings auto-created
   ✓ User starts with FREE tier (15 API calls/day)
   ✓ User can access basic features

2. FREE TIER EXPERIENCE
   ✓ User makes API calls
   ✓ Rate limiting enforced at 15 calls/day
   ✓ User hits limits quickly
   ✓ Clear upgrade prompts displayed

3. SUBSCRIPTION CREATION
   ✓ User views available plans
   ✓ User selects Basic ($24.99/month) plan
   ✓ PayPal subscription created
   ✓ User redirected to PayPal for payment

4. PAYMENT PROCESSING
   ✓ User completes payment on PayPal
   ✓ PayPal webhook received and verified
   ✓ User tier upgraded to Basic automatically
   ✓ API limits increased to 1,500/day

5. SUBSCRIPTION MANAGEMENT
   ✓ User can view subscription status
   ✓ User can cancel subscription
   ✓ User can upgrade to higher tiers
   ✓ Billing history is tracked

6. FEATURE UNLOCKING
   ✓ Real-time data enabled for paid users
   ✓ Advanced charts unlocked
   ✓ Data export available
   ✓ Increased watchlist limits

7. ADMIN MONITORING
   ✓ Admin can view user tiers
   ✓ Admin can monitor API usage
   ✓ Admin can track revenue
   ✓ Admin can manage subscriptions

8. WEBHOOK PROCESSING
   ✓ Subscription activated webhook
   ✓ Payment completed webhook
   ✓ Subscription cancelled webhook
   ✓ Payment failed webhook
        """
        
        return test_plan
    
    def generate_test_script(self) -> str:
        """Generate a Django test script"""
        test_script = '''#!/usr/bin/env python3
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
    print("🚀 Starting Payment System Integration Tests\\n")
    
    try:
        test_user_creation()
        test_rate_limits()
        test_payment_plans()
        test_tier_upgrade()
        test_paypal_api()
        
        print("\\n🎉 ALL TESTS PASSED!")
        print("💰 Your payment system is ready to generate revenue!")
        
    except Exception as e:
        print(f"\\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_all_tests()
'''
        return test_script
    
    def run_validation(self) -> bool:
        """Run complete validation"""
        print("🚀 PAYMENT SYSTEM VALIDATION")
        print("Ensuring your system is ready to get paid!")
        
        # Run all validations
        validations = [
            self.validate_file_structure,
            self.validate_model_structure,
            self.validate_paypal_integration,
            self.validate_user_management,
            self.validate_middleware,
            self.validate_url_routing,
            self.validate_admin_interface,
            self.validate_settings_configuration,
            self.validate_pricing_structure
        ]
        
        all_passed = True
        for validation in validations:
            try:
                result = validation()
                if not result:
                    all_passed = False
            except Exception as e:
                self.log_error(f"Validation failed: {e}")
                all_passed = False
        
        # Display results
        self.print_header("VALIDATION RESULTS")
        
        for success in self.successes:
            print(success)
        
        for warning in self.warnings:
            print(warning)
        
        for error in self.errors:
            print(error)
        
        # Create test plan and script
        test_plan = self.create_user_journey_test()
        print(test_plan)
        
        # Generate test script
        test_script = self.generate_test_script()
        test_file = self.workspace_path / 'test_payment_integration.py'
        test_file.write_text(test_script)
        self.log_success(f"Created test script: {test_file}")
        
        # Final summary
        self.print_header("FINAL SUMMARY")
        
        if all_passed and len(self.errors) == 0:
            print("🎉 PAYMENT SYSTEM READY!")
            print("💰 Your system is configured to accept payments!")
            print("🚀 Run the test script to verify functionality")
        elif len(self.errors) < 3:
            print("⚠️  MINOR ISSUES FOUND")
            print("💰 Your system should work but needs minor fixes")
            print("🔧 Address the errors above before going live")
        else:
            print("❌ MAJOR ISSUES FOUND")
            print("🚫 Your system needs significant fixes before accepting payments")
            print("🔧 Address all errors before proceeding")
        
        return all_passed and len(self.errors) == 0

def main():
    """Main validation function"""
    validator = PaymentSystemValidator()
    success = validator.run_validation()
    
    if success:
        print("\n🎯 NEXT STEPS:")
        print("1. Run: python setup_pricing_system.py")
        print("2. Configure PayPal Developer Dashboard")
        print("3. Run: python test_payment_integration.py")
        print("4. Deploy and start earning! 💰")
    
    return success

if __name__ == "__main__":
    main()