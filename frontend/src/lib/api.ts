import axios, { AxiosError, AxiosRequestConfig, AxiosResponse } from 'axios';
import { toast } from 'sonner';

const API_BASE_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

// Extend AxiosRequestConfig to include metadata
interface ExtendedAxiosRequestConfig extends AxiosRequestConfig {
  metadata?: { startTime: number };
}

// Create axios instance with enhanced configuration
export const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Token management
class TokenManager {
  private static TOKEN_KEY = 'rts_token';
  private static REFRESH_TOKEN_KEY = 'rts_refresh_token';
  private static TOKEN_EXPIRY_KEY = 'token_expiry';

  static getToken(): string | null {
    return localStorage.getItem(this.TOKEN_KEY);
  }

  static setToken(token: string, expiresIn?: number): void {
    localStorage.setItem(this.TOKEN_KEY, token);
    if (expiresIn) {
      const expiryTime = Date.now() + (expiresIn * 1000);
      localStorage.setItem(this.TOKEN_EXPIRY_KEY, expiryTime.toString());
    }
  }

  static getRefreshToken(): string | null {
    return localStorage.getItem(this.REFRESH_TOKEN_KEY);
  }

  static setRefreshToken(refreshToken: string): void {
    localStorage.setItem(this.REFRESH_TOKEN_KEY, refreshToken);
  }

  static clearTokens(): void {
    localStorage.removeItem(this.TOKEN_KEY);
    localStorage.removeItem(this.REFRESH_TOKEN_KEY);
    localStorage.removeItem(this.TOKEN_EXPIRY_KEY);
  }

  static isTokenExpired(): boolean {
    const expiryTime = localStorage.getItem(this.TOKEN_EXPIRY_KEY);
    if (!expiryTime) return false;
    return Date.now() > parseInt(expiryTime, 10);
  }

  static shouldRefreshToken(): boolean {
    const expiryTime = localStorage.getItem(this.TOKEN_EXPIRY_KEY);
    if (!expiryTime) return false;
    // Refresh if token expires in next 5 minutes
    return Date.now() > (parseInt(expiryTime, 10) - 5 * 60 * 1000);
  }
}

// Request interceptor
api.interceptors.request.use(
  (config) => {
    const token = TokenManager.getToken();
    if (token) {
      config.headers = config.headers || {};
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    // Add request timestamp for performance monitoring
    (config as any).metadata = { startTime: Date.now() };
    
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor with token refresh logic
api.interceptors.response.use(
  (response: AxiosResponse) => {
    // Log response time in development
    if (process.env.NODE_ENV === 'development') {
      const config = response.config as any;
      if (config.metadata) {
        const duration = Date.now() - config.metadata.startTime;
        console.log(`🚀 ${config.method?.toUpperCase()} ${config.url} - ${duration}ms`);
      }
    }
    
    return response;
  },
  async (error: AxiosError) => {
    const originalRequest = error.config as ExtendedAxiosRequestConfig & { _retry?: boolean };
    
    // Handle 401 errors with token refresh
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      const refreshToken = TokenManager.getRefreshToken();
      if (refreshToken) {
        try {
          const refreshResponse = await axios.post(`${API_BASE_URL}/api/auth/refresh/`, {
            refresh_token: refreshToken,
          });
          
          const { access_token, expires_in } = refreshResponse.data;
          TokenManager.setToken(access_token, expires_in);
          
          // Retry original request with new token
          if (originalRequest.headers) {
            originalRequest.headers.Authorization = `Bearer ${access_token}`;
          }
          
          return api(originalRequest);
        } catch (refreshError) {
          // Refresh failed, redirect to login
          TokenManager.clearTokens();
          window.location.href = '/auth';
          return Promise.reject(refreshError);
        }
      } else {
        // No refresh token, redirect to login
        TokenManager.clearTokens();
        window.location.href = '/auth';
      }
    }
    
    // Handle other errors with user-friendly messages
    const status = error.response?.status;
    if (status && status >= 500) {
      toast.error('Server error. Please try again later.');
    } else if (status === 429) {
      toast.error('Too many requests. Please wait a moment.');
    } else if (error.code === 'NETWORK_ERROR' || error.message === 'Network Error') {
      toast.error('Network connection error. Please check your internet connection.');
    }
    
    return Promise.reject(error);
  }
);

// API endpoints
export const endpoints = {
  // Authentication
  auth: {
    login: '/api/auth/login/',
    register: '/api/auth/register/',
    refresh: '/api/auth/refresh/',
    profile: '/api/user/profile/',
    updateProfile: '/api/user/profile/',
    changePassword: '/api/user/change-password/',
  },
  
  // Stocks
  stocks: {
    list: '/api/stocks/',
    detail: (symbol: string) => `/api/stocks/${symbol}/`,
    quote: (symbol: string) => `/api/stocks/${symbol}/quote/`,
    search: '/api/stocks/search/',
    nasdaq: '/api/stocks/nasdaq/',
    trending: '/api/trending/',
    realtime: (symbol: string) => `/api/realtime/${symbol}/`,
    filter: '/api/market/filter/',
  },
  
  // Market
  market: {
    stats: '/api/market/stats/',
    platformStats: '/api/platform-stats/',
  },
  
  // User features
  portfolio: {
    list: '/api/portfolio/',
    add: '/api/portfolio/add/',
  },
  
  watchlist: {
    list: '/api/watchlist/',
    add: '/api/watchlist/add/',
  },
  
  // Billing
  billing: {
    currentPlan: '/api/billing/current-plan/',
    history: '/api/billing/history/',
    stats: '/api/billing/stats/',
  },
  
  // Usage
  usage: '/api/usage/',
};

// Export token manager for use in components
export { TokenManager };

// Default export
export default api;