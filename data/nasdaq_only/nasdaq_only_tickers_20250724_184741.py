#!/usr/bin/env python3
"""
NASDAQ-Only Ticker List
Generated on: 2025-07-24 18:47:41
Total NASDAQ tickers: 146

Source: NASDAQ FTP - nasdaqlisted.txt ONLY
Exchange: NASDAQ ONLY (excludes NYSE, ARCA, BATS, etc.)

This file contains ONLY NASDAQ-listed securities.
"""

# NASDAQ-only ticker list (146 symbols)
NASDAQ_ONLY_TICKERS = [
"AAPL", "ABNB", "ADBE", "ADI", "ADP", "ADSK", "AFRM", "ALGN", "ALXN", "AMAT",
"AMD", "AMGN", "AMZN", "AVGO", "BE", "BIDU", "BIIB", "BILI", "BKNG", "BLDP",
"BMRN", "BNTX", "CCL", "CDNS", "CELG", "CHRW", "CHTR", "CMCSA", "COIN", "COST",
"CRWD", "CSCO", "CSX", "CTSH", "DDOG", "DEXC", "DISH", "DLTR", "DXCM", "ENPH",
"ENTG", "EXAS", "EXPD", "FAST", "FCEL", "FISV", "FOX", "FOXA", "FSLR", "FTNT",
"GILD", "GOOG", "GOOGL", "GRAB", "GSAT", "HON", "HOOD", "IDXX", "ILMN", "INCY",
"INTC", "INTU", "IRDM", "ISRG", "JD", "KLAC", "LBTYA", "LBTYK", "LC", "LCID",
"LI", "LRCX", "LULU", "MAR", "MCHP", "MDLZ", "MELI", "META", "MNST", "MPWR",
"MRNA", "MRVL", "MSFT", "MTSI", "NCLH", "NET", "NFLX", "NIO", "NOVA", "NU",
"NVDA", "NWS", "NWSA", "NXPI", "NYT", "OKTA", "ON", "ORLY", "PAGS", "PARA",
"PATH", "PAYX", "PDD", "PEP", "PLTR", "PLUG", "PYPL", "QCOM", "QRVO", "RBLX",
"REGN", "RIVN", "ROKU", "ROST", "RUN", "SBUX", "SE", "SEDG", "SHOP", "SIRI",
"SNOW", "SNPS", "SOFI", "SQ", "SWKS", "T", "TEAM", "TECH", "TER", "TEVA",
"TME", "TMUS", "TSLA", "TXN", "U", "ULTA", "UPST", "VRTX", "VTRS", "VZ",
"WB", "WBD", "WDAY", "XPEV", "ZM", "ZS"
]


# Statistics
TOTAL_NASDAQ_TICKERS = 146
EXCHANGE = "NASDAQ"
GENERATION_DATE = "2025-07-24 18:47:41"

def get_nasdaq_only_tickers():
"""Return NASDAQ-only ticker symbols"""
return NASDAQ_ONLY_TICKERS.copy()

def get_nasdaq_ticker_count():
"""Get total number of NASDAQ tickers"""
return TOTAL_NASDAQ_TICKERS

def is_nasdaq_ticker(symbol):
"""Check if a ticker symbol is NASDAQ-listed"""
return symbol.upper() in NASDAQ_ONLY_TICKERS

def search_nasdaq_tickers(query):
"""Search for NASDAQ tickers containing the query string"""
query = query.upper()
return [ticker for ticker in NASDAQ_ONLY_TICKERS if query in ticker]

def get_nasdaq_statistics():
"""Get NASDAQ generation statistics"""
return {
'total_tickers': TOTAL_NASDAQ_TICKERS,
'exchange': EXCHANGE,
'generation_date': GENERATION_DATE,
'source': 'NASDAQ FTP - nasdaqlisted.txt ONLY'
}

# Sample NASDAQ tickers
SAMPLE_NASDAQ_TICKERS = NASDAQ_ONLY_TICKERS[:20]

if __name__ == "__main__":
print(f" NASDAQ-Only Ticker List")
print(f" Total NASDAQ tickers: {get_nasdaq_ticker_count():,}")
print(f" Exchange: {EXCHANGE} ONLY")
print(f" Sample: {', '.join(SAMPLE_NASDAQ_TICKERS)}")
print(f" Ready for Stock Scanner integration!")
