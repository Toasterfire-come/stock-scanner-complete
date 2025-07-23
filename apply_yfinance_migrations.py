#!/usr/bin/env python3
"""
Apply YFinance System Migrations
Ensures all database changes are properly applied for the new API system
"""

import os
import sys
import django
from pathlib import Path

# Add the project directory to Python path
project_dir = Path(__file__).resolve().parent
sys.path.append(str(project_dir))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stockscanner_django.settings')
django.setup()

def run_migrations():
    """Run all pending migrations"""
    print("🔄 Applying database migrations...")
    
    from django.core.management import call_command
    from io import StringIO
    
    try:
        # Run makemigrations to create any new migrations
        print("   📝 Creating new migrations...")
        out = StringIO()
        call_command('makemigrations', stdout=out, verbosity=1)
        output = out.getvalue()
        
        if "No changes detected" in output:
            print("   ✅ No new migrations needed")
        else:
            print(f"   ✅ New migrations created: {output.strip()}")
        
        # Apply all migrations
        print("   🔄 Applying migrations...")
        out = StringIO()
        call_command('migrate', stdout=out, verbosity=1)
        output = out.getvalue()
        print(f"   ✅ Migrations applied: {output.strip()}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Migration failed: {e}")
        return False

def verify_model_fields():
    """Verify that all required model fields exist"""
    print("🔍 Verifying model fields...")
    
    try:
        from stocks.models import StockAlert
        
        # Check if required fields exist
        field_names = [field.name for field in StockAlert._meta.get_fields()]
        required_fields = [
            'ticker', 'company_name', 'current_price', 
            'price_change_today', 'price_change_percent',
            'volume_today', 'market_cap', 'last_updated', 
            'data_source', 'is_active'
        ]
        
        missing_fields = [field for field in required_fields if field not in field_names]
        
        if missing_fields:
            print(f"   ❌ Missing fields: {missing_fields}")
            return False
        else:
            print("   ✅ All required fields present")
            print(f"   📊 Total fields: {len(field_names)}")
            return True
            
    except Exception as e:
        print(f"   ❌ Field verification failed: {e}")
        return False

def update_data_source():
    """Update existing records to use new data source"""
    print("🔄 Updating data source for existing records...")
    
    try:
        from stocks.models import StockAlert
        from django.utils import timezone
        
        # Update records without data_source
        updated_count = StockAlert.objects.filter(
            data_source__isnull=True
        ).update(
            data_source='yahoo_finance',
            last_updated=timezone.now()
        )
        
        print(f"   ✅ Updated {updated_count} records with data_source")
        
        # Update records with old sources
        old_sources_updated = StockAlert.objects.filter(
            data_source__in=['iex', 'iex_cloud', 'alpha_vantage', 'twelve_data']
        ).update(
            data_source='yahoo_finance',
            last_updated=timezone.now()
        )
        
        print(f"   ✅ Updated {old_sources_updated} records from old sources")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Data source update failed: {e}")
        return False

def test_api_manager():
    """Test the new API manager"""
    print("🧪 Testing API manager...")
    
    try:
        from stocks.api_manager import stock_manager
        
        # Test initialization
        print("   ✅ API manager imported successfully")
        
        # Test configuration
        usage_stats = stock_manager.get_usage_stats()
        print(f"   📊 APIs configured: {len(usage_stats)}")
        
        # Test connections (optional - might be slow)
        print("   🔗 Testing API connections...")
        connections = stock_manager.test_connection()
        
        for api, connected in connections.items():
            status = "✅" if connected else "⚠️"
            print(f"      {status} {api.replace('_', ' ').title()}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ API manager test failed: {e}")
        return False

def main():
    """Run all migration and verification steps"""
    print("🚀 YFinance System Migration & Verification")
    print("=" * 50)
    
    steps = [
        ("Database Migrations", run_migrations),
        ("Model Field Verification", verify_model_fields),
        ("Data Source Update", update_data_source),
        ("API Manager Test", test_api_manager),
    ]
    
    results = []
    
    for step_name, step_func in steps:
        print(f"\n📋 {step_name}")
        print("-" * 30)
        
        try:
            result = step_func()
            results.append((step_name, result))
            
            if result:
                print(f"✅ {step_name}: COMPLETED")
            else:
                print(f"❌ {step_name}: FAILED")
                
        except Exception as e:
            print(f"💥 {step_name}: ERROR - {e}")
            results.append((step_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 MIGRATION SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for step_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status} - {step_name}")
    
    print(f"\n📈 Results: {passed}/{total} steps completed ({(passed/total*100):.1f}%)")
    
    if passed == total:
        print("🎉 ALL MIGRATION STEPS COMPLETED!")
        print("✅ Your system is ready for the new YFinance API")
    elif passed >= total * 0.8:
        print("✅ Most steps completed. System should be functional.")
    else:
        print("⚠️ Several steps failed. Please review and fix issues.")
    
    print("\n💡 Next steps:")
    print("   1. Run: python test_yfinance_system.py")
    print("   2. Run: python manage.py update_stocks_yfinance --test-mode")
    print("   3. Configure Finnhub backup keys (optional)")
    print("   4. Start using the new system!")
    
    return passed == total

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️ Migration interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Migration failed: {e}")
        sys.exit(1)