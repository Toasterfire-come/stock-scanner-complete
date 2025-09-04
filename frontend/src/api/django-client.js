/**
 * Django Backend API Client
 * Production-ready client for api.retailtradescanner.com
 */

import axios from 'axios';

// Production API configuration
const DJANGO_API_URL = 'https://api.retailtradescanner.com';
const API_PASSWORD = '((#cx+mb@f-(8x*p@9mfnanqe%ha1@6-b%w)q##v@)lanop';

// Create axios instances for different API prefixes
const apiClient = axios.create({
  baseURL: `${DJANGO_API_URL}/api`,
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
    'X-API-Key': API_PASSWORD
  }
});

const revenueClient = axios.create({
  baseURL: `${DJANGO_API_URL}/revenue`,
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
    'X-API-Key': API_PASSWORD
  }
});

// Request interceptor to add auth token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('django_auth_token');
    const sessionId = localStorage.getItem('django_session_id');
    
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    if (sessionId) {
      config.headers['X-Session-ID'] = sessionId;
    }
    
    // Add CSRF token if available
    const csrfToken = getCookie('csrftoken');
    if (csrfToken) {
      config.headers['X-CSRFToken'] = csrfToken;
    }
    
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // Clear auth data and redirect to login
      localStorage.removeItem('django_auth_token');
      localStorage.removeItem('django_session_id');
      localStorage.removeItem('django_user');
      
      if (!window.location.pathname.startsWith('/auth')) {
        window.location.href = '/auth/sign-in';
      }
    }
    
    return Promise.reject(error);
  }
);

// Apply same interceptors to revenue client
revenueClient.interceptors.request.use(apiClient.interceptors.request.handlers[0]);
revenueClient.interceptors.response.use(
  (response) => response,
  apiClient.interceptors.response.handlers[1]
);

// Helper function to get CSRF cookie
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

// ====================
// AUTHENTICATION
// ====================

export async function login(username, password) {
  try {
    const { data } = await apiClient.post('/auth/login/', {
      username,
      password
    });
    
    if (data.success) {
      // Store user data
      localStorage.setItem('django_user', JSON.stringify(data.data));
      
      // Store session if provided
      if (data.session_id) {
        localStorage.setItem('django_session_id', data.session_id);
      }
      
      // Store token if provided
      if (data.token) {
        localStorage.setItem('django_auth_token', data.token);
      }
    }
    
    return data;
  } catch (error) {
    return {
      success: false,
      message: error.response?.data?.message || 'Login failed'
    };
  }
}

export async function logout() {
  try {
    await apiClient.post('/auth/logout/');
  } catch (error) {
    console.error('Logout error:', error);
  } finally {
    localStorage.removeItem('django_auth_token');
    localStorage.removeItem('django_session_id');
    localStorage.removeItem('django_user');
  }
}

export async function register(userData) {
  try {
    const { data } = await apiClient.post('/auth/register/', userData);
    return data;
  } catch (error) {
    return {
      success: false,
      message: error.response?.data?.message || 'Registration failed'
    };
  }
}

// ====================
// USER PROFILE
// ====================

export async function getUserProfile() {
  try {
    const { data } = await apiClient.get('/user/profile/');
    return data;
  } catch (error) {
    throw error;
  }
}

export async function updateUserProfile(profileData) {
  try {
    const { data } = await apiClient.post('/user/profile/', profileData);
    return data;
  } catch (error) {
    throw error;
  }
}

export async function changePassword(currentPassword, newPassword, confirmPassword) {
  try {
    const { data } = await apiClient.post('/user/change-password/', {
      current_password: currentPassword,
      new_password: newPassword,
      confirm_password: confirmPassword
    });
    return data;
  } catch (error) {
    return {
      success: false,
      message: error.response?.data?.message || 'Password change failed'
    };
  }
}

// ====================
// BILLING & SUBSCRIPTIONS
// ====================

export async function getCurrentPlan() {
  try {
    const { data } = await apiClient.get('/billing/current-plan/');
    return data;
  } catch (error) {
    throw error;
  }
}

export async function changePlan(planType, billingCycle) {
  try {
    const { data } = await apiClient.post('/billing/change-plan/', {
      plan_type: planType,
      billing_cycle: billingCycle
    });
    return data;
  } catch (error) {
    return {
      success: false,
      message: error.response?.data?.message || 'Plan change failed'
    };
  }
}

export async function getBillingHistory(page = 1, limit = 10) {
  try {
    const { data } = await apiClient.get('/billing/history/', {
      params: { page, limit }
    });
    return data;
  } catch (error) {
    throw error;
  }
}

export async function getBillingStats() {
  try {
    const { data } = await apiClient.get('/billing/stats/');
    return data;
  } catch (error) {
    throw error;
  }
}

export async function updatePaymentMethod(paymentData) {
  try {
    const { data } = await apiClient.post('/user/update-payment/', paymentData);
    return data;
  } catch (error) {
    return {
      success: false,
      message: error.response?.data?.message || 'Payment update failed'
    };
  }
}

// ====================
// REVENUE & DISCOUNTS
// ====================

export async function validateDiscountCode(code) {
  try {
    const { data } = await revenueClient.post('/validate-discount/', { code });
    return data;
  } catch (error) {
    return {
      valid: false,
      message: error.response?.data?.message || 'Invalid discount code'
    };
  }
}

export async function applyDiscount(code, amount) {
  try {
    const { data } = await revenueClient.post('/apply-discount/', {
      code,
      amount
    });
    return data;
  } catch (error) {
    return {
      success: false,
      message: error.response?.data?.message || 'Failed to apply discount'
    };
  }
}

// ====================
// STOCKS & MARKET DATA
// ====================

export async function getStocks(params = {}) {
  try {
    const { data } = await apiClient.get('/stocks/', { params });
    return data;
  } catch (error) {
    throw error;
  }
}

export async function getStockDetails(ticker) {
  try {
    const { data } = await apiClient.get(`/stock/${ticker}/`);
    return data;
  } catch (error) {
    throw error;
  }
}

export async function searchStocks(query) {
  try {
    const { data } = await apiClient.get('/search/', {
      params: { q: query }
    });
    return data;
  } catch (error) {
    throw error;
  }
}

export async function getRealtimeData(ticker) {
  try {
    const { data } = await apiClient.get(`/realtime/${ticker}/`);
    return data;
  } catch (error) {
    throw error;
  }
}

export async function getTrendingStocks() {
  try {
    const { data } = await apiClient.get('/trending/');
    return data;
  } catch (error) {
    throw error;
  }
}

export async function getMarketStats() {
  try {
    const { data } = await apiClient.get('/market-stats/');
    return data;
  } catch (error) {
    throw error;
  }
}

export async function filterStocks(filters) {
  try {
    const { data } = await apiClient.get('/filter/', { params: filters });
    return data;
  } catch (error) {
    throw error;
  }
}

// ====================
// PORTFOLIO
// ====================

export async function getPortfolio() {
  try {
    const { data } = await apiClient.get('/portfolio/');
    return data;
  } catch (error) {
    throw error;
  }
}

export async function addToPortfolio(symbol, shares, avgCost, portfolioName = 'My Portfolio') {
  try {
    const { data } = await apiClient.post('/portfolio/add/', {
      symbol,
      shares,
      avg_cost: avgCost,
      portfolio_name: portfolioName
    });
    return data;
  } catch (error) {
    return {
      success: false,
      message: error.response?.data?.message || 'Failed to add to portfolio'
    };
  }
}

export async function removeFromPortfolio(holdingId) {
  try {
    const { data } = await apiClient.delete(`/portfolio/${holdingId}/`);
    return data;
  } catch (error) {
    return {
      success: false,
      message: error.response?.data?.message || 'Failed to remove from portfolio'
    };
  }
}

// ====================
// WATCHLIST
// ====================

export async function getWatchlist() {
  try {
    const { data } = await apiClient.get('/watchlist/');
    return data;
  } catch (error) {
    throw error;
  }
}

export async function addToWatchlist(symbol, watchlistName = 'My Watchlist', notes = '', alertPrice = null) {
  try {
    const { data } = await apiClient.post('/watchlist/add/', {
      symbol,
      watchlist_name: watchlistName,
      notes,
      alert_price: alertPrice
    });
    return data;
  } catch (error) {
    return {
      success: false,
      message: error.response?.data?.message || 'Failed to add to watchlist'
    };
  }
}

export async function removeFromWatchlist(itemId) {
  try {
    const { data } = await apiClient.delete(`/watchlist/${itemId}/`);
    return data;
  } catch (error) {
    return {
      success: false,
      message: error.response?.data?.message || 'Failed to remove from watchlist'
    };
  }
}

// ====================
// ALERTS
// ====================

export async function createAlert(ticker, targetPrice, condition, email) {
  try {
    const { data } = await apiClient.post('/alerts/create/', {
      ticker,
      target_price: targetPrice,
      condition,
      email
    });
    return data;
  } catch (error) {
    return {
      success: false,
      message: error.response?.data?.message || 'Failed to create alert'
    };
  }
}

// ====================
// NOTIFICATIONS
// ====================

export async function getNotificationSettings() {
  try {
    const { data } = await apiClient.get('/notifications/settings/');
    return data;
  } catch (error) {
    throw error;
  }
}

export async function updateNotificationSettings(settings) {
  try {
    const { data } = await apiClient.post('/notifications/settings/', settings);
    return data;
  } catch (error) {
    return {
      success: false,
      message: error.response?.data?.message || 'Failed to update settings'
    };
  }
}

export async function getNotificationHistory(params = {}) {
  try {
    const { data } = await apiClient.get('/notifications/history/', { params });
    return data;
  } catch (error) {
    throw error;
  }
}

export async function markNotificationsRead(notificationIds = [], markAll = false) {
  try {
    const { data } = await apiClient.post('/notifications/mark-read/', {
      notification_ids: notificationIds,
      mark_all: markAll
    });
    return data;
  } catch (error) {
    return {
      success: false,
      message: error.response?.data?.message || 'Failed to mark as read'
    };
  }
}

// ====================
// NEWS
// ====================

export async function getNewsFeed(limit = 20, category = null) {
  try {
    const { data } = await apiClient.get('/news/feed/', {
      params: { limit, category }
    });
    return data;
  } catch (error) {
    throw error;
  }
}

export async function markNewsRead(newsId) {
  try {
    const { data } = await apiClient.post('/news/mark-read/', {
      news_id: newsId
    });
    return data;
  } catch (error) {
    return {
      success: false,
      message: error.response?.data?.message || 'Failed to mark as read'
    };
  }
}

export async function updateNewsPreferences(preferences) {
  try {
    const { data } = await apiClient.post('/news/preferences/', preferences);
    return data;
  } catch (error) {
    return {
      success: false,
      message: error.response?.data?.message || 'Failed to update preferences'
    };
  }
}

// ====================
// SUBSCRIPTIONS
// ====================

export async function subscribeToNewsletter(email, category = null) {
  try {
    const { data } = await apiClient.post('/subscription/', {
      email,
      category
    });
    return data;
  } catch (error) {
    return {
      success: false,
      message: error.response?.data?.message || 'Subscription failed'
    };
  }
}

// ====================
// HEALTH & STATUS
// ====================

export async function checkHealth() {
  try {
    const { data } = await axios.get(`${DJANGO_API_URL}/health/`);
    return data;
  } catch (error) {
    return {
      status: 'error',
      message: 'API is unreachable'
    };
  }
}

export async function getEndpointStatus() {
  try {
    const { data } = await axios.get(`${DJANGO_API_URL}/endpoint-status/`);
    return data;
  } catch (error) {
    throw error;
  }
}

// ====================
// UTILITY FUNCTIONS
// ====================

export function isAuthenticated() {
  return !!localStorage.getItem('django_session_id') || !!localStorage.getItem('django_auth_token');
}

export function getCurrentUser() {
  const userStr = localStorage.getItem('django_user');
  return userStr ? JSON.parse(userStr) : null;
}

export function clearAuthData() {
  localStorage.removeItem('django_auth_token');
  localStorage.removeItem('django_session_id');
  localStorage.removeItem('django_user');
}

// Export clients for direct use if needed
export { apiClient, revenueClient };