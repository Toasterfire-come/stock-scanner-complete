import { useQuery, useMutation, useQueryClient, UseQueryOptions, UseMutationOptions } from '@tanstack/react-query';
import { api, endpoints } from '../lib/api';
import { toast } from 'sonner';

// Types
export interface Stock {
  ticker: string;
  symbol: string;
  company_name: string;
  name: string;
  exchange: string;
  current_price: number;
  price_change_today: number;
  change_percent: number;
  volume: number;
  volume_today: number;
  market_cap?: number;
  pe_ratio?: number;
  dividend_yield?: number;
  week_52_high?: number;
  week_52_low?: number;
  formatted_price: string;
  formatted_change: string;
  formatted_volume: string;
  formatted_market_cap?: string;
  last_updated: string;
  created_at: string;
  is_gaining: boolean;
  is_losing: boolean;
}

export interface StockQuote {
  success: boolean;
  symbol: string;
  price: number;
  change: number;
  change_percent: number;
  volume: number;
  timestamp: string;
  market_data: {
    open: number;
    high: number;
    low: number;
    previous_close: number;
    market_cap: number;
    pe_ratio?: number;
  };
  cached: boolean;
}

export interface StockFilters {
  limit?: number;
  search?: string;
  category?: string;
  min_price?: number;
  max_price?: number;
  min_volume?: number;
  exchange?: string;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
}

export interface TrendingData {
  success: boolean;
  high_volume: Array<{
    symbol: string;
    price: number;
    change_percent: number;
    volume: number;
  }>;
  top_gainers: Array<{
    symbol: string;
    price: number;
    change_percent: number;
    volume: number;
  }>;
  most_active: Array<{
    symbol: string;
    price: number;
    change_percent: number;
    volume: number;
  }>;
}

export interface MarketStats {
  success: boolean;
  data: {
    total_stocks: number;
    gainers: number;
    losers: number;
    unchanged: number;
    volume_leaders: string[];
  };
}

// Stock list query
export const useStocks = (filters?: StockFilters, options?: UseQueryOptions<Stock[]>) => {
  return useQuery({
    queryKey: ['stocks', filters],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (filters?.limit) params.append('limit', filters.limit.toString());
      if (filters?.search) params.append('search', filters.search);
      if (filters?.category) params.append('category', filters.category);
      if (filters?.min_price) params.append('min_price', filters.min_price.toString());
      if (filters?.max_price) params.append('max_price', filters.max_price.toString());
      if (filters?.min_volume) params.append('min_volume', filters.min_volume.toString());
      if (filters?.exchange) params.append('exchange', filters.exchange);
      if (filters?.sort_by) params.append('sort_by', filters.sort_by);
      if (filters?.sort_order) params.append('sort_order', filters.sort_order);

      const { data } = await api.get(`${endpoints.stocks.list}?${params.toString()}`);
      return data.data;
    },
    staleTime: 1000 * 60 * 2, // 2 minutes
    ...options,
  });
};

// Individual stock query
export const useStock = (symbol: string, options?: UseQueryOptions<Stock>) => {
  return useQuery({
    queryKey: ['stock', symbol],
    queryFn: async () => {
      const { data } = await api.get(endpoints.stocks.detail(symbol));
      return data.data;
    },
    enabled: !!symbol,
    staleTime: 1000 * 60 * 1, // 1 minute
    ...options,
  });
};

// Stock quote query
export const useStockQuote = (symbol: string, options?: UseQueryOptions<StockQuote>) => {
  return useQuery({
    queryKey: ['stock', 'quote', symbol],
    queryFn: async () => {
      const { data } = await api.get(endpoints.stocks.quote(symbol));
      return data;
    },
    enabled: !!symbol,
    staleTime: 1000 * 30, // 30 seconds
    refetchInterval: 1000 * 30, // Refetch every 30 seconds
    ...options,
  });
};

// Stock search query
export const useStockSearch = (query: string, options?: UseQueryOptions<any[]>) => {
  return useQuery({
    queryKey: ['stocks', 'search', query],
    queryFn: async () => {
      if (!query || query.length < 2) return [];
      const { data } = await api.get(`${endpoints.stocks.search}?q=${encodeURIComponent(query)}`);
      return data.data;
    },
    enabled: !!query && query.length >= 2,
    staleTime: 1000 * 60 * 5, // 5 minutes
    ...options,
  });
};

// Trending stocks query
export const useTrending = (options?: UseQueryOptions<TrendingData>) => {
  return useQuery({
    queryKey: ['trending'],
    queryFn: async () => {
      const { data } = await api.get(endpoints.stocks.trending);
      return data;
    },
    staleTime: 1000 * 60 * 2, // 2 minutes
    refetchInterval: 1000 * 60 * 2, // Refetch every 2 minutes
    ...options,
  });
};

// Market stats query
export const useMarketStats = (options?: UseQueryOptions<MarketStats>) => {
  return useQuery({
    queryKey: ['market', 'stats'],
    queryFn: async () => {
      const { data } = await api.get(endpoints.market.stats);
      return data;
    },
    staleTime: 1000 * 60 * 5, // 5 minutes
    ...options,
  });
};

// NASDAQ stocks query
export const useNasdaqStocks = (limit = 500, options?: UseQueryOptions<Stock[]>) => {
  return useQuery({
    queryKey: ['stocks', 'nasdaq', limit],
    queryFn: async () => {
      const { data } = await api.get(`${endpoints.stocks.nasdaq}?limit=${limit}`);
      return data.data;
    },
    staleTime: 1000 * 60 * 10, // 10 minutes
    ...options,
  });
};

// Real-time stock data query
export const useRealtimeStock = (symbol: string, options?: UseQueryOptions<any>) => {
  return useQuery({
    queryKey: ['stock', 'realtime', symbol],
    queryFn: async () => {
      const { data } = await api.get(endpoints.stocks.realtime(symbol));
      return data.data;
    },
    enabled: !!symbol,
    staleTime: 1000 * 15, // 15 seconds
    refetchInterval: 1000 * 15, // Refetch every 15 seconds
    ...options,
  });
};

// Portfolio queries
export const usePortfolio = (options?: UseQueryOptions<any[]>) => {
  return useQuery({
    queryKey: ['portfolio'],
    queryFn: async () => {
      const { data } = await api.get(endpoints.portfolio.list);
      return data.data;
    },
    staleTime: 1000 * 60 * 5, // 5 minutes
    ...options,
  });
};

export const useAddToPortfolio = (options?: UseMutationOptions<any, any, { symbol: string }>) => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationKey: ['portfolio', 'add'],
    mutationFn: async ({ symbol }: { symbol: string }) => {
      const { data } = await api.post(endpoints.portfolio.add, { symbol });
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['portfolio'] });
      toast.success('Added to portfolio successfully!');
    },
    ...options,
  });
};

// Watchlist queries
export const useWatchlist = (options?: UseQueryOptions<any[]>) => {
  return useQuery({
    queryKey: ['watchlist'],
    queryFn: async () => {
      const { data } = await api.get(endpoints.watchlist.list);
      return data.data;
    },
    staleTime: 1000 * 60 * 5, // 5 minutes
    ...options,
  });
};

export const useAddToWatchlist = (options?: UseMutationOptions<any, any, { symbol: string }>) => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationKey: ['watchlist', 'add'],
    mutationFn: async ({ symbol }: { symbol: string }) => {
      const { data } = await api.post(endpoints.watchlist.add, { symbol });
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['watchlist'] });
      toast.success('Added to watchlist successfully!');
    },
    ...options,
  });
};

// Filter stocks mutation for advanced filtering
export const useFilterStocks = (options?: UseMutationOptions<Stock[], any, StockFilters>) => {
  return useMutation({
    mutationKey: ['stocks', 'filter'],
    mutationFn: async (filters: StockFilters) => {
      const params = new URLSearchParams();
      if (filters.min_price) params.append('min_price', filters.min_price.toString());
      if (filters.max_price) params.append('max_price', filters.max_price.toString());
      if (filters.min_volume) params.append('min_volume', filters.min_volume.toString());
      if (filters.exchange) params.append('exchange', filters.exchange);

      const { data } = await api.get(`${endpoints.stocks.filter}?${params.toString()}`);
      return data.data;
    },
    ...options,
  });
};