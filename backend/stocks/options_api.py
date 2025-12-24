"""
Options Analytics API Endpoints
RESTful API for options chains, Greeks, IV surfaces, and analytics.
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.core.paginator import Paginator

from stocks.models import (
    Stock, OptionsChain, OptionsContract, ImpliedVolatilitySurface,
    OptionsScreenerResult, OptionsAnalytics, OptionsWatchlist, OptionsWatchlistItem
)
from stocks.services.options_service import OptionsService
from datetime import datetime, timedelta


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_options_chain(request, ticker):
    """
    Get options chain for a ticker with Greeks.

    Query params:
    - expiration: Filter by specific expiration date (YYYY-MM-DD)
    - min_dte: Minimum days to expiration
    - max_dte: Maximum days to expiration
    - min_volume: Minimum volume filter
    - moneyness: Filter by moneyness (itm, otm, atm)
    - force_refresh: Force fetch from yfinance (default: false)
    """
    ticker = ticker.upper()
    force_refresh = request.GET.get('force_refresh', 'false').lower() == 'true'

    # Fetch/update options chain
    result = OptionsService.fetch_options_chain(ticker, force_refresh=force_refresh)

    if not result['success']:
        return Response({
            'success': False,
            'error': result['message']
        }, status=status.HTTP_400_BAD_REQUEST)

    # Get the chain
    try:
        chain = OptionsChain.objects.get(id=result['chain_id'])
    except OptionsChain.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Options chain not found'
        }, status=status.HTTP_404_NOT_FOUND)

    # Build query for contracts
    contracts = OptionsContract.objects.filter(chain=chain)

    # Apply filters
    expiration_filter = request.GET.get('expiration')
    if expiration_filter:
        contracts = contracts.filter(expiration=expiration_filter)

    min_dte = request.GET.get('min_dte')
    if min_dte:
        contracts = contracts.filter(dte__gte=int(min_dte))

    max_dte = request.GET.get('max_dte')
    if max_dte:
        contracts = contracts.filter(dte__lte=int(max_dte))

    min_volume = request.GET.get('min_volume')
    if min_volume:
        contracts = contracts.filter(volume__gte=int(min_volume))

    moneyness = request.GET.get('moneyness')
    if moneyness:
        if moneyness.lower() == 'itm':
            contracts = contracts.filter(in_the_money=True)
        elif moneyness.lower() == 'otm':
            contracts = contracts.filter(in_the_money=False)
        elif moneyness.lower() == 'atm':
            # ATM defined as within 2% of current price
            spot_price = float(chain.underlying_price)
            lower = spot_price * 0.98
            upper = spot_price * 1.02
            contracts = contracts.filter(strike__gte=lower, strike__lte=upper)

    # Serialize contracts
    contracts_data = []
    for contract in contracts:
        contracts_data.append({
            'contract_symbol': contract.contract_symbol,
            'type': contract.contract_type,
            'strike': float(contract.strike),
            'expiration': contract.expiration.isoformat(),
            'dte': contract.dte,
            'last_price': float(contract.last_price) if contract.last_price else None,
            'bid': float(contract.bid) if contract.bid else None,
            'ask': float(contract.ask) if contract.ask else None,
            'mark': float(contract.mark) if contract.mark else None,
            'volume': contract.volume,
            'open_interest': contract.open_interest,
            'implied_volatility': float(contract.implied_volatility) if contract.implied_volatility else None,
            'greeks': {
                'delta': float(contract.delta) if contract.delta else None,
                'gamma': float(contract.gamma) if contract.gamma else None,
                'theta': float(contract.theta) if contract.theta else None,
                'vega': float(contract.vega) if contract.vega else None,
                'rho': float(contract.rho) if contract.rho else None,
            },
            'in_the_money': contract.in_the_money,
            'intrinsic_value': float(contract.intrinsic_value) if contract.intrinsic_value else None,
            'extrinsic_value': float(contract.extrinsic_value) if contract.extrinsic_value else None,
        })

    return Response({
        'success': True,
        'ticker': ticker,
        'underlying_price': float(chain.underlying_price),
        'expirations': chain.available_expirations,
        'total_contracts': chain.total_contracts,
        'fetch_timestamp': chain.fetch_timestamp.isoformat(),
        'contracts': contracts_data,
        'count': len(contracts_data)
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_iv_surface(request, ticker):
    """
    Get implied volatility surface for visualization.

    Returns 3D surface data with strikes, expirations, and IV values.
    """
    ticker = ticker.upper()

    # Check for recent IV surface (within 1 hour)
    one_hour_ago = datetime.now() - timedelta(hours=1)
    try:
        surface = ImpliedVolatilitySurface.objects.filter(
            ticker=ticker,
            fetch_timestamp__gte=one_hour_ago
        ).latest('fetch_timestamp')
    except ImpliedVolatilitySurface.DoesNotExist:
        # Generate new surface
        result = OptionsService.generate_iv_surface(ticker)

        if not result['success']:
            return Response({
                'success': False,
                'error': result['message']
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            surface = ImpliedVolatilitySurface.objects.get(id=result['surface_id'])
        except ImpliedVolatilitySurface.DoesNotExist:
            return Response({
                'success': False,
                'error': 'IV surface not found'
            }, status=status.HTTP_404_NOT_FOUND)

    return Response({
        'success': True,
        'ticker': ticker,
        'underlying_price': float(surface.underlying_price),
        'surface_data': surface.surface_data,
        'statistics': {
            'avg_iv': float(surface.avg_iv) if surface.avg_iv else None,
            'min_iv': float(surface.min_iv) if surface.min_iv else None,
            'max_iv': float(surface.max_iv) if surface.max_iv else None,
            'atm_iv': float(surface.atm_iv) if surface.atm_iv else None,
            'put_call_iv_ratio': float(surface.put_call_iv_ratio) if surface.put_call_iv_ratio else None,
        },
        'fetch_timestamp': surface.fetch_timestamp.isoformat()
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_options_analytics(request, ticker):
    """
    Get daily options analytics summary.

    Includes volume, open interest, IV metrics, and put/call ratios.
    """
    ticker = ticker.upper()

    # Get or calculate today's analytics
    result = OptionsService.calculate_options_analytics(ticker)

    if not result['success']:
        return Response({
            'success': False,
            'error': result['message']
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        analytics = OptionsAnalytics.objects.get(id=result['analytics_id'])
    except OptionsAnalytics.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Analytics not found'
        }, status=status.HTTP_404_NOT_FOUND)

    return Response({
        'success': True,
        'ticker': ticker,
        'date': analytics.date.isoformat(),
        'underlying_price': float(analytics.underlying_price),
        'volume': {
            'total_call_volume': analytics.total_call_volume,
            'total_put_volume': analytics.total_put_volume,
            'total_volume': analytics.total_volume,
            'put_call_volume_ratio': float(analytics.put_call_volume_ratio) if analytics.put_call_volume_ratio else None,
        },
        'open_interest': {
            'total_call_oi': analytics.total_call_oi,
            'total_put_oi': analytics.total_put_oi,
            'total_oi': analytics.total_oi,
            'put_call_oi_ratio': float(analytics.put_call_oi_ratio) if analytics.put_call_oi_ratio else None,
        },
        'implied_volatility': {
            'avg_call_iv': float(analytics.avg_call_iv) if analytics.avg_call_iv else None,
            'avg_put_iv': float(analytics.avg_put_iv) if analytics.avg_put_iv else None,
            'avg_iv': float(analytics.avg_iv) if analytics.avg_iv else None,
            'atm_iv': float(analytics.atm_iv) if analytics.atm_iv else None,
            'iv_rank': float(analytics.iv_rank) if analytics.iv_rank else None,
            'iv_percentile': float(analytics.iv_percentile) if analytics.iv_percentile else None,
        },
        'greeks': {
            'net_delta': float(analytics.net_delta) if analytics.net_delta else None,
            'net_gamma': float(analytics.net_gamma) if analytics.net_gamma else None,
        },
        'max_pain': {
            'max_pain_strike': float(analytics.max_pain_strike) if analytics.max_pain_strike else None,
            'distance_to_max_pain': float(analytics.distance_to_max_pain_pct) if analytics.distance_to_max_pain_pct else None,
        }
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def options_screener(request, screener_type):
    """
    Get options screener results.

    Types: unusual_volume, high_iv, earnings_plays, cheap_options

    Query params:
    - limit: Number of results (default: 50, max: 200)
    """
    valid_types = ['unusual_volume', 'high_iv', 'earnings_plays', 'cheap_options']
    if screener_type not in valid_types:
        return Response({
            'success': False,
            'error': f'Invalid screener type. Valid types: {valid_types}'
        }, status=status.HTTP_400_BAD_REQUEST)

    limit = min(int(request.GET.get('limit', 50)), 200)

    # Get recent screener results (within 1 hour)
    one_hour_ago = datetime.now() - timedelta(hours=1)
    results = OptionsScreenerResult.objects.filter(
        screener_type=screener_type,
        fetch_timestamp__gte=one_hour_ago
    ).order_by('-rank_score')[:limit]

    # If no recent results, trigger a screener run
    if not results.exists():
        # TODO: Implement screener calculation in OptionsService
        return Response({
            'success': False,
            'error': 'No recent screener results available. Please try again in a few minutes.'
        }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

    results_data = []
    for result in results:
        results_data.append({
            'ticker': result.ticker,
            'contract_symbol': result.contract_symbol,
            'contract_type': result.contract_type,
            'strike': float(result.strike),
            'expiration': result.expiration.isoformat(),
            'dte': result.dte,
            'rank_score': float(result.rank_score),
            'metrics': result.metrics,
            'reason': result.reason,
            'fetch_timestamp': result.fetch_timestamp.isoformat()
        })

    return Response({
        'success': True,
        'screener_type': screener_type,
        'results': results_data,
        'count': len(results_data)
    })


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def options_watchlist(request):
    """
    Get or create user's options watchlist.

    GET: List all watchlists
    POST: Create new watchlist
        - name: Watchlist name
        - description: Optional description
    """
    if request.method == 'GET':
        watchlists = OptionsWatchlist.objects.filter(
            user=request.user
        ).order_by('-created_at')

        watchlists_data = []
        for wl in watchlists:
            watchlists_data.append({
                'id': wl.id,
                'name': wl.name,
                'description': wl.description,
                'items_count': wl.items.count(),
                'created_at': wl.created_at.isoformat(),
                'last_updated': wl.last_updated.isoformat()
            })

        return Response({
            'success': True,
            'watchlists': watchlists_data,
            'count': len(watchlists_data)
        })

    else:  # POST
        name = request.data.get('name')
        description = request.data.get('description', '')

        if not name:
            return Response({
                'success': False,
                'error': 'Watchlist name is required'
            }, status=status.HTTP_400_BAD_REQUEST)

        watchlist = OptionsWatchlist.objects.create(
            user=request.user,
            name=name,
            description=description
        )

        return Response({
            'success': True,
            'message': 'Watchlist created successfully',
            'watchlist_id': watchlist.id
        }, status=status.HTTP_201_CREATED)


@api_view(['GET', 'POST', 'DELETE'])
@permission_classes([IsAuthenticated])
def watchlist_items(request, watchlist_id):
    """
    Manage watchlist items.

    GET: List all items in watchlist
    POST: Add item to watchlist
        - contract_symbol: Options contract symbol
        - notes: Optional notes
    DELETE: Remove item from watchlist
        Query param: item_id
    """
    # Verify watchlist ownership
    try:
        watchlist = OptionsWatchlist.objects.get(id=watchlist_id, user=request.user)
    except OptionsWatchlist.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Watchlist not found'
        }, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        items = OptionsWatchlistItem.objects.filter(
            watchlist=watchlist
        ).select_related('contract').order_by('-added_at')

        items_data = []
        for item in items:
            contract = item.contract
            items_data.append({
                'id': item.id,
                'contract_symbol': contract.contract_symbol,
                'ticker': contract.chain.ticker,
                'type': contract.contract_type,
                'strike': float(contract.strike),
                'expiration': contract.expiration.isoformat(),
                'dte': contract.dte,
                'last_price': float(contract.last_price) if contract.last_price else None,
                'implied_volatility': float(contract.implied_volatility) if contract.implied_volatility else None,
                'notes': item.notes,
                'added_at': item.added_at.isoformat(),
                'last_checked': item.last_checked.isoformat() if item.last_checked else None
            })

        return Response({
            'success': True,
            'watchlist_id': watchlist_id,
            'items': items_data,
            'count': len(items_data)
        })

    elif request.method == 'POST':
        contract_symbol = request.data.get('contract_symbol')
        notes = request.data.get('notes', '')

        if not contract_symbol:
            return Response({
                'success': False,
                'error': 'Contract symbol is required'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            contract = OptionsContract.objects.get(contract_symbol=contract_symbol)
        except OptionsContract.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Options contract not found'
            }, status=status.HTTP_404_NOT_FOUND)

        # Check if already in watchlist
        if OptionsWatchlistItem.objects.filter(watchlist=watchlist, contract=contract).exists():
            return Response({
                'success': False,
                'error': 'Contract already in watchlist'
            }, status=status.HTTP_400_BAD_REQUEST)

        item = OptionsWatchlistItem.objects.create(
            watchlist=watchlist,
            contract=contract,
            notes=notes
        )

        return Response({
            'success': True,
            'message': 'Contract added to watchlist',
            'item_id': item.id
        }, status=status.HTTP_201_CREATED)

    else:  # DELETE
        item_id = request.query_params.get('item_id')

        if not item_id:
            return Response({
                'success': False,
                'error': 'Item ID is required'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            item = OptionsWatchlistItem.objects.get(id=item_id, watchlist=watchlist)
            item.delete()

            return Response({
                'success': True,
                'message': 'Item removed from watchlist'
            })
        except OptionsWatchlistItem.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Item not found'
            }, status=status.HTTP_404_NOT_FOUND)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_watchlist(request, watchlist_id):
    """Delete a watchlist and all its items."""
    try:
        watchlist = OptionsWatchlist.objects.get(id=watchlist_id, user=request.user)
        watchlist.delete()

        return Response({
            'success': True,
            'message': 'Watchlist deleted successfully'
        })
    except OptionsWatchlist.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Watchlist not found'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def expirations_list(request, ticker):
    """
    Get list of available expiration dates for a ticker.
    """
    ticker = ticker.upper()

    # Get most recent chain
    try:
        chain = OptionsChain.objects.filter(ticker=ticker).latest('fetch_timestamp')

        return Response({
            'success': True,
            'ticker': ticker,
            'expirations': chain.available_expirations,
            'count': len(chain.available_expirations)
        })
    except OptionsChain.DoesNotExist:
        return Response({
            'success': False,
            'error': 'No options chain found for ticker'
        }, status=status.HTTP_404_NOT_FOUND)
