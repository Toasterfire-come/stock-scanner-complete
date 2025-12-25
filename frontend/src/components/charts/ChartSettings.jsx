import React, { useState } from 'react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
  DialogFooter,
} from '../ui/dialog';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { ScrollArea } from '../ui/scroll-area';
import { Badge } from '../ui/badge';
import { Settings, Upload, Download, Trash2, Plus } from 'lucide-react';
import { toast } from 'sonner';
import logger from '../../lib/logger';

/**
 * ChartSettings Component
 *
 * Advanced settings for Stooq charts including:
 * - Custom indicator imports
 * - Color scheme management
 * - Chart preferences
 * - Export/import settings
 */

const DEFAULT_INDICATORS = [
  { id: 'sma20', name: 'SMA 20', type: 'overlay', params: { period: 20 } },
  { id: 'sma50', name: 'SMA 50', type: 'overlay', params: { period: 50 } },
  { id: 'sma200', name: 'SMA 200', type: 'overlay', params: { period: 200 } },
  { id: 'ema12', name: 'EMA 12', type: 'overlay', params: { period: 12 } },
  { id: 'ema26', name: 'EMA 26', type: 'overlay', params: { period: 26 } },
  { id: 'bb', name: 'Bollinger Bands', type: 'overlay', params: { period: 20, deviation: 2 } },
  { id: 'rsi', name: 'RSI', type: 'oscillator', params: { period: 14 } },
  { id: 'macd', name: 'MACD', type: 'oscillator', params: { fast: 12, slow: 26, signal: 9 } },
  { id: 'stoch', name: 'Stochastic', type: 'oscillator', params: { k: 14, d: 3 } },
  { id: 'atr', name: 'ATR', type: 'indicator', params: { period: 14 } },
  { id: 'adx', name: 'ADX', type: 'indicator', params: { period: 14 } },
  { id: 'obv', name: 'OBV', type: 'indicator', params: {} },
];

export default function ChartSettings({ onSave, initialSettings = {} }) {
  const [customIndicators, setCustomIndicators] = useState(() => {
    const saved = localStorage.getItem('stooq_custom_indicators');
    return saved ? JSON.parse(saved) : [];
  });

  const [newIndicator, setNewIndicator] = useState({
    name: '',
    type: 'overlay',
    formula: '',
    params: {},
  });

  const [colorSchemes, setColorSchemes] = useState(() => {
    const saved = localStorage.getItem('stooq_color_schemes');
    return saved ? JSON.parse(saved) : [
      {
        id: 'default',
        name: 'Default',
        colors: {
          background: '#FFFFFF',
          gridLines: '#E5E7EB',
          textColor: '#111827',
          upCandle: '#10B981',
          downCandle: '#EF4444',
        },
      },
      {
        id: 'dark',
        name: 'Dark Mode',
        colors: {
          background: '#111827',
          gridLines: '#374151',
          textColor: '#F3F4F6',
          upCandle: '#10B981',
          downCandle: '#EF4444',
        },
      },
      {
        id: 'high_contrast',
        name: 'High Contrast',
        colors: {
          background: '#000000',
          gridLines: '#FFFFFF',
          textColor: '#FFFFFF',
          upCandle: '#00FF00',
          downCandle: '#FF0000',
        },
      },
    ];
  });

  const [newSchemeName, setNewSchemeName] = useState('');

  // Save custom indicators to localStorage
  const saveCustomIndicators = (indicators) => {
    setCustomIndicators(indicators);
    localStorage.setItem('stooq_custom_indicators', JSON.stringify(indicators));
    toast.success('Custom indicators saved');
  };

  // Add new custom indicator
  const addCustomIndicator = () => {
    if (!newIndicator.name.trim()) {
      toast.error('Indicator name is required');
      return;
    }

    const indicator = {
      id: `custom_${Date.now()}`,
      ...newIndicator,
      custom: true,
    };

    saveCustomIndicators([...customIndicators, indicator]);
    setNewIndicator({ name: '', type: 'overlay', formula: '', params: {} });
    toast.success(`Custom indicator "${indicator.name}" added`);
  };

  // Remove custom indicator
  const removeCustomIndicator = (id) => {
    const filtered = customIndicators.filter(i => i.id !== id);
    saveCustomIndicators(filtered);
    toast.success('Custom indicator removed');
  };

  // Export settings
  const exportSettings = () => {
    const settings = {
      customIndicators,
      colorSchemes,
      version: '1.0',
      exportedAt: new Date().toISOString(),
    };

    const blob = new Blob([JSON.stringify(settings, null, 2)], {
      type: 'application/json',
    });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `stooq_chart_settings_${Date.now()}.json`;
    link.click();
    URL.revokeObjectURL(url);

    toast.success('Settings exported');
  };

  // Import settings
  const importSettings = (event) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const settings = JSON.parse(e.target.result);

        if (settings.customIndicators) {
          saveCustomIndicators(settings.customIndicators);
        }

        if (settings.colorSchemes) {
          setColorSchemes(settings.colorSchemes);
          localStorage.setItem('stooq_color_schemes', JSON.stringify(settings.colorSchemes));
        }

        toast.success('Settings imported successfully');
      } catch (error) {
        toast.error('Failed to import settings');
        logger.error(error);
      }
    };
    reader.readAsText(file);
  };

  // Add new color scheme
  const addColorScheme = () => {
    if (!newSchemeName.trim()) {
      toast.error('Scheme name is required');
      return;
    }

    const scheme = {
      id: `scheme_${Date.now()}`,
      name: newSchemeName,
      colors: {
        background: '#FFFFFF',
        gridLines: '#E5E7EB',
        textColor: '#111827',
        upCandle: '#10B981',
        downCandle: '#EF4444',
      },
      custom: true,
    };

    const updated = [...colorSchemes, scheme];
    setColorSchemes(updated);
    localStorage.setItem('stooq_color_schemes', JSON.stringify(updated));
    setNewSchemeName('');
    toast.success(`Color scheme "${scheme.name}" added`);
  };

  const allIndicators = [...DEFAULT_INDICATORS, ...customIndicators];

  return (
    <Dialog>
      <DialogTrigger asChild>
        <Button variant="outline" size="sm" className="gap-2">
          <Settings className="h-4 w-4" />
          <span className="hidden sm:inline">Chart Settings</span>
        </Button>
      </DialogTrigger>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-hidden flex flex-col">
        <DialogHeader>
          <DialogTitle>Chart Settings</DialogTitle>
          <DialogDescription>
            Customize indicators, colors, and import custom settings
          </DialogDescription>
        </DialogHeader>

        <Tabs defaultValue="indicators" className="flex-1 flex flex-col overflow-hidden">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="indicators">Indicators</TabsTrigger>
            <TabsTrigger value="colors">Color Schemes</TabsTrigger>
            <TabsTrigger value="import-export">Import/Export</TabsTrigger>
          </TabsList>

          <TabsContent value="indicators" className="flex-1 overflow-hidden flex flex-col space-y-4">
            <ScrollArea className="flex-1 pr-4">
              {/* Built-in indicators */}
              <div className="space-y-2">
                <h3 className="text-sm font-semibold">Built-in Indicators</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                  {DEFAULT_INDICATORS.map(indicator => (
                    <div
                      key={indicator.id}
                      className="flex items-center justify-between p-3 border rounded-lg"
                    >
                      <div>
                        <p className="font-medium text-sm">{indicator.name}</p>
                        <p className="text-xs text-muted-foreground">
                          Type: {indicator.type}
                        </p>
                      </div>
                      <Badge variant="secondary">{indicator.type}</Badge>
                    </div>
                  ))}
                </div>
              </div>

              {/* Custom indicators */}
              {customIndicators.length > 0 && (
                <div className="space-y-2 mt-6">
                  <h3 className="text-sm font-semibold">Custom Indicators</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                    {customIndicators.map(indicator => (
                      <div
                        key={indicator.id}
                        className="flex items-center justify-between p-3 border rounded-lg"
                      >
                        <div>
                          <p className="font-medium text-sm">{indicator.name}</p>
                          <p className="text-xs text-muted-foreground">
                            {indicator.formula ? `Formula: ${indicator.formula.substring(0, 30)}...` : 'Custom indicator'}
                          </p>
                        </div>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => removeCustomIndicator(indicator.id)}
                          className="h-8 w-8 p-0"
                        >
                          <Trash2 className="h-4 w-4 text-destructive" />
                        </Button>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Add new custom indicator */}
              <div className="space-y-3 mt-6 p-4 border rounded-lg bg-muted/50">
                <h3 className="text-sm font-semibold">Add Custom Indicator</h3>
                <div className="grid gap-3">
                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <Label htmlFor="indicator-name">Name</Label>
                      <Input
                        id="indicator-name"
                        placeholder="e.g., Custom MA"
                        value={newIndicator.name}
                        onChange={(e) => setNewIndicator({...newIndicator, name: e.target.value})}
                      />
                    </div>
                    <div>
                      <Label htmlFor="indicator-type">Type</Label>
                      <select
                        id="indicator-type"
                        className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                        value={newIndicator.type}
                        onChange={(e) => setNewIndicator({...newIndicator, type: e.target.value})}
                      >
                        <option value="overlay">Overlay</option>
                        <option value="oscillator">Oscillator</option>
                        <option value="indicator">Indicator</option>
                      </select>
                    </div>
                  </div>
                  <div>
                    <Label htmlFor="indicator-formula">Formula (optional)</Label>
                    <Input
                      id="indicator-formula"
                      placeholder="e.g., (close + high + low) / 3"
                      value={newIndicator.formula}
                      onChange={(e) => setNewIndicator({...newIndicator, formula: e.target.value})}
                    />
                  </div>
                  <Button onClick={addCustomIndicator} className="w-full">
                    <Plus className="h-4 w-4 mr-2" />
                    Add Indicator
                  </Button>
                </div>
              </div>
            </ScrollArea>
          </TabsContent>

          <TabsContent value="colors" className="flex-1 overflow-hidden flex flex-col space-y-4">
            <ScrollArea className="flex-1 pr-4">
              <div className="space-y-4">
                {colorSchemes.map((scheme) => (
                  <div key={scheme.id} className="p-4 border rounded-lg space-y-3">
                    <div className="flex items-center justify-between">
                      <h3 className="font-semibold">{scheme.name}</h3>
                      {scheme.custom && (
                        <Badge variant="outline">Custom</Badge>
                      )}
                    </div>
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                      {Object.entries(scheme.colors).map(([key, value]) => (
                        <div key={key} className="flex items-center gap-2">
                          <div
                            className="w-8 h-8 rounded border"
                            style={{ backgroundColor: value }}
                          />
                          <span className="text-xs capitalize">
                            {key.replace(/([A-Z])/g, ' $1').trim()}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}

                {/* Add new color scheme */}
                <div className="p-4 border rounded-lg bg-muted/50 space-y-3">
                  <h3 className="text-sm font-semibold">Create Color Scheme</h3>
                  <div className="flex gap-2">
                    <Input
                      placeholder="Scheme name"
                      value={newSchemeName}
                      onChange={(e) => setNewSchemeName(e.target.value)}
                    />
                    <Button onClick={addColorScheme}>
                      <Plus className="h-4 w-4 mr-2" />
                      Add
                    </Button>
                  </div>
                </div>
              </div>
            </ScrollArea>
          </TabsContent>

          <TabsContent value="import-export" className="flex-1 flex flex-col space-y-4">
            <div className="space-y-4">
              <div className="p-4 border rounded-lg space-y-3">
                <h3 className="font-semibold">Export Settings</h3>
                <p className="text-sm text-muted-foreground">
                  Download your custom indicators and color schemes as a JSON file
                </p>
                <Button onClick={exportSettings} className="w-full">
                  <Download className="h-4 w-4 mr-2" />
                  Export Settings
                </Button>
              </div>

              <div className="p-4 border rounded-lg space-y-3">
                <h3 className="font-semibold">Import Settings</h3>
                <p className="text-sm text-muted-foreground">
                  Load previously exported settings or import from another source
                </p>
                <div className="relative">
                  <Input
                    type="file"
                    accept=".json"
                    onChange={importSettings}
                    className="cursor-pointer"
                  />
                  <Upload className="absolute right-3 top-3 h-4 w-4 pointer-events-none" />
                </div>
              </div>

              <div className="p-4 border rounded-lg space-y-3 bg-muted/50">
                <h3 className="font-semibold">Summary</h3>
                <div className="grid grid-cols-2 gap-3 text-sm">
                  <div>
                    <p className="text-muted-foreground">Built-in Indicators</p>
                    <p className="font-semibold">{DEFAULT_INDICATORS.length}</p>
                  </div>
                  <div>
                    <p className="text-muted-foreground">Custom Indicators</p>
                    <p className="font-semibold">{customIndicators.length}</p>
                  </div>
                  <div>
                    <p className="text-muted-foreground">Color Schemes</p>
                    <p className="font-semibold">{colorSchemes.length}</p>
                  </div>
                  <div>
                    <p className="text-muted-foreground">Total Settings</p>
                    <p className="font-semibold">
                      {DEFAULT_INDICATORS.length + customIndicators.length + colorSchemes.length}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </TabsContent>
        </Tabs>

        <DialogFooter>
          <Button variant="outline" onClick={() => document.querySelector('[role="dialog"] button[type="button"]')?.click()}>
            Close
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
