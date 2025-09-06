// ============ USER TYPES ============

export interface User {
  user_id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  plan: UserPlan;
  api_token: string;
  is_premium: boolean;
  limits: UserLimits;
  usage: UserUsage;
  subscription: UserSubscription;
  created_at?: string;
  last_login?: string;
}

export interface UserLimits {
  monthly: number;
  daily: number;
}

export interface UserUsage {
  monthly_calls: number;
  daily_calls: number;
  last_call?: string;
}

export interface UserSubscription {
  active: boolean;
  end_date?: string | null;
  trial_used: boolean;
}

export type UserPlan = 'free' | 'bronze' | 'silver' | 'gold';

export interface UserRegistration {
  username: string;
  email: string;
  password: string;
  firstName: string;
  lastName: string;
}

export interface UserLogin {
  username: string;
  password: string;
}

// ============ STOCK TYPES ============

export interface Stock {
  ticker: string;
  symbol: string;
  company_name: string;
  name: string;
  exchange: string;
  
  // Price data
  current_price: number;
  price_change_today: number;
  price_change_week?: number;
  price_change_month?: number;
  price_change_year?: number;
  change_percent: number;
  
  // Bid/Ask and Range
  bid_price?: number;
  ask_price?: number;
  bid_ask_spread?: number;
  days_range?: string;
  days_low?: number;
  days_high?: number;
  
  // Volume data
  volume: number;
  volume_today: number;
  avg_volume_3mon?: number;
  dvav?: number;
  shares_available?: number;
  
  // Market data
  market_cap?: number;
  market_cap_change_3mon?: number;
  formatted_market_cap?: string;
  
  // Financial ratios
  pe_ratio?: number;
  pe_change_3mon?: number;
  dividend_yield?: number;
  earnings_per_share?: number;
  book_value?: number;
  price_to_book?: number;
  
  // 52-week range
  week_52_low?: number;
  week_52_high?: number;
  
  // Additional metrics
  one_year_target?: number;
  formatted_price: string;
  formatted_change: string;
  formatted_volume: string;
  
  // Timestamps
  last_updated: string;
  created_at: string;
  
  // Calculated fields
  is_gaining: boolean;
  is_losing: boolean;
  volume_ratio?: number;
  price_near_52_week_high?: boolean;
  price_near_52_week_low?: boolean;
  price_position_52_week?: number;
}

export interface StockQuote {
  success: boolean;
  symbol: string;
  price: number;
  change: number;
  change_percent: number;
  volume: number;
  timestamp: string;
  rate_limit_warning: boolean;
  source: string;
  market_data: MarketData;
  cached: boolean;
}

export interface MarketData {
  open?: number;
  high?: number;
  low?: number;
  previous_close?: number;
  market_cap?: number;
  pe_ratio?: number;
}

export interface StockSearchResult {
  symbol: string;
  name: string;
  exchange: string;
}

export interface TrendingStocks {
  success: boolean;
  high_volume: TrendingStock[];
  top_gainers: TrendingStock[];
  most_active: TrendingStock[];
}

export interface TrendingStock {
  symbol: string;
  price: number;
  change_percent: number;
  volume: number;
}

// ============ PLATFORM TYPES ============

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
    plan: UserPlan;
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

// ============ API RESPONSE TYPES ============

export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
  timestamp?: string;
}

export interface PaginatedResponse<T = any> extends ApiResponse<T[]> {
  total: number;
  limit: number;
  offset?: number;
  page?: number;
}

// ============ FILTER TYPES ============

export interface StockFilters {
  limit?: number;
  search?: string;
  category?: StockCategory;
  min_price?: number;
  max_price?: number;
  min_volume?: number;
  exchange?: Exchange;
  sort_by?: SortBy;
  sort_order?: SortOrder;
}

export type StockCategory = 'gainers' | 'losers' | 'high_volume' | 'large_cap' | 'small_cap';
export type Exchange = 'NASDAQ' | 'NYSE';
export type SortBy = 'price' | 'volume' | 'market_cap' | 'change_percent';
export type SortOrder = 'asc' | 'desc';

// ============ PORTFOLIO & WATCHLIST TYPES ============

export interface PortfolioItem {
  symbol: string;
  added_at: string;
  user_id: number;
}

export interface WatchlistItem {
  symbol: string;
  added_at: string;
  user_id: number;
}

// ============ BILLING TYPES ============

export interface BillingInfo {
  plan: UserPlan;
  is_premium: boolean;
  limits: UserLimits;
  subscription: UserSubscription;
}

export interface BillingHistory {
  id: string;
  amount: number;
  date: string;
  description: string;
  status: 'paid' | 'pending' | 'failed';
}

// ============ ERROR TYPES ============

export interface AppError {
  message: string;
  code?: string;
  status?: number;
  details?: Record<string, any>;
}

// ============ COMPONENT PROP TYPES ============

export interface StockCardProps {
  stock: Stock;
  onClick?: (stock: Stock) => void;
  showActions?: boolean;
}

export interface StockDetailProps {
  stock: Stock;
  onBack: () => void;
}

export interface AuthFormProps {
  onToggleMode: () => void;
}

// ============ HOOK RETURN TYPES ============

export interface UseStockDataReturn {
  stocks: Stock[];
  loading: boolean;
  error: string | null;
  fetchStocks: (filters?: StockFilters) => Promise<void>;
  getStockQuote: (symbol: string) => Promise<StockQuote>;
  searchStocks: (query: string) => Promise<StockSearchResult[]>;
}

export interface UseAuthReturn {
  user: User | null;
  loading: boolean;
  error: string | null;
  sessionExpired: boolean;
  isAuthenticated: boolean;
  login: (credentials: UserLogin) => Promise<User>;
  register: (userData: UserRegistration) => Promise<User>;
  logout: () => void;
  refreshUser: () => Promise<User | null>;
  updateUser: (data: Partial<User>) => void;
  clearSessionExpired: () => void;
  validateSession: () => Promise<boolean>;
  getAuthHeaders: () => Promise<Record<string, string>>;
  isTokenExpiringSoon: () => boolean;
  getUserPlan: () => UserPlan;
  getUserLimits: () => UserLimits;
  getUserUsage: () => UserUsage;
}

// ============ QUERY TYPES ============

export interface QueryError {
  message: string;
  status?: number;
}

export interface QueryOptions {
  enabled?: boolean;
  staleTime?: number;
  refetchInterval?: number;
  refetchOnWindowFocus?: boolean;
}

// ============ THEME TYPES ============

export type Theme = 'light' | 'dark' | 'system';

// ============ NOTIFICATION TYPES ============

export interface Notification {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  message: string;
  duration?: number;
  action?: {
    label: string;
    onClick: () => void;
  };
}

// ============ ANALYTICS TYPES ============

export interface AnalyticsEvent {
  event: string;
  properties?: Record<string, any>;
  userId?: string;
  timestamp?: string;
}

// ============ PWA TYPES ============

export interface PWAInstallPrompt {
  prompt: () => Promise<void>;
  userChoice: Promise<{ outcome: 'accepted' | 'dismissed' }>;
}

// ============ UTILITY TYPES ============

export type Prettify<T> = {
  [K in keyof T]: T[K];
} & {};

export type Optional<T, K extends keyof T> = Omit<T, K> & Partial<Pick<T, K>>;

export type RequiredKeys<T, K extends keyof T> = Omit<T, K> & Required<Pick<T, K>>;