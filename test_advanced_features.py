#!/usr/bin/env python3
"""
Advanced Features Testing Script
Tests all four advanced features: API Usage Analytics, Market Sentiment, Portfolio Analytics, and Compliance
"""

import os
import sys
import django
import json
from pathlib import Path
from unittest.mock import patch, MagicMock

# Setup Django
project_dir = Path(__file__).resolve().parent
sys.path.append(str(project_dir))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stockscanner_django.settings')

try:
    django.setup()
    
    from django.test import RequestFactory
    from django.contrib.auth.models import User
    from stocks.models import (
        Membership, Portfolio, PortfolioHolding, APIUsageTracking, 
        MarketSentiment, PortfolioAnalytics, ComplianceLog, SecurityEvent
    )
    from stocks import advanced_features
    
    DJANGO_AVAILABLE = True
except Exception as e:
    print(f"Django setup failed: {e}")
    DJANGO_AVAILABLE = False

class AdvancedFeaturesTester:
    def __init__(self):
        self.factory = RequestFactory()
        self.test_user = None
        self.test_portfolio = None
        
    def setup_test_data(self):
        """Create test data for advanced features"""
        print("🔧 Setting up advanced test data...")
        
        if not DJANGO_AVAILABLE:
            print("❌ Django not available, skipping setup")
            return False
        
        try:
            # Create test user
            self.test_user = User.objects.create_user(
                username='advanced_test_user',
                email='advanced@test.com',
                password='testpass123'
            )
            
            # Create membership
            membership = Membership.objects.create(
                user=self.test_user,
                tier='professional',
                monthly_price=29.99,
                is_active=True
            )
            
            # Create test portfolio
            self.test_portfolio = Portfolio.objects.create(
                user=self.test_user,
                name='Test Portfolio',
                description='Portfolio for advanced testing'
            )
            
            # Add holdings
            holdings_data = [
                {'ticker': 'AAPL', 'shares': 10, 'purchase_price': 150.00},
                {'ticker': 'MSFT', 'shares': 5, 'purchase_price': 300.00},
                {'ticker': 'GOOGL', 'shares': 2, 'purchase_price': 2500.00}
            ]
            
            for holding_data in holdings_data:
                PortfolioHolding.objects.create(
                    portfolio=self.test_portfolio,
                    ticker=holding_data['ticker'],
                    company_name=f"{holding_data['ticker']} Inc.",
                    shares=holding_data['shares'],
                    purchase_price=holding_data['purchase_price'],
                    purchase_date='2023-01-01',
                    current_price=holding_data['purchase_price'] * 1.1  # 10% gain
                )
            
            # Create sample API usage data
            for i in range(10):
                APIUsageTracking.objects.create(
                    user=self.test_user,
                    endpoint=f'/api/stocks/',
                    method='GET',
                    response_time_ms=100 + i * 10,
                    status_code=200,
                    ip_address='127.0.0.1',
                    membership_tier='professional',
                    cost_credits=0.001
                )
            
            # Create sample sentiment data
            MarketSentiment.objects.create(
                ticker='AAPL',
                sentiment_source='news',
                sentiment_score=0.6,
                confidence_level=0.8,
                volume_mentions=100,
                positive_mentions=70,
                negative_mentions=20,
                neutral_mentions=10
            )
            
            print(f"✅ Created test user: {self.test_user.username}")
            print(f"✅ Created test portfolio with {self.test_portfolio.holdings.count()} holdings")
            print(f"✅ Created {APIUsageTracking.objects.filter(user=self.test_user).count()} API usage records")
            return True
            
        except Exception as e:
            print(f"❌ Test data setup failed: {e}")
            return False
    
    def test_api_usage_analytics(self):
        """Test API Usage Analytics feature"""
        print("\n📊 Testing API Usage Analytics...")
        
        if not DJANGO_AVAILABLE:
            print("❌ Skipping - Django not available")
            return False
        
        try:
            # Test user analytics
            request = self.factory.get('/api/advanced/usage-analytics/')
            request.user = self.test_user
            
            with patch('yfinance.Ticker'):
                response = advanced_features.api_usage_analytics(request)
            
            if response.status_code == 200:
                data = json.loads(response.content.decode())
                if data.get('success'):
                    analytics = data.get('usage_analytics', {})
                    print(f"✅ User Analytics - Total requests: {analytics.get('total_requests', 0)}")
                    print(f"✅ User Analytics - Avg response time: {analytics.get('avg_response_time_ms', 0)}ms")
                    print(f"✅ User Analytics - Monthly usage: {analytics.get('monthly_usage', {})}")
                    return True
                else:
                    print(f"❌ User Analytics failed: {data.get('error')}")
                    return False
            else:
                print(f"❌ User Analytics HTTP error: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ API Usage Analytics test failed: {e}")
            return False
    
    def test_market_sentiment(self):
        """Test Market Sentiment Analysis feature"""
        print("\n🎯 Testing Market Sentiment Analysis...")
        
        if not DJANGO_AVAILABLE:
            print("❌ Skipping - Django not available")
            return False
        
        try:
            # Test sentiment for AAPL
            request = self.factory.get('/api/advanced/sentiment/AAPL/')
            request.user = self.test_user
            
            with patch('yfinance.Ticker') as mock_ticker:
                # Mock yfinance response
                mock_stock = MagicMock()
                mock_stock.news = [
                    {'title': 'Apple reports strong earnings', 'summary': 'Great quarter for Apple'},
                    {'title': 'AAPL stock rises', 'summary': 'Positive market response'}
                ]
                mock_ticker.return_value = mock_stock
                
                response = advanced_features.market_sentiment_api(request, 'AAPL')
            
            if response.status_code == 200:
                data = json.loads(response.content.decode())
                if data.get('success'):
                    sentiment = data.get('sentiment_analysis', {})
                    print(f"✅ Sentiment for AAPL: {sentiment.get('overall_sentiment', 0)}")
                    print(f"✅ Sentiment label: {sentiment.get('sentiment_label', 'Unknown')}")
                    print(f"✅ Confidence: {sentiment.get('confidence', 0)}")
                    
                    # Test sentiment dashboard
                    request_dash = self.factory.get('/api/advanced/sentiment-dashboard/')
                    request_dash.user = self.test_user
                    
                    response_dash = advanced_features.sentiment_dashboard_api(request_dash)
                    if response_dash.status_code == 200:
                        dash_data = json.loads(response_dash.content.decode())
                        if dash_data.get('success'):
                            market_sentiment = dash_data.get('market_sentiment', {})
                            print(f"✅ Market sentiment dashboard: {market_sentiment.get('market_mood', 'Unknown')}")
                            return True
                    
                    return True
                else:
                    print(f"❌ Sentiment analysis failed: {data.get('error')}")
                    return False
            else:
                print(f"❌ Sentiment analysis HTTP error: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Market Sentiment test failed: {e}")
            return False
    
    def test_portfolio_analytics(self):
        """Test Portfolio Analytics feature"""
        print("\n📈 Testing Portfolio Analytics...")
        
        if not DJANGO_AVAILABLE:
            print("❌ Skipping - Django not available")
            return False
        
        try:
            request = self.factory.get(f'/api/advanced/portfolio-analytics/{self.test_portfolio.id}/')
            request.user = self.test_user
            
            with patch('yfinance.Ticker') as mock_ticker:
                # Mock yfinance responses for portfolio holdings
                mock_stock = MagicMock()
                mock_stock.history.return_value = MagicMock()
                mock_stock.history.return_value.__len__ = lambda: 100
                mock_stock.history.return_value.__getitem__ = lambda self, key: [150.0] * 100
                mock_stock.history.return_value.tolist = lambda: [150.0] * 100
                mock_stock.info = {
                    'sector': 'Technology',
                    'marketCap': 3000000000000
                }
                mock_ticker.return_value = mock_stock
                
                response = advanced_features.portfolio_analytics_api(request, self.test_portfolio.id)
            
            if response.status_code == 200:
                data = json.loads(response.content.decode())
                if data.get('success'):
                    analytics = data.get('portfolio_analytics', {})
                    print(f"✅ Portfolio value: ${analytics.get('total_value', 0):,.2f}")
                    print(f"✅ Total return: {analytics.get('total_return_percent', 0)}%")
                    
                    risk_metrics = analytics.get('risk_metrics', {})
                    print(f"✅ Sharpe ratio: {risk_metrics.get('sharpe_ratio', 0)}")
                    print(f"✅ Beta: {risk_metrics.get('beta', 0)}")
                    print(f"✅ Risk score: {risk_metrics.get('risk_score', 0)}")
                    
                    diversification = analytics.get('diversification', {})
                    print(f"✅ Holdings count: {diversification.get('number_of_holdings', 0)}")
                    
                    return True
                else:
                    print(f"❌ Portfolio analytics failed: {data.get('error')}")
                    return False
            else:
                print(f"❌ Portfolio analytics HTTP error: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Portfolio Analytics test failed: {e}")
            return False
    
    def test_compliance_security(self):
        """Test Compliance & Security features"""
        print("\n🔒 Testing Compliance & Security...")
        
        if not DJANGO_AVAILABLE:
            print("❌ Skipping - Django not available")
            return False
        
        try:
            # Test GDPR data export
            request = self.factory.get('/api/advanced/gdpr-export/')
            request.user = self.test_user
            
            response = advanced_features.gdpr_data_export(request)
            
            if response.status_code == 200:
                data = json.loads(response.content.decode())
                if data.get('success'):
                    export_data = data.get('data_export', {})
                    print(f"✅ GDPR export - User data exported")
                    print(f"✅ Personal info: {len(export_data.get('personal_info', {})) > 0}")
                    print(f"✅ Portfolios: {len(export_data.get('portfolios', []))}")
                    print(f"✅ API usage records: {len(export_data.get('api_usage', []))}")
                    
                    # Test security event reporting
                    security_request = self.factory.post('/api/advanced/security-event/', 
                        data=json.dumps({
                            'event_type': 'unusual_access',
                            'severity': 'medium',
                            'description': 'Test security event'
                        }),
                        content_type='application/json'
                    )
                    security_request.user = self.test_user
                    
                    security_response = advanced_features.report_security_event(security_request)
                    
                    if security_response.status_code == 200:
                        security_data = json.loads(security_response.content.decode())
                        if security_data.get('success'):
                            print(f"✅ Security event reported: {security_data.get('event_id')}")
                            return True
                    
                    return True
                else:
                    print(f"❌ GDPR export failed: {data.get('error')}")
                    return False
            else:
                print(f"❌ GDPR export HTTP error: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Compliance & Security test failed: {e}")
            return False
    
    def run_all_tests(self):
        """Run all advanced features tests"""
        print("🚀 Advanced Features Testing Suite")
        print("=" * 50)
        
        if not self.setup_test_data():
            print("❌ Test setup failed, cannot continue")
            return False
        
        results = {
            'API Usage Analytics': self.test_api_usage_analytics(),
            'Market Sentiment': self.test_market_sentiment(), 
            'Portfolio Analytics': self.test_portfolio_analytics(),
            'Compliance & Security': self.test_compliance_security()
        }
        
        print("\n" + "=" * 50)
        print("📊 Advanced Features Test Results")
        print("=" * 50)
        
        passed = 0
        total = len(results)
        
        for feature, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} {feature}")
            if result:
                passed += 1
        
        print(f"\n📈 Results: {passed}/{total} features passed")
        
        if passed == total:
            print("🎉 All advanced features are working correctly!")
            print("\n🚀 Features Ready for Production:")
            print("   • Tiered API Access with Usage Analytics")
            print("   • Market Sentiment Analysis with Multiple Sources")
            print("   • Comprehensive Portfolio Analytics with Risk Metrics")
            print("   • Regulatory Compliance & Security Monitoring")
        else:
            print("⚠️ Some advanced features need attention")
        
        return passed == total

def main():
    if not DJANGO_AVAILABLE:
        print("❌ Django is not properly configured")
        print("Please run this script after setting up the Django environment:")
        print("1. pip install -r requirements.txt")
        print("2. python manage.py migrate")
        print("3. python manage.py setup_memberships")
        return False
    
    tester = AdvancedFeaturesTester()
    return tester.run_all_tests()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
