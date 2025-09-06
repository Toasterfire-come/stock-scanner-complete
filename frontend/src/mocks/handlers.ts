import { http, HttpResponse } from 'msw';

const API_BASE = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

// Mock data
const mockUser = {
  user_id: 1,
  username: 'testuser',
  email: 'test@example.com',
  first_name: 'Test',
  last_name: 'User',
  plan: 'free',
  api_token: 'mock-token',
  is_premium: false,
  limits: { monthly: 15, daily: 15 },
  usage: { monthly_calls: 0, daily_calls: 0 },
  subscription: { active: false, trial_used: false },
};

const mockStocks = [
  {
    ticker: 'AAPL',
    symbol: 'AAPL',
    company_name: 'Apple Inc.',
    name: 'Apple Inc.',
    exchange: 'NASDAQ',
    current_price: 150.50,
    price_change_today: 2.50,
    change_percent: 1.69,
    volume: 50000000,
    volume_today: 50000000,
    market_cap: 2500000000000,
    pe_ratio: 25.5,
    dividend_yield: 0.5,
    week_52_high: 182.00,
    week_52_low: 124.17,
    formatted_price: '$150.50',
    formatted_change: '+$2.50 (1.69%)',
    formatted_volume: '50.0M',
    formatted_market_cap: '$2.50T',
    last_updated: new Date().toISOString(),
    created_at: new Date().toISOString(),
    is_gaining: true,
    is_losing: false,
  },
  // Add more mock stocks as needed
];

const mockTrending = {
  success: true,
  high_volume: [
    { symbol: 'AAPL', price: 150.50, change_percent: 1.69, volume: 50000000 },
    { symbol: 'GOOGL', price: 2750.00, change_percent: 0.85, volume: 25000000 },
  ],
  top_gainers: [
    { symbol: 'TSLA', price: 890.00, change_percent: 5.2, volume: 30000000 },
    { symbol: 'NVDA', price: 420.00, change_percent: 3.1, volume: 15000000 },
  ],
  most_active: [
    { symbol: 'AAPL', price: 150.50, change_percent: 1.69, volume: 50000000 },
    { symbol: 'TSLA', price: 890.00, change_percent: 5.2, volume: 30000000 },
  ],
};

export const handlers = [
  // Authentication endpoints
  http.post(`${API_BASE}/api/auth/login/`, async ({ request }) => {
    const body = await request.json() as any;
    
    if (body.username === 'testuser' && body.password === 'password') {
      return HttpResponse.json({
        success: true,
        data: mockUser,
        message: 'Login successful',
      });
    }
    
    return HttpResponse.json(
      { success: false, message: 'Invalid credentials' },
      { status: 401 }
    );
  }),

  http.post(`${API_BASE}/api/auth/register/`, async ({ request }) => {
    const body = await request.json() as any;
    
    return HttpResponse.json({
      success: true,
      data: { ...mockUser, ...body, user_id: 2 },
      message: 'User registered successfully',
    });
  }),

  http.get(`${API_BASE}/api/user/profile/`, () => {
    return HttpResponse.json({
      success: true,
      data: mockUser,
    });
  }),

  // Stock endpoints
  http.get(`${API_BASE}/api/stocks/`, ({ request }) => {
    const url = new URL(request.url);
    const limit = parseInt(url.searchParams.get('limit') || '50');
    const search = url.searchParams.get('search');
    
    let filteredStocks = [...mockStocks];
    
    if (search) {
      filteredStocks = mockStocks.filter(stock => 
        stock.symbol.toLowerCase().includes(search.toLowerCase()) ||
        stock.company_name.toLowerCase().includes(search.toLowerCase())
      );
    }
    
    return HttpResponse.json({
      success: true,
      data: filteredStocks.slice(0, limit),
      total: filteredStocks.length,
      limit,
    });
  }),

  http.get(`${API_BASE}/api/stocks/:symbol/`, ({ params }) => {
    const { symbol } = params;
    const stock = mockStocks.find(s => s.symbol === symbol?.toString().toUpperCase());
    
    if (!stock) {
      return HttpResponse.json(
        { success: false, message: 'Stock not found' },
        { status: 404 }
      );
    }
    
    return HttpResponse.json({
      success: true,
      data: stock,
    });
  }),

  http.get(`${API_BASE}/api/stocks/:symbol/quote/`, ({ params }) => {
    const { symbol } = params;
    const stock = mockStocks.find(s => s.symbol === symbol?.toString().toUpperCase());
    
    if (!stock) {
      return HttpResponse.json(
        { success: false, message: 'Stock not found' },
        { status: 404 }
      );
    }
    
    return HttpResponse.json({
      success: true,
      symbol: stock.symbol,
      price: stock.current_price,
      change: stock.price_change_today,
      change_percent: stock.change_percent,
      volume: stock.volume,
      timestamp: new Date().toISOString(),
      market_data: {
        open: stock.current_price * 0.99,
        high: stock.current_price * 1.02,
        low: stock.current_price * 0.98,
        previous_close: stock.current_price - stock.price_change_today,
        market_cap: stock.market_cap,
        pe_ratio: stock.pe_ratio,
      },
      cached: false,
    });
  }),

  http.get(`${API_BASE}/api/stocks/search/`, ({ request }) => {
    const url = new URL(request.url);
    const query = url.searchParams.get('q') || '';
    
    if (query.length < 2) {
      return HttpResponse.json({
        success: true,
        data: [],
      });
    }
    
    const results = mockStocks
      .filter(stock => 
        stock.symbol.toLowerCase().includes(query.toLowerCase()) ||
        stock.company_name.toLowerCase().includes(query.toLowerCase())
      )
      .map(stock => ({
        symbol: stock.symbol,
        name: stock.company_name,
        exchange: stock.exchange,
      }));
    
    return HttpResponse.json({
      success: true,
      data: results,
    });
  }),

  http.get(`${API_BASE}/api/trending/`, () => {
    return HttpResponse.json(mockTrending);
  }),

  http.get(`${API_BASE}/api/market/stats/`, () => {
    return HttpResponse.json({
      success: true,
      data: {
        total_stocks: 5000,
        gainers: 2500,
        losers: 2000,
        unchanged: 500,
        volume_leaders: ['AAPL', 'TSLA', 'AMZN'],
      },
    });
  }),

  http.get(`${API_BASE}/api/platform-stats/`, () => {
    return HttpResponse.json({
      success: true,
      nyse_stocks: 0,
      nasdaq_stocks: 5,
      total_stocks: 5,
      total_indicators: 14,
      scanner_combinations: 70,
      platform_stats: {
        total_users: 1000,
        premium_users: 100,
        recent_stock_updates: 5,
        api_calls_today: 1500,
      },
      market_stats: {
        exchanges_supported: ['NYSE', 'NASDAQ'],
        data_sources: ['yfinance', 'real-time feeds'],
        update_frequency: 'Real-time',
      },
      timestamp: new Date().toISOString(),
    });
  }),

  http.get(`${API_BASE}/api/usage/`, () => {
    return HttpResponse.json({
      success: true,
      usage: {
        plan: 'free',
        monthly_used: 5,
        monthly_limit: 15,
        daily_used: 2,
        daily_limit: 15,
      },
      rate_limits: {
        requests_this_minute: 1,
        requests_this_hour: 10,
        requests_this_day: 25,
        rate_limited: false,
      },
    });
  }),

  // Portfolio and watchlist endpoints
  http.get(`${API_BASE}/api/portfolio/`, () => {
    return HttpResponse.json({
      success: true,
      data: [],
    });
  }),

  http.post(`${API_BASE}/api/portfolio/add/`, async ({ request }) => {
    const body = await request.json() as any;
    return HttpResponse.json({
      success: true,
      message: `Added ${body.symbol} to portfolio`,
    });
  }),

  http.get(`${API_BASE}/api/watchlist/`, () => {
    return HttpResponse.json({
      success: true,
      data: [],
    });
  }),

  http.post(`${API_BASE}/api/watchlist/add/`, async ({ request }) => {
    const body = await request.json() as any;
    return HttpResponse.json({
      success: true,
      message: `Added ${body.symbol} to watchlist`,
    });
  }),

  // Billing endpoints
  http.get(`${API_BASE}/api/billing/current-plan/`, () => {
    return HttpResponse.json({
      success: true,
      data: {
        plan: 'free',
        is_premium: false,
        limits: { monthly: 15, daily: 15 },
        subscription: { active: false, trial_used: false },
      },
    });
  }),

  http.get(`${API_BASE}/api/billing/history/`, () => {
    return HttpResponse.json({
      success: true,
      data: [],
      message: 'No billing history found',
    });
  }),

  http.get(`${API_BASE}/api/billing/stats/`, () => {
    return HttpResponse.json({
      success: true,
      data: {
        total_spent: 0,
        current_month_spending: 0,
        plan_cost: 0,
      },
    });
  }),
];