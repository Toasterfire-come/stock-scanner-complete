from django.apps import AppConfig
import threading
import time


class StocksConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "stocks"
    
    def ready(self):
        import stocks.signals
        
        # Start background data loading after a short delay
        # This prevents issues during migrations and initial setup
        def delayed_startup():
            time.sleep(10)  # Wait 10 seconds after startup
            try:
                from django.core.management import call_command
                from django.db import connection
                
                # Check if database is ready
                with connection.cursor() as cursor:
                    cursor.execute("SELECT 1")
                
                print("🚀 Starting automatic data loading...")
                
                # Load NASDAQ tickers if none exist
                from .models import StockAlert
                if StockAlert.objects.count() == 0:
                    print("📊 Loading NASDAQ tickers...")
                    call_command('load_nasdaq_only')
                
                # Update stock data
                print("📈 Updating stock data...")
                call_command('update_stocks_yfinance')
                
                # Load news data
                print("📰 Loading news data...")
                from news.scraper import update_news_data
                update_news_data()
                
                print("✅ Automatic data loading completed!")
                
            except Exception as e:
                print(f"❌ Error during automatic data loading: {e}")
        
        # Run in background thread to avoid blocking startup
        if not hasattr(self, '_startup_thread_started'):
            self._startup_thread_started = True
            thread = threading.Thread(target=delayed_startup, daemon=True)
            thread.start()
