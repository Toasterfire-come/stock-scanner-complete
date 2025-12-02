import React from 'react';
import { useTradingMode } from '../context/TradingModeContext';
import { cn } from '../lib/utils';
import { Sparkles, ChevronRight } from 'lucide-react';

export default function ScreenerPresets({ onSelectPreset, className }) {
  const { config, isDayTrade } = useTradingMode();

  return (
    <div className={cn("space-y-2", className)} data-testid="screener-presets">
      <div className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-3">
        <Sparkles className={cn(
          "h-4 w-4",
          isDayTrade ? "text-amber-500" : "text-blue-500"
        )} />
        <span>Quick Presets</span>
      </div>
      
      <div className="grid grid-cols-2 gap-2">
        {config.screenerPresets.map((preset, index) => (
          <button
            key={index}
            onClick={() => onSelectPreset && onSelectPreset(preset)}
            data-testid={`preset-${preset.name.toLowerCase().replace(/\s+/g, '-')}`}
            className={cn(
              "flex items-center justify-between px-3 py-2 rounded-lg border text-sm font-medium transition-all",
              "hover:shadow-sm",
              isDayTrade
                ? "border-amber-200 bg-amber-50 text-amber-800 hover:bg-amber-100"
                : "border-blue-200 bg-blue-50 text-blue-800 hover:bg-blue-100"
            )}
          >
            <span>{preset.name}</span>
            <ChevronRight className="h-4 w-4 opacity-50" />
          </button>
        ))}
      </div>
    </div>
  );
}
