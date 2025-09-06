import { useQuery, useMutation, useInfiniteQuery } from '@tanstack/react-query';
import { stockAPI } from '../services/stockAPI';
import { queryKeys, queryClient, invalidateQueries } from '../lib/queryClient';
import { useAuth } from '../context/EnhancedAuthContext';

// ============ STOCK DATA HOOKS ============

export const useStocks = (filters = {}) => {
  return useQuery({
    queryKey: queryKeys.stocks.list(filters),
    queryFn: () => stockAPI.getStocks(filters),
    select: (data) => data?.success ? data.data : [],
    staleTime: 30 * 1000, // 30 seconds
    refetchInterval: 60 * 1000, // 1 minute
    placeholderData: [], // Show empty array while loading
  });
};

export const useStockDetail = (symbol) => {
  return useQuery({
    queryKey: queryKeys.stocks.detail(symbol),
    queryFn: () => stockAPI.getStockDetails(symbol),
    select: (data) => data?.success ? data.data : null,
    enabled: !!symbol,
    staleTime: 30 * 1000,
  });
};

export const useStockQuote = (symbol, options = {}) => {
  return useQuery({
    queryKey: queryKeys.stocks.quote(symbol),
    queryFn: () => stockAPI.getStockQuote(symbol),
    select: (data) => data?.success ? data : null,
    enabled: !!symbol,
    staleTime: 15 * 1000, // 15 seconds for quotes
    refetchInterval: options.realTime ? 15 * 1000 : 60 * 1000,
    ...options,
  });
};

export const useRealTimeData = (symbol) => {
  return useQuery({
    queryKey: queryKeys.stocks.realtime(symbol),
    queryFn: () => stockAPI.getRealTimeData(symbol),
    select: (data) => data?.success ? data.data : null,
    enabled: !!symbol,
    staleTime: 5 * 1000, // 5 seconds for real-time
    refetchInterval: 10 * 1000, // 10 seconds
  });
};

export const useStockSearch = (query) => {
  return useQuery({
    queryKey: queryKeys.stocks.search(query),
    queryFn: () => stockAPI.searchStocks(query),
    select: (data) => data?.success ? data.data : [],
    enabled: !!query && query.length >= 2,
    staleTime: 5 * 60 * 1000, // 5 minutes for search results
    placeholderData: [],
  });
};

export const useTrendingStocks = () => {
  return useQuery({
    queryKey: queryKeys.stocks.trending(),
    queryFn: () => stockAPI.getTrendingStocks(),
    select: (data) => data?.success ? data : null,
    staleTime: 2 * 60 * 1000, // 2 minutes
    refetchInterval: 3 * 60 * 1000, // 3 minutes
  });
};

// ============ PLATFORM HOOKS ============

export const usePlatformStats = () => {
  return useQuery({
    queryKey: queryKeys.platform.stats(),
    queryFn: () => stockAPI.getPlatformStats(),
    select: (data) => data?.success ? data : null,
    staleTime: 5 * 60 * 1000, // 5 minutes
    refetchInterval: 10 * 60 * 1000, // 10 minutes
  });
};

export const useUsageStats = () => {
  return useQuery({
    queryKey: queryKeys.platform.usage(),
    queryFn: () => stockAPI.getUsageStats(),
    select: (data) => data?.success ? data : null,
    staleTime: 60 * 1000, // 1 minute
    refetchInterval: 2 * 60 * 1000, // 2 minutes
  });
};

// ============ MARKET HOOKS ============

export const useMarketStats = () => {
  return useQuery({
    queryKey: queryKeys.market.stats(),
    queryFn: () => stockAPI.getMarketStats(),
    select: (data) => data?.success ? data.data : null,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};

export const useFilteredStocks = (filters) => {
  return useQuery({
    queryKey: queryKeys.market.filter(filters),
    queryFn: () => stockAPI.filterStocks(filters),
    select: (data) => data?.success ? data.data : [],
    enabled: Object.keys(filters).length > 0,
    staleTime: 60 * 1000, // 1 minute
  });
};

export const useNasdaqStocks = (limit = 500) => {
  return useQuery({
    queryKey: queryKeys.market.nasdaq(limit),
    queryFn: () => stockAPI.getNasdaqStocks(limit),
    select: (data) => data?.success ? data.data : [],
    staleTime: 10 * 60 * 1000, // 10 minutes
  });
};

// ============ USER HOOKS (Authenticated) ============

export const useUserProfile = () => {
  const { isAuthenticated } = useAuth();
  
  return useQuery({
    queryKey: queryKeys.user.profile(),
    queryFn: () => stockAPI.getUserProfile(),
    select: (data) => data?.success ? data.data : null,
    enabled: isAuthenticated,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};

export const usePortfolio = () => {
  const { isAuthenticated } = useAuth();
  
  return useQuery({
    queryKey: queryKeys.user.portfolio(),
    queryFn: () => stockAPI.getPortfolio(),
    select: (data) => data?.success ? data.data : [],
    enabled: isAuthenticated,
    staleTime: 60 * 1000, // 1 minute
  });
};

export const useWatchlist = () => {
  const { isAuthenticated } = useAuth();
  
  return useQuery({
    queryKey: queryKeys.user.watchlist(),
    queryFn: () => stockAPI.getWatchlist(),
    select: (data) => data?.success ? data.data : [],
    enabled: isAuthenticated,
    staleTime: 60 * 1000, // 1 minute
  });
};

// ============ MUTATION HOOKS ============

export const useAddToPortfolio = () => {
  return useMutation({
    mutationFn: (symbol) => stockAPI.addToPortfolio(symbol),
    onSuccess: () => {
      // Invalidate and refetch portfolio data
      invalidateQueries.userPortfolio();
    },
    onError: (error) => {
      console.error('Error adding to portfolio:', error);
    },
  });
};

export const useAddToWatchlist = () => {
  return useMutation({
    mutationFn: (symbol) => stockAPI.addToWatchlist(symbol),
    onSuccess: () => {
      // Invalidate and refetch watchlist data
      invalidateQueries.userWatchlist();
    },
    onError: (error) => {
      console.error('Error adding to watchlist:', error);
    },
  });
};

export const useUpdateProfile = () => {
  return useMutation({
    mutationFn: (profileData) => stockAPI.updateUserProfile(profileData),
    onSuccess: () => {
      // Invalidate and refetch user profile
      invalidateQueries.userProfile();
    },
    onError: (error) => {
      console.error('Error updating profile:', error);
    },
  });
};

// ============ INFINITE QUERY HOOKS ============

export const useInfiniteStocks = (filters = {}) => {
  return useInfiniteQuery({
    queryKey: ['stocks', 'infinite', filters],
    queryFn: ({ pageParam = 0 }) => 
      stockAPI.getStocks({ ...filters, offset: pageParam, limit: 20 }),
    getNextPageParam: (lastPage, pages) => {
      if (lastPage?.data?.length < 20) return undefined;
      return pages.length * 20;
    },
    select: (data) => ({
      pages: data.pages.map(page => page?.success ? page.data : []),
      pageParams: data.pageParams,
    }),
    staleTime: 60 * 1000,
  });
};

// ============ OPTIMISTIC UPDATES ============

export const useOptimisticPortfolio = () => {
  const addToPortfolio = useAddToPortfolio();
  
  const addWithOptimisticUpdate = (symbol) => {
    // Optimistically update the cache
    queryClient.setQueryData(queryKeys.user.portfolio(), (old) => [
      ...(old || []),
      { symbol, added_at: new Date().toISOString() }
    ]);
    
    // Perform the actual mutation
    addToPortfolio.mutate(symbol, {
      onError: () => {
        // Revert on error
        invalidateQueries.userPortfolio();
      },
    });
  };
  
  return { addWithOptimisticUpdate, ...addToPortfolio };
};

export const useOptimisticWatchlist = () => {
  const addToWatchlist = useAddToWatchlist();
  
  const addWithOptimisticUpdate = (symbol) => {
    // Optimistically update the cache
    queryClient.setQueryData(queryKeys.user.watchlist(), (old) => [
      ...(old || []),
      { symbol, added_at: new Date().toISOString() }
    ]);
    
    // Perform the actual mutation
    addToWatchlist.mutate(symbol, {
      onError: () => {
        // Revert on error
        invalidateQueries.userWatchlist();
      },
    });
  };
  
  return { addWithOptimisticUpdate, ...addToWatchlist };
};

// ============ CUSTOM HOOKS FOR SPECIFIC USE CASES ============

export const useStockWithQuote = (symbol) => {
  const stockDetail = useStockDetail(symbol);
  const stockQuote = useStockQuote(symbol, { 
    enabled: !!symbol,
    refetchInterval: 30 * 1000 // 30 seconds for active viewing
  });
  
  return {
    stock: stockDetail.data,
    quote: stockQuote.data,
    isLoading: stockDetail.isLoading || stockQuote.isLoading,
    error: stockDetail.error || stockQuote.error,
    refetch: () => {
      stockDetail.refetch();
      stockQuote.refetch();
    },
  };
};

export const useDashboardData = () => {
  const platformStats = usePlatformStats();
  const trendingStocks = useTrendingStocks();
  const usageStats = useUsageStats();
  
  return {
    platformStats: platformStats.data,
    trendingStocks: trendingStocks.data,
    usageStats: usageStats.data,
    isLoading: platformStats.isLoading || trendingStocks.isLoading || usageStats.isLoading,
    error: platformStats.error || trendingStocks.error || usageStats.error,
    refetch: () => {
      platformStats.refetch();
      trendingStocks.refetch();
      usageStats.refetch();
    },
  };
};