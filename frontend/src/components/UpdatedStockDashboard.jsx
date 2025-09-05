import React, { useState, useMemo } from 'react';
import { 
  useStocks, 
  usePlatformStats, 
  useTrendingStocks, 
  useUsageStats 
} from '../hooks/useStockQueries';
import MemoizedStockCard from './optimized/MemoizedStockCard';
import StockSearch from './StockSearch';
import StockFilters from './StockFilters';
import StockDetail from './StockDetail';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Loader2, BarChart3, TrendingUp, Users, Database, RefreshCw, AlertCircle } from 'lucide-react';
import ErrorBoundary from './common/ErrorBoundary';

// Performance monitoring component
const PerformanceMonitor = ({ onMetricsUpdate }) => {
  React.useEffect(() => {
    let observer;
    
    if ('PerformanceObserver' in window) {
      observer = new PerformanceObserver((list) => {
        const entries = list.getEntries();
        entries.forEach((entry) => {
          if (entry.entryType === 'largest-contentful-paint') {
            onMetricsUpdate?.({ LCP: entry.startTime });
          }
          if (entry.entryType === 'first-input') {
            onMetricsUpdate?.({ FID: entry.processingStart - entry.startTime });
          }
          if (entry.entryType === 'layout-shift' && !entry.hadRecentInput) {
            onMetricsUpdate?.({ CLS: entry.value });
          }
        });
      });
      
      observer.observe({ entryTypes: ['largest-contentful-paint', 'first-input', 'layout-shift'] });
    }
    
    return () => observer?.disconnect();
  }, [onMetricsUpdate]);
  
  return null;
};

// Retry component for failed queries
const RetryButton = ({ onRetry, loading, error }) => (
  <div className="flex items-center justify-center py-8">
    <div className="text-center">
      <AlertCircle className="w-12 h-12 text-red-400 mx-auto mb-4" />
      <h3 className="text-lg font-medium text-gray-900 mb-2">Unable to load data</h3>
      <p className="text-gray-600 mb-4">{error?.message || 'Something went wrong'}</p>
      <button
        onClick={onRetry}
        disabled={loading}
        className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
      >
        {loading ? (
          <Loader2 className="w-4 h-4 mr-2 animate-spin" />
        ) : (
          <RefreshCw className="w-4 h-4 mr-2" />
        )}
        Try Again
      </button>
    </div>
  </div>
);

// Platform stats component with error boundary
const PlatformStatsSection = ({ stats, loading, error, refetch }) => {
  if (error) {
    return (
      <div className="mb-8">
        <RetryButton onRetry={refetch} loading={loading} error={error} />
      </div>
    );
  }

  if (loading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        {[...Array(4)].map((_, i) => (
          <Card key={i} className="animate-pulse">
            <CardHeader className="pb-2">
              <div className="h-4 bg-gray-200 rounded w-3/4"></div>
            </CardHeader>
            <CardContent>
              <div className="h-8 bg-gray-200 rounded w-1/2 mb-2"></div>
              <div className="h-3 bg-gray-200 rounded w-full"></div>
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  if (!stats) return null;

  return (
    <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
      <Card className="hover:shadow-md transition-shadow">
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Total Stocks</CardTitle>
          <Database className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{stats.total_stocks}</div>
          <p className="text-xs text-muted-foreground">
            NYSE: {stats.nyse_stocks} | NASDAQ: {stats.nasdaq_stocks}
          </p>
        </CardContent>
      </Card>
      
      <Card className="hover:shadow-md transition-shadow">
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Total Users</CardTitle>
          <Users className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{stats.platform_stats.total_users}</div>
          <p className="text-xs text-muted-foreground">
            Premium: {stats.platform_stats.premium_users}
          </p>
        </CardContent>
      </Card>

      <Card className="hover:shadow-md transition-shadow">
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Indicators</CardTitle>
          <BarChart3 className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{stats.total_indicators}</div>
          <p className="text-xs text-muted-foreground">
            {stats.scanner_combinations} combinations
          </p>
        </CardContent>
      </Card>

      <Card className="hover:shadow-md transition-shadow">
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Data Sources</CardTitle>
          <TrendingUp className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{stats.market_stats.data_sources.length}</div>
          <p className="text-xs text-muted-foreground">
            {stats.market_stats.update_frequency}
          </p>
        </CardContent>
      </Card>
    </div>
  );
};

// Trending stocks component
const TrendingStocksSection = ({ trending, loading, error, refetch }) => {
  if (error) {
    return (
      <div className="mb-8">
        <h2 className="text-xl font-semibold mb-4">Trending Stocks</h2>
        <RetryButton onRetry={refetch} loading={loading} error={error} />
      </div>
    );
  }

  if (loading) {
    return (
      <div className="mb-8">
        <h2 className="text-xl font-semibold mb-4">Trending Stocks</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {[...Array(3)].map((_, i) => (
            <Card key={i} className="animate-pulse">
              <CardHeader>
                <div className="h-5 bg-gray-200 rounded w-3/4"></div>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {[...Array(3)].map((_, j) => (
                    <div key={j} className="h-4 bg-gray-200 rounded"></div>
                  ))}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    );
  }

  if (!trending) return null;

  return (
    <div className="mb-8">
      <h2 className="text-xl font-semibold mb-4">Trending Stocks</h2>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardHeader>
            <CardTitle className="text-lg text-green-600">Top Gainers</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {trending.top_gainers?.slice(0, 3).map((stock, index) => (
                <div key={index} className="flex justify-between items-center p-2 bg-green-50 rounded">
                  <span className="font-medium">{stock.symbol}</span>
                  <span className="text-green-600 font-semibold">+{stock.change_percent.toFixed(2)}%</span>
                </div>
              )) || (
                <div className="text-gray-500 text-sm">No data available</div>
              )}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-lg text-blue-600">High Volume</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {trending.high_volume?.slice(0, 3).map((stock, index) => (
                <div key={index} className="flex justify-between items-center p-2 bg-blue-50 rounded">
                  <span className="font-medium">{stock.symbol}</span>
                  <span className="text-blue-600 font-semibold">{(stock.volume / 1000000).toFixed(1)}M</span>
                </div>
              )) || (
                <div className="text-gray-500 text-sm">No data available</div>
              )}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-lg text-purple-600">Most Active</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {trending.most_active?.slice(0, 3).map((stock, index) => (
                <div key={index} className="flex justify-between items-center p-2 bg-purple-50 rounded">
                  <span className="font-medium">{stock.symbol}</span>
                  <span className="text-purple-600 font-semibold">${stock.price.toFixed(2)}</span>
                </div>
              )) || (
                <div className="text-gray-500 text-sm">No data available</div>
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

const UpdatedStockDashboard = () => {
  const [selectedStock, setSelectedStock] = useState(null);
  const [filters, setFilters] = useState({
    limit: 20,
    category: 'gainers'
  });
  
  // Use React Query hooks for data fetching
  const { 
    data: stocks = [], 
    isLoading: stocksLoading, 
    error: stocksError,
    refetch: refetchStocks 
  } = useStocks(filters);
  
  const { 
    data: platformStats, 
    isLoading: statsLoading, 
    error: statsError,
    refetch: refetchStats 
  } = usePlatformStats();
  
  const { 
    data: trending, 
    isLoading: trendingLoading, 
    error: trendingError,
    refetch: refetchTrending 
  } = useTrendingStocks();
  
  const { 
    data: usage 
  } = useUsageStats();

  // Memoized handlers
  const handleStockClick = React.useCallback((stock) => {
    setSelectedStock(stock);
  }, []);

  const handleFilterChange = React.useCallback((newFilters) => {
    setFilters(prev => ({ ...prev, ...newFilters }));
  }, []);

  // Memoized category title
  const categoryTitle = useMemo(() => {
    switch (filters.category) {
      case 'gainers': return 'Top Gainers';
      case 'losers': return 'Top Losers';
      case 'high_volume': return 'High Volume';
      case 'large_cap': return 'Large Cap';
      case 'small_cap': return 'Small Cap';
      default: return 'Stocks';
    }
  }, [filters.category]);

  // Performance monitoring
  const handleMetricsUpdate = React.useCallback((metrics) => {
    if (process.env.NODE_ENV === 'development') {
      console.log('Performance metrics:', metrics);
    }
  }, []);

  if (selectedStock) {
    return (
      <ErrorBoundary>
        <StockDetail 
          stock={selectedStock} 
          onBack={() => setSelectedStock(null)}
        />
      </ErrorBoundary>
    );
  }

  return (
    <ErrorBoundary>
      <PerformanceMonitor onMetricsUpdate={handleMetricsUpdate} />
      
      <div className="min-h-screen bg-gray-50 p-4">
        <div className="max-w-7xl mx-auto">
          {/* Header */}
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Stock Scanner</h1>
            <p className="text-gray-600">Real-time stock market data and analysis</p>
            
            {/* Usage stats */}
            {usage && (
              <div className="mt-4 text-sm text-gray-600">
                API Usage: {usage.usage.daily_used}/{usage.usage.daily_limit} daily calls
                {usage.rate_limits.rate_limited && (
                  <span className="ml-2 text-red-600 font-medium">⚠️ Rate limited</span>
                )}
              </div>
            )}
          </div>

          {/* Platform Stats */}
          <PlatformStatsSection 
            stats={platformStats} 
            loading={statsLoading} 
            error={statsError}
            refetch={refetchStats}
          />

          {/* Search and Filters */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 mb-8">
            <div className="lg:col-span-2">
              <ErrorBoundary fallback={<div className="h-16 bg-white rounded-lg border"></div>}>
                <StockSearch onSelect={handleStockClick} />
              </ErrorBoundary>
            </div>
            <div>
              <ErrorBoundary fallback={<div className="h-64 bg-white rounded-lg border"></div>}>
                <StockFilters onFilterChange={handleFilterChange} currentFilters={filters} />
              </ErrorBoundary>
            </div>
          </div>

          {/* Trending Stocks */}
          <TrendingStocksSection 
            trending={trending} 
            loading={trendingLoading} 
            error={trendingError}
            refetch={refetchTrending}
          />

          {/* Stock Grid */}
          <div className="mb-8">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-semibold">{categoryTitle}</h2>
              <div className="flex items-center gap-2">
                {stocksLoading && <Loader2 className="h-5 w-5 animate-spin text-blue-600" />}
                <button
                  onClick={() => refetchStocks()}
                  className="p-2 text-gray-500 hover:text-gray-700 transition-colors"
                  title="Refresh data"
                >
                  <RefreshCw className="h-4 w-4" />
                </button>
              </div>
            </div>

            {stocksError && (
              <RetryButton onRetry={refetchStocks} loading={stocksLoading} error={stocksError} />
            )}

            {!stocksError && (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                {stocksLoading && stocks.length === 0 ? (
                  // Loading skeletons
                  [...Array(8)].map((_, index) => (
                    <Card key={index} className="animate-pulse">
                      <CardHeader className="pb-3">
                        <div className="flex justify-between">
                          <div>
                            <div className="h-5 bg-gray-200 rounded w-16 mb-2"></div>
                            <div className="h-4 bg-gray-200 rounded w-24"></div>
                          </div>
                          <div className="text-right">
                            <div className="h-5 bg-gray-200 rounded w-20 mb-2"></div>
                            <div className="h-4 bg-gray-200 rounded w-16"></div>
                          </div>
                        </div>
                      </CardHeader>
                      <CardContent>
                        <div className="grid grid-cols-2 gap-4">
                          <div className="h-4 bg-gray-200 rounded"></div>
                          <div className="h-4 bg-gray-200 rounded"></div>
                          <div className="h-4 bg-gray-200 rounded"></div>
                          <div className="h-4 bg-gray-200 rounded"></div>
                        </div>
                      </CardContent>
                    </Card>
                  ))
                ) : (
                  // Actual stock cards
                  stocks.map((stock) => (
                    <MemoizedStockCard 
                      key={stock.ticker || stock.symbol} 
                      stock={stock} 
                      onClick={handleStockClick}
                      showActions={true}
                    />
                  ))
                )}
              </div>
            )}

            {!stocksLoading && !stocksError && stocks.length === 0 && (
              <div className="text-center py-12">
                <div className="text-gray-400 mb-4">
                  <BarChart3 className="w-16 h-16 mx-auto" />
                </div>
                <h3 className="text-lg font-medium text-gray-900 mb-2">No stocks found</h3>
                <p className="text-gray-600">Try adjusting your filters or search criteria.</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </ErrorBoundary>
  );
};

export default UpdatedStockDashboard;