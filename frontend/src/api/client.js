import axios from "axios";

const BASE_URL = (import.meta?.env?.REACT_APP_BACKEND_URL || process.env.REACT_APP_BACKEND_URL || "").trim();
if (!BASE_URL) {
  console.warn("REACT_APP_BACKEND_URL is not set. API calls will fail.");
}

export const API_ROOT = `${BASE_URL}/api`;

export const api = axios.create({
  baseURL: API_ROOT,
  withCredentials: false,
});

// Attach token if present
api.interceptors.request.use((config) => {
  try {
    const token = window.localStorage.getItem("rts_token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
      // Also add as query param for compatibility with session_authenticated endpoints
      config.params = config.params || {};
      config.params.authorization = `Bearer ${token}`;
    }
  } catch (e) {
    // ignore
  }
  return config;
});

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Clear token and redirect to login
      localStorage.removeItem("rts_token");
      window.location.href = "/auth/sign-in";
    }
    return Promise.reject(error);
  }
);

// ====================
// HEALTH & STATUS
// ====================
export async function pingHealth() {
  const { data } = await api.get("/health/");
  return data;
}

export async function getEndpointStatus() {
  const { data } = await api.get("/endpoint-status/");
  return data;
}

// ====================
// STOCKS & MARKET DATA
// ====================
export async function listStocks(params = {}) {
  const { data } = await api.get("/stocks/", { params });
  return data;
}

export async function getStock(ticker) {
  const { data } = await api.get(`/stock/${encodeURIComponent(ticker)}/`);
  return data;
}

export async function searchStocks(q) {
  const { data } = await api.get("/search/", { params: { q } });
  return data;
}

export async function getTrending() {
  const { data } = await api.get("/trending/");
  return data;
}

export async function getMarketStats() {
  const { data } = await api.get("/market-stats/");
  return data;
}

export async function getRealTimeQuote(ticker) {
  const { data } = await api.get(`/realtime/${encodeURIComponent(ticker)}/`);
  return data;
}

export async function filterStocks(params = {}) {
  const { data } = await api.get("/filter/", { params });
  return data;
}

export async function getStatistics() {
  const { data } = await api.get("/statistics/");
  return data;
}

export async function getMarketData() {
  const { data } = await api.get("/market-data/");
  return data;
}

// ====================
// AUTHENTICATION
// ====================
export async function login(username, password) {
  try {
    const { data } = await api.post("/auth/login/", { username, password });
    if (data.success && data.token) {
      localStorage.setItem("rts_token", data.token);
    }
    return data;
  } catch (error) {
    return {
      success: false,
      message: error.response?.data?.detail || "Login failed"
    };
  }
}

export async function logout() {
  try {
    await api.post("/auth/logout/");
  } catch (error) {
    // Continue with logout even if API call fails
  } finally {
    localStorage.removeItem("rts_token");
  }
}

// Note: Register endpoint not in JSON spec, using mock
export async function registerUser(userData) {
  try {
    // Mock registration since not in API spec
    return {
      success: true,
      message: "Registration successful"
    };
  } catch (error) {
    return {
      success: false,
      message: "Registration failed"
    };
  }
}

export async function getProfile() {
  const { data } = await api.get("/user/profile/");
  return data;
}

export async function updateProfile(profileData) {
  const { data } = await api.post("/user/profile/", profileData);
  return data;
}

export async function changePassword(passwordData) {
  const { data } = await api.post("/user/change-password/", passwordData);
  return data;
}

// ====================
// PORTFOLIO
// ====================
export async function getPortfolio() {
  const { data } = await api.get("/portfolio/");
  return data;
}

export async function addPortfolio(payload) {
  const { data } = await api.post("/portfolio/add/", payload);
  return data;
}

export async function deletePortfolio(id) {
  const { data } = await api.delete(`/portfolio/${id}/`);
  return data;
}

// ====================
// WATCHLISTS
// ====================
export async function getWatchlist() {
  const { data } = await api.get("/watchlist/");
  return data;
}

export async function addWatchlist(symbol, opts = {}) {
  const { data } = await api.post("/watchlist/add/", { symbol, ...opts });
  return data;
}

export async function deleteWatchlist(id) {
  const { data } = await api.delete(`/watchlist/${id}/`);
  return data;
}

// ====================
// ALERTS
// ====================
export async function alertsMeta() {
  const { data } = await api.get("/alerts/create/");
  return data;
}

export async function createAlert(payload) {
  const { data } = await api.post("/alerts/create/", payload);
  return data;
}

// ====================
// BILLING
// ====================
export async function getBillingHistory(params = {}) {
  const { data } = await api.get("/billing/history/", { params });
  return data;
}

export async function getCurrentPlan() {
  const { data } = await api.get("/billing/current-plan/");
  return data;
}

export async function changePlan(planData) {
  const { data } = await api.post("/billing/change-plan/", planData);
  return data;
}

export async function getBillingStats() {
  const { data } = await api.get("/billing/stats/");
  return data;
}

export async function downloadInvoice(invoiceId) {
  const response = await api.get(`/billing/download/${invoiceId}/`, {
    responseType: 'blob'
  });
  return response.data;
}

export async function updatePaymentMethod(paymentData) {
  const { data } = await api.post("/user/update-payment/", paymentData);
  return data;
}

// ====================
// NOTIFICATIONS
// ====================
export async function getNotificationSettings() {
  const { data } = await api.get("/user/notification-settings/");
  return data;
}

export async function updateNotificationSettings(settings) {
  const { data } = await api.post("/user/notification-settings/", settings);
  return data;
}

export async function getNotificationHistory(params = {}) {
  const { data } = await api.get("/notifications/history/", { params });
  return data;
}

export async function markNotificationsRead(payload) {
  const { data } = await api.post("/notifications/mark-read/", payload);
  return data;
}

// ====================
// NEWS
// ====================
export async function getNewsFeed(params = {}) {
  const { data } = await api.get("/news/feed/", { params });
  return data;
}

export async function markNewsRead(newsId) {
  const { data } = await api.post("/news/mark-read/", { news_id: newsId });
  return data;
}

export async function markNewsClicked(newsId) {
  const { data } = await api.post("/news/mark-clicked/", { news_id: newsId });
  return data;
}

export async function updateNewsPreferences(preferences) {
  const { data } = await api.post("/news/preferences/", preferences);
  return data;
}

export async function syncPortfolioNews() {
  const { data } = await api.post("/news/sync-portfolio/");
  return data;
}

// ====================
// REVENUE & DISCOUNTS
// ====================
export async function revenueInitialize() {
  const { data } = await api.post("/revenue/initialize-codes/");
  return data;
}

export async function revenueValidate(code) {
  const { data } = await api.post("/revenue/validate-discount/", { code });
  return data;
}

export async function revenueApply(code, amount) {
  const { data } = await api.post("/revenue/apply-discount/", { code, amount });
  return data;
}

export async function recordPayment(paymentData) {
  const { data } = await api.post("/revenue/record-payment/", paymentData);
  return data;
}

export async function getRevenueAnalytics(monthYear = null) {
  const url = monthYear ? `/revenue/revenue-analytics/${monthYear}/` : "/revenue/revenue-analytics/";
  const { data } = await api.get(url);
  return data;
}

// ====================
// SUBSCRIPTIONS
// ====================
export async function subscribe(email, category = null) {
  const { data } = await api.post("/subscription/", { email, category });
  return data;
}

export async function wordpressSubscribe(email, category = null) {
  const { data } = await api.post("/wordpress/subscribe/", { email, category });
  return data;
}

// ====================
// WORDPRESS INTEGRATION
// ====================
export async function getWordPressStocks(params = {}) {
  const { data } = await api.get("/wordpress/stocks/", { params });
  return data;
}

export async function getWordPressNews(params = {}) {
  const { data } = await api.get("/wordpress/news/", { params });
  return data;
}

export async function getWordPressAlerts(params = {}) {
  const { data } = await api.get("/wordpress/alerts/", { params });
  return data;
}

export async function updateStocks(symbols) {
  const { data } = await api.post("/stocks/update/", { symbols });
  return data;
}

export async function updateNews() {
  const { data } = await api.post("/news/update/");
  return data;
}