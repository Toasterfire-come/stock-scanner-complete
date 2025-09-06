import { QueryClient, DefaultOptions, MutationCache, QueryCache } from '@tanstack/react-query';
import { toast } from 'sonner';
import { TokenManager } from './api';

// Default query options
const defaultOptions: DefaultOptions = {
  queries: {
    staleTime: 1000 * 60 * 5, // 5 minutes
    gcTime: 1000 * 60 * 30, // 30 minutes (was cacheTime)
    retry: (failureCount, error: any) => {
      // Don't retry on 4xx errors except 408, 429
      if (error?.response?.status >= 400 && error?.response?.status < 500) {
        if ([408, 429].includes(error.response.status)) {
          return failureCount < 2;
        }
        return false;
      }
      // Retry up to 3 times for other errors
      return failureCount < 3;
    },
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
  },
  mutations: {
    retry: (failureCount, error: any) => {
      // Don't retry mutations on client errors
      if (error?.response?.status >= 400 && error?.response?.status < 500) {
        return false;
      }
      return failureCount < 1;
    },
  },
};

// Global error handler for queries
const queryCache = new QueryCache({
  onError: (error: any, query) => {
    console.error('Query error:', error, query);
    
    // Handle specific error cases
    if (error?.response?.status === 401) {
      // Don't show error toast for auth errors, let interceptor handle it
      return;
    }
    
    if (error?.response?.status >= 500) {
      toast.error('Server error occurred. Please try again.');
    } else if (error?.code === 'NETWORK_ERROR') {
      toast.error('Network error. Please check your connection.');
    } else if (error?.response?.data?.message) {
      toast.error(error.response.data.message);
    }
  },
});

// Global error handler for mutations
const mutationCache = new MutationCache({
  onError: (error: any, _variables, _context, mutation) => {
    console.error('Mutation error:', error, mutation);
    
    // Handle auth errors
    if (error?.response?.status === 401) {
      TokenManager.clearTokens();
      window.location.href = '/auth';
      return;
    }
    
    // Show specific error messages
    if (error?.response?.data?.detail) {
      toast.error(error.response.data.detail);
    } else if (error?.response?.status >= 500) {
      toast.error('Server error occurred. Please try again.');
    } else {
      toast.error('An error occurred. Please try again.');
    }
  },
  onSuccess: (_data, _variables, _context, mutation) => {
    // Show success messages for mutations
    const mutationKey = mutation.options.mutationKey;
    if (mutationKey?.includes('login')) {
      toast.success('Successfully logged in!');
    } else if (mutationKey?.includes('register')) {
      toast.success('Account created successfully!');
    } else if (mutationKey?.includes('profile')) {
      toast.success('Profile updated successfully!');
    } else if (mutationKey?.includes('password')) {
      toast.success('Password changed successfully!');
    }
  },
});

// Create query client
export const queryClient = new QueryClient({
  defaultOptions,
  queryCache,
  mutationCache,
});

// Background sync for real-time data
export const backgroundSync = {
  intervalId: null as NodeJS.Timeout | null,
  
  start() {
    // Sync every 30 seconds for real-time stock data
    this.intervalId = setInterval(() => {
      // Invalidate stock-related queries
      queryClient.invalidateQueries({ queryKey: ['stocks'] });
      queryClient.invalidateQueries({ queryKey: ['trending'] });
      queryClient.invalidateQueries({ queryKey: ['market'] });
      
      // Prefetch trending data
      queryClient.prefetchQuery({
        queryKey: ['trending'],
        queryFn: async () => {
          const { api, endpoints } = await import('./api');
          const { data } = await api.get(endpoints.stocks.trending);
          return data;
        },
        staleTime: 1000 * 30, // 30 seconds
      });
    }, 30000);
    
    return () => this.stop();
  },
  
  stop() {
    if (this.intervalId) {
      clearInterval(this.intervalId);
      this.intervalId = null;
    }
  },
};

// Prefetch utilities
export const prefetchUtils = {
  // Prefetch user profile on app start
  async prefetchUserProfile() {
    const token = TokenManager.getToken();
    if (token && !TokenManager.isTokenExpired()) {
      try {
        await queryClient.prefetchQuery({
          queryKey: ['user', 'profile'],
          queryFn: async () => {
            const { api, endpoints } = await import('./api');
            const { data } = await api.get(endpoints.auth.profile);
            return data;
          },
          staleTime: 1000 * 60 * 10, // 10 minutes
        });
      } catch (error) {
        console.warn('Failed to prefetch user profile:', error);
      }
    }
  },
  
  // Prefetch trending stocks
  async prefetchTrending() {
    try {
      await queryClient.prefetchQuery({
        queryKey: ['trending'],
        queryFn: async () => {
          const { api, endpoints } = await import('./api');
          const { data } = await api.get(endpoints.stocks.trending);
          return data;
        },
        staleTime: 1000 * 60 * 2, // 2 minutes
      });
    } catch (error) {
      console.warn('Failed to prefetch trending stocks:', error);
    }
  },
  
  // Prefetch platform stats
  async prefetchPlatformStats() {
    try {
      await queryClient.prefetchQuery({
        queryKey: ['platform', 'stats'],
        queryFn: async () => {
          const { api, endpoints } = await import('./api');
          const { data } = await api.get(endpoints.market.platformStats);
          return data;
        },
        staleTime: 1000 * 60 * 15, // 15 minutes
      });
    } catch (error) {
      console.warn('Failed to prefetch platform stats:', error);
    }
  },
};

export default queryClient;