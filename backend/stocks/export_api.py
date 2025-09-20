from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.http import HttpResponse
from django.utils import timezone
from django.core.cache import cache
import json

from .models import Stock, UserPortfolio, PortfolioHolding
from .api_views import stock_list_api, screeners_export_csv_api


@api_view(['GET'])
@permission_classes([AllowAny])
def export_stocks_csv_api(request):
    # Reuse stock_list_api to apply filters; then build CSV
    resp = stock_list_api(request)
    payload = getattr(resp, 'data', {}) or {}
    data = payload.get('data') or payload.get('stocks') or []
    headers = ["Ticker","Company","Price","Change %","Volume","Market Cap","Exchange"]
    lines = [",".join(headers)]
    for st in data:
        ticker = str(st.get('ticker') or st.get('symbol') or '-')
        company = str(st.get('company_name') or st.get('name') or '').replace(',', ' ')
        price = f"{float(st.get('current_price') or 0):.2f}"
        chg = f"{float(st.get('price_change_percent') or st.get('change_percent') or 0):.2f}"
        vol = str(int(st.get('volume') or 0))
        cap = str(int(float(st.get('market_cap') or 0)))
        exch = str(st.get('exchange') or '')
        lines.append(
            ",".join([ticker, company, price, chg, vol, cap, exch])
        )
    csv_content = "\n".join(lines)
    response = HttpResponse(csv_content, content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="stocks_export.csv"'
    return response


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_portfolio_csv_api(request):
    portfolios = UserPortfolio.objects.filter(user=request.user)
    holdings = PortfolioHolding.objects.filter(portfolio__in=portfolios).select_related('stock', 'portfolio')
    headers = ["Portfolio","Ticker","Shares","Avg Cost","Current Price","Market Value","Unrealized P/L","P/L %"]
    lines = [",".join(headers)]
    for h in holdings:
        mv = float(h.market_value or (h.shares * (h.stock.current_price or h.current_price or 0)))
        u = float(h.unrealized_gain_loss or (mv - float(h.shares * h.average_cost)))
        up = float(h.unrealized_gain_loss_percent or (u / float(h.shares * h.average_cost) * 100 if h.average_cost else 0))
        lines.append(
            ",".join([
                h.portfolio.name,
                h.stock.ticker,
                f"{float(h.shares):.4f}",
                f"{float(h.average_cost):.4f}",
                f"{float(h.stock.current_price or h.current_price or 0):.4f}",
                f"{mv:.2f}",
                f"{u:.2f}",
                f"{up:.2f}"
            ])
        )
    csv_content = "\n".join(lines)
    response = HttpResponse(csv_content, content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="portfolio_export.csv"'
    return response


@api_view(['GET'])
@permission_classes([AllowAny])
def export_screener_results_csv_api(request):
    # Accept screener_id as query param and delegate to existing exporter
    screener_id = request.GET.get('screener_id')
    if not screener_id:
        return Response({'success': False, 'error': 'screener_id is required'}, status=400)
    return screeners_export_csv_api(request, screener_id)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_watchlist_csv_api(request):
    # Expect watchlist_id param and reuse service logic via ORM
    from .models import UserWatchlist, WatchlistItem
    wid = request.GET.get('watchlist_id')
    if not wid:
        return Response({'success': False, 'error': 'watchlist_id is required'}, status=400)
    try:
        w = UserWatchlist.objects.get(id=wid, user=request.user)
    except UserWatchlist.DoesNotExist:
        return Response({'success': False, 'error': 'Watchlist not found'}, status=404)
    headers = ["Ticker","Added Price","Current Price","Change","Change %","Notes"]
    lines = [",".join(headers)]
    for it in w.items.select_related('stock').all():
        lines.append(
            ",".join([
                it.stock.ticker,
                f"{float(it.added_price):.4f}",
                f"{float(it.current_price):.4f}",
                f"{float(it.price_change):.4f}",
                f"{float(it.price_change_percent):.4f}",
                (it.notes or '').replace(',', ' ')
            ])
        )
    csv_content = "\n".join(lines)
    response = HttpResponse(csv_content, content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="watchlist_{w.id}.csv"'
    return response


# Custom reports (cache-backed)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reports_custom_create_api(request):
    body = getattr(request, 'data', None) or {}
    report_type = (body.get('type') or 'portfolio_summary').strip()
    report_id = f"RPT-{timezone.now().strftime('%Y%m%d%H%M%S')}-{request.user.id}"

    content = ""
    if report_type == 'portfolio_summary':
        # Simple CSV summary
        portfolios = UserPortfolio.objects.filter(user=request.user)
        headers = ["Portfolio","Total Value","Total Cost","Total Return","Return %"]
        lines = [",".join(headers)]
        for p in portfolios:
            lines.append(
                ",".join([
                    p.name,
                    f"{float(p.total_value):.2f}",
                    f"{float(p.total_cost):.2f}",
                    f"{float(p.total_return):.2f}",
                    f"{float(p.total_return_percent):.2f}"
                ])
            )
        content = "\n".join(lines)
    else:
        # Generic JSON echo
        content = json.dumps({'message': 'Custom report', 'type': report_type})

    cache.set(report_id, content, timeout=60 * 60 * 24)
    return Response({'success': True, 'report_id': report_id})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def reports_download_api(request, report_id: str):
    content = cache.get(report_id)
    if not content:
        return Response({'success': False, 'error': 'Report not found or expired'}, status=404)
    # Heuristic: CSV if has commas and newlines, else JSON
    is_csv = "," in content or "\n" in content
    ct = 'text/csv' if is_csv else 'application/json'
    response = HttpResponse(content, content_type=ct)
    response['Content-Disposition'] = f'attachment; filename="{report_id}.{"csv" if is_csv else "json"}"'
    return response

