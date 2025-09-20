from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.utils import timezone
from django.core.cache import cache
from decimal import Decimal

from .models import UserPortfolio, PortfolioHolding, PortfolioAnalytics, Stock
from .portfolio_api_updated import portfolio_api as base_portfolio_api


def _get_user(request):
    user = getattr(request, 'user', None)
    if user and getattr(user, 'is_authenticated', False):
        return user
    return None


def _format_decimal(d):
    try:
        return float(d)
    except Exception:
        return 0.0


@api_view(['GET'])
@permission_classes([AllowAny])
def portfolio_analytics_api(request):
    """
    GET /api/portfolio/analytics/
    Returns aggregate portfolio analytics for the authenticated user.
    """
    user = _get_user(request)
    if not user:
        return Response({'success': False, 'error': 'Authentication required'}, status=401)

    # Aggregate across all holdings for the user
    holdings = PortfolioHolding.objects.filter(portfolio__user=user).select_related('stock', 'portfolio')

    total_value = Decimal('0')
    total_cost = Decimal('0')
    day_change = Decimal('0')

    # Sector allocation without adding a DB field: best-effort using getattr fallback
    sector_alloc = {}

    for h in holdings:
        current_price = h.stock.current_price or h.current_price or Decimal('0')
        position_value = Decimal(h.shares) * Decimal(current_price or 0)
        cost_basis = Decimal(h.shares) * Decimal(h.average_cost)
        total_value += position_value
        total_cost += cost_basis

        # Day change from price_change_today if available
        day_delta = (h.stock.price_change_today or Decimal('0')) * Decimal(h.shares)
        day_change += Decimal(day_delta or 0)

        sector = getattr(h.stock, 'sector', None) or 'Unspecified'
        s = sector_alloc.setdefault(sector, {'value': Decimal('0'), 'count': 0})
        s['value'] += position_value
        s['count'] += 1

    total_gain_loss = total_value - total_cost
    total_gain_loss_percent = (total_gain_loss / total_cost * 100) if total_cost > 0 else Decimal('0')
    day_change_percent = (day_change / total_value * 100) if total_value > 0 else Decimal('0')

    # Normalize sector percentages
    sector_allocation = {}
    for name, info in sector_alloc.items():
        pct = float((info['value'] / total_value * 100) if total_value > 0 else 0)
        sector_allocation[name] = {
            'percentage': round(pct, 2),
            'value': round(float(info['value']), 2),
            'count': info['count']
        }

    risk_metrics = {
        'positions': holdings.count(),
        'concentration_top': sorted([float(v['value']) for v in sector_alloc.values()], reverse=True)[:3]
    }

    return Response({
        'success': True,
        'total_value': round(float(total_value), 2),
        'total_gain_loss': round(float(total_gain_loss), 2),
        'total_gain_loss_percent': round(float(total_gain_loss_percent), 2),
        'day_change': round(float(day_change), 2),
        'day_change_percent': round(float(day_change_percent), 2),
        'sector_allocation': sector_allocation,
        'risk_metrics': risk_metrics,
        'timestamp': timezone.now().isoformat()
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def portfolio_sector_allocation_api(request):
    """
    GET /api/portfolio/sector-allocation/
    Returns sector allocation (without adding DB sector field).
    """
    user = _get_user(request)
    if not user:
        return Response({'success': False, 'error': 'Authentication required'}, status=401)

    holdings = PortfolioHolding.objects.filter(portfolio__user=user).select_related('stock', 'portfolio')
    total_value = Decimal('0')
    sector_alloc = {}
    for h in holdings:
        current_price = h.stock.current_price or h.current_price or Decimal('0')
        position_value = Decimal(h.shares) * Decimal(current_price or 0)
        total_value += position_value
        sector = getattr(h.stock, 'sector', None) or 'Unspecified'
        s = sector_alloc.setdefault(sector, {'value': Decimal('0'), 'count': 0})
        s['value'] += position_value
        s['count'] += 1

    result = {}
    for name, info in sector_alloc.items():
        pct = float((info['value'] / total_value * 100) if total_value > 0 else 0)
        result[name] = {'percentage': round(pct, 2), 'value': round(float(info['value']), 2), 'count': info['count']}

    return Response({'success': True, 'allocation': result, 'timestamp': timezone.now().isoformat()})


@api_view(['GET'])
@permission_classes([AllowAny])
def portfolio_dividend_tracking_api(request):
    """
    GET /api/portfolio/dividend-tracking/
    Returns dividend projections based on dividend_yield and current prices.
    """
    user = _get_user(request)
    if not user:
        return Response({'success': False, 'error': 'Authentication required'}, status=401)

    holdings = PortfolioHolding.objects.filter(portfolio__user=user).select_related('stock', 'portfolio')
    projection_total = Decimal('0')
    items = []
    for h in holdings:
        price = Decimal(h.stock.current_price or h.current_price or 0)
        dy = Decimal(h.stock.dividend_yield or 0)
        annual_div = (Decimal(h.shares) * price * dy / Decimal('100')) if dy else Decimal('0')
        projection_total += annual_div
        items.append({
            'ticker': h.stock.ticker,
            'shares': float(h.shares),
            'current_price': float(price),
            'dividend_yield': float(dy),
            'projected_annual_dividend': round(float(annual_div), 2)
        })

    return Response({
        'success': True,
        'projection_total': round(float(projection_total), 2),
        'items': items,
        'history': [],
        'timestamp': timezone.now().isoformat()
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def portfolio_with_analytics_api(request):
    """
    GET /api/portfolio/ (enhanced): merge baseline holdings with analytics summary fields.
    """
    resp = base_portfolio_api(request)
    try:
        payload = getattr(resp, 'data', {}) or {}
        if not (getattr(request, 'user', None) and request.user.is_authenticated):
            return resp
        # Compute analytics summary
        holdings = PortfolioHolding.objects.filter(portfolio__user=request.user).select_related('stock')
        total_value = sum((h.shares * (h.stock.current_price or h.current_price or 0)) for h in holdings)
        total_cost = sum((h.shares * h.average_cost) for h in holdings)
        total_gain_loss = total_value - total_cost
        total_gain_loss_percent = (total_gain_loss / total_cost * 100) if total_cost > 0 else 0
        day_change = sum(((h.stock.price_change_today or 0) * h.shares) for h in holdings)
        day_change_percent = (day_change / total_value * 100) if total_value > 0 else 0
        payload['summary'] = {
            **(payload.get('summary') or {}),
            'total_value': round(float(total_value), 2),
            'total_gain_loss': round(float(total_gain_loss), 2),
            'total_gain_loss_percent': round(float(total_gain_loss_percent), 2),
            'day_change': round(float(day_change), 2),
            'day_change_percent': round(float(day_change_percent), 2),
        }
        resp.data = payload
        return resp
    except Exception:
        return resp

