/**
 * Main API Client
 * Re-exports Django client for backward compatibility
 */

// Re-export everything from django-client
export * from './django-client';

// Import the Django client
import { apiClient, revenueClient } from './django-client';

// Legacy exports for backward compatibility
export const API_ROOT = 'https://api.retailtradescanner.com/api';
export const REVENUE_ROOT = 'https://api.retailtradescanner.com/revenue';

// Export api client with backward compatible name
export const api = apiClient;
export { revenueClient };

// Simple network event bus for latency indicator (if used by other components)
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

// Re-export all functions from django-client for backward compatibility
export {
  login,
  logout,
  register,
  getUserProfile,
  updateUserProfile,
  changePassword,
  getCurrentPlan,
  changePlan,
  getBillingHistory,
  getBillingStats,
  updatePaymentMethod,
  validateDiscountCode,
  applyDiscount,
  getStocks,
  getStockDetails,
  searchStocks,
  getRealtimeData,
  getTrendingStocks,
  getMarketStats,
  filterStocks,
  getPortfolio,
  addToPortfolio,
  removeFromPortfolio,
  getWatchlist,
  addToWatchlist,
  removeFromWatchlist,
  createAlert,
  getNotificationSettings,
  updateNotificationSettings,
  getNotificationHistory,
  markNotificationsRead,
  getNewsFeed,
  markNewsRead,
  updateNewsPreferences,
  subscribeToNewsletter,
  checkHealth,
  getEndpointStatus,
  isAuthenticated,
  getCurrentUser,
  clearAuthData
} from './django-client';

// Cache functionality (if needed by legacy code)
export function getCache(key) {
  try {
    const item = localStorage.getItem(`cache_${key}`);
    if (!item) return null;
    
    const parsed = JSON.parse(item);
    if (Date.now() > parsed.expiry) {
      localStorage.removeItem(`cache_${key}`);
      return null;
    }
    return parsed.data;
  } catch {
    return null;
  }
}

export function setCache(key, data, ttlMinutes = 5) {
  try {
    const item = {
      data,
      expiry: Date.now() + (ttlMinutes * 60 * 1000)
    };
    localStorage.setItem(`cache_${key}`, JSON.stringify(item));
  } catch {
    // Ignore cache errors
  }
}

// Legacy function mappings (if any components use old names)
export const loginUser = login;
export const registerUser = register;
export const getProfile = getUserProfile;
export const updateProfile = updateUserProfile;