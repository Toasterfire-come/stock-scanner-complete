"""
Value Hunter Portfolio Service
Phase 5 Implementation

Automated weekly portfolio that:
- Buys Monday at 9:35 AM ET
- Sells Friday at 3:55 PM ET
- Selects top 10 undervalued stocks by valuation score
"""
from datetime import datetime, date, timedelta
from decimal import Decimal
from typing import List, Dict, Optional
import pytz
from django.db.models import Q
from ..models import ValueHunterWeek, ValueHunterPosition, Stock, StockFundamentals


class ValueHunterService:
    """Service for managing Value Hunter portfolio"""
    
    def __init__(self):
        self.eastern = pytz.timezone('US/Eastern')
        self.entry_time = "09:35:00"  # 9:35 AM ET
        self.exit_time = "15:55:00"   # 3:55 PM ET
    
    def get_current_week(self) -> tuple:
        """Get current ISO week and year"""
        today = date.today()
        iso_calendar = today.isocalendar()
        return iso_calendar.year, iso_calendar.week
    
    def get_or_create_week(self, year: int = None, week_number: int = None) -> ValueHunterWeek:
        """Get or create a Value Hunter week"""
        if year is None or week_number is None:
            year, week_number = self.get_current_week()
        
        # Calculate week start (Monday) and end (Friday)
        week_start = self._get_monday_of_week(year, week_number)
        week_end = week_start + timedelta(days=4)  # Friday
        
        week, created = ValueHunterWeek.objects.get_or_create(
            year=year,
            week_number=week_number,
            defaults={
                'week_start': week_start,
                'week_end': week_end,
                'starting_capital': Decimal('10000.00'),
                'status': 'pending'
            }
        )
        
        return week
    
    def _get_monday_of_week(self, year: int, week_number: int) -> date:
        """Get Monday of a given ISO week"""
        # January 4th is always in week 1
        jan_4 = date(year, 1, 4)
        week_1_monday = jan_4 - timedelta(days=jan_4.weekday())
        target_monday = week_1_monday + timedelta(weeks=week_number - 1)
        return target_monday
    
    def select_top_stocks(self, limit: int = 10) -> List[Stock]:
        """
        Select top undervalued stocks based on valuation score
        
        Returns:
            List of Stock objects with highest valuation scores
        """
        # Get stocks with fundamentals and valuation scores
        stocks = Stock.objects.filter(
            fundamentals__isnull=False,
            fundamentals__valuation_score__isnull=False,
            current_price__gt=0,
            volume__gt=0
        ).select_related('fundamentals').order_by(
            '-fundamentals__valuation_score'
        )[:limit]
        
        return list(stocks)
    
    def execute_entry(self, week: ValueHunterWeek) -> Dict:
        """
        Execute portfolio entry (Monday 9:35 AM ET)
        
        Returns:
            Dictionary with execution results
        """
        try:
            # Select top 10 stocks
            top_stocks = self.select_top_stocks(limit=10)
            
            if len(top_stocks) < 10:
                return {
                    'success': False,
                    'error': f'Only found {len(top_stocks)} stocks with valuation scores'
                }
            
            # Calculate position size (equal weight)
            capital_per_position = week.starting_capital / len(top_stocks)
            
            # Create positions
            positions = []
            entry_datetime = datetime.combine(week.week_start, datetime.strptime(self.entry_time, "%H:%M:%S").time())
            entry_datetime = self.eastern.localize(entry_datetime)
            
            for rank, stock in enumerate(top_stocks, start=1):
                # Get valuation score
                valuation_score = stock.fundamentals.valuation_score if hasattr(stock, 'fundamentals') else 0
                
                # Calculate shares (use current price as entry price)
                entry_price = stock.current_price
                shares = capital_per_position / entry_price if entry_price > 0 else 0
                
                position = ValueHunterPosition.objects.create(
                    week=week,
                    symbol=stock.ticker,
                    stock=stock,
                    valuation_score=valuation_score,
                    rank=rank,
                    shares=shares,
                    entry_price=entry_price,
                    entry_datetime=entry_datetime
                )
                
                positions.append(position)
            
            # Update week status
            week.status = 'active'
            week.executed_at = entry_datetime
            week.save()
            
            return {
                'success': True,
                'positions': len(positions),
                'symbols': [p.symbol for p in positions]
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def execute_exit(self, week: ValueHunterWeek) -> Dict:
        """
        Execute portfolio exit (Friday 3:55 PM ET)
        
        Returns:
            Dictionary with execution results
        """
        try:
            positions = week.positions.all()
            
            if not positions:
                return {
                    'success': False,
                    'error': 'No positions found for this week'
                }
            
            exit_datetime = datetime.combine(week.week_end, datetime.strptime(self.exit_time, "%H:%M:%S").time())
            exit_datetime = self.eastern.localize(exit_datetime)
            
            total_capital = Decimal('0')
            
            for position in positions:
                # Get current price as exit price
                stock = Stock.objects.filter(ticker=position.symbol).first()
                if stock:
                    exit_price = stock.current_price
                else:
                    # Fallback: use entry price if stock not found
                    exit_price = position.entry_price
                
                # Calculate return
                return_percent = ((exit_price - position.entry_price) / position.entry_price) * 100
                return_amount = position.shares * (exit_price - position.entry_price)
                
                # Update position
                position.exit_price = exit_price
                position.exit_datetime = exit_datetime
                position.return_percent = return_percent
                position.return_amount = return_amount
                position.save()
                
                # Add to total capital
                total_capital += position.shares * exit_price
            
            # Calculate week performance
            weekly_return = ((total_capital - week.starting_capital) / week.starting_capital) * 100
            
            # Calculate cumulative return (simplified - should track across all weeks)
            cumulative_return = weekly_return  # For first week, weekly = cumulative
            
            # Update week
            week.ending_capital = total_capital
            week.weekly_return = weekly_return
            week.cumulative_return = cumulative_return
            week.status = 'completed'
            week.save()
            
            return {
                'success': True,
                'starting_capital': float(week.starting_capital),
                'ending_capital': float(total_capital),
                'weekly_return': float(weekly_return),
                'positions_closed': len(positions)
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_portfolio_summary(self, year: int = None, week_number: int = None) -> Dict:
        """Get summary of Value Hunter portfolio for a specific week"""
        if year is None or week_number is None:
            year, week_number = self.get_current_week()
        
        try:
            week = ValueHunterWeek.objects.get(year=year, week_number=week_number)
            positions = week.positions.all().order_by('rank')
            
            return {
                'week_number': week.week_number,
                'year': week.year,
                'week_start': str(week.week_start),
                'week_end': str(week.week_end),
                'status': week.status,
                'starting_capital': float(week.starting_capital),
                'ending_capital': float(week.ending_capital) if week.ending_capital else None,
                'weekly_return': float(week.weekly_return) if week.weekly_return else None,
                'cumulative_return': float(week.cumulative_return) if week.cumulative_return else None,
                'positions': [
                    {
                        'rank': p.rank,
                        'symbol': p.symbol,
                        'valuation_score': float(p.valuation_score),
                        'shares': float(p.shares),
                        'entry_price': float(p.entry_price),
                        'exit_price': float(p.exit_price) if p.exit_price else None,
                        'return_percent': float(p.return_percent) if p.return_percent else None,
                    }
                    for p in positions
                ]
            }
        except ValueHunterWeek.DoesNotExist:
            return {
                'error': f'No Value Hunter week found for week {week_number} of {year}'
            }
    
    def get_all_weeks_summary(self) -> List[Dict]:
        """Get summary of all Value Hunter weeks"""
        weeks = ValueHunterWeek.objects.all().order_by('-year', '-week_number')
        
        return [
            {
                'week_number': week.week_number,
                'year': week.year,
                'week_start': str(week.week_start),
                'week_end': str(week.week_end),
                'status': week.status,
                'weekly_return': float(week.weekly_return) if week.weekly_return else None,
                'cumulative_return': float(week.cumulative_return) if week.cumulative_return else None,
                'positions_count': week.positions.count()
            }
            for week in weeks
        ]
