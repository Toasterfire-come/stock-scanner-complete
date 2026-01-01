"""
Sales Tax Calculation Utilities
Handles sales tax computation for subscription pricing
"""

from decimal import Decimal, ROUND_HALF_UP
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


def calculate_sales_tax(amount, tax_rate=None):
    """
    Calculate sales tax for a given amount

    Args:
        amount (Decimal or float): Base amount before tax
        tax_rate (float, optional): Tax rate (e.g., 0.07 for 7%). Defaults to settings.SALES_TAX_RATE

    Returns:
        Decimal: Sales tax amount rounded to 2 decimal places
    """
    if not settings.SALES_TAX_ENABLED:
        return Decimal('0.00')

    if tax_rate is None:
        tax_rate = settings.SALES_TAX_RATE

    try:
        amount_decimal = Decimal(str(amount))
        tax_rate_decimal = Decimal(str(tax_rate))

        # Calculate tax and round to 2 decimal places
        tax_amount = (amount_decimal * tax_rate_decimal).quantize(
            Decimal('0.01'),
            rounding=ROUND_HALF_UP
        )

        return tax_amount
    except (ValueError, TypeError) as e:
        logger.error(f"Failed to calculate sales tax: {e}")
        return Decimal('0.00')


def calculate_total_with_tax(amount, tax_rate=None):
    """
    Calculate total amount including sales tax

    Args:
        amount (Decimal or float): Base amount before tax
        tax_rate (float, optional): Tax rate (e.g., 0.07 for 7%). Defaults to settings.SALES_TAX_RATE

    Returns:
        dict: Dictionary containing subtotal, tax, and total amounts
    """
    try:
        subtotal = Decimal(str(amount))
        tax = calculate_sales_tax(amount, tax_rate)
        total = (subtotal + tax).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        return {
            'subtotal': float(subtotal),
            'tax': float(tax),
            'total': float(total),
            'tax_rate': tax_rate or settings.SALES_TAX_RATE,
            'tax_enabled': settings.SALES_TAX_ENABLED,
        }
    except (ValueError, TypeError) as e:
        logger.error(f"Failed to calculate total with tax: {e}")
        return {
            'subtotal': float(amount),
            'tax': 0.00,
            'total': float(amount),
            'tax_rate': 0.00,
            'tax_enabled': False,
        }


def get_plan_pricing_with_tax(plan, billing_cycle='monthly'):
    """
    Get subscription plan pricing with sales tax

    Args:
        plan (str): Plan tier ('bronze', 'silver') - Bronze=Basic, Silver=Pro
        billing_cycle (str): Billing cycle ('monthly' or 'yearly')

    Returns:
        dict: Pricing information including tax breakdown
    """
    # Plan pricing - Basic and Pro
    # 10% discount on annual plans
    pricing = {
        'basic': {
            'monthly': Decimal('9.99'),
            'yearly': Decimal('107.89'),  # $9.99 * 12 * 0.9 = $107.89
        },
        'pro': {
            'monthly': Decimal('24.99'),
            'yearly': Decimal('269.89'),  # $24.99 * 12 * 0.9 = $269.89
        },
        # Legacy support for bronze/silver
        'bronze': {
            'monthly': Decimal('9.99'),
            'yearly': Decimal('107.89'),
        },
        'silver': {
            'monthly': Decimal('24.99'),
            'yearly': Decimal('269.89'),
        },
    }

    # Get base price
    plan_lower = plan.lower()
    cycle_lower = billing_cycle.lower()

    if plan_lower not in pricing:
        logger.warning(f"Invalid plan: {plan}")
        return None

    if cycle_lower not in ['monthly', 'yearly']:
        logger.warning(f"Invalid billing cycle: {billing_cycle}")
        cycle_lower = 'monthly'

    base_price = pricing[plan_lower][cycle_lower]

    # Calculate with tax
    pricing_info = calculate_total_with_tax(base_price)
    pricing_info['plan'] = plan_lower
    pricing_info['billing_cycle'] = cycle_lower
    pricing_info['currency'] = 'USD'

    return pricing_info


def format_currency(amount):
    """
    Format amount as USD currency

    Args:
        amount (Decimal or float): Amount to format

    Returns:
        str: Formatted currency string (e.g., "$24.99")
    """
    try:
        amount_decimal = Decimal(str(amount))
        return f"${amount_decimal:.2f}"
    except (ValueError, TypeError):
        return "$0.00"
