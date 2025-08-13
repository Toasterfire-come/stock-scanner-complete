"""
Optimized Serializers for Stock Scanner API
Provides efficient data serialization with performance optimizations
"""

from rest_framework import serializers
from django.core.cache import cache
from django.utils import timezone
from decimal import Decimal
import logging

from .models import Stock, StockPrice, StockAlert, UserPortfolio, PortfolioHolding

logger = logging.getLogger(__name__)

class PerformanceSerializerMixin:
    """
    Mixin for performance optimizations in serializers
    """
    
    def to_representation(self, instance):
        """Override to add performance monitoring"""
        start_time = timezone.now()
        data = super().to_representation(instance)
        end_time = timezone.now()
        
        # Log slow serializations (>100ms)
        duration = (end_time - start_time).total_seconds()
        if duration > 0.1:
            logger.warning(f"Slow serialization: {self.__class__.__name__} took {duration:.3f}s")
        
        return data

class MinimalStockSerializer(PerformanceSerializerMixin, serializers.ModelSerializer):
    """
    Minimal stock data for high-performance list views
    """
    formatted_price = serializers.ReadOnlyField()
    formatted_change = serializers.ReadOnlyField()
    
    class Meta:
        model = Stock
        fields = [
            'id', 'ticker', 'company_name', 'current_price', 
            'change_percent', 'volume', 'formatted_price', 'formatted_change'
        ]

class StockSerializer(PerformanceSerializerMixin, serializers.ModelSerializer):
    """
    Full stock data serializer with computed fields
    """
    formatted_price = serializers.ReadOnlyField()
    formatted_change = serializers.ReadOnlyField()
    formatted_volume = serializers.ReadOnlyField()
    formatted_market_cap = serializers.ReadOnlyField()
    
    # Additional computed fields
    price_trend = serializers.SerializerMethodField()
    volatility_indicator = serializers.SerializerMethodField()
    trading_status = serializers.SerializerMethodField()
    
    class Meta:
        model = Stock
        fields = [
            'id', 'ticker', 'symbol', 'company_name', 'name', 'exchange',
            'current_price', 'price_change_today', 'price_change_week',
            'price_change_month', 'price_change_year', 'change_percent',
            'bid_price', 'ask_price', 'bid_ask_spread', 'days_range',
            'days_low', 'days_high', 'volume', 'volume_today', 'avg_volume_3mon',
            'dvav', 'shares_available', 'market_cap', 'market_cap_change_3mon',
            'pe_ratio', 'pe_change_3mon', 'dividend_yield', 'one_year_target',
            'week_52_low', 'week_52_high', 'earnings_per_share', 'book_value',
            'price_to_book', 'created_at', 'last_updated',
            'formatted_price', 'formatted_change', 'formatted_volume',
            'formatted_market_cap', 'price_trend', 'volatility_indicator',
            'trading_status'
        ]
    
    def get_price_trend(self, obj):
        """Calculate price trend indicator"""
        if obj.price_change_week and obj.price_change_month:
            if obj.price_change_week > 0 and obj.price_change_month > 0:
                return 'bullish'
            elif obj.price_change_week < 0 and obj.price_change_month < 0:
                return 'bearish'
            else:
                return 'mixed'
        return 'neutral'
    
    def get_volatility_indicator(self, obj):
        """Calculate volatility indicator"""
        if obj.days_low and obj.days_high and obj.current_price:
            range_size = float(obj.days_high - obj.days_low)
            current_position = float(obj.current_price - obj.days_low)
            
            if range_size > 0:
                volatility = (range_size / float(obj.current_price)) * 100
                if volatility > 5:
                    return 'high'
                elif volatility > 2:
                    return 'medium'
                else:
                    return 'low'
        return 'unknown'
    
    def get_trading_status(self, obj):
        """Determine trading status based on volume and price movement"""
        if obj.volume_today and obj.avg_volume_3mon:
            volume_ratio = float(obj.volume_today) / float(obj.avg_volume_3mon)
            
            if volume_ratio > 2 and obj.change_percent and abs(float(obj.change_percent)) > 5:
                return 'active'
            elif volume_ratio > 1.5:
                return 'moderate'
            else:
                return 'quiet'
        return 'unknown'

class CachedStockSerializer(StockSerializer):
    """
    Stock serializer with intelligent caching
    """
    cache_timeout = 300  # 5 minutes
    
    def to_representation(self, instance):
        """Override to implement caching"""
        cache_key = f"stock_serialized_{instance.id}_{instance.last_updated.timestamp()}"
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return cached_data
        
        data = super().to_representation(instance)
        cache.set(cache_key, data, self.cache_timeout)
        
        return data

class StockPriceSerializer(serializers.ModelSerializer):
    """
    Stock price history serializer
    """
    ticker = serializers.CharField(source='stock.ticker', read_only=True)
    
    class Meta:
        model = StockPrice
        fields = ['id', 'ticker', 'price', 'timestamp']

class StockAlertSerializer(serializers.ModelSerializer):
    """
    Stock alert serializer
    """
    stock_ticker = serializers.CharField(source='stock.ticker', read_only=True)
    stock_name = serializers.CharField(source='stock.company_name', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    
    class Meta:
        model = StockAlert
        fields = [
            'id', 'stock_ticker', 'stock_name', 'alert_type', 'target_value',
            'is_active', 'created_at', 'triggered_at', 'user_email'
        ]

class PortfolioHoldingSerializer(serializers.ModelSerializer):
    """
    Portfolio holding with performance calculations
    """
    stock_ticker = serializers.CharField(source='stock.ticker', read_only=True)
    stock_name = serializers.CharField(source='stock.company_name', read_only=True)
    current_price = serializers.DecimalField(source='stock.current_price', max_digits=15, decimal_places=4, read_only=True)
    
    # Performance calculations
    current_value = serializers.SerializerMethodField()
    total_return = serializers.SerializerMethodField()
    return_percent = serializers.SerializerMethodField()
    day_change = serializers.SerializerMethodField()
    
    class Meta:
        model = PortfolioHolding
        fields = [
            'id', 'stock_ticker', 'stock_name', 'quantity', 'purchase_price',
            'purchase_date', 'current_price', 'current_value', 'total_return',
            'return_percent', 'day_change', 'notes'
        ]
    
    def get_current_value(self, obj):
        """Calculate current value of holding"""
        if obj.stock.current_price and obj.quantity:
            return float(obj.stock.current_price) * float(obj.quantity)
        return 0
    
    def get_total_return(self, obj):
        """Calculate total return"""
        current_value = self.get_current_value(obj)
        cost_basis = float(obj.purchase_price) * float(obj.quantity)
        return current_value - cost_basis
    
    def get_return_percent(self, obj):
        """Calculate return percentage"""
        total_return = self.get_total_return(obj)
        cost_basis = float(obj.purchase_price) * float(obj.quantity)
        
        if cost_basis > 0:
            return (total_return / cost_basis) * 100
        return 0
    
    def get_day_change(self, obj):
        """Calculate day change in value"""
        if obj.stock.price_change_today and obj.quantity:
            return float(obj.stock.price_change_today) * float(obj.quantity)
        return 0

class UserPortfolioSerializer(serializers.ModelSerializer):
    """
    User portfolio with holdings and performance
    """
    holdings = PortfolioHoldingSerializer(many=True, read_only=True)
    holdings_count = serializers.SerializerMethodField()
    user_username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = UserPortfolio
        fields = [
            'id', 'name', 'description', 'is_public', 'created_at', 'updated_at',
            'total_value', 'total_cost', 'total_return', 'total_return_percent',
            'followers_count', 'likes_count', 'user_username', 'holdings',
            'holdings_count'
        ]
    
    def get_holdings_count(self, obj):
        """Get number of holdings in portfolio"""
        return obj.holdings.count()

class MarketStatsSerializer(serializers.Serializer):
    """
    Market statistics serializer
    """
    total_stocks = serializers.IntegerField()
    active_stocks = serializers.IntegerField()
    gainers_count = serializers.IntegerField()
    losers_count = serializers.IntegerField()
    unchanged_count = serializers.IntegerField()
    total_volume = serializers.IntegerField()
    avg_change_percent = serializers.DecimalField(max_digits=8, decimal_places=4)
    market_trend = serializers.CharField(max_length=20)
    last_updated = serializers.DateTimeField()

class SearchResultSerializer(serializers.Serializer):
    """
    Search result serializer with relevance scoring
    """
    stock = MinimalStockSerializer()
    relevance_score = serializers.DecimalField(max_digits=5, decimal_places=2)
    match_type = serializers.CharField(max_length=20)  # 'ticker', 'name', 'partial'

class BulkStockUpdateSerializer(serializers.Serializer):
    """
    Serializer for bulk stock updates
    """
    tickers = serializers.ListField(
        child=serializers.CharField(max_length=10),
        min_length=1,
        max_length=100
    )
    update_prices = serializers.BooleanField(default=True)
    update_fundamentals = serializers.BooleanField(default=False)
    force_update = serializers.BooleanField(default=False)

class ErrorResponseSerializer(serializers.Serializer):
    """
    Standardized error response serializer
    """
    status = serializers.CharField(default='error')
    message = serializers.CharField()
    error_code = serializers.CharField(required=False)
    details = serializers.DictField(required=False)
    timestamp = serializers.DateTimeField(default=timezone.now)

class SuccessResponseSerializer(serializers.Serializer):
    """
    Standardized success response serializer
    """
    status = serializers.CharField(default='success')
    message = serializers.CharField(required=False)
    data = serializers.DictField(required=False)
    timestamp = serializers.DateTimeField(default=timezone.now)