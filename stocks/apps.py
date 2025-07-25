from django.apps import AppConfig
import threading
import time
import schedule


class StocksConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "stocks"
    
    def ready(self):
        import stocks.signals
        
        # Start background data loading and scheduling
        def delayed_startup():
            time.sleep(10)  # Wait 10 seconds after startup
            try:
                from django.core.management import call_command
                from django.db import connection
                
                # Check if database is ready
                with connection.cursor() as cursor:
                    cursor.execute("SELECT 1")
                
                print("🚀 Starting automatic NASDAQ data scheduler...")
                
                # Load NASDAQ tickers if none exist (initial load)
                from .models import StockAlert
                if StockAlert.objects.count() == 0:
                    print("📊 Initial NASDAQ data load...")
                    call_command('load_nasdaq_only')
                
                # Define the data update function
                def update_nasdaq_data():
                    try:
                        print(f"🔄 [{time.strftime('%Y-%m-%d %H:%M:%S')}] Updating NASDAQ stock data...")
                        
                        # Update stock prices from yfinance
                        call_command('update_stocks_yfinance')
                        
                        # Scrape news data
                        from news.scraper import update_news_data
                        update_news_data()
                        
                        print(f"✅ [{time.strftime('%Y-%m-%d %H:%M:%S')}] NASDAQ data update completed!")
                        
                    except Exception as e:
                        print(f"❌ [{time.strftime('%Y-%m-%d %H:%M:%S')}] Error updating NASDAQ data: {e}")
                
                # Schedule the job every 10 minutes
                schedule.every(10).minutes.do(update_nasdaq_data)
                
                # Run initial update
                update_nasdaq_data()
                
                # Start the scheduler loop
                def run_scheduler():
                    while True:
                        schedule.run_pending()
                        time.sleep(30)  # Check every 30 seconds for pending jobs
                
                # Start scheduler in a separate thread
                scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
                scheduler_thread.start()
                
                print("✅ NASDAQ data scheduler started - updates every 10 minutes")
                
            except Exception as e:
                print(f"❌ Error during automatic data loading setup: {e}")
        
        # Run in background thread to avoid blocking startup
        if not hasattr(self, '_startup_thread_started'):
            self._startup_thread_started = True
            thread = threading.Thread(target=delayed_startup, daemon=True)
            thread.start()
