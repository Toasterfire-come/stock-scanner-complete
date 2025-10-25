"""
Portfolio Service - Complete portfolio management with performance analytics.
Handles portfolio CRUD operations, real-time performance calculations, alert-based trade tracking,
CSV import functionality, and ROI analysis.
"""

import csv
import io
import json
import logging
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List, Optional, Tuple, Any
from django.db import transaction
from django.db.models import Q, Sum, Avg, Count, F
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError
from .models import (
    Stock, UserPortfolio, PortfolioHolding, TradeTransaction, 
    StockAlert, UserProfile
)
from .plan_limits import get_limits_for_user, is_within_limit

logger = logging.getLogger(__name__)

class PortfolioService:
    """Comprehensive portfolio management service"""
    
    @staticmethod
    def create_portfolio(user: User, name: str, description: str = "", is_public: bool = False) -> UserPortfolio:
        """
        Create a new portfolio for the user.
        
        Args:
            user: User creating the portfolio
            name: Portfolio name
            description: Portfolio description
            is_public: Whether portfolio is publicly viewable
            
        Returns:
            UserPortfolio: Created portfolio instance
        """
        try:
            # Enforce per-plan portfolio count limit
            limits = get_limits_for_user(user)
            existing_count = UserPortfolio.objects.filter(user=user).count()
            if not is_within_limit(user, "portfolios", existing_count):
                raise ValidationError("Portfolio limit reached for your plan")
            with transaction.atomic():
                portfolio = UserPortfolio.objects.create(
                    user=user,
                    name=name,
                    description=description,
                    is_public=is_public
                )
                
                logger.info(f"Created portfolio '{name}' for user {user.username}")
                return portfolio
                
        except Exception as e:
            logger.error(f"Error creating portfolio for {user.username}: {str(e)}")
            raise ValidationError(f"Failed to create portfolio: {str(e)}")
    
    @staticmethod
    def add_holding(portfolio: UserPortfolio, stock_ticker: str, shares: Decimal, 
                   average_cost: Decimal, current_price: Optional[Decimal] = None,
                   from_alert: Optional[StockAlert] = None) -> PortfolioHolding:
        """
        Add a stock holding to a portfolio.
        
        Args:
            portfolio: Portfolio to add holding to
            stock_ticker: Stock ticker symbol
            shares: Number of shares
            average_cost: Average cost per share
            current_price: Current price per share (optional, will fetch if not provided)
            from_alert: Alert that triggered this position (optional)
            
        Returns:
            PortfolioHolding: Created or updated holding
        """
        try:
            with transaction.atomic():
                # Get or create stock
                stock = Stock.objects.filter(ticker=stock_ticker.upper()).first()
                if not stock:
                    raise ValidationError(f"Stock {stock_ticker} not found")
                
                # Get current price if not provided
                if current_price is None:
                    current_price = PortfolioService.get_current_price(stock_ticker)
                
                # Get or create holding
                holding, created = PortfolioHolding.objects.get_or_create(
                    portfolio=portfolio,
                    stock=stock,
                    defaults={
                        'shares': shares,
                        'average_cost': average_cost,
                        'current_price': current_price,
                        'from_alert': from_alert,
                        'alert_action_date': timezone.now() if from_alert else None
                    }
                )
                
                if not created:
                    # Update existing holding (average down/up)
                    total_cost = (holding.shares * holding.average_cost) + (shares * average_cost)
                    total_shares = holding.shares + shares
                    holding.average_cost = total_cost / total_shares
                    holding.shares = total_shares
                    holding.current_price = current_price
                    holding.save()
                
                # Update performance metrics
                holding.update_performance()
                
                # Update portfolio performance
                PortfolioService.update_portfolio_performance(portfolio)
                
                # Create transaction record
                TradeTransaction.objects.create(
                    portfolio=portfolio,
                    stock=stock,
                    transaction_type='buy',
                    shares=shares,
                    price=average_cost,
                    total_amount=shares * average_cost,
                    transaction_date=timezone.now(),
                    from_alert=from_alert,
                    alert_category=PortfolioService._get_alert_category(from_alert)
                )
                
                logger.info(f"Added {shares} shares of {stock_ticker} to portfolio {portfolio.name}")
                return holding
                
        except Exception as e:
            logger.error(f"Error adding holding to portfolio {portfolio.name}: {str(e)}")
            raise ValidationError(f"Failed to add holding: {str(e)}")
    
    @staticmethod
    def sell_holding(portfolio: UserPortfolio, stock_ticker: str, shares: Decimal,
                    sale_price: Decimal, fees: Decimal = Decimal('0')) -> Dict[str, Any]:
        """
        Sell shares from a portfolio holding.
        
        Args:
            portfolio: Portfolio to sell from
            stock_ticker: Stock ticker symbol
            shares: Number of shares to sell
            sale_price: Sale price per share
            fees: Transaction fees
            
        Returns:
            Dict with sale details including realized gain/loss
        """
        try:
            with transaction.atomic():
                stock = Stock.objects.filter(ticker=stock_ticker.upper()).first()
                if not stock:
                    raise ValidationError(f"Stock {stock_ticker} not found")
                
                holding = PortfolioHolding.objects.filter(
                    portfolio=portfolio, stock=stock
                ).first()
                
                if not holding:
                    raise ValidationError(f"No holding found for {stock_ticker}")
                
                if holding.shares < shares:
                    raise ValidationError(f"Insufficient shares. Have {holding.shares}, trying to sell {shares}")
                
                # Calculate realized gain/loss
                cost_basis = shares * holding.average_cost
                sale_proceeds = shares * sale_price - fees
                realized_gain_loss = sale_proceeds - cost_basis
                
                # Calculate holding period
                holding_period_days = (timezone.now() - holding.date_added).days
                
                # Update holding
                if holding.shares == shares:
                    # Selling all shares - delete holding
                    holding.delete()
                else:
                    # Partial sale - update shares
                    holding.shares -= shares
                    holding.current_price = sale_price
                    holding.update_performance()
                    holding.save()
                
                # Create transaction record
                transaction = TradeTransaction.objects.create(
                    portfolio=portfolio,
                    stock=stock,
                    transaction_type='sell',
                    shares=shares,
                    price=sale_price,
                    total_amount=sale_proceeds,
                    fees=fees,
                    transaction_date=timezone.now(),
                    from_alert=holding.from_alert if holding else None,
                    alert_category=PortfolioService._get_alert_category(holding.from_alert if holding else None),
                    realized_gain_loss=realized_gain_loss,
                    holding_period_days=holding_period_days
                )
                
                # Update portfolio performance
                PortfolioService.update_portfolio_performance(portfolio)
                
                result = {
                    'transaction_id': transaction.id,
                    'shares_sold': shares,
                    'sale_price': sale_price,
                    'total_proceeds': sale_proceeds,
                    'cost_basis': cost_basis,
                    'realized_gain_loss': realized_gain_loss,
                    'realized_gain_loss_percent': (realized_gain_loss / cost_basis * 100) if cost_basis > 0 else 0,
                    'holding_period_days': holding_period_days,
                    'fees': fees
                }
                
                logger.info(f"Sold {shares} shares of {stock_ticker} from portfolio {portfolio.name}")
                return result
                
        except Exception as e:
            logger.error(f"Error selling holding from portfolio {portfolio.name}: {str(e)}")
            raise ValidationError(f"Failed to sell holding: {str(e)}")
    
    @staticmethod
    def update_portfolio_performance(portfolio: UserPortfolio) -> None:
        """
        Update portfolio performance metrics.
        
        Args:
            portfolio: Portfolio to update
        """
        try:
            holdings = portfolio.holdings.all()
            
            total_value = Decimal('0')
            total_cost = Decimal('0')
            
            for holding in holdings:
                # Update individual holding performance first
                holding.update_performance()
                
                total_value += holding.market_value
                total_cost += holding.shares * holding.average_cost
            
            portfolio.total_value = total_value
            portfolio.total_cost = total_cost
            portfolio.total_return = total_value - total_cost
            
            if total_cost > 0:
                portfolio.total_return_percent = (portfolio.total_return / total_cost * 100).quantize(
                    Decimal('0.0001'), rounding=ROUND_HALF_UP
                )
            else:
                portfolio.total_return_percent = Decimal('0')
            
            portfolio.save()
            
        except Exception as e:
            logger.error(f"Error updating portfolio performance for {portfolio.name}: {str(e)}")
    
    @staticmethod
    def get_current_price(stock_ticker: str) -> Decimal:
        """
        Get current price for a stock.
        
        Args:
            stock_ticker: Stock ticker symbol
            
        Returns:
            Decimal: Current stock price
        """
        try:
            stock = Stock.objects.filter(ticker=stock_ticker.upper()).first()
            if stock and stock.current_price:
                return stock.current_price
            
            # If no current price available, return a default or fetch from external API
            # For now, return 0 - in production, this would fetch from real-time data source
            logger.warning(f"No current price available for {stock_ticker}")
            return Decimal('0')
            
        except Exception as e:
            logger.error(f"Error getting current price for {stock_ticker}: {str(e)}")
            return Decimal('0')
    
    @staticmethod
    def get_portfolio_performance(portfolio: UserPortfolio) -> Dict[str, Any]:
        """
        Get comprehensive portfolio performance metrics.
        
        Args:
            portfolio: Portfolio to analyze
            
        Returns:
            Dict with performance metrics
        """
        try:
            # Update performance first
            PortfolioService.update_portfolio_performance(portfolio)
            
            holdings = portfolio.holdings.select_related('stock').all()
            transactions = portfolio.transactions.select_related('stock').all()
            
            # Basic metrics
            total_holdings = holdings.count()
            total_transactions = transactions.count()
            
            # Performance metrics
            best_performer = holdings.order_by('-unrealized_gain_loss_percent').first()
            worst_performer = holdings.order_by('unrealized_gain_loss_percent').first()
            
            # Sector diversification
            sector_breakdown = {}
            for holding in holdings:
                sector = getattr(holding.stock, 'sector', 'Unknown')
                if sector not in sector_breakdown:
                    sector_breakdown[sector] = {'value': Decimal('0'), 'count': 0}
                sector_breakdown[sector]['value'] += holding.market_value
                sector_breakdown[sector]['count'] += 1
            
            # Calculate sector percentages
            for sector in sector_breakdown:
                if portfolio.total_value > 0:
                    sector_breakdown[sector]['percentage'] = float(
                        (sector_breakdown[sector]['value'] / portfolio.total_value * 100).quantize(
                            Decimal('0.01'), rounding=ROUND_HALF_UP
                        )
                    )
                else:
                    sector_breakdown[sector]['percentage'] = 0
            
            # Alert-based performance
            alert_performance = PortfolioService.calculate_alert_roi(portfolio)
            
            return {
                'portfolio_id': portfolio.id,
                'portfolio_name': portfolio.name,
                'total_value': float(portfolio.total_value),
                'total_cost': float(portfolio.total_cost),
                'total_return': float(portfolio.total_return),
                'total_return_percent': float(portfolio.total_return_percent),
                'total_holdings': total_holdings,
                'total_transactions': total_transactions,
                'best_performer': {
                    'ticker': best_performer.stock.ticker if best_performer else None,
                    'return_percent': float(best_performer.unrealized_gain_loss_percent) if best_performer else 0
                },
                'worst_performer': {
                    'ticker': worst_performer.stock.ticker if worst_performer else None,
                    'return_percent': float(worst_performer.unrealized_gain_loss_percent) if worst_performer else 0
                },
                'sector_breakdown': sector_breakdown,
                'alert_performance': alert_performance,
                'last_updated': portfolio.updated_at.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting portfolio performance for {portfolio.name}: {str(e)}")
            raise ValidationError(f"Failed to get portfolio performance: {str(e)}")
    
    @staticmethod
    def calculate_alert_roi(portfolio: UserPortfolio) -> Dict[str, Any]:
        """
        Calculate ROI and performance metrics for alert-based trades.
        
        Args:
            portfolio: Portfolio to analyze
            
        Returns:
            Dict with alert performance metrics
        """
        try:
            # Get all transactions with alert tracking
            alert_transactions = portfolio.transactions.filter(
                from_alert__isnull=False
            ).select_related('stock', 'from_alert')
            
            manual_transactions = portfolio.transactions.filter(
                from_alert__isnull=True
            ).select_related('stock')
            
            # Group by alert category
            alert_categories = {}
            for transaction in alert_transactions:
                category = transaction.alert_category
                if category not in alert_categories:
                    alert_categories[category] = {
                        'total_transactions': 0,
                        'profitable_trades': 0,
                        'total_realized_gain_loss': Decimal('0'),
                        'average_holding_period': 0,
                        'success_rate': 0
                    }
                
                alert_categories[category]['total_transactions'] += 1
                
                if transaction.realized_gain_loss:
                    alert_categories[category]['total_realized_gain_loss'] += transaction.realized_gain_loss
                    if transaction.realized_gain_loss > 0:
                        alert_categories[category]['profitable_trades'] += 1
                
                if transaction.holding_period_days:
                    alert_categories[category]['average_holding_period'] += transaction.holding_period_days
            
            # Calculate averages and success rates
            for category in alert_categories:
                data = alert_categories[category]
                total = data['total_transactions']
                
                if total > 0:
                    data['success_rate'] = (data['profitable_trades'] / total) * 100
                    data['average_holding_period'] = data['average_holding_period'] / total
                    data['average_roi'] = float(data['total_realized_gain_loss'] / total)
                else:
                    data['average_roi'] = 0
            
            # Overall alert vs manual performance comparison
            alert_performance = {
                'total_alert_transactions': alert_transactions.count(),
                'total_manual_transactions': manual_transactions.count(),
                'alert_success_rate': 0,
                'manual_success_rate': 0,
                'categories': alert_categories
            }
            
            # Calculate overall success rates
            if alert_transactions.exists():
                profitable_alerts = alert_transactions.filter(realized_gain_loss__gt=0).count()
                alert_performance['alert_success_rate'] = (profitable_alerts / alert_transactions.count()) * 100
            
            if manual_transactions.exists():
                profitable_manual = manual_transactions.filter(realized_gain_loss__gt=0).count()
                alert_performance['manual_success_rate'] = (profitable_manual / manual_transactions.count()) * 100
            
            return alert_performance
            
        except Exception as e:
            logger.error(f"Error calculating alert ROI for portfolio {portfolio.name}: {str(e)}")
            return {}
    
    @staticmethod
    def track_alert_action(alert: StockAlert, action_type: str, portfolio: UserPortfolio, 
                          shares: Decimal, price: Decimal) -> None:
        """
        Track when a user acts on a stock alert.
        
        Args:
            alert: Stock alert that was acted upon
            action_type: Type of action ('buy' or 'sell')
            portfolio: Portfolio for the action
            shares: Number of shares
            price: Price per share
        """
        try:
            # This method is called by add_holding and sell_holding automatically
            # when from_alert is provided, so mainly for logging purposes
            logger.info(f"Alert action tracked: {action_type} {shares} {alert.stock.ticker} "
                       f"at ${price} for portfolio {portfolio.name}")
            
        except Exception as e:
            logger.error(f"Error tracking alert action: {str(e)}")
    
    @staticmethod
    def get_user_portfolios(user: User) -> List[Dict[str, Any]]:
        """
        Get all portfolios for a user with basic performance metrics.
        
        Args:
            user: User to get portfolios for
            
        Returns:
            List of portfolio dictionaries
        """
        try:
            portfolios = UserPortfolio.objects.filter(user=user).order_by('-created_at')
            
            result = []
            for portfolio in portfolios:
                # Update performance
                PortfolioService.update_portfolio_performance(portfolio)
                
                result.append({
                    'id': portfolio.id,
                    'name': portfolio.name,
                    'description': portfolio.description,
                    'is_public': portfolio.is_public,
                    'total_value': float(portfolio.total_value),
                    'total_cost': float(portfolio.total_cost),
                    'total_return': float(portfolio.total_return),
                    'total_return_percent': float(portfolio.total_return_percent),
                    'holdings_count': portfolio.holdings.count(),
                    'created_at': portfolio.created_at.isoformat(),
                    'updated_at': portfolio.updated_at.isoformat()
                })
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting portfolios for user {user.username}: {str(e)}")
            raise ValidationError(f"Failed to get portfolios: {str(e)}")
    
    @staticmethod
    def import_portfolio_from_csv(user: User, portfolio_name: str, csv_content: str) -> Dict[str, Any]:
        """
        Import portfolio holdings from CSV content.
        
        Expected CSV format:
        ticker,shares,average_cost,current_price
        AAPL,100,150.00,165.00
        MSFT,50,200.00,210.00
        
        Args:
            user: User importing the portfolio
            portfolio_name: Name for the new portfolio
            csv_content: CSV content as string
            
        Returns:
            Dict with import results
        """
        try:
            with transaction.atomic():
                # Create portfolio
                portfolio = PortfolioService.create_portfolio(user, portfolio_name)
                
                # Parse CSV
                csv_reader = csv.DictReader(io.StringIO(csv_content))
                
                imported_count = 0
                errors = []
                # Enforce per-plan import size limits
                limits = get_limits_for_user(user)
                max_rows = int(limits.get("import_rows_max", 1000) or 1000)
                
                for row_num, row in enumerate(csv_reader, start=2):  # Start at 2 for header row
                    if imported_count >= max_rows:
                        errors.append(f"Row {row_num}: import limit reached ({max_rows}) for your plan")
                        break
                    try:
                        ticker = row.get('ticker', '').strip().upper()
                        shares = Decimal(row.get('shares', '0'))
                        average_cost = Decimal(row.get('average_cost', '0'))
                        current_price = row.get('current_price', '').strip()
                        
                        if not ticker:
                            errors.append(f"Row {row_num}: Missing ticker")
                            continue
                        
                        if shares <= 0:
                            errors.append(f"Row {row_num}: Invalid shares amount")
                            continue
                        
                        if average_cost <= 0:
                            errors.append(f"Row {row_num}: Invalid average cost")
                            continue
                        
                        # Use provided current price or fetch current
                        price = Decimal(current_price) if current_price else None
                        
                        # Add holding
                        PortfolioService.add_holding(
                            portfolio=portfolio,
                            stock_ticker=ticker,
                            shares=shares,
                            average_cost=average_cost,
                            current_price=price
                        )
                        
                        imported_count += 1
                        
                    except Exception as e:
                        errors.append(f"Row {row_num}: {str(e)}")
                
                result = {
                    'portfolio_id': portfolio.id,
                    'portfolio_name': portfolio.name,
                    'imported_count': imported_count,
                    'error_count': len(errors),
                    'errors': errors[:10]  # Limit to first 10 errors
                }
                
                logger.info(f"Imported portfolio '{portfolio_name}' for {user.username}: "
                           f"{imported_count} holdings, {len(errors)} errors")
                
                return result
                
        except Exception as e:
            logger.error(f"Error importing portfolio from CSV for {user.username}: {str(e)}")
            raise ValidationError(f"Failed to import portfolio: {str(e)}")
    
    @staticmethod
    def _get_alert_category(alert: Optional[StockAlert]) -> str:
        """
        Get alert category for transaction tracking.
        
        Args:
            alert: Stock alert (optional)
            
        Returns:
            String alert category
        """
        if not alert:
            return 'manual'
        
        # Map alert types to categories
        alert_type_mapping = {
            'price_above': 'price',
            'price_below': 'price',
            'volume_surge': 'volume',
            'price_change': 'price'
        }
        
        return alert_type_mapping.get(alert.alert_type, 'manual')