#!/usr/bin/env python3
"""
Comprehensive Ticker List Generator
====================================

Generates a complete list of tradeable instruments from yfinance:
- NYSE and NASDAQ stocks
- Major futures contracts
- Major indices

This list can be used for backtesting and historical data collection.
"""

import os
import sys
import json
import logging
from typing import List, Dict, Set
from datetime import datetime

logger = logging.getLogger(__name__)

# =====================================================
# TICKER CATEGORIES
# =====================================================

class TickerCategories:
    """Comprehensive list of tickers organized by category"""

    # Major US Indices
    INDICES = [
        # US Indices
        '^GSPC',    # S&P 500
        '^DJI',     # Dow Jones Industrial Average
        '^IXIC',    # NASDAQ Composite
        '^RUT',     # Russell 2000
        '^VIX',     # CBOE Volatility Index
        '^NYA',     # NYSE Composite
        '^XAX',     # NYSE AMEX Composite

        # Sector Indices
        '^GSPC',    # S&P 500
        'XLF',      # Financial Select Sector SPDR
        'XLE',      # Energy Select Sector SPDR
        'XLV',      # Health Care Select Sector SPDR
        'XLI',      # Industrial Select Sector SPDR
        'XLK',      # Technology Select Sector SPDR
        'XLP',      # Consumer Staples Select Sector SPDR
        'XLY',      # Consumer Discretionary Select Sector SPDR
        'XLU',      # Utilities Select Sector SPDR
        'XLB',      # Materials Select Sector SPDR
        'XLRE',     # Real Estate Select Sector SPDR
        'XLC',      # Communication Services Select Sector SPDR

        # Global Indices
        '^FTSE',    # FTSE 100
        '^GDAXI',   # DAX
        '^FCHI',    # CAC 40
        '^N225',    # Nikkei 225
        '^HSI',     # Hang Seng
    ]

    # Futures Contracts (use continuous contracts)
    FUTURES = [
        # Equity Index Futures
        'ES=F',     # E-mini S&P 500
        'NQ=F',     # E-mini NASDAQ-100
        'YM=F',     # E-mini Dow Jones
        'RTY=F',    # E-mini Russell 2000

        # Treasury Futures
        'ZB=F',     # 30-Year T-Bond
        'ZN=F',     # 10-Year T-Note
        'ZF=F',     # 5-Year T-Note
        'ZT=F',     # 2-Year T-Note

        # Currency Futures
        'EUR=F',    # Euro FX
        'GBP=F',    # British Pound
        'JPY=F',    # Japanese Yen
        'CAD=F',    # Canadian Dollar
        'AUD=F',    # Australian Dollar
        'CHF=F',    # Swiss Franc

        # Commodity Futures
        'GC=F',     # Gold
        'SI=F',     # Silver
        'PL=F',     # Platinum
        'HG=F',     # Copper
        'CL=F',     # Crude Oil WTI
        'BZ=F',     # Brent Crude Oil
        'NG=F',     # Natural Gas
        'RB=F',     # RBOB Gasoline
        'HO=F',     # Heating Oil

        # Agricultural Futures
        'ZC=F',     # Corn
        'ZS=F',     # Soybeans
        'ZW=F',     # Wheat
        'KC=F',     # Coffee
        'SB=F',     # Sugar
        'CC=F',     # Cocoa
        'CT=F',     # Cotton
        'LBS=F',    # Lumber

        # Livestock Futures
        'LE=F',     # Live Cattle
        'GF=F',     # Feeder Cattle
        'HE=F',     # Lean Hogs

        # Volatility Futures
        'VX=F',     # VIX Futures
    ]

    # Major ETFs (often used as proxies)
    MAJOR_ETFS = [
        # Equity ETFs
        'SPY',      # SPDR S&P 500
        'QQQ',      # Invesco QQQ (NASDAQ-100)
        'DIA',      # SPDR Dow Jones
        'IWM',      # iShares Russell 2000
        'VTI',      # Vanguard Total Stock Market

        # Bond ETFs
        'TLT',      # iShares 20+ Year Treasury
        'IEF',      # iShares 7-10 Year Treasury
        'SHY',      # iShares 1-3 Year Treasury
        'AGG',      # iShares Core US Aggregate Bond

        # Gold ETFs
        'GLD',      # SPDR Gold Shares
        'SLV',      # iShares Silver Trust

        # Oil ETFs
        'USO',      # United States Oil Fund
        'UNG',      # United States Natural Gas Fund
    ]

# =====================================================
# TICKER LIST GENERATOR
# =====================================================

class TickerListGenerator:
    """Generate comprehensive ticker lists"""

    def __init__(self):
        self.stocks: List[str] = []
        self.futures: List[str] = []
        self.indices: List[str] = []
        self.etfs: List[str] = []

    def load_nyse_nasdaq_stocks(self, file_path: str = None) -> List[str]:
        """
        Load NYSE and NASDAQ stocks from existing ticker files

        Falls back to loading from stock_retrieval if available
        """
        stocks = []

        try:
            # Try to use existing stock retrieval system
            sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

            from stock_retrieval.config import StockRetrievalConfig
            from stock_retrieval.ticker_loader import load_combined_tickers

            logger.info("Loading tickers from stock_retrieval system...")
            config = StockRetrievalConfig()
            result = load_combined_tickers(config)
            stocks = result.tickers

            logger.info(f"Loaded {len(stocks)} stocks from stock_retrieval")

        except Exception as e:
            logger.warning(f"Failed to load from stock_retrieval: {e}")

            # Fallback: Try to load from JSON files
            try:
                # Check for existing ticker files
                possible_files = [
                    'stock_retrieval/tickers/nyse_tickers.json',
                    'stock_retrieval/tickers/nasdaq_tickers.json',
                    'tickers.json'
                ]

                for file in possible_files:
                    file_path = os.path.join(os.path.dirname(__file__), file)
                    if os.path.exists(file_path):
                        with open(file_path, 'r') as f:
                            data = json.load(f)
                            if isinstance(data, list):
                                stocks.extend(data)
                            elif isinstance(data, dict):
                                stocks.extend(data.get('tickers', []))

                logger.info(f"Loaded {len(stocks)} stocks from JSON files")

            except Exception as e2:
                logger.error(f"Failed to load tickers from files: {e2}")
                logger.warning("Will only use futures and indices")

        return list(set(stocks))  # Remove duplicates

    def generate_comprehensive_list(self) -> Dict[str, List[str]]:
        """Generate comprehensive list of all tradeable instruments"""

        logger.info("=" * 70)
        logger.info("GENERATING COMPREHENSIVE TICKER LIST")
        logger.info("=" * 70)

        # Load stocks
        logger.info("\n1. Loading NYSE/NASDAQ stocks...")
        self.stocks = self.load_nyse_nasdaq_stocks()
        logger.info(f"   Loaded: {len(self.stocks)} stocks")

        # Add futures
        logger.info("\n2. Adding futures contracts...")
        self.futures = TickerCategories.FUTURES
        logger.info(f"   Added: {len(self.futures)} futures")

        # Add indices
        logger.info("\n3. Adding indices...")
        self.indices = list(set(TickerCategories.INDICES))  # Remove duplicates
        logger.info(f"   Added: {len(self.indices)} indices")

        # Add major ETFs
        logger.info("\n4. Adding major ETFs...")
        self.etfs = TickerCategories.MAJOR_ETFS
        logger.info(f"   Added: {len(self.etfs)} ETFs")

        # Combine all
        all_tickers = list(set(
            self.stocks + self.futures + self.indices + self.etfs
        ))

        logger.info("\n" + "=" * 70)
        logger.info("SUMMARY")
        logger.info("=" * 70)
        logger.info(f"Stocks:   {len(self.stocks):>6}")
        logger.info(f"Futures:  {len(self.futures):>6}")
        logger.info(f"Indices:  {len(self.indices):>6}")
        logger.info(f"ETFs:     {len(self.etfs):>6}")
        logger.info(f"{'=' * 20}")
        logger.info(f"TOTAL:    {len(all_tickers):>6}")
        logger.info("=" * 70)

        return {
            'stocks': self.stocks,
            'futures': self.futures,
            'indices': self.indices,
            'etfs': self.etfs,
            'all': all_tickers
        }

    def save_to_file(self, output_file: str = None):
        """Save ticker lists to JSON file"""

        if output_file is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f'comprehensive_tickers_{timestamp}.json'

        ticker_data = self.generate_comprehensive_list()

        # Add metadata
        ticker_data['metadata'] = {
            'generated_at': datetime.now().isoformat(),
            'total_tickers': len(ticker_data['all']),
            'breakdown': {
                'stocks': len(ticker_data['stocks']),
                'futures': len(ticker_data['futures']),
                'indices': len(ticker_data['indices']),
                'etfs': len(ticker_data['etfs'])
            }
        }

        with open(output_file, 'w') as f:
            json.dump(ticker_data, f, indent=2)

        logger.info(f"\nTicker list saved to: {output_file}")

        return output_file

# =====================================================
# CONVENIENCE FUNCTIONS
# =====================================================

def load_comprehensive_tickers() -> Dict[str, List[str]]:
    """Load comprehensive ticker list"""
    generator = TickerListGenerator()
    return generator.generate_comprehensive_list()

def get_all_tickers() -> List[str]:
    """Get flat list of all tickers"""
    ticker_data = load_comprehensive_tickers()
    return ticker_data['all']

def get_tickers_by_category(category: str) -> List[str]:
    """Get tickers for specific category"""
    ticker_data = load_comprehensive_tickers()
    return ticker_data.get(category, [])

# =====================================================
# MAIN
# =====================================================

def main():
    """Generate and save comprehensive ticker list"""

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s'
    )

    generator = TickerListGenerator()
    output_file = generator.save_to_file()

    logger.info("\n" + "=" * 70)
    logger.info("TICKER LIST GENERATION COMPLETE")
    logger.info("=" * 70)
    logger.info(f"Output file: {output_file}")
    logger.info("")
    logger.info("You can now use this list for:")
    logger.info("  - Historical data collection")
    logger.info("  - Backtesting")
    logger.info("  - Real-time monitoring")
    logger.info("=" * 70)

if __name__ == "__main__":
    main()
