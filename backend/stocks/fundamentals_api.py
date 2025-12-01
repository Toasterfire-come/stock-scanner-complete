"""
Comprehensive fundamentals API for long-term investors.
Separate endpoint for heavy calculations (dividend, growth, DCF, etc.)
Loaded asynchronously on frontend for better UX.
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.core.cache import cache
import yfinance as yf
from decimal import Decimal


def _safe_float(value):
    """Safely convert value to float."""
    if value is None:
        return None
    try:
        if isinstance(value, (int, float, Decimal)):
            return float(value)
        return float(value)
    except (ValueError, TypeError):
        return None


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_stock_fundamentals(request, ticker):
    """
    Get comprehensive fundamentals for a stock.
    This is a separate endpoint to avoid slowing down main stock detail page.

    Returns:
    - Dividend analysis (growth rates, sustainability)
    - Growth metrics (revenue/EPS CAGR)
    - Profitability margins (gross, operating, net)
    - Balance sheet health (debt ratios, liquidity)
    - Cash flow analysis (FCF, OCF)
    - DCF valuation
    """
    try:
        ticker = ticker.upper().strip()

        # Check cache first (15 minute TTL)
        cache_key = f'fundamentals_{ticker}'
        cached = cache.get(cache_key)
        if cached:
            return Response({'success': True, 'ticker': ticker, 'data': cached, 'cached': True})

        # Fetch from yfinance
        ticker_obj = yf.Ticker(ticker)
        info = ticker_obj.info

        if not info:
            return Response({'success': False, 'error': 'Stock not found'}, status=404)

        fundamentals = {}

        # ===== DIVIDEND ANALYSIS =====
        try:
            dividend_data = {}
            dividend_data['dividend_rate'] = _safe_float(info.get('dividendRate'))
            dividend_data['dividend_yield'] = _safe_float(info.get('dividendYield'))
            if dividend_data['dividend_yield'] and dividend_data['dividend_yield'] < 1:
                dividend_data['dividend_yield'] = dividend_data['dividend_yield'] * 100

            dividend_data['payout_ratio'] = _safe_float(info.get('payoutRatio'))
            if dividend_data['payout_ratio'] and dividend_data['payout_ratio'] < 1:
                dividend_data['payout_ratio'] = dividend_data['payout_ratio'] * 100

            # Dividend history
            dividends = ticker_obj.dividends
            if dividends is not None and len(dividends) > 0:
                dividend_data['years_of_dividends'] = len(dividends) // 4

                # 5-year growth
                if len(dividends) >= 20:
                    div_5y_ago = dividends.iloc[-20]
                    div_current = dividends.iloc[-1]
                    if div_5y_ago > 0:
                        dividend_data['growth_5y'] = round(((div_current / div_5y_ago) ** (1/5) - 1) * 100, 2)

                # 3-year growth
                if len(dividends) >= 12:
                    div_3y_ago = dividends.iloc[-12]
                    div_current = dividends.iloc[-1]
                    if div_3y_ago > 0:
                        dividend_data['growth_3y'] = round(((div_current / div_3y_ago) ** (1/3) - 1) * 100, 2)

                # 1-year growth
                if len(dividends) >= 4:
                    div_1y_ago = dividends.iloc[-4]
                    div_current = dividends.iloc[-1]
                    if div_1y_ago > 0:
                        dividend_data['growth_1y'] = round(((div_current / div_1y_ago) - 1) * 100, 2)

                # Consecutive years of growth
                consecutive = 0
                for i in range(len(dividends)-1, 3, -4):
                    if i-4 >= 0 and dividends.iloc[i] > dividends.iloc[i-4]:
                        consecutive += 1
                    else:
                        break
                dividend_data['consecutive_years_growth'] = consecutive

                # Recent dividend history (last 10 payments)
                recent_divs = dividends.tail(10).tolist()
                dividend_data['recent_payments'] = [round(d, 4) for d in recent_divs]

            # Sustainability
            payout = dividend_data.get('payout_ratio')
            if payout:
                if payout < 60:
                    dividend_data['sustainability'] = 'Sustainable'
                    dividend_data['sustainability_score'] = 85
                elif payout < 80:
                    dividend_data['sustainability'] = 'Moderate Risk'
                    dividend_data['sustainability_score'] = 60
                else:
                    dividend_data['sustainability'] = 'High Risk'
                    dividend_data['sustainability_score'] = 30
            else:
                dividend_data['sustainability'] = 'Unknown'
                dividend_data['sustainability_score'] = 50

            fundamentals['dividends'] = dividend_data
        except Exception as e:
            fundamentals['dividends'] = {'error': str(e)}

        # ===== GROWTH METRICS =====
        try:
            growth_data = {}

            # Revenue CAGR
            financials = ticker_obj.financials
            if financials is not None and not financials.empty and 'Total Revenue' in financials.index:
                revenues = financials.loc['Total Revenue'].dropna().sort_index()
                if len(revenues) >= 2:
                    years = len(revenues) - 1
                    if years > 0 and revenues.iloc[0] > 0:
                        growth_data['revenue_cagr'] = round(((revenues.iloc[-1] / revenues.iloc[0]) ** (1/years) - 1) * 100, 2)
                        growth_data['revenue_cagr_years'] = years

                    # Recent revenue values for chart
                    growth_data['revenue_history'] = [
                        {'year': str(revenues.index[i].year), 'revenue': float(revenues.iloc[i])}
                        for i in range(len(revenues))
                    ]

            # EPS CAGR
            earnings_hist = ticker_obj.earnings_history
            if earnings_hist is not None and not earnings_hist.empty and 'epsActual' in earnings_hist.columns:
                eps_data = earnings_hist['epsActual'].dropna()
                if len(eps_data) >= 8:
                    eps_2y_ago = eps_data.iloc[0]
                    eps_current = eps_data.iloc[-1]
                    if eps_2y_ago > 0:
                        growth_data['eps_cagr_2y'] = round(((eps_current / eps_2y_ago) ** (1/2) - 1) * 100, 2)

                # Recent EPS for chart
                growth_data['eps_history'] = [
                    {'quarter': i+1, 'eps': float(eps_data.iloc[i])}
                    for i in range(min(8, len(eps_data)))
                ]

            fundamentals['growth'] = growth_data
        except Exception as e:
            fundamentals['growth'] = {'error': str(e)}

        # ===== PROFITABILITY =====
        try:
            profit_data = {}
            profit_data['gross_margin'] = _safe_float(info.get('grossMargins'))
            profit_data['operating_margin'] = _safe_float(info.get('operatingMargins'))
            profit_data['profit_margin'] = _safe_float(info.get('profitMargins'))
            profit_data['ebitda_margin'] = _safe_float(info.get('ebitdaMargins'))

            # Convert to percentages
            for key in ['gross_margin', 'operating_margin', 'profit_margin', 'ebitda_margin']:
                if profit_data[key] and profit_data[key] < 1:
                    profit_data[key] = round(profit_data[key] * 100, 2)

            # Return metrics
            profit_data['roe'] = _safe_float(info.get('returnOnEquity'))
            profit_data['roa'] = _safe_float(info.get('returnOnAssets'))
            if profit_data['roe'] and profit_data['roe'] < 1:
                profit_data['roe'] = round(profit_data['roe'] * 100, 2)
            if profit_data['roa'] and profit_data['roa'] < 1:
                profit_data['roa'] = round(profit_data['roa'] * 100, 2)

            fundamentals['profitability'] = profit_data
        except Exception as e:
            fundamentals['profitability'] = {'error': str(e)}

        # ===== BALANCE SHEET =====
        try:
            balance_data = {}
            balance_data['debt_to_equity'] = _safe_float(info.get('debtToEquity'))
            balance_data['current_ratio'] = _safe_float(info.get('currentRatio'))
            balance_data['quick_ratio'] = _safe_float(info.get('quickRatio'))
            balance_data['total_debt'] = _safe_float(info.get('totalDebt'))
            balance_data['total_cash'] = _safe_float(info.get('totalCash'))

            # Net debt
            if balance_data['total_debt'] and balance_data['total_cash']:
                balance_data['net_debt'] = balance_data['total_debt'] - balance_data['total_cash']

            # Interest coverage
            ebit = _safe_float(info.get('ebit'))
            interest_expense = _safe_float(info.get('interestExpense'))
            if ebit and interest_expense and interest_expense != 0:
                balance_data['interest_coverage'] = round(ebit / abs(interest_expense), 2)

            # Health score
            health_score = 50  # Start neutral
            if balance_data.get('debt_to_equity'):
                if balance_data['debt_to_equity'] < 50:
                    health_score += 25
                elif balance_data['debt_to_equity'] > 150:
                    health_score -= 25

            if balance_data.get('current_ratio'):
                if balance_data['current_ratio'] > 1.5:
                    health_score += 25
                elif balance_data['current_ratio'] < 1.0:
                    health_score -= 25

            balance_data['health_score'] = max(0, min(100, health_score))

            fundamentals['balance_sheet'] = balance_data
        except Exception as e:
            fundamentals['balance_sheet'] = {'error': str(e)}

        # ===== CASH FLOW =====
        try:
            cf_data = {}
            cf = ticker_obj.cashflow
            if cf is not None and not cf.empty:
                if 'Operating Cash Flow' in cf.index:
                    ocf = cf.loc['Operating Cash Flow'].dropna()
                    if len(ocf) > 0:
                        cf_data['operating_cash_flow'] = float(ocf.iloc[0])

                if 'Free Cash Flow' in cf.index:
                    fcf = cf.loc['Free Cash Flow'].dropna()
                    if len(fcf) > 0:
                        cf_data['free_cash_flow'] = float(fcf.iloc[0])

                        # FCF Margin
                        if 'Total Revenue' in cf.index:
                            revenue = cf.loc['Total Revenue'].dropna()
                            if len(revenue) > 0 and revenue.iloc[0] != 0:
                                cf_data['fcf_margin'] = round((fcf.iloc[0] / revenue.iloc[0]) * 100, 2)

                        # Historical FCF for chart (last 5 years)
                        fcf_hist = fcf.head(5)
                        cf_data['fcf_history'] = [
                            {'year': str(fcf_hist.index[i].year), 'fcf': float(fcf_hist.iloc[i])}
                            for i in range(len(fcf_hist))
                        ]

            # FCF Yield
            market_cap = _safe_float(info.get('marketCap'))
            if cf_data.get('free_cash_flow') and market_cap and market_cap > 0:
                cf_data['fcf_yield'] = round((cf_data['free_cash_flow'] / market_cap) * 100, 2)

            fundamentals['cash_flow'] = cf_data
        except Exception as e:
            fundamentals['cash_flow'] = {'error': str(e)}

        # ===== DCF VALUATION =====
        try:
            dcf_data = {}
            fcf = fundamentals.get('cash_flow', {}).get('free_cash_flow')

            if fcf and fcf > 0:
                # Growth rate from revenue CAGR or default 5%
                growth_rate = 5.0
                if fundamentals.get('growth', {}).get('revenue_cagr'):
                    growth_rate = min(max(fundamentals['growth']['revenue_cagr'], 0), 25)

                dcf_data['growth_rate_used'] = growth_rate
                wacc = 10.0  # 10% discount rate
                terminal_growth = 3.0  # 3% perpetual

                # Project 5 years
                projections = []
                for year in range(1, 6):
                    fcf_future = fcf * ((1 + growth_rate/100) ** year)
                    pv = fcf_future / ((1 + wacc/100) ** year)
                    projections.append({
                        'year': year,
                        'fcf': round(fcf_future, 2),
                        'pv': round(pv, 2)
                    })

                dcf_data['projections'] = projections

                # Terminal value
                fcf_terminal = fcf * ((1 + growth_rate/100) ** 5) * (1 + terminal_growth/100)
                terminal_value = fcf_terminal / ((wacc/100) - (terminal_growth/100))
                pv_terminal = terminal_value / ((1 + wacc/100) ** 5)

                dcf_data['terminal_value'] = round(terminal_value, 2)
                dcf_data['pv_terminal'] = round(pv_terminal, 2)

                # Enterprise value
                enterprise_value = sum(p['pv'] for p in projections) + pv_terminal
                dcf_data['enterprise_value'] = round(enterprise_value, 2)

                # Equity value (subtract net debt)
                equity_value = enterprise_value
                net_debt = fundamentals.get('balance_sheet', {}).get('net_debt')
                if net_debt:
                    equity_value = enterprise_value - net_debt
                    dcf_data['net_debt_adjustment'] = round(net_debt, 2)

                dcf_data['equity_value'] = round(equity_value, 2)

                # Per share
                shares = _safe_float(info.get('sharesOutstanding'))
                if shares and shares > 0:
                    dcf_data['value_per_share'] = round(equity_value / shares, 2)

                    # Compare to current price
                    current_price = _safe_float(info.get('currentPrice'))
                    if current_price and current_price > 0:
                        dcf_data['current_price'] = current_price
                        upside = ((dcf_data['value_per_share'] - current_price) / current_price) * 100
                        dcf_data['upside_pct'] = round(upside, 2)

            fundamentals['dcf'] = dcf_data
        except Exception as e:
            fundamentals['dcf'] = {'error': str(e)}

        # Cache for 15 minutes
        cache.set(cache_key, fundamentals, 900)

        return Response({
            'success': True,
            'ticker': ticker,
            'data': fundamentals,
            'cached': False,
            'timestamp': info.get('regularMarketTime', 'unknown')
        })

    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)
