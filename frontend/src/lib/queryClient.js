import { QueryClient } from '@tanstack/react-query';

// Configure React Query client with optimized settings
export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      // Stale time for stock data (30 seconds)
      staleTime: 30 * 1000,
      // Cache time (5 minutes)
      gcTime: 5 * 60 * 1000,
      // Retry failed requests
      retry: (failureCount, error) => {
        // Don't retry on 4xx errors except 408, 429
        if (error?.status >= 400 && error?.status < 500 && ![408, 429].includes(error?.status)) {
          return false;
        }
        return failureCount < 3;
      },
      // Retry delay with exponential backoff
      retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
      // Refetch on window focus for live data
      refetchOnWindowFocus: true,
      // Background refetch interval for stock data (1 minute)
      refetchInterval: 60 * 1000,
      // Only refetch if component is visible
      refetchIntervalInBackground: false,
    },
    mutations: {
      retry: 1,
      retryDelay: 1000,
    },
  },
});

// Query keys factory for consistent key management
export const queryKeys = {
  // Stock data keys
  stocks: {
    all: ['stocks'],
    lists: () => [...queryKeys.stocks.all, 'list'],
    list: (filters) => [...queryKeys.stocks.lists(), filters],
    details: () => [...queryKeys.stocks.all, 'detail'],
    detail: (symbol) => [...queryKeys.stocks.details(), symbol],
    quote: (symbol) => [...queryKeys.stocks.all, 'quote', symbol],
    search: (query) => [...queryKeys.stocks.all, 'search', query],
    trending: () => [...queryKeys.stocks.all, 'trending'],
    realtime: (symbol) => [...queryKeys.stocks.all, 'realtime', symbol],
  },
  
  // Platform keys
  platform: {
    all: ['platform'],
    stats: () => [...queryKeys.platform.all, 'stats'],
    usage: () => [...queryKeys.platform.all, 'usage'],
  },
  
  // User keys
  user: {
    all: ['user'],
    profile: () => [...queryKeys.user.all, 'profile'],
    portfolio: () => [...queryKeys.user.all, 'portfolio'],
    watchlist: () => [...queryKeys.user.all, 'watchlist'],
    billing: () => [...queryKeys.user.all, 'billing'],
  },
  
  // Market keys
  market: {
    all: ['market'],
    stats: () => [...queryKeys.market.all, 'stats'],
    filter: (filters) => [...queryKeys.market.all, 'filter', filters],
    nasdaq: (limit) => [...queryKeys.market.all, 'nasdaq', limit],
  },
};

// Prefetch functions for better UX
export const prefetchQueries = {
  // Prefetch popular stock quotes
  async popularStocks() {
    const popularSymbols = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA'];
    
    const promises = popularSymbols.map(symbol =>
      queryClient.prefetchQuery({
        queryKey: queryKeys.stocks.quote(symbol),
        queryFn: () => import('../services/stockAPI').then(({ stockAPI }) => stockAPI.getStockQuote(symbol)),
        staleTime: 30 * 1000,
      })
    );
    
    await Promise.allSettled(promises);
  },
  
  // Prefetch trending stocks
  async trendingStocks() {
    await queryClient.prefetchQuery({
      queryKey: queryKeys.stocks.trending(),
      queryFn: () => import('../services/stockAPI').then(({ stockAPI }) => stockAPI.getTrendingStocks()),
      staleTime: 2 * 60 * 1000, // 2 minutes for trending data
    });
  },
  
  // Prefetch platform stats
  async platformStats() {
    await queryClient.prefetchQuery({
      queryKey: queryKeys.platform.stats(),
      queryFn: () => import('../services/stockAPI').then(({ stockAPI }) => stockAPI.getPlatformStats()),
      staleTime: 5 * 60 * 1000, // 5 minutes for platform stats
    });
  },
};

// Cache invalidation utilities
export const invalidateQueries = {
  // Invalidate all stock data
  allStocks: () => queryClient.invalidateQueries({ queryKey: queryKeys.stocks.all }),
  
  // Invalidate specific stock
  stock: (symbol) => queryClient.invalidateQueries({ queryKey: queryKeys.stocks.detail(symbol) }),
  
  // Invalidate user data
  userProfile: () => queryClient.invalidateQueries({ queryKey: queryKeys.user.profile() }),
  userPortfolio: () => queryClient.invalidateQueries({ queryKey: queryKeys.user.portfolio() }),
  userWatchlist: () => queryClient.invalidateQueries({ queryKey: queryKeys.user.watchlist() }),
  
  // Invalidate platform data
  platformStats: () => queryClient.invalidateQueries({ queryKey: queryKeys.platform.stats() }),
};

// Background sync for critical data
export const backgroundSync = {
  start: () => {
    // Sync trending stocks every 2 minutes
    const trendingInterval = setInterval(() => {
      queryClient.invalidateQueries({ queryKey: queryKeys.stocks.trending() });
    }, 2 * 60 * 1000);
    
    // Sync platform stats every 5 minutes
    const statsInterval = setInterval(() => {
      queryClient.invalidateQueries({ queryKey: queryKeys.platform.stats() });
    }, 5 * 60 * 1000);
    
    return () => {
      clearInterval(trendingInterval);
      clearInterval(statsInterval);
    };
  },
};