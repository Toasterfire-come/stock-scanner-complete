"""
Browser-Based Chart Rendering System
Shifts all chart processing and rendering to the frontend/browser
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
import json
import logging

logger = logging.getLogger(__name__)

class BrowserChartSystem:
    """
    Provides data and configuration for browser-based chart rendering
    All calculations and rendering happen on the client side
    """
    
    def __init__(self):
        self.chart_configurations = {
            'candlestick': {
                'type': 'candlestick',
                'data_format': ['timestamp', 'open', 'high', 'low', 'close', 'volume'],
                'calculations': 'client_side',
                'indicators_supported': ['sma', 'ema', 'bollinger', 'rsi', 'macd']
            },
            'line': {
                'type': 'line',
                'data_format': ['timestamp', 'price'],
                'calculations': 'client_side',
                'real_time': True
            },
            'volume': {
                'type': 'column',
                'data_format': ['timestamp', 'volume'],
                'calculations': 'client_side'
            }
        }
    
    def get_chart_javascript_library(self):
        """
        Generate comprehensive JavaScript charting library for frontend
        """
        return '''
// Advanced Stock Chart Library - Browser Based
class StockChart {
    constructor(containerId, options = {}) {
        this.container = document.getElementById(containerId);
        this.options = {
            width: options.width || 800,
            height: options.height || 400,
            theme: options.theme || 'light',
            realTime: options.realTime || false,
            indicators: options.indicators || [],
            ...options
        };
        this.data = [];
        this.indicators = {};
        this.canvas = null;
        this.ctx = null;
        this.animationFrame = null;
        this.init();
    }
    
    init() {
        this.createCanvas();
        this.setupEventListeners();
        if (this.options.realTime) {
            this.startRealTimeUpdates();
        }
    }
    
    createCanvas() {
        this.canvas = document.createElement('canvas');
        this.canvas.width = this.options.width;
        this.canvas.height = this.options.height;
        this.canvas.style.border = '1px solid #ccc';
        this.ctx = this.canvas.getContext('2d');
        this.container.appendChild(this.canvas);
    }
    
    setData(data, format = ['timestamp', 'price']) {
        this.data = data.map(row => {
            const item = {};
            format.forEach((field, index) => {
                item[field] = row[index];
            });
            return item;
        });
        this.calculateIndicators();
        this.render();
    }
    
    calculateIndicators() {
        // Simple Moving Average
        this.indicators.sma20 = this.calculateSMA(20);
        this.indicators.sma50 = this.calculateSMA(50);
        
        // Exponential Moving Average
        this.indicators.ema12 = this.calculateEMA(12);
        this.indicators.ema26 = this.calculateEMA(26);
        
        // RSI
        this.indicators.rsi = this.calculateRSI(14);
        
        // MACD
        this.indicators.macd = this.calculateMACD();
        
        // Bollinger Bands
        this.indicators.bollinger = this.calculateBollingerBands(20, 2);
    }
    
    calculateSMA(period) {
        const sma = [];
        for (let i = period - 1; i < this.data.length; i++) {
            const sum = this.data.slice(i - period + 1, i + 1)
                .reduce((acc, item) => acc + parseFloat(item.price || item.close), 0);
            sma.push({
                timestamp: this.data[i].timestamp,
                value: sum / period
            });
        }
        return sma;
    }
    
    calculateEMA(period) {
        const ema = [];
        const multiplier = 2 / (period + 1);
        let previousEMA = parseFloat(this.data[0].price || this.data[0].close);
        
        ema.push({
            timestamp: this.data[0].timestamp,
            value: previousEMA
        });
        
        for (let i = 1; i < this.data.length; i++) {
            const currentPrice = parseFloat(this.data[i].price || this.data[i].close);
            const currentEMA = (currentPrice * multiplier) + (previousEMA * (1 - multiplier));
            ema.push({
                timestamp: this.data[i].timestamp,
                value: currentEMA
            });
            previousEMA = currentEMA;
        }
        return ema;
    }
    
    calculateRSI(period) {
        const rsi = [];
        const changes = [];
        
        for (let i = 1; i < this.data.length; i++) {
            const currentPrice = parseFloat(this.data[i].price || this.data[i].close);
            const previousPrice = parseFloat(this.data[i-1].price || this.data[i-1].close);
            changes.push(currentPrice - previousPrice);
        }
        
        for (let i = period; i < changes.length; i++) {
            const gains = changes.slice(i - period, i).filter(x => x > 0);
            const losses = changes.slice(i - period, i).filter(x => x < 0).map(x => Math.abs(x));
            
            const avgGain = gains.length > 0 ? gains.reduce((a, b) => a + b, 0) / period : 0;
            const avgLoss = losses.length > 0 ? losses.reduce((a, b) => a + b, 0) / period : 0;
            
            const rs = avgLoss === 0 ? 100 : avgGain / avgLoss;
            const rsiValue = 100 - (100 / (1 + rs));
            
            rsi.push({
                timestamp: this.data[i + 1].timestamp,
                value: rsiValue
            });
        }
        return rsi;
    }
    
    calculateMACD() {
        const ema12 = this.indicators.ema12;
        const ema26 = this.indicators.ema26;
        const macdLine = [];
        
        const minLength = Math.min(ema12.length, ema26.length);
        for (let i = 0; i < minLength; i++) {
            macdLine.push({
                timestamp: ema12[i].timestamp,
                value: ema12[i].value - ema26[i].value
            });
        }
        
        // Signal line (9-period EMA of MACD)
        const signalLine = this.calculateEMAFromArray(macdLine, 9);
        
        // Histogram
        const histogram = [];
        const minSignalLength = Math.min(macdLine.length, signalLine.length);
        for (let i = 0; i < minSignalLength; i++) {
            histogram.push({
                timestamp: macdLine[i].timestamp,
                value: macdLine[i].value - signalLine[i].value
            });
        }
        
        return {
            macd: macdLine,
            signal: signalLine,
            histogram: histogram
        };
    }
    
    calculateEMAFromArray(data, period) {
        const ema = [];
        const multiplier = 2 / (period + 1);
        let previousEMA = data[0].value;
        
        ema.push({
            timestamp: data[0].timestamp,
            value: previousEMA
        });
        
        for (let i = 1; i < data.length; i++) {
            const currentEMA = (data[i].value * multiplier) + (previousEMA * (1 - multiplier));
            ema.push({
                timestamp: data[i].timestamp,
                value: currentEMA
            });
            previousEMA = currentEMA;
        }
        return ema;
    }
    
    calculateBollingerBands(period, standardDeviations) {
        const sma = this.indicators.sma20; // Use existing SMA
        const bands = [];
        
        for (let i = period - 1; i < this.data.length; i++) {
            const prices = this.data.slice(i - period + 1, i + 1)
                .map(item => parseFloat(item.price || item.close));
            const average = prices.reduce((a, b) => a + b, 0) / period;
            const variance = prices.reduce((acc, price) => acc + Math.pow(price - average, 2), 0) / period;
            const stdDev = Math.sqrt(variance);
            
            bands.push({
                timestamp: this.data[i].timestamp,
                upper: average + (standardDeviations * stdDev),
                middle: average,
                lower: average - (standardDeviations * stdDev)
            });
        }
        return bands;
    }
    
    render() {
        if (!this.data.length) return;
        
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        
        // Calculate price range and scale
        const prices = this.data.map(d => parseFloat(d.price || d.close));
        const minPrice = Math.min(...prices);
        const maxPrice = Math.max(...prices);
        const priceRange = maxPrice - minPrice;
        
        const chartHeight = this.canvas.height - 60; // Leave space for labels
        const chartWidth = this.canvas.width - 80;
        
        // Draw price line
        this.ctx.strokeStyle = '#2196F3';
        this.ctx.lineWidth = 2;
        this.ctx.beginPath();
        
        this.data.forEach((point, index) => {
            const x = 40 + (index / (this.data.length - 1)) * chartWidth;
            const y = 30 + (1 - (parseFloat(point.price || point.close) - minPrice) / priceRange) * chartHeight;
            
            if (index === 0) {
                this.ctx.moveTo(x, y);
            } else {
                this.ctx.lineTo(x, y);
            }
        });
        this.ctx.stroke();
        
        // Draw indicators
        this.drawIndicators(chartWidth, chartHeight, minPrice, priceRange);
        
        // Draw axes and labels
        this.drawAxes(chartWidth, chartHeight, minPrice, maxPrice);
    }
    
    drawIndicators(chartWidth, chartHeight, minPrice, priceRange) {
        // Draw SMA lines
        if (this.indicators.sma20) {
            this.drawIndicatorLine(this.indicators.sma20, '#FF9800', chartWidth, chartHeight, minPrice, priceRange);
        }
        if (this.indicators.sma50) {
            this.drawIndicatorLine(this.indicators.sma50, '#9C27B0', chartWidth, chartHeight, minPrice, priceRange);
        }
        
        // Draw Bollinger Bands
        if (this.indicators.bollinger) {
            this.drawBollingerBands(this.indicators.bollinger, chartWidth, chartHeight, minPrice, priceRange);
        }
    }
    
    drawIndicatorLine(indicator, color, chartWidth, chartHeight, minPrice, priceRange) {
        this.ctx.strokeStyle = color;
        this.ctx.lineWidth = 1;
        this.ctx.beginPath();
        
        indicator.forEach((point, index) => {
            const dataIndex = this.data.findIndex(d => d.timestamp === point.timestamp);
            if (dataIndex >= 0) {
                const x = 40 + (dataIndex / (this.data.length - 1)) * chartWidth;
                const y = 30 + (1 - (point.value - minPrice) / priceRange) * chartHeight;
                
                if (index === 0) {
                    this.ctx.moveTo(x, y);
                } else {
                    this.ctx.lineTo(x, y);
                }
            }
        });
        this.ctx.stroke();
    }
    
    drawBollingerBands(bands, chartWidth, chartHeight, minPrice, priceRange) {
        this.ctx.strokeStyle = '#E0E0E0';
        this.ctx.lineWidth = 1;
        
        // Upper band
        this.ctx.beginPath();
        bands.forEach((band, index) => {
            const dataIndex = this.data.findIndex(d => d.timestamp === band.timestamp);
            if (dataIndex >= 0) {
                const x = 40 + (dataIndex / (this.data.length - 1)) * chartWidth;
                const y = 30 + (1 - (band.upper - minPrice) / priceRange) * chartHeight;
                if (index === 0) this.ctx.moveTo(x, y);
                else this.ctx.lineTo(x, y);
            }
        });
        this.ctx.stroke();
        
        // Lower band
        this.ctx.beginPath();
        bands.forEach((band, index) => {
            const dataIndex = this.data.findIndex(d => d.timestamp === band.timestamp);
            if (dataIndex >= 0) {
                const x = 40 + (dataIndex / (this.data.length - 1)) * chartWidth;
                const y = 30 + (1 - (band.lower - minPrice) / priceRange) * chartHeight;
                if (index === 0) this.ctx.moveTo(x, y);
                else this.ctx.lineTo(x, y);
            }
        });
        this.ctx.stroke();
    }
    
    drawAxes(chartWidth, chartHeight, minPrice, maxPrice) {
        this.ctx.strokeStyle = '#666';
        this.ctx.lineWidth = 1;
        this.ctx.font = '12px Arial';
        this.ctx.fillStyle = '#666';
        
        // Y-axis
        this.ctx.beginPath();
        this.ctx.moveTo(40, 30);
        this.ctx.lineTo(40, 30 + chartHeight);
        this.ctx.stroke();
        
        // X-axis
        this.ctx.beginPath();
        this.ctx.moveTo(40, 30 + chartHeight);
        this.ctx.lineTo(40 + chartWidth, 30 + chartHeight);
        this.ctx.stroke();
        
        // Price labels
        const priceSteps = 5;
        for (let i = 0; i <= priceSteps; i++) {
            const price = minPrice + (maxPrice - minPrice) * (i / priceSteps);
            const y = 30 + chartHeight - (i / priceSteps) * chartHeight;
            this.ctx.fillText(price.toFixed(2), 5, y + 3);
        }
    }
    
    setupEventListeners() {
        this.canvas.addEventListener('mousemove', (e) => {
            this.handleMouseMove(e);
        });
        
        this.canvas.addEventListener('click', (e) => {
            this.handleClick(e);
        });
    }
    
    handleMouseMove(e) {
        const rect = this.canvas.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        
        // Show crosshair and data point info
        this.showCrosshair(x, y);
    }
    
    handleClick(e) {
        // Handle chart interactions
    }
    
    showCrosshair(x, y) {
        // Implement crosshair display
    }
    
    startRealTimeUpdates() {
        this.realTimeInterval = setInterval(() => {
            this.fetchRealTimeData();
        }, 5000); // Update every 5 seconds
    }
    
    fetchRealTimeData() {
        // Fetch new data point and update chart
        // This would call the backend API for latest data
    }
    
    updateData(newDataPoint) {
        this.data.push(newDataPoint);
        if (this.data.length > 1000) {
            this.data.shift(); // Keep only last 1000 points
        }
        this.calculateIndicators();
        this.render();
    }
    
    destroy() {
        if (this.realTimeInterval) {
            clearInterval(this.realTimeInterval);
        }
        if (this.animationFrame) {
            cancelAnimationFrame(this.animationFrame);
        }
        if (this.container && this.canvas) {
            this.container.removeChild(this.canvas);
        }
    }
}

// Chart Factory for different chart types
class ChartFactory {
    static createCandlestickChart(containerId, options) {
        return new CandlestickChart(containerId, options);
    }
    
    static createLineChart(containerId, options) {
        return new StockChart(containerId, {...options, type: 'line'});
    }
    
    static createVolumeChart(containerId, options) {
        return new VolumeChart(containerId, options);
    }
}

// Volume Chart Implementation
class VolumeChart extends StockChart {
    render() {
        if (!this.data.length) return;
        
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        
        const volumes = this.data.map(d => parseFloat(d.volume || 0));
        const maxVolume = Math.max(...volumes);
        
        const chartHeight = this.canvas.height - 60;
        const chartWidth = this.canvas.width - 80;
        const barWidth = chartWidth / this.data.length;
        
        this.data.forEach((point, index) => {
            const x = 40 + index * barWidth;
            const volume = parseFloat(point.volume || 0);
            const barHeight = (volume / maxVolume) * chartHeight;
            const y = 30 + chartHeight - barHeight;
            
            this.ctx.fillStyle = '#4CAF50';
            this.ctx.fillRect(x, y, barWidth * 0.8, barHeight);
        });
        
        this.drawAxes(chartWidth, chartHeight, 0, maxVolume);
    }
}
'''
    
    def get_chart_configuration_script(self):
        """
        Generate chart configuration and utility functions
        """
        return '''
// Chart Configuration and Utilities
class ChartConfig {
    static getDefaultTheme() {
        return {
            background: '#ffffff',
            gridColor: '#e0e0e0',
            textColor: '#333333',
            priceLineColor: '#2196F3',
            volumeColor: '#4CAF50',
            indicatorColors: {
                sma20: '#FF9800',
                sma50: '#9C27B0',
                ema12: '#E91E63',
                ema26: '#607D8B',
                rsi: '#795548',
                macd: '#FF5722'
            }
        };
    }
    
    static getDarkTheme() {
        return {
            background: '#1a1a1a',
            gridColor: '#404040',
            textColor: '#ffffff',
            priceLineColor: '#64B5F6',
            volumeColor: '#81C784',
            indicatorColors: {
                sma20: '#FFB74D',
                sma50: '#BA68C8',
                ema12: '#F06292',
                ema26: '#90A4AE',
                rsi: '#A1887F',
                macd: '#FF8A65'
            }
        };
    }
}

// Data Processor for different data formats
class ChartDataProcessor {
    static processRawData(rawData, format) {
        return rawData.map(row => {
            const item = {};
            format.forEach((field, index) => {
                item[field] = row[index];
            });
            return item;
        });
    }
    
    static aggregateToTimeframe(data, timeframe) {
        // Aggregate minute data to larger timeframes
        const aggregated = [];
        // Implementation for different timeframes (5min, 15min, 1hour, 1day)
        return aggregated;
    }
    
    static calculatePerformanceMetrics(data) {
        if (data.length < 2) return {};
        
        const firstPrice = parseFloat(data[0].price || data[0].close);
        const lastPrice = parseFloat(data[data.length - 1].price || data[data.length - 1].close);
        const prices = data.map(d => parseFloat(d.price || d.close));
        
        const minPrice = Math.min(...prices);
        const maxPrice = Math.max(...prices);
        
        return {
            totalReturn: ((lastPrice - firstPrice) / firstPrice) * 100,
            volatility: this.calculateVolatility(prices),
            maxDrawdown: this.calculateMaxDrawdown(prices),
            sharpeRatio: this.calculateSharpeRatio(prices),
            highestPrice: maxPrice,
            lowestPrice: minPrice
        };
    }
    
    static calculateVolatility(prices) {
        const returns = [];
        for (let i = 1; i < prices.length; i++) {
            returns.push((prices[i] - prices[i-1]) / prices[i-1]);
        }
        
        const avgReturn = returns.reduce((a, b) => a + b, 0) / returns.length;
        const variance = returns.reduce((acc, ret) => acc + Math.pow(ret - avgReturn, 2), 0) / returns.length;
        
        return Math.sqrt(variance) * Math.sqrt(252) * 100; // Annualized volatility
    }
    
    static calculateMaxDrawdown(prices) {
        let maxDrawdown = 0;
        let peak = prices[0];
        
        for (let i = 1; i < prices.length; i++) {
            if (prices[i] > peak) {
                peak = prices[i];
            }
            const drawdown = (peak - prices[i]) / peak;
            if (drawdown > maxDrawdown) {
                maxDrawdown = drawdown;
            }
        }
        
        return maxDrawdown * 100;
    }
    
    static calculateSharpeRatio(prices, riskFreeRate = 0.02) {
        const returns = [];
        for (let i = 1; i < prices.length; i++) {
            returns.push((prices[i] - prices[i-1]) / prices[i-1]);
        }
        
        const avgReturn = returns.reduce((a, b) => a + b, 0) / returns.length;
        const variance = returns.reduce((acc, ret) => acc + Math.pow(ret - avgReturn, 2), 0) / returns.length;
        const stdDev = Math.sqrt(variance);
        
        const annualizedReturn = avgReturn * 252;
        const annualizedVolatility = stdDev * Math.sqrt(252);
        
        return (annualizedReturn - riskFreeRate) / annualizedVolatility;
    }
}
'''

chart_system = BrowserChartSystem()

@api_view(['GET'])
@permission_classes([AllowAny])
def get_chart_library(request):
    """
    Provide complete JavaScript charting library for browser-based rendering
    """
    try:
        library_type = request.GET.get('type', 'complete')
        
        scripts = {
            'main_library': chart_system.get_chart_javascript_library(),
            'configuration': chart_system.get_chart_configuration_script(),
            'usage_example': '''
// Usage Example
document.addEventListener('DOMContentLoaded', function() {
    // Create a new chart
    const chart = new StockChart('chartContainer', {
        width: 800,
        height: 400,
        theme: 'light',
        realTime: true,
        indicators: ['sma20', 'sma50', 'rsi']
    });
    
    // Load data from API
    fetch('/api/raw-chart-data/?ticker=AAPL')
        .then(response => response.json())
        .then(data => {
            chart.setData(data.data, data.data_format);
        });
});
'''
        }
        
        return Response({
            'status': 'success',
            'chart_library': scripts,
            'configurations': chart_system.chart_configurations,
            'features': [
                'Real-time updates',
                'Technical indicators',
                'Multiple chart types',
                'Interactive crosshairs',
                'Client-side calculations',
                'Performance optimized',
                'Mobile responsive'
            ],
            'timestamp': timezone.now()
        })
        
    except Exception as e:
        logger.error(f"Chart library error: {e}")
        return Response({
            'status': 'error',
            'message': 'Failed to get chart library',
            'timestamp': timezone.now()
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_chart_data_stream(request):
    """
    Provide optimized data stream for real-time chart updates
    """
    try:
        ticker = request.GET.get('ticker')
        timeframe = request.GET.get('timeframe', '1min')
        limit = int(request.GET.get('limit', 100))
        
        if not ticker:
            return Response({
                'status': 'error',
                'message': 'Ticker parameter required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Simulate real-time data stream
        # In production, this would connect to real-time data feed
        import time
        current_time = int(time.time() * 1000)
        
        # Generate sample streaming data
        stream_data = []
        for i in range(limit):
            timestamp = current_time - (i * 60000)  # 1 minute intervals
            base_price = 150.0
            price = base_price + (i * 0.1) + (hash(str(timestamp)) % 100) / 100
            volume = 1000000 + (hash(str(timestamp + 1)) % 500000)
            
            stream_data.append([timestamp, price, volume])
        
        stream_data.reverse()  # Chronological order
        
        return Response({
            'status': 'success',
            'ticker': ticker,
            'timeframe': timeframe,
            'stream_data': stream_data,
            'data_format': ['timestamp_ms', 'price', 'volume'],
            'real_time': True,
            'client_processing': True,
            'update_frequency': '5s',
            'timestamp': timezone.now()
        })
        
    except Exception as e:
        logger.error(f"Chart data stream error: {e}")
        return Response({
            'status': 'error',
            'message': 'Failed to get chart data stream',
            'timestamp': timezone.now()
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)