"""
Database optimization management command
Adds indexes, cleans up old data, and optimizes queries
"""

from django.core.management.base import BaseCommand
from django.db import connection, transaction
from django.utils import timezone
from datetime import timedelta

from stocks.models import StockAlert, Membership, Portfolio, PortfolioHolding, TechnicalIndicator, MarketAnalysis
from emails.models import EmailSubscription


class Command(BaseCommand):
    help = 'Optimize database performance with indexes and cleanup'

    def add_arguments(self, parser):
        parser.add_argument(
            '--cleanup-only',
            action='store_true',
            help='Only perform cleanup, skip index creation',
        )
        parser.add_argument(
            '--indexes-only',
            action='store_true',
            help='Only create indexes, skip cleanup',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting database optimization...'))
        
        if not options['cleanup_only']:
            self.create_database_indexes()
        
        if not options['indexes_only']:
            self.cleanup_old_data()
        
        self.analyze_query_performance()
        
        self.stdout.write(self.style.SUCCESS('Database optimization complete!'))

    def create_database_indexes(self):
        """Create database indexes for better performance"""
        self.stdout.write('Creating database indexes...')
        
        with connection.cursor() as cursor:
            # StockAlert indexes
            indexes = [
                'CREATE INDEX IF NOT EXISTS idx_stockalert_ticker ON stocks_stockalert(ticker);',
                'CREATE INDEX IF NOT EXISTS idx_stockalert_price ON stocks_stockalert(current_price);',
                'CREATE INDEX IF NOT EXISTS idx_stockalert_volume ON stocks_stockalert(volume_today);',
                'CREATE INDEX IF NOT EXISTS idx_stockalert_market_cap ON stocks_stockalert(market_cap);',
                'CREATE INDEX IF NOT EXISTS idx_stockalert_sector ON stocks_stockalert(sector);',
                'CREATE INDEX IF NOT EXISTS idx_stockalert_last_update ON stocks_stockalert(last_update);',
                
                # Membership indexes
                'CREATE INDEX IF NOT EXISTS idx_membership_tier ON stocks_membership(tier);',
                'CREATE INDEX IF NOT EXISTS idx_membership_active ON stocks_membership(is_active);',
                'CREATE INDEX IF NOT EXISTS idx_membership_user ON stocks_membership(user_id);',
                'CREATE INDEX IF NOT EXISTS idx_membership_created ON stocks_membership(created_at);',
                
                # Portfolio indexes
                'CREATE INDEX IF NOT EXISTS idx_portfolio_user ON stocks_portfolio(user_id);',
                'CREATE INDEX IF NOT EXISTS idx_portfolio_active ON stocks_portfolio(is_active);',
                'CREATE INDEX IF NOT EXISTS idx_portfolio_created ON stocks_portfolio(created_at);',
                
                # PortfolioHolding indexes
                'CREATE INDEX IF NOT EXISTS idx_holding_portfolio ON stocks_portfolioholding(portfolio_id);',
                'CREATE INDEX IF NOT EXISTS idx_holding_ticker ON stocks_portfolioholding(ticker);',
                'CREATE INDEX IF NOT EXISTS idx_holding_updated ON stocks_portfolioholding(last_updated);',
                
                # TechnicalIndicator indexes
                'CREATE INDEX IF NOT EXISTS idx_indicator_ticker ON stocks_technicalindicator(ticker);',
                'CREATE INDEX IF NOT EXISTS idx_indicator_type ON stocks_technicalindicator(indicator_type);',
                'CREATE INDEX IF NOT EXISTS idx_indicator_calculated ON stocks_technicalindicator(calculated_at);',
                
                # MarketAnalysis indexes
                'CREATE INDEX IF NOT EXISTS idx_analysis_type ON stocks_marketanalysis(analysis_type);',
                'CREATE INDEX IF NOT EXISTS idx_analysis_premium ON stocks_marketanalysis(is_premium);',
                'CREATE INDEX IF NOT EXISTS idx_analysis_created ON stocks_marketanalysis(created_at);',
                'CREATE INDEX IF NOT EXISTS idx_analysis_author ON stocks_marketanalysis(author_id);',
                
                # EmailSubscription indexes
                'CREATE INDEX IF NOT EXISTS idx_email_active ON emails_emailsubscription(is_active);',
                'CREATE INDEX IF NOT EXISTS idx_email_category ON emails_emailsubscription(category);',
                'CREATE INDEX IF NOT EXISTS idx_email_created ON emails_emailsubscription(created_at);',
                
                # Composite indexes for common queries
                'CREATE INDEX IF NOT EXISTS idx_stockalert_price_volume ON stocks_stockalert(current_price, volume_today);',
                'CREATE INDEX IF NOT EXISTS idx_membership_tier_active ON stocks_membership(tier, is_active);',
                'CREATE INDEX IF NOT EXISTS idx_portfolio_user_active ON stocks_portfolio(user_id, is_active);',
                'CREATE INDEX IF NOT EXISTS idx_holding_portfolio_ticker ON stocks_portfolioholding(portfolio_id, ticker);',
                'CREATE INDEX IF NOT EXISTS idx_indicator_ticker_type ON stocks_technicalindicator(ticker, indicator_type);',
            ]
            
            for index_sql in indexes:
                try:
                    cursor.execute(index_sql)
                    self.stdout.write(f'  ✓ Created index')
                except Exception as e:
                    self.stdout.write(f'  ⚠ Index creation skipped: {str(e)[:50]}...')

    def cleanup_old_data(self):
        """Clean up old and unnecessary data"""
        self.stdout.write('Cleaning up old data...')
        
        # Clean up old technical indicators (older than 24 hours)
        old_indicators = TechnicalIndicator.objects.filter(
            calculated_at__lt=timezone.now() - timedelta(hours=24)
        )
        old_count = old_indicators.count()
        old_indicators.delete()
        self.stdout.write(f'  ✓ Removed {old_count} old technical indicators')
        
        # Clean up inactive email subscriptions older than 1 year
        old_emails = EmailSubscription.objects.filter(
            is_active=False,
            created_at__lt=timezone.now() - timedelta(days=365)
        )
        old_email_count = old_emails.count()
        old_emails.delete()
        self.stdout.write(f'  ✓ Removed {old_email_count} old email subscriptions')
        
        # Clean up very old stock alerts (older than 30 days)
        old_stocks = StockAlert.objects.filter(
            last_update__lt=timezone.now() - timedelta(days=30)
        )
        old_stock_count = old_stocks.count()
        old_stocks.delete()
        self.stdout.write(f'  ✓ Removed {old_stock_count} old stock alerts')
        
        # Update statistics
        self.update_database_statistics()

    def update_database_statistics(self):
        """Update database statistics for better query planning"""
        self.stdout.write('Updating database statistics...')
        
        with connection.cursor() as cursor:
            # SQLite specific optimization
            if 'sqlite' in connection.vendor:
                cursor.execute('ANALYZE;')
                cursor.execute('VACUUM;')
                self.stdout.write('  ✓ SQLite database optimized')
            
            # PostgreSQL specific optimization
            elif 'postgresql' in connection.vendor:
                cursor.execute('ANALYZE;')
                self.stdout.write('  ✓ PostgreSQL statistics updated')

    def analyze_query_performance(self):
        """Analyze and report on query performance"""
        self.stdout.write('Analyzing query performance...')
        
        # Test common queries and report performance
        test_queries = [
            ('Stock filtering', 'SELECT COUNT(*) FROM stocks_stockalert WHERE current_price > 50 AND volume_today > 1000000'),
            ('Membership analytics', 'SELECT tier, COUNT(*) FROM stocks_membership WHERE is_active = 1 GROUP BY tier'),
            ('Portfolio summary', 'SELECT COUNT(*) FROM stocks_portfolio WHERE is_active = 1'),
            ('Active subscriptions', 'SELECT COUNT(*) FROM emails_emailsubscription WHERE is_active = 1'),
        ]
        
        with connection.cursor() as cursor:
            for query_name, query_sql in test_queries:
                try:
                    import time
                    start_time = time.time()
                    cursor.execute(query_sql)
                    result = cursor.fetchall()
                    end_time = time.time()
                    
                    duration_ms = (end_time - start_time) * 1000
                    self.stdout.write(f'  ✓ {query_name}: {duration_ms:.2f}ms')
                    
                except Exception as e:
                    self.stdout.write(f'  ⚠ {query_name}: Error - {str(e)}')

    def get_database_size_info(self):
        """Get database size information"""
        with connection.cursor() as cursor:
            if 'sqlite' in connection.vendor:
                cursor.execute("SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size();")
                size = cursor.fetchone()[0] if cursor.rowcount > 0 else 0
                size_mb = size / (1024 * 1024)
                self.stdout.write(f'Database size: {size_mb:.2f} MB')
            
            # Count records in each table
            tables = [
                ('StockAlert', 'stocks_stockalert'),
                ('Membership', 'stocks_membership'),
                ('Portfolio', 'stocks_portfolio'),
                ('PortfolioHolding', 'stocks_portfolioholding'),
                ('TechnicalIndicator', 'stocks_technicalindicator'),
                ('MarketAnalysis', 'stocks_marketanalysis'),
                ('EmailSubscription', 'emails_emailsubscription'),
            ]
            
            for model_name, table_name in tables:
                try:
                    cursor.execute(f'SELECT COUNT(*) FROM {table_name};')
                    count = cursor.fetchone()[0]
                    self.stdout.write(f'{model_name}: {count:,} records')
                except Exception as e:
                    self.stdout.write(f'{model_name}: Error counting - {str(e)}')
