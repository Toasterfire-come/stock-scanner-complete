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
    
    # Try multiple PE ratio fields, prioritizing trailing PE
    pe_fields = ['trailingPE', 'forwardPE', 'pegRatio']
    
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
    
    dividend_fields = ['dividendYield', 'trailingAnnualDividendYield', 'yield', 'dividendRate']
    
    for field in dividend_fields:
        value = info.get(field)
        if value is not None and value != 0 and not pd.isna(value):
            try:
                div_value = float(value)
                # Handle both percentage (0-1) and actual yield values
                if 0 <= div_value <= 1:  # Percentage format (0-100%)
                    return safe_decimal_conversion(div_value)
                elif div_value > 1 and div_value <= 100:  # Could be percentage as whole number
                    return safe_decimal_conversion(div_value / 100)
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
    
    # Try robust extraction of shares outstanding for market cap fallback
    shares_outstanding = (info.get('sharesOutstanding') or
                           info.get('impliedSharesOutstanding') or
                           info.get('floatShares'))

    # Try robust extraction of average volume 3 months
    avg_vol_candidates = [
        info.get('averageVolume'),
        info.get('averageVolume10days'),
        info.get('averageDailyVolume10Day'),
        info.get('averageVolume3Months'),
    ]
    avg_vol_value = next((v for v in avg_vol_candidates if v not in (None, 0)), None)

    return {
        'ticker': symbol,
        'symbol': symbol,
        'company_name': info.get('longName', info.get('shortName', symbol)),
        'name': info.get('longName', info.get('shortName', symbol)),
        'current_price': safe_decimal_conversion(current_price) if current_price else safe_decimal_conversion(info.get('currentPrice')),
        
        # Price range data
        'days_low': safe_decimal_conversion(info.get('dayLow')),
        'days_high': safe_decimal_conversion(info.get('dayHigh')),
        
        # Volume data - try multiple fields
        'volume': safe_decimal_conversion(info.get('volume') or info.get('regularMarketVolume')),
        'volume_today': safe_decimal_conversion(info.get('volume') or info.get('regularMarketVolume')),
        'avg_volume_3mon': safe_decimal_conversion(avg_vol_value),
        
        # Market data
        'market_cap': safe_decimal_conversion(info.get('marketCap')),
        'shares_outstanding': safe_decimal_conversion(shares_outstanding),
        
        # Financial ratios
        'pe_ratio': extract_pe_ratio(info),
        'dividend_yield': extract_dividend_yield(info),
        
        # Target and range
        'one_year_target': safe_decimal_conversion(info.get('targetMeanPrice')),
        'week_52_low': safe_decimal_conversion(info.get('fiftyTwoWeekLow')),
        'week_52_high': safe_decimal_conversion(info.get('fiftyTwoWeekHigh')),
        
        # Additional metrics
        'earnings_per_share': safe_decimal_conversion(info.get('trailingEps') or info.get('forwardEps')),
        'book_value': safe_decimal_conversion(info.get('bookValue')),
        'price_to_book': safe_decimal_conversion(info.get('priceToBook')),
        'exchange': info.get('exchange', info.get('market', 'NYSE')),
    }

def extract_stock_data_from_fast_info(fast_info, symbol, current_price=None):
    """Extract best-effort stock data from yfinance fast_info object.
    This fills basic fields when full info is unavailable.
    """
    if not fast_info:
        return {}
    
    # Access attributes safely; fast_info provides attributes not dict keys
    get = lambda attr_names: next((getattr(fast_info, a, None) for a in attr_names if getattr(fast_info, a, None) is not None), None)
    
    day_low = get(['day_low', 'low'])
    day_high = get(['day_high', 'high'])
    volume = get(['last_volume', 'volume'])
    avg_vol_3m = get(['three_month_average_volume', 'ten_day_average_volume'])
    market_cap = get(['market_cap'])
    shares_outstanding = get(['shares_outstanding', 'shares'])
    wk52_low = get(['fifty_two_week_low', 'year_low'])
    wk52_high = get(['fifty_two_week_high', 'year_high'])
    exch = get(['exchange']) or 'NYSE'
    name = get(['short_name', 'long_name']) or symbol
    
    return {
        'ticker': symbol,
        'symbol': symbol,
        'company_name': name,
        'name': name,
        'current_price': safe_decimal_conversion(current_price) if current_price else None,
        'days_low': safe_decimal_conversion(day_low),
        'days_high': safe_decimal_conversion(day_high),
        'volume': safe_decimal_conversion(volume),
        'volume_today': safe_decimal_conversion(volume),
        'avg_volume_3mon': safe_decimal_conversion(avg_vol_3m),
        'market_cap': safe_decimal_conversion(market_cap),
        'shares_outstanding': safe_decimal_conversion(shares_outstanding),
        'pe_ratio': None,
        'dividend_yield': None,
        'one_year_target': None,
        'week_52_low': safe_decimal_conversion(wk52_low),
        'week_52_high': safe_decimal_conversion(wk52_high),
        'earnings_per_share': None,
        'book_value': None,
        'price_to_book': None,
        'exchange': exch,
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

def compute_market_cap_fallback(current_price, shares_outstanding):
    """Compute market cap from price and shares when API field is missing.
    Returns Decimal or None.
    """
    try:
        if current_price is None or shares_outstanding is None:
            return None
        # Guard against zeros and NaNs
        if pd.isna(current_price) or pd.isna(shares_outstanding):
            return None
        # Convert to Decimal safely
        price_dec = safe_decimal_conversion(current_price)
        shares_dec = safe_decimal_conversion(shares_outstanding)
        if price_dec is None or shares_dec is None:
            return None
        if price_dec <= 0 or shares_dec <= 0:
            return None
        return safe_decimal_conversion(price_dec * shares_dec)
    except Exception:
        return None