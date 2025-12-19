import React, { useEffect, useRef, useState, useCallback } from 'react';
import { createChart } from 'lightweight-charts';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Tabs, TabsList, TabsTrigger } from './ui/tabs';
import {
  RefreshCw,
  Play,
  Pause,
  Settings,
  Maximize2,
  TrendingUp,
  TrendingDown,
  Activity,
} from 'lucide-react';
import { cn } from '../lib/utils';
import { toast } from 'sonner';

// Client-side stock data fetcher using Yahoo Finance API proxy
const fetchYahooData = async (symbol, interval = '1d', range = '1mo') => {
  try {
    // Using Yahoo Finance public API endpoints
    const response = await fetch(
      `https://query1.finance.yahoo.com/v8/finance/chart/${symbol}?interval=${interval}&range=${range}`,
      { method: 'GET', headers: { 'User-Agent': 'Mozilla/5.0' } }
    );
    const data = await response.json();
    
    if (data.chart?.result?.[0]) {
      const result = data.chart.result[0];
      const timestamps = result.timestamp || [];
      const quotes = result.indicators.quote[0];
      
      return timestamps.map((time, i) => ({
        time,
        open: quotes.open[i],
        high: quotes.high[i],
        low: quotes.low[i],
        close: quotes.close[i],
        volume: quotes.volume[i],
      })).filter(d => d.close !== null);
    }
    return [];
  } catch (error) {
    console.error('Failed to fetch data:', error);
    return [];
  }
};

const INTERVALS = [
  { id: '1m', label: '1M', yahoo: '1m', range: '1d' },
  { id: '5m', label: '5M', yahoo: '5m', range: '5d' },
  { id: '15m', label: '15M', yahoo: '15m', range: '5d' },
  { id: '1h', label: '1H', yahoo: '1h', range: '1mo' },
  { id: '1d', label: '1D', yahoo: '1d', range: '3mo' },
  { id: '1wk', label: '1W', yahoo: '1wk', range: '1y' },
];

export default function EnhancedStockChart({
  symbol,
  height = 500,
  theme = 'light',
  onPriceUpdate,
  className,
}) {
  const containerRef = useRef(null);
  const chartRef = useRef(null);
  const mainSeriesRef = useRef(null);
  const volumeSeriesRef = useRef(null);
  const autoRefreshRef = useRef(null);

  const [interval, setInterval] = useState('1d');
  const [chartData, setChartData] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isAutoRefresh, setIsAutoRefresh] = useState(false);
  const [lastUpdate, setLastUpdate] = useState(null);
  const [priceChange, setPriceChange] = useState({ value: 0, percent: 0 });
  const [currentPrice, setCurrentPrice] = useState(null);

  const fetchData = useCallback(async () => {
    if (!symbol) return;
    
    setIsLoading(true);
    try {
      const intervalConfig = INTERVALS.find(i => i.id === interval);
      const data = await fetchYahooData(
        symbol,
        intervalConfig.yahoo,
        intervalConfig.range
      );
      
      if (data.length > 0) {
        setChartData(data);
        setLastUpdate(new Date());
        
        const latest = data[data.length - 1];
        const previous = data[data.length - 2];
        
        if (latest && previous) {
          const change = latest.close - previous.close;
          const changePercent = (change / previous.close) * 100;
          setPriceChange({ value: change, percent: changePercent });
          setCurrentPrice(latest.close);
          
          if (onPriceUpdate) {
            onPriceUpdate({
              price: latest.close,
              change,
              changePercent,
              volume: latest.volume,
            });
          }
        }
        
        toast.success('Chart updated');
      } else {
        toast.error('No data available');
      }
    } catch (error) {
      toast.error('Failed to fetch chart data');
      console.error(error);
    } finally {
      setIsLoading(false);
    }
  }, [symbol, interval, onPriceUpdate]);

  // Initial fetch
  useEffect(() => {
    fetchData();
  }, [fetchData]);

  // Auto-refresh logic
  useEffect(() => {
    if (isAutoRefresh) {
      // Refresh every 5 seconds for intraday, 30 seconds for daily+
      const refreshInterval = interval.includes('m') || interval.includes('h') ? 5000 : 30000;
      autoRefreshRef.current = setInterval(fetchData, refreshInterval);
      
      return () => {
        if (autoRefreshRef.current) {
          clearInterval(autoRefreshRef.current);
        }
      };
    }
  }, [isAutoRefresh, fetchData, interval]);

  // Initialize chart
  useEffect(() => {
    if (!containerRef.current || chartData.length === 0) return;

    const el = containerRef.current;
    const isDark = theme === 'dark';

    const chart = createChart(el, {
      height,
      autoSize: true,
      layout: {
        background: { color: isDark ? 'rgba(17,24,39,1)' : 'white' },
        textColor: isDark ? '#e5e7eb' : '#111827',
      },
      grid: {
        vertLines: { color: isDark ? 'rgba(55,65,81,0.2)' : 'rgba(229,231,235,0.5)' },
        horzLines: { color: isDark ? 'rgba(55,65,81,0.2)' : 'rgba(229,231,235,0.5)' },
      },
      rightPriceScale: {
        borderColor: isDark ? '#374151' : '#e5e7eb',
        scaleMargins: { top: 0.1, bottom: 0.2 },
      },
      timeScale: {
        borderColor: isDark ? '#374151' : '#e5e7eb',
        timeVisible: true,
        secondsVisible: false,
      },
      crosshair: {
        mode: 1,
        vertLine: {
          color: isDark ? '#6366f1' : '#3b82f6',
          width: 1,
          style: 3,
        },
        horzLine: {
          color: isDark ? '#6366f1' : '#3b82f6',
          width: 1,
          style: 3,
        },
      },
    });
    chartRef.current = chart;

    // Candlestick series
    const candleSeries = chart.addCandlestickSeries({
      upColor: '#10b981',
      downColor: '#ef4444',
      borderVisible: false,
      wickUpColor: '#10b981',
      wickDownColor: '#ef4444',
    });
    
    const formattedData = chartData.map(d => ({
      time: d.time,
      open: d.open,
      high: d.high,
      low: d.low,
      close: d.close,
    }));
    candleSeries.setData(formattedData);
    mainSeriesRef.current = candleSeries;

    // Volume series
    const volumeSeries = chart.addHistogramSeries({
      color: '#60a5fa',
      priceFormat: { type: 'volume' },
      priceScaleId: '',
      scaleMargins: { top: 0.85, bottom: 0 },
    });
    
    const volumeData = chartData.map(d => ({
      time: d.time,
      value: d.volume || 0,
      color: d.close >= d.open ? 'rgba(16, 185, 129, 0.5)' : 'rgba(239, 68, 68, 0.5)',
    }));
    volumeSeries.setData(volumeData);
    volumeSeriesRef.current = volumeSeries;

    chart.timeScale().fitContent();

    return () => {
      try {
        chart.remove();
      } catch {}
      chartRef.current = null;
    };
  }, [chartData, height, theme]);

  const toggleAutoRefresh = () => {
    setIsAutoRefresh(prev => !prev);
    toast.success(isAutoRefresh ? 'Auto-refresh disabled' : 'Auto-refresh enabled');
  };

  return (
    <Card className={cn('overflow-hidden', className)} data-testid="enhanced-stock-chart">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between flex-wrap gap-3">
          <div className="flex items-center gap-3">
            <CardTitle className="text-xl">Live Chart - {symbol}</CardTitle>
            {currentPrice && (
              <div className="flex items-center gap-2">
                <span className="text-2xl font-bold">${currentPrice.toFixed(2)}</span>
                <Badge
                  variant={priceChange.value >= 0 ? 'success' : 'destructive'}
                  className="flex items-center gap-1"
                >
                  {priceChange.value >= 0 ? (
                    <TrendingUp className="h-3 w-3" />
                  ) : (
                    <TrendingDown className="h-3 w-3" />
                  )}
                  {priceChange.value >= 0 ? '+' : ''}{priceChange.value.toFixed(2)} (
                  {priceChange.percent >= 0 ? '+' : ''}{priceChange.percent.toFixed(2)}%)
                </Badge>
              </div>
            )}
          </div>

          <div className="flex items-center gap-2">
            {/* Interval selector */}
            <Tabs value={interval} onValueChange={setInterval} className="w-auto">
              <TabsList className="h-8">
                {INTERVALS.map(int => (
                  <TabsTrigger
                    key={int.id}
                    value={int.id}
                    className="text-xs px-2"
                    data-testid={`interval-${int.id}`}
                  >
                    {int.label}
                  </TabsTrigger>
                ))}
              </TabsList>
            </Tabs>

            {/* Update button */}
            <Button
              variant="outline"
              size="sm"
              onClick={fetchData}
              disabled={isLoading}
              data-testid="update-chart-btn"
            >
              <RefreshCw className={cn('h-4 w-4 mr-2', isLoading && 'animate-spin')} />
              Update
            </Button>

            {/* Auto-refresh toggle */}
            <Button
              variant={isAutoRefresh ? 'default' : 'outline'}
              size="sm"
              onClick={toggleAutoRefresh}
              data-testid="auto-refresh-toggle"
            >
              {isAutoRefresh ? (
                <>
                  <Pause className="h-4 w-4 mr-2" />
                  Live
                </>
              ) : (
                <>
                  <Play className="h-4 w-4 mr-2" />
                  Auto
                </>
              )}
            </Button>
          </div>
        </div>

        {lastUpdate && (
          <div className="flex items-center gap-2 text-xs text-muted-foreground mt-2">
            <Activity className="h-3 w-3" />
            Last updated: {lastUpdate.toLocaleTimeString()}
            {isAutoRefresh && (
              <Badge variant="outline" className="ml-2 animate-pulse">
                Live
              </Badge>
            )}
          </div>
        )}
      </CardHeader>

      <CardContent className="p-0">
        {isLoading && chartData.length === 0 ? (
          <div className="flex items-center justify-center" style={{ height }}>
            <div className="text-center">
              <RefreshCw className="h-8 w-8 animate-spin mx-auto mb-2 text-primary" />
              <p className="text-sm text-muted-foreground">Loading chart data...</p>
            </div>
          </div>
        ) : (
          <div
            ref={containerRef}
            className="w-full"
            style={{ height }}
            data-testid="chart-container"
          />
        )}
      </CardContent>
    </Card>
  );
}
