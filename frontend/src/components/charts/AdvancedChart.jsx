import React, { useEffect, useRef, useState, useMemo, useCallback } from 'react';
import { createChart } from 'lightweight-charts';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { Tabs, TabsList, TabsTrigger } from '../ui/tabs';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
  DropdownMenuSeparator,
  DropdownMenuLabel,
  DropdownMenuCheckboxItem,
} from '../ui/dropdown-menu';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '../ui/tooltip';
import {
  CandlestickChart,
  LineChart,
  AreaChart,
  BarChart3,
  TrendingUp,
  Settings,
  Download,
  Maximize2,
  Minimize2,
  RefreshCw,
  Lock,
  Ruler,
  Minus,
  Square,
} from 'lucide-react';
import { cn } from '../../lib/utils';
import { api } from '../../api/client';

const TIMEFRAMES = [
  { id: '1m', label: '1M', premium: true },
  { id: '5m', label: '5M', premium: true },
  { id: '15m', label: '15M', premium: false },
  { id: '30m', label: '30M', premium: false },
  { id: '1h', label: '1H', premium: false },
  { id: '4h', label: '4H', premium: true },
  { id: '1d', label: '1D', premium: false },
  { id: '1wk', label: '1W', premium: false },
  { id: '1mo', label: '1M', premium: false },
];

const CHART_TYPES = [
  { id: 'candlestick', label: 'Candlestick', icon: CandlestickChart, premium: false },
  { id: 'line', label: 'Line', icon: LineChart, premium: false },
  { id: 'area', label: 'Area', icon: AreaChart, premium: false },
  { id: 'heikin_ashi', label: 'Heikin-Ashi', icon: BarChart3, premium: true },
];

const INDICATORS = [
  { id: 'sma_20', label: 'SMA 20', color: '#3b82f6', premium: false },
  { id: 'sma_50', label: 'SMA 50', color: '#8b5cf6', premium: false },
  { id: 'sma_200', label: 'SMA 200', color: '#6366f1', premium: false },
  { id: 'ema_12', label: 'EMA 12', color: '#f59e0b', premium: false },
  { id: 'ema_26', label: 'EMA 26', color: '#10b981', premium: false },
  { id: 'rsi', label: 'RSI', color: '#ef4444', premium: false, separate: true },
  { id: 'macd', label: 'MACD', color: '#1d4ed8', premium: true, separate: true },
  { id: 'bollinger', label: 'Bollinger Bands', color: '#9ca3af', premium: true },
  { id: 'vwap', label: 'VWAP', color: '#111827', premium: true },
];

const DRAWING_TOOLS = [
  { id: 'trend_line', label: 'Trend Line', icon: TrendingUp, premium: false },
  { id: 'horizontal_line', label: 'Horizontal Line', icon: Minus, premium: false },
  { id: 'rectangle', label: 'Rectangle', icon: Square, premium: true },
  { id: 'fibonacci', label: 'Fibonacci', icon: Ruler, premium: true },
];

export default function AdvancedChart({
  ticker,
  height = 500,
  theme = 'light',
  isPremium = false,
  onReady,
  className,
}) {
  const containerRef = useRef(null);
  const chartRef = useRef(null);
  const mainSeriesRef = useRef(null);
  const indicatorSeriesRef = useRef({});
  const rsiChartRef = useRef(null);
  const rsiSeriesRef = useRef(null);

  const [timeframe, setTimeframe] = useState('1d');
  const [chartType, setChartType] = useState('candlestick');
  const [activeIndicators, setActiveIndicators] = useState(['sma_20', 'sma_50']);
  const [isLoading, setIsLoading] = useState(false);
  const [chartData, setChartData] = useState([]);
  const [indicatorData, setIndicatorData] = useState({});
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [error, setError] = useState(null);
  const [activeTool, setActiveTool] = useState(null);

  // Fetch chart data
  const fetchChartData = useCallback(async () => {
    if (!ticker) return;
    setIsLoading(true);
    setError(null);
    try {
      const { data: response } = await api.get(`/chart/${ticker}/`, {
        params: { timeframe, chart_type: chartType }
      });
      if (response.success && response.data) {
        setChartData(response.data.data || []);
      } else {
        setError(response.error || 'Failed to load chart data');
      }
    } catch (err) {
      setError(err.message || 'Failed to load chart data');
    } finally {
      setIsLoading(false);
    }
  }, [ticker, timeframe, chartType]);

  // Fetch indicators
  const fetchIndicators = useCallback(async () => {
    if (!ticker || activeIndicators.length === 0) {
      setIndicatorData({});
      return;
    }
    try {
      const { data: response } = await api.get(`/chart/${ticker}/indicators/`, {
        params: { timeframe, indicators: activeIndicators.join(',') }
      });
      if (response.success && response.data) {
        setIndicatorData(response.data.indicators || {});
      }
    } catch (err) {
      console.error('Failed to load indicators:', err);
    }
  }, [ticker, timeframe, activeIndicators]);

  useEffect(() => {
    fetchChartData();
  }, [fetchChartData]);

  useEffect(() => {
    if (chartData.length > 0) {
      fetchIndicators();
    }
  }, [chartData, fetchIndicators]);

  // Initialize chart
  useEffect(() => {
    if (!containerRef.current || chartData.length === 0) return;

    const el = containerRef.current;
    const isDark = theme === 'dark';

    // Create main chart
    const chart = createChart(el, {
      height: isFullscreen ? window.innerHeight - 100 : height,
      autoSize: true,
      layout: {
        background: { color: isDark ? 'rgba(17,24,39,1)' : 'white' },
        textColor: isDark ? '#e5e7eb' : '#111827',
      },
      grid: {
        vertLines: { color: isDark ? 'rgba(55,65,81,0.3)' : 'rgba(229,231,235,0.7)' },
        horzLines: { color: isDark ? 'rgba(55,65,81,0.3)' : 'rgba(229,231,235,0.7)' },
      },
      rightPriceScale: { borderColor: isDark ? '#374151' : '#e5e7eb' },
      timeScale: { borderColor: isDark ? '#374151' : '#e5e7eb', timeVisible: true },
      crosshair: { mode: 1 },
    });
    chartRef.current = chart;

    // Create main series based on chart type
    let mainSeries;
    const formattedData = chartData.map(d => ({
      time: Math.floor(d.time / 1000),
      ...(chartType === 'candlestick' || chartType === 'heikin_ashi'
        ? { open: d.open, high: d.high, low: d.low, close: d.close }
        : { value: d.close || d.value })
    }));

    if (chartType === 'candlestick' || chartType === 'heikin_ashi') {
      mainSeries = chart.addCandlestickSeries({
        upColor: '#16a34a',
        downColor: '#dc2626',
        borderVisible: false,
        wickUpColor: '#16a34a',
        wickDownColor: '#dc2626',
      });
    } else if (chartType === 'line') {
      mainSeries = chart.addLineSeries({
        color: '#2563eb',
        lineWidth: 2,
      });
    } else {
      mainSeries = chart.addAreaSeries({
        lineColor: '#2563eb',
        topColor: 'rgba(37,99,235,0.25)',
        bottomColor: 'rgba(37,99,235,0.01)',
        lineWidth: 2,
      });
    }
    mainSeries.setData(formattedData);
    mainSeriesRef.current = mainSeries;

    // Add volume
    const volumeSeries = chart.addHistogramSeries({
      color: '#60a5fa',
      priceFormat: { type: 'volume' },
      priceScaleId: 'volume',
      scaleMargins: { top: 0.85, bottom: 0 },
    });
    volumeSeries.setData(chartData.map(d => ({
      time: Math.floor(d.time / 1000),
      value: d.volume || 0,
      color: d.close >= d.open ? 'rgba(34,197,94,0.4)' : 'rgba(239,68,68,0.4)',
    })));

    chart.timeScale().fitContent();

    if (typeof onReady === 'function') {
      onReady({ chart, mainSeries });
    }

    return () => {
      try {
        Object.values(indicatorSeriesRef.current).forEach(s => {
          try { chart.removeSeries(s); } catch {}
        });
        chart.remove();
      } catch {}
      chartRef.current = null;
      mainSeriesRef.current = null;
      indicatorSeriesRef.current = {};
    };
  }, [chartData, chartType, height, theme, isFullscreen]);

  // Update indicators on chart
  useEffect(() => {
    const chart = chartRef.current;
    if (!chart) return;

    // Remove old indicator series
    Object.entries(indicatorSeriesRef.current).forEach(([key, series]) => {
      if (!activeIndicators.includes(key)) {
        try { chart.removeSeries(series); } catch {}
        delete indicatorSeriesRef.current[key];
      }
    });

    // Add new indicator series
    Object.entries(indicatorData).forEach(([key, data]) => {
      if (!activeIndicators.includes(key) || indicatorSeriesRef.current[key]) return;

      const indicatorConfig = INDICATORS.find(i => i.id === key);
      if (!indicatorConfig) return;

      if (key === 'bollinger' && data.upper && data.middle && data.lower) {
        // Bollinger bands - 3 lines
        const upperSeries = chart.addLineSeries({ color: indicatorConfig.color, lineWidth: 1, lineStyle: 2 });
        const middleSeries = chart.addLineSeries({ color: indicatorConfig.color, lineWidth: 1 });
        const lowerSeries = chart.addLineSeries({ color: indicatorConfig.color, lineWidth: 1, lineStyle: 2 });
        upperSeries.setData(data.upper.map(d => ({ time: Math.floor(d.time / 1000), value: d.value })));
        middleSeries.setData(data.middle.map(d => ({ time: Math.floor(d.time / 1000), value: d.value })));
        lowerSeries.setData(data.lower.map(d => ({ time: Math.floor(d.time / 1000), value: d.value })));
        indicatorSeriesRef.current[key] = { upper: upperSeries, middle: middleSeries, lower: lowerSeries };
      } else if (Array.isArray(data)) {
        const series = chart.addLineSeries({ color: indicatorConfig.color, lineWidth: 1.5 });
        series.setData(data.map(d => ({ time: Math.floor(d.time / 1000), value: d.value })));
        indicatorSeriesRef.current[key] = series;
      }
    });
  }, [indicatorData, activeIndicators]);

  const toggleIndicator = (indicatorId) => {
    const indicator = INDICATORS.find(i => i.id === indicatorId);
    if (indicator?.premium && !isPremium) return;

    setActiveIndicators(prev =>
      prev.includes(indicatorId)
        ? prev.filter(i => i !== indicatorId)
        : [...prev, indicatorId]
    );
  };

  const handleTimeframeChange = (tf) => {
    const config = TIMEFRAMES.find(t => t.id === tf);
    if (config?.premium && !isPremium) return;
    setTimeframe(tf);
  };

  const handleChartTypeChange = (type) => {
    const config = CHART_TYPES.find(t => t.id === type);
    if (config?.premium && !isPremium) return;
    setChartType(type);
  };

  const handleExport = async (format) => {
    const chart = chartRef.current;
    if (!chart || !containerRef.current) return;

    if (format === 'png') {
      try {
        const canvas = containerRef.current.querySelector('canvas');
        if (canvas) {
          const link = document.createElement('a');
          link.download = `${ticker}_chart_${timeframe}.png`;
          link.href = canvas.toDataURL('image/png');
          link.click();
        }
      } catch (err) {
        console.error('Export failed:', err);
      }
    } else if (format === 'csv') {
      const csv = ['Time,Open,High,Low,Close,Volume'];
      chartData.forEach(d => {
        csv.push(`${new Date(d.time).toISOString()},${d.open},${d.high},${d.low},${d.close},${d.volume}`);
      });
      const blob = new Blob([csv.join('\n')], { type: 'text/csv' });
      const link = document.createElement('a');
      link.download = `${ticker}_data_${timeframe}.csv`;
      link.href = URL.createObjectURL(blob);
      link.click();
    }
  };

  const toggleFullscreen = () => {
    setIsFullscreen(prev => !prev);
  };

  return (
    <div className={cn(
      'relative border rounded-lg overflow-hidden bg-background',
      isFullscreen && 'fixed inset-0 z-50',
      className
    )}>
      {/* Toolbar */}
      <div className="flex items-center justify-between p-2 border-b bg-muted/30 flex-wrap gap-2">
        <div className="flex items-center gap-2">
          {/* Timeframe selector */}
          <Tabs value={timeframe} onValueChange={handleTimeframeChange}>
            <TabsList className="h-8">
              {TIMEFRAMES.map(tf => (
                <TabsTrigger
                  key={tf.id}
                  value={tf.id}
                  disabled={tf.premium && !isPremium}
                  className="relative text-xs px-2"
                  data-testid={`timeframe-${tf.id}`}
                >
                  {tf.label}
                  {tf.premium && !isPremium && (
                    <Lock className="h-2.5 w-2.5 ml-0.5 text-muted-foreground" />
                  )}
                </TabsTrigger>
              ))}
            </TabsList>
          </Tabs>

          {/* Chart type selector */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="outline" size="sm" className="gap-2" data-testid="chart-type-selector">
                {React.createElement(
                  CHART_TYPES.find(t => t.id === chartType)?.icon || CandlestickChart,
                  { className: 'h-4 w-4' }
                )}
                <span className="hidden sm:inline">
                  {CHART_TYPES.find(t => t.id === chartType)?.label}
                </span>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent>
              <DropdownMenuLabel>Chart Type</DropdownMenuLabel>
              <DropdownMenuSeparator />
              {CHART_TYPES.map(type => (
                <DropdownMenuItem
                  key={type.id}
                  onClick={() => handleChartTypeChange(type.id)}
                  disabled={type.premium && !isPremium}
                  className="gap-2"
                >
                  <type.icon className="h-4 w-4" />
                  {type.label}
                  {type.premium && !isPremium && <Lock className="h-3 w-3 ml-auto" />}
                  {chartType === type.id && <span className="ml-auto">✓</span>}
                </DropdownMenuItem>
              ))}
            </DropdownMenuContent>
          </DropdownMenu>
        </div>

        <div className="flex items-center gap-2">
          {/* Indicators */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="outline" size="sm" className="gap-2" data-testid="indicators-selector">
                <TrendingUp className="h-4 w-4" />
                <span className="hidden sm:inline">Indicators</span>
                {activeIndicators.length > 0 && (
                  <Badge variant="secondary" className="ml-1">
                    {activeIndicators.length}
                  </Badge>
                )}
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent className="w-56">
              <DropdownMenuLabel>Technical Indicators</DropdownMenuLabel>
              <DropdownMenuSeparator />
              {INDICATORS.map(indicator => (
                <DropdownMenuCheckboxItem
                  key={indicator.id}
                  checked={activeIndicators.includes(indicator.id)}
                  onCheckedChange={() => toggleIndicator(indicator.id)}
                  disabled={indicator.premium && !isPremium}
                  className="gap-2"
                >
                  <span
                    className="w-3 h-3 rounded-full mr-2"
                    style={{ backgroundColor: indicator.color }}
                  />
                  {indicator.label}
                  {indicator.premium && !isPremium && <Lock className="h-3 w-3 ml-auto" />}
                </DropdownMenuCheckboxItem>
              ))}
            </DropdownMenuContent>
          </DropdownMenu>

          {/* Drawing tools */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="outline" size="sm" className="gap-2" data-testid="drawing-tools">
                <Ruler className="h-4 w-4" />
                <span className="hidden sm:inline">Draw</span>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent>
              <DropdownMenuLabel>Drawing Tools</DropdownMenuLabel>
              <DropdownMenuSeparator />
              {DRAWING_TOOLS.map(tool => (
                <DropdownMenuItem
                  key={tool.id}
                  onClick={() => setActiveTool(tool.id)}
                  disabled={tool.premium && !isPremium}
                  className="gap-2"
                >
                  <tool.icon className="h-4 w-4" />
                  {tool.label}
                  {tool.premium && !isPremium && <Lock className="h-3 w-3 ml-auto" />}
                </DropdownMenuItem>
              ))}
            </DropdownMenuContent>
          </DropdownMenu>

          {/* Refresh */}
          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger asChild>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={fetchChartData}
                  disabled={isLoading}
                  data-testid="refresh-chart"
                >
                  <RefreshCw className={cn('h-4 w-4', isLoading && 'animate-spin')} />
                </Button>
              </TooltipTrigger>
              <TooltipContent>Refresh data</TooltipContent>
            </Tooltip>
          </TooltipProvider>

          {/* Export */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" size="sm" data-testid="export-chart">
                <Download className="h-4 w-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent>
              <DropdownMenuItem onClick={() => handleExport('png')}>
                Export as PNG
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => handleExport('csv')}>
                Export Data (CSV)
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>

          {/* Fullscreen */}
          <Button
            variant="ghost"
            size="sm"
            onClick={toggleFullscreen}
            data-testid="fullscreen-chart"
          >
            {isFullscreen ? <Minimize2 className="h-4 w-4" /> : <Maximize2 className="h-4 w-4" />}
          </Button>
        </div>
      </div>

      {/* Chart container */}
      <div className="relative">
        {isLoading && (
          <div className="absolute inset-0 flex items-center justify-center bg-background/50 z-10">
            <RefreshCw className="h-8 w-8 animate-spin text-primary" />
          </div>
        )}
        {error && (
          <div className="absolute inset-0 flex items-center justify-center bg-background/50 z-10">
            <div className="text-center text-destructive">
              <p>{error}</p>
              <Button variant="outline" size="sm" onClick={fetchChartData} className="mt-2">
                Retry
              </Button>
            </div>
          </div>
        )}
        <div
          ref={containerRef}
          className="w-full"
          style={{ height: isFullscreen ? 'calc(100vh - 100px)' : height }}
          data-testid="chart-container"
        />
      </div>

      {/* Active indicators legend */}
      {activeIndicators.length > 0 && (
        <div className="flex items-center gap-2 p-2 border-t flex-wrap">
          <span className="text-xs text-muted-foreground">Active:</span>
          {activeIndicators.map(id => {
            const indicator = INDICATORS.find(i => i.id === id);
            return indicator ? (
              <Badge
                key={id}
                variant="outline"
                className="gap-1 cursor-pointer"
                onClick={() => toggleIndicator(id)}
              >
                <span
                  className="w-2 h-2 rounded-full"
                  style={{ backgroundColor: indicator.color }}
                />
                {indicator.label}
                <span className="text-muted-foreground">×</span>
              </Badge>
            ) : null;
          })}
        </div>
      )}
    </div>
  );
}
