import React, { createContext, useContext, useState, useEffect, useMemo } from 'react';

export const TRADING_MODES = {
  DAY_TRADE: 'day_trade',
  LONG_TERM: 'long_term'
};

export const MODE_CONFIG = {
  [TRADING_MODES.DAY_TRADE]: {
    label: 'Day Trade',
    icon: 'Zap',
    color: 'amber',
    timeframes: ['1m', '5m', '15m', '30m', '1h'],
    defaultTimeframe: '5m',
    features: [
      'momentum_scanner',
      'volume_alerts', 
      'gap_scanner',
      'breakout_alerts',
      'vwap',
      'level2_preview'
    ],
    navigation: [
      { name: 'Dashboard', href: '/app/dashboard', icon: 'LayoutDashboard' },
      { name: 'Scanners', href: '/app/screeners', icon: 'Search' },
      { name: 'Charts', href: '/app/stocks', icon: 'CandlestickChart' },
      { name: 'Alerts', href: '/app/alerts', icon: 'Bell' },
      { name: 'Watchlists', href: '/app/watchlists', icon: 'Eye' },
      { name: 'Top Movers', href: '/app/top-movers', icon: 'TrendingUp' },
    ],
    screenerPresets: [
      { name: 'Gap Up >3%', filters: { gap_percent_min: 3 } },
      { name: 'Volume Surge', filters: { volume_ratio_min: 2 } },
      { name: 'Breaking HOD', filters: { breaking_high: true } },
      { name: 'RSI Oversold', filters: { rsi_max: 30 } },
    ]
  },
  [TRADING_MODES.LONG_TERM]: {
    label: 'Long-Term',
    icon: 'TrendingUp',
    color: 'blue',
    timeframes: ['1h', '4h', '1D'],
    defaultTimeframe: '1D',
    features: [
      'fundamentals',
      'fair_value',
      'earnings_calendar',
      'insider_trading',
      'dividend_tracker',
      'valuation_score'
    ],
    navigation: [
      { name: 'Dashboard', href: '/app/dashboard', icon: 'LayoutDashboard' },
      { name: 'Research', href: '/app/stocks', icon: 'FileSearch' },
      { name: 'Valuations', href: '/app/screeners', icon: 'Calculator' },
      { name: 'Portfolio', href: '/app/portfolio', icon: 'Briefcase' },
      { name: 'Watchlists', href: '/app/watchlists', icon: 'Eye' },
      { name: 'Sectors', href: '/app/sectors', icon: 'PieChart' },
    ],
    screenerPresets: [
      { name: 'Undervalued', filters: { valuation_score_min: 65 } },
      { name: 'Dividend Aristocrats', filters: { dividend_years_min: 25 } },
      { name: 'Low P/E Growth', filters: { pe_max: 15, eps_growth_min: 10 } },
      { name: 'High ROE', filters: { roe_min: 20 } },
    ]
  }
};

const TradingModeContext = createContext(null);

export function TradingModeProvider({ children }) {
  const [mode, setMode] = useState(() => {
    try {
      return localStorage.getItem('trading_mode') || TRADING_MODES.DAY_TRADE;
    } catch {
      return TRADING_MODES.DAY_TRADE;
    }
  });

  useEffect(() => {
    try {
      localStorage.setItem('trading_mode', mode);
    } catch {}
  }, [mode]);

  const toggleMode = () => {
    setMode(prev => 
      prev === TRADING_MODES.DAY_TRADE 
        ? TRADING_MODES.LONG_TERM 
        : TRADING_MODES.DAY_TRADE
    );
  };

  const config = MODE_CONFIG[mode];

  const value = useMemo(() => ({
    mode,
    setMode,
    toggleMode,
    config,
    isDayTrade: mode === TRADING_MODES.DAY_TRADE,
    isLongTerm: mode === TRADING_MODES.LONG_TERM,
  }), [mode, config]);

  return (
    <TradingModeContext.Provider value={value}>
      {children}
    </TradingModeContext.Provider>
  );
}

export const useTradingMode = () => {
  const context = useContext(TradingModeContext);
  if (!context) {
    throw new Error('useTradingMode must be used within TradingModeProvider');
  }
  return context;
};

export default TradingModeContext;
