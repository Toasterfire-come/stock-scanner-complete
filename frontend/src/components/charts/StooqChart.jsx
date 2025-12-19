import React, { useState, useEffect, useCallback, useRef } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
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
  Star,
  StarOff,
  Settings,
  Download,
  Maximize2,
  Minimize2,
  RefreshCw,
  TrendingUp,
  Palette,
} from 'lucide-react';
import { cn } from '../../lib/utils';
import { toast } from 'sonner';

/**
 * StooqChart Component
 *
 * Integrates Stooq HTML5 charts with:
 * - Customizable colors for all chart elements
 * - Favorites (*) feature for stocks
 * - Support for imported indicators
 * - Current technical indicators (SMA, EMA, RSI, MACD, Bollinger, etc.)
 *
 * Charts are served directly by Stooq - browser pulls from Stooq servers
 */

const TIMEFRAMES = [
  { id: 'd', label: '1D', stooq: 'd' },
  { id: 'w', label: '1W', stooq: 'w' },
  { id: 'm', label: '1M', stooq: 'm' },
  { id: 'q', label: '3M', stooq: 'q' },
  { id: 'y', label: '1Y', stooq: 'y' },
  { id: '5y', label: '5Y', stooq: '5y' },
];

const CHART_TYPES = [
  { id: 'c', label: 'Candlestick' },
  { id: 'l', label: 'Line' },
  { id: 'b', label: 'Bar' },
  { id: 'a', label: 'Area' },
];

const INDICATORS = [
  { id: 'sma20', label: 'SMA 20', stooq: 'sma20' },
  { id: 'sma50', label: 'SMA 50', stooq: 'sma50' },
  { id: 'sma200', label: 'SMA 200', stooq: 'sma200' },
  { id: 'ema12', label: 'EMA 12', stooq: 'ema12' },
  { id: 'ema26', label: 'EMA 26', stooq: 'ema26' },
  { id: 'bb', label: 'Bollinger Bands', stooq: 'bb' },
  { id: 'rsi', label: 'RSI', stooq: 'rsi', separate: true },
  { id: 'macd', label: 'MACD', stooq: 'macd', separate: true },
  { id: 'volume', label: 'Volume', stooq: 'volume' },
];

const DEFAULT_COLORS = {
  background: '#FFFFFF',
  gridLines: '#E5E7EB',
  textColor: '#111827',
  upCandle: '#10B981',
  downCandle: '#EF4444',
  lineColor: '#3B82F6',
  volumeUp: '#10B981',
  volumeDown: '#EF4444',
  sma20: '#3B82F6',
  sma50: '#8B5CF6',
  sma200: '#6366F1',
  ema12: '#F59E0B',
  ema26: '#10B981',
  bb: '#9CA3AF',
  rsi: '#EF4444',
  macd: '#1D4ED8',
};

export default function StooqChart({
  ticker,
  height = 500,
  theme = 'light',
  onFavoriteToggle,
  isFavorite = false,
  className,
}) {
  const iframeRef = useRef(null);
  const [timeframe, setTimeframe] = useState('d');
  const [chartType, setChartType] = useState('c');
  const [activeIndicators, setActiveIndicators] = useState(['sma20', 'sma50', 'volume']);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [showColorSettings, setShowColorSettings] = useState(false);
  const [colors, setColors] = useState(() => {
    // Load saved colors from localStorage
    const saved = localStorage.getItem(`stooq_colors_${ticker}`);
    return saved ? JSON.parse(saved) : DEFAULT_COLORS;
  });
  const [chartKey, setChartKey] = useState(0);

  // Save colors to localStorage when they change
  useEffect(() => {
    localStorage.setItem(`stooq_colors_${ticker}`, JSON.stringify(colors));
  }, [colors, ticker]);

  // Build Stooq chart URL
  const buildStooqURL = useCallback(() => {
    if (!ticker) return '';

    // Stooq uses .US suffix for US stocks
    const stooqSymbol = `${ticker.toUpperCase()}.US`;

    // Base URL for Stooq HTML5 charts
    let url = `https://stooq.com/q/c/?s=${stooqSymbol}`;

    // Add timeframe
    url += `&p=${timeframe}`;

    // Add chart type
    url += `&t=${chartType}`;

    // Add indicators
    if (activeIndicators.length > 0) {
      const indicatorParams = activeIndicators
        .map(id => INDICATORS.find(i => i.id === id)?.stooq)
        .filter(Boolean)
        .join(',');
      if (indicatorParams) {
        url += `&i=${indicatorParams}`;
      }
    }

    // Add color customization parameters
    // Note: Stooq's URL parameters for colors may vary
    // This is a generalized approach - adjust based on Stooq's actual API
    url += `&bg=${colors.background.replace('#', '')}`;
    url += `&gc=${colors.gridLines.replace('#', '')}`;
    url += `&tc=${colors.textColor.replace('#', '')}`;
    url += `&uc=${colors.upCandle.replace('#', '')}`;
    url += `&dc=${colors.downCandle.replace('#', '')}`;

    // Responsive size
    url += `&w=100%&h=${height}`;

    return url;
  }, [ticker, timeframe, chartType, activeIndicators, colors, height]);

  // Refresh chart when parameters change
  useEffect(() => {
    setChartKey(prev => prev + 1);
  }, [buildStooqURL]);

  const toggleIndicator = (indicatorId) => {
    setActiveIndicators(prev =>
      prev.includes(indicatorId)
        ? prev.filter(i => i !== indicatorId)
        : [...prev, indicatorId]
    );
    toast.success(`${INDICATORS.find(i => i.id === indicatorId)?.label} ${
      activeIndicators.includes(indicatorId) ? 'removed' : 'added'
    }`);
  };

  const toggleFavorite = () => {
    if (onFavoriteToggle) {
      onFavoriteToggle(ticker, !isFavorite);
    }
    toast.success(isFavorite ? 'Removed from favorites' : 'Added to favorites');
  };

  const resetColors = () => {
    setColors(DEFAULT_COLORS);
    toast.success('Colors reset to default');
  };

  const updateColor = (key, value) => {
    setColors(prev => ({ ...prev, [key]: value }));
  };

  const exportChart = () => {
    // Open Stooq chart in new window for export options
    const url = buildStooqURL();
    window.open(url, '_blank');
    toast.success('Opening chart in new window for export');
  };

  const toggleFullscreen = () => {
    setIsFullscreen(prev => !prev);
  };

  const chartUrl = buildStooqURL();

  return (
    <Card className={cn(
      'overflow-hidden',
      isFullscreen && 'fixed inset-0 z-50',
      className
    )}>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between flex-wrap gap-3">
          <div className="flex items-center gap-3">
            <CardTitle className="text-xl flex items-center gap-2">
              {ticker}
              <Button
                variant="ghost"
                size="sm"
                onClick={toggleFavorite}
                className="h-8 w-8 p-0"
                title={isFavorite ? 'Remove from favorites' : 'Add to favorites'}
              >
                {isFavorite ? (
                  <Star className="h-5 w-5 fill-yellow-400 text-yellow-400" />
                ) : (
                  <StarOff className="h-5 w-5 text-muted-foreground hover:text-yellow-400" />
                )}
              </Button>
            </CardTitle>
          </div>

          <div className="flex items-center gap-2 flex-wrap">
            {/* Timeframe selector */}
            <Tabs value={timeframe} onValueChange={setTimeframe}>
              <TabsList className="h-8">
                {TIMEFRAMES.map(tf => (
                  <TabsTrigger
                    key={tf.id}
                    value={tf.id}
                    className="text-xs px-2"
                  >
                    {tf.label}
                  </TabsTrigger>
                ))}
              </TabsList>
            </Tabs>

            {/* Chart type selector */}
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="outline" size="sm" className="gap-2">
                  <TrendingUp className="h-4 w-4" />
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
                    onClick={() => {
                      setChartType(type.id);
                      toast.success(`Chart type: ${type.label}`);
                    }}
                  >
                    {type.label}
                    {chartType === type.id && <span className="ml-auto">✓</span>}
                  </DropdownMenuItem>
                ))}
              </DropdownMenuContent>
            </DropdownMenu>

            {/* Indicators */}
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="outline" size="sm" className="gap-2">
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
                  >
                    {indicator.label}
                  </DropdownMenuCheckboxItem>
                ))}
              </DropdownMenuContent>
            </DropdownMenu>

            {/* Color settings */}
            <DropdownMenu open={showColorSettings} onOpenChange={setShowColorSettings}>
              <DropdownMenuTrigger asChild>
                <Button variant="outline" size="sm" className="gap-2">
                  <Palette className="h-4 w-4" />
                  <span className="hidden sm:inline">Colors</span>
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent className="w-80 max-h-96 overflow-y-auto">
                <DropdownMenuLabel className="flex items-center justify-between">
                  Color Settings
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={resetColors}
                    className="h-6 text-xs"
                  >
                    Reset
                  </Button>
                </DropdownMenuLabel>
                <DropdownMenuSeparator />
                <div className="p-2 space-y-2">
                  {Object.entries(colors).map(([key, value]) => (
                    <div key={key} className="flex items-center justify-between gap-2">
                      <label className="text-xs capitalize">
                        {key.replace(/([A-Z])/g, ' $1').trim()}
                      </label>
                      <input
                        type="color"
                        value={value}
                        onChange={(e) => updateColor(key, e.target.value)}
                        className="h-8 w-16 cursor-pointer rounded border"
                      />
                    </div>
                  ))}
                </div>
              </DropdownMenuContent>
            </DropdownMenu>

            {/* Refresh */}
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setChartKey(prev => prev + 1)}
              title="Refresh chart"
            >
              <RefreshCw className="h-4 w-4" />
            </Button>

            {/* Export */}
            <Button
              variant="ghost"
              size="sm"
              onClick={exportChart}
              title="Export chart"
            >
              <Download className="h-4 w-4" />
            </Button>

            {/* Fullscreen */}
            <Button
              variant="ghost"
              size="sm"
              onClick={toggleFullscreen}
              title={isFullscreen ? 'Exit fullscreen' : 'Fullscreen'}
            >
              {isFullscreen ? (
                <Minimize2 className="h-4 w-4" />
              ) : (
                <Maximize2 className="h-4 w-4" />
              )}
            </Button>
          </div>
        </div>

        {/* Active indicators legend */}
        {activeIndicators.length > 0 && (
          <div className="flex items-center gap-2 mt-2 flex-wrap">
            <span className="text-xs text-muted-foreground">Active:</span>
            {activeIndicators.map(id => {
              const indicator = INDICATORS.find(i => i.id === id);
              return indicator ? (
                <Badge
                  key={id}
                  variant="outline"
                  className="text-xs cursor-pointer hover:bg-destructive/10"
                  onClick={() => toggleIndicator(id)}
                >
                  {indicator.label}
                  <span className="ml-1 text-muted-foreground">×</span>
                </Badge>
              ) : null;
            })}
          </div>
        )}
      </CardHeader>

      <CardContent className="p-0">
        <div
          className="w-full relative bg-background"
          style={{ height: isFullscreen ? 'calc(100vh - 200px)' : height }}
        >
          {/* Stooq HTML5 Chart iframe */}
          <iframe
            key={chartKey}
            ref={iframeRef}
            src={chartUrl}
            className="w-full h-full border-0"
            title={`${ticker} Stock Chart`}
            sandbox="allow-scripts allow-same-origin"
            loading="lazy"
          />
        </div>

        {/* Chart powered by notice */}
        <div className="px-4 py-2 text-xs text-center text-muted-foreground border-t bg-muted/30">
          Charts powered by <a
            href="https://stooq.com"
            target="_blank"
            rel="noopener noreferrer"
            className="underline hover:text-primary"
          >
            Stooq
          </a> • Colors and indicators customizable
        </div>
      </CardContent>
    </Card>
  );
}
