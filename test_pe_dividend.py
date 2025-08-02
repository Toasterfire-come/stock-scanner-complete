#!/usr/bin/env python3
"""
Test script to verify PE ratio and dividend yield extraction
"""

import yfinance as yf
import pandas as pd

def _extract_pe_ratio(info):
    """Extract PE ratio with multiple fallback options"""
    if not info:
        return None
    
    # Try multiple PE ratio fields
    pe_fields = ['trailingPE', 'forwardPE', 'priceToBook', 'priceToSalesTrailing12Months']
    
    for field in pe_fields:
        value = info.get(field)
        if value is not None and value != 0 and not pd.isna(value):
            try:
                return float(value)
            except (ValueError, TypeError):
                continue
    
    return None

def _extract_dividend_yield(info):
    """Extract dividend yield with proper formatting"""
    if not info:
        return None
    
    # Try multiple dividend yield fields
    dividend_fields = ['dividendYield', 'fiveYearAvgDividendYield', 'trailingAnnualDividendYield']
    
    for field in dividend_fields:
        value = info.get(field)
        if value is not None and not pd.isna(value):
            try:
                # Convert to percentage if it's a decimal
                if isinstance(value, float) and value < 1:
                    return float(value * 100)
                else:
                    return float(value)
            except (ValueError, TypeError):
                continue
    
    return None

def test_stock_data(symbol):
    """Test stock data extraction for a given symbol"""
    print(f"\nTesting {symbol}...")
    
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        
        print(f"Company: {info.get('longName', 'N/A')}")
        print(f"Current Price: ${info.get('currentPrice', 'N/A')}")
        
        # Test PE ratio extraction
        pe_ratio = _extract_pe_ratio(info)
        print(f"PE Ratio: {pe_ratio}")
        
        # Test dividend yield extraction
        dividend_yield = _extract_dividend_yield(info)
        print(f"Dividend Yield: {dividend_yield}%")
        
        # Show raw values for debugging
        print(f"Raw trailingPE: {info.get('trailingPE')}")
        print(f"Raw dividendYield: {info.get('dividendYield')}")
        
        return True
        
    except Exception as e:
        print(f"Error testing {symbol}: {e}")
        return False

def main():
    """Test multiple stocks"""
    test_symbols = ['AAPL', 'MSFT', 'JNJ', 'KO', 'PG']
    
    print("Testing PE Ratio and Dividend Yield Extraction")
    print("=" * 50)
    
    success_count = 0
    for symbol in test_symbols:
        if test_stock_data(symbol):
            success_count += 1
    
    print(f"\nResults: {success_count}/{len(test_symbols)} stocks processed successfully")

if __name__ == "__main__":
    main()