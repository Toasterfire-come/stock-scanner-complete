"""
Stock Data Utility Functions
Provides helper functions for stock data processing and calculations
"""

from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


def compute_market_cap_fallback(current_price, shares_available):
    """
    Calculate market capitalization as a fallback when not directly available.

    Args:
        current_price (Decimal): Current stock price
        shares_available (int): Number of shares outstanding

    Returns:
        int: Market capitalization or None if calculation not possible
    """
    try:
        if current_price and shares_available:
            # Convert to float for calculation, then to int for market cap
            price_float = float(current_price)
            market_cap = int(price_float * shares_available)
            return market_cap
        return None
    except (ValueError, TypeError, AttributeError) as e:
        logger.warning(f"Failed to compute market cap fallback: {e}")
        return None
