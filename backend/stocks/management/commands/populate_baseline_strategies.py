"""
Management command to populate 20 baseline trading strategies
Run with: python manage.py populate_baseline_strategies
"""
from django.core.management.base import BaseCommand
from stocks.models import BaselineStrategy


class Command(BaseCommand):
    help = 'Populate 20 baseline trading strategies for backtesting'

    def handle(self, *args, **options):
        strategies = [
            # ===== DAY TRADING STRATEGIES (7) =====
            {
                'name': 'Opening Range Breakout (ORB)',
                'category': 'day_trading',
                'description': 'Buy when price breaks above the first 15-minute high with volume confirmation',
                'strategy_code': '''
def entry_condition(data, index):
    if index < 15:
        return False
    # Check if current price breaks above first 15min high
    first_15min_high = data.iloc[:15]['High'].max()
    current_price = data.iloc[index]['Close']
    volume_ratio = data.iloc[index]['Volume'] / data.iloc[:15]['Volume'].mean()
    return current_price > first_15min_high and volume_ratio > 1.5

def exit_condition(data, index, entry_price, entry_index):
    current_price = data.iloc[index]['Close']
    # Stop loss: 2% below entry
    if current_price < entry_price * 0.98:
        return True
    # Take profit: 3% above entry
    if current_price > entry_price * 1.03:
        return True
    # Exit at end of day
    return index >= len(data) - 10
'''
            },
            {
                'name': 'VWAP Bounce',
                'category': 'day_trading',
                'description': 'Buy when price bounces off VWAP with bullish momentum',
                'strategy_code': '''
import numpy as np

def calculate_vwap(data, index):
    prices = data.iloc[:index+1]['Close'].values
    volumes = data.iloc[:index+1]['Volume'].values
    return np.sum(prices * volumes) / np.sum(volumes)

def entry_condition(data, index):
    if index < 20:
        return False
    vwap = calculate_vwap(data, index)
    current_price = data.iloc[index]['Close']
    prev_price = data.iloc[index-1]['Close']
    # Buy on bounce: prev below VWAP, current above
    return prev_price < vwap and current_price > vwap

def exit_condition(data, index, entry_price, entry_index):
    current_price = data.iloc[index]['Close']
    if current_price < entry_price * 0.985:
        return True
    if current_price > entry_price * 1.025:
        return True
    return index >= len(data) - 5
'''
            },
            {
                'name': 'Gap and Go',
                'category': 'day_trading',
                'description': 'Trade stocks that gap up at open with strong volume',
                'strategy_code': '''
def entry_condition(data, index):
    if index < 1:
        return False
    prev_close = data.iloc[index-1]['Close']
    open_price = data.iloc[index]['Open']
    gap_percent = ((open_price - prev_close) / prev_close) * 100
    volume_ratio = data.iloc[index]['Volume'] / data.iloc[:max(1,index)]['Volume'].mean()
    return gap_percent > 2 and volume_ratio > 2

def exit_condition(data, index, entry_price, entry_index):
    current_price = data.iloc[index]['Close']
    if current_price < entry_price * 0.97:
        return True
    if current_price > entry_price * 1.05:
        return True
    return (index - entry_index) > 30
'''
            },
            {
                'name': 'Red to Green Move',
                'category': 'day_trading',
                'description': 'Buy when stock moves from red to green intraday',
                'strategy_code': '''
def entry_condition(data, index):
    if index < 5:
        return False
    open_price = data.iloc[index]['Open']
    current_price = data.iloc[index]['Close']
    prev_close = data.iloc[index-1]['Close']
    # Was below previous close, now above
    was_red = open_price < prev_close
    now_green = current_price > prev_close
    return was_red and now_green

def exit_condition(data, index, entry_price, entry_index):
    current_price = data.iloc[index]['Close']
    if current_price < entry_price * 0.98:
        return True
    if current_price > entry_price * 1.04:
        return True
    return (index - entry_index) > 20
'''
            },
            {
                'name': '9 EMA Scalping',
                'category': 'day_trading',
                'description': 'Scalp trades using 9 EMA as dynamic support',
                'strategy_code': '''
def calculate_ema(data, period, index):
    if index < period:
        return data.iloc[:index+1]['Close'].mean()
    prices = data.iloc[:index+1]['Close'].values
    multiplier = 2 / (period + 1)
    ema = prices[0]
    for price in prices[1:]:
        ema = (price * multiplier) + (ema * (1 - multiplier))
    return ema

def entry_condition(data, index):
    if index < 15:
        return False
    ema9 = calculate_ema(data, 9, index)
    current_price = data.iloc[index]['Close']
    prev_price = data.iloc[index-1]['Close']
    return prev_price < ema9 and current_price > ema9

def exit_condition(data, index, entry_price, entry_index):
    current_price = data.iloc[index]['Close']
    ema9 = calculate_ema(data, 9, index)
    if current_price < ema9:
        return True
    if current_price > entry_price * 1.02:
        return True
    return (index - entry_index) > 15
'''
            },
            {
                'name': 'High of Day Breakout',
                'category': 'day_trading',
                'description': 'Buy when price makes new high of day',
                'strategy_code': '''
def entry_condition(data, index):
    if index < 30:
        return False
    current_high = data.iloc[index]['High']
    previous_hod = data.iloc[:index]['High'].max()
    return current_high > previous_hod

def exit_condition(data, index, entry_price, entry_index):
    current_price = data.iloc[index]['Close']
    if current_price < entry_price * 0.985:
        return True
    if current_price > entry_price * 1.04:
        return True
    return index >= len(data) - 10
'''
            },
            {
                'name': 'Support/Resistance Reversal',
                'category': 'day_trading',
                'description': 'Buy at support level with reversal confirmation',
                'strategy_code': '''
def entry_condition(data, index):
    if index < 20:
        return False
    current_price = data.iloc[index]['Close']
    prev_low = data.iloc[index-5:index]['Low'].min()
    # Price near support and starting to bounce
    near_support = abs(current_price - prev_low) / prev_low < 0.01
    bullish_candle = data.iloc[index]['Close'] > data.iloc[index]['Open']
    return near_support and bullish_candle

def exit_condition(data, index, entry_price, entry_index):
    current_price = data.iloc[index]['Close']
    if current_price < entry_price * 0.98:
        return True
    if current_price > entry_price * 1.03:
        return True
    return (index - entry_index) > 25
'''
            },
            
            # ===== SWING TRADING STRATEGIES (7) =====
            {
                'name': '20/50 EMA Crossover',
                'category': 'swing_trading',
                'description': 'Buy when 20 EMA crosses above 50 EMA',
                'strategy_code': '''
def calculate_ema(data, period, index):
    if index < period:
        return data.iloc[:index+1]['Close'].mean()
    prices = data.iloc[:index+1]['Close'].values
    multiplier = 2 / (period + 1)
    ema = prices[0]
    for price in prices[1:]:
        ema = (price * multiplier) + (ema * (1 - multiplier))
    return ema

def entry_condition(data, index):
    if index < 60:
        return False
    ema20_curr = calculate_ema(data, 20, index)
    ema50_curr = calculate_ema(data, 50, index)
    ema20_prev = calculate_ema(data, 20, index-1)
    ema50_prev = calculate_ema(data, 50, index-1)
    # Bullish crossover
    return ema20_prev < ema50_prev and ema20_curr > ema50_curr

def exit_condition(data, index, entry_price, entry_index):
    current_price = data.iloc[index]['Close']
    ema20 = calculate_ema(data, 20, index)
    ema50 = calculate_ema(data, 50, index)
    # Exit on bearish crossover or stop loss
    if ema20 < ema50:
        return True
    if current_price < entry_price * 0.93:
        return True
    if current_price > entry_price * 1.15:
        return True
    return False
'''
            },
            {
                'name': 'RSI Oversold Bounce',
                'category': 'swing_trading',
                'description': 'Buy when RSI crosses above 30 from oversold',
                'strategy_code': '''
def calculate_rsi(data, period, index):
    if index < period + 1:
        return 50
    prices = data.iloc[index-period:index+1]['Close'].values
    deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
    gains = [d if d > 0 else 0 for d in deltas]
    losses = [-d if d < 0 else 0 for d in deltas]
    avg_gain = sum(gains) / period
    avg_loss = sum(losses) / period
    if avg_loss == 0:
        return 100
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def entry_condition(data, index):
    if index < 20:
        return False
    rsi_curr = calculate_rsi(data, 14, index)
    rsi_prev = calculate_rsi(data, 14, index-1)
    return rsi_prev < 30 and rsi_curr > 30

def exit_condition(data, index, entry_price, entry_index):
    current_price = data.iloc[index]['Close']
    rsi = calculate_rsi(data, 14, index)
    if rsi > 70:
        return True
    if current_price < entry_price * 0.92:
        return True
    if current_price > entry_price * 1.20:
        return True
    return False
'''
            },
            {
                'name': 'Cup and Handle Pattern',
                'category': 'swing_trading',
                'description': 'Buy on breakout from cup and handle formation',
                'strategy_code': '''
def entry_condition(data, index):
    if index < 50:
        return False
    # Simple cup detection: price makes a U-shape
    lookback = 30
    prices = data.iloc[index-lookback:index]['Close'].values
    mid_point = lookback // 2
    left_high = max(prices[:mid_point])
    cup_low = min(prices[mid_point-5:mid_point+5])
    right_high = max(prices[mid_point:])
    current_price = data.iloc[index]['Close']
    # Cup formed and breaking out
    cup_formed = abs(left_high - right_high) / left_high < 0.05
    breakout = current_price > right_high * 1.02
    return cup_formed and breakout

def exit_condition(data, index, entry_price, entry_index):
    current_price = data.iloc[index]['Close']
    if current_price < entry_price * 0.90:
        return True
    if current_price > entry_price * 1.25:
        return True
    return (index - entry_index) > 30
'''
            },
            {
                'name': 'Bollinger Band Squeeze',
                'category': 'swing_trading',
                'description': 'Buy on volatility expansion after squeeze',
                'strategy_code': '''
def calculate_bollinger_bands(data, period, index):
    if index < period:
        return None, None, None
    prices = data.iloc[index-period:index+1]['Close'].values
    sma = sum(prices) / len(prices)
    std = (sum((x - sma) ** 2 for x in prices) / len(prices)) ** 0.5
    upper = sma + (2 * std)
    lower = sma - (2 * std)
    return upper, sma, lower

def entry_condition(data, index):
    if index < 25:
        return False
    upper, sma, lower = calculate_bollinger_bands(data, 20, index)
    if not upper:
        return False
    bandwidth = (upper - lower) / sma
    prev_upper, prev_sma, prev_lower = calculate_bollinger_bands(data, 20, index-1)
    if not prev_upper:
        return False
    prev_bandwidth = (prev_upper - prev_lower) / prev_sma
    # Squeeze: bandwidth was small, now expanding
    current_price = data.iloc[index]['Close']
    squeeze = prev_bandwidth < 0.10
    expansion = bandwidth > prev_bandwidth * 1.1
    breakout = current_price > sma
    return squeeze and expansion and breakout

def exit_condition(data, index, entry_price, entry_index):
    current_price = data.iloc[index]['Close']
    if current_price < entry_price * 0.93:
        return True
    if current_price > entry_price * 1.18:
        return True
    return (index - entry_index) > 25
'''
            },
            {
                'name': 'MACD Histogram Reversal',
                'category': 'swing_trading',
                'description': 'Buy when MACD histogram turns positive',
                'strategy_code': '''
def calculate_ema(data, period, index):
    if index < period:
        return data.iloc[:index+1]['Close'].mean()
    prices = data.iloc[:index+1]['Close'].values
    multiplier = 2 / (period + 1)
    ema = prices[0]
    for price in prices[1:]:
        ema = (price * multiplier) + (ema * (1 - multiplier))
    return ema

def calculate_macd(data, index):
    if index < 26:
        return 0, 0, 0
    ema12 = calculate_ema(data, 12, index)
    ema26 = calculate_ema(data, 26, index)
    macd_line = ema12 - ema26
    # Simple signal line approximation
    signal_line = macd_line * 0.9
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram

def entry_condition(data, index):
    if index < 30:
        return False
    _, _, hist_curr = calculate_macd(data, index)
    _, _, hist_prev = calculate_macd(data, index-1)
    return hist_prev < 0 and hist_curr > 0

def exit_condition(data, index, entry_price, entry_index):
    current_price = data.iloc[index]['Close']
    _, _, histogram = calculate_macd(data, index)
    if histogram < 0:
        return True
    if current_price < entry_price * 0.92:
        return True
    if current_price > entry_price * 1.20:
        return True
    return False
'''
            },
            {
                'name': 'Weekly Breakout',
                'category': 'swing_trading',
                'description': 'Buy on breakout of weekly high with volume',
                'strategy_code': '''
def entry_condition(data, index):
    if index < 10:
        return False
    # Approximate weekly high (5 trading days)
    weekly_lookback = min(5, index)
    weekly_high = data.iloc[index-weekly_lookback:index]['High'].max()
    current_price = data.iloc[index]['Close']
    volume_ratio = data.iloc[index]['Volume'] / data.iloc[index-weekly_lookback:index]['Volume'].mean()
    return current_price > weekly_high and volume_ratio > 1.3

def exit_condition(data, index, entry_price, entry_index):
    current_price = data.iloc[index]['Close']
    if current_price < entry_price * 0.90:
        return True
    if current_price > entry_price * 1.25:
        return True
    return (index - entry_index) > 20
'''
            },
            {
                'name': 'Mean Reversion to 50 SMA',
                'category': 'swing_trading',
                'description': 'Buy when price reverts to 50-day SMA',
                'strategy_code': '''
def calculate_sma(data, period, index):
    if index < period:
        return data.iloc[:index+1]['Close'].mean()
    return data.iloc[index-period+1:index+1]['Close'].mean()

def entry_condition(data, index):
    if index < 55:
        return False
    sma50 = calculate_sma(data, 50, index)
    current_price = data.iloc[index]['Close']
    prev_price = data.iloc[index-1]['Close']
    # Price was below SMA, now touching or crossing above
    below_sma = prev_price < sma50 * 0.97
    at_sma = abs(current_price - sma50) / sma50 < 0.02
    return below_sma and at_sma

def exit_condition(data, index, entry_price, entry_index):
    current_price = data.iloc[index]['Close']
    sma50 = calculate_sma(data, 50, index)
    if current_price > sma50 * 1.05:
        return True
    if current_price < entry_price * 0.93:
        return True
    return (index - entry_index) > 15
'''
            },
            
            # ===== LONG-TERM STRATEGIES (6) =====
            {
                'name': 'Graham Value Investing',
                'category': 'long_term',
                'description': 'Buy undervalued stocks based on Benjamin Graham principles',
                'strategy_code': '''
def entry_condition(data, index):
    if index < 50:
        return False
    # Simple value entry: significant price drop
    current_price = data.iloc[index]['Close']
    avg_price_50d = data.iloc[index-50:index]['Close'].mean()
    price_discount = (avg_price_50d - current_price) / avg_price_50d
    return price_discount > 0.15

def exit_condition(data, index, entry_price, entry_index):
    current_price = data.iloc[index]['Close']
    # Long-term hold: exit at 30% gain or 15% loss
    if current_price > entry_price * 1.30:
        return True
    if current_price < entry_price * 0.85:
        return True
    # Or hold for 60 days minimum
    return (index - entry_index) > 60
'''
            },
            {
                'name': 'Dividend Growth Strategy',
                'category': 'long_term',
                'description': 'Invest in stocks with consistent dividend growth',
                'strategy_code': '''
def entry_condition(data, index):
    if index < 30:
        return False
    # Buy on dips in uptrend
    current_price = data.iloc[index]['Close']
    sma_30 = data.iloc[index-30:index]['Close'].mean()
    sma_60 = data.iloc[index-60:index]['Close'].mean() if index >= 60 else sma_30
    uptrend = sma_30 > sma_60
    dip = current_price < sma_30 * 0.97
    return uptrend and dip

def exit_condition(data, index, entry_price, entry_index):
    current_price = data.iloc[index]['Close']
    # Conservative exits for dividend strategy
    if current_price < entry_price * 0.88:
        return True
    if current_price > entry_price * 1.25:
        return True
    return False
'''
            },
            {
                'name': 'Growth at Reasonable Price (GARP)',
                'category': 'long_term',
                'description': 'Balance growth and value investing',
                'strategy_code': '''
def entry_condition(data, index):
    if index < 40:
        return False
    # Buy on pullback in growth stocks
    current_price = data.iloc[index]['Close']
    high_20d = data.iloc[index-20:index]['High'].max()
    pullback = (high_20d - current_price) / high_20d
    sma_40 = data.iloc[index-40:index]['Close'].mean()
    above_trend = current_price > sma_40
    return pullback > 0.08 and pullback < 0.20 and above_trend

def exit_condition(data, index, entry_price, entry_index):
    current_price = data.iloc[index]['Close']
    if current_price > entry_price * 1.35:
        return True
    if current_price < entry_price * 0.87:
        return True
    return (index - entry_index) > 50
'''
            },
            {
                'name': 'Dogs of the Dow',
                'category': 'long_term',
                'description': 'Buy highest dividend yielding stocks annually',
                'strategy_code': '''
def entry_condition(data, index):
    if index < 252:  # One year of data
        return False
    # Simple annual rebalance simulation: buy once per year
    if index % 252 == 0:  # Approximate annual rebalance
        return True
    return False

def exit_condition(data, index, entry_price, entry_index):
    current_price = data.iloc[index]['Close']
    # Hold for one year or until significant loss
    if current_price < entry_price * 0.80:
        return True
    return (index - entry_index) >= 252
'''
            },
            {
                'name': 'Momentum Factor Strategy',
                'category': 'long_term',
                'description': 'Follow strong momentum trends',
                'strategy_code': '''
def entry_condition(data, index):
    if index < 90:
        return False
    # Calculate 3-month momentum
    current_price = data.iloc[index]['Close']
    price_90d_ago = data.iloc[index-90]['Close']
    momentum = (current_price - price_90d_ago) / price_90d_ago
    # Strong positive momentum
    return momentum > 0.20

def exit_condition(data, index, entry_price, entry_index):
    current_price = data.iloc[index]['Close']
    if index < 30:
        return False
    # Exit if momentum reverses
    price_30d_ago = data.iloc[index-30]['Close']
    recent_momentum = (current_price - price_30d_ago) / price_30d_ago
    if recent_momentum < -0.10:
        return True
    if current_price < entry_price * 0.85:
        return True
    return (index - entry_index) > 120
'''
            },
            {
                'name': 'Small Cap Value',
                'category': 'long_term',
                'description': 'Invest in undervalued small-cap stocks',
                'strategy_code': '''
def entry_condition(data, index):
    if index < 60:
        return False
    # Buy on significant dips
    current_price = data.iloc[index]['Close']
    high_60d = data.iloc[index-60:index]['High'].max()
    drawdown = (high_60d - current_price) / high_60d
    # Look for 20%+ drawdowns as entry
    return drawdown > 0.20

def exit_condition(data, index, entry_price, entry_index):
    current_price = data.iloc[index]['Close']
    # Exit at 50% gain or 20% loss
    if current_price > entry_price * 1.50:
        return True
    if current_price < entry_price * 0.80:
        return True
    return False
'''
            }
        ]

        created_count = 0
        updated_count = 0

        for strategy_data in strategies:
            strategy, created = BaselineStrategy.objects.update_or_create(
                name=strategy_data['name'],
                defaults={
                    'category': strategy_data['category'],
                    'description': strategy_data['description'],
                    'strategy_code': strategy_data['strategy_code'],
                    'is_active': True
                }
            )
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'✓ Created: {strategy.name}'))
            else:
                updated_count += 1
                self.stdout.write(self.style.WARNING(f'↻ Updated: {strategy.name}'))

        self.stdout.write(self.style.SUCCESS(f'\n✅ Done! Created {created_count}, Updated {updated_count}'))
        self.stdout.write(self.style.SUCCESS(f'Total strategies: {BaselineStrategy.objects.count()}'))
