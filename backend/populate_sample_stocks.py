"""
Populate sample stock data for testing screener functionality
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stockscanner_django.settings_local_sqlite')
django.setup()

from stocks.models import Stock, StockFundamentals
from decimal import Decimal

def populate_sample_data():
    """Create sample stock data with fundamentals"""
    
    sample_stocks = [
        {
            'ticker': 'AAPL',
            'company_name': 'Apple Inc.',
            'exchange': 'NASDAQ',
            'current_price': Decimal('175.50'),
            'price_change_percent': Decimal('2.35'),
            'volume': 65000000,
            'market_cap': 2750000000000,
            'pe_ratio': Decimal('28.50'),
            'dividend_yield': Decimal('0.52'),
            'week_52_low': Decimal('124.17'),
            'week_52_high': Decimal('199.62'),
            'fundamentals': {
                'pe_ratio': Decimal('28.50'),
                'forward_pe': Decimal('26.20'),
                'peg_ratio': Decimal('2.15'),
                'price_to_book': Decimal('39.80'),
                'gross_margin': Decimal('0.4381'),
                'operating_margin': Decimal('0.3021'),
                'profit_margin': Decimal('0.2531'),
                'roe': Decimal('1.4702'),
                'roa': Decimal('0.2851'),
                'revenue_growth_yoy': Decimal('0.0789'),
                'earnings_growth_yoy': Decimal('0.1156'),
                'current_ratio': Decimal('0.98'),
                'debt_to_equity': Decimal('1.73'),
                'dividend_yield': Decimal('0.0052'),
                'valuation_score': Decimal('55.50'),
                'strength_score': Decimal('85.30'),
                'valuation_status': 'fair_value',
                'recommendation': 'BUY',
                'strength_grade': 'A',
                'sector': 'Technology',
                'industry': 'Consumer Electronics'
            }
        },
        {
            'ticker': 'MSFT',
            'company_name': 'Microsoft Corporation',
            'exchange': 'NASDAQ',
            'current_price': Decimal('380.25'),
            'price_change_percent': Decimal('1.85'),
            'volume': 28000000,
            'market_cap': 2830000000000,
            'pe_ratio': Decimal('35.60'),
            'dividend_yield': Decimal('0.78'),
            'week_52_low': Decimal('275.03'),
            'week_52_high': Decimal('430.82'),
            'fundamentals': {
                'pe_ratio': Decimal('35.60'),
                'forward_pe': Decimal('31.20'),
                'peg_ratio': Decimal('2.45'),
                'price_to_book': Decimal('11.80'),
                'gross_margin': Decimal('0.6923'),
                'operating_margin': Decimal('0.4254'),
                'profit_margin': Decimal('0.3652'),
                'roe': Decimal('0.4287'),
                'roa': Decimal('0.1852'),
                'revenue_growth_yoy': Decimal('0.1256'),
                'earnings_growth_yoy': Decimal('0.1489'),
                'current_ratio': Decimal('1.77'),
                'debt_to_equity': Decimal('0.38'),
                'dividend_yield': Decimal('0.0078'),
                'valuation_score': Decimal('60.20'),
                'strength_score': Decimal('90.50'),
                'valuation_status': 'fair_value',
                'recommendation': 'STRONG BUY',
                'strength_grade': 'A',
                'sector': 'Technology',
                'industry': 'Software'
            }
        },
        {
            'ticker': 'GOOGL',
            'company_name': 'Alphabet Inc.',
            'exchange': 'NASDAQ',
            'current_price': Decimal('140.85'),
            'price_change_percent': Decimal('-0.52'),
            'volume': 35000000,
            'market_cap': 1780000000000,
            'pe_ratio': Decimal('25.30'),
            'dividend_yield': Decimal('0.00'),
            'week_52_low': Decimal('102.21'),
            'week_52_high': Decimal('151.55'),
            'fundamentals': {
                'pe_ratio': Decimal('25.30'),
                'forward_pe': Decimal('22.80'),
                'peg_ratio': Decimal('1.85'),
                'price_to_book': Decimal('5.60'),
                'gross_margin': Decimal('0.5645'),
                'operating_margin': Decimal('0.2756'),
                'profit_margin': Decimal('0.2358'),
                'roe': Decimal('0.2656'),
                'roa': Decimal('0.1523'),
                'revenue_growth_yoy': Decimal('0.1089'),
                'earnings_growth_yoy': Decimal('0.1345'),
                'current_ratio': Decimal('2.85'),
                'debt_to_equity': Decimal('0.11'),
                'dividend_yield': Decimal('0.0000'),
                'valuation_score': Decimal('72.50'),
                'strength_score': Decimal('88.20'),
                'valuation_status': 'undervalued',
                'recommendation': 'STRONG BUY',
                'strength_grade': 'A',
                'sector': 'Technology',
                'industry': 'Internet Content & Information'
            }
        },
        {
            'ticker': 'JPM',
            'company_name': 'JPMorgan Chase & Co.',
            'exchange': 'NYSE',
            'current_price': Decimal('158.75'),
            'price_change_percent': Decimal('0.85'),
            'volume': 12500000,
            'market_cap': 460000000000,
            'pe_ratio': Decimal('10.50'),
            'dividend_yield': Decimal('2.45'),
            'week_52_low': Decimal('135.19'),
            'week_52_high': Decimal('172.96'),
            'fundamentals': {
                'pe_ratio': Decimal('10.50'),
                'forward_pe': Decimal('9.80'),
                'peg_ratio': Decimal('1.25'),
                'price_to_book': Decimal('1.75'),
                'gross_margin': Decimal('0.6523'),
                'operating_margin': Decimal('0.3852'),
                'profit_margin': Decimal('0.3156'),
                'roe': Decimal('0.1689'),
                'roa': Decimal('0.0145'),
                'revenue_growth_yoy': Decimal('0.0845'),
                'earnings_growth_yoy': Decimal('0.0956'),
                'current_ratio': Decimal('1.25'),
                'debt_to_equity': Decimal('1.45'),
                'dividend_yield': Decimal('0.0245'),
                'valuation_score': Decimal('78.30'),
                'strength_score': Decimal('82.10'),
                'valuation_status': 'undervalued',
                'recommendation': 'STRONG BUY',
                'strength_grade': 'B',
                'sector': 'Financials',
                'industry': 'Banks'
            }
        },
        {
            'ticker': 'JNJ',
            'company_name': 'Johnson & Johnson',
            'exchange': 'NYSE',
            'current_price': Decimal('156.30'),
            'price_change_percent': Decimal('-0.25'),
            'volume': 8500000,
            'market_cap': 385000000000,
            'pe_ratio': Decimal('15.80'),
            'dividend_yield': Decimal('3.05'),
            'week_52_low': Decimal('143.13'),
            'week_52_high': Decimal('170.13'),
            'fundamentals': {
                'pe_ratio': Decimal('15.80'),
                'forward_pe': Decimal('14.50'),
                'peg_ratio': Decimal('2.85'),
                'price_to_book': Decimal('5.20'),
                'gross_margin': Decimal('0.6812'),
                'operating_margin': Decimal('0.2456'),
                'profit_margin': Decimal('0.1923'),
                'roe': Decimal('0.2456'),
                'roa': Decimal('0.0856'),
                'revenue_growth_yoy': Decimal('0.0523'),
                'earnings_growth_yoy': Decimal('0.0612'),
                'current_ratio': Decimal('1.25'),
                'debt_to_equity': Decimal('0.52'),
                'dividend_yield': Decimal('0.0305'),
                'valuation_score': Decimal('68.90'),
                'strength_score': Decimal('76.50'),
                'valuation_status': 'undervalued',
                'recommendation': 'BUY',
                'strength_grade': 'B',
                'sector': 'Healthcare',
                'industry': 'Pharmaceuticals'
            }
        }
    ]
    
    for stock_data in sample_stocks:
        # Extract fundamentals data
        fundamentals_data = stock_data.pop('fundamentals')
        
        # Create or update stock
        stock, created = Stock.objects.update_or_create(
            ticker=stock_data['ticker'],
            defaults={
                'symbol': stock_data['ticker'],
                'name': stock_data['company_name'],
                **stock_data
            }
        )
        
        # Create or update fundamentals
        StockFundamentals.objects.update_or_create(
            stock=stock,
            defaults=fundamentals_data
        )
        
        print(f"{'Created' if created else 'Updated'} {stock.ticker} - {stock.company_name}")
    
    print(f"\n✅ Successfully populated {len(sample_stocks)} stocks with fundamentals")
    print(f"Total stocks in database: {Stock.objects.count()}")
    print(f"Stocks with fundamentals: {StockFundamentals.objects.count()}")

if __name__ == '__main__':
    populate_sample_data()
