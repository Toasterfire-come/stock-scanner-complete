"""
Valuation Service for calculating stock fair values using multiple models.
Implements DCF, EPV, Graham Number, PEG Fair Value, and Relative Valuation.
"""
from decimal import Decimal
from typing import Dict, Optional, Any
import math


class ValuationService:
    """Service for calculating comprehensive stock valuations"""
    
    @staticmethod
    def calculate_dcf(
        fcf: float,
        shares: int,
        growth_rate: float = 0.10,
        discount_rate: float = 0.10,
        terminal_growth: float = 0.025,
        years: int = 10
    ) -> Optional[Dict[str, Any]]:
        """
        Multi-stage Discounted Cash Flow model.
        
        Args:
            fcf: Current free cash flow
            shares: Shares outstanding
            growth_rate: Expected growth rate (will be capped at 25%)
            discount_rate: WACC or required return
            terminal_growth: Perpetual growth rate
            years: Projection period
            
        Returns:
            Dictionary with dcf_value, terminal_value, growth_value
        """
        if fcf <= 0 or shares <= 0:
            return None
        
        # Cap growth rate at 25%
        growth_rate = min(growth_rate, 0.25)
        
        projected_fcf = []
        current_fcf = fcf
        
        # Years 1-5: High growth phase
        for year in range(1, 6):
            current_fcf *= (1 + growth_rate)
            pv = current_fcf / ((1 + discount_rate) ** year)
            projected_fcf.append(pv)
        
        # Years 6-10: Declining growth to terminal rate
        for year in range(6, years + 1):
            # Linear decline from growth_rate to terminal_growth
            growth = growth_rate - (growth_rate - terminal_growth) * (year - 5) / 5
            current_fcf *= (1 + growth)
            pv = current_fcf / ((1 + discount_rate) ** year)
            projected_fcf.append(pv)
        
        # Terminal value using Gordon Growth Model
        terminal_fcf = current_fcf * (1 + terminal_growth)
        terminal_value = terminal_fcf / (discount_rate - terminal_growth)
        pv_terminal = terminal_value / ((1 + discount_rate) ** years)
        
        intrinsic_value = sum(projected_fcf) + pv_terminal
        per_share_value = intrinsic_value / shares
        
        return {
            'dcf_value': round(per_share_value, 2),
            'terminal_value': round(pv_terminal / shares, 2),
            'growth_value': round(sum(projected_fcf) / shares, 2),
            'assumptions': {
                'growth_rate': growth_rate,
                'discount_rate': discount_rate,
                'terminal_growth': terminal_growth,
                'years': years
            }
        }
    
    @staticmethod
    def calculate_epv(
        ebit: float,
        tax_rate: float = 0.25,
        cost_of_capital: float = 0.10,
        shares: int = 1,
        debt: float = 0,
        cash: float = 0
    ) -> Optional[Dict[str, Any]]:
        """
        Earnings Power Value - assumes no growth, values current earnings capacity.
        
        Args:
            ebit: Earnings before interest and taxes
            tax_rate: Corporate tax rate
            cost_of_capital: WACC
            shares: Shares outstanding
            debt: Total debt
            cash: Cash and equivalents
            
        Returns:
            Dictionary with epv_value per share
        """
        if ebit <= 0 or shares <= 0:
            return None
        
        # Normalize earnings
        nopat = ebit * (1 - tax_rate)
        
        # Enterprise value
        enterprise_value = nopat / cost_of_capital
        
        # Equity value
        equity_value = enterprise_value - debt + cash
        
        if equity_value <= 0:
            return None
        
        epv_per_share = equity_value / shares
        
        return {
            'epv_value': round(epv_per_share, 2),
            'enterprise_value': round(enterprise_value, 2),
            'equity_value': round(equity_value, 2)
        }
    
    @staticmethod
    def calculate_graham_number(
        eps: float,
        book_value: float
    ) -> Optional[Dict[str, Any]]:
        """
        Graham Number = sqrt(22.5 * EPS * Book Value)
        
        Based on Benjamin Graham's criteria:
        - P/E < 15
        - P/B < 1.5
        - Combined: P/E * P/B < 22.5
        
        Args:
            eps: Earnings per share (trailing 12 months)
            book_value: Book value per share
            
        Returns:
            Dictionary with graham_number
        """
        if eps <= 0 or book_value <= 0:
            return None
        
        graham_number = math.sqrt(22.5 * eps * book_value)
        
        # Also calculate individual components
        implied_pe = 15
        implied_pb = 1.5
        
        return {
            'graham_number': round(graham_number, 2),
            'implied_pe': implied_pe,
            'implied_pb': implied_pb,
            'eps_used': eps,
            'book_value_used': book_value
        }
    
    @staticmethod
    def calculate_peg_fair_value(
        eps: float,
        growth_rate: float
    ) -> Optional[Dict[str, Any]]:
        """
        PEG-based fair value assuming PEG ratio of 1.
        
        Fair P/E = Growth Rate (as percentage)
        Fair Value = EPS * Fair P/E
        
        Args:
            eps: Earnings per share
            growth_rate: Expected EPS growth rate (decimal, e.g., 0.15 for 15%)
            
        Returns:
            Dictionary with peg_fair_value and implied_pe
        """
        if eps <= 0 or growth_rate <= 0:
            return None
        
        # Convert to percentage
        growth_pct = growth_rate * 100
        
        # Cap at reasonable P/E (25x max)
        fair_pe = min(growth_pct, 25)
        fair_value = eps * fair_pe
        
        return {
            'peg_fair_value': round(fair_value, 2),
            'implied_pe': round(fair_pe, 1),
            'growth_rate_used': round(growth_rate * 100, 1)
        }
    
    @staticmethod
    def calculate_relative_value(
        stock_metrics: Dict[str, float],
        sector_medians: Dict[str, float]
    ) -> Optional[Dict[str, Any]]:
        """
        Compare stock valuation metrics to sector medians.
        
        Args:
            stock_metrics: Dict with pe_ratio, price_to_book, ev_to_ebitda, price_to_sales
            sector_medians: Dict with same keys for sector median values
            
        Returns:
            Dictionary with relative_score (>1 = undervalued) and status
        """
        metrics = ['pe_ratio', 'price_to_book', 'ev_to_ebitda', 'price_to_sales']
        scores = []
        breakdown = {}
        
        for metric in metrics:
            stock_val = stock_metrics.get(metric, 0)
            sector_val = sector_medians.get(metric, 0)
            
            if stock_val and sector_val and stock_val > 0 and sector_val > 0:
                # Lower stock value = more undervalued
                ratio = sector_val / stock_val
                # Cap at 2.0 to avoid extreme outliers
                capped_ratio = min(ratio, 2.0)
                scores.append(capped_ratio)
                breakdown[metric] = {
                    'stock': round(stock_val, 2),
                    'sector': round(sector_val, 2),
                    'ratio': round(ratio, 2)
                }
        
        if not scores:
            return None
        
        avg_score = sum(scores) / len(scores)
        
        # Determine status
        if avg_score > 1.2:
            status = 'significantly_undervalued'
        elif avg_score > 1.05:
            status = 'undervalued'
        elif avg_score >= 0.95:
            status = 'fair_value'
        elif avg_score >= 0.8:
            status = 'overvalued'
        else:
            status = 'significantly_overvalued'
        
        return {
            'relative_score': round(avg_score, 2),
            'status': status,
            'metrics_compared': len(scores),
            'breakdown': breakdown
        }
    
    @staticmethod
    def calculate_composite_score(
        current_price: float,
        dcf_value: Optional[float],
        epv_value: Optional[float],
        graham_number: Optional[float],
        peg_fair_value: Optional[float],
        relative_score: Optional[float]
    ) -> Dict[str, Any]:
        """
        Calculate composite valuation score (0-100) using weighted average.
        
        Weights:
        - DCF: 30%
        - EPV: 20%
        - Graham Number: 15%
        - PEG Fair Value: 10%
        - Relative Value: 25%
        
        Args:
            current_price: Current stock price
            dcf_value: Fair value from DCF model
            epv_value: Fair value from EPV model
            graham_number: Fair value from Graham Number
            peg_fair_value: Fair value from PEG model
            relative_score: Relative value score (1.0 = fair)
            
        Returns:
            Dictionary with composite_score, status, recommendation, breakdown
        """
        weights = {
            'dcf': 0.30,
            'epv': 0.20,
            'graham': 0.15,
            'peg': 0.10,
            'relative': 0.25
        }
        
        total_score = 0
        total_weight = 0
        breakdown = {}
        
        def margin_to_score(fair_value: float) -> Optional[float]:
            """Convert margin of safety to 0-100 score"""
            if not fair_value or current_price <= 0:
                return None
            margin = ((fair_value / current_price) - 1) * 100
            # Scale: -50% margin = 0, 0% margin = 50, +50% margin = 100
            return max(0, min(100, 50 + margin))
        
        # DCF
        if dcf_value:
            score = margin_to_score(dcf_value)
            if score is not None:
                total_score += score * weights['dcf']
                total_weight += weights['dcf']
                breakdown['dcf'] = {
                    'fair_value': dcf_value,
                    'margin': round(((dcf_value / current_price) - 1) * 100, 1),
                    'score': round(score, 1),
                    'weight': weights['dcf']
                }
        
        # EPV
        if epv_value:
            score = margin_to_score(epv_value)
            if score is not None:
                total_score += score * weights['epv']
                total_weight += weights['epv']
                breakdown['epv'] = {
                    'fair_value': epv_value,
                    'margin': round(((epv_value / current_price) - 1) * 100, 1),
                    'score': round(score, 1),
                    'weight': weights['epv']
                }
        
        # Graham Number
        if graham_number:
            score = margin_to_score(graham_number)
            if score is not None:
                total_score += score * weights['graham']
                total_weight += weights['graham']
                breakdown['graham'] = {
                    'fair_value': graham_number,
                    'margin': round(((graham_number / current_price) - 1) * 100, 1),
                    'score': round(score, 1),
                    'weight': weights['graham']
                }
        
        # PEG Fair Value
        if peg_fair_value:
            score = margin_to_score(peg_fair_value)
            if score is not None:
                total_score += score * weights['peg']
                total_weight += weights['peg']
                breakdown['peg'] = {
                    'fair_value': peg_fair_value,
                    'margin': round(((peg_fair_value / current_price) - 1) * 100, 1),
                    'score': round(score, 1),
                    'weight': weights['peg']
                }
        
        # Relative Value (already a ratio, not a price)
        if relative_score:
            # Convert relative score to 0-100
            # relative_score of 1.0 = 50 points, 2.0 = 100 points, 0.5 = 0 points
            score = max(0, min(100, (relative_score - 0.5) * 100))
            total_score += score * weights['relative']
            total_weight += weights['relative']
            breakdown['relative'] = {
                'ratio': relative_score,
                'score': round(score, 1),
                'weight': weights['relative']
            }
        
        if total_weight == 0:
            return {
                'composite_score': None,
                'status': 'insufficient_data',
                'recommendation': 'N/A',
                'confidence': 'none',
                'breakdown': {}
            }
        
        composite = total_score / total_weight
        
        # Determine status and recommendation
        if composite >= 70:
            status = 'significantly_undervalued'
            recommendation = 'STRONG BUY'
        elif composite >= 55:
            status = 'undervalued'
            recommendation = 'BUY'
        elif composite >= 45:
            status = 'fair_value'
            recommendation = 'HOLD'
        elif composite >= 30:
            status = 'overvalued'
            recommendation = 'SELL'
        else:
            status = 'significantly_overvalued'
            recommendation = 'STRONG SELL'
        
        # Confidence based on data coverage
        if total_weight >= 0.8:
            confidence = 'high'
        elif total_weight >= 0.5:
            confidence = 'medium'
        else:
            confidence = 'low'
        
        return {
            'composite_score': round(composite, 1),
            'status': status,
            'recommendation': recommendation,
            'confidence': confidence,
            'data_coverage': round(total_weight * 100, 0),
            'breakdown': breakdown,
            'current_price': current_price
        }
    
    @staticmethod
    def calculate_strength_score(fundamentals: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate financial strength score (0-100) based on fundamentals.
        
        Categories (25 points each):
        - Profitability: ROE, profit margin
        - Growth: Revenue growth, earnings growth
        - Financial Health: Current ratio, debt-to-equity
        - Cash Flow: FCF yield, cash conversion
        
        Args:
            fundamentals: Dict with roe, profit_margin, revenue_growth_yoy, 
                         earnings_growth_yoy, current_ratio, debt_to_equity,
                         fcf_yield, cash_conversion
                         
        Returns:
            Dictionary with strength_score and breakdown
        """
        breakdown = {}
        
        # Profitability (25 points)
        roe = fundamentals.get('roe', 0) or 0
        profit_margin = fundamentals.get('profit_margin', 0) or 0
        
        # ROE: 15% = full points (12.5), scale linearly
        roe_score = min(12.5, (roe * 100) * (12.5 / 15))
        # Profit margin: 10% = full points (12.5)
        pm_score = min(12.5, (profit_margin * 100) * (12.5 / 10))
        profitability = roe_score + pm_score
        breakdown['profitability'] = {
            'score': round(profitability, 1),
            'roe': round(roe * 100, 1) if roe else 0,
            'profit_margin': round(profit_margin * 100, 1) if profit_margin else 0
        }
        
        # Growth (25 points)
        rev_growth = fundamentals.get('revenue_growth_yoy', 0) or 0
        eps_growth = fundamentals.get('earnings_growth_yoy', 0) or 0
        
        # 20% growth = full points (12.5 each)
        rev_score = min(12.5, max(0, (rev_growth * 100) * (12.5 / 20)))
        eps_score = min(12.5, max(0, (eps_growth * 100) * (12.5 / 20)))
        growth = rev_score + eps_score
        breakdown['growth'] = {
            'score': round(growth, 1),
            'revenue_growth': round(rev_growth * 100, 1) if rev_growth else 0,
            'earnings_growth': round(eps_growth * 100, 1) if eps_growth else 0
        }
        
        # Financial Health (25 points)
        current_ratio = fundamentals.get('current_ratio', 0) or 0
        debt_equity = fundamentals.get('debt_to_equity', 0) or 0
        
        # Current ratio: 2.0 = full points (12.5)
        cr_score = min(12.5, current_ratio * (12.5 / 2))
        # Debt/equity: 0.5 = full points (12.5), higher is worse
        de_score = max(0, 12.5 - (debt_equity * (12.5 / 2)))
        health = cr_score + de_score
        breakdown['financial_health'] = {
            'score': round(health, 1),
            'current_ratio': round(current_ratio, 2) if current_ratio else 0,
            'debt_to_equity': round(debt_equity, 2) if debt_equity else 0
        }
        
        # Cash Flow (25 points)
        fcf_yield = fundamentals.get('fcf_yield', 0) or 0
        cash_conversion = fundamentals.get('cash_conversion', 0) or 0
        
        # FCF yield: 5% = full points (12.5)
        fcf_score = min(12.5, max(0, (fcf_yield * 100) * (12.5 / 5)))
        # Cash conversion: 100% = full points (12.5)
        cc_score = min(12.5, max(0, cash_conversion * 12.5))
        cash_flow = fcf_score + cc_score
        breakdown['cash_flow'] = {
            'score': round(cash_flow, 1),
            'fcf_yield': round(fcf_yield * 100, 1) if fcf_yield else 0,
            'cash_conversion': round(cash_conversion * 100, 1) if cash_conversion else 0
        }
        
        total = profitability + growth + health + cash_flow
        total = max(0, min(100, total))
        
        # Grade
        if total >= 80:
            grade = 'A'
        elif total >= 65:
            grade = 'B'
        elif total >= 50:
            grade = 'C'
        elif total >= 35:
            grade = 'D'
        else:
            grade = 'F'
        
        return {
            'strength_score': round(total, 1),
            'grade': grade,
            'breakdown': breakdown
        }


# Sector median data for relative valuation (can be updated periodically)
SECTOR_MEDIANS = {
    'Technology': {
        'pe_ratio': 25.0,
        'price_to_book': 5.0,
        'ev_to_ebitda': 15.0,
        'price_to_sales': 4.0
    },
    'Healthcare': {
        'pe_ratio': 20.0,
        'price_to_book': 3.5,
        'ev_to_ebitda': 12.0,
        'price_to_sales': 3.0
    },
    'Financial Services': {
        'pe_ratio': 12.0,
        'price_to_book': 1.2,
        'ev_to_ebitda': 8.0,
        'price_to_sales': 2.5
    },
    'Consumer Cyclical': {
        'pe_ratio': 18.0,
        'price_to_book': 4.0,
        'ev_to_ebitda': 10.0,
        'price_to_sales': 1.5
    },
    'Consumer Defensive': {
        'pe_ratio': 22.0,
        'price_to_book': 5.0,
        'ev_to_ebitda': 12.0,
        'price_to_sales': 2.0
    },
    'Industrials': {
        'pe_ratio': 18.0,
        'price_to_book': 3.0,
        'ev_to_ebitda': 11.0,
        'price_to_sales': 1.8
    },
    'Energy': {
        'pe_ratio': 10.0,
        'price_to_book': 1.5,
        'ev_to_ebitda': 5.0,
        'price_to_sales': 1.0
    },
    'Utilities': {
        'pe_ratio': 16.0,
        'price_to_book': 1.8,
        'ev_to_ebitda': 10.0,
        'price_to_sales': 2.5
    },
    'Real Estate': {
        'pe_ratio': 35.0,
        'price_to_book': 2.0,
        'ev_to_ebitda': 15.0,
        'price_to_sales': 8.0
    },
    'Basic Materials': {
        'pe_ratio': 12.0,
        'price_to_book': 2.0,
        'ev_to_ebitda': 7.0,
        'price_to_sales': 1.5
    },
    'Communication Services': {
        'pe_ratio': 18.0,
        'price_to_book': 3.0,
        'ev_to_ebitda': 10.0,
        'price_to_sales': 3.0
    },
    'default': {
        'pe_ratio': 18.0,
        'price_to_book': 3.0,
        'ev_to_ebitda': 10.0,
        'price_to_sales': 2.0
    }
}


def get_sector_medians(sector: str) -> Dict[str, float]:
    """Get sector median valuations for relative comparison"""
    return SECTOR_MEDIANS.get(sector, SECTOR_MEDIANS['default'])
