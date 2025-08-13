"""
Frontend Optimization System for Stock Scanner
Shifts computational load from backend to frontend/browser for better scalability
"""

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from django.core.cache import cache
import json
import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

class FrontendOptimizationManager:
    """
    Manages frontend optimization strategies to reduce backend computational load
    """
    
    def __init__(self):
        self.optimization_strategies = {
            'client_side_processing': True,
            'browser_caching': True,
            'progressive_loading': True,
            'minimal_payloads': True,
            'client_side_filtering': True,
            'browser_based_calculations': True
        }
    
    def get_minimal_stock_data(self, stocks_queryset, fields=None):
        """
        Return minimal stock data for frontend processing
        Frontend will handle formatting, calculations, and display logic
        """
        minimal_fields = fields or [
            'id', 'ticker', 'company_name', 'current_price', 
            'change_percent', 'volume', 'market_cap', 'last_updated'
        ]
        
        data = []
        for stock in stocks_queryset:
            stock_data = {}
            for field in minimal_fields:
                value = getattr(stock, field, None)
                if value is not None:
                    # Send raw values - frontend will format
                    stock_data[field] = str(value) if hasattr(value, '__str__') else value
            data.append(stock_data)
        
        return data
    
    def get_metadata_for_frontend(self):
        """
        Provide metadata that frontend needs for processing
        """
        return {
            'field_types': {
                'current_price': 'decimal',
                'change_percent': 'decimal', 
                'volume': 'integer',
                'market_cap': 'integer',
                'pe_ratio': 'decimal',
                'dividend_yield': 'decimal'
            },
            'formatting_rules': {
                'currency_fields': ['current_price', 'days_high', 'days_low'],
                'percentage_fields': ['change_percent', 'dividend_yield'],
                'large_number_fields': ['volume', 'market_cap', 'shares_available']
            },
            'calculation_formulas': {
                'price_change_dollar': 'current_price * (change_percent / 100)',
                'market_cap_formatted': 'market_cap / 1000000', # Convert to millions
                'volume_formatted': 'volume / 1000000' # Convert to millions
            },
            'default_sort_fields': ['market_cap', 'volume', 'change_percent'],
            'filter_ranges': {
                'price': {'min': 0, 'max': 10000, 'step': 0.01},
                'market_cap': {'min': 0, 'max': 5000000000000, 'step': 1000000},
                'volume': {'min': 0, 'max': 1000000000, 'step': 1000}
            }
        }
    
    def create_frontend_configuration(self):
        """
        Create configuration for frontend optimization features
        """
        return {
            'caching': {
                'enabled': True,
                'ttl': 300,  # 5 minutes
                'storage': 'localStorage',
                'compression': True
            },
            'pagination': {
                'client_side': True,
                'page_size': 50,
                'virtual_scrolling': True,
                'preload_pages': 2
            },
            'filtering': {
                'client_side': True,
                'debounce_ms': 300,
                'case_sensitive': False,
                'fuzzy_search': True
            },
            'sorting': {
                'client_side': True,
                'multi_column': True,
                'remember_state': True
            },
            'charts': {
                'client_side_rendering': True,
                'data_aggregation': 'browser',
                'real_time_updates': True,
                'progressive_loading': True
            },
            'calculations': {
                'technical_indicators': 'browser',
                'portfolio_metrics': 'browser', 
                'performance_analytics': 'browser'
            }
        }

# Global optimization manager
frontend_optimizer = FrontendOptimizationManager()

@api_view(['GET'])
@permission_classes([AllowAny])
def get_minimal_stocks_api(request):
    """
    Return minimal stock data for frontend processing
    Reduces backend load by sending raw data only
    """
    try:
        from .models import Stock
        
        # Get query parameters
        limit = int(request.GET.get('limit', 100))
        offset = int(request.GET.get('offset', 0))
        fields = request.GET.get('fields', '').split(',') if request.GET.get('fields') else None
        
        # Get minimal data
        stocks = Stock.objects.all()[offset:offset + limit]
        minimal_data = frontend_optimizer.get_minimal_stock_data(stocks, fields)
        
        # Get metadata for frontend
        metadata = frontend_optimizer.get_metadata_for_frontend()
        
        return Response({
            'status': 'success',
            'data': minimal_data,
            'metadata': metadata,
            'pagination': {
                'limit': limit,
                'offset': offset,
                'total': Stock.objects.count()
            },
            'frontend_processing': True,
            'timestamp': timezone.now()
        })
        
    except Exception as e:
        logger.error(f"Minimal stocks API error: {e}")
        return Response({
            'status': 'error',
            'message': 'Failed to get minimal stock data',
            'timestamp': timezone.now()
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_frontend_configuration(request):
    """
    Provide frontend optimization configuration
    """
    try:
        config = frontend_optimizer.create_frontend_configuration()
        
        return Response({
            'status': 'success',
            'configuration': config,
            'optimization_strategies': frontend_optimizer.optimization_strategies,
            'timestamp': timezone.now()
        })
        
    except Exception as e:
        logger.error(f"Frontend configuration error: {e}")
        return Response({
            'status': 'error',
            'message': 'Failed to get frontend configuration',
            'timestamp': timezone.now()
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_raw_chart_data(request):
    """
    Return raw data points for frontend chart rendering
    Frontend handles all chart calculations and rendering
    """
    try:
        ticker = request.GET.get('ticker')
        timeframe = request.GET.get('timeframe', '1day')
        
        if not ticker:
            return Response({
                'status': 'error',
                'message': 'Ticker parameter required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get raw price data (minimal processing)
        from .models import StockPrice
        
        price_data = StockPrice.objects.filter(
            stock__ticker=ticker
        ).order_by('timestamp').values('timestamp', 'price', 'volume')[:1000]
        
        # Convert to simple array format for frontend
        raw_data = [
            [
                int(item['timestamp'].timestamp() * 1000),  # Timestamp in milliseconds
                float(item['price']) if item['price'] else 0,
                int(item['volume']) if item['volume'] else 0
            ]
            for item in price_data
        ]
        
        return Response({
            'status': 'success',
            'ticker': ticker,
            'timeframe': timeframe,
            'data': raw_data,
            'data_format': ['timestamp_ms', 'price', 'volume'],
            'frontend_processing': True,
            'chart_calculations': 'client_side',
            'timestamp': timezone.now()
        })
        
    except Exception as e:
        logger.error(f"Raw chart data error: {e}")
        return Response({
            'status': 'error',
            'message': 'Failed to get raw chart data',
            'timestamp': timezone.now()
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def bulk_minimal_data(request):
    """
    Return bulk minimal data for multiple tickers
    Frontend handles all processing and formatting
    """
    try:
        tickers = request.data.get('tickers', [])
        fields = request.data.get('fields', [])
        
        if not tickers:
            return Response({
                'status': 'error',
                'message': 'Tickers list required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        from .models import Stock
        
        stocks = Stock.objects.filter(ticker__in=tickers)
        minimal_data = frontend_optimizer.get_minimal_stock_data(stocks, fields)
        
        # Group by ticker for easy frontend access
        data_by_ticker = {item['ticker']: item for item in minimal_data}
        
        return Response({
            'status': 'success',
            'data': data_by_ticker,
            'requested_tickers': tickers,
            'found_count': len(minimal_data),
            'frontend_processing': True,
            'timestamp': timezone.now()
        })
        
    except Exception as e:
        logger.error(f"Bulk minimal data error: {e}")
        return Response({
            'status': 'error',
            'message': 'Failed to get bulk minimal data',
            'timestamp': timezone.now()
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ClientSideJavaScriptGenerator:
    """
    Generates JavaScript code for client-side processing
    """
    
    @staticmethod
    def generate_stock_formatter():
        """
        Generate JavaScript for client-side stock data formatting
        """
        return '''
// Stock Data Formatter - Client Side Processing
class StockDataFormatter {
    constructor(metadata) {
        this.metadata = metadata || {};
        this.currencyFields = metadata.formatting_rules?.currency_fields || [];
        this.percentageFields = metadata.formatting_rules?.percentage_fields || [];
        this.largeNumberFields = metadata.formatting_rules?.large_number_fields || [];
    }
    
    formatCurrency(value) {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD',
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        }).format(parseFloat(value) || 0);
    }
    
    formatPercentage(value) {
        return new Intl.NumberFormat('en-US', {
            style: 'percent',
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        }).format((parseFloat(value) || 0) / 100);
    }
    
    formatLargeNumber(value) {
        const num = parseFloat(value) || 0;
        if (num >= 1e12) return (num / 1e12).toFixed(2) + 'T';
        if (num >= 1e9) return (num / 1e9).toFixed(2) + 'B';
        if (num >= 1e6) return (num / 1e6).toFixed(2) + 'M';
        if (num >= 1e3) return (num / 1e3).toFixed(2) + 'K';
        return num.toLocaleString();
    }
    
    formatStock(stockData) {
        const formatted = { ...stockData };
        
        // Format all fields based on metadata
        Object.keys(formatted).forEach(field => {
            if (this.currencyFields.includes(field)) {
                formatted[field + '_formatted'] = this.formatCurrency(formatted[field]);
            } else if (this.percentageFields.includes(field)) {
                formatted[field + '_formatted'] = this.formatPercentage(formatted[field]);
            } else if (this.largeNumberFields.includes(field)) {
                formatted[field + '_formatted'] = this.formatLargeNumber(formatted[field]);
            }
        });
        
        return formatted;
    }
    
    formatStockList(stockList) {
        return stockList.map(stock => this.formatStock(stock));
    }
}
'''
    
    @staticmethod
    def generate_client_calculator():
        """
        Generate JavaScript for client-side calculations
        """
        return '''
// Client-Side Stock Calculations
class StockCalculator {
    static calculatePriceChange(currentPrice, changePercent) {
        return parseFloat(currentPrice) * (parseFloat(changePercent) / 100);
    }
    
    static calculatePortfolioValue(holdings) {
        return holdings.reduce((total, holding) => {
            return total + (parseFloat(holding.shares) * parseFloat(holding.current_price));
        }, 0);
    }
    
    static calculatePortfolioReturn(holdings) {
        let totalValue = 0;
        let totalCost = 0;
        
        holdings.forEach(holding => {
            const currentValue = parseFloat(holding.shares) * parseFloat(holding.current_price);
            const costBasis = parseFloat(holding.shares) * parseFloat(holding.purchase_price);
            totalValue += currentValue;
            totalCost += costBasis;
        });
        
        return totalCost > 0 ? ((totalValue - totalCost) / totalCost) * 100 : 0;
    }
    
    static calculateTechnicalIndicators(priceData) {
        // Simple Moving Average
        const sma = (data, period) => {
            const result = [];
            for (let i = period - 1; i < data.length; i++) {
                const sum = data.slice(i - period + 1, i + 1).reduce((a, b) => a + b[1], 0);
                result.push([data[i][0], sum / period]);
            }
            return result;
        };
        
        // Relative Strength Index
        const rsi = (data, period = 14) => {
            const changes = [];
            for (let i = 1; i < data.length; i++) {
                changes.push(data[i][1] - data[i-1][1]);
            }
            
            const result = [];
            for (let i = period; i < changes.length; i++) {
                const gains = changes.slice(i - period, i).filter(x => x > 0);
                const losses = changes.slice(i - period, i).filter(x => x < 0).map(x => Math.abs(x));
                
                const avgGain = gains.length > 0 ? gains.reduce((a, b) => a + b, 0) / period : 0;
                const avgLoss = losses.length > 0 ? losses.reduce((a, b) => a + b, 0) / period : 0;
                
                const rs = avgLoss === 0 ? 100 : avgGain / avgLoss;
                const rsiValue = 100 - (100 / (1 + rs));
                
                result.push([data[i][0], rsiValue]);
            }
            return result;
        };
        
        return {
            sma20: sma(priceData, 20),
            sma50: sma(priceData, 50),
            rsi: rsi(priceData)
        };
    }
}
'''
    
    @staticmethod
    def generate_client_filter():
        """
        Generate JavaScript for client-side filtering and sorting
        """
        return '''
// Client-Side Filtering and Sorting
class StockFilter {
    constructor() {
        this.filters = {};
        this.sortConfig = { field: null, direction: 'asc' };
    }
    
    addFilter(field, operator, value) {
        this.filters[field] = { operator, value };
    }
    
    removeFilter(field) {
        delete this.filters[field];
    }
    
    applyFilters(stockList) {
        return stockList.filter(stock => {
            return Object.entries(this.filters).every(([field, filter]) => {
                const stockValue = parseFloat(stock[field]) || 0;
                const filterValue = parseFloat(filter.value) || 0;
                
                switch (filter.operator) {
                    case 'gt': return stockValue > filterValue;
                    case 'gte': return stockValue >= filterValue;
                    case 'lt': return stockValue < filterValue;
                    case 'lte': return stockValue <= filterValue;
                    case 'eq': return stockValue === filterValue;
                    case 'contains': return stock[field]?.toLowerCase().includes(filter.value.toLowerCase());
                    default: return true;
                }
            });
        });
    }
    
    sortStocks(stockList, field, direction = 'asc') {
        this.sortConfig = { field, direction };
        
        return [...stockList].sort((a, b) => {
            let aVal = a[field];
            let bVal = b[field];
            
            // Handle numeric fields
            if (!isNaN(aVal) && !isNaN(bVal)) {
                aVal = parseFloat(aVal);
                bVal = parseFloat(bVal);
            }
            
            if (aVal < bVal) return direction === 'asc' ? -1 : 1;
            if (aVal > bVal) return direction === 'asc' ? 1 : -1;
            return 0;
        });
    }
    
    searchStocks(stockList, query) {
        const lowerQuery = query.toLowerCase();
        return stockList.filter(stock => 
            stock.ticker?.toLowerCase().includes(lowerQuery) ||
            stock.company_name?.toLowerCase().includes(lowerQuery)
        );
    }
}
'''

js_generator = ClientSideJavaScriptGenerator()

@api_view(['GET'])
@permission_classes([AllowAny])
def get_client_side_scripts(request):
    """
    Provide JavaScript code for client-side processing
    """
    try:
        script_type = request.GET.get('type', 'all')
        
        scripts = {}
        
        if script_type in ['all', 'formatter']:
            scripts['formatter'] = js_generator.generate_stock_formatter()
        
        if script_type in ['all', 'calculator']:
            scripts['calculator'] = js_generator.generate_client_calculator()
        
        if script_type in ['all', 'filter']:
            scripts['filter'] = js_generator.generate_client_filter()
        
        return Response({
            'status': 'success',
            'scripts': scripts,
            'script_type': script_type,
            'usage': 'Include these scripts in your frontend for client-side processing',
            'timestamp': timezone.now()
        })
        
    except Exception as e:
        logger.error(f"Client-side scripts error: {e}")
        return Response({
            'status': 'error',
            'message': 'Failed to get client-side scripts',
            'timestamp': timezone.now()
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)