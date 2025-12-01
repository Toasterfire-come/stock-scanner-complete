"""
Advanced Charting API - Phase 3 MVP
Provides historical data with multiple timeframes and technical indicators.
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.core.cache import cache
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from decimal import Decimal


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


# Timeframe mapping for yfinance
TIMEFRAME_MAP = {
    '1m': {'interval': '1m', 'period': '7d'},
    '5m': {'interval': '5m', 'period': '60d'},
    '15m': {'interval': '15m', 'period': '60d'},
    '30m': {'interval': '30m', 'period': '60d'},
    '1h': {'interval': '1h', 'period': '730d'},
    '4h': {'interval': '1h', 'period': '730d'},  # Will aggregate
    '1d': {'interval': '1d', 'period': 'max'},
    '1wk': {'interval': '1wk', 'period': 'max'},
    '1mo': {'interval': '1mo', 'period': 'max'},
}

# Premium timeframes (require authentication)
PREMIUM_TIMEFRAMES = ['1m', '5m', '4h']


def calculate_sma(data: pd.Series, period: int) -> pd.Series:
    """Calculate Simple Moving Average."""
    return data.rolling(window=period).mean()


def calculate_ema(data: pd.Series, period: int) -> pd.Series:
    """Calculate Exponential Moving Average."""
    return data.ewm(span=period, adjust=False).mean()


def calculate_rsi(data: pd.Series, period: int = 14) -> pd.Series:
    """Calculate Relative Strength Index."""
    delta = data.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))


def calculate_macd(data: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9):
    """Calculate MACD."""
    ema_fast = calculate_ema(data, fast)
    ema_slow = calculate_ema(data, slow)
    macd_line = ema_fast - ema_slow
    signal_line = calculate_ema(macd_line, signal)
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram


def calculate_bollinger_bands(data: pd.Series, period: int = 20, std_dev: float = 2.0):
    """Calculate Bollinger Bands."""
    sma = calculate_sma(data, period)
    std = data.rolling(window=period).std()
    upper = sma + (std * std_dev)
    lower = sma - (std * std_dev)
    return upper, sma, lower


def calculate_vwap(df: pd.DataFrame) -> pd.Series:
    """Calculate Volume Weighted Average Price."""
    typical_price = (df['High'] + df['Low'] + df['Close']) / 3
    return (typical_price * df['Volume']).cumsum() / df['Volume'].cumsum()


def calculate_stochastic(df: pd.DataFrame, k_period: int = 14, d_period: int = 3):
    """Calculate Stochastic Oscillator."""
    low_min = df['Low'].rolling(window=k_period).min()
    high_max = df['High'].rolling(window=k_period).max()
    k = 100 * ((df['Close'] - low_min) / (high_max - low_min))
    d = k.rolling(window=d_period).mean()
    return k, d


def calculate_atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """Calculate Average True Range."""
    high_low = df['High'] - df['Low']
    high_close = np.abs(df['High'] - df['Close'].shift())
    low_close = np.abs(df['Low'] - df['Close'].shift())
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    return tr.rolling(window=period).mean()


def convert_to_heikin_ashi(df: pd.DataFrame) -> pd.DataFrame:
    """Convert OHLC data to Heikin-Ashi."""
    ha_df = df.copy()
    ha_df['Close'] = (df['Open'] + df['High'] + df['Low'] + df['Close']) / 4
    
    for i in range(len(ha_df)):
        if i == 0:
            ha_df.iloc[i, ha_df.columns.get_loc('Open')] = (df.iloc[i]['Open'] + df.iloc[i]['Close']) / 2
        else:
            ha_df.iloc[i, ha_df.columns.get_loc('Open')] = (ha_df.iloc[i-1]['Open'] + ha_df.iloc[i-1]['Close']) / 2
    
    ha_df['High'] = ha_df[['Open', 'Close', 'High']].max(axis=1)
    ha_df['Low'] = ha_df[['Open', 'Close', 'Low']].min(axis=1)
    
    return ha_df


@api_view(['GET'])
@permission_classes([AllowAny])
def get_chart_data(request, ticker):
    """
    GET /api/chart/{ticker}/
    
    Returns historical OHLCV data for charting.
    
    Query params:
    - timeframe: 1m, 5m, 15m, 30m, 1h, 4h, 1d, 1wk, 1mo (default: 1d)
    - chart_type: candlestick, line, area, heikin_ashi (default: candlestick)
    - start: Start date (YYYY-MM-DD)
    - end: End date (YYYY-MM-DD)
    """
    try:
        ticker = ticker.upper().strip()
        timeframe = request.GET.get('timeframe', '1d')
        chart_type = request.GET.get('chart_type', 'candlestick')
        start_date = request.GET.get('start')
        end_date = request.GET.get('end')
        
        # Check premium timeframes
        if timeframe in PREMIUM_TIMEFRAMES:
            if not request.user.is_authenticated:
                return Response({
                    'success': False,
                    'error': f'Timeframe {timeframe} requires Premium subscription',
                    'premium_required': True
                }, status=403)
        
        # Validate timeframe
        if timeframe not in TIMEFRAME_MAP:
            return Response({
                'success': False,
                'error': f'Invalid timeframe. Valid options: {list(TIMEFRAME_MAP.keys())}'
            }, status=400)
        
        # Cache key
        cache_key = f'chart_{ticker}_{timeframe}_{chart_type}_{start_date}_{end_date}'
        cached = cache.get(cache_key)
        if cached:
            return Response({'success': True, 'data': cached, 'cached': True})
        
        # Get data from yfinance
        yf_ticker = yf.Ticker(ticker)
        tf_config = TIMEFRAME_MAP[timeframe]
        
        if start_date and end_date:
            df = yf_ticker.history(start=start_date, end=end_date, interval=tf_config['interval'])
        else:
            df = yf_ticker.history(period=tf_config['period'], interval=tf_config['interval'])
        
        if df.empty:
            return Response({
                'success': False,
                'error': 'No data available for this ticker/timeframe'
            }, status=404)
        
        # Aggregate to 4h if needed
        if timeframe == '4h':
            df = df.resample('4H').agg({
                'Open': 'first',
                'High': 'max',
                'Low': 'min',
                'Close': 'last',
                'Volume': 'sum'
            }).dropna()
        
        # Convert to Heikin-Ashi if requested
        if chart_type == 'heikin_ashi':
            df = convert_to_heikin_ashi(df)
        
        # Format response
        data_list = []
        for idx, row in df.iterrows():
            timestamp = int(idx.timestamp() * 1000) if hasattr(idx, 'timestamp') else int(idx)
            
            if chart_type in ['candlestick', 'heikin_ashi']:
                data_list.append({
                    'time': timestamp,
                    'open': round(float(row['Open']), 4),
                    'high': round(float(row['High']), 4),
                    'low': round(float(row['Low']), 4),
                    'close': round(float(row['Close']), 4),
                    'volume': int(row['Volume']) if pd.notna(row['Volume']) else 0
                })
            else:  # line or area
                data_list.append({
                    'time': timestamp,
                    'value': round(float(row['Close']), 4),
                    'volume': int(row['Volume']) if pd.notna(row['Volume']) else 0
                })
        
        response_data = {
            'ticker': ticker,
            'timeframe': timeframe,
            'chart_type': chart_type,
            'data': data_list,
            'count': len(data_list),
            'start': data_list[0]['time'] if data_list else None,
            'end': data_list[-1]['time'] if data_list else None
        }
        
        # Cache for varying durations based on timeframe
        cache_ttl = 60 if timeframe in ['1m', '5m'] else 300 if timeframe in ['15m', '30m', '1h'] else 900
        cache.set(cache_key, response_data, cache_ttl)
        
        return Response({'success': True, 'data': response_data, 'cached': False})
        
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_chart_indicators(request, ticker):
    """
    GET /api/chart/{ticker}/indicators/
    
    Returns technical indicators for a stock.
    
    Query params:
    - indicators: Comma-separated list (sma_20,ema_50,rsi,macd,bollinger,vwap,stochastic,atr)
    - timeframe: Same as chart data (default: 1d)
    """
    try:
        ticker = ticker.upper().strip()
        timeframe = request.GET.get('timeframe', '1d')
        indicators_param = request.GET.get('indicators', 'sma_20,ema_50')
        requested_indicators = [i.strip().lower() for i in indicators_param.split(',')]
        
        # Validate timeframe
        if timeframe not in TIMEFRAME_MAP:
            return Response({
                'success': False,
                'error': f'Invalid timeframe'
            }, status=400)
        
        # Cache key
        cache_key = f'indicators_{ticker}_{timeframe}_{indicators_param}'
        cached = cache.get(cache_key)
        if cached:
            return Response({'success': True, 'data': cached, 'cached': True})
        
        # Get data
        yf_ticker = yf.Ticker(ticker)
        tf_config = TIMEFRAME_MAP[timeframe]
        df = yf_ticker.history(period=tf_config['period'], interval=tf_config['interval'])
        
        if df.empty:
            return Response({'success': False, 'error': 'No data available'}, status=404)
        
        results = {'ticker': ticker, 'timeframe': timeframe, 'indicators': {}}
        
        for indicator in requested_indicators:
            try:
                # SMA
                if indicator.startswith('sma_'):
                    period = int(indicator.split('_')[1])
                    sma = calculate_sma(df['Close'], period)
                    results['indicators'][indicator] = [
                        {'time': int(idx.timestamp() * 1000), 'value': round(float(v), 4)}
                        for idx, v in sma.dropna().items()
                    ]
                
                # EMA
                elif indicator.startswith('ema_'):
                    period = int(indicator.split('_')[1])
                    ema = calculate_ema(df['Close'], period)
                    results['indicators'][indicator] = [
                        {'time': int(idx.timestamp() * 1000), 'value': round(float(v), 4)}
                        for idx, v in ema.dropna().items()
                    ]
                
                # RSI
                elif indicator == 'rsi' or indicator.startswith('rsi_'):
                    period = int(indicator.split('_')[1]) if '_' in indicator else 14
                    rsi = calculate_rsi(df['Close'], period)
                    results['indicators']['rsi'] = [
                        {'time': int(idx.timestamp() * 1000), 'value': round(float(v), 2)}
                        for idx, v in rsi.dropna().items()
                    ]
                
                # MACD
                elif indicator == 'macd':
                    macd_line, signal_line, histogram = calculate_macd(df['Close'])
                    results['indicators']['macd'] = {
                        'macd': [
                            {'time': int(idx.timestamp() * 1000), 'value': round(float(v), 4)}
                            for idx, v in macd_line.dropna().items()
                        ],
                        'signal': [
                            {'time': int(idx.timestamp() * 1000), 'value': round(float(v), 4)}
                            for idx, v in signal_line.dropna().items()
                        ],
                        'histogram': [
                            {'time': int(idx.timestamp() * 1000), 'value': round(float(v), 4)}
                            for idx, v in histogram.dropna().items()
                        ]
                    }
                
                # Bollinger Bands
                elif indicator == 'bollinger':
                    upper, middle, lower = calculate_bollinger_bands(df['Close'])
                    results['indicators']['bollinger'] = {
                        'upper': [
                            {'time': int(idx.timestamp() * 1000), 'value': round(float(v), 4)}
                            for idx, v in upper.dropna().items()
                        ],
                        'middle': [
                            {'time': int(idx.timestamp() * 1000), 'value': round(float(v), 4)}
                            for idx, v in middle.dropna().items()
                        ],
                        'lower': [
                            {'time': int(idx.timestamp() * 1000), 'value': round(float(v), 4)}
                            for idx, v in lower.dropna().items()
                        ]
                    }
                
                # VWAP
                elif indicator == 'vwap':
                    vwap = calculate_vwap(df)
                    results['indicators']['vwap'] = [
                        {'time': int(idx.timestamp() * 1000), 'value': round(float(v), 4)}
                        for idx, v in vwap.dropna().items()
                    ]
                
                # Stochastic
                elif indicator == 'stochastic':
                    k, d = calculate_stochastic(df)
                    results['indicators']['stochastic'] = {
                        'k': [
                            {'time': int(idx.timestamp() * 1000), 'value': round(float(v), 2)}
                            for idx, v in k.dropna().items()
                        ],
                        'd': [
                            {'time': int(idx.timestamp() * 1000), 'value': round(float(v), 2)}
                            for idx, v in d.dropna().items()
                        ]
                    }
                
                # ATR
                elif indicator == 'atr' or indicator.startswith('atr_'):
                    period = int(indicator.split('_')[1]) if '_' in indicator else 14
                    atr = calculate_atr(df, period)
                    results['indicators']['atr'] = [
                        {'time': int(idx.timestamp() * 1000), 'value': round(float(v), 4)}
                        for idx, v in atr.dropna().items()
                    ]
                    
            except Exception as e:
                results['indicators'][indicator] = {'error': str(e)}
        
        # Cache for 5 minutes
        cache.set(cache_key, results, 300)
        
        return Response({'success': True, 'data': results, 'cached': False})
        
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_available_timeframes(request):
    """
    GET /api/chart/timeframes/
    
    Returns available chart timeframes with premium status.
    """
    is_authenticated = request.user.is_authenticated
    
    timeframes = []
    for tf, config in TIMEFRAME_MAP.items():
        is_premium = tf in PREMIUM_TIMEFRAMES
        timeframes.append({
            'id': tf,
            'label': tf.upper(),
            'premium': is_premium,
            'available': not is_premium or is_authenticated
        })
    
    return Response({
        'success': True,
        'data': {
            'timeframes': timeframes,
            'chart_types': [
                {'id': 'candlestick', 'label': 'Candlestick', 'premium': False},
                {'id': 'line', 'label': 'Line', 'premium': False},
                {'id': 'area', 'label': 'Area', 'premium': False},
                {'id': 'heikin_ashi', 'label': 'Heikin-Ashi', 'premium': True}
            ],
            'indicators': [
                {'id': 'sma', 'label': 'SMA (Simple Moving Average)', 'premium': False, 'params': ['period']},
                {'id': 'ema', 'label': 'EMA (Exponential Moving Average)', 'premium': False, 'params': ['period']},
                {'id': 'rsi', 'label': 'RSI (Relative Strength Index)', 'premium': False, 'params': ['period']},
                {'id': 'macd', 'label': 'MACD', 'premium': True, 'params': ['fast', 'slow', 'signal']},
                {'id': 'bollinger', 'label': 'Bollinger Bands', 'premium': True, 'params': ['period', 'std_dev']},
                {'id': 'vwap', 'label': 'VWAP', 'premium': True, 'params': []},
                {'id': 'stochastic', 'label': 'Stochastic Oscillator', 'premium': True, 'params': ['k_period', 'd_period']},
                {'id': 'atr', 'label': 'ATR (Average True Range)', 'premium': True, 'params': ['period']}
            ],
            'drawing_tools': [
                {'id': 'trend_line', 'label': 'Trend Line', 'premium': False},
                {'id': 'horizontal_line', 'label': 'Horizontal Line', 'premium': False},
                {'id': 'rectangle', 'label': 'Rectangle', 'premium': True},
                {'id': 'fibonacci_retracement', 'label': 'Fibonacci Retracement', 'premium': True},
                {'id': 'fibonacci_extension', 'label': 'Fibonacci Extension', 'premium': True},
                {'id': 'text_annotation', 'label': 'Text Annotation', 'premium': True}
            ]
        }
    })
