"""
Enhanced Screener API - Feature 2
Allows filtering on ALL database fields including all 50+ fundamentals
"""
import json
from decimal import Decimal
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db.models import Q, F
from django.core.paginator import Paginator
from .models import Stock, StockFundamentals


def _safe_float(value):
    """Convert to float safely"""
    if value is None:
        return None
    try:
        return float(value)
    except:
        return None


# All available filter fields with metadata
FILTER_FIELDS = {
    # Basic Stock Fields
    'current_price': {'model': 'stock', 'field': 'current_price', 'type': 'number', 'label': 'Current Price'},
    'price_change_percent': {'model': 'stock', 'field': 'price_change_percent', 'type': 'number', 'label': 'Price Change %'},
    'volume': {'model': 'stock', 'field': 'volume', 'type': 'number', 'label': 'Volume'},
    'market_cap': {'model': 'stock', 'field': 'market_cap', 'type': 'number', 'label': 'Market Cap'},
    'pe_ratio_basic': {'model': 'stock', 'field': 'pe_ratio', 'type': 'number', 'label': 'P/E Ratio (Basic)'},
    'dividend_yield_basic': {'model': 'stock', 'field': 'dividend_yield', 'type': 'number', 'label': 'Dividend Yield (Basic)'},
    'week_52_high': {'model': 'stock', 'field': 'week_52_high', 'type': 'number', 'label': '52 Week High'},
    'week_52_low': {'model': 'stock', 'field': 'week_52_low', 'type': 'number', 'label': '52 Week Low'},
    'avg_volume_3mon': {'model': 'stock', 'field': 'avg_volume_3mon', 'type': 'number', 'label': 'Avg Volume (3M)'},
    'exchange': {'model': 'stock', 'field': 'exchange', 'type': 'text', 'label': 'Exchange'},
    
    # Valuation Metrics (Fundamentals)
    'pe_ratio': {'model': 'fundamentals', 'field': 'pe_ratio', 'type': 'number', 'label': 'P/E Ratio'},
    'forward_pe': {'model': 'fundamentals', 'field': 'forward_pe', 'type': 'number', 'label': 'Forward P/E'},
    'peg_ratio': {'model': 'fundamentals', 'field': 'peg_ratio', 'type': 'number', 'label': 'PEG Ratio'},
    'price_to_sales': {'model': 'fundamentals', 'field': 'price_to_sales', 'type': 'number', 'label': 'Price/Sales'},
    'price_to_book': {'model': 'fundamentals', 'field': 'price_to_book', 'type': 'number', 'label': 'Price/Book'},
    'ev_to_revenue': {'model': 'fundamentals', 'field': 'ev_to_revenue', 'type': 'number', 'label': 'EV/Revenue'},
    'ev_to_ebitda': {'model': 'fundamentals', 'field': 'ev_to_ebitda', 'type': 'number', 'label': 'EV/EBITDA'},
    'enterprise_value': {'model': 'fundamentals', 'field': 'enterprise_value', 'type': 'number', 'label': 'Enterprise Value'},
    
    # Profitability Metrics
    'gross_margin': {'model': 'fundamentals', 'field': 'gross_margin', 'type': 'number', 'label': 'Gross Margin'},
    'operating_margin': {'model': 'fundamentals', 'field': 'operating_margin', 'type': 'number', 'label': 'Operating Margin'},
    'profit_margin': {'model': 'fundamentals', 'field': 'profit_margin', 'type': 'number', 'label': 'Profit Margin'},
    'roe': {'model': 'fundamentals', 'field': 'roe', 'type': 'number', 'label': 'ROE'},
    'roa': {'model': 'fundamentals', 'field': 'roa', 'type': 'number', 'label': 'ROA'},
    'roic': {'model': 'fundamentals', 'field': 'roic', 'type': 'number', 'label': 'ROIC'},
    
    # Growth Metrics
    'revenue_growth_yoy': {'model': 'fundamentals', 'field': 'revenue_growth_yoy', 'type': 'number', 'label': 'Revenue Growth YoY'},
    'revenue_growth_3y': {'model': 'fundamentals', 'field': 'revenue_growth_3y', 'type': 'number', 'label': 'Revenue Growth 3Y CAGR'},
    'revenue_growth_5y': {'model': 'fundamentals', 'field': 'revenue_growth_5y', 'type': 'number', 'label': 'Revenue Growth 5Y CAGR'},
    'earnings_growth_yoy': {'model': 'fundamentals', 'field': 'earnings_growth_yoy', 'type': 'number', 'label': 'Earnings Growth YoY'},
    'earnings_growth_5y': {'model': 'fundamentals', 'field': 'earnings_growth_5y', 'type': 'number', 'label': 'Earnings Growth 5Y'},
    'fcf_growth_yoy': {'model': 'fundamentals', 'field': 'fcf_growth_yoy', 'type': 'number', 'label': 'FCF Growth YoY'},
    
    # Financial Health
    'current_ratio': {'model': 'fundamentals', 'field': 'current_ratio', 'type': 'number', 'label': 'Current Ratio'},
    'quick_ratio': {'model': 'fundamentals', 'field': 'quick_ratio', 'type': 'number', 'label': 'Quick Ratio'},
    'debt_to_equity': {'model': 'fundamentals', 'field': 'debt_to_equity', 'type': 'number', 'label': 'Debt/Equity'},
    'debt_to_assets': {'model': 'fundamentals', 'field': 'debt_to_assets', 'type': 'number', 'label': 'Debt/Assets'},
    'interest_coverage': {'model': 'fundamentals', 'field': 'interest_coverage', 'type': 'number', 'label': 'Interest Coverage'},
    'altman_z_score': {'model': 'fundamentals', 'field': 'altman_z_score', 'type': 'number', 'label': 'Altman Z-Score'},
    'piotroski_f_score': {'model': 'fundamentals', 'field': 'piotroski_f_score', 'type': 'number', 'label': 'Piotroski F-Score'},
    
    # Cash Flow
    'operating_cash_flow': {'model': 'fundamentals', 'field': 'operating_cash_flow', 'type': 'number', 'label': 'Operating Cash Flow'},
    'free_cash_flow': {'model': 'fundamentals', 'field': 'free_cash_flow', 'type': 'number', 'label': 'Free Cash Flow'},
    'fcf_per_share': {'model': 'fundamentals', 'field': 'fcf_per_share', 'type': 'number', 'label': 'FCF/Share'},
    'fcf_yield': {'model': 'fundamentals', 'field': 'fcf_yield', 'type': 'number', 'label': 'FCF Yield'},
    'cash_conversion': {'model': 'fundamentals', 'field': 'cash_conversion', 'type': 'number', 'label': 'Cash Conversion'},
    
    # Dividend
    'dividend_yield': {'model': 'fundamentals', 'field': 'dividend_yield', 'type': 'number', 'label': 'Dividend Yield'},
    'dividend_payout_ratio': {'model': 'fundamentals', 'field': 'dividend_payout_ratio', 'type': 'number', 'label': 'Payout Ratio'},
    'years_dividend_growth': {'model': 'fundamentals', 'field': 'years_dividend_growth', 'type': 'number', 'label': 'Years Dividend Growth'},
    
    # Fair Value Calculations
    'dcf_value': {'model': 'fundamentals', 'field': 'dcf_value', 'type': 'number', 'label': 'DCF Fair Value'},
    'epv_value': {'model': 'fundamentals', 'field': 'epv_value', 'type': 'number', 'label': 'EPV Fair Value'},
    'graham_number': {'model': 'fundamentals', 'field': 'graham_number', 'type': 'number', 'label': 'Graham Number'},
    'peg_fair_value': {'model': 'fundamentals', 'field': 'peg_fair_value', 'type': 'number', 'label': 'PEG Fair Value'},
    'relative_value_score': {'model': 'fundamentals', 'field': 'relative_value_score', 'type': 'number', 'label': 'Relative Value Score'},
    
    # Composite Scores
    'valuation_score': {'model': 'fundamentals', 'field': 'valuation_score', 'type': 'number', 'label': 'Valuation Score (0-100)'},
    'valuation_status': {'model': 'fundamentals', 'field': 'valuation_status', 'type': 'text', 'label': 'Valuation Status'},
    'recommendation': {'model': 'fundamentals', 'field': 'recommendation', 'type': 'text', 'label': 'Recommendation'},
    'strength_score': {'model': 'fundamentals', 'field': 'strength_score', 'type': 'number', 'label': 'Strength Score (0-100)'},
    'strength_grade': {'model': 'fundamentals', 'field': 'strength_grade', 'type': 'text', 'label': 'Strength Grade'},
    
    # Classification
    'sector': {'model': 'fundamentals', 'field': 'sector', 'type': 'text', 'label': 'Sector'},
    'industry': {'model': 'fundamentals', 'field': 'industry', 'type': 'text', 'label': 'Industry'},
}

# Filter operators
OPERATORS = {
    'eq': lambda f, v: Q(**{f: v}),
    'ne': lambda f, v: ~Q(**{f: v}),
    'gt': lambda f, v: Q(**{f'{f}__gt': v}),
    'gte': lambda f, v: Q(**{f'{f}__gte': v}),
    'lt': lambda f, v: Q(**{f'{f}__lt': v}),
    'lte': lambda f, v: Q(**{f'{f}__lte': v}),
    'between': lambda f, v: Q(**{f'{f}__gte': v[0], f'{f}__lte': v[1]}),
    'contains': lambda f, v: Q(**{f'{f}__icontains': v}),
    'startswith': lambda f, v: Q(**{f'{f}__istartswith': v}),
    'endswith': lambda f, v: Q(**{f'{f}__iendswith': v}),
    'in': lambda f, v: Q(**{f'{f}__in': v}),
    'isnull': lambda f, v: Q(**{f'{f}__isnull': v}),
}


@csrf_exempt
@require_http_methods(["GET"])
def get_filter_fields(request):
    """
    GET /api/screener/fields/
    
    Get all available filter fields with metadata.
    """
    fields_by_category = {
        'basic': [],
        'valuation': [],
        'profitability': [],
        'growth': [],
        'financial_health': [],
        'cash_flow': [],
        'dividend': [],
        'fair_value': [],
        'scores': [],
        'classification': [],
    }
    
    category_map = {
        'current_price': 'basic', 'price_change_percent': 'basic', 'volume': 'basic',
        'market_cap': 'basic', 'pe_ratio_basic': 'basic', 'dividend_yield_basic': 'basic',
        'week_52_high': 'basic', 'week_52_low': 'basic', 'avg_volume_3mon': 'basic', 'exchange': 'basic',
        
        'pe_ratio': 'valuation', 'forward_pe': 'valuation', 'peg_ratio': 'valuation',
        'price_to_sales': 'valuation', 'price_to_book': 'valuation', 'ev_to_revenue': 'valuation',
        'ev_to_ebitda': 'valuation', 'enterprise_value': 'valuation',
        
        'gross_margin': 'profitability', 'operating_margin': 'profitability',
        'profit_margin': 'profitability', 'roe': 'profitability', 'roa': 'profitability', 'roic': 'profitability',
        
        'revenue_growth_yoy': 'growth', 'revenue_growth_3y': 'growth', 'revenue_growth_5y': 'growth',
        'earnings_growth_yoy': 'growth', 'earnings_growth_5y': 'growth', 'fcf_growth_yoy': 'growth',
        
        'current_ratio': 'financial_health', 'quick_ratio': 'financial_health',
        'debt_to_equity': 'financial_health', 'debt_to_assets': 'financial_health',
        'interest_coverage': 'financial_health', 'altman_z_score': 'financial_health',
        'piotroski_f_score': 'financial_health',
        
        'operating_cash_flow': 'cash_flow', 'free_cash_flow': 'cash_flow',
        'fcf_per_share': 'cash_flow', 'fcf_yield': 'cash_flow', 'cash_conversion': 'cash_flow',
        
        'dividend_yield': 'dividend', 'dividend_payout_ratio': 'dividend', 'years_dividend_growth': 'dividend',
        
        'dcf_value': 'fair_value', 'epv_value': 'fair_value', 'graham_number': 'fair_value',
        'peg_fair_value': 'fair_value', 'relative_value_score': 'fair_value',
        
        'valuation_score': 'scores', 'valuation_status': 'scores', 'recommendation': 'scores',
        'strength_score': 'scores', 'strength_grade': 'scores',
        
        'sector': 'classification', 'industry': 'classification',
    }
    
    for key, meta in FILTER_FIELDS.items():
        category = category_map.get(key, 'basic')
        fields_by_category[category].append({
            'key': key,
            'label': meta['label'],
            'type': meta['type'],
            'model': meta['model']
        })
    
    return JsonResponse({
        'success': True,
        'data': {
            'fields': FILTER_FIELDS,
            'fields_by_category': fields_by_category,
            'operators': {
                'number': ['eq', 'ne', 'gt', 'gte', 'lt', 'lte', 'between', 'isnull'],
                'text': ['eq', 'ne', 'contains', 'startswith', 'endswith', 'in', 'isnull']
            },
            'total_fields': len(FILTER_FIELDS)
        }
    })


@csrf_exempt
@require_http_methods(["POST"])
def advanced_filter(request):
    """
    POST /api/screener/filter/
    
    Filter stocks using advanced criteria on ALL fields.
    
    Body:
    {
        "filters": [
            {"field": "valuation_score", "operator": "gte", "value": 70},
            {"field": "pe_ratio", "operator": "between", "value": [5, 25]},
            {"field": "sector", "operator": "in", "value": ["Technology", "Healthcare"]},
            {"field": "roe", "operator": "gt", "value": 0.15}
        ],
        "sort_by": "valuation_score",
        "sort_order": "desc",
        "page": 1,
        "page_size": 50
    }
    """
    try:
        data = json.loads(request.body)
        filters = data.get('filters', [])
        sort_by = data.get('sort_by', 'market_cap')
        sort_order = data.get('sort_order', 'desc')
        page = data.get('page', 1)
        page_size = min(data.get('page_size', 50), 100)
        
        # Start with base queryset
        # Use select_related for fundamentals
        queryset = Stock.objects.select_related('fundamentals').all()
        
        # Build Q objects for filters
        stock_filters = Q()
        fundamentals_filters = Q()
        has_fundamentals_filter = False
        
        for f in filters:
            field_key = f.get('field')
            operator = f.get('operator', 'eq')
            value = f.get('value')
            
            if field_key not in FILTER_FIELDS:
                continue
            
            field_meta = FILTER_FIELDS[field_key]
            actual_field = field_meta['field']
            
            if operator not in OPERATORS:
                continue
            
            # Build the query
            if field_meta['model'] == 'stock':
                stock_filters &= OPERATORS[operator](actual_field, value)
            else:  # fundamentals
                has_fundamentals_filter = True
                fundamentals_filters &= OPERATORS[operator](f'fundamentals__{actual_field}', value)
        
        # Apply filters
        queryset = queryset.filter(stock_filters)
        if has_fundamentals_filter:
            queryset = queryset.filter(fundamentals_filters)
        
        # Sorting
        sort_field_meta = FILTER_FIELDS.get(sort_by, {})
        if sort_field_meta.get('model') == 'fundamentals':
            sort_field = f'fundamentals__{sort_field_meta["field"]}'
        elif sort_field_meta:
            sort_field = sort_field_meta['field']
        else:
            sort_field = 'market_cap'
        
        if sort_order == 'desc':
            sort_field = f'-{sort_field}'
        
        queryset = queryset.order_by(sort_field)
        
        # Pagination
        total_count = queryset.count()
        paginator = Paginator(queryset, page_size)
        page_obj = paginator.get_page(page)
        
        # Format results
        results = []
        for stock in page_obj:
            stock_data = {
                'ticker': stock.ticker,
                'company_name': stock.company_name,
                'current_price': _safe_float(stock.current_price),
                'price_change_percent': _safe_float(stock.price_change_percent or stock.change_percent),
                'volume': stock.volume,
                'market_cap': stock.market_cap,
                'pe_ratio': _safe_float(stock.pe_ratio),
                'exchange': stock.exchange,
            }
            
            # Add fundamentals if available
            try:
                if hasattr(stock, 'fundamentals') and stock.fundamentals:
                    f = stock.fundamentals
                    stock_data.update({
                        'forward_pe': _safe_float(f.forward_pe),
                        'peg_ratio': _safe_float(f.peg_ratio),
                        'price_to_book': _safe_float(f.price_to_book),
                        'gross_margin': _safe_float(f.gross_margin),
                        'operating_margin': _safe_float(f.operating_margin),
                        'profit_margin': _safe_float(f.profit_margin),
                        'roe': _safe_float(f.roe),
                        'roa': _safe_float(f.roa),
                        'revenue_growth_yoy': _safe_float(f.revenue_growth_yoy),
                        'earnings_growth_yoy': _safe_float(f.earnings_growth_yoy),
                        'current_ratio': _safe_float(f.current_ratio),
                        'debt_to_equity': _safe_float(f.debt_to_equity),
                        'dcf_value': _safe_float(f.dcf_value),
                        'graham_number': _safe_float(f.graham_number),
                        'valuation_score': _safe_float(f.valuation_score),
                        'valuation_status': f.valuation_status,
                        'strength_score': _safe_float(f.strength_score),
                        'strength_grade': f.strength_grade,
                        'sector': f.sector,
                        'industry': f.industry,
                    })
            except:
                pass
            
            results.append(stock_data)
        
        return JsonResponse({
            'success': True,
            'data': {
                'results': results,
                'pagination': {
                    'page': page,
                    'page_size': page_size,
                    'total_count': total_count,
                    'total_pages': paginator.num_pages,
                    'has_next': page_obj.has_next(),
                    'has_previous': page_obj.has_previous()
                },
                'filters_applied': len(filters),
                'sort_by': sort_by,
                'sort_order': sort_order
            }
        })
    
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_presets(request):
    """
    GET /api/screener/presets/
    
    Get predefined screener presets.
    """
    presets = [
        {
            'id': 'undervalued',
            'name': 'Undervalued Stocks',
            'description': 'Stocks with high valuation scores indicating undervaluation',
            'filters': [
                {'field': 'valuation_score', 'operator': 'gte', 'value': 70},
                {'field': 'market_cap', 'operator': 'gte', 'value': 1000000000}
            ]
        },
        {
            'id': 'high_growth',
            'name': 'High Growth',
            'description': 'Stocks with strong revenue and earnings growth',
            'filters': [
                {'field': 'revenue_growth_yoy', 'operator': 'gte', 'value': 0.20},
                {'field': 'earnings_growth_yoy', 'operator': 'gte', 'value': 0.15}
            ]
        },
        {
            'id': 'dividend_champions',
            'name': 'Dividend Champions',
            'description': 'Stocks with consistent dividend growth',
            'filters': [
                {'field': 'dividend_yield', 'operator': 'gte', 'value': 0.02},
                {'field': 'years_dividend_growth', 'operator': 'gte', 'value': 10},
                {'field': 'dividend_payout_ratio', 'operator': 'lte', 'value': 0.70}
            ]
        },
        {
            'id': 'quality',
            'name': 'Quality Stocks',
            'description': 'High quality stocks with strong fundamentals',
            'filters': [
                {'field': 'roe', 'operator': 'gte', 'value': 0.15},
                {'field': 'profit_margin', 'operator': 'gte', 'value': 0.10},
                {'field': 'current_ratio', 'operator': 'gte', 'value': 1.5},
                {'field': 'debt_to_equity', 'operator': 'lte', 'value': 0.5}
            ]
        },
        {
            'id': 'graham_value',
            'name': 'Graham Value',
            'description': 'Stocks meeting Benjamin Graham\'s criteria',
            'filters': [
                {'field': 'pe_ratio', 'operator': 'lte', 'value': 15},
                {'field': 'price_to_book', 'operator': 'lte', 'value': 1.5},
                {'field': 'current_ratio', 'operator': 'gte', 'value': 2.0},
                {'field': 'debt_to_equity', 'operator': 'lte', 'value': 0.5}
            ]
        },
        {
            'id': 'momentum',
            'name': 'Momentum Stocks',
            'description': 'Stocks with strong recent performance',
            'filters': [
                {'field': 'price_change_percent', 'operator': 'gte', 'value': 5},
                {'field': 'volume', 'operator': 'gte', 'value': 1000000}
            ]
        },
        {
            'id': 'cash_rich',
            'name': 'Cash Rich',
            'description': 'Companies with strong cash flow',
            'filters': [
                {'field': 'fcf_yield', 'operator': 'gte', 'value': 0.05},
                {'field': 'cash_conversion', 'operator': 'gte', 'value': 0.8},
                {'field': 'free_cash_flow', 'operator': 'gt', 'value': 0}
            ]
        },
        {
            'id': 'low_debt',
            'name': 'Low Debt',
            'description': 'Companies with minimal leverage',
            'filters': [
                {'field': 'debt_to_equity', 'operator': 'lte', 'value': 0.3},
                {'field': 'debt_to_assets', 'operator': 'lte', 'value': 0.2},
                {'field': 'interest_coverage', 'operator': 'gte', 'value': 10}
            ]
        }
    ]
    
    return JsonResponse({
        'success': True,
        'data': {
            'presets': presets
        }
    })
