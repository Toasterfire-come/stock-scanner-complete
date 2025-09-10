"""
Shared stock data utility functions
Centralizes common logic for stock data processing
"""

import pandas as pd
from decimal import Decimal, InvalidOperation
import logging

logger = logging.getLogger(__name__)

def safe_decimal_conversion(value):
    """Safely convert value to Decimal, skip Infinity/NaN"""
    if value is None or pd.isna(value):
        return None
    try:
        if value == float('inf') or value == float('-inf'):
            return None
        return Decimal(str(value))
    except (ValueError, TypeError, InvalidOperation):
        return None

def load_nyse_symbols_from_csv(csv_file, test_mode=False, max_symbols=None):
    """Load NYSE symbols from CSV file with filtering"""
    try:
        # Read NYSE data from CSV
        data = pd.read_csv(csv_file)
        
        # Enhanced filtering for active NYSE stocks
        active_count = 0
        delisted_count = 0
        etf_count = 0
        symbols = []
        
        for _, row in data.iterrows():
            symbol = str(row.get('Symbol', '')).strip().upper()
            name = str(row.get('Name', '')).strip()
            
            if not symbol or len(symbol) > 10:
                continue
                
            # Skip ETFs and funds (broader filtering)
            etf_indicators = ['ETF', 'FUND', 'TRUST', 'INDEX', 'REIT', 'ADR', 'DEPOSITARY']
            if any(indicator in name.upper() for indicator in etf_indicators):
                etf_count += 1
                continue
                
            # Skip symbols with special characters that indicate delisted/non-standard
            if any(char in symbol for char in ['.', '^', '/', '-', '=']):
                delisted_count += 1
                continue
                
            # Skip very short symbols (often test symbols)
            if len(symbol) < 1:
                delisted_count += 1
                continue
                
            symbols.append(symbol)
            active_count += 1
            
            # Test mode: limit to first N symbols
            if test_mode and len(symbols) >= 100:
                break
                
            # Max symbols limit
            if max_symbols and len(symbols) >= max_symbols:
                break
        
        logger.info(f"Loaded {len(symbols)} active NYSE symbols")
        logger.info(f"Filtered out {delisted_count} delisted stocks")
        logger.info(f"Filtered out {etf_count} ETFs")
        logger.info(f"Active stocks: {active_count}")
        
        return symbols
        
    except Exception as e:
        logger.error(f"Error loading NYSE symbols: {e}")
        return []

def extract_pe_ratio(info):
    """Extract PE ratio with multiple fallback options"""
    if not info:
        return None
    
    # Try multiple PE ratio fields
    pe_fields = ['trailingPE', 'forwardPE', 'priceToBook', 'priceToSalesTrailing12Months']
    
    for field in pe_fields:
        value = info.get(field)
        if value is not None and value != 0 and not pd.isna(value):
            try:
                pe_value = float(value)
                if 0 < pe_value < 1000:  # Reasonable PE range
                    return safe_decimal_conversion(pe_value)
            except (ValueError, TypeError):
                continue
    
    return None

def extract_dividend_yield(info):
    """Extract dividend yield with fallback options"""
    if not info:
        return None
    
    dividend_fields = ['dividendYield', 'yield', 'trailingAnnualDividendYield']
    
    for field in dividend_fields:
        value = info.get(field)
        if value is not None and value != 0 and not pd.isna(value):
            try:
                div_value = float(value)
                if 0 <= div_value <= 1:  # Reasonable dividend yield range (0-100%)
                    return safe_decimal_conversion(div_value)
            except (ValueError, TypeError):
                continue
    
    return None

def calculate_change_percent_from_history(hist, symbol):
    """Calculate price change percentage from historical data"""
    if hist is None or hist.empty or len(hist) < 2:
        return None, None
    
    try:
        current = hist['Close'].iloc[-1]
        previous = hist['Close'].iloc[-2]
        
        if current and previous and previous != 0:
            change = current - previous
            change_percent = (change / previous) * 100
            return safe_decimal_conversion(change), safe_decimal_conversion(change_percent)
    except (IndexError, KeyError, ZeroDivisionError, TypeError) as e:
        logger.debug(f"Failed to calculate price changes for {symbol}: {e}")
    
    return None, None

def extract_stock_data_from_info(info, symbol, current_price=None):
    """Extract comprehensive stock data from yfinance info object"""
    if not info:
        return {}
    
    return {
        'ticker': symbol,
        'symbol': symbol,
        'company_name': info.get('longName', info.get('shortName', symbol)),
        'name': info.get('longName', info.get('shortName', symbol)),
        'current_price': safe_decimal_conversion(current_price) if current_price else None,
        
        # Price range data
        'days_low': safe_decimal_conversion(info.get('dayLow')),
        'days_high': safe_decimal_conversion(info.get('dayHigh')),
        
        # Volume data
        'volume': safe_decimal_conversion(info.get('volume')),
        'volume_today': safe_decimal_conversion(info.get('volume')),
        'avg_volume_3mon': safe_decimal_conversion(info.get('averageVolume')),
        
        # Market data
        'market_cap': safe_decimal_conversion(info.get('marketCap')),
        
        # Financial ratios
        'pe_ratio': extract_pe_ratio(info),
        'dividend_yield': extract_dividend_yield(info),
        
        # Target and range
        'one_year_target': safe_decimal_conversion(info.get('targetMeanPrice')),
        'week_52_low': safe_decimal_conversion(info.get('fiftyTwoWeekLow')),
        'week_52_high': safe_decimal_conversion(info.get('fiftyTwoWeekHigh')),
        
        # Additional metrics
        'earnings_per_share': safe_decimal_conversion(info.get('trailingEps')),
        'book_value': safe_decimal_conversion(info.get('bookValue')),
        'price_to_book': safe_decimal_conversion(info.get('priceToBook')),
        'exchange': info.get('exchange', 'NYSE'),
    }

def calculate_volume_ratio(volume, avg_volume):
    """Calculate volume ratio (DVAV - Day Volume Over Average Volume)"""
    if not volume or not avg_volume or avg_volume == 0:
        return None
    
    try:
        ratio = volume / avg_volume
        return safe_decimal_conversion(ratio)
    except (ZeroDivisionError, TypeError, ValueError):
        return None