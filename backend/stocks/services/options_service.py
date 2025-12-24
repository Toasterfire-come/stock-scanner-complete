"""
Options Analytics Service
Comprehensive options data fetching, Greeks calculation, and IV analysis.
Integrates with yfinance for options chain data.
"""

import yfinance as yf
import numpy as np
from datetime import datetime, timedelta
from decimal import Decimal
from scipy.stats import norm
from scipy.optimize import brentq
from django.utils import timezone
from django.db import transaction
import logging

logger = logging.getLogger(__name__)


class OptionsService:
    """Service for options data and analytics"""

    # Risk-free rate (approximate - should be updated periodically)
    RISK_FREE_RATE = 0.045  # 4.5% annual rate

    @staticmethod
    def fetch_options_chain(ticker, force_refresh=False):
        """
        Fetch complete options chain for a ticker.

        Args:
            ticker: Stock ticker symbol
            force_refresh: Force refresh even if recent data exists

        Returns:
            dict: {
                'success': bool,
                'chain_id': int,
                'contracts_count': int,
                'expirations': list
            }
        """
        from stocks.models import Stock, OptionsChain, OptionsContract

        try:
            # Get stock
            stock = Stock.objects.get(ticker=ticker.upper())
        except Stock.DoesNotExist:
            return {'success': False, 'error': f'Stock {ticker} not found'}

        # Check if recent chain exists (within last hour)
        if not force_refresh:
            recent_chain = OptionsChain.objects.filter(
                stock=stock,
                is_current=True,
                snapshot_time__gte=timezone.now() - timedelta(hours=1)
            ).first()

            if recent_chain:
                return {
                    'success': True,
                    'chain_id': recent_chain.id,
                    'contracts_count': recent_chain.total_contracts,
                    'message': 'Using cached chain data',
                    'cached': True
                }

        try:
            # Fetch from yfinance
            ticker_obj = yf.Ticker(ticker)
            expirations = ticker_obj.options

            if not expirations:
                return {'success': False, 'error': 'No options available for this ticker'}

            snapshot_time = timezone.now()
            underlying_price = Decimal(str(stock.current_price or 0))

            # Mark previous chains as not current
            OptionsChain.objects.filter(stock=stock, is_current=True).update(is_current=False)

            # Create new chain
            with transaction.atomic():
                chain = OptionsChain.objects.create(
                    stock=stock,
                    snapshot_date=snapshot_time.date(),
                    snapshot_time=snapshot_time,
                    underlying_price=underlying_price,
                    expirations_count=len(expirations),
                    is_current=True
                )

                total_contracts = 0

                # Fetch each expiration
                for exp_date_str in expirations:
                    try:
                        opt_chain = ticker_obj.option_chain(exp_date_str)
                        exp_date = datetime.strptime(exp_date_str, '%Y-%m-%d').date()

                        # Calculate days to expiration
                        dte = (exp_date - snapshot_time.date()).days

                        # Process calls
                        for _, row in opt_chain.calls.iterrows():
                            contract = OptionsService._create_contract_from_row(
                                chain=chain,
                                stock=stock,
                                row=row,
                                contract_type='call',
                                expiration=exp_date,
                                dte=dte,
                                underlying_price=float(underlying_price)
                            )
                            if contract:
                                total_contracts += 1

                        # Process puts
                        for _, row in opt_chain.puts.iterrows():
                            contract = OptionsService._create_contract_from_row(
                                chain=chain,
                                stock=stock,
                                row=row,
                                contract_type='put',
                                expiration=exp_date,
                                dte=dte,
                                underlying_price=float(underlying_price)
                            )
                            if contract:
                                total_contracts += 1

                    except Exception as e:
                        logger.warning(f"Error fetching expiration {exp_date_str} for {ticker}: {str(e)}")
                        continue

                # Update chain totals
                chain.total_contracts = total_contracts
                chain.save()

                logger.info(f"Fetched options chain for {ticker}: {total_contracts} contracts")

                return {
                    'success': True,
                    'chain_id': chain.id,
                    'contracts_count': total_contracts,
                    'expirations': list(expirations),
                    'cached': False
                }

        except Exception as e:
            logger.error(f"Error fetching options for {ticker}: {str(e)}")
            return {'success': False, 'error': str(e)}

    @staticmethod
    def _create_contract_from_row(chain, stock, row, contract_type, expiration, dte, underlying_price):
        """Create OptionsContract from yfinance data row"""
        from stocks.models import OptionsContract

        try:
            strike = Decimal(str(row.get('strike', 0)))
            last_price = Decimal(str(row.get('lastPrice', 0)))
            bid = Decimal(str(row.get('bid', 0)))
            ask = Decimal(str(row.get('ask', 0)))

            # Calculate mark (mid price)
            if bid and ask:
                mark = (bid + ask) / 2
            else:
                mark = last_price

            # Get IV if available
            iv = row.get('impliedVolatility')
            if iv and not np.isnan(iv):
                iv = Decimal(str(iv))
            else:
                iv = None

            # Calculate Greeks if IV is available
            greeks = {}
            if iv and dte > 0:
                greeks = OptionsService.calculate_greeks(
                    S=underlying_price,
                    K=float(strike),
                    T=dte / 365.0,
                    r=OptionsService.RISK_FREE_RATE,
                    sigma=float(iv),
                    option_type=contract_type
                )

            # Determine moneyness
            if contract_type == 'call':
                in_the_money = underlying_price > strike
                intrinsic = max(Decimal(str(underlying_price)) - strike, Decimal('0'))
            else:  # put
                in_the_money = underlying_price < strike
                intrinsic = max(strike - Decimal(str(underlying_price)), Decimal('0'))

            extrinsic = max(mark - intrinsic, Decimal('0'))

            # Contract symbol
            contract_symbol = row.get('contractSymbol', f"{stock.ticker}_{expiration}_{strike}_{contract_type[0].upper()}")

            # Create contract
            contract = OptionsContract.objects.create(
                chain=chain,
                stock=stock,
                contract_symbol=contract_symbol,
                contract_type=contract_type,
                strike=strike,
                expiration=expiration,
                dte=dte,
                last_price=last_price,
                bid=bid,
                ask=ask,
                mark=mark,
                volume=row.get('volume'),
                open_interest=row.get('openInterest'),
                implied_volatility=iv,
                delta=Decimal(str(greeks.get('delta', 0))) if greeks else None,
                gamma=Decimal(str(greeks.get('gamma', 0))) if greeks else None,
                theta=Decimal(str(greeks.get('theta', 0))) if greeks else None,
                vega=Decimal(str(greeks.get('vega', 0))) if greeks else None,
                rho=Decimal(str(greeks.get('rho', 0))) if greeks else None,
                in_the_money=in_the_money,
                intrinsic_value=intrinsic,
                extrinsic_value=extrinsic,
                break_even=strike + mark if contract_type == 'call' else strike - mark,
                probability_itm=Decimal(str(abs(greeks.get('delta', 0)))) if greeks else None
            )

            return contract

        except Exception as e:
            logger.error(f"Error creating contract: {str(e)}")
            return None

    @staticmethod
    def calculate_greeks(S, K, T, r, sigma, option_type='call'):
        """
        Calculate option Greeks using Black-Scholes model.

        Args:
            S: Stock price
            K: Strike price
            T: Time to expiration (years)
            r: Risk-free rate
            sigma: Volatility (IV)
            option_type: 'call' or 'put'

        Returns:
            dict: {'delta', 'gamma', 'theta', 'vega', 'rho'}
        """
        if T <= 0 or sigma <= 0:
            return {}

        try:
            # Calculate d1 and d2
            d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
            d2 = d1 - sigma * np.sqrt(T)

            # Delta
            if option_type == 'call':
                delta = norm.cdf(d1)
            else:  # put
                delta = -norm.cdf(-d1)

            # Gamma (same for calls and puts)
            gamma = norm.pdf(d1) / (S * sigma * np.sqrt(T))

            # Theta
            if option_type == 'call':
                theta = (-S * norm.pdf(d1) * sigma / (2 * np.sqrt(T))
                        - r * K * np.exp(-r * T) * norm.cdf(d2)) / 365
            else:  # put
                theta = (-S * norm.pdf(d1) * sigma / (2 * np.sqrt(T))
                        + r * K * np.exp(-r * T) * norm.cdf(-d2)) / 365

            # Vega (same for calls and puts)
            vega = S * norm.pdf(d1) * np.sqrt(T) / 100  # Per 1% change in IV

            # Rho
            if option_type == 'call':
                rho = K * T * np.exp(-r * T) * norm.cdf(d2) / 100
            else:  # put
                rho = -K * T * np.exp(-r * T) * norm.cdf(-d2) / 100

            return {
                'delta': float(delta),
                'gamma': float(gamma),
                'theta': float(theta),
                'vega': float(vega),
                'rho': float(rho)
            }

        except Exception as e:
            logger.error(f"Error calculating Greeks: {str(e)}")
            return {}

    @staticmethod
    def generate_iv_surface(ticker):
        """
        Generate IV surface for visualization.

        Args:
            ticker: Stock ticker

        Returns:
            dict: {'success': bool, 'surface_id': int, 'data': dict}
        """
        from stocks.models import Stock, OptionsChain, OptionsContract, ImpliedVolatilitySurface

        try:
            stock = Stock.objects.get(ticker=ticker.upper())
        except Stock.DoesNotExist:
            return {'success': False, 'error': f'Stock {ticker} not found'}

        # Get current chain
        chain = OptionsChain.objects.filter(stock=stock, is_current=True).first()
        if not chain:
            return {'success': False, 'error': 'No options chain available. Fetch chain first.'}

        # Get all contracts with IV
        contracts = OptionsContract.objects.filter(
            chain=chain,
            implied_volatility__isnull=False
        ).order_by('expiration', 'strike')

        if not contracts.exists():
            return {'success': False, 'error': 'No IV data available'}

        # Group by expiration
        expirations = sorted(list(set(contracts.values_list('expiration', flat=True))))
        strikes = sorted(list(set(contracts.values_list('strike', flat=True))))

        # Build IV grids
        call_iv_grid = []
        put_iv_grid = []

        for exp in expirations:
            call_row = []
            put_row = []

            for strike in strikes:
                # Get call IV
                call_contract = contracts.filter(
                    expiration=exp,
                    strike=strike,
                    contract_type='call'
                ).first()
                call_row.append(float(call_contract.implied_volatility) if call_contract and call_contract.implied_volatility else None)

                # Get put IV
                put_contract = contracts.filter(
                    expiration=exp,
                    strike=strike,
                    contract_type='put'
                ).first()
                put_row.append(float(put_contract.implied_volatility) if put_contract and put_contract.implied_volatility else None)

            call_iv_grid.append(call_row)
            put_iv_grid.append(put_row)

        # Calculate statistics
        all_ivs = [float(c.implied_volatility) for c in contracts if c.implied_volatility]
        avg_iv = np.mean(all_ivs) if all_ivs else 0
        min_iv = np.min(all_ivs) if all_ivs else 0
        max_iv = np.max(all_ivs) if all_ivs else 0

        # Find ATM IV (closest to current price)
        atm_contracts = contracts.filter(
            expiration=expirations[0] if expirations else None
        ).order_by('strike')

        closest_strike = min(
            atm_contracts.values_list('strike', flat=True),
            key=lambda x: abs(float(x) - float(chain.underlying_price)),
            default=None
        )

        atm_call = contracts.filter(
            expiration=expirations[0] if expirations else None,
            strike=closest_strike,
            contract_type='call'
        ).first()

        atm_iv = float(atm_call.implied_volatility) if atm_call and atm_call.implied_volatility else avg_iv

        # Calculate put/call IV ratio
        avg_put_iv = np.mean([float(c.implied_volatility) for c in contracts.filter(contract_type='put') if c.implied_volatility])
        avg_call_iv = np.mean([float(c.implied_volatility) for c in contracts.filter(contract_type='call') if c.implied_volatility])
        pc_ratio = avg_put_iv / avg_call_iv if avg_call_iv > 0 else 1.0

        # Create surface data structure
        surface_data = {
            'expirations': [exp.isoformat() for exp in expirations],
            'strikes': [float(s) for s in strikes],
            'call_iv': call_iv_grid,
            'put_iv': put_iv_grid
        }

        # Save surface
        surface = ImpliedVolatilitySurface.objects.create(
            stock=stock,
            snapshot_date=chain.snapshot_date,
            snapshot_time=chain.snapshot_time,
            underlying_price=chain.underlying_price,
            surface_data=surface_data,
            avg_iv=Decimal(str(avg_iv)),
            min_iv=Decimal(str(min_iv)),
            max_iv=Decimal(str(max_iv)),
            atm_iv=Decimal(str(atm_iv)),
            put_call_iv_ratio=Decimal(str(pc_ratio))
        )

        logger.info(f"Generated IV surface for {ticker}")

        return {
            'success': True,
            'surface_id': surface.id,
            'data': surface_data,
            'stats': {
                'avg_iv': avg_iv,
                'min_iv': min_iv,
                'max_iv': max_iv,
                'atm_iv': atm_iv,
                'put_call_ratio': pc_ratio
            }
        }

    @staticmethod
    def calculate_options_analytics(ticker):
        """
        Calculate daily options analytics summary.

        Args:
            ticker: Stock ticker

        Returns:
            dict: Analytics summary
        """
        from stocks.models import Stock, OptionsChain, OptionsContract, OptionsAnalytics

        try:
            stock = Stock.objects.get(ticker=ticker.upper())
        except Stock.DoesNotExist:
            return {'success': False, 'error': f'Stock {ticker} not found'}

        # Get current chain
        chain = OptionsChain.objects.filter(stock=stock, is_current=True).first()
        if not chain:
            return {'success': False, 'error': 'No options chain available'}

        contracts = OptionsContract.objects.filter(chain=chain)

        # Calculate volume metrics
        total_call_vol = contracts.filter(contract_type='call', volume__isnull=False).aggregate(
            total=models.Sum('volume'))['total'] or 0
        total_put_vol = contracts.filter(contract_type='put', volume__isnull=False).aggregate(
            total=models.Sum('volume'))['total'] or 0

        pc_vol_ratio = total_put_vol / total_call_vol if total_call_vol > 0 else 0

        # Calculate OI metrics
        total_call_oi = contracts.filter(contract_type='call', open_interest__isnull=False).aggregate(
            total=models.Sum('open_interest'))['total'] or 0
        total_put_oi = contracts.filter(contract_type='put', open_interest__isnull=False).aggregate(
            total=models.Sum('open_interest'))['total'] or 0

        pc_oi_ratio = total_put_oi / total_call_oi if total_call_oi > 0 else 0

        # Calculate IV metrics
        call_ivs = [float(c.implied_volatility) for c in contracts.filter(contract_type='call', implied_volatility__isnull=False)]
        put_ivs = [float(c.implied_volatility) for c in contracts.filter(contract_type='put', implied_volatility__isnull=False)]

        avg_call_iv = np.mean(call_ivs) if call_ivs else None
        avg_put_iv = np.mean(put_ivs) if put_ivs else None

        # Find most active strikes
        most_active_call = contracts.filter(contract_type='call').order_by('-volume').first()
        most_active_put = contracts.filter(contract_type='put').order_by('-volume').first()

        # Create/update analytics
        analytics, created = OptionsAnalytics.objects.update_or_create(
            stock=stock,
            date=chain.snapshot_date,
            defaults={
                'total_call_volume': total_call_vol,
                'total_put_volume': total_put_vol,
                'put_call_volume_ratio': Decimal(str(pc_vol_ratio)),
                'total_call_oi': total_call_oi,
                'total_put_oi': total_put_oi,
                'put_call_oi_ratio': Decimal(str(pc_oi_ratio)),
                'avg_call_iv': Decimal(str(avg_call_iv)) if avg_call_iv else None,
                'avg_put_iv': Decimal(str(avg_put_iv)) if avg_put_iv else None,
                'most_active_call_strike': most_active_call.strike if most_active_call else None,
                'most_active_put_strike': most_active_put.strike if most_active_put else None,
            }
        )

        logger.info(f"Calculated options analytics for {ticker}")

        return {
            'success': True,
            'analytics_id': analytics.id,
            'metrics': {
                'total_call_volume': total_call_vol,
                'total_put_volume': total_put_vol,
                'put_call_volume_ratio': float(pc_vol_ratio),
                'total_call_oi': total_call_oi,
                'total_put_oi': total_put_oi,
                'put_call_oi_ratio': float(pc_oi_ratio),
                'avg_call_iv': avg_call_iv,
                'avg_put_iv': avg_put_iv,
            }
        }
