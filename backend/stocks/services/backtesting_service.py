"""
AI-Powered Backtesting Service with Static/Mock AI
Phase 4 Implementation - No API Keys Required
"""
import os
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Tuple
import yfinance as yf
from django.conf import settings
from ..models import BacktestRun, BaselineStrategy
import re
import signal
from .stooq_data import StooqSourceConfig, fetch_stooq_from_combined_csv, fetch_stooq_remote_daily


class BacktestingService:
    """Service for AI-powered strategy backtesting with static implementation"""
    
    def __init__(self):
        # Static mode - no API key required
        self.static_mode = True
    
    def parse_strategy_with_static_ai(self, strategy_text: str, category: str) -> Dict:
        """
        Parse natural language strategy using rule-based AI (no API key needed)
        
        Returns:
            Dict with parsed strategy components and AI understanding
        """
        strategy_lower = strategy_text.lower()
        
        # Extract key components
        parsed = {
            'indicators': [],
            'entry_conditions': [],
            'exit_conditions': [],
            'stop_loss': None,
            'take_profit': None,
            'position_sizing': '100% per trade',
            'understood': True,
            'clarifications_needed': []
        }
        
        # Detect indicators
        if 'rsi' in strategy_lower:
            parsed['indicators'].append('RSI')
            # Extract RSI threshold
            rsi_match = re.search(r'rsi.*?(\d+)', strategy_lower)
            if rsi_match:
                threshold = int(rsi_match.group(1))
                if threshold < 40:
                    parsed['entry_conditions'].append(f'RSI below {threshold} (oversold)')
                elif threshold > 60:
                    parsed['exit_conditions'].append(f'RSI above {threshold} (overbought)')
        
        if 'macd' in strategy_lower:
            parsed['indicators'].append('MACD')
            if 'cross' in strategy_lower:
                parsed['entry_conditions'].append('MACD bullish crossover')
                parsed['exit_conditions'].append('MACD bearish crossover')
        
        if 'moving average' in strategy_lower or 'ma' in strategy_lower:
            parsed['indicators'].append('Moving Average')
            if '50' in strategy_text and '200' in strategy_text:
                parsed['entry_conditions'].append('Golden Cross (50 MA crosses above 200 MA)')
                parsed['exit_conditions'].append('Death Cross (50 MA crosses below 200 MA)')
            elif 'cross above' in strategy_lower:
                parsed['entry_conditions'].append('Price crosses above MA')
        
        if 'bollinger' in strategy_lower:
            parsed['indicators'].append('Bollinger Bands')
            parsed['entry_conditions'].append('Price touches lower Bollinger Band')
            parsed['exit_conditions'].append('Price touches upper Bollinger Band')
        
        if 'volume' in strategy_lower:
            parsed['indicators'].append('Volume')
            if 'spike' in strategy_lower or 'high' in strategy_lower:
                parsed['entry_conditions'].append('High volume confirmation')
        
        # Detect stop loss
        stop_loss_match = re.search(r'stop.*?loss.*?(\d+)%', strategy_lower)
        if stop_loss_match:
            parsed['stop_loss'] = f"{stop_loss_match.group(1)}%"
        elif 'stop' in strategy_lower:
            parsed['stop_loss'] = "5% (default)"
        
        # Detect take profit
        take_profit_match = re.search(r'take.*?profit.*?(\d+)%', strategy_lower)
        if take_profit_match:
            parsed['take_profit'] = f"{take_profit_match.group(1)}%"
        elif 'profit' in strategy_lower and 'target' in strategy_lower:
            parsed['take_profit'] = "10% (default)"
        
        # Check if we need clarifications
        if not parsed['entry_conditions']:
            parsed['clarifications_needed'].append('What specific conditions should trigger a BUY?')
            parsed['understood'] = False
        
        if not parsed['exit_conditions']:
            parsed['clarifications_needed'].append('What conditions should trigger a SELL?')
            parsed['understood'] = False
        
        return parsed
    
    def generate_strategy_code(self, strategy_text: str, category: str) -> Tuple[str, str, Dict]:
        """
        Use static AI to convert natural language strategy to Python code
        
        Returns:
            Tuple of (generated_code, error_message, ai_understanding)
        """
        # Parse strategy with static AI
        ai_understanding = self.parse_strategy_with_static_ai(strategy_text, category)
        
        # If clarifications needed, return error
        if not ai_understanding['understood']:
            clarifications = '\n'.join(f"- {c}" for c in ai_understanding['clarifications_needed'])
            return "", f"Strategy needs clarification:\n{clarifications}", ai_understanding
        
        # Generate code based on parsed strategy
        code = self._generate_code_from_parsed_strategy(ai_understanding, category)
        
        return code, "", ai_understanding
    
    def _generate_code_from_parsed_strategy(self, parsed: Dict, category: str) -> str:
        """
        Generate Python code from parsed strategy components
        """
        # Default template-based code generation
        code_parts = []
        
        # Add imports and indicator calculations
        code_parts.append("""
import pandas as pd
import numpy as np

# Calculate technical indicators
def calculate_indicators(data):
    df = data.copy()
    
    # RSI
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    # Moving Averages
    df['MA_50'] = df['Close'].rolling(window=50).mean()
    df['MA_200'] = df['Close'].rolling(window=200).mean()
    
    # MACD
    exp1 = df['Close'].ewm(span=12, adjust=False).mean()
    exp2 = df['Close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = exp1 - exp2
    df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
    
    # Bollinger Bands
    df['BB_Middle'] = df['Close'].rolling(window=20).mean()
    bb_std = df['Close'].rolling(window=20).std()
    df['BB_Upper'] = df['BB_Middle'] + (bb_std * 2)
    df['BB_Lower'] = df['BB_Middle'] - (bb_std * 2)
    
    # Volume MA
    df['Volume_MA'] = df['Volume'].rolling(window=20).mean()
    
    return df

data = calculate_indicators(data)
""")
        
        # Generate entry condition
        entry_logic = []
        if 'RSI' in parsed['indicators']:
            entry_logic.append("data.iloc[index]['RSI'] < 30")
        if 'MACD' in parsed['indicators']:
            entry_logic.append("data.iloc[index]['MACD'] > data.iloc[index]['MACD_Signal']")
            entry_logic.append("data.iloc[index-1]['MACD'] <= data.iloc[index-1]['MACD_Signal']")
        if 'Moving Average' in parsed['indicators']:
            entry_logic.append("data.iloc[index]['MA_50'] > data.iloc[index]['MA_200']")
        if 'Bollinger Bands' in parsed['indicators']:
            entry_logic.append("data.iloc[index]['Close'] <= data.iloc[index]['BB_Lower']")
        if 'Volume' in parsed['indicators']:
            entry_logic.append("data.iloc[index]['Volume'] > data.iloc[index]['Volume_MA'] * 1.5")
        
        entry_condition = " and \n        ".join(entry_logic) if entry_logic else "data.iloc[index]['RSI'] < 30"
        
        code_parts.append(f"""
def entry_condition(data, index):
    if index < 200:  # Need enough data for indicators
        return False
    
    try:
        return ({entry_condition})
    except (KeyError, IndexError):
        return False
""")
        
        # Generate exit condition
        exit_logic = []
        if 'RSI' in parsed['indicators']:
            exit_logic.append("data.iloc[index]['RSI'] > 70")
        if 'MACD' in parsed['indicators']:
            exit_logic.append("data.iloc[index]['MACD'] < data.iloc[index]['MACD_Signal']")
        if 'Moving Average' in parsed['indicators']:
            exit_logic.append("data.iloc[index]['MA_50'] < data.iloc[index]['MA_200']")
        if 'Bollinger Bands' in parsed['indicators']:
            exit_logic.append("data.iloc[index]['Close'] >= data.iloc[index]['BB_Upper']")
        
        # Add stop loss and take profit
        stop_loss_pct = 5
        take_profit_pct = 10
        if parsed['stop_loss']:
            match = re.search(r'(\d+)', parsed['stop_loss'])
            if match:
                stop_loss_pct = int(match.group(1))
        if parsed['take_profit']:
            match = re.search(r'(\d+)', parsed['take_profit'])
            if match:
                take_profit_pct = int(match.group(1))
        
        exit_condition = " or \n        ".join(exit_logic) if exit_logic else "data.iloc[index]['RSI'] > 70"
        
        code_parts.append(f"""
def exit_condition(data, index, entry_price, entry_index):
    try:
        current_price = data.iloc[index]['Close']
        price_change_pct = ((current_price - entry_price) / entry_price) * 100
        
        # Stop loss
        if price_change_pct <= -{stop_loss_pct}:
            return True
        
        # Take profit
        if price_change_pct >= {take_profit_pct}:
            return True
        
        # Technical exit conditions
        return ({exit_condition})
    except (KeyError, IndexError):
        return False
""")
        
        return "\n".join(code_parts)
    
    def run_backtest(self, backtest_run: BacktestRun) -> Dict:
        """
        Execute the backtest and return results
        
        Args:
            backtest_run: BacktestRun model instance
        
        Returns:
            Dictionary with backtest results
        """
        try:
            # Generate code if not already generated
            if not backtest_run.generated_code:
                code, error, ai_understanding = self.generate_strategy_code(
                    backtest_run.strategy_text,
                    backtest_run.category
                )
                if error:
                    return {"error": error, "ai_understanding": ai_understanding}
                backtest_run.generated_code = code
                backtest_run.save()
            
            # Fetch historical data
            data = self._fetch_historical_data(
                backtest_run.symbols,
                backtest_run.start_date,
                backtest_run.end_date
            )
            
            if data.empty:
                return {"error": "No historical data available for selected symbols"}
            
            # Execute strategy
            results = self._execute_strategy(
                backtest_run.generated_code,
                data,
                float(backtest_run.initial_capital)
            )
            
            return results
        
        except Exception as e:
            return {"error": f"Backtest execution failed: {str(e)}"}
    
    def _fetch_historical_data(self, symbols: List[str], start_date, end_date) -> pd.DataFrame:
        """Fetch historical price data for symbols"""
        try:
            # For simplicity, use first symbol only
            # In production, you'd implement multi-symbol logic
            symbol = symbols[0] if isinstance(symbols, list) else symbols

            provider = (os.environ.get("BACKTEST_DATA_PROVIDER") or "yfinance").strip().lower()
            if provider == "stooq":
                cfg = StooqSourceConfig.from_env()
                interval = os.environ.get("BACKTEST_DATA_INTERVAL")  # optional, e.g. "60" or "5"
                df = fetch_stooq_from_combined_csv(symbol, start_date, end_date, cfg=cfg, interval=interval)
                if df.empty:
                    df = fetch_stooq_remote_daily(symbol, start_date, end_date, cfg=cfg)
                return df
            
            ticker = yf.Ticker(symbol)
            df = ticker.history(start=start_date, end=end_date)
            
            if df.empty:
                return pd.DataFrame()
            
            # Rename columns to match expected format
            df = df.reset_index()
            df.columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Dividends', 'Stock Splits']
            df = df[['Date', 'Open', 'High', 'Low', 'Close', 'Volume']]
            
            return df
        
        except Exception as e:
            print(f"Error fetching data: {e}")
            return pd.DataFrame()
    
    def _execute_strategy(self, code: str, data: pd.DataFrame, initial_capital: float) -> Dict:
        """
        Execute the trading strategy on historical data
        
        Returns:
            Dictionary with backtest metrics
        """
        try:
            # NOTE: This executes dynamically-generated code. Treat as high-risk.
            # We restrict builtins and perform a basic denylist check, but this is
            # not a complete sandbox. For production, run this in an isolated worker.
            # The code generator (and LLMs) often include `import` statements, but we don't
            # expose `__import__` in builtins. Strip imports to keep the execution surface
            # small and deterministic (pd/np are injected via the namespace below).
            code = "\n".join(
                line for line in code.splitlines()
                if not re.match(r"^\s*(import|from)\s+", line)
            )

            forbidden = ("open(", "exec(", "eval(", "__", "os.", "sys.", "subprocess", "socket", "pathlib")
            if any(tok in code for tok in forbidden):
                return {"error": "Generated strategy code contains forbidden operations"}

            safe_builtins = {
                "abs": abs,
                "min": min,
                "max": max,
                "sum": sum,
                "len": len,
                "range": range,
                "round": round,
            }

            # Create execution namespace (restricted)
            namespace = {
                "__builtins__": safe_builtins,
                "pd": pd,
                "np": np,
                "data": data,
            }

            def _with_timeout(seconds: float, fn):
                # Unix-only safety valve to prevent infinite execution.
                def _handler(signum, frame):  # noqa: ARG001
                    raise TimeoutError("Timed out")

                prev = signal.signal(signal.SIGALRM, _handler)
                signal.setitimer(signal.ITIMER_REAL, seconds)
                try:
                    return fn()
                finally:
                    signal.setitimer(signal.ITIMER_REAL, 0)
                    signal.signal(signal.SIGALRM, prev)

            # Execute the generated code to define functions (bounded time)
            _with_timeout(0.5, lambda: exec(code, namespace))
            
            # Get entry and exit functions
            entry_condition = namespace.get('entry_condition')
            exit_condition = namespace.get('exit_condition')
            
            if not entry_condition or not exit_condition:
                return {"error": "Generated code missing entry_condition or exit_condition functions"}
            
            # Run backtest simulation
            trades = []
            equity_curve = [initial_capital]
            cash = initial_capital
            position = None
            
            for i in range(len(data)):
                if position is None:
                    # Check for entry
                    try:
                        ok = _with_timeout(0.05, lambda: bool(entry_condition(data, i)))
                        if ok:
                            entry_price = data.iloc[i]['Close']
                            shares = cash / entry_price
                            position = {
                                'entry_index': i,
                                'entry_date': data.iloc[i]['Date'],
                                'entry_price': entry_price,
                                'shares': shares
                            }
                            cash = 0
                    except Exception as e:
                        print(f"Entry condition error at index {i}: {e}")
                else:
                    # Check for exit
                    try:
                        current_price = data.iloc[i]['Close']
                        ok = _with_timeout(
                            0.05,
                            lambda: bool(exit_condition(data, i, position['entry_price'], position['entry_index'])),
                        )
                        if ok:
                            exit_price = current_price
                            cash = position['shares'] * exit_price
                            
                            trade_return = ((exit_price - position['entry_price']) / position['entry_price']) * 100
                            trade_profit = (exit_price - position['entry_price']) * position['shares']
                            
                            trades.append({
                                'entry_date': str(position['entry_date']),
                                'exit_date': str(data.iloc[i]['Date']),
                                'entry_price': float(position['entry_price']),
                                'exit_price': float(exit_price),
                                'shares': float(position['shares']),
                                'return_pct': float(trade_return),
                                # Profit should be per-trade P&L, not cumulative vs initial capital.
                                'profit': float(trade_profit)
                            })
                            
                            position = None
                    except Exception as e:
                        print(f"Exit condition error at index {i}: {e}")
                
                # Update equity curve
                if position:
                    current_value = position['shares'] * data.iloc[i]['Close']
                    equity_curve.append(current_value)
                else:
                    equity_curve.append(cash)
            
            # Close any open position at the end
            if position:
                final_price = data.iloc[-1]['Close']
                cash = position['shares'] * final_price
                trade_return = ((final_price - position['entry_price']) / position['entry_price']) * 100
                trade_profit = (final_price - position['entry_price']) * position['shares']
                trades.append({
                    'entry_date': str(position['entry_date']),
                    'exit_date': str(data.iloc[-1]['Date']),
                    'entry_price': float(position['entry_price']),
                    'exit_price': float(final_price),
                    'shares': float(position['shares']),
                    'return_pct': float(trade_return),
                    # Profit should be per-trade P&L, not cumulative vs initial capital.
                    'profit': float(trade_profit)
                })
            
            # Calculate metrics
            metrics = self._calculate_metrics(trades, equity_curve, initial_capital)
            metrics['trades_data'] = trades
            metrics['equity_curve'] = [float(x) for x in equity_curve]
            
            return metrics
        
        except Exception as e:
            return {"error": f"Strategy execution failed: {str(e)}"}
    
    def _calculate_metrics(self, trades: List[Dict], equity_curve: List[float],
                          initial_capital: float) -> Dict:
        """Calculate comprehensive backtest performance metrics"""
        if not trades:
            return {
                'total_return': 0,
                'annualized_return': 0,
                'sharpe_ratio': 0,
                'sortino_ratio': 0,
                'calmar_ratio': 0,
                'omega_ratio': 0,
                'max_drawdown': 0,
                'win_rate': 0,
                'profit_factor': 0,
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'avg_win': 0,
                'avg_loss': 0,
                'expectancy': 0,
                'kelly_criterion': 0,
                'max_consecutive_wins': 0,
                'max_consecutive_losses': 0,
                'recovery_factor': 0,
                'ulcer_index': 0,
                'var_95': 0,
                'cvar_95': 0,
                't_statistic': 0,
                'p_value': 1.0,
                'composite_score': 0,
                'quality_grade': 'F'
            }

        # Basic calculations
        final_capital = equity_curve[-1]
        total_return = ((final_capital - initial_capital) / initial_capital) * 100

        # Annualized return (assume 252 trading days per year)
        days = len(equity_curve)
        years = days / 252
        annualized_return = (((final_capital / initial_capital) ** (1 / years)) - 1) * 100 if years > 0 else total_return

        # Daily returns
        returns = pd.Series(equity_curve).pct_change().dropna()

        # Sharpe ratio
        sharpe_ratio = (returns.mean() / returns.std()) * np.sqrt(252) if returns.std() > 0 else 0

        # === ADVANCED RISK METRICS ===

        # Sortino Ratio (only penalizes downside volatility)
        downside_returns = returns[returns < 0]
        downside_std = downside_returns.std() if len(downside_returns) > 0 else 0
        sortino_ratio = (returns.mean() / downside_std) * np.sqrt(252) if downside_std > 0 else 0

        # Max drawdown
        peak = np.maximum.accumulate(equity_curve)
        drawdown = (np.array(equity_curve) - peak) / peak
        max_drawdown = np.min(drawdown) * 100

        # Calmar Ratio (Return / Max Drawdown)
        calmar_ratio = annualized_return / abs(max_drawdown) if max_drawdown < 0 else 0

        # Omega Ratio (probability-weighted ratio of gains vs losses)
        threshold = 0
        gains = returns[returns > threshold].sum()
        losses = abs(returns[returns < threshold].sum())
        omega_ratio = gains / losses if losses > 0 else 0

        # Recovery Factor (Net Profit / Max Drawdown)
        net_profit = final_capital - initial_capital
        recovery_factor = net_profit / abs(max_drawdown * initial_capital / 100) if max_drawdown < 0 else 0

        # Ulcer Index (measure of downside volatility)
        drawdown_squared = drawdown ** 2
        ulcer_index = np.sqrt(np.mean(drawdown_squared)) * 100

        # Value at Risk (VaR) - 95% confidence
        var_95 = np.percentile(returns, 5) * 100

        # Conditional VaR (CVaR) - Expected loss when VaR is exceeded
        var_threshold = np.percentile(returns, 5)
        cvar_returns = returns[returns <= var_threshold]
        cvar_95 = np.mean(cvar_returns) * 100 if len(cvar_returns) > 0 else 0

        # === TRADE QUALITY METRICS ===

        winning_trades = [t for t in trades if t['return_pct'] > 0]
        losing_trades = [t for t in trades if t['return_pct'] <= 0]
        win_rate = (len(winning_trades) / len(trades)) * 100

        # Average win/loss
        avg_win = np.mean([t['return_pct'] for t in winning_trades]) if winning_trades else 0
        avg_loss = np.mean([t['return_pct'] for t in losing_trades]) if losing_trades else 0

        # Profit factor
        gross_profit = sum(t['profit'] for t in winning_trades)
        gross_loss = abs(sum(t['profit'] for t in losing_trades))
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0

        # Expectancy (average profit per trade)
        win_prob = len(winning_trades) / len(trades) if trades else 0
        loss_prob = 1 - win_prob
        expectancy = (win_prob * avg_win) + (loss_prob * avg_loss)

        # Kelly Criterion (optimal position size)
        win_loss_ratio = abs(avg_win / avg_loss) if avg_loss != 0 else 0
        kelly_criterion = (win_prob - (loss_prob / win_loss_ratio)) * 100 if win_loss_ratio > 0 else 0
        kelly_criterion = max(min(kelly_criterion, 100), 0)  # Clamp between 0-100%

        # Max consecutive wins/losses
        consecutive_wins = 0
        consecutive_losses = 0
        max_consecutive_wins = 0
        max_consecutive_losses = 0

        for trade in trades:
            if trade['return_pct'] > 0:
                consecutive_wins += 1
                consecutive_losses = 0
                max_consecutive_wins = max(max_consecutive_wins, consecutive_wins)
            else:
                consecutive_losses += 1
                consecutive_wins = 0
                max_consecutive_losses = max(max_consecutive_losses, consecutive_losses)

        # === STATISTICAL SIGNIFICANCE ===

        # T-statistic (tests if returns are significantly different from zero)
        from scipy import stats
        if len(returns) > 1:
            t_statistic, p_value = stats.ttest_1samp(returns, 0)
        else:
            t_statistic = 0
            p_value = 1.0

        # === COMPOSITE QUALITY SCORE ===

        # Component scores (0-100 scale)
        score_components = {
            'returns': min(max(annualized_return / 30 * 20, 0), 20),  # 20 points max
            'sharpe': min(max(sharpe_ratio / 2 * 15, 0), 15),  # 15 points max
            'sortino': min(max(sortino_ratio / 2 * 10, 0), 10),  # 10 points max
            'win_rate': (win_rate / 100) * 15,  # 15 points max
            'drawdown': max(20 + (max_drawdown / 5), 0),  # 20 points max (lower DD = higher score)
            'consistency': min(max(expectancy * 2, 0), 10),  # 10 points max
            'trade_count': min(len(trades) / 50 * 10, 10)  # 10 points max
        }

        composite_score = sum(score_components.values())

        # Quality grade
        if composite_score >= 90:
            quality_grade = 'A+'
        elif composite_score >= 80:
            quality_grade = 'A'
        elif composite_score >= 70:
            quality_grade = 'B'
        elif composite_score >= 60:
            quality_grade = 'C'
        elif composite_score >= 50:
            quality_grade = 'D'
        else:
            quality_grade = 'F'

        return {
            # Basic metrics
            'total_return': round(total_return, 2),
            'annualized_return': round(annualized_return, 2),

            # Risk-adjusted metrics
            'sharpe_ratio': round(sharpe_ratio, 4),
            'sortino_ratio': round(sortino_ratio, 4),
            'calmar_ratio': round(calmar_ratio, 4),
            'omega_ratio': round(omega_ratio, 4),

            # Risk metrics
            'max_drawdown': round(max_drawdown, 2),
            'recovery_factor': round(recovery_factor, 2),
            'ulcer_index': round(ulcer_index, 2),
            'var_95': round(var_95, 2),
            'cvar_95': round(cvar_95, 2),

            # Trade quality metrics
            'win_rate': round(win_rate, 2),
            'profit_factor': round(profit_factor, 4),
            'total_trades': len(trades),
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'avg_win': round(avg_win, 2),
            'avg_loss': round(avg_loss, 2),
            'expectancy': round(expectancy, 2),
            'kelly_criterion': round(kelly_criterion, 2),
            'max_consecutive_wins': max_consecutive_wins,
            'max_consecutive_losses': max_consecutive_losses,

            # Statistical significance
            't_statistic': round(float(t_statistic), 4),
            'p_value': round(float(p_value), 4),

            # Overall quality
            'composite_score': round(composite_score, 2),
            'quality_grade': quality_grade
        }
