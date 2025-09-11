import axios from "axios";
import { getCache, setCache } from "../lib/cache";

// Use REACT_APP_BACKEND_URL from environment, fallback to window.location.origin
const BASE_URL = process.env.REACT_APP_BACKEND_URL || (typeof window !== 'undefined' ? `${window.location.origin}` : '');

if (!process.env.REACT_APP_BACKEND_URL && BASE_URL) {
  // Informational log only
  console.warn("REACT_APP_BACKEND_URL not set; using window.location.origin as backend base.");
} else if (!BASE_URL) {
  console.error("REACT_APP_BACKEND_URL is not set and window origin unavailable. API calls will fail.");
}

export const API_ROOT = `${BASE_URL}/api`;
export const REVENUE_ROOT = `${BASE_URL}/api/revenue`;

// Secondary axios instance for non-API root endpoints (e.g., Django accounts login view for CSRF cookie)
const site = axios.create({
  baseURL: BASE_URL,
  withCredentials: true,
});

// Simple network event bus for latency indicator
(function initNetBus(){
  if (typeof window === 'undefined') return;
  if (!window.__NET) {
    const listeners = { start: new Set(), end: new Set(), slow: new Set() };
    window.__NET = {
      on(evt, cb){ listeners[evt]?.add(cb); },
      off(evt, cb){ listeners[evt]?.delete(cb); },
      emit(evt, payload){ listeners[evt]?.forEach(cb=>{ try{ cb(payload); } catch{} }); },
    };
  }
})();

export const api = axios.create({
  baseURL: API_ROOT,
  withCredentials: true,
  // Ensure axios picks up Django's CSRF cookie/header names when present
  xsrfCookieName: 'csrftoken',
  xsrfHeaderName: 'X-CSRFToken',
});

// Sanitize params to avoid sending empty/null/"none" values that cause unintended backend filters
function sanitizeParams(rawParams = {}) {
  const cleaned = {};
  Object.entries(rawParams || {}).forEach(([key, value]) => {
    if (value === undefined || value === null) return;
    if (typeof value === 'string') {
      const v = value.trim();
      if (!v) return;
      if (v.toLowerCase() === 'none' || v.toLowerCase() === 'null') return;
      cleaned[key] = v;
      return;
    }
    if (Array.isArray(value)) {
      const v = value.filter((x) => x !== undefined && x !== null && String(x).trim() !== '' && String(x).toLowerCase() !== 'none' && String(x).toLowerCase() !== 'null');
      if (v.length === 0) return;
      cleaned[key] = v;
      return;
    }
    cleaned[key] = value;
  });
  return cleaned;
}

// Fetch all stocks in batches to enable client-side sorting/pagination over the full set
export async function fetchAllStocks(baseParams = {}) {
  const PAGE_SIZE = Number(baseParams.limit) && Number(baseParams.limit) > 0 ? Number(baseParams.limit) : 500;
  const params = sanitizeParams({ ...baseParams });
  let offset = 0;
  const all = [];
  // Safety cap to prevent infinite loops
  for (let page = 0; page < 100; page++) {
    const pageParams = { ...params, limit: PAGE_SIZE, offset };
    // Ensure we do not leak empty/invalid values
    const safePageParams = sanitizeParams(pageParams);
    let response;
    try {
      const { data } = await api.get('/stocks/', { params: safePageParams });
      response = data;
    } catch (error) {
      // Surface partial results if any and stop
      break;
    }
    const items = Array.isArray(response) ? response : (response?.data || response?.results || []);
    if (!Array.isArray(items) || items.length === 0) break;
    all.push(...items);
    if (items.length < PAGE_SIZE) break;
    offset += PAGE_SIZE;
  }
  return all;
}

// ====================
// Plan limits enforcement (client-side guard; server should enforce as source of truth)
// ====================
const PLAN_LIMITS = {
  free: { monthlyApi: 100, alerts: 5, watchlists: 1, portfolios: 0 },
  bronze: { monthlyApi: 1500, alerts: 25, watchlists: 3, portfolios: 1 },
  silver: { monthlyApi: 5000, alerts: 100, watchlists: 10, portfolios: Infinity },
  gold: { monthlyApi: Infinity, alerts: Infinity, watchlists: Infinity, portfolios: Infinity },
};

function getStoredUserPlan() {
  try {
    const raw = window.localStorage.getItem('rts_user');
    if (!raw) return 'free';
    try {
      const parsed = JSON.parse(raw);
      return (parsed?.plan || 'free').toLowerCase();
    } catch {
      try {
        const parsed = JSON.parse(atob(raw));
        return (parsed?.plan || 'free').toLowerCase();
      } catch {
        return 'free';
      }
    }
  } catch { return 'free'; }
}

function getPlanLimits() {
  const plan = getStoredUserPlan();
  return PLAN_LIMITS[plan] || PLAN_LIMITS.free;
}

// REMOVED: Daily API quotas - server is source of truth
function ensureApiQuotaAndIncrement() {
  // Always return true - let server handle rate limits
  return true;
}

function getCsrfToken() {
  try {
    const m = document.cookie.match(/csrftoken=([^;]+)/);
    return m ? decodeURIComponent(m[1]) : null;
  } catch { return null; }
}

async function ensureCsrfCookie() {
  try {
    // Attempt to fetch CSRF cookie from a dedicated endpoint if available
    // Fallback to a lightweight GET that may be decorated server-side
    const hasToken = !!getCsrfToken();
    if (hasToken) return;
    // Prefer Django auth HTML endpoints which typically set csrftoken
    if (!getCsrfToken()) await site.get('/accounts/login/').catch(() => {});
    if (!getCsrfToken()) await site.get('/admin/login/').catch(() => {});
    // Then try API health/document endpoints which the backend can decorate with ensure_csrf_cookie
    if (!getCsrfToken()) await api.get('/health/').catch(() => {});
    if (!getCsrfToken()) await api.get('/health/detailed/').catch(() => {});
    if (!getCsrfToken()) await api.get('/').catch(() => {});
  } catch {}
}

let __csrfTokenCache = null;
async function fetchApiCsrfToken() {
  try {
    const { data } = await api.get('/auth/csrf/');
    const token = data?.csrfToken || data?.csrf_token || data?.token || null;
    if (token) __csrfTokenCache = token;
    return token;
  } catch {
    return null;
  }
}

// Attach token, CSRF safety and timing
api.interceptors.request.use((config) => {
  try {
    config.headers['X-Requested-With'] = 'XMLHttpRequest';
    const method = (config.method || 'get').toLowerCase();
    const csrf = __csrfTokenCache || getCsrfToken();
    if (csrf && ['post','put','patch','delete'].includes(method)) {
      config.headers['X-CSRFToken'] = csrf;
    }

    const token = (window.localStorage.getItem("rts_token") || '').trim();
    if (token && token !== 'undefined' && token !== 'null') {
      config.headers.Authorization = `Bearer ${token}`;
    }
  } catch {}
  // Skip client-side quota check - server handles all rate limiting
  config.metadata = { start: Date.now(), url: `${config.baseURL || ''}${config.url || ''}` };
  window.__NET?.emit('start', { url: config.metadata.url });
  return config;
});

api.interceptors.response.use(
  (response) => {
    const dur = Date.now() - (response.config.metadata?.start || Date.now());
    if (dur > 600) window.__NET?.emit('slow', { url: response.config.metadata?.url, duration: dur, status: response.status });
    window.__NET?.emit('end');
    // Non-blocking usage tracking for stock-data endpoints only
    try {
      const cfg = response.config || {};
      const method = (cfg.method || 'get').toUpperCase();
      const path = String(cfg.url || '');
      const isTrack = path.includes('/usage/track');
      const shouldTrack = method === 'GET' && !isTrack && (
        path.startsWith('/stocks/') ||
        path.startsWith('/stock/') ||
        path.startsWith('/search/') ||
        path.startsWith('/trending/') ||
        path.startsWith('/realtime/') ||
        path.startsWith('/filter/') ||
        path.startsWith('/market-stats/')
      );
      if (shouldTrack) {
        // Use authorized API client so usage increments for logged-in users
        api.post('/usage/track/', { endpoint: `/api${path}`, method }).catch(() => {});
      }
    } catch {}
    return response;
  },
  (error) => {
    try {
      const cfg = error.config || {}; const dur = Date.now() - (cfg.metadata?.start || Date.now());
      if (dur > 600) window.__NET?.emit('slow', { url: cfg.metadata?.url, duration: dur, status: error.response?.status });
      window.__NET?.emit('end');
    } catch {}
    if (error.response?.status === 401) {
      // Do not forcibly sign the user out on incidental 401s (e.g., news feed) – let pages handle it gracefully
      // Keep token/state intact and surface the error to callers
      return Promise.reject(error);
    }
    return Promise.reject(error);
  }
);

// Client-side error logging (observability)
export async function logClientError(payload) {
  try {
    await api.post('/logs/client/', { ...payload, ts: new Date().toISOString(), path: window.location.pathname });
  } catch {}
}

export async function logClientMetric(payload) {
  try {
    await api.post('/logs/metrics/', { ...payload, ts: new Date().toISOString() });
  } catch {}
}

// Expose to window for ErrorBoundary
if (typeof window !== 'undefined') {
  window.logClientError = logClientError;
}

// ====================
// Helpers: Normalizers for common endpoints
// ====================
function safeNumber(v, d = 0) { const n = Number(v); return Number.isFinite(n) ? n : d; }

export function normalizeTrending(raw) {
  const d = raw || {};
  const toStock = (s) => ({
    ticker: s?.ticker || s?.symbol || '-',
    name: s?.name || s?.company_name || '-',
    current_price: safeNumber(s?.current_price),
    price_change_today: safeNumber(s?.price_change_today ?? s?.price_change),
    change_percent: safeNumber(s?.change_percent),
    volume: safeNumber(s?.volume),
    market_cap: safeNumber(s?.market_cap),
  });
  return {
    high_volume: Array.isArray(d.high_volume) ? d.high_volume.map(toStock) : [],
    top_gainers: Array.isArray(d.top_gainers) ? d.top_gainers.map(toStock) : [],
    most_active: Array.isArray(d.most_active) ? d.most_active.map(toStock) : [],
    last_updated: d.last_updated || null,
  };
}

export function normalizeMarketStats(raw) {
  const d = raw || {};
  const mo = d.market_overview || {};
  return {
    market_overview: {
      total_stocks: safeNumber(mo.total_stocks),
      nyse_stocks: safeNumber(mo.nyse_stocks),
      gainers: safeNumber(mo.gainers),
      losers: safeNumber(mo.losers),
      unchanged: safeNumber(mo.unchanged),
    },
    top_gainers: Array.isArray(d.top_gainers) ? d.top_gainers : [],
    top_losers: Array.isArray(d.top_losers) ? d.top_losers : [],
    most_active: Array.isArray(d.most_active) ? d.most_active : [],
    // Pass through sector performance if provided by backend under common keys
    sectors: Array.isArray(d.sectors)
      ? d.sectors
      : (Array.isArray(d.sector_performance) ? d.sector_performance : []),
    last_updated: d.last_updated || null,
  };
}

async function cachedGet(path, cacheKey, ttlMs = 30000) {
  const cached = getCache(cacheKey);
  if (cached) return { cached: true, data: cached };
  const { data } = await api.get(path);
  setCache(cacheKey, data, ttlMs);
  return { cached: false, data };
}

export async function getTrendingSafe() {
  try {
    const res = await cachedGet('/trending/', 'trending', 30000);
    return { success: true, data: normalizeTrending(res.data) };
  } catch (error) {
    return { success: false, error: 'Service unavailable' };
  }
}

export async function getMarketStatsSafe() {
  try {
    const res = await cachedGet('/market-stats/', 'market-stats', 30000);
    return { success: true, data: normalizeMarketStats(res.data) };
  } catch (error) {
    return { success: false, error: 'Service unavailable' };
  }
}

export async function getStatisticsSafe() {
  try {
    const { data } = await api.get("/statistics/");
    return { success: true, data: data || { market_overview: {}, top_performers: {}, subscriptions: {} } };
  } catch (error) {
    return { success: false, error: error?.response?.data?.message || 'Failed to load statistics', data: { market_overview: {}, top_performers: {}, subscriptions: {} } };
  }
}

// ====================
// HEALTH & STATUS
// ====================
export async function pingHealth() { const { data } = await api.get('/health/'); return data; }
export async function getEndpointStatus() { const { data } = await api.get('/endpoint-status/'); return data; }

// ====================
// STOCKS & MARKET DATA
// ====================
export async function listStocks(params = {}) { 
  try {
    const { data } = await api.get('/stocks/', { params: sanitizeParams(params) });
    return data;
  } catch (error) {
    console.error('Failed to fetch stocks:', error);
    throw error;
  }
}
export async function getStock(ticker) { const { data } = await api.get(`/stock/${encodeURIComponent(ticker)}/`); return data; }
export async function searchStocks(q) { const { data } = await api.get('/search/', { params: { q } }); return data; }
export async function getTrending() { const { data } = await api.get('/trending/'); return data; }
export async function getMarketStats() { const { data } = await api.get('/market-stats/'); return data; }
// Align with backend quote endpoint: /stocks/{symbol}/quote
export async function getRealTimeQuote(ticker) { const { data } = await api.get(`/stocks/${encodeURIComponent(ticker)}/quote`); return data; }
export async function filterStocks(params = {}) { const { data } = await api.get('/filter/', { params: sanitizeParams(params) }); return data; }
export async function getStatistics() { const { data } = await api.get('/statistics/'); return data; }
export async function getMarketData() { const { data } = await api.get('/market-data/'); return data; }

// ====================
// AUTHENTICATION
// ====================
export async function login(username, password) {
  try {
    // Contract: fetch CSRF from API endpoint first, then ensure cookie
    const token = await fetchApiCsrfToken();
    if (!token) {
      await ensureCsrfCookie();
    }
    const { data } = await api.post('/auth/login/', { username, password });
    if (data.success && data.data) {
      // Store user data if login successful
      return { success: true, data: data.data, message: data.message };
    }
    return { success: false, message: data.message || 'Login failed' };
  } catch (error) {
    return { success: false, message: error.response?.data?.detail || error.response?.data?.message || 'Login failed' };
  }
}

export async function logout() { 
  try { 
    await api.post('/auth/logout/'); 
  } catch {} finally { 
    localStorage.removeItem('rts_token'); 
  } 
}

export async function registerUser(userData) {
  try {
    // Since there's no explicit registration endpoint in the provided list,
    // I'll assume it follows Django's standard pattern at /auth/register/
    const { data } = await api.post('/auth/register/', {
      username: userData.username,
      email: userData.email,
      password: userData.password,
      first_name: userData.first_name,
      last_name: userData.last_name
    });
    
    if (data.success) {
      return { 
        success: true, 
        data: data.data,
        message: data.message || 'Registration successful! Please verify your email.'
      };
    }
    return { success: false, message: data.message || 'Registration failed' };
  } catch (error) {
    if (error?.response?.status === 409) {
      return {
        success: false,
        message: 'This email is already registered. Please sign in or reset your password.'
      };
    }
    return {
      success: false,
      message: error.response?.data?.message || error.response?.data?.detail || 'Registration failed'
    };
  }
}
export async function getProfile() { const { data } = await api.get('/user/profile/'); return data; }
export async function updateProfile(profileData) { const { data } = await api.post('/user/profile/', profileData); return data; }
export async function changePassword(passwordData) { const { data } = await api.post('/user/change-password/', passwordData); return data; }

// ====================
// PORTFOLIO
// ====================
export async function getPortfolio() { 
  try {
    const { data } = await api.get('/portfolio/');
    return data;
  } catch (error) {
    console.error('Failed to fetch portfolio:', error);
    throw error;
  }
}
export async function addPortfolio(payload) { const { data } = await api.post('/portfolio/add/', payload); return data; }
export async function deletePortfolio(id) { const { data } = await api.delete(`/portfolio/${id}/`); return data; }

// ====================
// WATCHLISTS
// ====================
export async function getWatchlist() { 
  try {
    const { data } = await api.get('/watchlist/');
    return data;
  } catch (error) {
    console.error('Failed to fetch watchlist:', error);
    throw error;
  }
}
export async function addWatchlist(symbol, opts = {}) { const { data } = await api.post('/watchlist/add/', { symbol, ...opts }); return data; }
export async function deleteWatchlist(id) { const { data } = await api.delete(`/watchlist/${id}/`); return data; }

// ====================
// ALERTS
// ====================
export async function alertsMeta() { const { data } = await api.get('/alerts/create/'); return data; }
export async function createAlert(payload) { const { data } = await api.post('/alerts/create/', payload); return data; }

// ====================
// BILLING & PLANS
// ====================
export async function getBillingHistory(params = {}) { 
  const { data } = await api.get('/billing/history/', { params }); 
  return data; 
}

export async function getCurrentPlan() { 
  const { data } = await api.get('/billing/current-plan/'); 
  return data; 
}

export async function changePlan(planData) { 
  const { data } = await api.post('/billing/change-plan/', planData); 
  return data; 
}

export async function getBillingStats() { 
  const { data } = await api.get('/billing/stats/'); 
  return data; 
}

export async function downloadInvoice(invoiceId) { 
  const response = await api.get(`/billing/download/${invoiceId}/`, { responseType: 'blob' }); 
  return response.data; 
}

export async function updatePaymentMethod(paymentData) { 
  const { data } = await api.post('/user/update-payment/', paymentData); 
  return data; 
}

// PayPal Integration Functions - Updated for Django backend
export async function createPayPalOrder(planType, billingCycle, discountCode = null) {
  try {
    const orderData = {
      plan_type: planType,
      billing_cycle: billingCycle,
      discount_code: discountCode
    };
    
    // This integrates with your Django backend PayPal handling
    const { data } = await api.post('/billing/create-paypal-order/', orderData);
    return data;
  } catch (error) {
    console.error('PayPal order creation failed:', error);
    throw error;
  }
}

export async function capturePayPalOrder(orderId, paymentData) {
  try {
    const { data } = await api.post('/billing/capture-paypal-order/', {
      order_id: orderId,
      payment_data: paymentData
    });
    return data;
  } catch (error) {
    console.error('PayPal order capture failed:', error);
    throw error;
  }
}

// Alerts helpers (axios with credentials/CSRF)
export async function getAlerts() { const { data } = await api.get('/alerts/'); return data; }
export async function deleteAlert(alertId) { const { data } = await api.post(`/alerts/${encodeURIComponent(alertId)}/delete/`); return data; }
export async function toggleAlert(alertId) { const { data } = await api.post(`/alerts/${encodeURIComponent(alertId)}/toggle/`); return data; }

// ====================
// NOTIFICATIONS
// ====================
export async function getNotificationSettings() { const { data } = await api.get('/user/notification-settings/'); return data; }
export async function updateNotificationSettings(settings) { const { data } = await api.post('/user/notification-settings/', settings); return data; }
export async function getNotificationHistory(params = {}) { const { data } = await api.get('/notifications/history/', { params }); return data; }
export async function markNotificationsRead(payload) { const { data } = await api.post('/notifications/mark-read/', payload); return data; }

// ====================
// NEWS
// ====================
export async function getNewsFeed(params = {}) { const { data } = await api.get('/news/feed/', { params }); return data; }
export async function markNewsRead(newsId) { const { data } = await api.post('/news/mark-read/', { news_id: newsId }); return data; }
export async function markNewsClicked(newsId) { const { data } = await api.post('/news/mark-clicked/', { news_id: newsId }); return data; }
export async function updateNewsPreferences(preferences) { const { data } = await api.post('/news/preferences/', preferences); return data; }
export async function syncPortfolioNews() { const { data } = await api.post('/news/sync-portfolio/'); return data; }

// ====================
// USAGE (Dashboard)
// ====================
export async function getUsageSummary() {
  const { data } = await api.get('/usage/');
  return data;
}

//====================
// REVENUE & PAYMENTS (PAYPAL INTEGRATION)
//====================
export async function validateDiscountCode(code) { 
  const { data } = await api.post('/revenue/validate-discount/', { code }); 
  return data; 
}

export async function applyDiscountCode(code, amount) { 
  const { data } = await api.post('/revenue/apply-discount/', { code, amount }); 
  return data; 
}

export async function recordPayment(paymentData) { 
  const { data } = await api.post('/revenue/record-payment/', paymentData); 
  return data; 
}

export async function getRevenueAnalytics(monthYear = null) { 
  const url = monthYear ? `/revenue/revenue-analytics/${monthYear}/` : `/revenue/revenue-analytics/`; 
  const { data } = await api.get(url); 
  return data; 
}

export async function initializeDiscountCodes() { 
  const { data } = await api.post('/revenue/initialize-codes/'); 
  return data; 
}

// ====================
// SUBSCRIPTIONS
// ====================
export async function subscribe(email, category = null) { const { data } = await api.post('/subscription/', { email, category }); return data; }
export async function wordpressSubscribe(email, category = null) { const { data } = await api.post('/wordpress/subscribe/', { email, category }); return data; }

// ====================
// WORDPRESS INTEGRATION
// ====================
export async function getWordPressStocks(params = {}) { const { data } = await api.get('/wordpress/stocks/', { params }); return data; }
export async function getWordPressNews(params = {}) { const { data } = await api.get('/wordpress/news/', { params }); return data; }
export async function getWordPressAlerts(params = {}) { const { data } = await api.get('/wordpress/alerts/', { params }); return data; }
export async function updateStocks(symbols) { const { data } = await api.post('/stocks/update/', { symbols }); return data; }
export async function updateNews() { const { data } = await api.post('/news/update/'); return data; }