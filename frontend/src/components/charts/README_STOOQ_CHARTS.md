# Stooq HTML5 Charts Integration

## Overview

This implementation integrates Stooq's HTML5 charts directly into TradeScanPro, allowing users to view professional-grade stock charts with full customization capabilities.

## Features

### ✅ Implemented Features

1. **Stooq HTML5 Chart Integration**
   - Charts served directly by Stooq servers
   - Browser pulls chart data from Stooq
   - No backend processing required for charts
   - Responsive iframe embedding

2. **Customizable Colors**
   - All chart elements customizable (background, grid, text, candles, etc.)
   - Color settings persist in localStorage
   - Pre-built color schemes (Default, Dark Mode, High Contrast)
   - Create custom color schemes
   - Per-stock color preferences

3. **Favorites (*) Feature**
   - Star/unstar stocks for quick access
   - Favorites persist in localStorage
   - Sync with backend API (when logged in)
   - Visual indication with star icon
   - One-click toggle

4. **Technical Indicators**
   - **Built-in Indicators:**
     - SMA (20, 50, 200)
     - EMA (12, 26)
     - Bollinger Bands
     - RSI (Relative Strength Index)
     - MACD
     - Stochastic
     - ATR (Average True Range)
     - ADX
     - OBV (On-Balance Volume)

5. **Custom Indicator Import**
   - Add custom indicators with formulas
   - Define indicator type (overlay, oscillator, indicator)
   - Export/import custom indicators as JSON
   - Manage custom indicators through settings UI

6. **Chart Controls**
   - Multiple timeframes (1D, 1W, 1M, 3M, 1Y, 5Y)
   - Chart types (Candlestick, Line, Bar, Area)
   - Fullscreen mode
   - Export chart
   - Refresh on demand
   - Indicator management UI

## Components

### StooqChart.jsx

Main chart component that renders Stooq charts.

**Props:**
- `ticker` (string): Stock symbol
- `height` (number): Chart height in pixels (default: 500)
- `theme` (string): 'light' or 'dark'
- `onFavoriteToggle` (function): Callback when favorite status changes
- `isFavorite` (boolean): Whether stock is favorited
- `className` (string): Additional CSS classes

**Example Usage:**
```jsx
import StooqChart from './components/charts/StooqChart';
import { useFavorites } from './hooks/useFavorites';

function StockDetailPage({ ticker }) {
  const { isFavorite, toggleFavorite } = useFavorites();

  return (
    <StooqChart
      ticker={ticker}
      height={600}
      theme="light"
      isFavorite={isFavorite(ticker)}
      onFavoriteToggle={toggleFavorite}
    />
  );
}
```

### useFavorites Hook

Manages favorite stocks with persistence.

**API:**
```javascript
const {
  favorites,        // Array of favorite tickers
  isLoading,       // Loading state
  addFavorite,     // (ticker) => void
  removeFavorite,  // (ticker) => void
  toggleFavorite,  // (ticker) => void
  isFavorite,      // (ticker) => boolean
  clearFavorites,  // () => void
  syncWithBackend, // () => Promise<void>
} = useFavorites();
```

### ChartSettings.jsx

Advanced settings dialog for chart customization.

**Features:**
- View all available indicators
- Add custom indicators
- Manage color schemes
- Export/import settings

## How It Works

### Chart URL Construction

The StooqChart component builds a Stooq chart URL with the following parameters:

```
https://stooq.com/q/c/?s={SYMBOL}.US&p={TIMEFRAME}&t={CHART_TYPE}&i={INDICATORS}&...colors
```

Parameters:
- `s`: Stock symbol (e.g., AAPL.US)
- `p`: Timeframe (d, w, m, q, y, 5y)
- `t`: Chart type (c=candlestick, l=line, b=bar, a=area)
- `i`: Comma-separated list of indicators
- Color parameters (bg, gc, tc, uc, dc, etc.)

### Data Flow

```
User Interaction
      ↓
  StooqChart Component
      ↓
  Build Stooq URL with parameters
      ↓
  Browser fetches chart from Stooq servers
      ↓
  Chart renders in iframe
```

### Persistence

1. **Favorites**: Stored in localStorage under `tradescanpro_favorites`
2. **Colors**: Stored per-ticker in `stooq_colors_{ticker}`
3. **Custom Indicators**: Stored in `stooq_custom_indicators`
4. **Color Schemes**: Stored in `stooq_color_schemes`

## Migration from Old Charts

To replace existing charts:

### 1. Update Stock Detail Page

```jsx
// Before
import EnhancedStockChart from './components/EnhancedStockChart';

// After
import StooqChart from './components/charts/StooqChart';
import { useFavorites } from './hooks/useFavorites';

function StockDetail({ ticker }) {
  const { isFavorite, toggleFavorite } = useFavorites();

  return (
    <StooqChart
      ticker={ticker}
      isFavorite={isFavorite(ticker)}
      onFavoriteToggle={toggleFavorite}
    />
  );
}
```

### 2. Update Scanner Results

```jsx
import StooqChart from './components/charts/StooqChart';

function ScannerResults({ stocks }) {
  return (
    <div className="grid grid-cols-1 gap-4">
      {stocks.map(stock => (
        <StooqChart key={stock.ticker} ticker={stock.ticker} height={300} />
      ))}
    </div>
  );
}
```

### 3. Add Favorites List

```jsx
import { useFavorites } from './hooks/useFavorites';
import StooqChart from './components/charts/StooqChart';

function FavoritesList() {
  const { favorites, toggleFavorite, isFavorite } = useFavorites();

  return (
    <div className="space-y-4">
      <h2>My Favorites</h2>
      {favorites.map(ticker => (
        <StooqChart
          key={ticker}
          ticker={ticker}
          isFavorite={isFavorite(ticker)}
          onFavoriteToggle={toggleFavorite}
        />
      ))}
    </div>
  );
}
```

## Backend Integration

To sync favorites with backend, update the `useFavorites` hook:

```javascript
// In useFavorites.js
import { api } from '../api/client';

const syncWithBackend = useCallback(async () => {
  try {
    setIsLoading(true);
    const response = await api.get('/api/favorites/');
    if (response.data.favorites) {
      setFavorites(response.data.favorites);
    }
  } catch (error) {
    console.error('Failed to sync favorites:', error);
  } finally {
    setIsLoading(false);
  }
}, []);

const toggleFavorite = useCallback(async (ticker) => {
  const isFav = favorites.includes(ticker);

  // Optimistic update
  setFavorites(prev =>
    isFav ? prev.filter(t => t !== ticker) : [...prev, ticker]
  );

  // Sync with backend
  try {
    if (isFav) {
      await api.delete(`/api/favorites/${ticker}/`);
    } else {
      await api.post('/api/favorites/', { ticker });
    }
  } catch (error) {
    // Revert on error
    setFavorites(prev =>
      isFav ? [...prev, ticker] : prev.filter(t => t !== ticker)
    );
    toast.error('Failed to update favorite');
  }
}, [favorites]);
```

## Customization Examples

### Custom Color Scheme

```jsx
import StooqChart from './components/charts/StooqChart';

function MyChart() {
  return (
    <StooqChart
      ticker="AAPL"
      // Colors are managed through the color settings UI
      // or can be set programmatically via localStorage
    />
  );
}
```

### Custom Indicators

Use the ChartSettings component to add custom indicators:

1. Click "Chart Settings" button
2. Go to "Indicators" tab
3. Fill in custom indicator form:
   - Name: "My Custom MA"
   - Type: "overlay"
   - Formula: "(close + high + low) / 3"
4. Click "Add Indicator"

## Production Readiness Checklist

- [x] Stooq chart integration
- [x] Customizable colors
- [x] Favorites feature
- [x] Built-in indicators
- [x] Custom indicator support
- [x] Export/import settings
- [x] localStorage persistence
- [ ] Backend API integration for favorites
- [ ] User authentication check
- [ ] Error handling for failed chart loads
- [ ] Mobile responsiveness testing
- [ ] Cross-browser compatibility testing

## Known Limitations

1. **Stooq Rate Limits**: Stooq may have rate limits on chart requests
2. **Internet Required**: Charts require internet connection to load from Stooq
3. **No Offline Mode**: Cannot cache charts for offline viewing
4. **Limited Color Parameters**: Stooq's color customization depends on their API parameters

## Future Enhancements

1. **More Timeframes**: Add intraday timeframes (1m, 5m, 15m, 30m, 1h)
2. **Drawing Tools**: Add support for trendlines, fibonacci, etc.
3. **Comparison Charts**: Compare multiple stocks on same chart
4. **Alert Integration**: Create price alerts from chart
5. **Chart Annotations**: Add notes and markers to charts
6. **Advanced Patterns**: Automatic pattern detection (head & shoulders, triangles, etc.)

## Support

For issues or questions:
- Check Stooq documentation: https://stooq.com
- Review TradeScanPro docs
- Contact: carter.kiefer2010@outlook.com
