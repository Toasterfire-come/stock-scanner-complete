#!/usr/bin/env python
"""
Script to populate baseline strategies for the backtesting system.
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stockscanner_django.settings_local_sqlite')
django.setup()

from stocks.models import BaselineStrategy

BASELINE_STRATEGIES = [
    # Day Trading Strategies
    {
        "name": "Opening Range Breakout (ORB)",
        "category": "day_trading",
        "description": "Buy when price breaks above the first 15-minute high, sell at end of day or when price breaks below the opening range low.",
        "strategy_code": """
def generate_signals(data):
    signals = []
    for i in range(15, len(data)):
        opening_range = data.iloc[:15]
        or_high = opening_range['high'].max()
        or_low = opening_range['low'].min()
        
        if data.iloc[i]['close'] > or_high:
            signals.append({'type': 'buy', 'index': i})
        elif data.iloc[i]['close'] < or_low:
            signals.append({'type': 'sell', 'index': i})
    return signals
""",
        "default_params": {"timeframe": "15m", "holding_period": "1 day"}
    },
    {
        "name": "VWAP Bounce",
        "category": "day_trading",
        "description": "Buy when price pulls back to VWAP and bounces with increasing volume. Exit when price reaches 1% profit or falls 0.5% below entry.",
        "strategy_code": """
def generate_signals(data):
    vwap = (data['volume'] * (data['high'] + data['low'] + data['close']) / 3).cumsum() / data['volume'].cumsum()
    signals = []
    for i in range(1, len(data)):
        if data.iloc[i]['low'] <= vwap.iloc[i] <= data.iloc[i]['close']:
            if data.iloc[i]['volume'] > data.iloc[i-1]['volume']:
                signals.append({'type': 'buy', 'index': i, 'target': 1.01, 'stop': 0.995})
    return signals
""",
        "default_params": {"profit_target": 0.01, "stop_loss": 0.005}
    },
    {
        "name": "Gap and Go",
        "category": "day_trading",
        "description": "Buy stocks gapping up 3%+ at market open with high volume. Sell when momentum fades or at 2% profit target.",
        "strategy_code": """
def generate_signals(data):
    signals = []
    prev_close = data.iloc[0]['close']
    gap_pct = (data.iloc[1]['open'] - prev_close) / prev_close
    if gap_pct >= 0.03:
        signals.append({'type': 'buy', 'index': 1, 'target': 1.02})
    return signals
""",
        "default_params": {"min_gap": 0.03, "profit_target": 0.02}
    },
    {
        "name": "Red to Green Move",
        "category": "day_trading",
        "description": "Buy when a stock goes from red to green for the day with volume confirmation. Exit at prior day high or 3% profit.",
        "strategy_code": """
def generate_signals(data):
    signals = []
    prev_close = data.iloc[0]['close']
    for i in range(1, len(data)):
        if data.iloc[i-1]['close'] < prev_close and data.iloc[i]['close'] > prev_close:
            signals.append({'type': 'buy', 'index': i, 'target': 1.03})
    return signals
""",
        "default_params": {"profit_target": 0.03}
    },
    {
        "name": "9 EMA Scalping",
        "category": "day_trading",
        "description": "Buy when price crosses above 9 EMA on 5-min chart. Sell when price closes below 9 EMA.",
        "strategy_code": """
def generate_signals(data):
    ema9 = data['close'].ewm(span=9).mean()
    signals = []
    for i in range(1, len(data)):
        if data.iloc[i-1]['close'] < ema9.iloc[i-1] and data.iloc[i]['close'] > ema9.iloc[i]:
            signals.append({'type': 'buy', 'index': i})
        elif data.iloc[i-1]['close'] > ema9.iloc[i-1] and data.iloc[i]['close'] < ema9.iloc[i]:
            signals.append({'type': 'sell', 'index': i})
    return signals
""",
        "default_params": {"ema_period": 9, "timeframe": "5m"}
    },
    
    # Swing Trading Strategies
    {
        "name": "20/50 EMA Crossover",
        "category": "swing_trading",
        "description": "Buy when 20 EMA crosses above 50 EMA. Sell when 20 EMA crosses below 50 EMA.",
        "strategy_code": """
def generate_signals(data):
    ema20 = data['close'].ewm(span=20).mean()
    ema50 = data['close'].ewm(span=50).mean()
    signals = []
    for i in range(1, len(data)):
        if ema20.iloc[i-1] < ema50.iloc[i-1] and ema20.iloc[i] > ema50.iloc[i]:
            signals.append({'type': 'buy', 'index': i})
        elif ema20.iloc[i-1] > ema50.iloc[i-1] and ema20.iloc[i] < ema50.iloc[i]:
            signals.append({'type': 'sell', 'index': i})
    return signals
""",
        "default_params": {"fast_ema": 20, "slow_ema": 50}
    },
    {
        "name": "RSI Oversold Bounce",
        "category": "swing_trading",
        "description": "Buy when RSI drops below 30 and then rises back above 30. Sell when RSI reaches 70 or after 5 days.",
        "strategy_code": """
def generate_signals(data):
    delta = data['close'].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(14).mean()
    avg_loss = loss.rolling(14).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    signals = []
    for i in range(1, len(data)):
        if rsi.iloc[i-1] < 30 and rsi.iloc[i] > 30:
            signals.append({'type': 'buy', 'index': i})
        elif rsi.iloc[i] >= 70:
            signals.append({'type': 'sell', 'index': i})
    return signals
""",
        "default_params": {"rsi_period": 14, "oversold": 30, "overbought": 70}
    },
    {
        "name": "Bollinger Band Squeeze",
        "category": "swing_trading",
        "description": "Buy when price breaks above upper band after a squeeze. Sell when price touches middle band or 8% profit.",
        "strategy_code": """
def generate_signals(data):
    sma = data['close'].rolling(20).mean()
    std = data['close'].rolling(20).std()
    upper = sma + 2 * std
    lower = sma - 2 * std
    band_width = (upper - lower) / sma
    
    signals = []
    for i in range(1, len(data)):
        if band_width.iloc[i-1] < band_width.iloc[i-5:i-1].mean() * 0.8:  # Squeeze
            if data.iloc[i]['close'] > upper.iloc[i]:
                signals.append({'type': 'buy', 'index': i, 'target': 1.08})
    return signals
""",
        "default_params": {"bb_period": 20, "bb_std": 2, "profit_target": 0.08}
    },
    {
        "name": "MACD Histogram Reversal",
        "category": "swing_trading",
        "description": "Buy when MACD histogram turns positive after being negative. Sell when histogram turns negative again.",
        "strategy_code": """
def generate_signals(data):
    ema12 = data['close'].ewm(span=12).mean()
    ema26 = data['close'].ewm(span=26).mean()
    macd = ema12 - ema26
    signal = macd.ewm(span=9).mean()
    histogram = macd - signal
    
    signals = []
    for i in range(1, len(data)):
        if histogram.iloc[i-1] < 0 and histogram.iloc[i] > 0:
            signals.append({'type': 'buy', 'index': i})
        elif histogram.iloc[i-1] > 0 and histogram.iloc[i] < 0:
            signals.append({'type': 'sell', 'index': i})
    return signals
""",
        "default_params": {"fast": 12, "slow": 26, "signal": 9}
    },
    
    # Long-Term Strategies
    {
        "name": "Graham Value Investing",
        "category": "long_term",
        "description": "Buy stocks with P/E below 15, P/B below 1.5, and debt-to-equity below 0.5. Hold for 1 year minimum.",
        "strategy_code": """
def generate_signals(data, fundamentals):
    signals = []
    pe = fundamentals.get('pe_ratio', 999)
    pb = fundamentals.get('price_to_book', 999)
    de = fundamentals.get('debt_to_equity', 999)
    
    if pe < 15 and pb < 1.5 and de < 0.5:
        signals.append({'type': 'buy', 'hold_days': 365})
    return signals
""",
        "default_params": {"max_pe": 15, "max_pb": 1.5, "max_de": 0.5, "hold_period": 365}
    },
    {
        "name": "Dividend Growth Strategy",
        "category": "long_term",
        "description": "Buy stocks with 10+ years of consecutive dividend increases and yield above 2%. Hold indefinitely.",
        "strategy_code": """
def generate_signals(data, fundamentals):
    signals = []
    div_years = fundamentals.get('years_dividend_growth', 0)
    div_yield = fundamentals.get('dividend_yield', 0)
    
    if div_years >= 10 and div_yield >= 0.02:
        signals.append({'type': 'buy', 'hold': 'indefinite'})
    return signals
""",
        "default_params": {"min_div_years": 10, "min_yield": 0.02}
    },
    {
        "name": "Growth at Reasonable Price (GARP)",
        "category": "long_term",
        "description": "Buy stocks with PEG ratio below 1 and earnings growth above 15%. Hold until PEG exceeds 2.",
        "strategy_code": """
def generate_signals(data, fundamentals):
    signals = []
    peg = fundamentals.get('peg_ratio', 999)
    growth = fundamentals.get('earnings_growth_yoy', 0)
    
    if peg < 1 and growth > 0.15:
        signals.append({'type': 'buy'})
    elif peg > 2:
        signals.append({'type': 'sell'})
    return signals
""",
        "default_params": {"max_peg": 1, "min_growth": 0.15, "sell_peg": 2}
    },
    {
        "name": "Momentum Factor Strategy",
        "category": "long_term",
        "description": "Buy top 10% of stocks by 12-month momentum. Rebalance monthly.",
        "strategy_code": """
def generate_signals(data):
    if len(data) < 252:
        return []
    momentum_12m = (data.iloc[-1]['close'] - data.iloc[-252]['close']) / data.iloc[-252]['close']
    signals = []
    if momentum_12m > 0.20:  # Top performer threshold
        signals.append({'type': 'buy', 'rebalance': 'monthly'})
    return signals
""",
        "default_params": {"lookback": 252, "top_percentile": 10, "rebalance": "monthly"}
    },
]


def populate_strategies():
    """Populate the database with baseline strategies."""
    print("=" * 60)
    print("Populating Baseline Strategies")
    print("=" * 60)
    
    created = 0
    updated = 0
    
    for strategy_data in BASELINE_STRATEGIES:
        strategy, was_created = BaselineStrategy.objects.update_or_create(
            name=strategy_data['name'],
            defaults={
                'category': strategy_data['category'],
                'description': strategy_data['description'],
                'strategy_code': strategy_data['strategy_code'],
                'default_params': strategy_data['default_params'],
                'is_active': True,
            }
        )
        
        if was_created:
            created += 1
            print(f"  Created: {strategy.name} ({strategy.category})")
        else:
            updated += 1
            print(f"  Updated: {strategy.name}")
    
    print(f"\nCreated: {created}, Updated: {updated}")
    print(f"Total strategies: {BaselineStrategy.objects.count()}")
    print("=" * 60)


if __name__ == '__main__':
    populate_strategies()
