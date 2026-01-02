"""
Options Data Service - Real-Time Fetching
Fetches live options data from yfinance with no caching.
Per user requirements: Real-time data for better UX.
"""

import yfinance as yf
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Tuple
from stocks.greeks_calculator import GreeksCalculator


class OptionsDataService:
    """
    Service for fetching and processing real-time options data.

    NO CACHING - Always fetches fresh data from yfinance.
    Calculates Greeks on-the-fly for each request.
    """

    # Risk-free rate (approximation - can be updated to fetch from FRED API)
    DEFAULT_RISK_FREE_RATE = 0.045  # 4.5% current treasury rate

    @staticmethod
    def fetch_option_chain_realtime(ticker: str) -> Dict:
        """
        Fetch LIVE option chain from yfinance with no caching.

        Args:
            ticker: Stock ticker symbol

        Returns:
            Dictionary with option chain data and calculated Greeks
        """
        try:
            stock = yf.Ticker(ticker)

            # Get current stock price
            try:
                info = stock.info
                spot_price = info.get('currentPrice') or info.get('regularMarketPrice')
                if not spot_price:
                    # Fallback to history
                    hist = stock.history(period='1d')
                    if not hist.empty:
                        spot_price = float(hist['Close'].iloc[-1])
                    else:
                        return {'error': 'Unable to fetch current stock price'}
            except Exception as e:
                return {'error': f'Unable to fetch stock data: {str(e)}'}

            # Get available expiration dates
            try:
                expirations = stock.options
                if not expirations:
                    return {'error': 'No options data available for this ticker'}
            except Exception as e:
                return {'error': f'Unable to fetch expiration dates: {str(e)}'}

            # Fetch option chains for all expirations
            chains = []
            for expiration_date in expirations:
                try:
                    # Fetch option chain for this expiration
                    opt_chain = stock.option_chain(expiration_date)

                    # Calculate time to expiry
                    expiry_dt = datetime.strptime(expiration_date, '%Y-%m-%d')
                    today = datetime.now()
                    time_to_expiry = (expiry_dt - today).days / 365.25

                    if time_to_expiry <= 0:
                        continue  # Skip expired options

                    # Process calls
                    calls_data = []
                    if opt_chain.calls is not None and not opt_chain.calls.empty:
                        for _, row in opt_chain.calls.iterrows():
                            contract_data = OptionsDataService._process_contract(
                                row, spot_price, time_to_expiry, 'call'
                            )
                            if contract_data:
                                calls_data.append(contract_data)

                    # Process puts
                    puts_data = []
                    if opt_chain.puts is not None and not opt_chain.puts.empty:
                        for _, row in opt_chain.puts.iterrows():
                            contract_data = OptionsDataService._process_contract(
                                row, spot_price, time_to_expiry, 'put'
                            )
                            if contract_data:
                                puts_data.append(contract_data)

                    chains.append({
                        'expiration_date': expiration_date,
                        'time_to_expiry': time_to_expiry,
                        'calls': calls_data,
                        'puts': puts_data
                    })

                except Exception as e:
                    # Skip problematic expirations
                    continue

            return {
                'ticker': ticker,
                'spot_price': float(spot_price),
                'timestamp': datetime.now().isoformat(),
                'chains': chains,
                'expirations': list(expirations)
            }

        except Exception as e:
            return {'error': f'Failed to fetch option chain: {str(e)}'}

    @staticmethod
    def _process_contract(row, spot_price: float, time_to_expiry: float, option_type: str) -> Optional[Dict]:
        """
        Process a single option contract and calculate Greeks.

        Args:
            row: DataFrame row with contract data
            spot_price: Current stock price
            time_to_expiry: Time to expiration in years
            option_type: 'call' or 'put'

        Returns:
            Dictionary with contract data and Greeks
        """
        try:
            strike = float(row.get('strike', 0))
            last_price = float(row.get('lastPrice', 0))
            bid = float(row.get('bid', 0))
            ask = float(row.get('ask', 0))
            volume = int(row.get('volume', 0)) if row.get('volume') else 0
            open_interest = int(row.get('openInterest', 0)) if row.get('openInterest') else 0
            implied_volatility = float(row.get('impliedVolatility', 0))

            # Skip if no price data
            if last_price <= 0 and bid <= 0 and ask <= 0:
                return None

            # Use mid price if last price is not available
            price = last_price if last_price > 0 else (bid + ask) / 2 if (bid + ask) > 0 else 0

            if price <= 0:
                return None

            # Calculate Greeks
            greeks = GreeksCalculator.calculate_greeks(
                spot_price=spot_price,
                strike_price=strike,
                time_to_expiry=time_to_expiry,
                risk_free_rate=OptionsDataService.DEFAULT_RISK_FREE_RATE,
                volatility=implied_volatility if implied_volatility > 0 else 0.3,  # Default to 30% if IV is 0
                option_type=option_type
            )

            # Calculate intrinsic and extrinsic value
            if option_type == 'call':
                intrinsic_value = max(0, spot_price - strike)
            else:
                intrinsic_value = max(0, strike - spot_price)

            extrinsic_value = price - intrinsic_value

            # Determine if in/at/out of the money
            if option_type == 'call':
                moneyness = 'ITM' if spot_price > strike else ('ATM' if abs(spot_price - strike) < 0.5 else 'OTM')
            else:
                moneyness = 'ITM' if spot_price < strike else ('ATM' if abs(spot_price - strike) < 0.5 else 'OTM')

            return {
                'contract_symbol': row.get('contractSymbol', ''),
                'strike': strike,
                'last_price': last_price,
                'bid': bid,
                'ask': ask,
                'volume': volume,
                'open_interest': open_interest,
                'implied_volatility': implied_volatility,
                'delta': greeks['delta'],
                'gamma': greeks['gamma'],
                'theta': greeks['theta'],
                'vega': greeks['vega'],
                'rho': greeks['rho'],
                'intrinsic_value': intrinsic_value,
                'extrinsic_value': extrinsic_value,
                'moneyness': moneyness,
                'in_the_money': moneyness == 'ITM'
            }

        except Exception as e:
            return None

    @staticmethod
    def get_greeks_surface(ticker: str, expiration_date: str) -> Dict:
        """
        Generate Greeks surface for a specific expiration.

        Args:
            ticker: Stock ticker symbol
            expiration_date: Expiration date in YYYY-MM-DD format

        Returns:
            Dictionary with Greeks vs Strike data
        """
        try:
            stock = yf.Ticker(ticker)

            # Get current price
            info = stock.info
            spot_price = info.get('currentPrice') or info.get('regularMarketPrice')

            # Get option chain for specific expiration
            opt_chain = stock.option_chain(expiration_date)

            # Calculate time to expiry
            expiry_dt = datetime.strptime(expiration_date, '%Y-%m-%d')
            time_to_expiry = (expiry_dt - datetime.now()).days / 365.25

            # Build surface data
            strikes = []
            call_deltas = []
            call_gammas = []
            call_thetas = []
            call_vegas = []
            put_deltas = []
            put_gammas = []
            put_thetas = []
            put_vegas = []

            # Process calls
            for _, row in opt_chain.calls.iterrows():
                strike = float(row['strike'])
                iv = float(row.get('impliedVolatility', 0.3))

                greeks = GreeksCalculator.calculate_greeks(
                    spot_price, strike, time_to_expiry,
                    OptionsDataService.DEFAULT_RISK_FREE_RATE, iv, 'call'
                )

                strikes.append(strike)
                call_deltas.append(greeks['delta'])
                call_gammas.append(greeks['gamma'])
                call_thetas.append(greeks['theta'])
                call_vegas.append(greeks['vega'])

            # Process puts
            for _, row in opt_chain.puts.iterrows():
                strike = float(row['strike'])
                iv = float(row.get('impliedVolatility', 0.3))

                greeks = GreeksCalculator.calculate_greeks(
                    spot_price, strike, time_to_expiry,
                    OptionsDataService.DEFAULT_RISK_FREE_RATE, iv, 'put'
                )

                put_deltas.append(greeks['delta'])
                put_gammas.append(greeks['gamma'])
                put_thetas.append(greeks['theta'])
                put_vegas.append(greeks['vega'])

            return {
                'ticker': ticker,
                'expiration_date': expiration_date,
                'spot_price': float(spot_price),
                'strikes': strikes,
                'calls': {
                    'delta': call_deltas,
                    'gamma': call_gammas,
                    'theta': call_thetas,
                    'vega': call_vegas
                },
                'puts': {
                    'delta': put_deltas,
                    'gamma': put_gammas,
                    'theta': put_thetas,
                    'vega': put_vegas
                }
            }

        except Exception as e:
            return {'error': f'Failed to generate Greeks surface: {str(e)}'}

    @staticmethod
    def get_iv_surface_realtime(ticker: str) -> Dict:
        """
        Generate implied volatility surface from live data.

        Args:
            ticker: Stock ticker symbol

        Returns:
            Dictionary with IV surface data
        """
        try:
            stock = yf.Ticker(ticker)

            # Get current price
            info = stock.info
            spot_price = info.get('currentPrice') or info.get('regularMarketPrice')

            # Get expirations
            expirations = stock.options

            surface_data = {
                'ticker': ticker,
                'spot_price': float(spot_price),
                'timestamp': datetime.now().isoformat(),
                'expirations': [],
                'strikes': [],
                'call_iv': [],
                'put_iv': []
            }

            for expiration_date in expirations[:6]:  # Limit to first 6 expirations for performance
                try:
                    opt_chain = stock.option_chain(expiration_date)

                    expiry_dt = datetime.strptime(expiration_date, '%Y-%m-%d')
                    time_to_expiry = (expiry_dt - datetime.now()).days / 365.25

                    if time_to_expiry <= 0:
                        continue

                    surface_data['expirations'].append({
                        'date': expiration_date,
                        'days': int((expiry_dt - datetime.now()).days),
                        'time_to_expiry': time_to_expiry
                    })

                    # Get unique strikes
                    if not surface_data['strikes']:
                        strikes = sorted(set(opt_chain.calls['strike'].tolist()))
                        surface_data['strikes'] = [float(s) for s in strikes]

                    # Extract IVs
                    call_ivs = []
                    put_ivs = []

                    for strike in surface_data['strikes']:
                        # Find call IV
                        call_row = opt_chain.calls[opt_chain.calls['strike'] == strike]
                        if not call_row.empty:
                            call_ivs.append(float(call_row.iloc[0].get('impliedVolatility', 0)))
                        else:
                            call_ivs.append(None)

                        # Find put IV
                        put_row = opt_chain.puts[opt_chain.puts['strike'] == strike]
                        if not put_row.empty:
                            put_ivs.append(float(put_row.iloc[0].get('impliedVolatility', 0)))
                        else:
                            put_ivs.append(None)

                    surface_data['call_iv'].append(call_ivs)
                    surface_data['put_iv'].append(put_ivs)

                except Exception:
                    continue

            return surface_data

        except Exception as e:
            return {'error': f'Failed to generate IV surface: {str(e)}'}

    @staticmethod
    def calculate_theoretical_price(
        ticker: str,
        strike: float,
        expiration_date: str,
        volatility: float,
        option_type: str = 'call'
    ) -> Dict:
        """
        Calculate theoretical option price using Black-Scholes.

        Args:
            ticker: Stock ticker symbol
            strike: Strike price
            expiration_date: Expiration date in YYYY-MM-DD format
            volatility: Volatility to use (annualized)
            option_type: 'call' or 'put'

        Returns:
            Dictionary with price and Greeks
        """
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            spot_price = info.get('currentPrice') or info.get('regularMarketPrice')

            expiry_dt = datetime.strptime(expiration_date, '%Y-%m-%d')
            time_to_expiry = (expiry_dt - datetime.now()).days / 365.25

            if time_to_expiry <= 0:
                return {'error': 'Expiration date is in the past'}

            price = GreeksCalculator.black_scholes_price(
                spot_price, strike, time_to_expiry,
                OptionsDataService.DEFAULT_RISK_FREE_RATE,
                volatility, option_type
            )

            greeks = GreeksCalculator.calculate_greeks(
                spot_price, strike, time_to_expiry,
                OptionsDataService.DEFAULT_RISK_FREE_RATE,
                volatility, option_type
            )

            return {
                'ticker': ticker,
                'spot_price': float(spot_price),
                'strike': strike,
                'expiration_date': expiration_date,
                'time_to_expiry': time_to_expiry,
                'volatility': volatility,
                'option_type': option_type,
                'theoretical_price': float(price),
                'greeks': greeks
            }

        except Exception as e:
            return {'error': f'Failed to calculate price: {str(e)}'}
