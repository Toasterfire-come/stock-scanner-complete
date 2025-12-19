"""
Stock Grouping and Comparison API - Features 5 & 6
Allows grouping stocks, averaging metrics, charting groups, and comparing stocks/groups.
"""
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional
import yfinance as yf
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.cache import cache
from django.db.models import Avg, Sum, Min, Max, Count
from django.db import models
from .models import Stock, StockFundamentals


def _safe_float(value, default=None):
    """Safely convert to float"""
    if value is None:
        return default
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def _calculate_group_metrics(stocks_data: List[Dict]) -> Dict:
    """
    Calculate averaged metrics for a group of stocks.
    """
    if not stocks_data:
        return {}
    
    # Metrics to average
    numeric_fields = [
        'current_price', 'price_change_percent', 'volume', 'market_cap',
        'pe_ratio', 'dividend_yield', 'week_52_high', 'week_52_low',
        # Fundamentals
        'forward_pe', 'peg_ratio', 'price_to_sales', 'price_to_book',
        'gross_margin', 'operating_margin', 'profit_margin', 'roe', 'roa',
        'revenue_growth_yoy', 'earnings_growth_yoy',
        'current_ratio', 'debt_to_equity',
        'dcf_value', 'epv_value', 'graham_number',
        'valuation_score', 'strength_score'
    ]
    
    aggregates = {}
    for field in numeric_fields:
        values = [_safe_float(s.get(field)) for s in stocks_data if s.get(field) is not None]
        if values:
            aggregates[field] = {
                'average': round(sum(values) / len(values), 4),
                'min': round(min(values), 4),
                'max': round(max(values), 4),
                'median': round(sorted(values)[len(values)//2], 4),
                'count': len(values)
            }
    
    # Calculate total market cap
    market_caps = [_safe_float(s.get('market_cap'), 0) for s in stocks_data]
    aggregates['total_market_cap'] = sum(market_caps)
    
    # Calculate weighted average price change (by market cap)
    total_mcap = sum(market_caps)
    if total_mcap > 0:
        weighted_change = sum(
            _safe_float(s.get('price_change_percent'), 0) * _safe_float(s.get('market_cap'), 0)
            for s in stocks_data
        ) / total_mcap
        aggregates['weighted_price_change_percent'] = round(weighted_change, 4)
    
    return aggregates


def _get_stock_data_with_fundamentals(ticker: str) -> Optional[Dict]:
    """
    Get stock data including fundamentals.
    """
    try:
        stock = Stock.objects.filter(ticker=ticker.upper()).first()
        if not stock:
            return None
        
        data = {
            'ticker': stock.ticker,
            'company_name': stock.company_name,
            'current_price': _safe_float(stock.current_price),
            'price_change_percent': _safe_float(stock.price_change_percent or stock.change_percent),
            'volume': stock.volume,
            'market_cap': stock.market_cap,
            'pe_ratio': _safe_float(stock.pe_ratio),
            'dividend_yield': _safe_float(stock.dividend_yield),
            'week_52_high': _safe_float(stock.week_52_high),
            'week_52_low': _safe_float(stock.week_52_low),
        }
        
        # Add fundamentals if available
        try:
            fundamentals = stock.fundamentals
            if fundamentals:
                data.update({
                    'forward_pe': _safe_float(fundamentals.forward_pe),
                    'peg_ratio': _safe_float(fundamentals.peg_ratio),
                    'price_to_sales': _safe_float(fundamentals.price_to_sales),
                    'price_to_book': _safe_float(fundamentals.price_to_book),
                    'gross_margin': _safe_float(fundamentals.gross_margin),
                    'operating_margin': _safe_float(fundamentals.operating_margin),
                    'profit_margin': _safe_float(fundamentals.profit_margin),
                    'roe': _safe_float(fundamentals.roe),
                    'roa': _safe_float(fundamentals.roa),
                    'revenue_growth_yoy': _safe_float(fundamentals.revenue_growth_yoy),
                    'earnings_growth_yoy': _safe_float(fundamentals.earnings_growth_yoy),
                    'current_ratio': _safe_float(fundamentals.current_ratio),
                    'debt_to_equity': _safe_float(fundamentals.debt_to_equity),
                    'dcf_value': _safe_float(fundamentals.dcf_value),
                    'epv_value': _safe_float(fundamentals.epv_value),
                    'graham_number': _safe_float(fundamentals.graham_number),
                    'valuation_score': _safe_float(fundamentals.valuation_score),
                    'valuation_status': fundamentals.valuation_status,
                    'strength_score': _safe_float(fundamentals.strength_score),
                    'strength_grade': fundamentals.strength_grade,
                    'sector': fundamentals.sector,
                    'industry': fundamentals.industry,
                })
        except:
            pass
        
        return data
    except Exception as e:
        print(f"Error getting stock data for {ticker}: {e}")
        return None


@csrf_exempt
@require_http_methods(["POST"])
def create_stock_group(request):
    """
    POST /api/groups/create/
    
    Create a temporary stock group for analysis.
    
    Body:
    {
        "name": "Tech Giants",
        "symbols": ["AAPL", "MSFT", "GOOGL", "AMZN"]
    }
    """
    try:
        data = json.loads(request.body)
        name = data.get('name', 'Unnamed Group')
        symbols = data.get('symbols', [])
        
        if not symbols:
            return JsonResponse({
                'success': False,
                'error': 'At least one symbol is required'
            }, status=400)
        
        # Get stock data for each symbol
        stocks_data = []
        missing_symbols = []
        
        for symbol in symbols:
            stock_data = _get_stock_data_with_fundamentals(symbol)
            if stock_data:
                stocks_data.append(stock_data)
            else:
                missing_symbols.append(symbol)
        
        if not stocks_data:
            return JsonResponse({
                'success': False,
                'error': 'No valid stocks found for provided symbols'
            }, status=404)
        
        # Calculate group metrics
        group_metrics = _calculate_group_metrics(stocks_data)
        
        # Generate group ID
        import hashlib
        group_id = hashlib.md5(f"{name}_{','.join(sorted(symbols))}".encode()).hexdigest()[:12]
        
        # Store in cache for 1 hour
        group_data = {
            'id': group_id,
            'name': name,
            'symbols': [s['ticker'] for s in stocks_data],
            'stocks': stocks_data,
            'metrics': group_metrics,
            'missing_symbols': missing_symbols,
            'count': len(stocks_data),
            'created_at': datetime.now().isoformat()
        }
        
        cache.set(f'stock_group_{group_id}', group_data, 3600)
        
        return JsonResponse({
            'success': True,
            'group': group_data
        })
    
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_stock_group(request, group_id):
    """
    GET /api/groups/<group_id>/
    
    Get a stock group by ID.
    """
    try:
        group_data = cache.get(f'stock_group_{group_id}')
        
        if not group_data:
            return JsonResponse({
                'success': False,
                'error': 'Group not found or expired'
            }, status=404)
        
        # Refresh stock data
        symbols = group_data.get('symbols', [])
        stocks_data = []
        for symbol in symbols:
            stock_data = _get_stock_data_with_fundamentals(symbol)
            if stock_data:
                stocks_data.append(stock_data)
        
        if stocks_data:
            group_data['stocks'] = stocks_data
            group_data['metrics'] = _calculate_group_metrics(stocks_data)
            cache.set(f'stock_group_{group_id}', group_data, 3600)
        
        return JsonResponse({
            'success': True,
            'group': group_data
        })
    
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_group_chart(request, group_id):
    """
    GET /api/groups/<group_id>/chart/
    
    Get aggregated chart data for a stock group.
    
    Query params:
    - period: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, max (default: 1mo)
    - normalize: true/false - normalize prices to percentage change (default: true)
    """
    try:
        group_data = cache.get(f'stock_group_{group_id}')
        
        if not group_data:
            return JsonResponse({
                'success': False,
                'error': 'Group not found or expired'
            }, status=404)
        
        symbols = group_data.get('symbols', [])
        period = request.GET.get('period', '1mo')
        normalize = request.GET.get('normalize', 'true').lower() == 'true'
        
        # Fetch historical data for all symbols
        all_data = {}
        for symbol in symbols:
            try:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period=period)
                if not hist.empty:
                    all_data[symbol] = hist['Close']
            except:
                pass
        
        if not all_data:
            return JsonResponse({
                'success': False,
                'error': 'No chart data available'
            }, status=404)
        
        # Combine into DataFrame
        df = pd.DataFrame(all_data)
        
        # Forward fill missing values
        df = df.fillna(method='ffill').fillna(method='bfill')
        
        # Normalize to percentage change from first value if requested
        if normalize:
            df = (df / df.iloc[0] - 1) * 100
        
        # Calculate group average
        df['group_average'] = df.mean(axis=1)
        
        # Format response
        chart_data = []
        for idx in df.index:
            timestamp = int(idx.timestamp() * 1000) if hasattr(idx, 'timestamp') else int(idx)
            point = {
                'time': timestamp,
                'date': str(idx.date()) if hasattr(idx, 'date') else str(idx),
                'group_average': round(float(df.loc[idx, 'group_average']), 4)
            }
            for symbol in symbols:
                if symbol in df.columns:
                    point[symbol] = round(float(df.loc[idx, symbol]), 4)
            chart_data.append(point)
        
        return JsonResponse({
            'success': True,
            'data': {
                'group_id': group_id,
                'group_name': group_data.get('name'),
                'symbols': symbols,
                'period': period,
                'normalized': normalize,
                'chart': chart_data,
                'summary': {
                    'start_date': chart_data[0]['date'] if chart_data else None,
                    'end_date': chart_data[-1]['date'] if chart_data else None,
                    'group_return': round(chart_data[-1]['group_average'], 2) if chart_data else 0,
                    'individual_returns': {
                        s: round(chart_data[-1].get(s, 0), 2) for s in symbols
                    } if chart_data else {}
                }
            }
        })
    
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def compare_stocks(request):
    """
    POST /api/compare/stocks/
    
    Compare multiple stocks side by side.
    
    Body:
    {
        "symbols": ["AAPL", "MSFT", "GOOGL"],
        "metrics": ["pe_ratio", "roe", "valuation_score"] (optional - defaults to all)
    }
    """
    try:
        data = json.loads(request.body)
        symbols = data.get('symbols', [])
        selected_metrics = data.get('metrics')
        
        if len(symbols) < 2:
            return JsonResponse({
                'success': False,
                'error': 'At least 2 symbols required for comparison'
            }, status=400)
        
        if len(symbols) > 10:
            return JsonResponse({
                'success': False,
                'error': 'Maximum 10 symbols allowed'
            }, status=400)
        
        # Get data for all stocks
        stocks_data = []
        for symbol in symbols:
            stock_data = _get_stock_data_with_fundamentals(symbol)
            if stock_data:
                stocks_data.append(stock_data)
        
        if len(stocks_data) < 2:
            return JsonResponse({
                'success': False,
                'error': 'Not enough valid stocks for comparison'
            }, status=400)
        
        # Default metrics for comparison
        all_metrics = [
            # Basic
            ('current_price', 'Current Price', '$'),
            ('price_change_percent', 'Price Change %', '%'),
            ('market_cap', 'Market Cap', '$'),
            ('volume', 'Volume', ''),
            # Valuation
            ('pe_ratio', 'P/E Ratio', ''),
            ('forward_pe', 'Forward P/E', ''),
            ('peg_ratio', 'PEG Ratio', ''),
            ('price_to_book', 'P/B Ratio', ''),
            ('price_to_sales', 'P/S Ratio', ''),
            # Profitability
            ('gross_margin', 'Gross Margin', '%'),
            ('operating_margin', 'Operating Margin', '%'),
            ('profit_margin', 'Profit Margin', '%'),
            ('roe', 'ROE', '%'),
            ('roa', 'ROA', '%'),
            # Growth
            ('revenue_growth_yoy', 'Revenue Growth YoY', '%'),
            ('earnings_growth_yoy', 'Earnings Growth YoY', '%'),
            # Health
            ('current_ratio', 'Current Ratio', ''),
            ('debt_to_equity', 'Debt/Equity', ''),
            # Fair Value
            ('dcf_value', 'DCF Value', '$'),
            ('graham_number', 'Graham Number', '$'),
            ('valuation_score', 'Valuation Score', ''),
            ('strength_score', 'Strength Score', ''),
        ]
        
        # Filter metrics if specified
        if selected_metrics:
            all_metrics = [m for m in all_metrics if m[0] in selected_metrics]
        
        # Build comparison table
        comparison = []
        for metric_key, metric_name, unit in all_metrics:
            row = {
                'metric': metric_key,
                'name': metric_name,
                'unit': unit,
                'values': {}
            }
            
            values = []
            for stock in stocks_data:
                value = stock.get(metric_key)
                row['values'][stock['ticker']] = value
                if value is not None:
                    values.append((stock['ticker'], value))
            
            # Determine best/worst (higher is generally better except for some metrics)
            lower_is_better = metric_key in ['pe_ratio', 'forward_pe', 'peg_ratio', 'debt_to_equity', 'price_to_book', 'price_to_sales']
            
            if values:
                sorted_values = sorted(values, key=lambda x: x[1] if x[1] is not None else float('inf'))
                if lower_is_better:
                    row['best'] = sorted_values[0][0]
                    row['worst'] = sorted_values[-1][0]
                else:
                    row['best'] = sorted_values[-1][0]
                    row['worst'] = sorted_values[0][0]
            
            comparison.append(row)
        
        return JsonResponse({
            'success': True,
            'data': {
                'symbols': [s['ticker'] for s in stocks_data],
                'stocks': {s['ticker']: {'name': s.get('company_name', s['ticker']), 'sector': s.get('sector')} for s in stocks_data},
                'comparison': comparison,
                'summary': {
                    'count': len(stocks_data),
                    'sectors': list(set(s.get('sector', 'Unknown') for s in stocks_data if s.get('sector')))
                }
            }
        })
    
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def compare_groups(request):
    """
    POST /api/compare/groups/
    
    Compare multiple stock groups.
    
    Body:
    {
        "groups": [
            {"name": "Tech", "symbols": ["AAPL", "MSFT"]},
            {"name": "Finance", "symbols": ["JPM", "BAC"]}
        ]
    }
    """
    try:
        data = json.loads(request.body)
        groups = data.get('groups', [])
        
        if len(groups) < 2:
            return JsonResponse({
                'success': False,
                'error': 'At least 2 groups required for comparison'
            }, status=400)
        
        groups_data = []
        for group in groups:
            name = group.get('name', 'Unnamed')
            symbols = group.get('symbols', [])
            
            stocks_data = []
            for symbol in symbols:
                stock_data = _get_stock_data_with_fundamentals(symbol)
                if stock_data:
                    stocks_data.append(stock_data)
            
            if stocks_data:
                metrics = _calculate_group_metrics(stocks_data)
                groups_data.append({
                    'name': name,
                    'symbols': [s['ticker'] for s in stocks_data],
                    'count': len(stocks_data),
                    'metrics': metrics
                })
        
        if len(groups_data) < 2:
            return JsonResponse({
                'success': False,
                'error': 'Not enough valid groups for comparison'
            }, status=400)
        
        # Build comparison metrics
        comparison_metrics = [
            'current_price', 'price_change_percent', 'market_cap',
            'pe_ratio', 'roe', 'profit_margin', 'valuation_score', 'strength_score'
        ]
        
        comparison = []
        for metric in comparison_metrics:
            row = {
                'metric': metric,
                'values': {}
            }
            for group in groups_data:
                metrics = group['metrics']
                if metric in metrics and isinstance(metrics[metric], dict):
                    row['values'][group['name']] = metrics[metric].get('average')
            comparison.append(row)
        
        return JsonResponse({
            'success': True,
            'data': {
                'groups': groups_data,
                'comparison': comparison
            }
        })
    
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_comparison_chart(request):
    """
    GET /api/compare/chart/
    
    Get comparison chart data for multiple symbols.
    
    Query params:
    - symbols: comma-separated list of symbols
    - period: 1d, 5d, 1mo, 3mo, 6mo, 1y (default: 3mo)
    - normalize: true/false (default: true)
    """
    try:
        symbols_str = request.GET.get('symbols', '')
        symbols = [s.strip().upper() for s in symbols_str.split(',') if s.strip()]
        period = request.GET.get('period', '3mo')
        normalize = request.GET.get('normalize', 'true').lower() == 'true'
        
        if len(symbols) < 2:
            return JsonResponse({
                'success': False,
                'error': 'At least 2 symbols required'
            }, status=400)
        
        # Fetch data for all symbols
        all_data = {}
        for symbol in symbols:
            try:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period=period)
                if not hist.empty:
                    all_data[symbol] = hist['Close']
            except:
                pass
        
        if len(all_data) < 2:
            return JsonResponse({
                'success': False,
                'error': 'Not enough data available'
            }, status=404)
        
        df = pd.DataFrame(all_data)
        df = df.fillna(method='ffill').fillna(method='bfill')
        
        if normalize:
            df = (df / df.iloc[0] - 1) * 100
        
        chart_data = []
        for idx in df.index:
            timestamp = int(idx.timestamp() * 1000) if hasattr(idx, 'timestamp') else int(idx)
            point = {
                'time': timestamp,
                'date': str(idx.date()) if hasattr(idx, 'date') else str(idx)
            }
            for symbol in df.columns:
                point[symbol] = round(float(df.loc[idx, symbol]), 4)
            chart_data.append(point)
        
        # Calculate returns
        returns = {}
        for symbol in df.columns:
            returns[symbol] = round(float(df[symbol].iloc[-1]), 2)
        
        return JsonResponse({
            'success': True,
            'data': {
                'symbols': list(df.columns),
                'period': period,
                'normalized': normalize,
                'chart': chart_data,
                'returns': returns
            }
        })
    
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
