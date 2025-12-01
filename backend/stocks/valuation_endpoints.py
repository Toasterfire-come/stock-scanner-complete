"""
Additional Valuation Endpoints for Phase 2 MVP
Includes fundamentals sync and sector-based analysis.
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.core.cache import cache
from django.db.models import Avg, Count, Q
import yfinance as yf
from decimal import Decimal

from .models import Stock, StockFundamentals
from .services.valuation_service import ValuationService, get_sector_medians, SECTOR_MEDIANS


def _safe_float(value):
    """Safely convert value to float."""
    if value is None:
        return None
    try:
        if isinstance(value, (int, float, Decimal)):
            return float(value)
        return float(value)
    except (ValueError, TypeError):
        return None


def _safe_decimal(value):
    """Safely convert value to Decimal."""
    if value is None:
        return None
    try:
        return Decimal(str(value))
    except:
        return None


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def sync_stock_fundamentals(request, ticker):
    """
    POST /api/fundamentals/{ticker}/sync/
    
    Fetches fundamentals from yfinance and stores in StockFundamentals model.
    Calculates all valuation scores.
    """
    try:
        ticker = ticker.upper().strip()
        
        # Get or create stock
        stock, _ = Stock.objects.get_or_create(
            ticker=ticker,
            defaults={'symbol': ticker, 'company_name': ticker, 'name': ticker}
        )
        
        # Fetch from yfinance
        yf_ticker = yf.Ticker(ticker)
        info = yf_ticker.info
        
        if not info or not info.get('currentPrice'):
            return Response({
                'success': False,
                'error': 'Unable to fetch stock data'
            }, status=404)
        
        # Update stock price
        stock.current_price = _safe_decimal(info.get('currentPrice') or info.get('regularMarketPrice'))
        stock.company_name = info.get('shortName', ticker)
        stock.name = info.get('shortName', ticker)
        stock.pe_ratio = _safe_decimal(info.get('trailingPE'))
        stock.book_value = _safe_decimal(info.get('bookValue'))
        stock.earnings_per_share = _safe_decimal(info.get('trailingEps'))
        stock.market_cap = info.get('marketCap')
        stock.save()
        
        # Get or create fundamentals
        fundamentals, created = StockFundamentals.objects.get_or_create(stock=stock)
        
        # Update all fundamental fields
        fundamentals.pe_ratio = _safe_decimal(info.get('trailingPE'))
        fundamentals.forward_pe = _safe_decimal(info.get('forwardPE'))
        fundamentals.peg_ratio = _safe_decimal(info.get('pegRatio'))
        fundamentals.price_to_sales = _safe_decimal(info.get('priceToSalesTrailing12Months'))
        fundamentals.price_to_book = _safe_decimal(info.get('priceToBook'))
        fundamentals.ev_to_revenue = _safe_decimal(info.get('enterpriseToRevenue'))
        fundamentals.ev_to_ebitda = _safe_decimal(info.get('enterpriseToEbitda'))
        fundamentals.enterprise_value = info.get('enterpriseValue')
        
        # Profitability
        fundamentals.gross_margin = _safe_decimal(info.get('grossMargins'))
        fundamentals.operating_margin = _safe_decimal(info.get('operatingMargins'))
        fundamentals.profit_margin = _safe_decimal(info.get('profitMargins'))
        fundamentals.roe = _safe_decimal(info.get('returnOnEquity'))
        fundamentals.roa = _safe_decimal(info.get('returnOnAssets'))
        
        # Growth
        fundamentals.revenue_growth_yoy = _safe_decimal(info.get('revenueGrowth'))
        fundamentals.earnings_growth_yoy = _safe_decimal(info.get('earningsGrowth'))
        
        # Financial Health
        fundamentals.current_ratio = _safe_decimal(info.get('currentRatio'))
        fundamentals.quick_ratio = _safe_decimal(info.get('quickRatio'))
        debt_to_equity = _safe_float(info.get('debtToEquity'))
        if debt_to_equity:
            fundamentals.debt_to_equity = _safe_decimal(debt_to_equity / 100)
        
        # Cash Flow
        fundamentals.operating_cash_flow = info.get('operatingCashflow')
        fundamentals.free_cash_flow = info.get('freeCashflow')
        
        shares = _safe_float(info.get('sharesOutstanding')) or 1
        fcf = _safe_float(info.get('freeCashflow'))
        if fcf and shares:
            fundamentals.fcf_per_share = _safe_decimal(fcf / shares)
        
        market_cap = _safe_float(info.get('marketCap')) or 1
        if fcf and market_cap:
            fundamentals.fcf_yield = _safe_decimal(fcf / market_cap)
        
        # Dividends
        fundamentals.dividend_yield = _safe_decimal(info.get('dividendYield'))
        fundamentals.dividend_payout_ratio = _safe_decimal(info.get('payoutRatio'))
        
        # Sector/Industry
        sector = info.get('sector', '')
        fundamentals.sector = sector
        fundamentals.industry = info.get('industry', '')
        
        # Calculate valuation scores
        service = ValuationService()
        current_price = float(stock.current_price) if stock.current_price else 0
        eps = _safe_float(info.get('trailingEps'))
        book_value = _safe_float(info.get('bookValue'))
        growth_rate = _safe_float(info.get('earningsGrowth')) or 0.10
        ebit = _safe_float(info.get('ebit'))
        total_debt = _safe_float(info.get('totalDebt')) or 0
        total_cash = _safe_float(info.get('totalCash')) or 0
        
        dcf_value = None
        epv_value = None
        graham_number = None
        peg_fair_value = None
        relative_score = None
        
        # DCF
        if fcf and fcf > 0:
            dcf_result = service.calculate_dcf(
                fcf=fcf, shares=shares,
                growth_rate=max(0.05, min(growth_rate, 0.25)),
                discount_rate=0.10, terminal_growth=0.025
            )
            if dcf_result:
                dcf_value = dcf_result.get('dcf_value')
                fundamentals.dcf_value = _safe_decimal(dcf_value)
        
        # EPV
        if ebit and ebit > 0:
            epv_result = service.calculate_epv(
                ebit=ebit, tax_rate=0.25, cost_of_capital=0.10,
                shares=shares, debt=total_debt, cash=total_cash
            )
            if epv_result:
                epv_value = epv_result.get('epv_value')
                fundamentals.epv_value = _safe_decimal(epv_value)
        
        # Graham Number
        if eps and eps > 0 and book_value and book_value > 0:
            graham_result = service.calculate_graham_number(eps, book_value)
            if graham_result:
                graham_number = graham_result.get('graham_number')
                fundamentals.graham_number = _safe_decimal(graham_number)
        
        # PEG Fair Value
        if eps and eps > 0 and growth_rate and growth_rate > 0:
            peg_result = service.calculate_peg_fair_value(eps, growth_rate)
            if peg_result:
                peg_fair_value = peg_result.get('peg_fair_value')
                fundamentals.peg_fair_value = _safe_decimal(peg_fair_value)
        
        # Relative Value
        stock_metrics = {
            'pe_ratio': _safe_float(info.get('trailingPE')),
            'price_to_book': _safe_float(info.get('priceToBook')),
            'ev_to_ebitda': _safe_float(info.get('enterpriseToEbitda')),
            'price_to_sales': _safe_float(info.get('priceToSalesTrailing12Months'))
        }
        sector_medians = get_sector_medians(sector)
        if any(v for v in stock_metrics.values() if v):
            relative_result = service.calculate_relative_value(stock_metrics, sector_medians)
            if relative_result:
                relative_score = relative_result.get('relative_score')
                fundamentals.relative_value_score = _safe_decimal(relative_score)
        
        # Composite Score
        if current_price > 0:
            composite_result = service.calculate_composite_score(
                current_price=current_price,
                dcf_value=dcf_value,
                epv_value=epv_value,
                graham_number=graham_number,
                peg_fair_value=peg_fair_value,
                relative_score=relative_score
            )
            fundamentals.valuation_score = _safe_decimal(composite_result.get('composite_score'))
            fundamentals.valuation_status = composite_result.get('status', '')
            fundamentals.recommendation = composite_result.get('recommendation', '')
            fundamentals.confidence = composite_result.get('confidence', '')
        
        # Strength Score
        strength_result = service.calculate_strength_score({
            'roe': _safe_float(info.get('returnOnEquity')),
            'profit_margin': _safe_float(info.get('profitMargins')),
            'revenue_growth_yoy': _safe_float(info.get('revenueGrowth')),
            'earnings_growth_yoy': _safe_float(info.get('earningsGrowth')),
            'current_ratio': _safe_float(info.get('currentRatio')),
            'debt_to_equity': (debt_to_equity / 100) if debt_to_equity else None,
            'fcf_yield': float(fundamentals.fcf_yield) if fundamentals.fcf_yield else None,
            'cash_conversion': None  # Would need additional calculation
        })
        fundamentals.strength_score = _safe_decimal(strength_result.get('strength_score'))
        fundamentals.strength_grade = strength_result.get('grade', '')
        
        # Data quality
        fields_filled = sum(1 for f in [
            fundamentals.pe_ratio, fundamentals.price_to_book, fundamentals.roe,
            fundamentals.profit_margin, fundamentals.current_ratio, fundamentals.fcf_yield
        ] if f is not None)
        if fields_filled >= 5:
            fundamentals.data_quality = 'complete'
        elif fields_filled >= 3:
            fundamentals.data_quality = 'partial'
        else:
            fundamentals.data_quality = 'insufficient'
        
        fundamentals.save()
        
        return Response({
            'success': True,
            'ticker': ticker,
            'message': 'Fundamentals synced successfully',
            'data': {
                'valuation_score': float(fundamentals.valuation_score) if fundamentals.valuation_score else None,
                'valuation_status': fundamentals.valuation_status,
                'recommendation': fundamentals.recommendation,
                'strength_score': float(fundamentals.strength_score) if fundamentals.strength_score else None,
                'strength_grade': fundamentals.strength_grade,
                'data_quality': fundamentals.data_quality
            }
        })
        
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_sector_analysis(request):
    """
    GET /api/valuation/sectors/
    
    Returns sector-level valuation analysis and medians.
    """
    try:
        # Get sector stats from database
        sector_stats = StockFundamentals.objects.values('sector').annotate(
            avg_valuation_score=Avg('valuation_score'),
            avg_strength_score=Avg('strength_score'),
            count=Count('stock_id'),
            undervalued_count=Count('stock_id', filter=Q(valuation_score__gte=55))
        ).exclude(sector='').order_by('-avg_valuation_score')
        
        sectors = []
        for stat in sector_stats:
            sector_name = stat['sector']
            medians = SECTOR_MEDIANS.get(sector_name, SECTOR_MEDIANS['default'])
            
            sectors.append({
                'sector': sector_name,
                'avg_valuation_score': round(float(stat['avg_valuation_score']), 1) if stat['avg_valuation_score'] else None,
                'avg_strength_score': round(float(stat['avg_strength_score']), 1) if stat['avg_strength_score'] else None,
                'stock_count': stat['count'],
                'undervalued_count': stat['undervalued_count'],
                'medians': medians
            })
        
        return Response({
            'success': True,
            'data': {
                'sectors': sectors,
                'available_sectors': list(SECTOR_MEDIANS.keys())
            }
        })
        
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_top_value_stocks(request):
    """
    GET /api/valuation/top-value/
    
    Returns top undervalued stocks by valuation score.
    
    Query params:
    - sector: Filter by sector
    - min_market_cap: Minimum market cap in billions
    - limit: Number of results (default: 20)
    """
    try:
        sector = request.GET.get('sector')
        min_market_cap = float(request.GET.get('min_market_cap', 0)) * 1e9
        limit = int(request.GET.get('limit', 20))
        
        # Query stocks with fundamentals
        qs = StockFundamentals.objects.filter(
            valuation_score__gte=55,  # At least "undervalued"
            data_quality__in=['complete', 'partial']
        ).select_related('stock')
        
        if sector:
            qs = qs.filter(sector__icontains=sector)
        
        if min_market_cap > 0:
            qs = qs.filter(stock__market_cap__gte=min_market_cap)
        
        qs = qs.order_by('-valuation_score')[:limit]
        
        stocks = []
        for f in qs:
            stocks.append({
                'ticker': f.stock.ticker,
                'company_name': f.stock.company_name,
                'current_price': float(f.stock.current_price) if f.stock.current_price else None,
                'valuation_score': float(f.valuation_score) if f.valuation_score else None,
                'valuation_status': f.valuation_status,
                'recommendation': f.recommendation,
                'strength_score': float(f.strength_score) if f.strength_score else None,
                'strength_grade': f.strength_grade,
                'sector': f.sector,
                'pe_ratio': float(f.pe_ratio) if f.pe_ratio else None,
                'graham_number': float(f.graham_number) if f.graham_number else None,
                'margin_of_safety': round(((float(f.graham_number) / float(f.stock.current_price)) - 1) * 100, 1) if f.graham_number and f.stock.current_price else None,
                'market_cap': f.stock.market_cap
            })
        
        return Response({
            'success': True,
            'count': len(stocks),
            'filters': {
                'sector': sector,
                'min_market_cap': min_market_cap / 1e9 if min_market_cap else None
            },
            'stocks': stocks
        })
        
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_value_comparison(request):
    """
    GET /api/valuation/compare/
    
    Compare valuations of multiple stocks.
    
    Query params:
    - tickers: Comma-separated list of tickers
    """
    try:
        tickers_param = request.GET.get('tickers', '')
        if not tickers_param:
            return Response({
                'success': False,
                'error': 'Please provide tickers parameter'
            }, status=400)
        
        tickers = [t.strip().upper() for t in tickers_param.split(',')[:10]]  # Max 10
        
        comparisons = []
        for ticker in tickers:
            try:
                fund = StockFundamentals.objects.select_related('stock').get(stock__ticker=ticker)
                comparisons.append({
                    'ticker': ticker,
                    'company_name': fund.stock.company_name,
                    'current_price': float(fund.stock.current_price) if fund.stock.current_price else None,
                    'valuation_score': float(fund.valuation_score) if fund.valuation_score else None,
                    'valuation_status': fund.valuation_status,
                    'recommendation': fund.recommendation,
                    'strength_score': float(fund.strength_score) if fund.strength_score else None,
                    'strength_grade': fund.strength_grade,
                    'pe_ratio': float(fund.pe_ratio) if fund.pe_ratio else None,
                    'price_to_book': float(fund.price_to_book) if fund.price_to_book else None,
                    'roe': float(fund.roe) * 100 if fund.roe else None,
                    'profit_margin': float(fund.profit_margin) * 100 if fund.profit_margin else None,
                    'debt_to_equity': float(fund.debt_to_equity) * 100 if fund.debt_to_equity else None,
                    'dcf_value': float(fund.dcf_value) if fund.dcf_value else None,
                    'graham_number': float(fund.graham_number) if fund.graham_number else None,
                    'sector': fund.sector
                })
            except StockFundamentals.DoesNotExist:
                comparisons.append({
                    'ticker': ticker,
                    'error': 'Fundamentals not found. Please sync first.'
                })
        
        return Response({
            'success': True,
            'count': len(comparisons),
            'comparisons': comparisons
        })
        
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=500)
