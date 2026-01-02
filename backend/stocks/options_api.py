"""
Options Analytics API Endpoints - REAL-TIME (No Caching)
RESTful API for real-time options data and Greeks calculations.
Pro Tier Feature - MVP2 v3.4

Per user requirements: Always fetch fresh data from yfinance for better UX.
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from stocks.services.options_data_service import OptionsDataService


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_option_chain(request, ticker):
    """
    Get REAL-TIME option chain with calculated Greeks (no caching).

    URL: /api/stocks/options/<ticker>/chain/
    Query params:
    - expiration: Optional specific expiration date filter (YYYY-MM-DD)

    Returns:
        Complete option chain with Greeks for all expirations
    """
    ticker = ticker.upper()

    try:
        # Fetch real-time option chain
        chain_data = OptionsDataService.fetch_option_chain_realtime(ticker)

        if 'error' in chain_data:
            return Response({
                'success': False,
                'error': chain_data['error']
            }, status=status.HTTP_400_BAD_REQUEST)

        # Filter by expiration if requested
        expiration_filter = request.GET.get('expiration')
        if expiration_filter:
            chain_data['chains'] = [
                chain for chain in chain_data['chains']
                if chain['expiration_date'] == expiration_filter
            ]

        return Response({
            'success': True,
            'data': chain_data
        })

    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_greeks_surface(request, ticker):
    """
    Get Greeks surface for a specific expiration (REAL-TIME).

    URL: /api/stocks/options/<ticker>/greeks/
    Query params:
    - expiration: Expiration date (YYYY-MM-DD) - required

    Returns:
        Greeks vs Strike data for visualization
    """
    ticker = ticker.upper()
    expiration_date = request.GET.get('expiration')

    if not expiration_date:
        return Response({
            'success': False,
            'error': 'Expiration date is required'
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        surface_data = OptionsDataService.get_greeks_surface(ticker, expiration_date)

        if 'error' in surface_data:
            return Response({
                'success': False,
                'error': surface_data['error']
            }, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            'success': True,
            'data': surface_data
        })

    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_iv_surface(request, ticker):
    """
    Get implied volatility surface from REAL-TIME data.

    URL: /api/stocks/options/<ticker>/iv-surface/

    Returns:
        IV surface data for 3D visualization
    """
    ticker = ticker.upper()

    try:
        iv_data = OptionsDataService.get_iv_surface_realtime(ticker)

        if 'error' in iv_data:
            return Response({
                'success': False,
                'error': iv_data['error']
            }, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            'success': True,
            'data': iv_data
        })

    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def calculate_greeks(request):
    """
    Calculate theoretical option price and Greeks using Black-Scholes.

    POST /api/stocks/options/calculator/
    Body:
    - ticker: Stock ticker (required)
    - strike: Strike price (required)
    - expiration: Expiration date YYYY-MM-DD (required)
    - volatility: Implied volatility (required, decimal 0-5)
    - option_type: 'call' or 'put' (required)

    Returns:
        Theoretical price and all Greeks
    """
    try:
        ticker = request.data.get('ticker', '').upper()
        strike = request.data.get('strike')
        expiration = request.data.get('expiration')
        volatility = request.data.get('volatility')
        option_type = request.data.get('option_type', 'call').lower()

        # Validate inputs
        if not all([ticker, strike, expiration, volatility, option_type]):
            return Response({
                'success': False,
                'error': 'Missing required parameters: ticker, strike, expiration, volatility, option_type'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            strike = float(strike)
            volatility = float(volatility)
        except ValueError:
            return Response({
                'success': False,
                'error': 'Invalid strike or volatility value'
            }, status=status.HTTP_400_BAD_REQUEST)

        if option_type not in ['call', 'put']:
            return Response({
                'success': False,
                'error': 'option_type must be "call" or "put"'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Calculate price and Greeks
        result = OptionsDataService.calculate_theoretical_price(
            ticker, strike, expiration, volatility, option_type
        )

        if 'error' in result:
            return Response({
                'success': False,
                'error': result['error']
            }, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            'success': True,
            'data': result
        })

    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_expirations(request, ticker):
    """
    Get available expiration dates for a ticker.

    URL: /api/stocks/options/<ticker>/expirations/

    Returns:
        List of available expiration dates
    """
    import yfinance as yf

    ticker = ticker.upper()

    try:
        stock = yf.Ticker(ticker)
        expirations = stock.options

        if not expirations:
            return Response({
                'success': False,
                'error': 'No options data available for this ticker'
            }, status=status.HTTP_404_NOT_FOUND)

        return Response({
            'success': True,
            'ticker': ticker,
            'expirations': list(expirations)
        })

    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
