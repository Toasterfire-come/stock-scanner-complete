import React from 'react';
import { Zap, TrendingUp } from 'lucide-react';
import { useTradingMode, TRADING_MODES } from '../context/TradingModeContext';
import { cn } from '../lib/utils';

export default function TradingModeToggle({ variant = 'default', className }) {
  const { mode, toggleMode, config, isDayTrade } = useTradingMode();

  if (variant === 'compact') {
    return (
      <button 
        onClick={toggleMode}
        data-testid="trading-mode-toggle-compact"
        className={cn(
          "flex items-center gap-2 px-3 py-1.5 rounded-full transition-all",
          isDayTrade 
            ? "bg-amber-100 text-amber-700 hover:bg-amber-200" 
            : "bg-blue-100 text-blue-700 hover:bg-blue-200",
          className
        )}
      >
        {isDayTrade ? <Zap className="h-4 w-4" /> : <TrendingUp className="h-4 w-4" />}
        <span className="text-sm font-medium">{config.label}</span>
      </button>
    );
  }

  if (variant === 'pill') {
    return (
      <div className={cn("inline-flex rounded-full p-1 bg-gray-100", className)} data-testid="trading-mode-toggle-pill">
        <button
          onClick={() => !isDayTrade && toggleMode()}
          data-testid="trading-mode-day-trade-btn"
          className={cn(
            "flex items-center gap-1.5 px-4 py-2 rounded-full text-sm font-medium transition-all",
            isDayTrade 
              ? "bg-amber-500 text-white shadow-sm" 
              : "text-gray-600 hover:text-gray-900"
          )}
        >
          <Zap className="h-4 w-4" />
          Day Trade
        </button>
        <button
          onClick={() => isDayTrade && toggleMode()}
          data-testid="trading-mode-long-term-btn"
          className={cn(
            "flex items-center gap-1.5 px-4 py-2 rounded-full text-sm font-medium transition-all",
            !isDayTrade 
              ? "bg-blue-500 text-white shadow-sm" 
              : "text-gray-600 hover:text-gray-900"
          )}
        >
          <TrendingUp className="h-4 w-4" />
          Long-Term
        </button>
      </div>
    );
  }

  // Default variant - card style
  return (
    <div 
      className={cn("flex items-center gap-4 p-4 bg-white rounded-xl border shadow-sm", className)}
      data-testid="trading-mode-toggle-default"
    >
      <div className={cn(
        "flex items-center gap-2 transition-colors",
        isDayTrade ? "text-amber-600" : "text-gray-400"
      )}>
        <Zap className="h-5 w-5" />
        <span className="font-medium">Day Trade</span>
      </div>
      
      {/* Custom Switch */}
      <button
        onClick={toggleMode}
        data-testid="trading-mode-switch"
        className={cn(
          "relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2",
          isDayTrade 
            ? "bg-amber-500 focus:ring-amber-500" 
            : "bg-blue-500 focus:ring-blue-500"
        )}
      >
        <span
          className={cn(
            "inline-block h-4 w-4 transform rounded-full bg-white transition-transform",
            isDayTrade ? "translate-x-1" : "translate-x-6"
          )}
        />
      </button>
      
      <div className={cn(
        "flex items-center gap-2 transition-colors",
        !isDayTrade ? "text-blue-600" : "text-gray-400"
      )}>
        <TrendingUp className="h-5 w-5" />
        <span className="font-medium">Long-Term</span>
      </div>

      <div className="ml-4 px-3 py-1 bg-gray-100 rounded-full text-xs font-medium text-gray-600">
        {config.timeframes.join(' | ')}
      </div>
    </div>
  );
}
