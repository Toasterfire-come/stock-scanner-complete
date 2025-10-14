"""
Django REST API Views for Stock Data Integration
Provides comprehensive real-time stock data endpoints with full filtering capabilities
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.cache import cache
from django.db.models import Q, F
from django.core.exceptions import FieldError
from django.utils import timezone
from datetime import datetime, timedelta
import json
import logging
from decimal import Decimal
from django.contrib.auth.models import User
from utils.stock_data import compute_market_cap_fallback
from utils.instrument_classifier import classify_instrument, filter_fields_by_instrument

from .models import Stock, StockAlert, StockPrice, Screener, UserPortfolio, PortfolioHolding, UserWatchlist
from .plan_limits import get_limits_for_user
from emails.models import EmailSubscription
from django.conf import settings
# import yfinance as yf  # Disabled: DB-only mode
# import requests  # Disabled: DB-only mode
# from bs4 import BeautifulSoup  # Disabled: DB-only mode

logger = logging.getLogger(__name__)

def format_decimal_safe(value):
    """Safely format decimal values"""
    if value is None:
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None

def calculate_change_percent(current_price, price_change):
    """Calculate percentage change"""
    if not current_price or not price_change:
        return 0.0
# ====================
# SEC EDGAR INSIDER TRADES (Form 4)
# ====================
import re
import xml.etree.ElementTree as ET
import requests
from django.views.decorators.cache import cache_page
from django.contrib.auth import get_user_model

_SEC_TICKER_CACHE = {
    'last_fetch': None,
    'map': {}
}

def _ensure_sec_ticker_map():
    try:
        import time
        now = int(time.time())
        # Refresh at most every 6 hours
        if _SEC_TICKER_CACHE['last_fetch'] and (now - _SEC_TICKER_CACHE['last_fetch'] < 6*3600) and _SEC_TICKER_CACHE['map']:
            return _SEC_TICKER_CACHE['map']
        url = 'https://www.sec.gov/files/company_tickers.json'
        headers = {
            'User-Agent': 'TradeScanPro/1.0 (contact@tradescanpro.com)'
        }
        r = requests.get(url, headers=headers, timeout=15)
        r.raise_for_status()
        data = r.json()
        mapping = {}
        # Newer format is an array-like object with numeric keys
        if isinstance(data, dict):
            for _, obj in data.items():
                try:
                    t = str(obj.get('ticker') or '').upper().strip()
                    cik = int(obj.get('cik_str'))
                    if t:
                        mapping[t] = cik
                except Exception:
                    continue
        elif isinstance(data, list):
            for obj in data:
                try:
                    t = str(obj.get('ticker') or '').upper().strip()
                    cik = int(obj.get('cik_str'))
                    if t:
                        mapping[t] = cik
                except Exception:
                    continue
        if mapping:
            _SEC_TICKER_CACHE['map'] = mapping
            _SEC_TICKER_CACHE['last_fetch'] = now
        return _SEC_TICKER_CACHE['map']
    except Exception as e:
        logger.warning(f"SEC ticker map fetch failed: {e}")
        return _SEC_TICKER_CACHE['map'] or {}

def _get_cik_for_ticker(ticker: str) -> str | None:
    mapping = _ensure_sec_ticker_map()
    cik_int = mapping.get(ticker.upper())
    if not cik_int:
        return None
    return str(cik_int).zfill(10)

def _fetch_recent_form4_entries(cik: str, max_count: int = 20):
    """Fetch recent Form 4 filing entries (Atom) for a CIK."""
    try:
        url = f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={cik}&type=4&owner=only&count={max_count}&output=atom"
        headers = { 'User-Agent': 'TradeScanPro/1.0 (contact@tradescanpro.com)' }
        r = requests.get(url, headers=headers, timeout=20)
        r.raise_for_status()
        text = r.text
        # Parse Atom feed
        ns = {'a': 'http://www.w3.org/2005/Atom'}
        root = ET.fromstring(text)
        entries = []
        for entry in root.findall('a:entry', ns):
            title = (entry.findtext('a:title', default='', namespaces=ns) or '').strip()
            updated = (entry.findtext('a:updated', default='', namespaces=ns) or '').strip()
            link_el = entry.find('a:link', ns)
            href = link_el.get('href') if link_el is not None else ''
            # filing-date inside content? Some feeds include filing-date
            content_el = entry.find('a:content', ns)
            filing_date = ''
            accession = ''
            if content_el is not None and content_el.text:
                # Try to pull accession number and filing date via regex
                m = re.search(r'Accession Number:\s*([0-9\-]+)', content_el.text)
                if m: accession = m.group(1).strip()
                m2 = re.search(r'Filing Date:\s*([0-9\-]+)', content_el.text)
                if m2: filing_date = m2.group(1).strip()
            entries.append({ 'title': title, 'updated': updated, 'href': href, 'filing_date': filing_date, 'accession': accession })
        return entries
    except Exception as e:
        logger.warning(f"SEC Atom fetch failed for CIK {cik}: {e}")
        return []

def _fetch_index_json(filing_href: str) -> dict | None:
    try:
        if not filing_href:
            return None
        # Convert filing page URL to index.json
        # Typical filing page ends with '/index.htm'
        idx = filing_href.rfind('/index.htm')
        if idx == -1:
            return None
        index_json_url = filing_href[:idx] + '/index.json'
        headers = { 'User-Agent': 'TradeScanPro/1.0 (contact@tradescanpro.com)', 'Accept': 'application/json' }
        r = requests.get(index_json_url, headers=headers, timeout=20)
        r.raise_for_status()
        return r.json()
    except Exception:
        return None

def _find_form4_xml_path(index_json: dict) -> str | None:
    try:
        # The JSON usually has directory->item list with 'name'
        items = index_json.get('directory', {}).get('item', [])
        for it in items:
            name = (it.get('name') or '').lower()
            if name.endswith('.xml') and 'form4' in name:
                return it.get('name')
            # Many form4 primaries are named like 'xslF345X03/primary_doc.xml' or 'primary_doc.xml'
        # Fallback to first XML file
        for it in items:
            name = (it.get('name') or '').lower()
            if name.endswith('.xml'):
                return it.get('name')
    except Exception:
        pass
    return None

def _fetch_xml(url: str) -> ET.Element | None:
    try:
        headers = { 'User-Agent': 'TradeScanPro/1.0 (contact@tradescanpro.com)' }
        r = requests.get(url, headers=headers, timeout=25)
        r.raise_for_status()
        return ET.fromstring(r.content)
    except Exception:
        return None

def _parse_form4_xml(root: ET.Element) -> list[dict]:
    """Return list of transactions with keys: name, role, code, ad, date, shares, price, value."""
    if root is None:
        return []
    ns = {}
    # Extract reporter name and relationships
    reporter_name = None
    role = None
    try:
        r_owner = root.find('.//reportingOwner')
        if r_owner is not None:
            rid = r_owner.find('.//rptOwnerId')
            if rid is not None:
                nm = rid.findtext('rptOwnerName')
                reporter_name = nm.strip() if nm else None
            rel = r_owner.find('.//reportingOwnerRelationship')
            if rel is not None:
                # Prefer officer title
                officer = rel.findtext('officerTitle')
                if officer:
                    role = officer.strip()
                else:
                    # Director or officer flags
                    if (rel.findtext('isDirector') or '').lower() == 'true':
                        role = 'Director'
                    elif (rel.findtext('isOfficer') or '').lower() == 'true':
                        role = 'Officer'
    except Exception:
        pass

    def collect(table_xpath: str):
        items = []
        for tx in root.findall(table_xpath):
            try:
                code = (tx.findtext('.//transactionCoding/transactionCode') or '').strip()
                ad = (tx.findtext('.//transactionAmounts/transactionAcquiredDisposedCode/value') or '').strip().upper()
                dt = (tx.findtext('.//transactionDate/value') or '').strip()
                sh = tx.findtext('.//transactionAmounts/transactionShares/value')
                pr = tx.findtext('.//transactionAmounts/transactionPricePerShare/value')
                shares = float(sh) if sh not in (None, '') else None
                price = float(pr) if pr not in (None, '') else None
                value = shares * price if (shares is not None and price is not None) else None
                items.append({
                    'name': reporter_name,
                    'role': role,
                    'code': code,
                    'ad': ad,
                    'date': dt,
                    'shares': shares,
                    'price': price,
                    'value': value,
                    'table': 'nonDerivative' if 'nonDerivative' in table_xpath else 'derivative'
                })
            except Exception:
                continue
        return items

    txs = []
    txs += collect('.//nonDerivativeTable/nonDerivativeTransaction')
    txs += collect('.//derivativeTable/derivativeTransaction')
    return txs

@api_view(['GET'])
@permission_classes([AllowAny])
def stock_insiders_api(request, ticker: str):
    """Return recent insider transactions (Form 4) for a ticker (last 30 days)."""
    try:
        import datetime as _dt
        ticker = ticker.upper()
        # Basic cache
        cache_key = f"insiders_{ticker}"
        cached = cache.get(cache_key)
        if cached:
            return Response(cached)

        cik = _get_cik_for_ticker(ticker)
        if not cik:
            return Response({ 'success': False, 'error': 'CIK not found for ticker' }, status=404)

        entries = _fetch_recent_form4_entries(cik, max_count=25)
        cutoff = _dt.date.today() - _dt.timedelta(days=30)

        results = []
        net_shares = 0.0
        for e in entries:
            href = e.get('href') or ''
            if not href:
                continue
            idx_json = _fetch_index_json(href)
            if not idx_json:
                continue
            base_dir = idx_json.get('directory', {}).get('name') or ''
            # Build root URL prefix from href up to the folder
            # Example href: https://www.sec.gov/Archives/edgar/data/{cik}/{acc-no}/index.htm
            prefix = href[:href.rfind('/')]  # .../{acc}/index.htm -> .../{acc}
            form_xml_name = _find_form4_xml_path(idx_json)
            if not form_xml_name:
                continue
            xml_url = f"{prefix}/{form_xml_name}"
            root = _fetch_xml(xml_url)
            txs = _parse_form4_xml(root)
            for tx in txs:
                # Filter by date window
                try:
                    d = tx.get('date') or ''
                    d_obj = _dt.datetime.strptime(d, '%Y-%m-%d').date()
                except Exception:
                    # skip unparsable dates
                    continue
                if d_obj < cutoff:
                    continue
                shares = tx.get('shares') or 0.0
                ad = (tx.get('ad') or '').upper()
                if ad == 'A':
                    net_shares += float(shares)
                elif ad == 'D':
                    net_shares -= float(shares)
                results.append({
                    'insider_name': tx.get('name') or 'Unknown',
                    'role': tx.get('role') or 'Insider',
                    'transaction_type': tx.get('code') or '',
                    'ad': ad,
                    'date': tx.get('date'),
                    'shares': tx.get('shares'),
                    'price': tx.get('price'),
                    'value': tx.get('value'),
                })

        # Sort newest first
        results.sort(key=lambda r: r.get('date') or '', reverse=True)
        signal = 'Neutral'
        if net_shares > 0:
            signal = 'Net Insider Buying'
        elif net_shares < 0:
            signal = 'Net Insider Selling'

        payload = {
            'success': True,
            'ticker': ticker,
            'cik': cik,
            'timeframe_days': 30,
            'summary': {
                'net_insider_activity_shares': round(float(net_shares), 2),
                'signal': signal,
                'records_count': len(results)
            },
            'records': results[:100]
        }
        # Cache 30 minutes
        cache.set(cache_key, payload, 1800)
        return Response(payload)
    except Exception as e:
        logger.error(f"Insiders API error for {ticker}: {e}", exc_info=True)
        return Response({ 'success': False, 'error': 'Failed to fetch insider data' }, status=500)

# ====================
# SHAREABLE WATCHLISTS & PORTFOLIOS (no DB migration – HMAC slugs)
# ====================
import hmac
import hashlib
import base64
import os as _os

def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode('utf-8').rstrip('=')

def _b64url_decode(s: str) -> bytes:
    padding = '=' * (-len(s) % 4)
    return base64.urlsafe_b64decode(s + padding)

def _share_make_slug(resource_type: str, resource_id: str) -> str:
    # payload = type:id:nonce
    nonce = _b64url(_os.urandom(12))
    payload = f"{resource_type}:{resource_id}:{nonce}".encode('utf-8')
    key = (getattr(settings, 'SECRET_KEY', 'secret') or 'secret').encode('utf-8')
    sig = hmac.new(key, payload, hashlib.sha256).digest()
    return _b64url(payload) + '.' + _b64url(sig)

def _share_parse_slug(slug: str):
    try:
        parts = slug.split('.')
        if len(parts) != 2:
            return None
        raw, sig = parts
        payload = _b64url_decode(raw)
        key = (getattr(settings, 'SECRET_KEY', 'secret') or 'secret').encode('utf-8')
        expected = hmac.new(key, payload, hashlib.sha256).digest()
        if not hmac.compare_digest(expected, _b64url_decode(sig)):
            return None
        txt = payload.decode('utf-8')
        typ, rid, _nonce = txt.split(':', 2)
        return { 'type': typ, 'id': rid }
    except Exception:
        return None

from .models import UserWatchlist, WatchlistItem, UserPortfolio, PortfolioHolding
from django.contrib.auth.decorators import login_required

def _sanitize_watchlist_payload(w: UserWatchlist):
    try:
        items = WatchlistItem.objects.filter(watchlist=w).select_related('stock')
        stocks = []
        returns = []
        for it in items:
            ticker = getattr(it.stock, 'ticker', None) or ''
            name = getattr(it.stock, 'company_name', None) or getattr(it.stock, 'name', '')
            current_price = float(it.current_price or getattr(it.stock, 'current_price', 0) or 0)
            change_percent = float(getattr(it.stock, 'change_percent', 0) or 0)
            since_added_ret = None
            try:
                if it.added_price and it.added_price > 0 and it.current_price is not None:
                    since_added_ret = float(((it.current_price - it.added_price) / it.added_price) * 100)
            except Exception:
                since_added_ret = None
            if since_added_ret is not None:
                returns.append(since_added_ret)
            stocks.append({
                'ticker': ticker,
                'name': name,
                'current_price': current_price,
                'change_percent': change_percent,
                'since_added_return_percent': since_added_ret
            })
        avg_return = round(sum(returns)/len(returns), 2) if returns else 0.0
        return {
            'type': 'watchlist',
            'version': '1',
            'name': w.name,
            'description': w.description or '',
            'performance': { 'avg_return_percent': avg_return, 'window_days': 30 },
            'stocks': stocks,
            'last_updated': w.updated_at.isoformat() if hasattr(w, 'updated_at') and w.updated_at else None
        }
    except Exception:
        return { 'type': 'watchlist', 'version': '1', 'name': w.name, 'stocks': [] }

def _sanitize_portfolio_payload(p: UserPortfolio):
    try:
        holdings = PortfolioHolding.objects.filter(portfolio=p).select_related('stock')
        total_value = 0.0
        total_cost = 0.0
        items = []
        for h in holdings:
            ticker = getattr(h.stock, 'ticker', None) or ''
            name = getattr(h.stock, 'company_name', None) or getattr(h.stock, 'name', '')
            current_price = float(h.current_price or getattr(h.stock, 'current_price', 0) or 0)
            value = float(h.shares * h.current_price) if h.shares is not None and h.current_price is not None else 0.0
            cost = float(h.shares * h.average_cost) if h.shares is not None and h.average_cost is not None else 0.0
            total_value += value
            total_cost += cost
            items.append({
                'ticker': ticker,
                'name': name,
                'allocation_percent': None,  # computed below
                'shares': float(h.shares or 0),
                'average_cost': float(h.average_cost or 0),
                'current_price': current_price
            })
        alloc_sum = sum((i['shares'] * i['current_price']) for i in items) or 0.0
        for i in items:
            v = (i['shares'] * i['current_price'])
            i['allocation_percent'] = round((v/alloc_sum)*100, 2) if alloc_sum > 0 else 0.0
        total_ret_pct = round(((total_value - total_cost)/total_cost)*100, 2) if total_cost > 0 else 0.0
        return {
            'type': 'portfolio',
            'version': '1',
            'name': p.name,
            'performance': { 'total_value': round(total_value, 2), 'total_return_percent': total_ret_pct },
            'holdings': items,
            'last_updated': p.updated_at.isoformat() if hasattr(p, 'updated_at') and p.updated_at else None
        }
    except Exception:
        return { 'type': 'portfolio', 'version': '1', 'name': p.name, 'holdings': [] }

@api_view(['POST'])
@permission_classes([AllowAny])
def share_watchlist_create_link(request, watchlist_id: str):
    try:
        if not request.user.is_authenticated:
            return Response({ 'success': False, 'error': 'Authentication required' }, status=401)
        w = UserWatchlist.objects.get(id=watchlist_id, user=request.user)
        slug = _share_make_slug('watchlist', str(w.id))
        return Response({ 'success': True, 'slug': slug, 'url': f"/w/{slug}" })
    except UserWatchlist.DoesNotExist:
        return Response({ 'success': False, 'error': 'Not found' }, status=404)
    except Exception as e:
        logger.error(f"share_watchlist_create_link error: {e}")
        return Response({ 'success': False }, status=500)

@api_view(['POST'])
@permission_classes([AllowAny])
def share_portfolio_create_link(request, portfolio_id: str):
    try:
        if not request.user.is_authenticated:
            return Response({ 'success': False, 'error': 'Authentication required' }, status=401)
        p = UserPortfolio.objects.get(id=portfolio_id, user=request.user)
        slug = _share_make_slug('portfolio', str(p.id))
        return Response({ 'success': True, 'slug': slug, 'url': f"/p/{slug}" })
    except UserPortfolio.DoesNotExist:
        return Response({ 'success': False, 'error': 'Not found' }, status=404)
    except Exception as e:
        logger.error(f"share_portfolio_create_link error: {e}")
        return Response({ 'success': False }, status=500)

@api_view(['GET'])
@permission_classes([AllowAny])
def share_watchlist_public(request, slug: str):
    info = _share_parse_slug(slug)
    if not info or info.get('type') != 'watchlist':
        return Response({ 'success': False, 'error': 'Invalid link' }, status=404)
    try:
        w = UserWatchlist.objects.get(id=info['id'])
    except UserWatchlist.DoesNotExist:
        return Response({ 'success': False, 'error': 'Not found' }, status=404)
    payload = _sanitize_watchlist_payload(w)
    return Response({ 'success': True, **payload })

@api_view(['GET'])
@permission_classes([AllowAny])
def share_portfolio_public(request, slug: str):
    info = _share_parse_slug(slug)
    if not info or info.get('type') != 'portfolio':
        return Response({ 'success': False, 'error': 'Invalid link' }, status=404)
    try:
        p = UserPortfolio.objects.get(id=info['id'])
    except UserPortfolio.DoesNotExist:
        return Response({ 'success': False, 'error': 'Not found' }, status=404)
    payload = _sanitize_portfolio_payload(p)
    return Response({ 'success': True, **payload })

@api_view(['GET'])
@permission_classes([AllowAny])
def share_watchlist_export(request, slug: str):
    resp = share_watchlist_public(request, slug)
    return resp

@api_view(['GET'])
@permission_classes([AllowAny])
def share_portfolio_export(request, slug: str):
    resp = share_portfolio_public(request, slug)
    return resp

@api_view(['POST'])
@permission_classes([AllowAny])
def share_watchlist_copy(request, slug: str):
    if not request.user.is_authenticated:
        return Response({ 'success': False, 'error': 'Authentication required' }, status=401)
    info = _share_parse_slug(slug)
    if not info or info.get('type') != 'watchlist':
        return Response({ 'success': False, 'error': 'Invalid link' }, status=404)
    try:
        w = UserWatchlist.objects.get(id=info['id'])
        # Create new watchlist for user
        nw = UserWatchlist.objects.create(user=request.user, name=f"Copy of {w.name}")
        items = WatchlistItem.objects.filter(watchlist=w)
        for it in items:
            WatchlistItem.objects.create(
                watchlist=nw,
                stock=it.stock,
                added_price=it.added_price,
                current_price=it.current_price,
                notes=''
            )
        return Response({ 'success': True, 'id': nw.id, 'url': f"/app/watchlists/{nw.id}" })
    except UserWatchlist.DoesNotExist:
        return Response({ 'success': False, 'error': 'Not found' }, status=404)
    except Exception as e:
        logger.error(f"share_watchlist_copy error: {e}")
        return Response({ 'success': False }, status=500)

@api_view(['POST'])
@permission_classes([AllowAny])
def share_portfolio_copy(request, slug: str):
    if not request.user.is_authenticated:
        return Response({ 'success': False, 'error': 'Authentication required' }, status=401)
    info = _share_parse_slug(slug)
    if not info or info.get('type') != 'portfolio':
        return Response({ 'success': False, 'error': 'Invalid link' }, status=404)
    try:
        p = UserPortfolio.objects.get(id=info['id'])
        np = UserPortfolio.objects.create(user=request.user, name=f"Copy of {p.name}")
        hs = PortfolioHolding.objects.filter(portfolio=p)
        for h in hs:
            PortfolioHolding.objects.create(
                portfolio=np,
                stock=h.stock,
                shares=h.shares,
                average_cost=h.average_cost,
                current_price=h.current_price
            )
        return Response({ 'success': True, 'id': np.id, 'url': f"/app/portfolio" })
    except UserPortfolio.DoesNotExist:
        return Response({ 'success': False, 'error': 'Not found' }, status=404)
    except Exception as e:
        logger.error(f"share_portfolio_copy error: {e}")
        return Response({ 'success': False }, status=500)

    try:
        return float((price_change / (current_price - price_change)) * 100)
    except (ZeroDivisionError, TypeError):
        return 0.0

@api_view(['GET'])
@permission_classes([AllowAny])
def stock_list_api(request):
    """
    Get comprehensive list of stocks with full data and filtering - FIXED VERSION

    URL: /api/stocks/
    Parameters:
    - limit: Number of stocks to return (default: 50, max: 1000)
    - search: Search by ticker or company name
    - category: Filter by category (gainers, losers, high_volume, large_cap, small_cap, all)
    - min_price: Minimum price filter
    - max_price: Maximum price filter
    - min_volume: Minimum volume filter
    - min_market_cap: Minimum market cap filter
    - max_market_cap: Maximum market cap filter
    - min_pe: Minimum P/E ratio
    - max_pe: Maximum P/E ratio
    - exchange: Filter by exchange (omit or 'all' to include all)
    - sort_by: Sort field (price, volume, market_cap, change_percent, pe_ratio)
    - sort_order: Sort order (asc, desc) default: desc
    """
    try:
        # Parse parameters with pagination support
        page = int(request.GET.get('page', 1))
        limit = min(int(request.GET.get('limit', 50)), 1000)
        search = request.GET.get('search', '').strip()
        category = request.GET.get('category', '').strip()
        
        # Calculate offset for pagination
        offset = (page - 1) * limit
        
        # Price filters
        min_price = request.GET.get('min_price')
        max_price = request.GET.get('max_price')
        
        # Volume filters
        min_volume = request.GET.get('min_volume')
        
        # Market cap filters
        min_market_cap = request.GET.get('min_market_cap')
        max_market_cap = request.GET.get('max_market_cap')
        
        # P/E ratio filters
        min_pe = request.GET.get('min_pe')
        max_pe = request.GET.get('max_pe')
        
        # Exchange filter - do not default to NYSE; allow 'all' to include everything
        exchange = request.GET.get('exchange', '').strip()
        if exchange.lower() in ('all', ''):
            exchange = None
        
        # Sorting - default to last_updated for better results
        sort_by = request.GET.get('sort_by', 'last_updated')
        sort_order = request.GET.get('sort_order', 'desc')
        
        # Detect base request (no filters/search)
        is_base_request = (
            (not search) and (not category) and
            not any([min_price, max_price, min_volume, min_market_cap, max_market_cap, min_pe, max_pe]) and
            (exchange is None)
        )
        
        # Add intelligent caching to reduce database load
        cache_key = f"stocks_api_{category}_{sort_by}_{sort_order}_{limit}_{min_price}_{max_price}_{min_market_cap}_{max_market_cap}_{min_pe}_{max_pe}_{search}_{exchange or 'all'}_{page}_{offset}"
        cached_result = cache.get(cache_key)
        
        if cached_result:
            logger.info(f"Returning cached result for key: {cache_key}")
            return Response(cached_result, status=status.HTTP_200_OK)

        # Base queryset with better filtering
        # Be inclusive: do not drop stocks solely for missing current_price
        base_queryset = Stock.objects.exclude(
            ticker__isnull=True
        ).exclude(
            ticker__exact=''
        ).filter(
            # Prefer recently updated, but do not exclude older if needed
            last_updated__gte=timezone.now() - timedelta(days=90)
        )
        
        # Apply exchange filter (case insensitive, flexible)
        if exchange:
            # Try exact match first, then broader matches
            exchange_queries = [
                Q(exchange__iexact=exchange),
                Q(exchange__icontains=exchange),
                Q(exchange__icontains=exchange.upper()),
                Q(exchange__icontains=exchange.lower())
            ]
            
            exchange_query = exchange_queries[0]
            for eq in exchange_queries[1:]:
                exchange_query |= eq
            
            base_queryset = base_queryset.filter(exchange_query)
        
        # Apply search filter early (only if search has content)
        if search:
            base_queryset = base_queryset.filter(
                Q(ticker__icontains=search) | 
                Q(company_name__icontains=search) |
                Q(symbol__icontains=search) |
                Q(name__icontains=search)
            )
        
        # Get total count before further filtering
        total_available = base_queryset.count()
        
        # If it's the base request with no filters/search, return stocks with pagination
        if is_base_request:
            queryset = base_queryset
            # Base request should use reasonable pagination limit, not return all stocks
            limit = min(limit, 100)  # Cap at 100 for base requests
        else:
            # Apply progressive quality filters
            queryset = base_queryset
            
            # Only apply strict price filters for specific categories
            # Try to get stocks with good data first, but ensure inclusivity
            preferred_queryset = queryset.filter(
                current_price__isnull=False
            ).exclude(current_price=0)
            
            # If we get enough results, use the preferred set
            if preferred_queryset.count() >= min(limit, 50):
                queryset = preferred_queryset
            else:
                # Include stocks with ANY useful data (even if price is zero)
                queryset = queryset.filter(
                    Q(current_price__isnull=False) |
                    Q(volume__isnull=False) |
                    Q(market_cap__isnull=False)
                )
        
        # Search filter already applied above to base_queryset
        # No need to reapply here

        # Apply price filters
        if min_price:
            try:
                queryset = queryset.filter(current_price__gte=Decimal(min_price))
            except (ValueError, TypeError):
                pass
                
        if max_price:
            try:
                queryset = queryset.filter(current_price__lte=Decimal(max_price))
            except (ValueError, TypeError):
                pass

        # Apply volume filters
        if min_volume:
            try:
                queryset = queryset.filter(volume__gte=int(min_volume))
            except (ValueError, TypeError):
                pass

        # Apply market cap filters
        if min_market_cap:
            try:
                queryset = queryset.filter(market_cap__gte=int(min_market_cap))
            except (ValueError, TypeError):
                pass
                
        if max_market_cap:
            try:
                queryset = queryset.filter(market_cap__lte=int(max_market_cap))
            except (ValueError, TypeError):
                pass

        # Apply P/E ratio filters
        if min_pe:
            try:
                queryset = queryset.filter(pe_ratio__gte=Decimal(min_pe))
            except (ValueError, TypeError):
                pass
                
        if max_pe:
            try:
                queryset = queryset.filter(pe_ratio__lte=Decimal(max_pe))
            except (ValueError, TypeError):
                pass

        # Apply category filters with market hours awareness
        if category == 'gainers':
            # Try current day first, then fall back to most recent available data
            queryset = queryset.filter(price_change_today__gt=0)
            if not queryset.exists():
                logger.info("No gainers found for today, checking recent price changes...")
                queryset = base_queryset.filter(
                    Q(price_change_today__gt=0) |
                    Q(change_percent__gt=0) |
                    Q(price_change_week__gt=0)
                ).exclude(current_price__isnull=True).order_by('-last_updated')
                
        elif category == 'losers':
            # Try current day first, then fall back to most recent available data
            queryset = queryset.filter(price_change_today__lt=0)
            if not queryset.exists():
                logger.info("No losers found for today (market may be closed), checking recent price changes...")
                # Use weekly or monthly data when daily data is not available
                queryset = base_queryset.filter(
                    Q(price_change_today__lt=0) |
                    Q(change_percent__lt=0) |
                    Q(price_change_week__lt=0) |
                    Q(price_change_month__lt=0)
                ).exclude(current_price__isnull=True)
                
                # If still no results, get stocks with the most negative changes available
                if not queryset.exists():
                    logger.info("No negative price changes found, getting stocks with lowest prices...")
                    queryset = base_queryset.filter(
                        current_price__isnull=False,
                        current_price__gt=0
                    ).order_by('current_price')  # Lowest priced stocks
                    
        elif category == 'high_volume':
            queryset = queryset.filter(volume__isnull=False).exclude(volume=0)
            # If no high volume stocks found, get any stocks with volume data
            if not queryset.exists():
                queryset = base_queryset.filter(volume__isnull=False).order_by('-volume', '-last_updated')
                
        elif category == 'large_cap':
            queryset = queryset.filter(market_cap__gte=10000000000)  # $10B+
            # If no large cap found, try lower threshold
            if not queryset.exists():
                queryset = base_queryset.filter(market_cap__gte=5000000000).order_by('-market_cap', '-last_updated')
                
        elif category == 'small_cap':
            queryset = queryset.filter(market_cap__lt=2000000000, market_cap__gt=0)  # < $2B
            # If no small cap found, try different range
            if not queryset.exists():
                queryset = base_queryset.filter(market_cap__lt=5000000000, market_cap__gt=0).order_by('market_cap', '-last_updated')

        # Apply sorting with fallbacks
        sort_field = sort_by
        if sort_order == 'desc':
            sort_field = f'-{sort_by}'
            
        # Handle sorting with fallbacks
        try:
            if sort_by == 'change_percent':
                if sort_order == 'desc':
                    queryset = queryset.order_by('-change_percent', '-last_updated')
                else:
                    queryset = queryset.order_by('change_percent', '-last_updated')
            elif sort_by == 'volume':
                queryset = queryset.order_by(sort_field, '-last_updated')
            elif sort_by == 'last_updated':
                queryset = queryset.order_by(sort_field, '-id')
            else:
                queryset = queryset.order_by(sort_field, '-last_updated')
        except (AttributeError, FieldError, ValueError) as e:
            # Fallback sorting for invalid sort fields
            logger.warning(f"Invalid sort field '{sort_by}', using fallback: {e}")
            queryset = queryset.order_by('-last_updated', '-id')

        # EMERGENCY FALLBACK: If still no results, return most recent stocks (fully inclusive)
        if not queryset.exists() and not search:
            logger.warning(f"API returned 0 results for category '{category}', using emergency fallback with recent stocks")
            # Try to get stocks updated in the last 7 days first
            recent_cutoff = timezone.now() - timedelta(days=30)
            queryset = Stock.objects.exclude(ticker__isnull=True).exclude(ticker__exact='').order_by('-last_updated')
            if not queryset.exists():
                # If no recent stocks, get any stocks with valid price data
                queryset = base_queryset.exclude(current_price__isnull=True).order_by('-last_updated')
            queryset = queryset[:limit]

        # Limit results with pagination
        total_count = queryset.count()
        stocks = queryset[offset:offset + limit]

        # Format comprehensive data
        stock_data = []
        for stock in stocks:
            change_percent = calculate_change_percent(stock.current_price, stock.price_change_today)
            
            # Compute derived market cap when missing
            derived_market_cap = None
            try:
                # Use current_price and shares_available if available
                derived_market_cap = compute_market_cap_fallback(
                    stock.current_price,
                    stock.shares_available
                )
            except Exception:
                derived_market_cap = None

            instrument_type = classify_instrument(
                stock.ticker,
                stock.company_name or stock.name,
                getattr(stock, 'name', None),
                None,
                None
            )

            record = {
                # Basic info
                'ticker': stock.ticker,
                'symbol': stock.symbol or stock.ticker,
                'company_name': stock.company_name or stock.name or stock.ticker,
                'name': stock.name or stock.company_name or stock.ticker,
                'exchange': stock.exchange,
                'instrument_type': instrument_type,
                
                # Price data (with better fallbacks)
                'current_price': format_decimal_safe(stock.current_price) or 0.0,
                'price_change_today': format_decimal_safe(stock.price_change_today) or 0.0,
                'price_change_week': format_decimal_safe(stock.price_change_week) or 0.0,
                'price_change_month': format_decimal_safe(stock.price_change_month) or 0.0,
                'price_change_year': format_decimal_safe(stock.price_change_year) or 0.0,
                'change_percent': format_decimal_safe(stock.change_percent) or change_percent or 0.0,
                
                # Bid/Ask and Range
                'bid_price': format_decimal_safe(stock.bid_price),
                'ask_price': format_decimal_safe(stock.ask_price),
                'bid_ask_spread': stock.bid_ask_spread,
                'days_range': stock.days_range,
                'days_low': format_decimal_safe(stock.days_low),
                'days_high': format_decimal_safe(stock.days_high),
                
                # Volume data
                'volume': int(stock.volume) if stock.volume else 0,
                'volume_today': int(stock.volume_today or stock.volume) if (stock.volume_today or stock.volume) else 0,
                'avg_volume_3mon': int(stock.avg_volume_3mon) if stock.avg_volume_3mon else 0,
                'dvav': format_decimal_safe(stock.dvav) or 0.0,
                'shares_available': int(stock.shares_available) if stock.shares_available else 0,
                
                # Market data
                'market_cap': int(stock.market_cap or derived_market_cap) if (stock.market_cap or derived_market_cap) else 0,
                'market_cap_change_3mon': format_decimal_safe(stock.market_cap_change_3mon) or 0.0,
                'formatted_market_cap': (getattr(stock, 'formatted_market_cap', '') or (f"${(int(stock.market_cap or derived_market_cap)/1e12):.2f}T" if (stock.market_cap or derived_market_cap) and int(stock.market_cap or derived_market_cap) >= 1e12 else (f"${(int(stock.market_cap or derived_market_cap)/1e9):.2f}B" if (stock.market_cap or derived_market_cap) and int(stock.market_cap or derived_market_cap) >= 1e9 else (f"${(int(stock.market_cap or derived_market_cap)/1e6):.2f}M" if (stock.market_cap or derived_market_cap) and int(stock.market_cap or derived_market_cap) >= 1e6 else (f"${int(stock.market_cap or derived_market_cap):,}" if (stock.market_cap or derived_market_cap) else ''))))) ,
                
                # Financial ratios
                'pe_ratio': format_decimal_safe(stock.pe_ratio),
                'pe_change_3mon': format_decimal_safe(stock.pe_change_3mon),
                'dividend_yield': format_decimal_safe(stock.dividend_yield),
                
                # 52-week range
                'week_52_low': format_decimal_safe(stock.week_52_low),
                'week_52_high': format_decimal_safe(stock.week_52_high),
                
                # Additional metrics
                'one_year_target': format_decimal_safe(stock.one_year_target),
                'earnings_per_share': format_decimal_safe(stock.earnings_per_share),
                'book_value': format_decimal_safe(stock.book_value),
                'price_to_book': format_decimal_safe(stock.price_to_book),
                
                # Formatted values
                'formatted_price': stock.formatted_price,
                'formatted_change': stock.formatted_change,
                'formatted_volume': stock.formatted_volume,
                
                # Timestamps
                'last_updated': stock.last_updated.isoformat() if stock.last_updated else None,
                'created_at': stock.created_at.isoformat() if stock.created_at else None,
                
                # Calculated fields
                'is_gaining': (stock.price_change_today or 0) > 0,
                'is_losing': (stock.price_change_today or 0) < 0,
                'volume_ratio': format_decimal_safe(stock.dvav),
                
                # WordPress integration
                'wordpress_url': f"/stock/{stock.ticker.lower()}/"
            }
            
            # Remove None-valued fields for a cleaner payload
            cleaned_record = {k: v for k, v in record.items() if v is not None}
            # Omit non-applicable fields for instrument type
            cleaned_record = filter_fields_by_instrument(cleaned_record, instrument_type)
            stock_data.append(cleaned_record)

        # Ensure we always have a meaningful response
        final_count = len(stock_data)
        final_total = max(total_available, final_count)

        filters_raw = {
            'search': search,
            'category': category,
            'min_price': min_price,
            'max_price': max_price,
            'min_volume': min_volume,
            'min_market_cap': min_market_cap,
            'max_market_cap': max_market_cap,
            'min_pe': min_pe,
            'max_pe': max_pe,
            'exchange': exchange or 'all',
            'sort_by': sort_by,
            'sort_order': sort_order
        }
        # Remove empty strings and None from filters for a cleaner report
        filters_applied = {k: v for k, v in filters_raw.items() if v not in (None, '')}

        # Cache the final response
        cache.set(cache_key, {
            'success': True,
            'count': final_count,
            'total_available': final_total,
            'filters_applied': filters_applied,
            'data': stock_data,
            'timestamp': timezone.now().isoformat()
        }, 300) # Cache for 5 minutes

        return Response({
            'success': True,
            'page': page,
            'limit': limit,
            'count': final_count,
            'total_count': total_count,
            'total_pages': (total_count + limit - 1) // limit,
            'total_available': final_total,
            'filters_applied': filters_applied,
            'data': stock_data,
            'timestamp': timezone.now().isoformat()
        })

    except Exception as e:
        logger.error(f"Error in stock_list_api: {e}", exc_info=True)
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
def stock_detail_api(request, ticker):
    """
    Get comprehensive detailed information for a specific stock

    URL: /api/stocks/{ticker}/
    Returns: Full stock data with real-time information
    """
    try:
        ticker = ticker.upper()

        # Get stock from database
        try:
            stock = Stock.objects.get(Q(ticker=ticker) | Q(symbol=ticker))
        except Stock.DoesNotExist:
            # Fallback: try to fetch minimal info via yfinance for well-known tickers
            try:
                import yfinance as yf
                yf_ticker = yf.Ticker(ticker)
                info = yf_ticker.fast_info if hasattr(yf_ticker, 'fast_info') else {}
                if not info:
                    info = {}
                current_price = float(info.get('last_price') or info.get('last_trade') or 0) or None
                market_cap = info.get('market_cap') or None
                currency = info.get('currency') or 'USD'
                if current_price is not None:
                    return Response({
                        'success': True,
                        'data': {
                            'ticker': ticker,
                            'symbol': ticker,
                            'company_name': ticker,
                            'name': ticker,
                            'exchange': info.get('exchange', 'N/A'),
                            'current_price': current_price,
                            'market_cap': int(market_cap) if market_cap else None,
                            'currency': currency,
                            'note': 'Live fallback (yfinance). Add to DB for full details.'
                        },
                        'timestamp': timezone.now().isoformat()
                    })
            except Exception:
                pass
            return Response({
                'success': False,
                'error': f'Stock {ticker} not found',
                'available_endpoints': [
                    '/api/stocks/',
                    '/api/stocks/search/'
                ]
            }, status=status.HTTP_404_NOT_FOUND)

        # Calculate additional metrics
        change_percent = calculate_change_percent(stock.current_price, stock.price_change_today)
        
        # Get recent price history if available
        recent_prices = StockPrice.objects.filter(
            stock=stock
        ).order_by('-timestamp')[:10]
        
        price_history = []
        for price_record in recent_prices:
            price_history.append({
                'price': format_decimal_safe(price_record.price),
                'timestamp': price_record.timestamp.isoformat()
            })

        # Format comprehensive detailed data
        stock_data = {
            # Basic identification
            'ticker': stock.ticker,
            'symbol': stock.symbol or stock.ticker,
            'company_name': stock.company_name or stock.name,
            'name': stock.name or stock.company_name,
            'exchange': stock.exchange,
            
            # Current price data
            'current_price': format_decimal_safe(stock.current_price),
            'price_change_today': format_decimal_safe(stock.price_change_today),
            'price_change_week': format_decimal_safe(stock.price_change_week),
            'price_change_month': format_decimal_safe(stock.price_change_month),
            'price_change_year': format_decimal_safe(stock.price_change_year),
            'change_percent': format_decimal_safe(stock.change_percent) or change_percent,
            
            # Bid/Ask and daily range
            'bid_price': format_decimal_safe(stock.bid_price),
            'ask_price': format_decimal_safe(stock.ask_price),
            'bid_ask_spread': stock.bid_ask_spread,
            'days_range': stock.days_range,
            'days_low': format_decimal_safe(stock.days_low),
            'days_high': format_decimal_safe(stock.days_high),
            
            # Volume information
            'volume': stock.volume,
            'volume_today': stock.volume_today or stock.volume,
            'avg_volume_3mon': stock.avg_volume_3mon,
            'dvav': format_decimal_safe(stock.dvav),
            'shares_available': stock.shares_available,
            
            # Market capitalization
            'market_cap': stock.market_cap,
            'market_cap_change_3mon': format_decimal_safe(stock.market_cap_change_3mon),
            'formatted_market_cap': stock.formatted_market_cap,
            
            # Financial ratios and metrics
            'pe_ratio': format_decimal_safe(stock.pe_ratio),
            'pe_change_3mon': format_decimal_safe(stock.pe_change_3mon),
            'dividend_yield': format_decimal_safe(stock.dividend_yield),
            'earnings_per_share': format_decimal_safe(stock.earnings_per_share),
            'book_value': format_decimal_safe(stock.book_value),
            'price_to_book': format_decimal_safe(stock.price_to_book),
            
            # Price history (recent)
            'recent_prices': price_history,
            
            # Additional metadata
            'last_updated': stock.last_updated.isoformat() if getattr(stock, 'last_updated', None) else None,
            # Valuation JSON (if present)
            'valuation': getattr(stock, 'valuation_json', None),
        }

        return Response({
            'success': True,
            'data': stock_data,
            'timestamp': timezone.now().isoformat()
        })

    except Exception as e:
        logger.error(f"Error in stock_detail_api: {e}", exc_info=True)
        return Response({
            'success': False,
            'error': str(e),
            'ticker': ticker
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
def stock_search_api(request):
    """
    Advanced stock search with multiple criteria
    
    URL: /api/stocks/search/
    """
    try:
        query = request.GET.get('q', '').strip()
        if not query:
            return Response({
                'success': False,
                'error': 'Search query parameter "q" is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Search in multiple fields
        stocks = Stock.objects.filter(
            Q(ticker__icontains=query) |
            Q(symbol__icontains=query) |
            Q(company_name__icontains=query) |
            Q(name__icontains=query)
        ).order_by('ticker')[:50]
        
        search_results = []
        for stock in stocks:
            search_results.append({
                'ticker': stock.ticker,
                'company_name': stock.company_name or stock.name or stock.ticker,
                'current_price': format_decimal_safe(stock.current_price) or 0.0,
                'change_percent': format_decimal_safe(stock.change_percent) or 0.0,
                'market_cap': int(stock.market_cap) if stock.market_cap else 0,
                'exchange': stock.exchange or 'N/A',
                'match_type': 'ticker' if query.upper() in stock.ticker else 'company',
                'url': f'/api/stocks/{stock.ticker}/'
            })
        
        return Response({
            'success': True,
            'query': query,
            'count': len(search_results),
            'results': search_results,
            'timestamp': timezone.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in stock_search_api: {e}", exc_info=True)
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_exempt
def wordpress_subscription_api(request):
    """
    Handle email subscriptions from WordPress

    URL: /api/wordpress/subscribe/
    Method: POST
    Data: {"email": "user@example.com", "category": "dvsa-50"}
    """
    try:
        data = json.loads(request.body)
        email = data.get('email', '').strip()
        category = (data.get('category') or '').strip()

        if not email:
            return Response({
                'success': False,
                'error': 'Email is required'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Ensure a user is associated because the model requires a user FK
        default_username = f"wp_{email.split('@')[0]}"
        user, _ = User.objects.get_or_create(username=default_username, defaults={'email': email})

        # Create or update subscription (model has no category field; we ignore it here or could store elsewhere if added later)
        subscription, created = EmailSubscription.objects.get_or_create(
            user=user,
            email=email,
            defaults={'is_active': True}
        )

        return Response({
            'success': True,
            'message': 'Subscription created successfully' if created else 'Subscription updated',
            'data': {
                'email': email,
                'category': category or None,
                'is_active': subscription.is_active
            }
        })

    except Exception as e:
        logger.error(f"WordPress subscription error: {e}", exc_info=True)
        return Response({
            'success': False,
            'error': 'Unable to process subscription'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
def stock_statistics_api(request):
    """
    Get overall market statistics for WordPress dashboard

    URL: /api/stats/
    """
    try:
        # Cache key
        cache_key = "stock_statistics"
        cached_stats = cache.get(cache_key)

        if cached_stats:
            return Response(cached_stats)

        # Calculate statistics
        total_stocks = Stock.objects.count()
        gainers = Stock.objects.filter(price_change_today__gt=0).count()
        losers = Stock.objects.filter(price_change_today__lt=0).count()
        unchanged = total_stocks - gainers - losers

        # Recent updates
        recent_updates = Stock.objects.filter(
            last_updated__gte=timezone.now() - timedelta(hours=24)
        ).count()

        # Top performers
        top_gainer = Stock.objects.filter(
            price_change_today__gt=0
        ).order_by('-price_change_today').first()

        top_loser = Stock.objects.filter(
            price_change_today__lt=0
        ).order_by('price_change_today').first()

        most_active = Stock.objects.filter(
            volume__gt=0
        ).order_by('-volume').first()

        # Email subscriptions (safe fallback if table not available)
        try:
            active_subscriptions = EmailSubscription.objects.filter(is_active=True).count()
        except Exception:
            active_subscriptions = 0

        stats_data = {
            'success': True,
            'market_overview': {
                'total_stocks': total_stocks,
                'gainers': gainers,
                'losers': losers,
                'unchanged': unchanged,
                'gainer_percentage': round((gainers / total_stocks * 100), 1) if total_stocks > 0 else 0,
                'recent_updates': recent_updates
            },
            'top_performers': {
                'top_gainer': {
                    'ticker': top_gainer.ticker if top_gainer else None,
                    'company_name': top_gainer.company_name or top_gainer.name if top_gainer else None,
                    'price_change_percent': format_decimal_safe(top_gainer.change_percent) if top_gainer else 0,
                    'wordpress_url': f"/stock/{top_gainer.ticker.lower()}/" if top_gainer else None
                } if top_gainer else None,
                'top_loser': {
                    'ticker': top_loser.ticker if top_loser else None,
                    'company_name': top_loser.company_name or top_loser.name if top_loser else None,
                    'price_change_percent': format_decimal_safe(top_loser.change_percent) if top_loser else 0,
                    'wordpress_url': f"/stock/{top_loser.ticker.lower()}/" if top_loser else None
                } if top_loser else None,
                'most_active': {
                    'ticker': most_active.ticker if most_active else None,
                    'company_name': most_active.company_name or most_active.name if most_active else None,
                    'volume_today': int(most_active.volume) if most_active and most_active.volume else 0,
                    'wordpress_url': f"/stock/{most_active.ticker.lower()}/" if most_active else None
                } if most_active else None
            },
            'subscriptions': {
                'active_count': active_subscriptions
            },
            'timestamp': timezone.now().isoformat()
        }

        # Cache for 5 minutes
        cache.set(cache_key, stats_data, 300)
        return Response(stats_data)

    except Exception as e:
        logger.error(f"Error in stock_statistics_api: {e}", exc_info=True)
        # Graceful fallback with empty-safe payload
        return Response({
            'success': True,
            'market_overview': {
                'total_stocks': 0,
                'gainers': 0,
                'losers': 0,
                'unchanged': 0,
                'gainer_percentage': 0,
                'recent_updates': 0
            },
            'top_performers': None,
            'subscriptions': { 'active_count': 0 },
            'warning': 'fallback',
            'timestamp': timezone.now().isoformat()
        }, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([AllowAny])
def market_stats_api(request):
    """
    Get overall market statistics
    """
    try:
        # Get market statistics from database
        total_stocks = Stock.objects.count()
        nyse_stocks = Stock.objects.filter(exchange__iexact='NYSE').count()
        
        # Calculate market trends
        gainers = Stock.objects.filter(price_change_today__gt=0).count()
        losers = Stock.objects.filter(price_change_today__lt=0).count()
        unchanged = Stock.objects.filter(price_change_today=0).count()
        
        # Get top performers
        top_gainers = Stock.objects.filter(
            price_change_today__gt=0
        ).order_by('-change_percent')[:5].values(
            'ticker', 'name', 'current_price', 'price_change_today', 'change_percent'
        )
        
        top_losers = Stock.objects.filter(
            price_change_today__lt=0
        ).order_by('change_percent')[:5].values(
            'ticker', 'name', 'current_price', 'price_change_today', 'change_percent'
        )
        
        # Most active by volume
        most_active = Stock.objects.exclude(
            volume__isnull=True
        ).order_by('-volume')[:5].values(
            'ticker', 'name', 'current_price', 'volume'
        )
        
        # Optional sectors array for future use (currently empty placeholder)
        sectors = []
        stats = {
            'market_overview': {
                'total_stocks': total_stocks,
                'nyse_stocks': nyse_stocks,
                'gainers': gainers,
                'losers': losers,
                'unchanged': unchanged
            },
            'top_gainers': list(top_gainers),
            'top_losers': list(top_losers),
            'most_active': list(most_active),
            'sectors': sectors,
            'last_updated': timezone.now().isoformat()
        }
        # ETag/Last-Modified handling for efficient caching
        try:
            import hashlib as _hashlib
            payload_bytes = json.dumps(stats, sort_keys=True, default=str).encode('utf-8')
            etag_value = 'W/"' + _hashlib.md5(payload_bytes).hexdigest() + '"'
            inm = request.META.get('HTTP_IF_NONE_MATCH')
            if inm and inm.strip() == etag_value:
                resp304 = Response(status=status.HTTP_304_NOT_MODIFIED)
                resp304['ETag'] = etag_value
                resp304['Cache-Control'] = 'public, max-age=30'
                resp304['Last-Modified'] = stats['last_updated']
                return resp304
            resp = Response(stats, status=status.HTTP_200_OK)
            resp['ETag'] = etag_value
            resp['Cache-Control'] = 'public, max-age=30'
            resp['Last-Modified'] = stats['last_updated']
            return resp
        except Exception:
            return Response(stats, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Market stats API error: {e}", exc_info=True)
        # Graceful fallback
        return Response({
            'market_overview': {
                'total_stocks': 0,
                'nyse_stocks': 0,
                'gainers': 0,
                'losers': 0,
                'unchanged': 0
            },
            'top_gainers': [],
            'top_losers': [],
            'most_active': [],
            'sectors': [],
            'last_updated': timezone.now().isoformat(),
            'warning': 'fallback'
        }, status=status.HTTP_200_OK)

@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def filter_stocks_api(request):
    """
    Filter stocks based on various criteria
    """
    try:
        queryset = Stock.objects.all()
        
        # Apply filters
        # Support inclusive ranges and equality for all numeric fields
        min_price = request.GET.get('min_price')
        max_price = request.GET.get('max_price')
        eq_price = request.GET.get('price_eq') or request.GET.get('eq_price')
        min_volume = request.GET.get('min_volume')
        max_volume = request.GET.get('max_volume')
        eq_volume = request.GET.get('volume_eq') or request.GET.get('eq_volume')
        sector = request.GET.get('sector')
        exchange = request.GET.get('exchange')
        # Additional numeric filters
        min_market_cap = request.GET.get('market_cap_min')
        max_market_cap = request.GET.get('market_cap_max')
        eq_market_cap = request.GET.get('market_cap_eq')
        min_pe = request.GET.get('pe_ratio_min') or request.GET.get('min_pe')
        max_pe = request.GET.get('pe_ratio_max') or request.GET.get('max_pe')
        eq_pe = request.GET.get('pe_ratio_eq') or request.GET.get('pe_eq')
        min_div_yield = request.GET.get('dividend_yield_min')
        max_div_yield = request.GET.get('dividend_yield_max')
        eq_div_yield = request.GET.get('dividend_yield_eq')
        min_change_pct = request.GET.get('change_percent_min')
        max_change_pct = request.GET.get('change_percent_max')
        eq_change_pct = request.GET.get('change_percent_eq')
        # Technicals from valuation_json
        rsi_min = request.GET.get('rsi_min') or request.GET.get('rsi14_min')
        rsi_max = request.GET.get('rsi_max') or request.GET.get('rsi14_max')
        rsi_eq  = request.GET.get('rsi_eq')  or request.GET.get('rsi14_eq')
        vwap_min = request.GET.get('vwap_min')
        vwap_max = request.GET.get('vwap_max')
        vwap_eq  = request.GET.get('vwap_eq')
        
        if eq_price:
            queryset = queryset.filter(current_price=float(eq_price))
        else:
            if min_price:
                queryset = queryset.filter(current_price__gte=float(min_price))
            if max_price:
                queryset = queryset.filter(current_price__lte=float(max_price))
        if eq_volume:
            queryset = queryset.filter(volume=int(eq_volume))
        else:
            if min_volume:
                queryset = queryset.filter(volume__gte=int(min_volume))
            if max_volume:
                queryset = queryset.filter(volume__lte=int(max_volume))
        if sector:
            queryset = queryset.filter(sector__icontains=sector)
        if exchange:
            queryset = queryset.filter(exchange__icontains=exchange)
        # Market cap
        if eq_market_cap:
            queryset = queryset.filter(market_cap=int(eq_market_cap))
        else:
            if min_market_cap:
                queryset = queryset.filter(market_cap__gte=int(min_market_cap))
            if max_market_cap:
                queryset = queryset.filter(market_cap__lte=int(max_market_cap))
        # P/E
        if eq_pe:
            queryset = queryset.filter(pe_ratio=float(eq_pe))
        else:
            if min_pe:
                queryset = queryset.filter(pe_ratio__gte=float(min_pe))
            if max_pe:
                queryset = queryset.filter(pe_ratio__lte=float(max_pe))
        # Dividend yield
        if eq_div_yield:
            queryset = queryset.filter(dividend_yield=float(eq_div_yield))
        else:
            if min_div_yield:
                queryset = queryset.filter(dividend_yield__gte=float(min_div_yield))
            if max_div_yield:
                queryset = queryset.filter(dividend_yield__lte=float(max_div_yield))
        # Change percent (today)
        if eq_change_pct:
            queryset = queryset.filter(change_percent=float(eq_change_pct))
        else:
            if min_change_pct:
                queryset = queryset.filter(change_percent__gte=float(min_change_pct))
            if max_change_pct:
                queryset = queryset.filter(change_percent__lte=float(max_change_pct))
        
        # Order by
        order_by = request.GET.get('order_by', 'ticker')
        if order_by in ['ticker', 'current_price', 'volume', 'price_change_percent']:
            queryset = queryset.order_by(order_by)
        
        # Allow JSON body as alternate input (supports GET with body and POST)
        try:
            body = None
            try:
                # DRF Request may have .data already parsed
                body = getattr(request, 'data', None)
            except Exception:
                body = None
            if body is None:
                raw = getattr(request, 'body', b'') or b''
                if raw:
                    try:
                        body = json.loads(raw.decode('utf-8')) if isinstance(raw, (bytes, bytearray)) else json.loads(raw or '{}')
                    except Exception:
                        body = None
            if isinstance(body, dict):
                if 'criteria' in body and isinstance(body['criteria'], list):
                    # translate array criteria
                    for c in body['criteria']:
                        cid = (c.get('id') or '').lower()
                        if cid == 'market_cap':
                            if c.get('min') is not None: queryset = queryset.filter(market_cap__gte=int(c['min']))
                            if c.get('max') is not None: queryset = queryset.filter(market_cap__lte=int(c['max']))
                        if cid == 'price':
                            if c.get('min') is not None: queryset = queryset.filter(current_price__gte=float(c['min']))
                            if c.get('max') is not None: queryset = queryset.filter(current_price__lte=float(c['max']))
                        if cid == 'volume':
                            if c.get('min') is not None: queryset = queryset.filter(volume__gte=int(c['min']))
                            if c.get('max') is not None: queryset = queryset.filter(volume__lte=int(c['max']))
                        if cid == 'pe_ratio':
                            if c.get('min') is not None: queryset = queryset.filter(pe_ratio__gte=float(c['min']))
                            if c.get('max') is not None: queryset = queryset.filter(pe_ratio__lte=float(c['max']))
                        if cid == 'dividend_yield':
                            if c.get('min') is not None: queryset = queryset.filter(dividend_yield__gte=float(c['min']))
                            if c.get('max') is not None: queryset = queryset.filter(dividend_yield__lte=float(c['max']))
                        if cid == 'change_percent':
                            if c.get('min') is not None: queryset = queryset.filter(change_percent__gte=float(c['min']))
                            if c.get('max') is not None: queryset = queryset.filter(change_percent__lte=float(c['max']))
                        if cid in ('rsi','rsi14'):
                            if c.get('min') is not None: queryset = queryset.filter(valuation_json__rsi14__gte=float(c['min']))
                            if c.get('max') is not None: queryset = queryset.filter(valuation_json__rsi14__lte=float(c['max']))
                        if cid == 'vwap':
                            if c.get('min') is not None: queryset = queryset.filter(valuation_json__vwap__gte=float(c['min']))
                            if c.get('max') is not None: queryset = queryset.filter(valuation_json__vwap__lte=float(c['max']))
                        if cid == 'exchange':
                            if c.get('value'): queryset = queryset.filter(exchange__icontains=str(c['value']))
                else:
                    # simple flat mapping
                    m = body
                    if 'min_price' in m: queryset = queryset.filter(current_price__gte=float(m['min_price']))
                    if 'max_price' in m: queryset = queryset.filter(current_price__lte=float(m['max_price']))
                    if 'min_volume' in m: queryset = queryset.filter(volume__gte=int(m['min_volume']))
                    if 'max_volume' in m: queryset = queryset.filter(volume__lte=int(m['max_volume']))
                    if 'market_cap_min' in m: queryset = queryset.filter(market_cap__gte=int(m['market_cap_min']))
                    if 'market_cap_max' in m: queryset = queryset.filter(market_cap__lte=int(m['market_cap_max']))
                    if 'pe_ratio_min' in m: queryset = queryset.filter(pe_ratio__gte=float(m['pe_ratio_min']))
                    if 'pe_ratio_max' in m: queryset = queryset.filter(pe_ratio__lte=float(m['pe_ratio_max']))
                    if 'dividend_yield_min' in m: queryset = queryset.filter(dividend_yield__gte=float(m['dividend_yield_min']))
                    if 'dividend_yield_max' in m: queryset = queryset.filter(dividend_yield__lte=float(m['dividend_yield_max']))
                    if 'change_percent_min' in m: queryset = queryset.filter(change_percent__gte=float(m['change_percent_min']))
                    if 'change_percent_max' in m: queryset = queryset.filter(change_percent__lte=float(m['change_percent_max']))
                    if 'exchange' in m: queryset = queryset.filter(exchange__icontains=str(m['exchange']))
                    if 'rsi_min' in m: queryset = queryset.filter(valuation_json__rsi14__gte=float(m['rsi_min']))
                    if 'rsi_max' in m: queryset = queryset.filter(valuation_json__rsi14__lte=float(m['rsi_max']))
                    if 'vwap_min' in m: queryset = queryset.filter(valuation_json__vwap__gte=float(m['vwap_min']))
                    if 'vwap_max' in m: queryset = queryset.filter(valuation_json__vwap__lte=float(m['vwap_max']))
        except Exception as _:
            # ignore malformed JSON; fall back to query params only
            pass

        # Apply direct query param technical filters last (so they work without JSON body)
        try:
            if rsi_eq is not None:
                queryset = queryset.filter(valuation_json__rsi14=float(rsi_eq))
            else:
                if rsi_min is not None:
                    queryset = queryset.filter(valuation_json__rsi14__gte=float(rsi_min))
                if rsi_max is not None:
                    queryset = queryset.filter(valuation_json__rsi14__lte=float(rsi_max))
            if vwap_eq is not None:
                queryset = queryset.filter(valuation_json__vwap=float(vwap_eq))
            else:
                if vwap_min is not None:
                    queryset = queryset.filter(valuation_json__vwap__gte=float(vwap_min))
                if vwap_max is not None:
                    queryset = queryset.filter(valuation_json__vwap__lte=float(vwap_max))
        except Exception:
            pass

        # Pagination
        limit = int(request.GET.get('limit', 100))
        offset = int(request.GET.get('offset', 0))
        
        stocks = queryset[offset:offset + limit]
        
        result = []
        for stock in stocks:
            result.append({
                'ticker': stock.ticker,
                'name': stock.name or stock.company_name or stock.ticker,
                'current_price': format_decimal_safe(stock.current_price) or 0.0,
                'price_change': format_decimal_safe(stock.price_change_today) or 0.0,
                'price_change_percent': format_decimal_safe(stock.change_percent) or 0.0,
                'volume': int(stock.volume) if stock.volume else 0,
                'market_cap': format_decimal_safe(stock.market_cap) or 0.0,
                'exchange': stock.exchange or ''
            })
        
        return Response({
            'stocks': result,
            'total_count': queryset.count(),
            'filters_applied': {
                'min_price': min_price,
                'max_price': max_price,
                'min_volume': min_volume,
                'max_volume': max_volume,
                'sector': sector,
                'exchange': exchange
            }
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Filter stocks API error: {e}")
        return Response(
            {'error': 'Failed to filter stocks'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([AllowAny])
def realtime_stock_api(request, ticker):
    """
    Get current stock data from the database only
    """
    try:
        db_stock = Stock.objects.get(Q(ticker__iexact=ticker) | Q(symbol__iexact=ticker))
        data = {
            'ticker': db_stock.ticker,
            'company_name': db_stock.company_name or db_stock.name,
            'current_price': float(db_stock.current_price or 0.0),
            'open_price': None,
            'high_price': None,
            'low_price': None,
            'volume': int(db_stock.volume or 0),
            'market_cap': int(db_stock.market_cap or 0),
            'pe_ratio': float(db_stock.pe_ratio or 0) if db_stock.pe_ratio is not None else None,
            'dividend_yield': float(db_stock.dividend_yield or 0) if db_stock.dividend_yield is not None else None,
            'last_updated': db_stock.last_updated.isoformat() if db_stock.last_updated else timezone.now().isoformat(),
            'market_status': 'unknown'
        }
        return Response(data, status=status.HTTP_200_OK)
    except Stock.DoesNotExist:
        return Response(
            {'error': f'Stock {ticker} not found in database'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(f"Real-time stock API error for {ticker}: {e}")
        return Response(
            {'error': 'Failed to retrieve stock data'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([AllowAny])
def trending_stocks_api(request):
    """
    Get trending stocks based on volume and price changes - cached for 90 seconds
    """
    try:
        # Check cache first
        cache_key = "trending_stocks_api"
        cached_result = cache.get(cache_key)
        
        if cached_result:
            logger.info(f"Returning cached trending stocks result")
            return Response(cached_result, status=status.HTTP_200_OK)
        # Get top trending by volume - prioritize NYSE
        high_volume_stocks = Stock.objects.filter(
            exchange__iexact='NYSE'
        ).exclude(
            volume__isnull=True
        ).exclude(volume=0).order_by('-volume')[:10]
        
        # If not enough NYSE stocks, include other exchanges
        if len(high_volume_stocks) < 5:
            additional_stocks = Stock.objects.exclude(
                exchange__iexact='NYSE'
            ).exclude(
                volume__isnull=True
            ).exclude(volume=0).order_by('-volume')[:10-len(high_volume_stocks)]
            high_volume_stocks = list(high_volume_stocks) + list(additional_stocks)
        
        # Get top gainers (prefer positive changes, prioritize NYSE)
        top_gainers = Stock.objects.filter(
            exchange__iexact='NYSE',
            change_percent__gt=0
        ).order_by('-change_percent')[:10]
        
        # If not enough NYSE gainers, include other exchanges
        if len(top_gainers) < 5:
            additional_gainers = Stock.objects.filter(
                change_percent__gt=0
            ).exclude(
                exchange__iexact='NYSE'
            ).order_by('-change_percent')[:10-len(top_gainers)]
            top_gainers = list(top_gainers) + list(additional_gainers)
        
        # If still no gainers, get stocks with the best changes (even if negative)
        if len(top_gainers) == 0:
            top_gainers = Stock.objects.exclude(
                change_percent__isnull=True
            ).order_by('-change_percent')[:10]
        
        # Get most active (FIXED - more inclusive filtering)
        # Try NYSE stocks with good volume data first
        most_active = Stock.objects.filter(
            exchange__iexact='NYSE'
        ).exclude(
            volume__isnull=True
        ).exclude(volume=0).order_by('-volume')[:10]
        
        # If not enough NYSE active stocks, include other exchanges
        if len(most_active) < 5:
            additional_active = Stock.objects.exclude(
                exchange__iexact='NYSE'
            ).exclude(
                volume__isnull=True
            ).exclude(volume=0).order_by('-volume')[:10-len(most_active)]
            most_active = list(most_active) + list(additional_active)
        
        # Fallback for most active if volume filter is too restrictive
        if len(most_active) < 5:
            fallback_active = Stock.objects.exclude(
                volume__isnull=True
            ).exclude(volume=0).order_by('-volume')[:10]
            most_active = list(most_active) + [s for s in fallback_active if s not in most_active][:10]
        
        def format_stock_data(stocks):
            return [{
                'ticker': stock.ticker,
                'name': stock.name or stock.company_name or stock.ticker,
                'current_price': format_decimal_safe(stock.current_price) or 0.0,
                'price_change_today': format_decimal_safe(stock.price_change_today) or 0.0,
                'change_percent': format_decimal_safe(stock.change_percent) or 0.0,
                'volume': int(stock.volume) if stock.volume else 0,
                'market_cap': format_decimal_safe(stock.market_cap) or 0.0
            } for stock in stocks]
        
        trending_data = {
            'high_volume': format_stock_data(high_volume_stocks),
            'top_gainers': format_stock_data(top_gainers),
            'most_active': format_stock_data(most_active),
            'last_updated': timezone.now().isoformat()
        }
        # Cache the result for 90 seconds to reduce DB load during peak traffic
        cache.set(cache_key, trending_data, 90)
        # ETag/Last-Modified handling
        try:
            import hashlib as _hashlib
            payload_bytes = json.dumps(trending_data, sort_keys=True, default=str).encode('utf-8')
            etag_value = 'W/"' + _hashlib.md5(payload_bytes).hexdigest() + '"'
            inm = request.META.get('HTTP_IF_NONE_MATCH')
            if inm and inm.strip() == etag_value:
                resp304 = Response(status=status.HTTP_304_NOT_MODIFIED)
                resp304['ETag'] = etag_value
                resp304['Cache-Control'] = 'public, max-age=30'
                resp304['Last-Modified'] = trending_data['last_updated']
                return resp304
            resp = Response(trending_data, status=status.HTTP_200_OK)
            resp['ETag'] = etag_value
            resp['Cache-Control'] = 'public, max-age=30'
            resp['Last-Modified'] = trending_data['last_updated']
            return resp
        except Exception:
            return Response(trending_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Trending stocks API error: {e}", exc_info=True)
        # Graceful fallback
        return Response({
            'high_volume': [],
            'top_gainers': [],
            'most_active': [],
            'last_updated': timezone.now().isoformat(),
            'warning': 'fallback'
        }, status=status.HTTP_200_OK)


# ====================
# SCREENERS CRUD (powered by filter_stocks_api)
# ====================
@api_view(['GET'])
@permission_classes([AllowAny])
def screeners_list_api(request):
    user = getattr(request, 'user', None)
    qs = Screener.objects.all()
    if user and getattr(user, 'is_authenticated', False):
        qs = qs.filter(Q(is_public=True) | Q(user=user))
    else:
        qs = qs.filter(is_public=True)
    items = [{
        'id': s.id,
        'name': s.name,
        'description': s.description,
        'criteria': s.criteria,
        'is_public': s.is_public,
        'last_run': s.last_run.isoformat() if s.last_run else None,
    } for s in qs.order_by('-updated_at')[:100]]
    return Response({ 'data': items })

@api_view(['GET'])
@permission_classes([AllowAny])
def screeners_detail_api(request, screener_id: str):
    try:
        s = Screener.objects.get(id=screener_id)
        return Response({ 'data': {
            'id': s.id, 'name': s.name, 'description': s.description,
            'criteria': s.criteria, 'is_public': s.is_public,
            'last_run': s.last_run.isoformat() if s.last_run else None,
        }})
    except Screener.DoesNotExist:
        return Response({'error': 'Not found'}, status=404)

@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_exempt
def screeners_create_api(request):
    try:
        body = getattr(request, 'data', None) or json.loads(request.body or '{}')
        name = (body.get('name') or 'Untitled').strip()
        description = body.get('description') or ''
        criteria = body.get('criteria') or []
        # Enforce plan limit for screener criteria
        try:
            if getattr(request, 'user', None) and request.user.is_authenticated:
                limits = get_limits_for_user(request.user)
                max_criteria = int(limits.get('max_screener_criteria', 50) or 50)
                if isinstance(criteria, list) and len(criteria) > max_criteria:
                    criteria = criteria[:max_criteria]
        except Exception:
            pass
        is_public = bool(body.get('isPublic') or body.get('is_public') or False)
        user = request.user if getattr(request, 'user', None) and request.user.is_authenticated else None
        # Enforce per-plan screener count limit for authenticated users
        try:
            if user is not None:
                limits = get_limits_for_user(user)
                existing = Screener.objects.filter(user=user).count()
                cap = limits.get('screeners')
                if cap not in (None, float('inf')) and existing >= int(cap):
                    return Response({ 'success': False, 'error': 'Screener limit reached for your plan' }, status=429)
        except Exception:
            pass
        s = Screener.objects.create(user=user, name=name, description=description, criteria=criteria, is_public=is_public)
        return Response({ 'success': True, 'id': s.id })
    except Exception as e:
        logger.error(f"Create screener failed: {e}")
        return Response({'success': False}, status=500)

@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_exempt
def screeners_update_api(request, screener_id: str):
    try:
        s = Screener.objects.get(id=screener_id)
        body = getattr(request, 'data', None) or json.loads(request.body or '{}')
        if 'name' in body: s.name = (body.get('name') or s.name)
        if 'description' in body: s.description = body.get('description') or ''
        if 'criteria' in body: s.criteria = body.get('criteria') or []
        if 'is_public' in body or 'isPublic' in body: s.is_public = bool(body.get('is_public') or body.get('isPublic'))
        s.save()
        return Response({ 'success': True })
    except Screener.DoesNotExist:
        return Response({'error': 'Not found'}, status=404)
    except Exception as e:
        logger.error(f"Update screener failed: {e}")
        return Response({'success': False}, status=500)

@api_view(['DELETE'])
@permission_classes([AllowAny])
def screeners_delete_api(request, screener_id: str):
    try:
        s = Screener.objects.get(id=screener_id)
        s.delete()
        return Response({ 'success': True })
    except Screener.DoesNotExist:
        return Response({'error': 'Not found'}, status=404)

@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
@csrf_exempt
def screeners_results_api(request, screener_id: str):
    try:
        s = Screener.objects.get(id=screener_id)
    except Screener.DoesNotExist:
        return Response({'error': 'Not found'}, status=404)
    # Proxy to filter_stocks_api using criteria as JSON
    request._dont_enforce_csrf_checks = True
    try:
        # Ensure we pass a Django HttpRequest into the @api_view-wrapped filter_stocks_api
        django_request = getattr(request, '_request', request)
        try:
            django_request.method = 'POST'
        except Exception:
            pass
        try:
            django_request._body = json.dumps({ 'criteria': s.criteria }).encode('utf-8')
        except Exception:
            pass
        try:
            if hasattr(django_request, 'META'):
                django_request.META['CONTENT_TYPE'] = 'application/json'
        except Exception:
            pass
        resp = filter_stocks_api(django_request)
        if hasattr(resp, 'data'):
            s.last_run = timezone.now(); s.save(update_fields=['last_run'])
        return resp
    except Exception as e:
        logger.error(f"Screener results failed: {e}")
        return Response({'stocks': [], 'total_count': 0})

@api_view(['GET'])
@permission_classes([AllowAny])
def screeners_export_csv_api(request, screener_id: str):
    """Export screener results as CSV."""
    try:
        s = Screener.objects.get(id=screener_id)
    except Screener.DoesNotExist:
        return Response({'error': 'Not found'}, status=404)

    # Reuse filter_stocks_api to get results
    try:
        request._dont_enforce_csrf_checks = True
        request.body = json.dumps({ 'criteria': s.criteria }).encode('utf-8')
        resp = filter_stocks_api(request)
        payload = getattr(resp, 'data', {}) or {}
        stocks = payload.get('stocks') or payload.get('data') or []
    except Exception as e:
        logger.error(f"Export screener CSV failed: {e}")
        stocks = []

    # Build CSV
    headers = ["Ticker","Company","Price","Change %","Volume","Market Cap","Exchange"]
    lines = [",".join(headers)]
    for st in stocks:
        ticker = str(st.get('ticker') or st.get('symbol') or '-')
        company = str(st.get('company_name') or st.get('name') or '').replace(',', ' ')
        price = f"{float(st.get('current_price') or 0):.2f}"
        chg = f"{float(st.get('price_change_percent') or st.get('change_percent') or 0):.2f}"
        vol = str(int(st.get('volume') or 0))
        cap = str(int(float(st.get('market_cap') or 0)))
        exch = str(st.get('exchange') or '')
        lines.append(
            ",".join([ticker, company, price, chg, vol, cap, exch])
        )

    csv_content = "\n".join(lines)
    response = HttpResponse(csv_content, content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="screener-{screener_id}-results.csv"'
    return response

# ====================
# Simple CSV export endpoints (no keys required)
# ====================

@api_view(['GET'])
@permission_classes([AllowAny])
def export_stocks_csv_api(request):
    try:
        headers = ["Ticker","Company","Price","% Change","Volume","Market Cap","Exchange"]
        lines = [",".join(headers)]
        qs = Stock.objects.all().order_by('ticker')[:5000]
        for s in qs:
            lines.append(
                ",".join([
                    s.ticker,
                    (s.company_name or s.name or '').replace(',', ' '),
                    f"{float(s.current_price or 0):.2f}",
                    f"{float(s.change_percent or 0):.2f}",
                    str(int(s.volume or 0)),
                    str(int(float(s.market_cap or 0))),
                    s.exchange or ''
                ])
            )
        content = "\n".join(lines)
        resp = HttpResponse(content, content_type='text/csv')
        resp['Content-Disposition'] = 'attachment; filename="stocks.csv"'
        return resp
    except Exception as e:
        logger.error(f"export_stocks_csv_api error: {e}")
        return Response({'success': False, 'error': 'Export failed'}, status=500)

@api_view(['GET'])
@permission_classes([AllowAny])
def export_portfolio_csv_api(request):
    try:
        # Try to use authenticated user; fallback to a demo/test user if available
        user = getattr(request, 'user', None)
        if not user or not getattr(user, 'is_authenticated', False):
            try:
                User = get_user_model()
                user = User.objects.filter(username='test_user').first() or User.objects.first()
            except Exception:
                user = None
        headers = ["Portfolio","Ticker","Shares","Avg Cost","Current Price","Market Value","Unrealized P/L","Unrealized P/L %"]
        lines = [",".join(headers)]
        if user:
            portfolios = UserPortfolio.objects.filter(user=user)
            for pf in portfolios:
                holdings = PortfolioHolding.objects.filter(portfolio=pf)
                for h in holdings:
                    market_value = float(h.shares or 0) * float(h.current_price or 0)
                    cost_basis = float(h.shares or 0) * float(h.average_cost or 0)
                    pl = market_value - cost_basis
                    pl_pct = (pl / cost_basis * 100) if cost_basis > 0 else 0
                    lines.append(
                        ",".join([
                            pf.name,
                            h.stock.ticker,
                            f"{float(h.shares or 0):.4f}",
                            f"{float(h.average_cost or 0):.4f}",
                            f"{float(h.current_price or 0):.4f}",
                            f"{market_value:.2f}",
                            f"{pl:.2f}",
                            f"{pl_pct:.2f}"
                        ])
                    )
        content = "\n".join(lines)
        resp = HttpResponse(content, content_type='text/csv')
        resp['Content-Disposition'] = 'attachment; filename="portfolio.csv"'
        return resp
    except Exception as e:
        logger.error(f"export_portfolio_csv_api error: {e}")
        return Response({'success': False, 'error': 'Export failed'}, status=500)

@api_view(['GET'])
@permission_classes([AllowAny])
def export_watchlist_csv_api(request):
    try:
        # Try to use authenticated user; fallback to a demo/test user if available
        user = getattr(request, 'user', None)
        if not user or not getattr(user, 'is_authenticated', False):
            try:
                User = get_user_model()
                user = User.objects.filter(username='test_user').first() or User.objects.first()
            except Exception:
                user = None
        headers = ["Watchlist","Ticker","Company","Added At","Notes"]
        lines = [",".join(headers)]
        if user:
            lists = UserWatchlist.objects.filter(user=user)
            for wl in lists:
                items = wl.items.select_related('stock').all()
                for it in items:
                    lines.append(
                        ",".join([
                            wl.name,
                            it.stock.ticker,
                            (it.stock.company_name or it.stock.name or '').replace(',', ' '),
                            it.added_at.strftime('%Y-%m-%d'),
                            (it.notes or '').replace(',', ' ')
                        ])
                    )
        content = "\n".join(lines)
        resp = HttpResponse(content, content_type='text/csv')
        resp['Content-Disposition'] = 'attachment; filename="watchlists.csv"'
        return resp
    except Exception as e:
        logger.error(f"export_watchlist_csv_api error: {e}")
        return Response({'success': False, 'error': 'Export failed'}, status=500)

@api_view(['GET'])
@permission_classes([AllowAny])
def reports_download_api(request, report_id: str):
    try:
        pdf = f"""
        REPORT {report_id}

        Generated: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}
        This is a demo report.
        """
        resp = HttpResponse(pdf.encode('utf-8'), content_type='application/pdf')
        resp['Content-Disposition'] = f'attachment; filename="report_{report_id}.pdf"'
        return resp
    except Exception as e:
        logger.error(f"reports_download_api error: {e}")
        return Response({'success': False}, status=500)

@api_view(['GET'])
@permission_classes([AllowAny])
def screeners_templates_api(request):
    # Placeholder templates
    return Response({ 'data': [] })

@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def create_alert_api(request):
    """
    Create a new stock price alert
    GET: Returns endpoint information
    POST: Creates a new alert
    """
    if request.method == 'GET':
        return Response({
            'endpoint': '/api/alerts/create/',
            'method': 'POST',
            'description': 'Create a new stock price alert',
            'required_fields': {
                'ticker': 'Stock symbol (e.g., AAPL)',
                'target_price': 'Alert trigger price (number)',
                'alert_type': 'Type of alert ("above" or "below")',
                'email': 'Email address for notifications (optional)'
            },
            'example_request': {
                'ticker': 'AAPL',
                'target_price': 200.00,
                'alert_type': 'above',
                'email': 'user@example.com'
            },
            'usage': 'Send POST request with JSON data to create an alert'
        }, status=status.HTTP_200_OK)
    
    # Handle POST request
    try:
        data = json.loads(request.body)
        
        # Support both legacy fields and model fields
        required_fields = ['ticker', 'target_price', 'condition', 'email']
        for field in required_fields:
            if field not in data:
                return Response(
                    {'error': f'Missing required field: {field}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Validate condition
        if data['condition'] not in ['above', 'below']:
            return Response(
                {'error': 'Condition must be "above" or "below"'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if stock exists
        try:
            stock = Stock.objects.get(ticker=data['ticker'].upper())
        except Stock.DoesNotExist:
            return Response(
                {'error': f'Stock {data["ticker"]} not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Map to model: find or create a system user for alerts
        system_user, _ = User.objects.get_or_create(username='system_alerts', defaults={'is_staff': False, 'is_superuser': False})
        
        # Translate condition to alert_type if needed
        condition = data['condition']
        if condition == 'above':
            alert_type = 'price_above'
        elif condition == 'below':
            alert_type = 'price_below'
        else:
            alert_type = 'price_change'
        
        target_value = Decimal(str(data['target_price']))
        
        # Create alert
        alert = StockAlert.objects.create(
            user=system_user,
            stock=stock,
            alert_type=alert_type,
            target_value=target_value,
            is_active=True
        )
        
        return Response({
            'alert_id': alert.id,
            'message': f'Alert created for {stock.ticker}',
            'details': {
                'ticker': stock.ticker,
                'target_value': float(alert.target_value),
                'alert_type': alert.alert_type,
                'created_at': alert.created_at.isoformat()
            }
        }, status=status.HTTP_201_CREATED)
        
    except json.JSONDecodeError:
        return Response(
            {'error': 'Invalid JSON data'},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        logger.error(f"Create alert API error: {e}")
        return Response(
            {'error': 'Failed to create alert'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

# NEW ENDPOINTS REQUESTED BY USER

@api_view(['GET'])
@permission_classes([AllowAny])
def total_tickers_api(request):
    """
    Get total number of tickers in the database
    URL: /api/stats/total-tickers/
    """
    try:
        total_tickers = Stock.objects.count()
        return Response({
            'success': True,
            'total_tickers': total_tickers,
            'timestamp': timezone.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error in total_tickers_api: {e}", exc_info=True)
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
def gainers_losers_stats_api(request):
    """
    Get total gainers and losers with percentages
    URL: /api/stats/gainers-losers/
    """
    try:
        total_tickers = Stock.objects.count()
        total_gainers = Stock.objects.filter(price_change_today__gt=0).count()
        total_losers = Stock.objects.filter(price_change_today__lt=0).count()
        
        # Calculate percentages
        gainer_percentage = round((total_gainers / total_tickers * 100), 2) if total_tickers > 0 else 0
        loser_percentage = round((total_losers / total_tickers * 100), 2) if total_tickers > 0 else 0
        
        return Response({
            'success': True,
            'total_tickers': total_tickers,
            'total_gainers': total_gainers,
            'total_losers': total_losers,
            'gainer_percentage': gainer_percentage,
            'loser_percentage': loser_percentage,
            'timestamp': timezone.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error in gainers_losers_stats_api: {e}", exc_info=True)
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
def total_alerts_api(request):
    """
    Get total number of alerts in the system
    URL: /api/stats/total-alerts/
    """
    try:
        total_alerts = StockAlert.objects.count()
        active_alerts = StockAlert.objects.filter(is_active=True).count()
        
        return Response({
            'success': True,
            'total_alerts': total_alerts,
            'active_alerts': active_alerts,
            'timestamp': timezone.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error in total_alerts_api: {e}", exc_info=True)
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
def top_gainers_api(request):
    """
    Get top gainers with pagination
    URL: /api/stocks/top-gainers/
    Parameters:
    - page: Page number (default: 1)
    - limit: Results per page (default: 50)
    """
    try:
        page = int(request.GET.get('page', 1))
        limit = min(int(request.GET.get('limit', 50)), 100)
        
        # Calculate offset for pagination
        offset = (page - 1) * limit
        
        # Get top gainers
        queryset = Stock.objects.filter(
            price_change_today__gt=0
        ).order_by('-change_percent')
        
        total_count = queryset.count()
        stocks = queryset[offset:offset + limit]
        
        stock_data = []
        for stock in stocks:
            stock_data.append({
                'ticker': stock.ticker,
                'company_name': stock.company_name or stock.name,
                'current_price': format_decimal_safe(stock.current_price),
                'price_change_today': format_decimal_safe(stock.price_change_today),
                'change_percent': format_decimal_safe(stock.change_percent),
                'volume': stock.volume,
                'market_cap': stock.market_cap,
                'formatted_price': stock.formatted_price,
                'formatted_change': stock.formatted_change,
                'last_updated': stock.last_updated.isoformat() if stock.last_updated else None
            })
        
        return Response({
            'success': True,
            'page': page,
            'limit': limit,
            'total_count': total_count,
            'total_pages': (total_count + limit - 1) // limit,
            'data': stock_data,
            'timestamp': timezone.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in top_gainers_api: {e}", exc_info=True)
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
def top_losers_api(request):
    """
    Get top losers with pagination
    URL: /api/stocks/top-losers/
    Parameters:
    - page: Page number (default: 1)
    - limit: Results per page (default: 50)
    """
    try:
        page = int(request.GET.get('page', 1))
        limit = min(int(request.GET.get('limit', 50)), 100)
        
        # Calculate offset for pagination
        offset = (page - 1) * limit
        
        # Get top losers
        queryset = Stock.objects.filter(
            price_change_today__lt=0
        ).order_by('change_percent')
        
        total_count = queryset.count()
        stocks = queryset[offset:offset + limit]
        
        stock_data = []
        for stock in stocks:
            stock_data.append({
                'ticker': stock.ticker,
                'company_name': stock.company_name or stock.name,
                'current_price': format_decimal_safe(stock.current_price),
                'price_change_today': format_decimal_safe(stock.price_change_today),
                'change_percent': format_decimal_safe(stock.change_percent),
                'volume': stock.volume,
                'market_cap': stock.market_cap,
                'formatted_price': stock.formatted_price,
                'formatted_change': stock.formatted_change,
                'last_updated': stock.last_updated.isoformat() if stock.last_updated else None
            })
        
        return Response({
            'success': True,
            'page': page,
            'limit': limit,
            'total_count': total_count,
            'total_pages': (total_count + limit - 1) // limit,
            'data': stock_data,
            'timestamp': timezone.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in top_losers_api: {e}", exc_info=True)
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
def most_active_api(request):
    """
    Get most active stocks with pagination
    URL: /api/stocks/most-active/
    Parameters:
    - page: Page number (default: 1)
    - limit: Results per page (default: 50)
    """
    try:
        page = int(request.GET.get('page', 1))
        limit = min(int(request.GET.get('limit', 50)), 100)
        
        # Calculate offset for pagination
        offset = (page - 1) * limit
        
        # Get most active stocks
        queryset = Stock.objects.filter(
            volume__isnull=False
        ).exclude(volume=0).order_by('-volume')
        
        total_count = queryset.count()
        stocks = queryset[offset:offset + limit]
        
        stock_data = []
        for stock in stocks:
            stock_data.append({
                'ticker': stock.ticker,
                'company_name': stock.company_name or stock.name,
                'current_price': format_decimal_safe(stock.current_price),
                'price_change_today': format_decimal_safe(stock.price_change_today),
                'change_percent': format_decimal_safe(stock.change_percent),
                'volume': stock.volume,
                'market_cap': stock.market_cap,
                'formatted_price': stock.formatted_price,
                'formatted_change': stock.formatted_change,
                'formatted_volume': stock.formatted_volume,
                'last_updated': stock.last_updated.isoformat() if stock.last_updated else None
            })
        
        return Response({
            'success': True,
            'page': page,
            'limit': limit,
            'total_count': total_count,
            'total_pages': (total_count + limit - 1) // limit,
            'data': stock_data,
            'timestamp': timezone.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in most_active_api: {e}", exc_info=True)
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# PORTFOLIO ENDPOINTS

from .models import UserPortfolio, PortfolioHolding, TradeTransaction
from django.contrib.auth.decorators import login_required

@api_view(['GET'])
@permission_classes([AllowAny])
def portfolio_value_api(request):
    """
    Get portfolio total value for authenticated user
    URL: /api/portfolio/value/
    """
    try:
        if not request.user.is_authenticated:
            return Response({
                'success': False,
                'error': 'Authentication required'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # Get all portfolios for the user
        portfolios = UserPortfolio.objects.filter(user=request.user)
        
        total_value = sum(portfolio.total_value for portfolio in portfolios)
        portfolio_count = portfolios.count()
        # Limits for display
        limits = get_limits_for_user(request.user)
        
        return Response({
            'success': True,
            'total_value': float(total_value),
            'portfolio_count': portfolio_count,
            'limits': {
                'portfolios': limits.get('portfolios'),
            },
            'portfolios': [
                {
                    'id': p.id,
                    'name': p.name,
                    'value': float(p.total_value),
                    'return_percent': float(p.total_return_percent)
                } for p in portfolios
            ],
            'timestamp': timezone.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in portfolio_value_api: {e}", exc_info=True)
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
def portfolio_pnl_api(request):
    """
    Get portfolio total P&L for authenticated user
    URL: /api/portfolio/pnl/
    """
    try:
        if not request.user.is_authenticated:
            return Response({
                'success': False,
                'error': 'Authentication required'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # Get all portfolios for the user
        portfolios = UserPortfolio.objects.filter(user=request.user)
        
        total_return = sum(portfolio.total_return for portfolio in portfolios)
        total_cost = sum(portfolio.total_cost for portfolio in portfolios)
        total_value = sum(portfolio.total_value for portfolio in portfolios)
        
        # Calculate overall return percentage
        overall_return_percent = (total_return / total_cost * 100) if total_cost > 0 else 0
        
        return Response({
            'success': True,
            'total_pnl': float(total_return),
            'total_cost': float(total_cost),
            'total_value': float(total_value),
            'return_percent': float(overall_return_percent),
            'portfolios': [
                {
                    'id': p.id,
                    'name': p.name,
                    'pnl': float(p.total_return),
                    'return_percent': float(p.total_return_percent),
                    'cost': float(p.total_cost),
                    'value': float(p.total_value)
                } for p in portfolios
            ],
            'timestamp': timezone.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in portfolio_pnl_api: {e}", exc_info=True)
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
def portfolio_return_api(request):
    """
    Get portfolio total return for authenticated user
    URL: /api/portfolio/return/
    """
    try:
        if not request.user.is_authenticated:
            return Response({
                'success': False,
                'error': 'Authentication required'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # Get all portfolios for the user
        portfolios = UserPortfolio.objects.filter(user=request.user)
        
        total_return = sum(portfolio.total_return for portfolio in portfolios)
        total_cost = sum(portfolio.total_cost for portfolio in portfolios)
        
        # Calculate overall return percentage
        overall_return_percent = (total_return / total_cost * 100) if total_cost > 0 else 0
        
        return Response({
            'success': True,
            'total_return': float(total_return),
            'return_percent': float(overall_return_percent),
            'portfolios': [
                {
                    'id': p.id,
                    'name': p.name,
                    'return_amount': float(p.total_return),
                    'return_percent': float(p.total_return_percent)
                } for p in portfolios
            ],
            'timestamp': timezone.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in portfolio_return_api: {e}", exc_info=True)
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
def portfolio_holdings_count_api(request):
    """
    Get number of holdings in user's portfolios
    URL: /api/portfolio/holdings-count/
    """
    try:
        if not request.user.is_authenticated:
            return Response({
                'success': False,
                'error': 'Authentication required'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # Get all portfolios for the user
        portfolios = UserPortfolio.objects.filter(user=request.user)
        
        total_holdings = 0
        portfolio_details = []
        
        for portfolio in portfolios:
            holdings_count = PortfolioHolding.objects.filter(portfolio=portfolio).count()
            total_holdings += holdings_count
            
            portfolio_details.append({
                'id': portfolio.id,
                'name': portfolio.name,
                'holdings_count': holdings_count
            })
        
        limits = get_limits_for_user(request.user)
        return Response({
            'success': True,
            'total_holdings': total_holdings,
            'portfolio_count': portfolios.count(),
            'limits': {
                'portfolios': limits.get('portfolios'),
            },
            'portfolios': portfolio_details,
            'timestamp': timezone.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in portfolio_holdings_count_api: {e}", exc_info=True)
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Helper functions - moved to utils for better organization
