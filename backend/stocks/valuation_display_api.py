"""
Enhanced Valuation Display API - Feature 4
Aesthetic displays of fair value vs real value and all metrics comparisons
"""
import json
from decimal import Decimal
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.cache import cache
import yfinance as yf
from .models import Stock, StockFundamentals


def _safe_float(value, decimals=4):
    """Safely convert to float and round"""
    if value is None:
        return None
    try:
        return round(float(value), decimals)
    except:
        return None


def _calculate_fair_value_summary(stock, fundamentals):
    """
    Calculate comprehensive fair value summary with multiple methods.
    """
    current_price = _safe_float(stock.current_price, 2)
    if not current_price or current_price <= 0:
        return None
    
    fair_values = {}
    
    # DCF Fair Value
    dcf = _safe_float(fundamentals.dcf_value, 2) if fundamentals else None
    if dcf and dcf > 0:
        fair_values['dcf'] = {
            'value': dcf,
            'upside': round(((dcf / current_price) - 1) * 100, 2),
            'status': 'undervalued' if dcf > current_price else 'overvalued',
            'method': 'Discounted Cash Flow',
            'description': 'Projects future cash flows and discounts to present value'
        }
    
    # EPV Fair Value
    epv = _safe_float(fundamentals.epv_value, 2) if fundamentals else None
    if epv and epv > 0:
        fair_values['epv'] = {
            'value': epv,
            'upside': round(((epv / current_price) - 1) * 100, 2),
            'status': 'undervalued' if epv > current_price else 'overvalued',
            'method': 'Earnings Power Value',
            'description': 'Based on normalized earnings capacity'
        }
    
    # Graham Number
    graham = _safe_float(fundamentals.graham_number, 2) if fundamentals else None
    if graham and graham > 0:
        fair_values['graham'] = {
            'value': graham,
            'upside': round(((graham / current_price) - 1) * 100, 2),
            'status': 'undervalued' if graham > current_price else 'overvalued',
            'method': 'Graham Number',
            'description': 'sqrt(22.5 × EPS × Book Value) - Ben Graham formula'
        }
    
    # PEG Fair Value
    peg_fv = _safe_float(fundamentals.peg_fair_value, 2) if fundamentals else None
    if peg_fv and peg_fv > 0:
        fair_values['peg'] = {
            'value': peg_fv,
            'upside': round(((peg_fv / current_price) - 1) * 100, 2),
            'status': 'undervalued' if peg_fv > current_price else 'overvalued',
            'method': 'PEG-Based Fair Value',
            'description': 'Based on price-to-earnings-growth ratio'
        }
    
    # Calculate weighted average fair value
    if fair_values:
        weights = {'dcf': 0.30, 'epv': 0.25, 'graham': 0.25, 'peg': 0.20}
        total_weight = sum(weights.get(k, 0) for k in fair_values.keys())
        
        if total_weight > 0:
            weighted_fv = sum(
                fv['value'] * weights.get(k, 0) / total_weight 
                for k, fv in fair_values.items()
            )
            fair_values['weighted_average'] = {
                'value': round(weighted_fv, 2),
                'upside': round(((weighted_fv / current_price) - 1) * 100, 2),
                'status': 'undervalued' if weighted_fv > current_price else 'overvalued',
                'method': 'Weighted Average',
                'description': 'Weighted average of all fair value methods'
            }
    
    return fair_values


def _calculate_margin_of_safety(current_price, fair_values):
    """
    Calculate margin of safety based on average fair value.
    """
    if not fair_values or not current_price:
        return None
    
    values = [fv['value'] for fv in fair_values.values() if fv.get('value')]
    if not values:
        return None
    
    avg_fair_value = sum(values) / len(values)
    margin = ((avg_fair_value - current_price) / avg_fair_value) * 100
    
    return {
        'percentage': round(margin, 2),
        'interpretation': (
            'Excellent (>30%)' if margin > 30 else
            'Good (20-30%)' if margin > 20 else
            'Moderate (10-20%)' if margin > 10 else
            'Low (0-10%)' if margin > 0 else
            'Negative - Potentially Overvalued'
        ),
        'is_safe': margin > 15
    }


@csrf_exempt
@require_http_methods(["GET"])
def get_valuation_display(request, ticker):
    """
    GET /api/valuation/<ticker>/display/
    
    Get comprehensive valuation display with fair value vs real value comparison.
    """
    try:
        ticker = ticker.upper().strip()
        
        # Cache key
        cache_key = f'valuation_display_{ticker}'
        cached = cache.get(cache_key)
        if cached:
            return JsonResponse({'success': True, 'data': cached, 'cached': True})
        
        stock = Stock.objects.filter(ticker=ticker).first()
        if not stock:
            return JsonResponse({
                'success': False,
                'error': f'Stock {ticker} not found'
            }, status=404)
        
        current_price = _safe_float(stock.current_price, 2)
        
        # Get fundamentals
        try:
            fundamentals = stock.fundamentals
        except:
            fundamentals = None
        
        # Build response
        data = {
            'ticker': ticker,
            'company_name': stock.company_name,
            'current_price': current_price,
            'price_change': _safe_float(stock.price_change, 2),
            'price_change_percent': _safe_float(stock.price_change_percent or stock.change_percent, 2),
            
            # Fair Value Analysis
            'fair_values': _calculate_fair_value_summary(stock, fundamentals) if fundamentals else {},
            
            # Key Valuation Metrics
            'valuation_metrics': {
                'pe_ratio': {
                    'value': _safe_float(fundamentals.pe_ratio if fundamentals else stock.pe_ratio),
                    'label': 'P/E Ratio',
                    'benchmark': 15,
                    'interpretation': 'Lower is better (generally)'
                },
                'forward_pe': {
                    'value': _safe_float(fundamentals.forward_pe) if fundamentals else None,
                    'label': 'Forward P/E',
                    'benchmark': 15,
                    'interpretation': 'Based on estimated future earnings'
                },
                'peg_ratio': {
                    'value': _safe_float(fundamentals.peg_ratio) if fundamentals else None,
                    'label': 'PEG Ratio',
                    'benchmark': 1.0,
                    'interpretation': '<1 may indicate undervaluation relative to growth'
                },
                'price_to_book': {
                    'value': _safe_float(fundamentals.price_to_book if fundamentals else stock.price_to_book),
                    'label': 'Price/Book',
                    'benchmark': 1.5,
                    'interpretation': '<1 may indicate undervaluation'
                },
                'price_to_sales': {
                    'value': _safe_float(fundamentals.price_to_sales) if fundamentals else None,
                    'label': 'Price/Sales',
                    'benchmark': 2.0,
                    'interpretation': 'Lower is generally better'
                },
                'ev_to_ebitda': {
                    'value': _safe_float(fundamentals.ev_to_ebitda) if fundamentals else None,
                    'label': 'EV/EBITDA',
                    'benchmark': 10.0,
                    'interpretation': 'Lower may indicate undervaluation'
                }
            },
            
            # Quality Metrics
            'quality_metrics': {
                'roe': {
                    'value': _safe_float(fundamentals.roe) if fundamentals else None,
                    'label': 'Return on Equity',
                    'benchmark': 0.15,
                    'interpretation': 'Higher is better (>15% is good)',
                    'format': 'percent'
                },
                'roa': {
                    'value': _safe_float(fundamentals.roa) if fundamentals else None,
                    'label': 'Return on Assets',
                    'benchmark': 0.05,
                    'interpretation': 'Higher is better (>5% is good)',
                    'format': 'percent'
                },
                'profit_margin': {
                    'value': _safe_float(fundamentals.profit_margin) if fundamentals else None,
                    'label': 'Profit Margin',
                    'benchmark': 0.10,
                    'interpretation': 'Higher is better',
                    'format': 'percent'
                },
                'gross_margin': {
                    'value': _safe_float(fundamentals.gross_margin) if fundamentals else None,
                    'label': 'Gross Margin',
                    'benchmark': 0.40,
                    'interpretation': 'Higher indicates pricing power',
                    'format': 'percent'
                }
            },
            
            # Financial Health
            'health_metrics': {
                'current_ratio': {
                    'value': _safe_float(fundamentals.current_ratio) if fundamentals else None,
                    'label': 'Current Ratio',
                    'benchmark': 1.5,
                    'interpretation': '>1.5 indicates good liquidity'
                },
                'quick_ratio': {
                    'value': _safe_float(fundamentals.quick_ratio) if fundamentals else None,
                    'label': 'Quick Ratio',
                    'benchmark': 1.0,
                    'interpretation': '>1 indicates strong liquidity'
                },
                'debt_to_equity': {
                    'value': _safe_float(fundamentals.debt_to_equity) if fundamentals else None,
                    'label': 'Debt/Equity',
                    'benchmark': 0.5,
                    'interpretation': 'Lower is better (<0.5 is conservative)'
                },
                'interest_coverage': {
                    'value': _safe_float(fundamentals.interest_coverage) if fundamentals else None,
                    'label': 'Interest Coverage',
                    'benchmark': 5.0,
                    'interpretation': '>5x is considered safe'
                }
            },
            
            # Growth Metrics
            'growth_metrics': {
                'revenue_growth_yoy': {
                    'value': _safe_float(fundamentals.revenue_growth_yoy) if fundamentals else None,
                    'label': 'Revenue Growth YoY',
                    'benchmark': 0.10,
                    'format': 'percent'
                },
                'earnings_growth_yoy': {
                    'value': _safe_float(fundamentals.earnings_growth_yoy) if fundamentals else None,
                    'label': 'Earnings Growth YoY',
                    'benchmark': 0.10,
                    'format': 'percent'
                },
                'revenue_growth_5y': {
                    'value': _safe_float(fundamentals.revenue_growth_5y) if fundamentals else None,
                    'label': '5Y Revenue CAGR',
                    'benchmark': 0.08,
                    'format': 'percent'
                }
            },
            
            # Dividend Info
            'dividend': {
                'yield': _safe_float(fundamentals.dividend_yield if fundamentals else stock.dividend_yield),
                'payout_ratio': _safe_float(fundamentals.dividend_payout_ratio) if fundamentals else None,
                'years_growth': fundamentals.years_dividend_growth if fundamentals else None
            } if (fundamentals and fundamentals.dividend_yield) or stock.dividend_yield else None,
            
            # Scores and Summary
            'scores': {
                'valuation_score': _safe_float(fundamentals.valuation_score) if fundamentals else None,
                'valuation_status': fundamentals.valuation_status if fundamentals else None,
                'recommendation': fundamentals.recommendation if fundamentals else None,
                'strength_score': _safe_float(fundamentals.strength_score) if fundamentals else None,
                'strength_grade': fundamentals.strength_grade if fundamentals else None
            },
            
            # Classification
            'classification': {
                'sector': fundamentals.sector if fundamentals else None,
                'industry': fundamentals.industry if fundamentals else None,
                'exchange': stock.exchange
            },
            
            # Price Targets
            'price_context': {
                'week_52_high': _safe_float(stock.week_52_high, 2),
                'week_52_low': _safe_float(stock.week_52_low, 2),
                'target_price': _safe_float(stock.one_year_target, 2),
                'from_52_high': round(((current_price / _safe_float(stock.week_52_high, 2)) - 1) * 100, 2) if stock.week_52_high and current_price else None,
                'from_52_low': round(((current_price / _safe_float(stock.week_52_low, 2)) - 1) * 100, 2) if stock.week_52_low and current_price else None
            }
        }
        
        # Calculate margin of safety
        if data['fair_values']:
            data['margin_of_safety'] = _calculate_margin_of_safety(current_price, data['fair_values'])
        
        # Cache for 15 minutes
        cache.set(cache_key, data, 900)
        
        return JsonResponse({'success': True, 'data': data, 'cached': False})
    
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_valuation_comparison(request):
    """
    GET /api/valuation/compare/
    
    Compare valuation metrics across multiple stocks.
    
    Query params:
    - symbols: comma-separated list of symbols
    """
    try:
        symbols_str = request.GET.get('symbols', '')
        symbols = [s.strip().upper() for s in symbols_str.split(',') if s.strip()][:10]
        
        if len(symbols) < 2:
            return JsonResponse({
                'success': False,
                'error': 'At least 2 symbols required'
            }, status=400)
        
        stocks_data = []
        for symbol in symbols:
            stock = Stock.objects.filter(ticker=symbol).select_related('fundamentals').first()
            if stock:
                try:
                    fundamentals = stock.fundamentals
                except:
                    fundamentals = None
                
                stock_data = {
                    'ticker': stock.ticker,
                    'company_name': stock.company_name,
                    'current_price': _safe_float(stock.current_price, 2),
                    'fair_values': _calculate_fair_value_summary(stock, fundamentals) if fundamentals else {},
                    'pe_ratio': _safe_float(fundamentals.pe_ratio if fundamentals else stock.pe_ratio),
                    'peg_ratio': _safe_float(fundamentals.peg_ratio) if fundamentals else None,
                    'price_to_book': _safe_float(fundamentals.price_to_book if fundamentals else stock.price_to_book),
                    'roe': _safe_float(fundamentals.roe) if fundamentals else None,
                    'profit_margin': _safe_float(fundamentals.profit_margin) if fundamentals else None,
                    'valuation_score': _safe_float(fundamentals.valuation_score) if fundamentals else None,
                    'strength_score': _safe_float(fundamentals.strength_score) if fundamentals else None,
                    'sector': fundamentals.sector if fundamentals else None
                }
                stocks_data.append(stock_data)
        
        if len(stocks_data) < 2:
            return JsonResponse({
                'success': False,
                'error': 'Not enough valid stocks found'
            }, status=404)
        
        return JsonResponse({
            'success': True,
            'data': {
                'stocks': stocks_data,
                'count': len(stocks_data)
            }
        })
    
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_sector_valuation(request, sector):
    """
    GET /api/valuation/sector/<sector>/
    
    Get average valuation metrics for a sector.
    """
    try:
        from django.db.models import Avg, Count
        
        stocks = Stock.objects.filter(
            fundamentals__sector__iexact=sector
        ).select_related('fundamentals')
        
        if not stocks.exists():
            return JsonResponse({
                'success': False,
                'error': f'No stocks found in sector: {sector}'
            }, status=404)
        
        # Calculate averages
        aggregates = StockFundamentals.objects.filter(
            sector__iexact=sector
        ).aggregate(
            avg_pe=Avg('pe_ratio'),
            avg_pb=Avg('price_to_book'),
            avg_roe=Avg('roe'),
            avg_profit_margin=Avg('profit_margin'),
            avg_valuation_score=Avg('valuation_score'),
            avg_strength_score=Avg('strength_score'),
            count=Count('stock')
        )
        
        # Get top stocks by valuation score
        top_stocks = stocks.order_by('-fundamentals__valuation_score')[:10]
        
        return JsonResponse({
            'success': True,
            'data': {
                'sector': sector,
                'stock_count': aggregates['count'],
                'averages': {
                    'pe_ratio': _safe_float(aggregates['avg_pe']),
                    'price_to_book': _safe_float(aggregates['avg_pb']),
                    'roe': _safe_float(aggregates['avg_roe']),
                    'profit_margin': _safe_float(aggregates['avg_profit_margin']),
                    'valuation_score': _safe_float(aggregates['avg_valuation_score']),
                    'strength_score': _safe_float(aggregates['avg_strength_score'])
                },
                'top_undervalued': [
                    {
                        'ticker': s.ticker,
                        'company_name': s.company_name,
                        'current_price': _safe_float(s.current_price, 2),
                        'valuation_score': _safe_float(s.fundamentals.valuation_score) if hasattr(s, 'fundamentals') else None
                    }
                    for s in top_stocks
                ]
            }
        })
    
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
