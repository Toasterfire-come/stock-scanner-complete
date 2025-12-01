"""
AI-Powered Backtesting Service
Phase 4 Implementation - Enhanced with Emergent LLM Integration
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
from .ai_chat_service import SyncAIStrategyService


class BacktestingService:
    """Service for AI-powered strategy backtesting"""
    
    def __init__(self):
        try:
            self.ai_service = SyncAIStrategyService()
        except ValueError as e:
            print(f"Warning: AI service not available: {e}")
            self.ai_service = None
    
    def generate_strategy_code(self, strategy_text: str, category: str) -> Tuple[str, str]:
        """
        Use AI to convert natural language strategy to Python code
        
        Returns:
            Tuple of (generated_code, error_message)
        """
        if not self.ai_service:
            return "", "AI service not available. Please check EMERGENT_LLM_KEY configuration."
        
        return self.ai_service.generate_strategy_code(strategy_text, category)
    
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
                code, error = self.generate_strategy_code(
                    backtest_run.strategy_text,
                    backtest_run.category
                )
                if error:
                    return {"error": error}
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
            symbol = symbols[0] if isinstance(symbols, list) else symbols
            
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
            # Create execution namespace
            namespace = {
                'pd': pd,
                'np': np,
                'data': data,
            }
            
            # Execute the generated code to define functions
            exec(code, namespace)
            
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
                        if entry_condition(data, i):
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
                        if exit_condition(data, i, position['entry_price'], position['entry_index']):
                            exit_price = current_price
                            cash = position['shares'] * exit_price
                            
                            trade_return = ((exit_price - position['entry_price']) / position['entry_price']) * 100
                            
                            trades.append({
                                'entry_date': str(position['entry_date']),
                                'exit_date': str(data.iloc[i]['Date']),
                                'entry_price': float(position['entry_price']),
                                'exit_price': float(exit_price),
                                'shares': float(position['shares']),
                                'return_pct': float(trade_return),
                                'profit': float(cash - initial_capital)
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
                trades.append({
                    'entry_date': str(position['entry_date']),
                    'exit_date': str(data.iloc[-1]['Date']),
                    'entry_price': float(position['entry_price']),
                    'exit_price': float(final_price),
                    'shares': float(position['shares']),
                    'return_pct': float(trade_return),
                    'profit': float(cash - initial_capital)
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
        """Calculate backtest performance metrics"""
        if not trades:
            return {
                'total_return': 0,
                'annualized_return': 0,
                'sharpe_ratio': 0,
                'max_drawdown': 0,
                'win_rate': 0,
                'profit_factor': 0,
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'composite_score': 0
            }
        
        # Total return
        final_capital = equity_curve[-1]
        total_return = ((final_capital - initial_capital) / initial_capital) * 100
        
        # Annualized return (assume 252 trading days per year)
        days = len(equity_curve)
        years = days / 252
        annualized_return = (((final_capital / initial_capital) ** (1 / max(years, 0.01))) - 1) * 100 if years > 0 else total_return
        
        # Sharpe ratio
        returns = pd.Series(equity_curve).pct_change().dropna()
        sharpe_ratio = (returns.mean() / returns.std()) * np.sqrt(252) if len(returns) > 0 and returns.std() > 0 else 0
        
        # Max drawdown
        equity_arr = np.array(equity_curve)
        peak = np.maximum.accumulate(equity_arr)
        drawdown = (equity_arr - peak) / peak
        max_drawdown = np.min(drawdown) * 100
        
        # Win rate
        winning_trades = [t for t in trades if t['return_pct'] > 0]
        losing_trades = [t for t in trades if t['return_pct'] <= 0]
        win_rate = (len(winning_trades) / len(trades)) * 100
        
        # Profit factor
        gross_profit = sum(t['profit'] for t in winning_trades) if winning_trades else 0
        gross_loss = abs(sum(t['profit'] for t in losing_trades)) if losing_trades else 0
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else (999 if gross_profit > 0 else 0)
        
        # Composite score (weighted average)
        score = (
            min(max(total_return, 0), 100) * 0.30 +  # 30% weight on returns
            min(max(sharpe_ratio * 20, 0), 100) * 0.25 +  # 25% weight on sharpe
            min(win_rate, 100) * 0.20 +  # 20% weight on win rate
            min(max(100 + max_drawdown, 0), 100) * 0.15 +  # 15% weight on drawdown
            min(max(profit_factor * 10, 0), 100) * 0.10  # 10% weight on profit factor
        )
        
        return {
            'total_return': round(total_return, 2),
            'annualized_return': round(annualized_return, 2),
            'sharpe_ratio': round(float(sharpe_ratio), 4),
            'max_drawdown': round(max_drawdown, 2),
            'win_rate': round(win_rate, 2),
            'profit_factor': round(profit_factor, 4),
            'total_trades': len(trades),
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'composite_score': round(score, 2)
        }
