"""
Daily Update Service - Updates all stock fundamentals and technicals once per day.
This service pulls:
- Stock fundamentals (PE, PEG, margins, growth metrics, etc.)
- Valuation scores (DCF, EPV, Graham Number, etc.)
- Technical indicators (daily timeframe)
- Market cap, 52-week ranges, and other low-frequency data

Real-time data (price, volume, intraday charts) is handled by frontend.
"""
import yfinance as yf
import logging
from decimal import Decimal
from typing import Dict, Optional, Any, List
from django.utils import timezone
from django.db import transaction
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from ..models import Stock, StockFundamentals
from .valuation_service import ValuationService, get_sector_medians

logger = logging.getLogger(__name__)


class DailyUpdateService:
    """Service for daily data updates"""
    
    def __init__(self):
        self.valuation_service = ValuationService()
        self.updated_count = 0
        self.failed_count = 0
        self.errors = []
    
    def _safe_float(self, value) -> Optional[float]:
        """Safely convert value to float."""
        if value is None:
            return None
        try:
            if isinstance(value, (int, float, Decimal)):
                return float(value)
            return float(value)
        except (ValueError, TypeError):
            return None
    
    def _safe_decimal(self, value, max_digits=15, decimal_places=4) -> Optional[Decimal]:
        """Safely convert value to Decimal."""
        try:
            if value is None:
                return None
            if isinstance(value, Decimal):
                return value
            if isinstance(value, (int, float)):
                if pd.isna(value) or np.isnan(value):
                    return None
                return Decimal(str(round(float(value), decimal_places)))
            return Decimal(str(round(float(value), decimal_places)))
        except (ValueError, TypeError, decimal.InvalidOperation):
            return None
    
    def update_stock_fundamentals(self, ticker: str, force_update: bool = False) -> Dict[str, Any]:
        """
        Update fundamental data for a single stock.
        
        Updates:
        - Stock model: market_cap, 52-week range, avg volume, PE ratio, etc.
        - StockFundamentals model: all 50+ valuation metrics
        
        Args:
            ticker: Stock ticker symbol
            force_update: Force update even if recently updated
            
        Returns:
            Dict with success status and updated data
        """
        try:
            ticker = ticker.upper().strip()
            logger.info(f"Updating fundamentals for {ticker}")
            
            # Get or create stock
            stock, created = Stock.objects.get_or_create(
                ticker=ticker,
                defaults={
                    'symbol': ticker,
                    'company_name': ticker,
                    'name': ticker
                }
            )
            
            # Fetch from yfinance
            yf_ticker = yf.Ticker(ticker)
            info = yf_ticker.info
            
            if not info or 'currentPrice' not in info:
                logger.warning(f"No data available for {ticker}")
                return {'success': False, 'error': 'No data available'}
            
            # Update Stock model with daily/low-frequency data
            stock.company_name = info.get('shortName') or info.get('longName') or ticker
            stock.name = stock.company_name
            stock.exchange = info.get('exchange', 'NASDAQ')
            stock.market_cap = info.get('marketCap')
            stock.week_52_low = self._safe_decimal(info.get('fiftyTwoWeekLow'))
            stock.week_52_high = self._safe_decimal(info.get('fiftyTwoWeekHigh'))
            stock.avg_volume_3mon = info.get('averageVolume')
            stock.shares_available = info.get('sharesOutstanding')
            stock.one_year_target = self._safe_decimal(info.get('targetMeanPrice'))
            stock.pe_ratio = self._safe_decimal(info.get('trailingPE'), decimal_places=6)
            stock.dividend_yield = self._safe_decimal(info.get('dividendYield'), decimal_places=6)
            stock.earnings_per_share = self._safe_decimal(info.get('trailingEps'))
            stock.book_value = self._safe_decimal(info.get('bookValue'))
            stock.price_to_book = self._safe_decimal(info.get('priceToBook'))
            
            # Get current price (still needed for valuation calculations)
            current_price = self._safe_float(info.get('currentPrice')) or self._safe_float(info.get('regularMarketPrice'))
            if current_price:
                stock.current_price = self._safe_decimal(current_price)
            
            stock.save()
            
            # Update or create StockFundamentals
            fundamentals, created = StockFundamentals.objects.get_or_create(
                stock=stock
            )
            
            # Price & Valuation Metrics
            fundamentals.pe_ratio = self._safe_decimal(info.get('trailingPE'))
            fundamentals.forward_pe = self._safe_decimal(info.get('forwardPE'))
            fundamentals.peg_ratio = self._safe_decimal(info.get('pegRatio'))
            fundamentals.price_to_sales = self._safe_decimal(info.get('priceToSalesTrailing12Months'))
            fundamentals.price_to_book = self._safe_decimal(info.get('priceToBook'))
            fundamentals.ev_to_revenue = self._safe_decimal(info.get('enterpriseToRevenue'))
            fundamentals.ev_to_ebitda = self._safe_decimal(info.get('enterpriseToEbitda'))
            fundamentals.enterprise_value = info.get('enterpriseValue')
            
            # Profitability Metrics
            fundamentals.gross_margin = self._safe_decimal(info.get('grossMargins'), decimal_places=4)
            fundamentals.operating_margin = self._safe_decimal(info.get('operatingMargins'), decimal_places=4)
            fundamentals.profit_margin = self._safe_decimal(info.get('profitMargins'), decimal_places=4)
            fundamentals.roe = self._safe_decimal(info.get('returnOnEquity'), decimal_places=4)
            fundamentals.roa = self._safe_decimal(info.get('returnOnAssets'), decimal_places=4)
            fundamentals.roic = self._safe_decimal(info.get('returnOnCapital'), decimal_places=4)
            
            # Growth Metrics
            fundamentals.revenue_growth_yoy = self._safe_decimal(info.get('revenueGrowth'), decimal_places=4)
            fundamentals.earnings_growth_yoy = self._safe_decimal(info.get('earningsGrowth'), decimal_places=4)
            
            # Calculate 3-year and 5-year growth from historical data
            try:
                financials = yf_ticker.financials
                if financials is not None and not financials.empty and 'Total Revenue' in financials.index:
                    revenue_data = financials.loc['Total Revenue'].sort_index()
                    if len(revenue_data) >= 3:
                        # 3-year CAGR
                        r_current = revenue_data.iloc[-1]
                        r_3y_ago = revenue_data.iloc[-3]
                        if r_3y_ago > 0:
                            cagr_3y = ((r_current / r_3y_ago) ** (1/3)) - 1
                            fundamentals.revenue_growth_3y = self._safe_decimal(cagr_3y, decimal_places=4)
                    
                    if len(revenue_data) >= 5:
                        # 5-year CAGR
                        r_current = revenue_data.iloc[-1]
                        r_5y_ago = revenue_data.iloc[-5]
                        if r_5y_ago > 0:
                            cagr_5y = ((r_current / r_5y_ago) ** (1/5)) - 1
                            fundamentals.revenue_growth_5y = self._safe_decimal(cagr_5y, decimal_places=4)
            except Exception as e:
                logger.warning(f"Could not calculate historical growth for {ticker}: {e}")
            
            # Financial Health Metrics
            fundamentals.current_ratio = self._safe_decimal(info.get('currentRatio'), decimal_places=4)
            fundamentals.quick_ratio = self._safe_decimal(info.get('quickRatio'), decimal_places=4)
            fundamentals.debt_to_equity = self._safe_decimal(info.get('debtToEquity'))
            fundamentals.interest_coverage = self._safe_decimal(info.get('interestCoverage'))
            
            # Calculate debt to assets
            total_debt = self._safe_float(info.get('totalDebt'))
            total_assets = self._safe_float(info.get('totalAssets'))
            if total_debt and total_assets and total_assets > 0:
                fundamentals.debt_to_assets = self._safe_decimal(total_debt / total_assets, decimal_places=4)
            
            # Cash Flow Metrics
            fundamentals.operating_cash_flow = info.get('operatingCashflow')
            fundamentals.free_cash_flow = info.get('freeCashflow')
            
            fcf = self._safe_float(info.get('freeCashflow'))
            shares = self._safe_float(info.get('sharesOutstanding'))
            if fcf and shares and shares > 0:
                fundamentals.fcf_per_share = self._safe_decimal(fcf / shares)
            
            market_cap = self._safe_float(info.get('marketCap'))
            if fcf and market_cap and market_cap > 0:
                fundamentals.fcf_yield = self._safe_decimal(fcf / market_cap, decimal_places=4)
            
            # Cash conversion ratio
            net_income = self._safe_float(info.get('netIncomeToCommon'))
            if fcf and net_income and net_income > 0:
                fundamentals.cash_conversion = self._safe_decimal(fcf / net_income, decimal_places=4)
            
            # Dividend Metrics
            fundamentals.dividend_yield = self._safe_decimal(info.get('dividendYield'), decimal_places=4)
            fundamentals.dividend_payout_ratio = self._safe_decimal(info.get('payoutRatio'), decimal_places=4)
            
            # Sector and Industry
            fundamentals.sector = info.get('sector', '')
            fundamentals.industry = info.get('industry', '')
            
            # Calculate Valuations using ValuationService
            eps = self._safe_float(info.get('trailingEps'))
            book_value = self._safe_float(info.get('bookValue'))
            ebit = self._safe_float(info.get('ebit'))
            total_cash = self._safe_float(info.get('totalCash')) or 0
            growth_rate = self._safe_float(info.get('earningsGrowth')) or 0.10
            
            # DCF Value
            if fcf and fcf > 0 and shares and shares > 0:
                dcf_result = self.valuation_service.calculate_dcf(
                    fcf=fcf,
                    shares=shares,
                    growth_rate=max(0.05, min(growth_rate, 0.25)),
                    discount_rate=0.10,
                    terminal_growth=0.025
                )
                if dcf_result:
                    fundamentals.dcf_value = self._safe_decimal(dcf_result.get('dcf_value'))
            
            # EPV Value
            if ebit and ebit > 0 and shares and shares > 0:
                epv_result = self.valuation_service.calculate_epv(
                    ebit=ebit,
                    tax_rate=0.25,
                    cost_of_capital=0.10,
                    shares=shares,
                    debt=total_debt or 0,
                    cash=total_cash
                )
                if epv_result:
                    fundamentals.epv_value = self._safe_decimal(epv_result.get('epv_value'))
            
            # Graham Number
            if eps and eps > 0 and book_value and book_value > 0:
                graham_result = self.valuation_service.calculate_graham_number(eps, book_value)
                if graham_result:
                    fundamentals.graham_number = self._safe_decimal(graham_result.get('graham_number'))
            
            # PEG Fair Value
            if eps and eps > 0 and growth_rate and growth_rate > 0:
                peg_result = self.valuation_service.calculate_peg_fair_value(eps, growth_rate)
                if peg_result:
                    fundamentals.peg_fair_value = self._safe_decimal(peg_result.get('peg_fair_value'))
            
            # Relative Value Score
            stock_metrics = {
                'pe_ratio': self._safe_float(fundamentals.pe_ratio),
                'price_to_book': self._safe_float(fundamentals.price_to_book),
                'ev_to_ebitda': self._safe_float(fundamentals.ev_to_ebitda),
                'price_to_sales': self._safe_float(fundamentals.price_to_sales)
            }
            sector = fundamentals.sector or 'default'
            sector_medians = get_sector_medians(sector)
            
            if any(v for v in stock_metrics.values() if v):
                relative_result = self.valuation_service.calculate_relative_value(stock_metrics, sector_medians)
                if relative_result:
                    fundamentals.relative_value_score = self._safe_decimal(relative_result.get('relative_score'), decimal_places=4)
            
            # Composite Valuation Score
            if current_price:
                composite_result = self.valuation_service.calculate_composite_score(
                    current_price=current_price,
                    dcf_value=self._safe_float(fundamentals.dcf_value),
                    epv_value=self._safe_float(fundamentals.epv_value),
                    graham_number=self._safe_float(fundamentals.graham_number),
                    peg_fair_value=self._safe_float(fundamentals.peg_fair_value),
                    relative_score=self._safe_float(fundamentals.relative_value_score)
                )
                
                fundamentals.valuation_score = self._safe_decimal(composite_result.get('composite_score'), decimal_places=2)
                fundamentals.valuation_status = composite_result.get('status', '')
                fundamentals.recommendation = composite_result.get('recommendation', '')
                fundamentals.confidence = composite_result.get('confidence', '')
            
            # Strength Score
            strength_result = self.valuation_service.calculate_strength_score({
                'roe': self._safe_float(fundamentals.roe),
                'profit_margin': self._safe_float(fundamentals.profit_margin),
                'revenue_growth_yoy': self._safe_float(fundamentals.revenue_growth_yoy),
                'earnings_growth_yoy': self._safe_float(fundamentals.earnings_growth_yoy),
                'current_ratio': self._safe_float(fundamentals.current_ratio),
                'debt_to_equity': self._safe_float(fundamentals.debt_to_equity),
                'fcf_yield': self._safe_float(fundamentals.fcf_yield),
                'cash_conversion': self._safe_float(fundamentals.cash_conversion)
            })
            
            fundamentals.strength_score = self._safe_decimal(strength_result.get('strength_score'), decimal_places=2)
            fundamentals.strength_grade = strength_result.get('grade', '')
            
            # Data quality assessment
            required_fields = ['pe_ratio', 'book_value', 'roe', 'profit_margin', 'revenue_growth_yoy']
            available_fields = sum(1 for field in required_fields if getattr(fundamentals, field, None) is not None)
            
            if available_fields >= 4:
                fundamentals.data_quality = 'complete'
            elif available_fields >= 2:
                fundamentals.data_quality = 'partial'
            else:
                fundamentals.data_quality = 'insufficient'
            
            fundamentals.last_updated = timezone.now()
            fundamentals.save()
            
            self.updated_count += 1
            logger.info(f"Successfully updated {ticker}")
            
            return {
                'success': True,
                'ticker': ticker,
                'valuation_score': float(fundamentals.valuation_score) if fundamentals.valuation_score else None,
                'recommendation': fundamentals.recommendation,
                'data_quality': fundamentals.data_quality
            }
            
        except Exception as e:
            self.failed_count += 1
            error_msg = f"Failed to update {ticker}: {str(e)}"
            logger.error(error_msg)
            self.errors.append(error_msg)
            return {'success': False, 'ticker': ticker, 'error': str(e)}
    
    def update_all_stocks(self, limit: Optional[int] = None) -> Dict[str, Any]:
        """
        Update fundamentals for all stocks in database.
        
        Args:
            limit: Maximum number of stocks to update (None = all)
            
        Returns:
            Summary dict with counts and errors
        """
        logger.info("Starting daily update for all stocks")
        start_time = timezone.now()
        
        stocks = Stock.objects.all().order_by('last_updated')
        if limit:
            stocks = stocks[:limit]
        
        total_stocks = stocks.count()
        logger.info(f"Updating {total_stocks} stocks")
        
        for stock in stocks:
            self.update_stock_fundamentals(stock.ticker)
        
        end_time = timezone.now()
        duration = (end_time - start_time).total_seconds()
        
        summary = {
            'start_time': start_time.isoformat(),
            'end_time': end_time.isoformat(),
            'duration_seconds': duration,
            'total_stocks': total_stocks,
            'updated': self.updated_count,
            'failed': self.failed_count,
            'success_rate': f"{(self.updated_count / total_stocks * 100):.2f}%" if total_stocks > 0 else '0%',
            'errors': self.errors[:10]  # First 10 errors
        }
        
        logger.info(f"Daily update completed: {self.updated_count} updated, {self.failed_count} failed")
        return summary
    
    def update_stock_list(self, tickers: List[str]) -> Dict[str, Any]:
        """
        Update fundamentals for a specific list of tickers.
        
        Args:
            tickers: List of ticker symbols
            
        Returns:
            Summary dict
        """
        logger.info(f"Updating {len(tickers)} specified stocks")
        start_time = timezone.now()
        
        for ticker in tickers:
            self.update_stock_fundamentals(ticker)
        
        end_time = timezone.now()
        duration = (end_time - start_time).total_seconds()
        
        return {
            'start_time': start_time.isoformat(),
            'end_time': end_time.isoformat(),
            'duration_seconds': duration,
            'total_stocks': len(tickers),
            'updated': self.updated_count,
            'failed': self.failed_count,
            'errors': self.errors
        }
