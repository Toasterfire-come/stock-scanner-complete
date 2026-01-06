"""
AI-Powered Backtesting Service with GROQ Integration
Phase 4 Implementation - Full AI Strategy Generation
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
import re
import signal

# Groq integration
try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False


class GroqBacktestingService:
    """
    Enhanced backtesting service with real Groq AI integration.
    Provides conversational strategy refinement and code generation.
    """
    
    def __init__(self):
        self.groq_api_key = os.environ.get('GROQ_API_KEY')
        self.client = None
        self.model = 'llama-3.3-70b-versatile'
        
        if GROQ_AVAILABLE and self.groq_api_key:
            try:
                self.client = Groq(api_key=self.groq_api_key)
            except Exception as e:
                print(f"Failed to initialize Groq client: {e}")
    
    @property
    def is_ai_available(self) -> bool:
        """Check if AI is available"""
        return self.client is not None
    
    def chat_with_ai(self, messages: List[Dict], system_prompt: str = None) -> str:
        """
        Chat with Groq AI to refine strategy.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            system_prompt: Optional system prompt
        
        Returns:
            AI response text
        """
        if not self.client:
            return "AI not available. Please provide GROQ_API_KEY."
        
        try:
            full_messages = []
            if system_prompt:
                full_messages.append({"role": "system", "content": system_prompt})
            full_messages.extend(messages)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=full_messages,
                temperature=0.7,
                max_tokens=2000
            )
            
            return response.choices[0].message.content
        except Exception as e:
            return f"AI error: {str(e)}"
    
    def understand_strategy(self, strategy_text: str, category: str) -> Dict:
        """
        Use AI to understand and parse the strategy.
        
        Returns:
            Dict with AI understanding, clarifications, and parsed components
        """
        if not self.client:
            # Fallback to rule-based parsing
            return self._fallback_parse_strategy(strategy_text, category)
        
        system_prompt = """You are a quantitative trading strategy analyst. Your job is to:
1. Understand trading strategies described in natural language
2. Extract key components: indicators, entry conditions, exit conditions, risk management
3. Ask clarifying questions if the strategy is ambiguous
4. Respond in JSON format

Category types:
- day_trading: Intraday strategies, holding period < 1 day
- swing_trading: 2-14 day holding periods
- long_term: Weeks to months holding periods"""

        prompt = f"""Analyze this {category.replace('_', ' ')} strategy and respond in JSON format:

"{strategy_text}"

Respond with this exact JSON structure:
{{
    "understood": true/false,
    "confidence": 0-100,
    "summary": "Brief summary of the strategy",
    "indicators": ["list of technical indicators used"],
    "entry_conditions": ["list of conditions to enter a trade"],
    "exit_conditions": ["list of conditions to exit a trade"],
    "stop_loss": "stop loss rule or null",
    "take_profit": "take profit rule or null",
    "position_sizing": "position sizing rule",
    "holding_period": "expected holding period",
    "clarifications_needed": ["list of questions if strategy is unclear"],
    "suggestions": ["optional improvements to the strategy"]
}}"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1500
            )
            
            response_text = response.choices[0].message.content
            
            # Extract JSON from response
            json_match = re.search(r'\{[\s\S]*\}', response_text)
            if json_match:
                return json.loads(json_match.group())
            else:
                return self._fallback_parse_strategy(strategy_text, category)
        
        except Exception as e:
            print(f"AI understanding error: {e}")
            return self._fallback_parse_strategy(strategy_text, category)
    
    def generate_strategy_code(self, strategy_text: str, category: str, 
                               ai_understanding: Dict = None) -> Tuple[str, str, Dict]:
        """
        Generate Python backtesting code from strategy description.
        
        Returns:
            Tuple of (code, error_message, ai_understanding)
        """
        # Get AI understanding if not provided
        if not ai_understanding:
            ai_understanding = self.understand_strategy(strategy_text, category)
        
        # Check if clarifications needed
        if not ai_understanding.get('understood', False) and ai_understanding.get('clarifications_needed'):
            clarifications = '\n'.join(f"- {c}" for c in ai_understanding['clarifications_needed'])
            return "", f"Strategy needs clarification:\n{clarifications}", ai_understanding
        
        if not self.client:
            # Fallback to template-based code generation
            code = self._generate_code_from_parsed_strategy(ai_understanding, category)
            return code, "", ai_understanding
        
        # Use AI to generate code
        system_prompt = """You are an expert Python developer specializing in quantitative finance.
Generate clean, efficient Python code for backtesting trading strategies.

The code must define these functions:
1. calculate_indicators(data) - Calculate all required technical indicators
2. entry_condition(data, index) - Return True when entry conditions are met
3. exit_condition(data, index, entry_price, entry_index) - Return True when exit conditions are met

The data parameter is a pandas DataFrame with columns: Date, Open, High, Low, Close, Volume
Use proper error handling and edge cases."""

        prompt = f"""Generate Python backtesting code for this {category.replace('_', ' ')} strategy:

Strategy: "{strategy_text}"

AI Understanding:
{json.dumps(ai_understanding, indent=2)}

Generate complete Python code with:
1. calculate_indicators() function
2. entry_condition() function  
3. exit_condition() function with stop loss and take profit

Only output the Python code, no explanations."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=3000
            )
            
            code = response.choices[0].message.content
            
            # Extract code block if wrapped in markdown
            code_match = re.search(r'```python\n([\s\S]*?)\n```', code)
            if code_match:
                code = code_match.group(1)
            elif code.startswith('```'):
                code = re.sub(r'^```\w*\n|\n```$', '', code)
            
            # Validate code syntax
            try:
                compile(code, '<string>', 'exec')
            except SyntaxError as e:
                return "", f"Generated code has syntax error: {e}", ai_understanding
            
            return code, "", ai_understanding
        
        except Exception as e:
            print(f"AI code generation error: {e}")
            # Fallback to template-based code
            code = self._generate_code_from_parsed_strategy(ai_understanding, category)
            return code, "", ai_understanding
    
    def refine_strategy_conversation(self, conversation_history: List[Dict], 
                                     user_message: str) -> Dict:
        """
        Have a conversation to refine the strategy.
        
        Args:
            conversation_history: Previous messages
            user_message: New user message
        
        Returns:
            Dict with AI response and updated understanding
        """
        if not self.client:
            return {
                "response": "AI not available. Please provide strategy details directly.",
                "understanding_complete": False,
                "understanding": None
            }
        
        system_prompt = """You are a helpful trading strategy consultant. Your goal is to:
1. Help users define clear, testable trading strategies
2. Ask clarifying questions about entry/exit conditions, indicators, and risk management
3. Ensure the strategy is specific enough to be coded and backtested
4. Be conversational and helpful

Once you have enough information, summarize the complete strategy.
Always end your response with either:
- More questions if unclear
- "STRATEGY_COMPLETE" followed by a JSON summary if you have enough info"""

        messages = conversation_history + [{"role": "user", "content": user_message}]
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "system", "content": system_prompt}] + messages,
                temperature=0.7,
                max_tokens=1500
            )
            
            ai_response = response.choices[0].message.content
            
            # Check if strategy is complete
            is_complete = "STRATEGY_COMPLETE" in ai_response
            understanding = None
            
            if is_complete:
                # Extract JSON summary
                json_match = re.search(r'\{[\s\S]*\}', ai_response.split("STRATEGY_COMPLETE")[1])
                if json_match:
                    try:
                        understanding = json.loads(json_match.group())
                    except:
                        pass
                # Clean response
                ai_response = ai_response.split("STRATEGY_COMPLETE")[0].strip()
            
            return {
                "response": ai_response,
                "understanding_complete": is_complete,
                "understanding": understanding
            }
        
        except Exception as e:
            return {
                "response": f"Error communicating with AI: {str(e)}",
                "understanding_complete": False,
                "understanding": None
            }
    
    def run_backtest(self, backtest_run) -> Dict:
        """
        Execute the backtest and return results.
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
    
    def _fallback_parse_strategy(self, strategy_text: str, category: str) -> Dict:
        """Fallback rule-based strategy parsing"""
        strategy_lower = strategy_text.lower()
        
        parsed = {
            'understood': True,
            'confidence': 70,
            'summary': f"Rule-based parsing of {category} strategy",
            'indicators': [],
            'entry_conditions': [],
            'exit_conditions': [],
            'stop_loss': None,
            'take_profit': None,
            'position_sizing': '100% per trade',
            'holding_period': category.replace('_', ' '),
            'clarifications_needed': [],
            'suggestions': []
        }
        
        # Detect indicators
        indicator_patterns = {
            'rsi': 'RSI',
            'macd': 'MACD',
            'moving average': 'Moving Average',
            'sma': 'SMA',
            'ema': 'EMA',
            'bollinger': 'Bollinger Bands',
            'volume': 'Volume',
            'vwap': 'VWAP',
            'stochastic': 'Stochastic'
        }
        
        for pattern, name in indicator_patterns.items():
            if pattern in strategy_lower:
                parsed['indicators'].append(name)
        
        # Entry/Exit conditions
        if 'rsi' in strategy_lower:
            rsi_match = re.search(r'rsi.*?(\d+)', strategy_lower)
            if rsi_match:
                threshold = int(rsi_match.group(1))
                if threshold < 40:
                    parsed['entry_conditions'].append(f'RSI below {threshold}')
                elif threshold > 60:
                    parsed['exit_conditions'].append(f'RSI above {threshold}')
        
        if 'cross' in strategy_lower and 'ma' in strategy_lower:
            parsed['entry_conditions'].append('Moving average crossover')
        
        # Stop loss / take profit
        stop_match = re.search(r'stop.*?loss.*?(\d+)%', strategy_lower)
        if stop_match:
            parsed['stop_loss'] = f"{stop_match.group(1)}%"
        else:
            parsed['stop_loss'] = '5%'
        
        profit_match = re.search(r'(take.*?profit|target).*?(\d+)%', strategy_lower)
        if profit_match:
            parsed['take_profit'] = f"{profit_match.group(2)}%"
        else:
            parsed['take_profit'] = '10%'
        
        if not parsed['entry_conditions']:
            parsed['entry_conditions'].append('RSI below 30 (oversold)')
        if not parsed['exit_conditions']:
            parsed['exit_conditions'].append('RSI above 70 (overbought)')
        if not parsed['indicators']:
            parsed['indicators'].append('RSI')
        
        return parsed
    
    def _generate_code_from_parsed_strategy(self, parsed: Dict, category: str) -> str:
        """Generate Python code from parsed strategy"""
        indicators = parsed.get('indicators', ['RSI'])
        stop_loss = 5
        take_profit = 10
        
        if parsed.get('stop_loss'):
            match = re.search(r'(\d+)', str(parsed['stop_loss']))
            if match:
                stop_loss = int(match.group(1))
        
        if parsed.get('take_profit'):
            match = re.search(r'(\d+)', str(parsed['take_profit']))
            if match:
                take_profit = int(match.group(1))
        
        code = '''
import pandas as pd
import numpy as np

def calculate_indicators(data):
    df = data.copy()
    
    # RSI
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    # Moving Averages
    df['SMA_20'] = df['Close'].rolling(window=20).mean()
    df['SMA_50'] = df['Close'].rolling(window=50).mean()
    df['EMA_12'] = df['Close'].ewm(span=12, adjust=False).mean()
    df['EMA_26'] = df['Close'].ewm(span=26, adjust=False).mean()
    
    # MACD
    df['MACD'] = df['EMA_12'] - df['EMA_26']
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

def entry_condition(data, index):
    if index < 50:
        return False
    try:
'''
        
        # Add entry logic
        entry_conditions = []
        if 'RSI' in indicators:
            entry_conditions.append("data.iloc[index]['RSI'] < 30")
        if 'MACD' in indicators:
            entry_conditions.append("data.iloc[index]['MACD'] > data.iloc[index]['MACD_Signal']")
        if 'Moving Average' in indicators or 'SMA' in indicators or 'EMA' in indicators:
            entry_conditions.append("data.iloc[index]['SMA_20'] > data.iloc[index]['SMA_50']")
        if 'Bollinger Bands' in indicators:
            entry_conditions.append("data.iloc[index]['Close'] <= data.iloc[index]['BB_Lower']")
        if 'Volume' in indicators:
            entry_conditions.append("data.iloc[index]['Volume'] > data.iloc[index]['Volume_MA'] * 1.5")
        
        if not entry_conditions:
            entry_conditions = ["data.iloc[index]['RSI'] < 30"]
        
        entry_logic = " and \n            ".join(entry_conditions)
        
        code += f'''        return ({entry_logic})
    except:
        return False

def exit_condition(data, index, entry_price, entry_index):
    try:
        current_price = data.iloc[index]['Close']
        price_change_pct = ((current_price - entry_price) / entry_price) * 100
        
        # Stop loss at {stop_loss}%
        if price_change_pct <= -{stop_loss}:
            return True
        
        # Take profit at {take_profit}%
        if price_change_pct >= {take_profit}:
            return True
        
        # Technical exit
'''
        
        # Add exit logic
        exit_conditions = []
        if 'RSI' in indicators:
            exit_conditions.append("data.iloc[index]['RSI'] > 70")
        if 'MACD' in indicators:
            exit_conditions.append("data.iloc[index]['MACD'] < data.iloc[index]['MACD_Signal']")
        if 'Moving Average' in indicators or 'SMA' in indicators:
            exit_conditions.append("data.iloc[index]['SMA_20'] < data.iloc[index]['SMA_50']")
        if 'Bollinger Bands' in indicators:
            exit_conditions.append("data.iloc[index]['Close'] >= data.iloc[index]['BB_Upper']")
        
        if not exit_conditions:
            exit_conditions = ["data.iloc[index]['RSI'] > 70"]
        
        exit_logic = " or \n            ".join(exit_conditions)
        
        code += f'''        return ({exit_logic})
    except:
        return False
'''
        
        return code
    
    def _fetch_historical_data(self, symbols: List[str], start_date, end_date) -> pd.DataFrame:
        """Fetch historical price data with robust error handling"""
        try:
            symbol = symbols[0] if isinstance(symbols, list) else symbols
            print(f"Fetching historical data for {symbol} from {start_date} to {end_date}")

            ticker = yf.Ticker(symbol)
            df = ticker.history(start=start_date, end=end_date, auto_adjust=True, actions=False)

            if df.empty:
                print(f"No data returned for {symbol}")
                return pd.DataFrame()

            # Reset index to make Date a column
            df = df.reset_index()

            # Ensure we have all required columns
            required_cols = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']

            # yfinance may return different column names, standardize them
            if 'Datetime' in df.columns:
                df.rename(columns={'Datetime': 'Date'}, inplace=True)

            # Check for missing columns
            missing_cols = [col for col in required_cols if col not in df.columns]
            if missing_cols:
                print(f"Missing columns: {missing_cols}")
                return pd.DataFrame()

            # Select only required columns
            df = df[required_cols].copy()

            # Convert Date to datetime if it isn't already
            df['Date'] = pd.to_datetime(df['Date'])

            # Remove any rows with NaN values in critical columns
            df = df.dropna(subset=['Open', 'High', 'Low', 'Close', 'Volume'])

            # Ensure proper data types
            for col in ['Open', 'High', 'Low', 'Close']:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            df['Volume'] = pd.to_numeric(df['Volume'], errors='coerce').fillna(0).astype(int)

            print(f"Successfully fetched {len(df)} rows of data for {symbol}")
            return df

        except Exception as e:
            print(f"Error fetching data for {symbol}: {str(e)}")
            import traceback
            traceback.print_exc()
            return pd.DataFrame()
    
    def _execute_strategy(self, code: str, data: pd.DataFrame, initial_capital: float) -> Dict:
        """Execute the trading strategy"""
        try:
            # NOTE: This executes dynamically-generated code. Treat as high-risk.
            # We restrict builtins and perform a basic denylist check, but this is
            # not a complete sandbox. For production, run this in an isolated worker.
            # Strip import statements (we do not expose __import__; pd/np are injected).
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

            def _with_timeout(seconds: float, fn):
                def _handler(signum, frame):  # noqa: ARG001
                    raise TimeoutError("Timed out")

                prev = signal.signal(signal.SIGALRM, _handler)
                signal.setitimer(signal.ITIMER_REAL, seconds)
                try:
                    return fn()
                finally:
                    signal.setitimer(signal.ITIMER_REAL, 0)
                    signal.signal(signal.SIGALRM, prev)

            namespace = {"__builtins__": safe_builtins, "pd": pd, "np": np, "data": data}
            _with_timeout(0.5, lambda: exec(code, namespace))
            
            entry_condition = namespace.get('entry_condition')
            exit_condition = namespace.get('exit_condition')
            
            if not entry_condition or not exit_condition:
                return {"error": "Generated code missing entry/exit functions"}
            
            trades = []
            equity_curve = [initial_capital]
            cash = initial_capital
            position = None
            
            for i in range(len(data)):
                if position is None:
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
                    except:
                        pass
                else:
                    try:
                        current_price = data.iloc[i]['Close']
                        ok = _with_timeout(
                            0.05,
                            lambda: bool(exit_condition(data, i, position['entry_price'], position['entry_index'])),
                        )
                        if ok:
                            cash = position['shares'] * current_price
                            trade_return = ((current_price - position['entry_price']) / position['entry_price']) * 100
                            trade_profit = (current_price - position['entry_price']) * position['shares']
                            
                            trades.append({
                                'entry_date': str(position['entry_date']),
                                'exit_date': str(data.iloc[i]['Date']),
                                'entry_price': float(position['entry_price']),
                                'exit_price': float(current_price),
                                'shares': float(position['shares']),
                                'return_pct': float(trade_return),
                                # Profit should be per-trade P&L, not cumulative vs initial capital.
                                'profit': float(trade_profit)
                            })
                            position = None
                    except:
                        pass
                
                if position:
                    equity_curve.append(position['shares'] * data.iloc[i]['Close'])
                else:
                    equity_curve.append(cash)
            
            # Close open position
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
            
            metrics = self._calculate_metrics(trades, equity_curve, initial_capital)
            metrics['trades_data'] = trades
            metrics['equity_curve'] = [float(x) for x in equity_curve]
            
            return metrics
        
        except Exception as e:
            return {"error": f"Strategy execution failed: {str(e)}"}
    
    def _calculate_metrics(self, trades: List[Dict], equity_curve: List[float], 
                          initial_capital: float) -> Dict:
        """Calculate comprehensive backtest performance metrics (same shape as static service)."""
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

        final_capital = equity_curve[-1]
        total_return = ((final_capital - initial_capital) / initial_capital) * 100

        days = len(equity_curve)
        years = days / 252
        annualized_return = (((final_capital / initial_capital) ** (1 / years)) - 1) * 100 if years > 0 else total_return

        returns = pd.Series(equity_curve).pct_change().dropna()

        sharpe_ratio = (returns.mean() / returns.std()) * np.sqrt(252) if returns.std() > 0 else 0

        # Sortino Ratio
        downside_returns = returns[returns < 0]
        downside_std = downside_returns.std() if len(downside_returns) > 0 else 0
        sortino_ratio = (returns.mean() / downside_std) * np.sqrt(252) if downside_std > 0 else 0

        # Max drawdown
        peak = np.maximum.accumulate(equity_curve)
        drawdown = (np.array(equity_curve) - peak) / peak
        max_drawdown = np.min(drawdown) * 100

        # Calmar Ratio
        calmar_ratio = annualized_return / abs(max_drawdown) if max_drawdown < 0 else 0

        # Omega Ratio
        threshold = 0
        gains = returns[returns > threshold].sum()
        losses = abs(returns[returns < threshold].sum())
        omega_ratio = gains / losses if losses > 0 else 0

        # Recovery Factor
        net_profit = final_capital - initial_capital
        recovery_factor = net_profit / abs(max_drawdown * initial_capital / 100) if max_drawdown < 0 else 0

        # Ulcer Index
        drawdown_squared = drawdown ** 2
        ulcer_index = np.sqrt(np.mean(drawdown_squared)) * 100

        # VaR / CVaR
        var_95 = np.percentile(returns, 5) * 100
        var_threshold = np.percentile(returns, 5)
        cvar_returns = returns[returns <= var_threshold]
        cvar_95 = np.mean(cvar_returns) * 100 if len(cvar_returns) > 0 else 0

        winning_trades = [t for t in trades if t['return_pct'] > 0]
        losing_trades = [t for t in trades if t['return_pct'] <= 0]
        win_rate = (len(winning_trades) / len(trades)) * 100

        avg_win = np.mean([t['return_pct'] for t in winning_trades]) if winning_trades else 0
        avg_loss = np.mean([t['return_pct'] for t in losing_trades]) if losing_trades else 0

        gross_profit = sum(t['profit'] for t in winning_trades)
        gross_loss = abs(sum(t['profit'] for t in losing_trades))
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0

        win_prob = len(winning_trades) / len(trades) if trades else 0
        loss_prob = 1 - win_prob
        expectancy = (win_prob * avg_win) + (loss_prob * avg_loss)

        win_loss_ratio = abs(avg_win / avg_loss) if avg_loss != 0 else 0
        kelly_criterion = (win_prob - (loss_prob / win_loss_ratio)) * 100 if win_loss_ratio > 0 else 0
        kelly_criterion = max(min(kelly_criterion, 100), 0)

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

        # Statistical significance
        from scipy import stats
        if len(returns) > 1:
            t_statistic, p_value = stats.ttest_1samp(returns, 0)
        else:
            t_statistic = 0
            p_value = 1.0

        score_components = {
            'returns': min(max(annualized_return / 30 * 20, 0), 20),
            'sharpe': min(max(sharpe_ratio / 2 * 15, 0), 15),
            'sortino': min(max(sortino_ratio / 2 * 10, 0), 10),
            'win_rate': (win_rate / 100) * 15,
            'drawdown': max(20 + (max_drawdown / 5), 0),
            'consistency': min(max(expectancy * 2, 0), 10),
            'trade_count': min(len(trades) / 50 * 10, 10),
        }
        composite_score = sum(score_components.values())

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
            'total_return': round(total_return, 2),
            'annualized_return': round(annualized_return, 2),
            'sharpe_ratio': round(sharpe_ratio, 4),
            'sortino_ratio': round(sortino_ratio, 4),
            'calmar_ratio': round(calmar_ratio, 4),
            'omega_ratio': round(omega_ratio, 4),
            'max_drawdown': round(max_drawdown, 2),
            'recovery_factor': round(recovery_factor, 2),
            'ulcer_index': round(ulcer_index, 2),
            'var_95': round(var_95, 2),
            'cvar_95': round(cvar_95, 2),
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
            't_statistic': round(float(t_statistic), 4),
            'p_value': round(float(p_value), 4),
            'composite_score': round(composite_score, 2),
            'quality_grade': quality_grade,
        }
