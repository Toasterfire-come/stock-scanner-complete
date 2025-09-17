"""
Watchlist Service - Enhanced watchlist management with import/export and performance tracking.
Handles multiple watchlist support, CSV/JSON import and export, performance tracking since addition,
target price and stop-loss management, and best/worst performer identification.
"""

import csv
import io
import json
import logging
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List, Optional, Tuple, Any
from django.db import transaction
from django.db.models import Q, Sum, Avg, Count, F, Max, Min
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.http import HttpResponse
from .models import Stock, UserWatchlist, WatchlistItem
from .portfolio_service import PortfolioService

logger = logging.getLogger(__name__)

class WatchlistService:
    """Enhanced watchlist management service"""
    
    @staticmethod
    def create_watchlist(user: User, name: str, description: str = "") -> UserWatchlist:
        """
        Create a new watchlist for the user.
        
        Args:
            user: User creating the watchlist
            name: Watchlist name
            description: Watchlist description
            
        Returns:
            UserWatchlist: Created watchlist instance
        """
        try:
            with transaction.atomic():
                watchlist = UserWatchlist.objects.create(
                    user=user,
                    name=name,
                    description=description
                )
                
                logger.info(f"Created watchlist '{name}' for user {user.username}")
                return watchlist
                
        except Exception as e:
            logger.error(f"Error creating watchlist for {user.username}: {str(e)}")
            raise ValidationError(f"Failed to create watchlist: {str(e)}")
    
    @staticmethod
    def add_stock_to_watchlist(watchlist: UserWatchlist, stock_ticker: str, 
                              added_price: Optional[Decimal] = None, notes: str = "",
                              target_price: Optional[Decimal] = None, 
                              stop_loss: Optional[Decimal] = None,
                              price_alert_enabled: bool = False,
                              news_alert_enabled: bool = False) -> WatchlistItem:
        """
        Add a stock to a watchlist.
        
        Args:
            watchlist: Watchlist to add stock to
            stock_ticker: Stock ticker symbol
            added_price: Price when added (optional, will fetch current if not provided)
            notes: User notes about this stock
            target_price: Target price for alerts
            stop_loss: Stop loss price for alerts
            price_alert_enabled: Enable price alerts
            news_alert_enabled: Enable news alerts
            
        Returns:
            WatchlistItem: Created watchlist item
        """
        try:
            with transaction.atomic():
                # Get or create stock
                stock = Stock.objects.filter(ticker=stock_ticker.upper()).first()
                if not stock:
                    raise ValidationError(f"Stock {stock_ticker} not found")
                
                # Check if already in watchlist
                existing_item = WatchlistItem.objects.filter(
                    watchlist=watchlist, stock=stock
                ).first()
                
                if existing_item:
                    raise ValidationError(f"Stock {stock_ticker} already in watchlist {watchlist.name}")
                
                # Get current price if not provided
                if added_price is None:
                    added_price = PortfolioService.get_current_price(stock_ticker)
                
                current_price = PortfolioService.get_current_price(stock_ticker)
                
                # Create watchlist item
                item = WatchlistItem.objects.create(
                    watchlist=watchlist,
                    stock=stock,
                    added_price=added_price,
                    current_price=current_price,
                    notes=notes,
                    target_price=target_price,
                    stop_loss=stop_loss,
                    price_alert_enabled=price_alert_enabled,
                    news_alert_enabled=news_alert_enabled
                )
                
                # Update performance metrics
                item.update_performance()
                
                # Update watchlist performance
                WatchlistService.update_watchlist_performance(watchlist)
                
                logger.info(f"Added {stock_ticker} to watchlist {watchlist.name}")
                return item
                
        except Exception as e:
            logger.error(f"Error adding stock to watchlist {watchlist.name}: {str(e)}")
            raise ValidationError(f"Failed to add stock to watchlist: {str(e)}")
    
    @staticmethod
    def remove_stock_from_watchlist(watchlist: UserWatchlist, stock_ticker: str) -> bool:
        """
        Remove a stock from a watchlist.
        
        Args:
            watchlist: Watchlist to remove stock from
            stock_ticker: Stock ticker symbol
            
        Returns:
            bool: True if removed successfully
        """
        try:
            with transaction.atomic():
                stock = Stock.objects.filter(ticker=stock_ticker.upper()).first()
                if not stock:
                    raise ValidationError(f"Stock {stock_ticker} not found")
                
                item = WatchlistItem.objects.filter(
                    watchlist=watchlist, stock=stock
                ).first()
                
                if not item:
                    raise ValidationError(f"Stock {stock_ticker} not in watchlist {watchlist.name}")
                
                item.delete()
                
                # Update watchlist performance
                WatchlistService.update_watchlist_performance(watchlist)
                
                logger.info(f"Removed {stock_ticker} from watchlist {watchlist.name}")
                return True
                
        except Exception as e:
            logger.error(f"Error removing stock from watchlist {watchlist.name}: {str(e)}")
            raise ValidationError(f"Failed to remove stock from watchlist: {str(e)}")
    
    @staticmethod
    def get_current_price(stock_ticker: str) -> Decimal:
        """
        Get current price for a stock (delegate to PortfolioService).
        
        Args:
            stock_ticker: Stock ticker symbol
            
        Returns:
            Decimal: Current stock price
        """
        return PortfolioService.get_current_price(stock_ticker)
    
    @staticmethod
    def update_watchlist_performance(watchlist: UserWatchlist) -> None:
        """
        Update watchlist performance metrics.
        
        Args:
            watchlist: Watchlist to update
        """
        try:
            items = watchlist.items.select_related('stock').all()
            
            if not items.exists():
                watchlist.total_return_percent = Decimal('0')
                watchlist.best_performer = ""
                watchlist.worst_performer = ""
                watchlist.save()
                return
            
            # Update individual item performance first
            for item in items:
                item.current_price = WatchlistService.get_current_price(item.stock.ticker)
                item.update_performance()
            
            # Calculate average return
            returns = [item.price_change_percent for item in items if item.price_change_percent is not None]
            if returns:
                avg_return = sum(returns) / len(returns)
                watchlist.total_return_percent = Decimal(str(avg_return)).quantize(
                    Decimal('0.0001'), rounding=ROUND_HALF_UP
                )
            else:
                watchlist.total_return_percent = Decimal('0')
            
            # Find best and worst performers
            best_item = max(items, key=lambda x: x.price_change_percent or 0)
            worst_item = min(items, key=lambda x: x.price_change_percent or 0)
            
            watchlist.best_performer = best_item.stock.ticker
            watchlist.worst_performer = worst_item.stock.ticker
            
            watchlist.save()
            
        except Exception as e:
            logger.error(f"Error updating watchlist performance for {watchlist.name}: {str(e)}")
    
    @staticmethod
    def get_watchlist_performance(watchlist: UserWatchlist) -> Dict[str, Any]:
        """
        Get comprehensive watchlist performance metrics.
        
        Args:
            watchlist: Watchlist to analyze
            
        Returns:
            Dict with performance metrics
        """
        try:
            # Update performance first
            WatchlistService.update_watchlist_performance(watchlist)
            
            items = watchlist.items.select_related('stock').all()
            
            # Basic metrics
            total_items = items.count()
            
            # Performance metrics
            gains = items.filter(price_change_percent__gt=0).count()
            losses = items.filter(price_change_percent__lt=0).count()
            
            # Top performers
            top_performers = items.order_by('-price_change_percent')[:5]
            bottom_performers = items.order_by('price_change_percent')[:5]
            
            # Alert statistics
            items_with_targets = items.filter(target_price__isnull=False).count()
            items_with_stop_loss = items.filter(stop_loss__isnull=False).count()
            price_alerts_enabled = items.filter(price_alert_enabled=True).count()
            news_alerts_enabled = items.filter(news_alert_enabled=True).count()
            
            # Target and stop loss analysis
            targets_hit = 0
            stop_losses_hit = 0
            
            for item in items:
                if item.target_price and item.current_price >= item.target_price:
                    targets_hit += 1
                if item.stop_loss and item.current_price <= item.stop_loss:
                    stop_losses_hit += 1
            
            return {
                'watchlist_id': watchlist.id,
                'watchlist_name': watchlist.name,
                'total_items': total_items,
                'total_return_percent': float(watchlist.total_return_percent),
                'gains': gains,
                'losses': losses,
                'win_rate': (gains / total_items * 100) if total_items > 0 else 0,
                'best_performer': {
                    'ticker': watchlist.best_performer,
                    'return_percent': float(
                        items.filter(stock__ticker=watchlist.best_performer).first().price_change_percent or 0
                    ) if watchlist.best_performer else 0
                },
                'worst_performer': {
                    'ticker': watchlist.worst_performer,
                    'return_percent': float(
                        items.filter(stock__ticker=watchlist.worst_performer).first().price_change_percent or 0
                    ) if watchlist.worst_performer else 0
                },
                'top_performers': [
                    {
                        'ticker': item.stock.ticker,
                        'return_percent': float(item.price_change_percent or 0),
                        'current_price': float(item.current_price),
                        'added_price': float(item.added_price)
                    }
                    for item in top_performers
                ],
                'bottom_performers': [
                    {
                        'ticker': item.stock.ticker,
                        'return_percent': float(item.price_change_percent or 0),
                        'current_price': float(item.current_price),
                        'added_price': float(item.added_price)
                    }
                    for item in bottom_performers
                ],
                'alerts': {
                    'items_with_targets': items_with_targets,
                    'items_with_stop_loss': items_with_stop_loss,
                    'price_alerts_enabled': price_alerts_enabled,
                    'news_alerts_enabled': news_alerts_enabled,
                    'targets_hit': targets_hit,
                    'stop_losses_hit': stop_losses_hit
                },
                'last_updated': watchlist.updated_at.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting watchlist performance for {watchlist.name}: {str(e)}")
            raise ValidationError(f"Failed to get watchlist performance: {str(e)}")
    
    @staticmethod
    def export_watchlist_to_csv(watchlist: UserWatchlist) -> str:
        """
        Export watchlist to CSV format.
        
        Args:
            watchlist: Watchlist to export
            
        Returns:
            str: CSV content
        """
        try:
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write header
            writer.writerow([
                'ticker', 'company_name', 'added_at', 'added_price', 'current_price',
                'price_change', 'price_change_percent', 'notes', 'target_price',
                'stop_loss', 'price_alert_enabled', 'news_alert_enabled'
            ])
            
            # Write data
            items = watchlist.items.select_related('stock').order_by('added_at')
            
            for item in items:
                writer.writerow([
                    item.stock.ticker,
                    item.stock.company_name,
                    item.added_at.strftime('%Y-%m-%d %H:%M:%S'),
                    float(item.added_price),
                    float(item.current_price),
                    float(item.price_change),
                    float(item.price_change_percent),
                    item.notes,
                    float(item.target_price) if item.target_price else '',
                    float(item.stop_loss) if item.stop_loss else '',
                    item.price_alert_enabled,
                    item.news_alert_enabled
                ])
            
            return output.getvalue()
            
        except Exception as e:
            logger.error(f"Error exporting watchlist to CSV for {watchlist.name}: {str(e)}")
            raise ValidationError(f"Failed to export watchlist to CSV: {str(e)}")
    
    @staticmethod
    def export_watchlist_to_json(watchlist: UserWatchlist) -> str:
        """
        Export watchlist to JSON format.
        
        Args:
            watchlist: Watchlist to export
            
        Returns:
            str: JSON content
        """
        try:
            items = watchlist.items.select_related('stock').order_by('added_at')
            
            data = {
                'watchlist_info': {
                    'name': watchlist.name,
                    'description': watchlist.description,
                    'created_at': watchlist.created_at.isoformat(),
                    'updated_at': watchlist.updated_at.isoformat(),
                    'total_return_percent': float(watchlist.total_return_percent),
                    'best_performer': watchlist.best_performer,
                    'worst_performer': watchlist.worst_performer
                },
                'items': []
            }
            
            for item in items:
                data['items'].append({
                    'ticker': item.stock.ticker,
                    'company_name': item.stock.company_name,
                    'added_at': item.added_at.isoformat(),
                    'added_price': float(item.added_price),
                    'current_price': float(item.current_price),
                    'price_change': float(item.price_change),
                    'price_change_percent': float(item.price_change_percent),
                    'notes': item.notes,
                    'target_price': float(item.target_price) if item.target_price else None,
                    'stop_loss': float(item.stop_loss) if item.stop_loss else None,
                    'price_alert_enabled': item.price_alert_enabled,
                    'news_alert_enabled': item.news_alert_enabled
                })
            
            return json.dumps(data, indent=2)
            
        except Exception as e:
            logger.error(f"Error exporting watchlist to JSON for {watchlist.name}: {str(e)}")
            raise ValidationError(f"Failed to export watchlist to JSON: {str(e)}")
    
    @staticmethod
    def import_watchlist_from_csv(user: User, watchlist_name: str, csv_content: str) -> Dict[str, Any]:
        """
        Import watchlist from CSV content.
        
        Expected CSV format:
        ticker,added_price,notes,target_price,stop_loss,price_alert_enabled,news_alert_enabled
        AAPL,150.00,Good growth stock,180.00,140.00,true,false
        MSFT,200.00,Solid dividend,220.00,,false,true
        
        Args:
            user: User importing the watchlist
            watchlist_name: Name for the new watchlist
            csv_content: CSV content as string
            
        Returns:
            Dict with import results
        """
        try:
            with transaction.atomic():
                # Create watchlist
                watchlist = WatchlistService.create_watchlist(user, watchlist_name)
                
                # Parse CSV
                csv_reader = csv.DictReader(io.StringIO(csv_content))
                
                imported_count = 0
                errors = []
                
                for row_num, row in enumerate(csv_reader, start=2):  # Start at 2 for header row
                    try:
                        ticker = row.get('ticker', '').strip().upper()
                        added_price = row.get('added_price', '').strip()
                        notes = row.get('notes', '').strip()
                        target_price = row.get('target_price', '').strip()
                        stop_loss = row.get('stop_loss', '').strip()
                        price_alert_enabled = row.get('price_alert_enabled', 'false').strip().lower() == 'true'
                        news_alert_enabled = row.get('news_alert_enabled', 'false').strip().lower() == 'true'
                        
                        if not ticker:
                            errors.append(f"Row {row_num}: Missing ticker")
                            continue
                        
                        # Convert prices
                        added_price_decimal = Decimal(added_price) if added_price else None
                        target_price_decimal = Decimal(target_price) if target_price else None
                        stop_loss_decimal = Decimal(stop_loss) if stop_loss else None
                        
                        # Add to watchlist
                        WatchlistService.add_stock_to_watchlist(
                            watchlist=watchlist,
                            stock_ticker=ticker,
                            added_price=added_price_decimal,
                            notes=notes,
                            target_price=target_price_decimal,
                            stop_loss=stop_loss_decimal,
                            price_alert_enabled=price_alert_enabled,
                            news_alert_enabled=news_alert_enabled
                        )
                        
                        imported_count += 1
                        
                    except Exception as e:
                        errors.append(f"Row {row_num}: {str(e)}")
                
                result = {
                    'watchlist_id': watchlist.id,
                    'watchlist_name': watchlist.name,
                    'imported_count': imported_count,
                    'error_count': len(errors),
                    'errors': errors[:10]  # Limit to first 10 errors
                }
                
                logger.info(f"Imported watchlist '{watchlist_name}' for {user.username}: "
                           f"{imported_count} items, {len(errors)} errors")
                
                return result
                
        except Exception as e:
            logger.error(f"Error importing watchlist from CSV for {user.username}: {str(e)}")
            raise ValidationError(f"Failed to import watchlist: {str(e)}")
    
    @staticmethod
    def import_watchlist_from_json(user: User, json_content: str) -> Dict[str, Any]:
        """
        Import watchlist from JSON content.
        
        Args:
            user: User importing the watchlist
            json_content: JSON content as string
            
        Returns:
            Dict with import results
        """
        try:
            with transaction.atomic():
                # Parse JSON
                data = json.loads(json_content)
                
                # Extract watchlist info
                watchlist_info = data.get('watchlist_info', {})
                watchlist_name = watchlist_info.get('name', 'Imported Watchlist')
                watchlist_description = watchlist_info.get('description', '')
                
                # Create watchlist
                watchlist = WatchlistService.create_watchlist(
                    user, watchlist_name, watchlist_description
                )
                
                imported_count = 0
                errors = []
                
                items = data.get('items', [])
                
                for item_num, item_data in enumerate(items, start=1):
                    try:
                        ticker = item_data.get('ticker', '').strip().upper()
                        added_price = item_data.get('added_price')
                        notes = item_data.get('notes', '')
                        target_price = item_data.get('target_price')
                        stop_loss = item_data.get('stop_loss')
                        price_alert_enabled = item_data.get('price_alert_enabled', False)
                        news_alert_enabled = item_data.get('news_alert_enabled', False)
                        
                        if not ticker:
                            errors.append(f"Item {item_num}: Missing ticker")
                            continue
                        
                        # Convert prices
                        added_price_decimal = Decimal(str(added_price)) if added_price else None
                        target_price_decimal = Decimal(str(target_price)) if target_price else None
                        stop_loss_decimal = Decimal(str(stop_loss)) if stop_loss else None
                        
                        # Add to watchlist
                        WatchlistService.add_stock_to_watchlist(
                            watchlist=watchlist,
                            stock_ticker=ticker,
                            added_price=added_price_decimal,
                            notes=notes,
                            target_price=target_price_decimal,
                            stop_loss=stop_loss_decimal,
                            price_alert_enabled=price_alert_enabled,
                            news_alert_enabled=news_alert_enabled
                        )
                        
                        imported_count += 1
                        
                    except Exception as e:
                        errors.append(f"Item {item_num}: {str(e)}")
                
                result = {
                    'watchlist_id': watchlist.id,
                    'watchlist_name': watchlist.name,
                    'imported_count': imported_count,
                    'error_count': len(errors),
                    'errors': errors[:10]  # Limit to first 10 errors
                }
                
                logger.info(f"Imported watchlist '{watchlist_name}' for {user.username}: "
                           f"{imported_count} items, {len(errors)} errors")
                
                return result
                
        except Exception as e:
            logger.error(f"Error importing watchlist from JSON for {user.username}: {str(e)}")
            raise ValidationError(f"Failed to import watchlist: {str(e)}")
    
    @staticmethod
    def get_user_watchlists(user: User) -> List[Dict[str, Any]]:
        """
        Get all watchlists for a user with basic performance metrics.
        
        Args:
            user: User to get watchlists for
            
        Returns:
            List of watchlist dictionaries
        """
        try:
            watchlists = UserWatchlist.objects.filter(user=user).order_by('-created_at')
            
            result = []
            for watchlist in watchlists:
                # Update performance
                WatchlistService.update_watchlist_performance(watchlist)
                
                result.append({
                    'id': watchlist.id,
                    'name': watchlist.name,
                    'description': watchlist.description,
                    'total_return_percent': float(watchlist.total_return_percent),
                    'best_performer': watchlist.best_performer,
                    'worst_performer': watchlist.worst_performer,
                    'items_count': watchlist.items.count(),
                    'created_at': watchlist.created_at.isoformat(),
                    'updated_at': watchlist.updated_at.isoformat()
                })
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting watchlists for user {user.username}: {str(e)}")
            raise ValidationError(f"Failed to get watchlists: {str(e)}")
    
    @staticmethod
    def delete_watchlist(watchlist: UserWatchlist) -> bool:
        """
        Delete a watchlist and all its items.
        
        Args:
            watchlist: Watchlist to delete
            
        Returns:
            bool: True if deleted successfully
        """
        try:
            with transaction.atomic():
                watchlist_name = watchlist.name
                user = watchlist.user
                watchlist.delete()
                
                logger.info(f"Deleted watchlist '{watchlist_name}' for user {user.username}")
                return True
                
        except Exception as e:
            logger.error(f"Error deleting watchlist {watchlist.name}: {str(e)}")
            raise ValidationError(f"Failed to delete watchlist: {str(e)}")
    
    @staticmethod
    def update_watchlist_item(item: WatchlistItem, **kwargs) -> WatchlistItem:
        """
        Update a watchlist item with new values.
        
        Args:
            item: Watchlist item to update
            **kwargs: Fields to update
            
        Returns:
            WatchlistItem: Updated item
        """
        try:
            with transaction.atomic():
                # Update allowed fields
                allowed_fields = [
                    'notes', 'target_price', 'stop_loss', 
                    'price_alert_enabled', 'news_alert_enabled'
                ]
                
                for field, value in kwargs.items():
                    if field in allowed_fields:
                        setattr(item, field, value)
                
                # Update current price and performance
                item.current_price = WatchlistService.get_current_price(item.stock.ticker)
                item.update_performance()
                item.save()
                
                # Update watchlist performance
                WatchlistService.update_watchlist_performance(item.watchlist)
                
                logger.info(f"Updated watchlist item {item.stock.ticker} in {item.watchlist.name}")
                return item
                
        except Exception as e:
            logger.error(f"Error updating watchlist item {item.stock.ticker}: {str(e)}")
            raise ValidationError(f"Failed to update watchlist item: {str(e)}")