from django.apps import AppConfig
import threading
import time
import schedule


class StocksConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "stocks"
    
    def ready(self):
        import stocks.signals
        
        # Start background scheduler when server starts
        def start_nasdaq_scheduler():
            time.sleep(15)  # Wait 15 seconds after server start
            try:
                from django.core.management import call_command
                from django.db import connection
                
                # Check if database is ready
                with connection.cursor() as cursor:
                    cursor.execute("SELECT 1")
                
                print("🚀 Starting NASDAQ data scheduler (every 10 minutes)...")
                
                # Define the NASDAQ update function
                def update_nasdaq_data():
                    try:
                        print(f"🔄 [{time.strftime('%Y-%m-%d %H:%M:%S')}] Updating NASDAQ stock data...")
                        
                        # Update only NASDAQ stock prices
                        call_command('update_stocks_yfinance')
                        
                        # Scrape news data
                        from news.scraper import update_news_data
                        update_news_data()
                        
                        print(f"✅ [{time.strftime('%Y-%m-%d %H:%M:%S')}] NASDAQ data update completed!")
                        
                    except Exception as e:
                        print(f"❌ [{time.strftime('%Y-%m-%d %H:%M:%S')}] Error updating NASDAQ data: {e}")
                
                # Schedule NASDAQ updates every 10 minutes
                schedule.every(10).minutes.do(update_nasdaq_data)
                
                # Run first update immediately
                update_nasdaq_data()
                
                # Start the scheduler loop
                def run_scheduler():
                    print("⏰ NASDAQ scheduler started - updates every 10 minutes")
                    while True:
                        schedule.run_pending()
                        time.sleep(30)  # Check every 30 seconds
                
                # Start scheduler in background thread
                scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
                scheduler_thread.start()
                
            except Exception as e:
                print(f"❌ Error starting NASDAQ scheduler: {e}")
        
        # Start scheduler when server starts (only once)
        if not hasattr(self, '_scheduler_started'):
            self._scheduler_started = True
            thread = threading.Thread(target=start_nasdaq_scheduler, daemon=True)
            thread.start()
