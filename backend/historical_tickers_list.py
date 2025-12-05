#!/usr/bin/env python3
"""
Comprehensive Historical Data Ticker List
==========================================
Includes major indices, futures, and all NYSE/NASDAQ stocks for backtesting
"""

# Major US Indices
MAJOR_INDICES = [
    # S&P Indices
    "^GSPC",    # S&P 500
    "^SP400",   # S&P 400 Mid Cap
    "^SP600",   # S&P 600 Small Cap

    # Dow Jones Indices
    "^DJI",     # Dow Jones Industrial Average
    "^DJT",     # Dow Jones Transportation
    "^DJU",     # Dow Jones Utilities

    # NASDAQ Indices
    "^IXIC",    # NASDAQ Composite
    "^NDX",     # NASDAQ-100

    # Russell Indices
    "^RUT",     # Russell 2000
    "^RUI",     # Russell 1000
    "^RUA",     # Russell 3000

    # Volatility Index
    "^VIX",     # CBOE Volatility Index
]

# Major International Indices
INTERNATIONAL_INDICES = [
    # Europe
    "^FTSE",    # FTSE 100 (UK)
    "^GDAXI",   # DAX (Germany)
    "^FCHI",    # CAC 40 (France)

    # Asia Pacific
    "^N225",    # Nikkei 225 (Japan)
    "^HSI",     # Hang Seng (Hong Kong)
    "000001.SS", # SSE Composite (China)
    "^AXJO",    # ASX 200 (Australia)
]

# Major Commodity Futures
COMMODITY_FUTURES = [
    # Energy
    "CL=F",     # Crude Oil WTI
    "BZ=F",     # Brent Crude Oil
    "NG=F",     # Natural Gas
    "RB=F",     # RBOB Gasoline
    "HO=F",     # Heating Oil

    # Metals
    "GC=F",     # Gold
    "SI=F",     # Silver
    "PL=F",     # Platinum
    "PA=F",     # Palladium
    "HG=F",     # Copper

    # Agriculture
    "ZC=F",     # Corn
    "ZW=F",     # Wheat
    "ZS=F",     # Soybeans
    "ZO=F",     # Oats
    "KC=F",     # Coffee
    "CT=F",     # Cotton
    "SB=F",     # Sugar
    "CC=F",     # Cocoa
]

# Currency Futures
CURRENCY_FUTURES = [
    "EURUSD=X", # Euro/USD
    "GBPUSD=X", # British Pound/USD
    "JPYUSD=X", # Japanese Yen/USD
    "AUDUSD=X", # Australian Dollar/USD
    "CADUSD=X", # Canadian Dollar/USD
    "CHFUSD=X", # Swiss Franc/USD
    "BTCUSD=X", # Bitcoin/USD
    "ETHUSD=X", # Ethereum/USD
]

# Bond Futures
BOND_FUTURES = [
    "ZB=F",     # 30-Year Treasury Bond
    "ZN=F",     # 10-Year Treasury Note
    "ZF=F",     # 5-Year Treasury Note
    "ZT=F",     # 2-Year Treasury Note
]

# Popular ETFs (for backtesting strategies)
POPULAR_ETFS = [
    # Broad Market
    "SPY",      # S&P 500 ETF
    "QQQ",      # NASDAQ-100 ETF
    "IWM",      # Russell 2000 ETF
    "DIA",      # Dow Jones ETF
    "VTI",      # Total Stock Market ETF

    # Sector ETFs
    "XLF",      # Financial
    "XLE",      # Energy
    "XLK",      # Technology
    "XLV",      # Healthcare
    "XLI",      # Industrial
    "XLP",      # Consumer Staples
    "XLY",      # Consumer Discretionary
    "XLU",      # Utilities
    "XLB",      # Materials
    "XLRE",     # Real Estate

    # International
    "EFA",      # EAFE
    "EEM",      # Emerging Markets
    "VWO",      # Vanguard Emerging Markets

    # Bonds
    "TLT",      # 20+ Year Treasury
    "AGG",      # Aggregate Bond
    "LQD",      # Investment Grade Corporate
    "HYG",      # High Yield Corporate

    # Commodities
    "GLD",      # Gold
    "SLV",      # Silver
    "USO",      # Oil
    "UNG",      # Natural Gas

    # Volatility
    "VXX",      # Short-term VIX Futures
    "UVXY",     # Ultra VIX Short-term
]

# Function to get all tickers dynamically
def get_all_stock_tickers():
    """
    Load all NYSE and NASDAQ tickers from the combined ticker files.
    This uses the same data files as the other scanners.
    """
    from pathlib import Path
    import importlib.util

    BASE_DIR = Path(__file__).resolve().parent
    combined_dir = BASE_DIR / "data" / "combined"

    ticker_files = sorted(combined_dir.glob("combined_tickers_*.py"))
    if not ticker_files:
        return []

    latest_file = ticker_files[-1]
    spec = importlib.util.spec_from_file_location("combined_tickers", latest_file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    return module.COMBINED_TICKERS

# Combine all tickers for historical data fetching
def get_all_historical_tickers():
    """Get comprehensive list of all tickers for historical data collection"""
    all_tickers = []

    # Add indices
    all_tickers.extend(MAJOR_INDICES)
    all_tickers.extend(INTERNATIONAL_INDICES)

    # Add futures
    all_tickers.extend(COMMODITY_FUTURES)
    all_tickers.extend(CURRENCY_FUTURES)
    all_tickers.extend(BOND_FUTURES)

    # Add ETFs
    all_tickers.extend(POPULAR_ETFS)

    # Add all stocks
    stock_tickers = get_all_stock_tickers()
    all_tickers.extend(stock_tickers)

    # Remove duplicates while preserving order
    seen = set()
    unique_tickers = []
    for ticker in all_tickers:
        if ticker not in seen:
            seen.add(ticker)
            unique_tickers.append(ticker)

    return unique_tickers

if __name__ == "__main__":
    all_tickers = get_all_historical_tickers()
    print(f"Total tickers for historical data: {len(all_tickers)}")
    print(f"  - Major indices: {len(MAJOR_INDICES)}")
    print(f"  - International indices: {len(INTERNATIONAL_INDICES)}")
    print(f"  - Commodity futures: {len(COMMODITY_FUTURES)}")
    print(f"  - Currency futures: {len(CURRENCY_FUTURES)}")
    print(f"  - Bond futures: {len(BOND_FUTURES)}")
    print(f"  - Popular ETFs: {len(POPULAR_ETFS)}")
    print(f"  - Individual stocks: {len(get_all_stock_tickers())}")
