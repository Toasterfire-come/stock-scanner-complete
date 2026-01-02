"""
Greeks Calculator using Black-Scholes Model
Calculates option prices and Greeks (Delta, Gamma, Theta, Vega, Rho)
"""

import numpy as np
from scipy.stats import norm
from decimal import Decimal
from typing import Dict, Tuple


class GreeksCalculator:
    """
    Black-Scholes option pricing and Greeks calculation.

    Uses the standard Black-Scholes-Merton model for European-style options.
    """

    @staticmethod
    def black_scholes_price(
        spot_price: float,
        strike_price: float,
        time_to_expiry: float,
        risk_free_rate: float,
        volatility: float,
        option_type: str = 'call'
    ) -> float:
        """
        Calculate option price using Black-Scholes formula.

        Args:
            spot_price: Current stock price
            strike_price: Option strike price
            time_to_expiry: Time to expiration in years
            risk_free_rate: Risk-free interest rate (annualized)
            volatility: Implied volatility (annualized)
            option_type: 'call' or 'put'

        Returns:
            Option price
        """
        if time_to_expiry <= 0:
            # At expiration, option value is intrinsic value
            if option_type == 'call':
                return max(0, spot_price - strike_price)
            else:
                return max(0, strike_price - spot_price)

        # Calculate d1 and d2
        d1 = (np.log(spot_price / strike_price) +
              (risk_free_rate + 0.5 * volatility ** 2) * time_to_expiry) / (
              volatility * np.sqrt(time_to_expiry))
        d2 = d1 - volatility * np.sqrt(time_to_expiry)

        if option_type == 'call':
            price = (spot_price * norm.cdf(d1) -
                    strike_price * np.exp(-risk_free_rate * time_to_expiry) * norm.cdf(d2))
        else:  # put
            price = (strike_price * np.exp(-risk_free_rate * time_to_expiry) * norm.cdf(-d2) -
                    spot_price * norm.cdf(-d1))

        return float(price)

    @staticmethod
    def calculate_greeks(
        spot_price: float,
        strike_price: float,
        time_to_expiry: float,
        risk_free_rate: float,
        volatility: float,
        option_type: str = 'call'
    ) -> Dict[str, float]:
        """
        Calculate all Greeks for an option.

        Args:
            spot_price: Current stock price
            strike_price: Option strike price
            time_to_expiry: Time to expiration in years
            risk_free_rate: Risk-free interest rate (annualized)
            volatility: Implied volatility (annualized)
            option_type: 'call' or 'put'

        Returns:
            Dictionary with delta, gamma, theta, vega, rho
        """
        if time_to_expiry <= 0:
            return {
                'delta': 1.0 if option_type == 'call' and spot_price > strike_price else 0.0,
                'gamma': 0.0,
                'theta': 0.0,
                'vega': 0.0,
                'rho': 0.0
            }

        # Calculate d1 and d2
        d1 = (np.log(spot_price / strike_price) +
              (risk_free_rate + 0.5 * volatility ** 2) * time_to_expiry) / (
              volatility * np.sqrt(time_to_expiry))
        d2 = d1 - volatility * np.sqrt(time_to_expiry)

        # Delta
        if option_type == 'call':
            delta = norm.cdf(d1)
        else:  # put
            delta = norm.cdf(d1) - 1

        # Gamma (same for both calls and puts)
        gamma = norm.pdf(d1) / (spot_price * volatility * np.sqrt(time_to_expiry))

        # Theta
        theta_term1 = -(spot_price * norm.pdf(d1) * volatility) / (2 * np.sqrt(time_to_expiry))
        if option_type == 'call':
            theta_term2 = -risk_free_rate * strike_price * np.exp(-risk_free_rate * time_to_expiry) * norm.cdf(d2)
            theta = (theta_term1 + theta_term2) / 365  # Convert to daily theta
        else:  # put
            theta_term2 = risk_free_rate * strike_price * np.exp(-risk_free_rate * time_to_expiry) * norm.cdf(-d2)
            theta = (theta_term1 + theta_term2) / 365  # Convert to daily theta

        # Vega (same for both calls and puts)
        vega = spot_price * norm.pdf(d1) * np.sqrt(time_to_expiry) / 100  # Vega per 1% change in IV

        # Rho
        if option_type == 'call':
            rho = strike_price * time_to_expiry * np.exp(-risk_free_rate * time_to_expiry) * norm.cdf(d2) / 100
        else:  # put
            rho = -strike_price * time_to_expiry * np.exp(-risk_free_rate * time_to_expiry) * norm.cdf(-d2) / 100

        return {
            'delta': float(delta),
            'gamma': float(gamma),
            'theta': float(theta),
            'vega': float(vega),
            'rho': float(rho)
        }

    @staticmethod
    def calculate_implied_volatility(
        option_price: float,
        spot_price: float,
        strike_price: float,
        time_to_expiry: float,
        risk_free_rate: float,
        option_type: str = 'call',
        tolerance: float = 0.0001,
        max_iterations: int = 100
    ) -> float:
        """
        Calculate implied volatility using Newton-Raphson method.

        Args:
            option_price: Market price of the option
            spot_price: Current stock price
            strike_price: Option strike price
            time_to_expiry: Time to expiration in years
            risk_free_rate: Risk-free interest rate (annualized)
            option_type: 'call' or 'put'
            tolerance: Convergence tolerance
            max_iterations: Maximum number of iterations

        Returns:
            Implied volatility
        """
        # Initial guess using Brenner-Subrahmanyam approximation
        sigma = np.sqrt(2 * np.pi / time_to_expiry) * (option_price / spot_price)

        for i in range(max_iterations):
            # Calculate option price and vega at current sigma
            price = GreeksCalculator.black_scholes_price(
                spot_price, strike_price, time_to_expiry,
                risk_free_rate, sigma, option_type
            )

            greeks = GreeksCalculator.calculate_greeks(
                spot_price, strike_price, time_to_expiry,
                risk_free_rate, sigma, option_type
            )
            vega = greeks['vega'] * 100  # Convert back to total vega

            # Calculate price difference
            diff = price - option_price

            # Check for convergence
            if abs(diff) < tolerance:
                return float(sigma)

            # Newton-Raphson update
            if vega != 0:
                sigma = sigma - diff / vega
            else:
                break

            # Keep sigma positive and reasonable
            sigma = max(0.01, min(5.0, sigma))

        # If convergence failed, return best estimate
        return float(sigma)

    @staticmethod
    def create_iv_surface(
        spot_price: float,
        strike_prices: list,
        expiration_dates: list,  # List of (date, time_to_expiry_years)
        risk_free_rate: float,
        option_chain_data: dict  # {(strike, expiration): {'call_price': X, 'put_price': Y}}
    ) -> Dict:
        """
        Generate implied volatility surface from option chain data.

        Args:
            spot_price: Current stock price
            strike_prices: List of strike prices
            expiration_dates: List of tuples (expiration_date, time_to_expiry_years)
            risk_free_rate: Risk-free interest rate
            option_chain_data: Dictionary mapping (strike, expiration) to prices

        Returns:
            Dictionary with IV surface data
        """
        surface_data = {
            'strikes': strike_prices,
            'expirations': [exp[0] for exp in expiration_dates],
            'times_to_expiry': [exp[1] for exp in expiration_dates],
            'call_iv': [],
            'put_iv': []
        }

        for expiry_date, time_to_expiry in expiration_dates:
            call_ivs = []
            put_ivs = []

            for strike in strike_prices:
                key = (strike, expiry_date)

                if key in option_chain_data:
                    data = option_chain_data[key]

                    # Calculate call IV
                    if 'call_price' in data and data['call_price'] > 0:
                        try:
                            call_iv = GreeksCalculator.calculate_implied_volatility(
                                data['call_price'], spot_price, strike,
                                time_to_expiry, risk_free_rate, 'call'
                            )
                            call_ivs.append(call_iv)
                        except:
                            call_ivs.append(None)
                    else:
                        call_ivs.append(None)

                    # Calculate put IV
                    if 'put_price' in data and data['put_price'] > 0:
                        try:
                            put_iv = GreeksCalculator.calculate_implied_volatility(
                                data['put_price'], spot_price, strike,
                                time_to_expiry, risk_free_rate, 'put'
                            )
                            put_ivs.append(put_iv)
                        except:
                            put_ivs.append(None)
                    else:
                        put_ivs.append(None)
                else:
                    call_ivs.append(None)
                    put_ivs.append(None)

            surface_data['call_iv'].append(call_ivs)
            surface_data['put_iv'].append(put_ivs)

        return surface_data
