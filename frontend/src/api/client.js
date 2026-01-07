import axios from "axios";
import { getCache, setCache } from "../lib/cache";
import { getReferralFromCookie, normalizeReferralCode } from "../lib/referral";
import logger from '../lib/logger';

// Use REACT_APP_BACKEND_URL exclusively from environment, with production fallback
const BASE_URL = process.env.REACT_APP_BACKEND_URL || "https://api.retailtradescanner.com";

if (!BASE_URL) {
  logger.error("REACT_APP_BACKEND_URL is not set. API calls will fail.");
}

export const API_ROOT = `${BASE_URL}/api`;

// Remove secondary axios instance; use one layer with withCredentials for CSRF
// (deduped per spec)

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
  basic: {
    monthlyApi: 1500,
    alerts: 50,
    watchlists: 2,
    portfolios: 0,
    screeners: 10
  },
  pro: {
    monthlyApi: Infinity,
    alerts: Infinity,
    watchlists: Infinity,
    portfolios: Infinity,
    screeners: Infinity
  },
  // Legacy plan mappings for backward compatibility
  bronze: {
    monthlyApi: 1500,
    alerts: 50,
    watchlists: 2,
    portfolios: 0,
    screeners: 10
  },
  silver: {
    monthlyApi: 5000,
    alerts: 100,
    watchlists: 10,
    portfolios: 1,
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
    // Bootstrap CSRF once via dedicated endpoint
    if (ensureCsrfCookie.__bootstrapped) return;
    if (getCsrfToken()) { ensureCsrfCookie.__bootstrapped = true; return; }
    await api.get('/auth/csrf/').catch(() => {});
    ensureCsrfCookie.__bootstrapped = true;
  } catch {}
}
ensureCsrfCookie.__bootstrapped = false;
try { setTimeout(() => { ensureCsrfCookie().catch(()=>{}); }, 0); } catch {}

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
api.interceptors.request.use(async (config) => {
  try {
    config.headers['X-Requested-With'] = 'XMLHttpRequest';
    const method = (config.method || 'get').toLowerCase();
    const csrf = __csrfTokenCache || getCsrfToken();
    if (csrf && ['post','put','patch','delete'].includes(method)) {
      config.headers['X-CSRFToken'] = csrf;
    }

    // Prefer encrypted token from secureStorage if available, fallback to localStorage
    let bearerToken = null;
    try {
      const sec = await import('../lib/security');
      bearerToken = await sec.secureStorage.getDecrypted(sec.SECURITY_CONFIG.TOKEN_STORAGE_KEY);
    } catch {}
    if (!bearerToken) {
      try {
        const localToken = (window.localStorage.getItem('rts_token') || '').trim();
        if (localToken && localToken !== 'undefined' && localToken !== 'null') {
          bearerToken = localToken;
        }
      } catch {}
    }
    if (bearerToken) {
      config.headers.Authorization = `Bearer ${bearerToken}`;
    }

    // Attach referral if available (server-side attribution)
    try {
      const ref = getReferralFromCookie();
      const norm = normalizeReferralCode(ref);
      if (norm) {
        config.headers['X-Referral-Code'] = norm;
      }
    } catch {}
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
    // Simple retry/backoff for transient 5xx errors (max 2 retries)
    try {
      const cfg = error.config || {};
      const status = error?.response?.status;
      const isIdempotent = (cfg.method || 'get').toLowerCase() === 'get';
      if (status && status >= 500 && status < 600 && isIdempotent) {
        cfg.__retryCount = (cfg.__retryCount || 0) + 1;
        if (cfg.__retryCount <= 2) {
          const delayMs = 300 * Math.pow(3, cfg.__retryCount - 1);
          return new Promise((resolve) => setTimeout(resolve, delayMs)).then(() => api.request(cfg));
        }
      }
    } catch {}
    // Standardize 401 handling at the callsite; do not auto-logout here
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
    return { success: true, data: normalizeMarketStats(res.data), cached: !!res.cached };
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
// PARTNER / REFERRAL ANALYTICS
// ====================
export async function getPartnerReferralSummary(params = {}) {
  try {
    const query = {};
    if (params.code) query.code = params.code;
    if (params.from) query.from = params.from;
    if (params.to) query.to = params.to;
    const { data } = await api.get('/partner/analytics/summary', { params: query });
    if (data?.success) {
      return { success: true, data };
    }
    return { success: false, error: data?.error || 'Failed to load referral analytics', data };
  } catch (error) {
    const message = error?.response?.data?.error || error.message || 'Failed to load referral analytics';
    return { success: false, error: message, data: error?.response?.data };
  }
}

export async function getPartnerReferralTimeseries(params = {}) {
  try {
    const query = {};
    if (params.code) query.code = params.code;
    if (params.from) query.from = params.from;
    if (params.to) query.to = params.to;
    if (params.interval) query.interval = params.interval;
    const { data } = await api.get('/partner/analytics/timeseries', { params: query });
    if (data?.success) {
      return { success: true, data };
    }
    return { success: false, error: data?.error || 'Failed to load referral trend data', data };
  } catch (error) {
    const message = error?.response?.data?.error || error.message || 'Failed to load referral trend data';
    return { success: false, error: message, data: error?.response?.data };
  }
}

// ====================
// HEALTH & STATUS
// ====================
export async function pingHealth() {
  // Use documented health endpoints only - prefer /api/health/ (no redirect)
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
    logger.error('Failed to fetch stocks:', error);
    throw error;
  }
}
export async function getStock(ticker) { 
  ensureApiQuotaAndIncrement('getStock');
  const sym = String(ticker || '').toUpperCase();
  const { data } = await api.get(`/stocks/${encodeURIComponent(sym)}/`); 
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
  const sym = String(ticker || '').toUpperCase();
  const { data } = await api.get(`/realtime/${encodeURIComponent(sym)}/`); 
  return data; 
}

// ====================
// INSIDERS (SEC FORM 4)
// ====================
export async function getInsiderTrades(ticker) {
  try {
    ensureApiQuotaAndIncrement('getStock');
    const sym = String(ticker || '').toUpperCase();
    const { data } = await api.get(`/stocks/${encodeURIComponent(sym)}/insiders/`);
    return data;
  } catch (error) {
    return { success: false, error: error?.response?.data?.error || 'Failed to load insiders' };
  }
}

// ====================
// SHARING (PUBLIC VIEW + COPY)
// ====================
export async function getSharedWatchlist(slug) {
  const { data } = await api.get(`/share/watchlists/${encodeURIComponent(slug)}/`);
  return data;
}
export async function getSharedPortfolio(slug) {
  const { data } = await api.get(`/share/portfolios/${encodeURIComponent(slug)}/`);
  return data;
}
export async function copySharedWatchlist(slug) {
  const { data } = await api.post(`/share/watchlists/${encodeURIComponent(slug)}/copy`);
  return data;
}
export async function copySharedPortfolio(slug) {
  const { data } = await api.post(`/share/portfolios/${encodeURIComponent(slug)}/copy`);
  return data;
}
export async function createShareLinkForWatchlist(id) {
  const { data } = await api.post(`/share/watchlists/${encodeURIComponent(id)}/create`);
  return data;
}
export async function createShareLinkForPortfolio(id) {
  const { data } = await api.post(`/share/portfolios/${encodeURIComponent(id)}/create`);
  return data;
}

export async function revokeShareLinkForPortfolio(id) {
  const { data } = await api.post(`/share/portfolios/${encodeURIComponent(id)}/revoke`);
  return data;
}

export async function revokeShareLinkForWatchlist(id) {
  const { data } = await api.post(`/share/watchlists/${encodeURIComponent(id)}/revoke`);
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
export async function updateProfile(profileData) {
  try {
    const payload = {
      first_name: profileData.first_name || profileData.firstName,
      last_name: profileData.last_name || profileData.lastName,
      email: profileData.email,
    };
    const { data } = await api.post('/user/profile/', payload); // use canonical endpoint
    return data;
  } catch (error) {
    const resp = error?.response?.data;
    if (resp && typeof resp === 'object') {
      // Normalize server errors to {field, message}
      const normalized = Object.keys(resp).map((k) => ({ field: k, message: String(resp[k]) }));
      return { success: false, errors: normalized, message: resp.message || 'Failed to update profile' };
    }
    return { success: false, message: 'Failed to update profile' };
  }
}
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
export async function getPortfolio(params = {}) { 
  try {
    ensureApiQuotaAndIncrement('getPortfolio');
    const { data } = await api.get('/portfolio/', { params });
    return data;
  } catch (error) {
    logger.error('Failed to fetch portfolio:', error);
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

// Multi-portfolio helpers
export async function listPortfolios() {
  ensureApiQuotaAndIncrement('getPortfolio');
  const { data } = await api.get('/portfolio/list/');
  return data;
}

export async function createPortfolio(payload) {
  ensureApiQuotaAndIncrement('addPortfolio');
  const { data } = await api.post('/portfolio/create/', payload);
  return data;
}

export async function deletePortfolioById(portfolioId) {
  ensureApiQuotaAndIncrement('deletePortfolio');
  const { data } = await api.delete(`/portfolio/${encodeURIComponent(portfolioId)}/delete/`);
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
      // Detect server capabilities once
      if (typeof window !== 'undefined') {
        window.__API_CAPS = window.__API_CAPS || {};
        window.__API_CAPS.watchlist = window.__API_CAPS.watchlist || {};
        window.__API_CAPS.watchlist.list = true;
      }
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
    try { const { data } = await attempt(); return data; } catch (e) { 
      const s = e?.response?.status;
      if (s === 409) return { success: false, message: 'This watchlist already exists.' };
      lastErr = e; 
    }
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
      const s = e?.response?.status;
      if (s === 409) return { success: false, message: 'This symbol is already in your watchlist.' };
      if (s && ![404, 405, 400].includes(s)) { lastErr = e; break; }
      lastErr = e;
    }
  }
  throw lastErr;
}

// Bulk operations (no-op fallbacks if backend lacks support)
export async function addWatchlistBulk(symbols = [], opts = {}) {
  const unique = Array.from(new Set(symbols.map(s => String(s || '').toUpperCase()).filter(Boolean)));
  if (unique.length === 0) return { success: true, added: 0, duplicates: 0, errors: 0 };
  // Try bulk endpoint if available, else sequential
  try {
    const { data } = await api.post('/watchlist/bulk-add/', { symbols: unique, watchlist_name: opts.watchlist_name || 'My Watchlist' });
    return data;
  } catch (_) {}
  let added = 0, duplicates = 0, errors = 0;
  for (const sym of unique) {
    const res = await addWatchlist(sym, { watchlist_name: opts.watchlist_name, notes: opts.notes });
    if (res?.success === false && /already/i.test(res?.message || '')) duplicates++; else if (res?.success === false) errors++; else added++;
  }
  return { success: true, added, duplicates, errors };
}

export async function removeWatchlistBulk(items = []) {
  const normalized = items.map(x => (typeof x === 'string' ? { id: x } : x)).filter(Boolean);
  if (normalized.length === 0) return { success: true, removed: 0, notFound: 0, errors: 0 };
  try {
    const { data } = await api.post('/watchlist/bulk-remove/', { items: normalized });
    return data;
  } catch (_) {}
  let removed = 0, notFound = 0, errors = 0;
  for (const it of normalized) {
    try {
      await deleteWatchlist(it.id || it);
      removed++;
    } catch (e) {
      if ((e?.message || '').toLowerCase().includes('not in your watchlist') || (e?.message || '').toLowerCase().includes('already removed')) notFound++; else errors++;
    }
  }
  return { success: true, removed, notFound, errors };
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
    // Friendly duplicate/conflict handling
    const s = e?.response?.status;
    if (s === 409) {
      return { success: false, message: 'This symbol is already in your watchlist.' };
    }
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
    try { return await removeWatchlistStock(idOrPayload); } catch (e) {
      const s = e?.response?.status;
      if (s === 404) throw new Error('That item is not in your watchlist.');
      if (s === 405) throw new Error('Delete not supported by this server.');
      if (s === 409) throw new Error('Conflict deleting this item. Try again.');
      throw e;
    }
  }
  const id = String(idOrPayload || '').trim();
  if (!id) {
    throw new Error('deleteWatchlist requires item id or {watchlist_id, stock_ticker}');
  }
  try {
    const { data } = await api.delete(`/watchlist/${encodeURIComponent(id)}/`);
    return data;
  } catch (e) {
    const s = e?.response?.status;
    if (s === 404) throw new Error('Item already removed.');
    if (s === 405) throw new Error('Delete not supported by this server.');
    if (s === 409) throw new Error('Could not delete this item right now.');
    throw e;
  }
}

// ====================
// ALERTS
// ====================
export async function alertsMeta() { 
  ensureApiQuotaAndIncrement('default');
  const { data } = await api.get('/alerts/meta/'); 
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

// ====================
// ADMIN
// ====================
export async function getAdminMetrics() {
  try {
    const { data } = await api.get('/admin/metrics/');
    return { success: true, data };
  } catch (error) {
    return { success: false, error: error?.response?.data?.message || 'Failed to load admin metrics' };
  }
}

export async function downloadInvoice(invoiceId) { 
  const response = await api.get(`/billing/download/${invoiceId}/`, { responseType: 'blob' }); 
  // Attempt to parse JSON error payloads hidden in blob responses
  try {
    const ct = response.headers['content-type'] || '';
    if (!ct.includes('application/pdf') && response.data) {
      const text = await response.data.text?.() || '';
      try { const json = JSON.parse(text); throw Object.assign(new Error(json?.message || 'Invoice not available'), { json }); } catch {}
    }
  } catch {}
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
    logger.error('PayPal order creation failed:', error);
    throw error;
  }
}

export async function capturePayPalOrder(orderId, paymentData) {
  try {
    const { data } = await api.post('/billing/capture-paypal-order/', {
      order_id: orderId,
      ...(paymentData || {})
    });
    return data;
  } catch (error) {
    logger.error('PayPal order capture failed:', error);
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
export async function getAllNews(params = {}, options = {}) {
  ensureApiQuotaAndIncrement('getNews');
  const { data } = await api.get('/news/all/', { params, signal: options.signal });
  return data;
}
export async function markNewsRead(newsId) { const { data } = await api.post('/news/mark-read/', { news_id: newsId }); return data; }
export async function markNewsClicked(newsId) { const { data } = await api.post('/news/mark-clicked/', { news_id: newsId }); return data; }
export async function updateNewsPreferences(preferences) { const { data } = await api.post('/news/preferences/', preferences); return data; }
export async function syncPortfolioNews() { const { data } = await api.post('/news/sync-portfolio/'); return data; }

// (Removed unsupported /revenue/* helper functions)
// ====================
// SMS (Local provider only; no external API)
// ====================
export async function requestSmsCode(phoneNumber) {
  const { data } = await api.post('/sms/request-code/', { phone_number: phoneNumber });
  return data;
}

export async function verifySmsCode(code) {
  const { data } = await api.post('/sms/verify/', { code });
  return data;
}

export async function sendTestSms(message = 'Test message') {
  const { data } = await api.post('/sms/send-test/', { message });
  return data;
}


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
  const { data } = await api.post('/screeners/create/', screenerData); 
  return data; 
}

export async function getScreener(id) { 
  ensureApiQuotaAndIncrement('getScreener');
  const { data } = await api.get(`/screeners/${id}/`); 
  return data; 
}

export async function updateScreener(id, screenerData) { 
  ensureApiQuotaAndIncrement('updateScreener');
  const { data } = await api.post(`/screeners/${id}/update/`, screenerData); 
  return data; 
}

export async function deleteScreener(id) { 
  ensureApiQuotaAndIncrement('deleteScreener');
  const { data } = await api.delete(`/screeners/${id}/delete/`); 
  return data; 
}

export async function getScreenerTemplates() { 
  ensureApiQuotaAndIncrement('getScreenerTemplates');
  const { data } = await api.get('/screeners/templates/'); 
  return data; 
}

export async function runScreener(id) { 
  ensureApiQuotaAndIncrement('runScreener');
  const { data } = await api.post(`/screeners/${id}/results/`); 
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
  const response = await api.get(`/screeners/${encodeURIComponent(screenerId)}/export.csv`, { params, responseType: 'blob' }); 
  // Add UTF-8 BOM for Excel compatibility
  const blob = response.data instanceof Blob ? response.data : new Blob([response.data], { type: 'text/csv' });
  const withBom = new Blob([new Uint8Array([0xEF, 0xBB, 0xBF]), blob], { type: 'text/csv;charset=utf-8;' });
  return withBom; 
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
  try {
    const ct = response.headers['content-type'] || '';
    if (!ct.includes('application/pdf') && !ct.includes('text/csv') && response.data) {
      const text = await response.data.text?.() || '';
      try { const json = JSON.parse(text); throw Object.assign(new Error(json?.message || 'Download failed'), { json }); } catch {}
    }
  } catch {}
  return response.data; 
}

// Enhanced Market Data
export async function getSectorPerformance() { 
  ensureApiQuotaAndIncrement('loadMarket');
  const { data } = await api.get('/market-stats/');
  return Array.isArray(data?.sectors) ? data.sectors : (Array.isArray(data?.sector_performance) ? data.sector_performance : []);
}

export async function getMarketStatus() { 
  ensureApiQuotaAndIncrement('getMarketStatus');
  const { data } = await api.get('/market-stats/');
  const now = new Date();
  const toET = (d) => new Date(d.toLocaleString('en-US', { timeZone: 'America/New_York' }));
  const etNow = toET(now);
  const openET = new Date(etNow); openET.setHours(9, 30, 0, 0);
  const closeET = new Date(etNow); closeET.setHours(16, 0, 0, 0);
  const day = etNow.getDay();
  const isWeekday = day >= 1 && day <= 5;
  const status = isWeekday && etNow >= openET && etNow <= closeET ? 'open' : 'closed';
  return { market: { status, open: openET.toISOString(), close: closeET.toISOString(), last_updated: data?.last_updated || null } };
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

// Public usage summary suitable for Account/Plan usage UI
export async function getUsageSummary() {
  try {
    const { data } = await api.get('/usage/');
    const safe = (x) => (x && typeof x === 'object') ? x : {};
    const monthly = safe(data?.data?.monthly);
    const daily = safe(data?.data?.daily);
    return {
      success: !!data?.success,
      data: {
        daily: {
          api_calls: Number(daily.api_calls || 0),
          requests: Number(daily.requests || 0),
          date: daily.date || null,
        },
        monthly: {
          api_calls: Number(monthly.api_calls || 0),
          requests: Number(monthly.requests || 0),
          limit: Number.isFinite(Number(monthly.limit)) ? Number(monthly.limit) : 0,
          remaining: Number.isFinite(Number(monthly.remaining)) ? Number(monthly.remaining) : 0,
        },
        categories: safe(data?.data?.categories),
      }
    };
  } catch (error) {
    return { success: false, error: error?.response?.data?.message || 'Failed to load usage summary' };
  }
}
// ====================
// AI BACKTESTING (Phase 4)
// ====================
export async function createBacktest(backtestData) {
  const { data } = await api.post('/backtesting/create/', backtestData);
  return data;
}

export async function runBacktest(backtestId) {
  const { data } = await api.post(`/backtesting/${backtestId}/run/`);
  return data;
}

export async function getBacktest(backtestId) {
  const { data } = await api.get(`/backtesting/${backtestId}/`);
  return data;
}

export async function listBacktests(category = null) {
  const params = category ? { category } : {};
  const { data } = await api.get('/backtesting/list/', { params });
  return data;
}

export async function getBaselineStrategies() {
  const { data } = await api.get('/backtesting/baseline-strategies/');
  return data;
}

// ====================
// VALUE HUNTER (Phase 5)
// ====================
export async function getValueHunterCurrentWeek() {
  const { data } = await api.get('/value-hunter/current/');
  return data;
}

export async function getValueHunterWeek(year, weekNumber) {
  const { data } = await api.get(`/value-hunter/${year}/${weekNumber}/`);
  return data;
}

export async function listValueHunterWeeks() {
  const { data } = await api.get('/value-hunter/list/');
  return data;
}

export async function getValueHunterTopStocks() {
  const { data } = await api.get('/value-hunter/top-stocks/');
  return data;
}


// ====================
// CUSTOM INDICATORS (Phase 9)
// ====================
export async function listIndicators(params = {}) {
  const { data } = await api.get('/indicators/', { params });
  return data;
}

export async function createIndicator(indicatorData) {
  const { data } = await api.post('/indicators/create/', indicatorData);
  return data;
}

export async function getIndicator(indicatorId) {
  const { data } = await api.get(`/indicators/${indicatorId}/`);
  return data;
}

export async function updateIndicator(indicatorId, indicatorData) {
  const { data } = await api.put(`/indicators/${indicatorId}/`, indicatorData);
  return data;
}

export async function deleteIndicator(indicatorId) {
  const { data } = await api.delete(`/indicators/${indicatorId}/`);
  return data;
}

// ====================
// TRADING JOURNAL (Phase 9)
// ====================
export async function listJournalEntries(params = {}) {
  const { data } = await api.get('/journal/', { params });
  return data;
}

export async function createJournalEntry(entryData) {
  const { data } = await api.post('/journal/', entryData);
  return data;
}

export async function getJournalEntry(entryId) {
  const { data } = await api.get(`/journal/${entryId}/`);
  return data;
}

export async function updateJournalEntry(entryId, entryData) {
  const { data } = await api.put(`/journal/${entryId}/`, entryData);
  return data;
}

export async function deleteJournalEntry(entryId) {
  const { data } = await api.delete(`/journal/${entryId}/`);
  return data;
}

export async function getJournalStats(params = {}) {
  const { data } = await api.get('/journal/stats/', { params });
  return data;
}

// ====================
// EXPORT MANAGER (history + schedules)
// ====================
export async function listExportHistory() {
  const { data } = await api.get('/exports/history/');
  return data;
}

export async function listExportSchedules() {
  const { data } = await api.get('/exports/schedules/');
  return data;
}

export async function createExportSchedule(payload) {
  const { data } = await api.post('/exports/schedules/', payload);
  return data;
}

export async function updateExportSchedule(id, payload) {
  const { data } = await api.put(`/exports/schedules/${encodeURIComponent(id)}/`, payload);
  return data;
}

export async function deleteExportSchedule(id) {
  const { data } = await api.delete(`/exports/schedules/${encodeURIComponent(id)}/`);
  return data;
}

export async function runExportScheduleNow(id) {
  const { data } = await api.post(`/exports/schedules/${encodeURIComponent(id)}/run-now/`);
  return data;
}

// ====================
// TAX REPORTING (Phase 9)
// ====================
export async function getTaxSummary(year) {
  const { data } = await api.get(`/tax/summary/${year}/`);
  return data;
}

export async function getTaxTransactions(year, params = {}) {
  const { data } = await api.get(`/tax/transactions/${year}/`, { params });
  return data;
}

export async function exportTaxReport(year, format = 'csv') {
  const response = await api.get(`/tax/export/${year}/`, { 
    params: { format },
    responseType: 'blob' 
  });
  return response.data;
}

// ====================
// SOCIAL SHARING (Phase 8)
// ====================
export async function shareBacktest(backtestId) {
  const { data } = await api.post(`/share/backtests/${backtestId}/create`);
  return data;
}

export async function getSharedBacktest(slug) {
  const { data } = await api.get(`/share/backtests/${encodeURIComponent(slug)}/`);
  return data;
}

export async function revokeSharedBacktest(backtestId) {
  const { data } = await api.post(`/share/backtests/${backtestId}/revoke`);
  return data;
}

export async function forkSharedBacktest(slug) {
  const { data } = await api.post(`/share/backtests/${encodeURIComponent(slug)}/fork`);
  return data;
}

export async function forkBacktest(backtestId) {
  const { data } = await api.post(`/backtesting/${backtestId}/fork/`);
  return data;
}

export async function getPublicProfile(username) {
  const { data } = await api.get(`/user/public/${encodeURIComponent(username)}/`);
  return data;
}

export async function updatePublicProfile(profileData) {
  const { data } = await api.post('/user/public/update/', profileData);
  return data;
}
