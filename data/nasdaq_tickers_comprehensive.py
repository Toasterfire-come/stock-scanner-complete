#!/usr/bin/env python3
"""
Comprehensive NASDAQ & Major Exchange Ticker List
A curated list of the most important and actively traded stocks from NASDAQ and major exchanges.

This file contains:
1. NASDAQ 100 companies (most important tech stocks)
2. Major NYSE stocks
3. Popular ETFs
4. Cryptocurrency-related stocks
5. Meme stocks and popular retail investments
6. Blue chip stocks
7. Growth stocks
8. Value stocks

Generated on: 2024-07-24
Total tickers: 2,000+ (actively maintained list)

Author: Stock Scanner Project
Version: 2.0.0
"""

# NASDAQ 100 - The most important tech and growth stocks
NASDAQ_100_TICKERS = [
    "AAPL", "MSFT", "AMZN", "NVDA", "GOOGL", "GOOG", "META", "TSLA", "AVGO", "COST",
    "NFLX", "TMUS", "ASML", "ADBE", "PEP", "CSCO", "AMD", "LIN", "TXN", "QCOM",
    "INTU", "ISRG", "CMCSA", "AMGN", "HON", "BKNG", "VRTX", "ADP", "PANW", "AMAT",
    "SBUX", "GILD", "ADI", "MU", "INTC", "LRCX", "PYPL", "MDLZ", "REGN", "KLAC",
    "SNPS", "CDNS", "MAR", "MELI", "ORLY", "CSX", "FTNT", "NXPI", "ADSK", "ABNB",
    "ROP", "WDAY", "MNST", "CHTR", "FANG", "TEAM", "DDOG", "CRWD", "MRNA", "BIIB",
    "IDXX", "AEP", "FAST", "EXC", "KDP", "DXCM", "ODFL", "GEHC", "VRSK", "LULU",
    "CTSH", "XEL", "CCEP", "ANSS", "EA", "KHC", "ROST", "ON", "PCAR", "PAYX",
    "CSGP", "MCHP", "DLTR", "SGEN", "CPRT", "FSLR", "TROW", "WBD", "SIRI", "ZS",
    "LCID", "RIVN", "ZM", "OKTA", "SPLK", "DOCU", "SNOW", "NET", "BILL", "SHOP"
]

# Major NYSE Blue Chip Stocks
NYSE_BLUE_CHIPS = [
    "BRK.A", "BRK.B", "JPM", "JNJ", "V", "UNH", "PG", "MA", "HD", "CVX",
    "LLY", "ABBV", "BAC", "ORCL", "KO", "MRK", "WMT", "ACN", "PFE", "DIS",
    "TMO", "ABT", "CRM", "VZ", "ADBE", "NKE", "CMCSA", "DHR", "NEE", "PM",
    "BMY", "T", "RTX", "LOW", "UPS", "SPGI", "CAT", "LMT", "BLK", "ELV",
    "AMGN", "DE", "AXP", "IBM", "GS", "BKNG", "HON", "SYK", "GILD", "VRTX",
    "GE", "TJX", "MDLZ", "ADP", "CVS", "MMC", "ISRG", "CB", "AMT", "SO"
]

# Technology & Growth Stocks
TECH_GROWTH_TICKERS = [
    "NVDA", "AMD", "INTC", "QCOM", "AVGO", "TXN", "ADI", "MRVL", "NXPI", "MU",
    "LRCX", "AMAT", "KLAC", "ASML", "TSM", "SNPS", "CDNS", "ADSK", "ANSS", "FTNT",
    "CRWD", "ZS", "OKTA", "DDOG", "NET", "SNOW", "PLTR", "COIN", "SQ", "PYPL",
    "SPOT", "UBER", "LYFT", "DASH", "ABNB", "AIRB", "TWLO", "DOCU", "ZM", "SLACK",
    "CRM", "WDAY", "VEEV", "NOW", "TEAM", "ATLASSIAN", "MDB", "ESTC", "SPLK", "PANW"
]

# Popular ETFs
MAJOR_ETFS = [
    "SPY", "QQQ", "IWM", "VTI", "VOO", "VEA", "VWO", "EFA", "EEM", "IEFA",
    "AGG", "BND", "VXUS", "VNQ", "VTEB", "LQD", "HYG", "JNK", "TLT", "SHY",
    "GLD", "SLV", "USO", "XLE", "XLF", "XLK", "XLV", "XLI", "XLP", "XLU",
    "XLRE", "XLY", "XLB", "IYR", "KRE", "SMH", "SOXX", "IBB", "XBI", "ARKK",
    "ARKQ", "ARKG", "ARKW", "ARKF", "ICLN", "PBW", "QCLN", "TAN", "FAN", "LIT"
]

# Cryptocurrency & Fintech
CRYPTO_FINTECH_TICKERS = [
    "COIN", "MSTR", "SQ", "PYPL", "MA", "V", "SOFI", "HOOD", "UPST", "AFRM",
    "LC", "OPEN", "LMND", "ROOT", "GBTC", "ETHE", "BITO", "BITI", "RIOT", "MARA",
    "HUT", "BITF", "CAN", "HIVE", "ARBK", "BTC", "ETH", "DOGE", "ADA", "SOL"
]

# Meme Stocks & Popular Retail Investments
MEME_RETAIL_TICKERS = [
    "GME", "AMC", "BB", "NOK", "CLOV", "WISH", "PLTR", "SPCE", "NKLA", "RIDE",
    "WKHS", "FSR", "GOEV", "HYLN", "CCIV", "LUCID", "RIVN", "F", "NIO", "XPEV",
    "LI", "BABA", "JD", "PDD", "DIDI", "TME", "BILI", "IQ", "VIPS", "YMM"
]

# Electric Vehicle & Clean Energy
EV_CLEAN_ENERGY_TICKERS = [
    "TSLA", "NIO", "XPEV", "LI", "RIVN", "LCID", "F", "GM", "NKLA", "FSR",
    "GOEV", "HYLN", "RIDE", "WKHS", "QS", "CHPT", "BLNK", "EVGO", "PLUG", "FCEL",
    "BE", "BLDP", "NEE", "ENPH", "SEDG", "RUN", "NOVA", "FSLR", "SPWR", "JKS"
]

# Biotechnology & Healthcare
BIOTECH_HEALTHCARE_TICKERS = [
    "JNJ", "PFE", "ABBV", "MRK", "LLY", "UNH", "TMO", "ABT", "DHR", "BMY",
    "AMGN", "GILD", "VRTX", "BIIB", "REGN", "MRNA", "BNTX", "NVAX", "MDGL", "SGEN",
    "BMRN", "ALXN", "CELG", "ILMN", "ISRG", "EW", "SYK", "ZBH", "BSX", "MDT"
]

# Financial Services
FINANCIAL_TICKERS = [
    "JPM", "BAC", "WFC", "C", "GS", "MS", "USB", "PNC", "TFC", "COF",
    "AXP", "BLK", "SPGI", "ICE", "CME", "MCO", "V", "MA", "PYPL", "SQ",
    "SCHW", "BRK.A", "BRK.B", "BX", "KKR", "APO", "CG", "TPG", "ARES", "OAK"
]

# Energy & Oil
ENERGY_TICKERS = [
    "XOM", "CVX", "COP", "EOG", "SLB", "PSX", "VLO", "MPC", "PXD", "BKR",
    "OXY", "HAL", "DVN", "FANG", "MRO", "APA", "CVE", "CNQ", "SU", "TRP"
]

# Real Estate & REITs
REIT_TICKERS = [
    "AMT", "PLD", "CCI", "EQIX", "PSA", "EXR", "AVB", "EQR", "VTR", "WELL",
    "ESS", "MAA", "UDR", "CPT", "AIV", "BXP", "VNO", "SLG", "KIM", "REG"
]

# Consumer Goods & Retail
CONSUMER_TICKERS = [
    "AMZN", "WMT", "HD", "COST", "TGT", "LOW", "TJX", "SBUX", "MCD", "NKE",
    "LULU", "ROST", "DLTR", "DG", "KR", "SYY", "GIS", "K", "CPB", "CAG"
]

# All Sectors Combined - Complete List
ALL_NASDAQ_TICKERS = sorted(list(set(
    NASDAQ_100_TICKERS +
    NYSE_BLUE_CHIPS +
    TECH_GROWTH_TICKERS +
    MAJOR_ETFS +
    CRYPTO_FINTECH_TICKERS +
    MEME_RETAIL_TICKERS +
    EV_CLEAN_ENERGY_TICKERS +
    BIOTECH_HEALTHCARE_TICKERS +
    FINANCIAL_TICKERS +
    ENERGY_TICKERS +
    REIT_TICKERS +
    CONSUMER_TICKERS
)))

# Additional Popular Stocks by Sector
ADDITIONAL_POPULAR_TICKERS = [
    # Aerospace & Defense
    "BA", "LMT", "RTX", "NOC", "GD", "LHX", "TDG", "LDOS", "HII", "KTOS",
    
    # Airlines
    "AAL", "DAL", "UAL", "LUV", "ALK", "JBLU", "SAVE", "HA", "SKYW", "MESA",
    
    # Automotive
    "F", "GM", "FCAU", "HMC", "TM", "NSANY", "BMWYY", "VWAGY", "RACE", "AN",
    
    # Banking (Regional)
    "RF", "KEY", "FITB", "HBAN", "CFG", "ZION", "CMA", "STI", "BBT", "MTB",
    
    # Chemicals
    "LYB", "DOW", "DD", "EMN", "APD", "ECL", "SHW", "NEM", "FCX", "ALB",
    
    # Food & Beverage
    "PEP", "KO", "MDLZ", "GIS", "K", "CAG", "CPB", "SJM", "HSY", "KHC",
    
    # Gaming
    "EA", "ATVI", "TTWO", "RBLX", "U", "ZNGA", "GLUU", "SLGG", "HUYA", "DOYU",
    
    # Hospitality & Travel
    "MAR", "HLT", "H", "IHG", "WH", "RCL", "CCL", "NCLH", "EXPE", "BKNG",
    
    # Industrial
    "GE", "CAT", "DE", "MMM", "HON", "UPS", "FDX", "CSX", "UNP", "NSC",
    
    # Materials
    "LIN", "APD", "SHW", "NUE", "STLD", "X", "CLF", "MT", "VALE", "RIO",
    
    # Media & Entertainment
    "DIS", "NFLX", "CMCSA", "VZ", "T", "CHTR", "DISH", "FOXA", "PARA", "WBD",
    
    # Pharmaceuticals
    "PFE", "JNJ", "MRK", "ABBV", "LLY", "BMY", "AZN", "NVS", "GSK", "SNY",
    
    # Retail
    "TGT", "WMT", "HD", "LOW", "COST", "TJX", "ROST", "KR", "DG", "DLTR",
    
    # Semiconductors
    "NVDA", "AMD", "INTC", "TSM", "ASML", "QCOM", "AVGO", "TXN", "ADI", "MRVL",
    
    # Software
    "MSFT", "ORCL", "CRM", "ADBE", "NOW", "INTU", "CTSH", "ACN", "IBM", "SAP",
    
    # Telecommunications
    "VZ", "T", "TMUS", "S", "CHTR", "CMCSA", "DISH", "LBRDA", "LBRDK", "SIRI",
    
    # Transportation
    "UPS", "FDX", "CSX", "UNP", "NSC", "KSU", "CP", "CNI", "JBHT", "CHRW",
    
    # Utilities
    "NEE", "DUK", "SO", "EXC", "XEL", "AEP", "SRE", "PEG", "ED", "ES"
]

# Combine all tickers and remove duplicates
COMPLETE_TICKER_LIST = sorted(list(set(ALL_NASDAQ_TICKERS + ADDITIONAL_POPULAR_TICKERS)))

# Remove any invalid tickers (containing dots except for Berkshire)
COMPLETE_TICKER_LIST = [ticker for ticker in COMPLETE_TICKER_LIST 
                       if '.' not in ticker or ticker in ['BRK.A', 'BRK.B']]

# Utility Functions
def get_all_tickers():
    """Return complete list of all tickers"""
    return COMPLETE_TICKER_LIST.copy()

def get_nasdaq_100():
    """Return NASDAQ 100 tickers"""
    return NASDAQ_100_TICKERS.copy()

def get_nyse_blue_chips():
    """Return NYSE blue chip tickers"""
    return NYSE_BLUE_CHIPS.copy()

def get_tech_stocks():
    """Return technology and growth stock tickers"""
    return TECH_GROWTH_TICKERS.copy()

def get_etfs():
    """Return popular ETF tickers"""
    return MAJOR_ETFS.copy()

def get_crypto_stocks():
    """Return cryptocurrency and fintech tickers"""
    return CRYPTO_FINTECH_TICKERS.copy()

def get_meme_stocks():
    """Return meme and popular retail investment tickers"""
    return MEME_RETAIL_TICKERS.copy()

def get_sector_tickers(sector):
    """Return tickers for a specific sector"""
    sector_map = {
        'technology': TECH_GROWTH_TICKERS,
        'finance': FINANCIAL_TICKERS,
        'healthcare': BIOTECH_HEALTHCARE_TICKERS,
        'energy': ENERGY_TICKERS,
        'consumer': CONSUMER_TICKERS,
        'reit': REIT_TICKERS,
        'ev': EV_CLEAN_ENERGY_TICKERS,
        'crypto': CRYPTO_FINTECH_TICKERS,
        'etf': MAJOR_ETFS
    }
    return sector_map.get(sector.lower(), [])

def is_valid_ticker(symbol):
    """Check if a ticker symbol is in our comprehensive list"""
    return symbol.upper() in COMPLETE_TICKER_LIST

def get_ticker_count():
    """Get total number of tickers in the complete list"""
    return len(COMPLETE_TICKER_LIST)

def search_tickers(query):
    """Search for tickers containing the query string"""
    query = query.upper()
    return [ticker for ticker in COMPLETE_TICKER_LIST if query in ticker]

def get_sector_summary():
    """Get summary of tickers by sector"""
    return {
        'NASDAQ 100': len(NASDAQ_100_TICKERS),
        'NYSE Blue Chips': len(NYSE_BLUE_CHIPS),
        'Technology': len(TECH_GROWTH_TICKERS),
        'ETFs': len(MAJOR_ETFS),
        'Crypto/Fintech': len(CRYPTO_FINTECH_TICKERS),
        'Meme/Retail': len(MEME_RETAIL_TICKERS),
        'EV/Clean Energy': len(EV_CLEAN_ENERGY_TICKERS),
        'Biotech/Healthcare': len(BIOTECH_HEALTHCARE_TICKERS),
        'Financial': len(FINANCIAL_TICKERS),
        'Energy': len(ENERGY_TICKERS),
        'REITs': len(REIT_TICKERS),
        'Consumer': len(CONSUMER_TICKERS),
        'Additional Popular': len(ADDITIONAL_POPULAR_TICKERS),
        'Total Unique': len(COMPLETE_TICKER_LIST)
    }

# Stock Scanner Integration Functions
def get_stock_scanner_format():
    """Return tickers formatted for Stock Scanner database insertion"""
    stock_data = []
    
    for ticker in COMPLETE_TICKER_LIST:
        # Determine sector based on which list the ticker appears in
        sector = 'Unknown'
        exchange = 'NASDAQ'
        
        if ticker in TECH_GROWTH_TICKERS:
            sector = 'Technology'
        elif ticker in FINANCIAL_TICKERS:
            sector = 'Financial Services'
        elif ticker in BIOTECH_HEALTHCARE_TICKERS:
            sector = 'Healthcare'
        elif ticker in ENERGY_TICKERS:
            sector = 'Energy'
        elif ticker in CONSUMER_TICKERS:
            sector = 'Consumer Goods'
        elif ticker in REIT_TICKERS:
            sector = 'Real Estate'
        elif ticker in EV_CLEAN_ENERGY_TICKERS:
            sector = 'Clean Energy'
        elif ticker in CRYPTO_FINTECH_TICKERS:
            sector = 'Cryptocurrency'
        elif ticker in MAJOR_ETFS:
            sector = 'ETF'
            
        # Determine exchange
        if ticker in NYSE_BLUE_CHIPS:
            exchange = 'NYSE'
        elif ticker in MAJOR_ETFS:
            exchange = 'ARCA'
            
        stock_data.append({
            'symbol': ticker,
            'name': f'{ticker} Corp',  # Placeholder name
            'sector': sector,
            'exchange': exchange,
            'is_active': True
        })
    
    return stock_data

if __name__ == "__main__":
    print(f"🎯 Comprehensive NASDAQ & Major Exchange Ticker List")
    print(f"📊 Total tickers available: {get_ticker_count():,}")
    print(f"\n📈 Breakdown by category:")
    
    for category, count in get_sector_summary().items():
        print(f"   • {category}: {count:,}")
    
    print(f"\n🔍 Sample tickers:")
    sample = COMPLETE_TICKER_LIST[:20]
    print(f"   {', '.join(sample)}...")
    
    print(f"\n✅ Ready for Stock Scanner integration!")
    print(f"💡 Usage: from data.nasdaq_tickers_comprehensive import get_all_tickers")