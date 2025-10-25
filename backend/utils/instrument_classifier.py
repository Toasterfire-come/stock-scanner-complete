"""
Instrument classification utilities for stocks and related tickers.

Provides a simple heuristic-based classifier and a mapping of which fields
are applicable for each instrument type.
"""

from __future__ import annotations

from typing import Dict, Set


INSTRUMENT_APPLICABLE_FIELDS: Dict[str, Set[str]] = {
    # Core market data fields kept for all
    'equity': {
        'ticker','symbol','company_name','name','exchange','current_price','price_change_today','price_change_week',
        'price_change_month','price_change_year','change_percent','bid_price','ask_price','bid_ask_spread','days_range',
        'days_low','days_high','volume','volume_today','avg_volume_3mon','dvav','shares_available','market_cap',
        'market_cap_change_3mon','formatted_market_cap','pe_ratio','pe_change_3mon','dividend_yield','week_52_low',
        'week_52_high','one_year_target','earnings_per_share','book_value','price_to_book','formatted_price',
        'formatted_change','formatted_volume','last_updated','created_at','is_gaining','is_losing','volume_ratio',
        'wordpress_url','instrument_type'
    },
    'etf': {
        # For ETFs, include trading and yield info but omit company fundamentals
        'ticker','symbol','company_name','name','exchange','current_price','price_change_today','price_change_week',
        'price_change_month','price_change_year','change_percent','bid_price','ask_price','bid_ask_spread','days_range',
        'days_low','days_high','volume','volume_today','avg_volume_3mon','dvav','shares_available',
        # Omit market_cap per user request; keep formatted_market_cap off
        'dividend_yield','week_52_low','week_52_high','formatted_price','formatted_change','formatted_volume',
        'last_updated','created_at','is_gaining','is_losing','volume_ratio','wordpress_url','instrument_type'
    },
    'warrant': {
        'ticker','symbol','company_name','name','exchange','current_price','price_change_today','change_percent',
        'days_low','days_high','days_range','volume','volume_today','avg_volume_3mon','dvav','formatted_price',
        'formatted_change','formatted_volume','last_updated','created_at','is_gaining','is_losing','wordpress_url',
        'instrument_type'
    },
    'right': {
        'ticker','symbol','company_name','name','exchange','current_price','price_change_today','change_percent',
        'days_low','days_high','days_range','volume','volume_today','avg_volume_3mon','dvav','formatted_price',
        'formatted_change','formatted_volume','last_updated','created_at','is_gaining','is_losing','wordpress_url',
        'instrument_type'
    },
    'unit': {
        'ticker','symbol','company_name','name','exchange','current_price','price_change_today','change_percent',
        'volume','volume_today','avg_volume_3mon','dvav','formatted_price','formatted_change','formatted_volume',
        'last_updated','created_at','is_gaining','is_losing','wordpress_url','instrument_type'
    },
    'etn': {
        'ticker','symbol','company_name','name','exchange','current_price','price_change_today','change_percent',
        'days_low','days_high','days_range','volume','volume_today','avg_volume_3mon','dvav','formatted_price',
        'formatted_change','formatted_volume','last_updated','created_at','is_gaining','is_losing','wordpress_url',
        'instrument_type'
    },
    'adr': {
        # Treat as equity
        'ticker','symbol','company_name','name','exchange','current_price','price_change_today','price_change_week',
        'price_change_month','price_change_year','change_percent','bid_price','ask_price','bid_ask_spread','days_range',
        'days_low','days_high','volume','volume_today','avg_volume_3mon','dvav','shares_available','market_cap',
        'market_cap_change_3mon','formatted_market_cap','dividend_yield','week_52_low','week_52_high','one_year_target',
        'earnings_per_share','book_value','price_to_book','formatted_price','formatted_change','formatted_volume',
        'last_updated','created_at','is_gaining','is_losing','volume_ratio','wordpress_url','instrument_type'
    },
}


def classify_instrument(symbol: str | None, name: str | None, security_name: str | None = None,
                        is_etf_flag: str | bool | None = None, quote_type: str | None = None) -> str:
    """Classify instrument type based on names, flags, and quote_type.

    Returns one of: 'equity','etf','warrant','right','unit','etn','adr','preferred'
    """
    s = (symbol or '').upper()
    nm = (name or '').lower()
    sn = (security_name or '').lower()

    if quote_type:
        qt = quote_type.lower()
        if 'etf' in qt:
            return 'etf'
    if isinstance(is_etf_flag, str):
        if is_etf_flag.strip().upper() == 'Y':
            return 'etf'
    elif isinstance(is_etf_flag, bool) and is_etf_flag:
        return 'etf'
    if ' etf' in nm or nm.endswith(' etf') or ' etf' in sn:
        return 'etf'
    if 'exchange traded fund' in nm or 'exchange traded fund' in sn:
        return 'etf'
    if 'warrant' in nm or 'warrant' in sn or s.endswith('W') or s.endswith('WS') or '.W' in s or s.endswith('+'):
        return 'warrant'
    if ' right' in nm or ' rights' in nm or 'right' in sn or s.endswith('R'):
        return 'right'
    if ' unit' in nm or ' units' in nm or 'unit' in sn or s.endswith('U') or '.U' in s or '=' in s:
        return 'unit'
    if 'note' in nm or 'etn' in nm or 'exchange-traded note' in nm or 'note' in sn:
        return 'etn'
    if 'preferred' in nm or 'pref' in nm or '$' in s or ('PR' in s and '-' in s):
        return 'preferred'
    if 'depositary' in nm or 'depositary' in sn or 'adr' in nm or 'adr' in sn:
        return 'adr'
    return 'equity'


def filter_fields_by_instrument(payload: Dict[str, object], instrument_type: str) -> Dict[str, object]:
    """Return a copy of payload containing only fields applicable to the instrument type."""
    allowed = INSTRUMENT_APPLICABLE_FIELDS.get(instrument_type, INSTRUMENT_APPLICABLE_FIELDS['equity'])
    return {k: v for k, v in payload.items() if k in allowed}

