"""
Paper Trading Service
Handles order execution, position management, and performance tracking for paper trading accounts.
"""

from decimal import Decimal
from django.utils import timezone
from django.db.models import Q, F, Sum, Avg
from datetime import datetime, timedelta
from stocks.models import (
    PaperTradingAccount,
    PaperTrade,
    PaperTradePerformance,
    Stock,
    User
)


class PaperTradingService:
    """Service for managing paper trading operations"""

    @staticmethod
    def create_account(user, name="Paper Trading Account", initial_balance=100000.00):
        """
        Create a new paper trading account for a user.

        Args:
            user: User instance
            name: Account name
            initial_balance: Starting cash balance

        Returns:
            PaperTradingAccount instance
        """
        account = PaperTradingAccount.objects.create(
            user=user,
            name=name,
            initial_balance=Decimal(str(initial_balance)),
            cash_balance=Decimal(str(initial_balance)),
            total_value=Decimal(str(initial_balance))
        )
        return account

    @staticmethod
    def get_or_create_account(user):
        """
        Get user's active paper trading account or create one if it doesn't exist.

        Args:
            user: User instance

        Returns:
            PaperTradingAccount instance
        """
        account = PaperTradingAccount.objects.filter(
            user=user,
            is_active=True
        ).first()

        if not account:
            account = PaperTradingService.create_account(user)

        return account

    @staticmethod
    def place_market_order(account, ticker, shares, side='long', notes=''):
        """
        Place a market order (instant execution at current price).

        Args:
            account: PaperTradingAccount instance
            ticker: Stock ticker symbol
            shares: Number of shares
            side: 'long' or 'short'
            notes: Optional trade notes

        Returns:
            tuple: (success: bool, message: str, trade: PaperTrade or None)
        """
        # Validate shares
        try:
            shares = Decimal(str(shares))
            if shares <= 0:
                return False, "Shares must be greater than 0", None
        except (ValueError, TypeError):
            return False, "Invalid shares value", None

        # Get stock
        try:
            stock = Stock.objects.get(ticker=ticker.upper())
        except Stock.DoesNotExist:
            return False, f"Stock {ticker} not found", None

        # Check if stock has current price
        if not stock.current_price or stock.current_price <= 0:
            return False, f"No current price available for {ticker}", None

        # Check if shorting is allowed
        if side == 'short' and not account.allow_shorting:
            return False, "Short selling not allowed for this account (Pro tier required)", None

        # Calculate required funds
        required_funds = shares * stock.current_price

        # Check if account has sufficient funds
        if required_funds > account.cash_balance:
            return False, f"Insufficient funds. Required: ${required_funds:,.2f}, Available: ${account.cash_balance:,.2f}", None

        # Create the trade
        trade = PaperTrade.objects.create(
            account=account,
            stock=stock,
            order_type='market',
            side=side,
            shares=shares,
            status='pending',
            notes=notes
        )

        # Execute the market order
        if trade.execute_market_order():
            return True, f"Market order executed: {side.upper()} {shares} shares of {ticker} @ ${trade.entry_price}", trade
        else:
            return False, "Order execution failed", trade

    @staticmethod
    def place_limit_order(account, ticker, shares, limit_price, side='long', notes=''):
        """
        Place a limit order (executes when price reaches limit).

        Args:
            account: PaperTradingAccount instance
            ticker: Stock ticker symbol
            shares: Number of shares
            limit_price: Limit price for execution
            side: 'long' or 'short'
            notes: Optional trade notes

        Returns:
            tuple: (success: bool, message: str, trade: PaperTrade or None)
        """
        # Validate inputs
        try:
            shares = Decimal(str(shares))
            limit_price = Decimal(str(limit_price))
            if shares <= 0 or limit_price <= 0:
                return False, "Shares and limit price must be greater than 0", None
        except (ValueError, TypeError):
            return False, "Invalid shares or limit_price value", None

        # Get stock
        try:
            stock = Stock.objects.get(ticker=ticker.upper())
        except Stock.DoesNotExist:
            return False, f"Stock {ticker} not found", None

        # Check if shorting is allowed
        if side == 'short' and not account.allow_shorting:
            return False, "Short selling not allowed for this account (Pro tier required)", None

        # Calculate required funds
        required_funds = shares * limit_price

        # Check if account has sufficient funds
        if required_funds > account.cash_balance:
            return False, f"Insufficient funds. Required: ${required_funds:,.2f}, Available: ${account.cash_balance:,.2f}", None

        # Create the trade
        trade = PaperTrade.objects.create(
            account=account,
            stock=stock,
            order_type='limit',
            side=side,
            shares=shares,
            limit_price=limit_price,
            status='pending',
            notes=notes
        )

        return True, f"Limit order placed: {side.upper()} {shares} shares of {ticker} @ ${limit_price}", trade

    @staticmethod
    def place_bracket_order(account, ticker, shares, take_profit_price, stop_loss_price, notes=''):
        """
        Place a bracket order with take profit and stop loss (Pro tier).

        Args:
            account: PaperTradingAccount instance
            ticker: Stock ticker symbol
            shares: Number of shares
            take_profit_price: Take profit price
            stop_loss_price: Stop loss price
            notes: Optional trade notes

        Returns:
            tuple: (success: bool, message: str, trade: PaperTrade or None)
        """
        # Validate inputs
        try:
            shares = Decimal(str(shares))
            take_profit_price = Decimal(str(take_profit_price))
            stop_loss_price = Decimal(str(stop_loss_price))
            if shares <= 0 or take_profit_price <= 0 or stop_loss_price <= 0:
                return False, "All values must be greater than 0", None
        except (ValueError, TypeError):
            return False, "Invalid input values", None

        # Get stock
        try:
            stock = Stock.objects.get(ticker=ticker.upper())
        except Stock.DoesNotExist:
            return False, f"Stock {ticker} not found", None

        # Check if stock has current price
        if not stock.current_price or stock.current_price <= 0:
            return False, f"No current price available for {ticker}", None

        # Validate bracket prices
        current_price = stock.current_price
        if take_profit_price <= current_price:
            return False, "Take profit price must be above current price", None
        if stop_loss_price >= current_price:
            return False, "Stop loss price must be below current price", None

        # Calculate required funds
        required_funds = shares * current_price

        # Check if account has sufficient funds
        if required_funds > account.cash_balance:
            return False, f"Insufficient funds. Required: ${required_funds:,.2f}, Available: ${account.cash_balance:,.2f}", None

        # Create the bracket order (executes as market order first)
        trade = PaperTrade.objects.create(
            account=account,
            stock=stock,
            order_type='bracket',
            side='long',
            shares=shares,
            take_profit_price=take_profit_price,
            stop_loss_price=stop_loss_price,
            status='pending',
            notes=notes
        )

        # Execute the market portion
        if trade.execute_market_order():
            return True, f"Bracket order executed: LONG {shares} shares of {ticker} @ ${trade.entry_price} (TP: ${take_profit_price}, SL: ${stop_loss_price})", trade
        else:
            return False, "Order execution failed", trade

    @staticmethod
    def close_position(trade_id, exit_price=None):
        """
        Close an open position.

        Args:
            trade_id: ID of the trade to close
            exit_price: Optional exit price (uses current market price if None)

        Returns:
            tuple: (success: bool, message: str, trade: PaperTrade or None)
        """
        try:
            trade = PaperTrade.objects.get(id=trade_id)
        except PaperTrade.DoesNotExist:
            return False, "Trade not found", None

        if trade.status != 'open':
            return False, f"Trade is not open (status: {trade.status})", trade

        # Close the position
        if trade.close_position(exit_price):
            profit_loss = trade.realized_pl
            pl_pct = trade.realized_pl_pct
            return True, f"Position closed: {trade.stock.ticker} - P/L: ${profit_loss:,.2f} ({pl_pct:.2f}%)", trade
        else:
            return False, "Failed to close position", trade

    @staticmethod
    def cancel_order(trade_id):
        """
        Cancel a pending order.

        Args:
            trade_id: ID of the trade to cancel

        Returns:
            tuple: (success: bool, message: str, trade: PaperTrade or None)
        """
        try:
            trade = PaperTrade.objects.get(id=trade_id)
        except PaperTrade.DoesNotExist:
            return False, "Trade not found", None

        if trade.status != 'pending':
            return False, f"Cannot cancel trade in status: {trade.status}", trade

        trade.status = 'cancelled'
        trade.save()

        return True, f"Order cancelled: {trade.stock.ticker}", trade

    @staticmethod
    def get_account_summary(account):
        """
        Get comprehensive account summary with all metrics.

        Args:
            account: PaperTradingAccount instance

        Returns:
            dict: Account summary data
        """
        # Update account balances first
        account.update_balances()
        account.refresh_from_db()

        # Get open positions
        open_positions = PaperTrade.objects.filter(
            account=account,
            status='open'
        ).select_related('stock')

        # Update current values for open positions
        for position in open_positions:
            position.update_current_value()

        # Get recent closed trades
        recent_trades = PaperTrade.objects.filter(
            account=account,
            status='closed'
        ).order_by('-closed_at')[:10]

        # Calculate today's P/L
        today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_trades = PaperTrade.objects.filter(
            account=account,
            status='closed',
            closed_at__gte=today_start
        )
        today_pl = today_trades.aggregate(total=Sum('realized_pl'))['total'] or Decimal('0.00')

        return {
            'account_value': float(account.total_value),
            'cash_balance': float(account.cash_balance),
            'equity_value': float(account.equity_value),
            'total_return': float(account.total_return),
            'total_profit_loss': float(account.total_profit_loss),
            'realized_pl': float(account.realized_pl),
            'unrealized_pl': float(account.unrealized_pl),
            'total_trades': account.total_trades,
            'winning_trades': account.winning_trades,
            'losing_trades': account.losing_trades,
            'win_rate': float(account.win_rate),
            'max_drawdown': float(account.max_drawdown),
            'sharpe_ratio': float(account.sharpe_ratio) if account.sharpe_ratio else None,
            'today_pl': float(today_pl),
            'open_positions_count': open_positions.count(),
            'open_positions': [
                {
                    'id': pos.id,
                    'ticker': pos.stock.ticker,
                    'side': pos.side,
                    'shares': float(pos.shares),
                    'entry_price': float(pos.entry_price),
                    'current_price': float(pos.current_price) if pos.current_price else None,
                    'unrealized_pl': float(pos.unrealized_pl) if pos.unrealized_pl else 0.00,
                    'unrealized_pl_pct': float(pos.unrealized_pl_pct) if pos.unrealized_pl_pct else 0.00,
                    'entry_value': float(pos.entry_value) if pos.entry_value else 0.00,
                    'current_value': float(pos.current_value) if pos.current_value else 0.00,
                }
                for pos in open_positions
            ],
            'recent_trades': [
                {
                    'id': trade.id,
                    'ticker': trade.stock.ticker,
                    'side': trade.side,
                    'shares': float(trade.shares),
                    'entry_price': float(trade.entry_price),
                    'exit_price': float(trade.exit_price) if trade.exit_price else None,
                    'realized_pl': float(trade.realized_pl) if trade.realized_pl else 0.00,
                    'realized_pl_pct': float(trade.realized_pl_pct) if trade.realized_pl_pct else 0.00,
                    'closed_at': trade.closed_at.isoformat() if trade.closed_at else None,
                }
                for trade in recent_trades
            ]
        }

    @staticmethod
    def check_bracket_orders(account):
        """
        Check and execute bracket order exits (take profit / stop loss).
        Should be called periodically (e.g., every minute).

        Args:
            account: PaperTradingAccount instance

        Returns:
            list: List of trades that were auto-closed
        """
        bracket_positions = PaperTrade.objects.filter(
            account=account,
            status='open',
            order_type='bracket'
        ).select_related('stock')

        closed_trades = []

        for trade in bracket_positions:
            current_price = trade.stock.current_price
            if not current_price:
                continue

            # Check take profit
            if trade.take_profit_price and current_price >= trade.take_profit_price:
                success, message, updated_trade = PaperTradingService.close_position(
                    trade.id,
                    exit_price=trade.take_profit_price
                )
                if success:
                    updated_trade.notes += f"\nAuto-closed: Take Profit hit @ ${trade.take_profit_price}"
                    updated_trade.save()
                    closed_trades.append(updated_trade)

            # Check stop loss
            elif trade.stop_loss_price and current_price <= trade.stop_loss_price:
                success, message, updated_trade = PaperTradingService.close_position(
                    trade.id,
                    exit_price=trade.stop_loss_price
                )
                if success:
                    updated_trade.notes += f"\nAuto-closed: Stop Loss hit @ ${trade.stop_loss_price}"
                    updated_trade.save()
                    closed_trades.append(updated_trade)

        return closed_trades

    @staticmethod
    def reset_account(account):
        """
        Reset a paper trading account to initial state.
        Closes all open positions and restores initial balance.

        Args:
            account: PaperTradingAccount instance

        Returns:
            bool: Success status
        """
        # Close all open positions at current market price
        open_positions = PaperTrade.objects.filter(account=account, status='open')
        for trade in open_positions:
            trade.close_position()

        # Reset account balances
        account.cash_balance = account.initial_balance
        account.equity_value = Decimal('0.00')
        account.total_value = account.initial_balance
        account.total_return = Decimal('0.00')
        account.total_profit_loss = Decimal('0.00')
        account.realized_pl = Decimal('0.00')
        account.unrealized_pl = Decimal('0.00')
        account.total_trades = 0
        account.winning_trades = 0
        account.losing_trades = 0
        account.win_rate = Decimal('0.00')
        account.max_drawdown = Decimal('0.00')
        account.sharpe_ratio = None
        account.last_trade_at = None
        account.save()

        return True

    @staticmethod
    def calculate_performance_metrics(account, period_type='daily', period_start=None, period_end=None):
        """
        Calculate performance metrics for a given period.

        Args:
            account: PaperTradingAccount instance
            period_type: 'daily', 'weekly', or 'monthly'
            period_start: Start date (defaults to today for daily)
            period_end: End date (defaults to today for daily)

        Returns:
            PaperTradePerformance instance or None
        """
        if not period_start:
            period_start = timezone.now().date()
        if not period_end:
            period_end = period_start

        # Get trades for this period
        trades_in_period = PaperTrade.objects.filter(
            account=account,
            status='closed',
            closed_at__date__gte=period_start,
            closed_at__date__lte=period_end
        )

        if not trades_in_period.exists():
            return None

        # Calculate metrics
        trades_closed = trades_in_period.count()
        winning_trades = trades_in_period.filter(realized_pl__gt=0).count()
        losing_trades = trades_in_period.filter(realized_pl__lt=0).count()

        total_pl = trades_in_period.aggregate(total=Sum('realized_pl'))['total'] or Decimal('0.00')
        max_gain = trades_in_period.aggregate(max=Sum('realized_pl'))['max'] or Decimal('0.00')
        max_loss = trades_in_period.aggregate(min=Sum('realized_pl'))['min'] or Decimal('0.00')

        # Calculate period return (would need account snapshots for accuracy)
        period_return = (total_pl / account.initial_balance) * 100 if account.initial_balance > 0 else Decimal('0.00')

        # Create or update performance record
        perf, created = PaperTradePerformance.objects.get_or_create(
            account=account,
            period_type=period_type,
            period_start=period_start,
            defaults={
                'period_end': period_end,
                'starting_value': account.initial_balance,
                'ending_value': account.total_value,
                'period_return': period_return,
                'period_pl': total_pl,
                'trades_closed': trades_closed,
                'winning_trades': winning_trades,
                'losing_trades': losing_trades,
                'period_win_rate': (winning_trades / trades_closed * 100) if trades_closed > 0 else Decimal('0.00'),
                'max_gain': max_gain,
                'max_loss': max_loss,
            }
        )

        if not created:
            # Update existing record
            perf.period_end = period_end
            perf.ending_value = account.total_value
            perf.period_return = period_return
            perf.period_pl = total_pl
            perf.trades_closed = trades_closed
            perf.winning_trades = winning_trades
            perf.losing_trades = losing_trades
            perf.period_win_rate = (winning_trades / trades_closed * 100) if trades_closed > 0 else Decimal('0.00')
            perf.max_gain = max_gain
            perf.max_loss = max_loss
            perf.save()

        return perf
