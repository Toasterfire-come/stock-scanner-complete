#!/usr/bin/env python3
"""
Fix Stock Company Names - Fast Version
Updates stock company names with hardcoded proper names for popular stocks
"""

import os
import sys
import django

# Setup Django environment
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stockscanner_django.settings')
django.setup()

from stocks.models import Stock

# Hardcoded proper company names for popular stocks
STOCK_NAMES = {
    # Tech Giants
    'AAPL': 'Apple Inc.',
    'MSFT': 'Microsoft Corporation',
    'GOOGL': 'Alphabet Inc.',
    'GOOG': 'Alphabet Inc.',
    'AMZN': 'Amazon.com, Inc.',
    'META': 'Meta Platforms, Inc.',
    'TSLA': 'Tesla, Inc.',
    'NVDA': 'NVIDIA Corporation',
    'AMD': 'Advanced Micro Devices, Inc.',
    'INTC': 'Intel Corporation',
    'ORCL': 'Oracle Corporation',
    'IBM': 'International Business Machines Corporation',
    'CSCO': 'Cisco Systems, Inc.',
    'ADBE': 'Adobe Inc.',
    'CRM': 'Salesforce, Inc.',
    'NFLX': 'Netflix, Inc.',
    'PYPL': 'PayPal Holdings, Inc.',
    'UBER': 'Uber Technologies, Inc.',
    'LYFT': 'Lyft, Inc.',
    'SNAP': 'Snap Inc.',
    'TWTR': 'Twitter, Inc.',
    'SQ': 'Block, Inc.',
    'SHOP': 'Shopify Inc.',
    'SPOT': 'Spotify Technology S.A.',
    'ZM': 'Zoom Video Communications, Inc.',
    'DOCU': 'DocuSign, Inc.',
    'SNOW': 'Snowflake Inc.',
    'PLTR': 'Palantir Technologies Inc.',
    'COIN': 'Coinbase Global, Inc.',

    # Financial
    'JPM': 'JPMorgan Chase & Co.',
    'BAC': 'Bank of America Corporation',
    'WFC': 'Wells Fargo & Company',
    'GS': 'The Goldman Sachs Group, Inc.',
    'MS': 'Morgan Stanley',
    'C': 'Citigroup Inc.',
    'BLK': 'BlackRock, Inc.',
    'SCHW': 'The Charles Schwab Corporation',
    'AXP': 'American Express Company',
    'V': 'Visa Inc.',
    'MA': 'Mastercard Incorporated',
    'COF': 'Capital One Financial Corporation',

    # Retail & Consumer
    'WMT': 'Walmart Inc.',
    'TGT': 'Target Corporation',
    'HD': 'The Home Depot, Inc.',
    'LOW': 'Lowe\'s Companies, Inc.',
    'COST': 'Costco Wholesale Corporation',
    'NKE': 'NIKE, Inc.',
    'SBUX': 'Starbucks Corporation',
    'MCD': 'McDonald\'s Corporation',
    'KO': 'The Coca-Cola Company',
    'PEP': 'PepsiCo, Inc.',
    'PG': 'The Procter & Gamble Company',
    'DIS': 'The Walt Disney Company',

    # Healthcare & Pharma
    'JNJ': 'Johnson & Johnson',
    'UNH': 'UnitedHealth Group Incorporated',
    'PFE': 'Pfizer Inc.',
    'ABBV': 'AbbVie Inc.',
    'TMO': 'Thermo Fisher Scientific Inc.',
    'ABT': 'Abbott Laboratories',
    'MRK': 'Merck & Co., Inc.',
    'LLY': 'Eli Lilly and Company',
    'BMY': 'Bristol-Myers Squibb Company',
    'AMGN': 'Amgen Inc.',
    'GILD': 'Gilead Sciences, Inc.',
    'CVS': 'CVS Health Corporation',
    'MDLZ': 'Mondelez International, Inc.',

    # Telecom
    'T': 'AT&T Inc.',
    'VZ': 'Verizon Communications Inc.',
    'TMUS': 'T-Mobile US, Inc.',

    # Energy
    'XOM': 'Exxon Mobil Corporation',
    'CVX': 'Chevron Corporation',
    'COP': 'ConocoPhillips',
    'SLB': 'Schlumberger Limited',

    # Industrial
    'BA': 'The Boeing Company',
    'CAT': 'Caterpillar Inc.',
    'GE': 'General Electric Company',
    'MMM': '3M Company',
    'HON': 'Honeywell International Inc.',
    'UPS': 'United Parcel Service, Inc.',
    'FDX': 'FedEx Corporation',

    # Automotive
    'F': 'Ford Motor Company',
    'GM': 'General Motors Company',
    'RIVN': 'Rivian Automotive, Inc.',
    'LCID': 'Lucid Group, Inc.',

    # Semiconductors
    'TSM': 'Taiwan Semiconductor Manufacturing Company Limited',
    'QCOM': 'QUALCOMM Incorporated',
    'AVGO': 'Broadcom Inc.',
    'TXN': 'Texas Instruments Incorporated',
    'MU': 'Micron Technology, Inc.',
    'AMAT': 'Applied Materials, Inc.',
    'LRCX': 'Lam Research Corporation',
    'KLAC': 'KLA Corporation',
    'MRVL': 'Marvell Technology, Inc.',

    # Entertainment & Media
    'CMCSA': 'Comcast Corporation',
    'PARA': 'Paramount Global',
    'WBD': 'Warner Bros. Discovery, Inc.',
    'SONY': 'Sony Group Corporation',
    'EA': 'Electronic Arts Inc.',
    'TTWO': 'Take-Two Interactive Software, Inc.',
    'ATVI': 'Activision Blizzard, Inc.',

    # E-commerce & Delivery
    'EBAY': 'eBay Inc.',
    'ETSY': 'Etsy, Inc.',
    'W': 'Wayfair Inc.',
    'DASH': 'DoorDash, Inc.',

    # Software & Cloud
    'NOW': 'ServiceNow, Inc.',
    'WDAY': 'Workday, Inc.',
    'TEAM': 'Atlassian Corporation',
    'ZS': 'Zscaler, Inc.',
    'CRWD': 'CrowdStrike Holdings, Inc.',
    'DDOG': 'Datadog, Inc.',
    'NET': 'Cloudflare, Inc.',
    'MDB': 'MongoDB, Inc.',
    'OKTA': 'Okta, Inc.',

    # Biotech
    'MRNA': 'Moderna, Inc.',
    'BNTX': 'BioNTech SE',
    'REGN': 'Regeneron Pharmaceuticals, Inc.',
    'VRTX': 'Vertex Pharmaceuticals Incorporated',
    'BIIB': 'Biogen Inc.',

    # Real Estate & Housing
    'Z': 'Zillow Group, Inc.',
    'RDFN': 'Redfin Corporation',

    # Travel & Hospitality
    'ABNB': 'Airbnb, Inc.',
    'BKNG': 'Booking Holdings Inc.',
    'EXPE': 'Expedia Group, Inc.',
    'MAR': 'Marriott International, Inc.',
    'HLT': 'Hilton Worldwide Holdings Inc.',
    'AAL': 'American Airlines Group Inc.',
    'DAL': 'Delta Air Lines, Inc.',
    'UAL': 'United Airlines Holdings, Inc.',
    'LUV': 'Southwest Airlines Co.',

    # Cannabis
    'TLRY': 'Tilray Brands, Inc.',
    'CGC': 'Canopy Growth Corporation',
    'SNDL': 'SNDL Inc.',
    'ACB': 'Aurora Cannabis Inc.',
    'CRON': 'Cronos Group Inc.',

    # Meme Stocks
    'GME': 'GameStop Corp.',
    'AMC': 'AMC Entertainment Holdings, Inc.',
    'BB': 'BlackBerry Limited',
    'NOK': 'Nokia Corporation',
    'BBBY': 'Bed Bath & Beyond Inc.',

    # Banking
    'USB': 'U.S. Bancorp',
    'PNC': 'The PNC Financial Services Group, Inc.',
    'TFC': 'Truist Financial Corporation',

    # Insurance
    'BRK.A': 'Berkshire Hathaway Inc.',
    'BRK.B': 'Berkshire Hathaway Inc.',
    'PGR': 'The Progressive Corporation',
    'ALL': 'The Allstate Corporation',
    'MET': 'MetLife, Inc.',
    'PRU': 'Prudential Financial, Inc.',

    # Utilities
    'NEE': 'NextEra Energy, Inc.',
    'DUK': 'Duke Energy Corporation',
    'SO': 'The Southern Company',
    'D': 'Dominion Energy, Inc.',

    # Retail Pharmacy
    'WBA': 'Walgreens Boots Alliance, Inc.',
    'RAD': 'Rite Aid Corporation',
}

def fix_stock_names():
    """Update stock company names with proper names"""
    updated = 0
    not_found = 0
    already_correct = 0

    print(f"Updating {len(STOCK_NAMES)} popular stocks...")
    print("=" * 60)

    for ticker, proper_name in STOCK_NAMES.items():
        try:
            stock = Stock.objects.get(ticker=ticker)
            current_name = stock.company_name or stock.name

            # Check if already correct
            if current_name == proper_name:
                already_correct += 1
                print(f"[SKIP] {ticker}: Already correct")
                continue

            # Update both fields
            stock.company_name = proper_name
            stock.name = proper_name
            stock.save(update_fields=['company_name', 'name'])
            updated += 1
            print(f"[OK] {ticker}: Updated from '{current_name}' to '{proper_name}'")

        except Stock.DoesNotExist:
            not_found += 1
            print(f"[WARN] {ticker}: Not found in database")
            continue

    print("\n" + "=" * 60)
    print(f"Update complete!")
    print(f"  Successfully updated: {updated}")
    print(f"  Already correct: {already_correct}")
    print(f"  Not found: {not_found}")
    print("=" * 60)

    return updated

if __name__ == '__main__':
    print("Stock Company Name Fixer - Fast Version")
    print("=" * 60)
    print(f"This will update {len(STOCK_NAMES)} popular stocks with proper names")
    print("=" * 60)

    # Show sample of current data
    print("\nCurrent stock names (sample):")
    sample_tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA']
    for ticker in sample_tickers:
        try:
            stock = Stock.objects.get(ticker=ticker)
            print(f"  {stock.ticker}: {stock.company_name or stock.name}")
        except Stock.DoesNotExist:
            print(f"  {ticker}: Not found")

    print("\nStarting update...")
    updated_count = fix_stock_names()

    if updated_count > 0:
        print(f"\n[SUCCESS] Updated {updated_count} stocks!")
        print("\nUpdated stock names (sample):")
        for ticker in sample_tickers:
            try:
                stock = Stock.objects.get(ticker=ticker)
                print(f"  {stock.ticker}: {stock.company_name}")
            except Stock.DoesNotExist:
                pass
