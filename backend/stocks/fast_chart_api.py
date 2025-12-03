"""
Enhanced Charting API with Fast Refresh - Feature 3
Fast updates with refresh endpoint for real-time-like experience
"""
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.cache import cache
import yfinance as yf
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


def _safe_float(value):
    """Safely convert to float"""
    if value is None:
        return None
    try:
        return float(value)
    except:
        return None


@csrf_exempt
@require_http_methods(["GET"])
def get_fast_quote(request, ticker):
    """
    GET /api/chart/<ticker>/quote/
    
    Get fast quote data for real-time updates.
    Minimal caching for near real-time experience.
    """
    try:
        ticker = ticker.upper().strip()
        
        # Very short cache (10 seconds)
        cache_key = f'fast_quote_{ticker}'
        cached = cache.get(cache_key)
        if cached:
            return JsonResponse({'success': True, 'data': cached, 'cached': True})
        
        yf_ticker = yf.Ticker(ticker)
        info = yf_ticker.fast_info
        
        data = {
            'ticker': ticker,
            'price': _safe_float(info.last_price),
            'previous_close': _safe_float(info.previous_close),
            'change': None,
            'change_percent': None,
            'day_high': _safe_float(info.day_high),
            'day_low': _safe_float(info.day_low),
            'volume': info.last_volume,
            'market_cap': info.market_cap,
            'timestamp': datetime.now().isoformat()
        }
        
        # Calculate change
        if data['price'] and data['previous_close']:
            data['change'] = round(data['price'] - data['previous_close'], 4)
            data['change_percent'] = round((data['change'] / data['previous_close']) * 100, 2)
        
        # Cache for 10 seconds only
        cache.set(cache_key, data, 10)
        
        return JsonResponse({'success': True, 'data': data, 'cached': False})
    
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_intraday_data(request, ticker):
    """
    GET /api/chart/<ticker>/intraday/
    
    Get intraday data with 1-minute or 5-minute intervals.
    Optimized for fast updates.
    
    Query params:
    - interval: 1m, 5m, 15m (default: 5m)
    - period: 1d, 5d (default: 1d)
    """
    try:
        ticker = ticker.upper().strip()
        interval = request.GET.get('interval', '5m')
        period = request.GET.get('period', '1d')
        
        # Validate
        if interval not in ['1m', '5m', '15m']:
            interval = '5m'
        if period not in ['1d', '5d']:
            period = '1d'
        
        # Short cache for intraday data
        cache_ttl = 30 if interval == '1m' else 60
        cache_key = f'intraday_{ticker}_{interval}_{period}'
        cached = cache.get(cache_key)
        if cached:
            return JsonResponse({'success': True, 'data': cached, 'cached': True})
        
        yf_ticker = yf.Ticker(ticker)
        df = yf_ticker.history(period=period, interval=interval)
        
        if df.empty:
            return JsonResponse({
                'success': False,
                'error': 'No intraday data available'
            }, status=404)
        
        # Format data
        data_points = []
        for idx, row in df.iterrows():
            timestamp = int(idx.timestamp() * 1000) if hasattr(idx, 'timestamp') else int(idx)
            data_points.append({
                'time': timestamp,
                'open': round(float(row['Open']), 4),
                'high': round(float(row['High']), 4),
                'low': round(float(row['Low']), 4),
                'close': round(float(row['Close']), 4),
                'volume': int(row['Volume']) if pd.notna(row['Volume']) else 0
            })
        
        result = {
            'ticker': ticker,
            'interval': interval,
            'period': period,
            'data': data_points,
            'count': len(data_points),
            'last_update': datetime.now().isoformat()
        }
        
        cache.set(cache_key, result, cache_ttl)
        
        return JsonResponse({'success': True, 'data': result, 'cached': False})
    
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_latest_candle(request, ticker):
    """
    GET /api/chart/<ticker>/latest/
    
    Get only the latest candle for incremental chart updates.
    Minimal data transfer for fast refresh.
    
    Query params:
    - interval: 1m, 5m, 15m, 1h, 1d (default: 5m)
    """
    try:
        ticker = ticker.upper().strip()
        interval = request.GET.get('interval', '5m')
        
        if interval not in ['1m', '5m', '15m', '1h', '1d']:
            interval = '5m'
        
        # Very short cache (5-15 seconds based on interval)
        cache_ttl = 5 if interval == '1m' else 15 if interval == '5m' else 30
        cache_key = f'latest_candle_{ticker}_{interval}'
        cached = cache.get(cache_key)
        if cached:
            return JsonResponse({'success': True, 'data': cached, 'cached': True})
        
        yf_ticker = yf.Ticker(ticker)
        
        # Get just the last 2 candles
        if interval in ['1m', '5m', '15m']:
            df = yf_ticker.history(period='1d', interval=interval)
        else:
            df = yf_ticker.history(period='5d', interval=interval)
        
        if df.empty:
            return JsonResponse({
                'success': False,
                'error': 'No data available'
            }, status=404)
        
        # Get last row
        last_row = df.iloc[-1]
        last_idx = df.index[-1]
        
        result = {
            'ticker': ticker,
            'interval': interval,
            'candle': {
                'time': int(last_idx.timestamp() * 1000) if hasattr(last_idx, 'timestamp') else int(last_idx),
                'open': round(float(last_row['Open']), 4),
                'high': round(float(last_row['High']), 4),
                'low': round(float(last_row['Low']), 4),
                'close': round(float(last_row['Close']), 4),
                'volume': int(last_row['Volume']) if pd.notna(last_row['Volume']) else 0
            },
            'timestamp': datetime.now().isoformat()
        }
        
        cache.set(cache_key, result, cache_ttl)
        
        return JsonResponse({'success': True, 'data': result, 'cached': False})
    
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def batch_quotes(request):
    """
    POST /api/chart/batch-quotes/
    
    Get quotes for multiple symbols in one request.
    Efficient for dashboard/watchlist updates.
    
    Body:
    {
        "symbols": ["AAPL", "MSFT", "GOOGL"]
    }
    """
    try:
        data = json.loads(request.body)
        symbols = data.get('symbols', [])[:50]  # Max 50 symbols
        
        if not symbols:
            return JsonResponse({
                'success': False,
                'error': 'No symbols provided'
            }, status=400)
        
        results = {}
        for symbol in symbols:
            symbol = symbol.upper().strip()
            try:
                # Check cache first
                cache_key = f'fast_quote_{symbol}'
                cached = cache.get(cache_key)
                
                if cached:
                    results[symbol] = cached
                else:
                    yf_ticker = yf.Ticker(symbol)
                    info = yf_ticker.fast_info
                    
                    quote_data = {
                        'price': _safe_float(info.last_price),
                        'previous_close': _safe_float(info.previous_close),
                        'change': None,
                        'change_percent': None,
                        'volume': info.last_volume
                    }
                    
                    if quote_data['price'] and quote_data['previous_close']:
                        quote_data['change'] = round(quote_data['price'] - quote_data['previous_close'], 4)
                        quote_data['change_percent'] = round((quote_data['change'] / quote_data['previous_close']) * 100, 2)
                    
                    cache.set(cache_key, quote_data, 10)
                    results[symbol] = quote_data
            
            except Exception as e:
                results[symbol] = {'error': str(e)}
        
        return JsonResponse({
            'success': True,
            'data': {
                'quotes': results,
                'count': len(results),
                'timestamp': datetime.now().isoformat()
            }
        })
    
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_chart_with_indicators(request, ticker):
    """
    GET /api/chart/<ticker>/full/
    
    Get complete chart data with indicators in one request.
    Reduces round trips for initial chart load.
    
    Query params:
    - period: 1mo, 3mo, 6mo, 1y, 2y, 5y (default: 3mo)
    - interval: 1d, 1h (default: 1d)
    - indicators: comma-separated (sma_20,sma_50,rsi,macd,bollinger)
    """
    try:
        ticker = ticker.upper().strip()
        period = request.GET.get('period', '3mo')
        interval = request.GET.get('interval', '1d')
        indicators_str = request.GET.get('indicators', 'sma_20,sma_50,rsi')
        indicators = [i.strip().lower() for i in indicators_str.split(',')]
        
        # Cache key
        cache_key = f'chart_full_{ticker}_{period}_{interval}_{indicators_str}'
        cached = cache.get(cache_key)
        if cached:
            return JsonResponse({'success': True, 'data': cached, 'cached': True})
        
        yf_ticker = yf.Ticker(ticker)
        df = yf_ticker.history(period=period, interval=interval)
        
        if df.empty:
            return JsonResponse({
                'success': False,
                'error': 'No data available'
            }, status=404)
        
        # Calculate indicators
        close = df['Close']
        
        # SMA
        for ind in indicators:
            if ind.startswith('sma_'):
                period_val = int(ind.split('_')[1])
                df[f'SMA_{period_val}'] = close.rolling(window=period_val).mean()
            elif ind.startswith('ema_'):
                period_val = int(ind.split('_')[1])
                df[f'EMA_{period_val}'] = close.ewm(span=period_val, adjust=False).mean()
        
        # RSI
        if 'rsi' in indicators:
            delta = close.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            df['RSI'] = 100 - (100 / (1 + rs))
        
        # MACD
        if 'macd' in indicators:
            ema12 = close.ewm(span=12, adjust=False).mean()
            ema26 = close.ewm(span=26, adjust=False).mean()
            df['MACD'] = ema12 - ema26
            df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
            df['MACD_Hist'] = df['MACD'] - df['MACD_Signal']
        
        # Bollinger Bands
        if 'bollinger' in indicators:
            sma20 = close.rolling(window=20).mean()
            std20 = close.rolling(window=20).std()
            df['BB_Upper'] = sma20 + (std20 * 2)
            df['BB_Middle'] = sma20
            df['BB_Lower'] = sma20 - (std20 * 2)
        
        # Format response
        candles = []
        indicator_data = {ind: [] for ind in indicators}
        
        for idx, row in df.iterrows():
            timestamp = int(idx.timestamp() * 1000) if hasattr(idx, 'timestamp') else int(idx)
            
            candles.append({
                'time': timestamp,
                'open': round(float(row['Open']), 4),
                'high': round(float(row['High']), 4),
                'low': round(float(row['Low']), 4),
                'close': round(float(row['Close']), 4),
                'volume': int(row['Volume']) if pd.notna(row['Volume']) else 0
            })
            
            # Add indicator values
            for ind in indicators:
                if ind.startswith('sma_'):
                    col = f"SMA_{ind.split('_')[1]}"
                    if col in df.columns and pd.notna(row[col]):
                        indicator_data[ind].append({'time': timestamp, 'value': round(float(row[col]), 4)})
                elif ind.startswith('ema_'):
                    col = f"EMA_{ind.split('_')[1]}"
                    if col in df.columns and pd.notna(row[col]):
                        indicator_data[ind].append({'time': timestamp, 'value': round(float(row[col]), 4)})
                elif ind == 'rsi' and 'RSI' in df.columns and pd.notna(row['RSI']):
                    indicator_data['rsi'].append({'time': timestamp, 'value': round(float(row['RSI']), 2)})
                elif ind == 'macd' and 'MACD' in df.columns:
                    if pd.notna(row['MACD']):
                        indicator_data['macd'].append({
                            'time': timestamp,
                            'macd': round(float(row['MACD']), 4),
                            'signal': round(float(row['MACD_Signal']), 4) if pd.notna(row['MACD_Signal']) else None,
                            'histogram': round(float(row['MACD_Hist']), 4) if pd.notna(row['MACD_Hist']) else None
                        })
                elif ind == 'bollinger' and 'BB_Upper' in df.columns:
                    if pd.notna(row['BB_Upper']):
                        indicator_data['bollinger'].append({
                            'time': timestamp,
                            'upper': round(float(row['BB_Upper']), 4),
                            'middle': round(float(row['BB_Middle']), 4),
                            'lower': round(float(row['BB_Lower']), 4)
                        })
        
        result = {
            'ticker': ticker,
            'period': period,
            'interval': interval,
            'candles': candles,
            'indicators': indicator_data,
            'count': len(candles),
            'last_update': datetime.now().isoformat()
        }
        
        # Cache for 5 minutes
        cache.set(cache_key, result, 300)
        
        return JsonResponse({'success': True, 'data': result, 'cached': False})
    
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
