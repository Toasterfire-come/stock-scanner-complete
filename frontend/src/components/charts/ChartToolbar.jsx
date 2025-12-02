import React from 'react';
import { Button } from '../ui/button';
import {
  Download,
  Maximize2,
  Minimize2,
  Settings,
  Palette,
  Share2,
  Printer,
  Image as ImageIcon,
  TrendingUp,
  BarChart3,
  LineChart as LineChartIcon,
  CandlestickChart
} from 'lucide-react';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
  DropdownMenuCheckboxItem,
  DropdownMenuGroup,
} from '../ui/dropdown-menu';
import { Separator } from '../ui/separator';
import { cn } from '../../lib/utils';

const ChartToolbar = ({
  onExport,
  onFullscreen,
  onSettings,
  onThemeChange,
  onChartTypeChange,
  chartType = 'candlestick',
  isFullscreen = false,
  theme = 'light',
  showIndicators = true,
  onToggleIndicators,
  className,
  compact = false
}) => {
  const handleExportPNG = async () => {
    if (onExport) {
      await onExport('png');
    }
  };

  const handleExportSVG = async () => {
    if (onExport) {
      await onExport('svg');
    }
  };

  const handleExportCSV = async () => {
    if (onExport) {
      await onExport('csv');
    }
  };

  const handlePrint = () => {
    window.print();
  };

  const chartTypes = [
    { value: 'candlestick', label: 'Candlestick', icon: CandlestickChart },
    { value: 'line', label: 'Line', icon: LineChartIcon },
    { value: 'area', label: 'Area', icon: TrendingUp },
    { value: 'bar', label: 'Bar', icon: BarChart3 },
  ];

  const themes = [
    { value: 'light', label: 'Light' },
    { value: 'dark', label: 'Dark' },
    { value: 'high-contrast', label: 'High Contrast' },
    { value: 'colorblind', label: 'Colorblind Friendly' },
  ];

  if (compact) {
    return (
      <div className={cn("flex items-center gap-1", className)}>
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" size="sm">
              <Settings className="h-4 w-4" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="w-56">
            <DropdownMenuLabel>Chart Options</DropdownMenuLabel>
            <DropdownMenuSeparator />

            <DropdownMenuGroup>
              <DropdownMenuLabel className="text-xs">Chart Type</DropdownMenuLabel>
              {chartTypes.map((type) => (
                <DropdownMenuItem
                  key={type.value}
                  onClick={() => onChartTypeChange?.(type.value)}
                >
                  <type.icon className="h-4 w-4 mr-2" />
                  {type.label}
                  {chartType === type.value && <span className="ml-auto">✓</span>}
                </DropdownMenuItem>
              ))}
            </DropdownMenuGroup>

            <DropdownMenuSeparator />

            <DropdownMenuGroup>
              <DropdownMenuLabel className="text-xs">Theme</DropdownMenuLabel>
              {themes.map((t) => (
                <DropdownMenuItem
                  key={t.value}
                  onClick={() => onThemeChange?.(t.value)}
                >
                  {t.label}
                  {theme === t.value && <span className="ml-auto">✓</span>}
                </DropdownMenuItem>
              ))}
            </DropdownMenuGroup>

            <DropdownMenuSeparator />

            {showIndicators !== undefined && (
              <>
                <DropdownMenuCheckboxItem
                  checked={showIndicators}
                  onCheckedChange={onToggleIndicators}
                >
                  Show Indicators
                </DropdownMenuCheckboxItem>
                <DropdownMenuSeparator />
              </>
            )}

            <DropdownMenuItem onClick={handleExportPNG}>
              <ImageIcon className="h-4 w-4 mr-2" />
              Export as PNG
            </DropdownMenuItem>
            <DropdownMenuItem onClick={handleExportSVG}>
              <Download className="h-4 w-4 mr-2" />
              Export as SVG
            </DropdownMenuItem>
            <DropdownMenuItem onClick={handleExportCSV}>
              <Download className="h-4 w-4 mr-2" />
              Export Data (CSV)
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>

        <Button
          variant="ghost"
          size="sm"
          onClick={onFullscreen}
          title={isFullscreen ? "Exit fullscreen" : "Fullscreen"}
        >
          {isFullscreen ? <Minimize2 className="h-4 w-4" /> : <Maximize2 className="h-4 w-4" />}
        </Button>
      </div>
    );
  }

  return (
    <div className={cn("flex items-center gap-2 p-2 border-b bg-muted/30", className)}>
      {/* Chart Type Selector */}
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button variant="outline" size="sm" className="gap-2">
            {React.createElement(
              chartTypes.find(t => t.value === chartType)?.icon || CandlestickChart,
              { className: "h-4 w-4" }
            )}
            <span className="hidden sm:inline">
              {chartTypes.find(t => t.value === chartType)?.label || 'Chart'}
            </span>
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent>
          <DropdownMenuLabel>Chart Type</DropdownMenuLabel>
          <DropdownMenuSeparator />
          {chartTypes.map((type) => (
            <DropdownMenuItem
              key={type.value}
              onClick={() => onChartTypeChange?.(type.value)}
              className="gap-2"
            >
              <type.icon className="h-4 w-4" />
              {type.label}
              {chartType === type.value && <span className="ml-auto text-primary">✓</span>}
            </DropdownMenuItem>
          ))}
        </DropdownMenuContent>
      </DropdownMenu>

      <Separator orientation="vertical" className="h-6" />

      {/* Theme Selector */}
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button variant="outline" size="sm" className="gap-2">
            <Palette className="h-4 w-4" />
            <span className="hidden sm:inline">Theme</span>
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent>
          <DropdownMenuLabel>Chart Theme</DropdownMenuLabel>
          <DropdownMenuSeparator />
          {themes.map((t) => (
            <DropdownMenuItem
              key={t.value}
              onClick={() => onThemeChange?.(t.value)}
            >
              {t.label}
              {theme === t.value && <span className="ml-auto text-primary">✓</span>}
            </DropdownMenuItem>
          ))}
        </DropdownMenuContent>
      </DropdownMenu>

      {/* Indicators Toggle */}
      {showIndicators !== undefined && (
        <Button
          variant={showIndicators ? "default" : "outline"}
          size="sm"
          onClick={onToggleIndicators}
          className="gap-2"
        >
          <TrendingUp className="h-4 w-4" />
          <span className="hidden sm:inline">Indicators</span>
        </Button>
      )}

      <Separator orientation="vertical" className="h-6" />

      {/* Export Options */}
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button variant="outline" size="sm" className="gap-2">
            <Download className="h-4 w-4" />
            <span className="hidden sm:inline">Export</span>
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent>
          <DropdownMenuLabel>Export Options</DropdownMenuLabel>
          <DropdownMenuSeparator />
          <DropdownMenuItem onClick={handleExportPNG} className="gap-2">
            <ImageIcon className="h-4 w-4" />
            Export as PNG
          </DropdownMenuItem>
          <DropdownMenuItem onClick={handleExportSVG} className="gap-2">
            <Download className="h-4 w-4" />
            Export as SVG
          </DropdownMenuItem>
          <DropdownMenuSeparator />
          <DropdownMenuItem onClick={handleExportCSV} className="gap-2">
            <Download className="h-4 w-4" />
            Export Data (CSV)
          </DropdownMenuItem>
          <DropdownMenuSeparator />
          <DropdownMenuItem onClick={handlePrint} className="gap-2">
            <Printer className="h-4 w-4" />
            Print Chart
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>

      {/* Settings */}
      {onSettings && (
        <Button variant="outline" size="sm" onClick={onSettings} className="gap-2">
          <Settings className="h-4 w-4" />
          <span className="hidden sm:inline">Settings</span>
        </Button>
      )}

      {/* Spacer */}
      <div className="flex-1" />

      {/* Share Button */}
      <Button variant="ghost" size="sm" className="gap-2">
        <Share2 className="h-4 w-4" />
        <span className="hidden sm:inline">Share</span>
      </Button>

      {/* Fullscreen */}
      <Button
        variant="ghost"
        size="sm"
        onClick={onFullscreen}
        title={isFullscreen ? "Exit fullscreen" : "Fullscreen"}
      >
        {isFullscreen ? <Minimize2 className="h-4 w-4" /> : <Maximize2 className="h-4 w-4" />}
      </Button>
    </div>
  );
};

export default ChartToolbar;
