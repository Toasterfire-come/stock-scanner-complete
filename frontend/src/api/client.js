import axios from "axios";
import { getCache, setCache } from "../lib/cache";

// Use REACT_APP_BACKEND_URL exclusively from environment, with production fallback
const BASE_URL = process.env.REACT_APP_BACKEND_URL || "https://api.retailtradescanner.com";

if (!BASE_URL) {
  console.error("REACT_APP_BACKEND_URL is not set. API calls will fail.");
}

export const API_ROOT = `${BASE_URL}/api`;

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

// ====================
// Plan limits enforcement (client-side guard; server should enforce as source of truth)
// ====================
const PLAN_LIMITS = {
  free: { 
    monthlyApi: 30, 
    alerts: 0, 
    watchlists: 0, 
    portfolios: 1,
    screeners: 1
  },
  bronze: { 
    monthlyApi: 1500, 
    alerts: 100, 
    watchlists: 2, 
    portfolios: 1,
    screeners: 10
  },
  silver: { 
    monthlyApi: 5000, 
    alerts: 500, 
    watchlists: 5, 
    portfolios: 5,
    screeners: 20
  },
  gold: { 
    monthlyApi: Infinity, 
    alerts: Infinity, 
    watchlists: Infinity, 
    portfolios: Infinity,
    screeners: Infinity
  },
};

// API Call Cost Mapping according to specifications
const API_CALL_COSTS = {
  'listStocks': 5,           // listing all stocks = 5
  'getStock': 1,             // one stock = 1
  'runScreener': 2,          // running a screener = 2
  'addAlert': 2,             // adding an alert = 2
  'loadMarket': 2,           // loading market page = 2
  'createWatchlist': 2,      // making a watchlist = 2
  'default': 1               // everything else = 1
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

// API call counting with cost-based system
function getApiCallCost(operationType) {
  return API_CALL_COSTS[operationType] || API_CALL_COSTS.default;
}

function trackApiCall(operationType) {
  try {
    const cost = getApiCallCost(operationType);
    const currentMonth = new Date().toISOString().slice(0, 7); // YYYY-MM format
    const storageKey = `api_usage_${currentMonth}`;
    
    let usage = JSON.parse(localStorage.getItem(storageKey) || '{"calls": 0, "operations": {}}');
    usage.calls += cost;
    usage.operations[operationType] = (usage.operations[operationType] || 0) + 1;
    
    localStorage.setItem(storageKey, JSON.stringify(usage));
    return usage.calls;
  } catch {
    return 0;
  }
}

function getCurrentApiUsage() {
  try {
    const currentMonth = new Date().toISOString().slice(0, 7);
    const storageKey = `api_usage_${currentMonth}`;
    const usage = JSON.parse(localStorage.getItem(storageKey) || '{"calls": 0, "operations": {}}');
    return usage.calls;
  } catch {
    return 0;
  }
}

function checkApiQuota(operationType) {
  const limits = getPlanLimits();
  const cost = getApiCallCost(operationType);
  const currentUsage = getCurrentApiUsage();
  
  if (limits.monthlyApi === Infinity) return true;
  return (currentUsage + cost) <= limits.monthlyApi;
}

function ensureApiQuotaAndIncrement(operationType = 'default') {
  if (!checkApiQuota(operationType)) {
    const limits = getPlanLimits();
    const plan = getStoredUserPlan();
    throw new Error(`API limit exceeded. Your ${plan} plan allows ${limits.monthlyApi} calls per month. Consider upgrading your plan.`);
  }
  trackApiCall(operationType);
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
    const hasToken = !!getCsrfToken();
    if (hasToken) return;
    // Use only documented API endpoints for CSRF and health
    if (!getCsrfToken()) await api.get('/auth/csrf/').catch(() => {});
    if (!getCsrfToken()) await api.get('/health/').catch(() => {});
    if (!getCsrfToken()) await api.get('/health/detailed/').catch(() => {});
    if (!getCsrfToken()) await api.get('/health/ready/').catch(() => {});
    if (!getCsrfToken()) await api.get('/health/live/').catch(() => {});
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
  
  config.metadata = { start: Date.now(), url: `${config.baseURL || ''}${config.url || ''}` };
  window.__NET?.emit('start', { url: config.metadata.url });
  return config;
});

api.interceptors.response.use(
  (response) => {
    const dur = Date.now() - (response.config.metadata?.start || Date.now());
    if (dur > 600) window.__NET?.emit('slow', { url: response.config.metadata?.url, duration: dur, status: response.status });
    window.__NET?.emit('end');
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
    ensureApiQuotaAndIncrement('getTrending');
    const res = await cachedGet('/trending/', 'trending', 30000);
    return { success: true, data: normalizeTrending(res.data) };
  } catch (error) {
    return { success: false, error: error.message || 'Service unavailable' };
  }
}

export async function getMarketStatsSafe() {
  try {
    ensureApiQuotaAndIncrement('loadMarket');
    const res = await cachedGet('/market-stats/', 'market-stats', 30000);
    return { success: true, data: normalizeMarketStats(res.data) };
  } catch (error) {
    return { success: false, error: error.message || 'Service unavailable' };
  }
}

export async function getStatisticsSafe() {
  try {
    ensureApiQuotaAndIncrement('getStatistics');
    const { data } = await api.get('/status/');
    return { success: true, data };
  } catch (error) {
    return { success: false, error: error?.response?.data?.message || error.message || 'Failed to load system status', data: {} };
  }
}

// ====================
// HEALTH & STATUS
// ====================
export async function pingHealth() {
  // Use documented health endpoints only
  try {
    const { data } = await api.get('/health/', { timeout: 5000 });
    return data;
  } catch (e1) {
    try { const { data } = await api.get('/health/detailed/', { timeout: 5000 }); return data; } catch (e2) {}
    try { const { data } = await api.get('/health/ready/', { timeout: 5000 }); return data; } catch (e3) {}
    const { data } = await api.get('/health/live/', { timeout: 5000 });
    return data;
  }
}
export async function getEndpointStatus() {
  // Normalize system status to an object used by EndpointStatus page
  const { data } = await api.get('/status/');
  const ok = (data?.status || '').toLowerCase() === 'ok';
  return {
    success: true,
    data: {
      endpoints: [],
      total_tested: 1,
      successful: ok ? 1 : 0,
      failed: ok ? 0 : 1,
    }
  };
}

// ====================
// STOCKS & MARKET DATA
// ====================
export async function listStocks(params = {}, options = {}) { 
  try {
    ensureApiQuotaAndIncrement('listStocks');
    const { data } = await api.get('/stocks/', { params, signal: options.signal });
    return data;
  } catch (error) {
    console.error('Failed to fetch stocks:', error);
    throw error;
  }
}
export async function getStock(ticker) { 
  ensureApiQuotaAndIncrement('getStock');
  const { data } = await api.get(`/stocks/${encodeURIComponent(ticker)}/`); 
  return data; 
}
export async function searchStocks(q, options = {}) { 
  ensureApiQuotaAndIncrement('searchStocks');
  const { data } = await api.get('/stocks/search/', { params: { q }, signal: options.signal }); 
  return data; 
}
export async function getTrending() { 
  ensureApiQuotaAndIncrement('getTrending');
  const { data } = await api.get('/trending/'); 
  return data; 
}
export async function getMarketStats() { 
  ensureApiQuotaAndIncrement('loadMarket');
  const { data } = await api.get('/market-stats/'); 
  return data; 
}
export async function getRealTimeQuote(ticker) { 
  ensureApiQuotaAndIncrement('getStock');
  // Use the stock detail endpoint as the source of truth for current price
  const { data } = await api.get(`/stocks/${encodeURIComponent(ticker)}/`); 
  return data; 
}
export async function filterStocks(params = {}) { 
  ensureApiQuotaAndIncrement('runScreener');
  const { data } = await api.get('/filter/', { params }); 
  return data; 
}

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
    if (data.success && (data.user || data.data)) {
      // Normalize response to { success, data: user }
      const user = data.user || data.data;
      return { success: true, data: user, message: data.message };
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
// Profile update endpoint is not available in the allowed API list
export async function updateProfile(profileData) { return { success: false, message: 'Profile update is not supported.' }; }
export async function changePassword(passwordData) {
  const payload = {
    old_password: passwordData.old_password || passwordData.current_password,
    new_password: passwordData.new_password,
  };
  const { data } = await api.post('/user/change-password/', payload); return data; 
}

// ====================
// PORTFOLIO
// ====================
export async function getPortfolio() { 
  try {
    ensureApiQuotaAndIncrement('getPortfolio');
    const { data } = await api.get('/portfolio/');
    return data;
  } catch (error) {
    console.error('Failed to fetch portfolio:', error);
    throw error;
  }
}
export async function addPortfolio(payload) { 
  ensureApiQuotaAndIncrement('addPortfolio');
  const { data } = await api.post('/portfolio/add/', payload); 
  return data; 
}
export async function deletePortfolio(id) { 
  ensureApiQuotaAndIncrement('deletePortfolio');
  const { data } = await api.delete(`/portfolio/${id}/`); 
  return data; 
}

// ====================
// WATCHLISTS
// ====================
// Watchlists (use documented endpoints)
export async function listWatchlists() {
  // Prefer RESTful list: GET /api/watchlist/; then try legacy variants
  const attempts = [
    () => api.get('/watchlist/'),
    () => api.get('/watchlist/list/'),
    () => api.get('/watchlists/'),
  ];
  let lastErr;
  for (const attempt of attempts) {
    try {
      const { data } = await attempt();
      return data;
    } catch (e) {
      lastErr = e;
    }
  }
  throw lastErr;
}
export async function createWatchlist(payload) {
  // Try a few common endpoints/methods
  const attempts = [
    () => api.post('/watchlist/create/', payload),
    () => api.post('/watchlist/', payload),
    () => api.put('/watchlist/', payload),
  ];
  let lastErr;
  for (const attempt of attempts) {
    try { const { data } = await attempt(); return data; } catch (e) { lastErr = e; }
  }
  throw lastErr;
}

export async function addWatchlistStock(payload) {
  // Normalize payload: prefer watchlist_id if numeric, otherwise send watchlist_name
  const norm = { stock_ticker: payload.stock_ticker };
  if (Number.isFinite(Number(payload.watchlist_id))) norm.watchlist_id = Number(payload.watchlist_id);
  if (payload.watchlist_name && !norm.watchlist_id) norm.watchlist_name = payload.watchlist_name;
  if (payload.notes) norm.notes = payload.notes;

  const attempts = [
    () => api.post('/watchlist/add-stock/', norm),
    () => api.put('/watchlist/add-stock/', norm),
    () => api.post('/watchlist/add/', norm),
    () => api.post('/watchlists/add-stock/', norm),
  ];
  let lastErr;
  for (const attempt of attempts) {
    try { const { data } = await attempt(); return data; } catch (e) {
      if (e?.response?.status && ![404, 405, 400].includes(e.response.status)) { lastErr = e; break; }
      lastErr = e;
    }
  }
  throw lastErr;
}

export async function removeWatchlistStock(payload) {
  const norm = { stock_ticker: payload.stock_ticker };
  if (Number.isFinite(Number(payload.watchlist_id))) norm.watchlist_id = Number(payload.watchlist_id);
  if (payload.watchlist_name && !norm.watchlist_id) norm.watchlist_name = payload.watchlist_name;

  const attempts = [
    () => api.delete('/watchlist/remove-stock/', { data: norm }),
    () => api.post('/watchlist/remove-stock/', norm),
    () => api.post('/watchlist/remove/', norm),
  ];
  let lastErr;
  for (const attempt of attempts) {
    try { const { data } = await attempt(); return data; } catch (e) {
      if (e?.response?.status && ![404, 405, 400].includes(e.response.status)) { lastErr = e; break; }
      lastErr = e;
    }
  }
  throw lastErr;
}
// Backward-compatible wrappers (may return limited data)
export async function getWatchlist() { try { ensureApiQuotaAndIncrement('getWatchlist'); const res = await listWatchlists(); return res; } catch (e) { throw e; } }
export async function addWatchlist(symbol, opts = {}) {
  // Prefer the RESTful endpoint that expects { symbol, watchlist_name, notes, alert_price }
  const payload = {
    symbol: (symbol || '').toUpperCase(),
    watchlist_name: opts.watchlist_name || 'My Watchlist',
    notes: opts.notes || undefined,
    alert_price: opts.alert_price != null ? opts.alert_price : undefined,
  };
  try {
    const { data } = await api.post('/watchlist/add/', payload);
    return data;
  } catch (e) {
    // Fallback to legacy add if RESTful endpoint is unavailable
    const legacyPayload = { stock_ticker: payload.symbol };
    if (opts.watchlist_id) legacyPayload.watchlist_id = opts.watchlist_id;
    legacyPayload.watchlist_name = opts.watchlist_name || (!opts.watchlist_id ? 'My Watchlist' : undefined);
    if (opts.notes) legacyPayload.notes = opts.notes;
    return addWatchlistStock(legacyPayload);
  }
}
export async function deleteWatchlist(idOrPayload) {
  // Support deleting by item id (RESTful) or via legacy payload
  if (typeof idOrPayload === 'object') {
    return removeWatchlistStock(idOrPayload);
  }
  const id = String(idOrPayload || '').trim();
  if (!id) {
    throw new Error('deleteWatchlist requires item id or {watchlist_id, stock_ticker}');
  }
  const { data } = await api.delete(`/watchlist/${encodeURIComponent(id)}/`);
  return data;
}

// ====================
// ALERTS
// ====================
export async function alertsMeta() { 
  ensureApiQuotaAndIncrement('default');
  const { data } = await api.get('/alerts/create/'); 
  return data; 
}
export async function createAlert(payload) { 
  ensureApiQuotaAndIncrement('addAlert');
  const { data } = await api.post('/alerts/create/', payload); 
  return data; 
}

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
    const orderData = { plan_type: planType, billing_cycle: billingCycle, discount_code: discountCode };
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
export async function getNewsFeed(params = {}) { 
  ensureApiQuotaAndIncrement('getNews');
  const { data } = await api.get('/news/feed/', { params }); 
  return data; 
}
export async function markNewsRead(newsId) { const { data } = await api.post('/news/mark-read/', { news_id: newsId }); return data; }
export async function markNewsClicked(newsId) { const { data } = await api.post('/news/mark-clicked/', { news_id: newsId }); return data; }
export async function updateNewsPreferences(preferences) { const { data } = await api.post('/news/preferences/', preferences); return data; }
export async function syncPortfolioNews() { const { data } = await api.post('/news/sync-portfolio/'); return data; }

// (Removed unsupported /revenue/* helper functions)

// ====================
// SUBSCRIPTIONS
// ====================
export async function wordpressSubscribe(email, category = null) { const { data } = await api.post('/wordpress/subscribe/', { email, category }); return data; }

// ====================
// WORDPRESS INTEGRATION
// ====================
export async function getWordPressStocks(params = {}) { const { data } = await api.get('/wordpress/stocks/', { params }); return data; }
export async function getWordPressNews(params = {}) { const { data } = await api.get('/wordpress/news/', { params }); return data; }
export async function getWordPressAlerts(params = {}) { const { data } = await api.get('/wordpress/alerts/', { params }); return data; }

// ====================
// PORTFOLIO ANALYTICS & ADVANCED FEATURES
// ====================

// Portfolio Analytics
export async function getPortfolioAnalytics() { 
  ensureApiQuotaAndIncrement('getPortfolioAnalytics');
  const { data } = await api.get('/portfolio/analytics/'); 
  return data; 
}

export async function getPortfolioSectorAllocation() { 
  ensureApiQuotaAndIncrement('getPortfolioAnalytics');
  const { data } = await api.get('/portfolio/sector-allocation/'); 
  return data; 
}

export async function getPortfolioDividendTracking() { 
  ensureApiQuotaAndIncrement('getPortfolioAnalytics');
  const { data } = await api.get('/portfolio/dividend-tracking/'); 
  return data; 
}

// Advanced Screeners
export async function getScreeners() { 
  ensureApiQuotaAndIncrement('getScreeners');
  const { data } = await api.get('/screeners/'); 
  return data; 
}

export async function createScreener(screenerData) { 
  ensureApiQuotaAndIncrement('createScreener');
  const { data } = await api.post('/screeners/', screenerData); 
  return data; 
}

export async function getScreener(id) { 
  ensureApiQuotaAndIncrement('getScreener');
  const { data } = await api.get(`/screeners/${id}/`); 
  return data; 
}

export async function updateScreener(id, screenerData) { 
  ensureApiQuotaAndIncrement('updateScreener');
  const { data } = await api.put(`/screeners/${id}/`, screenerData); 
  return data; 
}

export async function deleteScreener(id) { 
  ensureApiQuotaAndIncrement('deleteScreener');
  const { data } = await api.delete(`/screeners/${id}/`); 
  return data; 
}

export async function getScreenerTemplates() { 
  ensureApiQuotaAndIncrement('getScreenerTemplates');
  const { data } = await api.get('/screeners/templates/'); 
  return data; 
}

export async function runScreener(id) { 
  ensureApiQuotaAndIncrement('runScreener');
  const { data } = await api.post(`/screeners/${id}/run/`); 
  return data; 
}

// Data Export
export async function exportStocksCSV(params = {}) { 
  const response = await api.get('/export/stocks/csv', { params, responseType: 'blob' }); 
  return response.data; 
}

export async function exportPortfolioCSV(params = {}) { 
  const response = await api.get('/export/portfolio/csv', { params, responseType: 'blob' }); 
  return response.data; 
}

export async function exportScreenerResultsCSV(screenerId, params = {}) { 
  const response = await api.get('/export/screener-results/csv', { params: { ...params, screener_id: screenerId }, responseType: 'blob' }); 
  return response.data; 
}

export async function exportWatchlistCSV(params = {}) { 
  const response = await api.get('/export/watchlist/csv', { params, responseType: 'blob' }); 
  return response.data; 
}

export async function generateCustomReport(reportData) { 
  const { data } = await api.post('/reports/custom/', reportData); 
  return data; 
}

export async function downloadReport(id) { 
  const response = await api.get(`/reports/${id}/download`, { responseType: 'blob' }); 
  return response.data; 
}

// Enhanced Market Data
export async function getSectorPerformance() { 
  ensureApiQuotaAndIncrement('loadMarket');
  const { data } = await api.get('/market/sectors/performance'); 
  return data; 
}

export async function getMarketStatus() { 
  ensureApiQuotaAndIncrement('getMarketStatus');
  const { data } = await api.get('/market/market-status'); 
  return data; 
}

export async function getStockNews(symbol) { 
  ensureApiQuotaAndIncrement('getStockNews');
  const { data } = await api.get(`/news/ticker/${encodeURIComponent(symbol)}/`); 
  return data; 
}

// Developer Tools (Gold Plan)
export async function getApiKeys() { 
  const { data } = await api.get('/developer/api-keys/'); 
  return data; 
}

export async function createApiKey(keyData) { 
  const { data } = await api.post('/developer/api-keys/', keyData); 
  return data; 
}

export async function deleteApiKey(id) { 
  const { data } = await api.delete(`/developer/api-keys/${id}/`); 
  return data; 
}

export async function getUsageStats() { 
  const { data } = await api.get('/developer/usage-stats/'); 
  return data; 
}

export async function getApiDocumentation() { 
  const { data } = await api.get('/developer/documentation/'); 
  return data; 
}

// Enterprise Solutions
export async function submitEnterpriseContact(contactData) { 
  const { data } = await api.post('/enterprise/contact/', contactData); 
  return data; 
}

export async function getEnterpriseSolutions() { 
  const { data } = await api.get('/enterprise/solutions/'); 
  return data; 
}

export async function submitQuoteRequest(quoteData) { 
  const { data } = await api.post('/enterprise/quote-request/', quoteData); 
  return data; 
}

// User Activity & Analytics
export async function getUserActivityFeed() { 
  ensureApiQuotaAndIncrement('getUserActivity');
  const { data } = await api.get('/user/activity-feed/'); 
  return data; 
}

export async function getUserInsights() { 
  ensureApiQuotaAndIncrement('getUserInsights');
  const { data } = await api.get('/analytics/user-insights/'); 
  return data; 
}

// ====================
// USAGE TRACKING & LIMITS EXPORT
// ====================
export { getCurrentApiUsage, getPlanLimits, getStoredUserPlan, API_CALL_COSTS };