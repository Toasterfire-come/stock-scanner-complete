from django.core.management.base import BaseCommand
from stocks.models import Stock
from decimal import Decimal

class Command(BaseCommand):
    help = 'Load sample NASDAQ stock data for testing'
    
    def handle(self, *args, **options):
        sample_stocks = [
            {
                'ticker': 'AAPL',
                'symbol': 'AAPL',
                'company_name': 'Apple Inc.',
                'name': 'Apple Inc.',
                'current_price': Decimal('175.25'),
                'change_percent': Decimal('2.34'),
                'volume': 45678900,
                'market_cap': 2750000000000,
                'pe_ratio': Decimal('28.5'),
                'dividend_yield': Decimal('0.52'),
            },
            {
                'ticker': 'MSFT',
                'symbol': 'MSFT',
                'company_name': 'Microsoft Corporation',
                'name': 'Microsoft Corporation',
                'current_price': Decimal('412.80'),
                'change_percent': Decimal('-0.87'),
                'volume': 23456780,
                'market_cap': 3100000000000,
                'pe_ratio': Decimal('31.2'),
                'dividend_yield': Decimal('0.68'),
            },
            {
                'ticker': 'GOOGL',
                'symbol': 'GOOGL',
                'company_name': 'Alphabet Inc.',
                'name': 'Alphabet Inc.',
                'current_price': Decimal('142.65'),
                'change_percent': Decimal('1.56'),
                'volume': 34567890,
                'market_cap': 1800000000000,
                'pe_ratio': Decimal('25.8'),
                'dividend_yield': Decimal('0.00'),
            },
            {
                'ticker': 'TSLA',
                'symbol': 'TSLA', 
                'company_name': 'Tesla, Inc.',
                'name': 'Tesla, Inc.',
                'current_price': Decimal('242.64'),
                'change_percent': Decimal('3.59'),
                'volume': 45827394,
                'market_cap': 769384756293,
                'pe_ratio': Decimal('65.4'),
                'dividend_yield': Decimal('0.00'),
            },
            {
                'ticker': 'NVDA',
                'symbol': 'NVDA',
                'company_name': 'NVIDIA Corporation', 
                'name': 'NVIDIA Corporation',
                'current_price': Decimal('875.28'),
                'change_percent': Decimal('1.43'),
                'volume': 31847293,
                'market_cap': 2164857392847,
                'pe_ratio': Decimal('58.7'),
                'dividend_yield': Decimal('0.03'),
            }
        ]
        
        created_count = 0
        updated_count = 0
        
        for stock_data in sample_stocks:
            stock, created = Stock.objects.get_or_create(
                ticker=stock_data['ticker'],
                defaults=stock_data
            )
            
            if created:
                created_count += 1
                self.stdout.write(f"Created: {stock.ticker} - {stock.company_name}")
            else:
                # Update existing stock with new data
                for field, value in stock_data.items():
                    setattr(stock, field, value)
                stock.save()
                updated_count += 1
                self.stdout.write(f"Updated: {stock.ticker} - {stock.company_name}")
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully loaded {created_count} new stocks and updated {updated_count} existing stocks!'
            )
        )