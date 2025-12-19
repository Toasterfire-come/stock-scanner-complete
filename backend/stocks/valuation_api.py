"""
Enhanced Valuation API - Complete valuation analysis with multiple models.
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.core.cache import cache
from django.shortcuts import get_object_or_404
from decimal import Decimal
import yfinance as yf

from .models import Stock
from .services.valuation_service import ValuationService, get_sector_medians


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


@api_view(['GET'])
@permission_classes([AllowAny])
def get_stock_valuation(request, ticker):
    """
    GET /api/valuation/{ticker}/
    
    Returns comprehensive valuation analysis including:
    - DCF value
    - EPV value
    - Graham Number
    - PEG Fair Value
    - Relative Value vs sector
    - Composite valuation score (0-100)
    - Strength score (0-100)
    - Recommendation
    """
    try:
        ticker = ticker.upper().strip()
        
        # Check cache (10 minute TTL)
        cache_key = f'valuation_{ticker}'
        cached = cache.get(cache_key)
        if cached:
            return Response({
                'success': True,
                'ticker': ticker,
                'data': cached,
                'cached': True
            })
        
        # Fetch data from yfinance
        yf_ticker = yf.Ticker(ticker)
        info = yf_ticker.info
        
        if not info or 'currentPrice' not in info:
            return Response({
                'success': False,
                'error': 'Stock not found or no data available'
            }, status=404)
        
        # Extract needed values
        current_price = _safe_float(info.get('currentPrice')) or _safe_float(info.get('regularMarketPrice'))
        if not current_price:
            return Response({
                'success': False,
                'error': 'Unable to get current price'
            }, status=404)
        
        eps = _safe_float(info.get('trailingEps'))
        book_value = _safe_float(info.get('bookValue'))
        fcf = _safe_float(info.get('freeCashflow'))
        shares = _safe_float(info.get('sharesOutstanding')) or 1
        ebit = _safe_float(info.get('ebit'))
        total_debt = _safe_float(info.get('totalDebt')) or 0
        total_cash = _safe_float(info.get('totalCash')) or 0
        growth_rate = _safe_float(info.get('earningsGrowth')) or 0.10
        sector = info.get('sector', 'default')
        
        # Valuation metrics for relative comparison
        pe_ratio = _safe_float(info.get('trailingPE'))
        price_to_book = _safe_float(info.get('priceToBook'))
        ev_to_ebitda = _safe_float(info.get('enterpriseToEbitda'))
        price_to_sales = _safe_float(info.get('priceToSalesTrailing12Months'))
        
        # Strength score inputs
        roe = _safe_float(info.get('returnOnEquity'))
        profit_margin = _safe_float(info.get('profitMargins'))
        revenue_growth = _safe_float(info.get('revenueGrowth'))
        earnings_growth = _safe_float(info.get('earningsGrowth'))
        current_ratio = _safe_float(info.get('currentRatio'))
        debt_to_equity = _safe_float(info.get('debtToEquity'))
        if debt_to_equity:
            debt_to_equity = debt_to_equity / 100  # Convert from percentage
        
        market_cap = _safe_float(info.get('marketCap')) or 1
        fcf_yield = (fcf / market_cap) if fcf and market_cap else None
        
        # Calculate cash conversion (FCF / Net Income)
        net_income = _safe_float(info.get('netIncomeToCommon'))
        cash_conversion = (fcf / net_income) if fcf and net_income and net_income > 0 else None
        
        # Initialize valuation service
        service = ValuationService()
        
        # Calculate each valuation model
        dcf_result = None
        epv_result = None
        graham_result = None
        peg_result = None
        relative_result = None
        
        # DCF
        if fcf and fcf > 0:
            dcf_result = service.calculate_dcf(
                fcf=fcf,
                shares=shares,
                growth_rate=max(0.05, min(growth_rate, 0.25)),
                discount_rate=0.10,
                terminal_growth=0.025
            )
        
        # EPV
        if ebit and ebit > 0:
            epv_result = service.calculate_epv(
                ebit=ebit,
                tax_rate=0.25,
                cost_of_capital=0.10,
                shares=shares,
                debt=total_debt,
                cash=total_cash
            )
        
        # Graham Number
        if eps and eps > 0 and book_value and book_value > 0:
            graham_result = service.calculate_graham_number(eps, book_value)
        
        # PEG Fair Value
        if eps and eps > 0 and growth_rate and growth_rate > 0:
            peg_result = service.calculate_peg_fair_value(eps, growth_rate)
        
        # Relative Value
        stock_metrics = {
            'pe_ratio': pe_ratio,
            'price_to_book': price_to_book,
            'ev_to_ebitda': ev_to_ebitda,
            'price_to_sales': price_to_sales
        }
        sector_medians = get_sector_medians(sector)
        if any(v for v in stock_metrics.values() if v):
            relative_result = service.calculate_relative_value(stock_metrics, sector_medians)
        
        # Composite Score
        composite_result = service.calculate_composite_score(
            current_price=current_price,
            dcf_value=dcf_result.get('dcf_value') if dcf_result else None,
            epv_value=epv_result.get('epv_value') if epv_result else None,
            graham_number=graham_result.get('graham_number') if graham_result else None,
            peg_fair_value=peg_result.get('peg_fair_value') if peg_result else None,
            relative_score=relative_result.get('relative_score') if relative_result else None
        )
        
        # Strength Score
        strength_result = service.calculate_strength_score({
            'roe': roe,
            'profit_margin': profit_margin,
            'revenue_growth_yoy': revenue_growth,
            'earnings_growth_yoy': earnings_growth,
            'current_ratio': current_ratio,
            'debt_to_equity': debt_to_equity,
            'fcf_yield': fcf_yield,
            'cash_conversion': cash_conversion
        })
        
        # Build response
        response_data = {
            'ticker': ticker,
            'company_name': info.get('shortName', ticker),
            'sector': sector,
            'current_price': current_price,
            
            # Valuation Models
            'models': {
                'dcf': dcf_result,
                'epv': epv_result,
                'graham_number': graham_result,
                'peg_fair_value': peg_result,
                'relative_value': relative_result
            },
            
            # Composite Scores
            'valuation_score': composite_result.get('composite_score'),
            'valuation_status': composite_result.get('status'),
            'recommendation': composite_result.get('recommendation'),
            'confidence': composite_result.get('confidence'),
            'valuation_breakdown': composite_result.get('breakdown'),
            
            # Strength Score
            'strength_score': strength_result.get('strength_score'),
            'strength_grade': strength_result.get('grade'),
            'strength_breakdown': strength_result.get('breakdown'),
            
            # Key Metrics Used
            'metrics': {
                'pe_ratio': pe_ratio,
                'forward_pe': _safe_float(info.get('forwardPE')),
                'peg_ratio': _safe_float(info.get('pegRatio')),
                'price_to_book': price_to_book,
                'price_to_sales': price_to_sales,
                'ev_to_ebitda': ev_to_ebitda,
                'roe': round(roe * 100, 2) if roe else None,
                'profit_margin': round(profit_margin * 100, 2) if profit_margin else None,
                'debt_to_equity': round(debt_to_equity * 100, 2) if debt_to_equity else None,
                'current_ratio': current_ratio,
                'fcf_yield': round(fcf_yield * 100, 2) if fcf_yield else None,
                'dividend_yield': round(_safe_float(info.get('dividendYield')) * 100, 2) if info.get('dividendYield') else None
            },
            
            # Analyst Data
            'analyst': {
                'target_mean': _safe_float(info.get('targetMeanPrice')),
                'target_high': _safe_float(info.get('targetHighPrice')),
                'target_low': _safe_float(info.get('targetLowPrice')),
                'num_analysts': info.get('numberOfAnalystOpinions', 0),
                'recommendation': info.get('recommendationKey', 'N/A')
            }
        }
        
        # Cache for 10 minutes
        cache.set(cache_key, response_data, 600)
        
        return Response({
            'success': True,
            'ticker': ticker,
            'data': response_data,
            'cached': False
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_undervalued_screener(request):
    """
    GET /api/screener/undervalued/
    
    Returns top undervalued stocks based on composite valuation score.
    
    Query params:
    - min_score: Minimum valuation score (default: 60)
    - min_market_cap: Minimum market cap in billions (default: 1)
    - sector: Filter by sector (optional)
    - limit: Number of results (default: 20)
    """
    try:
        min_score = float(request.GET.get('min_score', 60))
        min_market_cap = float(request.GET.get('min_market_cap', 1)) * 1e9
        sector = request.GET.get('sector')
        limit = int(request.GET.get('limit', 20))
        
        # Get stocks from database that meet basic criteria
        stocks_qs = Stock.objects.filter(
            market_cap__gte=min_market_cap
        )
        
        if sector:
            stocks_qs = stocks_qs.filter(sector__icontains=sector)
        
        # Limit initial query
        stocks = stocks_qs[:100]
        
        # Calculate valuation for each
        results = []
        service = ValuationService()
        
        for stock in stocks:
            try:
                # Quick valuation check using stored data
                if stock.pe_ratio and stock.book_value and stock.earnings_per_share:
                    eps = float(stock.earnings_per_share) if stock.earnings_per_share else 0
                    bv = float(stock.book_value) if stock.book_value else 0
                    price = float(stock.current_price) if stock.current_price else 0
                    
                    if eps > 0 and bv > 0 and price > 0:
                        graham = service.calculate_graham_number(eps, bv)
                        if graham:
                            graham_val = graham.get('graham_number', 0)
                            margin = ((graham_val / price) - 1) * 100 if price > 0 else 0
                            score = 50 + margin  # Simple score approximation
                            
                            if score >= min_score:
                                results.append({
                                    'ticker': stock.ticker,
                                    'company_name': stock.company_name,
                                    'current_price': price,
                                    'graham_number': graham_val,
                                    'margin_of_safety': round(margin, 1),
                                    'estimated_score': round(max(0, min(100, score)), 1),
                                    'pe_ratio': float(stock.pe_ratio) if stock.pe_ratio else None,
                                    'market_cap': stock.market_cap
                                })
            except Exception:
                continue
        
        # Sort by score and limit
        results.sort(key=lambda x: x.get('estimated_score', 0), reverse=True)
        results = results[:limit]
        
        return Response({
            'success': True,
            'count': len(results),
            'filters': {
                'min_score': min_score,
                'min_market_cap': min_market_cap / 1e9,
                'sector': sector
            },
            'stocks': results
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_quick_valuation(request, ticker):
    """
    GET /api/valuation/{ticker}/quick/
    
    Returns quick valuation summary (lighter weight).
    """
    try:
        ticker = ticker.upper().strip()
        
        # Check cache
        cache_key = f'quick_val_{ticker}'
        cached = cache.get(cache_key)
        if cached:
            return Response({'success': True, 'data': cached, 'cached': True})
        
        yf_ticker = yf.Ticker(ticker)
        info = yf_ticker.info
        
        if not info:
            return Response({'success': False, 'error': 'Stock not found'}, status=404)
        
        current_price = _safe_float(info.get('currentPrice')) or _safe_float(info.get('regularMarketPrice'))
        eps = _safe_float(info.get('trailingEps'))
        book_value = _safe_float(info.get('bookValue'))
        target_mean = _safe_float(info.get('targetMeanPrice'))
        
        service = ValuationService()
        graham = None
        if eps and eps > 0 and book_value and book_value > 0:
            graham_result = service.calculate_graham_number(eps, book_value)
            graham = graham_result.get('graham_number') if graham_result else None
        
        # Simple status based on Graham Number
        status = 'unknown'
        if graham and current_price:
            margin = ((graham / current_price) - 1) * 100
            if margin > 30:
                status = 'significantly_undervalued'
            elif margin > 10:
                status = 'undervalued'
            elif margin > -10:
                status = 'fair_value'
            elif margin > -30:
                status = 'overvalued'
            else:
                status = 'significantly_overvalued'
        
        result = {
            'ticker': ticker,
            'current_price': current_price,
            'graham_number': graham,
            'analyst_target': target_mean,
            'pe_ratio': _safe_float(info.get('trailingPE')),
            'status': status,
            'margin_of_safety': round(((graham / current_price) - 1) * 100, 1) if graham and current_price else None
        }
        
        cache.set(cache_key, result, 300)  # 5 min cache
        
        return Response({'success': True, 'data': result, 'cached': False})
        
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=500)
