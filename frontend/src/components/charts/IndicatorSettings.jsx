import React, { useState } from 'react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '../ui/dialog';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Switch } from '../ui/switch';
import { Slider } from '../ui/slider';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { ScrollArea } from '../ui/scroll-area';
import { Badge } from '../ui/badge';
import { Separator } from '../ui/separator';
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from '../ui/accordion';
import { Settings, TrendingUp, BarChart3, Activity } from 'lucide-react';

const IndicatorSettings = ({ indicators = {}, onUpdate, trigger }) => {
  const [localIndicators, setLocalIndicators] = useState(indicators);

  const defaultIndicators = {
    sma20: { enabled: false, period: 20, color: '#3b82f6', lineWidth: 1.5 },
    sma50: { enabled: false, period: 50, color: '#8b5cf6', lineWidth: 1.2 },
    sma200: { enabled: false, period: 200, color: '#6366f1', lineWidth: 1.2 },
    ema12: { enabled: false, period: 12, color: '#f59e0b', lineWidth: 1.2 },
    ema26: { enabled: false, period: 26, color: '#10b981', lineWidth: 1.2 },
    vwap: { enabled: false, color: '#111827', lineWidth: 1.1, style: 'dashed' },
    bb: { enabled: false, period: 20, multiplier: 2, color: '#9ca3af', lineWidth: 1 },
    rsi: { enabled: false, period: 14, overbought: 70, oversold: 30, color: '#111827' },
    macd: { enabled: false, fast: 12, slow: 26, signal: 9, colors: { macd: '#1d4ed8', signal: '#f59e0b', histogram: '#86efac' } },
    volume: { enabled: true, upColor: '#a7f3d0', downColor: '#fecaca' },
  };

  const mergedIndicators = { ...defaultIndicators, ...localIndicators };

  const handleIndicatorChange = (indicatorKey, field, value) => {
    setLocalIndicators(prev => ({
      ...prev,
      [indicatorKey]: {
        ...(prev[indicatorKey] || defaultIndicators[indicatorKey]),
        [field]: value
      }
    }));
  };

  const handleSave = () => {
    if (onUpdate) {
      onUpdate(localIndicators);
    }
  };

  const handleReset = () => {
    setLocalIndicators({});
    if (onUpdate) {
      onUpdate({});
    }
  };

  const renderIndicatorSettings = (key, settings, label, description) => (
    <AccordionItem value={key}>
      <AccordionTrigger className="hover:no-underline">
        <div className="flex items-center justify-between w-full pr-4">
          <div className="flex items-center gap-2">
            <span className="font-medium">{label}</span>
            {settings.enabled && <Badge variant="secondary" className="text-xs">Active</Badge>}
          </div>
        </div>
      </AccordionTrigger>
      <AccordionContent>
        <div className="space-y-4 pt-4">
          <div className="flex items-center justify-between">
            <div>
              <Label className="font-medium">{description}</Label>
            </div>
            <Switch
              checked={settings.enabled}
              onCheckedChange={(checked) => handleIndicatorChange(key, 'enabled', checked)}
            />
          </div>

          {settings.enabled && (
            <div className="space-y-4 pl-4 border-l-2 border-muted">
              {/* Period setting */}
              {settings.period !== undefined && (
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <Label htmlFor={`${key}-period`} className="text-sm">Period</Label>
                    <span className="text-sm font-medium">{settings.period}</span>
                  </div>
                  <Slider
                    id={`${key}-period`}
                    value={[settings.period]}
                    onValueChange={([value]) => handleIndicatorChange(key, 'period', value)}
                    min={5}
                    max={200}
                    step={1}
                    className="w-full"
                  />
                </div>
              )}

              {/* Fast/Slow/Signal for MACD */}
              {settings.fast !== undefined && (
                <>
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <Label htmlFor={`${key}-fast`} className="text-sm">Fast Period</Label>
                      <span className="text-sm font-medium">{settings.fast}</span>
                    </div>
                    <Slider
                      id={`${key}-fast`}
                      value={[settings.fast]}
                      onValueChange={([value]) => handleIndicatorChange(key, 'fast', value)}
                      min={5}
                      max={50}
                      step={1}
                    />
                  </div>
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <Label htmlFor={`${key}-slow`} className="text-sm">Slow Period</Label>
                      <span className="text-sm font-medium">{settings.slow}</span>
                    </div>
                    <Slider
                      id={`${key}-slow`}
                      value={[settings.slow]}
                      onValueChange={([value]) => handleIndicatorChange(key, 'slow', value)}
                      min={10}
                      max={100}
                      step={1}
                    />
                  </div>
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <Label htmlFor={`${key}-signal`} className="text-sm">Signal Period</Label>
                      <span className="text-sm font-medium">{settings.signal}</span>
                    </div>
                    <Slider
                      id={`${key}-signal`}
                      value={[settings.signal]}
                      onValueChange={([value]) => handleIndicatorChange(key, 'signal', value)}
                      min={5}
                      max={50}
                      step={1}
                    />
                  </div>
                </>
              )}

              {/* Multiplier for Bollinger Bands */}
              {settings.multiplier !== undefined && (
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <Label htmlFor={`${key}-multiplier`} className="text-sm">Standard Deviations</Label>
                    <span className="text-sm font-medium">{settings.multiplier}</span>
                  </div>
                  <Slider
                    id={`${key}-multiplier`}
                    value={[settings.multiplier]}
                    onValueChange={([value]) => handleIndicatorChange(key, 'multiplier', value)}
                    min={1}
                    max={4}
                    step={0.1}
                  />
                </div>
              )}

              {/* RSI Levels */}
              {settings.overbought !== undefined && (
                <>
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <Label htmlFor={`${key}-overbought`} className="text-sm">Overbought Level</Label>
                      <span className="text-sm font-medium">{settings.overbought}</span>
                    </div>
                    <Slider
                      id={`${key}-overbought`}
                      value={[settings.overbought]}
                      onValueChange={([value]) => handleIndicatorChange(key, 'overbought', value)}
                      min={50}
                      max={90}
                      step={1}
                    />
                  </div>
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <Label htmlFor={`${key}-oversold`} className="text-sm">Oversold Level</Label>
                      <span className="text-sm font-medium">{settings.oversold}</span>
                    </div>
                    <Slider
                      id={`${key}-oversold`}
                      value={[settings.oversold]}
                      onValueChange={([value]) => handleIndicatorChange(key, 'oversold', value)}
                      min={10}
                      max={50}
                      step={1}
                    />
                  </div>
                </>
              )}

              {/* Color picker */}
              {settings.color && (
                <div className="space-y-2">
                  <Label htmlFor={`${key}-color`} className="text-sm">Color</Label>
                  <div className="flex gap-2">
                    <Input
                      id={`${key}-color`}
                      type="color"
                      value={settings.color}
                      onChange={(e) => handleIndicatorChange(key, 'color', e.target.value)}
                      className="w-20 h-10"
                    />
                    <Input
                      value={settings.color}
                      onChange={(e) => handleIndicatorChange(key, 'color', e.target.value)}
                      className="flex-1"
                      placeholder="#000000"
                    />
                  </div>
                </div>
              )}

              {/* Line width */}
              {settings.lineWidth !== undefined && (
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <Label htmlFor={`${key}-lineWidth`} className="text-sm">Line Width</Label>
                    <span className="text-sm font-medium">{settings.lineWidth}px</span>
                  </div>
                  <Slider
                    id={`${key}-lineWidth`}
                    value={[settings.lineWidth]}
                    onValueChange={([value]) => handleIndicatorChange(key, 'lineWidth', value)}
                    min={0.5}
                    max={5}
                    step={0.1}
                  />
                </div>
              )}
            </div>
          )}
        </div>
      </AccordionContent>
    </AccordionItem>
  );

  return (
    <Dialog>
      <DialogTrigger asChild>
        {trigger || (
          <Button variant="outline" size="sm">
            <Settings className="h-4 w-4 mr-2" />
            Indicator Settings
          </Button>
        )}
      </DialogTrigger>
      <DialogContent className="max-w-2xl max-h-[85vh] p-0">
        <DialogHeader className="p-6 pb-4">
          <DialogTitle className="flex items-center gap-2">
            <Activity className="h-5 w-5" />
            Technical Indicator Settings
          </DialogTitle>
          <DialogDescription>
            Customize technical indicators, periods, and visual styles
          </DialogDescription>
        </DialogHeader>

        <Tabs defaultValue="moving-averages" className="flex-1">
          <div className="px-6">
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="moving-averages">Moving Averages</TabsTrigger>
              <TabsTrigger value="oscillators">Oscillators</TabsTrigger>
              <TabsTrigger value="volume">Volume</TabsTrigger>
            </TabsList>
          </div>

          <ScrollArea className="h-[400px] px-6">
            <TabsContent value="moving-averages" className="mt-4 space-y-2">
              <Accordion type="single" collapsible className="w-full">
                {renderIndicatorSettings('sma20', mergedIndicators.sma20, 'SMA 20', 'Simple Moving Average (20 period)')}
                {renderIndicatorSettings('sma50', mergedIndicators.sma50, 'SMA 50', 'Simple Moving Average (50 period)')}
                {renderIndicatorSettings('sma200', mergedIndicators.sma200, 'SMA 200', 'Simple Moving Average (200 period)')}
                {renderIndicatorSettings('ema12', mergedIndicators.ema12, 'EMA 12', 'Exponential Moving Average (12 period)')}
                {renderIndicatorSettings('ema26', mergedIndicators.ema26, 'EMA 26', 'Exponential Moving Average (26 period)')}
                {renderIndicatorSettings('vwap', mergedIndicators.vwap, 'VWAP', 'Volume Weighted Average Price')}
                {renderIndicatorSettings('bb', mergedIndicators.bb, 'Bollinger Bands', 'Bollinger Bands (volatility indicator)')}
              </Accordion>
            </TabsContent>

            <TabsContent value="oscillators" className="mt-4 space-y-2">
              <Accordion type="single" collapsible className="w-full">
                {renderIndicatorSettings('rsi', mergedIndicators.rsi, 'RSI', 'Relative Strength Index')}
                {renderIndicatorSettings('macd', mergedIndicators.macd, 'MACD', 'Moving Average Convergence Divergence')}
              </Accordion>
            </TabsContent>

            <TabsContent value="volume" className="mt-4 space-y-2">
              <Accordion type="single" collapsible className="w-full">
                {renderIndicatorSettings('volume', mergedIndicators.volume, 'Volume Bars', 'Trading volume visualization')}
              </Accordion>
            </TabsContent>
          </ScrollArea>
        </Tabs>

        <Separator />

        <DialogFooter className="p-6 pt-4">
          <Button variant="outline" onClick={handleReset}>
            Reset to Defaults
          </Button>
          <Button onClick={handleSave}>
            Apply Settings
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

export default IndicatorSettings;
