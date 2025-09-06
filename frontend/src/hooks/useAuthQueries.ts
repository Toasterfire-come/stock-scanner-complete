import { useQuery, useMutation, useQueryClient, UseQueryOptions, UseMutationOptions } from '@tanstack/react-query';
import { api, endpoints, TokenManager } from '../lib/api';
import { toast } from 'sonner';

// Types
export interface User {
  user_id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  plan: string;
  api_token: string;
  is_premium: boolean;
  limits: {
    monthly: number;
    daily: number;
  };
  usage: {
    monthly_calls: number;
    daily_calls: number;
    last_call?: string;
  };
  subscription: {
    active: boolean;
    end_date?: string;
    trial_used: boolean;
  };
}

export interface LoginCredentials {
  username: string;
  password: string;
}

export interface RegisterData {
  username: string;
  email: string;
  password: string;
  first_name: string;
  last_name: string;
}

export interface AuthResponse {
  success: boolean;
  data: User;
  message: string;
}

export interface ProfileUpdateData {
  first_name?: string;
  last_name?: string;
  email?: string;
}

export interface PasswordChangeData {
  current_password: string;
  new_password: string;
}

export interface PlatformStats {
  success: boolean;
  nyse_stocks: number;
  nasdaq_stocks: number;
  total_stocks: number;
  total_indicators: number;
  scanner_combinations: number;
  platform_stats: {
    total_users: number;
    premium_users: number;
    recent_stock_updates: number;
    api_calls_today: number;
  };
  market_stats: {
    exchanges_supported: string[];
    data_sources: string[];
    update_frequency: string;
  };
  timestamp: string;
}

export interface UsageStats {
  success: boolean;
  usage: {
    plan: string;
    monthly_used: number;
    monthly_limit: number;
    daily_used: number;
    daily_limit: number;
  };
  rate_limits: {
    requests_this_minute: number;
    requests_this_hour: number;
    requests_this_day: number;
    rate_limited: boolean;
  };
}

// Login mutation
export const useLogin = (options?: UseMutationOptions<AuthResponse, any, LoginCredentials>) => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationKey: ['auth', 'login'],
    mutationFn: async (credentials: LoginCredentials) => {
      const { data } = await api.post(endpoints.auth.login, credentials);
      
      // Store tokens
      TokenManager.setToken(data.data.api_token);
      
      return data;
    },
    onSuccess: (data) => {
      // Set user data in cache
      queryClient.setQueryData(['user', 'profile'], data.data);
      
      // Prefetch user-related data
      queryClient.prefetchQuery({
        queryKey: ['portfolio'],
        staleTime: 1000 * 60 * 5,
      });
      
      queryClient.prefetchQuery({
        queryKey: ['watchlist'], 
        staleTime: 1000 * 60 * 5,
      });
    },
    ...options,
  });
};

// Register mutation
export const useRegister = (options?: UseMutationOptions<AuthResponse, any, RegisterData>) => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationKey: ['auth', 'register'],
    mutationFn: async (userData: RegisterData) => {
      const { data } = await api.post(endpoints.auth.register, userData);
      
      // Store tokens
      TokenManager.setToken(data.data.api_token);
      
      return data;
    },
    onSuccess: (data) => {
      // Set user data in cache
      queryClient.setQueryData(['user', 'profile'], data.data);
    },
    ...options,
  });
};

// Logout mutation
export const useLogout = (options?: UseMutationOptions<void, any, void>) => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationKey: ['auth', 'logout'],
    mutationFn: async () => {
      // Clear tokens
      TokenManager.clearTokens();
    },
    onSuccess: () => {
      // Clear all cached data
      queryClient.clear();
      
      // Show success message
      toast.success('Logged out successfully');
      
      // Redirect to auth page
      window.location.href = '/auth';
    },
    ...options,
  });
};

// User profile query
export const useUserProfile = (options?: UseQueryOptions<User>) => {
  return useQuery({
    queryKey: ['user', 'profile'],
    queryFn: async () => {
      const { data } = await api.get(endpoints.auth.profile);
      return data.data;
    },
    enabled: !!TokenManager.getToken(),
    staleTime: 1000 * 60 * 10, // 10 minutes
    retry: (failureCount, error: any) => {
      // Don't retry on auth errors
      if (error?.response?.status === 401) {
        return false;
      }
      return failureCount < 2;
    },
    ...options,
  });
};

// Update profile mutation
export const useUpdateProfile = (options?: UseMutationOptions<any, any, ProfileUpdateData>) => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationKey: ['user', 'profile', 'update'],
    mutationFn: async (profileData: ProfileUpdateData) => {
      const { data } = await api.post(endpoints.auth.updateProfile, profileData);
      return data;
    },
    onSuccess: () => {
      // Invalidate user profile to refetch updated data
      queryClient.invalidateQueries({ queryKey: ['user', 'profile'] });
    },
    ...options,
  });
};

// Change password mutation
export const useChangePassword = (options?: UseMutationOptions<any, any, PasswordChangeData>) => {
  return useMutation({
    mutationKey: ['user', 'password', 'change'],
    mutationFn: async (passwordData: PasswordChangeData) => {
      const { data } = await api.post(endpoints.auth.changePassword, passwordData);
      return data;
    },
    ...options,
  });
};

// Platform stats query
export const usePlatformStats = (options?: UseQueryOptions<PlatformStats>) => {
  return useQuery({
    queryKey: ['platform', 'stats'],
    queryFn: async () => {
      const { data } = await api.get(endpoints.market.platformStats);
      return data;
    },
    staleTime: 1000 * 60 * 15, // 15 minutes
    ...options,
  });
};

// Usage stats query
export const useUsageStats = (options?: UseQueryOptions<UsageStats>) => {
  return useQuery({
    queryKey: ['usage', 'stats'],
    queryFn: async () => {
      const { data } = await api.get(endpoints.usage);
      return data;
    },
    enabled: !!TokenManager.getToken(),
    staleTime: 1000 * 60 * 5, // 5 minutes
    ...options,
  });
};

// Billing queries
export const useBillingPlan = (options?: UseQueryOptions<any>) => {
  return useQuery({
    queryKey: ['billing', 'plan'],
    queryFn: async () => {
      const { data } = await api.get(endpoints.billing.currentPlan);
      return data.data;
    },
    enabled: !!TokenManager.getToken(),
    staleTime: 1000 * 60 * 10, // 10 minutes
    ...options,
  });
};

export const useBillingHistory = (options?: UseQueryOptions<any[]>) => {
  return useQuery({
    queryKey: ['billing', 'history'],
    queryFn: async () => {
      const { data } = await api.get(endpoints.billing.history);
      return data.data;
    },
    enabled: !!TokenManager.getToken(),
    staleTime: 1000 * 60 * 15, // 15 minutes
    ...options,
  });
};

export const useBillingStats = (options?: UseQueryOptions<any>) => {
  return useQuery({
    queryKey: ['billing', 'stats'],
    queryFn: async () => {
      const { data } = await api.get(endpoints.billing.stats);
      return data.data;
    },
    enabled: !!TokenManager.getToken(),
    staleTime: 1000 * 60 * 10, // 10 minutes
    ...options,
  });
};