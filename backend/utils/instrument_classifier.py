"""
Instrument Classification Utilities
Classifies financial instruments and filters relevant fields
"""

import logging

logger = logging.getLogger(__name__)


def classify_instrument(ticker, name, exchange=None):
    """
    Classify the type of financial instrument based on ticker and name.

    Args:
        ticker (str): Stock ticker symbol
        name (str): Company/instrument name
        exchange (str, optional): Exchange name

    Returns:
        str: Instrument type ('stock', 'etf', 'index', 'crypto', 'forex', 'commodity', 'bond')
    """
    ticker_upper = ticker.upper() if ticker else ""
    name_upper = name.upper() if name else ""

    # ETF Detection
    etf_keywords = ['ETF', 'FUND', 'TRUST', 'INDEX FUND']
    if any(keyword in name_upper for keyword in etf_keywords):
        return 'etf'

    # Index Detection
    index_keywords = ['^', 'INDEX']
    if ticker_upper.startswith('^') or any(keyword in name_upper for keyword in index_keywords):
        return 'index'

    # Cryptocurrency Detection
    crypto_keywords = ['BITCOIN', 'ETHEREUM', 'CRYPTO', 'COIN']
    crypto_suffixes = ['-USD', '/USD', 'USDT']
    if any(keyword in name_upper for keyword in crypto_keywords) or \
       any(ticker_upper.endswith(suffix) for suffix in crypto_suffixes):
        return 'crypto'

    # Forex Detection
    forex_pattern = len(ticker_upper) == 6 and ticker_upper.endswith('USD')
    if forex_pattern or 'FOREX' in name_upper or 'CURRENCY' in name_upper:
        return 'forex'

    # Commodity Detection
    commodity_keywords = ['GOLD', 'SILVER', 'OIL', 'GAS', 'COMMODITY']
    if any(keyword in name_upper for keyword in commodity_keywords):
        return 'commodity'

    # Bond Detection
    bond_keywords = ['BOND', 'TREASURY', 'NOTE', 'YIELD']
    if any(keyword in name_upper for keyword in bond_keywords):
        return 'bond'

    # Default to stock
    return 'stock'


def filter_fields_by_instrument(stock_data, instrument_type):
    """
    Filter stock data fields based on instrument type to return only relevant fields.

    Args:
        stock_data (dict): Complete stock data dictionary
        instrument_type (str): Instrument type from classify_instrument

    Returns:
        dict: Filtered stock data with only relevant fields for the instrument type
    """
    # Common fields for all instruments
    base_fields = [
        'ticker', 'symbol', 'name', 'company_name', 'exchange',
        'current_price', 'price_change', 'price_change_percent',
        'volume', 'last_updated'
    ]

    # Instrument-specific fields
    instrument_fields = {
        'stock': [
            'market_cap', 'pe_ratio', 'dividend_yield', 'earnings_per_share',
            'book_value', 'price_to_book', 'shares_available',
            'week_52_low', 'week_52_high', 'days_low', 'days_high',
            'avg_volume_3mon', 'one_year_target', 'bid_price', 'ask_price'
        ],
        'etf': [
            'market_cap', 'dividend_yield', 'week_52_low', 'week_52_high',
            'days_low', 'days_high', 'avg_volume_3mon', 'bid_price', 'ask_price'
        ],
        'index': [
            'week_52_low', 'week_52_high', 'days_low', 'days_high'
        ],
        'crypto': [
            'market_cap', 'week_52_low', 'week_52_high',
            'days_low', 'days_high', 'volume'
        ],
        'forex': [
            'bid_price', 'ask_price', 'days_low', 'days_high'
        ],
        'commodity': [
            'week_52_low', 'week_52_high', 'days_low', 'days_high'
        ],
        'bond': [
            'dividend_yield', 'current_price', 'price_change'
        ]
    }

    # Get relevant fields for this instrument type
    relevant_fields = set(base_fields + instrument_fields.get(instrument_type, []))

    # Filter the stock data
    filtered_data = {k: v for k, v in stock_data.items() if k in relevant_fields}

    # Add instrument type to the response
    filtered_data['instrument_type'] = instrument_type

    return filtered_data
